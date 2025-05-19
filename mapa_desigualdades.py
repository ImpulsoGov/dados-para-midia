import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import webbrowser

# Carregar os arquivos Excel
df_prenatal_2022 = pd.read_excel("prenatal2022.xlsx")
df_prenatal_2023 = pd.read_excel("prenatal2023.xlsx")
df_ultrassom_2022 = pd.read_excel("ultrassom2022.xlsx")
df_ultrassom_2023 = pd.read_excel("ultrassom 2023.xlsx")  # ou renomeie para evitar o espaço

custom_palette = {
    2022: "#1F7A99",  # azul para 2022
    2023: "#E95F3A"   # laranja para 2023
}

# Função para calcular coberturas
def calcular_cobertura(df_prenatal, df_ultrassom, ano):
    df = df_prenatal[["DSEI_GESTAO", "Nº GESTANTES", "6 OU MAIS CONSULTAS"]].copy()
    df.columns = ["DSEI", "gestantes", "consultas_6mais"]
    df["cobertura_prenatal"] = df["consultas_6mais"] / df["gestantes"] * 100

    df_us = df_ultrassom[["DSEI_GESTAO", "Nº GESTANTES", "COM ACESSO AO EXAME DE ULTRASSOM"]].copy()
    df_us.columns = ["DSEI", "gestantes_us", "ultrassons"]
    df_us["cobertura_ultrassom"] = df_us["ultrassons"] / df_us["gestantes_us"] * 100

    df_merged = pd.merge(df, df_us[["DSEI", "cobertura_ultrassom"]], on="DSEI", how="left")
    df_merged["ano"] = ano
    return df_merged

# Calcular coberturas para cada ano e unir os dados
df_2022 = calcular_cobertura(df_prenatal_2022, df_ultrassom_2022, 2022)
df_2023 = calcular_cobertura(df_prenatal_2023, df_ultrassom_2023, 2023)
df_combined = pd.concat([df_2022, df_2023], ignore_index=True)


# Mapeamento de DSEIs para regiões do Brasil
regioes_dsei = {
    "ALAGOAS E SERGIPE": "Nordeste", "ALTAMIRA": "Norte", "ALTO RIO JURUÁ": "Norte",
    "ALTO RIO NEGRO": "Norte", "ALTO RIO SOLIMÕES": "Norte", "AMANÃ": "Norte",
    "AMAPÁ E NORTE DO PARÁ": "Norte", "ARAGUAIA": "Centro-Oeste", "BAHIA": "Nordeste",
    "CEARÁ": "Nordeste", "CUIABÁ": "Centro-Oeste", "GUAMÁ-TOCANTINS": "Norte",
    "INTERIOR SUL": "Sul", "KAIAPÓ DO PARÁ": "Norte", "KAIAPÓ DO MATO GROSSO": "Centro-Oeste",
    "LITORAL SUL": "Sul", "MANAUS": "Norte", "MATO GROSSO DO SUL": "Centro-Oeste",
    "MÉDIO RIO PURUS": "Norte", "MÉDIO RIO SOLIMÕES E AFLUENTES": "Norte",
    "MINAS GERAIS E ESPÍRITO SANTO": "Sudeste", "PARINTINS": "Norte",
    "PERNAMBUCO": "Nordeste", "PORTO VELHO": "Norte", "POTIGUARA": "Nordeste",
    "RIO TAPAJÓS": "Norte", "TOCANTINS": "Norte", "VALE DO JURUA": "Norte",
    "VILHENA": "Norte", "XAVANTE": "Centro-Oeste", "XINGU": "Centro-Oeste",
    "YANOMAMI": "Norte", "LESTE DE RORAIMA": "Norte"
}
df_combined["regiao"] = df_combined["DSEI"].map(regioes_dsei)

# Adicionar coordenadas geográficas aos DSEIs
coordenadas_dsei = {
    "ALAGOAS E SERGIPE": (-10.9, -37.1), "ALTAMIRA": (-3.2, -52.2), "ALTO RIO JURUÁ": (-7.6, -72.7),
    "ALTO RIO NEGRO": (0.6, -65.0), "ALTO RIO SOLIMÕES": (-3.5, -68.7), "AMANÃ": (-2.5, -63.1),
    "AMAPÁ E NORTE DO PARÁ": (1.4, -52.0), "ARAGUAIA": (-12.0, -51.8), "BAHIA": (-12.9, -38.5),
    "CEARÁ": (-4.3, -38.9), "CUIABÁ": (-15.6, -56.1), "GUAMÁ-TOCANTINS": (-1.7, -47.9),
    "INTERIOR SUL": (-29.9, -50.3), "KAIAPÓ DO PARÁ": (-5.3, -51.2), "KAIAPÓ DO MATO GROSSO": (-10.0, -53.0),
    "LITORAL SUL": (-27.6, -48.6), "MANAUS": (-3.1, -60.0), "MATO GROSSO DO SUL": (-20.4, -54.6),
    "MÉDIO RIO PURUS": (-7.7, -64.9), "MÉDIO RIO SOLIMÕES E AFLUENTES": (-3.6, -65.1),
    "MINAS GERAIS E ESPÍRITO SANTO": (-18.8, -41.9), "PARINTINS": (-2.6, -56.0),
    "PERNAMBUCO": (-8.0, -34.9), "PORTO VELHO": (-8.8, -63.9), "POTIGUARA": (-6.6, -34.9),
    "RIO TAPAJÓS": (-4.2, -55.0), "TOCANTINS": (-10.2, -48.3), "VALE DO JURUA": (-7.6, -72.5),
    "VILHENA": (-12.7, -60.1), "XAVANTE": (-14.5, -52.2), "XINGU": (-11.0, -52.0),
    "YANOMAMI": (3.2, -64.7), "LESTE DE RORAIMA": (2.8, -60.7)
}
df_combined["latitude"] = df_combined["DSEI"].map(lambda x: coordenadas_dsei.get(x, (None, None))[0])
df_combined["longitude"] = df_combined["DSEI"].map(lambda x: coordenadas_dsei.get(x, (None, None))[1])

# Agrupar dados por região e ano
df_grouped = df_combined.groupby(["regiao", "ano"])[["cobertura_prenatal", "cobertura_ultrassom"]].mean().reset_index()
print(df_grouped)

# Gráficos comparativos
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.barplot(data=df_grouped, x="regiao", y="cobertura_prenatal", hue="ano", palette=custom_palette)
plt.title("Cobertura Pré-Natal (6 ou mais consultas)")
plt.ylabel("Cobertura (%)")
plt.xlabel("Região")
plt.xticks(rotation=45)

plt.subplot(1, 2, 2)
sns.barplot(data=df_grouped, x="regiao", y="cobertura_ultrassom", hue="ano", palette=custom_palette)
plt.title("Cobertura de Ultrassom")
plt.ylabel("Cobertura (%)")
plt.xlabel("Região")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


# Mapa Interativo dos DSEIs (2023)
mapa = folium.Map(location=[-10, -55], zoom_start=4)

for _, row in df_combined[df_combined["ano"] == 2023].iterrows():
    if pd.notnull(row["latitude"]) and pd.notnull(row["longitude"]):
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6,
            fill=True,
            fill_opacity=0.7,
            color="blue",
            popup=folium.Popup(
                f"<b>{row['DSEI']}</b><br>Região: {row['regiao']}<br>"
                f"Pré-natal: {row['cobertura_prenatal']:.1f}%<br>"
                f"Ultrassom: {row['cobertura_ultrassom']:.1f}%", max_width=300
            )
        ).add_to(mapa)

mapa.save("mapa_dsei_cobertura.html")
print("Mapa salvo como mapa_dsei_cobertura.html")
webbrowser.open("mapa_dsei_cobertura.html")