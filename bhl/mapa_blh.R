library(geobr)
library(ggplot2)
library(sf)
library(readr)
library(dplyr)

distantes <- read_csv("municipios_distantes.csv", show_col_types = FALSE)
blhs <- read_csv("cidades_com_blh.csv", show_col_types = FALSE)

distantes <- distantes %>%
  mutate(faixa = cut(distancia_km,
                     breaks = c(0, 300, 500, Inf),
                     labels = c("200 a 300 km", "300 a 500 km", "Mais de 500 km"),
                     right = FALSE))

estados <- read_state(year = 2020, showProgress = FALSE) %>% st_transform(4326)
brasil <- read_country(year = 2020, showProgress = FALSE) %>% st_transform(4326)

filtrar_dentro_brasil <- function(df) {
  pontos <- st_as_sf(df, coords = c("longitude", "latitude"), crs = 4326, remove = FALSE)
  dentro <- lengths(st_intersects(pontos, brasil)) > 0
  df[dentro, ]
}

distantes <- filtrar_dentro_brasil(distantes)
blhs <- filtrar_dentro_brasil(blhs)

distantes <- distantes %>% arrange(distancia_km)

cores_faixa <- c(
  "200 a 300 km"   = "#E8C4B8",
  "300 a 500 km"   = "#D64545",
  "Mais de 500 km" = "#5C0A0A"
)

tamanhos_faixa <- c(
  "200 a 300 km"   = 1.2,
  "300 a 500 km"   = 2.6,
  "Mais de 500 km" = 4.2
)

alphas_faixa <- c(
  "200 a 300 km"   = 0.55,
  "300 a 500 km"   = 0.85,
  "Mais de 500 km" = 0.95
)

mapa <- ggplot() +
  geom_sf(data = estados, fill = "#f7f5ee", color = "#b8b5aa", linewidth = 0.35) +
  geom_sf(data = brasil, fill = NA, color = "#3d3a33", linewidth = 0.55) +
  geom_point(data = distantes,
             aes(x = longitude, y = latitude, color = faixa, size = faixa, alpha = faixa),
             stroke = 0) +
  geom_point(data = filter(distantes, faixa == "Mais de 500 km"),
             aes(x = longitude, y = latitude),
             shape = 21, fill = "#5C0A0A", color = "#1a0000",
             size = 4.2, stroke = 0.6) +
  geom_point(data = blhs,
             aes(x = longitude, y = latitude, shape = "Cidade com BLH"),
             color = "#0b3d2e", fill = "#0b3d2e",
             size = 2.2, stroke = 0.6) +
  scale_color_manual(values = cores_faixa, name = "Distância ao BLH mais próximo") +
  scale_size_manual(values = tamanhos_faixa, name = "Distância ao BLH mais próximo") +
  scale_alpha_manual(values = alphas_faixa, guide = "none") +
  scale_shape_manual(values = c("Cidade com BLH" = 17), name = NULL) +
  guides(
    color = guide_legend(order = 1, override.aes = list(size = c(2, 3, 4.5), alpha = 1)),
    size  = guide_legend(order = 1),
    shape = guide_legend(order = 2, override.aes = list(size = 2.5, color = "#0b3d2e"))
  ) +
  coord_sf(xlim = c(-74, -34), ylim = c(-34, 6), expand = FALSE) +
  labs(
    title = "Os 400 municípios brasileiros mais distantes de um banco de leite humano",
    subtitle = "Distância em linha reta entre a sede do município e o BLH mais próximo",
    caption = "Fonte: Rede Brasileira de Bancos de Leite Humano (rBLH/Fiocruz) e IBGE",
    x = NULL, y = NULL
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title = element_text(face = "bold", size = 13),
    plot.subtitle = element_text(color = "grey40", margin = margin(b = 12)),
    plot.caption = element_text(color = "grey50", size = 9, hjust = 0),
    legend.position = "bottom",
    legend.box = "horizontal",
    panel.grid = element_blank(),
    panel.background = element_rect(fill = "white", color = NA),
    axis.text = element_blank(),
    axis.ticks = element_blank()
  )

ggsave("mapa_blh.png", mapa, width = 9, height = 9, dpi = 300, bg = "white")
ggsave("mapa_blh.pdf", mapa, width = 9, height = 9)

print(mapa)