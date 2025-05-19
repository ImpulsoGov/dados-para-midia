import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cores personalizadas
ULTRA_COLOR = "#E95F3A"
PRENATAL_COLOR = "#1F7A99"

# Função para identificar colunas por padrão
def find_column(df, patterns):
    for pattern in patterns:
        matching_cols = [col for col in df.columns if pattern.lower() in str(col).lower()]
        if matching_cols:
            return matching_cols[0]
    return None

# Processar dados de pré-natal
def process_prenatal_data(df):
    dsei_col = find_column(df, ['dsei', 'dsei_gestao'])
    gestantes_col = find_column(df, ['gestante', 'nº gestantes'])
    consultas_col = find_column(df, ['6 ou mais', '6_ou_mais', '≥6'])

    grouped = df.groupby(dsei_col).agg({
        gestantes_col: 'sum',
        consultas_col: 'sum'
    }).reset_index()

    grouped['cobertura'] = grouped[consultas_col] / grouped[gestantes_col]
    grouped['cobertura'] = grouped['cobertura'].fillna(0)
    grouped['categoria'] = 'Pré-Natal (≥6 consultas)'
    grouped.rename(columns={dsei_col: 'dsei'}, inplace=True)
    return grouped

# Processar dados de ultrassom
def process_ultrassom_data(df):
    dsei_col = find_column(df, ['dsei', 'dsei_gestao'])
    gestantes_col = find_column(df, ['gestante', 'nº gestantes'])
    ultrassom_col = find_column(df, ['ultrassom', 'acesso ao exame'])

    grouped = df.groupby(dsei_col).agg({
        gestantes_col: 'sum',
        ultrassom_col: 'sum'
    }).reset_index()

    grouped['cobertura'] = grouped[ultrassom_col] / grouped[gestantes_col]
    grouped['cobertura'] = grouped['cobertura'].fillna(0)
    grouped['categoria'] = 'Ultrassonografia'
    grouped.rename(columns={dsei_col: 'dsei'}, inplace=True)
    return grouped

# Gráfico de barras sem linha de meta
def plot_gap_graph(df_combined, year_label):
    plt.figure(figsize=(14, 7))
    sns.barplot(
        data=df_combined,
        x='cobertura',
        y='dsei',
        hue='categoria',
        palette=[PRENATAL_COLOR, ULTRA_COLOR]
    )
    plt.xlabel("Cobertura (%)")
    plt.ylabel("DSEI")
    plt.title(f"Cobertura de Pré-Natal e Ultrassonografia Para Mulheres Indígenas ({year_label})", fontsize=14)
    plt.xticks(
        ticks=[0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0],
        labels=["0%", "10%", "20%", "30%", "45%", "60%", "80%", "100%"]
    )
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    plt.xlim(0, 1)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(f"grafico_{year_label}.png")
    plt.show()

# Gerar gráfico para um ano específico
def generate_graph(df_prenatal, df_ultrassom, year_label):
    prenatal_data = process_prenatal_data(df_prenatal)
    ultrassom_data = process_ultrassom_data(df_ultrassom)

    top5_prenatal = prenatal_data.sort_values('cobertura', ascending=False).head(5)
    top5_ultrassom = ultrassom_data.sort_values('cobertura', ascending=False).head(5)

    combined_data = pd.concat([top5_prenatal, top5_ultrassom])
    plot_gap_graph(combined_data, year_label)
    return combined_data

# Caminhos dos arquivos (ajuste conforme necessário)
paths = {
    "prenatal2022": "prenatal2022.xlsx",
    "ultrassom2022": "ultrassom2022.xlsx",
    "prenatal2023": "prenatal2023.xlsx",
    "ultrassom2023": "ultrassom 2023.xlsx"
}

# Carregar arquivos
df_prenatal_2022 = pd.read_excel(paths["prenatal2022"])
df_ultrassom_2022 = pd.read_excel(paths["ultrassom2022"])
df_prenatal_2023 = pd.read_excel(paths["prenatal2023"])
df_ultrassom_2023 = pd.read_excel(paths["ultrassom2023"])

# Gerar gráficos
generate_graph(df_prenatal_2022, df_ultrassom_2022, "2022")
generate_graph(df_prenatal_2023, df_ultrassom_2023, "2023")
