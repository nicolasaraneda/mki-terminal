# ============================================================
# Utilidades de la API (Etapa 4.7) — SOLO capa de presentación.
#
# Nada de lógica de señales aquí: cache TTL para no recomputar el motor en
# cada request, la consulta de earnings (utilidad de datos que el motor
# recibe como parámetro, igual que hace app.py), y la descarga OHLC para el
# gráfico de velas del detalle.
# ============================================================

import time
from datetime import date, datetime
from functools import wraps

import pandas as pd
import yfinance as yf

_cache: dict = {}


def cache_ttl(segundos: int):
    """Cache en memoria por argumentos, con vencimiento. La API es de solo
    lectura sobre datos diarios: recomputar el motor por request sería
    desperdicio, pero el cache nunca debe sobrevivir al día de datos."""
    def decorador(fn):
        @wraps(fn)
        def envuelto(*args, **kwargs):
            clave = (fn.__name__, args, tuple(sorted(kwargs.items())))
            ahora = time.time()
            if clave in _cache:
                ts, valor = _cache[clave]
                if ahora - ts < segundos:
                    return valor
            valor = fn(*args, **kwargs)
            _cache[clave] = (ahora, valor)
            return valor
        return envuelto
    return decorador


@cache_ttl(86400)
def dias_a_proximos_earnings(tickers: tuple) -> dict:
    """Días calendario al próximo reporte por acción (yfinance ticker.calendar).
    Utilidad de presentación equivalente a la de app.py: el motor la recibe
    como parámetro (dias_earnings) — la señal no se toca."""
    hoy = date.today()
    resultado = {}
    for t in tickers:
        try:
            cal = yf.Ticker(t).calendar
            fechas = cal.get("Earnings Date") if isinstance(cal, dict) else None
            if not fechas:
                continue
            futuras = []
            for f in fechas:
                if isinstance(f, datetime):
                    f = f.date()
                if isinstance(f, date) and f >= hoy:
                    futuras.append(f)
            if futuras:
                resultado[t] = (min(futuras) - hoy).days
        except Exception:
            continue
    return resultado


@cache_ttl(900)
def ohlc_1y(ticker: str) -> list:
    """OHLCV diario del último año, en moneda local, para el gráfico de velas.
    Formato lightweight-charts: t/o/h/l/c/v."""
    data = yf.download(ticker, period="1y", interval="1d",
                       auto_adjust=True, progress=False)
    if data.empty:
        return []
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.dropna(subset=["Open", "High", "Low", "Close"])
    return [
        {"t": idx.date().isoformat(),
         "o": round(float(f["Open"]), 4), "h": round(float(f["High"]), 4),
         "l": round(float(f["Low"]), 4), "c": round(float(f["Close"]), 4),
         "v": int(f["Volume"]) if f["Volume"] == f["Volume"] else 0}
        for idx, f in data.iterrows()
    ]


def serie_a_lista(serie: pd.Series, redondeo: int = 4) -> dict:
    """Serie pandas → {fechas: [...], valores: [...]} JSON-friendly."""
    serie = serie.dropna()
    return {
        "fechas": [i.date().isoformat() for i in serie.index],
        "valores": [round(float(v), redondeo) for v in serie.values],
    }
