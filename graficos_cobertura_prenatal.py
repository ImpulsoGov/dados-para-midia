"""
Visualização de Dados de Cobertura de Pré-Natal para Mulheres Indígenas (2022-2023)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

COLORS = {
    'good': '#2EB886',
    'accent': '#FF5A5F',
    'neutral': '#767676'
}
seq_orange = ['#FFBE7D', '#FD8D3C', '#E65100', '#A63603']

def carregar_dados_prenatal():
    try:
        prenatal_2022 = pd.read_excel("prenatal2022.xlsx")
        prenatal_2023 = pd.read_excel("prenatal2023.xlsx")
        prenatal_2022['ano'] = 2022
        prenatal_2023['ano'] = 2023
        df_prenatal = pd.concat([prenatal_2022, prenatal_2023], ignore_index=True)
        df_prenatal = clean_column_names(df_prenatal)
        print("Dados de pré-natal carregados com sucesso!")
        return df_prenatal
    except Exception as e:
        print(f"Erro ao carregar os dados de pré-natal: {e}")
        return None

def clean_column_names(df):
    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.lower()
    df_clean.columns = df_clean.columns.str.replace(' ', '_')
    df_clean.columns = df_clean.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    return df_clean

def gerar_resumo_estatistico(df):
    dsei_col = [col for col in df.columns if 'dsei' in col.lower()][0]
    gestantes_col = [col for col in df.columns if 'gestante' in col.lower()][0]
    consultas_col = [col for col in df.columns if '6_ou_mais' in col.lower() or '≥6' in col.lower()][0]
    ano_col = [col for col in df.columns if 'ano' in col.lower()][0]

    grouped = df.groupby(ano_col).agg({
        gestantes_col: 'sum',
        consultas_col: 'sum'
    }).reset_index()

    grouped['cobertura'] = grouped[consultas_col] / grouped[gestantes_col]
    grouped['média'] = grouped['cobertura'].apply(lambda x: f"{x:.1%}")
    return grouped[[ano_col, 'média']]

def plot_cobertura_prenatal(df_prenatal, ano, tipo='top', salvar=False):
    """
    Plota os 5 DSEIs com maior OU menor cobertura de pré-natal para um ano específico.
    
    Parâmetros:
    - df_prenatal: DataFrame com os dados.
    - ano: 2022 ou 2023.
    - tipo: 'top' para os 5 com maior cobertura, 'bottom' para os 5 com menor.
    - salvar: se True, salva o gráfico como PNG.
    """
    dsei_col = [col for col in df_prenatal.columns if 'dsei' in col.lower()][0]
    gestantes_col = [col for col in df_prenatal.columns if 'gestante' in col.lower()][0]
    consultas_col = [col for col in df_prenatal.columns if '6_ou_mais' in col.lower() or '≥6' in col.lower()][0]
    ano_col = [col for col in df_prenatal.columns if 'ano' in col.lower()][0]

    df_filtrado = df_prenatal[df_prenatal[ano_col] == ano]
    grouped = df_filtrado.groupby(dsei_col).agg({
        gestantes_col: 'sum',
        consultas_col: 'sum'
    }).reset_index()
    grouped['cobertura'] = grouped[consultas_col] / grouped[gestantes_col]

    if tipo == 'top':
        df_final = grouped.sort_values('cobertura', ascending=False).head(5)
        cor = COLORS['good']
        titulo = f"Top 5 DSEIs com Maior Cobertura de Pré-Natal ({ano})"
    elif tipo == 'bottom':
        df_final = grouped.sort_values('cobertura', ascending=True).head(5)
        cor = seq_orange[2]
        titulo = f"Top 5 DSEIs com Menor Cobertura de Pré-Natal ({ano})"
    else:
        raise ValueError("O parâmetro 'tipo' deve ser 'top' ou 'bottom'.")

    # Plot
    plt.figure(figsize=(14, 7))
    sns.barplot(data=df_final, x='cobertura', y=dsei_col, color=cor)
    plt.axvline(x=0.45, color=COLORS['accent'], linestyle='--', linewidth=2, label='Meta Nacional (45%)')
    plt.xlabel("Cobertura de Pré-Natal (6 ou mais consultas por gestante)")
    plt.ylabel("Distrito Sanitário Especial Indígena")
    plt.title(titulo, fontsize=14, weight='bold')
    plt.xticks(ticks=[0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0],
               labels=["0%", "10%", "20%", "30%", "45% (Meta)", "60%", "80%", "100%"])
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    plt.xlim(0, 1)
    plt.legend(loc='lower right', fontsize=10)
    plt.tight_layout()

    if salvar:
        nome_arquivo = f"{tipo}_cobertura_prenatal_{ano}.png"
        plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo como {nome_arquivo}")

    plt.show()

def plot_comparativo_cobertura(df_prenatal, tipo='top', salvar=False):
    """
    Plota gráfico comparando 2022 e 2023 para os 5 DSEIs com maior ou menor cobertura.

    Parâmetros:
    - df_prenatal: DataFrame com os dados.
    - tipo: 'top' para maiores coberturas, 'bottom' para menores.
    - salvar: se True, salva o gráfico.
    """
    dsei_col = [col for col in df_prenatal.columns if 'dsei' in col.lower()][0]
    gestantes_col = [col for col in df_prenatal.columns if 'gestante' in col.lower()][0]
    consultas_col = [col for col in df_prenatal.columns if '6_ou_mais' in col.lower() or '≥6' in col.lower()][0]
    ano_col = [col for col in df_prenatal.columns if 'ano' in col.lower()][0]

    df_agrupado = df_prenatal.groupby([dsei_col, ano_col]).agg({
        gestantes_col: 'sum',
        consultas_col: 'sum'
    }).reset_index()
    df_agrupado['cobertura'] = df_agrupado[consultas_col] / df_agrupado[gestantes_col]

    # Pivota para seleção dos top/bottom
    df_pivot = df_agrupado.pivot(index=dsei_col, columns=ano_col, values='cobertura').reset_index()
    df_pivot = df_pivot.dropna()

    if tipo == 'top':
        selecionados = df_pivot.sort_values(by=2023, ascending=False).head(5)[dsei_col]
        titulo = "Top 5 DSEIs com Maior Cobertura de Pré-Natal (2022 e 2023)"
        cor = COLORS['good']
    elif tipo == 'bottom':
        selecionados = df_pivot.sort_values(by=2023, ascending=True).head(5)[dsei_col]
        titulo = "Top 5 DSEIs com Menor Cobertura de Pré-Natal (2022 e 2023)"
        cor = seq_orange[2]
    else:
        raise ValueError("tipo deve ser 'top' ou 'bottom'.")

    df_plot = df_agrupado[df_agrupado[dsei_col].isin(selecionados)]

    # Gráfico
    plt.figure(figsize=(14, 7))
    sns.barplot(data=df_plot, x='cobertura', y=dsei_col, hue=ano_col, palette=[cor, '#114354'])
    plt.axvline(x=0.45, color=COLORS['accent'], linestyle='--', linewidth=2, label="Meta Nacional (45%)")
    plt.xlabel("Cobertura de Pré-Natal (6 ou mais consultas por gestante)")
    plt.ylabel("Distrito Sanitário Especial Indígena")
    plt.title(titulo, fontsize=14, weight='bold')
    plt.xticks(ticks=[0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.8, 1.0],
               labels=["0%", "10%", "20%", "30%", "45% (Meta)", "60%", "80%", "100%"])
    plt.xlim(0, 1)
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    plt.legend(title="Ano", loc='lower right')
    plt.tight_layout()

    if salvar:
        nome = f"{tipo}_comparativo_cobertura_2022_2023.png"
        plt.savefig(nome, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo como {nome}")

    plt.show()


def comparar_evolucao_cobertura(df_prenatal):
    dsei_col = [col for col in df_prenatal.columns if 'dsei' in col.lower()][0]
    gestantes_col = [col for col in df_prenatal.columns if 'gestante' in col.lower()][0]
    consultas_col = [col for col in df_prenatal.columns if '6_ou_mais' in col.lower() or '≥6' in col.lower()][0]
    ano_col = [col for col in df_prenatal.columns if 'ano' in col.lower()][0]

    grouped = df_prenatal.groupby([dsei_col, ano_col]).agg({
        gestantes_col: 'sum',
        consultas_col: 'sum'
    }).reset_index()
    grouped['cobertura'] = grouped[consultas_col] / grouped[gestantes_col]

    pivot_df = grouped.pivot(index=dsei_col, columns=ano_col, values='cobertura').reset_index()
    pivot_df.columns.name = None

    if 2022 in pivot_df.columns and 2023 in pivot_df.columns:
        pivot_df = pivot_df.dropna(subset=[2022, 2023])
        pivot_df['variacao'] = ((pivot_df[2023] - pivot_df[2022]) / pivot_df[2022]) * 100  # variação relativa (%)
        destaque_dseis = pivot_df.sort_values(by='variacao', ascending=False)

        # GRÁFICO 1: Variação Percentual (%)
        plt.figure(figsize=(12, 18))
        colors = ['#2EB886' if x > 0 else '#FF5A5F' for x in destaque_dseis['variacao']]
        sns.barplot(data=destaque_dseis, x='variacao', y=dsei_col, palette=colors)
        plt.axvline(x=0, color='black', linestyle='--', linewidth=1)
        plt.title("Variação Percentual da Cobertura de Pré-Natal por DSEI (2022–2023)", fontsize=16, weight='bold', pad=20)
        plt.xlabel("Variação Percentual da Cobertura (%)")
        plt.ylabel("Distritot")
        plt.xlim(-100, 150)
        plt.xticks(
         ticks=range(-100, 151, 25),
        labels=[f"{i}%" for i in range(-100, 151, 25)]
        )
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        plt.tight_layout()
        plt.savefig("variacao_percentual_por_dsei_2022_2023.png", dpi=300, bbox_inches='tight')
        plt.show()

        # GRÁFICO 2: Evolução da Cobertura (10 maiores aumentos)
        top_10_dseis = destaque_dseis.sort_values(by='variacao', ascending=False).head(10)

        melt_df = top_10_dseis.melt(
            id_vars=[dsei_col],
            value_vars=[2022, 2023],
            var_name='Ano',
            value_name='Cobertura'
        )
        melt_df['Ano'] = melt_df['Ano'].astype(int)

        plt.figure(figsize=(14, 8))
        sns.lineplot(
            data=melt_df,
            x='Ano',
            y='Cobertura',
            hue=dsei_col,
            palette='tab10',
            marker='o',
            linewidth=2
        )

        for dsei in top_10_dseis[dsei_col]:
            dsei_data = melt_df[melt_df[dsei_col] == dsei]
            for _, row in dsei_data.iterrows():
                plt.text(
                    row['Ano'],
                    row['Cobertura'] + 0.02,
                    f"{row['Cobertura']:.2f}",
                    ha='center',
                    fontsize=9
                )

        plt.axhline(y=0.45, color='#FF5A5F', linestyle='--', linewidth=2, label='Meta Nacional (45%)')
        plt.title("Evolução da Cobertura de Pré-Natal (2022–2023)", fontsize=15, weight='bold', pad=15)
        plt.xlabel("Ano", fontsize=12)
        plt.ylabel("Cobertura de Pré-Natal", fontsize=12)
        plt.xticks([2022, 2023], fontsize=11)
        plt.yticks(fontsize=11)
        plt.ylim(0, 1.0)
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.legend(title="DSEI", bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9, title_fontsize=10)
        plt.tight_layout()
        plt.savefig("evolucao_top10_cobertura_dsei_2022_2023.png", dpi=300, bbox_inches='tight')
        plt.show()

def visualizar_todos_graficos():
    df_prenatal = carregar_dados_prenatal()
    if df_prenatal is not None:
        print("\n=== Resumo Estatístico da Cobertura de Pré-Natal ===")
        resumo = gerar_resumo_estatistico(df_prenatal)
        print(resumo)

        if '2022' in resumo.iloc[:, 0].values and '2023' in resumo.iloc[:, 0].values:
            media_2022 = float(resumo[resumo.iloc[:, 0] == 2022]['média'].iloc[0].strip('%')) / 100
            media_2023 = float(resumo[resumo.iloc[:, 0] == 2023]['média'].iloc[0].strip('%')) / 100
            variacao = media_2023 - media_2022
            print(f"\n- Houve uma {'melhora' if variacao > 0 else 'redução'} de {abs(variacao):.1%} na média de cobertura entre 2022 e 2023")

        print("\nGerando gráficos separados por ano:")
        for ano in [2022, 2023]:
            print(f" - Top 5 {ano}")
            plot_cobertura_prenatal(df_prenatal, ano=ano, tipo='top', salvar=True)

            print(f" - Bottom 5 {ano}")
            plot_cobertura_prenatal(df_prenatal, ano=ano, tipo='bottom', salvar=True)

        print("\nGerando gráfico combinado (2022–2023)...")
        plot_comparativo_cobertura(df_prenatal, tipo='top', salvar=True)
        plot_comparativo_cobertura(df_prenatal, tipo='bottom', salvar=True)

        print("Gerando gráficos de evolução...")
        comparar_evolucao_cobertura(df_prenatal)
        print("\nTodos os gráficos foram gerados com sucesso!")
    else:
        print("Erro no carregamento de dados.")

if __name__ == "__main__":
    visualizar_todos_graficos()