# PT-BR version
# Dashboard-Series-Temporais

Dashboard interativo desenvolvido em **Streamlit** para a análise temporal da relação entre o **Atraso Zenital Úmido (ZWD / TRWET)**, derivado de dados GNSS (`.trop`), e a **precipitação** observada em superfície.

- **Estação GNSS:** MGMC (RBMC) — séries troposféricas do Nevada Geodetic Laboratory (UNR)
- **Estação meteorológica:** OMM 83437 (INMET)
- **Local / período:** Montes Claros/MG, 2011–2024

---

## 📌 Objetivo do Projeto

- Baixar e processar grandes volumes de arquivos GNSS `.trop`
- Armazenar ZWD e precipitação diária em banco **PostgreSQL**
- Calcular estatísticas temporais (médias diárias e mensais, máximos/mínimos anuais, anomalias)
- Decompor a série de ZWD em tendência, sazonalidade e resíduo
- Investigar a correlação entre ZWD e precipitação em diferentes escalas
- Apoiar análises climatológicas e geodésicas baseadas em séries temporais

---

## 🧠 Páginas do Dashboard

| Página | Conteúdo |
|---|---|
| **Página Inicial** | Contexto do estudo, indicadores (período, estações, local) e atalhos para as análises. |
| **01 · Séries Temporais** | Séries diárias e mensais de ZWD **ou** precipitação, para um ano específico ou todo o período; anomalias normalizadas (Z-score) mensais e semanais. |
| **02 · Decomposição** | Decomposição da série diária de ZWD com **Prophet**: tendência, sazonalidade anual e resíduo. |
| **03 · Correlações** | Dispersão diária e mensal ZWD × precipitação, ajuste de curvas (linear, logarítmica, raiz quadrada, Michaelis-Menten) com R²/RMSE/MAE, séries sobrepostas, correlação cruzada com defasagem (±15 dias) e correlação/matriz de confusão de sinais das anomalias mensais e semanais. |
| **04 · Tabelas** | Máximos e mínimos anuais, médias diárias de ZWD, precipitação diária e soma mensal. |

---

## 🏗️ Estrutura do Projeto

```text
Dashboard-Series-Temporais/
│
├── .streamlit/config.toml                       # Tema (claro) ao rodar a partir da raiz
├── src/
│   ├── .streamlit/config.toml                   # Tema (escuro) ao rodar a partir de src/
│   │
│   │   # ── Pipeline de dados ──────────────────────────────
│   ├── 1_Baixar_DadosWGET_RM.py                 # Download dos .zip de séries troposféricas (UNR) via wget
│   ├── 2_Descompactar_Arquivos_RM.py            # Descompacta .zip / .gz em arquivos .trop
│   ├── 3_1_Calcular_Dados_RM_Manipulacao_arquivo.py  # Lê o bloco TROP/SOLUTION e gera resultado_TROP_todos.csv
│   ├── importar_trwet_postgres.py               # Converte o EPOCH e importa para a tabela trwet_diario
│   ├── importar_precipitacao_postgres.py        # Importa a precipitação (upsert) para precipitacao_diaria
│   ├── precipitacao_diaria_83437.csv            # Precipitação diária da estação INMET 83437
│   │
│   │   # ── Lógica de cálculo ──────────────────────────────
│   ├── CalcularRM.py                            # Consulta do ZWD, médias, anomalias, decomposição (Prophet)
│   ├── CalcularPrecipitacao.py                  # Consulta da precipitação, somas mensais, extremos, anomalias
│   ├── CalcularCorrelacoes.py                   # Merge ZWD × precipitação, correlações, defasagem, ajuste de curvas
│   │
│   │   # ── Interface ─────────────────────────────────────
│   ├── navegacao.py                             # Ponto de entrada: configuração e navegação entre páginas
│   ├── estilo.py                                # Identidade visual (CSS) e template dos gráficos Plotly
│   ├── paginaInicial.py
│   ├── 01_series_temporais.py
│   ├── 02_decomposicao.py
│   ├── 03_correlacoes.py
│   └── 04_tabelas.py
│
├── dados_baixados_Matheus/                      # Dados GNSS brutos (não versionar)
├── README.md
└── .env                                         # Credenciais do banco (não versionado)
```

---

## ⚙️ Como Executar

### 1. Dependências

Python 3.12 e um servidor PostgreSQL acessível.

```bash
pip install streamlit pandas numpy scipy plotly prophet sqlalchemy psycopg2-binary python-dotenv
```

### 2. Variáveis de ambiente

Crie um arquivo `.env` na pasta de onde os scripts serão executados:

```env
POSTGRES_USER=usuario
POSTGRES_PASSWORD=senha
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nome_do_banco
```

> ⚠️ O `.env` está no `.gitignore` e **nunca** deve ser versionado.

### 3. Preparação dos dados (executar uma vez)

Os scripts de pipeline contêm caminhos absolutos no topo do arquivo (`local_wget`, `base`, `csv_file`) — ajuste-os para a sua máquina antes de rodar.

```bash
python src/1_Baixar_DadosWGET_RM.py                    # baixa os .zip da estação MGMC
python src/2_Descompactar_Arquivos_RM.py               # extrai os arquivos .trop
python src/3_1_Calcular_Dados_RM_Manipulacao_arquivo.py  # consolida em resultado_TROP_todos.csv
python src/importar_trwet_postgres.py                  # popula trwet_diario
python src/importar_precipitacao_postgres.py           # popula precipitacao_diaria
```

### 4. Dashboard

```bash
cd src
streamlit run navegacao.py
```

---

## 🗄️ Banco de Dados

### 📌 `trwet_diario`

- `epoch` *(timestamp — convertido de `AA:DDD:SSSSS`, ano + dia juliano + segundos)*
- `TRWET` (ZWD), `TROTOT`, `WVAPOR`, `MTEMP`, gradientes `TGETOT`/`TGNTOT` e respectivos desvios
- `arquivo`, `pasta_ano` *(origem do registro)*

### 📌 `precipitacao_diaria`

- `data` *(DATE)*, `codigo_estacao` *(TEXT)* — chave primária composta
- `precipitacao_mm`, `dado_faltante`

A importação usa uma tabela temporária + `ON CONFLICT DO UPDATE`, então pode ser reexecutada sem duplicar registros. A conexão é feita via **SQLAlchemy** (`postgresql+psycopg2`) com as credenciais do `.env`; as consultas do dashboard usam `st.cache_data`.

---

## 🧪 Tecnologias Utilizadas

- **Python 3.12**
- **Streamlit**
- **Pandas** / **NumPy** / **SciPy**
- **Plotly**
- **Prophet**
- **PostgreSQL** + **SQLAlchemy**

---

## 📚 Contexto Acadêmico

Este projeto é desenvolvido no contexto de **Iniciação Científica**, com aplicações diretas nas áreas de:

- 🌍 Geodésia
- 🌦️ Climatologia
- ⏱️ Séries temporais ambientais
- 📡 Análise de dados **GNSS**

---

## 👤 Autores

**Matheus Seiti, Rafael Luiz**
Projeto acadêmico – *Iniciação Científica*

---

## 📄 Licença

Projeto destinado exclusivamente a **uso acadêmico e científico**.

---

# English version
# Dashboard – Time Series

Interactive **Streamlit** dashboard for analyzing the relationship between the GNSS-derived **Zenith Wet Delay (ZWD / TRWET)** and surface **precipitation** — GNSS station MGMC (RBMC) and INMET weather station WMO 83437, Montes Claros/MG, Brazil, 2011–2024.

## Pages

| Page | Content |
|---|---|
| **Home** | Study context, key indicators and shortcuts. |
| **01 · Time Series** | Daily and monthly ZWD or precipitation series, per year or full period; monthly and weekly normalized anomalies (Z-score). |
| **02 · Decomposition** | Prophet decomposition of daily ZWD into trend, yearly seasonality and residual. |
| **03 · Correlations** | Daily/monthly scatter plots, curve fitting (linear, log, square root, Michaelis-Menten) with R²/RMSE/MAE, lagged cross-correlation (±15 days), and anomaly correlation with sign confusion matrices. |
| **04 · Tables** | Annual extremes, daily ZWD means, daily and monthly precipitation. |

## Quick start

```bash
pip install streamlit pandas numpy scipy plotly prophet sqlalchemy psycopg2-binary python-dotenv
# create .env with POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
# run the data pipeline (src/1_*, 2_*, 3_1_*, importar_*.py) once — adjust the absolute paths first
cd src
streamlit run navegacao.py
```

Data is stored in PostgreSQL tables `trwet_diario` (GNSS troposphere solutions) and `precipitacao_diaria` (daily rainfall, upserted on `data` + `codigo_estacao`).

## Authors

**Matheus Seiti, Rafael Luiz** — Undergraduate Research (*Iniciação Científica*). For academic and scientific use only. Work in progress.
