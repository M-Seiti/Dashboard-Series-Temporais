import streamlit as st

pages = {
    "Início": [
        st.Page("paginaInicial.py", title="Página Inicial", icon="🏠"),
    ],
    "Análises": [
        st.Page("01_series_temporais.py", title="Séries Temporais", icon="📈"),
        st.Page("02_decomposicao.py",     title="Decomposição",      icon="🧩"),
        st.Page("03_correlacoes.py",      title="Correlações",       icon="🔗"),
    ],
    "Dados": [
        st.Page("04_tabelas.py", title="Tabelas", icon="📋"),
    ],
}

pg = st.navigation(pages)
pg.run()