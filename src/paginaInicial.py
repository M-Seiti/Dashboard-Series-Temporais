import streamlit as st

st.title("🌍 Análise Temporal de Variáveis Atmosféricas")

st.markdown(
    """
     ### Sobre
    Este dashboard apresenta uma análise exploratória e temporal de séries atmosféricas,
    com foco em padrões de **tendência**, **sazonalidade** e **variabilidade**, 
    a partir de observações geofísicas.
    
    As visualizações permitem investigar o comportamento dos dados ao longo do tempo,
    identificar mudanças de regime e compreender a ocorrência de eventos extremos.

     ### Navegação
    
    Utilize o menu lateral para acessar as diferentes funcionalidades do dashboard:
    
    - **Gráficos**: permite a visualização dos dados por meio de gráficos interativos, 
      facilitando a análise do comportamento temporal, tendências, sazonalidades e variabilidade das séries.
    
    - **Tabelas**: disponibiliza os dados organizados em formato tabular, possibilitando a consulta,
      inspeção detalhada e verificação dos valores utilizados nas análises.
    
    Essa separação entre gráficos e tabelas oferece uma abordagem complementar, unindo 
    visualização exploratória e análise quantitativa dos dados.

    """
)