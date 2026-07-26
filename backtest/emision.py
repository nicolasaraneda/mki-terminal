# ============================================================
# El reloj de emisión del backtest (DISEÑO.md §4).
#
# Cada día hábil de Chile a las 22:15 UTC (la hora real del job de
# producción) se simula una emisión. La sesión objetivo de cada acción es
# la próxima apertura de SU bolsa después de ese instante — con los
# feriados reales de exchange-calendars, exactamente la función que usa el
# sistema en vivo. La regla maestra vive aquí como código: una emisión
# cuya apertura objetivo no sea ESTRICTAMENTE posterior revienta.
# ============================================================

from datetime import date, datetime, time, timedelta, timezone

import calendarios

HORA_EMISION_UTC = time(22, 15)


def emisiones(desde: date, hasta: date) -> list:
    """Instantes de emisión simulados: lunes a viernes, 22:15 UTC."""
    resultado = []
    d = desde
    while d <= hasta:
        if d.weekday() < 5:
            resultado.append(datetime.combine(d, HORA_EMISION_UTC, tzinfo=timezone.utc))
        d += timedelta(days=1)
    return resultado


def sesion_objetivo(exchange: str, emision: datetime) -> tuple:
    """(sesion, apertura_utc, cierre_utc) de la sesión que esta emisión
    anticipa. REGLA MAESTRA: la apertura debe ser estrictamente posterior
    a la emisión — si el calendario devolviera otra cosa, es un bug del
    framework y debe reventar, no degradarse."""
    sesion, apertura, cierre = calendarios.proxima_sesion_despues_de(exchange, emision)
    if apertura <= emision:
        raise RuntimeError(
            f"regla maestra violada: apertura {apertura} <= emisión {emision}")
    return sesion, apertura, cierre


def sesion_conocida_al(exchange: str, sesion: str, instante: datetime) -> bool:
    """¿El outcome de `sesion` era CONOCIBLE en `instante`? (cierre + 2h de
    margen de publicación, el mismo criterio del verificador en vivo).
    Gobierna qué filas pueden entrar a un set de entrenamiento."""
    try:
        cierre = calendarios.cierre_utc(exchange, sesion)
    except Exception:
        return False
    return (instante - cierre).total_seconds() >= 2 * 3600
