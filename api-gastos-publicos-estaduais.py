"""
SIOPS - Despesas em Saúde e APS por Estado
===========================================
Consulta a API pública do SIOPS e extrai, para todos os estados do Brasil:
  - Gasto TOTAL em saúde     (grupo=17, valor10)
  - Gasto em APS / Subfunção 301 (grupo=1 + grupo=2, valor10)

Baseado no script municipal (siops_municipios_aps_2023.py).
A diferença principal é o endpoint estadual, que não recebe co_municipio:
  Municipal: /v1/despesas-por-subfuncao/{co_uf}/{co_municipio}/{ano}/{periodo}
  Estadual:  /v1/despesas-por-subfuncao/{co_uf}/{ano}/{periodo}   ← assumido

IMPORTANTE: verifique o endpoint correto no Swagger antes de rodar:
  https://siops-consulta-publica-api.saude.gov.br/swagger-ui/

Documentação:
  https://siops-consulta-publica-api.saude.gov.br/swagger-ui/
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
ANO      = "2023"
PERIODO  = "2"    # 6º Bimestre / Anual (jan-dez) — mesmo padrão do script municipal

OUTPUT_CSV = Path("siops_estados_aps_2023.csv")
TIMEOUT    = 30
SLEEP_BETWEEN = 0.3   # estados são poucos (27), pode ser mais conservador

# Grupos da subfunção 301 (Atenção Básica = APS)
GRUPOS_APS        = {"1", "2"}   # 1 = Corrente, 2 = Capital
GRUPO_TOTAL_SAUDE = "17"
CAMPO_VALOR_TOTAL = "valor10"   # API estadual usa "valor10", não "vl_coluna10" (municipal)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("siops_estados")

# ---------------------------------------------------------------------------
# SESSÃO HTTP COM RETRY
# ---------------------------------------------------------------------------
def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1.5,
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
# VERIFICAÇÃO DO ENDPOINT ANTES DE RODAR TUDO
# ---------------------------------------------------------------------------
def verificar_endpoint(co_uf_teste: str = "35") -> bool:
    """
    Testa o endpoint estadual com SP (co_uf=35) antes de processar todos os estados.
    Se falhar, imprime sugestão de endpoint alternativo.
    """
    log.info("Verificando endpoint estadual com UF=35 (SP)...")
    try:
        resultado = get_json(f"/v1/despesas-por-subfuncao/{co_uf_teste}/{ANO}/{PERIODO}")
        if resultado:
            log.info("Endpoint OK. Primeiro registro: %s", resultado[0])
            return True
        else:
            log.warning("Endpoint respondeu 200 mas retornou lista vazia.")
            return True  # endpoint existe, só sem dado
    except requests.HTTPError as e:
        log.error("Endpoint /v1/despesas-por-subfuncao/{co_uf}/{ano}/{periodo} falhou: %s", e)
        log.error("Verifique o Swagger em: https://siops-consulta-publica-api.saude.gov.br/swagger-ui/")
        log.error("Possíveis alternativas:")
        log.error("  /v1/despesas-por-subfuncao/estadual/{co_uf}/{ano}/{periodo}")
        log.error("  /v1/despesas-por-subfuncao/estado/{co_uf}/{ano}/{periodo}")
        return False

# ---------------------------------------------------------------------------
# COLETA DE METADADOS
# ---------------------------------------------------------------------------
def listar_estados() -> list[dict]:
    log.info("Buscando lista de UFs...")
    return get_json("/v1/ente/estados")

# ---------------------------------------------------------------------------
# CONSULTA DE DESPESAS ESTADUAIS
# ---------------------------------------------------------------------------
def consultar_despesas_estado(co_uf: str, ano: str, periodo: str) -> list[dict]:
    """
    Endpoint estadual: sem co_municipio.
    Se a API usar caminho diferente, ajuste aqui.
    """
    return get_json(f"/v1/despesas-por-subfuncao/{co_uf}/{ano}/{periodo}")

def _to_float(v) -> float:
    if v is None or v == "":
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))

def extrair_totais(linhas: list[dict]) -> tuple[float, float]:
    total_saude = 0.0
    total_aps   = 0.0
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
    # Verifica endpoint antes de processar tudo
    if not verificar_endpoint():
        log.error("Abortando. Corrija o endpoint e tente novamente.")
        return

    estados = listar_estados()
    log.info("Encontradas %d UFs.", len(estados))

    gasto_total_brasil   = 0.0
    gasto_aps_brasil     = 0.0
    total_erros          = 0

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "co_uf", "sg_uf", "no_uf",
            "ano", "periodo",
            "gasto_total_saude",
            "gasto_aps",
            "perc_aps_sobre_total",
            "status",
        ])

        for uf in estados:
            co_uf = uf["co_uf"]
            sg_uf = uf["sg_uf"]
            no_uf = uf["no_uf"]

            try:
                linhas = consultar_despesas_estado(co_uf, ANO, PERIODO)

                if not linhas:
                    log.warning("Sem dados para %s (%s)", sg_uf, no_uf)
                    writer.writerow([co_uf, sg_uf, no_uf, ANO, PERIODO,
                                     0, 0, 0, "SEM_DADOS"])
                    f.flush()
                    continue

                total_saude, total_aps = extrair_totais(linhas)
                perc = (total_aps / total_saude * 100) if total_saude else 0.0

                gasto_total_brasil += total_saude
                gasto_aps_brasil   += total_aps

                writer.writerow([
                    co_uf, sg_uf, no_uf,
                    ANO, PERIODO,
                    f"{total_saude:.2f}",
                    f"{total_aps:.2f}",
                    f"{perc:.2f}",
                    "OK",
                ])
                f.flush()
                log.info("%-5s %-25s | Saúde: R$ %15.2f | APS: R$ %15.2f (%.1f%%)",
                         sg_uf, no_uf, total_saude, total_aps, perc)

            except requests.HTTPError as e:
                total_erros += 1
                log.warning("Erro HTTP em %s: %s", sg_uf, e)
                writer.writerow([co_uf, sg_uf, no_uf, ANO, PERIODO,
                                 "", "", "", f"ERRO_HTTP_{e.response.status_code}"])
                f.flush()

            except Exception as e:
                total_erros += 1
                log.warning("Erro inesperado em %s: %s", sg_uf, e)
                writer.writerow([co_uf, sg_uf, no_uf, ANO, PERIODO,
                                 "", "", "", f"ERRO:{type(e).__name__}"])
                f.flush()

            time.sleep(SLEEP_BETWEEN)

    # Resumo final
    perc_total = (gasto_aps_brasil / gasto_total_brasil * 100) if gasto_total_brasil else 0
    log.info("=" * 70)
    log.info("FIM. Estados processados com sucesso. Erros: %d", total_erros)
    log.info("Gasto TOTAL estadual em saúde : R$ %.2f", gasto_total_brasil)
    log.info("Gasto estadual em APS (301)   : R$ %.2f", gasto_aps_brasil)
    log.info("%% APS sobre o total           : %.2f%%", perc_total)
    log.info("Arquivo gerado: %s", OUTPUT_CSV.resolve())

if __name__ == "__main__":
    main()
