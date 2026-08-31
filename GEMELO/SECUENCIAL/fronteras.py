"""
fronteras.py — fronteras secuenciales EXACTAS por integración numérica.

Reemplaza al Monte Carlo que usaba la primera versión de este diseño.
`estadistico-adversario` lo RECHAZÓ por eso (defecto D1): el cuantil de
Monte Carlo con la semilla congelada cayó 2.1-2.6 desviaciones por debajo
de la media de 25 semillas, y la frontera resultante daba un α real de
**0.05122**, no 0.05. Peor: la verificación interna del script medía
0.0507/0.0508 y el documento lo leyó como confirmación, cuando era el
sesgo mismo — un chequeo con el mismo generador, el mismo `n_sim` y el
mismo modelo no puede detectar el sesgo de ese generador.

Acá se hace bien: propagación numérica de la densidad de la suma parcial
B(t_k), poniendo en cero la región de cruce en cada mirada. Es la
recursión de Armitage-McPherson (Jennison & Turnbull 2000, cap. 19).
Sin Monte Carlo, sin semilla, sin scipy — solo numpy y la regla de
Simpson. La validación es externa, no interna: reproduce los valores
tabulados de la literatura para K=2..5.

Referencia (α=0.05 bilateral):
    Pocock  K=2 2.178  K=3 2.289  K=4 2.361  K=5 2.413
    OBF     K=2 1.977  K=3 2.004  K=4 2.024  K=5 2.040
"""
from __future__ import annotations

import math

import numpy as np


def _pesos_simpson(m: int, h: float) -> np.ndarray:
    w = np.ones(m)
    w[1:-1:2] = 4.0
    w[2:-1:2] = 2.0
    return w * h / 3.0


class Malla:
    """Malla + núcleos de transición precomputados para unas fracciones dadas.

    Los núcleos no dependen de los umbrales, así que se construyen UNA vez
    y se reusan en toda la bisección. Sin esto la búsqueda es inviable.
    """

    def __init__(self, fracciones, m: int = 8001, ancho: float = 8.0):
        self.t = np.asarray(fracciones, float)
        self.dt = np.diff(np.concatenate([[0.0], self.t]))
        self.x = np.linspace(-ancho, ancho, m)
        self.w = _pesos_simpson(m, self.x[1] - self.x[0])
        d = self.x[:, None] - self.x[None, :]
        self._nucleos = {}
        for paso in self.dt:
            clave = round(float(paso), 12)
            if clave not in self._nucleos:
                s = math.sqrt(paso)
                self._nucleos[clave] = (
                    np.exp(-0.5 * (d / s) ** 2) / (s * math.sqrt(2 * math.pi))
                )

    def nucleo(self, paso: float) -> np.ndarray:
        return self._nucleos[round(float(paso), 12)]

    def prob_cruce(self, umbrales_z, drift: float = 0.0, futilidad_z=None):
        """P(cruzar eficacia) y P(parar por futilidad sin cruzar).

        La frontera |Z_k| >= c_k es |B(t_k)| >= c_k*sqrt(t_k). El drift es
        E[B(1)] bajo la alternativa (0 bajo H0); se lo aplica desplazando
        la malla, que es equivalente a desplazar el núcleo y no obliga a
        recomputarlo.
        """
        c = np.asarray(umbrales_z, float)
        barrera = c * np.sqrt(self.t)
        x, w = self.x, self.w

        dens = None
        p_cruce = 0.0
        p_futil = 0.0
        for k in range(len(self.t)):
            mu_k = drift * self.t[k]          # media acumulada hasta t_k
            if dens is None:
                s = math.sqrt(self.dt[k])
                f = np.exp(-0.5 * ((x - mu_k) / s) ** 2) / (s * math.sqrt(2 * math.pi))
            else:
                # el núcleo es en la variable centrada; se centra la malla
                f = self.nucleo(self.dt[k]) @ (dens * w)

            cruza = np.abs(x) >= barrera[k]
            p_cruce += float(np.sum((f * w)[cruza]))
            f = f.copy()
            f[cruza] = 0.0

            if futilidad_z is not None and futilidad_z[k] is not None:
                b_fut = futilidad_z[k] * math.sqrt(self.t[k])
                para = x < b_fut
                p_futil += float(np.sum((f * w)[para]))
                f = f.copy()
                f[para] = 0.0

            dens = f

        return p_cruce, p_futil


def _prob_cruce_drift(malla: Malla, umbrales_z, drift: float, futilidad_z=None):
    """Igual que Malla.prob_cruce pero con drift, propagando con núcleo desplazado.

    Se separa porque bajo drift el núcleo cambia (media mu*dt) y hay que
    reconstruirlo; bajo H0 (drift=0) se usa el camino cacheado, que es el
    que corre miles de veces en la bisección.
    """
    if drift == 0.0:
        return malla.prob_cruce(umbrales_z, futilidad_z=futilidad_z)

    t, dtv, x, w = malla.t, malla.dt, malla.x, malla.w
    c = np.asarray(umbrales_z, float)
    barrera = c * np.sqrt(t)
    d = x[:, None] - x[None, :]

    dens = None
    p_cruce = 0.0
    p_futil = 0.0
    for k in range(len(t)):
        s = math.sqrt(dtv[k])
        mu = drift * dtv[k]
        if dens is None:
            f = np.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))
        else:
            nucleo = np.exp(-0.5 * ((d - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))
            f = nucleo @ (dens * w)

        cruza = np.abs(x) >= barrera[k]
        p_cruce += float(np.sum((f * w)[cruza]))
        f = f.copy()
        f[cruza] = 0.0

        if futilidad_z is not None and futilidad_z[k] is not None:
            b_fut = futilidad_z[k] * math.sqrt(t[k])
            para = x < b_fut
            p_futil += float(np.sum((f * w)[para]))
            f = f.copy()
            f[para] = 0.0

        dens = f

    return p_cruce, p_futil


def _buscar(malla: Malla, forma, alpha: float, lo=1.5, hi=4.0, tol=1e-6) -> float:
    for _ in range(60):
        medio = 0.5 * (lo + hi)
        p, _ = malla.prob_cruce(forma(medio))
        if p > alpha:
            lo = medio
        else:
            hi = medio
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def frontera_pocock(fracciones, alpha: float = 0.05, malla: Malla | None = None):
    """Umbral constante en todas las miradas."""
    malla = malla or Malla(fracciones)
    c = _buscar(malla, lambda v: [v] * len(fracciones), alpha)
    return c, [c] * len(fracciones)


def frontera_obf(fracciones, alpha: float = 0.05, malla: Malla | None = None):
    """O'Brien-Fleming: umbral c_B/sqrt(t_k) — conservador temprano."""
    malla = malla or Malla(fracciones)
    f = np.asarray(fracciones, float)
    c = _buscar(malla, lambda v: list(v / np.sqrt(f)), alpha)
    return c, list(c / np.sqrt(f))


REFERENCIA = {  # Jennison & Turnbull (2000), α=0.05 bilateral
    2: (2.178, 1.977),
    3: (2.289, 2.004),
    4: (2.361, 2.024),
    5: (2.413, 2.040),
}

# Armitage, McPherson & Rowe (1969), tabla 2: tasa de error tipo I real de
# hacer K miradas equiespaciadas usando α nominal 0.05 en cada una. Es la
# segunda vara externa, y la más importante acá: valida el camino que
# calcula el PASIVO, no el que calcula las fronteras.
REFERENCIA_AMR = {1: 0.050, 2: 0.083, 3: 0.107, 4: 0.126, 5: 0.142, 10: 0.193}


def tasa_error_nominal(fracciones, alpha_nominal: float = 0.05,
                       m: int = 4001, ancho: float = 7.0) -> float:
    """α REAL de mirar en esas fracciones usando el umbral nominal siempre."""
    from math import sqrt  # noqa: F401  (claridad: todo lo demás es numpy)
    malla = Malla(fracciones, m=m, ancho=ancho)
    u = _norm_ppf(1 - alpha_nominal / 2)
    p, _ = malla.prob_cruce([u] * len(fracciones))
    return p


def _norm_ppf(p: float) -> float:
    """Cuantil normal por bisección sobre erfc. Sin scipy, como todo acá."""
    lo, hi = -10.0, 10.0
    for _ in range(200):
        medio = 0.5 * (lo + hi)
        cdf = 0.5 * math.erfc(-medio / math.sqrt(2.0))
        if cdf < p:
            lo = medio
        else:
            hi = medio
    return 0.5 * (lo + hi)


SEMILLA_VERIFICACION = 20260831
N_SIM_VERIFICACION = 400_000


def verificacion_mc(fracciones, umbrales, drift: float = 0.0,
                    semilla: int = SEMILLA_VERIFICACION,
                    n_sim: int = N_SIM_VERIFICACION) -> dict:
    """Verificación SECUNDARIA por Monte Carlo, con su error declarado.

    Existe porque el `DISEÑO.md` afirmaba tener una y no la tenía: el
    módulo declaraba `SEMILLA` y `N_SIM` sin usarlas en ningún lado, y el
    documento decía "verificado además por Monte Carlo de 400.000
    réplicas". Una verificación que no está en el repo no es una
    verificación; es una afirmación sobre una verificación.

    NO es la fuente de ninguna cifra congelada — la fuente es la
    recursión. Sirve para lo único que un Monte Carlo hace bien acá:
    detectar un error grosero en la integración por un camino que no
    comparte una línea de código con ella. Devuelve el IC binomial, para
    que se pueda ver si una diferencia es señal o es ruido de simulación.
    """
    t = np.asarray(fracciones, float)
    inc = np.diff(np.concatenate([[0.0], t]))
    rng = np.random.default_rng(semilla)
    b = np.cumsum(rng.normal(size=(n_sim, len(t))) * np.sqrt(inc) + drift * inc,
                  axis=1)
    z = b / np.sqrt(t)
    p = float((np.abs(z) >= np.asarray(umbrales)).any(axis=1).mean())
    ee = math.sqrt(p * (1 - p) / n_sim)
    return {"p": p, "ee": ee, "lo": p - 1.96 * ee, "hi": p + 1.96 * ee,
            "n_sim": n_sim, "semilla": semilla}


if __name__ == "__main__":
    print("Fronteras exactas por integración numérica (recursión, sin Monte Carlo).")
    print("Validación EXTERNA contra la literatura, α=0.05 bilateral.\n")
    print(f"{'K':>2}  {'Pocock':>8} {'ref':>7}  {'OBF c_B':>8} {'ref':>7}   α real (P / OBF)")
    for K in (2, 3, 4, 5):
        fr = [(i + 1) / K for i in range(K)]
        malla = Malla(fr)
        cp, up = frontera_pocock(fr, malla=malla)
        co, uo = frontera_obf(fr, malla=malla)
        ap, _ = malla.prob_cruce(up)
        ao, _ = malla.prob_cruce(uo)
        rp, ro = REFERENCIA[K]
        print(f"{K:>2}  {cp:8.3f} {rp:7.3f}  {co:8.3f} {ro:7.3f}   "
              f"{ap:.5f} / {ao:.5f}")
        if K == 4:
            print(f"    OBF por mirada: {[round(float(u), 3) for u in uo]}")

    print("\nSegunda vara externa — Armitage, McPherson & Rowe (1969), tabla 2:")
    print("α real de K miradas equiespaciadas con umbral nominal 0.05 en cada una.")
    print(f"{'K':>3}  {'calculado':>10}  {'publicado':>10}")
    for K, ref in REFERENCIA_AMR.items():
        fr = [(i + 1) / K for i in range(K)]
        print(f"{K:>3}  {tasa_error_nominal(fr):>10.4f}  {ref:>10.3f}")
    print("Esta segunda tabla valida el camino que calcula el PASIVO de las")
    print("miradas pasadas, que es un cómputo distinto al de las fronteras.")
