"""GEMELO/juez_lineal_d3.py — el juez lineal bajo D3 (novena corrida, 3-sep-2026).

PROPUESTA. Pre-registro: `GEMELO/preregistro/juez_lineal_d3.md` (leerlo
antes; nada de acá se cambia después de ver resultados). Reusa la
maquinaria del WS2b (`GEMELO/experimento.py`, `GEMELO/control_lineal.py`)
y le pone encima la capa de métrica de D3: MAE contra predecir cero y CRPS
contra una climatología CAUSAL, con intervalos de clúster de día;
dirección como secundaria.

Aislamiento: no importa nada del camino de sellado; lee las filas selladas
vía `backtest.linea_base` (mode=ro). DESCARGA PROHIBIDA: inutiliza
`yf.download` y acepta el caché sin TTL antes de tocar nada.

Uso: python -m GEMELO.juez_lineal_d3 → GEMELO/resultados/corrida09/juez_lineal_d3.{json,md}
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(_AQUI)
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from universo import MERCADOS_POR_ABRIR                      # noqa: E402
from backtest import linea_base as lb                        # noqa: E402
from GEMELO import bifurcaciones as bf                       # noqa: E402
from GEMELO import control_lineal as cl                      # noqa: E402
from GEMELO import datos, features                           # noqa: E402
from GEMELO import experimento as ex                         # noqa: E402

# --- congelado (pre-registro §2-§5) ---
CORTE = "2026-09-02"
CONFIGS = ("C1", "C2")
SEMILLA = 20260903
N_BOOT = 4000
N_PERM = 4000
Z80 = 1.2816
VENTANA_R2 = ("2026-07-15", "2026-07-23")
INTENTOS_DECLARADOS = 36
DIR_SALIDA = os.path.join(_RAIZ, "GEMELO", "resultados", "corrida09")


def _prohibir_descarga():
    """Caché sin TTL y `yf.download` inutilizado: si falta un caché, el
    script muere en vez de bajar datos."""
    datos._cache_vigente = lambda ruta, ttl_horas=None: os.path.exists(ruta)

    def _no(*a, **k):
        raise RuntimeError("descarga prohibida en la corrida 09 (pre-registro §2)")
    datos.yf.download = _no


def filas_selladas(corte: str = CORTE) -> pd.DataFrame:
    df = lb.aplicar_convencion(lb.cargar(hasta_sello=corte, dedup=True), lb.CONVENCION_OFICIAL)
    df = df.rename(columns={"apertura_estimada_pct": "pred_campeon"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df[["fecha", "ticker", "gap_pct", "pred_campeon", "intervalo80_pp", "exchange", "acierto_gap", "base_acierto"]]


def climatologia_causal(panel: pd.DataFrame, fechas: list, embargo: int) -> pd.DataFrame:
    """μ y σ del gap del panel hasta fecha − embargo, por fecha de emisión."""
    out = []
    for f in fechas:
        corte = pd.Timestamp(f) - pd.Timedelta(days=embargo)
        g = panel.loc[panel["fecha"] <= corte, "gap_pct"]
        out.append({"fecha": f, "mu_clim": float(g.mean()), "sd_clim": float(g.std(ddof=1)), "n_clim": int(len(g))})
    return pd.DataFrame(out)


def _crps(y, mu, sigma):
    return cl.crps_normal(np.asarray(y, float), np.asarray(mu, float), np.asarray(sigma, float))


def metricas_por_fila(df: pd.DataFrame) -> pd.DataFrame:
    """m = |g| − |p − g|; c = CRPS(clim) − CRPS(modelo); d = acierto − base."""
    d = df.copy()
    g, p = d["gap_pct"].to_numpy(float), d["pred"].to_numpy(float)
    d["MAE"] = np.abs(g) - np.abs(p - g)
    d["CRPS"] = _crps(g, d["mu_clim"], d["sd_clim"]) - _crps(g, p, d["sigma"])
    d["DIR"] = ((p >= 0) == (g > 0)).astype(float) - (g > 0).astype(float)
    return d


def _resumen_dia(d: pd.DataFrame, col: str, semilla: int) -> dict:
    vals = d[col].to_numpy(float)
    fechas = d["fecha"].astype(str).to_numpy()
    grupos = [vals[fechas == f] for f in sorted(set(fechas))]
    k = len(grupos)
    punto, lo_t, hi_t = bf._ic_t_cluster(grupos)
    _, lo_p, hi_p = bf._bootstrap_dia(grupos, N_BOOT, semilla=semilla)
    p = bf._p_permutacion_dia(grupos, N_PERM, semilla=semilla)
    icc = bf.icc_y_deff(grupos) if k >= 2 else {}
    supera = bool((lo_t > 0) and (p < 0.05))
    return {"n": int(len(vals)), "dias": k, "punto": round(float(punto), 4),
            "ic95_t_cluster": [round(float(lo_t), 4), round(float(hi_t), 4)],
            "ic95_percentil_dia": [round(float(lo_p), 4), round(float(hi_p), 4)],
            "p_permutacion_dia": round(float(p), 4),
            "icc": round(float(icc.get("icc", float("nan"))), 3), "deff": round(float(icc.get("deff", float("nan"))), 2),
            "supera": supera}


def evaluar_todo(preds: dict, etiqueta: str, semilla: int) -> dict:
    res = {"celdas": {}, "pares": {}, "mae_absolutos": {}}
    # dictamen del adversario (3-sep, 12:49): el campeón se publica TAMBIÉN sobre
    # las filas comunes con cada configuración; comparar celdas absolutas
    # sobre filas distintas no es legítimo (C1 no predice el 5-jul).
    preds = dict(preds)
    for cfg in ("C1", "C2"):
        if cfg in preds and "CAMPEON" in preds and len(preds[cfg]):
            comunes = preds["CAMPEON"].merge(preds[cfg][["fecha", "ticker"]], on=["fecha", "ticker"])
            preds[f"CAMPEON@{cfg}"] = comunes
    for nombre, d in preds.items():
        m = metricas_por_fila(d)
        res["celdas"][nombre] = {col: _resumen_dia(m, col, semilla) for col in ("MAE", "CRPS", "DIR")}
        res["mae_absolutos"][nombre] = {"mae_modelo": round(float(np.abs(m["pred"] - m["gap_pct"]).mean()), 4),
                                        "mae_cero": round(float(np.abs(m["gap_pct"]).mean()), 4),
                                        "crps_modelo": round(float(_crps(m["gap_pct"], m["pred"], m["sigma"]).mean()), 4),
                                        "crps_clim": round(float(_crps(m["gap_pct"], m["mu_clim"], m["sd_clim"]).mean()), 4)}
    for a, b in (("C2", "C1"), ("C1", "CAMPEON"), ("C2", "CAMPEON")):
        ma, mb = metricas_por_fila(preds[a]), metricas_por_fila(preds[b])
        j = ma.merge(mb, on=["fecha", "ticker"], suffixes=("_a", "_b"))
        par = {"n": int(len(j))}
        for col in ("MAE", "CRPS", "DIR"):
            dd = j[["fecha"]].copy()
            dd["dif"] = j[f"{col}_a"] - j[f"{col}_b"]
            par[col] = _resumen_dia(dd.rename(columns={"dif": col}), col, semilla)
        res["pares"][f"{a} - {b}"] = par
    res["etiqueta"] = etiqueta
    return res


def _huella(ruta: str) -> dict:
    import hashlib
    from datetime import datetime as _dt
    with open(ruta, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    return {"ruta": os.path.relpath(ruta, _RAIZ), "sha256": sha,
            "mtime_utc": _dt.fromtimestamp(os.path.getmtime(ruta), tz=timezone.utc).isoformat()}


def correr(embargo: int = cl.EMBARGO_DIAS) -> dict:
    _prohibir_descarga()
    sellado = filas_selladas()
    # --- auditoría de look-ahead (3-sep, 5.º auditor), exigido 1: la caché se
    # bajó ANTES del cierre de NY (mtime 13:16 UTC del 1-sep) y su última fila
    # tiene barras intradía parciales y ^SOX en NaN. Se descarta toda fecha
    # posterior a la última barra COMPLETA de ^SOX en la caché cruda, y se
    # sella la huella (sha256 + mtime) de cada caché usado.
    crudos = datos.descargar_cierres(anios=8, usar_cache=True)
    ultima_sox = crudos["^SOX"].dropna().index.max()
    ruta_cierres = datos._ruta_cache(tuple(datos.TICKERS), 8)
    series, descartadas = datos.series_para_investigacion(anios=8, usar_cache=True)
    series = series.loc[:ultima_sox]
    excluidas = sellado[sellado["fecha"] > ultima_sox]
    sellado = sellado[sellado["fecha"] <= ultima_sox].copy()
    # exigido 2: la guarda de conocibilidad ENCENDIDA; si revienta, se sella el
    # motivo y el juez no corre.
    feats = features.construir(series, verificar=True)
    gaps = datos.descargar_gaps(tuple(MERCADOS_POR_ABRIR), anios=8, usar_cache=True)
    import glob
    ruta_gaps = sorted(glob.glob(os.path.join(datos.DIR_CACHE, "gaps_*.csv")))
    gaps = gaps[gaps["sesion"] <= ultima_sox + pd.Timedelta(days=3)]
    panel = ex.construir_panel(feats, gaps)
    if panel.empty:
        raise RuntimeError("panel vacío: falta caché (no se descarga)")
    evaluacion = sellado.merge(feats, left_on="fecha", right_index=True, how="left")
    fechas = sorted(sellado["fecha"].unique())
    clim = climatologia_causal(panel, fechas, embargo)
    # exigido 4: σ del campeón sin nulos ni ceros
    assert sellado["intervalo80_pp"].notna().all() and (sellado["intervalo80_pp"] > 0).all(), "intervalo80_pp con nulos o ceros"

    preds = {}
    for nombre in CONFIGS:
        df = cl.correr_configuracion(nombre, panel, evaluacion, embargo)
        preds[nombre] = df.merge(clim, on="fecha", how="left")
    camp = sellado.dropna(subset=["pred_campeon"]).copy()
    camp["pred"] = camp["pred_campeon"]
    camp["sigma"] = (camp["intervalo80_pp"] / Z80).replace(0.0, np.nan)
    camp["sigma"] = camp["sigma"].fillna(camp["sigma"].median())
    preds["CAMPEON"] = camp[["fecha", "ticker", "pred", "sigma", "gap_pct"]].merge(clim, on="fecha", how="left")

    completo = evaluar_todo(preds, "ventana sellada completa", SEMILLA)
    r2_preds = {k: v[~((v["fecha"] >= VENTANA_R2[0]) & (v["fecha"] <= VENTANA_R2[1]))] for k, v in preds.items()}
    r2 = evaluar_todo(r2_preds, f"R2: sin emisiones {VENTANA_R2[0]}..{VENTANA_R2[1]}", SEMILLA + 2)

    from GEMELO.relevo_asiatico import N_INTENTOS_ACUMULADO
    return {
        "es_veredicto_5_1": False,
        "etiqueta": "PROPUESTA — juez lineal bajo D3, novena corrida; pendiente de dictamen del estadistico-adversario",
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "preregistro": "GEMELO/preregistro/juez_lineal_d3.md",
        "parametros": {"corte": CORTE, "dedup": True, "convencion": lb.CONVENCION_OFICIAL, "configs": list(CONFIGS),
                       "embargo_dias": embargo, "embargo_unidad": "días CALENDARIO (Timedelta), no sesiones",
                       "semilla": SEMILLA, "n_boot": N_BOOT, "n_perm": N_PERM,
                       "cache": {"cierres": _huella(ruta_cierres), "gaps": [_huella(r) for r in ruta_gaps],
                                 "ultima_barra_completa_sox": str(ultima_sox.date()),
                                 "filas_selladas_excluidas_por_cache_parcial": int(len(excluidas)),
                                 "fechas_excluidas": sorted(str(x.date()) for x in excluidas["fecha"].unique())},
                       "verificar_conocibles": "encendido (features.construir(verificar=True)) sobre la última fecha del panel",
                       "rango_predicho_por_config": {k: [str(v["fecha"].min().date()), str(v["fecha"].max().date())] if len(v) else None
                                                     for k, v in preds.items()},
                       "lectura_C2": "C2 sólo predice fechas con vix_term disponible (^VIX3M sin datos desde el 17-jul en la caché): "
                                     "toda comparación con C2 es PAREADA sobre filas comunes y se lee sólo sobre ese rango; "
                                     "sus celdas absolutas no se comparan con las de C1/campeón (enmienda del pre-registro, 3-sep)",
                       "alphas_cv": list(cl.ALPHAS_CV), "pliegues_cv": cl.PLIEGUES_CV, "minimo_entrenamiento": cl.MINIMO_ENTRENAMIENTO,
                       "ventana_r2": list(VENTANA_R2), "intentos_declarados": INTENTOS_DECLARADOS,
                       "registro_intentos_al_correr": int(N_INTENTOS_ACUMULADO),
                       "descartadas_por_cobertura": descartadas},
        "n_sellado": int(len(sellado)), "dias_sellados": len(fechas), "n_panel": int(len(panel)),
        "n_predichas": {k: int(len(v)) for k, v in preds.items()},
        "climatologia_causal_ultima_fecha": clim.iloc[-1].to_dict(),
        "alpha_por_config": {k: sorted(set(round(float(a), 3) for a in v["alpha"].dropna())) for k, v in preds.items() if "alpha" in v},
        "completo": completo, "R2": r2,
        "_filas": {k: metricas_por_fila(v) for k, v in preds.items()},
    }


def _f(c, escala: float = 1.0, dec: int = 3):
    """DIR es una proporción por fila: se publica ×100 en pp (dictamen, exigido iii)."""
    lo, hi = c["ic95_t_cluster"]
    return (f"{escala * c['punto']:+.{dec}f} [{escala * lo:+.{dec}f}, {escala * hi:+.{dec}f}] · "
            f"p día {c['p_permutacion_dia']:.3f} · {'**SUPERA**' if c['supera'] else 'no supera'}")


def _sin_nan(o):
    """NaN → None para que el JSON sea JSON (allow_nan=False)."""
    if isinstance(o, dict):
        return {k: _sin_nan(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_sin_nan(v) for v in o]
    if isinstance(o, float) and o != o:
        return None
    return o


def informe(r: dict) -> str:
    L = ["# El juez lineal bajo D3 — ¿los features disponibles traen magnitud? (novena corrida, 3-sep-2026)\n",
         f"> **{r['etiqueta']}.** No es el veredicto 5.1. Pre-registro: `{r['preregistro']}`. Generado {r['generado_utc']}.\n",
         f"- Filas selladas evaluadas: **{r['n_sellado']}** en **{r['dias_sellados']} días** (corte `{r['parametros']['corte']}`, "
         f"`{r['parametros']['convencion']}`, regla de deduplicación firmada). Panel de entrenamiento: {r['n_panel']} filas; "
         f"embargo {r['parametros']['embargo_dias']} d; series descartadas por cobertura: {r['parametros']['descartadas_por_cobertura']}.",
         f"- Predichas por configuración: {r['n_predichas']}. α elegidos: {r['alpha_por_config']}.",
         f"- Intentos del DSR: **{r['parametros']['intentos_declarados']} declarados antes de correr**; registro al correr "
         f"{r['parametros']['registro_intentos_al_correr']} → {r['parametros']['registro_intentos_al_correr'] + r['parametros']['intentos_declarados']}.",
         "- Unidad: el día. IC95 por t de clúster (gl = k−1); p por permutación de signo de la suma diaria. «Supera» = IC excluye el cero Y p < 0,05.\n"]
    for bloque in ("completo", "R2"):
        b = r[bloque]
        L += [f"## {b['etiqueta']}\n",
              "### Cada modelo contra su vara de D3 (MAE contra predecir cero; CRPS contra la climatología causal; dirección contra «siempre al alza», secundaria)\n",
              "| modelo | n · días | MAE modelo / cero (pp) | ganancia MAE (pp) | CRPS modelo / clim | ganancia CRPS | dirección (pp, ×100) |", "|---|---|---|---|---|---|---|"]
        for nombre, c in b["celdas"].items():
            ab = b["mae_absolutos"][nombre]
            L.append(f"| **{nombre}** | {c['MAE']['n']} · {c['MAE']['dias']} | {ab['mae_modelo']:.3f} / {ab['mae_cero']:.3f} | {_f(c['MAE'])} | "
                     f"{ab['crps_modelo']:.3f} / {ab['crps_clim']:.3f} | {_f(c['CRPS'])} | {_f(c['DIR'], 100, 1)} |")
        L += ["\n### Pareadas sobre las filas que ambos predijeron (positivo = el primero mejor)\n",
              "| par | n · días | Δ ganancia MAE (pp) | Δ ganancia CRPS | Δ dirección (pp) |", "|---|---|---|---|---|"]
        for par, c in b["pares"].items():
            L.append(f"| **{par}** | {c['n']} · {c['MAE']['dias']} | {_f(c['MAE'])} | {_f(c['CRPS'])} | {_f(c['DIR'], 100, 1)} |")
        L.append("")
    c = r["completo"]["celdas"]; r2c = r["R2"]["celdas"]; pr = r["completo"]["pares"]
    L += ["## Lectura (pre-registro §6; redacción exigida por el dictamen del adversario, 3-sep 12:49)\n",
          f"Sobre {r['n_sellado']} filas / {r['dias_sellados']} días, **C1 supera a predecir cero en la ventana completa** "
          f"(MAE {_f(c['C1']['MAE'])}) **pero la ventaja NO sobrevive a R2** (criterio congelado: MAE {_f(r2c['C1']['MAE'])}); "
          f"**no supera al campeón sobre las mismas filas** (C1 − campeón, MAE {_f(pr['C1 - CAMPEON']['MAE'])}: contiene el cero, punto a favor del campeón), "
          f"y **sobre esas mismas {c.get('CAMPEON@C1', c['CAMPEON'])['MAE']['n']} filas el campeón supera a cero más que C1** "
          f"(campeón@C1: MAE {_f(c.get('CAMPEON@C1', c['CAMPEON'])['MAE'])}; la celda del campeón sobre sus {c['CAMPEON']['MAE']['n']} filas —MAE {_f(c['CAMPEON']['MAE'])}— "
          "no es comparable con la de C1: las 8 filas que C1 no predice son el domingo 5-jul, donde el campeón perdió contra cero). "
          f"La información extra (C2 − C1, {pr['C2 - C1']['n']} filas / {pr['C2 - C1']['MAE']['dias']} días) no trae magnitud detectable en ningún sentido: potencia nula, no ausencia. "
          "**Conclusión honesta:** los features disponibles no traen señal de magnitud detectable con esta ventana que sea distinta de la que ya porta SOX(t, t−1) ni robusta a R2. "
          "C1 agrupada emite una sola predicción por día (signo del SOX con magnitud encogida por la ridge, α = 100): por eso C1 − campeón en dirección es 0,000 exacto. "
          "La potencia de magnitud al efecto observado es 0,86 [0,83, 0,89] el 25-oct (`espera_firma` §29); ninguna fecha se afirma. "
          "Este juez es EXPLORATORIO (V1-bis sin firma; endpoint elegido tras ver la ventana; sin hash de commit anterior a la corrida) y no computa como evidencia de R1.\n",
          "## Lo que este diseño no puede decir (pre-registro §7)\n",
          "Un solo régimen sellado; el campeón está en muestra (sus β se estimaron sobre esta misma historia); la climatología causal es "
          "agrupada (no por ticker; el adversario midió que sesga A FAVOR de los modelos por +0,012 [+0,000, +0,023] de CRPS, sin cambiar ninguna celda); "
          "la normal subestima colas (CRPS = cota optimista para todos por igual). ICC/DEFF por celda en el JSON; un DEFF < 1 (p. ej. C2 − C1 en dirección) "
          "es un ICC negativo con pocos clústeres, no un error. Embargo en días calendario. CSV por fila en `corrida09/juez_lineal_d3_filas_*.csv`.\n"]
    return "\n".join(L) + "\n"


def main() -> int:
    r = correr()
    os.makedirs(DIR_SALIDA, exist_ok=True)
    for nombre, d in r.pop("_filas").items():
        d.to_csv(os.path.join(DIR_SALIDA, f"juez_lineal_d3_filas_{nombre}.csv"), index=False)
    with open(os.path.join(DIR_SALIDA, "juez_lineal_d3.json"), "w") as f:
        json.dump(_sin_nan(r), f, indent=1, ensure_ascii=False, default=str, allow_nan=False)
    with open(os.path.join(DIR_SALIDA, "juez_lineal_d3.md"), "w") as f:
        f.write(informe(r))
    print(informe(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
