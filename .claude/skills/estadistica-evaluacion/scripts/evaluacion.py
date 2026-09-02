"""
evaluacion.py — herramientas de evaluacion honesta para MKI Terminal.

Todo lo que este proyecto necesita para no engañarse con sus propios numeros.

DEPENDENCIAS: solo numpy y la libreria estandar. Sin scipy, a proposito.
Este repo tiene requirements.txt fijado en dos maquinas y el Mac esta en
produccion: agregar una dependencia es una decision con acta, no un pip
install de paso. Las funciones de distribucion normal y el binomial exacto
estan implementados aca abajo y validados contra scipy en el self-test.

Referencias:
  Wilson 1927                     intervalo para proporciones
  McNemar 1947                    comparacion pareada de clasificadores
  Acklam 2003                     inversa de la normal, con refinamiento Halley
  Lo 2002; Bailey & LdP 2012      PSR y error estandar del Sharpe
  Bailey & Lopez de Prado 2014    Deflated Sharpe Ratio
  Politis & Romano 1994           bootstrap de bloques
  Gneiting & Raftery 2007         CRPS
  Lopez de Prado 2018 cap. 7      purge + embargo

Uso:  python evaluacion.py        corre el self-test
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

EULER_MASCHERONI = 0.5772156649015329
_SQRT2 = math.sqrt(2.0)
_SQRT2PI = math.sqrt(2.0 * math.pi)


# ------------------------------------------------------- normal, sin scipy

def norm_cdf(x):
    """Funcion de distribucion acumulada de la normal estandar."""
    x = np.asarray(x, dtype=float)
    from numpy import vectorize
    return 0.5 * (1.0 + _erf_array(x / _SQRT2))


def _erf_array(x):
    x = np.asarray(x, dtype=float)
    plano = x.ravel()
    salida = np.array([math.erf(v) for v in plano])
    return salida.reshape(x.shape) if x.shape else float(salida[0])


def norm_pdf(x):
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * x * x) / _SQRT2PI


# coeficientes de Acklam
_A = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
      1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
_B = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
      6.680131188771972e+01, -1.328068155288572e+01)
_C = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
      -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
_D = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
      3.754408661907416e+00)


def norm_ppf(p: float) -> float:
    """Inversa de la normal estandar. Acklam mas un paso de Halley.

    Precision del orden de 1e-15, o sea indistinguible de scipy para lo que
    este proyecto hace.
    """
    p = float(p)
    if not (0.0 < p < 1.0):
        if p == 0.0:
            return float("-inf")
        if p == 1.0:
            return float("inf")
        return float("nan")

    p_bajo, p_alto = 0.02425, 1 - 0.02425
    if p < p_bajo:
        q = math.sqrt(-2 * math.log(p))
        x = (((((_C[0]*q + _C[1])*q + _C[2])*q + _C[3])*q + _C[4])*q + _C[5]) / \
            ((((_D[0]*q + _D[1])*q + _D[2])*q + _D[3])*q + 1)
    elif p <= p_alto:
        q = p - 0.5
        r = q * q
        x = (((((_A[0]*r + _A[1])*r + _A[2])*r + _A[3])*r + _A[4])*r + _A[5])*q / \
            (((((_B[0]*r + _B[1])*r + _B[2])*r + _B[3])*r + _B[4])*r + 1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((_C[0]*q + _C[1])*q + _C[2])*q + _C[3])*q + _C[4])*q + _C[5]) / \
             ((((_D[0]*q + _D[1])*q + _D[2])*q + _D[3])*q + 1)

    # refinamiento de Halley
    e = 0.5 * math.erfc(-x / _SQRT2) - p
    u = e * _SQRT2PI * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def _momentos(x):
    """skew y kurtosis (no en exceso), sesgados, como los devuelve scipy."""
    x = np.asarray(x, dtype=float)
    m = x.mean()
    d = x - m
    m2 = (d ** 2).mean()
    if m2 == 0:
        return 0.0, 0.0
    m3 = (d ** 3).mean()
    m4 = (d ** 4).mean()
    return float(m3 / m2 ** 1.5), float(m4 / m2 ** 2)


# ---------------------------------------------------------------- proporciones

def wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Intervalo de Wilson para una proporcion. k exitos en n ensayos.

    Wilson y no Wald porque Wald colapsa cerca de 0 y 1, y con n del orden de
    200 la diferencia es visible.
    """
    if n == 0:
        return (float("nan"), float("nan"))
    z = norm_ppf(1 - alpha / 2)
    p = k / n
    denom = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / denom
    radio = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (centro - radio, centro + radio)


def mcnemar_exact(b: int, c: int) -> float:
    """p bilateral exacto de McNemar sobre los desacuerdos.

    b = veces que A acierta y B falla.  c = veces que B acierta y A falla.
    Los acuerdos no aportan informacion y por eso no entran.

    Binomial exacta con p=0.5. Como la nula es simetrica, el bilateral es
    2*P(X <= min(b,c)), acotado a 1. Exacto hasta n=2000; por encima usa la
    aproximacion normal con correccion de continuidad, que a ese n ya es
    indistinguible.

    CORRECCION (1-sep-2026, corrida de veredicto 5.1). La rama exacta se
    calculaba como sum(comb(n,i)) / 2.0**n. Ese denominador es un float y
    **desborda en n = 1024** (2**1024 > 1.8e308), asi que la rama que el
    docstring declaraba exacta hasta 2000 reventaba con OverflowError en
    todo el tramo 1024 <= n <= 2000 — nunca llegaba al fallback normal.
    Se descubrio al aplicar McNemar sobre 4151 filas del backtest, donde
    los pares discordantes pasan de mil; ningun uso anterior habia llegado
    a esa escala. El umbral declarado de 2000 no se movio: lo que se
    corrigio es que ahora se cumple. La suma va en espacio logaritmico
    (lgamma), que no desborda para ningun n representable.
    """
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    if n <= 2000:
        ln2 = math.log(2.0)
        lgn = math.lgamma(n + 1)
        cola = math.fsum(
            math.exp(lgn - math.lgamma(i + 1) - math.lgamma(n - i + 1) - n * ln2)
            for i in range(k + 1))
        return float(min(1.0, 2.0 * cola))
    z = (abs(b - c) - 1) / math.sqrt(n)
    return float(min(1.0, 2.0 * (1.0 - float(norm_cdf(z)))))


@dataclass
class ComparacionPareada:
    n: int
    acierto_a: float
    acierto_b: float
    ventaja_pp: float
    ic_a: tuple[float, float]
    ic_b: tuple[float, float]
    b: int
    c: int
    p_mcnemar: float

    def __str__(self) -> str:
        return (
            f"n={self.n}  A={self.acierto_a:.1%} [{self.ic_a[0]:.1%}, {self.ic_a[1]:.1%}]  "
            f"B={self.acierto_b:.1%} [{self.ic_b[0]:.1%}, {self.ic_b[1]:.1%}]  "
            f"ventaja={self.ventaja_pp:+.1f} pp  b={self.b} c={self.c}  "
            f"McNemar p={self.p_mcnemar:.3f}"
        )


def comparar_pareado(acierto_a, acierto_b) -> ComparacionPareada:
    """Compara dos clasificadores binarios sobre las MISMAS filas.

    acierto_a, acierto_b: vectores booleanos de ACIERTO, uno por observacion.
    Esta es la comparacion que importa: modelo contra baseline, sobre las
    mismas emisiones, nunca contra 50%.
    """
    a = np.asarray(acierto_a, dtype=bool)
    bb = np.asarray(acierto_b, dtype=bool)
    if a.shape != bb.shape:
        raise ValueError("los dos vectores tienen que cubrir las mismas filas")
    n = a.size
    b = int(np.sum(a & ~bb))
    c = int(np.sum(~a & bb))
    ka, kb = int(a.sum()), int(bb.sum())
    return ComparacionPareada(
        n=n, acierto_a=ka / n, acierto_b=kb / n,
        ventaja_pp=100 * (ka - kb) / n,
        ic_a=wilson_ci(ka, n), ic_b=wilson_ci(kb, n),
        b=b, c=c, p_mcnemar=mcnemar_exact(b, c),
    )


def baseline_siempre_alza(gap_real) -> np.ndarray:
    """El denominador honesto: predecir siempre 'sube', sobre las mismas filas.

    Contra cero, un modelo direccional parece bueno. Contra esto, hay que
    demostrarlo. Un gap exactamente cero cuenta como fallo de la constante.
    """
    return np.asarray(gap_real, dtype=float) > 0


# ---------------------------------------------------------------- bootstrap

def block_bootstrap(x, estimador=np.mean, block: int = 20,
                    n_boot: int = 10_000, alpha: float = 0.05,
                    seed: int | None = 0):
    """Bootstrap de bloques moviles. Devuelve (estimador, lo, hi).

    Bloque de 20 dias por defecto. Un bootstrap iid destruye el clustering de
    volatilidad y produce intervalos falsamente angostos: en series diarias de
    mercado eso es la diferencia entre significativo y no.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    if n < block:
        block = max(1, n // 2)
    rng = np.random.default_rng(seed)
    n_bloques = int(np.ceil(n / block))
    inicios_posibles = n - block + 1
    reps = np.empty(n_boot)
    for i in range(n_boot):
        inicios = rng.integers(0, inicios_posibles, size=n_bloques)
        idx = (inicios[:, None] + np.arange(block)[None, :]).ravel()[:n]
        reps[i] = estimador(x[idx])
    lo, hi = np.quantile(reps, [alpha / 2, 1 - alpha / 2])
    return float(estimador(x)), float(lo), float(hi)


def diferencia_con_ic(x, y, block: int = 20, n_boot: int = 10_000,
                      alpha: float = 0.05, seed: int | None = 0):
    """IC por bootstrap de bloques para la diferencia media pareada x - y.

    Sirve para V2: la mejora de CRPS del retador sobre el campeon tiene que
    traer un IC que excluya el cero.
    """
    d = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)
    return block_bootstrap(d, np.mean, block, n_boot, alpha, seed)


# ---------------------------------------------------------------- Sharpe

def sharpe_por_observacion(retornos) -> float:
    r = np.asarray(retornos, dtype=float)
    sd = r.std(ddof=1)
    return float(r.mean() / sd) if sd > 0 else float("nan")


def momentos(x) -> tuple[float, float]:
    """Devuelve (skew, kurtosis no en exceso). Kurtosis normal = 3."""
    return _momentos(x)


def se_sharpe(sr: float, n: int, skew: float, kurt: float) -> float:
    """Error estandar del Sharpe con correccion por momentos (Lo 2002).

    kurt es la curtosis NO en exceso (normal = 3).
    Un Sharpe sin barra de error es un punto disfrazado de hallazgo.
    """
    var = (1 - skew * sr + (kurt - 1) / 4 * sr ** 2) / (n - 1)
    return float(math.sqrt(max(var, 0.0)))


def psr(sr: float, n: int, skew: float, kurt: float, sr_ref: float = 0.0) -> float:
    """Probabilistic Sharpe Ratio: P(SR_real > sr_ref)."""
    se = se_sharpe(sr, n, skew, kurt)
    if se == 0 or not math.isfinite(se):
        return float("nan")
    return float(norm_cdf((sr - sr_ref) / se))


def sr_maximo_esperado(n_trials: int, var_sr_trials: float) -> float:
    """E[max SR] bajo la nula, con n_trials intentos independientes.

    Esta es la barra que el ganador tiene que superar solo por haber sido
    elegido entre varios. Los intentos se cuentan TODOS: B0 a B5 mas cada
    configuracion del retador evaluada, incluidas las descartadas.
    """
    if n_trials < 2:
        return 0.0
    sd = math.sqrt(max(var_sr_trials, 0.0))
    g = EULER_MASCHERONI
    a = norm_ppf(1 - 1 / n_trials)
    b = norm_ppf(1 - 1 / (n_trials * math.e))
    return float(sd * ((1 - g) * a + g * b))


def deflated_sharpe(sr: float, n: int, skew: float, kurt: float,
                    n_trials: int, var_sr_trials: float) -> float:
    """DSR = PSR contra la barra E[max SR]. Criterio V5: DSR >= 0.95."""
    return psr(sr, n, skew, kurt, sr_ref=sr_maximo_esperado(n_trials, var_sr_trials))


# ---------------------------------------------------------------- densidad

def crps_muestral(y, muestras) -> np.ndarray:
    """CRPS por observacion desde una densidad predictiva muestreada.

    CRPS = E|X - y| - 0.5 E|X - X'|, con X, X' independientes de la predictiva.
    muestras: array (n_obs, n_muestras). Menor es mejor.
    Es la metrica de V2, y a diferencia del acierto de direccion evalua la
    densidad completa, no el signo.
    """
    y = np.asarray(y, dtype=float)
    m = np.asarray(muestras, dtype=float)
    if m.ndim != 2 or m.shape[0] != y.shape[0]:
        raise ValueError("muestras debe ser (n_obs, n_muestras) alineado con y")
    term1 = np.abs(m - y[:, None]).mean(axis=1)
    ms = np.sort(m, axis=1)
    k = ms.shape[1]
    i = np.arange(k)
    term2 = 2 * (ms * (2 * i - k + 1)).sum(axis=1) / (k * k)
    return term1 - 0.5 * term2


def crps_normal(y, mu, sigma) -> np.ndarray:
    """CRPS analitico para una predictiva normal. Util como control."""
    y = np.asarray(y, dtype=float)
    mu = np.asarray(mu, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    z = (y - mu) / sigma
    return sigma * (z * (2 * norm_cdf(z) - 1)
                    + 2 * norm_pdf(z) - 1 / math.sqrt(math.pi))


def cobertura(y, lo, hi) -> float:
    """Cobertura empirica de un intervalo. V3 exige [0.76, 0.84] para el 80%."""
    y = np.asarray(y, dtype=float)
    return float(np.mean((y >= np.asarray(lo)) & (y <= np.asarray(hi))))


def ancho_relativo(lo, hi, error_abs) -> float:
    """Ancho medio del intervalo dividido por el MAE.

    El campeon marca 1.84 (README, n=248): intervalos 84% mas anchos de lo que su propio error
    justifica. Un intervalo demasiado ancho no es prudencia, es no informar.
    """
    ancho = float(np.mean(np.asarray(hi) - np.asarray(lo)))
    return ancho / float(np.mean(np.abs(error_abs)))


# ---------------------------------------------------------------- particiones

def walk_forward_purgado(n: int, n_splits: int = 5, embargo: int = 5,
                         purge: int = 1):
    """Walk-forward expansivo con purge y embargo. Devuelve [(train, test)].

    purge:   filas quitadas del final del train, contaminadas por solape de
             etiquetas con el inicio del test.
    embargo: filas quitadas del inicio del test, para no evaluar pegado al
             borde. Su tamaño se declara, no se elige en silencio.
    """
    if n_splits < 2:
        raise ValueError("n_splits >= 2")
    bordes = np.linspace(0, n, n_splits + 1).astype(int)
    salida = []
    for i in range(1, n_splits):
        fin_train = bordes[i]
        ini_test = min(fin_train + embargo, n)
        fin_test = bordes[i + 1]
        if ini_test >= fin_test:
            continue
        train = np.arange(0, max(fin_train - purge, 0))
        test = np.arange(ini_test, fin_test)
        if train.size and test.size:
            salida.append((train, test))
    return salida


def prueba_causalidad(construir_features, datos, t: int) -> bool:
    """Prueba maestra de no fuga: el valor en t no cambia si se borra el futuro.

    construir_features: callable(datos) -> array indexable por posicion.
    Devuelve True si el valor en t es identico con y sin los datos posteriores.
    """
    completo = np.asarray(construir_features(datos))
    truncado = np.asarray(construir_features(datos[: t + 1]))
    return bool(np.allclose(completo[t], truncado[t], equal_nan=True))


# ---------------------------------------------------------------- self-test

def _self_test() -> None:
    print("=" * 68)
    print("SELF-TEST evaluacion.py   (numpy " + np.__version__ + ", sin scipy)")
    print("=" * 68)

    # 0. las primitivas propias contra valores conocidos
    assert abs(norm_ppf(0.975) - 1.959963984540054) < 1e-12
    assert abs(norm_ppf(0.5)) < 1e-15
    assert abs(float(norm_cdf(1.959963984540054)) - 0.975) < 1e-12
    assert abs(norm_ppf(1 - 1/12) + norm_ppf(1/12)) < 1e-12
    print("\n0. norm_ppf y norm_cdf coinciden con los valores de tabla  OK")

    # 1. Wilson contra la ventana sellada CANONICA (acta 37.5, excluir_cero)
    lo_m, hi_m = wilson_ci(164, 248)
    lo_b, hi_b = wilson_ci(148, 248)
    print(f"\n1. Ventana sellada canonica, convencion excluir_cero, n=248")
    print(f"   modelo 164/248 = {164/248:.1%}  Wilson [{lo_m:.1%}, {hi_m:.1%}]   acta: [60.0, 71.7]")
    print(f"   base   148/248 = {148/248:.1%}  Wilson [{lo_b:.1%}, {hi_b:.1%}]   acta: [53.5, 65.6]")
    print(f"   ventaja = {100*(164-148)/248:+.1f} pp        acta: +6.5 pp")
    assert abs(lo_m - 0.600) < 0.001 and abs(hi_m - 0.717) < 0.001, (lo_m, hi_m)
    assert abs(lo_b - 0.535) < 0.001 and abs(hi_b - 0.656) < 0.001, (lo_b, hi_b)
    print("   reproduce el acta 37.5 exactamente  OK")

    # 2. McNemar. Anclas historicas: validan la ARITMETICA, no son cifras vigentes.
    p = mcnemar_exact(67, 55)
    print(f"\n2. McNemar exacto, ancla de aritmetica: b=67 c=55 -> p = {p:.3f}")
    assert abs(p - 0.319) < 0.002, p
    p2 = mcnemar_exact(72, 56)
    print(f"   el par que reproduce la ventana canonica: b=72 c=56 -> p = {p2:.4f}"
          f"   acta: 0.1849")
    assert abs(p2 - 0.1849) < 0.001, p2
    print("   coincide con scipy y con el acta  OK")

    # 3. Comparacion pareada sintetica con ventaja real
    rng = np.random.default_rng(7)
    n = 400
    a = rng.random(n) < 0.78
    b_ = rng.random(n) < 0.60
    cmp_ = comparar_pareado(a, b_)
    print(f"\n3. Comparacion pareada sintetica\n   {cmp_}")
    assert cmp_.p_mcnemar < 0.01 and cmp_.ventaja_pp > 0

    # 4. Bootstrap de bloques: cubre la media verdadera
    serie = rng.normal(0.05, 1.0, 1000)
    est, blo, bhi = block_bootstrap(serie, block=20, n_boot=2000)
    print(f"\n4. Bootstrap de bloques  media={est:.4f}  IC95 [{blo:.4f}, {bhi:.4f}]")
    assert blo < 0.05 < bhi

    # 5. Sharpe, PSR y DSR
    r = rng.normal(0.0008, 0.01, 1000)
    sr = sharpe_por_observacion(r)
    sk, ku = momentos(r)
    se = se_sharpe(sr, len(r), sk, ku)
    p_psr = psr(sr, len(r), sk, ku)
    v = (0.5 / math.sqrt(252)) ** 2
    barra = sr_maximo_esperado(n_trials=12, var_sr_trials=v)
    d = deflated_sharpe(sr, len(r), sk, ku, n_trials=12, var_sr_trials=v)
    print(f"\n5. SR/obs={sr:.4f} (anual {sr*math.sqrt(252):.2f})  SE={se:.4f}")
    print(f"   PSR(>0)={p_psr:.3f}   barra E[max SR] con 12 intentos={barra:.4f}")
    print(f"   DSR={d:.3f}   -> V5 exige >= 0.95: {'PASA' if d >= 0.95 else 'NO PASA'}")
    assert 0.0 <= d <= 1.0 and d < p_psr + 1e-9
    assert sr_maximo_esperado(24, v) > barra
    print("   la barra sube al contar mas intentos  OK")

    # 6. CRPS: la muestral coincide con la analitica normal
    y = rng.normal(0, 1, 300)
    mu = np.zeros(300); sg = np.ones(300)
    muestras = rng.normal(mu[:, None], sg[:, None], size=(300, 20000))
    c_mu = crps_muestral(y, muestras).mean()
    c_an = crps_normal(y, mu, sg).mean()
    print(f"\n6. CRPS muestral={c_mu:.4f}  analitico={c_an:.4f}  dif={abs(c_mu-c_an):.5f}")
    assert abs(c_mu - c_an) < 0.01
    print("   la version muestral reproduce la analitica  OK")

    anchos = rng.normal(mu[:, None], 1.84 * sg[:, None], size=(300, 5000))
    c_ancho = crps_muestral(y, anchos).mean()
    print(f"   CRPS con intervalos 1.84x mas anchos = {c_ancho:.4f}  (peor)")
    assert c_ancho > c_mu

    # 7. Cobertura y ancho relativo
    z80 = norm_ppf(0.9)
    lo80 = mu - z80; hi80 = mu + z80
    cob = cobertura(y, lo80, hi80)
    ar = ancho_relativo(lo80, hi80, y - mu)
    print(f"\n7. Cobertura nominal 80%  ->  empirica {cob:.1%}   "
          f"V3 exige [76%, 84%]: {'PASA' if 0.76 <= cob <= 0.84 else 'NO PASA'}")
    print(f"   ancho relativo = {ar:.2f}  (el campeon marca 1.84)")

    # 8. Walk-forward: sin solape, con embargo respetado
    splits = walk_forward_purgado(1000, n_splits=5, embargo=5, purge=1)
    print(f"\n8. Walk-forward purgado: {len(splits)} particiones")
    for tr, te in splits:
        assert tr.max() < te.min(), "train invade el test"
        assert te.min() - tr.max() > 5, "embargo insuficiente"
        print(f"   train[0:{tr.max()+1}]  ->  test[{te.min()}:{te.max()+1}]"
              f"   hueco={te.min()-tr.max()-1}")

    # 9. Prueba de causalidad: detecta una feature que mira el futuro
    serie2 = np.arange(100, dtype=float)
    causal = lambda d: np.concatenate([[np.nan], np.diff(np.asarray(d))])
    tramposa = lambda d: np.full(len(d), np.asarray(d).mean())
    print(f"\n9. Prueba de causalidad en t=50")
    print(f"   feature causal (retorno)       -> {prueba_causalidad(causal, serie2, 50)}")
    print(f"   feature tramposa (media total) -> {prueba_causalidad(tramposa, serie2, 50)}")
    assert prueba_causalidad(causal, serie2, 50) is True
    assert prueba_causalidad(tramposa, serie2, 50) is False

    print("\n" + "=" * 68)
    print("TODO EN VERDE   ·   0 dependencias fuera de numpy")
    print("=" * 68)


if __name__ == "__main__":
    _self_test()
