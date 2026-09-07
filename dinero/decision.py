# ============================================================
# dinero/decision.py — LA CAPA QUE FALTABA: de predicción a orden.
#
# Hasta la corrida 10 el proyecto predecía y se medía, y no tenía nada que
# convirtiera una predicción en una orden. Esto es esa pieza.
#
# CONTRATO, y es el punto entero del archivo:
#   · función PURA. Entran señales, cartera, presupuesto y reglas; sale una
#     lista de órdenes propuestas. No hay efectos laterales, no hay red, no
#     se escribe en senales.db ni en ninguna otra base, no se lee la hora
#     del reloj (el día entra como argumento).
#   · DETERMINISTA. La misma entrada da exactamente la misma salida, y hay
#     un test de propiedad que lo comprueba en vez de confiar.
#   · Los NÚMEROS NO VIVEN ACÁ. Umbrales, topes, tenencia y presupuestos
#     están en `dinero/reglas.json`, versionado, y ninguno está firmado
#     todavía: hasta que Nicolás firme rige el juego `conservador`, por
#     regla escrita y no por su resultado en la cuenta en papel.
#   · NADA de este archivo envía una orden a una corredora. Una "orden" acá
#     es un registro de texto que la cuenta en papel del bloque 4 ejecuta
#     contra precios guardados. No hay cuenta abierta.
# ============================================================
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, replace
from datetime import date

import numpy as np

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_REGLAS = os.path.join(DIRECTORIO, "reglas.json")

COMPRA = "compra"
VENTA = "venta"


# ------------------------------------------------------------
# Los tipos. Inmutables a propósito: una capa de decisión que muta su
# entrada es una capa de decisión con efectos laterales.
# ------------------------------------------------------------
@dataclass(frozen=True)
class Senal:
    """Una señal del día para un instrumento.

    `magnitud_pp` es el movimiento esperado en puntos porcentuales sobre el
    horizonte del riel. `banda_baja_pp`/`banda_alta_pp` son su intervalo:
    una señal SIN intervalo no se puede usar para decidir y la capa la
    rechaza, que es la misma regla que rige en todo el proyecto."""
    ticker: str
    magnitud_pp: float
    banda_baja_pp: float
    banda_alta_pp: float

    @property
    def cruza_cero(self) -> bool:
        return self.banda_baja_pp <= 0.0 <= self.banda_alta_pp


@dataclass(frozen=True)
class Posicion:
    ticker: str
    acciones: int
    costo_total_usd: float     # incluida la comisión pagada al entrar
    abierta_el: date


@dataclass(frozen=True)
class Cartera:
    efectivo_usd: float
    posiciones: tuple = ()

    def por_ticker(self, ticker: str):
        for p in self.posiciones:
            if p.ticker == ticker:
                return p
        return None


@dataclass(frozen=True)
class EstadoRiel:
    """Lo que el riel arrastra entre días: cuánto lleva gastado en cada
    ventana y cuánto lleva perdido. El interruptor NO se calcula acá dentro
    a partir de la pérdida y ya: se calcula, se declara, y una vez apagado
    sólo lo reactiva una firma humana."""
    gastado_hoy_usd: float = 0.0
    gastado_semana_usd: float = 0.0
    gastado_mes_usd: float = 0.0
    perdida_acumulada_usd: float = 0.0
    apagado: bool = False
    motivo_apagado: str = ""


@dataclass(frozen=True)
class Orden:
    ticker: str
    lado: str                  # compra | venta
    acciones: int
    precio_ref_usd: float
    monto_usd: float           # acciones * precio
    comision_usd: float
    desembolso_usd: float      # lo que sale de la caja (compra) o entra (venta)
    motivo: str


@dataclass(frozen=True)
class Decision:
    """Salida completa: las órdenes Y por qué no se emitieron las otras.
    Un motor que sólo devuelve lo que hizo es un motor imposible de auditar."""
    dia: date
    ordenes: tuple = ()
    descartes: tuple = ()      # (ticker, razón)
    riel_apagado: bool = False


# ------------------------------------------------------------
# Reglas
# ------------------------------------------------------------
def cargar_reglas(ruta: str = RUTA_REGLAS) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def juego(cfg: dict, nombre: str | None = None) -> dict:
    """Devuelve el juego de parámetros activo.

    Sin firma humana, rige el conservador. Esto NO es una preferencia de
    estilo: es la regla escrita del encargo, para que el juego por defecto
    no lo elija el resultado de la cuenta en papel."""
    juegos = cfg["juegos"]
    nombre = nombre or cfg.get("juego_activo") or "conservador"
    if nombre not in juegos:
        raise KeyError(f"juego desconocido: {nombre}; hay {sorted(juegos)}")
    return juegos[nombre]


def _comision(n_acciones: int, precio: float, costos: dict) -> float:
    if n_acciones <= 0:
        return 0.0
    monto = n_acciones * precio
    bruta = max(costos["comision_minima_usd"],
                costos["comision_por_accion_usd"] * n_acciones)
    return min(bruta, costos["comision_tope_pct_del_monto"] / 100.0 * monto)


# ------------------------------------------------------------
# La función
# ------------------------------------------------------------
def proponer_ordenes(senales, cartera: Cartera, presupuesto_usd: float,
                     cfg: dict, dia: date, precios_ref: dict,
                     estado: EstadoRiel | None = None,
                     nombre_juego: str | None = None) -> Decision:
    """De las señales del día a una lista de órdenes propuestas.

    El orden en que se evalúan los candidatos es determinista y explícito:
    por magnitud de señal descendente y, ante empate, por ticker. Dejarlo al
    orden de un diccionario sería introducir una dependencia invisible."""
    estado = estado or EstadoRiel()
    j = juego(cfg, nombre_juego)
    costos = cfg["costos"]
    descartes = []

    # --- el interruptor va PRIMERO: apagado es apagado ---
    if estado.apagado:
        return Decision(dia=dia, ordenes=(), riel_apagado=True,
                        descartes=(("*", "riel apagado: " +
                                    (estado.motivo_apagado or "sin motivo "
                                     "registrado") + ". Reactivar exige "
                                    "firma humana."),))
    tope_perdida = presupuesto_usd * j["apagado_por_perdida_pct"] / 100.0
    if estado.perdida_acumulada_usd >= tope_perdida > 0:
        return Decision(
            dia=dia, ordenes=(), riel_apagado=True,
            descartes=(("*", f"pérdida acumulada {estado.perdida_acumulada_usd:.2f} "
                        f"USD alcanzó el tope de {tope_perdida:.2f} USD "
                        f"({j['apagado_por_perdida_pct']}% del presupuesto). "
                        f"El riel se apaga y reactivar exige firma humana."),))

    # --- ventas primero: liberan caja, y la tenencia mínima manda ---
    ordenes = []
    caja = cartera.efectivo_usd
    minimo_habiles = j["tenencia_minima_dias_habiles"]
    for pos in sorted(cartera.posiciones, key=lambda p: p.ticker):
        s = next((x for x in senales if x.ticker == pos.ticker), None)
        precio = precios_ref.get(pos.ticker)
        if precio is None:
            descartes.append((pos.ticker, "sin precio de referencia: no se "
                                          "opera a ciegas"))
            continue
        quiere_salir = s is not None and s.magnitud_pp <= -j["umbral_senal_pp"]
        if not quiere_salir:
            continue
        # Días HÁBILES, no de calendario: la tenencia mínima se deriva de
        # los horizontes pre-registrados (20 y 60 días hábiles) y contarla
        # en días corridos la acortaría un 40% sin que nadie lo note.
        habiles = int(np.busday_count(pos.abierta_el, dia))
        if habiles < minimo_habiles:
            descartes.append((pos.ticker,
                              f"tenencia mínima: lleva {habiles} días "
                              f"hábiles de {minimo_habiles}"))
            continue
        monto = pos.acciones * precio
        com = _comision(pos.acciones, precio, costos)
        ordenes.append(Orden(pos.ticker, VENTA, pos.acciones, precio, monto,
                             com, -(monto - com),
                             f"señal {s.magnitud_pp:+.2f} pp bajo el umbral "
                             f"de salida"))
        caja += monto - com

    # --- compras ---
    candidatas = sorted(
        [s for s in senales], key=lambda s: (-s.magnitud_pp, s.ticker))
    tope_posicion = presupuesto_usd * j["tope_posicion_pct"] / 100.0
    disponibles = [
        presupuesto_usd - _valor_invertido(cartera, precios_ref),
        j["presupuesto_diario_usd"] - estado.gastado_hoy_usd,
        j["presupuesto_semanal_usd"] - estado.gastado_semana_usd,
        j["presupuesto_mensual_usd"] - estado.gastado_mes_usd,
        caja,
    ]
    sobrante = max(0.0, min(disponibles))

    for s in candidatas:
        if s.magnitud_pp < j["umbral_senal_pp"]:
            descartes.append((s.ticker, f"señal {s.magnitud_pp:+.2f} pp bajo "
                                        f"el umbral {j['umbral_senal_pp']:+.2f} pp"))
            continue
        if j["exigir_intervalo_que_no_cruce_cero"] and s.cruza_cero:
            descartes.append((s.ticker, f"su intervalo [{s.banda_baja_pp:+.2f}, "
                                        f"{s.banda_alta_pp:+.2f}] contiene el cero"))
            continue
        precio = precios_ref.get(s.ticker)
        if precio is None or precio <= 0:
            descartes.append((s.ticker, "sin precio de referencia"))
            continue
        ya = cartera.por_ticker(s.ticker)
        expuesto = (ya.acciones * precio) if ya else 0.0
        margen = min(tope_posicion - expuesto, sobrante)
        n = _cuantas_acciones(margen, precio, costos)
        if n <= 0:
            descartes.append((s.ticker, _por_que_ninguna(
                margen, precio, tope_posicion, expuesto, sobrante)))
            continue
        monto = n * precio
        com = _comision(n, precio, costos)
        ordenes.append(Orden(s.ticker, COMPRA, n, precio, monto, com,
                             monto + com,
                             f"señal {s.magnitud_pp:+.2f} pp sobre el umbral "
                             f"{j['umbral_senal_pp']:+.2f} pp"))
        sobrante -= monto + com

    return Decision(dia=dia, ordenes=tuple(ordenes),
                    descartes=tuple(descartes), riel_apagado=False)


def _valor_invertido(cartera: Cartera, precios_ref: dict) -> float:
    return sum(p.acciones * precios_ref.get(p.ticker, 0.0)
               for p in cartera.posiciones)


def _cuantas_acciones(margen: float, precio: float, costos: dict) -> int:
    if margen <= 0 or precio <= 0:
        return 0
    n = int(margen // precio)
    while n > 0 and n * precio + _comision(n, precio, costos) > margen:
        n -= 1
    return n


def _por_que_ninguna(margen, precio, tope_posicion, expuesto, sobrante) -> str:
    if margen <= 0:
        if tope_posicion - expuesto <= 0:
            return (f"la posición ya está en el tope "
                    f"({expuesto:.2f} de {tope_posicion:.2f} USD)")
        return f"no queda presupuesto disponible ({sobrante:.2f} USD)"
    return (f"una acción cuesta {precio:.2f} USD y el margen disponible es "
            f"{margen:.2f} USD; el riel no compra fracciones")
