import pandas as pd
from datetime import datetime, timedelta
import streamlit as st


csv_path = (r"C:\Users\seiti\OneDrive\Desktop\IC\dados_baixados_Matheus\resultado_TROP_todos.csv")

@st.cache_data
def carregar_dados():
    df = pd.read_csv(csv_path)
    return df


def adicionar_colunas_tempo(df):
    partes = df["arquivo"].str.split(".", expand=True)

    df["ano"] = partes[1].astype(int)
    df["dia_juliano"] = partes[2].astype(int)


    df["data"] = df.apply(
        lambda row: datetime.strptime(
            f"{int(row['ano'])} {int(row['dia_juliano'])}",
            "%Y %j"
        ),
        axis=1
    )


    df["mes"] = df["data"].dt.month
    df["dia"] = df["data"].dt.day

    return df

def calc_media_diaria(df):
   df_media_dia=( df.groupby("arquivo")["TRWET"]
      .mean()
      .reset_index(name="TRWET_medio")
    )
   
   return df_media_dia

def preparar_dados_dashboard():
    df = carregar_dados()
    df = adicionar_colunas_tempo(df)
    df_media_dia = calc_media_diaria(df)
    df_merged = df_media_dia.merge(
        df[["arquivo", "ano", "dia_juliano", "data"]].drop_duplicates(),
        on="arquivo",
        how="left"
    )
    return df_merged

def filtrar_por_ano(df, ano):
    df_ano = df[df["ano"] == ano].sort_values("data")
    return df_ano

def calc_media_mensal(df):
    df = df.copy()
    df["mes"] = df["data"].dt.month
    df_mensal = (
        df.groupby(["ano", "mes"])["TRWET_medio"]
          .sum()
          .reset_index(name="TRWET_media_mensal")
    )
    return df_mensal