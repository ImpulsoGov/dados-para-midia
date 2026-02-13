library(dplyr)
library(readr)
library(geobr)
library(ggplot2)
library(shadowtext)
library(ggrepel)
library(sf)
library(scales)
library(httr)
library(jsonlite)
library(readxl)
df <- read_csv("sih_estrangeiros_2019_2025_filtrado_urgencia.csv")
estrangeiros_municipios <- df %>%
  mutate(cod_mun = MUNIC_MOV) %>%
  group_by(cod_mun) %>%
  summarise(total_estrangeiros = n(), .groups = "drop")
municipios_geo <- read_municipality(year = 2020) %>%
  mutate(cod_mun = floor(code_muni / 10))
estados_geo <- read_state(year = 2020)
pop_df <- read_excel("populacao_municipio_2022.xlsx")
pop_df$cod_mun <- substr(pop_df$cod_mun, 1, 6)
pop_df$cod_mun <- as.integer(pop_df$cod_mun)
estrangeiros_municipios$cod_mun <- as.integer(estrangeiros_municipios$cod_mun)
municipios_geo$cod_mun <- as.integer(municipios_geo$cod_mun)
estrangeiros_municipios <- municipios_geo %>%
  left_join(estrangeiros_municipios %>% st_drop_geometry(), by = "cod_mun") %>%
  left_join(pop_df, by = "cod_mun") %>%
  mutate(
    taxa_estrangeiros = (total_estrangeiros / pop) * 100000
  )
top3 <- estrangeiros_municipios %>%
  st_drop_geometry() %>%
  arrange(desc(taxa_estrangeiros)) %>%
  slice_head(n = 3) %>%
  pull(code_muni)
top3_coords <- estrangeiros_municipios %>%
  filter(code_muni %in% top3)
centroides <- st_centroid(top3_coords$geom)
coords <- st_coordinates(centroides)
top3_coords <- cbind(top3_coords, coords)
top3_coords <- top3_coords %>%
  mutate(
    nudge_x_val = case_when(
      name_muni == "Boa Vista" ~ 12,
      name_muni == "Pacaraima" ~ 14,
      name_muni == "Paranhos" ~ -12,
      TRUE ~ 12
    ),
    nudge_y_val = case_when(
      name_muni == "Boa Vista" ~ 6,
      name_muni == "Pacaraima" ~ 6,
      name_muni == "Paranhos" ~ -6,
      TRUE ~ 4
    )
  )
ggplot() +
  geom_sf(data = estrangeiros_municipios, aes(fill = taxa_estrangeiros),
          color = "white", size = 0.1) +
  geom_sf(data = estados_geo, fill = NA, color = "gray40", size = 0.3) +
  geom_sf_text(data = estados_geo, aes(label = abbrev_state),
               size = 3.5, fontface = "bold", color = "gray25") +
  geom_text_repel(
    data = top3_coords,
    aes(
      x = X, y = Y,
      label = paste0(
        name_muni, " – ", abbrev_state, "\n",
        format(round(taxa_estrangeiros, 0), big.mark = ".", decimal.mark = ","), 
        " por 100.000 hab."
      )
    ),
    color = "black",
    size = 3,
    fontface = "bold",
    box.padding = 1,
    segment.color = "gray30",
    segment.size = 0.6,
    arrow = arrow(length = unit(0.18, "inches"), type = "closed"),
    nudge_x = top3_coords$nudge_x_val,
    nudge_y = top3_coords$nudge_y_val
  ) +
  scale_fill_gradientn(
    colours = c("
    na.value = "gray95",
    labels = label_number(big.mark = ".", decimal.mark = ",", accuracy = 1)
  ) +
  labs(
    title = "Taxa de internações de estrangeiros no SUS\npor 100.000 habitantes (2019–ago/2025)",
    subtitle = "Top 3 municípios com maiores taxas",
    fill = "Taxa",
    caption = "Fonte: SIH/SUS – Sistema de Informações Hospitalares do SUS (DATASUS)"
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(size = 16, face = "bold"),
    plot.subtitle = element_text(size = 12),
    legend.title = element_text(face = "bold"),
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    panel.grid = element_blank()
  )
ggsave("mapa_estrangeiros_taxa.png", width = 10, height = 6, dpi = 300)