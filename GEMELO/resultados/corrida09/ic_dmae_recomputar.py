"""Corrida 09, Frente 2f, Parte 1 — recomputa los IC del ΔMAE del WS2b
por bootstrap de CLÚSTER DE DÍA (GEMELO.bifurcaciones._bootstrap_dia).

SIN RED: bloquea socket y fuerza la caché de GEMELO/cache (TTL ignorado).
Solo lectura de senales.db (backtest.linea_base abre en mode=ro).
No escribe en GEMELO/resultados/*.json: sus salidas van a corrida09/.
"""
import argparse, json, os, socket, sys
from datetime import datetime, timezone
import numpy as np, pandas as pd

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, RAIZ)
AQUI = os.path.dirname(os.path.abspath(__file__))


def _sin_red(*a, **k):
    raise RuntimeError("RED BLOQUEADA por el preámbulo de la corrida 09")


socket.socket.connect = _sin_red   # cualquier intento de bajar algo revienta
socket.create_connection = _sin_red
socket.getaddrinfo = _sin_red

from GEMELO import datos                      # noqa: E402
datos._cache_vigente = lambda ruta, ttl: os.path.exists(ruta)   # caché forzada
from GEMELO import control_lineal as cl, experimento as ex, features   # noqa: E402
from GEMELO import bifurcaciones as bf        # noqa: E402
from backtest import inferencia as inf, linea_base as lb          # noqa: E402
from universo import MERCADOS_POR_ABRIR       # noqa: E402

N_BOOT = 4000
SEMILLA = bf.SEMILLA
PARES = (("C2", "C1"), ("C3", "C1"), ("C3", "C2"),
         ("C1", "CAMPEON"), ("C2", "CAMPEON"), ("C3", "CAMPEON"))


def sellado(hasta_sello, dedup):
    df = lb.aplicar_convencion(lb.cargar(hasta_sello=hasta_sello, dedup=dedup),
                               lb.CONVENCION_OFICIAL)
    df = df.rename(columns={"apertura_estimada_pct": "pred_campeon"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df[["fecha", "ticker", "gap_pct", "pred_campeon", "intervalo80_pp", "exchange"]]


def _grupos(j, dif):
    return [g.to_numpy(float) for _, g in pd.Series(dif, index=j.index).groupby(j["fecha"].values)]


def ic_dia(j, dif):
    g = _grupos(j, dif)
    punto, lo, hi = bf._bootstrap_dia(g, N_BOOT, 0.05, SEMILLA)
    p = bf._p_permutacion_dia(g, semilla=SEMILLA)
    _, tlo, thi = bf._ic_t_cluster(g)
    return {"n": int(len(dif)), "dias": len(g), "punto": round(punto, 4),
            "ic_dia": [round(lo, 4), round(hi, 4)],
            "ic_t_cluster": [round(tlo, 4), round(thi, 4)],
            "p_perm_dia": round(p, 4), "excluye_cero_dia": bool(lo > 0 or hi < 0)}


def ic_viejo(dif):
    a = inf.bootstrap_bloques(dif, semilla=cl.SEMILLA_BOOTSTRAP, bloque=cl.BLOQUE_BOOTSTRAP,
                              alpha=cl.ALPHA_BOOTSTRAP, anualizar=1)
    m = inf.bootstrap_media(dif, semilla=cl.SEMILLA_BOOTSTRAP, bloque=cl.BLOQUE_BOOTSTRAP,
                            alpha=cl.ALPHA_BOOTSTRAP)
    return {"ic_sharpe_publicado": [round(a["lo"], 4), round(a["hi"], 4)],
            "ic_media_bloques_filas": [round(m["lo"], 4), round(m["hi"], 4)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hasta-sello", default=None)
    ap.add_argument("--dedup", action="store_true")
    ap.add_argument("--solo-conteo", action="store_true")
    ap.add_argument("--cache-cierres", default=None,
                    help="ruta de un CSV de caché de cierres que sustituye al hash (p.ej. el del 26-ago)")
    a = ap.parse_args()
    if a.cache_cierres:
        ruta_fija = os.path.abspath(a.cache_cierres)
        datos._ruta_cache = lambda tickers, anios: ruta_fija
    sel = sellado(a.hasta_sello, a.dedup)
    print("sellado n =", len(sel), "fechas", sel["fecha"].min().date(), "→", sel["fecha"].max().date(), flush=True)
    if a.solo_conteo:
        return 0
    series, desc = datos.series_para_investigacion(anios=8, usar_cache=True)
    feats = features.construir(series, verificar=False)
    gaps = datos.descargar_gaps(tuple(MERCADOS_POR_ABRIR), anios=8, usar_cache=True)
    panel = ex.construir_panel(feats, gaps)
    ev = sel.merge(feats, left_on="fecha", right_index=True, how="left")
    pred = {}
    for nombre in cl.CONFIGURACIONES:
        pred[nombre] = cl.correr_configuracion(nombre, panel, ev, cl.EMBARGO_DIAS)
        print(nombre, "listo n =", len(pred[nombre]), flush=True)
    pred["CAMPEON"] = ex.evaluar_campeon(sel)
    for k, v in pred.items():
        v.to_csv(os.path.join(AQUI, f"ic_dmae_filas_{k}.csv"), index=False)

    out = {"generado_utc": datetime.now(timezone.utc).isoformat(),
           "hasta_sello": a.hasta_sello, "dedup": a.dedup, "n_boot": N_BOOT,
           "semilla": SEMILLA, "descartadas": desc,
           "fuente_cache": sorted(os.listdir(datos.DIR_CACHE)), "cache_cierres_forzada": a.cache_cierres,
           "pares": [], "vs_cero": []}
    for A, B in PARES:
        j = pred[A].merge(pred[B], on=["fecha", "ticker"], suffixes=("_a", "_b"))
        gap = j["gap_pct_a"].to_numpy(float)
        dif = (np.abs(j["pred_b"] - gap) - np.abs(j["pred_a"] - gap)).to_numpy(float)
        r = {"par": f"{A} vs {B}", **ic_dia(j, dif), **ic_viejo(dif),
             "comparar_original": cl.comparar(pred[A], pred[B], A, B)}
        out["pares"].append(r); print(r["par"], r["punto"], r["ic_dia"], r["p_perm_dia"], flush=True)
    for k in ("C1", "C2", "C3", "CAMPEON"):
        j = pred[k]
        gap = j["gap_pct"].to_numpy(float)
        dif = (np.abs(gap) - np.abs(j["pred"] - gap)).to_numpy(float)
        r = {"config": k, **ic_dia(j, dif), **ic_viejo(dif),
             "mae": round(float(np.abs(j["pred"] - gap).mean()), 4),
             "mae_cero": round(float(np.abs(gap).mean()), 4)}
        out["vs_cero"].append(r); print(k, "vs 0:", r["punto"], r["ic_dia"], r["p_perm_dia"], flush=True)
    with open(os.path.join(AQUI, "ic_dmae_recomputados.json"), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, default=str)
    print("OK", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
