library(dplyr)
library(readr)
library(geobr)
library(readxl)
library(openxlsx)
df <- read_csv("sih_estrangeiros_2019_2025_filtrado_urgencia.csv")
estrangeiros_municipios <- df %>%
  mutate(cod_mun = MUNIC_MOV) %>%
  group_by(cod_mun) %>%
  summarise(total_estrangeiros = n(), .groups = "drop")
municipios_geo <- read_municipality(year = 2020) %>%
  mutate(cod_mun = floor(code_muni / 10)) %>%
  select(cod_mun, name_muni, abbrev_state)
estrangeiros_municipios$cod_mun <- as.integer(estrangeiros_municipios$cod_mun)
municipios_geo$cod_mun <- as.integer(municipios_geo$cod_mun)
tabela_estrangeiros <- estrangeiros_municipios %>%
  left_join(municipios_geo, by = "cod_mun")
top20 <- tabela_estrangeiros %>%
  arrange(desc(total_estrangeiros)) %>%
  slice_head(n = 20) %>%
  select(name_muni, abbrev_state, total_estrangeiros)
print(top20)
write.xlsx(top20, file = "top20_municipios_estrangeiros_absoluto.xlsx")