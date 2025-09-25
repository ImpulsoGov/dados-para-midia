import pandas as pd

df = pd.read_excel('visita_domiciliar_com_populacao.xlsx')

numeric_cols = [col for col in df.columns if col not in ['Brasil', 'ano', 'populacao_nacional']]

df_melted = df.melt(id_vars=['ano', 'populacao_nacional'], value_vars=numeric_cols, var_name='tipo_visita', value_name='visitas')

df_melted['taxa_100k'] = (df_melted['visitas'] / df_melted['populacao_nacional']) * 100000

missing_years = [2019, 2020]
for ano in missing_years:
    if ano not in df['ano'].values:
        new_row = df.iloc[0].copy()
        new_row['ano'] = ano
        for col in numeric_cols:
            new_row[col] = 0
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

df_melted = df.melt(id_vars=['ano', 'populacao_nacional'], value_vars=numeric_cols, var_name='tipo_visita', value_name='visitas')
df_melted['taxa_100k'] = (df_melted['visitas'] / df_melted['populacao_nacional']) * 100000

pivot_df = df_melted.pivot(index='tipo_visita', columns='ano', values='taxa_100k').reset_index()

anos = sorted(df['ano'].unique())
column_names = ['tipo_visita'] + [f'ano_{ano}' for ano in anos]
pivot_df.columns = column_names

pivot_df.to_excel('visita_domiciliar_pivot.xlsx', index=False)
print("Pivot table saved as 'visita_domiciliar_pivot.xlsx'")