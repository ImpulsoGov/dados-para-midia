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
df_usa = df_junto[df_junto['NACIONAL'] == 36]
df_usa['US_TOT'] = pd.to_numeric(df_usa['US_TOT'], errors='coerce')
df_usa['PROC_REA_str'] = df_usa['PROC_REA'].astype(str).str.strip()
df_usa['sub_grupo'] = df_usa['PROC_REA_str'].str[:5]
total_usa = len(df_usa)
if total_usa > 0:
    with open("analise_usa.html", "w", encoding="utf-8") as f:
        f.write("<h1>Análise Detalhada: Estados Unidos</h1>\n")
        total_fmt = f"{total_usa:,}".replace(",", ".")
        f.write(f"<p><strong>Quantidade de internações:</strong> {total_fmt}</p>\n")
        municipios_usa = df_usa.groupby(['nome_municipio', 'uf']).size().reset_index(name='Quantidade')
        municipios_usa = municipios_usa.sort_values('Quantidade', ascending=False).head(5)
        f.write("<p><strong>Top 5 municípios com maior quantidade de internações:</strong></p>\n<ul>\n")
        for _, row in municipios_usa.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['nome_municipio']} ({row['uf']}): {qty}</li>\n")
        f.write("</ul>\n")
        ufs_usa = df_usa.groupby('uf').size().reset_index(name='Quantidade')
        ufs_usa['Percentual'] = (ufs_usa['Quantidade'] / total_usa) * 100
        ufs_top5_usa = ufs_usa.sort_values('Percentual', ascending=False).head(5)
        f.write("<p><strong>Top 5 UFs por percentual:</strong></p>\n<ul>\n")
        for _, row in ufs_top5_usa.iterrows():
            pct = int(round(row['Percentual']))
            f.write(f"<li>{row['uf']}: {pct}%</li>\n")
        f.write("</ul>\n")
        grupos_usa = df_usa.groupby('grupo_procedimento').size().reset_index(name='Quantidade')
        grupos_usa['Percentual'] = (grupos_usa['Quantidade'] / total_usa) * 100
        f.write("<p><strong>Percentual distribuição por grupo de procedimento:</strong></p>\n<ul>\n")
        for _, row in grupos_usa.sort_values('Percentual', ascending=False).iterrows():
            pct = int(round(row['Percentual']))
            f.write(f"<li>{row['grupo_procedimento']}: {pct}%</li>\n")
        f.write("</ul>\n")
        internacoes_por_ano_ate_agosto = df_usa.query("MES_CMPT <= 8")
        anos_usa_ate_agosto = internacoes_por_ano_ate_agosto.groupby('ANO_CMPT').size().reset_index(name='Quantidade')
        anos_usa_ate_agosto = anos_usa_ate_agosto.sort_values('ANO_CMPT')
        anos_usa = df_usa.groupby('ANO_CMPT').size().reset_index(name='Quantidade')
        anos_usa = anos_usa.sort_values('ANO_CMPT')
        f.write("<p><strong>Quantidade de internações por ano:</strong></p>\n<ul>\n")
        for _, row in anos_usa.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['ANO_CMPT']}: {qty}</li>\n")
        f.write("</ul>\n")
        sub_grupos_usa = df_usa.groupby('sub_grupo').size().reset_index(name='Quantidade')
        sub_grupos_usa = sub_grupos_usa.sort_values('Quantidade', ascending=False).head(10)
        f.write("<p><strong>Top 10 sub-grupos de procedimento por quantidade:</strong></p>\n<ul>\n")
        for _, row in sub_grupos_usa.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['sub_grupo']}: {qty}</li>\n")
        f.write("</ul>\n")
        idade_media = df_usa['IDADE'].mean()
        f.write(f"<p><strong>Idade média:</strong> {idade_media:.1f} anos</p>\n")
        sexo_usa = df_usa.groupby('SEXO').size().reset_index(name='Quantidade')
        sexo_usa['Percentual'] = (sexo_usa['Quantidade'] / total_usa) * 100
        f.write("<p><strong>Distribuição por sexo:</strong></p>\n<ul>\n")
        for _, row in sexo_usa.iterrows():
            pct = int(round(row['Percentual']))
            sexo_nome = "Masculino" if row['SEXO'] == 1 else "Feminino" if row['SEXO'] == 3 else f"Código {row['SEXO']}"
            f.write(f"<li>{sexo_nome}: {pct}% ({row['Quantidade']:,})</li>\n")
        f.write("</ul>\n")
    def mil_formatter(x, pos):
        if x >= 1000:
            return f"{int(x/1000)} mil"
        else:
            return str(int(x))
    plt.figure(figsize=(10, 6))
    plt.plot(
        anos_usa_ate_agosto["ANO_CMPT"],
        anos_usa_ate_agosto["Quantidade"]
    )
    plt.title("Internações de urgência no SUS de pacientes dos Estados Unidos, por ano \n (Janeiro a Agosto de cada ano)", fontsize=14)
    plt.xlabel("Ano", fontsize=12)
    plt.ylabel("Quantidade de internações", fontsize=12)
    plt.xticks(anos_usa["ANO_CMPT"], fontsize=10)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(mil_formatter))
    max_y = anos_usa_ate_agosto["Quantidade"].max()
    plt.ylim(bottom=0, top=max_y * 1.1)
    for i, row in anos_usa_ate_agosto.iterrows():
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
        "Fonte: SIH/SUS – Sistema de Informações Hospitalares do SUS (Datasus).",
        ha="center", fontsize=9, style="italic"
    )
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    plt.savefig("internacoes_usa_por_ano_ate_agosto.png", dpi=300, bbox_inches='tight')
    plt.show()
    valorespor_ano_ate_agosto = df_usa.query("MES_CMPT <= 8")
    valores_por_ano_ate_agosto = valorespor_ano_ate_agosto.groupby('ANO_CMPT')['US_TOT'].sum().reset_index()
    valores_por_ano_ate_agosto = valores_por_ano_ate_agosto.sort_values('ANO_CMPT')
    plt.figure(figsize=(10, 6))
    plt.plot(
        valores_por_ano_ate_agosto["ANO_CMPT"],
        valores_por_ano_ate_agosto["US_TOT"]
    )
    plt.title("Valor total dos procedimentos realizados no SUS para pacientes dos Estados Unidos, por ano \n (Janeiro a Agosto de cada ano)", fontsize=12)
    plt.xlabel("Ano", fontsize=12)
    plt.ylabel("Valor total (US$)", fontsize=12)
    plt.xticks(valores_por_ano_ate_agosto["ANO_CMPT"], fontsize=10)
    def milhao_formatter(x, pos):
        if x >= 1000000:
            return f"{int(x/1000000)} milhões"
        elif x >= 1000:
            return f"{int(x/1000)} mil"
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
        "Fonte: SIH/SUS – Sistema de Informações Hospitalares do SUS (Datasus).",
        ha="center", fontsize=9, style="italic"
    )
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    plt.savefig("valores_usa_por_ano.png", dpi=300, bbox_inches='tight')
    plt.show()
    print("Análise dos EUA salva em analise_usa.html e gráfico em internacoes_usa_por_ano.png")
else:
    print("Nenhum dado encontrado para Estados Unidos")