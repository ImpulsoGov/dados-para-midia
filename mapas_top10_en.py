import pandas as pd
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
df_junto = pd.read_csv("dados_paises_sus_estrangeiros.csv")
df_junto = df_junto.query("pais != 'RESERVADO'")
top_paises = df_junto.groupby('pais').size().reset_index(name='Quantidade')
top_paises = top_paises.sort_values(by='Quantidade', ascending=False)
top10_paises = top_paises.head(10)
lista_top10 = top10_paises['pais'].tolist()
format_paises = {
    'VENEZUELA': 'Venezuela',
    'BOLIVIA': 'Bolivia',
    'PARAGUAI': 'Paraguay',
    'REPUBLICA DO HAITI': 'Haiti',
    'PORTUGAL': 'Portugal',
    'ARGENTINA': 'Argentina',
    'JAPAO': 'Japan',
    'CUBA': 'Cuba',
    'CHILE': 'Chile',
    'ITALIA': 'Italy'
}
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
url_geo = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
gdf = gpd.read_file(url_geo)
fig, axes = plt.subplots(2, 5, figsize=(20, 10))
axes = axes.flatten()
for i, pais in enumerate(lista_top10):
    ax = axes[i]
    df_pais = df_junto[df_junto['pais'] == pais]
    ufs = df_pais.groupby('uf').size().reset_index(name='Quantidade')
    total = ufs['Quantidade'].sum()
    ufs['Percentual'] = (ufs['Quantidade'] / total) * 100
    gdf_pais = gdf.merge(ufs, left_on='sigla', right_on='uf', how='left')
    gdf_pais['Percentual'] = gdf_pais['Percentual'].fillna(0)
    gdf_pais.plot(column='Percentual', ax=ax, cmap='Reds',
                  vmin=0, vmax=ufs['Percentual'].max() if not ufs.empty else 0,
                  edgecolor='black', linewidth=0.3)
    formatted_pais = format_paises.get(pais, pais)
    ax.set_title(f'{formatted_pais}')
    ax.axis('off')
    for _, row in gdf_pais.iterrows():
        centroid = row.geometry.centroid
        area = row.geometry.area
        fontsize = 8 if area > 1e10 else 6
        x, y = centroid.x, centroid.y
        if row['sigla'] == 'DF':
            x += 0.5e6
        bbox = dict(boxstyle="round,pad=0.1", facecolor="white", edgecolor="none")
        ax.annotate(row['sigla'], (x, y), ha='center', va='center', fontsize=fontsize, color='black', fontweight='bold', bbox=bbox)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="2%", pad=0.05)
    sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize(vmin=0, vmax=ufs['Percentual'].max() if not ufs.empty else 0))
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cax, orientation='horizontal')
    cbar.set_label('Percentage (%)', fontsize=6)
    cbar.ax.tick_params(labelsize=5)
plt.tight_layout()
fig.suptitle('Distribution of hospital admissions of foreign nationals across Brazilian states in the Unified Health System (SUS), 2019 to August 2025', fontsize=16, y=0.98)
plt.subplots_adjust(top=0.88, bottom=0.1, hspace=0.3)
fig.text(0.5, 0.02, 'Source: SIH/SUS - Hospital Information System of SUS.', ha='center', fontsize=10)
plt.savefig('mapas_top10_grid_en.png', dpi=300, bbox_inches='tight')
print("Maps saved in mapas_top10_grid_en.png")