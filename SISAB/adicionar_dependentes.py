import pandas as pd

def adicionar_dependentes_sus():
    ans_file = '../ANS/dados/merged_ans_populacao.xlsx'
    urgencia_file = './dados/consolidado_final_com_urgencia.xlsx'
    sem_urgencia_file = './dados/consolidado_final_sem_urgencia.xlsx'
    
    try:
        df_ans = pd.read_excel(ans_file)
        df_ans_merge = df_ans[['ano', 'uf', 'dependentes_do_sus', 'percentual_dependentes']].copy()
        df_ans_merge['uf'] = df_ans_merge['uf'].str.upper()
        
        df_urgencia = pd.read_excel(urgencia_file)
        df_sem_urgencia = pd.read_excel(sem_urgencia_file)
        
        df_urgencia_merged = pd.merge(
            df_urgencia,
            df_ans_merge,
            left_on=['Uf', 'Ano'],
            right_on=['uf', 'ano'],
            how='left'
        )
        df_urgencia_merged = df_urgencia_merged.drop(['uf', 'ano'], axis=1)
        
        df_sem_urgencia_merged = pd.merge(
            df_sem_urgencia,
            df_ans_merge,
            left_on=['Uf', 'Ano'],
            right_on=['uf', 'ano'],
            how='left'
        )
        df_sem_urgencia_merged = df_sem_urgencia_merged.drop(['uf', 'ano'], axis=1)
        
        urgencia_matches = df_urgencia_merged['dependentes_do_sus'].notna().sum()
        sem_urgencia_matches = df_sem_urgencia_merged['dependentes_do_sus'].notna().sum()

        print(f"Matches urgência: {urgencia_matches}")
        print(f"Matches sem urgência: {sem_urgencia_matches}")

        if urgencia_matches > 0 or sem_urgencia_matches > 0:
            df_urgencia_merged.to_excel(urgencia_file, index=False)
            df_sem_urgencia_merged.to_excel(sem_urgencia_file, index=False)
            print(f"✅ Colunas adicionadas com sucesso!")
        else:
            print("❌ Nenhum match encontrado, arquivos não salvos.")
        
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    adicionar_dependentes_sus()