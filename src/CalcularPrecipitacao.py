import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import streamlit as st

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
def carregar_precipitacao(ano: int | None = None) -> pd.DataFrame:
    """Carrega precipitação diária do Postgres. ano=None traz todo o intervalo."""
    if ano is None:
        query = """
            SELECT data, precipitacao_mm, dado_faltante
            FROM precipitacao_diaria
            WHERE data >= '2011-01-01'::date
              AND data <  '2025-01-01'::date
            ORDER BY data;
        """
        df = pd.read_sql_query(query, engine)
    else:
        query = """
            SELECT data, precipitacao_mm, dado_faltante
            FROM precipitacao_diaria
            WHERE EXTRACT(YEAR FROM data) = %(ano)s
            ORDER BY data;
        """
        df = pd.read_sql_query(query, engine, params={"ano": int(ano)})

    if df.empty:
        return df

    df["data"] = pd.to_datetime(df["data"]).dt.normalize()
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    return df


@st.cache_data
def carregar_anos_precipitacao_disponiveis():
    query = """
        SELECT DISTINCT EXTRACT(YEAR FROM data)::int AS ano
        FROM precipitacao_diaria
        ORDER BY ano;
    """
    df = pd.read_sql_query(query, engine)
    return df["ano"].tolist()


def calc_precip_mensal(df: pd.DataFrame) -> pd.DataFrame:
    """Soma mensal de precipitação (mm/mês)."""
    if df.empty:
        return df

    df_mensal = (
        df.groupby(["ano", "mes"], as_index=False)["precipitacao_mm"]
          .sum()
          .rename(columns={"precipitacao_mm": "precipitacao_mensal"})
    )
    df_mensal["data_mes"] = pd.to_datetime(
        {"year": df_mensal["ano"], "month": df_mensal["mes"], "day": 1}
    )
    return df_mensal


def calc_precip_max_min_anual(df: pd.DataFrame) -> pd.DataFrame:
    """Máximo e mínimo diário de precipitação por ano."""
    if df.empty:
        return df

    return (
        df.groupby("ano")["precipitacao_mm"]
          .agg(valor_maximo="max", valor_minimo="min")
    )


def calc_anomalia_precipitacao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Anomalia mensal de precipitação:
        anomalia = soma_mensal - climatologia_mensal
    A climatologia é a média das somas mensais para cada mês ao longo dos anos.
    """
    if df.empty:
        return df

    df = df.copy()
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month

    mensal = (
        df.groupby(["ano", "mes"])["precipitacao_mm"]
        .sum()
        .reset_index(name="soma_mensal")
    )

    climatologia = (
        mensal.groupby("mes")["soma_mensal"]
        .agg(climatologia_prec="mean", desvio_padrao_prec="std")
        .reset_index()
    )

    mensal = mensal.merge(climatologia, on="mes")
    mensal["anomalia_prec"] = mensal["soma_mensal"] - mensal["climatologia_prec"]
    mensal["zscore_prec"] = mensal["anomalia_prec"] / mensal["desvio_padrao_prec"]
    mensal["data_mes"] = pd.to_datetime(
        {"year": mensal["ano"], "month": mensal["mes"], "day": 1}
    )
    return mensal.sort_values("data_mes").reset_index(drop=True)


def calc_anomalia_precipitacao_semanal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Anomalia semanal de precipitação (ISO week):
        anomalia = soma_semanal - climatologia_semanal
    A climatologia é a média das somas semanais para cada semana ISO ao longo dos anos.
    """
    if df.empty:
        return df

    df = df.copy()
    iso = df["data"].dt.isocalendar()
    df["semana"] = iso.week.astype(int)
    df["ano"]    = iso.year.astype(int)

    semanal = (
        df.groupby(["ano", "semana"])["precipitacao_mm"]
        .sum()
        .reset_index(name="soma_semanal")
    )

    climatologia = (
        semanal.groupby("semana")["soma_semanal"]
        .agg(climatologia_prec="mean", desvio_padrao_prec="std")
        .reset_index()
    )

    semanal = semanal.merge(climatologia, on="semana")
    semanal["anomalia_prec"] = semanal["soma_semanal"] - semanal["climatologia_prec"]
    semanal["zscore_prec"]   = semanal["anomalia_prec"] / semanal["desvio_padrao_prec"]
    semanal["data_semana"]   = pd.to_datetime(
        semanal["ano"].astype(str) + semanal["semana"].astype(str).str.zfill(2) + "1",
        format="%G%V%u",
    )
    return semanal.sort_values("data_semana").reset_index(drop=True)
