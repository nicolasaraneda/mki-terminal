# ============================================================
# GEMELO/sonda_cierre_resumen.py — resumen del CSV de la sonda: por ticker,
# la hora (NY) mediana y máxima a la que apareció el cierre de la sesión;
# por noche, la hora a la que estuvieron los N. Corrida 13, bloque 3.4.
#
#   python -m GEMELO.sonda_cierre_resumen [--csv data/sonda_cierre.csv] [--salida GEMELO/resultados/sonda_cierre_resumen]
#
# Es el insumo de la decisión de la hora del timer (espera_firma.md §58):
# produce el dato, no la decisión. Sin red, sin bases; lee un CSV y escribe
# un .md y un .json. Un CSV de pocas noches da un resumen de pocas noches, y
# el informe dice cuántas son en cada fila.
#
# CORRIDA 14, bloque 1.3: la noche es UNA unidad desde las 20:05 NY hasta la
# última sonda de la madrugada. El reloj de la noche tiene que ser monótono o
# las cuentas mienten: con minutos de reloj a secas, 01:05 vale 65 y 20:05
# vale 1.205, así que `min` elegía la sonda de la madrugada como la PRIMERA
# de la noche y una aparición de las 01:05 se leía como anterior a todas las
# de la tarde. Ahora los minutos se cuentan desde la medianoche de la SESIÓN
# atribuida, con el desfase de días que separa la fecha de Nueva York de la
# observación de la fecha de la sesión: 20:05 → 1.205, 01:05 del día
# siguiente → 1.505. Se muestran como reloj de pared con su marca «(+1d)»,
# así que el informe de una noche que termina antes de medianoche sale
# idéntico al de antes.
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import statistics
from datetime import datetime, timezone

import exchange_calendars as xcals
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCHANGE = "XNYS"
RUTA_CSV = os.path.join(RAIZ, "data", "sonda_cierre.csv")
SALIDA = os.path.join(RAIZ, "GEMELO", "resultados", "sonda_cierre_resumen")
ZONA_NY = "America/New_York"


def _minutos(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _hhmm(minutos) -> str | None:
    """Reloj de pared con la marca del día: 1.205 → «20:05», 1.505 → «01:05
    (+1d)». Por debajo de 1.440 devuelve exactamente lo de siempre."""
    if minutos is None:
        return None
    dias, resto = divmod(int(minutos), 1440)
    reloj = f"{resto // 60:02d}:{resto % 60:02d}"
    return f"{reloj} (+{dias}d)" if dias else reloj


def minutos_del_cierre(sesion: str) -> int:
    """Minutos de Nueva York del CIERRE de esa sesión: 960 (16:00) en una
    sesión normal, 780 (13:00) en media sesión de feriado. Sale del
    calendario, no de una constante, porque una media sesión con el umbral
    fijo en 16:00 descartaría observaciones que sí son posteriores al
    cierre."""
    cierre = xcals.get_calendar(EXCHANGE).session_close(pd.Timestamp(sesion))
    hhmm = pd.Timestamp(cierre).tz_convert(ZONA_NY).strftime("%H:%M")
    return _minutos(hhmm)


def minutos_de_la_noche(timestamp_utc: str, sesion_ny: str, hora_ny: str) -> int:
    """Minutos desde la medianoche (Nueva York) de la sesión atribuida, para
    que la noche sea monótona al cruzar la medianoche.

    El desfase de días sale de comparar la FECHA de Nueva York del instante
    con la fecha de la sesión; los minutos del día salen de `hora_ny`, que es
    lo que la sonda grabó. No se recalcula la hora desde `timestamp_utc` a
    propósito: `hora_ny` es el dato observado y cualquier discrepancia entre
    los dos campos es un hallazgo del CSV, no algo que este resumen deba
    corregir en silencio."""
    fecha_ny = pd.Timestamp(timestamp_utc).tz_convert(ZONA_NY).date()
    dias = (fecha_ny - pd.Timestamp(sesion_ny).date()).days
    return max(dias, 0) * 1440 + _minutos(hora_ny)


def cargar(ruta: str = RUTA_CSV) -> pd.DataFrame:
    df = pd.read_csv(ruta, dtype={"sesion_ny": str, "ultima_fecha_close": str, "hora_ny": str})
    df["sesion_ny"] = df["sesion_ny"].fillna("")
    df["es_sesion_de_hoy"] = df["es_sesion_de_hoy"].astype(int)
    return df


def resumen(df: pd.DataFrame) -> dict:
    """Por (noche, ticker): la PRIMERA sonda de la noche que vio el cierre de
    esa sesión (`hora_aparicion`), o None si ninguna lo vio. Por ticker:
    mediana y máximo de esa hora sobre las noches en que apareció, y cuántas
    noches no apareció hasta la última sonda. Por noche: la hora a la que
    estuvieron todos (máximo de las apariciones), o None y quiénes faltaron."""
    d = df[df["sesion_ny"] != ""].copy()
    if d.empty:
        return {"noches": 0, "tickers": {}, "por_noche": {}, "descartadas_antes_del_cierre": {},
                "nota": "sin sondas en días con sesión"}
    d["minutos"] = [minutos_de_la_noche(ts, s, h)
                    for ts, s, h in zip(d["timestamp_utc"], d["sesion_ny"], d["hora_ny"])]

    # Corrida 14 (A9 del pre-mortem): una observación hecha ANTES del cierre de
    # su sesión no puede decir a qué hora apareció el cierre. `es_sesion_de_hoy`
    # se pone en 1 desde la primera barra intradía, porque yfinance etiqueta la
    # barra del día en curso con la fecha del día: el 28-sep-2026 a las 13:42 NY,
    # con la bolsa abierta, 35 de 36 tickers ya la daban. Sin este filtro el
    # informe habría publicado «el cierre apareció a las 13:42» para 35 tickers
    # y habría corrido la mediana de todos ellos. Se descartan y se DECLARA
    # cuántas: no se borra ninguna fila del CSV.
    antes = d["minutos"] < [minutos_del_cierre(s) for s in d["sesion_ny"]]
    fuera = d[antes]
    d = d[~antes]
    descartadas = {
        "filas": int(len(fuera)),
        "motivo": "observación anterior al cierre de su sesión: no es evidencia de cuándo apareció el cierre",
        "por_sesion": {s: sorted(g["hora_ny"].unique().tolist())
                       for s, g in fuera.groupby("sesion_ny")} if len(fuera) else {},
    }
    if d.empty:
        return {"noches": 0, "tickers": {}, "por_noche": {}, "descartadas_antes_del_cierre": descartadas,
                "nota": "todas las sondas de días con sesión son anteriores al cierre de su sesión"}
    noches = sorted(d["sesion_ny"].unique())
    tickers = sorted(d["ticker"].unique())
    ultima_sonda = d.groupby("sesion_ny")["minutos"].max().to_dict()
    aparicion = {}     # (noche, ticker) -> minutos o None
    for (noche, t), g in d.groupby(["sesion_ny", "ticker"]):
        vistos = g.loc[g["es_sesion_de_hoy"] == 1, "minutos"]
        aparicion[(noche, t)] = int(vistos.min()) if len(vistos) else None
    por_ticker = {}
    for t in tickers:
        horas = [aparicion[(n, t)] for n in noches if (n, t) in aparicion]
        vistas = [h for h in horas if h is not None]
        por_ticker[t] = {
            "noches": len(horas),
            "noches_con_cierre": len(vistas),
            "noches_sin_cierre_hasta_la_ultima_sonda": len(horas) - len(vistas),
            "hora_mediana_ny": _hhmm(statistics.median(vistas)) if vistas else None,
            "hora_maxima_ny": _hhmm(max(vistas)) if vistas else None,
            "hora_minima_ny": _hhmm(min(vistas)) if vistas else None,
        }
    por_noche = {}
    for n in noches:
        horas = {t: aparicion.get((n, t)) for t in tickers}
        faltan = sorted(t for t, h in horas.items() if h is None)
        minutos_todos = max((h for h in horas.values() if h is not None), default=None) if not faltan and horas else None
        por_noche[n] = {
            "tickers": len(horas),
            "con_cierre": len(horas) - len(faltan),
            "minutos_todos": minutos_todos,
            "hora_todos_ny": _hhmm(minutos_todos),
            "faltan_hasta_la_ultima_sonda": faltan,
            "ultima_sonda_ny": _hhmm(ultima_sonda[n]),
            "sondas": int(d.loc[d["sesion_ny"] == n, "timestamp_utc"].nunique()),
        }
    completas = [v["minutos_todos"] for v in por_noche.values() if v["minutos_todos"] is not None]
    return {
        "noches": len(noches),
        "noches_con_todos": len(completas),
        "hora_todos_mediana_ny": _hhmm(statistics.median(completas)) if completas else None,
        "hora_todos_maxima_ny": _hhmm(max(completas)) if completas else None,
        "tickers": por_ticker,
        "por_noche": por_noche,
        "descartadas_antes_del_cierre": descartadas,
        "estatus": "PROPUESTA: dato de la sonda, no decisión; la hora del timer la fija Nicolás por acta (§58)",
    }


def informe(r: dict, ruta_csv: str = RUTA_CSV) -> str:
    L = ["# Sonda del cierre — a qué hora existe el cierre de hoy en yfinance", "",
         f"- Generado: {datetime.now(timezone.utc).isoformat(timespec='seconds')} · fuente: `{os.path.relpath(ruta_csv, RAIZ)}`",
         f"- Noches con sesión: **{r['noches']}** · noches en que estuvieron todos antes de la última sonda: "
         f"**{r.get('noches_con_todos', 0)}** · hora (NY) a la que estuvieron todos: mediana "
         f"**{r.get('hora_todos_mediana_ny') or '—'}**, máxima **{r.get('hora_todos_maxima_ny') or '—'}**",
         f"- Estatus: {r.get('estatus', '')}"]
    desc = r.get("descartadas_antes_del_cierre") or {}
    if desc.get("filas"):
        detalle = "; ".join(f"{s}: {', '.join(h)}" for s, h in sorted(desc["por_sesion"].items()))
        L.append(f"- Observaciones descartadas por ser anteriores al cierre de su sesión: "
                 f"**{desc['filas']}** ({detalle}). No dicen a qué hora apareció el cierre: "
                 f"yfinance etiqueta la barra intradía con la fecha del día, así que con el mercado "
                 f"abierto el «cierre de hoy» ya figura. Las filas siguen en el CSV.")
    L.append("")
    if r["noches"] == 0:
        L.append(r.get("nota", "sin datos"))
        return "\n".join(L) + "\n"
    L += ["## Por ticker (hora de Nueva York a la que apareció el cierre de la sesión)", "",
          "| ticker | noches | con cierre | sin cierre hasta la última sonda | mínima | mediana | máxima |", "|---|---|---|---|---|---|---|"]
    for t, v in sorted(r["tickers"].items(), key=lambda kv: (-(kv[1]["noches_sin_cierre_hasta_la_ultima_sonda"]),
                                                            kv[1]["hora_maxima_ny"] or "", kv[0])):
        L.append(f"| {t} | {v['noches']} | {v['noches_con_cierre']} | {v['noches_sin_cierre_hasta_la_ultima_sonda']} | "
                 f"{v['hora_minima_ny'] or '—'} | {v['hora_mediana_ny'] or '—'} | {v['hora_maxima_ny'] or '—'} |")
    L += ["", "## Por noche", "", "| sesión | sondas | última sonda (NY) | con cierre | hora en que estuvieron todos | faltaron hasta la última sonda |",
          "|---|---|---|---|---|---|"]
    for n, v in r["por_noche"].items():
        L.append(f"| {n} | {v['sondas']} | {v['ultima_sonda_ny']} | {v['con_cierre']}/{v['tickers']} | "
                 f"{v['hora_todos_ny'] or '—'} | {', '.join(v['faltan_hasta_la_ultima_sonda']) or '—'} |")
    L += ["", "Una noche sin «hora en que estuvieron todos» es una noche en que el sellador, a cualquiera de "
          "esas horas, habría sellado `insumo_incompleto` bajo la definición firmada (§57)."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=RUTA_CSV)
    ap.add_argument("--salida", default=SALIDA, help="prefijo: se escriben <prefijo>.md y <prefijo>.json")
    a = ap.parse_args(argv)
    r = resumen(cargar(a.csv))
    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    with open(a.salida + ".md", "w", encoding="utf-8") as f:
        f.write(informe(r, a.csv))
    with open(a.salida + ".json", "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(a.salida + ".md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
