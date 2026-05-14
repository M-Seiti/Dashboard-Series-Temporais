import streamlit as st
import plotly.express as px
import pandas as pd
import calendar

from CalcularRM import (
    preparar_dados_dashboard,
    carregar_anos_disponiveis,
    calc_media_mensal,
    calc_anomalia_zwd,
    calc_anomalia_zwd_semanal,
)
from CalcularPrecipitacao import (
    carregar_precipitacao,
    carregar_anos_precipitacao_disponiveis,
    calc_precip_mensal,
    calc_anomalia_precipitacao,
    calc_anomalia_precipitacao_semanal,
)

st.title("📈 Séries Temporais")

# -------------------------------------------------------------------- sidebar
st.sidebar.title("⚙️ Controles")

variavel = st.sidebar.radio(
    "**Variável**",
    ["ZWD", "Precipitação"],
    help="Escolha a variável que deseja visualizar.",
)

modo = st.sidebar.selectbox(
    "**📌 Modo de visualização**",
    ["Todos os anos", "Lista de anos"],
    index=None,
    placeholder="Selecione uma opção",
    help=(
        "👉 'Todos os anos' mostra a série inteira.\n\n"
        "👉 'Lista de anos' permite escolher um ano específico."
    ),
)

if modo is None:
    st.info("Selecione um modo de visualização na barra lateral.")
    st.stop()

# ------------------------------------------------------------------- ZWD
if variavel == "ZWD":
    anos_disp = carregar_anos_disponiveis()

    if modo == "Todos os anos":
        df_merged = preparar_dados_dashboard(ano=None)
        df_mensal = calc_media_mensal(df_merged)

        st.write("Dias disponíveis:", len(df_merged))

        st.subheader("Média diária do ZWD — todos os anos")
        fig = px.scatter(df_merged, x="data", y="zwd_medio", trendline="ols")
        fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=4))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Soma mensal das médias diárias do ZWD")
        df_mensal["data_mes"] = pd.to_datetime(
            {"year": df_mensal["ano"], "month": df_mensal["mes"], "day": 1}
        )
        st.plotly_chart(
            px.bar(df_mensal, x="data_mes", y="ZWD_media_mensal"),
            use_container_width=True,
        )

        st.subheader("Anomalia normalizada (Z-score) do ZWD mensal")
        st.caption(
            "Z-score = (ZWD médio mensal − climatologia do mês) ÷ desvio padrão do mês. "
            "Valores > 0 indicam meses acima da média histórica."
        )
        df_anom = calc_anomalia_zwd(df_merged)
        fig_anom = px.bar(
            df_anom,
            x="data_mes",
            y="zscore_zwd",
            color="zscore_zwd",
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=0,
            labels={"zscore_zwd": "Z-score ZWD", "data_mes": "Mês"},
        )
        fig_anom.update_coloraxes(showscale=False)
        fig_anom.update_layout(yaxis_title="Z-score")
        st.plotly_chart(fig_anom, use_container_width=True)

        st.subheader("Anomalia normalizada (Z-score) do ZWD semanal")
        st.caption(
            "Z-score = (ZWD médio semanal − climatologia da semana ISO) ÷ desvio padrão da semana. "
            "Valores > 0 indicam semanas acima da média histórica."
        )
        df_anom_sem = calc_anomalia_zwd_semanal(df_merged)
        fig_anom_sem = px.bar(
            df_anom_sem,
            x="data_semana",
            y="zscore_zwd",
            color="zscore_zwd",
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=0,
            labels={"zscore_zwd": "Z-score ZWD", "data_semana": "Semana"},
        )
        fig_anom_sem.update_coloraxes(showscale=False)
        fig_anom_sem.update_layout(yaxis_title="Z-score")
        st.plotly_chart(fig_anom_sem, use_container_width=True)

    else:  # Lista de anos
        ano = st.sidebar.selectbox("Selecione o ano:", anos_disp)
        df_merged = preparar_dados_dashboard(ano)
        df_mensal = calc_media_mensal(df_merged)

        qtd = df_merged["dia_juliano"].nunique()
        total = 366 if calendar.isleap(ano) else 365
        faltantes = max(total - qtd, 0)

        c1, c2, c3 = st.columns(3)
        c1.metric("Dias disponíveis", qtd)
        c2.metric("Dias ausentes", faltantes)
        c3.metric("Total esperado", total)

        st.subheader(f"Média diária do ZWD — {ano}")
        fig = px.line(df_merged, x="data", y="zwd_medio")
        fig.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(size=4))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"Soma mensal da média diária do ZWD — {ano}")
        df_mensal["data_mes"] = pd.to_datetime(
            {"year": df_mensal["ano"], "month": df_mensal["mes"], "day": 1}
        )
        st.plotly_chart(
            px.bar(df_mensal, x="data_mes", y="ZWD_media_mensal"),
            use_container_width=True,
        )

        st.subheader(f"Anomalia normalizada (Z-score) do ZWD mensal — {ano}")
        st.caption(
            "Z-score = (ZWD médio mensal − climatologia do mês) ÷ desvio padrão do mês. "
            "A climatologia é calculada sobre toda a série histórica."
        )
        df_anom_all = calc_anomalia_zwd(preparar_dados_dashboard(ano=None))
        df_anom = df_anom_all[df_anom_all["ano"] == ano].copy()
        fig_anom = px.bar(
            df_anom,
            x="data_mes",
            y="zscore_zwd",
            color="zscore_zwd",
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=0,
            labels={"zscore_zwd": "Z-score ZWD", "data_mes": "Mês"},
        )
        fig_anom.update_coloraxes(showscale=False)
        fig_anom.update_layout(yaxis_title="Z-score")
        st.plotly_chart(fig_anom, use_container_width=True)

        st.subheader(f"Anomalia normalizada (Z-score) do ZWD semanal — {ano}")
        st.caption(
            "Z-score = (ZWD médio semanal − climatologia da semana ISO) ÷ desvio padrão da semana. "
            "A climatologia é calculada sobre toda a série histórica."
        )
        df_anom_sem_all = calc_anomalia_zwd_semanal(preparar_dados_dashboard(ano=None))
        df_anom_sem = df_anom_sem_all[df_anom_sem_all["ano"] == ano].copy()
        fig_anom_sem = px.bar(
            df_anom_sem,
            x="data_semana",
            y="zscore_zwd",
            color="zscore_zwd",
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=0,
            labels={"zscore_zwd": "Z-score ZWD", "data_semana": "Semana"},
        )
        fig_anom_sem.update_coloraxes(showscale=False)
        fig_anom_sem.update_layout(yaxis_title="Z-score")
        st.plotly_chart(fig_anom_sem, use_container_width=True)

# ---------------------------------------------------------------- Precipitação
else:
    anos_disp = carregar_anos_precipitacao_disponiveis()

    if modo == "Todos os anos":
        df = carregar_precipitacao(ano=None)

        st.write("Dias disponíveis:", len(df))

        st.subheader("Precipitação diária — todos os anos")
        st.plotly_chart(
            px.bar(df, x="data", y="precipitacao_mm"),
            use_container_width=True,
        )

        st.subheader("Soma mensal de precipitação")
        df_mensal = calc_precip_mensal(df)
        st.plotly_chart(
            px.bar(df_mensal, x="data_mes", y="precipitacao_mensal"),
            use_container_width=True,
        )

        st.subheader("Anomalia normalizada (Z-score) de precipitação mensal")
        st.caption(
            "Z-score = (soma mensal − climatologia do mês) ÷ desvio padrão do mês. "
            "Valores > 0 indicam meses acima da média histórica."
        )
        df_anom = calc_anomalia_precipitacao(df)
        fig_anom = px.bar(
            df_anom,
            x="data_mes",
            y="zscore_prec",
            color="zscore_prec",
            color_continuous_scale="BrBG",
            color_continuous_midpoint=0,
            labels={"zscore_prec": "Z-score Precipitação", "data_mes": "Mês"},
        )
        fig_anom.update_coloraxes(showscale=False)
        fig_anom.update_layout(yaxis_title="Z-score")
        st.plotly_chart(fig_anom, use_container_width=True)

        st.subheader("Anomalia normalizada (Z-score) de precipitação semanal")
        st.caption(
            "Z-score = (soma semanal − climatologia da semana ISO) ÷ desvio padrão da semana. "
            "Valores > 0 indicam semanas acima da média histórica."
        )
        df_anom_sem = calc_anomalia_precipitacao_semanal(df)
        fig_anom_sem = px.bar(
            df_anom_sem,
            x="data_semana",
            y="zscore_prec",
            color="zscore_prec",
            color_continuous_scale="BrBG",
            color_continuous_midpoint=0,
            labels={"zscore_prec": "Z-score Precipitação", "data_semana": "Semana"},
        )
        fig_anom_sem.update_coloraxes(showscale=False)
        fig_anom_sem.update_layout(yaxis_title="Z-score")
        st.plotly_chart(fig_anom_sem, use_container_width=True)

    else:
        ano = st.sidebar.selectbox("Selecione o ano:", anos_disp)
        df = carregar_precipitacao(ano)

        qtd = len(df)
        total = 366 if calendar.isleap(ano) else 365
        faltantes = max(total - qtd, 0)

        c1, c2, c3 = st.columns(3)
        c1.metric("Dias disponíveis", qtd)
        c2.metric("Dias ausentes", faltantes)
        c3.metric("Total esperado", total)

        st.subheader(f"Precipitação diária — {ano}")
        st.plotly_chart(
            px.bar(df, x="data", y="precipitacao_mm"),
            use_container_width=True,
        )

        st.subheader(f"Soma mensal de precipitação — {ano}")
        df_mensal = calc_precip_mensal(df)
        st.plotly_chart(
            px.bar(df_mensal, x="data_mes", y="precipitacao_mensal"),
            use_container_width=True,
        )

        st.subheader(f"Anomalia normalizada (Z-score) de precipitação mensal — {ano}")
        st.caption(
            "Z-score = (soma mensal − climatologia do mês) ÷ desvio padrão do mês. "
            "A climatologia é calculada sobre toda a série histórica."
        )
        df_anom_all = calc_anomalia_precipitacao(carregar_precipitacao(ano=None))
        df_anom = df_anom_all[df_anom_all["ano"] == ano].copy()
        fig_anom = px.bar(
            df_anom,
            x="data_mes",
            y="zscore_prec",
            color="zscore_prec",
            color_continuous_scale="BrBG",
            color_continuous_midpoint=0,
            labels={"zscore_prec": "Z-score Precipitação", "data_mes": "Mês"},
        )
        fig_anom.update_coloraxes(showscale=False)
        fig_anom.update_layout(yaxis_title="Z-score")
        st.plotly_chart(fig_anom, use_container_width=True)

        st.subheader(f"Anomalia normalizada (Z-score) de precipitação semanal — {ano}")
        st.caption(
            "Z-score = (soma semanal − climatologia da semana ISO) ÷ desvio padrão da semana. "
            "A climatologia é calculada sobre toda a série histórica."
        )
        df_anom_sem_all = calc_anomalia_precipitacao_semanal(carregar_precipitacao(ano=None))
        df_anom_sem = df_anom_sem_all[df_anom_sem_all["ano"] == ano].copy()
        fig_anom_sem = px.bar(
            df_anom_sem,
            x="data_semana",
            y="zscore_prec",
            color="zscore_prec",
            color_continuous_scale="BrBG",
            color_continuous_midpoint=0,
            labels={"zscore_prec": "Z-score Precipitação", "data_semana": "Semana"},
        )
        fig_anom_sem.update_coloraxes(showscale=False)
        fig_anom_sem.update_layout(yaxis_title="Z-score")
        st.plotly_chart(fig_anom_sem, use_container_width=True)
