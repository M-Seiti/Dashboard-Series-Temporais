import streamlit as st
import pandas as pd

st.title("Tabelas")

from CalcularRM import (
    preparar_dados_dashboard,
    calcular_max_min,
)


df_merged = preparar_dados_dashboard(ano=None)
df_max_min = calcular_max_min(df_merged)

st.subheader("Valores máximos e mínimos das médias anuais")
st.dataframe(df_max_min)
st.subheader("Valores médios por dia dos anos de 2011 - 2024")
st.dataframe(df_merged)