if (!require(ggplot2)) install.packages("ggplot2")
if (!require(dplyr)) install.packages("dplyr")
if (!require(readxl)) install.packages("readxl")

library(ggplot2)
library(dplyr)
library(readxl)

dados <- read_excel("./dados/merged_ans_populacao.xlsx")

regioes <- data.frame(
  uf = c("AC", "AM", "AP", "PA", "RO", "RR", "TO", "AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE", "DF", "GO", "MS", "MT", "ES", "MG", "RJ", "SP", "PR", "RS", "SC"),
  regiao = c(rep("Norte", 7), rep("Nordeste", 9), rep("Centro-Oeste", 4), rep("Sudeste", 4), rep("Sul", 3))
)

dados <- left_join(dados, regioes, by = "uf")

dados_regioes <- dados %>%
  group_by(ano, regiao) %>%
  summarise(
    total_populacao = sum(populacao, na.rm = TRUE),
    total_dependentes = sum(dependentes_do_sus, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(percentual_sus_dependente = (total_dependentes / total_populacao) * 100)

dados_brasil <- dados %>%
  group_by(ano) %>%
  summarise(
    total_populacao = sum(populacao, na.rm = TRUE),
    total_dependentes = sum(dependentes_do_sus, na.rm = TRUE)
  ) %>%
  mutate(
    percentual_sus_dependente = (total_dependentes / total_populacao) * 100,
    regiao = "Brasil"
  )

dados_combinados <- bind_rows(dados_regioes, dados_brasil)

dados_combinados$regiao <- factor(dados_combinados$regiao, levels = c("Norte", "Nordeste", "Sul", "Brasil", "Centro-Oeste", "Sudeste"))

dados_combinados <- dados_combinados %>%
  mutate(nudge_value = case_when(
    regiao == "Brasil" ~ 1.5,
    regiao == "Norte" ~ 3.0,
    regiao == "Nordeste" ~ 4.5,
    regiao == "Centro-Oeste" ~ 6.0,
    regiao == "Sudeste" ~ 7.5,
    regiao == "Sul" ~ 9.0
  ))

ggplot(dados_combinados, aes(x = ano, y = percentual_sus_dependente, color = regiao, group = regiao)) +
  geom_line(linewidth = 1.2) +
  scale_color_manual(values = c("Norte" = "#E95F3A", "Nordeste" = "#EF8264", "Sul" = "#9C462F", "Brasil" = "#114354", "Centro-Oeste" = "#81CBD3", "Sudeste" = "#632F21")) +
  scale_x_continuous(breaks = 2019:2025, limits = c(2019, 2025)) +
  scale_y_continuous(limits = c(0, NA)) +
  labs(
    title = "Percentual de pessoas idosas dependentes exclusivamente do SUS por região (2019-2025)",
    x = "Ano",
    y = "Percentual (%)",
    color = "Região",
    caption = "Fonte: ANS (dados de junho de cada ano) e IBGE"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 14),
    plot.caption = element_text(hjust = 0.5, size = 10),
    axis.text = element_text(size = 10),
    axis.title = element_text(size = 12),
    panel.grid = element_blank(),
    legend.position = "bottom",
    plot.margin = margin(5, 5, 5, 5)
  ) +
  guides(color = guide_legend(override.aes = list(linetype = "solid", shape = NA)))

ggsave("./resultados/linha_sus_dependente_brasil.png", width = 10, height = 6, dpi = 600, bg = "white")
