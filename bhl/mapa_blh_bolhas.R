library(geobr)
library(ggplot2)
library(sf)
library(readr)
library(dplyr)

distantes <- read_csv("municipios_distantes_nv.csv", show_col_types = FALSE)
blhs <- read_csv("cidades_com_blh.csv", show_col_types = FALSE)

estados <- read_state(year = 2020, showProgress = FALSE) %>% st_transform(4326)
brasil <- read_country(year = 2020, showProgress = FALSE) %>% st_transform(4326)

dentro <- function(df) {
  p <- st_as_sf(df, coords = c("longitude", "latitude"), crs = 4326, remove = FALSE)
  df[lengths(st_intersects(p, brasil)) > 0, ]
}

distantes <- dentro(distantes)
blhs <- dentro(blhs)

distantes <- distantes %>% arrange(nv_2024)
destaques <- distantes %>% filter(nv_2024 >= 2000)

mapa <- ggplot() +
  geom_sf(data = estados, fill = "#f7f5ee", color = "#b8b5aa", linewidth = 0.35) +
  geom_sf(data = brasil, fill = NA, color = "#3d3a33", linewidth = 0.55) +
  geom_point(data = blhs,
             aes(x = longitude, y = latitude, shape = "Cidade com BLH"),
             color = "#0b3d2e", fill = "#0b3d2e",
             size = 1.8, stroke = 0.5) +
  geom_point(data = distantes,
             aes(x = longitude, y = latitude, size = nv_2024),
             color = "#1a0000", fill = "#C0392B",
             shape = 21, alpha = 0.75, stroke = 0.4) +
  geom_text(data = destaques,
            aes(x = longitude, y = latitude, label = municipio),
            size = 2.9, fontface = "bold", color = "#1a0000",
            nudge_y = 0.7, check_overlap = TRUE) +
  scale_size_continuous(name = "Nascidos vivos (2024)",
                        range = c(1, 11),
                        breaks = c(100, 500, 1500, 3000, 6000)) +
  scale_shape_manual(values = c("Cidade com BLH" = 17), name = NULL) +
  guides(
    size  = guide_legend(order = 1),
    shape = guide_legend(order = 2, override.aes = list(size = 2.5))
  ) +
  coord_sf(xlim = c(-74, -34), ylim = c(-34, 6), expand = FALSE) +
  labs(
    title = "Onde nascem os bebês mais distantes de um banco de leite humano",
    subtitle = "Cada bolha vermelha é um município a mais de 200 km do BLH mais próximo.\nO tamanho indica quantos bebês nasceram ali em 2024.",
    caption = "Fonte: rBLH/Fiocruz, SINASC/DATASUS 2024 e IBGE. Distância em linha reta.",
    x = NULL, y = NULL
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title = element_text(face = "bold", size = 13),
    plot.subtitle = element_text(color = "grey40", margin = margin(b = 12), lineheight = 1.2),
    plot.caption = element_text(color = "grey50", size = 9, hjust = 0),
    legend.position = "bottom",
    legend.box = "horizontal",
    panel.grid = element_blank(),
    panel.background = element_rect(fill = "white", color = NA),
    axis.text = element_blank(),
    axis.ticks = element_blank()
  )

ggsave("mapa_blh_bolhas.png", mapa, width = 10, height = 10, dpi = 300, bg = "white")
ggsave("mapa_blh_bolhas.pdf", mapa, width = 10, height = 10)

print(mapa)