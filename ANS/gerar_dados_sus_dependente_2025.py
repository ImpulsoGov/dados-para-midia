import pandas as pd

# Carregar dados
df = pd.read_excel('dados/merged_ans_populacao.xlsx')

# Filtrar para 2025
df_2025 = df[df['ano'] == 2025]

# Selecionar colunas: uf, percentual (multiplicado por 100), numero absoluto de dependentes
df_final = df_2025[['uf', 'percentual_dependentes', 'dependentes_do_sus']].copy()
df_final['percentual'] = df_final['percentual_dependentes'] * 100
df_final = df_final[['uf', 'percentual', 'dependentes_do_sus']].rename(columns={'dependentes_do_sus': 'numero absoluto de dependentes'})

# Salvar Excel
df_final.to_excel('dados_sus_dependente_2025.xlsx', index=False)
print("Excel salvo como 'dados_sus_dependente_2025.xlsx'")