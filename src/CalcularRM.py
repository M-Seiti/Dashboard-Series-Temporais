import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
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
          .rename(columns={"trwet": "trwet_medio"})
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
        df.groupby(["ano", "mes"])["trwet_medio"]
          .sum()
          .reset_index(name="TRWET_media_mensal")
    )
    return df_mensal


@st.cache_data(show_spinner=False)
def decomposicao(df):

    df_prophet = df.copy()
    df_prophet = df_prophet.rename(columns={
        "data": "ds",
        "trwet_medio": "y"
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
    df["residuo"] = df["trwet_medio"] - forecast["yhat"].values

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
        .groupby("ano")["trwet_medio"]
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