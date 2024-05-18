"""
Main file
"""

from bs4 import BeautifulSoup as bs
import pandas as pd

# import numpy as np
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from services.helper import filter_df, clean_df, rank_columns, groupby_count, groupby_mean, weighted_average, clear_rank_columns, print_means
# import openpyxl as op

print("--- iniciando ---")

# Abrindo webdriver firefox
print("Abrindo webdriver e carregando dados do site")
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.get("https://www.fundsexplorer.com.br/ranking")

# Carregando dados da web
soup = bs(driver.page_source, "lxml")

# Fechando webdriver firefox
driver.close()

# Selecionando dados do xml para colocalos no dataframe
print("carregando dados em dataframe")
table = soup.find("table", class_="default-fiis-table__container__table")

data = []
row = []
column_names = [th.text for th in table.find_all("th")]

for tr in table.find_all("tr"):
    for td in tr.find_all("td"):
        if td.text == "N/A":
            row.append("0")
        else:
            row.append(td.text)
    data.append(row[:])
    row.clear()

data.pop(0)
# Populando dataframe com dados selecionados
df = pd.DataFrame(data, columns=column_names)

unclean_df = df.copy(deep=True)

## Tipando dados categóricos
print("tipando dados categóricos")
categorical_columns = ["Fundos", "Setor"]
idx_cat = df[df["Setor"].isna()].index
df.drop(idx_cat, inplace=True)
df[categorical_columns] = df[categorical_columns].astype("category")

## Tipando e adaptando dados flutuantes
print("tipando e adaptando dados flutuantes")
col_floats = list(df.iloc[:, 2:].columns)

df[col_floats] = df[col_floats].map(
    lambda x: str(x)
    .replace("R$", "")
    #    .replace(".0", "")
    .replace(".", "")
    .replace("%", "")
    .replace(",", ".")
)

df[col_floats] = df[col_floats].astype("float")

## Tipando e adaptando dados inteiros
print("tipando e adaptando dados inteiros")
integer_columns = ["Quant. Ativos", "Num. Cotistas"]
idx_int = df[df["Quant. Ativos"].isna()].index
df.drop(idx_int, inplace=True)
df[integer_columns] = df[integer_columns].astype("int64")

# limpando dados sem valor do df
print("limpando dados sem valor")
cleaned_df = clean_df(df)

# df_count = groupby_count(cleaned_df)
# df_group_mean = groupby_mean(cleaned_df)
# print_means(cleaned_df)

# filtrando dados via parametros
print("realizando filtragem de dados")
filtered_df = filter_df(cleaned_df)

# ranqueamento de colunas
print("ranqueando colunas de indices importantes")
ranked_df = rank_columns(filtered_df)

# media ponderada sobre as colunas ranqueadas
print("aplicando media ponderada")
weighted_df = weighted_average(ranked_df)
weighted_df.sort_values(["Weighted rank"], inplace=True)

final_df = clear_rank_columns(weighted_df)
# df_count = groupby_count(final_df)

print("exportando para excell")
with pd.ExcelWriter("output.xlsx") as writer:
    final_df.to_excel(writer, sheet_name="weighted_rank")
    # weighted_df.to_excel(writer, sheet_name="weights")
    # df_count.to_excel(writer, sheet_name="setor_count")
    # df_group_mean.to_excel(writer, sheet_name="setor_means")
    # unclean_df.to_excel(writer, sheet_name="unclean_df")
    # cleaned_df.to_excel(writer, sheet_name="cleaned_df")
    # filtered_df.to_excel(writer, sheet_name="filtered_df")
    # ranked_df.to_excel(writer, sheet_name="ranked_df")

print("--- finalizado! ---")
