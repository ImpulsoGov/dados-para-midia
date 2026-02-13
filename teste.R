library(ggplot2)
library(dplyr)
library(sf)
library(rnaturalearth)
library(rnaturalearthdata)
library(cowplot)
library(scales)
library(readr)
options(repos = c(CRAN = "https://cloud.r-project.org")) 
install.packages("ggspatial")
library(ggspatial)
df <- read_csv("dados_paises_sus_estrangeiros.csv")
df <- df %>%
  group_by(pais) %>%
  summarise(qtd = n())
total_geral <- 64497987
df <- df %>%
  mutate(porcentagem_total = (qtd / total_geral) * 100)
df <- df %>%
  mutate(
    pais_formatado = dplyr::recode(
      pais,
      "VENEZUELA" = "Venezuela",
      "BOLIVIA" = "Bolívia",
      "PARAGUAI" = "Paraguai",
      "ESTADOS UNIDOS" = "Estados Unidos",
      "REINO UNIDO" = "Reino Unido",
      "NOVA ZELÂNDIA" = "Nova Zelândia"
    )
  )
library(ggplot2)
library(dplyr)
library(sf)
library(rnaturalearth)
library(rnaturalearthdata)
library(cowplot)
library(scales)
library(readr)
options(repos = c(CRAN = "https://cloud.r-project.org")) 
install.packages("ggspatial")
library(ggspatial)
df <- read_csv("dados_paises_sus_estrangeiros.csv")
df <- df %>%
  group_by(pais) %>%
  summarise(qtd = n())
total_geral <- 64497987
df <- df %>%
  mutate(porcentagem_total = (qtd / total_geral) * 100)
df <- df %>%
  mutate(
    pais_formatado = dplyr::recode(
      pais,
      "VENEZUELA" = "Venezuela",
      "BOLIVIA" = "Bolívia",
      "PARAGUAI" = "Paraguai",
      "ESTADOS UNIDOS" = "Estados Unidos",
      "REINO UNIDO" = "Reino Unido",
      "NOVA ZELÂNDIA" = "Nova Zelândia"
    )
  )
world <- ne_countries(scale = "medium", returnclass = "sf") %>%
  mutate(name_pt = dplyr::recode(
    name,
    "United States" = "Estados Unidos",
    "Bolivia" = "Bolívia",
    "Venezuela" = "Venezuela",
    "Paraguay" = "Paraguai",
    "United Kingdom" = "Reino Unido",
    "New Zealand" = "Nova Zelândia"
  ))
dados_geo <- world %>%
  left_join(df, by = c("name_pt" = "pais_formatado"))
plot_continente <- function(data, continente_nome,
                            xlim = NULL, ylim = NULL) {
  ggplot(data) +
    geom_sf(aes(fill = porcentagem_total), color = "white", size = 0.1) +
    scale_fill_gradientn(
      colours = c("
      na.value = "gray90",
      labels = percent_format(accuracy = 0.01),
      name = "% do total"
    ) +
    geom_point(
      aes(x = longitude, y = latitude, size = quantidade_absoluta),
      color = "black",
      alpha = 0.7
    ) +
    scale_size_continuous(name = "Quantidade absoluta") +
    coord_sf(xlim = xlim, ylim = ylim, expand = FALSE) +
    labs(
      title = continente_nome,
      caption = "Fonte: SIHSUS – Sistema de Informações Hospitalares do SUS (DATASUS)"
    ) +
    theme_minimal(base_size = 12) +
    theme(
      legend.position = "bottom",
      plot.title = element_text(size = 16, face = "bold"),
      plot.margin = margin(15, 15, 15, 15)
    )
}
map_as <- dados_geo %>% filter(region_un == "South America")
plot_as <- plot_continente(map_as, "América do Sul")
map_nac <- dados_geo %>% filter(region_un %in% c("North America", "Central America"))
plot_nac <- plot_continente(map_nac, "América do Norte e Central")
map_eu <- dados_geo %>% filter(region_un == "Europe")
plot_eu <- plot_continente(map_eu, "Europa")
map_af <- dados_geo %>% filter(region_un == "Africa")
plot_af <- plot_continente(map_af, "África")
map_asia <- dados_geo %>% filter(region_un == "Asia")
plot_asia <- plot_continente(map_asia, "Ásia")
map_oc <- dados_geo %>% filter(region_un == "Oceania")
plot_oc <- plot_continente(map_oc, "Oceania")
painel_final <- plot_grid(
  plot_as,     plot_nac,
  plot_eu,     plot_af,
  plot_asia,   plot_oc,
  ncol = 2,
  align = "hv",
  labels = NULL
)
ggsave(
  "painel_mapas_sus.png",
  painel_final,
  width = 18,
  height = 22,
  dpi = 300
)