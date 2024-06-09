"""
Main file
"""

from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from services.helper import (
    filter_df,
    clean_df,
    rank_columns,
    weighted_average,
    clear_rank_columns,
)
from services.database import (
    get_last_extraction,
    load_history,
    get_last_data,
)
from datetime import datetime
import sqlalchemy

engine = sqlalchemy.create_engine("mariadb+mariadbconnector://root:Zxc!123456@127.0.0.1:3306/fiis")

print("--- iniciando ---")

current_date = datetime.today().strftime("%Y-%m-%d")
current_month = datetime.today().strftime("%m")
current_year = datetime.today().strftime("%Y")
url = "https://www.fundsexplorer.com.br/ranking"

last_extraction = get_last_extraction(engine)

if last_extraction is None:
    last_extraction = [0, 0, 0]

if (last_extraction[0] < int(current_month)) | (last_extraction[1] < int(current_year)):
    # Abrindo webdriver firefox
    print("Abrindo webdriver e carregando dados do site")
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    driver.get(url)

    # Carregando dados da web
    soup = bs(driver.page_source, "lxml")

    # Fechando webdriver firefox
    driver.close()

    # Selecionando dados do xml para coloca-los no dataframe
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
    initial_df = pd.DataFrame(data, columns=column_names)

    # Limpeza de valores faltantes por garantia
    df = initial_df.dropna(axis=0)

    ## Tipando dados categóricos
    print("tipando dados categóricos")
    categorical_columns = ["Fundos", "Setor"]
    df[categorical_columns] = df[categorical_columns].astype("category")

    ## Tipando e adaptando dados flutuantes
    print("tipando e adaptando dados flutuantes")
    col_floats = list(df.iloc[:, 2:].columns)

    df[col_floats] = df[col_floats].map(
        lambda x: str(x).replace("R$", "").replace(".", "").replace("%", "").replace(",", ".")
    )

    df[col_floats] = df[col_floats].astype("float")

    ## Tipando e adaptando dados inteiros
    print("tipando e adaptando dados inteiros")
    integer_columns = ["Quant. Ativos", "Num. Cotistas"]
    df[integer_columns] = df[integer_columns].astype("int64")

    # limpando dados sem valor do df
    print("limpando dados sem valor")
    cleaned_df = clean_df(df)
    load_history(df=cleaned_df, engine=engine, source=url, date=current_date)

else:
    print("carregando dados da base")
    cleaned_df = get_last_data(engine=engine, extraction_id=last_extraction[2])

# filtrando dados via parametros
print("realizando filtragem de dados")
filtered_df = filter_df(cleaned_df)

# ranqueamento de colunas
print("ranqueando colunas de indices importantes")
ranked_df = rank_columns(filtered_df)

# media ponderada sobre as colunas ranqueadas
print("aplicando media ponderada")
weighted_df = weighted_average(ranked_df)
weighted_df.sort_values(["Rank"], inplace=True)

# limpeza de colunas de ranqueamento
final_df = clear_rank_columns(weighted_df)
# df_count = groupby_count(final_df)

print("exportando para excell")
with pd.ExcelWriter("output.xlsx") as writer:
    final_df.to_excel(writer, sheet_name="ranking")

print("--- finalizado! ---")
