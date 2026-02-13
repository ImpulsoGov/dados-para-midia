import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
df_junto = pd.read_csv("dados_paises_sus_estrangeiros.csv")
df_junto = df_junto.query("pais != 'RESERVADO'")
url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
resp = requests.get(url).json()
uf_map = {
    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
    '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE', '29': 'BA',
    '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
    '41': 'PR', '42': 'SC', '43': 'RS',
    '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
}
ibge = pd.DataFrame([
    {
        "codigo_ibge_7": str(item["id"]),
        "codigo_ibge_6": str(item["id"])[:-1],
        "nome_municipio": item["nome"],
        "uf": uf_map.get(str(item["id"])[:2], "N/A")
    }
    for item in resp
])
df_junto['MUNIC_MOV'] = df_junto['MUNIC_MOV'].astype(str)
df_junto = df_junto.merge(
    ibge,
    left_on='MUNIC_MOV',
    right_on='codigo_ibge_6',
    how='left'
).drop(columns=['codigo_ibge_6'])
df_ing = df_junto[df_junto['pais'] == 'INGLATERRA']
df_ing['US_TOT'] = pd.to_numeric(df_ing['US_TOT'], errors='coerce')
df_ing['PROC_REA_str'] = df_ing['PROC_REA'].astype(str).str.strip()
df_ing['sub_grupo'] = df_ing['PROC_REA_str'].str[:5]
total_ing = len(df_ing)
if total_ing > 0:
    with open("analise_inglaterra.html", "w", encoding="utf-8") as f:
        f.write("<h1>Análise Detalhada: Reino Unido</h1>\n")
        total_fmt = f"{total_ing:,}".replace(",", ".")
        f.write(f"<p><strong>Quantidade de internações:</strong> {total_fmt}</p>\n")
        municipios_ing = df_ing.groupby(['nome_municipio', 'uf']).size().reset_index(name='Quantidade')
        municipios_ing = municipios_ing.sort_values('Quantidade', ascending=False).head(5)
        f.write("<p><strong>Top 5 municípios com maior quantidade de internações:</strong></p>\n<ul>\n")
        for _, row in municipios_ing.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['nome_municipio']} ({row['uf']}): {qty}</li>\n")
        f.write("</ul>\n")
        ufs_ing = df_ing.groupby('uf').size().reset_index(name='Quantidade')
        ufs_ing['Percentual'] = (ufs_ing['Quantidade'] / total_ing) * 100
        ufs_top5_ing = ufs_ing.sort_values('Percentual', ascending=False).head(5)
        f.write("<p><strong>Top 5 UFs por percentual:</strong></p>\n<ul>\n")
        for _, row in ufs_top5_ing.iterrows():
            pct = int(round(row['Percentual']))
            f.write(f"<li>{row['uf']}: {pct}%</li>\n")
        f.write("</ul>\n")
        grupos_ing = df_ing.groupby('grupo_procedimento').size().reset_index(name='Quantidade')
        grupos_ing['Percentual'] = (grupos_ing['Quantidade'] / total_ing) * 100
        f.write("<p><strong>Percentual distribuição por grupo de procedimento:</strong></p>\n<ul>\n")
        for _, row in grupos_ing.sort_values('Percentual', ascending=False).iterrows():
            pct = int(round(row['Percentual']))
            f.write(f"<li>{row['grupo_procedimento']}: {pct}%</li>\n")
        f.write("</ul>\n")
        anos_ing = df_ing.groupby('ANO_CMPT').size().reset_index(name='Quantidade')
        anos_ing = anos_ing.sort_values('ANO_CMPT')
        f.write("<p><strong>Quantidade de internações por ano:</strong></p>\n<ul>\n")
        for _, row in anos_ing.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['ANO_CMPT']}: {qty}</li>\n")
        f.write("</ul>\n")
        sub_grupos_ing = df_ing.groupby('sub_grupo').size().reset_index(name='Quantidade')
        sub_grupos_ing = sub_grupos_ing.sort_values('Quantidade', ascending=False).head(10)
        f.write("<p><strong>Top 10 sub-grupos de procedimento por quantidade:</strong></p>\n<ul>\n")
        for _, row in sub_grupos_ing.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['sub_grupo']}: {qty}</li>\n")
        f.write("</ul>\n")
        idade_media = df_ing['IDADE'].mean()
        f.write(f"<p><strong>Idade média:</strong> {idade_media:.1f} anos</p>\n")
        sexo_ing = df_ing.groupby('SEXO').size().reset_index(name='Quantidade')
        sexo_ing['Percentual'] = (sexo_ing['Quantidade'] / total_ing) * 100
        f.write("<p><strong>Distribuição por sexo:</strong></p>\n<ul>\n")
        for _, row in sexo_ing.iterrows():
            pct = int(round(row['Percentual']))
            sexo_nome = "Masculino" if row['SEXO'] == 1 else "Feminino" if row['SEXO'] == 3 else f"Código {row['SEXO']}"
            qty_sexo = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{sexo_nome}: {pct}% ({qty_sexo})</li>\n")
        f.write("</ul>\n")
    plt.figure(figsize=(10, 6))
    dados_ate_2024 = anos_ing[anos_ing["ANO_CMPT"] < 2025]
    dados_2025 = anos_ing[anos_ing["ANO_CMPT"] == 2025]
    plt.plot(
        dados_ate_2024["ANO_CMPT"],
        dados_ate_2024["Quantidade"],
        color="C0"
    )
    if not dados_2025.empty:
        ultimo_2024 = dados_ate_2024.iloc[-1]
        plt.plot(
            [ultimo_2024["ANO_CMPT"], dados_2025["ANO_CMPT"].values[0]],
            [ultimo_2024["Quantidade"], dados_2025["Quantidade"].values[0]],
            color="C0",
            linestyle="--",
            marker=""
        )
    plt.title("Internações de urgência no SUS de pacientes da Inglaterra, por ano", fontsize=14)
    plt.xlabel("Ano", fontsize=12)
    plt.ylabel("Quantidade de internações", fontsize=12)
    plt.xticks(anos_ing["ANO_CMPT"], fontsize=10)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{int(x/1000)} mil" if x >= 1000 else str(int(x))))
    max_y = anos_ing["Quantidade"].max()
    plt.ylim(bottom=0, top=max_y * 1.1)
    for i, row in anos_ing.iterrows():
        valor = row["Quantidade"]
        label = f"{int(valor/1000)} mil" if valor >= 1000 else str(int(valor))
        plt.text(
            row["ANO_CMPT"],
            valor + max_y * 0.02,
            label,
            ha="center",
            va="bottom",
            fontsize=10
        )
    plt.figtext(0.5, -0.01, "Fonte: SIH/SUS – Sistema de Informações Hospitalares do SUS (Datasus).", ha="center", fontsize=9, style="italic")
    plt.figtext(0.5, -0.05, "Nota: Dados de 2025 são parciais (até agosto de 2025) e estão indicados pela linha tracejada.", ha="center", fontsize=9, style="italic")
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    plt.savefig("internacoes_inglaterra_por_ano.png", dpi=300, bbox_inches='tight')
    plt.close()
    valores_por_ano = df_ing.groupby('ANO_CMPT')['US_TOT'].sum().reset_index()
    valores_por_ano = valores_por_ano.sort_values('ANO_CMPT')
    plt.figure(figsize=(10, 6))
    valores_ate_2024 = valores_por_ano[valores_por_ano["ANO_CMPT"] < 2025]
    valores_2025 = valores_por_ano[valores_por_ano["ANO_CMPT"] == 2025]
    plt.plot(
        valores_ate_2024["ANO_CMPT"],
        valores_ate_2024["US_TOT"],
        color="C0"
    )
    if not valores_2025.empty:
        ultimo_2024 = valores_ate_2024.iloc[-1]
        plt.plot(
            [ultimo_2024["ANO_CMPT"], valores_2025["ANO_CMPT"].values[0]],
            [ultimo_2024["US_TOT"], valores_2025["US_TOT"].values[0]],
            color="C0",
            linestyle="--",
            marker=""
        )
    plt.title("Valor total dos procedimentos realizados no SUS para pacientes da Inglaterra, por ano (em US$)", fontsize=14)
    plt.xlabel("Ano", fontsize=12)
    plt.ylabel("Valor total (US$)", fontsize=12)
    plt.xticks(valores_por_ano["ANO_CMPT"], fontsize=10)
    def milhao_formatter(x, pos):
        if x >= 1000000:
            return f"{int(x/1000000)} milhões"
        elif x >= 1000:
            return f"{int(x/1000)} mil"
        else:
            return str(int(x))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(milhao_formatter))
    max_y = valores_por_ano["US_TOT"].max()
    plt.ylim(bottom=0, top=max_y * 1.1)
    for i, row in valores_por_ano.iterrows():
        valor = row["US_TOT"]
        label = milhao_formatter(valor, None)
        plt.text(
            row["ANO_CMPT"],
            valor + max_y * 0.02,
            label,
            ha="center",
            va="bottom",
            fontsize=10
        )
    plt.figtext(0.5, -0.01, "Fonte: SIH/SUS – Sistema de Informações Hospitalares do SUS (Datasus).", ha="center", fontsize=9, style="italic")
    plt.figtext(0.5, -0.05, "Nota: Dados de 2025 são parciais (até agosto de 2025) e estão indicados pela linha tracejada.", ha="center", fontsize=9, style="italic")
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    plt.savefig("valores_inglaterra_por_ano.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Análise da Inglaterra salva em analise_inglaterra.html e gráficos gerados")
else:
    print("Nenhum dado encontrado para Reino Unido")