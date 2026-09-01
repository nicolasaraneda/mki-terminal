# ============================================================
# GEMELO/control_lineal.py — el control lineal (6.0.0 WS2b, §4.3).
#
# Es la HIPÓTESIS NULA del retador: si una ridge sobre las mismas features
# gana, la capacidad del modelo grande estaría ajustando ruido (§4.3.2); y
# si NINGUNO supera la baseline de la §2.1, los features no traen señal y
# la conclusión honesta es ésa (§4.3.3).
#
# ============================================================
# LA PIEZA QUE NO PUEDE FALTAR: EL CONTROL DE INFORMACIÓN
# ============================================================
# Correr solo el modelo de 16 features y verlo ganar al campeón no
# responde nada: puede ser la información nueva, o puede ser que ridge con
# walk-forward y embargo sea mejor MAQUINARIA que una OLS rodante de 120
# sesiones. Son dos explicaciones distintas y la diferencia lo es todo —
# una dice que la tesis tiene dónde crecer, la otra que el campeón está mal
# implementado.
#
# Por eso C1 usa el MISMO conjunto de información que el campeón (el SOX,
# t y t-1) con la MAQUINARIA NUEVA. La comparación que responde la pregunta
# real es **C2 contra C1**, no C2 contra el campeón.
#
# NO se toca motor.py, senales.py, snapshot.py ni el camino de sellado.
# Este módulo no escribe en ninguna base ni descarga nada: recibe features
# y etiquetas ya construidas. El runner es GEMELO/experimento.py.
# ============================================================

import math

import numpy as np
import pandas as pd

from backtest import inferencia as inf

# ------------------------------------------------------------
# LAS TRES CONFIGURACIONES — declaradas ANTES de correr ninguna
# ------------------------------------------------------------
FEATURES_SOLO_SOX = ("sox_t", "sox_t1")
FEATURES_COMPLETO = (
    "sox_t", "sox_t1", "es_ret", "nq_ret", "krw_ret", "twd_ret", "jpy_ret",
    "eurusd_ret", "ks11_ret", "twii_ret", "n225_ret", "gdaxi_ret",
    "vix_term", "vix_dln", "credit_ratio", "vol_regime")

CONFIGURACIONES = {
    "C1": {"features": FEATURES_SOLO_SOX, "agrupado": True,
           "descripcion": "ridge agrupado, SOLO el SOX (t y t-1) — "
                          "CONTROL DE INFORMACIÓN: mismo insumo que el "
                          "campeón, maquinaria nueva"},
    "C2": {"features": FEATURES_COMPLETO, "agrupado": True,
           "descripcion": "ridge agrupado, catálogo completo (16 features)"},
    "C3": {"features": FEATURES_COMPLETO, "agrupado": False,
           "descripcion": "ridge por ticker, catálogo completo (16 features)"},
}

# CONTEO DE INTENTOS PARA EL DSR (§4.2 bis), declarado antes de la primera
# corrida: 3 configuraciones de aquí + 6 baselines B0→B5 ya evaluadas sobre
# los mismos folds = 9. Si se evaluara una cuarta variante, N pasa a 10 y
# TODO se recalcula. Un DSR con el N mal contado miente hacia arriba.
N_INTENTOS_DECLARADO = 9

# La búsqueda de alpha es INTERNA a cada configuración y NO suma a N: se
# resuelve dentro de cada ventana de entrenamiento por CV temporal, sin
# tocar jamás una fila de evaluación. Lo que el DSR debe contar son las
# decisiones tomadas MIRANDO el resultado de evaluación; ésta no lo es.
ALPHAS_CV = (0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0)
PLIEGUES_CV = 3

EMBARGO_DIAS = 5
MINIMO_ENTRENAMIENTO = 250     # filas mínimas para ajustar
SEMILLA_BOOTSTRAP = 20260826
BLOQUE_BOOTSTRAP = 20
ALPHA_BOOTSTRAP = 0.05

# Un Sharpe ANUALIZADO sobre pocas decenas de días no es una estimación:
# es un artefacto de multiplicar por √252. Por debajo de este umbral el
# PSR y el DSR se reportan como NO INTERPRETABLES en vez de emitir un
# 1.0000 que se leería como certeza — y que, peor, se leería como que V5
# (DSR ≥ 0.95) está superado. Ver DECISIONES.md §26.3 sobre la saturación
# de Phi: un DSR de 1.000 significa "más allá de lo que el doble
# distingue", no "seguro".
MINIMO_DIAS_SHARPE = 60

# Ventana que sostiene casi toda la ventaja del campeón (§2.2). R2 del
# §6.2 descarta a quien pierda su ventaja al excluirla; se aplica por
# FECHAS porque el índice de bloque depende del orden de las filas (§2.8.2).
VENTANA_R2 = ("2026-07-15", "2026-07-23")


# ------------------------------------------------------------
# Ridge — forma cerrada, sin dependencias nuevas
# ------------------------------------------------------------
def ajustar_ridge(X: np.ndarray, y: np.ndarray, alpha: float) -> dict:
    """Ridge estandarizada. Devuelve coeficientes, escalas y sigma residual.

    Se estandariza DENTRO del ajuste y con estadísticos del entrenamiento:
    usar los de todo el histórico filtraría información de evaluación por
    la puerta de atrás.
    """
    mu, sd = X.mean(axis=0), X.std(axis=0)
    sd = np.where(sd == 0, 1.0, sd)
    Xs = (X - mu) / sd
    y_mu = y.mean()
    yc = y - y_mu
    p = Xs.shape[1]
    coef = np.linalg.solve(Xs.T @ Xs + alpha * np.eye(p), Xs.T @ yc)
    resid = yc - Xs @ coef
    # sigma con corrección por grados de libertad; nunca cero
    gl = max(len(y) - p - 1, 1)
    sigma = float(np.sqrt((resid @ resid) / gl))
    return {"coef": coef, "mu": mu, "sd": sd, "y_mu": float(y_mu),
            "sigma": max(sigma, 1e-9), "alpha": alpha, "n": len(y)}


def predecir_ridge(modelo: dict, X: np.ndarray) -> np.ndarray:
    Xs = (X - modelo["mu"]) / modelo["sd"]
    return Xs @ modelo["coef"] + modelo["y_mu"]


def elegir_alpha(X: np.ndarray, y: np.ndarray, orden: np.ndarray,
                 alphas=ALPHAS_CV, pliegues: int = PLIEGUES_CV) -> float:
    """CV TEMPORAL dentro de la ventana de entrenamiento: pliegues
    expansivos ordenados por fecha, cada uno valida sobre el tramo
    siguiente. Jamás toca filas de evaluación — es interno al fold."""
    n = len(y)
    if n < MINIMO_ENTRENAMIENTO:
        return 1.0
    idx = np.argsort(orden, kind="stable")
    Xo, yo = X[idx], y[idx]
    cortes = [int(n * (k + 1) / (pliegues + 1)) for k in range(pliegues)]
    errores = {a: [] for a in alphas}
    for c in cortes:
        fin = int(n * (cortes.index(c) + 2) / (pliegues + 1))
        if c < 30 or fin <= c:
            continue
        Xtr, ytr, Xva, yva = Xo[:c], yo[:c], Xo[c:fin], yo[c:fin]
        for a in alphas:
            try:
                m = ajustar_ridge(Xtr, ytr, a)
            except np.linalg.LinAlgError:
                continue
            errores[a].append(float(np.mean(np.abs(predecir_ridge(m, Xva) - yva))))
    validos = {a: np.mean(v) for a, v in errores.items() if v}
    return min(validos, key=validos.get) if validos else 1.0


# ------------------------------------------------------------
# Walk-forward expansivo con embargo
# ------------------------------------------------------------
def correr_configuracion(nombre: str, panel: pd.DataFrame,
                         evaluacion: pd.DataFrame,
                         embargo_dias: int = EMBARGO_DIAS,
                         cfg: dict | None = None) -> pd.DataFrame:
    """Predice cada fila de `evaluacion` entrenando solo con el pasado.

    `cfg` permite pasar una configuración EXPLÍCITA en vez de buscar
    `nombre` en CONFIGURACIONES. Se añadió en WS5, donde el conjunto de
    features depende de la bolsa del objetivo (hay que excluir su propio
    índice local, que es casi circular) y por tanto no puede vivir en un
    diccionario fijo. Con `cfg=None` el comportamiento es EXACTAMENTE el
    de antes — hay un test que lo fija.

    `panel`: columnas fecha, ticker, gap_pct + las features. Es el histórico
    completo de entrenamiento (etiquetas ya cerradas).
    `evaluacion`: las filas selladas del campeón a predecir.

    WALK-FORWARD EXPANSIVO: para cada fecha de emisión D se entrena con
    TODAS las filas cuya sesión objetivo cerró en o antes de D − embargo.
    El embargo purga la frontera: las features son rodantes y la etiqueta
    de ayer comparte casi toda su ventana con las features de hoy
    (DECISIONES.md §27).
    """
    cfg = cfg if cfg is not None else CONFIGURACIONES[nombre]
    cols = [c for c in cfg["features"] if c in panel.columns]
    if not cols:
        return pd.DataFrame()

    panel = panel.dropna(subset=cols + ["gap_pct"]).copy()
    salida = []
    for fecha in sorted(evaluacion["fecha"].unique()):
        corte = pd.Timestamp(fecha) - pd.Timedelta(days=embargo_dias)
        tr = panel[panel["fecha"] <= corte]
        filas_dia = evaluacion[evaluacion["fecha"] == fecha]
        if tr.empty:
            continue
        # Se ajusta UNA vez por grupo y fecha, no una por fila: en las
        # configuraciones agrupadas el conjunto de entrenamiento es el
        # mismo para todos los tickers de ese día.
        modelos = {}
        for _, fila in filas_dia.iterrows():
            clave = "_pool_" if cfg["agrupado"] else fila["ticker"]
            if clave not in modelos:
                sub = tr if cfg["agrupado"] else tr[tr["ticker"] == fila["ticker"]]
                if len(sub) < MINIMO_ENTRENAMIENTO:
                    modelos[clave] = None
                else:
                    X = sub[cols].to_numpy(float)
                    y = sub["gap_pct"].to_numpy(float)
                    a = elegir_alpha(X, y, sub["fecha"].to_numpy())
                    try:
                        modelos[clave] = ajustar_ridge(X, y, a)
                    except np.linalg.LinAlgError:
                        modelos[clave] = None
            m = modelos[clave]
            if m is None:
                continue
            x = fila[cols].to_numpy(float).reshape(1, -1)
            if np.isnan(x).any():
                continue
            salida.append({
                "fecha": fila["fecha"], "ticker": fila["ticker"],
                "pred": float(predecir_ridge(m, x)[0]),
                "sigma": m["sigma"], "alpha": m["alpha"], "n_train": m["n"],
                "gap_pct": float(fila["gap_pct"]),
            })
    return pd.DataFrame(salida)


# ------------------------------------------------------------
# Evaluación
# ------------------------------------------------------------
def crps_normal(y: np.ndarray, mu: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    """CRPS de una predictiva NORMAL, forma cerrada.

    PRIMERA PASADA, declarado como tal: ridge entrega punto más varianza
    residual, y una normal es defendible para empezar — pero la §2.7 ya
    mostró colas más gruesas de lo normal en este objetivo, así que este
    CRPS es una cota optimista. La densidad con colas (Student-t) es
    Nivel 4 del retador, no de este control.
    """
    sigma = np.maximum(np.asarray(sigma, float), 1e-9)
    z = (np.asarray(y, float) - np.asarray(mu, float)) / sigma
    Phi = np.array([inf.Phi(v) for v in z])
    phi = np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    return sigma * (z * (2 * Phi - 1) + 2 * phi - 1.0 / math.sqrt(math.pi))


def _acierto(pred, gap):
    """Misma convención que el verificador: (pred>=0) == (gap>=0)."""
    return ((np.asarray(pred) >= 0) == (np.asarray(gap) >= 0)).astype(int)


def retornos_diarios(df: pd.DataFrame) -> pd.Series:
    """Long-short equiponderado por día: sign(pred) * gap.

    Proxy económico de PRIMERA PASADA, sin costos: es optimista por
    construcción y NO es la prueba del benchmark obligatorio (§6.1 V6),
    que exige SMH y 25 pb por lado.
    """
    if df.empty:
        return pd.Series(dtype=float)
    d = df.copy()
    d["r"] = np.sign(d["pred"]) * d["gap_pct"]
    return d.groupby("fecha")["r"].mean().sort_index()


def evaluar(df: pd.DataFrame, etiqueta: str) -> dict:
    """Métricas de una configuración sobre las filas que predijo."""
    if df.empty:
        return {"config": etiqueta, "n": 0}
    gap = df["gap_pct"].to_numpy(float)
    pred = df["pred"].to_numpy(float)
    acierto = _acierto(pred, gap)
    base = (gap > 0).astype(int)          # "siempre al alza"
    b01 = int(((acierto == 1) & (base == 0)).sum())
    b10 = int(((acierto == 0) & (base == 1)).sum())
    r = retornos_diarios(df)
    sr = inf.sharpe(r.to_numpy(), anualizar=252) if len(r) >= 2 else float("nan")
    return {
        "config": etiqueta, "n": int(len(df)),
        "acierto_pct": round(100 * acierto.mean(), 1),
        "base_pct": round(100 * base.mean(), 1),
        "ventaja_pp": round(100 * (acierto.mean() - base.mean()), 1),
        "mcnemar_b01": b01, "mcnemar_b10": b10,
        "mcnemar_p": round(_mcnemar(b01, b10), 4),
        "mae": round(float(np.abs(pred - gap).mean()), 4),
        "crps": round(float(crps_normal(gap, pred, df["sigma"].to_numpy(float)).mean()), 4),
        "sharpe_ls_sin_costos": None if math.isnan(sr) else round(sr, 3),
        "dias": int(len(r)),
        # el campeón no tiene alpha ni ventana de entrenamiento de ridge
        "alpha_mediana": (round(float(df["alpha"].median()), 3)
                          if df["alpha"].notna().any() else None),
        "n_train_mediano": (int(df["n_train"].median())
                            if df["n_train"].notna().any() else None),
    }


def _mcnemar(b01: int, b10: int) -> float:
    """Chi-cuadrado con corrección de continuidad — la misma variante que
    reproduce el p de la §2 (DECISIONES.md §25)."""
    n = b01 + b10
    if n == 0:
        return 1.0
    d = max(abs(b01 - b10) - 1, 0)
    return _chi2_sf(d * d / n)


def _chi2_sf(x: float) -> float:
    return math.erfc(math.sqrt(x / 2.0)) if x > 0 else 1.0


def comparar(a: pd.DataFrame, b: pd.DataFrame, nombre_a: str,
             nombre_b: str) -> dict:
    """Comparación pareada sobre las filas que AMBOS predijeron.

    Es la comparación honesta: si una configuración predijo menos filas que
    otra, compararlas sobre conjuntos distintos mezclaría la diferencia de
    modelo con la de cobertura.
    """
    if a.empty or b.empty:
        return {"par": f"{nombre_a} vs {nombre_b}", "n": 0}
    j = a.merge(b, on=["fecha", "ticker"], suffixes=("_a", "_b"))
    if j.empty:
        return {"par": f"{nombre_a} vs {nombre_b}", "n": 0}
    gap = j["gap_pct_a"].to_numpy(float)
    ha = _acierto(j["pred_a"], gap)
    hb = _acierto(j["pred_b"], gap)
    b01 = int(((ha == 1) & (hb == 0)).sum())
    b10 = int(((ha == 0) & (hb == 1)).sum())
    mae_a = np.abs(j["pred_a"] - gap)
    mae_b = np.abs(j["pred_b"] - gap)
    dif = (mae_b - mae_a).to_numpy(float)      # >0 ⇒ A tiene MENOS error
    ic = inf.bootstrap_bloques(dif, semilla=SEMILLA_BOOTSTRAP,
                               bloque=BLOQUE_BOOTSTRAP, alpha=ALPHA_BOOTSTRAP,
                               anualizar=1)
    return {
        "par": f"{nombre_a} vs {nombre_b}", "n": int(len(j)),
        "acierto_a_pct": round(100 * ha.mean(), 1),
        "acierto_b_pct": round(100 * hb.mean(), 1),
        "ventaja_pp": round(100 * (ha.mean() - hb.mean()), 1),
        "mcnemar": f"{b01} vs {b10}", "mcnemar_p": round(_mcnemar(b01, b10), 4),
        "mae_a": round(float(mae_a.mean()), 4),
        "mae_b": round(float(mae_b.mean()), 4),
        "delta_mae": round(float(dif.mean()), 4),
        "delta_mae_ic": [round(ic["lo"], 4), round(ic["hi"], 4)],
        "ic_excluye_cero": bool(ic["lo"] > 0 or ic["hi"] < 0),
    }


def evaluar_r2(df: pd.DataFrame, etiqueta: str,
               ventana=VENTANA_R2) -> dict:
    """R2 del §6.2 aplicado a una configuración: ¿sobrevive su ventaja al
    excluir la ventana que sostiene casi toda la del campeón?"""
    if df.empty:
        return {"config": etiqueta, "n": 0}
    f = pd.to_datetime(df["fecha"])
    fuera = df[(f < ventana[0]) | (f > ventana[1])]
    if fuera.empty:
        return {"config": etiqueta, "n": 0}
    gap = fuera["gap_pct"].to_numpy(float)
    ac = _acierto(fuera["pred"].to_numpy(float), gap)
    base = (gap > 0).astype(int)
    b01 = int(((ac == 1) & (base == 0)).sum())
    b10 = int(((ac == 0) & (base == 1)).sum())
    return {"config": etiqueta, "n": int(len(fuera)),
            "acierto_pct": round(100 * ac.mean(), 1),
            "base_pct": round(100 * base.mean(), 1),
            "ventaja_pp": round(100 * (ac.mean() - base.mean()), 1),
            "mcnemar_p": round(_mcnemar(b01, b10), 4),
            "mae": round(float(np.abs(fuera["pred"] - gap).mean()), 4),
            "sobrevive_R2": bool(ac.mean() > base.mean())}


def inferencia_sharpe(resultados: dict, n_intentos: int) -> list:
    """PSR y DSR de cada configuración, con el N que el llamador declara.

    **`n_intentos` NO TIENE VALOR POR DEFECTO, y es deliberado.** Esta
    firma tenía `= N_INTENTOS_DECLARADO` (9) hasta el 1-sep-2026, y
    `experimento.py` la llamaba sin pasar N, así que consumía a ciegas el
    conteo más rancio del repo. `backtest/inferencia.py`:127 había quitado
    ese mismo default **a propósito, con acta (`DECISIONES.md` §26.1) y
    con un test que lo exige**, porque *"un DSR calculado con un N que
    alguien olvidó actualizar miente, y miente hacia arriba"*. Este módulo
    lo había reintroducido, anulando la defensa desde adentro.

    Medido el 1-sep: `SR0(9) = 0.9986` contra `SR0(86) = 1.6266`. **El
    default regalaba 0.63 de umbral**, y a un Sharpe anualizado de 1.2–1.5
    —el rango realista— **el veredicto V5 se daba vuelta de PASA a NO
    PASA**. Hoy no publicaba nada malo sólo porque el WS2b tiene menos de
    60 días y corta antes por `MINIMO_DIAS_SHARPE`. Era un vector vivo, no
    una deuda cosmética.

    Es la cuarta regla de la casa: un número retirado que sigue ofrecido
    en el código vuelve a circular — acá, ofrecido como valor por defecto
    de un parámetro.

    V_intentos se estima con la varianza de los Sharpe disponibles. Es una
    SUBESTIMACIÓN declarada: los Sharpe de las seis baselines B0→B5 vienen
    de una corrida legacy con bootstrap no circular y sin embargo
    (DECISIONES.md §28.5), así que no se mezclan. Un V menor da un SR0
    menor y por tanto un DSR **optimista**: la cifra que se reporta es una
    cota superior, y así queda dicha.
    """
    sharpes = [v["sharpe_ls_sin_costos"] for v in resultados.values()
               if v.get("sharpe_ls_sin_costos") is not None]
    V = float(np.var(sharpes, ddof=1)) if len(sharpes) >= 2 else 0.25
    filas = []
    for nombre, v in resultados.items():
        sr, dias = v.get("sharpe_ls_sin_costos"), v.get("dias", 0)
        if sr is None or dias < 2:
            continue
        interpretable = dias >= MINIMO_DIAS_SHARPE
        filas.append({
            "config": nombre, "sharpe": sr, "dias": dias,
            "interpretable": interpretable,
            "psr_vs_cero": (round(inf.psr(sr, 0.0, dias, 0.0, 3.0), 4)
                            if interpretable else "NO INTERPRETABLE"),
            "sr0_deflacionado": round(inf.sr0_deflacionado(n_intentos, V), 4),
            "dsr": (round(inf.dsr(sr, dias, 0.0, 3.0, n_intentos, V), 4)
                    if interpretable else "NO INTERPRETABLE"),
            "N_intentos": n_intentos, "V_intentos": round(V, 4),
        })
    return filas
