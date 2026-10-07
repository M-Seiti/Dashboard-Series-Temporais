# -*- coding: utf-8 -*-
"""
estilo.py — Identidade visual do dashboard (azul-noite, minimalista).

Uso:
    from estilo import aplicar_estilo
    aplicar_estilo()        # chamar uma vez (em navegacao.py, antes de pg.run())

Auxiliares de aparência (não mexem em dados nem em cálculos):
    ROTULOS             nomes legíveis das colunas, para labels= do Plotly Express
    CORES               cores de série única, barras e tendência OLS
    ESCALA_ZSCORE       escala dos Z-scores (usar com color_continuous_midpoint=0)
    ESCALA_MATRIZ       escala das matrizes de confusão
    estilo_plotly(fig)  grava o tema na figura; usar em cada st.plotly_chart:
                            st.plotly_chart(estilo_plotly(fig), use_container_width=True)
    estilo_matriz(fig)  idem, para o heatmap anotado (números sempre legíveis)
    renomear_series()   nomes legíveis das séries na legenda e no hover
    feixes_de_luz_svg() fundo decorativo do hero da página inicial
"""
import copy

import streamlit as st
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go

# ──────────────────────────────────────────────────────────────────────────────
# Paleta
# ──────────────────────────────────────────────────────────────────────────────
FUNDO        = "#040F2E"   # azul-noite
SUPERFICIE   = "#0A1F52"   # cards, sidebar
ATIVO        = "#102C6E"   # hover / item ativo
PROFUNDO     = "#061640"   # campos, tooltips
BORDA        = "rgba(69,137,255,0.22)"
PRIMARIA     = "#0F62FE"   # azul elétrico (botões, destaques, barras)
AZUL_CLARO   = "#4589FF"   # linhas, brilhos
AZUL_CLARO_2 = "#78A9FF"
GELO         = "#A6C8FF"   # séries secundárias
GELO_CLARO   = "#D0E2FF"
TEXTO        = "#C9D9F7"   # texto corrido
TEXTO_SUAVE  = "#8FA9DB"   # legendas, eixos (contraste ≥ 5:1 sobre as superfícies)
BRANCO       = "#FFFFFF"   # títulos e números-chave

CORES = {
    "serie":     AZUL_CLARO,   # série única (linhas, barras muito densas)
    "barra":     PRIMARIA,     # série única (barras)
    "tendencia": BRANCO,       # linhas de tendência OLS
}

# Duas séries: azul × azul-gelo. Demais tons só entram se houver mais séries.
SEQ_CATEGORICA = [AZUL_CLARO, GELO_CLARO, PRIMARIA, GELO, AZUL_CLARO_2, BRANCO]

# Sequencial: azul profundo → azul-gelo
ESCALA_AZUL = [[0.0, "#123A8F"], [0.55, "#3B7CF5"], [1.0, GELO_CLARO]]

# Z-scores: o sinal muda o tom (corte seco em 0), a intensidade cresce com |z|.
#   negativos → azul-gelo (mais claro quanto mais negativo)
#   positivos → azul elétrico (mais saturado quanto mais positivo)
# Os tons perto de zero continuam com contraste ≥ 3:1 sobre o card.
ESCALA_ZSCORE = [
    [0.0, "#F2F7FF"],
    [0.5, "#9DB9EC"],
    [0.5, "#3F74E0"],
    [1.0, PRIMARIA],
]

# Matrizes de confusão: azul profundo (poucos casos) → azul-gelo (muitos casos)
ESCALA_MATRIZ = ESCALA_AZUL

FONTE = "'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif"

# Nomes legíveis para eixos, legendas e hover (sem inventar unidades)
ROTULOS = {
    "data": "Data",
    "data_mes": "Mês",
    "data_semana": "Semana",
    "zwd_medio": "ZWD médio",
    "ZWD_media_mensal": "Soma mensal do ZWD",
    "zwd_medio_mensal": "ZWD médio mensal",
    "precipitacao_mm": "Precipitação (mm)",
    "precipitacao_mensal": "Precipitação mensal (mm)",
    "tendencia": "Tendência",
    "sazonalidade": "Sazonalidade",
    "residuo": "Resíduo",
    "lag_dias": "Defasagem (dias)",
    "correlacao": "Correlação",
    "zscore_zwd": "Z-score ZWD",
    "zscore_prec": "Z-score Precipitação",
    "value": "Valor",
    "variable": "Série",
}


# ──────────────────────────────────────────────────────────────────────────────
# Tema dos gráficos (Plotly)
# ──────────────────────────────────────────────────────────────────────────────
# O st.plotly_chart aplica o tema do próprio Streamlit por cima do template do
# Plotly; só valores gravados na figura sobrevivem. Por isso o tema existe como
# dicionário: vira template global e também é gravado na figura por
# estilo_plotly(), usado em cada st.plotly_chart das páginas.
_EIXO = dict(
    showgrid=True, gridcolor="rgba(166,200,255,0.07)", gridwidth=1,
    zeroline=True, zerolinecolor="rgba(166,200,255,0.30)", zerolinewidth=1,
    showline=True, linecolor="rgba(166,200,255,0.22)", linewidth=1,
    ticks="", automargin=True,
    tickfont=dict(family=FONTE, size=11, color=TEXTO_SUAVE),
    title=dict(font=dict(family=FONTE, size=12, color=GELO), standoff=12),
)
_COLORBAR = dict(
    outlinewidth=0, thickness=10, ticks="",
    tickfont=dict(family=FONTE, size=11, color=TEXTO_SUAVE),
)
_LAYOUT = dict(
    font=dict(family=FONTE, size=12, color=TEXTO),
    paper_bgcolor="rgba(0,0,0,0)",      # transparente: aparece o card
    plot_bgcolor="rgba(0,0,0,0)",
    colorway=SEQ_CATEGORICA,
    xaxis=_EIXO, yaxis=_EIXO,
    bargap=0.18,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
        font=dict(family=FONTE, size=12, color=TEXTO),
        title=dict(font=dict(family=FONTE, size=12, color=TEXTO_SUAVE), side="left"),
    ),
    hoverlabel=dict(
        bgcolor=PROFUNDO, bordercolor=AZUL_CLARO,
        font=dict(family=FONTE, size=12, color=BRANCO),
    ),
    coloraxis=dict(colorbar=_COLORBAR),
    modebar=dict(bgcolor="rgba(0,0,0,0)", color=TEXTO_SUAVE, activecolor=BRANCO),
)
_MARGEM = dict(l=16, r=24, t=24, b=12)   # o resto vem do automargin dos eixos
_MARGEM_TOPO_LEGENDA = 56                # espaço para a legenda horizontal no topo


def _registrar_template() -> None:
    tema = go.layout.Template()
    tema.layout = go.Layout(
        **_LAYOUT, margin=_MARGEM,
        title=dict(font=dict(family=FONTE, size=16, color=BRANCO), x=0.0, xanchor="left"),
        colorscale=dict(sequential=ESCALA_AZUL, diverging=ESCALA_ZSCORE),
    )
    tema.data.bar = [go.Bar(marker=dict(line=dict(width=0)))]
    tema.data.heatmap = [go.Heatmap(colorbar=_COLORBAR)]
    pio.templates["noite"] = tema
    # base escura do Plotly + nossas cores por cima
    pio.templates.default = "plotly_dark+noite"
    px.defaults.template = "plotly_dark+noite"
    px.defaults.color_discrete_sequence = SEQ_CATEGORICA
    px.defaults.color_continuous_scale = ESCALA_AZUL


def _preencher(destino: dict, base: dict) -> dict:
    """Copia de `base` só o que a figura ainda não definiu (recursivo)."""
    for chave, valor in base.items():
        if chave not in destino:
            destino[chave] = copy.deepcopy(valor)
        elif isinstance(valor, dict) and isinstance(destino[chave], dict):
            _preencher(destino[chave], valor)
    return destino


def estilo_plotly(fig: go.Figure, altura: int | None = None) -> go.Figure:
    """Grava o tema na figura, para valer também sob o tema do Streamlit.

    O que a página já definiu na figura (títulos de eixo, legenda, cores das
    séries...) é mantido; o tema só preenche o resto.
    """
    layout = fig.layout.to_plotly_json()
    layout.pop("template", None)
    fig.update_layout(_preencher(layout, _LAYOUT))
    legenda = fig.layout.showlegend
    if legenda is None:  # regra do Plotly: legenda aparece com 2+ séries visíveis
        legenda = sum(1 for t in fig.data if t.showlegend is not False) > 1
    fig.update_layout(margin=dict(_MARGEM, t=_MARGEM_TOPO_LEGENDA if legenda else _MARGEM["t"]))
    if altura:
        fig.update_layout(height=altura)
    return fig


def renomear_series(fig: go.Figure, nomes: dict = ROTULOS) -> go.Figure:
    """Troca nomes crus de colunas por nomes legíveis na legenda e no hover."""
    for trace in fig.data:
        novo = nomes.get(trace.name)
        if novo:
            if trace.hovertemplate:
                trace.hovertemplate = trace.hovertemplate.replace(f"={trace.name}<", f"={novo}<")
            trace.name = novo
    return fig


def estilo_matriz(fig: go.Figure) -> go.Figure:
    """Heatmap anotado (matriz de confusão): números grandes, sempre legíveis.

    O figure_factory já escolhe texto claro nas células escuras e texto escuro
    nas claras; aqui só trocamos o preto pelo azul-noite e aumentamos o corpo.
    """
    for anotacao in fig.layout.annotations:
        escuro = str(anotacao.font.color).lower() in ("#000000", "black", "#000")
        anotacao.font.color = FUNDO if escuro else BRANCO
        anotacao.font.size = 22
        anotacao.font.family = FONTE
    fig.update_traces(xgap=3, ygap=3, colorbar=_COLORBAR)
    fig.update_xaxes(showgrid=False, zeroline=False, showline=False)
    fig.update_yaxes(showgrid=False, zeroline=False, showline=False)
    return estilo_plotly(fig)


# ──────────────────────────────────────────────────────────────────────────────
# Fundo do hero: feixes de luz convergindo para um ponto de fuga (SVG inline)
# ──────────────────────────────────────────────────────────────────────────────
def feixes_de_luz_svg() -> str:
    """SVG decorativo do hero: feixes azuis que convergem para um ponto de
    fuga e uma nuvem de partículas. Determinístico (semente fixa)."""
    import math
    import random

    rnd = random.Random(7)
    vx, vy = 770.0, 285.0          # ponto de fuga (≈ 64% × 41% do hero)
    comp = 1500.0                  # comprimento dos feixes (saem do quadro)

    # Leques de ângulos (graus, eixo y para baixo). O quadrante inferior
    # direito fica livre para não passar atrás do parágrafo de apoio.
    leques = [(150, 212, 13), (212, 300, 9), (300, 352, 6), (95, 150, 4)]
    feixes = []
    for a0, a1, n in leques:
        for _ in range(n):
            ang = math.radians(rnd.uniform(a0, a1))
            meia = math.radians(rnd.uniform(0.12, 1.1))
            op = rnd.uniform(0.25, 0.85)
            x1, y1 = vx + comp * math.cos(ang - meia), vy + comp * math.sin(ang - meia)
            x2, y2 = vx + comp * math.cos(ang + meia), vy + comp * math.sin(ang + meia)
            feixes.append(
                f'<path d="M{vx:.0f} {vy:.0f}L{x1:.0f} {y1:.0f}L{x2:.0f} {y2:.0f}Z" '
                f'fill="url(#hf-raio)" opacity="{op:.2f}"/>'
            )
    riscos = []
    for _ in range(9):
        ang = math.radians(rnd.choice([rnd.uniform(155, 205), rnd.uniform(215, 340)]))
        x2, y2 = vx + comp * math.cos(ang), vy + comp * math.sin(ang)
        riscos.append(
            f'<line x1="{vx:.0f}" y1="{vy:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="url(#hf-raio)" stroke-width="{rnd.uniform(0.6, 1.4):.1f}"/>'
        )

    grupos = {"a": [], "b": [], "c": []}
    for i in range(170):
        r = rnd.expovariate(1 / 150.0)
        ang = rnd.uniform(0, 2 * math.pi)
        x = vx + 1.5 * r * math.cos(ang)
        y = vy + 0.8 * r * math.sin(ang)
        if not (-20 < x < 1220 and -20 < y < 720):
            continue
        cor = rnd.choice(["#78A9FF", "#4589FF", "#4589FF", "#A6C8FF", "#D0E2FF", "#FFFFFF"])
        tam = rnd.uniform(0.5, 1.4) if r > 90 else rnd.uniform(0.8, 2.2)
        op = rnd.uniform(0.35, 1.0)
        grupos["abc"[i % 3]].append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{tam:.1f}" fill="{cor}" opacity="{op:.2f}"/>'
        )

    return (
        '<svg viewBox="0 0 1200 700" preserveAspectRatio="xMidYMid slice" '
        'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
        '<defs>'
        f'<radialGradient id="hf-raio" gradientUnits="userSpaceOnUse" cx="{vx:.0f}" cy="{vy:.0f}" r="900">'
        '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.95"/>'
        '<stop offset="0.05" stop-color="#78A9FF" stop-opacity="0.85"/>'
        '<stop offset="0.32" stop-color="#0F62FE" stop-opacity="0.40"/>'
        '<stop offset="0.75" stop-color="#0F62FE" stop-opacity="0.08"/>'
        '<stop offset="1" stop-color="#0F62FE" stop-opacity="0"/>'
        '</radialGradient>'
        f'<radialGradient id="hf-halo" gradientUnits="userSpaceOnUse" cx="{vx:.0f}" cy="{vy:.0f}" r="300">'
        '<stop offset="0" stop-color="#4589FF" stop-opacity="0.55"/>'
        '<stop offset="0.4" stop-color="#0F62FE" stop-opacity="0.18"/>'
        '<stop offset="1" stop-color="#0F62FE" stop-opacity="0"/>'
        '</radialGradient>'
        '</defs>'
        f'<ellipse cx="{vx:.0f}" cy="{vy:.0f}" rx="520" ry="300" fill="url(#hf-halo)"/>'
        f'<g class="feixes">{"".join(feixes)}{"".join(riscos)}</g>'
        f'<circle cx="{vx:.0f}" cy="{vy:.0f}" r="3" fill="#FFFFFF"/>'
        f'<g class="particulas-a">{"".join(grupos["a"])}</g>'
        f'<g class="particulas-b">{"".join(grupos["b"])}</g>'
        f'<g class="particulas-c">{"".join(grupos["c"])}</g>'
        '</svg>'
    )


# ──────────────────────────────────────────────────────────────────────────────
# CSS global
# ──────────────────────────────────────────────────────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root{
  --fundo:#040F2E; --superficie:#0A1F52; --ativo:#102C6E; --profundo:#061640;
  --borda:rgba(69,137,255,0.22); --borda-forte:rgba(69,137,255,0.45);
  --azul:#0F62FE; --azul-claro:#4589FF; --azul-claro-2:#78A9FF;
  --gelo:#A6C8FF; --gelo-claro:#D0E2FF;
  --texto:#C9D9F7; --texto-suave:#8FA9DB; --branco:#FFFFFF;
  --fonte:'IBM Plex Sans','Helvetica Neue',Arial,sans-serif;
}

/* ───────── Base ───────── */
.stApp{
  font-family:var(--fonte);
  color:var(--texto);
  background:
    radial-gradient(1100px 520px at 92% -12%, rgba(15,98,254,0.10), transparent 62%),
    var(--fundo);
}
[data-testid="stHeader"]{
  background:rgba(4,15,46,0.72);
  backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
}
footer{ visibility:hidden; }
.block-container, [data-testid="stMainBlockContainer"]{
  max-width:1240px; padding-top:3.4rem; padding-bottom:4.5rem;
}

/* ───────── Tipografia ───────── */
.stApp h1, .stApp h2, .stApp h3, .stApp h4{
  color:var(--branco) !important; font-family:var(--fonte);
}
.stApp h1{
  font-weight:300 !important; font-size:clamp(2.2rem, 3.4vw, 3.15rem);
  letter-spacing:-0.025em; line-height:1.08; padding-bottom:1.1rem;
}
.stApp h2{
  font-weight:300 !important; font-size:clamp(1.6rem, 2.3vw, 2.05rem);
  letter-spacing:-0.015em; line-height:1.15;
}
.stApp h3{
  font-weight:400 !important; font-size:1.22rem; letter-spacing:-0.005em;
  line-height:1.3; margin-top:0.9rem;
}
/* marcador quadrado em azul elétrico antes dos subtítulos */
[data-testid="stMain"] h3::before{
  content:""; display:inline-block; width:7px; height:7px; margin:0 12px 0 1px;
  vertical-align:0.2em; background:var(--azul);
  box-shadow:0 0 10px rgba(69,137,255,0.85);
}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li{
  color:var(--texto); line-height:1.65;
}
.stApp strong, .stApp b{ color:var(--branco); font-weight:600; }
.stApp a{ color:var(--azul-claro-2); }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p{
  color:var(--texto-suave) !important; font-size:0.86rem; line-height:1.55;
  opacity:1 !important;   /* o Streamlit aplica 0.6 e o contraste cai abaixo de 4.5:1 */
}
[data-testid="stCaptionContainer"] strong{ color:var(--gelo-claro); }
.stApp hr{ border:none !important; border-top:1px solid var(--borda) !important; margin:2.6rem 0 1.4rem; }

/* ───────── Métricas ───────── */
[data-testid="stMetric"]{
  position:relative; overflow:hidden;
  background:linear-gradient(180deg, rgba(16,44,110,0.55) 0%, rgba(10,31,82,0.92) 100%);
  border:1px solid var(--borda); border-radius:2px; padding:18px 20px 16px;
  transition:border-color .2s ease, box-shadow .2s ease;
}
[data-testid="stMetric"]::before{
  content:""; position:absolute; left:0; top:0; height:1px; width:100%;
  background:linear-gradient(90deg, var(--azul-claro) 0%, rgba(69,137,255,0) 75%);
}
[data-testid="stMetric"]:hover{
  border-color:var(--borda-forte); box-shadow:0 0 24px -8px rgba(15,98,254,0.55);
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *{
  color:var(--texto-suave) !important; font-size:0.8rem !important;
  font-weight:500 !important; letter-spacing:0.02em;
}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] *{
  color:var(--branco) !important; font-weight:300 !important;
  font-size:clamp(1.7rem, 2.5vw, 2.45rem) !important;
  letter-spacing:-0.02em; line-height:1.15;
}

/* cards de uma mesma linha com a mesma altura */
[data-testid="stColumn"]:has([data-testid="stMetric"]) [data-testid="stVerticalBlock"],
[data-testid="stColumn"]:has([data-testid="stMetric"]) [data-testid="stElementContainer"]:has([data-testid="stMetric"]),
[data-testid="stColumn"]:has([data-testid="stMetric"]) [data-testid="stMetric"]{ height:100%; }
/* rótulos longos quebram linha em vez de virar "..." */
[data-testid="stMetricLabel"] *{ white-space:normal !important; overflow:visible !important; text-overflow:clip !important; }
/* página inicial: valores textuais (local, estação) acompanham a largura do cartão
   e quebram entre palavras em vez de cortar */
.stApp:has(.hero) [data-testid="stMetric"]{ container-type:inline-size; }
.stApp:has(.hero) [data-testid="stMetricValue"], .stApp:has(.hero) [data-testid="stMetricValue"] *{
  font-size:clamp(1.05rem, 12cqi, 1.95rem) !important; line-height:1.2 !important;
  white-space:normal !important; overflow:visible !important; text-overflow:clip !important;
  overflow-wrap:normal !important; word-break:normal !important;
}

/* ───────── Gráficos em card ───────── */
[data-testid="stPlotlyChart"]{
  background:linear-gradient(180deg, #0B2259 0%, var(--superficie) 100%);
  border:1px solid var(--borda); border-radius:2px;
  padding:12px 0 6px;   /* sem padding lateral: o Plotly usa a largura toda */
  box-shadow:0 22px 44px -34px rgba(15,98,254,0.75);
}

/* ───────── Tabelas ───────── */
[data-testid="stDataFrame"], [data-testid="stTable"]{
  border:1px solid var(--borda); border-radius:2px; background:var(--superficie);
}

/* ───────── Avisos (info / warning) ───────── */
[data-testid="stAlertContainer"]{
  border-radius:2px !important; border:1px solid var(--borda);
  border-left:2px solid var(--azul-claro);
  background:rgba(15,98,254,0.12) !important;
}
[data-testid="stAlertContainer"] p, [data-testid="stAlertContainer"] div{ color:var(--gelo-claro) !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]){
  border-left-color:var(--gelo-claro); background:rgba(208,226,255,0.07) !important;
}

/* ───────── Abas ───────── */
[data-testid="stTab"]{ font-weight:500; }
[data-testid="stTab"] p{ color:var(--texto-suave); font-size:0.95rem; }
[data-testid="stTab"][aria-selected="true"] p{ color:var(--branco); }
[data-baseweb="tab-highlight"]{ background:var(--azul) !important; height:2px; }
[data-baseweb="tab-border"]{ background:var(--borda) !important; }

/* ───────── Widgets ───────── */
[data-testid="stWidgetLabel"] p{ color:var(--texto) !important; font-weight:500; }
[data-baseweb="select"] > div{ border-radius:2px !important; }
[data-testid="stTooltipIcon"] svg{ color:var(--texto-suave); }
.stButton > button, .stDownloadButton > button{
  border-radius:0; border:1px solid var(--azul); background:var(--azul);
  color:var(--branco) !important; font-weight:500;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  background:#0050E6; border-color:#0050E6;
}

/* ───────── Barra lateral ───────── */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg, #0A1F52 0%, #081A49 45%, #06163F 100%) !important;
  border-right:1px solid var(--borda);
}
[data-testid="stSidebar"] > div:first-child{ background:transparent; }
[data-testid="stSidebarNav"]{ margin-top:34px; }
[data-testid="stNavSectionHeader"], [data-testid="stNavSectionHeader"] *{
  color:var(--texto-suave) !important; font-size:0.72rem !important;
  font-weight:600 !important; letter-spacing:0.12em;
}
[data-testid="stSidebarNavLink"]{
  border-radius:0 !important; transition:background .15s ease;
}
[data-testid="stSidebarNavLink"] span{ color:var(--texto) !important; }
[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"]{ color:var(--texto-suave) !important; }
[data-testid="stSidebarNavLink"]:hover{ background:var(--ativo) !important; }
[data-testid="stSidebarNavLink"][aria-current="page"]{
  background:linear-gradient(90deg, rgba(15,98,254,0.30) 0%, rgba(15,98,254,0.08) 100%) !important;
  box-shadow:inset 3px 0 0 var(--azul);
}
[data-testid="stSidebarNavLink"][aria-current="page"] span{ color:var(--branco) !important; font-weight:600; }
[data-testid="stSidebarNavLink"][aria-current="page"] [data-testid="stIconMaterial"]{
  color:var(--azul-claro) !important;
}
[data-testid="stSidebarNavSeparator"]{ border-color:var(--borda) !important; }
/* título "Controles" da barra lateral como rótulo discreto */
[data-testid="stSidebar"] h1{
  font-size:0.78rem !important; font-weight:600 !important; letter-spacing:0.12em;
  color:var(--texto-suave) !important; padding:0.6rem 0 0.35rem !important;
}

/* Cabeçalho da barra lateral: levado ao topo, acima da navegação */
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.sb-marca),
[data-testid="stSidebarUserContent"] .element-container:has(.sb-marca){
  position:absolute !important; top:18px; left:0; right:0; padding:0 1.5rem;
}
.sb-marca{ display:flex; align-items:center; gap:12px; padding-right:1.6rem; }
.sb-marca svg{ flex:0 0 auto; }
.sb-marca-titulo{ color:var(--branco); font-weight:600; font-size:0.98rem; line-height:1.2; letter-spacing:-0.005em; }
.sb-marca-sub{ color:var(--texto-suave); font-size:0.74rem; margin-top:3px; white-space:nowrap; }

/* ───────── Página inicial: hero ───────── */
.hero{
  position:relative; isolation:isolate; overflow:hidden; container-type:inline-size;
  min-height:clamp(560px, calc(100vh - 7rem), 900px);
  display:flex; flex-direction:column; justify-content:space-between;
  padding:6px 0 48px; margin:-1.2rem 0 3.2rem;
}
.hero-luz{
  position:absolute; inset:0; z-index:-1; pointer-events:none;
  /* bordas dissolvidas no fundo: sem retângulo visível */
  -webkit-mask-image:
    linear-gradient(90deg, transparent 0%, #000 16%, #000 86%, transparent 100%),
    linear-gradient(180deg, transparent 0%, #000 14%, #000 70%, transparent 100%);
  -webkit-mask-composite:source-in;
          mask-image:
    linear-gradient(90deg, transparent 0%, #000 16%, #000 86%, transparent 100%),
    linear-gradient(180deg, transparent 0%, #000 14%, #000 70%, transparent 100%);
          mask-composite:intersect;
}
.hero-luz svg{ width:100%; height:100%; display:block; }
.hero .badge{
  display:inline-flex; align-items:center; gap:10px;
  color:var(--gelo); font-size:0.78rem; font-weight:500; letter-spacing:0.08em;
  padding:7px 12px; border:1px solid var(--borda); background:rgba(4,15,46,0.55);
}
.hero .badge::before{
  content:""; width:6px; height:6px; background:var(--azul-claro);
  box-shadow:0 0 10px var(--azul-claro);
}
.hero-corpo{
  display:grid; grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);
  gap:40px; align-items:end;
}
.hero-titulo{
  color:var(--branco); font-weight:300; letter-spacing:-0.035em; line-height:0.98;
  font-size:clamp(2.6rem, 4.6vw, 5.2rem); margin:0;
  font-size:clamp(2.6rem, 6.8cqi, 5.6rem);
}
.hero-titulo span{ display:block; }
.hero-apoio{ max-width:400px; justify-self:end; padding-bottom:10px; }
.hero-apoio p{
  color:var(--texto-suave) !important; font-size:0.98rem; line-height:1.65; margin:0 0 26px;
}
.hero-apoio p strong{ color:var(--branco); font-weight:600; }
.hero-botao, .hero-botao:visited{
  display:inline-flex; align-items:center; justify-content:space-between; gap:36px;
  min-width:220px; padding:15px 18px 15px 20px;
  background:var(--azul); color:var(--branco) !important; text-decoration:none !important;
  font-size:0.95rem; font-weight:500; border-radius:0;
  transition:background .2s ease, box-shadow .2s ease;
}
.hero-botao:hover{ background:#0050E6; box-shadow:0 0 30px -6px rgba(15,98,254,0.9); }
.hero-botao svg{ transition:transform .2s ease; }
.hero-botao:hover svg{ transform:translateX(4px); }
@media (max-width:900px){
  .hero-corpo{ grid-template-columns:1fr; gap:28px; }
  .hero-apoio{ justify-self:start; }
}

/* animação lenta, só para quem não pediu movimento reduzido */
@media (prefers-reduced-motion: no-preference){
  .hero-luz .feixes{ animation:respirar 14s ease-in-out infinite; }
  .hero-luz .particulas-a{ animation:cintilar 9s ease-in-out infinite; }
  .hero-luz .particulas-b{ animation:cintilar 13s ease-in-out -4s infinite; }
  .hero-luz .particulas-c{ animation:derivar 22s ease-in-out infinite alternate; }
}
@keyframes respirar{ 0%,100%{ opacity:.82; } 50%{ opacity:1; } }
@keyframes cintilar{ 0%,100%{ opacity:.35; } 50%{ opacity:1; } }
@keyframes derivar{ from{ transform:translate(0,0); } to{ transform:translate(-14px,6px); } }

/* ───────── Página inicial: cards de navegação ───────── */
.nav-grid{
  display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:1px;
  background:var(--borda); border:1px solid var(--borda); margin-top:10px;
}
@media (max-width:1100px){ .nav-grid{ grid-template-columns:repeat(2, minmax(0,1fr)); } }
@media (max-width:640px){ .nav-grid{ grid-template-columns:1fr; } }
.nav-card, .nav-card:visited{
  position:relative; display:flex; flex-direction:column; gap:10px; min-height:250px;
  padding:22px 22px 20px; background:var(--superficie);
  color:inherit; text-decoration:none !important; transition:background .2s ease;
}
.nav-card::before{
  content:""; position:absolute; left:0; top:0; height:2px; width:0;
  background:var(--azul); transition:width .3s ease;
}
.nav-card:hover{ background:var(--ativo); }
.nav-card:hover::before{ width:100%; }
.nav-num{ color:var(--azul-claro); font-size:0.8rem; font-weight:500; letter-spacing:0.08em; }
.nav-titulo{ color:var(--branco); font-size:1.28rem; font-weight:300; letter-spacing:-0.01em; margin-top:18px; }
.nav-card p{ color:var(--texto-suave) !important; font-size:0.9rem; line-height:1.55; margin:0; }
.nav-seta{ margin-top:auto; color:var(--azul-claro); }
.nav-seta svg{ transition:transform .2s ease; }
.nav-card:hover .nav-seta svg{ transform:translateX(5px); }
.hero-botao:focus-visible, .nav-card:focus-visible{ outline:2px solid var(--azul-claro-2); outline-offset:3px; }
</style>
"""


def aplicar_estilo() -> None:
    """Registra o template Plotly e injeta o CSS. Chamar uma única vez."""
    _registrar_template()
    st.markdown(_CSS, unsafe_allow_html=True)
