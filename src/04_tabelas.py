import streamlit as st

from CalcularRM import preparar_dados_dashboard, calcular_max_min
from CalcularPrecipitacao import (
    carregar_precipitacao,
    calc_precip_max_min_anual,
    calc_precip_mensal,
)

st.title("📋 Tabelas")

aba_zwd, aba_precip = st.tabs(["ZWD", "Precipitação"])

# ---------------------------------------------------------------- ZWD
with aba_zwd:
    df_merged  = preparar_dados_dashboard(ano=None)
    df_max_min = calcular_max_min(df_merged)

    st.subheader("Valores máximos e mínimos das médias anuais — ZWD")
    st.dataframe(df_max_min, use_container_width=True)

    st.subheader("Valores médios diários — ZWD (2011–2024)")
    st.dataframe(df_merged, use_container_width=True)

# ---------------------------------------------------------------- Precipitação
with aba_precip:
    df_precip = carregar_precipitacao(ano=None)
    df_precip_max_min = calc_precip_max_min_anual(df_precip)
    df_precip_mensal  = calc_precip_mensal(df_precip)

    st.subheader("Máximos e mínimos diários por ano — Precipitação")
    st.dataframe(df_precip_max_min, use_container_width=True)

    st.subheader("Soma mensal de precipitação")
    st.dataframe(df_precip_mensal, use_container_width=True)

    st.subheader("Precipitação diária (2011–2024)")
    st.dataframe(df_precip, use_container_width=True)
