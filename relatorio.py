import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


st.set_page_config(layout="wide", page_title="Dashboard TRWET", page_icon="🌧️")
st.title("🌧️ Dashboard TRWET – GNSS / TROP")
st.markdown("Visualização diária e mensal do **TRWET** a partir de arquivos `.trop`.")
st.markdown("---") 

if 'data' in st.session_state and not st.session_state["data"].empty:
    df_relatorio = st.session_state["data"]
else:
    st.warning("Dados não encontrados")

st.dataframe(df_relatorio)