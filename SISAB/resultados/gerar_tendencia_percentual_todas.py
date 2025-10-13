import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel('../dados/consolidado_final.xlsx')

all_doencas = [col for col in df.columns if col not in ['Uf', 'Ano', 'populacao_ibge', 'dependentes_do_sus', 'percentual_dependentes']]

doencas_selecionadas = ['Hipertensão arterial', 'Diabetes', 'Saúde mental', 'Reabilitação', 'Obesidade' ,'Saúde sexual e reprodutiva']

df_agrupado_all = df.groupby('Ano')[all_doencas].sum().reset_index()

df_agrupado_all['Total_Todas'] = df_agrupado_all[all_doencas].sum(axis=1)

df_agrupado = df_agrupado_all.copy()

for doenca in doencas_selecionadas:
    df_agrupado[f'Percentual_{doenca}'] = (df_agrupado[doenca] / df_agrupado['Total_Todas']) * 100

avg_percentages = {}
for doenca in doencas_selecionadas:
    avg = df_agrupado[f'Percentual_{doenca}'].mean()
    avg_percentages[doenca] = avg

doencas_ordenadas = sorted(doencas_selecionadas, key=lambda x: avg_percentages[x], reverse=True)

cores_fixas = ["#EF8264", "#E95F3A", "#632F21", "#81CBD3", "#114354","#B8947A"]
color_dict = dict(zip(doencas_ordenadas, cores_fixas))

plt.figure(figsize=(14, 8))

for doenca in doencas_ordenadas:
    data_doenca = df_agrupado[['Ano', f'Percentual_{doenca}']].copy()
    data_doenca.columns = ['Ano', 'Percentual']
    
    data_solid = data_doenca[data_doenca['Ano'] <= 2024]
    plt.plot(data_solid['Ano'], data_solid['Percentual'], linestyle='-', color=color_dict[doenca], label=doenca, linewidth=2)
    
    if 2024 in data_doenca['Ano'].values and 2025 in data_doenca['Ano'].values:
        val_2024 = data_doenca[data_doenca['Ano'] == 2024]['Percentual'].values[0]
        val_2025 = data_doenca[data_doenca['Ano'] == 2025]['Percentual'].values[0]
        plt.plot([2024, 2025], [val_2024, val_2025], linestyle='--', color=color_dict[doenca], linewidth=2)

plt.title('Tendência percentual dos principais atendimentos a pessoas idosas no SISAB (por ano)', fontsize=14)
plt.xlabel('Ano', fontsize=12)
plt.ylabel('Percentual atendimentos (%)', fontsize=12)
plt.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=5, fontsize=10)
plt.figtext(0.5, -0.05, 'Nota: Dados de 2025 são parciais (até julho) e estão representados por linhas tracejadas.', ha='center', fontsize=10)
plt.figtext(0.5, -0.08, 'Fonte: SISAB', ha='center', fontsize=9, style='italic')
plt.tight_layout()

anos_selecionados = [2019, 2024, 2025]
df_excel = df_agrupado_all[df_agrupado_all['Ano'].isin(anos_selecionados)].copy()

for doenca in all_doencas:
    df_excel[f'Percentual_{doenca}'] = (df_excel[doenca] / df_excel['Total_Todas']) * 100

df_abs = df_excel.melt(id_vars='Ano', value_vars=all_doencas, var_name='Doença', value_name='Absoluto')
df_abs = df_abs.pivot(index='Doença', columns='Ano', values='Absoluto').reset_index()
df_abs.columns.name = None
df_abs = df_abs.rename(columns={2019: '2019 (absoluto)', 2024: '2024 (absoluto)', 2025: '2025 (absoluto)'})

percentual_cols = [f'Percentual_{doenca}' for doenca in all_doencas]
df_perc = df_excel.melt(id_vars='Ano', value_vars=percentual_cols, var_name='Doença', value_name='Percentual')
df_perc['Doença'] = df_perc['Doença'].str.replace('Percentual_', '')
df_perc = df_perc.pivot(index='Doença', columns='Ano', values='Percentual').reset_index()
df_perc.columns.name = None
df_perc = df_perc.rename(columns={2019: '2019 (%)', 2024: '2024 (%)', 2025: '2025 (%)'})

df_final = pd.merge(df_abs, df_perc, on='Doença')

cols_order = ['Doença', '2019 (absoluto)', '2019 (%)', '2024 (absoluto)', '2024 (%)', '2025 (absoluto)', '2025 (%)']
df_final = df_final[cols_order]

df_final.to_excel('percentuais_doencas_2019_2024_2025.xlsx', index=False)
print("Excel salvo como 'percentuais_doencas_2019_2024_2025.xlsx'")

cols_to_export = ['Ano'] + [f'Percentual_{doenca}' for doenca in doencas_selecionadas]
df_grafico = df_agrupado[cols_to_export].copy()
df_grafico.to_excel('dados_grafico_tendencia_percentual_todas.xlsx', index=False)
print("Excel dos dados do gráfico salvo como 'dados_grafico_tendencia_percentual_todas.xlsx'")

plt.savefig('tendencia_percentual_todas.png', dpi=300, bbox_inches='tight')
print("Gráfico salvo como 'tendencia_percentual_todas.png'")