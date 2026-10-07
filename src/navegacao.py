import streamlit as st

# Configuração da página (deve vir antes de qualquer outro comando visual)
st.set_page_config(
    page_title="Análise Temporal — ZWD × Precipitação",
    page_icon=":material/satellite_alt:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Identidade visual (CSS + tema dos gráficos). Aplicada uma única vez,
# antes de pg.run(), portanto vale para todas as páginas.
from estilo import aplicar_estilo
aplicar_estilo()

# Cabeçalho da barra lateral (o CSS o posiciona no topo, acima da navegação)
st.sidebar.markdown(
    """
    <div class="sb-marca">
      <svg width="30" height="30" viewBox="0 0 30 30" fill="none" aria-hidden="true">
        <rect x="0.5" y="0.5" width="29" height="29" stroke="#4589FF" stroke-opacity="0.55"/>
        <path d="M5 19 C 8 19, 9 11, 12 11 S 16 21, 19 21 S 23 13, 25 13" stroke="#FFFFFF" stroke-width="1.3" fill="none"/>
        <rect x="23.5" y="11.5" width="3" height="3" fill="#0F62FE"/>
      </svg>
      <div>
        <div class="sb-marca-titulo">ZWD&nbsp;×&nbsp;Precipitação</div>
        <div class="sb-marca-sub">Montes Claros, MG · 2011–2024</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

pages = {
    "Início": [
        st.Page("paginaInicial.py", title="Página Inicial", icon=":material/home:"),
    ],
    "Análises": [
        st.Page("01_series_temporais.py", title="Séries Temporais", icon=":material/show_chart:"),
        st.Page("02_decomposicao.py",     title="Decomposição",      icon=":material/stacked_line_chart:"),
        st.Page("03_correlacoes.py",      title="Correlações",       icon=":material/scatter_plot:"),
    ],
    "Dados": [
        st.Page("04_tabelas.py", title="Tabelas", icon=":material/table_chart:"),
    ],
}

pg = st.navigation(pages)
pg.run()
