if (!require(geobr)) install.packages("geobr")
if (!require(ggplot2)) install.packages("ggplot2")
if (!require(sf)) install.packages("sf")
if (!require(dplyr)) install.packages("dplyr")
if (!require(RColorBrewer)) install.packages("RColorBrewer")
if (!require(gridExtra)) install.packages("gridExtra")

library(geobr)
library(ggplot2)
library(sf)
library(dplyr)
library(RColorBrewer)
library(gridExtra)

dados <- read.csv("../dados/cids_demencia/taxas_demencia_por_uf_ano.csv")

dados_2024 <- dados[dados$Ano == 2024, ]
dados_2025 <- dados[dados$Ano == 2025, ]

estados <- geobr::read_state(year = 2020, simplified = TRUE)

mapa_2024 <- left_join(estados, dados_2024, by = c("abbrev_state" = "UF"))
mapa_2025 <- left_join(estados, dados_2025, by = c("abbrev_state" = "UF"))

cores_mapa <- brewer.pal(9, "YlOrRd")

plot_2024 <- ggplot(mapa_2024) +
  geom_sf(aes(fill = demencia_100k), color = "white", size = 0.2) +
  geom_sf_label(aes(label = abbrev_state), size = 2.5, color = "black", fontface = "bold",
                fill = "white", alpha = 0.8, label.r = unit(0.15, "lines")) +
  scale_fill_gradientn(colors = cores_mapa, na.value = "grey80",
                        name = "Taxa por 100.000 hab.") +
  labs(title = "Taxa de atendimentos de demências (CID-10) por estado — 2024",
       caption = "Fonte: Dados SISAB e IBGE") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
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

plot_2025 <- ggplot(mapa_2025) +
  geom_sf(aes(fill = demencia_100k), color = "white", size = 0.2) +
  geom_sf_label(aes(label = abbrev_state), size = 2.5, color = "black", fontface = "bold",
                fill = "white", alpha = 0.8, label.r = unit(0.15, "lines")) +
  scale_fill_gradientn(colors = cores_mapa, na.value = "grey80",
                        name = "Taxa por 100.000 hab.") +
  labs(title = "Taxa de atendimentos de demências (CID-10) por estado — 2025",
       caption = "Fonte: Dados SISAB e IBGE") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
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

combined_plot <- grid.arrange(plot_2024, plot_2025, ncol = 2)

ggsave("../resultados/mapa_demencia_2024_2025.png", combined_plot, width = 20, height = 9, dpi = 600, bg = "white")