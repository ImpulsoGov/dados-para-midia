import pandas as pd
import matplotlib.pyplot as plt

file_path = 'pessoas_idosas_sisab.xlsx'

df = pd.read_excel(file_path, sheet_name=1)

df_plot = df[['Ano', 'Percentual']]

df_plot = df_plot.sort_values('Ano')

plt.figure(figsize=(10, 6))

data_2019_2024 = df_plot[df_plot['Ano'] <= 2024]
data_2025 = df_plot[df_plot['Ano'] == 2025]

plt.plot(data_2019_2024['Ano'], data_2019_2024['Percentual'] * 100, linestyle='-', color='#114354')

if not data_2025.empty:
    data_2024 = data_2019_2024[data_2019_2024['Ano'] == 2024]
    if not data_2024.empty:
        plt.plot([2024, 2025], [data_2024['Percentual'].values[0] * 100, data_2025['Percentual'].values[0] * 100],
                 linestyle='--', color='#114354')

for _, row in df_plot.iterrows():
    plt.text(row['Ano'], row['Percentual'] * 100, f"{round(row['Percentual'] * 100, 1)}%",
             ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.title('Percentual de visitas domiciliares para pessoas idosas no SISAB')
plt.xlabel('Ano')
plt.ylabel('Percentual (%)')
plt.ylim(bottom=0, top=110)

plt.subplots_adjust(bottom=0.25)

plt.figtext(0.5, 0.15, 'Nota: Os dados de 2025 são parciais (até julho), por isso a linha está em pontilhado.',
            ha='center', fontsize=10)

plt.figtext(0.5, 0.11, 'Fonte: SISAB e IBGE',
            ha='center', fontsize=9, style='italic')

plt.savefig('visita_plot.png')