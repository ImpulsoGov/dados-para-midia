import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel('visita_domiciliar_com_populacao.xlsx')

numeric_cols = [col for col in df.columns if col not in ['Brasil', 'ano', 'populacao_nacional']]

groups = {
    'Condições crônicas / clínicas': [
        'Acomp. Pessoa c/ Diabetes', 'Acomp. Pessoa c/ Hipertensão', 'Acomp. Pessoas c/ D. Crônicas',
        'Acomp. Pessoa c/ Asma', 'Acomp. - DPOC/Enfisema', 'Acomp. Pessoa c/ Câncer', 'Acomp. Pessoa c/ Desnutrição'
    ],
    'Saúde mental e uso de substâncias': [
        'Acomp. Usuário de álcool', 'Acomp. - Usuário de drogas', 'Acompanhamento - Tabagista', 'Acompanhamento - Saúde mental'
    ],
    'Vigilância em saúde': [
        'Acomp. Condições de V.S.', 'Acomp. Sintomáticos Resp.', 'Controle de Ambientes/Vetores'
    ],
    'Busca ativa / acompanhamento programado': [
        'B.A. - Cond. Bolsa Família', 'Busca ativa - Consulta', 'Busca ativa - Exame',
        'Busca ativa - Vacina', 'Cadastramento/Atualização'
    ],
    'Ações complementares': [
        'Convite At.Col./Camp. Saúde', 'Egresso de Internação', 'Orientação / Prevenção', 'Visita periódica'
    ]
}

df_melted = df.melt(id_vars=['ano', 'populacao_nacional'], value_vars=numeric_cols, var_name='tipo_visita', value_name='visitas')

for group_name, tipos in groups.items():
    for ano in df['ano'].unique():
        data_year = df_melted[(df_melted['ano'] == ano) & (df_melted['tipo_visita'].isin(tipos))]
        total_group = data_year['visitas'].sum()
        if total_group > 0:
            for tipo in tipos:
                if tipo in data_year['tipo_visita'].values:
                    visits = data_year[data_year['tipo_visita'] == tipo]['visitas'].values[0]
                    perc = (visits / total_group) * 100
                    df_melted.loc[(df_melted['ano'] == ano) & (df_melted['tipo_visita'] == tipo), 'percentual_grupo'] = perc
                else:
                    df_melted.loc[(df_melted['ano'] == ano) & (df_melted['tipo_visita'] == tipo), 'percentual_grupo'] = 0
        else:
            for tipo in tipos:
                df_melted.loc[(df_melted['ano'] == ano) & (df_melted['tipo_visita'] == tipo), 'percentual_grupo'] = 0

cat_colors = ["#114354", "#1F7A99", "#2EA6BC", "#81CBD3",
              "#632F21", "#9C462F", "#E95F3A", "#EF8264"]

for group_idx, (group_name, tipos) in enumerate(groups.items()):
    plt.figure(figsize=(12, 8))

    for i, tipo in enumerate(tipos):
        if tipo in df_melted['tipo_visita'].unique():
            color = cat_colors[(i + group_idx) % len(cat_colors)]  
            data_tipo = df_melted[df_melted['tipo_visita'] == tipo].sort_values('ano')
            data_solid = data_tipo[data_tipo['ano'] <= 2024]
            plt.plot(data_solid['ano'], data_solid['percentual_grupo'], linestyle='-', color=color, label=tipo, linewidth=2)
            if 2024 in data_tipo['ano'].values and 2025 in data_tipo['ano'].values:
                val_2024 = data_tipo[data_tipo['ano'] == 2024]['percentual_grupo'].values[0]
                val_2025 = data_tipo[data_tipo['ano'] == 2025]['percentual_grupo'].values[0]
                plt.plot([2024, 2025], [val_2024, val_2025], linestyle='--', color=color, linewidth=2)

    plt.title(f'Visitas domiciliares de {group_name} - Percentual dentro do grupo (2019-2025)', fontsize=14)
    plt.xlabel('Ano', fontsize=12)
    plt.ylabel('Percentual (%)', fontsize=12)
    plt.ylim(bottom=0)
    plt.xticks(sorted(df['ano'].unique()))
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

    plt.figtext(0.5, 0.02, 'Nota: Dados de 2025 são parciais (até julho-2025).', ha='center', fontsize=10)

    plt.figtext(0.5, 0.02, 'Nota: Dados de 2025 são parciais (até julho-2025).', ha='center', fontsize=10)
    filename = f'visita_domiciliar_{group_name.replace(" ", "_").replace("/", "_").replace(".", "")}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Graph saved as '{filename}'")