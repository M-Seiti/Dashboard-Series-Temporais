import streamlit as st
import plotly.express as px
import pandas as pd
import calendar

from CalcularRM import (
    preparar_dados_dashboard,
    carregar_anos_disponiveis,
    calc_media_mensal,
)

st.set_page_config(layout="wide", page_title="Dashboard TRWET", page_icon="🌧️")
st.title("🌧️ Dashboard TRWET – GNSS / TROP")
st.markdown("Visualização diária e mensal do **TRWET** a partir de arquivos `.trop`.")
st.markdown("---")



st.sidebar.title("⚙️ Controles")
anos_disponiveis = carregar_anos_disponiveis()
ano = st.sidebar.selectbox("Selecione o ano", anos_disponiveis)

df = preparar_dados_dashboard(ano)

df_mensal = calc_media_mensal(df)

qtd_dias_arquivo = len(df)

total_esperado = 366 if calendar.isleap(ano) else 365

dias_faltantes = total_esperado - qtd_dias_arquivo
if dias_faltantes < 0:
    dias_faltantes = 0


col5, col6, col7 = st.columns(3)
col1, col2 = st.columns(2)

with col5:
    st.write("Dias disponíveis: :green", qtd_dias_arquivo)
with col6:
    st.write("Dias ausentes:", dias_faltantes)
with col7:
    st.write("Total esperado:", total_esperado)

# ----------------- GRÁFICOS -----------------
with col1:
    st.subheader(f"Média diária do TRWET - {ano}")
    fig_dia = px.line(df, x="data", y="trwet_medio")
    fig_dia.update_traces(
        mode="lines+markers",
        line=dict(width=2),
        marker=dict(size=4),
    )
    st.plotly_chart(fig_dia, use_container_width=True)

with col2:
    st.subheader(f"Média mensal do TRWET - {ano}")
    df_mensal["data_mes"] = pd.to_datetime(
        {"year": df_mensal["ano"], "month": df_mensal["mes"], "day": 1}
    )
    fig_mes = px.bar(df_mensal, x="data_mes", y="TRWET_media_mensal")
    st.plotly_chart(fig_mes, use_container_width=True)

st.subheader("Dados filtrados")
st.dataframe(df)
