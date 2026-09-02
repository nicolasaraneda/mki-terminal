# ============================================================
# inferencia.py — la maquinaria para JUZGAR un modelo (Etapa 6.0.0, WS1).
#
# Especificada en GEMELO/DISEÑO.md §5. Se construye ANTES que el retador a
# propósito: si el modelo se construyera primero, su primer resultado se
# evaluaría con instrumentos que ya sabemos que no alcanzan, y esa primera
# lectura contamina todo lo que viene después.
#
# Incorporada de `vcalderone/equity-direction-research` v2.1.0, licencia
# MIT (atribución en DECISIONES.md §24; la MIT exige conservar el aviso).
#
# Referencias:
#   · Lo (2002)                      — error estándar del Sharpe
#   · Bailey & López de Prado (2012) — Probabilistic Sharpe Ratio
#   · Bailey & López de Prado (2014) — Deflated Sharpe Ratio
#   · Politis & Romano (1994)        — bootstrap circular de bloques
#
# Funciones PURAS: sin estado, sin E/S, sin tocar ninguna base. No importa
# nada de backtest/ para que se pueda testear y razonar en aislamiento.
#
# SIN scipy: el proyecto fija requirements.txt y las dos máquinas deben
# tener dependencias idénticas (DECISIONES.md §1). La normal se resuelve
# con math.erfc y su inversa por bisección — 400 iteraciones sobre un
# intervalo acotado dan precisión de doble, y una bisección es trivial de
# verificar contra valores tabulados, que es justo lo que se quiere en el
# módulo que decide si un modelo gana.
#
# LÍMITE DE PRECISIÓN, a tener presente al leer un informe: por encima de
# z ≈ 8.3, Phi devuelve 1.0 EXACTO en doble precisión. Un PSR o un DSR que
# salga 1.000 significa "más allá de lo que el doble distingue", NO
# "certeza"; y en esa zona saturada la monotonía deja de ser estricta. La
# zona que informa algo es la de los valores intermedios — que es
# justamente donde caen los casos reales con n=228.
# ============================================================

import math

import numpy as np

# Euler-Mascheroni. Entra en el umbral del Deflated Sharpe por la
# aproximación del máximo de N normales independientes.
GAMMA = 0.5772156649015329


# ------------------------------------------------------------
# Normal estándar
# ------------------------------------------------------------
def Phi(x: float) -> float:
    """Función de distribución acumulada de la normal estándar."""
    return 0.5 * math.erfc(-float(x) / math.sqrt(2.0))


def Phi_inv(p: float, tol: float = 1e-15, iteraciones: int = 400) -> float:
    """Inversa de Phi por bisección. Exacta a doble precisión en el rango
    útil; se prefiere a una aproximación racional porque se puede auditar
    contra valores tabulados sin depender de coeficientes mágicos."""
    p = float(p)
    if not 0.0 < p < 1.0:
        raise ValueError(f"Phi_inv espera p en (0,1), recibió {p}")
    lo, hi = -40.0, 40.0
    for _ in range(iteraciones):
        medio = (lo + hi) / 2.0
        if Phi(medio) < p:
            lo = medio
        else:
            hi = medio
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0


# ------------------------------------------------------------
# Error estándar del Sharpe (Lo 2002; forma de Mertens)
# ------------------------------------------------------------
def var_sharpe(sr: float, n: int, skew: float = 0.0, kurt: float = 3.0) -> float:
    """Varianza del Sharpe estimado.

        Var(SR) = (1 - skew*SR + (kurt-1)/4 * SR^2) / (n-1)

    `kurt` es la curtosis NO exceso (3 = normal). Con asimetría negativa y
    colas gruesas —el caso de los retornos reales— esta varianza es MAYOR
    que bajo normalidad: un Sharpe sin esta corrección se presenta con más
    seguridad de la que tiene. Ésa es la razón de ser de la corrección.
    """
    n = int(n)
    if n < 2:
        raise ValueError("var_sharpe necesita n >= 2")
    return (1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr) / (n - 1)


def se_sharpe(sr: float, n: int, skew: float = 0.0, kurt: float = 3.0) -> float:
    """Error estándar del Sharpe. Un Sharpe sin barra de error es un punto
    disfrazado de hallazgo (§5 del diseño)."""
    v = var_sharpe(sr, n, skew, kurt)
    if v < 0:
        raise ValueError(
            f"var_sharpe negativa ({v:.6g}): combinación de sr/skew/kurt "
            "fuera del rango donde la aproximación de Lo tiene sentido")
    return math.sqrt(v)


# ------------------------------------------------------------
# Probabilistic Sharpe Ratio (Bailey & LdP 2012)
# ------------------------------------------------------------
def psr(sr: float, sr_ref: float, n: int,
        skew: float = 0.0, kurt: float = 3.0) -> float:
    """Probabilidad de que el Sharpe verdadero supere `sr_ref`.

        PSR = Phi( (SR - SR_ref) / sqrt(Var(SR)) )

    Por construcción vale exactamente 0.5 cuando SR == SR_ref, para
    cualquier n, skew y kurt: la incertidumbre no mueve el punto medio,
    solo la pendiente con que se sale de él.

    PRECONDICIÓN (2-sep-2026): `sr` es el Sharpe POR PERÍODO — la unidad
    de `var_sharpe`. Dos de tres llamadores del proyecto rompieron ese
    contrato pasando el anualizado (z inflado por √252), así que el
    contrato ahora se hace cumplir: un |Sharpe| por período mayor que
    `SHARPE_PERIODO_MAXIMO` no ocurre en datos diarios reales (equivale a
    un t de Student de 3·√n) y delata un anualizado.
    """
    _exigir_por_periodo(sr, "psr")
    return Phi((sr - sr_ref) / se_sharpe(sr, n, skew, kurt))


# ------------------------------------------------------------
# Deflated Sharpe Ratio (Bailey & LdP 2014)
# ------------------------------------------------------------
def sr0_deflacionado(N_intentos: int, V_intentos: float) -> float:
    """Umbral del Deflated Sharpe: el Sharpe que se esperaría del MEJOR de
    `N_intentos` estrategias sin habilidad ninguna.

        SR0 = sqrt(V) * [ (1-γ)·Φ⁻¹(1 - 1/N) + γ·Φ⁻¹(1 - 1/(N·e)) ]

    `N_intentos` NO TIENE VALOR POR DEFECTO, y es deliberado: un DSR
    calculado con un N que alguien olvidó actualizar **miente, y miente
    hacia arriba** — declara habilidad donde solo hubo búsqueda. Obligar a
    escribir el número en cada llamada es la única defensa barata contra
    ese olvido. Se cuentan TODOS los intentos: las seis baselines B0→B5 y
    cada configuración del retador evaluada (§6.1 V5).

    `V_intentos` es la varianza de los Sharpe ENTRE intentos: cuanto más
    dispersos, más alto puede llegar el mejor por puro azar.

    Con N < 2 no hay selección que deflactar y SR0 = 0 por definición; el
    DSR se reduce entonces al PSR contra cero.
    """
    N = int(N_intentos)
    if N < 1:
        raise ValueError("N_intentos debe ser >= 1")
    if float(V_intentos) < 0:
        raise ValueError("V_intentos no puede ser negativa")
    if N < 2:
        return 0.0
    return math.sqrt(float(V_intentos)) * (
        (1.0 - GAMMA) * Phi_inv(1.0 - 1.0 / N)
        + GAMMA * Phi_inv(1.0 - 1.0 / (N * math.e)))


def dsr(sr: float, n: int, skew: float, kurt: float,
        N_intentos: int, V_intentos: float) -> float:
    """Deflated Sharpe Ratio: PSR contra el umbral deflactado por el número
    de intentos. La barra del diseño es DSR >= 0.95 (§6.1 V5)."""
    return psr(sr, sr0_deflacionado(N_intentos, V_intentos), n, skew, kurt)


# ------------------------------------------------------------
# Bootstrap circular de bloques (Politis & Romano 1994)
# ------------------------------------------------------------
PERIODOS_POR_ANIO = 252
SHARPE_PERIODO_MAXIMO = 3.0   # por encima, casi seguro alguien pasó un Sharpe anualizado


class ErrorUnidadSharpe(ValueError):
    """El Sharpe que llegó a psr/dsr no está en la unidad por período."""


def _exigir_por_periodo(sr: float, quien: str) -> None:
    if sr == sr and abs(sr) > SHARPE_PERIODO_MAXIMO:
        raise ErrorUnidadSharpe(
            f"{quien}: |Sharpe| = {abs(sr):.3f} no es un Sharpe por período (máximo plausible "
            f"{SHARPE_PERIODO_MAXIMO}); ¿se pasó el anualizado? Usar inferencia.sharpe(serie, anualizar=1).")


def anualizar_sharpe(sr_periodo: float, periodos: int = PERIODOS_POR_ANIO) -> float:
    """Sharpe por período → anualizado (sólo para REPORTAR: la inferencia
    —psr, dsr, var_sharpe— trabaja siempre por período)."""
    return sr_periodo * math.sqrt(periodos)


def sharpe(serie, anualizar: int = 252) -> float:
    """Sharpe muestral de una serie de retornos (en las unidades en que
    venga: no se reescala nada). `anualizar=1` deja el Sharpe por período,
    que es la unidad en que trabaja var_sharpe."""
    r = np.asarray(serie, dtype=float)
    r = r[~np.isnan(r)]
    if len(r) < 2:
        return float("nan")
    sd = r.std(ddof=1)
    if sd == 0:
        return float("nan")
    return float(r.mean() / sd * math.sqrt(anualizar))


def _remuestrear_circular(r: "np.ndarray", semilla: int, n_draws: int,
                          bloque: int) -> "np.ndarray":
    """El remuestreo CIRCULAR de bloques, compartido por los estimadores.

    Vive aparte para que `bootstrap_bloques` (IC del Sharpe) y
    `bootstrap_media` (IC de la media) usen EXACTAMENTE el mismo sorteo
    con la misma semilla: si divergieran, dos intervalos del mismo dato
    dejarían de ser comparables sin que nadie lo notara.
    """
    n = len(r)
    rng = np.random.default_rng(semilla)
    n_bloques = int(math.ceil(n / bloque))
    inicios = rng.integers(0, n, size=(n_draws, n_bloques))
    desplaz = np.arange(bloque)
    idx = (inicios[:, :, None] + desplaz[None, None, :]) % n
    return r[idx.reshape(n_draws, -1)[:, :n]]


def bootstrap_media(serie, semilla: int, n_draws: int = 1000,
                    bloque: int = 20, alpha: float = 0.05) -> dict:
    """IC de la MEDIA por bootstrap circular de bloques.

    ============================================================
    POR QUÉ EXISTE (hallazgo del WS5)
    ============================================================
    `bootstrap_bloques` devuelve el IC del SHARPE (media/desv). Usarlo
    para acompañar una diferencia de MAE —como hacía `comparar` desde el
    WS2b— imprime un intervalo en escala ESTANDARIZADA junto a un punto
    estimado en **pp**. Se ve a simple vista: en 8 de 12 pares del WS5 el
    punto estimado caía FUERA de su propio intervalo.

    La DECISIÓN no cambiaba —«el IC excluye el cero» es exactamente
    equivalente en ambas escalas, porque `sd > 0` conserva el signo réplica
    a réplica y el evento depende solo de la proporción de réplicas sobre
    cero—, pero el número impreso no era el intervalo de lo que decía ser.

    Comparte el sorteo con `bootstrap_bloques`: misma semilla, mismos
    bloques, mismas réplicas.
    """
    r = np.asarray(serie, dtype=float)
    r = r[~np.isnan(r)]
    n = len(r)
    if bloque < 1:
        raise ValueError("bloque debe ser >= 1")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha debe estar en (0,1)")
    if n < 2 or n < bloque:
        return {"n": n, "media": float("nan"), "lo": float("nan"),
                "hi": float("nan"), "bloque": bloque, "alpha": alpha,
                "semilla": semilla}
    medias = _remuestrear_circular(r, semilla, n_draws, bloque).mean(axis=1)
    return {
        "n": n, "media": float(r.mean()),
        "lo": float(np.quantile(medias, alpha / 2.0)),
        "hi": float(np.quantile(medias, 1.0 - alpha / 2.0)),
        "bloque": bloque, "alpha": alpha, "semilla": semilla,
    }


def bootstrap_bloques(serie, semilla: int, n_draws: int = 1000,
                      bloque: int = 20, alpha: float = 0.05,
                      anualizar: int = 252) -> dict:
    """IC del Sharpe por bootstrap CIRCULAR de bloques.

    Remuestrea bloques contiguos de largo `bloque` para preservar el
    clustering de volatilidad y la autocorrelación que un bootstrap iid
    destruiría — y que, destruidas, producen intervalos demasiado
    estrechos. Con `bloque=1` degenera exactamente en el bootstrap iid,
    lo que hace la comparación entre ambos trivial de escribir.

    CIRCULAR: los bloques envuelven por el final de la serie. Sin eso, las
    últimas `bloque-1` observaciones no pueden iniciar ningún bloque y la
    cola queda sistemáticamente submuestreada.

    `semilla` es OBLIGATORIA y explícita: nada de estado global de numpy.
    Dos corridas con la misma semilla dan el mismo intervalo, que es lo
    mínimo exigible a un número que va a decidir si un modelo gana.
    """
    r = np.asarray(serie, dtype=float)
    r = r[~np.isnan(r)]
    n = len(r)
    if bloque < 1:
        raise ValueError("bloque debe ser >= 1")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha debe estar en (0,1)")
    if n < 2 or n < bloque:
        return {"n": n, "sharpe": float("nan"), "lo": float("nan"),
                "hi": float("nan"), "n_validos": 0, "bloque": bloque,
                "alpha": alpha, "semilla": semilla}

    muestras = _remuestrear_circular(r, semilla, n_draws, bloque)

    sd = muestras.std(axis=1, ddof=1)
    validas = sd > 0
    sh = np.full(n_draws, np.nan)
    sh[validas] = (muestras[validas].mean(axis=1) / sd[validas]
                   * math.sqrt(anualizar))
    sh = sh[~np.isnan(sh)]
    if len(sh) == 0:
        return {"n": n, "sharpe": sharpe(r, anualizar), "lo": float("nan"),
                "hi": float("nan"), "n_validos": 0, "bloque": bloque,
                "alpha": alpha, "semilla": semilla}
    return {
        "n": n,
        "sharpe": sharpe(r, anualizar),
        "lo": float(np.quantile(sh, alpha / 2.0)),
        "hi": float(np.quantile(sh, 1.0 - alpha / 2.0)),
        "n_validos": int(len(sh)),
        "bloque": bloque, "alpha": alpha, "semilla": semilla,
    }
