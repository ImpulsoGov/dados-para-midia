import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel('visita_domiciliar_com_populacao.xlsx')

numeric_cols = [col for col in df.columns if col not in ['Brasil', 'ano', 'populacao_nacional']]

df['total_visitas'] = df[numeric_cols].sum(axis=1)

df = df.sort_values('ano')

# Plot
plt.figure(figsize=(12, 8))
data_solid = df[df['ano'] <= 2024]
plt.plot(data_solid['ano'], data_solid['total_visitas'], marker='o', linestyle='-', color='#114354', linewidth=2)

if 2024 in df['ano'].values and 2025 in df['ano'].values:
    val_2024 = df[df['ano'] == 2024]['total_visitas'].values[0]
    val_2025 = df[df['ano'] == 2025]['total_visitas'].values[0]
    plt.plot([2024, 2025], [val_2024, val_2025], linestyle='--', color='#114354', linewidth=2)
    plt.plot(2025, val_2025, marker='o', color='#114354')

for i, row in df.iterrows():
    millions = row['total_visitas'] / 1000000
    plt.text(row['ano'], row['total_visitas'], f"{millions:.1f}".replace('.', ','),
             ha='center', va='bottom', fontsize=9, fontweight='bold')

def millions_formatter(x, pos):
    return f'{x / 1e6:.0f}'

import matplotlib.ticker as ticker
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))

plt.title('Total de Visitas Domiciliares no Brasil (2019-2025)', fontsize=14)
plt.xlabel('Ano', fontsize=12)
plt.ylabel('Total de Visitas (em milhões)', fontsize=12)
plt.ylim(bottom=0)
plt.xticks(sorted(df['ano'].unique()))

plt.figtext(0.5, 0.02, 'Nota: Dados de 2025 são parciais (até julho-2025).', ha='center', fontsize=10)

plt.savefig('total_visitas_domiciliares_brasil.png', dpi=300, bbox_inches='tight')
print("Graph saved as 'total_visitas_domiciliares_brasil.png'")