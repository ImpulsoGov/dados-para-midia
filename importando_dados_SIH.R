library(microdatasus)
library(dplyr)
library(purrr)
ufs <- c("AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS",
         "MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC",
         "SE","SP","TO")
anos <- 2019:2025
baixar_filtrar <- function(uf, ano){
  message("Baixando: ", uf, " - ", ano)
  dados <- fetch_datasus(
    year_start = ano, year_end = ano,
    month_start = 1, month_end = 12,
    uf = uf,
    information_system = "SIH-RD"
  )
  dados %>%
    filter(NACIONAL != "010", !is.na(NACIONAL)) %>%
    mutate(uf = uf, ano = ano)
}
sih_estrangeiros <- map_dfr(ufs, function(uf){
  map_dfr(anos, ~baixar_filtrar(uf, .x))
})
write.csv(sih_estrangeiros, "sih_estrangeiros_2019_2025.csv", row.names = FALSE)
message("✅ Arquivo salvo: sih_estrangeiros_2019_2025.csv")
table(sih_estrangeiros$uf)
length(unique(sih_estrangeiros$uf))
table(sih_estrangeiros$uf, sih_estrangeiros$ano)
expected <- expand.grid(uf = ufs, ano = anos)
missing <- anti_join(expected, sih_estrangeiros %>% select(uf, ano) %>% distinct(),
                     by = c("uf","ano"))
missing
sih_estrangeiros %>%
  count(uf, ano) %>%
  arrange(n)