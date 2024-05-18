"""
Helper file
"""


def filter_df(df):
    df_pvp = df[["P/VP"]].copy(deep=True)
    df_cot = df[["Num. Cotistas"]].copy(deep=True)
    df_vpc = df[["Variação Preço"]].copy(deep=True)
    df_prc = df[["Preço Atual (R$)"]].copy(deep=True)
    df_lqz = df[["Liquidez Diária (R$)"]].copy(deep=True)
    pvp_max = 1.1
    df_pvp_min = 0.7
    cot_min = 45000
    vpc_min = -4
    vpc_max = 2.5
    prc_min = 1
    lqz_min = 1200000

    filter_ = (
        (df_pvp["P/VP"] <= pvp_max)
        & (df_pvp["P/VP"] >= df_pvp_min)
        & (df_cot["Num. Cotistas"] > cot_min)
        & (df_vpc["Variação Preço"] >= vpc_min)
        & (df_vpc["Variação Preço"] <= vpc_max)
        & (df_prc["Preço Atual (R$)"] >= prc_min)
        & (df_lqz["Liquidez Diária (R$)"] >= lqz_min)
    )

    return df[filter_]


def clean_df(df):
    df_aux = df.drop(df[df["Preço Atual (R$)"] == 0].index)
    df_aux = df_aux.drop(df_aux[df_aux["Num. Cotistas"] == 0].index)
    df_aux = df_aux.drop(df_aux[df_aux["Dividend Yield"] == 0].index)
    df_aux = df_aux.drop(
        [
            "Tax. Gestão",
            "Tax. Performance",
            "Tax. Administração",
            "DY Patrimonial",
            "Variação Patrimonial",
            "Rentab. Patr. Período",
            "Rentab. Patr. Acumulada",
            "DY Ano",
            "DY (12M) Acumulado",
            "DY (6M) Acumulado",
            "DY (3M) Acumulado",
            "P/VPA",
            "VPA",
            "Patrimônio Líquido",
            "Rentab. Período",
            "Rentab. Acumulada",
        ],
        axis=1,
    )

    return df_aux


def rank_columns(df):
    df_aux = df.copy()

    df_aux["DY (12M) média_rank"] = df_aux["DY (12M) média"].rank(ascending=False)
    df_aux["DY (6M) média_rank"] = df_aux["DY (6M) média"].rank(ascending=False)
    df_aux["DY (3M) média_rank"] = df_aux["DY (3M) média"].rank(ascending=False)
    df_aux["Liquidez Diária (R$)_rank"] = df_aux["Liquidez Diária (R$)"].rank(ascending=False)
    df_aux["Num. Cotistas_rank"] = df_aux["Num. Cotistas"].rank(ascending=False)
    df_aux["P/VP_rank"] = df_aux["P/VP"].rank(ascending=True)
    df_aux["Volatilidade_rank"] = df_aux["Volatilidade"].rank(ascending=True)

    return df_aux


def clear_rank_columns(df):
    df_aux = df.copy()
    df_aux = df_aux.drop(
        [
            "DY (12M) média_rank",
            "DY (6M) média_rank",
            "DY (3M) média_rank",
            "Liquidez Diária (R$)_rank",
            "Num. Cotistas_rank",
            "P/VP_rank",
            "Volatilidade_rank",
            "Weighted rank"
        ],
        axis=1,
    )
    return df_aux


def groupby_count(df):
    df_aux = df.groupby(["Setor"], observed=False)["Setor"].count()

    return df_aux


def groupby_mean(df):
    df_aux = df.groupby(["Setor"], observed=False, as_index=False)[
        [
            "Preço Atual (R$)",
            "Liquidez Diária (R$)",
            "P/VP",
            "Dividend Yield",
            "Variação Preço",
            "Quant. Ativos",
            "Volatilidade",
            "Num. Cotistas",
        ]
    ].mean()

    return df_aux


def weighted_average(df):
    df_aux = df.copy()

    dy_12m_weight = 1.25
    dy_6m_weight = 1
    dy_3m_weight = 0.75
    liquidez_weight = 0.75
    cotistas_weight = 0.75
    pvp_weight = 1.25
    volatilidade_weight = 1
    # price_weight = 0.5

    weights_sum = (
        dy_12m_weight
        + dy_6m_weight
        + dy_3m_weight
        + liquidez_weight
        + cotistas_weight
        + pvp_weight
        + volatilidade_weight
        # + price_weight
    )

    df_aux["DY (12M) média_rank"] = df_aux["DY (12M) média_rank"] * dy_12m_weight
    df_aux["DY (6M) média_rank"] = df_aux["DY (6M) média_rank"] * dy_6m_weight
    df_aux["DY (3M) média_rank"] = df_aux["DY (3M) média_rank"] * dy_3m_weight
    df_aux["Liquidez Diária (R$)_rank"] = df_aux["Liquidez Diária (R$)_rank"] * liquidez_weight
    df_aux["Num. Cotistas_rank"] = df_aux["Num. Cotistas_rank"] * cotistas_weight
    df_aux["P/VP_rank"] = df_aux["P/VP_rank"] * pvp_weight
    df_aux["Volatilidade_rank"] = df_aux["Volatilidade_rank"] * volatilidade_weight
    # df_aux["Preço Atual (R$)_rank"] = df_aux["Preço Atual (R$)_rank"] * price_weight

    cols = [col for col in df_aux.columns if "_rank" in col]

    df_aux["Weighted rank"] = df_aux[cols].mean(axis=1) / weights_sum
    df_aux["Rank"] = df_aux["Weighted rank"].rank(method="dense", ascending=True)
    first_column = df_aux.pop("Rank")
    df_aux.insert(0, "Rank", first_column)

    return df_aux


def print_means(df):
    print("Mediana p/vp: ")
    print(df["P/VP"].mean())

    prc_lst_one = df.loc[(df["P/VP"] < 0.99)]["P/VP"].mean()
    print("Mediana p/vp menor que 1: ")
    print(prc_lst_one)

    print("Mediana liquidez: ")
    print(df["Liquidez Diária (R$)"].mean())
    print("Mediana cotistas: ")
    print(df["Num. Cotistas"].mean())

    prc_var_neg = df.loc[(df["Variação Preço"] < 0)]["Variação Preço"].mean()
    prc_var_pos = df.loc[(df["Variação Preço"] > 0)]["Variação Preço"].mean()
    print("Mediana variação preço negativo: ")
    print(prc_var_neg)
    print("Mediana variação preço positivo: ")
    print(prc_var_pos)
    return 
