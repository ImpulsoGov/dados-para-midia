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

dados_variacao <- dados %>%
  filter(ano %in% c(2019, 2025)) %>%
  select(uf, ano, percentual_dependentes) %>%
  pivot_wider(names_from = ano, values_from = percentual_dependentes, names_prefix = "ano_") %>%
  mutate(variacao = (ano_2025 - ano_2019) * 100) %>%
  select(uf, variacao)

estados <- geobr::read_state(year = 2020, simplified = TRUE)

mapa_dados <- left_join(estados, dados_variacao, by = c("abbrev_state" = "uf"))

ggplot(mapa_dados) +
  geom_sf(aes(fill = variacao), color = "white", size = 0.2) +
  geom_sf_label(aes(label = paste(abbrev_state, sprintf("%.1f%%", variacao))), size = 2.5, color = "black", fontface = "bold",
                fill = "white", alpha = 0.8, label.r = unit(0.15, "lines")) +
  scale_fill_gradientn(colors = c("#FFFF00", "#FFA500", "#FF0000", "#B22222", "#8B0000"),
                       na.value = "grey80",
                       name = "Variação Percentual SUS-Dependente (2019-2025)") +
  labs(title = "Variação do Percentual da População SUS-Dependente por Estado (2019-2025) - Pessoas Idosas",
       caption = "Fonte: ANS e IBGE") +
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

ggsave("./resultados/mapa_variacao_sus_dependente_2019_2025.png", width = 12, height = 8, dpi = 600, bg = "white")
