import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import streamlit as st

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

def carregar_dados_ano(ano: int)-> pd.DataFrame:
    query = """
        SELECT
            site,
            trotot,
            sig_trotot,
            trwet,
            tgetot,
            sig_tgetot,
            tgntot,
            sig_tgntot,
            wvapor,
            sig_wvapor,
            mtemp,
            arquivo,
            pasta_ano,
            epoch
        FROM trwet_diario
        WHERE EXTRACT(YEAR FROM epoch) = %(ano)s
        ORDER BY epoch;
    """
    df = pd.read_sql_query(query, engine, params={"ano": ano})
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
    return df




def calc_media_diaria(df):
  if df.empty:
        return df

  df_media_dia = (
        df.groupby("arquivo", as_index=False)["trwet"]
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

def preparar_dados_dashboard(ano):
  df = carregar_dados_ano(ano)
  df = adicionar_colunas_tempo(df)

  if df.empty:
        return df

  df_media_dia = calc_media_diaria(df)

  meta = df[["arquivo", "ano", "dia_juliano", "data"]].drop_duplicates()

  df_merged = df_media_dia.merge(meta, on="arquivo", how="left")
  df_merged = df_merged.sort_values("data")

  return df_merged

def calc_media_mensal(df):
    df = df.copy()
    df["mes"] = df["data"].dt.month
    df_mensal = (
        df.groupby(["ano", "mes"])["trwet_medio"]
          .sum()
          .reset_index(name="TRWET_media_mensal")
    )
    return df_mensal