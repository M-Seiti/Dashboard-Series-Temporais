import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("POSTGRES_USER")
PWD  = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST", "localhost")
PORT = os.getenv("POSTGRES_PORT", "5432")
DB   = os.getenv("POSTGRES_DB")

engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PWD}@{HOST}:{PORT}/{DB}"
)

# Ajuste o caminho conforme necessário
csv_file = Path(
    r"C:\Users\seiti\OneDrive\Desktop\IC\Dashboard-Series-Temporais\src\precipitacao_diaria_83437.csv"
)


def precipitacao_diaria():
    TABELA = "precipitacao_diaria"

    print(f"Lendo: {csv_file.name}")

    df = pd.read_csv(
        csv_file,
        sep=",",
        decimal=".",
    )

    # Normalização de tipos
    df["data"] = pd.to_datetime(df["data"]).dt.normalize()
    df["precipitacao_mm"] = pd.to_numeric(df["precipitacao_mm"], errors="coerce")
    df["codigo_estacao"] = df["codigo_estacao"].astype(str)
    df["dado_faltante"] = df["dado_faltante"].astype(bool)

    df = df[["data", "precipitacao_mm", "codigo_estacao", "dado_faltante"]]

    # Cria a tabela com PK composta para evitar duplicidade em reimportações
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS precipitacao_diaria (
                data            DATE        NOT NULL,
                precipitacao_mm DOUBLE PRECISION,
                codigo_estacao  TEXT        NOT NULL,
                dado_faltante   BOOLEAN     NOT NULL DEFAULT FALSE,
                PRIMARY KEY (data, codigo_estacao)
            );
        """))

    # Estratégia idempotente: stage temporária + upsert
    df.to_sql("precipitacao_stage", engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO precipitacao_diaria
                (data, precipitacao_mm, codigo_estacao, dado_faltante)
            SELECT data, precipitacao_mm, codigo_estacao, dado_faltante
            FROM precipitacao_stage
            ON CONFLICT (data, codigo_estacao) DO UPDATE
                SET precipitacao_mm = EXCLUDED.precipitacao_mm,
                    dado_faltante   = EXCLUDED.dado_faltante;
        """))
        conn.execute(text("DROP TABLE IF EXISTS precipitacao_stage;"))

    print(f"  → {len(df)} linhas inseridas/atualizadas em {TABELA}.")
    print("✅ Importação concluída.")


if __name__ == "__main__":
    precipitacao_diaria()
