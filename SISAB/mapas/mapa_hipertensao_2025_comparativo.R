# Instalar pacotes se necessário
if (!require(geobr)) install.packages("geobr")
if (!require(ggplot2)) install.packages("ggplot2")
if (!require(sf)) install.packages("sf")
if (!require(dplyr)) install.packages("dplyr")
if (!require(RColorBrewer)) install.packages("RColorBrewer")
if (!require(readxl)) install.packages("readxl")
if (!require(gridExtra)) install.packages("gridExtra")
if (!require(grid)) install.packages("grid")

library(geobr)
library(ggplot2)
library(sf)
library(dplyr)
library(RColorBrewer)
library(readxl)
library(gridExtra)
library(grid)

# Carregar dados dos arquivos consolidados
dados_com_urgencia <- read_excel("../dados/consolidado_final_com_urgencia.xlsx")
dados_sem_urgencia <- read_excel("../dados/consolidado_final_sem_urgencia.xlsx")

# Filtrar dados de 2025
dados_com_urgencia_2025 <- dados_com_urgencia[dados_com_urgencia$Ano == 2025, ]
dados_sem_urgencia_2025 <- dados_sem_urgencia[dados_sem_urgencia$Ano == 2025, ]

# Calcular taxa por 100.000 habitantes para hipertensão arterial
dados_com_urgencia_2025$hipertensao_100k <- (dados_com_urgencia_2025$`Hipertensão arterial` / dados_com_urgencia_2025$dependentes_do_sus) * 100000
dados_sem_urgencia_2025$hipertensao_100k <- (dados_sem_urgencia_2025$`Hipertensão arterial` / dados_sem_urgencia_2025$dependentes_do_sus) * 100000

# Carregar geometria dos estados
estados <- geobr::read_state(year = 2020, simplified = TRUE)

# Fazer join dos dados com a geometria
mapa_com_urgencia <- left_join(estados, dados_com_urgencia_2025, by = c("abbrev_state" = "Uf"))
mapa_sem_urgencia <- left_join(estados, dados_sem_urgencia_2025, by = c("abbrev_state" = "Uf"))

# Definir escala de cores para ambos os mapas
cores_mapa <- brewer.pal(9, "YlOrRd")

# Calcular limites independentes para cada mapa
min_urgencia <- min(mapa_com_urgencia$hipertensao_100k, na.rm = TRUE)
max_urgencia <- max(mapa_com_urgencia$hipertensao_100k, na.rm = TRUE)
min_sem_urgencia <- min(mapa_sem_urgencia$hipertensao_100k, na.rm = TRUE)
max_sem_urgencia <- max(mapa_sem_urgencia$hipertensao_100k, na.rm = TRUE)

# Criar mapa para atendimentos COM urgência (escala independente)
mapa1 <- ggplot(mapa_com_urgencia) +
  geom_sf(aes(fill = hipertensao_100k), color = "white", size = 0.2) +
  geom_sf_label(aes(label = abbrev_state), size = 5, color = "black", fontface = "bold",
                fill = "white", alpha = 0.8, label.r = unit(0.1, "lines")) +
  scale_fill_gradientn(colors = cores_mapa, na.value = "grey80",
                       name = "Taxa por 100.000 hab.",
                       limits = c(min_urgencia, max_urgencia)) +
  labs(title = "Gráfico 1: Atendimentos de hipertensão arterial com urgência") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(hjust = 0.5, size = 16, face = "bold", margin = margin(t = 20, b = 10)),
        plot.subtitle = element_text(hjust = 0.5, size = 9, color = "gray50"),
        panel.grid = element_blank(),
        panel.background = element_rect(fill = "white", color = NA),
        plot.background = element_rect(fill = "white", color = NA),
        axis.text = element_blank(),
        axis.ticks = element_blank(),
        legend.key.size = unit(0.6, "cm"),
        legend.key.width = unit(2, "cm"),
        legend.text = element_text(size = 10),
        legend.title = element_text(size = 12))

# Criar mapa para atendimentos SEM urgência (escala independente)
mapa2 <- ggplot(mapa_sem_urgencia) +
  geom_sf(aes(fill = hipertensao_100k), color = "white", size = 0.2) +
  geom_sf_label(aes(label = abbrev_state), size = 5, color = "black", fontface = "bold",
                fill = "white", alpha = 0.8, label.r = unit(0.1, "lines")) +
  scale_fill_gradientn(colors = cores_mapa, na.value = "grey80",
                       name = "Taxa por 100.000 hab.",
                       limits = c(min_sem_urgencia, max_sem_urgencia)) +
  labs(title = "Gráfico 2: Atendimentos de hipertensão arterial sem urgência") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(hjust = 0.5, size = 16, face = "bold", margin = margin(t = 20, b = 10)),
        plot.subtitle = element_text(hjust = 0.5, size = 9, color = "gray50"),
        panel.grid = element_blank(),
        panel.background = element_rect(fill = "white", color = NA),
        plot.background = element_rect(fill = "white", color = NA),
        axis.text = element_blank(),
        axis.ticks = element_blank(),
        legend.key.size = unit(0.6, "cm"),
        legend.key.width = unit(2, "cm"),
        legend.text = element_text(size = 10),
        legend.title = element_text(size = 12))

# Combinar os dois mapas lado a lado
mapa_combinado <- grid.arrange(mapa1, mapa2, ncol = 2,
                              top = textGrob("Atendimentos de hipertensão arterial em pessoas idosas que dependem\nexclusivamente do SUS por estado — 2025",
                                           gp = gpar(fontsize = 20, fontface = "bold")),
                              bottom = textGrob("Fonte: Dados SISAB e ANS",
                                              gp = gpar(fontsize = 14)))

# Salvar o mapa combinado
ggsave("../resultados/mapa_hipertensao_2025_comparativo.png",
       plot = mapa_combinado,
       width = 24, height = 14, dpi = 600, bg = "white")