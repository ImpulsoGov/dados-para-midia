if (!require(geobr)) install.packages("geobr")
if (!require(ggplot2)) install.packages("ggplot2")
if (!require(sf)) install.packages("sf")
if (!require(dplyr)) install.packages("dplyr")
if (!require(readxl)) install.packages("readxl")
if (!require(tidyr)) install.packages("tidyr")

library(geobr)
library(ggplot2)
library(sf)
library(dplyr)
library(readxl)
library(tidyr)

dados <- read_excel("./dados/merged_ans_populacao.xlsx")

dados_sus <- dados %>%
  mutate(percentual_sus_dependente = ((populacao - beneficiarios) / populacao) * 100) %>%
  select(ano, uf, percentual_sus_dependente)

dados_wide <- dados_sus %>%
  pivot_wider(names_from = ano, values_from = percentual_sus_dependente, names_prefix = "sus_")

dados_variacao <- dados_wide %>%
  mutate(variacao_percentual = sus_2024 - sus_2020) %>%
  select(uf, variacao_percentual)

estados <- geobr::read_state(year = 2020, simplified = TRUE)

mapa_dados <- left_join(estados, dados_variacao, by = c("abbrev_state" = "uf"))

ggplot(mapa_dados) +
  geom_sf(aes(fill = variacao_percentual), color = "white", size = 0.2) +
  geom_sf_label(aes(label = paste(abbrev_state, ifelse(variacao_percentual >= 0, "+", ""), sprintf("%.0f%%", variacao_percentual))), size = 2.5, color = "black", fontface = "bold",
                fill = "white", alpha = 0.8, label.r = unit(0.15, "lines")) +
  scale_fill_gradientn(colors = c("#FFD700", "#FF8C00", "#FF0000", "#B22222", "#8B0000"),
                       na.value = "grey80",
                       name = "Variação Percentual (%)") +
  labs(title = "Variação Percentual SUS-Dependente por Estado (2020-2024) - Pessoas Idosas",
       caption = "Fonte: ANS + IBGE") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(hjust = 0.5, size = 14),
        plot.subtitle = element_text(hjust = 0.5, size = 10),
        plot.caption = element_text(hjust = 0.5, size = 10),
        panel.grid = element_blank(),
        panel.background = element_rect(fill = "white", color = NA),
        plot.background = element_rect(fill = "white", color = NA),
        axis.text = element_blank(),
        axis.ticks = element_blank(),
        legend.key.size = unit(0.8, "cm"),
        legend.key.width = unit(3, "cm"),
        legend.text = element_text(size = 8),
        legend.title = element_text(size = 10))

ggsave("./resultados/mapa_variacao_ans_uf.png", width = 12, height = 8, dpi = 600, bg = "white")
