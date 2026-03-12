import streamlit as st

pages = {
    "Sobre": [
        st.Page("paginaInicial.py", title="Sobre o projeto"),
    ],
    "Visualização de gráficos": [
        st.Page("graficos.py", title="Gráficos"),
    ],
    "Visualização de tabelas": [
        st.Page("tabelas.py", title="Tabelas"),
    ],
}

pg = st.navigation(pages)
pg.run()