# ============================================================
# dinero/precios.py — adquisición y CONGELADO de precios del riel de dinero.
#
# POR QUÉ EXISTE ESTE ARCHIVO, dicho sin adorno: el proyecto NO guardaba
# precios. `motor._datos_crudos` cachea sólo en memoria; `data/backups/*.csv`
# son filas SELLADAS (gaps, betas, puntajes) y noticias, no series de
# cierres; `GEMELO/cache/` tiene las 15 series macro del DISEÑO §4.1 y está
# en .gitignore. El encargo de la corrida 10 pedía que la cuenta en papel
# corriera "contra los precios ya guardados, sin descargas nuevas", y esos
# precios no existían.
#
# La salida honesta no es llamar "ya guardados" a lo que uno mismo bajó hace
# diez minutos. Es: se baja UNA vez, se CONGELA con fecha, huella y lista de
# tickers, y a partir de ahí todo lo que mide (bloques 4 y 6) lee el archivo
# congelado y no la red. La fuente de datos queda fija por corrida, que es
# la misma regla que backtest/ ya aplica.
#
# AISLAMIENTO: no se importa nada del camino de sellado. La descarga se
# DUPLICA a propósito en vez de reutilizar `motor._datos_crudos`: trece
# instrumentos nuevos son trece formas nuevas de que Yahoo tumbe el sello de
# las 18:15. Mismo criterio que GEMELO/datos.py.
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime, timezone

import pandas as pd
import yfinance as yf

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
DIR_DATOS = os.path.join(DIRECTORIO, "datos")
RUTA_CIERRES = os.path.join(DIR_DATOS, "cierres_congelados.csv")
RUTA_META = os.path.join(DIR_DATOS, "cierres_congelados.meta.json")

ANIOS_POR_DEFECTO = 8


def _huella(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(65536), b""):
            h.update(trozo)
    return h.hexdigest()


def descargar_cierres(tickers, anios: int = ANIOS_POR_DEFECTO) -> pd.DataFrame:
    """Cierres diarios ajustados. Toca la red: esta es la ÚNICA función del
    paquete que lo hace, para que se vea de un vistazo dónde está el riesgo."""
    tickers = list(dict.fromkeys(tickers))
    datos = yf.download(tickers, period=f"{anios}y", interval="1d",
                        auto_adjust=True, progress=False)
    if datos.empty:
        return pd.DataFrame()
    cierres = (datos["Close"] if isinstance(datos.columns, pd.MultiIndex)
               else datos[["Close"]])
    if isinstance(cierres, pd.Series):
        cierres = cierres.to_frame(name=tickers[0])
    return cierres.reindex(columns=[t for t in tickers if t in cierres.columns])


def congelar(cierres: pd.DataFrame, motivo: str,
             ruta: str = RUTA_CIERRES) -> dict:
    """Escribe el archivo congelado y su metadato. Devuelve el metadato."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    cierres.to_csv(ruta)
    meta = {
        "congelado_en_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "motivo": motivo,
        "fuente": "yfinance (mismo proveedor que ya ingiere el proyecto)",
        "tickers": list(cierres.columns),
        "filas": int(len(cierres)),
        "desde": str(cierres.index.min().date()) if len(cierres) else None,
        "hasta": str(cierres.index.max().date()) if len(cierres) else None,
        "sha256": _huella(ruta),
        "advertencia": (
            "Los cierres de yfinance son AJUSTADOS retroactivamente por "
            "splits y dividendos: la serie NO es point-in-time. Para el "
            "riel de dinero eso sesga a favor y está declarado como "
            "limitación, no corregido."),
    }
    ruta_meta = os.path.splitext(ruta)[0] + ".meta.json"
    with open(ruta_meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return meta


def cargar_congelado(ruta: str = RUTA_CIERRES) -> pd.DataFrame:
    """Lee el congelado. NO toca la red: si no está, es un error y no un
    permiso para descargar."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"no hay precios congelados en {ruta}. Se generan una vez con "
            f"`python -m dinero.universo_dinero --congelar`; medir bajando "
            f"datos al vuelo es lo que este archivo existe para impedir.")
    df = pd.read_csv(ruta, index_col=0, parse_dates=True)
    return df


def meta_congelado(ruta: str = RUTA_META) -> dict:
    if not os.path.exists(ruta):
        return {}
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def ultimo_cierre(cierres: pd.DataFrame, ticker: str):
    """(precio, fecha) del último cierre NO nulo, o (None, None)."""
    if ticker not in cierres.columns:
        return None, None
    serie = cierres[ticker].dropna()
    if serie.empty:
        return None, None
    return float(serie.iloc[-1]), serie.index[-1].date()
