# ============================================================
# Calendarios de mercado (Etapa 4.6) — la fundación del timing honesto.
#
# REGLA MAESTRA: una predicción solo es verificable si fue emitida ANTES
# de la apertura de la sesión que intenta anticipar, y eso debe ser
# demostrable con timestamps UTC. Este módulo responde las preguntas de
# timing: ¿cuál es la próxima sesión de este exchange después de este
# instante? ¿a qué hora UTC abre y cierra?
#
# Usa exchange-calendars (feriados y horarios reales por bolsa). El cruce
# de fecha por huso horario queda cubierto de forma natural: la sesión del
# lunes de Seúl (KRX) abre el domingo ~00:00 UTC, y eso es exactamente lo
# que devuelve apertura_utc().
# ============================================================

from datetime import datetime, timezone
from functools import lru_cache

import exchange_calendars as xcals
import pandas as pd


@lru_cache(maxsize=8)
def _calendario(exchange: str):
    return xcals.get_calendar(exchange)


def apertura_utc(exchange: str, sesion: str) -> datetime:
    """Hora UTC de apertura de una sesión (fecha local 'YYYY-MM-DD') de un exchange."""
    return _calendario(exchange).session_open(sesion).to_pydatetime()


def cierre_utc(exchange: str, sesion: str) -> datetime:
    """Hora UTC de cierre de una sesión de un exchange."""
    return _calendario(exchange).session_close(sesion).to_pydatetime()


def es_sesion(exchange: str, fecha: str) -> bool:
    return _calendario(exchange).is_session(fecha)


def proxima_sesion_despues_de(exchange: str, instante_utc: datetime) -> tuple:
    """La primera sesión de `exchange` cuya APERTURA es posterior a `instante_utc`.

    Esa es la sesión objetivo de una predicción emitida en ese instante:
    la próxima vez que ese mercado va a abrir. Devuelve
    (sesion 'YYYY-MM-DD', apertura_utc, cierre_utc)."""
    cal = _calendario(exchange)
    ts = pd.Timestamp(instante_utc)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    # minute_to_future_session ancla en el calendario de minutos de la bolsa;
    # más simple y robusto: buscar linealmente desde la fecha UTC del instante.
    candidata = ts.tz_convert("UTC").normalize().tz_localize(None)
    for _ in range(15):  # nunca hay 15 días corridos sin sesión
        fecha_str = candidata.date().isoformat()
        if cal.is_session(fecha_str):
            open_utc = cal.session_open(fecha_str)
            if open_utc > ts:
                return fecha_str, open_utc.to_pydatetime(), cal.session_close(fecha_str).to_pydatetime()
        candidata += pd.Timedelta(days=1)
    raise RuntimeError(f"No se encontró sesión futura para {exchange} tras {instante_utc}")


def sesion_anterior(exchange: str, sesion: str) -> str:
    """La sesión inmediatamente anterior a `sesion` en el calendario del exchange."""
    cal = _calendario(exchange)
    return cal.previous_session(sesion).date().isoformat()


def sesion_ya_cerro(exchange: str, sesion: str, margen_horas: float = 2.0) -> bool:
    """True si la sesión ya cerró hace al menos `margen_horas` (margen para que
    Yahoo publique los datos de cierre)."""
    ahora = datetime.now(timezone.utc)
    cierre = cierre_utc(exchange, sesion)
    return (ahora - cierre).total_seconds() >= margen_horas * 3600


def tabla_horarios() -> pd.DataFrame:
    """Tabla de referencia: horarios de apertura/cierre en UTC por exchange,
    usando la próxima sesión de cada uno (los horarios UTC cambian con el
    horario de verano local, así que se muestran los vigentes)."""
    ahora = datetime.now(timezone.utc)
    filas = []
    for exchange, nombre_ex in [("XNYS", "NYSE / Nasdaq (EE.UU.)"),
                                ("XKRX", "KRX (Corea)"),
                                ("XTAI", "TWSE (Taiwán)"),
                                ("XTKS", "TSE (Japón)"),
                                ("XETR", "XETRA (Alemania)")]:
        try:
            sesion, open_u, close_u = proxima_sesion_despues_de(exchange, ahora)
            filas.append({
                "Exchange": nombre_ex,
                "Próxima sesión (local)": sesion,
                "Apertura UTC": open_u.strftime("%Y-%m-%d %H:%M"),
                "Cierre UTC": close_u.strftime("%Y-%m-%d %H:%M"),
            })
        except Exception:
            continue
    return pd.DataFrame(filas)
