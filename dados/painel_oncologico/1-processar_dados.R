library(read.dbc)
library(dplyr)

dados_2013 <- read.dbc("./dados/painel_oncologico/POBR2013.dbc", as.is = TRUE)
dados_2014 <- read.dbc("./dados/painel_oncologico/POBR2014.dbc", as.is = TRUE)
dados_2015 <- read.dbc("./dados/painel_oncologico/POBR2015.dbc", as.is = TRUE) 
dados_2016 <- read.dbc("./dados/painel_oncologico/POBR2016.dbc", as.is = TRUE) 
dados_2017 <- read.dbc("./dados/painel_oncologico/POBR2017.dbc", as.is = TRUE) 
dados_2018 <- read.dbc("./dados/painel_oncologico/POBR2018.dbc", as.is = TRUE) 
dados_2019 <- read.dbc("./dados/painel_oncologico/POBR2019.dbc", as.is = TRUE)
dados_2020 <- read.dbc("./dados/painel_oncologico/POBR2020.dbc", as.is = TRUE) 
dados_2021 <- read.dbc("./dados/painel_oncologico/POBR2021.dbc", as.is = TRUE) 
dados_2022 <- read.dbc("./dados/painel_oncologico/POBR2022.dbc", as.is = TRUE) 
dados_2023 <- read.dbc("./dados/painel_oncologico/POBR2023.dbc", as.is = TRUE) 
dados_2024 <- read.dbc("./dados/painel_oncologico/POBR2024.dbc", as.is = TRUE) 
dados_2025 <- read.dbc("./dados/painel_oncologico/POBR2025.dbc", as.is = TRUE) 


dados_completos <- bind_rows(
  dados_2013, 
  dados_2014, 
  dados_2015,
  dados_2016, 
  dados_2017, 
  dados_2018, 
  dados_2019, 
  dados_2020, 
  dados_2021, 
  dados_2022, 
  dados_2023, 
  dados_2024,
  dados_2025
)

unique(dados_completos$ANO_DIAGN)


nrow(dados_completos)
write.csv(dados_completos, "./dados/painel_oncologico/dados_oncologicos_completos.csv")
