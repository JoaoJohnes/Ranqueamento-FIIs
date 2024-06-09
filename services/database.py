"""
Database helper file
"""

import pandas as pd
import numpy as np


def load_db_append(df, engine, table):
    df.to_sql(table, con=engine, if_exists="append", index=False)
    return


def load_db_replace(df, engine, table):
    df.to_sql(table, con=engine, if_exists="replace", index=False)


def load_history(df, engine, source, date):
    df_extraction_history = pd.read_sql(sql="extraction_history", con=engine)
    if df_extraction_history.empty:
        new_index = 0
    else:
        last_index = df_extraction_history["id_extraction_history"].iloc[-1]
        new_index = last_index + 1

    df_extraction_history_new = pd.DataFrame(
        data={"id_extraction_history": [new_index], "source": [source], "extraction_date": [date]}
    )
    df_extraction_history_new.to_sql(
        "extraction_history", con=engine, if_exists="append", index=False
    )

    df_sectors = pd.read_sql(sql="sectors", con=engine)

    df_aux = df.copy()

    df_aux["Setor"] = df_aux["Setor"].map(df_sectors.set_index("Setor")["id_sector"])
    df_aux.rename(
        columns={
            "Setor": "id_sector",
            "Fundos": "fund_code",
            "Preço Atual (R$)": "price",
            "Liquidez Diária (R$)": "liquidity",
            "P/VP": "pvp",
            "Último Dividendo": "last_dividend",
            "Dividend Yield": "dy",
            "DY (3M) média": "dy_3m_average",
            "DY (6M) média": "dy_6m_average",
            "DY (12M) média": "dy_12m_average",
            "Variação Preço": "price_variation",
            "Quant. Ativos": "actives_quantity",
            "Volatilidade": "volatility",
            "Num. Cotistas": "total_shareholders",
        },
        inplace=True,
    )

    df_aux.insert(len(df.columns), "id_extraction_history", new_index)
    df_aux.to_sql("funds_history", con=engine, if_exists="append", index=False)


def load_df(engine, table):
    df = pd.read_sql(sql=table, con=engine)
    return df


def get_last_data(engine, extraction_id):
    df = pd.read_sql(
        "SELECT * FROM funds_history WHERE id_extraction_history = %(extraction_id)s",
        params={"extraction_id": extraction_id},
        con=engine,
    )
    df = df.drop(["id_extraction_history"], axis=1)

    df_sectors = pd.read_sql(sql="sectors", con=engine)
    df["id_sector"] = df["id_sector"].map(df_sectors.set_index("id_sector")["Setor"])
    df.rename(
        columns={
            "id_sector": "Setor",
            "fund_code": "Fundos",
            "price": "Preço Atual (R$)",
            "liquidity": "Liquidez Diária (R$)",
            "pvp": "P/VP",
            "last_dividend": "Último Dividendo",
            "dy": "Dividend Yield",
            "dy_3m_average": "DY (3M) média",
            "dy_6m_average": "DY (6M) média",
            "dy_12m_average": "DY (12M) média",
            "price_variation": "Variação Preço",
            "actives_quantity": "Quant. Ativos",
            "volatility": "Volatilidade",
            "total_shareholders": "Num. Cotistas",
        }, 
        inplace=True)

    print(df)

    return df


def get_last_extraction(engine):
    df = pd.read_sql(sql="extraction_history", con=engine)
    if df.empty:
        return None
    df["extraction_date"] = pd.to_datetime(df["extraction_date"])
    month = df["extraction_date"].iloc[-1].month
    year = df["extraction_date"].iloc[-1].year
    index = df["id_extraction_history"].iloc[-1]
    date = [month, year, index]
    return date
