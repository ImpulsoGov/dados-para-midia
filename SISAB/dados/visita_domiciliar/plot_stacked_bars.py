import pandas as pd
import matplotlib.pyplot as plt

file_path = 'visitas_gerais.xlsx'

df = pd.read_excel(file_path)

df['Total'] = df['visita_idoso'] + df['visita_crianca'] + df['visita_adulto']
df['Percentual Idosos'] = (df['visita_idoso'] / df['Total']) * 100
df['Percentual Crianças'] = (df['visita_crianca'] / df['Total']) * 100
df['Percentual Adultos'] = (df['visita_adulto'] / df['Total']) * 100

df_plot = df[['Ano', 'Percentual Idosos', 'Percentual Crianças', 'Percentual Adultos']]

df_plot = df_plot.sort_values('Ano')

plt.figure(figsize=(10, 6))

anos = df_plot['Ano']
idosos = df_plot['Percentual Idosos']
criancas = df_plot['Percentual Crianças']
adultos = df_plot['Percentual Adultos']

plt.bar(anos, criancas, label='Crianças (0 até 14 anos)', color='#6c757d')
plt.bar(anos, adultos, bottom=criancas, label='Adultos (15 até 59 anos)', color='#28a745')
plt.bar(anos, idosos, bottom=criancas + adultos, label='Idosos (60 anos ou mais)', color='#114354')

for i, ano in enumerate(anos):
    plt.text(ano, criancas[i]/2, f"{criancas[i]:.1f}%", ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    plt.text(ano, criancas[i] + adultos[i]/2, f"{adultos[i]:.1f}%", ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    plt.text(ano, criancas[i] + adultos[i] + idosos[i]/2, f"{idosos[i]:.1f}%", ha='center', va='center', fontsize=8, color='white', fontweight='bold')

plt.title('Percentual de visitas domiciliares por grupo etário no SISAB')
plt.xlabel('Ano')
plt.ylabel('Percentual (%)')
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=False, shadow=False, frameon=False, ncol=3)

plt.subplots_adjust(bottom=0.35)

plt.figtext(0.5, 0.15, 'Nota: Os dados de 2025 são parciais (até julho).',
            ha='center', fontsize=10)

plt.figtext(0.5, 0.11, 'Fonte: SISAB',
            ha='center', fontsize=9, style='italic')

plt.savefig('visitas_stacked_bars.png')