# ============================================================
# GEMELO/sonda_cierre.py — la sonda: ¿a qué hora existe el cierre en yfinance?
# Corrida 13 (19-sep-2026), encargo §5 (bloque 3); acta §86.4 la pidió.
#
#   python -m GEMELO.sonda_cierre                 # descarga y registra una fila por ticker
#   python -m GEMELO.sonda_cierre --desde-csv X   # sin red: observa un CSV de cierres ya grabado
#
# POR QUÉ EXISTE. El sellador del riel de dinero (dinero/sello_dinero.py)
# dispara a las 23:30 de Nueva York y exige el cierre de TODOS los operables
# en la sesión del día (§57, firmada): una sola columna vacía pierde la
# sesión. Dos de nueve noches se perdieron así — el 9-sep a las 21:00 Chile
# faltaban 34 de 36 columnas; el 18-sep a las 23:30 NY faltaba UNA (TOELY).
# La hora del timer se eligió con un argumento que no sobrevivió a la
# primera noche; la siguiente se elige con DATO. Esta sonda produce ese dato:
# cada media hora de la tarde/noche de Nueva York pregunta a yfinance qué
# tickers ya tienen el cierre de la sesión de hoy y lo anota.
#
# QUÉ NO HACE, y hay test: no sella, no escribe en `dinero/`, no abre
# `dinero/sello_dinero.db` ni ninguna base, no importa nada del camino de
# sellado ni de `dinero/`. Lee la lista de tickers del meta del congelado
# grande como TEXTO (json) y anota en `data/sonda_cierre.csv` (append).
#
# LA RESPUESTA GRABADA: cada `dinero/datos/sello/ext_<fecha>.csv` es la
# matriz `Close` que yfinance devolvió esa noche a las 23:30 NY; el test
# alimenta `observar()` con una de ellas y no toca la red.
# ============================================================
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timezone

import exchange_calendars as xcals
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_TICKERS = os.path.join(RAIZ, "dinero", "datos", "cierres_congelados.meta.json")
RUTA_CSV = os.path.join(RAIZ, "data", "sonda_cierre.csv")
EXCHANGE = "XNYS"
ZONA_NY = "America/New_York"
DIAS_DESCARGA = 7            # holgura: fines de semana y feriados largos
COLUMNAS = ("timestamp_utc", "hora_ny", "sesion_ny", "ticker", "ultima_fecha_close",
            "es_sesion_de_hoy", "close_ultimo", "n_filas_respuesta")


def tickers_operables(ruta: str = RUTA_TICKERS) -> list:
    """La lista del congelado grande (36 columnas), leída como texto."""
    with open(ruta, encoding="utf-8") as f:
        return list(json.load(f)["tickers"])


def _cal():
    return xcals.get_calendar(EXCHANGE)


def _a_utc(instante: datetime) -> datetime:
    if instante.tzinfo is None:
        raise ValueError("el instante tiene que traer zona horaria")
    return instante.astimezone(timezone.utc)


def hora_ny(instante_utc: datetime) -> str:
    return pd.Timestamp(_a_utc(instante_utc)).tz_convert(ZONA_NY).strftime("%H:%M")


def sesion_de_hoy(instante_utc: datetime) -> str | None:
    """La sesión de XNYS cuya fecha es la fecha de Nueva York del instante,
    o None si ese día no hay sesión (fin de semana, feriado). Es la sesión
    cuyo cierre la sonda quiere ver aparecer."""
    fecha = pd.Timestamp(_a_utc(instante_utc)).tz_convert(ZONA_NY).normalize().tz_localize(None)
    return str(fecha.date()) if _cal().is_session(fecha) else None


def descargar(tickers, dias: int = DIAS_DESCARGA) -> pd.DataFrame:
    """La ÚNICA función de este módulo que toca la red. Devuelve la matriz
    `Close` (fecha × ticker) tal como yfinance la entrega."""
    import yfinance as yf
    datos = yf.download(list(tickers), period=f"{dias}d", interval="1d", auto_adjust=True, progress=False)
    if datos.empty:
        return pd.DataFrame(columns=list(tickers))
    cierres = datos["Close"] if isinstance(datos.columns, pd.MultiIndex) else datos[["Close"]]
    return cierres.reindex(columns=[t for t in tickers if t in cierres.columns])


def observar(cierres: pd.DataFrame, ahora_utc: datetime, tickers=None) -> list:
    """Una fila por ticker: la última fecha con `Close` no nulo y si esa
    fecha es la sesión de hoy. Función pura de (respuesta, instante)."""
    ahora = _a_utc(ahora_utc)
    idx = pd.to_datetime(cierres.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    cierres = cierres.copy()
    cierres.index = idx
    hoy = sesion_de_hoy(ahora)
    filas = []
    for t in (tickers or list(cierres.columns)):
        s = cierres[t].dropna() if t in cierres.columns else pd.Series(dtype=float)
        ultima = str(s.index[-1].date()) if len(s) else None
        filas.append({
            "timestamp_utc": ahora.isoformat(),
            "hora_ny": hora_ny(ahora),
            "sesion_ny": hoy or "",
            "ticker": t,
            "ultima_fecha_close": ultima or "",
            "es_sesion_de_hoy": int(bool(hoy) and ultima == hoy),
            "close_ultimo": (f"{float(s.iloc[-1]):.6f}" if len(s) else ""),
            "n_filas_respuesta": int(len(cierres)),
        })
    return filas


def registrar(filas: list, ruta: str = RUTA_CSV) -> str:
    """Append al CSV; la cabecera sólo cuando el archivo nace."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    nuevo = not os.path.exists(ruta) or os.path.getsize(ruta) == 0
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(COLUMNAS))
        if nuevo:
            w.writeheader()
        for fila in filas:
            w.writerow({k: fila.get(k, "") for k in COLUMNAS})
    return ruta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="sonda: a qué hora existe el cierre de hoy en yfinance")
    ap.add_argument("--csv", default=RUTA_CSV, help="dónde anotar (append)")
    ap.add_argument("--desde-csv", default=None, help="sin red: observar esta matriz de cierres ya grabada")
    ap.add_argument("--ahora-utc", default=None, help="instante ISO con zona (pruebas); por defecto, el reloj")
    a = ap.parse_args(argv)
    ahora = datetime.fromisoformat(a.ahora_utc) if a.ahora_utc else datetime.now(timezone.utc)
    tickers = tickers_operables()
    if a.desde_csv:
        cierres = pd.read_csv(a.desde_csv, index_col=0, parse_dates=True)
    else:
        cierres = descargar(tickers)
    filas = observar(cierres, ahora, tickers)
    ruta = registrar(filas, a.csv)
    con_hoy = sum(f["es_sesion_de_hoy"] for f in filas)
    print(f"{hora_ny(ahora)} NY · sesión {filas[0]['sesion_ny'] or 'sin sesión'} · "
          f"{con_hoy}/{len(filas)} con cierre de hoy · faltan: "
          f"{[f['ticker'] for f in filas if not f['es_sesion_de_hoy']] if filas[0]['sesion_ny'] else 'n/a'} · {ruta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
