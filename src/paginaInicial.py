import streamlit as st
from estilo import aplicar_estilo, feixes_de_luz_svg

aplicar_estilo()

_SETA = (
    '<svg width="22" height="12" viewBox="0 0 22 12" fill="none" aria-hidden="true">'
    '<path d="M0 6h20M15 1l5 5-5 5" stroke="currentColor" stroke-width="1.3"/></svg>'
)


def _html(bloco: str) -> str:
    """Junta o HTML numa linha só (o Markdown não o confunde com código)."""
    return " ".join(linha.strip() for linha in bloco.splitlines() if linha.strip())


# Hero
st.markdown(
    _html(
        f"""
        <section class="hero">
          <div class="hero-luz" aria-hidden="true">{feixes_de_luz_svg()}</div>
          <div><span class="badge">Iniciação Científica · Ciências Geodésicas</span></div>
          <div class="hero-corpo">
            <div class="hero-titulo" role="heading" aria-level="1">
              <span>Análise Temporal</span>
              <span>de Variáveis</span>
              <span>Atmosféricas</span>
            </div>
            <div class="hero-apoio">
              <p>Relação entre o <strong>Atraso Zenital Úmido (ZWD)</strong> derivado de GNSS e a
              <strong>precipitação</strong> observada em superfície — estação MGMC (RBMC) e estação
              automática OMM&nbsp;83437 (INMET), Montes Claros/MG, 2011–2024.</p>
              <a class="hero-botao" href="series_temporais" target="_self">
                <span>Séries Temporais</span>{_SETA}
              </a>
            </div>
          </div>
        </section>
        """
    ),
    unsafe_allow_html=True,
)

# KPIs de contexto (configuração do estudo)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Período analisado", "2011–2024")
c2.metric("Estação GNSS", "MGMC")
c3.metric("Estação INMET", "OMM 83437")
c4.metric("Local", "Montes Claros/MG")

st.markdown("### Sobre")
st.markdown(
    """
    Este dashboard apresenta uma análise exploratória e temporal de séries
    atmosféricas, com foco em padrões de **tendência**, **sazonalidade** e
    **variabilidade**, a partir de observações geofísicas (ZWD de estações
    GNSS) e meteorológicas (precipitação diária).
    """
)

st.markdown("### Navegação")
st.markdown(
    _html(
        f"""
        <div class="nav-grid">
          <a class="nav-card" href="series_temporais" target="_self">
            <span class="nav-num">01</span>
            <span class="nav-titulo">Séries Temporais</span>
            <p>Séries diárias e mensais de ZWD e precipitação, por ano ou em todo
            o período, com anomalias normalizadas (Z-score).</p>
            <span class="nav-seta">{_SETA}</span>
          </a>
          <a class="nav-card" href="decomposicao" target="_self">
            <span class="nav-num">02</span>
            <span class="nav-titulo">Decomposição</span>
            <p>Separação da série de ZWD em tendência, sazonalidade anual e
            resíduo, destacando padrões e eventos extremos.</p>
            <span class="nav-seta">{_SETA}</span>
          </a>
          <a class="nav-card" href="correlacoes" target="_self">
            <span class="nav-num">03</span>
            <span class="nav-titulo">Correlações</span>
            <p>Cruzamento entre ZWD e precipitação nas escalas diária e mensal,
            ajuste de curvas e análise de defasagem (lag).</p>
            <span class="nav-seta">{_SETA}</span>
          </a>
          <a class="nav-card" href="tabelas" target="_self">
            <span class="nav-num">04</span>
            <span class="nav-titulo">Tabelas</span>
            <p>Dados em formato tabular para inspeção e verificação dos valores
            utilizados nas análises.</p>
            <span class="nav-seta">{_SETA}</span>
          </a>
        </div>
        """
    ),
    unsafe_allow_html=True,
)

st.caption("Use o menu lateral para navegar entre as análises.")
