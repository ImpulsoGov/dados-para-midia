"""
Análise Comparativa de Cobertura de Pré-Natal e Ultrassonografia (2022-2023)

Este script realiza uma análise comparativa entre a cobertura de pré-natal (≥6 consultas) 
e a cobertura de ultrassonografia para gestantes indígenas nos diferentes Distritos 
Sanitários Especiais Indígenas (DSEIs) do Brasil.

O script:
1. Carrega dados de pré-natal e ultrassonografia de 2022 e 2023
2. Calcula as coberturas para cada DSEI
3. Identifica o "gap tecnológico" entre a cobertura de pré-natal e ultrassonografia
4. Gera visualizações comparativas ordenadas pelo gap

Interpretação do gap tecnológico:
- Um gap positivo indica DSEIs onde a cobertura de pré-natal é maior que a de ultrassonografia,
  sugerindo dificuldade de acesso a tecnologia de imagem
- Um gap negativo indica DSEIs onde há mais cobertura de ultrassonografia do que de 
  consultas de pré-natal completas, o que pode indicar priorização de tecnologia sobre 
  acompanhamento clínico contínuo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# Definição de cores para visualização
PRENATAL_COLOR = "#1F7A99"  # Azul para pré-natal
ULTRASSOM_COLOR = "#E95F3A"  # Laranja para ultrassom
COLORS = {
    'good': '#2EB886',      # Verde para indicadores positivos
    'accent': '#FF5A5F',    # Vermelho para linhas de destaque/metas
    'neutral': '#767676'    # Cinza para elementos neutros
}

def carregar_dados():
    """
    Carrega os dados de pré-natal e ultrassonografia dos arquivos Excel
    """
    try:
        # Carregando dados de pré-natal
        prenatal_2022 = pd.read_excel("prenatal2022.xlsx")
        prenatal_2023 = pd.read_excel("prenatal2023.xlsx")
        
        # Carregando dados de ultrassom
        ultrassom_2022 = pd.read_excel("ultrassom2022.xlsx")
        ultrassom_2023 = pd.read_excel("ultrassom 2023.xlsx")
        
        # Verifica se os dados foram carregados corretamente
        for df, nome in [(prenatal_2022, "Pré-natal 2022"), 
                         (prenatal_2023, "Pré-natal 2023"),
                         (ultrassom_2022, "Ultrassom 2022"),
                         (ultrassom_2023, "Ultrassom 2023")]:
            if df.empty:
                print(f"Aviso: DataFrame {nome} está vazio!")
        
        print("Dados carregados com sucesso!")
        return prenatal_2022, prenatal_2023, ultrassom_2022, ultrassom_2023
    
    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return None, None, None, None

def clean_column_names(df):
    """
    Padroniza os nomes das colunas, removendo espaços e convertendo para minúsculas
    """
    # Copia do DataFrame para não modificar o original
    df_clean = df.copy()
    
    # Converte todos os nomes de colunas para minúsculas e remove espaços extras
    df_clean.columns = df_clean.columns.str.strip().str.lower().str.replace(' ', '_')
    
    # Normaliza caracteres acentuados
    df_clean.columns = df_clean.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    
    return df_clean

def create_heatmap_comparison(prenatal_2022, prenatal_2023, ultrassom_2022, ultrassom_2023, salvar=False):
    """
    Cria gráfico de barras agrupadas com dados combinados de 2022 e 2023
    para comparar cobertura de pré-natal e ultrassonografia por DSEI,
    ordenado por gap tecnológico.
    """
    # Limpeza de colunas
    prenatal_2022 = clean_column_names(prenatal_2022)
    prenatal_2023 = clean_column_names(prenatal_2023)
    ultrassom_2022 = clean_column_names(ultrassom_2022)
    ultrassom_2023 = clean_column_names(ultrassom_2023)
    
    # Adiciona coluna de ano
    prenatal_2022["ano"] = 2022
    prenatal_2023["ano"] = 2023
    ultrassom_2022["ano"] = 2022
    ultrassom_2023["ano"] = 2023
    
    # Concatena os dataframes
    df_prenatal = pd.concat([prenatal_2022, prenatal_2023], ignore_index=True)
    df_ultrassom = pd.concat([ultrassom_2022, ultrassom_2023], ignore_index=True)
    
    # Identifica colunas
    dsei_col = [col for col in df_prenatal.columns if 'dsei' in col][0]
    gestantes_col = [col for col in df_prenatal.columns if 'gestante' in col][0]
    consultas_col = [col for col in df_prenatal.columns if '6_ou_mais' in col or '≥6' in col][0]
    
    ultrassom_gest_col = [col for col in df_ultrassom.columns if 'gestante' in col][0]
    ultrassons_col = [col for col in df_ultrassom.columns if 'ultrassom' in col or 'ultrassonografia' in col][0]
    
    # Agrupamento por DSEI
    prenatal_grouped = df_prenatal.groupby(dsei_col).agg({
        gestantes_col: 'sum',
        consultas_col: 'sum'
    }).reset_index()
    prenatal_grouped["cobertura_prenatal"] = prenatal_grouped[consultas_col] / prenatal_grouped[gestantes_col]
    
    ultrassom_grouped = df_ultrassom.groupby(dsei_col).agg({
        ultrassom_gest_col: 'sum',
        ultrassons_col: 'sum'
    }).reset_index()
    ultrassom_grouped["cobertura_ultrassom"] = ultrassom_grouped[ultrassons_col] / ultrassom_grouped[ultrassom_gest_col]
    
    # Merge
    df = prenatal_grouped[[dsei_col, "cobertura_prenatal"]].merge(
        ultrassom_grouped[[dsei_col, "cobertura_ultrassom"]],
        on=dsei_col
    )
    
    # Ordena pelo gap tecnológico
    df["gap"] = df["cobertura_prenatal"] - df["cobertura_ultrassom"]
    df_sorted = df.sort_values("gap", ascending=False)
    
    # Gráfico de barras
    plt.figure(figsize=(16, 10))  # Aumentei a altura para acomodar os rótulos
    x = np.arange(len(df_sorted))
    width = 0.4
    
    # MODIFICAÇÃO 1: Armazene as barras em variáveis
    prenatal_bars = plt.bar(x - width/2, df_sorted["cobertura_prenatal"] * 100, width=width, 
            label="Pré-Natal (≥6 consultas)", color=PRENATAL_COLOR)
    ultrassom_bars = plt.bar(x + width/2, df_sorted["cobertura_ultrassom"] * 100, width=width, 
            label="Ultrassonografia", color=ULTRASSOM_COLOR)
    
    # MODIFICAÇÃO 2: Adicione a função add_labels aqui
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:  # Só adiciona rótulos em barras visíveis
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + 1,  # Posicionar um pouco acima da barra
                    f'{height:.0f}%',
                    ha='center',
                    va='bottom',
                    fontsize=8,
                    rotation=0,
                    fontweight='bold'
                )
    
    # MODIFICAÇÃO 3: Chame a função add_labels para adicionar os rótulos
    add_labels(prenatal_bars)
    add_labels(ultrassom_bars)
    
    # Configurar o gráfico
    plt.xticks(ticks=x, labels=df_sorted[dsei_col], rotation=45, ha="right", fontsize=10)
    plt.ylabel("Cobertura (%)", fontsize=12)
    plt.xlabel("DSEI", fontsize=12)
    plt.title("Comparação de Coberturas por Distrito Sanitário Especial Indígena (2022–2023)", 
             fontsize=14, weight='bold')
    plt.axhline(45, color='red', linestyle='--', linewidth=1.5, label='Meta Nacional (45%)')
    plt.grid(axis='y', alpha=0.3)
    plt.ylim(0, 100)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
    
    # Salvar o gráfico se solicitado
    if salvar:
        plt.savefig("comparacao_prenatal_ultrassom.png", dpi=300, bbox_inches='tight')
    
    plt.show()
    
    return df_sorted

def create_gap_heatmap(df_sorted, salvar=False):
    """
    Cria um mapa de calor para visualizar o gap tecnológico entre 
    cobertura de pré-natal e ultrassonografia por DSEI.
    
    Parâmetros:
    - df_sorted: DataFrame com os dados de cobertura e gap, já ordenado
    - salvar: Se True, salva o gráfico como arquivo de imagem
    """
    # Identificar a coluna do DSEI
    dsei_col = df_sorted.columns[0]
    
    # Criar um DataFrame para o heatmap
    heatmap_data = df_sorted[[dsei_col, 'cobertura_prenatal', 'cobertura_ultrassom', 'gap']].copy()
    
    # Converter valores para percentual
    heatmap_data['cobertura_prenatal'] = heatmap_data['cobertura_prenatal'] * 100
    heatmap_data['cobertura_ultrassom'] = heatmap_data['cobertura_ultrassom'] * 100
    heatmap_data['gap'] = heatmap_data['gap'] * 100
    
    # Formatar valores
    heatmap_data['cobertura_prenatal'] = heatmap_data['cobertura_prenatal'].round(1).astype(str) + '%'
    heatmap_data['cobertura_ultrassom'] = heatmap_data['cobertura_ultrassom'].round(1).astype(str) + '%'
    heatmap_data['gap'] = heatmap_data['gap'].round(1).astype(str) + ' pp'
    
    # Configurar figura
    plt.figure(figsize=(12, len(heatmap_data) * 0.4 + 2))
    
    # Criar uma tabela estilizada
    ax = plt.subplot(111, frame_on=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    
    # Criar tabela
    colLabels = ['Cobertura Pré-Natal', 'Cobertura Ultrassom', 'Gap Tecnológico']
    table = plt.table(
        cellText=heatmap_data[[dsei_col, 'cobertura_prenatal', 'cobertura_ultrassom', 'gap']].values,
        colLabels=['DSEI'] + colLabels,
        loc='center',
        cellLoc='center',
        cellColours=plt.cm.RdYlGn_r(np.linspace(0.8, 0.2, len(heatmap_data)))[:, np.newaxis].repeat(4, axis=1),
        colWidths=[0.4, 0.2, 0.2, 0.2]
    )
    
    # Ajustar tamanho da fonte
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    
    plt.title('Gap Tecnológico por DSEI - Pré-Natal vs. Ultrassonografia (2022-2023)', 
              fontsize=14, weight='bold', pad=30)
    
    # Salvar o gráfico se solicitado
    if salvar:
        plt.savefig("gap_tecnologico_tabela.png", dpi=300, bbox_inches='tight')
    
    plt.tight_layout()
    plt.show()

def analisar_gap_tecnologico():
    """
    Função principal para realizar a análise do gap tecnológico
    entre cobertura de pré-natal e ultrassonografia
    """
    # Carregar os dados
    prenatal_2022, prenatal_2023, ultrassom_2022, ultrassom_2023 = carregar_dados()
    
    if all(df is not None for df in [prenatal_2022, prenatal_2023, ultrassom_2022, ultrassom_2023]):
        print("\n=== Iniciando análise do gap tecnológico ===")
        
        # Gerar gráfico de barras comparativas
        print("Gerando gráfico de barras comparativas...")
        df_sorted = create_heatmap_comparison(
            prenatal_2022, prenatal_2023, ultrassom_2022, ultrassom_2023, salvar=True
        )
        
        # Análise resumida do gap
        print("\n=== Resumo do Gap Tecnológico ===")
        gap_positivo = (df_sorted['gap'] > 0).sum()
        gap_negativo = (df_sorted['gap'] < 0).sum()
        print(f"DSEIs com maior cobertura de pré-natal do que ultrassom: {gap_positivo}")
        print(f"DSEIs com maior cobertura de ultrassom do que pré-natal: {gap_negativo}")
        
        # Médias de cobertura
        prenatal_medio = df_sorted['cobertura_prenatal'].mean() * 100
        ultrassom_medio = df_sorted['cobertura_ultrassom'].mean() * 100
        gap_medio = df_sorted['gap'].mean() * 100
        print(f"\nCobertura média de pré-natal: {prenatal_medio:.1f}%")
        print(f"Cobertura média de ultrassonografia: {ultrassom_medio:.1f}%")
        print(f"Gap tecnológico médio: {gap_medio:.1f} pontos percentuais")
        
        # Top 3 maiores e menores gaps
        print("\n=== DSEIs com maiores gaps tecnológicos ===")
        top_gaps = df_sorted.head(3)
        for i, row in top_gaps.iterrows():
            dsei = row[df_sorted.columns[0]]
            gap = row['gap'] * 100
            print(f"{dsei}: {gap:.1f} pontos percentuais")
        
        print("\n=== DSEIs com menores gaps tecnológicos (ou negativos) ===")
        bottom_gaps = df_sorted.tail(3)
        for i, row in bottom_gaps.iloc[::-1].iterrows():
            dsei = row[df_sorted.columns[0]]
            gap = row['gap'] * 100
            print(f"{dsei}: {gap:.1f} pontos percentuais")
        
        # Gerar tabela de calor
        print("\nGerando tabela com gaps tecnológicos...")
        create_gap_heatmap(df_sorted, salvar=True)
        
        print("\nTodas as análises foram concluídas com sucesso!")
        
    else:
        print("Não foi possível realizar a análise devido a erros no carregamento dos dados.")

# Se este arquivo for executado diretamente
if __name__ == "__main__":
    analisar_gap_tecnologico()