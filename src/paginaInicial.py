import streamlit as st

st.title("🌍 Análise Temporal de Variáveis Atmosféricas")

st.markdown(
    """
    ### Sobre
    Este dashboard apresenta uma análise exploratória e temporal de séries
    atmosféricas, com foco em padrões de **tendência**, **sazonalidade** e
    **variabilidade**, a partir de observações geofísicas (ZWD de estações
    GNSS) e meteorológicas (precipitação diária).

    ### Navegação

    Use o menu lateral para acessar as diferentes análises:

    - **Séries Temporais** — visualização das séries diárias e mensais de
      ZWD e precipitação, individualmente, por ano ou em todo o período.
    - **Decomposição** — separação da série de ZWD em componentes de
      tendência, sazonalidade e resíduo, permitindo identificar padrões e
      eventos extremos.
    - **Correlações** — cruzamento entre ZWD e precipitação em escala
      diária e mensal, incluindo análise de defasagem (lag).
    - **Tabelas** — dados organizados em formato tabular para inspeção e
      verificação dos valores utilizados nas análises.
    """
)