library(microdatasus)
library(dplyr)
library(purrr)
ufs <- c("AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS",
         "MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC",
         "SE","SP","TO")
anos <- 2019:2025
baixar_filtrar_sia <- function(uf, ano){
  message("Baixando SIA: ", uf, " - ", ano)
  tryCatch({
    dados <- fetch_datasus(
      year_start = ano, year_end = ano,
      month_start = 1, month_end = 12,
      uf = uf,
      information_system = "SIA-PA"
    )
    if("NACIONAL" %in% names(dados)){
      dados <- dados %>%
        filter(NACIONAL != "010", !is.na(NACIONAL)) %>%
        mutate(uf = uf, ano = ano)
    } else {
      message("⚠️ Coluna NACIONAL não encontrada para ", uf, " - ", ano)
      dados <- dados %>% mutate(uf = uf, ano = ano)
    }
    return(dados)
  }, error = function(e){
    message("❌ Erro ao baixar ", uf, " - ", ano, ": ", e$message)
    return(NULL)
  })
}
sia_estrangeiros <- map_dfr(ufs, function(uf){
  map_dfr(anos, ~baixar_filtrar_sia(uf, .x))
})
write.csv(sia_estrangeiros, "sia_estrangeiros_2019_2025.csv", row.names = FALSE)
message("✅ Arquivo salvo: sia_estrangeiros_2019_2025.csv")
table(sia_estrangeiros$uf)
length(unique(sia_estrangeiros$uf))
table(sia_estrangeiros$uf, sia_estrangeiros$ano)
expected <- expand.grid(uf = ufs, ano = anos)
missing <- anti_join(expected, 
                     sia_estrangeiros %>% select(uf, ano) %>% distinct(),
                     by = c("uf","ano"))
print(missing)
sia_estrangeiros %>%
  count(uf, ano) %>%
  arrange(n)