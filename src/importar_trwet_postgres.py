import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


load_dotenv()

USER = os.getenv("POSTGRES_USER")
PWD  = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")
DB   = os.getenv("POSTGRES_DB")

csv_file = Path(r"C:\Users\Player\Desktop\IC\Dashboard-Series-Temporais\dados_baixados_Matheus\resultado_TROP_todos.csv")

engine = create_engine(
    f"postgresql+psycopg2://{USER}:{PWD}@{HOST}:{PORT}/{DB}"
)
def trwe_diario():
    TABELA = "trwet_diario"


    print(f"Lendo: {csv_file.name}")

    df = pd.read_csv(
    csv_file,
        sep=",",          
        decimal=".",      
    )


    df = df[[
        "SITE",
        "EPOCH",
        "TROTOT",
        "SIG_TROTOT",
        "TRWET",
        "TGETOT",
        "SIG_TGETOT",
        "TGNTOT",
        "SIG_TGNTOT",
        "WVAPOR",
        "SIG_WVAPOR",
        "MTEMP",
        "arquivo",
        "pasta_ano",
    ]]


    partes = df["EPOCH"].str.split(":", expand=True)

    df["ano"] = 2000 + partes[0].astype(int)
    df["dia_jul"] = partes[1].astype(int)
    df["segundos"] = partes[2].astype(int)

    df["epoch"] = (
    pd.to_datetime(df["ano"].astype(str), format="%Y") +
    pd.to_timedelta(df["dia_jul"] - 1, unit="D") +
    pd.to_timedelta(df["segundos"], unit="s")
    )

    df.drop(columns=["ano", "dia_jul", "segundos"], inplace=True)


    df = df.rename(columns={
        "SITE": "site",
        "TROTOT": "trotot",
        "SIG_TROTOT": "sig_trotot",
        "TRWET": "trwet",
        "TGETOT": "tgetot",
        "SIG_TGETOT": "sig_tgetot",
        "TGNTOT": "tgntot",
        "SIG_TGNTOT": "sig_tgntot",
        "WVAPOR": "wvapor",
        "SIG_WVAPOR": "sig_wvapor",
        "MTEMP": "mtemp",
        "arquivo": "arquivo",
        "pasta_ano": "pasta_ano",
    })


    df.to_sql(TABELA, engine, if_exists="append", index=False)
    print(f"  → {len(df)} linhas inseridas.")

    print("✅ Importação concluída.") 

if __name__ == "__main__":
    trwe_diario()
