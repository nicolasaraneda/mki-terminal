# ============================================================
# Capa de datos point-in-time del backtest (DISEÑO.md §5).
#
# Principios:
#  1. UNA descarga al inicio de la corrida (FuenteCongelada): motor.py pasa
#     a servir desde frames congelados — los datos no pueden cambiar a
#     mitad de corrida (el TTL de la caché del motor re-descargaría) y la
#     corrida es determinista. Las funciones *_al(fecha) del motor siguen
#     recortando a <= fecha por su propia vía auditada.
#  2. Toda serie de FEATURES se construye con transformaciones
#     exclusivamente RETROSPECTIVAS (rolling/shift hacia atrás): el valor
#     en la fecha d solo usa datos <= d — point-in-time por construcción.
#  3. validar_sin_futuro() es la guardia dura: cualquier frame de features
#     con fechas posteriores a la emisión revienta con ErrorLookAhead
#     (tests/test_backtest.py lo prueba inyectando un dato futuro).
#  4. Las bases de producción se abren SOLO LECTURA (uri mode=ro).
# ============================================================

import os
import sqlite3
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

import motor
from universo import (EXCHANGE_POR_TICKER, FX_POR_EXCHANGE,
                      INDICE_LOCAL_POR_EXCHANGE, MERCADOS_POR_ABRIR,
                      MONEDA_TICKER, PARES_FX, UNIVERSO)

from backtest.emision import HORA_EMISION_UTC

DIRECTORIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_SENALES = os.path.join(DIRECTORIO, "senales.db")
RUTA_NOTICIAS = os.path.join(DIRECTORIO, "noticias.db")

FECHA_PRIMER_SELLO = date(2026, 7, 5)  # desde aquí existe sentimiento sellado

VENTANA_BUZZ = 14   # días de la media móvil de referencia del buzz


def instante_emision(fecha: date) -> datetime:
    """El instante en que se emite la predicción de `fecha` (22:15 UTC, la
    hora real del job de producción). Todo dato con marca posterior a este
    instante NO existía cuando la predicción se emitió."""
    return datetime.combine(fecha, HORA_EMISION_UTC, tzinfo=timezone.utc)


class ErrorLookAhead(Exception):
    """Un frame de features contiene datos posteriores a la emisión."""


def validar_sin_futuro(df: pd.DataFrame | pd.Series, fecha: date) -> None:
    """Aserción de índice: si el frame trae CUALQUIER fila posterior a
    `fecha`, revienta.

    ADVERTENCIA — y está aquí porque se pagó caro: llamar a esta función
    sobre un frame que el propio llamador acaba de recortar con el MISMO
    predicado (`index.date <= fecha`) NO es una guarda: su condición de
    disparo es inalcanzable por construcción (medido: 401.184 invocaciones
    en un walk-forward, cero capaces de disparar). Para eso existe
    `recortar_pit()`, que recibe la serie SIN recortar y es dueña del corte.
    Y ninguna de las dos ve una fuga que desplace VALORES sin desplazar el
    índice (`shift(-1)`): esa la detecta sólo el gate de invariancia al
    truncado (`backtest/causalidad.py`), que tiene su contraprueba."""
    if df is None or len(df) == 0:
        return
    maxima = pd.Timestamp(df.index.max()).date()
    if maxima > fecha:
        raise ErrorLookAhead(
            f"features con fecha {maxima} > emisión {fecha} — look-ahead")


def recortar_pit(serie, fecha: date):
    """Recorta `serie` a `<= fecha` Y valida — el corte lo hace la guarda,
    no el llamador, que es lo que la vuelve capaz de mirar el futuro que
    descarta en vez de validar su propio recorte.

    Comprueba, sobre la serie SIN recortar:
      1. que el índice esté ORDENADO (si no lo está, "<= fecha" no separa
         pasado de futuro y todo el resto es humo);
      2. que el recorte no arrastre ninguna fila posterior a `fecha`.
    Lo que NO puede ver, y hay que decirlo: una fuga que deje el índice
    quieto y desplace los valores. Ésa es del gate de causalidad."""
    if serie is None or len(serie) == 0:
        return serie
    idx = serie.index
    if not idx.is_monotonic_increasing:
        raise ErrorLookAhead(
            "índice no ordenado: el recorte '<= fecha' no separa pasado de "
            "futuro y la guarda no puede afirmar nada")
    if isinstance(idx, pd.DatetimeIndex):
        # searchsorted en vez de máscara booleana: el arnés hace millones de
        # recortes y `idx.date` materializa un array nuevo en cada uno.
        limite = pd.Timestamp(fecha) + pd.Timedelta(days=1)
        if idx.tz is not None:
            limite = limite.tz_localize(idx.tz)
        corte = serie.iloc[:int(idx.searchsorted(limite, side="left"))]
    elif hasattr(idx, "date"):
        corte = serie[idx.date <= fecha]
    else:
        corte = serie[idx <= pd.Timestamp(fecha)]
    validar_sin_futuro(corte, fecha)
    return corte


def _conexion_ro(ruta: str) -> sqlite3.Connection:
    """Conexión ESTRICTAMENTE de solo lectura a una base de producción."""
    return sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)


class FuenteCongelada:
    """Congela la descarga del run: baja todo UNA vez y reemplaza
    motor._datos_crudos por un servidor de esos frames (context manager).
    Para tests, `series` permite inyectar datos sintéticos sin red."""

    def __init__(self, series: pd.DataFrame | None = None,
                 ohlc: dict | None = None):
        self._series = series          # DataFrame ancho: columna por ticker
        self._ohlc = ohlc or {}        # {ticker: DataFrame[Open, Close]}
        self._original = None

    def _tickers_necesarios(self) -> tuple:
        extras = ("^SOX",) + tuple(PARES_FX) + tuple(
            INDICE_LOCAL_POR_EXCHANGE.values())
        return tuple(sorted(set(list(UNIVERSO.keys()) + list(extras))))

    def __enter__(self):
        import yfinance as yf
        if self._series is None:
            todos = self._tickers_necesarios()
            data = yf.download(list(todos), period=f"{motor.ANIOS_DATOS}y",
                               interval="1d", auto_adjust=True, progress=False)
            self._series = (data["Close"] if isinstance(data.columns, pd.MultiIndex)
                            else data[["Close"]])
            # OHLC de las acciones objetivo (gap y capturable necesitan Open;
            # motor._datos_crudos solo conserva Close). Es dato de OUTCOME,
            # no de feature — ver emision/motorbt para su uso posterior a la
            # sesión objetivo.
            for t in MERCADOS_POR_ABRIR:
                d = yf.download(t, period=f"{motor.ANIOS_DATOS}y", interval="1d",
                                auto_adjust=True, progress=False)
                if isinstance(d.columns, pd.MultiIndex):
                    d.columns = d.columns.get_level_values(0)
                self._ohlc[t] = d[["Open", "Close"]].dropna(how="all")
        self._original = motor._datos_crudos

        series = self._series

        def congelado(tickers: tuple) -> pd.DataFrame:
            presentes = [t for t in tickers if t in series.columns]
            return series[presentes].copy()

        motor._datos_crudos = congelado
        motor._cache.clear()
        return self

    def __exit__(self, *exc):
        motor._datos_crudos = self._original
        motor._cache.clear()
        return False

    # ---------- outcomes (etiquetas, no features) ----------
    def resultado_sesion(self, ticker: str, sesion: str) -> dict | None:
        """gap / retorno de sesión / retorno CAPTURABLE de una sesión local.
        None si la fuente no tiene esa sesión (descarte contado, jamás
        rellenado)."""
        ohlc = self._ohlc.get(ticker)
        if ohlc is None or ohlc.empty:
            return None
        fechas = ohlc.index.strftime("%Y-%m-%d")
        posiciones = {f: i for i, f in enumerate(fechas)}
        if sesion not in posiciones or posiciones[sesion] == 0:
            return None
        i = posiciones[sesion]
        open_obj = float(ohlc["Open"].iloc[i])
        close_obj = float(ohlc["Close"].iloc[i])
        close_ant = float(ohlc["Close"].iloc[i - 1])
        if close_ant <= 0 or open_obj <= 0:
            return None
        return {
            "gap_pct": (open_obj / close_ant - 1) * 100,
            "retorno_sesion_pct": (close_obj / close_ant - 1) * 100,
            "capturable_pct": (close_obj / open_obj - 1) * 100,
        }

    # ---------- features vectorizadas (retrospectivas) ----------
    def cierres(self, tickers: tuple) -> pd.DataFrame:
        return self._series[[t for t in tickers if t in self._series.columns]]

    def serie_benchmark(self, ticker: str) -> pd.Series:
        return self._series[ticker].dropna() if ticker in self._series.columns \
            else pd.Series(dtype=float)


def residual_rolling(ret: pd.Series, ret_idx: pd.Series | None,
                     ret_fx: pd.Series | None, ventana: int = 120) -> pd.Series:
    """Residuos de la acción contra índice local (+FX) con OLS de ventana
    RODANTE de `ventana` sesiones — la variante point-in-time vectorizada
    del _residualizar del motor (que usa ventana expansiva hasta la fecha).
    Cada beta en la fecha d usa solo las `ventana` sesiones <= d.
    La diferencia (rodante vs expansiva) se documenta en DISEÑO.md/código:
    features del backtest, jamás una señal de producción."""
    if ret_idx is None:
        # sin índice local disponible: des-mediado rodante (retrospectivo)
        return (ret - ret.rolling(ventana).mean()).dropna()
    df = pd.concat({"y": ret, "x1": ret_idx}, axis=1)
    if ret_fx is not None:
        df["x2"] = ret_fx
    df = df.dropna()
    if len(df) < ventana:
        return pd.Series(dtype=float)
    medias = df.rolling(ventana).mean()
    if ret_fx is None:
        cov = df["y"].rolling(ventana).cov(df["x1"])
        var = df["x1"].rolling(ventana).var()
        beta = cov / var.replace(0, np.nan)
        res = (df["y"] - medias["y"]) - beta * (df["x1"] - medias["x1"])
        return res.dropna()
    # dos regresores: resolver el sistema 2x2 con momentos rodantes
    c11 = df["x1"].rolling(ventana).var()
    c22 = df["x2"].rolling(ventana).var()
    c12 = df["x1"].rolling(ventana).cov(df["x2"])
    cy1 = df["y"].rolling(ventana).cov(df["x1"])
    cy2 = df["y"].rolling(ventana).cov(df["x2"])
    det = (c11 * c22 - c12 * c12).replace(0, np.nan)
    b1 = (cy1 * c22 - cy2 * c12) / det
    b2 = (cy2 * c11 - cy1 * c12) / det
    res = ((df["y"] - medias["y"])
           - b1 * (df["x1"] - medias["x1"])
           - b2 * (df["x2"] - medias["x2"]))
    return res.dropna()


def _ordinal_disponible(marca: pd.Series) -> np.ndarray:
    """Primer día de EMISIÓN (ordinal) en que un dato con marca temporal
    `marca` ya existía: su propio día si llegó antes de las 22:15 UTC, el
    siguiente si llegó después. Un dato que aparece a las 23:00 no estaba
    disponible en la emisión de ese día — sumarlo sería la fuga."""
    marca = pd.to_datetime(marca, utc=True, errors="coerce")
    dias = marca.dt.normalize()
    corte = dias + pd.Timedelta(hours=HORA_EMISION_UTC.hour,
                                minutes=HORA_EMISION_UTC.minute)
    ordinales = np.array([d.toordinal() if pd.notna(d) else 10 ** 9
                          for d in dias.dt.date])
    return ordinales + (marca > corte).to_numpy().astype(int)


class SentimientoPIT:
    """Sentimiento por acción "as of" una fecha, con grado de evidencia.

    B-1 (corregido el 2026-09-01 — la fuga que invalidó la corrida
    `20260901-061708-5.1-invalidada-por-fuga`): el dato que alimenta la
    feature NO es el titular, es el JUICIO de la IA sobre el titular, y ese
    juicio tiene su propia marca temporal (`analisis.analizado_en`). La
    versión anterior cortaba por `titulares.fecha` (publicación) y nunca
    miraba `analizado_en`: medido sobre `noticias.db`, **3.407 de 5.094
    análisis (66,9 %) se produjeron después de las 22:15 UTC de su día de
    publicación**, con rezago máximo de 320 días, y el primer juicio que
    existe en el sistema es del 2026-07-04 mientras los titulares arrancan
    el 2025-09-09.

    La disponibilidad de una fila es, por tanto, el MÁXIMO de sus dos
    marcas: `max(publicación, analizado_en)` — hacen falta las dos para que
    el número exista. (El expediente escribió "min" al enunciar el arreglo;
    la corrección va al ejecutable: con `min` bastaría una sola de las dos
    y la fuga seguiría entrando.) El corte se aplica contra el instante de
    emisión, 22:15 UTC.

    Grado A: el valor SELLADO en senales_ticker ese día (existe desde el
    05-jul-2026). Grado B: reconstrucción desde noticias.db con la MISMA
    fórmula de producción (decaimiento 0.7^días con piso 0.1 × relevancia,
    NULL→1.0) sobre las filas YA DISPONIBLES a la emisión. Ya no significa
    "el juicio llegó después": esas filas ahora no entran."""

    COLUMNAS = ["fecha", "ticker", "sentimiento", "relevancia",
                "analizado_en", "disponible_ord", "publicado_ord"]

    def __init__(self, truncar_en: date | None = None):
        limite = truncar_en.toordinal() if truncar_en else None
        self._sellado = {}
        if os.path.exists(RUTA_SENALES):
            conn = _conexion_ro(RUTA_SENALES)
            for f, t, s in conn.execute(
                    "SELECT fecha, ticker, sentimiento_ia FROM senales_ticker "
                    "WHERE sentimiento_ia IS NOT NULL"):
                if limite is not None and str(f)[:10] > truncar_en.isoformat():
                    continue
                self._sellado[(f, t)] = float(s)
            conn.close()
        self._titulares = pd.DataFrame(columns=self.COLUMNAS)
        if os.path.exists(RUTA_NOTICIAS):
            conn = _conexion_ro(RUTA_NOTICIAS)
            filas = conn.execute("""
                SELECT t.fecha, a.tickers_afectados, a.sentimiento,
                       COALESCE(a.relevancia, 1.0), a.analizado_en
                FROM analisis a JOIN titulares t ON t.id = a.titular_id
            """).fetchall()
            conn.close()
            registros = []
            for fecha_t, tickers, sent, rel, analizado in filas:
                for t in (tickers or "").split(","):
                    t = t.strip()
                    if t in UNIVERSO:
                        registros.append({"fecha": str(fecha_t)[:10], "ticker": t,
                                          "publicado_en": fecha_t,
                                          "sentimiento": float(sent),
                                          "relevancia": float(rel),
                                          "analizado_en": analizado})
            if registros:
                df = pd.DataFrame(registros)
                pub = _ordinal_disponible(df["publicado_en"])
                ana = _ordinal_disponible(df["analizado_en"])
                # max(): hacen falta LAS DOS marcas para que el dato exista
                df["disponible_ord"] = np.maximum(pub, ana)
                df["publicado_ord"] = np.array(
                    [date.fromisoformat(f).toordinal() for f in df["fecha"]])
                if limite is not None:
                    df = df[df["disponible_ord"] <= limite]
                self._titulares = df.reset_index(drop=True)
        self._indice = {}
        for t, g in self._titulares.groupby("ticker"):
            self._indice[t] = {
                "disp": g["disponible_ord"].to_numpy(),
                "pub": g["publicado_ord"].to_numpy(),
                "sent": g["sentimiento"].to_numpy(dtype=float),
                "rel": g["relevancia"].to_numpy(dtype=float),
            }
        self._memo_buzz = {}

    # ---------- sentimiento ----------
    def valor(self, ticker: str, fecha: date) -> tuple:
        """(sentimiento | None, grado 'A'|'B'). None = no había NINGÚN
        juicio de IA disponible a la emisión de `fecha`: no es un cero, es
        una ausencia, y quien la rellene con cero tiene que declararlo."""
        clave = (fecha.isoformat(), ticker)
        if clave in self._sellado:
            return self._sellado[clave], "A"
        arr = self._indice.get(ticker)
        if arr is None:
            return None, "B"
        d = fecha.toordinal()
        m = arr["disp"] <= d          # ya publicado Y ya analizado
        if not m.any():
            return None, "B"
        dias = np.maximum(d - arr["pub"][m], 0)
        pesos = np.maximum(0.7 ** dias, 0.1) * arr["rel"][m]
        if pesos.sum() <= 0:
            return None, "B"
        return float((arr["sent"][m] * pesos).sum() / pesos.sum()), "B"

    # ---------- buzz ----------
    def buzz(self, ticker: str, fecha: date) -> float | None:
        """Titulares del día vs. la media de los `VENTANA_BUZZ` días
        previos, contando SOLO los ya disponibles a la emisión.

        Antes el buzz salía del mismo join que el sentimiento y no tenía
        grado ninguno: un titular sólo entra al buzz si fue analizado, y el
        66,9 % lo fue tarde. Ahora cuenta con el mismo corte."""
        panel = self._memo_buzz.get(fecha)
        if panel is None:
            panel = self._buzz_al(fecha)
            self._memo_buzz[fecha] = panel
        return panel.get(ticker)

    def _buzz_al(self, fecha: date) -> dict:
        df = self._titulares
        if df.empty:
            return {}
        d = fecha.toordinal()
        disp = df["disponible_ord"].to_numpy()
        pub = df["publicado_ord"].to_numpy()
        vivos = disp <= d
        hoy = vivos & (pub == d)
        previos = vivos & (pub >= d - VENTANA_BUZZ) & (pub <= d - 1)
        tickers = df["ticker"].to_numpy()
        salida = {}
        for t in np.unique(tickers[vivos]):
            es_t = tickers == t
            base = int((previos & es_t).sum()) / VENTANA_BUZZ
            if base <= 0:
                continue          # sin base no hay razón: ausencia, no cero
            salida[t] = float(int((hoy & es_t).sum()) / base)
        return salida

    # ---------- diagnóstico (no es feature: es evidencia) ----------
    def cobertura(self) -> dict:
        """Qué queda del sentimiento después del corte honesto."""
        df = self._titulares
        if df.empty:
            return {"filas": 0}
        pub = df["publicado_ord"].to_numpy()
        disp = df["disponible_ord"].to_numpy()
        tarde = int((disp > pub).sum())
        return {
            "filas_ticker_analisis": int(len(df)),
            "filas_disponibles_tarde": tarde,
            "pct_tarde": round(100 * tarde / len(df), 1),
            "rezago_max_dias": int((disp - pub).max()),
            "primer_dia_con_dato_disponible": date.fromordinal(
                int(disp.min())).isoformat(),
            "primer_titular_publicado": date.fromordinal(
                int(pub.min())).isoformat(),
        }


def predicciones_selladas() -> pd.DataFrame:
    """Las predicciones selladas reales (para la auditoría de reproducción
    de B2). Solo lectura."""
    if not os.path.exists(RUTA_SENALES):
        return pd.DataFrame()
    conn = _conexion_ro(RUTA_SENALES)
    df = pd.read_sql_query("""
        SELECT fecha, ticker, apertura_estimada_pct, sesion_objetivo
        FROM senales_ticker
        WHERE apertura_estimada_pct IS NOT NULL AND timestamp_utc IS NOT NULL
    """, conn)
    conn.close()
    return df
