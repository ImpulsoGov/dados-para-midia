library(dplyr)
library(readr)
library(ggplot2)
library(scales)
library(readxl)
library(geobr)
df <- read_csv("sih_estrangeiros_2019_2025_filtrado_urgencia.csv")
foreigners_municipalities <- df %>%
  mutate(mun_code = MUNIC_MOV) %>%
  group_by(mun_code) %>%
  summarise(total_foreigners = n(), .groups = "drop")
municipalities_geo <- read_municipality(year = 2020) %>%
  mutate(mun_code = floor(code_muni / 10)) %>%
  select(mun_code, name_muni, abbrev_state)
pop_df <- read_excel("populacao_municipio_2022.xlsx")
pop_df$mun_code <- substr(pop_df$cod_mun, 1, 6)
pop_df$mun_code <- as.integer(pop_df$mun_code)
foreigners_municipalities$mun_code <- as.integer(foreigners_municipalities$mun_code)
municipalities_geo$mun_code <- as.integer(municipalities_geo$mun_code)
data <- foreigners_municipalities %>%
  left_join(municipalities_geo, by = "mun_code") %>%
  left_join(pop_df, by = "mun_code") %>%
  mutate(
    rate_foreigners = (total_foreigners / pop) * 100000
  ) %>%
  filter(!is.na(rate_foreigners)) %>%
  arrange(desc(rate_foreigners)) %>%
  slice_head(n = 10)
ggplot(data, aes(x = reorder(paste(name_muni, abbrev_state, sep = " - "), rate_foreigners), y = rate_foreigners)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  coord_flip() +
  scale_y_continuous(trans = "log10", labels = label_number(big.mark = ",", accuracy = 1)) +
  labs(
    title = "Top 10 municipalities with highest foreigner\nhospitalization rates in SUS per 100,000 inhabitants",
    x = "Municipality",
    y = "Rate per 100,000 inhabitants (log scale)",
    caption = "Source: SIH/SUS – Hospital Information System of SUS (DATASUS)"
  ) +
  theme_minimal(base_size = 10) +
  theme(
    plot.title = element_text(size = 12, face = "bold"),
    axis.text.y = element_text(size = 8)
  )
ggsave("chart_rate_foreigners.png", width = 10, height = 6, dpi = 300)