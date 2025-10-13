import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel('../dados/consolidado_final_com_urgencia.xlsx')

all_doencas = [col for col in df.columns if col not in ['Uf', 'Ano', 'populacao_ibge', 'dependentes_do_sus', 'percentual_dependentes']]

doencas_selecionadas = ['Hipertensão arterial', 'Diabetes', 'Saúde mental', 'Reabilitação', 'Saúde sexual e reprodutiva']

df_agrupado_all = df.groupby('Ano')[all_doencas].sum().reset_index()

df_agrupado_all['Total_Todas'] = df_agrupado_all[all_doencas].sum(axis=1)

for doenca in doencas_selecionadas:
    df_agrupado_all[f'Percentual_{doenca}'] = (df_agrupado_all[doenca] / df_agrupado_all['Total_Todas']) * 100

avg_percentages = {}
for doenca in doencas_selecionadas:
    avg = df_agrupado_all[f'Percentual_{doenca}'].mean()
    avg_percentages[doenca] = avg

doencas_ordenadas = sorted(doencas_selecionadas, key=lambda x: avg_percentages[x], reverse=True)

cores_fixas = ["#EF8264", "#E95F3A", "#632F21", "#81CBD3", "#114354"]
color_dict = dict(zip(doencas_ordenadas, cores_fixas))

plt.figure(figsize=(14, 8))

for doenca in doencas_ordenadas:
    data_doenca = df_agrupado_all[['Ano', f'Percentual_{doenca}']].copy()
    data_doenca.columns = ['Ano', 'Percentual']
    
    data_solid = data_doenca[data_doenca['Ano'] <= 2024]
    plt.plot(data_solid['Ano'], data_solid['Percentual'], linestyle='-', color=color_dict[doenca], label=doenca, linewidth=2)
    
    if 2024 in data_doenca['Ano'].values and 2025 in data_doenca['Ano'].values:
        val_2024 = data_doenca[data_doenca['Ano'] == 2024]['Percentual'].values[0]
        val_2025 = data_doenca[data_doenca['Ano'] == 2025]['Percentual'].values[0]
        plt.plot([2024, 2025], [val_2024, val_2025], linestyle='--', color=color_dict[doenca], linewidth=2)

plt.title('Tendência percentual dos 5 principais atendimentos a pessoas idosas no SISAB (urgência) (por ano)', fontsize=14)
plt.xlabel('Ano', fontsize=12)
plt.ylabel('Percentual atendimentos (%)', fontsize=12)
plt.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=5, fontsize=10)
plt.figtext(0.5, -0.05, 'Nota: Dados de 2025 são parciais (até julho) e estão representados por linhas tracejadas.', ha='center', fontsize=10)
plt.figtext(0.5, -0.08, 'Fonte: SISAB / Elaboração ImpulsoGov', ha='center', fontsize=9, style='italic')
plt.tight_layout()

plt.savefig('tendencia_percentual_urgencia.png', dpi=300, bbox_inches='tight')
print("Gráfico salvo como 'tendencia_percentual_urgencia.png'")