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
df_trans = df_junto[df_junto['grupo_procedimento'] == 'Transplantes de órgãos, tecidos e células']
df_trans['US_TOT'] = pd.to_numeric(df_trans['US_TOT'], errors='coerce')
total_trans = len(df_trans)
if total_trans > 0:
    with open("analise_transplantes_en.html", "w", encoding="utf-8") as f:
        f.write("<h1>Detailed Analysis: Organ, Tissue and Cell Transplants</h1>\n")
        total_fmt = f"{total_trans:,}".replace(",", ".")
        f.write(f"<p><strong>Total number of transplants:</strong> {total_fmt}</p>\n")
        paises_trans = df_trans.groupby('pais').size().reset_index(name='Quantidade')
        paises_trans = paises_trans.sort_values('Quantidade', ascending=False).head(10)
        f.write("<p><strong>Top 10 countries by number of transplants:</strong></p>\n<ul>\n")
        for _, row in paises_trans.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['pais']}: {qty}</li>\n")
        f.write("</ul>\n")
        ufs_trans = df_trans.groupby('uf').size().reset_index(name='Quantidade')
        ufs_trans['Percentual'] = (ufs_trans['Quantidade'] / total_trans) * 100
        ufs_top5_trans = ufs_trans.sort_values('Percentual', ascending=False).head(5)
        f.write("<p><strong>Top 5 states by percentage:</strong></p>\n<ul>\n")
        for _, row in ufs_top5_trans.iterrows():
            pct = int(round(row['Percentual']))
            f.write(f"<li>{row['uf']}: {pct}%</li>\n")
        f.write("</ul>\n")
        municipios_trans = df_trans.groupby(['nome_municipio', 'uf']).size().reset_index(name='Quantidade')
        municipios_trans = municipios_trans.sort_values('Quantidade', ascending=False).head(10)
        f.write("<p><strong>Top 10 municipalities with the highest number of transplants:</strong></p>\n<ul>\n")
        for _, row in municipios_trans.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['nome_municipio']} ({row['uf']}): {qty}</li>\n")
        f.write("</ul>\n")
        anos_trans = df_trans.groupby('ANO_CMPT').size().reset_index(name='Quantidade')
        anos_trans = anos_trans.sort_values('ANO_CMPT')
        f.write("<p><strong>Number of transplants by year:</strong></p>\n<ul>\n")
        for _, row in anos_trans.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['ANO_CMPT']}: {qty}</li>\n")
        f.write("</ul>\n")
        idade_media = df_trans['IDADE'].mean()
        f.write(f"<p><strong>Average age:</strong> {idade_media:.1f} years</p>\n")
        sexo_trans = df_trans.groupby('SEXO').size().reset_index(name='Quantidade')
        sexo_trans['Percentual'] = (sexo_trans['Quantidade'] / total_trans) * 100
        f.write("<p><strong>Distribution by gender:</strong></p>\n<ul>\n")
        for _, row in sexo_trans.iterrows():
            pct = int(round(row['Percentual']))
            sexo_nome = "Male" if row['SEXO'] == 1 else "Female" if row['SEXO'] == 3 else f"Code {row['SEXO']}"
            qty_sexo = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{sexo_nome}: {pct}% ({qty_sexo})</li>\n")
        f.write("</ul>\n")
        proc_trans = df_trans.groupby('PROC_REA').size().reset_index(name='Quantidade')
        proc_trans = proc_trans.sort_values('Quantidade', ascending=False).head(10)
        f.write("<p><strong>Top 10 PROC_REA codes by number of transplants:</strong></p>\n<ul>\n")
        for _, row in proc_trans.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['PROC_REA']}: {qty}</li>\n")
        f.write("</ul>\n")
    def k_formatter(x, pos):
        if x >= 1000:
            return f"{int(x/1000)}k"
        else:
            return str(int(x))
    plt.figure(figsize=(10, 6))
    dados_ate_2024 = anos_trans[anos_trans["ANO_CMPT"] < 2025]
    dados_2025 = anos_trans[anos_trans["ANO_CMPT"] == 2025]
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
    plt.title("Annual hospital admissions of foreign nationals for transplant procedures in Brazil’s Unified Health System (SUS)", fontsize=12)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Number of Transplants", fontsize=12)
    plt.xticks(anos_trans["ANO_CMPT"], fontsize=10)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(k_formatter))
    max_y = anos_trans["Quantidade"].max()
    plt.ylim(bottom=0, top=max_y * 1.1)
    for i, row in anos_trans.iterrows():
        valor = row["Quantidade"]
        label = k_formatter(valor, None)
        plt.text(
            row["ANO_CMPT"],
            valor + max_y * 0.02,
            label,
            ha="center",
            va="bottom",
            fontsize=10
        )
    plt.figtext(0.5, -0.01, "Source: SIH/SUS – Hospital Information System of SUS (Datasus).", ha="center", fontsize=9, style="italic")
    plt.figtext(0.5, -0.05, "Note: 2025 data is partial (up to August 2025) and is indicated by the dashed line.", ha="center", fontsize=9, style="italic")
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    plt.savefig("transplantes_por_ano_en.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Transplant analysis saved in analise_transplantes_en.html and chart generated")
else:
    print("No data found for transplants")