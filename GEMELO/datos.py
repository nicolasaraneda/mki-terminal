# ============================================================
# GEMELO/datos.py — adquisición de series con SEMÁNTICA DE DISPONIBILIDAD
# (Etapa 6.0.0 WS2a; especificado en GEMELO/DISEÑO.md §4.1).
#
# Caché en disco con TTL y las dos compuertas de robustez (ffill acotado y
# cobertura mínima) se incorporan de `vcalderone/equity-direction-research`
# v2.1.0, licencia MIT — atribución en DECISIONES.md §24.
#
# AISLAMIENTO: no se importa nada del camino de sellado. La descarga se
# DUPLICA a propósito en vez de reutilizar motor._datos_crudos.
#
# ============================================================
# LA TRAMPA CENTRAL: las barras diarias NO son el mismo instante
# ============================================================
# Dos barras de yfinance con la misma etiqueta de fecha pueden estar
# separadas por catorce horas. ^KS11 del día D cerró a las 06:30 UTC;
# ^SOX del día D cerró a las 20:00 UTC. Bajo el mismo rótulo "D".
#
# No es cosmético: es la vía por la que entra look-ahead sin que ninguna
# guarda se queje, de la misma familia que el problema que cerró el embargo
# (DECISIONES.md §27). Por eso cada serie lleva su hora de cierre SELLADA
# en el código y su available_at CALCULADO, igual que el SOX ya lo lleva en
# producción — y hay un test que revienta si una feature combina dos series
# cuyo available_at es posterior a la emisión.
#
# EMISIÓN: 18:15 Chile = 22:15 UTC.
#
# | Serie      | Bloque         | Cierre local   | UTC (peor caso) | bar del día D |
# |------------|----------------|----------------|-----------------|---------------|
# | ^SOX       | contagio       | 16:00 ET       | 21:00           | conocible     |
# | ES=F       | overnight US   | 17:00 ET       | 22:00           | conocible ⚠   |
# | NQ=F       | overnight US   | 17:00 ET       | 22:00           | conocible ⚠   |
# | ^VIX       | volatilidad    | 16:15 ET       | 21:15           | conocible     |
# | ^VIX3M     | volatilidad    | 16:15 ET       | 21:15           | conocible     |
# | HYG        | crédito        | 16:00 ET       | 21:00           | conocible     |
# | LQD        | crédito        | 16:00 ET       | 21:00           | conocible     |
# | KRW=X      | divisa         | continuo       | 22:00           | conocible     |
# | TWD=X      | divisa         | continuo       | 22:00           | conocible     |
# | JPY=X      | divisa         | continuo       | 22:00           | conocible     |
# | EURUSD=X   | divisa         | continuo       | 22:00           | conocible     |
# | ^KS11      | mercado local  | 15:30 KST      | 06:30           | conocible     |
# | ^TWII      | mercado local  | 13:30 TWT      | 05:30           | conocible     |
# | ^N225      | mercado local  | 15:00 JST      | 06:00           | conocible     |
# | ^GDAXI     | mercado local  | 17:30 CET      | 16:30           | conocible     |
#
# "UTC (peor caso)" usa el offset MÁS TARDÍO del año: horario de INVIERNO
# para ET (EST, UTC-5) y CET (UTC+1). Sellar el peor caso y no el habitual
# es lo que hace que la afirmación "conocible a las 22:15" valga los 365
# días, y no solo en verano. KST/TWT/JST no tienen horario de verano.
#
# ⚠ LOS FUTUROS SON LA SERIE MÁS AJUSTADA del conjunto: su barra diaria
# cierra a las 17:00 ET, que en invierno son las 22:00 UTC — quince minutos
# antes de la emisión. Es holgura real pero mínima. Se documenta porque:
#   (a) es exactamente el bloque que más valor aporta (se mueve entre el
#       cierre del SOX y la apertura asiática, que es información que hoy
#       se tira), así que retroceder a D-1 lo vaciaría de sentido; y
#   (b) el sistema en producción usa un margen de publicación de 2 h para
#       decidir si una sesión es conocible (`calendarios.sesion_ya_cerro`).
#       Con ESE margen, los futuros NO pasarían. Ver MARGEN_PUBLICACION_H.
# ============================================================

import hashlib
import json
import os
import time as _time
from datetime import date, datetime, time, timedelta, timezone

import pandas as pd
import yfinance as yf

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
DIR_CACHE = os.path.join(DIRECTORIO, "cache")

# Emisión real del sistema: 18:15 Chile = 22:15 UTC.
HORA_EMISION_UTC = time(22, 15)

# Margen de publicación exigido a una serie para considerarla conocible.
# 0.0 = basta con que la barra haya cerrado (criterio de esta capa de
# investigación). El sistema en producción usa 2 h para las sesiones que
# verifica; con 2 h aquí, ES=F/NQ=F/las divisas quedarían fuera. Se deja
# como parámetro para que la tensión sea MEDIBLE y no una nota al pie:
# tests/test_gemelo_datos.py declara qué series caen con cada margen.
MARGEN_PUBLICACION_H = 0.0

TTL_CACHE_HORAS = 12
ANIOS_DATOS = 8
FFILL_LIMITE_DIAS = 5
COBERTURA_MINIMA = 0.80


class SerieNoConocible(Exception):
    """Una serie se usó para una emisión en la que su barra aún no cerró."""


class _Serie:
    """Una serie con su semántica de disponibilidad sellada."""

    def __init__(self, ticker, bloque, descripcion, cierre_local,
                 cierre_utc_peor_caso):
        self.ticker = ticker
        self.bloque = bloque
        self.descripcion = descripcion
        self.cierre_local = cierre_local
        self.cierre_utc = cierre_utc_peor_caso

    def available_at(self, dia: date) -> datetime:
        """Instante UTC en que la barra del día `dia` pasa a ser conocible.
        Se calcula, no se asume — igual que el `available_at` que el sello
        de producción ya guarda para el SOX."""
        return datetime.combine(dia, self.cierre_utc, tzinfo=timezone.utc)

    def conocible_en(self, dia: date, emision: datetime,
                     margen_h: float = MARGEN_PUBLICACION_H) -> bool:
        return (emision - self.available_at(dia)).total_seconds() >= margen_h * 3600

    def __repr__(self):
        return f"_Serie({self.ticker!r}, cierre_utc={self.cierre_utc})"


def _s(t, b, d, cl, h, m):
    return _Serie(t, b, d, cl, time(h, m))


# El catálogo. Duplicado a propósito respecto de universo.py: GEMELO no
# importa nada de producción, y ninguno de estos tickers está en UNIVERSO.
CATALOGO = {s.ticker: s for s in (
    _s("^SOX",     "contagio",      "Índice de semiconductores", "16:00 ET", 21, 0),
    _s("ES=F",     "overnight_us",  "Futuro S&P 500",            "17:00 ET", 22, 0),
    _s("NQ=F",     "overnight_us",  "Futuro Nasdaq 100",         "17:00 ET", 22, 0),
    _s("^VIX",     "volatilidad",   "VIX spot",                  "16:15 ET", 21, 15),
    _s("^VIX3M",   "volatilidad",   "VIX a 3 meses",             "16:15 ET", 21, 15),
    _s("HYG",      "credito",       "ETF de alto rendimiento",   "16:00 ET", 21, 0),
    _s("LQD",      "credito",       "ETF grado de inversión",    "16:00 ET", 21, 0),
    _s("KRW=X",    "divisa",        "USD/KRW",                   "continuo", 22, 0),
    _s("TWD=X",    "divisa",        "USD/TWD",                   "continuo", 22, 0),
    _s("JPY=X",    "divisa",        "USD/JPY",                   "continuo", 22, 0),
    _s("EURUSD=X", "divisa",        "EUR/USD",                   "continuo", 22, 0),
    _s("^KS11",    "mercado_local", "KOSPI",                     "15:30 KST", 6, 30),
    _s("^TWII",    "mercado_local", "TWSE",                      "13:30 TWT", 5, 30),
    _s("^N225",    "mercado_local", "Nikkei 225",                "15:00 JST", 6, 0),
    _s("^GDAXI",   "mercado_local", "DAX",                       "17:30 CET", 16, 30),
)}

TICKERS = tuple(CATALOGO)


def emision_utc(dia: date) -> datetime:
    """El instante de emisión del día `dia`."""
    return datetime.combine(dia, HORA_EMISION_UTC, tzinfo=timezone.utc)


def verificar_conocibles(tickers, dia: date,
                         margen_h: float = MARGEN_PUBLICACION_H) -> None:
    """Revienta si alguna serie NO es conocible a la emisión de `dia`.

    Es la guarda dura de la asincronía: se llama antes de construir
    cualquier feature, para que combinar dos barras con el mismo rótulo
    pero distinto instante sea imposible en vez de improbable.
    """
    emision = emision_utc(dia)
    culpables = [
        (t, CATALOGO[t].available_at(dia).isoformat())
        for t in tickers
        if t in CATALOGO and not CATALOGO[t].conocible_en(dia, emision, margen_h)
    ]
    if culpables:
        detalle = "; ".join(f"{t} disponible {a}" for t, a in culpables)
        raise SerieNoConocible(
            f"emisión {emision.isoformat()} (margen {margen_h} h): {detalle}")


def tabla_disponibilidad(dia: date | None = None) -> pd.DataFrame:
    """La tabla del docstring, calculada. Que exista como DATO y no solo
    como comentario es lo que permite testearla."""
    dia = dia or date(2026, 8, 24)
    emision = emision_utc(dia)
    return pd.DataFrame([{
        "ticker": s.ticker, "bloque": s.bloque, "cierre_local": s.cierre_local,
        "cierre_utc": s.cierre_utc.strftime("%H:%M"),
        "available_at": s.available_at(dia).isoformat(),
        "horas_antes_de_emision": round(
            (emision - s.available_at(dia)).total_seconds() / 3600, 2),
        "conocible_dia_D": s.conocible_en(dia, emision),
    } for s in CATALOGO.values()])


# ------------------------------------------------------------
# Caché en disco con TTL
# ------------------------------------------------------------
def _ruta_cache(tickers, anios: int) -> str:
    clave = hashlib.sha256(
        json.dumps([sorted(tickers), anios]).encode()).hexdigest()[:16]
    return os.path.join(DIR_CACHE, f"cierres_{clave}.csv")


def _cache_vigente(ruta: str, ttl_horas: float) -> bool:
    if not os.path.exists(ruta):
        return False
    return (_time.time() - os.path.getmtime(ruta)) < ttl_horas * 3600


def descargar_cierres(tickers=TICKERS, anios: int = ANIOS_DATOS,
                      ttl_horas: float = TTL_CACHE_HORAS,
                      usar_cache: bool = True) -> pd.DataFrame:
    """Cierres diarios. Caché en disco con TTL: sin él, cada iteración de
    investigación vuelve a bajar años de historia y Yahoo acaba limitando."""
    tickers = tuple(tickers)
    ruta = _ruta_cache(tickers, anios)
    if usar_cache and _cache_vigente(ruta, ttl_horas):
        df = pd.read_csv(ruta, index_col=0, parse_dates=True)
        return df.reindex(columns=[t for t in tickers if t in df.columns])

    data = yf.download(list(tickers), period=f"{anios}y", interval="1d",
                       auto_adjust=True, progress=False)
    if data.empty:
        return pd.DataFrame()
    cierres = (data["Close"] if isinstance(data.columns, pd.MultiIndex)
               else data[["Close"]])
    if isinstance(cierres, pd.Series):
        cierres = cierres.to_frame(name=tickers[0])
    cierres = cierres.reindex(columns=[t for t in tickers if t in cierres.columns])
    if usar_cache:
        try:
            os.makedirs(DIR_CACHE, exist_ok=True)
            cierres.to_csv(ruta)
        except OSError:
            pass  # una caché que no escribe no puede tumbar la investigación
    return cierres


# ------------------------------------------------------------
# Compuertas de robustez
# ------------------------------------------------------------
def ffill_acotado(df: pd.DataFrame, limite: int = FFILL_LIMITE_DIAS) -> pd.DataFrame:
    """ffill con TOPE. Un ffill sin límite alimenta para siempre el último
    valor de una serie muerta, y el modelo nunca se entera: la feature
    sigue existiendo, constante, aparentando dato."""
    return df.ffill(limit=limite)


def filtrar_por_cobertura(df: pd.DataFrame, minimo: float = COBERTURA_MINIMA,
                          objetivo: pd.Index | None = None) -> tuple:
    """Descarta columnas con cobertura < `minimo` sobre el histórico del
    objetivo. Devuelve (df_filtrado, descartadas).

    Sin esto, un `dropna()` posterior alinea por la serie más corta y borra
    años de TODAS las demás en silencio: ^VIX3M arranca ~2017 y bastaría
    para amputar el histórico entero sin un solo aviso. Se descarta la
    serie corta con aviso explícito, no el histórico de las buenas.
    """
    if df.empty:
        return df, []
    objetivo = objetivo if objetivo is not None else df.index
    n = len(objetivo)
    if n == 0:
        return df, []
    cobertura = df.reindex(objetivo).notna().sum() / n
    descartadas = [{"ticker": c, "cobertura": round(float(cobertura[c]), 3)}
                   for c in df.columns if cobertura[c] < minimo]
    quedan = [c for c in df.columns if cobertura[c] >= minimo]
    return df[quedan], descartadas


def series_para_investigacion(tickers=TICKERS, anios: int = ANIOS_DATOS,
                              ttl_horas: float = TTL_CACHE_HORAS,
                              usar_cache: bool = True,
                              minimo_cobertura: float = COBERTURA_MINIMA) -> tuple:
    """Punto ÚNICO de entrada de datos crudos: descarga, ffill acotado y
    filtro de cobertura. Que sea uno solo es lo que permite al test de
    causalidad truncar la entrada y comprobar la invariancia."""
    crudos = descargar_cierres(tickers, anios, ttl_horas, usar_cache)
    if crudos.empty:
        return crudos, []
    df, descartadas = filtrar_por_cobertura(crudos, minimo_cobertura)
    return ffill_acotado(df), descartadas
