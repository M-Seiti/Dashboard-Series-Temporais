import streamlit as st

pages = {
    "Pagina Inicial": [
        st.Page("paginaInicial.py", title="Pagina Inicial"),
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