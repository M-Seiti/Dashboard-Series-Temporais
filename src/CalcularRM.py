import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import streamlit as st
from prophet import Prophet

csv_path = (r"C:\Users\seiti\OneDrive\Desktop\IC\dados_baixados_Matheus\resultado_TROP_todos.csv")
load_dotenv()

USER = os.getenv("POSTGRES_USER")
PWD  = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")
DB   = os.getenv("POSTGRES_DB")

engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PWD}@{HOST}:{PORT}/{DB}"
)

@st.cache_data(show_spinner=False)
def carregar_dados_ano(ano: int)-> pd.DataFrame:
    if ano is None:
     query_todos = """
        SELECT
            trwet,
            arquivo,
            epoch
        FROM trwet_diario
        WHERE epoch >= '2011-01-01'::timestamp
        AND epoch <  '2025-01-01'::timestamp
        AND epoch::time >= TIME '01:00'
        AND epoch::time <= TIME '23:00'
            ORDER BY epoch;
        """
     df = pd.read_sql_query(query_todos, engine)

    else:
        query_ano_especifico = """
        SELECT
            trwet,
            arquivo,
            epoch
        FROM trwet_diario
        WHERE EXTRACT(YEAR FROM epoch) = %(ano)s
        AND epoch::time >= TIME '01:00'
        AND epoch::time <= TIME '23:00'
            ORDER BY epoch;
        """
        df = pd.read_sql_query(query_ano_especifico, engine, params={"ano": int(ano)})

    return df

def adicionar_colunas_tempo(df):
    if df.empty:
        return df

    df = df.copy()

    df["epoch"] = pd.to_datetime(df["epoch"])
    df["data"] = df["epoch"].dt.normalize()
    df["ano"] = df["epoch"].dt.year
    df["mes"] = df["epoch"].dt.month
    df["dia"] = df["epoch"].dt.day
    df["dia_juliano"] = df["epoch"].dt.dayofyear
    df["hora"] = df["epoch"].dt.hour
    df["minuto"] = df["epoch"].dt.minute

    return df


def calc_media_diaria(df):
  if df.empty:
        return df

  df_media_dia = (
        df.groupby(["ano", "data", "dia_juliano"], as_index=False)["trwet"]
          .mean()
          .rename(columns={"trwet": "zwd_medio"})
    )
  return df_media_dia

@st.cache_data
def carregar_anos_disponiveis():
    query = """
        SELECT DISTINCT EXTRACT(YEAR FROM epoch)::int AS ano
        FROM trwet_diario
        ORDER BY ano;
    """
    df = pd.read_sql_query(query, engine)
    return df["ano"].tolist()

def carregar_meses_disponiveis():
    query = """
        SELECT DISTINCT EXTRACT(MONTH FROM epoch)::int AS mes
        FROM trwet_diario
        ORDER BY mes;
    """
    df = pd.read_sql_query(query, engine)
    return df["mes"].tolist()

def preparar_dados_dashboard(ano: int):
  df = carregar_dados_ano(ano)
  df = adicionar_colunas_tempo(df)

  if df.empty:
        return df

  df_media_dia = calc_media_diaria(df)
  df_merged = df_media_dia.sort_values("data")

  return df_merged

def calc_media_mensal(df):
    df = df.copy()
    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year

    df_mensal = (
        df.groupby(["ano", "mes"])["zwd_medio"]
          .sum()
          .reset_index(name="ZWD_media_mensal")
    )
    return df_mensal


def calc_anomalia_zwd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Anomalia mensal do ZWD:
        anomalia = media_mensal - climatologia_mensal
    A climatologia é a média histórica de cada mês ao longo de todos os anos.
    """
    df = df.copy()
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month

    mensal = (
        df.groupby(["ano", "mes"])["zwd_medio"]
        .mean()
        .reset_index(name="media_mensal_zwd")
    )

    climatologia = (
        mensal.groupby("mes")["media_mensal_zwd"]
        .agg(climatologia_zwd="mean", desvio_padrao_zwd="std")
        .reset_index()
    )

    mensal = mensal.merge(climatologia, on="mes")
    mensal["anomalia_zwd"] = mensal["media_mensal_zwd"] - mensal["climatologia_zwd"]
    mensal["zscore_zwd"] = mensal["anomalia_zwd"] / mensal["desvio_padrao_zwd"]
    mensal["data_mes"] = pd.to_datetime(
        {"year": mensal["ano"], "month": mensal["mes"], "day": 1}
    )
    return mensal.sort_values("data_mes").reset_index(drop=True)


def calc_anomalia_zwd_semanal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Anomalia semanal do ZWD (ISO week):
        anomalia = media_semanal - climatologia_semanal
    A climatologia é a média histórica de cada semana ISO ao longo dos anos.
    """
    df = df.copy()
    iso = df["data"].dt.isocalendar()
    df["semana"] = iso.week.astype(int)
    df["ano"]    = iso.year.astype(int)

    semanal = (
        df.groupby(["ano", "semana"])["zwd_medio"]
        .mean()
        .reset_index(name="media_semanal_zwd")
    )

    climatologia = (
        semanal.groupby("semana")["media_semanal_zwd"]
        .agg(climatologia_zwd="mean", desvio_padrao_zwd="std")
        .reset_index()
    )

    semanal = semanal.merge(climatologia, on="semana")
    semanal["anomalia_zwd"] = semanal["media_semanal_zwd"] - semanal["climatologia_zwd"]
    semanal["zscore_zwd"]   = semanal["anomalia_zwd"] / semanal["desvio_padrao_zwd"]
    semanal["data_semana"]  = pd.to_datetime(
        semanal["ano"].astype(str) + semanal["semana"].astype(str).str.zfill(2) + "1",
        format="%G%V%u",
    )
    return semanal.sort_values("data_semana").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def decomposicao(df):

    df_prophet = df.copy()
    df_prophet = df_prophet.rename(columns={
        "data": "ds",
        "zwd_medio": "y"
    })

    m = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False,
    changepoint_prior_scale=0.05,
    seasonality_prior_scale=10.0,
  )
    m.fit(df_prophet)

    forecast = m.predict(df_prophet[["ds"]])
    df["tendencia"] = forecast["trend"].values
    df["sazonalidade"] = forecast["yearly"].values
    df["residuo"] = df["zwd_medio"] - forecast["yhat"].values

    return df

def media_desvio(df):

    df = df.copy()

    df["mes"] = df["data"].dt.month

    df_media_desvio = (
    df.assign(mes=df["data"].dt.month)
      .groupby("mes", as_index=False)["residuo"]
      .agg(media_residuo="mean", desvio_padrao_residuo="std")
)

    return df_media_desvio

def calcular_dias_mes(df):
    df = df.copy()

    df["mes"] = df["data"].dt.month
    df["dia"] = df["data"].dt.day

    df_dias_meses = (
        df
        .groupby("mes")["dia"]
        .count()
    )
    return df_dias_meses

def calcular_max_min(df):

    df_max_min = df.copy()

    max_min = (
        df_max_min
        .groupby("ano")["zwd_medio"]
        .agg(valor_maximo="max", valor_minimo="min")
    )
    return max_min

def calc_media_mensal_por_ano(df):
    df = df.copy()
    df["mes"] = pd.to_datetime(df["data"]).dt.month
    df["ano"] = pd.to_datetime(df["data"]).dt.year

    df_mensal = (
        df.groupby(["ano", "mes"])["trwet_medio"]
          .mean()
          .reset_index(name="media_mensal")
    )
    return df_mensal


def calc_climatologia_mensal(df_mensal):
    df_climatologia = (
        df_mensal.groupby("mes")["media_mensal"]
                 .agg(media_climatologica="mean", desvio_padrao="std")
                 .reset_index()
    )
    return df_climatologia


def calc_anomalias_mensais(df_mensal, df_climatologia):
    df = df_mensal.merge(df_climatologia, on="mes", how="left")

    df["anomalia"] = (df["media_mensal"] - df["media_climatologica"]) / df["desvio_padrao"]

    return df.drop(columns=["media_climatologica", "desvio_padrao"])


# ──────────────────────────────────────────────────────────────────────────────
# PRECIPITAÇÃO
# ──────────────────────────────────────────────────────────────────────────────

import numpy as np
from scipy import stats

def carregar_precipitacao(csv_path: str) -> pd.DataFrame:
    """Lê o CSV de precipitação e devolve com coluna 'data' como date."""
    df = pd.read_csv(csv_path, parse_dates=["data"])
    df["data"] = df["data"].dt.normalize()
    df = df[df["dado_faltante"] == False].copy()
    df = df[["data", "precipitacao_mm"]].sort_values("data").reset_index(drop=True)
    return df


def anomalia_precipitacao(df_prec: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a anomalia mensal de precipitação:
        anomalia = soma_mensal - climatologia_mensal
    A climatologia é a média histórica de cada mês (jan, fev, ...) ao longo de todos os anos.
    """
    df = df_prec.copy()
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month

    mensal = (
        df.groupby(["ano", "mes"])["precipitacao_mm"]
        .sum()
        .reset_index(name="soma_mensal")
    )

    climatologia = (
        mensal.groupby("mes")["soma_mensal"]
        .mean()
        .reset_index(name="climatologia")
    )

    mensal = mensal.merge(climatologia, on="mes")
    mensal["anomalia_prec"] = mensal["soma_mensal"] - mensal["climatologia"]
    mensal["data_mes"] = pd.to_datetime(
        {"year": mensal["ano"], "month": mensal["mes"], "day": 1}
    )
    return mensal.sort_values("data_mes").reset_index(drop=True)


# ──────────────────────────────────────────────────────────────────────────────
# CORRELAÇÃO  ZWD / PRECIPITAÇÃO
# ──────────────────────────────────────────────────────────────────────────────

def correlacao_mensal(df_gnss: pd.DataFrame, df_prec: pd.DataFrame) -> pd.DataFrame:
    """
    Junta médias mensais de ZWD com soma mensal de precipitação
    e calcula correlações de Pearson e Spearman.

    Retorna um DataFrame com colunas:
        par, pearson_r, pearson_p, spearman_r, spearman_p
    """
    df_g = df_gnss.copy()
    df_g["ano"] = df_g["data"].dt.year
    df_g["mes"] = df_g["data"].dt.month

    gnss_mensal = (
        df_g.groupby(["ano", "mes"])
        .agg(zwd_medio=("zwd_medio", "mean"))
        .reset_index()
    )

    df_p = df_prec.copy()
    df_p["ano"] = df_p["data"].dt.year
    df_p["mes"] = df_p["data"].dt.month
    prec_mensal = (
        df_p.groupby(["ano", "mes"])["precipitacao_mm"]
        .sum()
        .reset_index(name="prec_mensal")
    )

    merged = gnss_mensal.merge(prec_mensal, on=["ano", "mes"]).dropna()

    resultados = []
    pares = [("zwd_medio", "prec_mensal")]
    nomes = [("ZWD", "Precipitação")]

    for (col_a, col_b), (nome_a, nome_b) in zip(pares, nomes):
        x = merged[col_a].values
        y = merged[col_b].values
        pr, pp = stats.pearsonr(x, y)
        sr, sp = stats.spearmanr(x, y)
        resultados.append({
            "par": f"{nome_a} × {nome_b}",
            "pearson_r": round(pr, 4),
            "pearson_p": round(pp, 6),
            "spearman_r": round(sr, 4),
            "spearman_p": round(sp, 6),
            "n": len(x),
        })

    return pd.DataFrame(resultados), merged


def scatter_correlacao(merged: pd.DataFrame) -> pd.DataFrame:
    """Retorna o df pronto para scatter ZWD × precipitação."""
    return merged[["ano", "mes", "zwd_medio", "prec_mensal"]].copy()


# ──────────────────────────────────────────────────────────────────────────────
# ANÁLISE POR INTERVALOS DE PRECIPITAÇÃO
# ──────────────────────────────────────────────────────────────────────────────

def analise_intervalos_precipitacao(
    df_gnss: pd.DataFrame,
    df_prec: pd.DataFrame,
    bins: list = None,
) -> pd.DataFrame:
    """
    Para cada dia, junta o ZWD médio com a precipitação.
    Classifica a precipitação em intervalos (bins) e calcula:
        - ZWD médio por intervalo
        - frequência de ocorrência (dias) por intervalo
        - percentual de ocorrência

    Parâmetro bins: lista de limites ex. [0, 0.1, 10, 20, 40, 80, 999]
    """
    if bins is None:
        bins = [0, 0.1, 10, 20, 40, 80, 9999]

    labels = []
    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i + 1]
        if hi >= 9000:
            labels.append(f">{lo} mm")
        elif lo == 0:
            labels.append("Sem chuva (0 mm)")
        else:
            labels.append(f"{lo}–{hi} mm")

    df_g = df_gnss[["data", "zwd_medio"]].copy()
    df_p = df_prec[["data", "precipitacao_mm"]].copy()
    daily = df_g.merge(df_p, on="data", how="inner")

    daily["intervalo"] = pd.cut(
        daily["precipitacao_mm"],
        bins=bins,
        labels=labels,
        right=True,
        include_lowest=True,
    )

    resultado = (
        daily.groupby("intervalo", observed=True)
        .agg(
            zwd_medio=("zwd_medio", "mean"),
            zwd_std=("zwd_medio", "std"),
            frequencia=("zwd_medio", "count"),
        )
        .reset_index()
    )
    resultado["percentual"] = (
        resultado["frequencia"] / resultado["frequencia"].sum() * 100
    ).round(2)

    return resultado, daily
