import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_excel('visita_domiciliar_com_populacao.xlsx')

numeric_cols = [col for col in df.columns if col not in ['Brasil', 'ano', 'populacao_nacional']]

selected_tipos = [
    'Acomp. Pessoa c/ Hipertensão', 'Acomp.  Pessoa c/ Diabetes', 'Acomp.  Pessoas c/ D. Crônicas',
    'Acompanhamento - Saúde mental', 'Acompanhamento - Tabagista', 'Acomp. Usuário de álcool',
    'Busca ativa - Exame', 'Busca ativa - Vacina', 'Orientação / Prevenção', 'Visita periódica'
]

df_melted = df.melt(id_vars=['ano', 'populacao_nacional'], value_vars=numeric_cols, var_name='tipo_visita', value_name='visitas')
for ano in df['ano'].unique():
    data_year = df_melted[df_melted['ano'] == ano]
    total_visitas = data_year['visitas'].sum()
    if total_visitas > 0:
        for tipo in selected_tipos:
            if tipo in data_year['tipo_visita'].values:
                visits = data_year[data_year['tipo_visita'] == tipo]['visitas'].values[0]
                perc = (visits / total_visitas) * 100
                df_melted.loc[(df_melted['ano'] == ano) & (df_melted['tipo_visita'] == tipo), 'percentual_total'] = perc
            else:
                df_melted.loc[(df_melted['ano'] == ano) & (df_melted['tipo_visita'] == tipo), 'percentual_total'] = 0

avg_percentages = {}
for tipo in selected_tipos:
    if tipo in df_melted['tipo_visita'].unique():
        avg = df_melted[df_melted['tipo_visita'] == tipo]['percentual_total'].mean()
        avg_percentages[tipo] = avg
    else:
        avg_percentages[tipo] = 0

selected_tipos_sorted = sorted(selected_tipos, key=lambda x: avg_percentages[x], reverse=True)

cat_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

plt.figure(figsize=(14, 10))

for i, tipo in enumerate(selected_tipos_sorted):
    if tipo in df_melted['tipo_visita'].unique():
        color = cat_colors[i % len(cat_colors)]
        data_tipo = df_melted[df_melted['tipo_visita'] == tipo].sort_values('ano')
        data_solid = data_tipo[data_tipo['ano'] <= 2024]
        plt.plot(data_solid['ano'], data_solid['percentual_total'], linestyle='-', color=color, label=tipo, linewidth=2)
        if 2024 in data_tipo['ano'].values and 2025 in data_tipo['ano'].values:
            val_2024 = data_tipo[data_tipo['ano'] == 2024]['percentual_total'].values[0]
            val_2025 = data_tipo[data_tipo['ano'] == 2025]['percentual_total'].values[0]
            plt.plot([2024, 2025], [val_2024, val_2025], linestyle='--', color=color, linewidth=2)

plt.title('Visitas domiciliares selecionadas - Percentual do total (2019-2025)', fontsize=14)
plt.xlabel('Ano', fontsize=12)
plt.ylabel('Percentual do total (%)', fontsize=12)
plt.ylim(bottom=0)
plt.xticks(sorted(df['ano'].unique()))
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

plt.figtext(0.5, 0.02, 'Nota: Dados de 2025 são parciais (até julho-2025).', ha='center', fontsize=10)

plt.savefig('visita_domiciliar_geral_selecionadas.png', dpi=300, bbox_inches='tight')
print("Graph saved as 'visita_domiciliar_geral_selecionadas.png'")