# ============================================================
# Capa de datos point-in-time del backtest (DISEÑO.md §5).
#
# Principios:
#  1. UNA descarga al inicio de la corrida (FuenteCongelada): motor.py pasa
#     a servir desde frames congelados — los datos no pueden cambiar a
#     mitad de corrida (el TTL de la caché del motor re-descargaría) y la
#     corrida es determinista. Las funciones *_al(fecha) del motor siguen
#     recortando a <= fecha por su propia vía auditada.
#  2. Toda serie de FEATURES se construye con transformaciones
#     exclusivamente RETROSPECTIVAS (rolling/shift hacia atrás): el valor
#     en la fecha d solo usa datos <= d — point-in-time por construcción.
#  3. validar_sin_futuro() es la guardia dura: cualquier frame de features
#     con fechas posteriores a la emisión revienta con ErrorLookAhead
#     (tests/test_backtest.py lo prueba inyectando un dato futuro).
#  4. Las bases de producción se abren SOLO LECTURA (uri mode=ro).
# ============================================================

import os
import sqlite3
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

import motor
from universo import (EXCHANGE_POR_TICKER, FX_POR_EXCHANGE,
                      INDICE_LOCAL_POR_EXCHANGE, MERCADOS_POR_ABRIR,
                      MONEDA_TICKER, PARES_FX, UNIVERSO)

DIRECTORIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_SENALES = os.path.join(DIRECTORIO, "senales.db")
RUTA_NOTICIAS = os.path.join(DIRECTORIO, "noticias.db")

FECHA_PRIMER_SELLO = date(2026, 7, 5)  # desde aquí existe sentimiento sellado


class ErrorLookAhead(Exception):
    """Un frame de features contiene datos posteriores a la emisión."""


def validar_sin_futuro(df: pd.DataFrame | pd.Series, fecha: date) -> None:
    """Guardia dura de la regla maestra en la capa de features: si el frame
    trae CUALQUIER fila posterior a `fecha`, la corrida muere aquí."""
    if df is None or len(df) == 0:
        return
    maxima = pd.Timestamp(df.index.max()).date()
    if maxima > fecha:
        raise ErrorLookAhead(
            f"features con fecha {maxima} > emisión {fecha} — look-ahead")


def _conexion_ro(ruta: str) -> sqlite3.Connection:
    """Conexión ESTRICTAMENTE de solo lectura a una base de producción."""
    return sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)


class FuenteCongelada:
    """Congela la descarga del run: baja todo UNA vez y reemplaza
    motor._datos_crudos por un servidor de esos frames (context manager).
    Para tests, `series` permite inyectar datos sintéticos sin red."""

    def __init__(self, series: pd.DataFrame | None = None,
                 ohlc: dict | None = None):
        self._series = series          # DataFrame ancho: columna por ticker
        self._ohlc = ohlc or {}        # {ticker: DataFrame[Open, Close]}
        self._original = None

    def _tickers_necesarios(self) -> tuple:
        extras = ("^SOX",) + tuple(PARES_FX) + tuple(
            INDICE_LOCAL_POR_EXCHANGE.values())
        return tuple(sorted(set(list(UNIVERSO.keys()) + list(extras))))

    def __enter__(self):
        import yfinance as yf
        if self._series is None:
            todos = self._tickers_necesarios()
            data = yf.download(list(todos), period=f"{motor.ANIOS_DATOS}y",
                               interval="1d", auto_adjust=True, progress=False)
            self._series = (data["Close"] if isinstance(data.columns, pd.MultiIndex)
                            else data[["Close"]])
            # OHLC de las acciones objetivo (gap y capturable necesitan Open;
            # motor._datos_crudos solo conserva Close). Es dato de OUTCOME,
            # no de feature — ver emision/motorbt para su uso posterior a la
            # sesión objetivo.
            for t in MERCADOS_POR_ABRIR:
                d = yf.download(t, period=f"{motor.ANIOS_DATOS}y", interval="1d",
                                auto_adjust=True, progress=False)
                if isinstance(d.columns, pd.MultiIndex):
                    d.columns = d.columns.get_level_values(0)
                self._ohlc[t] = d[["Open", "Close"]].dropna(how="all")
        self._original = motor._datos_crudos

        series = self._series

        def congelado(tickers: tuple) -> pd.DataFrame:
            presentes = [t for t in tickers if t in series.columns]
            return series[presentes].copy()

        motor._datos_crudos = congelado
        motor._cache.clear()
        return self

    def __exit__(self, *exc):
        motor._datos_crudos = self._original
        motor._cache.clear()
        return False

    # ---------- outcomes (etiquetas, no features) ----------
    def resultado_sesion(self, ticker: str, sesion: str) -> dict | None:
        """gap / retorno de sesión / retorno CAPTURABLE de una sesión local.
        None si la fuente no tiene esa sesión (descarte contado, jamás
        rellenado)."""
        ohlc = self._ohlc.get(ticker)
        if ohlc is None or ohlc.empty:
            return None
        fechas = ohlc.index.strftime("%Y-%m-%d")
        posiciones = {f: i for i, f in enumerate(fechas)}
        if sesion not in posiciones or posiciones[sesion] == 0:
            return None
        i = posiciones[sesion]
        open_obj = float(ohlc["Open"].iloc[i])
        close_obj = float(ohlc["Close"].iloc[i])
        close_ant = float(ohlc["Close"].iloc[i - 1])
        if close_ant <= 0 or open_obj <= 0:
            return None
        return {
            "gap_pct": (open_obj / close_ant - 1) * 100,
            "retorno_sesion_pct": (close_obj / close_ant - 1) * 100,
            "capturable_pct": (close_obj / open_obj - 1) * 100,
        }

    # ---------- features vectorizadas (retrospectivas) ----------
    def cierres(self, tickers: tuple) -> pd.DataFrame:
        return self._series[[t for t in tickers if t in self._series.columns]]

    def serie_benchmark(self, ticker: str) -> pd.Series:
        return self._series[ticker].dropna() if ticker in self._series.columns \
            else pd.Series(dtype=float)


def residual_rolling(ret: pd.Series, ret_idx: pd.Series | None,
                     ret_fx: pd.Series | None, ventana: int = 120) -> pd.Series:
    """Residuos de la acción contra índice local (+FX) con OLS de ventana
    RODANTE de `ventana` sesiones — la variante point-in-time vectorizada
    del _residualizar del motor (que usa ventana expansiva hasta la fecha).
    Cada beta en la fecha d usa solo las `ventana` sesiones <= d.
    La diferencia (rodante vs expansiva) se documenta en DISEÑO.md/código:
    features del backtest, jamás una señal de producción."""
    if ret_idx is None:
        # sin índice local disponible: des-mediado rodante (retrospectivo)
        return (ret - ret.rolling(ventana).mean()).dropna()
    df = pd.concat({"y": ret, "x1": ret_idx}, axis=1)
    if ret_fx is not None:
        df["x2"] = ret_fx
    df = df.dropna()
    if len(df) < ventana:
        return pd.Series(dtype=float)
    medias = df.rolling(ventana).mean()
    if ret_fx is None:
        cov = df["y"].rolling(ventana).cov(df["x1"])
        var = df["x1"].rolling(ventana).var()
        beta = cov / var.replace(0, np.nan)
        res = (df["y"] - medias["y"]) - beta * (df["x1"] - medias["x1"])
        return res.dropna()
    # dos regresores: resolver el sistema 2x2 con momentos rodantes
    c11 = df["x1"].rolling(ventana).var()
    c22 = df["x2"].rolling(ventana).var()
    c12 = df["x1"].rolling(ventana).cov(df["x2"])
    cy1 = df["y"].rolling(ventana).cov(df["x1"])
    cy2 = df["y"].rolling(ventana).cov(df["x2"])
    det = (c11 * c22 - c12 * c12).replace(0, np.nan)
    b1 = (cy1 * c22 - cy2 * c12) / det
    b2 = (cy2 * c11 - cy1 * c12) / det
    res = ((df["y"] - medias["y"])
           - b1 * (df["x1"] - medias["x1"])
           - b2 * (df["x2"] - medias["x2"]))
    return res.dropna()


class SentimientoPIT:
    """Sentimiento por acción "as of" una fecha, con grado de evidencia.

    Grado A: el valor SELLADO en senales_ticker ese día (existe desde el
    05-jul-2026). Grado B: reconstrucción desde noticias.db usando SOLO
    titulares con fecha de publicación <= la fecha pedida, con la MISMA
    fórmula de producción (decaimiento 0.7^días con piso 0.1 × relevancia,
    NULL→1.0) — pero el juicio de la IA se emitió después (analizado_en
    posterior), y por eso es grado B: se declara, no se esconde."""

    def __init__(self):
        self._sellado = {}
        if os.path.exists(RUTA_SENALES):
            conn = _conexion_ro(RUTA_SENALES)
            for f, t, s in conn.execute(
                    "SELECT fecha, ticker, sentimiento_ia FROM senales_ticker "
                    "WHERE sentimiento_ia IS NOT NULL"):
                self._sellado[(f, t)] = float(s)
            conn.close()
        self._titulares = pd.DataFrame(
            columns=["fecha", "ticker", "sentimiento", "relevancia"])
        if os.path.exists(RUTA_NOTICIAS):
            conn = _conexion_ro(RUTA_NOTICIAS)
            filas = conn.execute("""
                SELECT t.fecha, a.tickers_afectados, a.sentimiento,
                       COALESCE(a.relevancia, 1.0)
                FROM analisis a JOIN titulares t ON t.id = a.titular_id
            """).fetchall()
            conn.close()
            registros = []
            for fecha_t, tickers, sent, rel in filas:
                for t in (tickers or "").split(","):
                    t = t.strip()
                    if t in UNIVERSO:
                        registros.append({"fecha": str(fecha_t)[:10], "ticker": t,
                                          "sentimiento": float(sent),
                                          "relevancia": float(rel)})
            if registros:
                self._titulares = pd.DataFrame(registros)

    def valor(self, ticker: str, fecha: date) -> tuple:
        """(sentimiento | None, grado 'A'|'B')."""
        clave = (fecha.isoformat(), ticker)
        if clave in self._sellado:
            return self._sellado[clave], "A"
        df = self._titulares
        df = df[(df["ticker"] == ticker) & (df["fecha"] <= fecha.isoformat())]
        if df.empty:
            return None, "B"
        dias = (pd.Timestamp(fecha) - pd.to_datetime(df["fecha"])).dt.days.clip(lower=0)
        pesos = np.maximum(0.7 ** dias, 0.1) * df["relevancia"].values
        if pesos.sum() <= 0:
            return None, "B"
        return float((df["sentimiento"].values * pesos).sum() / pesos.sum()), "B"


def predicciones_selladas() -> pd.DataFrame:
    """Las predicciones selladas reales (para la auditoría de reproducción
    de B2). Solo lectura."""
    if not os.path.exists(RUTA_SENALES):
        return pd.DataFrame()
    conn = _conexion_ro(RUTA_SENALES)
    df = pd.read_sql_query("""
        SELECT fecha, ticker, apertura_estimada_pct, sesion_objetivo
        FROM senales_ticker
        WHERE apertura_estimada_pct IS NOT NULL AND timestamp_utc IS NOT NULL
    """, conn)
    conn.close()
    return df
