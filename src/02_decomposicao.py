import streamlit as st
import plotly.express as px

from CalcularRM import preparar_dados_dashboard, decomposicao

st.title("🧩 Decomposição da Série — ZWD")

st.markdown(
    "Decomposição aditiva da série diária de ZWD em **tendência**, "
    "**sazonalidade** (período de 365 dias) e **resíduo**."
)

df_merged = preparar_dados_dashboard(ano=None)

if df_merged.empty:
    st.warning("Nenhum dado disponível para decomposição.")
    st.stop()

df_decomp = decomposicao(df_merged)

st.write("Dias utilizados na decomposição:", len(df_decomp))

# ---------------------------------------------------------------- tendência
st.subheader("Tendência (média móvel)")
fig = px.line(df_decomp, x="data", y="tendencia")
fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=4))
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- sazonalidade
st.subheader("Sazonalidade (período = 365 dias)")
fig = px.line(df_decomp, x="data", y="sazonalidade")
fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=4))
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- resíduo
st.subheader("Resíduo")
fig = px.line(df_decomp, x="data", y="residuo")
fig.update_traces(mode="lines", line=dict(width=2))
st.plotly_chart(fig, use_container_width=True)
