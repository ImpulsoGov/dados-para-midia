library(dplyr)
library(readr)
library(geobr)
library(ggplot2)
library(shadowtext)
library(ggrepel)
library(sf)
library(scales)
df <- read_csv("sih_estrangeiros_2019_2025_filtrado_urgencia.csv")
estrangeiros_municipios <- df %>%
  mutate(code_muni = MUNIC_MOV)
estrangeiros_municipios <- estrangeiros_municipios %>%
  group_by(code_muni) %>%
  summarise(total_estrangeiros = n(), .groups = "drop")
municipios_geo <- municipios_geo %>%
  mutate(code_muni = as.numeric(substr(as.character(code_muni), 1, nchar(code_muni) - 1)))
estrangeiros_municipios <- estrangeiros_municipios %>%
  left_join(municipios_geo, by = "code_muni")
top20_municipios <- estrangeiros_municipios %>%
  arrange(desc(total_estrangeiros)) %>%
  slice_head(n = 20)
top20_municipios %>%
  select(name_muni, abbrev_state, total_estrangeiros)
df <- read_csv("sih_estrangeiros_2019_2025_filtrado_urgencia.csv")
estrangeiros_municipios <- df %>%
  group_by(MUNIC_MOV) %>%
  summarise(total_estrangeiros = n(), .groups = "drop") %>%
  mutate(code_muni = as.numeric(MUNIC_MOV))
municipios_geo <- read_municipality(year = 2020) %>%
  mutate(code_muni = floor(code_muni / 10))
estados_geo <- read_state(year = 2020)
dados_mapa <- municipios_geo %>%
  left_join(estrangeiros_municipios, by = "code_muni")
top5 <- dados_mapa %>%
  st_drop_geometry() %>%
  arrange(desc(total_estrangeiros)) %>%
  slice_head(n = 3)
top5_coords <- dados_mapa %>%
  filter(code_muni %in% top5$code_muni)
centroides <- st_centroid(top5_coords$geom)
coords <- st_coordinates(centroides)
top5_coords <- cbind(top5_coords, coords)
top5_coords <- top5_coords %>%
  mutate(
    geom = if_else(
      name_muni == "Chapecó" & abbrev_state == "SC",
      geom,
      geom
    )
  )
top5_coords <- top5_coords %>%
  mutate(
    nudge_x_val = case_when(
      name_muni == "Foz Do Iguaçu" ~ -6,   
      name_muni == "São Paulo" ~ 6,        
      name_muni == "Chapecó" ~ -6,         
      TRUE ~ 8                             
    ),
    nudge_y_val = case_when(
      name_muni == "Foz Do Iguaçu" ~ 2,
      name_muni == "São Paulo" ~ -2,
      name_muni == "Chapecó" ~ 3,          
      TRUE ~ 2
    )
  )
ggplot() +
  geom_sf(data = dados_mapa, aes(fill = total_estrangeiros), color = "white", size = 0.1) +
  geom_sf(data = estados_geo, fill = NA, color = "gray40", size = 0.3) +
  geom_sf_text(data = estados_geo, aes(label = abbrev_state),
               size = 3.5, fontface = "bold", color = "gray25") +
  geom_text_repel(
    data = top5_coords,
    aes(
      x = X, y = Y,
      label = paste0(
        name_muni, " – ", abbrev_state, "\n",
        format(total_estrangeiros, big.mark = ".", decimal.mark = ",")
      )
    ),
    color = "black",
    size = 4,
    fontface = "bold",
    box.padding = 1,
    segment.color = "gray30",
    segment.size = 0.6,
    segment.curvature = 0.3,
    segment.ncp = 5,
    arrow = arrow(length = unit(0.18, "inches"), type = "closed"),
    nudge_x = top5_coords$nudge_x_val,
    nudge_y = top5_coords$nudge_y_val
  ) +
  scale_fill_gradientn(
    colours = c("
    trans = "log10",
    na.value = "gray95",
    labels = label_number(
      big.mark = ".", decimal.mark = ",",
      accuracy = 1
    ),
    breaks = c(500, 1000, 3000, 7000, 15000, 30000),
    guide = guide_colorbar(
      barheight = unit(6, "cm"),
      barwidth = unit(0.6, "cm"),
      title.position = "top",
      title.hjust = 0.5,
      label.position = "right"
    )
  ) +
  labs(
    title = "Internações com urgência de pessoas estrangeiras no SUS (2019–agosto/2025)",
    subtitle = "Top 5 municípios com maior número de internações de urgência",
    fill = "Internações (escala logarítmica)",
    caption = "Fonte: SIH/SUS – Sistema de Informações Hospitalares do SUS (DATASUS)"
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title = element_text(size = 16, face = "bold"),
    plot.subtitle = element_text(size = 12),
    legend.title = element_text(face = "bold"),
    legend.text = element_text(size = 10),
    legend.position = "right",
    legend.box.margin = margin(10, 10, 10, 10),
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    panel.grid = element_blank()
  )