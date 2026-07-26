# ============================================================
# De la señal a la cartera (DISEÑO.md §7).
#
# Solo se opera lo físicamente posible: entrada en la subasta de APERTURA
# de la sesión objetivo, salida en la de cierre (retorno capturable). Dos
# construcciones por baseline: long-only top-3 y long-short por terciles.
# Costos por lado en puntos base sobre la exposición bruta (entrada y
# salida = 2 lados por día). Benchmark obligatorio: buy-and-hold de SMH.
# ============================================================

import numpy as np
import pandas as pd

TOP_LONG = 3


def retornos_cartera(df: pd.DataFrame, costo_pb: float) -> dict:
    """`df`: una fila por (fecha_emision, ticker) con `est` y
    `capturable_pct`. Devuelve las series diarias de retorno NETO (%) de
    las dos carteras y su turnover bruto diario."""
    long_only, long_short, fechas = [], [], []
    for fecha, grupo in df.groupby("fecha_emision"):
        g = grupo.dropna(subset=["capturable_pct"]).sort_values("est", ascending=False)
        if len(g) < 4:
            continue
        costo_dia = 2 * costo_pb / 100.0  # % por unidad de exposición bruta

        top = g.head(TOP_LONG)
        ret_lo = float(top["capturable_pct"].mean()) - costo_dia

        tercio = max(1, len(g) // 3)
        largo = g.head(tercio)["capturable_pct"].mean()
        corto = g.tail(tercio)["capturable_pct"].mean()
        # neutral en neto: 0.5 largo − 0.5 corto; bruto = 1.0
        ret_ls = float(0.5 * largo - 0.5 * corto) - costo_dia

        fechas.append(fecha)
        long_only.append(ret_lo)
        long_short.append(ret_ls)
    indice = pd.to_datetime(fechas)
    return {
        "long_only": pd.Series(long_only, index=indice),
        "long_short": pd.Series(long_short, index=indice),
        "turnover_diario": 2.0,  # entra y sale completa cada día, por diseño
    }


def benchmark_smh(serie_smh: pd.Series, fechas: pd.DatetimeIndex) -> pd.Series:
    """Retornos diarios (%) de comprar SMH y no hacer nada, sobre las
    mismas fechas de emisión de la corrida (la respuesta explícita a
    '¿le gana a comprar SMH?' — ajuste del GATE B)."""
    if serie_smh.empty or len(fechas) == 0:
        return pd.Series(dtype=float)
    ret = serie_smh.pct_change() * 100
    ret = ret[(ret.index >= fechas.min()) & (ret.index <= fechas.max())]
    return ret.dropna()
