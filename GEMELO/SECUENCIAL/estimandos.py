"""Frente E de la séptima corrida (2-sep-2026): estimandos alternativos.

PROPUESTA (regla quinta): ninguno de estos estimandos reemplaza al endpoint
congelado (`acierto_gap` contra «siempre al alza») sin firma de Nicolás y
sin dictamen de `estadistico-adversario`. Este script sólo mide, sobre los
MISMOS datos que ya existen, cuánta señal por día entrega cada uno.

La pregunta: si el endpoint binario necesita ~250 días sellados para ver
9 pp (Frente B), ¿hay un estimando que, con la misma información, necesite
menos? La vara común es «días sellados para potencia 0,80 al efecto
OBSERVADO», extrapolando 1/√D desde el z observado con clúster de día.
Advertencia que gobierna la lectura: el efecto observado de cada candidato
lleva sesgo de ganador (se eligió mirando), así que los días son una COTA
INFERIOR optimista y sirven para COMPARAR estimandos, no para prometer
fechas. La fecha se promete sólo con un MDE fijado antes (Frente B).

Candidatos (por fila i, predicción p_i = `apertura_estimada_pct`, gap g_i):

  E0  Dirección (el endpoint actual): d = 1[signo p = signo g] − 1[g > 0].
  E1  Magnitud: s = |g| − |p − g|. Cuánto reduce el error absoluto conocer
      p frente a predecir gap cero. Supuesto nuevo: que el error L1 es lo
      que importa. NO dice nada de dirección ni de capturabilidad.
  E2  Gap capturado continuo: s = g·(signo p − 1) = lo que se captura
      siguiendo el signo del modelo MENOS lo que captura «siempre al alza».
      Sólo es distinto de cero en las bajas predichas. Supuesto nuevo:
      posición proporcional al signo, sin costos. NO dice si el retorno de
      sesión lo captura (ya se sabe que no).
  E3  Pendiente de calibración: b en g = a + b·p (OLS agrupado, IC por
      bootstrap de día). H0: b = 0. Supuesto nuevo: linealidad. Dice si la
      MAGNITUD predicha ordena la magnitud realizada, no sólo el signo.
  E4  Mecanismo como restricción: pendiente de d sobre h = horas entre la
      emisión (22:15Z) y la apertura objetivo (XTKS/XKRX 1,75; XTAI 2,75;
      XETR 8,75). H0: pendiente 0. Es el decaimiento medido DENTRO de la
      ventana sellada. Supuesto nuevo: que las bolsas difieren sólo en h.
  E5  El decaimiento como estimando sobre la ventana larga reconstruida
      (`backtest/resultados/20260901-133154-*/predicciones_B2.csv`, ~490
      fechas): la misma pendiente y el contraste Asia − Fráncfort, con
      bootstrap de fechas. Dice qué afirmación permite hoy un estimando de
      MECANISMO con dos años en vez de 35 días. NO es sellado.

Uso: `python GEMELO/SECUENCIAL/estimandos.py` → `GEMELO/resultados/estimandos.{json,md}`.
"""
from __future__ import annotations

import glob
import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from backtest import linea_base as lb                     # noqa: E402
from backtest.inferencia import Phi_inv                   # noqa: E402

DIR_RESULTADOS = os.path.join(_RAIZ, "GEMELO", "resultados")
RUTA_B2 = sorted(glob.glob(os.path.join(
    _RAIZ, "backtest", "resultados", "20260901-133154-*", "predicciones_B2.csv")))
HORAS_HASTA_APERTURA = {"XTKS": 1.75, "XKRX": 1.75, "XTAI": 2.75, "XETR": 8.75}
SEMILLA = 20260902
N_BOOT = 4000
ZT = Phi_inv(0.975) + Phi_inv(0.80)      # 2,80: z necesario para potencia 0,80


def _boot_fechas(df: pd.DataFrame, f, n_boot: int = N_BOOT, semilla: int = SEMILLA) -> dict:
    """IC95 por remuestreo de FECHAS enteras de un estadístico f(df)->float."""
    fechas = df["fecha"].unique()
    grupos = {d: g for d, g in df.groupby("fecha")}
    rng = np.random.default_rng(semilla)
    punto = float(f(df))
    reps = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(fechas), size=len(fechas))
        reps.append(f(pd.concat([grupos[fechas[j]] for j in idx])))
    reps = np.array(reps, dtype=float)
    reps = reps[np.isfinite(reps)]
    lo, hi = np.quantile(reps, [0.025, 0.975])
    se = float(reps.std(ddof=1))
    z = punto / se if se > 0 else float("nan")
    return {"punto": punto, "ic95": [float(lo), float(hi)], "se": se, "z": z,
            "dias": int(len(fechas)),
            "dias_para_potencia_0_80_al_efecto_observado":
                (int(round(len(fechas) * (ZT / z) ** 2)) if z and abs(z) > 1e-9 else None)}


def _preparar(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["p"] = out["apertura_estimada_pct"].astype(float)
    out["g"] = out["gap_pct"].astype(float)
    out["sg_p"] = np.where(out["p"] >= 0, 1.0, -1.0)
    out["E0"] = ((out["sg_p"] > 0) == (out["g"] > 0)).astype(float) - (out["g"] > 0).astype(float)
    out["E1"] = out["g"].abs() - (out["p"] - out["g"]).abs()
    out["E2"] = out["g"] * (out["sg_p"] - 1.0)
    out["h"] = out["exchange"].map(HORAS_HASTA_APERTURA)
    return out


def _pendiente(df: pd.DataFrame, x: str, y: str) -> float:
    xv, yv = df[x].to_numpy(float), df[y].to_numpy(float)
    vx = xv.var()
    return float(((xv - xv.mean()) * (yv - yv.mean())).mean() / vx) if vx > 0 else float("nan")


def evaluar(df: pd.DataFrame, etiqueta: str) -> dict:
    df = _preparar(df)
    res = {"etiqueta": etiqueta, "filas": int(len(df)), "dias": int(df["fecha"].nunique())}
    res["E0_direccion_pp"] = _boot_fechas(df, lambda d: 100 * d["E0"].mean())
    res["E1_magnitud_pp"] = _boot_fechas(df, lambda d: d["E1"].mean())
    res["E2_gap_capturado_pp"] = _boot_fechas(df, lambda d: d["E2"].mean())
    res["E3_pendiente_calibracion"] = _boot_fechas(df, lambda d: _pendiente(d, "p", "g"))
    res["E4_pendiente_decaimiento_pp_por_hora"] = _boot_fechas(df, lambda d: 100 * _pendiente(d, "h", "E0"))
    asia = df[df["exchange"].isin(("XTKS", "XKRX", "XTAI"))]
    res["contraste_asia_menos_xetr_pp"] = _boot_fechas(
        df, lambda d: 100 * (d[d["exchange"] != "XETR"]["E0"].mean() - d[d["exchange"] == "XETR"]["E0"].mean())
        if (d["exchange"] == "XETR").any() and (d["exchange"] != "XETR").any() else float("nan"))
    res["por_bolsa"] = {}
    for ex, g in df.groupby("exchange"):
        res["por_bolsa"][ex] = {"filas": int(len(g)), "h": HORAS_HASTA_APERTURA.get(ex),
                               "E0_pp": round(100 * g["E0"].mean(), 2)}
    res["_n_asia"] = int(len(asia))
    return res


def ventana_larga() -> pd.DataFrame:
    df = pd.read_csv(RUTA_B2[-1])
    df = df.drop_duplicates(subset=["ticker", "sesion_objetivo"], keep="first")
    df = df[df["gap_pct"] != 0].rename(columns={"fecha_emision": "fecha", "est": "apertura_estimada_pct"})
    return df


def main() -> dict:
    sellada = lb.aplicar_convencion(lb.cargar(hasta_sello=None), lb.CONVENCION_OFICIAL)
    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — ningún estimando reemplaza al endpoint congelado sin firma y sin dictamen",
           "parametros": {"n_boot": N_BOOT, "semilla": SEMILLA, "z_potencia_0_80": round(ZT, 4),
                          "horas_hasta_apertura": HORAS_HASTA_APERTURA},
           "sellada": evaluar(sellada, f"ventana sellada viva hasta {sellada['fecha'].max()}"),
           "larga": evaluar(ventana_larga(), "ventana larga reconstruida (B2, sep-2024 → ago-2026)")}
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "estimandos.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "estimandos.md"), "w") as f:
        f.write(informe(res))
    return res


CLAVES = (("E0_direccion_pp", "E0 dirección (endpoint actual), pp"),
          ("E1_magnitud_pp", "E1 magnitud: |g| − |p−g|, pp"),
          ("E2_gap_capturado_pp", "E2 gap capturado − siempre al alza, pp"),
          ("E3_pendiente_calibracion", "E3 pendiente g ~ p"),
          ("E4_pendiente_decaimiento_pp_por_hora",
           "E4 decaimiento: pp de ventaja por hora — **RETIRADO por dictamen** (unidad de replicación = bolsa; 4 bolsas, 2 valores de h; p mínimo 1/13). IC y z NO admisibles"),
          ("contraste_asia_menos_xetr_pp",
           "E4' contraste Asia − Fráncfort, pp — **RETIRADO como pendiente**; publicable sólo como comparación de 4 bolsas, no como IC de fecha sobre el mecanismo"))


def _fila(r: dict, k: str, nombre: str) -> str:
    v = r[k]
    d = v["dias_para_potencia_0_80_al_efecto_observado"]
    return (f"| {nombre} | {v['punto']:.3f} | [{v['ic95'][0]:.3f}, {v['ic95'][1]:.3f}] | "
            f"{v['z']:.2f} | {d if d is not None else '—'} |")


def informe(r: dict) -> str:
    L = ["# Estimandos alternativos — Frente E (PROPUESTA)\n", f"> **{r['etiqueta']}**\n",
         f"- Generado: {r['generado_en_utc']} · `python GEMELO/SECUENCIAL/estimandos.py`",
         "- IC95 y z por bootstrap de FECHAS enteras (clúster de día). «Días para 0,80» = días × (2,80/z)²: "
         "cota inferior optimista con sesgo de ganador, sirve para COMPARAR estimandos, no para prometer fechas.",
         "- **Dictamen del `estadistico-adversario` (2-sep, `dictamen_07/DICTAMEN.md`): E4 y E4' RETIRADOS como "
         "estimandos con IC de fecha** — para un parámetro sobre h la unidad de replicación es la bolsa (4, con 2 "
         "valores de h): permutación exacta p = 0,231, p mínimo alcanzable 1/13; bootstrap de bolsas IC95 [−5,4, −1,4]. "
         "Las filas se conservan sólo como registro de lo que se computó; no son afirmaciones del proyecto. "
         "E-1 (E3) entra sólo pre-registrada contra el control lineal.\n"]
    for bloque in ("sellada", "larga"):
        s = r[bloque]
        L += [f"## {s['etiqueta']} — {s['filas']} filas, {s['dias']} días\n",
              "| estimando | punto | IC95 (día) | z | días para 0,80 al efecto observado |", "|---|---|---|---|---|"]
        for k, nombre in CLAVES:
            L.append(_fila(s, k, nombre))
        L += ["\n| bolsa | h | filas | E0 pp |", "|---|---|---|---|"]
        for ex, v in sorted(s["por_bolsa"].items(), key=lambda kv: kv[1]["h"] or 0):
            L.append(f"| {ex} | {v['h']} | {v['filas']} | {v['E0_pp']} |")
        L.append("")
    return "\n".join(L) + "\n"


def solo_informe() -> None:
    """Regenera el `.md` desde el `.json` ya sellado, sin recomputar (7 min)."""
    with open(os.path.join(DIR_RESULTADOS, "estimandos.json")) as f:
        r = json.load(f)
    with open(os.path.join(DIR_RESULTADOS, "estimandos.md"), "w") as f:
        f.write(informe(r))


if __name__ == "__main__":
    if "--solo-informe" in sys.argv:
        solo_informe()
        sys.exit(0)
    r = main()
    for b in ("sellada", "larga"):
        print(b)
        for k, n in CLAVES:
            v = r[b][k]
            print(f"  {n:45s} {v['punto']:8.3f} [{v['ic95'][0]:7.3f},{v['ic95'][1]:7.3f}] z={v['z']:5.2f} D80={v['dias_para_potencia_0_80_al_efecto_observado']}")
