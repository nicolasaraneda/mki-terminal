"""Frente A de la octava corrida: el instrumento contra un patrón conocido.

Cuatro experimentos sobre `GEMELO/simulador/proceso.py` con verdad
conocida (pre-registro: `GEMELO/preregistro/frente_A.md`):

  A1  cobertura del IC95 de clúster de día (percentil / básico / t de
      clúster gl = k−1) vs del IC95 iid de filas — semilla de bootstrap
      POR RÉPLICA, ≥ 10.000 réplicas
  A2  tamaño de las 192 celdas legítimas (`bifurcaciones.EJES` +
      `bifurcaciones.aplicar`) bajo δ = 0 Y bajo la alternativa (6,5 y 9 pp),
      con la permutación de signo por día; P(0 de 192) y cociente de
      verosimilitudes de «0 de 192»
  A3  DSR con el registro vigente bajo la nula, en las DOS unidades
      (anualizada = el defecto; por período = la corrección), tamaño
      teórico exacto y sensibilidad a la elección de V
  A4  potencia frente a 9 / 6,5 / 5 pp en los horizontes de `horizonte.md`,
      comparación PAREADA con `horizonte.md` (McNemar exacto) y una tercera
      ruta cerrada (normal) que usa sólo la sd de la suma por día real
  A5  sensibilidad del DGP: ν, c y dependencia entre días (AR(1) en los
      factores de día) — lo que el pre-registro prometió y la primera
      versión no entregó

Versión 2 (2-sep-2026, después del dictamen del `estadistico-adversario`
sobre la versión 1: NO SOSTIENE tal como estaba escrita). Toda fracción
lleva Wilson; cada generador declara su verdad medida 8 veces a 200.000
días, con intervalo. Uso: `python GEMELO/simulador/calibracion.py` →
`GEMELO/resultados/calibracion_instrumento.{json,md}`.
"""
from __future__ import annotations

import itertools
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

from backtest import inferencia as inf                      # noqa: E402
from backtest import linea_base as lb                       # noqa: E402
from GEMELO import bifurcaciones as bf                      # noqa: E402
from GEMELO.simulador import proceso as pr                  # noqa: E402

DIR_RESULTADOS = os.path.join(_RAIZ, "GEMELO", "resultados")
SEMILLA = 20260902
ICC_OBJETIVO = None          # se lee de la máquina en main()
N_REP_COBERTURA = 10000
N_REP_CELDAS = 300
N_REP_CELDAS_ALT = 200
N_REP_DSR = 4000
N_REP_POTENCIA = 500
N_REP_SENSIBILIDAD = 3000
N_MEDIDAS_VERDAD = 8
N_BOOT = 400
N_PERM = 400
HORIZONTES = (35, 73, 125, 250, 475, 803)
DELTAS = (0.05, 0.065, 0.09)
N_INTENTOS_REGISTRO = None   # se lee de la máquina en main()
Z95 = 1.959963984540054


def _wilson(k, n):
    lo, hi = lb._wilson(int(k), int(n))
    return [round(lo / 100, 4), round(hi / 100, 4)]


def _phi(z):
    return 0.5 * math.erfc(-z / math.sqrt(2))


def _grupos(df):
    d = df[df["gap_pct"] != 0].copy()
    d["fecha"] = d["dia"]
    vals = (d["acierto_gap"] - (d["gap_pct"] > 0).astype(int)).to_numpy(dtype=float)
    return d, vals, bf._por_dia(d, vals)


def verdad_con_intervalo(q, n_medidas=N_MEDIDAS_VERDAD, semilla=SEMILLA):
    """δ verdadero del generador: media de `n_medidas` mediciones
    independientes a 200.000 días, con su sd e IC95 (el punto sin intervalo
    fue una de las objeciones del adversario)."""
    v = [pr.ventaja(pr.simular(q, 200_000, np.random.default_rng(semilla + 99 + 1000 * i)))
         for i in range(n_medidas)]
    v = np.array(v)
    m, sd = float(v.mean()), float(v.std(ddof=1))
    return m, {"verdad_delta_pp": round(100 * m, 3), "sd_pp": round(100 * sd, 3),
               "ic95_pp": [round(100 * (m - Z95 * sd / math.sqrt(n_medidas)), 3),
                           round(100 * (m + Z95 * sd / math.sqrt(n_medidas)), 3)],
               "n_medidas": n_medidas, "dias_por_medida": 200_000}


# ------------------------------------------------------------
# A1 · cobertura, cuatro estimadores, semilla por réplica
# ------------------------------------------------------------
def cobertura(p, verdad, n_dias, n_rep=N_REP_COBERTURA, semilla=SEMILLA, con_permutacion=False):
    rng = np.random.default_rng(semilla)
    dentro = {"percentil": 0, "basico": 0, "t_cluster": 0, "iid": 0}
    anchos = {k: [] for k in dentro}
    rech_perm = 0
    for r in range(n_rep):
        df = pr.simular(p, n_dias, rng)
        _, vals, g = _grupos(df)
        punto, lo, hi = bf._bootstrap_dia(g, n_boot=N_BOOT, semilla=semilla + 104729 * (r + 1))
        lo_b, hi_b = 2 * punto - hi, 2 * punto - lo
        _, lo_t, hi_t = bf._ic_t_cluster(g)
        m, se = vals.mean(), vals.std(ddof=1) / math.sqrt(len(vals))
        lo_i, hi_i = m - Z95 * se, m + Z95 * se
        for k, (a, b) in {"percentil": (lo, hi), "basico": (lo_b, hi_b),
                          "t_cluster": (lo_t, hi_t), "iid": (lo_i, hi_i)}.items():
            dentro[k] += a <= verdad <= b
            anchos[k].append(b - a)
        if con_permutacion:
            rech_perm += bf._p_permutacion_dia(g, N_PERM, semilla=semilla + 7 * r + 3) < 0.05
    out = {"n_rep": n_rep, "verdad_pp": round(100 * verdad, 3)}
    for k in dentro:
        out[f"cobertura_{k}"] = round(dentro[k] / n_rep, 4)
        out[f"ic95_{k}"] = _wilson(dentro[k], n_rep)
        out[f"ancho_medio_{k}_pp"] = round(100 * float(np.mean(anchos[k])), 2)
    # compatibilidad con la v1 del informe
    out["cobertura_dia"], out["ic95_dia"] = out["cobertura_percentil"], out["ic95_percentil"]
    out["cobertura_iid"], out["ic95_iid"] = out["cobertura_iid"], out["ic95_iid"]
    if con_permutacion:
        out["tamano_permutacion_dia"] = round(rech_perm / n_rep, 4)
        out["ic95_tamano_permutacion"] = _wilson(rech_perm, n_rep)
    return out


# ------------------------------------------------------------
# A2 · las 192 celdas bajo la nula y bajo la alternativa
# ------------------------------------------------------------
def _celdas():
    ejes = list(bf.EJES.keys())
    for combo in itertools.product(*[bf.EJES[e] for e in ejes]):
        yield dict(zip(ejes, combo))


def celdas(p, fechas_reales, n_rep=N_REP_CELDAS, semilla=SEMILLA):
    """Simula ventanas del tamaño de la viva, mapea `dia` a las fechas reales
    (para que los ejes de fecha —R2, 29-jul, parciales, corte— seleccionen
    las mismas posiciones que en la realidad) y aplica las 192 celdas con
    el código del proyecto. Cuenta p < 0,05 por celda y por réplica. Bajo
    δ = 0 mide el tamaño familywise; bajo δ > 0, cuántas celdas cruzan
    cuando SÍ hay efecto — sin eso «0 de 192» no se puede leer."""
    rng = np.random.default_rng(semilla + 1)
    lista = list(_celdas())
    n_dias = len(fechas_reales)
    cruces_por_rep, cruces_por_celda = [], np.zeros(len(lista))
    for r in range(n_rep):
        df = pr.simular(p, n_dias, rng)
        df["fecha"] = np.array(fechas_reales)[df["dia"].to_numpy()]
        k = 0
        for j, c in enumerate(lista):
            base = df if c["corte"] == "vivo" else df[df["fecha"] <= lb.CORTE_SECCION_2]
            out = bf.aplicar(base, c)
            vals = (out["acierto"] - out["base_acierto"]).to_numpy(dtype=float)
            g = bf._por_dia(out, vals)
            pv = bf._p_permutacion_dia(g, N_PERM, semilla=semilla + 7919 * r + j)
            if pv < 0.05:
                k += 1
                cruces_por_celda[j] += 1
        cruces_por_rep.append(k)
    cr = np.array(cruces_por_rep)
    al_menos_una = int((cr >= 1).sum())
    cero = int((cr == 0).sum())
    # IC de la tasa por celda remuestreando RÉPLICAS (la unidad de clustering:
    # las 192 celdas miran casi las mismas filas). El agregado ingenuo
    # 192 × n_rep sería el intervalo equivocado.
    rb = np.random.default_rng(semilla + 5)
    tasas = [cr[rb.integers(0, n_rep, n_rep)].mean() / len(lista) for _ in range(2000)]
    return {"n_rep": n_rep, "celdas": len(lista), "n_perm": N_PERM,
            "media_celdas_con_p_menor_005": round(float(cr.mean()), 2),
            "tasa_media_por_celda": round(float(cr.mean() / len(lista)), 4),
            "ic95_tasa_por_celda_sobre_replicas": [round(float(np.quantile(tasas, 0.025)), 4),
                                                   round(float(np.quantile(tasas, 0.975)), 4)],
            "p_cero_de_192": round(cero / n_rep, 4), "ic95_cero_de_192": _wilson(cero, n_rep),
            "p_al_menos_una": round(al_menos_una / n_rep, 4), "ic95_al_menos_una": _wilson(al_menos_una, n_rep),
            "p_al_menos_10": round(float((cr >= 10).sum() / n_rep), 4),
            "cuantiles_celdas_por_rep": {q: int(np.quantile(cr, q)) for q in (0.5, 0.9, 0.95, 0.99)},
            "max_celdas_en_una_rep": int(cr.max()),
            "celda_mas_permisiva": {"tasa": round(float(cruces_por_celda.max() / n_rep), 4),
                                    "celda": lista[int(cruces_por_celda.argmax())]},
            "observado_en_la_ventana_real": "0 de 192 (bifurcaciones.md)"}


# ------------------------------------------------------------
# A3 · DSR bajo la nula, dos unidades, tamaño teórico, elección de V
# ------------------------------------------------------------
def dsr_bajo_nula(N, T, n_rep=N_REP_DSR, semilla=SEMILLA):
    """N estrategias sin habilidad (retornos diarios t_4 iid, media 0) durante
    T días; se elige la de mejor Sharpe. Fracción con DSR ≥ 0,95 en:
      · `anualizado` — Sharpe·√252 con n = T (EL DEFECTO que tenían los
        dos llamadores hasta el 2-sep; se publica etiquetado, no como
        instrumento);
      · `por_periodo` — Sharpe por período (la corrección), con V = varianza
        de los N Sharpes INCLUIDO el ganador (la regla del proyecto);
      · `por_periodo_V_sin_ganador` y `por_periodo_V_teorica` (V = 1/T):
        la elección de V es de primer orden a N chico."""
    rng = np.random.default_rng(semilla + 2)
    k = {"anualizado": 0, "por_periodo": 0, "por_periodo_V_sin_ganador": 0, "por_periodo_V_teorica": 0}
    k_psr = 0
    for _ in range(n_rep):
        r = pr._t(rng, (N, T), 4) * 0.01
        sh_p = r.mean(axis=1) / r.std(axis=1, ddof=1)
        sh_a = sh_p * math.sqrt(252)
        i = int(sh_p.argmax())
        # el defecto se COMPUTA con la misma aritmética que tenían los llamadores,
        # sin pasar por la guarda de unidad (que nació de esta medición): nunca
        # un supuesto en el lugar de un cómputo (guardián, O2)
        k["anualizado"] += _dsr_sin_guarda(float(sh_a.max()), T, N, float(sh_a.var(ddof=1))) >= 0.95
        k["por_periodo"] += inf.dsr(float(sh_p[i]), T, 0.0, 3.0, N, float(sh_p.var(ddof=1))) >= 0.95
        resto = np.delete(sh_p, i)
        k["por_periodo_V_sin_ganador"] += inf.dsr(float(sh_p[i]), T, 0.0, 3.0, N, float(resto.var(ddof=1))) >= 0.95
        k["por_periodo_V_teorica"] += inf.dsr(float(sh_p[i]), T, 0.0, 3.0, N, 1.0 / T) >= 0.95
        k_psr += inf.Phi(float(sh_a.max()) / inf.se_sharpe(float(sh_a.max()), T, 0.0, 3.0)) >= 0.95
    out = {"N_intentos": N, "T_dias": T, "n_rep": n_rep, "tamano_teorico_gaussiano": tamano_teorico(N)}
    for nombre, c in k.items():
        out[f"p_dsr_mayor_095_{nombre}"] = round(c / n_rep, 4)
        out[f"ic95_{nombre}"] = _wilson(c, n_rep)
    out["p_psr_anualizado_del_mejor_mayor_095"] = round(k_psr / n_rep, 4)
    out["ic95_psr_anualizado"] = _wilson(k_psr, n_rep)
    # compatibilidad con la v1 (el defecto, etiquetado)
    out["p_dsr_mayor_095"] = out["p_dsr_mayor_095_anualizado"]
    out["ic95"] = out["ic95_anualizado"]
    return out


def _dsr_sin_guarda(sr, T, N, V):
    """DSR con la aritmética exacta de `inferencia.dsr` pero sin la guarda de
    unidad: Phi((sr − sr0)/se). Sólo para medir el defecto anualizado."""
    sr0 = inf.sr0_deflacionado(N, V)
    return inf.Phi((sr - sr0) / inf.se_sharpe(sr, T, 0.0, 3.0))


def tamano_teorico(N, n=400_000, semilla=SEMILLA + 11):
    """«DSR ≥ 0,95» NO es un test de tamaño 5%: sr0 es el máximo ESPERADO
    de N nulos. En el límite gaussiano exacto: P(max_N Z > E[max_N Z] +
    1,645), por sorteo del máximo de N normales."""
    rng = np.random.default_rng(semilla)
    maxs = np.concatenate([rng.standard_normal((50_000, N)).max(axis=1) for _ in range(n // 50_000)])
    m = float(maxs.mean())
    return {"m_N_sd": round(m, 4), "tamano": round(float((maxs > m + 1.645).mean()), 5), "sorteos": len(maxs)}


# ------------------------------------------------------------
# A4 · potencia, comparación pareada y tercera ruta cerrada
# ------------------------------------------------------------
def potencia(p, n_dias, n_rep=N_REP_POTENCIA, semilla=SEMILLA):
    rng = np.random.default_rng(semilla + 3)
    k = 0
    for r in range(n_rep):
        df = pr.simular(p, n_dias, rng)
        _, _, g = _grupos(df)
        if bf._p_permutacion_dia(g, N_PERM, semilla=semilla + 31 * r + n_dias) < 0.05:
            k += 1
    return {"n_dias": n_dias, "n_rep": n_rep, "potencia": round(k / n_rep, 3), "ic95": _wilson(k, n_rep)}


def potencia_normal_cerrada(delta, n_dias, n_medio, sd_suma_dia):
    """Tercera ruta, sin simulación: la permutación de signo sobre sumas de
    día es ~ un test z de la media de D sumas con sd `sd_suma_dia` y media
    δ·n̄. potencia = 1 − Φ(1,96 − z) + Φ(−1,96 − z), z = δ·n̄·√D / sd."""
    z = delta * n_medio * math.sqrt(n_dias) / sd_suma_dia
    return round(1 - _phi(Z95 - z) + _phi(-Z95 - z), 3)


def _mcnemar_exacto(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return round(min(1.0, 2 * p), 6)


def comparar_con_horizonte(a4, ref, semilla=SEMILLA):
    """Comparación PAREADA simulador vs `horizonte.md` celda a celda (mismo
    δ, mismo horizonte): signo de la diferencia (McNemar exacto) y
    diferencia media con IC por bootstrap sobre las celdas."""
    pares = []
    for objetivo, bloque in a4.items():
        clave = {"0.05": "potencia_5.0pp", "0.065": "potencia_6.5pp", "0.09": "potencia_9.0pp"}.get(objetivo)
        for fila in bloque["por_horizonte"]:
            h = ref.get(str(fila["n_dias"]), {})
            if clave and clave in h and isinstance(h[clave], (int, float)):
                pares.append((objetivo, fila["n_dias"], fila["potencia"], float(h[clave])))
    if not pares:
        return {"pares": 0}
    d = np.array([s - r for _, _, s, r in pares])
    b, c = int((d < 0).sum()), int((d > 0).sum())
    rng = np.random.default_rng(semilla + 17)
    boot = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(4000)]
    return {"pares": len(pares), "simulador_por_debajo": b, "simulador_por_encima": c,
            "mcnemar_exacto_p": _mcnemar_exacto(b, c),
            "diferencia_media_horizonte_menos_simulador_pp": round(-100 * float(d.mean()), 2),
            "ic95_pp": [round(-100 * float(np.quantile(boot, 0.975)), 2), round(-100 * float(np.quantile(boot, 0.025)), 2)],
            "detalle": [{"delta": o, "dias": n, "simulador": s, "horizonte": r} for o, n, s, r in pares]}


# ------------------------------------------------------------
# A5 · sensibilidad del DGP
# ------------------------------------------------------------
def sensibilidad(q0, base, n_rep=N_REP_SENSIBILIDAD, semilla=SEMILLA):
    out = {"nu": [], "c": [], "rho": []}
    for nu in (4, 6, 10, 30):
        q = pr.Parametros(**{**q0.__dict__, "nu": nu})
        v, vd = verdad_con_intervalo(q, n_medidas=2, semilla=semilla + nu)
        cob = cobertura(q, v, len(base.tamanos), n_rep=n_rep, semilla=semilla + 100 + nu)
        out["nu"].append({"nu": nu, **vd, **{k: cob[k] for k in cob if k.startswith(("cobertura_", "ic95_"))}})
    for f in (0.5, 1.5):
        q = pr.Parametros(**{**q0.__dict__, "c": q0.c * f})
        v, vd = verdad_con_intervalo(q, n_medidas=2, semilla=semilla + int(10 * f))
        icc = pr.icc_de_aciertos(pr.simular(q, 80_000, np.random.default_rng(semilla + 1)))
        cob = cobertura(q, v, len(base.tamanos), n_rep=n_rep, semilla=semilla + 200 + int(10 * f))
        out["c"].append({"factor_c": f, "c": round(q.c, 4), "icc_sim": round(icc["icc"], 4), **vd,
                         **{k: cob[k] for k in cob if k.startswith(("cobertura_", "ic95_"))}})
    for rho in (0.0, 0.2, 0.4):
        q = pr.Parametros(**{**q0.__dict__, "rho": rho})
        v, vd = verdad_con_intervalo(q, n_medidas=2, semilla=semilla + int(100 * rho))
        cob = cobertura(q, v, len(base.tamanos), n_rep=n_rep, semilla=semilla + 300 + int(100 * rho),
                        con_permutacion=True)
        out["rho"].append({"rho": rho, **vd, **{k: cob[k] for k in cob
                                                 if k.startswith(("cobertura_", "ic95_", "tamano_"))}})
    return out


def piso_idiosincratico(q):
    """En qué tickers la parte común β²(b²·esc² + c²) excede la σ total
    sellada y el piso del 30% ata (la varianza marginal simulada queda por
    encima de la real: infla la dependencia intra-día simulada)."""
    filas = []
    for t in q.tickers:
        comun = q.beta[t] ** 2 * (q.b ** 2 * q.escala_sox ** 2 + q.c ** 2)
        sd_sim = math.sqrt(comun + pr.sigma_idiosincratica(q)[t] ** 2)
        filas.append({"ticker": t, "sigma_sellada": round(q.sigma[t], 3), "raiz_comun": round(math.sqrt(comun), 3),
                      "piso_ata": bool(comun > q.sigma[t] ** 2 * (1 - pr.PISO_IDIOSINCRATICO ** 2)),
                      "sd_gap_simulada": round(sd_sim, 3),
                      "exceso_pct": round(100 * (sd_sim / q.sigma[t] - 1), 1)})
    return filas


def main() -> dict:
    global ICC_OBJETIVO, N_INTENTOS_REGISTRO
    from GEMELO.relevo_asiatico import N_INTENTOS_ACUMULADO
    from backtest.veredicto_51 import N_INTENTOS_51
    N_INTENTOS_REGISTRO = int(N_INTENTOS_ACUMULADO)
    base = pr.calibrar_desde_sellado()
    df_real = lb.aplicar_convencion(lb.cargar(hasta_sello=lb.CORTE_REGLA_FIRMADA), lb.CONVENCION_OFICIAL)
    vals = (df_real["acierto_gap"] - df_real["base_acierto"]).to_numpy(dtype=float)
    g_real = bf._por_dia(df_real, vals)
    icc_real = bf.icc_y_deff(g_real)
    ICC_OBJETIVO = float(icc_real["icc"])
    sumas = np.array([g.sum() for g in g_real]); cuentas = np.array([len(g) for g in g_real])
    sd_suma_dia = float(sumas.std(ddof=1)); n_medio = float(cuentas.mean())
    vivo = lb.aplicar_convencion(lb.cargar(hasta_sello=None), lb.CONVENCION_OFICIAL)
    fechas_reales = sorted(vivo["fecha"].unique())
    tamanos_vivo = [int(x) for x in vivo.groupby("fecha").size().tolist()]

    res = {"generado_en_utc": datetime.now(timezone.utc).isoformat(),
           "etiqueta": "PROPUESTA — Frente A v2, octava corrida; reescrito tras el dictamen del adversario",
           "calibracion_leida_de_la_maquina": {
               "advertencia_procedencia": "ancla = cadena LOCAL a CORTE_REGLA_FIRMADA (31-ago), NO la ventana canónica publicada (n = 248, cadena compuesta)",
               "icc_real": round(ICC_OBJETIVO, 4), "deff_real": round(icc_real["deff"], 4),
               "n_efectivo_real": round(icc_real["n_efectivo"], 2), "n": int(len(df_real)),
               "dias": int(df_real["fecha"].nunique()), "dias_vivos": len(fechas_reales),
               "sd_suma_por_dia_real": round(sd_suma_dia, 4), "n_medio_por_dia_real": round(n_medio, 3),
               "registro_intentos": N_INTENTOS_REGISTRO, "N_51": int(N_INTENTOS_51),
               "parametros_base": base.como_dict()},
           "generadores": {}}

    gens = {}
    for objetivo in (0.0,) + DELTAS:
        q = pr.calibrar(base, objetivo, ICC_OBJETIVO)
        verdad, vd = verdad_con_intervalo(q)
        icc = pr.icc_de_aciertos(pr.simular(q, 80_000, np.random.default_rng(SEMILLA + 98)))
        grande = pr.simular(q, 200_000, np.random.default_rng(SEMILLA + 99))
        gens[objetivo] = (q, verdad)
        res["generadores"][str(objetivo)] = {
            "b": round(q.b, 4), "c": round(q.c, 4), **vd,
            "icc_objetivo": round(ICC_OBJETIVO, 4), "icc_sim": round(icc["icc"], 4),
            "icc_fuera_de_tolerancia_0005": bool(abs(icc["icc"] - ICC_OBJETIVO) > 0.005),
            "deff_sim": round(icc["deff"], 3),
            "sigma_idiosincratica": {k: round(v, 3) for k, v in pr.sigma_idiosincratica(q).items()},
            "piso_idiosincratico": piso_idiosincratico(q),
            "tasa_base_up": round(float((grande["gap_pct"] > 0).mean()), 4),
            "frac_llamados_baja": round(float((grande["apertura_estimada_pct"] < 0).mean()), 4),
            "acierto_gap": round(float(grande["acierto_gap"].mean()), 4),
            "acierto_sesion": round(float(grande["acierto_direccion"].mean()), 4)}

    q0, v0 = gens[0.0]
    q9, v9 = gens[0.09]
    q65, v65 = gens[0.065]
    res["A1_cobertura"] = {"delta_0": cobertura(q0, v0, len(base.tamanos)),
                           "delta_9pp": cobertura(q9, v9, len(base.tamanos))}
    def _vivo(q):
        qq = pr.Parametros(**{**q.__dict__}); qq.tamanos = tamanos_vivo; return qq
    res["A2_celdas"] = {"delta_0": celdas(_vivo(q0), fechas_reales),
                        "delta_6.5pp": celdas(_vivo(q65), fechas_reales, n_rep=N_REP_CELDAS_ALT, semilla=SEMILLA + 65),
                        "delta_9pp": celdas(_vivo(q9), fechas_reales, n_rep=N_REP_CELDAS_ALT, semilla=SEMILLA + 90)}
    a2 = res["A2_celdas"]
    res["A2_celdas"]["cociente_verosimilitud_cero_de_192_nula_vs_9pp"] = round(
        a2["delta_0"]["p_cero_de_192"] / max(a2["delta_9pp"]["p_cero_de_192"], 1e-9), 2)
    res["A2_celdas_bajo_nula"] = a2["delta_0"]          # compatibilidad v1
    res["A3_dsr_bajo_nula"] = {f"N{N}_T{T}": dsr_bajo_nula(N, T)
                               for N, T in ((N_INTENTOS_REGISTRO, 518), (int(N_INTENTOS_51), 518),
                                            (int(N_INTENTOS_51), 250), (9, 518), (9, 30))}
    res["A4_potencia"] = {}
    for objetivo in DELTAS:
        q, verdad = gens[objetivo]
        res["A4_potencia"][str(objetivo)] = {
            "verdad_pp": round(100 * verdad, 2),
            "por_horizonte": [{**potencia(q, D),
                               "normal_cerrada_con_sd_real": potencia_normal_cerrada(objetivo, D, n_medio, sd_suma_dia)}
                              for D in HORIZONTES]}
    try:
        with open(os.path.join(DIR_RESULTADOS, "horizonte.json")) as f:
            h = json.load(f)
        res["referencia_horizonte"] = {str(x["dias"]): {k: v for k, v in x.items() if k.startswith("potencia")}
                                       for x in h["simulacion"]}
    except Exception as exc:  # pragma: no cover
        res["referencia_horizonte"] = {"error": str(exc)}
    res["A4_comparacion_pareada"] = comparar_con_horizonte(res["A4_potencia"], res["referencia_horizonte"])
    res["A5_sensibilidad"] = sensibilidad(q0, base)

    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(os.path.join(DIR_RESULTADOS, "calibracion_instrumento.json"), "w") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "calibracion_instrumento.md"), "w") as f:
        f.write(informe(res))
    return res


def informe(r: dict) -> str:
    c = r["calibracion_leida_de_la_maquina"]
    L = ["# El instrumento contra un patrón conocido — Frente A v2 (PROPUESTA, octava corrida)", "",
         f"> {r['etiqueta']}. Generado {r['generado_en_utc']}. Pre-registro: `GEMELO/preregistro/frente_A.md`.",
         "> **Versión 2, reescrita el 2-sep-2026 después del dictamen del `estadistico-adversario`** sobre la",
         "> versión 1 (NO SOSTIENE tal como estaba escrita): semilla de bootstrap por réplica, cuatro estimadores",
         "> de IC, matriz bajo la alternativa, DSR en las dos unidades con tamaño teórico, comparación pareada",
         "> con `horizonte.md`, y la sensibilidad a ν, c y a la dependencia entre días que el pre-registro",
         "> prometía y la v1 no entregó.", "",
         f"**Ancla de calibración:** {c['advertencia_procedencia']}: n = {c['n']} filas en {c['dias']} días,",
         f"ICC {c['icc_real']}, DEFF {c['deff_real']}, n efectivo {c['n_efectivo_real']}. sd de la suma por día",
         f"{c['sd_suma_por_dia_real']}, n̄ {c['n_medio_por_dia_real']}. Registro de intentos {c['registro_intentos']}",
         f"(N del 5.1: {c['N_51']}).", "",
         "## Generadores (verdad medida 8 veces a 200.000 días, con intervalo)", "",
         "| δ objetivo | b | c | verdad δ (pp) | IC95 verdad | ICC objetivo | ICC logrado | fuera de tol. 0,005 |",
         "|---|---|---|---|---|---|---|---|"]
    for k, v in r["generadores"].items():
        L.append(f"| {k} | {v['b']} | {v['c']} | **{v['verdad_delta_pp']}** | {v['ic95_pp']} | {v['icc_objetivo']} | "
                 f"{v['icc_sim']} | {'**SÍ**' if v['icc_fuera_de_tolerancia_0005'] else 'no'} |")
    L += ["", "**Piso idiosincrático (30% de σ):** en los tickers marcados la parte común β²(b²·esc² + c²) excede",
          "la σ total sellada y el piso ata: la sd simulada del gap queda por ENCIMA de la real e **infla la",
          "dependencia intra-día simulada** (dirección del sesgo: hace ver el estimador de clúster más necesario",
          "de lo que los datos justifican).", "",
          "| generador | ticker | σ sellada | √común | piso ata | sd simulada | exceso |", "|---|---|---|---|---|---|---|"]
    for k, v in r["generadores"].items():
        for f in v["piso_idiosincratico"]:
            if f["piso_ata"] or k == "0.0":
                L.append(f"| {k} | {f['ticker']} | {f['sigma_sellada']} | {f['raiz_comun']} | {'**SÍ**' if f['piso_ata'] else 'no'} | {f['sd_gap_simulada']} | {f['exceso_pct']}% |")
    a1 = r["A1_cobertura"]
    def _crit(v):
        return v["cobertura_percentil"] < 0.93 and v["ic95_percentil"][1] < 0.95
    cumple = {k: _crit(v) for k, v in a1.items()}
    L += ["", "## A1 · Cobertura del IC95 (semilla de bootstrap por réplica)", "",
          "**Criterio de refutación congelado en el pre-registro:** «cobertura del IC de día < 93% con IC que",
          "excluya 95%» refuta la hipótesis de que el instrumento de clúster está calibrado. Evaluado sobre el",
          "estimador percentil, COMPUTADO celda a celda (no afirmado): " +
          "; ".join(f"δ = {v['verdad_pp']} pp → cobertura {v['cobertura_percentil']} {v['ic95_percentil']}: "
                    f"{'SE CUMPLE (refutada)' if cumple[k] else 'NO se cumple literalmente (cobertura ≥ 0,93 aunque el IC excluye 0,95)'}"
                    for k, v in a1.items()) + ".",
          "El adversario, con otro flujo de réplicas, midió 0,9271/0,9275 y el criterio SÍ se cumplía. **Un criterio",
          "cuya decisión cambia con la semilla al tercer decimal es un criterio en el filo, y se dice así.** Lo que",
          "no depende de la semilla: el percentil sub-cubre (IC que excluye 0,95 en las dos celdas y en las dos",
          "mediciones) y la t de clúster con gl = k−1 cubre ~0,95. La corrección es cambiar el estimador; la",
          "elección del estimador DESPUÉS de ver la cobertura es un grado de libertad que se declara como eje",
          "(`bifurcaciones.NO_EJES`).", "",
          "| verdad δ | réplicas | percentil | IC95 | básico | IC95 | **t de clúster** | IC95 | iid filas | IC95 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in a1.items():
        L.append(f"| {v['verdad_pp']} pp | {v['n_rep']} | {v['cobertura_percentil']} | {v['ic95_percentil']} | "
                 f"{v['cobertura_basico']} | {v['ic95_basico']} | **{v['cobertura_t_cluster']}** | {v['ic95_t_cluster']} | "
                 f"**{v['cobertura_iid']}** | {v['ic95_iid']} |")
    L += ["", "Anchos medios (pp): " + "; ".join(
        f"δ={v['verdad_pp']}: percentil {v['ancho_medio_percentil_pp']}, t de clúster {v['ancho_medio_t_cluster_pp']}, iid {v['ancho_medio_iid_pp']}"
        for v in a1.values()), "",
          "Percentil-t: medido por el adversario (0,9335), no arregla; BCa: no probado.", ""]
    a2 = r["A2_celdas"]
    L += ["## A2 · Las 192 celdas bajo la nula Y bajo la alternativa", "",
          "| verdad | réplicas | media de celdas p<0,05 | tasa por celda [IC sobre réplicas] | **P(0 de 192)** | IC95 | P(≥1) |",
          "|---|---|---|---|---|---|---|"]
    for k in ("delta_0", "delta_6.5pp", "delta_9pp"):
        v = a2[k]
        L.append(f"| {k} | {v['n_rep']} | {v['media_celdas_con_p_menor_005']} | {v['tasa_media_por_celda']} "
                 f"{v['ic95_tasa_por_celda_sobre_replicas']} | **{v['p_cero_de_192']}** | {v['ic95_cero_de_192']} | {v['p_al_menos_una']} |")
    L += ["", f"**La frase que sobrevive:** «0 de 192» es prácticamente no informativo: la nula lo produce el "
          f"{100*a2['delta_0']['p_cero_de_192']:.1f}% de las veces y una ventaja verdadera de ~9 pp el "
          f"{100*a2['delta_9pp']['p_cero_de_192']:.1f}% — cociente de verosimilitudes "
          f"**{a2['cociente_verosimilitud_cero_de_192_nula_vs_9pp']}**. La v1 decía «la mitad de las veces»: era falsa.",
          "Salvedad: es la nula INTERCAMBIABLE (qué tickers faltan y qué fechas caen en R2 se sortean), no la",
          "dependencia real entre ejes y datos.", ""]
    L += ["## A3 · DSR bajo la nula: las dos unidades", "",
          "`anualizado` = el defecto (Sharpe·√252 con n = T, lo que los dos llamadores hacían hasta el 2-sep);",
          "`por período` = la corrección. La regla V5 (DSR de al menos 0,95) no tiene tamaño 5%: su tamaño teórico gaussiano",
          "es P(max_N Z > E[max_N Z] + 1,645). La elección de V es de primer orden a N chico.", "",
          "| N | T | anualizado (defecto) | IC95 | **por período, V incl. ganador** | IC95 | V sin ganador | V = 1/T | tamaño teórico |",
          "|---|---|---|---|---|---|---|---|---|"]
    for v in r["A3_dsr_bajo_nula"].values():
        L.append(f"| {v['N_intentos']} | {v['T_dias']} | {v['p_dsr_mayor_095_anualizado']} | {v['ic95_anualizado']} | "
                 f"**{v['p_dsr_mayor_095_por_periodo']}** | {v['ic95_por_periodo']} | {v['p_dsr_mayor_095_por_periodo_V_sin_ganador']} | "
                 f"{v['p_dsr_mayor_095_por_periodo_V_teorica']} | {v['tamano_teorico_gaussiano']['tamano']} |")
    cp = r["A4_comparacion_pareada"]
    L += ["", "## A4 · Potencia: simulador, `horizonte.md` y una tercera ruta cerrada", "",
          "| δ verdad | días | simulador | IC95 | normal cerrada (sd real) | horizonte.md |", "|---|---|---|---|---|---|"]
    ref = r["referencia_horizonte"]
    for obj, bloque in r["A4_potencia"].items():
        clave = {"0.05": "potencia_5.0pp", "0.065": "potencia_6.5pp", "0.09": "potencia_9.0pp"}[obj]
        for f in bloque["por_horizonte"]:
            L.append(f"| {bloque['verdad_pp']} | {f['n_dias']} | {f['potencia']} | {f['ic95']} | {f['normal_cerrada_con_sd_real']} | "
                     f"{ref.get(str(f['n_dias']), {}).get(clave, '—')} |")
    if cp.get("pares"):
        L += ["", f"**Comparación pareada** ({cp['pares']} celdas): simulador por debajo en {cp['simulador_por_debajo']}, por encima en "
              f"{cp['simulador_por_encima']}; McNemar exacto p = {cp['mcnemar_exacto_p']}; diferencia media horizonte − simulador "
              f"**{cp['diferencia_media_horizonte_menos_simulador_pp']} pp** [{cp['ic95_pp'][0]}, {cp['ic95_pp'][1]}].",
              "**No son dos rutas independientes:** la potencia del test de signo por día es función de un escalar",
              "(δ·n̄·√D / sd de la suma por día) al que el simulador fue calibrado; la normal cerrada lo reproduce con",
              "sólo dos números reales. La brecha sistemática tiene causa: `horizonte.potencia_simulada` suma un δ",
              "CONSTANTE a cada fila; el simulador entrega δ por el canal de información (concentrado en los días de",
              "|S| grande), que es lo fiel. **La tabla de potencia de `horizonte.md`, las fechas de horizonte derivadas",
              "y la «potencia 0,36 [0,34, 0,37]» del 25-oct son OPTIMISTAS** por la diferencia medida arriba."]
    s5 = r["A5_sensibilidad"]
    L += ["", "## A5 · Sensibilidad del DGP (lo que el pre-registro prometió)", "",
          "**Seis puntos del DGP que la v1 no declaraba:** (1) el shock U entra por las MISMAS β que S — la covarianza",
          "intra-día es de rango 1 con las cargas que el campeón conoce: la forma más benigna de clúster inexplicado;",
          "(2) no había dependencia ENTRE días (S, U, ε iid en d) — la intercambiabilidad exacta que el bootstrap de",
          "día y la permutación necesitan; medida abajo con AR(1); (3) la β verdadera es la que usa el campeón, sin",
          "error de estimación (la rodante real de 120 sesiones es autocorrelada); (4) el piso del 30% ata en los",
          "tickers de la tabla de arriba; (5) el ICC logrado queda fuera de la tolerancia 0,005 de `calibrar_c` en",
          "los generadores marcados (la bisección se detiene en el ruido de Monte Carlo); (6) el pre-registro decía",
          "«c y la escala de S ajustados al ICC y al SE de día»: el código calibra SÓLO c al ICC; la escala del SOX",
          "se lee del sello y el SE de día no se persigue.", "",
          "**Puntos que siguen sin intervalo, declarados:** `icc_sim` (medido una vez a 80.000 días) y `escala_sox`, que se lee",
          "del sello sobre las fechas con `sox_usado_pct` (una fracción de las 35: ~15% de error estándar) y entra al DGP como punto.", "",
          "| ν | verdad (pp) | percentil | t de clúster | iid |", "|---|---|---|---|---|"]
    for v in s5["nu"]:
        L.append(f"| {v['nu']} | {v['verdad_delta_pp']} | {v['cobertura_percentil']} {v['ic95_percentil']} | "
                 f"{v['cobertura_t_cluster']} {v['ic95_t_cluster']} | {v['cobertura_iid']} |")
    L += ["", "| factor de c | c | ICC simulado | verdad (pp) | percentil | t de clúster |", "|---|---|---|---|---|---|"]
    for v in s5["c"]:
        L.append(f"| {v['factor_c']} | {v['c']} | {v['icc_sim']} | {v['verdad_delta_pp']} | {v['cobertura_percentil']} | {v['cobertura_t_cluster']} |")
    L += ["", "**Dependencia entre días (AR(1) en S y U; AC1 real −0,13 ± 0,17, ρ = 0,2 es compatible):**", "",
          "| ρ | verdad (pp) | percentil | t de clúster | tamaño de la permutación de día | IC95 |", "|---|---|---|---|---|---|"]
    for v in s5["rho"]:
        L.append(f"| {v['rho']} | {v['verdad_delta_pp']} | {v['cobertura_percentil']} | {v['cobertura_t_cluster']} | "
                 f"**{v['tamano_permutacion_dia']}** | {v['ic95_tamano_permutacion']} |")
    L += ["", "**Lectura:** el simulador publicado no podía detectar el modo de fallo que los datos dejan abierto",
          "(dependencia entre días) porque asumía que no existe. Con ρ > 0 el tamaño de la permutación de día sube por",
          "encima de 0,05 y la cobertura cae: es un riesgo DECLARADO del instrumento, no resuelto.", "",
          "## Lo que este frente SÍ sostiene", "",
          "- El estimador iid de filas cubre ~0,70 donde promete 0,95: inservible, sin margen.",
          "- El defecto de unidades del PSR/DSR es real, verificado contra el código y la teoría; la corrección es",
          "  aritméticamente correcta y su tamaño por período coincide con el teórico.",
          "- El δ logrado se re-mide a 200.000 días en vez de suponerse igual al objetivo.",
          "- El percentil de día con k = 35 sub-cubre ~2,3 pp; la t de clúster con gl = k−1 corrige.", ""]
    return "\n".join(L)


def solo_a3() -> dict:
    """Recomputa SÓLO A3 (rápido) y regenera el informe: la rama anualizada
    pasó de un supuesto a un cómputo (guardián O2)."""
    with open(os.path.join(DIR_RESULTADOS, "calibracion_instrumento.json")) as f:
        r = json.load(f)
    c = r["calibracion_leida_de_la_maquina"]
    r["A3_dsr_bajo_nula"] = {f"N{N}_T{T}": dsr_bajo_nula(N, T)
                             for N, T in ((int(c["registro_intentos"]), 518), (int(c["N_51"]), 518),
                                          (int(c["N_51"]), 250), (9, 518), (9, 30))}
    r["A3_nota"] = "A3 recomputado el 2-sep 15:15 con la rama anualizada COMPUTADA (sin la guarda de unidad); el resto del JSON es de la corrida de las 14:12"
    with open(os.path.join(DIR_RESULTADOS, "calibracion_instrumento.json"), "w") as f:
        json.dump(r, f, indent=1, ensure_ascii=False, default=str)
    return solo_informe()


def solo_informe() -> dict:
    """Regenera el .md desde el .json sellado (recomputa sólo la comparación
    pareada con horizonte.md, que es aritmética sobre cifras ya guardadas)."""
    with open(os.path.join(DIR_RESULTADOS, "calibracion_instrumento.json")) as f:
        r = json.load(f)
    r["A4_comparacion_pareada"] = comparar_con_horizonte(r["A4_potencia"], r["referencia_horizonte"])
    with open(os.path.join(DIR_RESULTADOS, "calibracion_instrumento.json"), "w") as f:
        json.dump(r, f, indent=1, ensure_ascii=False, default=str)
    with open(os.path.join(DIR_RESULTADOS, "calibracion_instrumento.md"), "w") as f:
        f.write(informe(r))
    return r


if __name__ == "__main__":
    if "--solo-a3" in sys.argv:
        solo_a3(); sys.exit(0)
    if "--solo-informe" in sys.argv:
        r = solo_informe()
        print(json.dumps(r["A4_comparacion_pareada"], indent=1)[:1500]); sys.exit(0)
    r = main()
    print(json.dumps({k: r[k] for k in ("generadores", "A1_cobertura", "A3_dsr_bajo_nula", "A4_comparacion_pareada")},
                     indent=1, default=str)[:6000])
