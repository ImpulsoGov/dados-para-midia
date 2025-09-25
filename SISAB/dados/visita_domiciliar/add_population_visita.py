import pandas as pd
import os

df = pd.read_excel('combined_visita_domiciliar.xlsx')
if 'populacao_nacional' in df.columns:
    df = df.drop('populacao_nacional', axis=1)

ibge_path = '../../../../dados/IBGE/populacao_PNAD.xlsx'
proj_path = '../../../../dados/IBGE/projecao_2025.xlsx'

if os.path.exists(ibge_path):
    df_ibge = pd.read_excel(ibge_path)
    df_ibge_long = pd.melt(
        df_ibge,
        id_vars=['Cód.', 'Unidade da Federação'],
        value_vars=[2019, 2020, 2021, 2022, 2023, 2024],
        var_name='ano', value_name='populacao_uf'
    )
else:
    df_ibge_long = pd.DataFrame()

if os.path.exists(proj_path):
    df_proj_2025 = pd.read_excel(proj_path)
    df_proj_2025 = df_proj_2025.rename(columns={'total': 'populacao_uf'})
    df_proj_2025['ano'] = 2025
    df_ibge_long = pd.concat([df_ibge_long, df_proj_2025], ignore_index=True)

if not df_ibge_long.empty:
    df_ibge_long = df_ibge_long.rename(columns={
        'Cód.': 'cod_uf',
        'Unidade da Federação': 'nome_uf'
    })

    df_ibge_long['ano'] = df_ibge_long['ano'].astype(int)

    mask_ate_2024 = df_ibge_long['ano'] <= 2024
    df_ibge_long.loc[mask_ate_2024, 'populacao_uf'] = df_ibge_long.loc[mask_ate_2024, 'populacao_uf'] * 1000

    national_pop = df_ibge_long.groupby('ano')['populacao_uf'].sum().reset_index()
    national_pop = national_pop.rename(columns={'populacao_uf': 'populacao_nacional'})

    df['ano'] = df['ano'].astype(int)
    df_with_pop = pd.merge(df, national_pop, on='ano', how='left')

    df_with_pop.to_excel('visita_domiciliar_com_populacao.xlsx', index=False)
