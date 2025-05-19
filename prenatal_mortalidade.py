import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Leitura dos dados
prenatal_2022 = pd.read_excel("prenatal2022.xlsx")
prenatal_2023 = pd.read_excel("prenatal2023.xlsx")
obitos_2022 = pd.read_excel("obitos 2022.xlsx", skiprows=3)
obitos_2023 = pd.read_excel("obitos 2023.xlsx", skiprows=3)

# Padronização e limpeza
prenatal_2022.columns = prenatal_2022.columns.str.strip()
prenatal_2023.columns = prenatal_2023.columns.str.strip()
prenatal_2022 = prenatal_2022.dropna(subset=["DSEI_GESTAO"])
prenatal_2023 = prenatal_2023.dropna(subset=["DSEI_GESTAO"])

# Agrupamento dos dados de pré-natal
prenatal = pd.concat([prenatal_2022, prenatal_2023])
prenatal_grouped = prenatal.groupby("DSEI_GESTAO").agg({
    "Nº GESTANTES": "sum",
    "6 OU MAIS CONSULTAS": "sum"
}).reset_index()
prenatal_grouped["Cobertura Pré-Natal (%)"] = (
    prenatal_grouped["6 OU MAIS CONSULTAS"] / prenatal_grouped["Nº GESTANTES"]
) * 100

# Processamento dos dados de óbitos
obitos = pd.concat([obitos_2022, obitos_2023])
obitos.columns = ["DSEI", "NASCIDOS VIVOS", "ÓBITOS MATERNOS", "ÓBITOS INFANTIS"]
obitos_grouped = obitos.groupby("DSEI").agg({
    "NASCIDOS VIVOS": "sum",
    "ÓBITOS INFANTIS": "sum"
}).reset_index()

# Taxa de sobrevivência e mortalidade por 1.000
obitos_grouped["Sobrevivência (por mil)"] = (
    (obitos_grouped["NASCIDOS VIVOS"] - obitos_grouped["ÓBITOS INFANTIS"]) / obitos_grouped["NASCIDOS VIVOS"]
) * 1000
obitos_grouped["Mortalidade Infantil (por mil)"] = (
    obitos_grouped["ÓBITOS INFANTIS"] / obitos_grouped["NASCIDOS VIVOS"]
) * 1000

# Merge com pré-natal
df_full = pd.merge(prenatal_grouped, obitos_grouped, left_on="DSEI_GESTAO", right_on="DSEI")

# ---------- GRÁFICO 1: TOP 10 POR NASCIDOS VIVOS ----------
top10_nascidos = df_full.sort_values("NASCIDOS VIVOS", ascending=False).head(10)

plt.figure(figsize=(14, 8))
sns.set(style="whitegrid")
bar_width = 0.4
indices = range(len(top10_nascidos))

plt.barh(
    [i + bar_width for i in indices],
    top10_nascidos["Cobertura Pré-Natal (%)"],
    height=bar_width,
    label="Cobertura Percentual de Pré-Natal",
    color="#E95F3A"
)

plt.barh(
    indices,
    top10_nascidos["Sobrevivência (por mil)"],
    height=bar_width,
    label="Taxa de Nascidos Vivos que Sobreviveram (por 1.000)",
    color="#114354"
)

for i, (surv, pre) in enumerate(zip(top10_nascidos["Sobrevivência (por mil)"], top10_nascidos["Cobertura Pré-Natal (%)"])):
    plt.text(surv + 5, i, f"{surv:.1f}", va='center', fontsize=9)
    plt.text(pre + 1, i + bar_width, f"{pre:.1f}", va='center', fontsize=9)

plt.yticks([i + bar_width / 2 for i in indices], top10_nascidos["DSEI_GESTAO"])
plt.xlabel("Indicadores por 1.000 Nascidos Vivos")
plt.ylabel("Distrito")
plt.title("Top 10 Distritos com Maior Número de Nascidos Vivos (2022–2023)", fontsize=14, weight="bold")
plt.legend(title="Indicadores", loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2, frameon=False)
plt.subplots_adjust(top=0.82)
plt.savefig("grafico_top10_nascidos_vivos.png", dpi=300)
plt.show()

# ---------- GRÁFICO 2: TOP 10 POR TAXA DE MORTALIDADE ----------
top10_mortalidade = df_full.sort_values("Mortalidade Infantil (por mil)", ascending=False).head(10)

plt.figure(figsize=(14, 8))
indices = range(len(top10_mortalidade))

plt.barh(
    [i + bar_width for i in indices],
    top10_mortalidade["Cobertura Pré-Natal (%)"],
    height=bar_width,
    label="Cobertura Percentual de Pré-Natal",
    color="#E95F3A"
)

plt.barh(
    indices,
    top10_mortalidade["Mortalidade Infantil (por mil)"],
    height=bar_width,
    label="Taxa de Mortalidade Infantil (por 1.000)",
    color="#114354"
)

for i, (mort, pre) in enumerate(zip(top10_mortalidade["Mortalidade Infantil (por mil)"], top10_mortalidade["Cobertura Pré-Natal (%)"])):
    plt.text(mort + 1, i, f"{mort:.1f}", va='center', fontsize=9)
    plt.text(pre + 1, i + bar_width, f"{pre:.1f}", va='center', fontsize=9)

plt.yticks(
    [i + bar_width / 2 for i in indices],
    top10_mortalidade["DSEI"]
)
plt.xlabel("Indicadores por 1.000 Nascidos Vivos")
plt.ylabel("Distrito")
plt.title("Top 10 Distritos com Maior Taxa de Mortalidade Infantil (2022–2023)", fontsize=14, weight="bold")
plt.legend(title="Indicadores", loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2, frameon=False)
plt.subplots_adjust(top=0.82)
plt.savefig("grafico_top10_mortalidade.png", dpi=300)
plt.show()
