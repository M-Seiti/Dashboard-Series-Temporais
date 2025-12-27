# PT-BR version
# Dashboard-Series-Temporais

Dashboard interativo desenvolvido em **Streamlit** para análise de séries temporais de **TRWET** a partir de dados GNSS (`.TROP`).

O sistema realiza processamento temporal, agregações estatísticas e visualizações dinâmicas, permitindo investigar **comportamentos médios, tendências e sazonalidades** ao longo dos anos.

---

## 📌 Objetivo do Projeto

Este projeto tem como objetivo:

- Processar grandes volumes de dados GNSS relacionados ao **TRWET**
- Armazenar os dados em banco **PostgreSQL**
- Calcular estatísticas temporais (médias diárias, mensais, máximos e mínimos anuais)
- Visualizar os resultados em um **dashboard interativo**
- Apoiar análises climatológicas e geodésicas baseadas em séries temporais

---

## 🧠 Funcionalidades

- 📥 Importação de dados GNSS (`.csv`) para PostgreSQL  
- 🕒 Conversão de tempo GNSS  
  *(ano + dia juliano + segundos → timestamp)*
- 📊 Cálculo de:
  - Média diária do TRWET
  - Média mensal
  - Máximos e mínimos por ano
- 📈 Visualização interativa:
  - Séries temporais
  - Tendência (média móvel / regressão)
  - Gráficos por ano ou para todo o período
- 🗂️ Navegação entre páginas:
  - Página inicial
  - Gráficos
  - Tabelas

---

## 🏗️ Estrutura do Projeto

```text
Dashboard-Series-Temporais/
│
├── src/
│   ├── navegacao.py               # Controle de navegação entre páginas
│   ├── pagina_inicial.py          # Página inicial do dashboard
│   ├── graficos.py                # Visualizações gráficas
│   ├── tabelas.py                 # Visualização de tabelas
│   ├── CalcularRM.py              # Funções de processamento e estatísticas
│   └── importar_trwet_postgres.py # Importação de dados para o PostgreSQL
│
├── dados_baixados_Matheus/
│   └── resultado_TROP_todos.csv   # Dados GNSS consolidados
│
├── README.md
└── .env                           # Variáveis de ambiente (não versionado)
```
---
# 🗄️ Banco de Dados

O projeto utiliza **PostgreSQL**, com a tabela principal:

### 📌 `trwet_diario`

**Campos principais:**
- `epoch` *(timestamp)*
- `trwet`
- `arquivo`
- Variáveis GNSS auxiliares *(TROTOT, WVAPOR, etc.)*

A conexão com o banco de dados é realizada via **SQLAlchemy**, utilizando **variáveis de ambiente** para garantir segurança e portabilidade.

---

# 📊 Exemplos de Análises

O dashboard permite realizar diferentes tipos de análises temporais e estatísticas, incluindo:

- 📈 Evolução temporal do **TRWET médio**
- 📆 Comparação entre **anos**
- 📉 Identificação de **tendências de longo prazo**
- 🔁 Avaliação da **sazonalidade anual**
- ⚠️ Análise de **extremos**  
  *(máximo e mínimo anual)*

---

# 🧪 Tecnologias Utilizadas

- **Python 3.12**
- **Streamlit**
- **Pandas**
- **Plotly**
- **PostgreSQL**
- **SQLAlchemy**
- **Statsmodels**

---

# 📚 Contexto Acadêmico

Este projeto é desenvolvido no contexto de **Iniciação Científica**, com aplicações diretas nas áreas de:

- 🌍 Geodésia  
- 🌦️ Climatologia  
- ⏱️ Séries temporais ambientais  
- 📡 Análise de dados **GNSS**

---

# 👤 Autor

**Matheus Seiti**  
Projeto acadêmico – *Iniciação Científica*

---

# 📄 Licença

Projeto destinado exclusivamente a **uso acadêmico e científico**.
## 🚧 Status do Projeto

Este projeto está **atualmente em desenvolvimento** e **ainda não está finalizado**.

Novas funcionalidades, melhorias e refinamentos estão sendo continuamente implementados como parte das atividades em andamento da **Iniciação Científica**.  
Dessa forma, algumas funcionalidades, análises ou componentes visuais podem sofrer alterações em versões futuras.

---

# English version
# Dashboard – Time Series

Interactive dashboard developed in **Streamlit** for the analysis of **TRWET** time series derived from GNSS (`.TROP`) data.

The system performs temporal processing, statistical aggregations, and dynamic visualizations, allowing the investigation of **mean behavior, trends, and seasonal patterns** over the years.

---

## 📌 Project Objective

This project aims to:

- Process large volumes of GNSS data related to **TRWET**
- Store the data in a **PostgreSQL** database
- Compute temporal statistics (daily and monthly means, annual maxima and minima)
- Visualize results through an **interactive dashboard**
- Support climatological and geodetic analyses based on time series

---

## 🧠 Features

- 📥 Import of GNSS data (`.csv`) into PostgreSQL  
- 🕒 GNSS time conversion  
  *(year + Julian day + seconds → timestamp)*
- 📊 Computation of:
  - Daily TRWET mean
  - Monthly mean
  - Annual maximum and minimum values
- 📈 Interactive visualization:
  - Time series plots
  - Trend analysis (moving average / regression)
  - Graphs by year or for the full period
- 🗂️ Page navigation:
  - Home page
  - Charts
  - Tables

---

## 🏗️ Project Structure

```text
Dashboard-Series-Temporais/
│
├── src/
│   ├── navegacao.py               # Page navigation control
│   ├── pagina_inicial.py          # Dashboard home page
│   ├── graficos.py                # Graphical visualizations
│   ├── tabelas.py                 # Table visualizations
│   ├── CalcularRM.py              # Processing and statistical functions
│   └── importar_trwet_postgres.py # Data import into PostgreSQL
│
├── dados_baixados_Matheus/
│   └── resultado_TROP_todos.csv   # Consolidated GNSS data
│
├── README.md
└── .env                           # Environment variables (not versioned)
```
---

## 🗄️ Database

The project uses **PostgreSQL**, with the main table:

### 📌 `trwet_diario`

**Main fields:**
- `epoch` *(timestamp)*
- `trwet`
- `arquivo`
- Auxiliary GNSS variables *(TROTOT, WVAPOR, etc.)*

The database connection is handled via **SQLAlchemy**, using **environment variables** to ensure security and portability.

---

## 📊 Analysis Examples

The dashboard enables several temporal and statistical analyses, including:

- 📈 Temporal evolution of the **mean TRWET**
- 📆 Comparison between **years**
- 📉 Identification of **long-term trends**
- 🔁 Assessment of **annual seasonality**
- ⚠️ **Extreme value analysis**  
  *(annual maximum and minimum)*

---

## 🧪 Technologies Used

- **Python 3.12**
- **Streamlit**
- **Pandas**
- **Plotly**
- **PostgreSQL**
- **SQLAlchemy**
- **Statsmodels**

---

## 📚 Academic Context

This project is developed within the scope of **Undergraduate Research (Iniciação Científica)**, with applications in:

- 🌍 Geodesy  
- 🌦️ Climatology  
- ⏱️ Environmental time series  
- 📡 **GNSS** data analysis

---

## 👤 Author

**Matheus Seiti**  
Academic project – *Undergraduate Research*

---

## 📄 License

Project intended exclusively for **academic and scientific use**.

---

## 🚧 Project Status

This project is **currently under development** and is **not yet finalized**.

New features, improvements, and refinements are continuously being implemented as part of the ongoing **Undergraduate Research (Iniciação Científica)** activities.  
Therefore, some functionalities, analyses, or visual components may change in future versions.

---
