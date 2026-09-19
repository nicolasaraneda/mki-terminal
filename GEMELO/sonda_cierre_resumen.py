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
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import statistics
from datetime import datetime, timezone

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_CSV = os.path.join(RAIZ, "data", "sonda_cierre.csv")
SALIDA = os.path.join(RAIZ, "GEMELO", "resultados", "sonda_cierre_resumen")


def _minutos(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _hhmm(minutos) -> str | None:
    if minutos is None:
        return None
    return f"{int(minutos) // 60:02d}:{int(minutos) % 60:02d}"


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
        return {"noches": 0, "tickers": {}, "por_noche": {}, "nota": "sin sondas en días con sesión"}
    d["minutos"] = d["hora_ny"].map(_minutos)
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
        por_noche[n] = {
            "tickers": len(horas),
            "con_cierre": len(horas) - len(faltan),
            "hora_todos_ny": _hhmm(max(h for h in horas.values() if h is not None)) if not faltan and horas else None,
            "faltan_hasta_la_ultima_sonda": faltan,
            "ultima_sonda_ny": _hhmm(ultima_sonda[n]),
            "sondas": int(d.loc[d["sesion_ny"] == n, "timestamp_utc"].nunique()),
        }
    completas = [v["hora_todos_ny"] for v in por_noche.values() if v["hora_todos_ny"]]
    return {
        "noches": len(noches),
        "noches_con_todos": len(completas),
        "hora_todos_mediana_ny": _hhmm(statistics.median(_minutos(h) for h in completas)) if completas else None,
        "hora_todos_maxima_ny": _hhmm(max(_minutos(h) for h in completas)) if completas else None,
        "tickers": por_ticker,
        "por_noche": por_noche,
        "estatus": "PROPUESTA: dato de la sonda, no decisión; la hora del timer la fija Nicolás por acta (§58)",
    }


def informe(r: dict, ruta_csv: str = RUTA_CSV) -> str:
    L = ["# Sonda del cierre — a qué hora existe el cierre de hoy en yfinance", "",
         f"- Generado: {datetime.now(timezone.utc).isoformat(timespec='seconds')} · fuente: `{os.path.relpath(ruta_csv, RAIZ)}`",
         f"- Noches con sesión: **{r['noches']}** · noches en que estuvieron todos antes de la última sonda: "
         f"**{r.get('noches_con_todos', 0)}** · hora (NY) a la que estuvieron todos: mediana "
         f"**{r.get('hora_todos_mediana_ny') or '—'}**, máxima **{r.get('hora_todos_maxima_ny') or '—'}**",
         f"- Estatus: {r.get('estatus', '')}", ""]
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
