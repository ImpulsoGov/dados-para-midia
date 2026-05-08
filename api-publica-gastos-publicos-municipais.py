"""
SIOPS - Despesas em Saúde e APS por Município
==============================================
Consulta a API pública do SIOPS e extrai, para todos os municípios do Brasil:
  - Gasto TOTAL em saúde     (grupo=17, valor10)
  - Gasto em APS / Subfunção 301 (grupo=1 + grupo=2, valor10)

Documentação:
  https://siops-consulta-publica-api.saude.gov.br/swagger-ui/

Autor: gerado com ajuda do Claude
"""

import csv
import time
import logging
from pathlib import Path
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------
BASE_URL = "https://siops-consulta-publica-api.saude.gov.br"

ANO = "2023"
PERIODO = "2"    # 6º Bimestre / Anual — dado consolidado e definitivo do ano.
                 # Os períodos do SIOPS são ACUMULADOS no ano, não fatias:
                 #   12 = jan-fev   (1º Bim)
                 #   14 = jan-abr   (2º Bim)
                 #   1  = jan-jun   (3º Bim / 1º Semestre)
                 #   18 = jan-ago   (4º Bim)
                 #   20 = jan-out   (5º Bim)
                 #   2  = jan-dez   (6º Bim / ANUAL) ← este aqui
                 # Confirme disponibilidade em GET /ente/anos antes de rodar.

OUTPUT_CSV = Path("siops_municipios_aps_2023.csv")
TIMEOUT = 30          
SLEEP_BETWEEN = 0.15  

# Grupos da subfunção 301 (Atenção Básica = APS)
# Atenção: a API retorna `grupo` como string ("1", "2", "17") — comparar como str.
GRUPOS_APS = {"1", "2"}      # 1 = Corrente, 2 = Capital
GRUPO_TOTAL_SAUDE = "17"

# Nome real do campo de valor total na resposta da API (PDF de metadados está desatualizado).
CAMPO_VALOR_TOTAL = "vl_coluna10"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("siops")


# ---------------------------------------------------------------------------
# SESSÃO HTTP COM RETRY
# ---------------------------------------------------------------------------
def make_session() -> requests.Session:
    """Sessão com retry automático em erros 5xx e timeouts."""
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.5,        # 1.5s, 3s, 6s, 12s, 24s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"Accept": "application/json"})
    return s


SESSION = make_session()


def get_json(path: str, params: Optional[dict] = None):
    url = f"{BASE_URL}{path}"
    r = SESSION.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# COLETA DE METADADOS (UFs e municípios)
# ---------------------------------------------------------------------------
def listar_estados() -> list[dict]:
    log.info("Buscando lista de UFs...")
    return get_json("/v1/ente/estados")


def listar_municipios(co_uf: str) -> list[dict]:
    return get_json(f"/v1/ente/municipal/{co_uf}")


# ---------------------------------------------------------------------------
# CONSULTA DE DESPESAS POR SUBFUNÇÃO
# ---------------------------------------------------------------------------
def consultar_despesas(co_uf: str, co_municipio: str, ano: str, periodo: str):
    """Retorna a lista de linhas do relatório despesas-por-subfuncao."""
    return get_json(
        f"/v1/despesas-por-subfuncao/{co_uf}/{co_municipio}/{ano}/{periodo}"
    )


def _to_float(v) -> float:
    """Converte valor da API pra float; trata None, vazio, vírgula decimal."""
    if v is None or v == "":
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def extrair_totais(linhas: list[dict]) -> tuple[float, float]:
    """
    Recebe o JSON do despesas-por-subfuncao e devolve:
      (gasto_total_saude, gasto_aps)
    Ambos extraídos da coluna vl_coluna10 (Valor Total) conforme retorno real da API.
    """
    total_saude = 0.0
    total_aps = 0.0

    for linha in linhas:
        grupo = str(linha.get("grupo", "")).strip()
        valor = _to_float(linha.get(CAMPO_VALOR_TOTAL))

        if grupo == GRUPO_TOTAL_SAUDE:
            total_saude += valor
        if grupo in GRUPOS_APS:
            total_aps += valor

    return total_saude, total_aps


# ---------------------------------------------------------------------------
# PIPELINE PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    estados = listar_estados()
    log.info("Encontradas %d UFs.", len(estados))

    # Abre o CSV em modo escrita incremental — se travar no meio, você não perde tudo.
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "co_uf", "sg_uf", "no_uf",
            "co_municipio", "no_municipio",
            "ano", "periodo",
            "gasto_total_saude", "gasto_aps",
            "perc_aps_sobre_total",
            "status",
        ])

        total_municipios_processados = 0
        total_erros = 0

        for uf in estados:
            co_uf = uf["co_uf"]
            sg_uf = uf["sg_uf"]
            no_uf = uf["no_uf"]

            log.info("=== UF %s (%s) — buscando municípios...", sg_uf, no_uf)
            try:
                municipios = listar_municipios(co_uf)
            except Exception as e:
                log.error("Falha ao listar municípios de %s: %s", sg_uf, e)
                continue

            log.info("    %d municípios em %s", len(municipios), sg_uf)

            for i, mun in enumerate(municipios, 1):
                co_mun = mun["co_municipio"]
                no_mun = mun["no_municipio"]

                try:
                    linhas = consultar_despesas(co_uf, co_mun, ANO, PERIODO)
                    if not linhas:
                        # Município sem dado informado pra esse período
                        writer.writerow([
                            co_uf, sg_uf, no_uf, co_mun, no_mun,
                            ANO, PERIODO, 0, 0, 0, "SEM_DADOS"
                        ])
                        f.flush()
                        continue

                    total_saude, total_aps = extrair_totais(linhas)
                    perc = (total_aps / total_saude * 100) if total_saude else 0.0

                    writer.writerow([
                        co_uf, sg_uf, no_uf, co_mun, no_mun,
                        ANO, PERIODO,
                        f"{total_saude:.2f}",
                        f"{total_aps:.2f}",
                        f"{perc:.2f}",
                        "OK",
                    ])
                    f.flush()
                    total_municipios_processados += 1

                except requests.HTTPError as e:
                    total_erros += 1
                    log.warning("Erro HTTP em %s/%s: %s", sg_uf, no_mun, e)
                    writer.writerow([
                        co_uf, sg_uf, no_uf, co_mun, no_mun,
                        ANO, PERIODO, "", "", "", f"ERRO_HTTP_{e.response.status_code}"
                    ])
                    f.flush()
                except Exception as e:
                    total_erros += 1
                    log.warning("Erro inesperado em %s/%s: %s", sg_uf, no_mun, e)
                    writer.writerow([
                        co_uf, sg_uf, no_uf, co_mun, no_mun,
                        ANO, PERIODO, "", "", "", f"ERRO:{type(e).__name__}"
                    ])
                    f.flush()

                if i % 50 == 0:
                    log.info("    [%s] %d/%d municípios processados",
                             sg_uf, i, len(municipios))

                time.sleep(SLEEP_BETWEEN)

        log.info("=" * 60)
        log.info("FIM. Municípios OK: %d | Erros: %d",
                 total_municipios_processados, total_erros)
        log.info("Arquivo gerado: %s", OUTPUT_CSV.resolve())


if __name__ == "__main__":
    main()
