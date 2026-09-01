# ============================================================
# Los seis baselines B0→B5 (DISEÑO.md §3) y su contexto de features.
#
# Toda feature es una serie construida con operaciones RETROSPECTIVAS
# (rolling/shift) sobre los frames congelados: el valor en la fecha d usa
# solo datos <= d. Antes de emitir, cada baseline pasa su rebanada por
# validar_sin_futuro() — la guardia dura.
#
# B2 es la excepción arquitectónica deliberada: NO se reconstruye — llama
# a motor.prediccion_apertura_al(D), el modelo de producción congelado
# v4.6.0, porque su rol es AUDITARLO, no imitarlo. Para las features
# "beta·SOX" de B3+ sí existe una reconstrucción vectorizada equivalente
# (rolling cov/var), documentada como feature, no como señal.
# ============================================================

from datetime import date, timedelta

import numpy as np
import pandas as pd

import motor
from universo import (EXCHANGE_POR_TICKER, FX_POR_EXCHANGE,
                      INDICE_LOCAL_POR_EXCHANGE, MERCADOS_POR_ABRIR,
                      PARES_COMPETIDORES, TICKERS_POR_NIVEL, UNIVERSO)

from backtest.datos import (FuenteCongelada, SentimientoPIT, recortar_pit,
                            residual_rolling)

Z80 = motor.Z80
VENTANA_ENTRENAMIENTO = 250   # sesiones de train para B1/B3-B5 (congelado)
DIAS_REAJUSTE = 7             # re-ajuste semanal (congelado en el diseño)

# EMBARGO (Etapa 6.0.0 WS1 · López de Prado 2018 cap. 7)
# ------------------------------------------------------------
# El framework ya impedía el look-ahead duro: ninguna fila con fecha
# posterior a la emisión entra (validar_sin_futuro). Pero eso no basta.
# La FRONTERA entre entrenamiento y prueba sigue contaminada: las features
# son rodantes (medias, momentum, residuales a 20/50/200 sesiones), así que
# una etiqueta del día anterior a la emisión se construyó con una ventana
# que se solapa casi entera con la ventana de las features con que se
# predice HOY. El modelo entrena sobre información que es, en la práctica,
# la misma que va a usar para predecir — y su error de entrenamiento sale
# optimista sin que ninguna guarda se queje.
#
# El embargo purga las últimas `EMBARGO_DIAS` jornadas antes de la emisión.
# Se paga en datos (se entrena con menos historia) y se cobra en honestidad.
#
# Por qué 5 y por qué ahora: 5 días hábiles cubren una semana completa, que
# es el reajuste (DIAS_REAJUSTE=7 corridos) y el horizonte de las features
# más cortas. Es una ELECCIÓN NUEVA, no un valor recuperado: revisar contra
# las primeras corridas reales. Y se introduce ahora porque **ninguna
# corrida con veredicto se ha ejecutado todavía**: cambiarlo hoy no
# invalida ningún resultado publicado. Después del primer veredicto, tocar
# esto sería cambiar las reglas a mitad del experimento.
EMBARGO_DIAS = 5


class ContextoRun:
    """Features point-in-time del run completo, construidas UNA vez.

    Cada serie es retrospectiva; el acceso por emisión rebana `<= D` y
    valida. Los outcomes (gaps por sesión) viven aparte: son etiquetas de
    entrenamiento solo para sesiones ya CONOCIBLES a la emisión (a las
    22:15 UTC toda sesión de Asia/Europa del mismo día ya cerró +2h)."""

    def __init__(self, fuente: FuenteCongelada, embargo_dias: int = EMBARGO_DIAS,
                 sentimiento: SentimientoPIT | None = None):
        self.fuente = fuente
        if int(embargo_dias) < 0:
            raise ValueError("embargo_dias no puede ser negativo")
        self.embargo_dias = int(embargo_dias)
        # inyectable para que el gate de causalidad pueda truncar TAMBIÉN la
        # base de noticias: truncar sólo los precios dejaría la mitad del
        # arnés sin probar, que es donde vivía B-1.
        self.sentimiento = sentimiento if sentimiento is not None else SentimientoPIT()
        self._memo_sent = {}
        # memo de vectores de features: el walk-forward reajusta cada 7 días
        # sobre ventanas que se solapan casi enteras, así que el mismo
        # (ticker, fecha, columnas) se pide decenas de veces. Es memo puro:
        # nada aquí depende de la fecha de emisión que lo pide.
        self._memo_fila = {}
        # contadores de EVIDENCIA, no features: cuántos pares (ticker, fecha)
        # DISTINTOS se resolvieron con sentimiento real y cuántos con el
        # relleno neutro.
        self.filas_con_sentimiento = 0
        self.filas_sin_sentimiento = 0
        cierres = fuente.cierres(tuple(UNIVERSO.keys()))
        self.cierres = cierres.ffill()
        self.ret = self.cierres.pct_change()
        self.mom20 = self.cierres / self.cierres.shift(20) - 1

        # --- SOX: retorno diario y "último movimiento real" (feriado = 0)
        sox = fuente.cierres(("^SOX",))
        self.sox_ret = (sox.iloc[:, 0].pct_change().dropna()
                        if not sox.empty else pd.Series(dtype=float))
        no_cero = self.sox_ret.where(self.sox_ret.abs() >= 1e-6)
        self.sox_ultimo_real = (no_cero.ffill() * 100)  # % del último mov real

        # --- régimen (solo tendencia, para dummy y desglose): MA50 vs MA200
        serie_sox = sox.iloc[:, 0].dropna() if not sox.empty else pd.Series(dtype=float)
        ratio = serie_sox.rolling(50).mean() / serie_sox.rolling(200).mean() - 1
        self.regimen = pd.cut(ratio, [-np.inf, -0.01, 0.01, np.inf],
                              labels=["Bajista", "Lateral", "Alcista"])

        # --- índices locales
        self.mom20_idx = {}
        for ex, idx in INDICE_LOCAL_POR_EXCHANGE.items():
            s = fuente.cierres((idx,))
            if not s.empty:
                serie = s.iloc[:, 0].ffill()
                self.mom20_idx[ex] = serie / serie.shift(20) - 1

        # --- beta de contagio vectorizada (feature de B3+): cov/var rodante
        #     120 del retorno propio contra SOX(t-1), por ticker
        self.beta_sox = {}
        for t in MERCADOS_POR_ABRIR:
            if t not in self.ret.columns:
                continue
            par = pd.concat({"y": self.ret[t], "x": self.sox_ret.shift(1)},
                            axis=1).dropna()
            beta = (par["y"].rolling(120).cov(par["x"])
                    / par["x"].rolling(120).var().replace(0, np.nan))
            self.beta_sox[t] = beta

        # --- divergencias residualizadas (rolling, ver datos.residual_rolling):
        #     z del spread de momentum residual del par, con signo por miembro
        self.z_divergencia = {}
        fx_series = {par: fuente.cierres((par,)).iloc[:, 0].pct_change()
                     for par in set(FX_POR_EXCHANGE.values())
                     if not fuente.cierres((par,)).empty}
        for _, miembros in PARES_COMPETIDORES:
            presentes = [t for t in miembros if t in self.ret.columns]
            for i in range(len(presentes)):
                for j in range(i + 1, len(presentes)):
                    a, b = presentes[i], presentes[j]
                    res = {}
                    for t in (a, b):
                        ex = EXCHANGE_POR_TICKER.get(t, "XNYS")
                        idx = INDICE_LOCAL_POR_EXCHANGE.get(ex)
                        cierre_idx = (self.fuente.cierres((idx,))
                                      if idx else pd.DataFrame())
                        s_idx = (cierre_idx.iloc[:, 0].pct_change()
                                 if not cierre_idx.empty else None)
                        s_fx = fx_series.get(FX_POR_EXCHANGE.get(ex))
                        res[t] = residual_rolling(self.ret[t], s_idx, s_fx)
                    spread = (res[a].rolling(20).sum()
                              - res[b].rolling(20).sum()).dropna() * 100
                    if spread.empty:
                        continue
                    z = ((spread - spread.rolling(120).mean())
                         / spread.rolling(120).std().replace(0, np.nan))
                    self.z_divergencia.setdefault(a, []).append(z)
                    self.z_divergencia.setdefault(b, []).append(-z)
        self.z_divergencia = {t: pd.concat(series, axis=1).mean(axis=1)
                              for t, series in self.z_divergencia.items()}

        # --- cadena: Roca→Chip como percentil rodante (mismas ventanas del
        #     motor: media de momentum 20d por eslabón, percentil 252)
        series_nivel = {}
        for nivel, tickers in TICKERS_POR_NIVEL.items():
            cols = [t for t in tickers if t in self.mom20.columns]
            if cols:
                series_nivel[nivel] = self.mom20[cols].mean(axis=1)
        self.mom_nivel = series_nivel
        cadena = pd.concat(series_nivel.values(), axis=1).mean(axis=1).dropna() * 100
        self.roca_pct = (cadena.rolling(252, min_periods=61)
                         .apply(lambda v: (v <= v[-1]).mean() * 100, raw=True))

        # --- buzz: vive en SentimientoPIT y pasa por el MISMO corte de
        #     disponibilidad que el sentimiento (B-1). El panel precomputado
        #     que había aquí mezclaba vintages: contaba un titular en su día
        #     de publicación aunque su análisis —lo único que lo hace
        #     visible— llegara meses después.

        # --- outcomes por ticker: gap por sesión (etiquetas de train)
        self.gaps = {}
        for t in MERCADOS_POR_ABRIR:
            ohlc = fuente._ohlc.get(t)
            if ohlc is None or ohlc.empty:
                continue
            gap = (ohlc["Open"] / ohlc["Close"].shift(1) - 1) * 100
            self.gaps[t] = gap.dropna()

    # -------- accesos point-in-time --------
    def _al(self, serie: pd.Series, fecha: date):
        """Último valor de la serie con índice <= fecha.

        El recorte lo hace la guarda (`recortar_pit`), que recibe la serie
        SIN recortar: antes este método recortaba y después le pedía a
        `validar_sin_futuro` que comprobara su propio recorte, con lo que la
        condición de disparo era inalcanzable por construcción."""
        if serie is None or serie.empty:
            return None
        corte = recortar_pit(serie, fecha)
        if corte is None or corte.empty or pd.isna(corte.iloc[-1]):
            return None
        return float(corte.iloc[-1])

    def sent(self, ticker: str, fecha: date) -> tuple:
        clave = (ticker, fecha)
        if clave not in self._memo_sent:
            self._memo_sent[clave] = self.sentimiento.valor(ticker, fecha)
        return self._memo_sent[clave]

    def upstream(self, ticker: str, fecha: date):
        """Momentum 20d promedio de los eslabones aguas ARRIBA del ticker
        (nivel < el suyo); fabless (nivel None) usan la cadena completa."""
        nivel = UNIVERSO.get(ticker, {}).get("nivel")
        niveles = ([n for n in self.mom_nivel if nivel is not None and n < nivel]
                   or list(self.mom_nivel))
        valores = [self._al(self.mom_nivel[n], fecha) for n in niveles]
        valores = [v for v in valores if v is not None]
        return float(np.mean(valores)) if valores else None

    def fila_features(self, ticker: str, fecha: date, columnas: tuple) -> dict | None:
        """Vector de features de `ticker` conocido al cierre de `fecha`.
        None si falta alguna feature (la fila no se emite/entrena)."""
        clave = (ticker, fecha, columnas)
        if clave in self._memo_fila:
            fila = self._memo_fila[clave]
            return dict(fila) if fila is not None else None
        fila = self._fila_features(ticker, fecha, columnas)
        self._memo_fila[clave] = fila
        return dict(fila) if fila is not None else None

    def _fila_features(self, ticker: str, fecha: date, columnas: tuple) -> dict | None:
        ex = EXCHANGE_POR_TICKER.get(ticker, "XNYS")
        valores = {}
        for c in columnas:
            if c == "beta_sox":
                beta = self._al(self.beta_sox.get(ticker), fecha)
                sox = self._al(self.sox_ultimo_real, fecha)
                v = beta * sox if beta is not None and sox is not None else None
            elif c == "mom20":
                v = self._al(self.mom20.get(ticker), fecha)
            elif c == "mom20_idx":
                v = self._al(self.mom20_idx.get(ex), fecha)
            elif c == "regimen_alcista":
                r = recortar_pit(self.regimen, fecha)
                v = None if r is None or r.empty or pd.isna(r.iloc[-1]) \
                    else float(r.iloc[-1] == "Alcista")
            elif c == "z_divergencia":
                v = self._al(self.z_divergencia.get(ticker), fecha)
                v = 0.0 if v is None else v  # sin par → sin divergencia
            elif c == "sentimiento":
                v, _ = self.sent(ticker, fecha)
                # sin juicio DISPONIBLE → relleno neutro. No es un dato: es
                # una ausencia rellenada, y se cuenta para poder declararla.
                if v is None:
                    self.filas_sin_sentimiento += 1
                    v = 0.0
                else:
                    self.filas_con_sentimiento += 1
            elif c == "sentimiento_sector":
                vals = [self.sent(t, fecha)[0] for t in MERCADOS_POR_ABRIR]
                vals = [x for x in vals if x is not None]
                v = float(np.mean(vals)) if vals else 0.0
            elif c == "buzz":
                v = self.sentimiento.buzz(ticker, fecha)
                v = 0.0 if v is None else min(v, 10.0)
            elif c == "roca_pct":
                v = self._al(self.roca_pct, fecha)
            elif c == "upstream":
                v = self.upstream(ticker, fecha)
            else:
                raise ValueError(f"feature desconocida: {c}")
            if v is None:
                return None
            valores[c] = v
        return valores


# ============================================================
# Baselines
# ============================================================
class B0Nulo:
    """Señal nula (est=0). Piso de MAE y, como cartera, equiponderada."""
    nombre = "B0"
    pregunta = "¿El período regaló retornos? (piso de MAE, cartera sin criterio)"

    def __init__(self, ctx: ContextoRun):
        self.ctx = ctx

    def predecir(self, fecha: date) -> pd.DataFrame:
        return pd.DataFrame([{"Ticker": t, "est": 0.0, "int80": None, "grado": "A"}
                             for t in MERCADOS_POR_ABRIR])


class B2Produccion:
    """El modelo de producción v4.6.0, llamado tal cual — auditoría, no
    imitación. Requiere la FuenteCongelada activa (motor lee de ella)."""
    nombre = "B2"
    pregunta = "¿El contagio del SOX agrega sobre la inercia propia?"

    def __init__(self, ctx: ContextoRun):
        self.ctx = ctx

    def predecir(self, fecha: date) -> pd.DataFrame:
        pred = motor.prediccion_apertura_al(fecha)
        if pred is None or pred.empty:
            return pd.DataFrame(columns=["Ticker", "est", "int80", "grado"])
        return pd.DataFrame([{
            "Ticker": p["Ticker"], "est": float(p["Apertura estimada %"]),
            "int80": float(p["Intervalo80 pp"]), "grado": "A",
        } for _, p in pred.iterrows()])


class _BaselineAjustada:
    """Base común de B1/B3/B4/B5: regresión lineal walk-forward sobre un
    set de features, re-ajustada cada DIAS_REAJUSTE con las últimas
    VENTANA_ENTRENAMIENTO sesiones conocidas. Sin regularización, sin
    túnel de hiperparámetros (congelado en DISEÑO.md §6)."""
    nombre = "?"
    pregunta = "?"
    columnas: tuple = ()
    agrupado = True  # un solo modelo para todos los tickers (pooled)

    def __init__(self, ctx: ContextoRun):
        self.ctx = ctx
        self._coef = None
        self._medias = None
        self._stds = None
        self._sigma = None
        self._ultimo_ajuste: date | None = None

    def _entrenar(self, fecha: date) -> None:
        filas_X, filas_y = [], []
        for t in MERCADOS_POR_ABRIR:
            gaps = self.ctx.gaps.get(t)
            if gaps is None or gaps.empty:
                continue
            # etiquetas: gaps de sesiones <= fecha (conocibles a las 22:15);
            # features: al cierre de la sesión ANTERIOR a cada etiqueta.
            # EMBARGO: se purga la frontera. Sin esto, la etiqueta de ayer
            # comparte casi toda su ventana rodante con las features de hoy.
            corte = fecha - timedelta(days=self.ctx.embargo_dias)
            gaps_t = recortar_pit(gaps, corte).tail(VENTANA_ENTRENAMIENTO)
            fechas_sesion = list(gaps_t.index)
            for k in range(1, len(fechas_sesion)):
                f_label = fechas_sesion[k]
                f_info = fechas_sesion[k - 1].date()
                fila = self.ctx.fila_features(t, f_info, self.columnas)
                if fila is None:
                    continue
                filas_X.append([fila[c] for c in self.columnas])
                filas_y.append(float(gaps_t.loc[f_label]))
        if len(filas_y) < 60:
            return  # sin datos suficientes: el modelo anterior sigue vigente
        X = np.asarray(filas_X, dtype=float)
        y = np.asarray(filas_y, dtype=float)
        self._medias = X.mean(axis=0)
        self._stds = np.where(X.std(axis=0) == 0, 1.0, X.std(axis=0))
        Xs = (X - self._medias) / self._stds
        Xs = np.hstack([Xs, np.ones((len(Xs), 1))])
        coef, *_ = np.linalg.lstsq(Xs, y, rcond=None)
        self._coef = coef
        self._sigma = float((y - Xs @ coef).std())
        self._ultimo_ajuste = fecha

    def predecir(self, fecha: date) -> pd.DataFrame:
        if (self._ultimo_ajuste is None
                or (fecha - self._ultimo_ajuste) >= timedelta(days=DIAS_REAJUSTE)):
            self._entrenar(fecha)
        if self._coef is None:
            return pd.DataFrame(columns=["Ticker", "est", "int80", "grado"])
        filas = []
        for t in MERCADOS_POR_ABRIR:
            fila = self.ctx.fila_features(t, fecha, self.columnas)
            if fila is None:
                continue
            x = (np.array([fila[c] for c in self.columnas]) - self._medias) / self._stds
            est = float(np.append(x, 1.0) @ self._coef)
            grado = self._grado(t, fecha)
            filas.append({"Ticker": t, "est": round(est, 4),
                          "int80": round(Z80 * self._sigma, 4), "grado": grado})
        return pd.DataFrame(filas)

    def _grado(self, ticker: str, fecha: date) -> str:
        return "A"


class B1Momentum(_BaselineAjustada):
    nombre = "B1"
    pregunta = "¿Basta la inercia propia (momentum 20d), sin mirar el SOX?"
    columnas = ("mom20",)


class B3Cuant(_BaselineAjustada):
    nombre = "B3"
    pregunta = "¿Combinar las señales de PRECIO mejora al contagio solo?"
    columnas = ("beta_sox", "mom20", "mom20_idx", "regimen_alcista", "z_divergencia")


class B4Noticias(B3Cuant):
    nombre = "B4"
    pregunta = "¿Las noticias agregan algo que el precio no traía?"
    columnas = B3Cuant.columnas + ("sentimiento", "sentimiento_sector", "buzz")

    def _grado(self, ticker: str, fecha: date) -> str:
        """A = sentimiento SELLADO por producción ese día.
        B = reconstruido desde noticias.db con juicios YA disponibles.
        S = SIN sentimiento: no había ningún juicio de IA disponible a la
            emisión y la fila se emitió con el relleno neutro (0.0).

        El grado B ya no significa "el juicio llegó después" — esas filas
        ahora no entran. Y S es el grado que faltaba: la corrida anterior
        rellenaba con cero y lo contaba como si fuera dato."""
        v, grado = self.ctx.sent(ticker, fecha)
        if v is None:
            return "S"
        return grado


class B5Cadena(B4Noticias):
    nombre = "B5"
    pregunta = "¿La cadena roca→chip agrega valor marginal medible?"
    columnas = B4Noticias.columnas + ("roca_pct", "upstream")


def construir_baselines(ctx: ContextoRun, cuales: tuple) -> dict:
    catalogo = {"B0": B0Nulo, "B1": B1Momentum, "B2": B2Produccion,
                "B3": B3Cuant, "B4": B4Noticias, "B5": B5Cadena}
    return {n: catalogo[n](ctx) for n in cuales}
