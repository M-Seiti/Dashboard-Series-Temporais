import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def calc_mean(df):
    return (
        df.groupby("arquivo")["TRWET"]
          .mean()
          .reset_index(name="TRWET_medio")
    )
     
def calc_month_sum(df):
    df = df.copy()
    df["mes"] = df["data"].dt.month

    df_mensal = (
        df.groupby(["ano", "mes"])["TRWET_medio"]
        .sum()
        .reset_index(name="TRWET_media_mensal")
    )
    return df_mensal

def doy_para_data(ano, doy):
    return datetime(ano, 1, 1) + timedelta(days=doy - 1)

df = pd.read_csv(r"C:\Users\seiti\OneDrive\Desktop\IC\dados_baixados_Matheus\resultado_TROP_todos.csv")

df_media_dia = calc_mean(df)


df_media_dia["ano"] = df_media_dia["arquivo"].str.split(".").str[1].astype(int)
df_media_dia["dia_juliano"] = df_media_dia["arquivo"].str.split(".").str[2].astype(int)

df_media_dia["data"] = df_media_dia.apply(
    lambda row: doy_para_data(row["ano"], row["dia_juliano"]),
    axis=1
)

if 'data' not in st.session_state:
    st.session_state['data'] = df

df_media_mensal = calc_month_sum(df_media_dia)

df_media_mensal["data_mes"] = pd.to_datetime({
    "year": df_media_mensal["ano"],
    "month": df_media_mensal["mes"],
    "day": 1,
})

st.set_page_config(layout="wide", page_title="Dashboard TRWET", page_icon="🌧️")
st.title("🌧️ Dashboard TRWET – GNSS / TROP")
st.markdown("Visualização diária e mensal do **TRWET** a partir de arquivos `.trop`.")
st.markdown("---") 

col5, col6, col7 = st.columns(3)
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

st.sidebar.title("⚙️ Controles")
ano = st.sidebar.selectbox("Selecione o ano", df_media_dia["ano"].unique())

df_filtered_ano = df_media_dia[df_media_dia["ano"] == ano].sort_values("dia_juliano")
df_filtered_mes = df_media_mensal[df_media_mensal["ano"] == ano].sort_values("mes")

df_qtd_dias_arquivo = df_filtered_ano["arquivo"].count()
df_dias_faltantes = 365 - df_qtd_dias_arquivo

if df_dias_faltantes == -1:
    df_dias_faltantes = 0
   

#config dos graficos-------------------------------------------------------------------
fig_media_dia = px.line(
   df_filtered_ano,
   x="data",
   y="TRWET_medio",
   title=f"Média diária do TRWET para o ano {ano}",
)

fig_media_mensal = px.bar(
   df_filtered_mes,
   x="data_mes",
   y="TRWET_media_mensal",
   title=f"Media mensal para o ano de {ano}",
   color="TRWET_media_mensal",
   color_continuous_scale="Blues"
)
#----------------------------------------------------------------------------------------
#Estilização-----------------------------------------------------------------------------
# deixa a linha com marcadores nos pontos
fig_media_dia.update_traces(
    mode="lines+markers",
    line=dict(width=2),
    marker=dict(size=4)
)

# layout geral
fig_media_dia.update_layout(
    template="plotly_dark",        
    height=450,
    title_font_size=22,
    xaxis_title="Data",
    yaxis_title="TRWET médio (mm)",
    xaxis_title_font_size=16,
    yaxis_title_font_size=16,
    hovermode="x unified",         
    margin=dict(l=60, r=20, t=60, b=60),
)

# eixo X (datas)
fig_media_dia.update_xaxes(
    tickformat="%d/%m/%Y",   
    showgrid=True,
)

# eixo Y
fig_media_dia.update_yaxes(
    showgrid=True,
    zeroline=False
)

st.markdown("""
<style>
div[data-testid="stMetric"]:nth-of-type(2) div[data-testid="stMetricValue"] {
    color: red !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)
#------------------------------------------------------------
#verificação do total esperado
total_esperado = 365
if len(df_filtered_ano) == 366:
    total_esperado = 366
#------------------------------------------------------------
#Gráficos
with col5:
 col5 = st.metric("Dias disponíveis", len(df_filtered_ano))
with col6:
 col6 = st.metric("Dias ausentes", df_dias_faltantes)
with col7: 
 col7 = st.metric("Total esperado", total_esperado)
col1.plotly_chart(fig_media_dia, use_container_width=True)
col2.dataframe(df_filtered_ano)
col3.plotly_chart(fig_media_mensal)
col4.dataframe(df_filtered_mes)
