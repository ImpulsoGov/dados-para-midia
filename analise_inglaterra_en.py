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
    with open("analise_inglaterra_en.html", "w", encoding="utf-8") as f:
        f.write("<h1>Detailed Analysis: England</h1>\n")
        total_fmt = f"{total_ing:,}".replace(",", ".")
        f.write(f"<p><strong>Number of hospitalizations:</strong> {total_fmt}</p>\n")
        municipios_ing = df_ing.groupby(['nome_municipio', 'uf']).size().reset_index(name='Quantidade')
        municipios_ing = municipios_ing.sort_values('Quantidade', ascending=False).head(5)
        f.write("<p><strong>Top 5 municipalities with the highest number of hospitalizations:</strong></p>\n<ul>\n")
        for _, row in municipios_ing.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['nome_municipio']} ({row['uf']}): {qty}</li>\n")
        f.write("</ul>\n")
        ufs_ing = df_ing.groupby('uf').size().reset_index(name='Quantidade')
        ufs_ing['Percentual'] = (ufs_ing['Quantidade'] / total_ing) * 100
        ufs_top5_ing = ufs_ing.sort_values('Percentual', ascending=False).head(5)
        f.write("<p><strong>Top 5 states by percentage:</strong></p>\n<ul>\n")
        for _, row in ufs_top5_ing.iterrows():
            pct = int(round(row['Percentual']))
            f.write(f"<li>{row['uf']}: {pct}%</li>\n")
        f.write("</ul>\n")
        grupos_ing = df_ing.groupby('grupo_procedimento').size().reset_index(name='Quantidade')
        grupos_ing['Percentual'] = (grupos_ing['Quantidade'] / total_ing) * 100
        f.write("<p><strong>Percentage distribution by procedure group:</strong></p>\n<ul>\n")
        for _, row in grupos_ing.sort_values('Percentual', ascending=False).iterrows():
            pct = int(round(row['Percentual']))
            f.write(f"<li>{row['grupo_procedimento']}: {pct}%</li>\n")
        f.write("</ul>\n")
        anos_ing = df_ing.groupby('ANO_CMPT').size().reset_index(name='Quantidade')
        anos_ing = anos_ing.sort_values('ANO_CMPT')
        internacao_urgencia_ate_agosto = df_ing.query("MES_CMPT <= 8")
        anos_ing_ate_agosto = internacao_urgencia_ate_agosto.groupby('ANO_CMPT').size().reset_index(name='Quantidade')
        anos_ing_ate_agosto = anos_ing_ate_agosto.sort_values('ANO_CMPT')
        f.write("<p><strong>Number of hospitalizations by year:</strong></p>\n<ul>\n")
        for _, row in anos_ing.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['ANO_CMPT']}: {qty}</li>\n")
        f.write("</ul>\n")
        sub_grupos_ing = df_ing.groupby('sub_grupo').size().reset_index(name='Quantidade')
        sub_grupos_ing = sub_grupos_ing.sort_values('Quantidade', ascending=False).head(10)
        f.write("<p><strong>Top 10 procedure sub-groups by quantity:</strong></p>\n<ul>\n")
        for _, row in sub_grupos_ing.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['sub_grupo']}: {qty}</li>\n")
        f.write("</ul>\n")
        idade_media = df_ing['IDADE'].mean()
        f.write(f"<p><strong>Average age:</strong> {idade_media:.1f} years</p>\n")
        sexo_ing = df_ing.groupby('SEXO').size().reset_index(name='Quantidade')
        sexo_ing['Percentual'] = (sexo_ing['Quantidade'] / total_ing) * 100
        f.write("<p><strong>Distribution by gender:</strong></p>\n<ul>\n")
        for _, row in sexo_ing.iterrows():
            pct = int(round(row['Percentual']))
            sexo_nome = "Male" if row['SEXO'] == 1 else "Female" if row['SEXO'] == 3 else f"Code {row['SEXO']}"
            f.write(f"<li>{sexo_nome}: {pct}% ({row['Quantidade']:,})</li>\n")
        f.write("</ul>\n")
    def mil_formatter(x, pos):
        if x >= 1000:
            return f"{int(x/1000)}k"
        else:
            return str(int(x))
    plt.figure(figsize=(10, 6))
    plt.plot(
        anos_ing_ate_agosto["ANO_CMPT"],
        anos_ing_ate_agosto["Quantidade"]
    )
    plt.title("Annual emergency hospital admissions of English nationals in Brazil’s Unified Health System (SUS) \n (each year includes data through August only)", fontsize=12)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Number of hospitalizations", fontsize=12)
    plt.xticks(anos_ing_ate_agosto["ANO_CMPT"], fontsize=10)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(mil_formatter))
    max_y = anos_ing_ate_agosto["Quantidade"].max()
    plt.ylim(bottom=0, top=max_y * 1.1)
    for i, row in anos_ing_ate_agosto.iterrows():
        valor = row["Quantidade"]
        label = mil_formatter(valor, None)
        plt.text(
            row["ANO_CMPT"],
            valor + max_y * 0.02,
            label,
            ha="center",
            va="bottom",
            fontsize=10
        )
    plt.figtext(
        0.5, -0.01,
        "Source: SIH/SUS – Hospital Information System of SUS (Datasus).",
        ha="center", fontsize=9, style="italic"
    )
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    plt.savefig("internacoes_inglaterra_por_ano_en_ate_agosto.png", dpi=300, bbox_inches='tight')
    plt.show()
    valores_por_ano_ate_agosto = df_ing.query("MES_CMPT <= 8")
    valores_por_ano_ate_agosto = df_ing.groupby('ANO_CMPT')['US_TOT'].sum().reset_index()
    valores_por_ano_ate_agosto = valores_por_ano_ate_agosto.sort_values('ANO_CMPT')
    plt.figure(figsize=(10, 6))
    plt.plot(
        valores_por_ano_ate_agosto["ANO_CMPT"],
        valores_por_ano_ate_agosto["US_TOT"]
    )
    plt.title("Annual total value of procedures performed in Brazil’s Unified Health System (SUS)  \n for patients from England (each year includes data through August only)", fontsize=12)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Total value (US$)", fontsize=12)
    plt.xticks(valores_por_ano_ate_agosto["ANO_CMPT"], fontsize=10)
    def milhao_formatter(x, pos):
        if x >= 1000000:
            return f"{int(x/1000000)} million"
        elif x >= 1000:
            return f"{int(x/1000)}k"
        else:
            return str(int(x))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(milhao_formatter))
    max_y = valores_por_ano_ate_agosto["US_TOT"].max()
    plt.ylim(bottom=0, top=max_y * 1.1)
    for i, row in valores_por_ano_ate_agosto.iterrows():
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
    plt.figtext(
        0.5, -0.01,
        "Source: SIH/SUS – Hospital Information System of SUS (Datasus).",
        ha="center", fontsize=9, style="italic"
    )
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    plt.savefig("valores_inglaterra_por_ano_en_por_ano.png", dpi=300, bbox_inches='tight')
    plt.show()
    print("England analysis saved in analise_inglaterra_en.html and chart in internacoes_inglaterra_por_ano_en.png")
else:
    print("No data found for England")