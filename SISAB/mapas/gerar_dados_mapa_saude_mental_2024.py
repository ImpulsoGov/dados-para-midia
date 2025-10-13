import pandas as pd

# Carregar dados de urgência e sem urgência
df_urgencia = pd.read_excel('../dados/consolidado_final_com_urgencia.xlsx')
df_sem_urgencia = pd.read_excel('../dados/consolidado_final_sem_urgencia.xlsx')

# Filtrar para 2024 e 2025
df_urgencia_2024 = df_urgencia[df_urgencia['Ano'] == 2024]
df_sem_urgencia_2024 = df_sem_urgencia[df_sem_urgencia['Ano'] == 2024]
df_urgencia_2025 = df_urgencia[df_urgencia['Ano'] == 2025]
df_sem_urgencia_2025 = df_sem_urgencia[df_sem_urgencia['Ano'] == 2025]

# Agrupar por UF para taxas 2024
taxa_urgencia = df_urgencia_2024.groupby('Uf').agg({
    'Saúde mental': 'sum',
    'dependentes_do_sus': 'sum'
}).reset_index()

taxa_sem_urgencia = df_sem_urgencia_2024.groupby('Uf').agg({
    'Saúde mental': 'sum',
    'dependentes_do_sus': 'sum'
}).reset_index()

# Calcular taxas por 100.000 dependentes do SUS
taxa_urgencia['Taxa atendimento com urgencia'] = (taxa_urgencia['Saúde mental'] / taxa_urgencia['dependentes_do_sus']) * 100000
taxa_sem_urgencia['Taxa atendimento sem urgencia'] = (taxa_sem_urgencia['Saúde mental'] / taxa_sem_urgencia['dependentes_do_sus']) * 100000

# Agrupar para absolutos 2024
abs_2024_urgencia = df_urgencia_2024.groupby('Uf')['Saúde mental'].sum().reset_index().rename(columns={'Saúde mental': 'Numero absoluto 2024 com urgencia'})
abs_2024_sem_urgencia = df_sem_urgencia_2024.groupby('Uf')['Saúde mental'].sum().reset_index().rename(columns={'Saúde mental': 'Numero absoluto 2024 sem urgencia'})

# Agrupar para absolutos 2025
abs_2025_urgencia = df_urgencia_2025.groupby('Uf')['Saúde mental'].sum().reset_index().rename(columns={'Saúde mental': 'Numero absoluto 2025 com urgencia'})
abs_2025_sem_urgencia = df_sem_urgencia_2025.groupby('Uf')['Saúde mental'].sum().reset_index().rename(columns={'Saúde mental': 'Numero absoluto 2025 sem urgencia'})

# Mesclar tudo
df_final = taxa_urgencia[['Uf', 'Taxa atendimento com urgencia', 'dependentes_do_sus']].rename(columns={'dependentes_do_sus': 'Numero pessoas idosas exclusivas do SUS'})
df_final = pd.merge(df_final, taxa_sem_urgencia[['Uf', 'Taxa atendimento sem urgencia']], on='Uf', how='outer')
df_final = pd.merge(df_final, abs_2024_urgencia, on='Uf', how='outer')
df_final = pd.merge(df_final, abs_2024_sem_urgencia, on='Uf', how='outer')
df_final = pd.merge(df_final, abs_2025_urgencia, on='Uf', how='outer')
df_final = pd.merge(df_final, abs_2025_sem_urgencia, on='Uf', how='outer')

# Renomear UF para maiúsculo
df_final['UF'] = df_final['Uf'].str.upper()
df_final = df_final[['UF',  'Taxa atendimento com urgencia', 'Taxa atendimento sem urgencia','Numero absoluto 2024 com urgencia', 'Numero absoluto 2024 sem urgencia', 'Numero pessoas idosas exclusivas do SUS']]

# Salvar Excel
df_final.to_excel('dados_mapa_saude_mental_2024_comparativo.xlsx', index=False)
print("Excel salvo como 'dados_mapa_saude_mental_2024_comparativo.xlsx'")