import pandas as pd
import numpy as np
import streamlit as st
from scipy import stats
from scipy.optimize import curve_fit


@st.cache_data(show_spinner=False)
def merge_zwd_precipitacao(
    df_zwd: pd.DataFrame,
    df_precip: pd.DataFrame,
) -> pd.DataFrame:
    """Faz merge diário entre ZWD (df_merged) e Precipitação por coluna 'data'."""
    if df_zwd.empty or df_precip.empty:
        return pd.DataFrame()

    df_z = df_zwd[["data", "zwd_medio"]].copy()
    df_p = df_precip[["data", "precipitacao_mm"]].copy()

    df_z["data"] = pd.to_datetime(df_z["data"]).dt.normalize()
    df_p["data"] = pd.to_datetime(df_p["data"]).dt.normalize()

    df = pd.merge(df_z, df_p, on="data", how="inner").sort_values("data")
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    return df


def correlacao_diaria(df_join: pd.DataFrame, metodo: str = "pearson") -> float:
    """Correlação diária ZWD × Precipitação."""
    if df_join.empty:
        return float("nan")
    return df_join["zwd_medio"].corr(df_join["precipitacao_mm"], method=metodo)


def agregar_mensal(df_join: pd.DataFrame) -> pd.DataFrame:
    """Agrega para escala mensal: ZWD média mensal e Precipitação somada."""
    if df_join.empty:
        return df_join

    df_mensal = (
        df_join.groupby(["ano", "mes"], as_index=False)
        .agg(
            zwd_medio_mensal=("zwd_medio", "mean"),
            precipitacao_mensal=("precipitacao_mm", "sum"),
        )
    )
    df_mensal["data_mes"] = pd.to_datetime(
        {"year": df_mensal["ano"], "month": df_mensal["mes"], "day": 1}
    )
    return df_mensal


def correlacao_mensal(df_mensal: pd.DataFrame, metodo: str = "pearson") -> float:
    if df_mensal.empty:
        return float("nan")
    return df_mensal["zwd_medio_mensal"].corr(
        df_mensal["precipitacao_mensal"], method=metodo
    )


def correlacao_com_defasagem(
    df_join: pd.DataFrame,
    lags: range = range(-15, 16),
    metodo: str = "pearson",
) -> pd.DataFrame:
    """
    Correlação cruzada ZWD × Precipitação com defasagem em dias.
    Lag positivo = precipitação atrasada em relação ao ZWD (ZWD 'antecipa' chuva).
    Lag negativo = precipitação adiantada (chuva precede o ZWD).
    """
    if df_join.empty:
        return pd.DataFrame(columns=["lag_dias", "correlacao"])

    s_zwd  = df_join.set_index("data")["zwd_medio"]
    s_prec = df_join.set_index("data")["precipitacao_mm"]

    resultados = []
    for lag in lags:
        s_prec_shift = s_prec.shift(lag)
        corr = s_zwd.corr(s_prec_shift, method=metodo)
        resultados.append({"lag_dias": lag, "correlacao": corr})

    return pd.DataFrame(resultados)


def correlacao_anomalias_mensal(
    df_anom_zwd: pd.DataFrame,
    df_anom_prec: pd.DataFrame,
    metodo: str = "pearson",
) -> tuple:
    """
    Correlação entre anomalias mensais de ZWD e precipitação.
    Retorna (valor_correlação, df_merged_anomalias).
    """
    if df_anom_zwd.empty or df_anom_prec.empty:
        return float("nan"), pd.DataFrame()

    df_z = df_anom_zwd[["ano", "mes", "anomalia_zwd"]].copy()
    df_p = df_anom_prec[["ano", "mes", "anomalia_prec"]].copy()

    df = df_z.merge(df_p, on=["ano", "mes"]).dropna()

    if df.empty:
        return float("nan"), df

    corr = df["anomalia_zwd"].corr(df["anomalia_prec"], method=metodo)
    df["data_mes"] = pd.to_datetime(
        {"year": df["ano"], "month": df["mes"], "day": 1}
    )
    return corr, df


def correlacao_anomalias_semanal(
    df_anom_zwd: pd.DataFrame,
    df_anom_prec: pd.DataFrame,
    metodo: str = "pearson",
) -> tuple:
    """
    Correlação entre anomalias semanais de ZWD e precipitação.
    Retorna (valor_correlação, df_merged_anomalias).
    """
    if df_anom_zwd.empty or df_anom_prec.empty:
        return float("nan"), pd.DataFrame()

    df_z = df_anom_zwd[["ano", "semana", "anomalia_zwd", "zscore_zwd"]].copy()
    df_p = df_anom_prec[["ano", "semana", "anomalia_prec", "zscore_prec"]].copy()

    df = df_z.merge(df_p, on=["ano", "semana"]).dropna()

    if df.empty:
        return float("nan"), df

    corr = df["anomalia_zwd"].corr(df["anomalia_prec"], method=metodo)
    df["data_semana"] = pd.to_datetime(
        df["ano"].astype(str) + df["semana"].astype(str).str.zfill(2) + "1",
        format="%G%V%u",
    )
    return corr, df.sort_values("data_semana").reset_index(drop=True)


def matriz_confusao_sinais(
    df: pd.DataFrame,
    col_z1: str = "zscore_zwd",
    col_z2: str = "zscore_prec",
) -> pd.DataFrame:
    """
    Matriz de confusão dos sinais dos z-scores de ZWD e precipitação.
    Linhas = sinal do ZWD, Colunas = sinal da precipitação.
    """
    df = df.dropna(subset=[col_z1, col_z2]).copy()
    df["sinal_zwd"]  = df[col_z1].apply(lambda x: "ZWD +" if x >= 0 else "ZWD −")
    df["sinal_prec"] = df[col_z2].apply(lambda x: "Prec +" if x >= 0 else "Prec −")

    return pd.crosstab(
        df["sinal_zwd"],
        df["sinal_prec"],
        rownames=["Z-score ZWD"],
        colnames=["Z-score Precipitação"],
    )


def ajustar_curvas(x, y) -> tuple:
    """
    Ajusta 4 modelos ao par (x=precipitação, y=ZWD):
      Linear          : ZWD = a + b·P
      Logarítmica     : ZWD = a + b·ln(P+1)
      Raiz quadrada   : ZWD = a + b·√P
      Michaelis-Menten: ZWD = y_min + dy·P/(K+P)

    Retorna
    -------
    tabela : pd.DataFrame  — Modelo, Equação, R², RMSE, MAE
    curvas : list[tuple]   — (nome, callable(xv) -> y_pred)
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]

    if len(x) < 4:
        return pd.DataFrame(), []

    ss_tot = np.sum((y - y.mean()) ** 2)

    def _metrics(y_pred):
        r2   = float(1.0 - np.sum((y - y_pred) ** 2) / ss_tot) if ss_tot > 0 else float("nan")
        rmse = float(np.sqrt(np.mean((y - y_pred) ** 2)))
        mae  = float(np.mean(np.abs(y - y_pred)))
        return r2, rmse, mae

    rows, curvas = [], []

    # Linear
    slope, intercept, *_ = stats.linregress(x, y)
    r2, rmse, mae = _metrics(intercept + slope * x)
    rows.append({"Modelo": "Linear",
                 "Equação": f"ZWD = {intercept:.2f} + {slope:.4f}·P",
                 "R²": r2, "RMSE": rmse, "MAE": mae})
    curvas.append(("Linear", lambda xv, _a=intercept, _b=slope: _a + _b * xv))

    # Logarítmica
    slope_l, intercept_l, *_ = stats.linregress(np.log(x + 1), y)
    r2, rmse, mae = _metrics(intercept_l + slope_l * np.log(x + 1))
    rows.append({"Modelo": "Logarítmica",
                 "Equação": f"ZWD = {intercept_l:.2f} + {slope_l:.3f}·ln(P+1)",
                 "R²": r2, "RMSE": rmse, "MAE": mae})
    curvas.append(("Logarítmica", lambda xv, _a=intercept_l, _b=slope_l: _a + _b * np.log(xv + 1)))

    # Raiz quadrada
    slope_s, intercept_s, *_ = stats.linregress(np.sqrt(x), y)
    r2, rmse, mae = _metrics(intercept_s + slope_s * np.sqrt(x))
    rows.append({"Modelo": "Raiz quadrada",
                 "Equação": f"ZWD = {intercept_s:.2f} + {slope_s:.3f}·√P",
                 "R²": r2, "RMSE": rmse, "MAE": mae})
    curvas.append(("Raiz quadrada", lambda xv, _a=intercept_s, _b=slope_s: _a + _b * np.sqrt(xv)))

    # Michaelis-Menten: ZWD = y_min + dy·P / (K + P)
    def _mm(P, y_min, dy, K):
        return y_min + dy * P / (K + P)

    try:
        K0 = float(np.median(x[x > 0])) if np.any(x > 0) else 50.0
        p0 = [float(y.min()), float(y.max() - y.min()), K0]
        bounds = ([0.0, 0.0, 1e-3], [1e4, 1e4, 1e6])
        popt, _ = curve_fit(_mm, x, y, p0=p0, bounds=bounds, maxfev=20_000)
        r2, rmse, mae = _metrics(_mm(x, *popt))
        rows.append({"Modelo": "Michaelis-Menten",
                     "Equação": f"ZWD = {popt[0]:.2f} + {popt[1]:.2f}·P/(P + {popt[2]:.1f})",
                     "R²": r2, "RMSE": rmse, "MAE": mae})
        curvas.append(("Michaelis-Menten", lambda xv, _p=popt: _mm(xv, *_p)))
    except Exception:
        pass

    return pd.DataFrame(rows), curvas
