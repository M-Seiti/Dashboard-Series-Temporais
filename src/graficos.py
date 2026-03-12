import streamlit as st
import plotly.express as px
import pandas as pd
import calendar

from CalcularRM import (
    preparar_dados_dashboard,
    carregar_anos_disponiveis,
    carregar_meses_disponiveis,
    calc_media_mensal,
    decomposicao,
    calcular_dias_mes,
    media_desvio
)


st.sidebar.title("⚙️ Controles")
anos_disponiveis = carregar_anos_disponiveis()
meses_disponiveis = carregar_meses_disponiveis()

opcao = st.sidebar.selectbox(
    "**📌 Modo de visualização**",
    ["Todos os anos", "Lista de anos"],
    index = None,
    placeholder="Selecione uma opção para visualizaçãos",
    help="👉 Selecione 'Todos os anos' para ver todos os anos.\n\n👉 Selecione 'Lista de anos' para ver a lista de anos disponíveis",
)
st.sidebar.write("Selecionado:", opcao)

if opcao == "Todos os anos":
    meses = st.sidebar.selectbox("Selecione o mes:", meses_disponiveis)
    df_merged = preparar_dados_dashboard(ano=None)
    df_decomp = decomposicao(df_merged)
    df_mensal = calc_media_mensal(df_merged)
    qtd_dias_arquivo = len(df_merged)

    st.write("Dias disponíveis:", qtd_dias_arquivo)

    st.subheader("Média diária do TRWET de todos os anos")

    fig_todos = px.scatter(
        df_decomp,
        x="data",
        y="trwet_medio",
        trendline="ols",
    )

    fig_todos.update_traces(
        selector=dict(mode="markers"),
        marker=dict(size=4, color="rgba(0, 123, 255, 0.6)")
    )

    fig_todos.update_traces(
        selector=dict(name="trendline"),
        line=dict(color="red", width=3)
    )

    st.plotly_chart(fig_todos, use_container_width=True)
    
    st.subheader(f"Tendência do TRWET - Média móvel")
    fig_decomp = px.line(df_decomp, x="data", y="tendencia")
    fig_decomp.update_traces(
    mode="lines+markers",
    line=dict(width=2),
    marker=dict(size=4),
    )
    st.plotly_chart(fig_decomp, use_container_width=True)

    st.subheader(f"Sazonalidade do TRWET")
    fig_decomp = px.line(df_decomp, x="data", y="sazonalidade")
    fig_decomp.update_traces(
    mode="lines+markers",
    line=dict(width=2),
    marker=dict(size=4),
    )
    st.plotly_chart(fig_decomp, use_container_width=True)

    st.subheader(f"Resíduo do TRWET")
    fig_decomp = px.line(df_decomp, x="data", y="residuo")
    fig_decomp.update_traces(
    mode="lines",
    line=dict(width=2)  
    )
    st.plotly_chart(fig_decomp, use_container_width=True)

    st.subheader(f"Soma Mensal das Médias Diárias")
    df_mensal["data_mes"] = pd.to_datetime(
    {"year": df_mensal["ano"], "month": df_mensal["mes"], "day": 1}
    )
    fig_mes_todos = px.bar(df_mensal, x="data_mes", y="TRWET_media_mensal")
    st.plotly_chart(fig_mes_todos, use_container_width=True)
     
    df_mensal = df_mensal[df_mensal["mes"] == meses]
    st.subheader(f"Soma das medias mensais de todos os anos")
    fig_mes_todos_soma = px.bar(df_mensal, x="data_mes", y="TRWET_media_mensal")
    st.plotly_chart(fig_mes_todos_soma, use_container_width=True)
    
elif opcao == "Lista de anos":
        ano = st.sidebar.selectbox("Selecione o ano:", anos_disponiveis)
        df_merged = preparar_dados_dashboard(ano)
        df_mensal = calc_media_mensal(df_merged)
        df_dias_mes = calcular_dias_mes(df_merged)
        df_decomp = decomposicao(df_merged)
        df_media_desvio = media_desvio(df_decomp)
        qtd_dias_arquivo = df_merged["dia_juliano"].nunique()
        total_esperado = 366 if calendar.isleap(ano) else 365

        dias_faltantes = total_esperado - qtd_dias_arquivo
        if dias_faltantes < 0:
            dias_faltantes = 0

        col5, col6, col7 = st.columns(3)
        with col5:
            st.write("Dias disponíveis:", qtd_dias_arquivo)
        with col6:
            st.write("Dias ausentes:", dias_faltantes)
        with col7:
            st.write("Total esperado:", total_esperado)

        st.subheader("Total de dias disponiveis no mes")
        st.dataframe(df_dias_mes)

        st.subheader(f"Média diária do TRWET - {ano}")
        fig_dia = px.line(df_merged, x="data", y="trwet_medio")
        fig_dia.update_traces(
        mode="lines+markers",
        line=dict(width=2),
        marker=dict(size=4),
        )
        st.plotly_chart(fig_dia, use_container_width=True)

    
        st.subheader(f"Soma Mensal da Média Diária - {ano}")
        df_mensal["data_mes"] = pd.to_datetime(
        {"year": df_mensal["ano"], "month": df_mensal["mes"], "day": 1}
        )
        fig_mes = px.bar(df_mensal, x="data_mes", y="TRWET_media_mensal")
        st.plotly_chart(fig_mes, use_container_width=True)

        st.subheader(f"Media e desvio padrão mensal do resíduo ao longo dos anos")
        fig_media_desvio = px.bar(df_media_desvio, x="mes", y="media_residuo", error_y="desvio_padrao_residuo")
        st.plotly_chart(fig_media_desvio, use_container_width=True)

else:  
     st.title("Pagina inicial")
     