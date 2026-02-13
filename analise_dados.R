library(dplyr)
library(dplyr)
library(readr)
arquivo <- "sih_estrangeiros_2019_2025.csv"
dados <- read_csv(arquivo)
dados_filtrado <- dados %>%
  filter(!NACIONAL %in% c("010", "020"))
write_csv(dados_filtrado, "sih_estrangeiros_2019_2025_filtardo.csv")
df <- read_csv("sih_estrangeiros_2019_2025_filtardo.csv")
colnames(df)
depara_nacionalidade <- tribble(
  ~NACIONAL, ~pais,
  "092", "Paraguai",
  "022", "Bolívia",
  "024", "Argentina",
  "062", "Haiti",
  "050", "Venezuela",
  "020", "Chile",
  "045", "Peru",
  "021", "Colômbia",
  "041", "Uruguai",
  "023", "Equador",
  "052", "Cuba",
  "039", "Portugal",
  "025", "México",
  "081", "Estados Unidos",
  "030", "Espanha",
  "048", "República Dominicana",
  "026", "Panamá",
  "035", "Alemanha",
  "100", "China",
  "032", "Itália"
)
df <- df %>% mutate(NACIONAL = as.character(NACIONAL))
top20_nacional <- df %>%
  filter(!is.na(NACIONAL), NACIONAL != "") %>% 
  count(NACIONAL, sort = TRUE) %>%
  slice_head(n = 20)
resultado <- top20_nacional %>%
  left_join(depara_nacionalidade, by = "NACIONAL")
resultado
library(dplyr)
library(ggplot2)
depara_nacionalidade <- tribble(
  ~NACIONAL, ~pais,
  "092", "Paraguai",
  "022", "Bolívia",
  "024", "Argentina",
  "062", "Haiti",
  "050", "Venezuela",
  "020", "Chile",
  "045", "Peru",
  "021", "Colômbia",
  "041", "Uruguai",
  "023", "Equador",
  "052", "Cuba",
  "039", "Portugal",
  "025", "México",
  "081", "Estados Unidos",
  "030", "Espanha",
  "048", "República Dominicana",
  "026", "Panamá",
  "035", "Alemanha",
  "100", "China",
  "032", "Itália"
)
df <- df %>% mutate(NACIONAL = as.character(NACIONAL))
top5_por_ano <- df %>%
  filter(!is.na(NACIONAL), NACIONAL != "") %>%
  count(ano, NACIONAL) %>%
  group_by(ano) %>%
  slice_max(n, n = 5) %>%
  ungroup() %>%
  left_join(depara_nacionalidade, by = "NACIONAL") %>%
  mutate(pais = ifelse(is.na(pais), paste0("Código ", NACIONAL), pais))
ggplot(top5_por_ano, aes(x = ano, y = n, color = pais, group = pais)) +
  geom_line() +
  geom_point() +
  labs(
    title = "Top 5 nacionalidades estrangeiras por ano",
    x = "Ano",
    y = "Número de registros",
    color = "País"
  ) +
  theme_minimal()
cod_brasil <- c("010", "020", "10", "20")
df %>%
  filter(NACIONAL %in% cod_brasil) %>%
  count(NACIONAL)
library(dplyr)
library(dplyr)
procedimentos_mais_realizados <- df %>%
  group_by(PROC_REA) %>%
  summarise(total = n()) %>%
  arrange(desc(total))
head(procedimentos_mais_realizados, 10)
top10 <- head(procedimentos_mais_realizados, 10)
ggplot(top10, aes(x = reorder(PROC_REA, total), y = total)) +
  geom_col(fill = "steelblue") +
  coord_flip() +
  labs(title = "Top 10 procedimentos mais realizados",
       x = "Código do Procedimento",
       y = "Número de internações") +
  theme_minimal()
library(dplyr)
library(ggplot2)
top10 <- data.frame(
  PROC_REA = c("PARTO NORMAL", "PARTO CESARIANO", "PARTO CESARIANO ALTO RISCO", 
               "0303140151 (Respiratório)", "0303100044 (Intercorrência Gravidez)", 
               "PARTO NORMAL ALTO RISCO", "DIAGNÓSTICO/ATEND URG CLÍNICA MÉDICA", 
               "TRATAMENTO COM CIRURGIAS MÚLTIPLAS", "CURETAGEM PÓS‑ABORTAMENTO", 
               "TRATAMENTO OUTRAS DOENÇAS BACTERIANAS"),
  total = c(35872, 16006, 10772, 9523, 8145, 6548, 5615, 5467, 5359, 5332)
)
ggplot(top10, aes(x = reorder(PROC_REA, total), y = total)) +
  geom_col(fill = "steelblue") +
  coord_flip() +
  labs(
    title = "Top 10 procedimentos mais realizados entre estrangeiros internados no SUS",
    x = "Procedimento",
    y = "Total de internações"
  ) +
  theme_minimal(base_size = 14)
library(dplyr)
top5_paises <- df %>%
  group_by(NACIONAL) %>%
  summarise(total_internacoes = n()) %>%
  arrange(desc(total_internacoes)) %>%
  slice_head(n = 5)
top5_paises
df_top5 <- df %>%
  filter(NACIONAL %in% top5_paises$NACIONAL)
procedimentos_por_pais <- df_top5 %>%
  group_by(NACIONAL, PROC_REA) %>%
  summarise(total = n(), .groups = "drop") %>%
  arrange(NACIONAL, desc(total))
procedimentos_por_pais %>% 
  filter(NACIONAL == top5_paises$NACIONAL[1]) %>%
  head(10)
library(ggplot2)
top_procs_por_pais <- procedimentos_por_pais %>%
  group_by(NACIONAL) %>%
  slice_max(total, n = 10) %>%
  ungroup()
ggplot(top_procs_por_pais, aes(x = reorder(PROC_REA, total), y = total, fill = factor(NACIONAL))) +
  geom_col() +
  coord_flip() +
  facet_wrap(~NACIONAL, scales = "free_y") +
  labs(title = "Top 10 procedimentos por país de nacionalidade",
       x = "Procedimento",
       y = "Número de internações",
       fill = "País (código)") +
  theme_minimal(base_size = 12)
depara <- data.frame(
  PROC_REA = c("0310010039", "0411010034", "0411010026", "0303140151", "0303100044",
               "0310010047", "0301060088", "0415010012", "0411020013", "0303010037"),
  NOME_PROC = c("Parto normal", "Parto cesariano", "Parto cesariano alto risco", 
                "Tratamento respiratório", "Intercorrência gravidez",
                "Parto normal alto risco", "Diagnóstico/urgência clínica médica",
                "Cirurgias múltiplas", "Curetagem pós-abortamento", "Outras doenças bacterianas")
)
library(dplyr)
procedimentos_por_pais <- procedimentos_por_pais %>%
  left_join(depara, by = "PROC_REA")
library(ggplot2)
top_procs_por_pais <- procedimentos_por_pais %>%
  group_by(NACIONAL) %>%
  slice_max(total, n = 10) %>%
  ungroup()
ggplot(top_procs_por_pais, aes(x = reorder(NOME_PROC, total), y = total, fill = factor(NACIONAL))) +
  geom_col() +
  coord_flip() +
  facet_wrap(~NACIONAL, scales = "free_y") +
  labs(title = "Top 10 procedimentos por país de nacionalidade",
       x = "Procedimento",
       y = "Número de internações",
       fill = "País (código)") +
  theme_minimal(base_size = 12)
library(dplyr)
library(ggplot2)
procedimentos_por_pais <- procedimentos_por_pais %>%
  left_join(depara_nacionalidade, by = "NACIONAL") %>%
  mutate(pais = ifelse(is.na(pais), NACIONAL, pais))
procedimentos_por_pais <- procedimentos_por_pais %>%
  left_join(depara, by = "PROC_REA") %>%
  mutate(NOME_PROC = ifelse(is.na(NOME_PROC), PROC_REA, NOME_PROC))
top_procs_por_pais <- procedimentos_por_pais %>%
  group_by(pais) %>%
  slice_max(total, n = 10) %>%
  ungroup()
ggplot(top_procs_por_pais, aes(x = reorder(NOME_PROC, total), y = total, fill = pais)) +
  geom_col() +
  coord_flip() +
  facet_wrap(~pais, scales = "free_y") +
  labs(
    title = "Top 10 procedimentos por país de nacionalidade",
    x = "Procedimento",
    y = "Número de internações",
    fill = "País"
  ) +
  theme_minimal(base_size = 12)
library(dplyr)
library(ggplot2)
procedimentos_por_pais <- procedimentos_por_pais %>%
  mutate(
    pais = depara_nacionalidade$pais[match(NACIONAL, depara_nacionalidade$NACIONAL)],
    pais = ifelse(is.na(pais), NACIONAL, pais)
  )
procedimentos_por_pais <- procedimentos_por_pais %>%
  mutate(
    NOME_PROC = depara$NOME_PROC[match(PROC_REA, depara$PROC_REA)],
    NOME_PROC = ifelse(is.na(NOME_PROC), PROC_REA, NOME_PROC)
  )
top_procs_por_pais <- procedimentos_por_pais %>%
  group_by(pais) %>%
  slice_max(total, n = 10) %>%
  ungroup()
ggplot(top_procs_por_pais, aes(x = reorder(NOME_PROC, total), y = total, fill = pais)) +
  geom_col() +
  coord_flip() +
  facet_wrap(~pais, scales = "free_y") +
  labs(
    title = "Top 10 procedimentos por país de nacionalidade",
    x = "Procedimento",
    y = "Número de internações",
    fill = "País"
  ) +
  theme_minimal(base_size = 12)
library(dplyr)
library(ggplot2)
top5_paises_valor <- df %>%
  group_by(NACIONAL) %>%
  summarise(total_USD = sum(US_TOT, na.rm = TRUE)) %>%
  arrange(desc(total_USD)) %>%
  slice_head(n = 5)
df_top5_valor <- df %>%
  filter(NACIONAL %in% top5_paises_valor$NACIONAL)
valor_por_pais_proc <- df_top5_valor %>%
  group_by(NACIONAL, PROC_REA) %>%
  summarise(total_USD = sum(US_TOT, na.rm = TRUE), .groups = "drop")
valor_por_pais_proc <- valor_por_pais_proc %>%
  mutate(
    pais = depara_nacionalidade$pais[match(NACIONAL, depara_nacionalidade$NACIONAL)],
    pais = ifelse(is.na(pais), NACIONAL, pais)
  )
valor_por_pais_proc <- valor_por_pais_proc %>%
  mutate(
    NOME_PROC = depara$NOME_PROC[match(PROC_REA, depara$PROC_REA)],
    NOME_PROC = ifelse(is.na(NOME_PROC), PROC_REA, NOME_PROC)
  )
top_valor_procs_por_pais <- valor_por_pais_proc %>%
  group_by(pais) %>%
  slice_max(total_USD, n = 10) %>%
  ungroup()
ggplot(top_valor_procs_por_pais, aes(x = reorder(NOME_PROC, total_USD), y = total_USD, fill = pais)) +
  geom_col() +
  coord_flip() +
  facet_wrap(~pais, scales = "free_y") +
  labs(
    title = "Top 10 procedimentos por país de nacionalidade (em valor USD)",
    x = "Procedimento",
    y = "Valor total de internações (USD)",
    fill = "País"
  ) +
  theme_minimal(base_size = 12)
library(ggplot2)
top_valor_procs_por_pais %>%
  group_by(pais) %>%
  summarise(max_total = max(total_USD))
library(ggplot2)
library(scales)
  ggplot(top_valor_procs_por_pais, aes(x = reorder(NOME_PROC, total_USD), y = total_USD, fill = pais)) +
    geom_col() +
    geom_text(aes(label = scales::dollar(total_USD, accuracy = 0.01)), 
              hjust = -0.1, size = 3.5)+
    coord_flip() +
    facet_wrap(~pais, scales = "fixed") +
    labs(
      title = "Top 10 procedimentos por país de nacionalidade (em valor USD)",
      x = "Procedimento",
      y = "Valor total de internações (USD)",
      fill = "País"
    ) +
    theme_minimal(base_size = 12) +
    scale_y_continuous(expand = expansion(mult = c(0, 0.15)))