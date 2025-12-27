import pandas as pd
from pathlib import Path

def ler_trop(path):
 
 path = Path(path)
 linhas_dados = []
 dentro_do_bloco = False

 with path.open("r", errors = "replace") as f:
        for linha in f:
            if linha.startswith("+TROP/SOLUTION"):
                dentro_do_bloco = True
                _cabecalho = next(f)
                continue
            if dentro_do_bloco:
                 if linha.startswith("-TROP/SOLUTION"):
                      break
                 partes = linha.split()
                 site = partes[0]
                 epoch = partes[1]
                 numeros = list(map(float,partes[2:]))
                 linhas_dados.append([site, epoch] + numeros)
 colunas = [
        "SITE", "EPOCH",
        "TROTOT", "SIG_TROTOT",
        "TRWET",
        "TGETOT", "SIG_TGETOT",
        "TGNTOT", "SIG_TGNTOT",
        "WVAPOR", "SIG_WVAPOR",
        "MTEMP",
    ]
 return pd.DataFrame(linhas_dados, columns = colunas)


base = Path(r"C:\Users\Player\Desktop\IC\Dashboard-Series-Temporais\dados_baixados_Matheus\MGMC")

dfs = []

for arq in base.rglob("*.trop"):

    if not arq.is_file():
        continue

    print(f"Lendo {arq} ...")
    df_tmp = ler_trop(arq)
    df_tmp["arquivo"] = arq.name
    df_tmp["pasta_ano"] = arq.parent.name
    dfs.append(df_tmp)

df_tudo = pd.concat(dfs, ignore_index=True)
print(df_tudo.head())

saida = base.parent / "resultado_TROP_todos.csv"
df_tudo.to_csv(saida, index=False)
print("Salvo em:", saida)


