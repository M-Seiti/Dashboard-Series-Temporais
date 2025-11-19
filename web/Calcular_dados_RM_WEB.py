from fastapi import FastAPI
import pandas as pd

app = FastAPI()

df = pd.read_csv(r"C:\Users\seiti\OneDrive\Desktop\IC\dados_baixados_Matheus\resultado_TROP_todos.csv")

@app.get("/media-por-ano")
def media_por_ano():
    df_media = (
        df.groupby("pasta_ano")["TRWET"]
          .mean()
          .reset_index(name="TRWET_medio")
    )
    return df_media.to_dict(orient="records")
