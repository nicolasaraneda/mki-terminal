"""Simulador del proceso generador de la ventana sellada, con verdad conocida.

Frente A de la octava corrida (2-sep-2026). PROPUESTA hasta el dictamen del
`estadistico-adversario`. Pre-registro: `GEMELO/preregistro/frente_A.md`.

    gap_{i,d} = μ_i + β_i·(b·S_d + c·U_d) + σ_i·ε_{i,d}

- S_d: el retorno del SOX que el modelo VE (t de Student, ν grados, escala
  calibrada a la desviación del `sox_usado_pct` sellado).
- U_d: un shock de día que el modelo NO ve; induce dependencia dentro del
  día que no es la mecánica del campeón (c lo escala).
- ε_{i,d}: innovación idiosincrática con colas (t de Student).
- Predicción del campeón: p_{i,d} = β_i·S_d. Baseline: «siempre al alza».
- b fija la INFORMACIÓN: la ventaja direccional δ(b) = E[acierto_modelo −
  acierto_base] se obtiene por bisección para el δ pedido. b = 0 NO es
  δ = 0 (con deriva positiva, un llamado independiente del gap pierde
  contra «siempre al alza»); δ = 0 es el b en que los llamados a la baja
  aciertan la mitad de las veces.

Nada de esto lee el sello salvo `calibrar_desde_sellado()`, que toma
parámetros (β, μ, σ por ticker; tamaños de clúster por fecha; escala del
SOX) de las filas selladas en `mode=ro` vía `backtest.linea_base`, y los
sella en un dict para que el `.json` de resultados los declare.
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

NU = 4                  # grados de libertad de las t (colas)
SEMILLA = 20260902


@dataclass
class Parametros:
    tickers: list
    beta: dict            # β_i
    mu: dict              # μ_i (deriva del gap, pp)
    sigma: dict           # σ_i: desviación TOTAL del gap por ticker (pp), leída del sello
    escala_sox: float     # escala de S_d (pp)
    tamanos: list         # tamaño de clúster por fecha (lista de ints)
    b: float = 1.0        # información del SOX en el gap
    c: float = 0.0        # shock de día no visto por el modelo (pp)
    nu: int = NU
    rho: float = 0.0      # AR(1) de los factores de día S y U (0 = iid entre días, lo publicado)
    fuente: dict = field(default_factory=dict)

    def como_dict(self) -> dict:
        d = self.__dict__.copy()
        d["tamanos"] = list(map(int, self.tamanos))
        return d


def _t(rng, size, nu):
    """t de Student estandarizada a varianza 1 (nu > 2)."""
    return rng.standard_t(nu, size=size) / math.sqrt(nu / (nu - 2))


PISO_IDIOSINCRATICO = 0.30   # fracción mínima de la desviación total que queda idiosincrática


def _ar1(e: np.ndarray, rho: float) -> np.ndarray:
    """Filtro AR(1) con varianza marginal conservada: x_t = ρ·x_{t−1} +
    √(1−ρ²)·e_t. Con ρ = 0 devuelve `e` tal cual. Existe porque el DGP
    publicado era iid entre días —la intercambiabilidad que los dos
    instrumentos titulares necesitan— y el adversario exigió medir qué
    pasa cuando no lo es (AC1 real = −0,13 ± 0,17: ρ = 0,2 es compatible)."""
    if not rho:
        return e
    x = np.empty_like(e)
    x[0] = e[0]
    a = math.sqrt(1 - rho * rho)
    for t in range(1, len(e)):
        x[t] = rho * x[t - 1] + a * e[t]
    return x


def sigma_idiosincratica(p: Parametros) -> dict:
    """La desviación TOTAL del gap sellado ya contiene la parte común
    (β·S y el shock de día). Para que el gap simulado tenga la misma
    varianza marginal que el real, la escala idiosincrática es lo que queda
    después de descontar la común: √(σ_total² − β²(b²·esc_S² + c²)), con un
    piso para que no se anule (si b o c son grandes, el piso es lo que
    limita el ICC alcanzable — se declara)."""
    out = {}
    for t in p.tickers:
        comun = p.beta[t] ** 2 * (p.b ** 2 * p.escala_sox ** 2 + p.c ** 2)
        resto = max(p.sigma[t] ** 2 - comun, (PISO_IDIOSINCRATICO * p.sigma[t]) ** 2)
        out[t] = math.sqrt(resto)
    return out


def simular(p: Parametros, n_dias: int, rng: np.random.Generator,
            ruido_sesion: float = 1.0) -> pd.DataFrame:
    """Una ventana sintética de `n_dias` fechas (vectorizada). Los tamaños de
    clúster se toman cíclicamente de `p.tamanos`; en una fecha con tamaño
    < 8 los tickers presentes se sortean. Devuelve el mismo esquema de
    columnas que las filas selladas que consumen `bifurcaciones.aplicar` y
    `linea_base.duelo`. El «retorno de sesión» sintético es el gap más un
    ruido idiosincrático adicional de escala `ruido_sesion`·σ_idio (la
    sesión es más ruidosa que el gap; en lo real 60,9% vs 66,1% de acierto)."""
    T = list(p.tickers)
    m = len(T)
    beta = np.array([p.beta[t] for t in T])
    mu = np.array([p.mu[t] for t in T])
    sig = np.array([sigma_idiosincratica(p)[t] for t in T])
    S = _ar1(_t(rng, n_dias, p.nu), p.rho) * p.escala_sox
    U = _ar1(_t(rng, n_dias, p.nu), p.rho)
    eps = _t(rng, (n_dias, m), p.nu)
    eps2 = _t(rng, (n_dias, m), p.nu)
    gap = mu[None, :] + beta[None, :] * (p.b * S[:, None] + p.c * U[:, None]) + sig[None, :] * eps
    pred = beta[None, :] * S[:, None]
    ret = gap + ruido_sesion * sig[None, :] * eps2
    tam = np.array([p.tamanos[i % len(p.tamanos)] for i in range(n_dias)])
    presente = np.ones((n_dias, m), dtype=bool)
    for d in np.where(tam < m)[0]:
        fuera = rng.choice(m, size=m - tam[d], replace=False)
        presente[d, fuera] = False
    dias, cols = np.where(presente)
    df = pd.DataFrame({"dia": dias, "ticker": np.array(T)[cols],
                       "apertura_estimada_pct": pred[dias, cols],
                       "gap_pct": gap[dias, cols], "sox": S[dias],
                       "retorno_real_pct": ret[dias, cols]})
    df["acierto_gap"] = ((df["apertura_estimada_pct"] >= 0) == (df["gap_pct"] >= 0)).astype(int)
    df["error_gap_pp"] = (df["apertura_estimada_pct"] - df["gap_pct"]).abs()
    df["acierto_direccion"] = ((df["apertura_estimada_pct"] >= 0) == (df["retorno_real_pct"] >= 0)).astype(int)
    df["error_pp"] = (df["apertura_estimada_pct"] - df["retorno_real_pct"]).abs()
    return df


def ventaja(df: pd.DataFrame) -> float:
    """δ observado con la convención `excluir_cero`: E[acierto_modelo − acierto_base]."""
    d = df[df["gap_pct"] != 0]
    base = (d["gap_pct"] > 0).astype(int)
    return float((d["acierto_gap"] - base).mean())


def ventaja_esperada(p: Parametros, n_dias: int = 40000, semilla: int = SEMILLA) -> float:
    """δ(b) por Monte Carlo grande (error ~0,15 pp con 40.000 días)."""
    rng = np.random.default_rng(semilla)
    return ventaja(simular(p, n_dias, rng))


def calibrar_b(p: Parametros, delta_objetivo: float, n_dias: int = 40000,
               tol: float = 0.0015, semilla: int = SEMILLA) -> float:
    """Bisección sobre b para que δ(b) = delta_objetivo (fracción). δ es
    monótona creciente en b. Devuelve b; NO modifica p."""
    lo, hi = 0.0, 4.0
    q = Parametros(**{**p.__dict__})
    for _ in range(40):
        mid = (lo + hi) / 2
        q.b = mid
        v = ventaja_esperada(q, n_dias, semilla)
        if abs(v - delta_objetivo) < tol:
            return mid
        if v < delta_objetivo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def icc_de_aciertos(df: pd.DataFrame) -> dict:
    """ICC y DEFF de la diferencia pareada por día, con la misma función que
    el proyecto usa sobre la ventana real (`bifurcaciones.icc_y_deff`)."""
    from GEMELO import bifurcaciones as bf
    d = df[df["gap_pct"] != 0].copy()
    d["fecha"] = d["dia"]
    base = (d["gap_pct"] > 0).astype(int)
    vals = (d["acierto_gap"] - base).to_numpy(dtype=float)
    return bf.icc_y_deff(bf._por_dia(d, vals))


def calibrar_desde_sellado(hasta_sello: str | None = None) -> Parametros:
    """Parámetros leídos de las filas selladas (mode=ro vía linea_base):
    β_i media, μ_i y σ_i del gap por ticker, escala del SOX sellado,
    tamaños de clúster por fecha. b y c quedan en 1 y 0: se calibran aparte."""
    from backtest import linea_base as lb
    corte = hasta_sello or lb.CORTE_REGLA_FIRMADA
    df = lb.aplicar_convencion(lb.cargar(hasta_sello=corte), lb.CONVENCION_OFICIAL)
    g = df.groupby("ticker")
    tickers = sorted(df["ticker"].unique())
    sox = df.drop_duplicates("fecha")["sox_usado_pct"].dropna()
    return Parametros(
        tickers=tickers,
        beta={t: float(g["beta"].mean()[t]) for t in tickers},
        mu={t: float(g["gap_pct"].mean()[t]) for t in tickers},
        sigma={t: float(g["gap_pct"].std()[t]) for t in tickers},
        escala_sox=float(sox.std()),
        tamanos=[int(x) for x in df.groupby("fecha").size().tolist()],
        fuente={"hasta_sello": corte, "n": int(len(df)), "dias": int(df["fecha"].nunique()),
                "convencion": lb.CONVENCION_OFICIAL, "fechas_con_sox": int(len(sox))},
    )


def calibrar_c(p: Parametros, icc_objetivo: float, n_dias: int = 3000,
               semilla: int = SEMILLA) -> float:
    """Bisección sobre c (shock de día no visto) para que el ICC de los
    aciertos reproduzca el medido. A b fijo. Devuelve c; NO modifica p."""
    lo, hi = 0.0, 12.0
    q = Parametros(**{**p.__dict__})
    for _ in range(30):
        mid = (lo + hi) / 2
        q.c = mid
        icc = icc_de_aciertos(simular(q, n_dias, np.random.default_rng(semilla)))["icc"]
        if abs(icc - icc_objetivo) < 0.005:
            return mid
        if icc < icc_objetivo:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def calibrar(p: Parametros, delta_objetivo: float, icc_objetivo: float,
             vueltas: int = 3) -> Parametros:
    """Calibración alternada: c para el ICC a b fijo, b para δ a c fijo,
    `vueltas` veces. Devuelve una COPIA calibrada; no toca `p`."""
    q = Parametros(**{**p.__dict__})
    for _ in range(vueltas):
        q.c = calibrar_c(q, icc_objetivo)
        q.b = calibrar_b(q, delta_objetivo)
    return q
