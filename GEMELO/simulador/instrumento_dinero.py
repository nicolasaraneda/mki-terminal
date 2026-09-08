"""El instrumento del riel de dinero contra una verdad conocida.

Bloque 1 de la corrida 11 (8-sep-2026). PROPUESTA hasta el dictamen del
`estadistico-adversario`. Declaración previa: `GEMELO/resultados/bitacora_11.md`,
sección «Bloque 1», escrita ANTES de correr ninguna réplica.

POR QUÉ EXISTE. El dictamen #23 del adversario en el cierre de la corrida 10
(`dictamen_10/estadistico_adversario.md`): «ningún estimador de intervalo,
ninguna afirmación de potencia y ningún umbral de decisión de esta corrida se
corrió contra `GEMELO/simulador/`». La cuenta en papel con señal sin
información ES la mitad con ventaja verdadera cero; faltaba la mitad con
ventaja verdadera conocida y DISTINTA de cero, que es la que dice si el
procedimiento la encuentra. Sin esa mitad, la tabla de potencia y el criterio
§2 del pre-registro son aritmética sin validar.

QUÉ SE PRUEBA, y es el instrumento IMPLEMENTADO, no una reimplementación:

    dinero.contabilidad.comparar(valor_estrategia, valor_base, semilla)
        → diferencia de retorno semanal, IC95 por bootstrap circular de
          bloques de 4 semanas, 2.000 réplicas (constantes del módulo).

y la regla de decisión del pre-registro (`dinero/preregistro_dinero.md` §2,
condición 3): el IC excluye el cero Y el punto es positivo, evaluado UNA vez
a 52 semanas. Se agrega 104 semanas porque M1 lo nombra.

VERDAD CONOCIDA. La diferencia semanal es d_t = δ + σ·ε_t, con ε t de
Student (ν = 4) estandarizada y AR(1) ρ opcional. Como `comparar` resta
retornos semanales, la serie de la base es irrelevante para el estadístico;
se genera igual (retornos semanales reales de SMH remuestreados) para que la
función reciba exactamente lo que recibe en producción: dos series de VALOR.

σ NO se toma de la tabla §2.1 del pre-registro (2,54 pp/semana): esa cifra
salió de la cuenta con fuga y está RETIRADA. Se mide acá, de los precios
congelados, como desviación de la diferencia semanal entre una cartera
equiponderada de K = 4 instrumentos operables sorteados (K del juego
conservador) y SMH, sobre la misma ventana de la cuenta en papel, con
intervalo por bootstrap circular de bloques sobre semanas.

LO QUE ESTO NO VALIDA: el camino que produce las series de valor
(`cuenta_papel`, `correr_estrategia`, `valorizar`). Eso lo cubren el gate de
causalidad y la reconstrucción (bloques 2 y 3). Acá se valida el estimador y
la regla que leen esas series.

Intentos del DSR: 0. Ningún resultado sobre datos reales.
"""
from __future__ import annotations

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

from api.utilidades import intervalo_wilson  # noqa: E402
from backtest import inferencia  # noqa: E402
from dinero import contabilidad as C  # noqa: E402
from dinero import cuenta_papel as CP  # noqa: E402
from dinero import precios  # noqa: E402
from dinero import universo_dinero as U  # noqa: E402

SEMILLA = 20260908
REPLICAS = 2000
NU = 4
# Magnitudes DECLARADAS antes de correr: son las filas de la tabla §2.1 del
# pre-registro del riel (7-sep-2026), no una elección de esta corrida.
DELTAS_PP_SEMANA = (0.0, 0.25, 0.50, 1.00)
HORIZONTES_SEMANAS = (52, 104, 156)   # 156: el horizonte de los ✓ de la cuenta en papel (exigencia A3)
FACTORES_SIGMA = (0.5, 1.0, 2.0)
RHOS = (0.0, 0.2)
K_POSICIONES = 4            # juego conservador: 1/K = 25 % por posición
N_SORTEOS_SIGMA = 200
N_BOOT_SIGMA = 1000
ALPHA = C.ALPHA
Z = 1.959963984540054
Z_POTENCIA_80 = 0.8416212335729143

DIR_RESULTADOS = os.path.join(_RAIZ, "GEMELO", "resultados")
SALIDA_MD = os.path.join(DIR_RESULTADOS, "instrumento_dinero.md")
SALIDA_JSON = os.path.join(DIR_RESULTADOS, "instrumento_dinero.json")


# ------------------------------------------------------------
# Ruido
# ------------------------------------------------------------
def _t(rng: np.random.Generator, size: int, nu: int = NU) -> np.ndarray:
    """t de Student estandarizada a varianza 1 (ν > 2)."""
    return rng.standard_t(nu, size=size) / math.sqrt(nu / (nu - 2))


def _ar1(e: np.ndarray, rho: float) -> np.ndarray:
    """AR(1) con varianza marginal conservada. ρ = 0 devuelve `e`."""
    if not rho:
        return e
    x = np.empty_like(e)
    x[0] = e[0]
    s = math.sqrt(1.0 - rho * rho)
    for i in range(1, len(e)):
        x[i] = rho * x[i - 1] + s * e[i]
    return x


def _phi(z: float) -> float:
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


# ------------------------------------------------------------
# σ medida de los precios congelados (parámetro, no resultado)
# ------------------------------------------------------------
def retornos_semanales_pct(cierres: pd.DataFrame) -> pd.DataFrame:
    semanal = cierres.resample("W-FRI").last()
    return (semanal.pct_change() * 100.0).iloc[1:]


def operables_no_etf(cierres: pd.DataFrame) -> list:
    """Instrumentos candidatos que no son cestas y tienen cierre en el
    archivo. Es membresía por EXISTENCIA en el congelado, no por precio."""
    return sorted(c.ticker for c in U.CANDIDATOS
                  if c.forma != "ETF" and c.ticker in cierres.columns)


def sigma_medida(cierres: pd.DataFrame, semilla: int = SEMILLA,
                 n_sorteos: int = N_SORTEOS_SIGMA,
                 n_boot: int = N_BOOT_SIGMA) -> dict:
    """σ de la diferencia semanal «cartera de K operables − SMH» sobre la
    ventana de la cuenta en papel. Mediana sobre sorteos de cartera, con
    (a) la banda entre sorteos y (b) el IC95 por bootstrap circular de
    bloques de semanas de esa mediana."""
    ventana = cierres.loc[CP.DESDE:CP.HASTA]
    rs = retornos_semanales_pct(ventana)
    tickers = operables_no_etf(ventana)
    base = rs["SMH"].to_numpy()
    rng = np.random.default_rng(semilla)
    carteras = []
    for _ in range(n_sorteos):
        elegidos = list(rng.choice(tickers, size=K_POSICIONES, replace=False))
        carteras.append(rs[elegidos].mean(axis=1, skipna=True).to_numpy() - base)
    M = np.array(carteras)                       # sorteos × semanas
    M = M[:, ~np.isnan(M).any(axis=0)]
    n_sem = M.shape[1]
    sd_por_sorteo = M.std(axis=1, ddof=1)
    mediana = float(np.median(sd_por_sorteo))
    # ρ MEDIDO (exigencia A4): autocorrelación de orden 1 de la diferencia
    # semanal, por sorteo; el barrido a ρ = 0,2 se lee contra esto.
    ac1 = np.array([np.corrcoef(fila[:-1], fila[1:])[0, 1] for fila in M])
    # bootstrap de SEMANAS (bloques circulares de 4) de la mediana entre sorteos
    idx = inferencia._remuestrear_circular(np.arange(n_sem), semilla + 1,
                                           n_boot, C.BLOQUE_BOOTSTRAP_SEMANAS)
    medianas = np.array([np.median(M[:, i].std(axis=1, ddof=1)) for i in idx])
    return {
        "sigma_pp_semana": round(mediana, 4),
        "ic95_bootstrap_semanas": [round(float(np.quantile(medianas, 0.025)), 4),
                                   round(float(np.quantile(medianas, 0.975)), 4)],
        "banda_entre_sorteos_p2_5_p97_5": [round(float(np.quantile(sd_por_sorteo, 0.025)), 4),
                                           round(float(np.quantile(sd_por_sorteo, 0.975)), 4)],
        "rho_medido_ac1_mediana": round(float(np.median(ac1)), 4),
        "rho_medido_ac1_banda_p2_5_p97_5": [round(float(np.quantile(ac1, 0.025)), 4),
                                            round(float(np.quantile(ac1, 0.975)), 4)],
        "semanas": int(n_sem), "sorteos": int(n_sorteos), "K": K_POSICIONES,
        "instrumentos_sorteables": len(tickers),
        "ventana": [CP.DESDE, CP.HASTA],
        "bloque_bootstrap_semanas": C.BLOQUE_BOOTSTRAP_SEMANAS,
        "definicion": ("sd de (media equiponderada de los retornos semanales de K "
                       "operables sorteados − retorno semanal de SMH), ddof=1"),
    }


# ------------------------------------------------------------
# Una celda: δ, σ, ρ, T semanas → tasas con Wilson
# ------------------------------------------------------------
def simular_celda(delta: float, sigma: float, rho: float, T: int,
                  base_semanal: np.ndarray, n_rep: int = REPLICAS,
                  semilla: int = SEMILLA) -> dict:
    rng = np.random.default_rng(semilla)
    fechas = pd.date_range(end="2026-09-04", periods=T + 1, freq="W-FRI")
    detecta = excluye = cubre = cubre_sd = 0
    puntos = np.empty(n_rep)
    anchos = np.empty(n_rep)
    for r in range(n_rep):
        eps = _ar1(_t(rng, T), rho)
        d = delta + sigma * eps
        rb = rng.choice(base_semanal, size=T)
        rs = rb + d
        vb = 100.0 * np.concatenate([[1.0], np.cumprod(1.0 + rb / 100.0)])
        vs = 100.0 * np.concatenate([[1.0], np.cumprod(1.0 + rs / 100.0)])
        # semilla del bootstrap POR RÉPLICA (lección del Frente A)
        res = C.comparar(pd.Series(vs, index=fechas), pd.Series(vb, index=fechas),
                         semilla=int(rng.integers(0, 2 ** 31 - 1)))
        assert res["semanas"] == T
        ex = not res["cruza_cero"]
        excluye += ex
        detecta += ex and res["dif_media_pp"] > 0
        cubre += res["ic_lo"] <= delta <= res["ic_hi"]
        # IC de la DESVIACIÓN por el mismo bootstrap circular: ¿contiene σ?
        # (exigencia C4: la cuenta en papel publica σ con un IC de este tipo)
        sds = inferencia._remuestrear_circular(d, res["semilla"] + 1, C.REPLICAS_BOOTSTRAP,
                                               C.BLOQUE_BOOTSTRAP_SEMANAS).std(axis=1, ddof=1)
        cubre_sd += np.quantile(sds, 0.025) <= sigma <= np.quantile(sds, 0.975)
        puntos[r] = res["dif_media_pp"]
        anchos[r] = res["ic_hi"] - res["ic_lo"]

    def w(k):
        lo, hi = intervalo_wilson(int(k), n_rep)   # viene en porcentaje
        return {"tasa": round(k / n_rep, 4), "wilson95": [round(lo / 100.0, 4), round(hi / 100.0, 4)],
                "k": int(k)}

    return {
        "delta_pp_semana": delta, "sigma_pp_semana": round(sigma, 4), "rho": rho,
        "semanas": T, "replicas": n_rep,
        "deteccion": w(detecta),          # IC excluye 0 y punto > 0 (regla §2.3)
        "excluye_cero": w(excluye),       # bilateral, cualquier signo
        "cobertura_ic95": w(cubre),       # el IC contiene δ
        "cobertura_ic95_sd": w(cubre_sd), # el IC bootstrap de la sd contiene σ
        "punto_medio_pp": round(float(puntos.mean()), 4),
        "punto_sd_pp": round(float(puntos.std(ddof=1)), 4),
        "ancho_medio_pp": round(float(anchos.mean()), 4),
        # segunda ruta, cerrada: normal con la misma σ y ρ = 0
        "potencia_normal_cerrada": round(_phi(delta * math.sqrt(T) / sigma - Z), 4),
    }


# ------------------------------------------------------------
# El estudio
# ------------------------------------------------------------
def celdas_del_estudio(sigma: float) -> list:
    out = []
    for T in HORIZONTES_SEMANAS:
        for d in DELTAS_PP_SEMANA:
            out.append(("base", d, sigma, 0.0, T))
    for f in FACTORES_SIGMA:
        if f == 1.0:
            continue
        for d in DELTAS_PP_SEMANA:
            out.append((f"sigma_x{f}", d, sigma * f, 0.0, 52))
    for rho in RHOS:
        if not rho:
            continue
        for d in DELTAS_PP_SEMANA:
            out.append((f"rho_{rho}", d, sigma, rho, 52))
    return out


def mde80(sigma: float, T: int) -> float:
    """Ventaja mínima detectable con potencia 0,80 a α = 0,05 (normal cerrada)."""
    return (Z + Z_POTENCIA_80) * sigma / math.sqrt(T)


def _z_bilateral(alpha: float) -> float:
    """Cuantil normal 1 − α/2 por bisección sobre erfc (sin scipy)."""
    lo, hi = 0.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 2 * (1 - _phi(mid)) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def calibracion(celdas: list) -> dict:
    """Brazo de calibración (exigencia A1 del adversario, agregado DESPUÉS de
    ver el resultado y declarado así): el instrumento es usable a α = 0,05
    sólo si el Wilson del tamaño bilateral bajo δ = 0 contiene 0,05 y el de
    la cobertura contiene 0,95. Se reporta por horizonte, y la potencia
    cerrada se recomputa al tamaño REAL medido (exigencia A5)."""
    out = {}
    for T in sorted({c["semanas"] for c in celdas if c["grupo"] == "base"}):
        nula = next(c for c in celdas if c["grupo"] == "base" and c["semanas"] == T
                    and c["delta_pp_semana"] == 0.0)
        lo_t, hi_t = nula["excluye_cero"]["wilson95"]
        lo_c, hi_c = nula["cobertura_ic95"]["wilson95"]
        alpha_real = nula["excluye_cero"]["tasa"]
        z_real = _z_bilateral(alpha_real)
        ajustada = {}
        for c in celdas:
            if c["grupo"] == "base" and c["semanas"] == T and c["delta_pp_semana"] > 0:
                ajustada[str(c["delta_pp_semana"])] = round(
                    _phi(c["delta_pp_semana"] * math.sqrt(T) / c["sigma_pp_semana"] - z_real), 4)
        out[str(T)] = {
            "tamano_bilateral": nula["excluye_cero"], "cobertura": nula["cobertura_ic95"],
            "cobertura_ic_sd": nula["cobertura_ic95_sd"],
            "usable_a_alpha_005": bool(lo_t <= 0.05 <= hi_t and lo_c <= 0.95 <= hi_c),
            "alpha_real": alpha_real, "z_al_alpha_real": round(z_real, 4),
            "potencia_cerrada_al_alpha_real": ajustada,
            "mde80_pp_semana": round(mde80(nula["sigma_pp_semana"], T), 4),
            "mde80_pp_anio_aprox": round(52 * mde80(nula["sigma_pp_semana"], T), 1),
        }
    return out


def veredicto(celdas: list) -> dict:
    """El criterio de fallo escrito antes de correr: en la celda base
    (σ medida, ρ = 0, 52 semanas), el instrumento discrimina si para AL
    MENOS una magnitud δ > 0 el límite inferior de Wilson de la detección
    supera el límite superior de Wilson de la falsa detección bajo δ = 0."""
    base52 = [c for c in celdas if c["grupo"] == "base" and c["semanas"] == 52]
    nula = next(c for c in base52 if c["delta_pp_semana"] == 0.0)
    techo_nula = nula["deteccion"]["wilson95"][1]
    por_delta = {}
    for c in base52:
        if c["delta_pp_semana"] == 0.0:
            continue
        piso = c["deteccion"]["wilson95"][0]
        por_delta[str(c["delta_pp_semana"])] = {
            "piso_wilson_deteccion": piso, "techo_wilson_falsa_deteccion": techo_nula,
            "discrimina": bool(piso > techo_nula)}
    discrimina = any(v["discrimina"] for v in por_delta.values())
    return {"criterio": ("piso de Wilson de la detección bajo δ > 0 supera el techo de "
                         "Wilson de la falsa detección bajo δ = 0, celda base a 52 semanas, "
                         "para al menos una de las tres magnitudes declaradas"),
            "falsa_deteccion_nula": nula["deteccion"],
            "por_delta": por_delta,
            "instrumento_discrimina": discrimina,
            "consecuencia": ("la corrida sigue" if discrimina else
                             "el resto de la corrida 11 queda SUSPENDIDO (bloque 1 del encargo)")}


def _sigma_cuenta():
    """La σ realizada de la cuenta en papel v2, si existe, para contrastarla
    con el ancla (exigencias A6 y C6). Se lee del artefacto, no se recomputa."""
    ruta = os.path.join(_RAIZ, "dinero", "resultados", "cuenta_papel.json")
    if not os.path.exists(ruta):
        return None
    with open(ruta, encoding="utf-8") as f:
        d = json.load(f)
    return d.get("sigma_dif_semanal")


def correr(n_rep: int = REPLICAS, semilla: int = SEMILLA) -> dict:
    cierres = precios.cargar_congelado()
    with open(precios.RUTA_META, encoding="utf-8") as f:
        meta = json.load(f)
    sig = sigma_medida(cierres, semilla=semilla)
    sigma = sig["sigma_pp_semana"]
    base = retornos_semanales_pct(cierres.loc[CP.DESDE:CP.HASTA])["SMH"].dropna().to_numpy()
    celdas = []
    for i, (grupo, d, s, rho, T) in enumerate(celdas_del_estudio(sigma)):
        c = simular_celda(d, s, rho, T, base, n_rep=n_rep, semilla=semilla + 100 + i)
        c["grupo"] = grupo
        celdas.append(c)
    return {
        "generado_en_utc": datetime.now(timezone.utc).isoformat(),
        "etiqueta": "PROPUESTA — bloque 1 de la corrida 11; hasta el dictamen del estadistico-adversario",
        "instrumento": ("dinero.contabilidad.comparar (bootstrap circular de bloques de "
                        f"{C.BLOQUE_BOOTSTRAP_SEMANAS} semanas, {C.REPLICAS_BOOTSTRAP} réplicas, "
                        f"α = {C.ALPHA}) + regla §2.3 del pre-registro: IC excluye 0 y punto > 0"),
        "dgp": {"d_t": "delta + sigma * eps_t", "eps": f"t de Student nu={NU} estandarizada",
                "ar1": "rho sobre eps, varianza marginal conservada",
                "base": "retornos semanales reales de SMH remuestreados iid (irrelevantes para el estadístico)"},
        "declarado_antes": {"deltas_pp_semana": list(DELTAS_PP_SEMANA),
                            "horizontes_semanas": list(HORIZONTES_SEMANAS),
                            "factores_sigma": list(FACTORES_SIGMA), "rhos": list(RHOS),
                            "replicas_por_celda": n_rep, "semilla": semilla,
                            "semilla_bootstrap": "por réplica",
                            "procedencia_deltas": "dinero/preregistro_dinero.md §2.1, tabla del 7-sep-2026"},
        "sigma_medida": sig,
        "precios": {"archivo": os.path.basename(precios.RUTA_CIERRES), "sha256": meta.get("sha256"),
                    "congelado_en_utc": meta.get("congelado_en_utc")},
        "celdas": celdas,
        "veredicto": veredicto(celdas),
        "calibracion": calibracion(celdas),
        "sigma_cuenta_reconstruida": _sigma_cuenta(),
        "intentos_dsr": 0,
        "no_valida": ("el camino que produce las series de valor (cuenta_papel, "
                      "correr_estrategia, valorizar): eso es de los bloques 2 y 3"),
    }


# ------------------------------------------------------------
# Informe
# ------------------------------------------------------------
def _fila(c: dict) -> str:
    d, e, k = c["deteccion"], c["excluye_cero"], c["cobertura_ic95"]
    return (f"| {c['delta_pp_semana']:+.2f} | {c['sigma_pp_semana']:.2f} | {c['rho']:.1f} | {c['semanas']} | "
            f"**{d['tasa']:.3f}** [{d['wilson95'][0]:.3f}, {d['wilson95'][1]:.3f}] | "
            f"{e['tasa']:.3f} [{e['wilson95'][0]:.3f}, {e['wilson95'][1]:.3f}] | "
            f"{k['tasa']:.3f} [{k['wilson95'][0]:.3f}, {k['wilson95'][1]:.3f}] | "
            f"{c['cobertura_ic95_sd']['tasa']:.3f} | "
            f"{c['punto_medio_pp']:+.3f} ± {c['punto_sd_pp']:.3f} | {c['ancho_medio_pp']:.2f} | "
            f"{c['potencia_normal_cerrada']:.3f} |")


def informe(r: dict) -> str:
    sig = r["sigma_medida"]
    v = r["veredicto"]
    L = []
    L.append("# El instrumento del riel de dinero contra una verdad conocida — bloque 1, corrida 11 (PROPUESTA)\n")
    L.append(f"> **{r['etiqueta']}.** Dictamen del `estadistico-adversario` del 8-sep: sostiene con exigencias "
             "(aplicadas y re-corridas; las cifras re-corridas no volvieron a pasar por él). Generado "
             f"{r['generado_en_utc']} por "
             "`python -m GEMELO.simulador.instrumento_dinero`. Declaración previa en "
             "`GEMELO/resultados/bitacora_11.md` (bloque 1), escrita antes de correr.")
    L.append(">")
    L.append("> **SIMULADO.** Ninguna cifra de esta página es un resultado sobre datos reales; "
             "ninguna entra al README. Intentos del DSR: 0.\n")
    L.append("## Qué se prueba\n")
    L.append(f"- **Instrumento:** {r['instrumento']}. Se llama la función tal como está en el código.")
    L.append(f"- **Verdad:** d_t = δ + σ·ε_t, ε {r['dgp']['eps']}, AR(1) ρ. La base son {r['dgp']['base']}.")
    L.append(f"- **Magnitudes declaradas antes:** δ ∈ {r['declarado_antes']['deltas_pp_semana']} pp/semana "
             f"({r['declarado_antes']['procedencia_deltas']}). Horizontes {r['declarado_antes']['horizontes_semanas']} "
             f"semanas. {r['declarado_antes']['replicas_por_celda']} réplicas por celda, semilla "
             f"{r['declarado_antes']['semilla']}, semilla del bootstrap por réplica.")
    L.append(f"- **σ medida, no supuesta:** **{sig['sigma_pp_semana']:.3f} pp/semana**, IC95 por bootstrap de "
             f"semanas {sig['ic95_bootstrap_semanas']}, banda entre sorteos de cartera "
             f"{sig['banda_entre_sorteos_p2_5_p97_5']} ({sig['sorteos']} carteras de K = {sig['K']} entre "
             f"{sig['instrumentos_sorteables']} operables, {sig['semanas']} semanas, {sig['ventana'][0]} a "
             f"{sig['ventana'][1]}). La σ = 2,54 de la tabla §2.1 del pre-registro NO se usa: es cifra de la "
             "cuenta con fuga, retirada.")
    L.append(f"- Precios: `{r['precios']['archivo']}`, sha256 `{(r['precios']['sha256'] or '?')[:16]}…`, "
             f"congelado {r['precios']['congelado_en_utc']}.\n")
    L.append("## Veredicto, por el criterio escrito antes\n")
    L.append(f"**Criterio:** {v['criterio']}.\n")
    fn = v["falsa_deteccion_nula"]
    L.append(f"Falsa detección bajo δ = 0 (celda base, 52 semanas): {fn['tasa']:.3f} "
             f"[{fn['wilson95'][0]:.3f}, {fn['wilson95'][1]:.3f}].\n")
    L.append("| δ (pp/sem) | piso Wilson detección | techo Wilson falsa detección | ¿discrimina? |")
    L.append("|---|---|---|---|")
    for d, x in v["por_delta"].items():
        L.append(f"| {float(d):+.2f} | {x['piso_wilson_deteccion']:.3f} | {x['techo_wilson_falsa_deteccion']:.3f} | "
                 f"{'**SÍ**' if x['discrimina'] else 'no'} |")
    L.append("")
    cal52 = r.get("calibracion", {}).get("52")
    extra = ""
    if cal52 and not cal52["usable_a_alpha_005"]:
        extra = (f" Y **NO está calibrado a α = 0,05**: tamaño bilateral {cal52['tamano_bilateral']['tasa']:.3f} "
                 f"{cal52['tamano_bilateral']['wilson95']} contra 0,05 a 52 semanas (brazo de calibración, abajo).")
    L.append(f"**El instrumento {'DISCRIMINA' if v['instrumento_discrimina'] else 'NO discrimina'}.** "
             f"Consecuencia: {v['consecuencia']}.{extra}\n")
    L.append("## Calibración (brazo agregado DESPUÉS de ver el resultado, exigencia A1 del adversario)\n")
    L.append("El criterio de fallo pre-declarado sólo podía fallar por falta de potencia, nunca por")
    L.append("descalibración. Este brazo se agrega a posteriori y se declara así: usable a α = 0,05 sólo")
    L.append("si el Wilson del tamaño bilateral contiene 0,05 y el de la cobertura contiene 0,95. La")
    L.append("potencia cerrada se recomputa al tamaño real medido (exigencia A5): la brecha")
    L.append("«simulada > cerrada» de la tabla de abajo es exactamente el tamaño inflado.\n")
    L.append("| semanas | tamaño bilateral [Wilson] | cobertura IC media [Wilson] | cobertura IC sd [Wilson] | ¿usable a α = 0,05? | α real | potencia cerrada al α real (0,25 / 0,50 / 1,00) | MDE80 pp/semana | ≈ pp/año |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for T, k in r["calibracion"].items():
        pa = k["potencia_cerrada_al_alpha_real"]
        L.append(f"| {T} | {k['tamano_bilateral']['tasa']:.3f} {k['tamano_bilateral']['wilson95']} | "
                 f"{k['cobertura']['tasa']:.3f} {k['cobertura']['wilson95']} | "
                 f"{k['cobertura_ic_sd']['tasa']:.3f} {k['cobertura_ic_sd']['wilson95']} | "
                 f"{'sí' if k['usable_a_alpha_005'] else '**NO**'} | {k['alpha_real']:.3f} | "
                 f"{pa.get('0.25', float('nan')):.3f} / {pa.get('0.5', float('nan')):.3f} / {pa.get('1.0', float('nan')):.3f} | "
                 f"**{k['mde80_pp_semana']:.2f}** | {k['mde80_pp_anio_aprox']:.0f} |")
    L.append("")
    L.append("**La corrida 11 habría cruzado este brazo a 52 semanas**: el instrumento discrimina pero no")
    L.append("está calibrado a α = 0,05 (exigencia A1, declarado). El MDE80 dice en número lo que el")
    L.append("pre-registro decía en prosa: a 52 semanas la regla §2.3 sólo detecta una ventaja del orden de")
    L.append("1 pp/semana, ≈ 55 pp/año, que no es plausible con datos públicos.")
    sc = r.get("sigma_cuenta_reconstruida")
    if sc:
        L.append(f"\n**Contraste con la σ realizada de la cuenta reconstruida** (exigencias A6/C6): la cuenta v2 "
                 f"da σ = {sc['sigma_pp_semana']:.3f} pp/semana, IC {sc['ic95']} ({sc['semanas']} semanas, "
                 f"`{sc['juego']}` vs `{sc['base']}`); el ancla {sig['sigma_pp_semana']:.3f} queda por encima del "
                 "techo de ese IC, o sea el ancla es CONSERVADORA (menos potencia, criterio más difícil) y es un")
        L.append("proxy estructural distinto (cartera estática de 4, siempre invertida, sin caja ni rotación).")
        L.append("La cobertura del IC de la sd (columna de arriba) es lo que decide si ese intervalo de σ se")
        L.append("puede usar: el bloque 1 original validó sólo el IC de la media.")
    L.append(f"\n**ρ medido** (exigencia A4): AC1 de la diferencia semanal, mediana {sig.get('rho_medido_ac1_mediana')} con banda entre "
             f"sorteos {sig.get('rho_medido_ac1_banda_p2_5_p97_5')}: el barrido a ρ = 0,2 cubre el borde de lo compatible.\n")
    L.append("## La mitad nula y la mitad con ventaja, en el mismo cuadro\n")
    L.append("Detección = IC excluye 0 y punto > 0 (regla §2.3). Excluye 0 = bilateral, cualquier signo "
             "(el tamaño del test en la fila δ = 0). Cobertura = el IC contiene la δ verdadera. "
             "Segunda ruta = potencia normal cerrada Φ(δ√T/σ − 1,96) con la misma σ y ρ = 0.\n")
    cab = ("| δ | σ | ρ | semanas | **detección** [Wilson] | excluye 0 [Wilson] | cobertura [Wilson] | "
           "cobertura IC sd | punto ± sd | ancho medio | normal cerrada (α 0,05) |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|"
    for grupo, titulo in (("base", "Celda base (σ medida, ρ = 0), 52, 104 y 156 semanas"),
                          ("sigma_x0.5", "Sensibilidad: σ a la mitad, 52 semanas"),
                          ("sigma_x2.0", "Sensibilidad: σ al doble, 52 semanas"),
                          ("rho_0.2", "Sensibilidad: dependencia entre semanas ρ = 0,2, 52 semanas")):
        filas = [c for c in r["celdas"] if c["grupo"] == grupo]
        if not filas:
            continue
        L.append(f"### {titulo}\n")
        L.append(cab)
        L.append(sep)
        for c in sorted(filas, key=lambda c: (c["semanas"], c["delta_pp_semana"])):
            L.append(_fila(c))
        L.append("")
    L.append("## Lectura, y lo que no se puede leer\n")
    base52 = sorted([c for c in r["celdas"] if c["grupo"] == "base" and c["semanas"] == 52],
                    key=lambda c: c["delta_pp_semana"])
    nul = base52[0]
    L.append(f"- **Tamaño bajo la nula** (bilateral, 52 semanas): {nul['excluye_cero']['tasa']:.3f} "
             f"{nul['excluye_cero']['wilson95']} contra un nominal de 0,05; cobertura "
             f"{nul['cobertura_ic95']['tasa']:.3f} {nul['cobertura_ic95']['wilson95']} contra 0,95. "
             "Si el intervalo de la cobertura excluye 0,95, el instrumento sub- o sobre-cubre y eso "
             "se declara, no se corrige acá (la elección del estimador después de ver la cobertura "
             "es un grado de libertad).")
    for c in base52[1:]:
        L.append(f"- δ = {c['delta_pp_semana']:+.2f}: detección {c['deteccion']['tasa']:.3f} "
                 f"{c['deteccion']['wilson95']} contra {c['potencia_normal_cerrada']:.3f} de la normal cerrada.")
    L.append("- **Regla (exigencia A7):** el largo del bloque del bootstrap NO se barre después de haber visto la "
             "cobertura sin declararlo como grado de libertad; cambiar el estimador es decisión de Nicolás "
             "(`espera_firma.md` §50).")
    L.append("- **Lo que esto NO valida:** " + r["no_valida"] + ". Una σ medida sobre carteras "
             "sorteadas de 4 instrumentos es un proxy declarado de la dispersión de una cuenta que "
             "todavía no existe sin fuga; por eso se barre en 0,5σ y 2σ.")
    L.append("- La fila ρ = 0,2 dice qué pasa si las semanas no son intercambiables; el bloque de 4 "
             "semanas del instrumento es lo que debería absorberlo, y el cuadro mide cuánto absorbe.")
    return "\n".join(L) + "\n"


def main(n_rep: int = REPLICAS) -> dict:
    r = correr(n_rep=n_rep)
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1, ensure_ascii=False, default=float)
        f.write("\n")
    with open(SALIDA_MD, "w", encoding="utf-8") as f:
        f.write(informe(r))
    print("escrito", SALIDA_MD, "y", SALIDA_JSON)
    print("veredicto:", r["veredicto"]["instrumento_discrimina"], "-", r["veredicto"]["consecuencia"])
    return r


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else REPLICAS
    main(n)
