# ============================================================
# Etapa 5.0 — registro de costos de IA y guardarraíl de presupuesto.
#
#   Constitución 5.0: jamás un loop sin límite de gasto. Cada corrida que
#   gasta (o decide no gastar) en la API de Anthropic queda registrada como
#   UNA línea JSON en data/costos_ia.log (gitignoreado, como todo *.log).
#   El tope diario vive en .env: NOTICIAS_PRESUPUESTO_USD_DIA (default 0.50).
#
#   Consumidores: mki_noticias.py (freno duro entre lotes), mki_vigia.py
#   (¿corrió el job hoy?) y la vista /salud del dashboard (gasto vs tope).
# ============================================================

import json
import os
from datetime import date, datetime, timezone

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_LOG = os.path.join(DIRECTORIO, "data", "costos_ia.log")
TOPE_DEFAULT_USD = 0.50


def tope_diario_usd() -> float:
    """Tope de gasto diario en USD, desde .env. Un valor ausente, no numérico
    o ≤ 0 cae al default conservador — el guardarraíl no puede desactivarse
    por un typo."""
    try:
        valor = float(os.environ.get("NOTICIAS_PRESUPUESTO_USD_DIA", ""))
        return valor if valor > 0 else TOPE_DEFAULT_USD
    except (TypeError, ValueError):
        return TOPE_DEFAULT_USD


def _leer_corridas() -> list:
    if not os.path.exists(RUTA_LOG):
        return []
    corridas = []
    with open(RUTA_LOG, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                corridas.append(json.loads(linea))
            except json.JSONDecodeError:
                continue  # una línea corrupta no puede tumbar el guardarraíl
    return corridas


def corridas_del_dia(origen: str = None, fecha: str = None) -> list:
    fecha = fecha or date.today().isoformat()
    return [c for c in _leer_corridas()
            if c.get("fecha") == fecha and (origen is None or c.get("origen") == origen)]


def gasto_del_dia(fecha: str = None) -> float:
    return round(sum(float(c.get("costo_usd", 0.0)) for c in corridas_del_dia(fecha=fecha)), 6)


def gasto_del_mes(anio_mes: str = None) -> float:
    """Suma del mes 'YYYY-MM' (default: el actual) — para la vista /salud."""
    anio_mes = anio_mes or date.today().isoformat()[:7]
    return round(sum(float(c.get("costo_usd", 0.0)) for c in _leer_corridas()
                     if str(c.get("fecha", "")).startswith(anio_mes)), 6)


def estado_presupuesto() -> dict:
    gasto = gasto_del_dia()
    tope = tope_diario_usd()
    return {"fecha": date.today().isoformat(), "gasto_usd": gasto,
            "tope_usd": tope, "restante_usd": round(max(0.0, tope - gasto), 6),
            "agotado": gasto >= tope}


def registrar_corrida(origen: str, costo_usd: float, detalle: dict = None) -> dict:
    """Registra una corrida en el log de costos y devuelve la línea escrita
    (incluye el acumulado del día YA CONTANDO esta corrida)."""
    os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)
    registro = {
        "fecha": date.today().isoformat(),
        "hora_utc": datetime.now(timezone.utc).isoformat(),
        "origen": origen,
        "costo_usd": round(float(costo_usd), 6),
        "tope_usd": tope_diario_usd(),
        **(detalle or {}),
    }
    registro["acumulado_dia_usd"] = round(gasto_del_dia() + registro["costo_usd"], 6)
    with open(RUTA_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return registro
