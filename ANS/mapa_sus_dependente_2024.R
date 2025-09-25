if (!require(geobr)) install.packages("geobr")
if (!require(ggplot2)) install.packages("ggplot2")
if (!require(sf)) install.packages("sf")
if (!require(dplyr)) install.packages("dplyr")
if (!require(readxl)) install.packages("readxl")

library(geobr)
library(ggplot2)
library(sf)
library(dplyr)
library(readxl)

dados <- read_excel("./dados/merged_ans_populacao.xlsx")

dados_2024 <- dados %>%
  filter(ano == 2024) %>%
  mutate(percentual_sus_dependente = ((populacao - beneficiarios) / populacao) * 100) %>%
  select(uf, percentual_sus_dependente)

estados <- geobr::read_state(year = 2020, simplified = TRUE)

mapa_dados <- left_join(estados, dados_2024, by = c("abbrev_state" = "uf"))

ggplot(mapa_dados) +
  geom_sf(aes(fill = percentual_sus_dependente), color = "white", size = 0.2) +
  geom_sf_label(aes(label = paste(abbrev_state, sprintf("%.0f%%", percentual_sus_dependente))), size = 2.5, color = "black", fontface = "bold",
                fill = "white", alpha = 0.8, label.r = unit(0.15, "lines")) +
  scale_fill_gradientn(colors = c("#FFD700", "#FF8C00", "#FF0000", "#B22222", "#8B0000"),
                       na.value = "grey80",
                       name = "Percentual SUS-Dependente (%)") +
  labs(title = "Percentual da População SUS-Dependente por Estado (2024) - Pessoas Idosas",
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

ggsave("./resultados/mapa_sus_dependente_2024.png", width = 12, height = 8, dpi = 600, bg = "white")
