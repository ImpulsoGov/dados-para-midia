import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Define colors
COLORS = {
    'primary': '#1F7A99',    # Azul
    'secondary': '#2EA6BC',  # Azul claro
    'accent': '#E95F3A',     # Laranja
    'dark': '#114354',       # Azul escuro
    'light': '#81CBD3',      # Azul muito claro
    'highlight': '#EF8264',  # Laranja claro
    'good': '#2EB280',       # Verde
    'bad': '#EF565D'         # Vermelho
}

# Configure plot style
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.family'] = 'Arial'

def ultrassom_coverage_analysis():
    """Análise específica para cobertura de ultrassom em 2022"""
    print("Iniciando análise de cobertura de ultrassonografia (2022)...")

    try:
        # Carregar o arquivo de ultrassom
        df_ultrassom = pd.read_excel('ultrassom2022.xlsx')

        # Padronizar nomes das colunas
        df_ultrassom.columns = df_ultrassom.columns.str.strip().str.lower()

        # Renomear colunas conhecidas
        df_ultrassom = df_ultrassom.rename(columns={
            'dsei_gestao': 'dsei',
            'nº gestantes': 'gestantes',
            'com acesso ao exame de ultrassom': 'ultrassons'
        })

        # Converter colunas numéricas
        df_ultrassom['gestantes'] = pd.to_numeric(df_ultrassom['gestantes'], errors='coerce')
        df_ultrassom['ultrassons'] = pd.to_numeric(df_ultrassom['ultrassons'], errors='coerce')

        # Remover linhas inválidas
        df_ultrassom = df_ultrassom.dropna(subset=['dsei', 'gestantes', 'ultrassons'])
        df_ultrassom = df_ultrassom[df_ultrassom['gestantes'] > 0]

        # Calcular cobertura
        df_ultrassom['cobertura'] = df_ultrassom['ultrassons'] / df_ultrassom['gestantes']
        df_ultrassom['cobertura_percentual'] = df_ultrassom['cobertura'] * 100

        # Top 5 maiores e menores coberturas
        top5 = df_ultrassom.sort_values('cobertura', ascending=False).head(5)
        bottom5 = df_ultrassom.sort_values('cobertura').head(5)
        top5['categoria'] = 'Mais Cobertura'
        bottom5['categoria'] = 'Menos Cobertura'
        final_df = pd.concat([top5, bottom5])

        print("Dados para o gráfico:")
        print(final_df[['dsei', 'cobertura_percentual', 'categoria']])

        # Gráfico
        plt.figure(figsize=(14, 7))
        ax = sns.barplot(
            data=final_df,
            x='cobertura_percentual',
            y='dsei',
            hue='categoria',
            palette=[COLORS['good'], COLORS['bad']]
        )

        # Adicionar rótulos
        for i, row in enumerate(final_df.itertuples()):
            plt.text(
                row.cobertura_percentual + 1,
                i,
                f"{row.cobertura_percentual:.1f}%",
                va='center',
                fontsize=9
            )

        plt.xlabel("Cobertura de Ultrassonografia (por gestante)", fontsize=12)
        plt.ylabel("DSEI", fontsize=12)
        plt.title("Top 5 DSEIs Com Mais e Menos Cobertura de Ultrassonografia Para Mulheres Indígenas (2022)",
                  fontsize=14, weight='bold')
        plt.xticks(ticks=[0, 20, 40, 60, 80, 100], labels=["0%", "20%", "40%", "60%", "80%", "100%"])
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        plt.xlim(0, 105)
        plt.legend(loc='lower right', fontsize=10)
        plt.tight_layout()

        # Salvar gráfico
        plt.savefig('ultrassom_top5_coverage.png', dpi=300, bbox_inches='tight', facecolor='white')
        print("Gráfico salvo como 'ultrassom_top5_coverage.png'")
        plt.show()

        print("Análise de cobertura de ultrassonografia concluída com sucesso.")

    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

# Esta função deve estar no mesmo nível de indentação da função anterior
def ultrassom_coverage_analysis_2023():
    """Análise específica para cobertura de ultrassom em 2023"""
    print("Iniciando análise de cobertura de ultrassonografia (2023)...")

    try:
        # Carregar o arquivo de ultrassom 2023
        df_ultrassom = pd.read_excel('ultrassom 2023.xlsx')  # Note o espaço no nome do arquivo

        # Padronizar nomes das colunas
        df_ultrassom.columns = df_ultrassom.columns.str.strip().str.lower()

        # Mostrar as colunas disponíveis para diagnóstico
        print(f"Colunas disponíveis: {df_ultrassom.columns.tolist()}")

        # Renomear colunas conhecidas - ajuste os nomes se necessário
        column_mapping = {}
        for col in df_ultrassom.columns:
            if 'dsei' in col.lower() or 'distrito' in col.lower():
                column_mapping[col] = 'dsei'
            elif 'gestante' in col.lower():
                column_mapping[col] = 'gestantes'
            elif 'ultrassom' in col.lower() or 'acesso' in col.lower():
                column_mapping[col] = 'ultrassons'
        
        # Aplicar o mapeamento de colunas
        df_ultrassom = df_ultrassom.rename(columns=column_mapping)
        print(f"Colunas após renomeação: {df_ultrassom.columns.tolist()}")

        # Converter colunas numéricas
        df_ultrassom['gestantes'] = pd.to_numeric(df_ultrassom['gestantes'], errors='coerce')
        df_ultrassom['ultrassons'] = pd.to_numeric(df_ultrassom['ultrassons'], errors='coerce')

        # Remover linhas inválidas
        df_ultrassom = df_ultrassom.dropna(subset=['dsei', 'gestantes', 'ultrassons'])
        df_ultrassom = df_ultrassom[df_ultrassom['gestantes'] > 0]
        print(f"Registros válidos após filtragem: {len(df_ultrassom)}")

        # Calcular cobertura
        df_ultrassom['cobertura'] = df_ultrassom['ultrassons'] / df_ultrassom['gestantes']
        df_ultrassom['cobertura_percentual'] = df_ultrassom['cobertura'] * 100
        
        print(f"Cobertura média: {df_ultrassom['cobertura'].mean():.2%}")
        print(f"Cobertura máxima: {df_ultrassom['cobertura'].max():.2%}")
        print(f"Cobertura mínima: {df_ultrassom['cobertura'].min():.2%}")

        # Top 5 maiores e menores coberturas
        top5 = df_ultrassom.sort_values('cobertura', ascending=False).head(5)
        bottom5 = df_ultrassom.sort_values('cobertura').head(5)
        top5['categoria'] = 'Mais Cobertura'
        bottom5['categoria'] = 'Menos Cobertura'
        final_df = pd.concat([top5, bottom5])

        print("Dados para o gráfico:")
        print(final_df[['dsei', 'cobertura_percentual', 'categoria']])

        # Gráfico
        plt.figure(figsize=(14, 7))
        ax = sns.barplot(
            data=final_df,
            x='cobertura_percentual',
            y='dsei',
            hue='categoria',
            palette=[COLORS['good'], COLORS['bad']]
        )

        # Adicionar rótulos
        for i, row in enumerate(final_df.itertuples()):
            plt.text(
                row.cobertura_percentual + 1,
                i,
                f"{row.cobertura_percentual:.1f}%",
                va='center',
                fontsize=9
            )

        plt.xlabel("Cobertura de Ultrassonografia (por gestante)", fontsize=12)
        plt.ylabel("DSEI", fontsize=12)
        plt.title("Top 5 DSEIs Com Mais e Menos Cobertura de Ultrassonografia Para Mulheres Indígenas (2023)",
                  fontsize=14, weight='bold')
        plt.xticks(ticks=[0, 20, 40, 60, 80, 100], labels=["0%", "20%", "40%", "60%", "80%", "100%"])
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        plt.xlim(0, 105)
        plt.legend(loc='lower right', fontsize=10)
        plt.tight_layout()

        # Salvar gráfico
        plt.savefig('ultrassom_top5_coverage_2023.png', dpi=300, bbox_inches='tight', facecolor='white')
        print("Gráfico salvo como 'ultrassom_top5_coverage_2023.png'")
        
        # Exibir o gráfico
        plt.show()

        print("Análise de cobertura de ultrassonografia 2023 concluída com sucesso.")

    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

# Nova função para análise combinada de 2022-2023
def ultrassom_coverage_combined_2022_2023():
    """Análise combinada da cobertura de ultrassom para 2022-2023"""
    print("Iniciando análise combinada de cobertura de ultrassonografia (2022-2023)...")

    try:
        # Carregar o arquivo de ultrassom 2022
        df_2022 = pd.read_excel('ultrassom2022.xlsx')
        df_2022.columns = df_2022.columns.str.strip().str.lower()
        df_2022 = df_2022.rename(columns={
            'dsei_gestao': 'dsei',
            'nº gestantes': 'gestantes',
            'com acesso ao exame de ultrassom': 'ultrassons'
        })
        df_2022['gestantes'] = pd.to_numeric(df_2022['gestantes'], errors='coerce')
        df_2022['ultrassons'] = pd.to_numeric(df_2022['ultrassons'], errors='coerce')
        df_2022 = df_2022.dropna(subset=['dsei', 'gestantes', 'ultrassons'])
        df_2022 = df_2022[df_2022['gestantes'] > 0]
        df_2022['cobertura'] = df_2022['ultrassons'] / df_2022['gestantes']
        df_2022['cobertura_percentual'] = df_2022['cobertura'] * 100
        
        # Carregar o arquivo de ultrassom 2023
        df_2023 = pd.read_excel('ultrassom 2023.xlsx')
        df_2023.columns = df_2023.columns.str.strip().str.lower()
        column_mapping = {}
        for col in df_2023.columns:
            if 'dsei' in col.lower() or 'distrito' in col.lower():
                column_mapping[col] = 'dsei'
            elif 'gestante' in col.lower():
                column_mapping[col] = 'gestantes'
            elif 'ultrassom' in col.lower() or 'acesso' in col.lower():
                column_mapping[col] = 'ultrassons'
        df_2023 = df_2023.rename(columns=column_mapping)
        df_2023['gestantes'] = pd.to_numeric(df_2023['gestantes'], errors='coerce')
        df_2023['ultrassons'] = pd.to_numeric(df_2023['ultrassons'], errors='coerce')
        df_2023 = df_2023.dropna(subset=['dsei', 'gestantes', 'ultrassons'])
        df_2023 = df_2023[df_2023['gestantes'] > 0]
        df_2023['cobertura'] = df_2023['ultrassons'] / df_2023['gestantes']
        df_2023['cobertura_percentual'] = df_2023['cobertura'] * 100
        
        # Combinar os dois DataFrames
        df_combined = pd.concat([
            df_2022[['dsei', 'cobertura', 'cobertura_percentual']],
            df_2023[['dsei', 'cobertura', 'cobertura_percentual']]
        ])
        
        # Calcular a média da cobertura por DSEI
        df_avg = df_combined.groupby('dsei')['cobertura_percentual'].mean().reset_index()
        
        # Top 5 maiores e menores coberturas
        top5 = df_avg.sort_values('cobertura_percentual', ascending=False).head(5)
        bottom5 = df_avg.sort_values('cobertura_percentual', ascending=True).head(5)
        top5['categoria'] = 'Mais Cobertura'
        bottom5['categoria'] = 'Menos Cobertura'
        final_df = pd.concat([top5, bottom5])
        
        print("Dados para o gráfico combinado (2022-2023):")
        print(final_df[['dsei', 'cobertura_percentual', 'categoria']])
        
        # Gráfico no mesmo estilo dos outros
        plt.figure(figsize=(14, 7))
        ax = sns.barplot(
            data=final_df,
            x='cobertura_percentual',
            y='dsei',
            hue='categoria',
            palette=[COLORS['good'], COLORS['bad']]
        )
        
        # Adicionar rótulos
        for i, row in enumerate(final_df.itertuples()):
            plt.text(
                row.cobertura_percentual + 1,
                i,
                f"{row.cobertura_percentual:.1f}%",
                va='center',
                fontsize=9
            )
        
        plt.xlabel("Cobertura de Ultrassonografia (por gestante)", fontsize=12)
        plt.ylabel("DSEI", fontsize=12)
        plt.title("Top 5 DSEIs Com Mais e Menos Cobertura de Ultrassonografia Para Mulheres Indígenas (2022–2023)",
                 fontsize=14, weight='bold')
        plt.xticks(ticks=[0, 20, 40, 60, 80, 100], labels=["0%", "20%", "40%", "60%", "80%", "100%"])
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        plt.xlim(0, 105)
        plt.legend(loc='lower right', fontsize=10)
        plt.tight_layout()
        
        # Salvar gráfico
        plt.savefig('ultrassom_top5_coverage_2022_2023.png', dpi=300, bbox_inches='tight', facecolor='white')
        print("Gráfico salvo como 'ultrassom_top5_coverage_2022_2023.png'")
        
        # Exibir o gráfico
        plt.show()
        
        print("Análise combinada de cobertura de ultrassonografia concluída com sucesso.")
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

# Executar 
if __name__ == "__main__":
    ultrassom_coverage_analysis()  # Análise para 2022
    ultrassom_coverage_analysis_2023()  # Análise para 2023
    ultrassom_coverage_combined_2022_2023()  # Análise combinada para 2022-2023
