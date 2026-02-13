library(microdatasus)
library(dplyr)
library(purrr)
ufs <- c("AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS",
         "MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC",
         "SE","SP","TO")
anos <- 2019:2019
baixar_contar <- function(uf, ano){
  message("Baixando: ", uf, " - ", ano)
  fetch_datasus(
    year_start = ano, year_end = ano,
    month_start = 1, month_end = 12,
    uf = uf,
    information_system = "SIH-RD"
  ) %>%
    summarise(
      total_internacoes = n(),
      .groups = "drop"
    ) %>%
    mutate(uf = uf, ano = ano)
}
sih_totais <- map_dfr(ufs, function(uf){
  map_dfr(anos, ~baixar_contar(uf, .x))
})
sih_totais
write.csv(sih_totais, "sih_totais.csv", row.names = FALSE)