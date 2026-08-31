"""
diseno_secuencial.py — la aritmética del diseño secuencial pre-registrado.

Todo número que aparezca en `GEMELO/SECUENCIAL/DISEÑO.md` sale de correr
este archivo. **Versionado desde el primer cómputo**: es la lección
operativa que dejó la corrida anterior (`DECISIONES.md` §45 — un análisis
que vivió en comandos sueltos costó dos rondas de auditoría y terminó
retractado, en parte porque no se podía reproducir).

Sin scipy, por la misma razón que el resto del proyecto: `requirements.txt`
está fijado y agregar una dependencia es una decisión con acta.

**Versión 2 — corregida tras el RECHAZO de `estadistico-adversario`
(31-ago-2026).** El cambio de fondo: las fronteras ya NO salen de Monte
Carlo. La v1 las sacaba de un cuantil simulado con semilla congelada, y
ese cuantil cayó por debajo de la media de las semillas, así que la
frontera congelada tenía α real 0.05122 y no 0.05. La verificación
interna del propio script medía 0.0507 y el documento lo leyó como
confirmación: era el sesgo mismo. Ahora salen de `fronteras.py`
(recursión numérica exacta) y se validan contra la literatura, que es
una vara externa. El Monte Carlo queda como verificación secundaria.

Corre con:  python GEMELO/SECUENCIAL/diseno_secuencial.py
"""
from __future__ import annotations

import datetime as dt
import math
import os
import sys

import numpy as np

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
sys.path.insert(0, os.path.join(_RAIZ, ".claude/skills/estadistica-evaluacion/scripts"))
sys.path.insert(0, _AQUI)
from backtest import inferencia as inf  # noqa: E402
from evaluacion import norm_cdf, norm_ppf, wilson_ci  # noqa: E402
from fronteras import (REFERENCIA, Malla, _prob_cruce_drift,  # noqa: E402
                       verificacion_mc)

SEMILLA = 20260831   # usada por verificacion_mc y por la simulación de correlación serial


# ---------------------------------------------------------------------------
# Parámetros medidos, no elegidos. Cada uno con su procedencia.
# ---------------------------------------------------------------------------

# Tasa de discordancia observada en la ventana sellada actual (b+c)/n con
# b=72, c=56, n=248 — `GEMELO/resultados/concentracion.md` §A1, reproducida
# cuatro veces por vías independientes.
P_D_OBSERVADA = 128 / 248

# Efecto de diseño por clustering intra-fecha: los ~7-8 tickers de una misma
# fecha comparten el signo de la predicción (el modelo sigue el signo del
# SOX de esa noche), así que las filas NO son independientes. Medido por
# bootstrap por fecha: DEFF ≈ 2.5-3.6, con el extremo teórico ρ=1 en 7.26.
#
# ATENCIÓN — esto es un parámetro de PLANIFICACIÓN, no del estadístico.
# Sirve para elegir N_max y las fechas del calendario. El estadístico de
# cada mirada NO lo usa: re-estima su propia varianza cluster-robusta
# sobre las fechas acumuladas (ver DISEÑO.md §A3.2 y `sensibilidad_deff()`
# más abajo, que muestra qué pasaría si se congelara: con DEFF verdadero
# 4.6 el α real sería 0.09, con 5.83 sería 0.14).
DEFF_PLANIFICACION = 3.6
DEFF_RANGO = (2.5, 3.6, 4.6, 5.83, 7.26)

# Ritmo de acumulación medido (`integridad-datos`, corridas anteriores):
# ~6.5 filas verificadas por día hábil, ~0.89 fechas de emisión por día
# hábil (34 fechas en 38 días hábiles de la ventana actual).
FILAS_POR_DIA_HABIL = 6.5
FECHAS_POR_DIA_HABIL = 34 / 38

FECHA_CONGELAMIENTO = dt.date(2026, 8, 31)

FRACCIONES = [0.25, 0.50, 0.75, 1.00]
MDE = 0.10


# ---------------------------------------------------------------------------
# 1. Tamaño de muestra para un McNemar pareado (Connor 1987)
# ---------------------------------------------------------------------------

def n_mcnemar(delta: float, p_d: float = P_D_OBSERVADA,
              alpha: float = 0.05, potencia: float = 0.80) -> float:
    """n de FILAS bajo independencia. `delta` en proporción (0.05 = 5pp)."""
    z_a2 = norm_ppf(1 - alpha / 2)
    z_b = norm_ppf(potencia)
    num = (z_a2 * math.sqrt(p_d) + z_b * math.sqrt(p_d - delta ** 2)) ** 2
    return num / delta ** 2


def n_ajustado(delta: float, deff: float = DEFF_PLANIFICACION, **kw):
    """Devuelve (n_iid, n_filas_con_DEFF, n_fechas_equivalentes)."""
    n_iid = n_mcnemar(delta, **kw)
    n_filas = n_iid * deff
    n_fechas = n_filas / (FILAS_POR_DIA_HABIL / FECHAS_POR_DIA_HABIL)
    return n_iid, n_filas, n_fechas


# ---------------------------------------------------------------------------
# 2. Potencia y características operativas del plan secuencial
# ---------------------------------------------------------------------------

def potencia_secuencial(malla: Malla, umbrales, drift: float, futilidad_z=None):
    """(P(cruzar eficacia), P(parar por futilidad)) para un drift dado.

    Bajo drift=0 el primero ES la tasa de error tipo I global."""
    return _prob_cruce_drift(malla, umbrales, drift, futilidad_z=futilidad_z)


def drift_para_potencia(malla: Malla, umbrales, objetivo=0.80,
                        futilidad_z=None, tol=1e-5) -> float:
    """El drift (Z esperado en el análisis final) que da la potencia pedida.

    Un test de muestra fija a α=0.05 lo lograría con drift 1.96+0.8416 =
    2.802. El plan secuencial necesita MÁS, porque su umbral final (2.024)
    es más alto que 1.96. Ese exceso es lo que hay que pagar en N: es la
    corrección que la v1 no hizo y por eso su potencia real era 0.795."""
    lo, hi = 1.0, 6.0
    for _ in range(60):
        medio = 0.5 * (lo + hi)
        p, _ = potencia_secuencial(malla, umbrales, medio, futilidad_z)
        if p < objetivo:
            lo = medio
        else:
            hi = medio
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def sensibilidad_deff(malla: Malla, umbrales, deff_plan: float, deffs):
    """Qué α REAL tendría el plan si el estadístico congelara `deff_plan`
    y el clustering verdadero fuera otro.

    Si el estadístico divide por sqrt(deff_plan) y la varianza verdadera
    es deff_real veces la iid, el Z reportado queda inflado por
    sqrt(deff_real/deff_plan) — equivale a bajar toda la frontera por ese
    factor. Es el defecto D3, y es la razón por la que el estadístico
    re-estima su varianza en cada mirada en vez de congelarla."""
    fila = []
    for deff_real in deffs:
        escala = math.sqrt(deff_plan / deff_real)
        alfa, _ = malla.prob_cruce([u * escala for u in umbrales])
        fila.append((deff_real, alfa))
    return fila


# ---------------------------------------------------------------------------
# 3. Futilidad por potencia condicional (curtailment estocástico)
# ---------------------------------------------------------------------------

def potencia_condicional(z_k: float, t: float, z_final: float, drift_total: float) -> float:
    """P(cruzar el umbral final | lo observado hasta t), asumiendo que el
    efecto real es el del diseño (drift_total = Z esperado al final)."""
    if t >= 1.0:
        return 1.0 if z_k >= z_final else 0.0
    num = z_final - z_k * math.sqrt(t) - drift_total * (1 - t)
    den = math.sqrt(1 - t)
    return float(1 - norm_cdf(num / den))


def z_futilidad(t: float, z_final: float, drift_total: float, umbral_pc: float = 0.20) -> float:
    """El Z observado por debajo del cual la potencia condicional cae bajo
    `umbral_pc` — o sea, seguir acumulando ya casi no puede cambiar el
    resultado. Es una frontera NO VINCULANTE: parar acá es una opción, no
    una obligación, y no consume alfa."""
    if t >= 1.0:
        return z_final
    objetivo = norm_ppf(1 - umbral_pc)
    return (z_final - drift_total * (1 - t) - objetivo * math.sqrt(1 - t)) / math.sqrt(t)


# ---------------------------------------------------------------------------
# 4. Calendario
# ---------------------------------------------------------------------------

def fecha_para_filas(filas_objetivo: float, desde: dt.date = FECHA_CONGELAMIENTO) -> dt.date:
    dias_habiles = filas_objetivo / FILAS_POR_DIA_HABIL
    dias_calendario = dias_habiles * 7 / 5
    return desde + dt.timedelta(days=round(dias_calendario))


# ---------------------------------------------------------------------------
# 5. El pasivo: cuánto infló el alfa mirar (al menos) 12 veces sin declararlo
# ---------------------------------------------------------------------------

# Las miradas reconstruidas por `orientador` desde DECISIONES.md, README y
# git log. Ver DISEÑO.md §A1 para la tabla completa con sus citas. El rango
# real de n es 184-253: la v1 usaba `linspace(200, 260)` en la fila de
# referencia, que no es el rango de nada (defecto D5).
MIRADAS_PASADAS_N = [228, 228, 228, 223, 184, 223, 245, 240, 253, 253, 248, 248]
N_MIN, N_MAX_PASADO = 184, 253
# El hueco declarado en §A1: entre el 26-jul (n=80, cuando solo se publicaba
# la tasa cruda) y el 25-ago (n=228, la primera medición contra baseline) no
# hay registro de cuántas veces se miró el número intermedio.
N_HUECO_DESDE = 80


def inflacion_por_miradas(ns, alpha_nominal=0.05) -> float:
    """Tasa de error tipo I REAL de haber mirado k veces a medida que los
    datos se acumulaban, usando siempre el umbral nominal de alfa=0.05.

    EXACTA por integración numérica — no simulada. Las miradas NO son
    independientes (comparten casi todas las filas), y esa correlación es
    justamente lo que hace que la inflación sea mucho menor que un
    Bonferroni ingenuo, pero mayor que 0.05, que es el punto. Estructura
    canónica de datos que se acumulan: Z_k = B(t_k)/sqrt(t_k), t_k =
    n_k/max(n). Miradas con el mismo n colapsan a la misma t: se
    deduplican, porque dos lecturas de la MISMA cifra no son dos
    oportunidades de cruzar."""
    fracciones = sorted({n / max(ns) for n in ns})
    if fracciones[-1] < 1.0:
        fracciones.append(1.0)
    malla = Malla(fracciones, m=4001, ancho=7.0)
    umbral = norm_ppf(1 - alpha_nominal / 2)
    p, _ = malla.prob_cruce([umbral] * len(fracciones))
    return p


# ---------------------------------------------------------------------------
# 6. El eje al que un bootstrap de clúster es ciego: la dependencia ENTRE
#    fechas. Es el defecto que el segundo dictamen encontró.
# ---------------------------------------------------------------------------

# Las fechas acumuladas en cada mirada salen del MISMO calendario que el
# resto del documento: n_k / (filas por fecha) con n_k = t_k × N_max = 371,
# 742, 1114, 1485 y 7.31 filas por fecha. La v3 usaba (53, 102, 153, 204)
# "a ojo", y más fechas = mejor bootstrap = α simulado más bajo: el redondeo
# iba en la dirección optimista.
FECHAS_POR_MIRADA = tuple(
    round(t * 1485 / (FILAS_POR_DIA_HABIL / FECHAS_POR_DIA_HABIL))
    for t in (0.25, 0.50, 0.75, 1.00))
UMBRALES_OBF = (4.048, 2.862, 2.337, 2.024)

# Sorteos del bootstrap INTERNO de la simulación. No son los 200.000 que usa
# `mirada.py`: 200.000 × 4 miradas × 20.000 réplicas es inviable. El sesgo de
# usar menos está medido y su dirección es conocida — menos sorteos, más
# ruido en V̂, más sesgo hacia arriba del máximo, menos cruces: o sea la
# simulación sale OPTIMISTA. Con 400 el sesgo en Z era 0.15-0.49%; con 2.000
# es ~4× menor. Se declara en vez de esconderse.
N_DRAWS_SIMULACION = 600


def alfa_plan_bajo_correlacion(ac1_objetivo: float, bloques=(1, 5, 10),
                               n_rep: int = 20_000, por_fecha: int = 7,
                               n_draws: int = N_DRAWS_SIMULACION,
                               semilla: int = SEMILLA + 7) -> dict:
    """α GLOBAL del plan entero si d_j está autocorrelado entre fechas.

    Simula el procedimiento COMPLETO bajo H0: acumula fechas, en cada
    mirada re-estima V̂ con el mismo bootstrap que usa `mirada.py`, y
    compara contra el umbral OBF de esa mirada, parando al primer cruce.

    Es la medición que faltaba, y la que decide si el estimador de
    varianza cumple lo que el pre-registro promete. Un bootstrap que
    sortea FECHAS corrige la dependencia DENTRO de la fecha y es
    estructuralmente ciego a la de fecha a fecha; si esa existe, V̂ sale
    corta y Z sale inflado.

    Detalle que importa y que el diseño no había notado: la mirada donde
    V̂ es MENOS confiable (la 1, con ~51 fechas) es la que tiene el umbral
    MÁS alto (4.048). La conservadurismo temprano de O'Brien-Fleming y la
    debilidad del bootstrap están anti-correlacionados, y eso amortigua
    parte del daño sin que nadie lo hubiera diseñado así.
    """
    rng = np.random.default_rng(semilla)
    phi = ac1_objetivo
    cruces = 0
    m = FECHAS_POR_MIRADA[-1]
    raiz = math.sqrt(max(1 - phi * phi, 1e-9))
    for r in range(n_rep):
        e = rng.normal(size=m)
        d = np.empty(m)
        d[0] = e[0]
        for j in range(1, m):
            d[j] = phi * d[j - 1] + raiz * e[j]
        d = np.round(d * por_fecha / 2.0)          # a escala de discordantes
        for k, nf in enumerate(FECHAS_POR_MIRADA):
            dk = d[:nf]
            var_iid = float(np.abs(dk).sum()) or 1.0
            z0 = dk.sum() / math.sqrt(var_iid)
            v = max(
                float(np.var(inf._remuestrear_circular(
                    dk, semilla + r * 4 + k, n_draws, b).sum(axis=1), ddof=1)) / var_iid
                for b in bloques)
            z = z0 / math.sqrt(v) if v > 0 else 0.0
            if abs(z) >= UMBRALES_OBF[k]:
                cruces += 1
                break
    lo, hi = wilson_ci(cruces, n_rep)
    return {"alfa": cruces / n_rep, "lo": lo, "hi": hi,
            "cruces": cruces, "n_rep": n_rep, "n_draws": n_draws,
            "bloques": tuple(bloques), "ac1": ac1_objetivo}


def ac1_ventana_antecedente() -> dict:
    """Autocorrelación lag-1 de d_j sobre la ventana sellada de hoy.

    **Es un parámetro de estorbo de VARIANZA, de la misma clase que p_d y
    el DEFF** (`DISEÑO.md` §A2): no dice nada sobre si hay ventaja, y no se
    computa ninguna ventaja acá. Se mide porque el diseño necesita saber si
    el eje al que su bootstrap es ciego está vivo o no.
    """
    try:
        from backtest.linea_base import aplicar_convencion, cargar
        from GEMELO.SECUENCIAL.mirada import (autocorrelacion_lag1,
                                              contribuciones_por_fecha)
    except Exception as exc:                       # pragma: no cover
        return {"error": str(exc)}
    df = cargar()
    if df.empty:
        return {"error": "sin filas"}
    df = aplicar_convencion(df, "excluir_cero")
    d = contribuciones_por_fecha(df)
    ac1, ee = autocorrelacion_lag1(d)
    return {"ac1": ac1, "ee": ee, "fechas": len(d)}


def _linea(titulo: str) -> None:
    print("\n" + titulo)
    print("-" * len(titulo))


def main() -> None:
    print("=" * 74)
    print("DISEÑO SECUENCIAL — aritmética (v2, post-rechazo)")
    print(f"p_d observada={P_D_OBSERVADA:.4f}  DEFF planificación={DEFF_PLANIFICACION}  "
          f"ritmo={FILAS_POR_DIA_HABIL} filas/día hábil")
    print("=" * 74)

    _linea("0. VALIDACIÓN EXTERNA DE LAS FRONTERAS (contra la literatura)")
    print(f"{'K':>2}  {'Pocock':>8} {'ref':>7}  {'OBF c_B':>8} {'ref':>7}")
    for K in (2, 3, 4):
        fr = [(i + 1) / K for i in range(K)]
        m = Malla(fr)
        from fronteras import frontera_obf, frontera_pocock
        cp, _ = frontera_pocock(fr, malla=m)
        co, _ = frontera_obf(fr, malla=m)
        rp, ro = REFERENCIA[K]
        print(f"{K:>2}  {cp:8.3f} {rp:7.3f}  {co:8.3f} {ro:7.3f}")
    print("  (si estas cuatro columnas no coinciden, no seguir: la máquina de")
    print("   fronteras está mal y todo lo de abajo hereda el error)")

    _linea("1. EL PASIVO — cuánto costó mirar sin declararlo (D5: es un RANGO)")
    tasa = inflacion_por_miradas(MIRADAS_PASADAS_N)
    n_dist = len({n for n in MIRADAS_PASADAS_N})
    print(f"  PISO — solo las {len(MIRADAS_PASADAS_N)} miradas reconstruidas")
    print(f"  ({n_dist} valores distintos de n, de {N_MIN} a {N_MAX_PASADO}; dos")
    print(f"  lecturas de la MISMA cifra no son dos oportunidades de cruzar):")
    print(f"      α real = {tasa:.4f}   ({tasa/0.05:.1f}× el nominal)\n")
    print(f"  Pero {len(MIRADAS_PASADAS_N)} es un piso, no un conteo. Entre el 26-jul "
          f"(n={N_HUECO_DESDE})")
    print("  y el 25-ago (n=228) no hay registro de cuántas veces se miró el")
    print("  número intermedio, y esas miradas son las que MÁS inflan, porque")
    print("  comparten menos filas con las de hoy. Poblando ese hueco:")
    for k in (0, 2, 4, 8, 16):
        extra = list(np.linspace(N_HUECO_DESDE, N_MIN, k + 1)[:-1]) if k else []
        a = inflacion_por_miradas(MIRADAS_PASADAS_N + extra)
        print(f"    +{k:>2} miradas en el hueco  ->  α = {a:.4f}  ({a/0.05:.1f}×)")
    techo = list(np.arange(N_HUECO_DESDE, N_MAX_PASADO, FILAS_POR_DIA_HABIL))
    a_techo = inflacion_por_miradas(MIRADAS_PASADAS_N + techo)
    print(f"  TECHO — una mirada en cada fecha de emisión desde n={N_HUECO_DESDE}:")
    print(f"      α real = {a_techo:.4f}   ({a_techo/0.05:.1f}× el nominal)")
    print(f"\n  >> El rango honesto es α ∈ [{tasa:.2f}, {a_techo:.2f}], o sea "
          f"{tasa/0.05:.1f}× a {a_techo/0.05:.1f}× el nominal.")
    print("     Citar solo el piso como si fuera el número sería el mismo error")
    print("     que este documento le reprocha al proyecto.")

    _linea("2. TAMAÑO DE MUESTRA (potencia 0.80, alfa 0.05 bilateral, muestra fija)")
    print(f"{'efecto':>10} {'n iid':>10} {'n filas (×DEFF)':>18} {'fechas':>10} {'fecha estimada':>16}")
    for pp in (15.66, 10.0, 6.45, 5.0, 3.0):
        n_iid, n_filas, n_fechas = n_ajustado(pp / 100)
        print(f"{pp:>9.2f}pp {n_iid:>10.0f} {n_filas:>18.0f} {n_fechas:>10.0f} "
              f"{fecha_para_filas(n_filas).isoformat():>16}")

    # --- el diseño propuesto: MDE de 10pp, 4 miradas (3 intermedias + final).
    n_iid, n_filas_fijo, _ = n_ajustado(MDE)
    malla = Malla(FRACCIONES)
    from fronteras import frontera_obf, frontera_pocock
    c_p, umbrales_p = frontera_pocock(FRACCIONES, malla=malla)
    c_o, umbrales_o = frontera_obf(FRACCIONES, malla=malla)

    _linea(f"3. FRONTERAS DEL PLAN (MDE={MDE*100:.0f}pp, {len(FRACCIONES)} miradas)")
    print(f"{'t':>6} | {'Pocock Z':>9} {'α nominal':>10} | {'OBF Z':>9} {'α nominal':>10}")
    for t, up, uo in zip(FRACCIONES, umbrales_p, umbrales_o):
        print(f"{t:>6.2f} | {up:>9.3f} {2*(1-norm_cdf(up)):>10.5f} | "
              f"{uo:>9.3f} {2*(1-norm_cdf(uo)):>10.5f}")
    a_p, _ = malla.prob_cruce(umbrales_p)
    a_o, _ = malla.prob_cruce(umbrales_o)
    print(f"  α global exacto:  Pocock {a_p:.5f}   OBF {a_o:.5f}")
    v = verificacion_mc(FRACCIONES, umbrales_o)
    print(f"  verificación secundaria por Monte Carlo ({v['n_sim']:,} réplicas, "
          f"semilla {v['semilla']}):")
    print(f"    α = {v['p']:.5f}  IC95 [{v['lo']:.5f}, {v['hi']:.5f}]  "
          f"— contiene al exacto: {v['lo'] <= a_o <= v['hi']}")
    print("    (NO es la fuente de ninguna cifra: la fuente es la recursión.")
    print("     Sirve para detectar un error grosero por un camino que no")
    print("     comparte una línea de código con ella.)")

    _linea("4. POTENCIA REAL Y N_max (defecto D2)")
    drift_fijo = norm_ppf(0.975) + norm_ppf(0.80)
    pot_al_n_fijo, _ = potencia_secuencial(malla, umbrales_o, drift_fijo)
    print(f"  Con N={n_filas_fijo:.0f} filas (el n de muestra fija) el drift es "
          f"{drift_fijo:.3f}")
    print(f"  y la potencia REAL del plan secuencial es {pot_al_n_fijo:.4f}, no 0.80.")
    print("  El umbral final del plan (2.024) es más alto que el 1.96 de muestra")
    print("  fija: esa diferencia se paga en N o se paga en potencia.")
    drift_ok = drift_para_potencia(malla, umbrales_o, 0.80)
    factor = (drift_ok / drift_fijo) ** 2
    n_max = n_filas_fijo * factor
    print(f"  Drift necesario para potencia 0.80: {drift_ok:.4f}  "
          f"-> N_max = {n_filas_fijo:.0f} × {factor:.4f} = **{n_max:.0f} filas**")

    z_final = umbrales_o[-1]
    fut = [z_futilidad(t, z_final, drift_ok) for t in FRACCIONES[:-1]] + [None]
    pot_con_fut, p_fut_h1 = potencia_secuencial(malla, umbrales_o, drift_ok, fut)
    _, p_fut_h0 = potencia_secuencial(malla, umbrales_o, 0.0, fut)
    print(f"\n  Características operativas (frontera de futilidad incluida):")
    print(f"    potencia sin futilidad ...................... {0.80:.4f} (por construcción)")
    print(f"    potencia si se PARA en la futilidad ......... {pot_con_fut:.4f}")
    print(f"    P(parar por futilidad | H1 cierta) .......... {p_fut_h1:.4f}")
    print(f"    P(parar por futilidad | H0 cierta) .......... {p_fut_h0:.4f}")
    print("    (la última es la que hace útil el diseño: bajo H0 se corta temprano)")

    _linea("5. SENSIBILIDAD AL DEFF — por qué el estadístico NO lo congela (D3)")
    print("  α real del plan si el estadístico congelara DEFF=3.6 y el")
    print("  clustering verdadero fuera otro:")
    for deff_real, alfa in sensibilidad_deff(malla, umbrales_o, DEFF_PLANIFICACION, DEFF_RANGO):
        nota = "  <- el supuesto" if deff_real == DEFF_PLANIFICACION else ""
        if deff_real == 7.26:
            nota = "  <- extremo teórico ρ=1"
        print(f"    DEFF verdadero {deff_real:>4.2f}  ->  α = {alfa:.4f}{nota}")
    print("  Un α que se mueve entre 0.02 y 0.19 según un parámetro estimado")
    print("  a ojo NO es un α controlado. Por eso la varianza se re-estima en")
    print("  cada mirada sobre las fechas acumuladas (DISEÑO.md §A3.2).")

    _linea("5-bis. EL EJE CIEGO: dependencia ENTRE fechas (defecto del 2º dictamen)")
    print("  Un bootstrap que sortea FECHAS corrige el agrupamiento DENTRO de")
    print("  la fecha y es estructuralmente ciego al de fecha a fecha. Si esa")
    print("  dependencia existe, V̂ sale corta y Z sale inflado. α GLOBAL del")
    print("  plan entero, simulado bajo H0 con un AR(1) en d_j:")
    print(f"  (fechas acumuladas por mirada: {FECHAS_POR_MIRADA}, del mismo")
    print(f"   calendario que el resto; {N_DRAWS_SIMULACION} sorteos internos)")
    print(f"\n{'ac1 real':>9} | {'solo bloque 1 (IC95)':>30} | "
          f"{'max(1,5,10) (IC95)':>30} | {'reduce':>7}")
    for phi in (0.0, 0.10, 0.20, 0.30):
        a1 = alfa_plan_bajo_correlacion(phi, bloques=(1,))
        am = alfa_plan_bajo_correlacion(phi, bloques=(1, 5, 10))
        red = 100 * (1 - am["alfa"] / a1["alfa"]) if a1["alfa"] else float("nan")
        print(f"{phi:>+9.2f} | {a1['alfa']:.4f} [{a1['lo']:.4f}, {a1['hi']:.4f}]"
              f"{'':>7} | {am['alfa']:.4f} [{am['lo']:.4f}, {am['hi']:.4f}]"
              f"{'':>7} | {red:>6.0f}%")
    print("\n  La reducción NO es pareja: es chica donde el proyecto midió que")
    print("  está la autocorrelación y grande solo en el extremo. Y NO elimina")
    print("  la exposición. Con ~51 fechas en la primera mirada eso no se")
    print("  arregla con un estimador mejor: es el límite del n, y va")
    print("  DECLARADO en §A3.2 con sus intervalos en vez de escondido.")
    med = ac1_ventana_antecedente()
    if "error" in med:
        print(f"\n  (no se pudo medir sobre la ventana antecedente: {med['error']})")
    else:
        print(f"\n  Medida sobre la ventana antecedente (parámetro de estorbo de")
        print(f"  VARIANZA, igual que p_d y el DEFF — no se computa ninguna")
        print(f"  ventaja acá): ac1 = {med['ac1']:+.3f} ± {med['ee']:.3f} sobre "
              f"{med['fechas']} fechas.")
        print("  O sea: los datos de hoy NO distinguen 0 de +0.2. Por eso el")
        print("  estadístico toma V̂ = max(bloque 1, bloque 5) — el máximo solo")
        print("  puede inflar la varianza, y por lo tanto solo puede bajar el α.")

    _linea("6. FUTILIDAD (potencia condicional < 20%, NO vinculante)")
    print(f"{'t':>6} {'n filas':>10} {'Z futilidad':>13}")
    for t, zf in zip(FRACCIONES[:-1], fut[:-1]):
        print(f"{t:>6.2f} {t*n_max:>10.0f} {zf:>13.3f}")

    _linea(f"7. CALENDARIO (desde {FECHA_CONGELAMIENTO.isoformat()}, "
           f"{FILAS_POR_DIA_HABIL} filas/día hábil)")
    for t in FRACCIONES:
        filas = t * n_max
        print(f"  mirada t={t:>4.2f}  n={filas:>7.0f} filas  "
              f"(~{filas/(FILAS_POR_DIA_HABIL/FECHAS_POR_DIA_HABIL):>5.0f} fechas)  "
              f"-> {fecha_para_filas(filas).isoformat()}")

    _linea("8. EL PRECIO DE UNA MIRADA FURTIVA (gobernanza con número, D8)")
    print("  Si alguien computa el estadístico entre miradas y no lo declara,")
    print("  el α del plan deja de ser 0.05. Cuánto deja de serlo:")
    for extra in (0, 1, 2, 3):
        fr = sorted(set(FRACCIONES) | {0.125 + 0.25 * i for i in range(extra)})
        m2 = Malla(fr, m=4001, ancho=7.0)
        # la frontera del plan se mantiene; las miradas extra usan α nominal 0.05
        umbrales = []
        for t in fr:
            if t in FRACCIONES:
                umbrales.append(umbrales_o[FRACCIONES.index(t)])
            else:
                umbrales.append(norm_ppf(0.975))
        a, _ = m2.prob_cruce(umbrales)
        print(f"    {extra} mirada(s) furtiva(s) a α nominal 0.05  ->  α real = {a:.4f}")

    _linea("9. LO QUE ESTE DISEÑO NO PUEDE RESPONDER — la hipótesis CONDICIONAL")
    print("  Tres precios distintos para tres preguntas distintas. Publicar solo")
    print("  el del medio, como hacía la v1, esconde que ese cálculo SUPONE que")
    print("  el efecto es homogéneo entre subgrupos — que es la hipótesis nula")
    print("  de la pregunta condicional (defecto D6).\n")

    # (a) interacción: detectar que Δ difiere ENTRE subgrupos. Var(Δ1-Δ2) =
    #     2×Var(Δ) y cada subgrupo tiene n/2 -> 4× el n del efecto principal.
    n_interaccion = n_filas_fijo * 4
    print(f"  (a) INTERACCIÓN, k=2 — 'la ventaja difiere entre los dos grupos'")
    print(f"      4× el efecto principal      -> {n_interaccion:>7.0f} filas  "
          f"-> {fecha_para_filas(n_interaccion).isoformat()}")

    # (b) efecto principal DENTRO de cada subgrupo, con Bonferroni. Supone
    #     que el efecto es del tamaño del MDE en cada uno: homogéneo.
    n_dentro = n_mcnemar(MDE, alpha=0.05 / 2) * DEFF_PLANIFICACION * 2
    print(f"  (b) MDE dentro de cada subgrupo (Bonferroni k=2)")
    print(f"      SUPONE efecto homogéneo     -> {n_dentro:>7.0f} filas  "
          f"-> {fecha_para_filas(n_dentro).isoformat()}")

    # (c) concentración total: todo el efecto vive en un subgrupo, al doble
    #     de tamaño (para que el promedio siga siendo el MDE).
    n_concentrado = n_mcnemar(2 * MDE, alpha=0.05 / 2) * DEFF_PLANIFICACION * 2
    print(f"  (c) CONCENTRACIÓN TOTAL — todo el efecto en un grupo, al doble")
    print(f"      el caso más favorable       -> {n_concentrado:>7.0f} filas  "
          f"-> {fecha_para_filas(n_concentrado).isoformat()}")

    print("\n  Y las mismas tres para más subgrupos (solo el caso (b), que es el")
    print("  que escala peor):")
    for k, etiqueta in ((4, "cuatro estratos"),
                        (6, "las seis condiciones candidatas")):
        n_total = n_mcnemar(MDE, alpha=0.05 / k) * DEFF_PLANIFICACION * k
        print(f"    k={k} ({etiqueta:<32}) -> {n_total:>8.0f} filas  "
              f"-> {fecha_para_filas(n_total).isoformat()}")


if __name__ == "__main__":
    main()
