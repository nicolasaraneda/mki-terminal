# ============================================================
# dinero/derivacion.py — de dónde salen los números de reglas.json.
#
# El encargo lo dice sin rodeos: "No inventes los números". Así que ninguno
# de los parámetros del riel es un valor elegido a ojo, y ninguno se elige
# mirando cómo le fue en la cuenta en papel —eso sería escoger la vara
# después de ver el tiro—. Cada uno sale de una REGLA DE DERIVACIÓN escrita
# acá, y hay un test que recomputa la regla y la compara con lo guardado.
#
# Las reglas:
#
#   umbral_senal_pp = k × costo de ida y vuelta de la orden de referencia
#       del propio juego. Una señal que no supera lo que cuesta entrar y
#       salir no es una señal: es una donación al corredor.
#
#   tope_posicion_pct = 1 / (número de posiciones simultáneas que el
#       presupuesto permite físicamente). Con 500 dólares y acciones
#       enteras, ese número es chico y conviene que se vea.
#
#   tenencia_minima_dias_habiles: de los horizontes PRE-REGISTRADOS del
#       riel (20 y 60 días hábiles). No se inventa un tercer horizonte.
#
#   presupuestos diario/semanal/mensual: del ritmo de despliegue declarado
#       (en cuántas semanas se pone a trabajar todo el capital).
#
#   apagado_por_perdida_pct = k × desviación estándar del retorno a 60 días
#       hábiles del ETF del sector, MEDIDA sobre los precios congelados. Un
#       interruptor que salta con un vaivén normal del mercado no es un
#       interruptor: es ruido con autoridad.
# ============================================================
from __future__ import annotations

import math

import numpy as np

# El ETF de referencia para la volatilidad del sector es el mismo BENCHMARK
# que el riel de medición ya usa. Se nombra acá como cadena y NO se importa
# universo.py: el aislamiento vale más que ahorrar una constante.
ETF_REFERENCIA = "SMH"
HORIZONTE_LARGO_HABILES = 60


def costo_ida_y_vuelta_pp(monto_usd: float, precio_usd: float,
                          costos: dict) -> float:
    """Cuánto cuesta, en puntos porcentuales del monto, entrar y salir.

    Comisión de compra + comisión de venta + deslizamiento de los dos lados.
    Es el piso absoluto de cualquier umbral con sentido."""
    if monto_usd <= 0 or precio_usd <= 0:
        return math.inf
    n = int(monto_usd // precio_usd)
    if n <= 0:
        return math.inf
    efectivo = n * precio_usd
    bruta = max(costos["comision_minima_usd"],
                costos["comision_por_accion_usd"] * n)
    com = min(bruta, costos["comision_tope_pct_del_monto"] / 100.0 * efectivo)
    desliz = costos["deslizamiento_pb_por_lado"] / 100.0   # pb → pp
    return 2.0 * (100.0 * com / efectivo) + 2.0 * desliz


def umbral_derivado_pp(k: float, tope_posicion_pct: float, techo_usd: float,
                       precio_referencia_usd: float, costos: dict) -> float:
    """k veces el costo de ida y vuelta de la orden de referencia del juego."""
    monto = techo_usd * tope_posicion_pct / 100.0
    return round(k * costo_ida_y_vuelta_pp(monto, precio_referencia_usd, costos), 2)


def sigma_60d_pct(cierres, ticker: str = ETF_REFERENCIA,
                  horizonte: int = HORIZONTE_LARGO_HABILES) -> float:
    """Desviación estándar del retorno a `horizonte` días hábiles, en %.

    Se calcula sobre ventanas SOLAPADAS y eso infla la muestra sin inflar
    la información: el número sirve para dimensionar un interruptor, no
    para sostener una afirmación con intervalo."""
    serie = cierres[ticker].dropna()
    ret = (serie.shift(-horizonte) / serie - 1.0).dropna()
    return float(np.std(ret.to_numpy(), ddof=1) * 100.0)


def apagado_derivado_pct(k: float, sigma_pct: float) -> float:
    return round(k * sigma_pct, 1)
