import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np

from CalcularRM import preparar_dados_dashboard, calc_anomalia_zwd, calc_anomalia_zwd_semanal
from CalcularPrecipitacao import carregar_precipitacao, calc_anomalia_precipitacao, calc_anomalia_precipitacao_semanal
from CalcularCorrelacoes import (
    merge_zwd_precipitacao,
    correlacao_diaria,
    agregar_mensal,
    correlacao_mensal,
    correlacao_com_defasagem,
    correlacao_anomalias_mensal,
    correlacao_anomalias_semanal,
    matriz_confusao_sinais,
    ajustar_curvas,
)

_CORES_MODELOS = {
    "Linear":           "#EF553B",
    "Logarítmica":      "#00CC96",
    "Raiz quadrada":    "#AB63FA",
    "Michaelis-Menten": "#FFA15A",
}


def _secao_ajuste(x, y, label_x, label_y, escala):
    """Exibe gráfico multi-curva + tabela de indicadores de qualidade."""
    df_stats, curvas = ajustar_curvas(x, y)
    if df_stats.empty:
        st.warning("Dados insuficientes para ajuste de curvas.")
        return

    x_range = np.linspace(0.0, float(x.max()), 400)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers", name="Dados observados",
        marker=dict(size=5, opacity=0.45, color="#636EFA"),
    ))
    for nome, fn in curvas:
        fig.add_trace(go.Scatter(
            x=x_range, y=fn(x_range), mode="lines", name=nome,
            line=dict(width=2.5, color=_CORES_MODELOS.get(nome, "gray")),
        ))
    fig.update_layout(
        xaxis_title=label_x,
        yaxis_title=label_y,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de qualidade de ajuste
    st.caption(f"Indicadores de qualidade do ajuste — escala {escala}")
    df_show = df_stats.copy()

    # Destaca o melhor R² (maior valor)
    idx_best = df_show["R²"].idxmax()

    df_show["R²"]   = df_show["R²"].map("{:.4f}".format)
    df_show["RMSE"] = df_show["RMSE"].map("{:.3f}".format)
    df_show["MAE"]  = df_show["MAE"].map("{:.3f}".format)

    def _highlight(row):
        return ["font-weight: bold; background-color: #d4edda" if row.name == idx_best else "" for _ in row]

    st.dataframe(
        df_show.style.apply(_highlight, axis=1),
        hide_index=True,
        use_container_width=True,
    )

st.title("🔗 Correlações — ZWD × Precipitação")

# -------------------------------------------------------------------- sidebar
st.sidebar.title("⚙️ Controles")

metodo = st.sidebar.selectbox(
    "**Método de correlação**",
    ["pearson", "spearman", "kendall"],
    index=0,
    help=(
        "Pearson: relação linear.\n\n"
        "Spearman/Kendall: monotônica (mais robusto a outliers e não-linearidades)."
    ),
)

lag_max = st.sidebar.slider(
    "**Defasagem máxima (± dias)**",
    min_value=5, max_value=60, value=15, step=1,
    help="Define a janela da correlação cruzada com lags positivos e negativos.",
)

# -------------------------------------------------------------------- dados
df_zwd    = preparar_dados_dashboard(ano=None)
df_precip = carregar_precipitacao(ano=None)
df_join   = merge_zwd_precipitacao(df_zwd, df_precip)

if df_join.empty:
    st.warning(
        "Sem sobreposição entre as séries de ZWD e Precipitação. "
        "Verifique se a tabela `precipitacao_diaria` foi populada."
    )
    st.stop()

# -------------------------------------------------------------------- métricas
df_mensal = agregar_mensal(df_join)
corr_dia  = correlacao_diaria(df_join, metodo=metodo)
corr_mes  = correlacao_mensal(df_mensal, metodo=metodo)

c1, c2, c3 = st.columns(3)
c1.metric("Dias pareados", len(df_join))
c2.metric(f"Corr. diária ({metodo})", f"{corr_dia:.3f}")
c3.metric(f"Corr. mensal ({metodo})", f"{corr_mes:.3f}")

# -------------------------------------------------------------------- dispersão + ajuste diário
st.subheader("Dispersão diária — ZWD vs Precipitação")
_secao_ajuste(
    x=df_join["precipitacao_mm"].values,
    y=df_join["zwd_medio"].values,
    label_x="Precipitação (mm/dia)",
    label_y="ZWD médio",
    escala="diária",
)

# -------------------------------------------------------------------- dispersão + ajuste mensal
st.subheader("Dispersão mensal — ZWD (média) vs Precipitação (soma)")
_secao_ajuste(
    x=df_mensal["precipitacao_mensal"].values,
    y=df_mensal["zwd_medio_mensal"].values,
    label_x="Precipitação mensal (mm)",
    label_y="ZWD médio mensal",
    escala="mensal",
)

# -------------------------------------------------------------------- série dual
st.subheader("Séries sobrepostas (escala mensal)")
fig = px.line(
    df_mensal,
    x="data_mes",
    y=["zwd_medio_mensal", "precipitacao_mensal"],
)
fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=4))
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------------- lag
st.subheader("Correlação cruzada com defasagem")
st.caption(
    "Lag positivo: precipitação **deslocada para frente** "
    "(ZWD de hoje vs chuva de daqui a *N* dias). "
    "Lag negativo: chuva precede o ZWD."
)

df_lag = correlacao_com_defasagem(
    df_join,
    lags=range(-lag_max, lag_max + 1),
    metodo=metodo,
)
fig = px.bar(df_lag, x="lag_dias", y="correlacao")
fig.update_layout(xaxis_title="Defasagem (dias)", yaxis_title=f"Correlação ({metodo})")
st.plotly_chart(fig, use_container_width=True)

idx_max = df_lag["correlacao"].abs().idxmax()
lag_pico  = int(df_lag.loc[idx_max, "lag_dias"])
corr_pico = float(df_lag.loc[idx_max, "correlacao"])
st.info(f"Pico de correlação em **lag = {lag_pico} dias** → corr = **{corr_pico:.3f}**")

# -------------------------------------------------------------------- anomalias mensais
st.divider()
st.header("📉 Correlações das Anomalias Mensais")
st.markdown(
    "Correlação entre as **anomalias mensais** de ZWD e de precipitação — "
    "ou seja, os desvios em relação à climatologia de cada mês."
)

df_anom_zwd  = calc_anomalia_zwd(df_zwd)
df_anom_prec = calc_anomalia_precipitacao(df_precip)

corr_anom, df_anom_merged = correlacao_anomalias_mensal(
    df_anom_zwd, df_anom_prec, metodo=metodo
)

if df_anom_merged.empty:
    st.warning("Sem sobreposição entre as anomalias de ZWD e Precipitação.")
else:
    c1, c2 = st.columns(2)
    c1.metric("Meses pareados (anomalias)", len(df_anom_merged))
    c2.metric(f"Corr. anomalias ({metodo})", f"{corr_anom:.3f}")

    df_anom_merged = df_anom_merged.merge(
        df_anom_zwd[["ano", "mes", "zscore_zwd"]], on=["ano", "mes"], how="left"
    ).merge(
        df_anom_prec[["ano", "mes", "zscore_prec"]], on=["ano", "mes"], how="left"
    )

    st.subheader("Dispersão — anomalia mensal do ZWD (Z-Score) vs anomalia mensal da precipitação (Z-Score)")
    fig = px.scatter(
        df_anom_merged,
        x="zscore_prec",
        y="zscore_zwd",
        trendline="ols",
        opacity=0.6,
        labels={"zscore_prec": "Z-score Precipitação", "zscore_zwd": "Z-score ZWD"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Séries temporais dos Z-scores mensais")
    fig = px.line(
        df_anom_merged,
        x="data_mes",
        y=["zscore_zwd", "zscore_prec"],
        labels={"value": "Z-score", "variable": "Variável", "data_mes": "Mês"},
    )
    fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=4))
    newnames = {"zscore_zwd": "Z-score ZWD", "zscore_prec": "Z-score Precipitação"}
    fig.for_each_trace(lambda t: t.update(name=newnames.get(t.name, t.name)))
    st.plotly_chart(fig, use_container_width=True)

    # ---- matriz de confusão mensal
    st.subheader("Matriz de confusão de sinais — Z-scores mensais")
    st.caption(
        "Cada célula mostra quantas vezes os sinais do Z-score ZWD e da "
        "Z-score Precipitação coincidem (diagonal) ou divergem (fora da diagonal)."
    )
    conf_mes = matriz_confusao_sinais(df_anom_merged, "zscore_zwd", "zscore_prec")

    total_mes       = int(conf_mes.values.sum())
    concordancia_mes = int(np.trace(conf_mes.values))
    pct_mes         = concordancia_mes / total_mes * 100 if total_mes else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de meses", total_mes)
    c2.metric("Sinais concordantes", concordancia_mes)
    c3.metric("Taxa de concordância", f"{pct_mes:.1f} %")

    z_vals   = conf_mes.values.tolist()
    x_labels = list(conf_mes.columns)
    y_labels = list(conf_mes.index)
    annot    = [[str(v) for v in row] for row in z_vals]

    fig_conf = ff.create_annotated_heatmap(
        z=z_vals,
        x=x_labels,
        y=y_labels,
        annotation_text=annot,
        colorscale="Blues",
        showscale=True,
    )
    fig_conf.update_layout(
        xaxis_title="Z-score Precipitação",
        yaxis_title="Z-score ZWD",
        xaxis=dict(side="bottom"),
    )
    st.plotly_chart(fig_conf, use_container_width=True)


# -------------------------------------------------------------------- anomalias semanais
st.divider()
st.header("📅 Correlações das Anomalias Semanais")
st.markdown(
    "Mesma análise das anomalias, mas agregada por **semana ISO** "
    "(semana que começa na segunda-feira)."
)

df_anom_zwd_sem  = calc_anomalia_zwd_semanal(df_zwd)
df_anom_prec_sem = calc_anomalia_precipitacao_semanal(df_precip)

corr_anom_sem, df_anom_merged_sem = correlacao_anomalias_semanal(
    df_anom_zwd_sem, df_anom_prec_sem, metodo=metodo
)

if df_anom_merged_sem.empty:
    st.warning("Sem sobreposição entre as anomalias semanais de ZWD e Precipitação.")
else:
    c1, c2 = st.columns(2)
    c1.metric("Semanas pareadas (anomalias)", len(df_anom_merged_sem))
    c2.metric(f"Corr. anomalias semanais ({metodo})", f"{corr_anom_sem:.3f}")

    st.subheader("Dispersão — anomalia semanal do ZWD (Z-Score) vs anomalia semanal da precipitação (Z-Score)")
    fig = px.scatter(
        df_anom_merged_sem,
        x="zscore_prec",
        y="zscore_zwd",
        trendline="ols",
        opacity=0.6,
        labels={"zscore_prec": "Z-score Precipitação (semanal)", "zscore_zwd": "Z-score ZWD (semanal)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Séries temporais dos Z-scores semanais")
    fig = px.line(
        df_anom_merged_sem,
        x="data_semana",
        y=["zscore_zwd", "zscore_prec"],
        labels={"value": "Z-score", "variable": "Variável", "data_semana": "Semana"},
    )
    fig.update_traces(mode="lines+markers", line=dict(width=1.5), marker=dict(size=3))
    newnames = {"zscore_zwd": "Z-score ZWD", "zscore_prec": "Z-score Precipitação"}
    fig.for_each_trace(lambda t: t.update(name=newnames.get(t.name, t.name)))
    st.plotly_chart(fig, use_container_width=True)

    # ---- matriz de confusão semanal
    st.subheader("Matriz de confusão de sinais — Z-scores semanais")
    st.caption(
        "Cada célula mostra quantas vezes os sinais do Z-score ZWD e da "
        "Z-score Precipitação coincidem (diagonal) ou divergem (fora da diagonal)."
    )
    conf_sem = matriz_confusao_sinais(df_anom_merged_sem, "zscore_zwd", "zscore_prec")

    total_sem        = int(conf_sem.values.sum())
    concordancia_sem = int(np.trace(conf_sem.values))
    pct_sem          = concordancia_sem / total_sem * 100 if total_sem else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de semanas", total_sem)
    c2.metric("Sinais concordantes", concordancia_sem)
    c3.metric("Taxa de concordância", f"{pct_sem:.1f} %")

    z_vals   = conf_sem.values.tolist()
    x_labels = list(conf_sem.columns)
    y_labels = list(conf_sem.index)
    annot    = [[str(v) for v in row] for row in z_vals]

    fig_conf = ff.create_annotated_heatmap(
        z=z_vals,
        x=x_labels,
        y=y_labels,
        annotation_text=annot,
        colorscale="Blues",
        showscale=True,
    )
    fig_conf.update_layout(
        xaxis_title="Z-score Precipitação",
        yaxis_title="Z-score ZWD",
        xaxis=dict(side="bottom"),
    )
    st.plotly_chart(fig_conf, use_container_width=True)
