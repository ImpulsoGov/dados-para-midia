boliimport pandas as pd
import requests
df_junto = pd.read_csv("dados_paises_sus_estrangeiros.csv")
df_junto = df_junto.query("pais != 'RESERVADO'")
top_paises = df_junto.groupby('pais').size().reset_index(name='Quantidade')
top_paises = top_paises.sort_values(by='Quantidade', ascending=False)
top10_paises = top_paises.head(10)
lista_top10 = top10_paises['pais'].tolist()
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
analise_pais = (
    df_junto[df_junto['pais'].isin(lista_top10)]
    .groupby('pais')
    .size()
    .reset_index(name='Quantidade')
    .sort_values(by='Quantidade', ascending=False)
)
analise_pais_municipio = (
    df_junto[df_junto['pais'].isin(lista_top10)]
    .groupby(['pais', 'MUNIC_MOV'])
    .size()
    .reset_index(name='Quantidade')
    .sort_values(['pais', 'Quantidade'], ascending=[True, False])
)
analise_pais_municipio = analise_pais_municipio.merge(
    ibge,
    left_on='MUNIC_MOV',
    right_on='codigo_ibge_6',
    how='left'
).drop(columns=['codigo_ibge_6', 'codigo_ibge_7'])
analise_pais_grupo = (
    df_junto[df_junto['pais'].isin(lista_top10)]
    .groupby(['pais', 'grupo_procedimento'])
    .size()
    .reset_index(name='Quantidade')
    .sort_values(['pais', 'Quantidade'], ascending=[True, False])
)
with open("analise_top10_resultados.html", "w", encoding="utf-8") as f:
    f.write("<h1>Análise Descritiva dos Top 10 Países com Mais Internações de Estrangeiros no SUS</h1>\n")
    f.write("<p>Dados de internações de urgência/emergência (2019-2025 parcial).</p>\n")
    for i, pais in enumerate(lista_top10, 1):
        f.write(f"<h2>{i}. {pais}</h2>\n")
        total = analise_pais[analise_pais['pais'] == pais]['Quantidade'].values[0]
        total_fmt = f"{total:,}".replace(",", ".")
        f.write(f"<p><strong>Quantidade de internações:</strong> {total_fmt}</p>\n")
        municipios = analise_pais_municipio[analise_pais_municipio['pais'] == pais].head(5)
        f.write("<p><strong>Top 5 municípios com maior quantidade de internações:</strong></p>\n<ul>\n")
        for _, row in municipios.iterrows():
            qty = f"{row['Quantidade']:,}".replace(",", ".")
            f.write(f"<li>{row['nome_municipio']} ({row['uf']}): {qty}</li>\n")
        f.write("</ul>\n")
        ufs = df_junto[df_junto['pais'] == pais].groupby('uf').size().reset_index(name='Quantidade')
        ufs['Percentual'] = (ufs['Quantidade'] / total) * 100
        ufs_top5 = ufs.sort_values('Percentual', ascending=False).head(5)
        f.write("<p><strong>Top 5 UFs por percentual:</strong></p>\n<ul>\n")
        for _, row in ufs_top5.iterrows():
            f.write(f"<li>{row['uf']}: {int(round(row['Percentual']))}%</li>\n")
        f.write("</ul>\n")
        grupos = analise_pais_grupo[analise_pais_grupo['pais'] == pais].copy()
        grupos['Percentual'] = (grupos['Quantidade'] / total) * 100
        f.write("<p><strong>Percentual distribuição por grupo de procedimento:</strong></p>\n<ul>\n")
        for _, row in grupos.sort_values('Percentual', ascending=False).iterrows():
            pct = int(round(row['Percentual']))
            f.write(f"<li>{row['grupo_procedimento']}: {pct}%</li>\n")
        f.write("</ul>\n")
print("Resultados salvos em analise_top10_resultados.html")