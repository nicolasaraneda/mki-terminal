# ============================================================
# corredor/ibkr.py — adaptador mínimo a la cuenta de PRÁCTICA de Interactive
# Brokers por la TWS API (IB Gateway / TWS), decisión D-C del acta §84.4.2.
# Corrida 12, bloque 4. Estado: construido contra una RÉPLICA escrita desde la
# documentación (corredor/replica/), NO contra una sesión real: E1 queda
# **NO EJECUTADO** (sin credenciales ni gateway en la máquina la noche del
# 8/9-sep-2026; y de noche NYSE está cerrada, así que «enviar y leer la
# ejecución en el mismo ciclo» no era ejecutable aunque hubiera cuenta).
#
# GUARDIA DE PAPEL, en código y no como promesa: este adaptador se NIEGA a
# conectarse a un puerto que no sea de práctica y a operar sobre una cuenta
# cuyo identificador no sea de práctica. Los dos chequeos son independientes
# y cualquiera de los dos basta para negarse. Hay test con una cuenta
# simulada que finge ser real (tests/test_corredor.py).
#
# FUENTES OFICIALES consultadas el 8/9-sep-2026 (URL y qué dijo cada una en
# GEMELO/resultados/bitacora_12.md, bloque 4). Lo que la máquina pudo leer:
#   · puertos por defecto de TWS: 7496 real, 7497 práctica
#     (interactivebrokers.github.io/tws-api/initial_setup.html, página oficial
#     marcada como DEPRECADA que remite a IBKR Campus; el Campus devolvió 403
#     a esta máquina). Los puertos 4001/4002 del IB Gateway salieron de un
#     resumen de búsqueda sobre páginas de interactivebrokers.com, no de una
#     página leída entera: quedan DECLARADOS COMO NO VERIFICADOS DIRECTAMENTE.
#   · el cliente Python oficial se distribuye desde interactivebrokers.github.io
#     bajo la «TWS API Non-Commercial License» con aceptación previa; la
#     versión vigente (10.50, 26-ago-2026) es la única que incluye Python. El
#     `ibapi` de PyPI es 9.81.1.post1 (dic-2020), subido por IBG LLC. Por eso
#     este módulo importa `ibapi` de forma PEREZOSA y `requirements.txt` NO lo
#     instala: instalarlo desde el zip oficial es acto de Nicolás (licencia).
#   · las órdenes por API dirigidas pierden Tiered; SmartRouting lo conserva
#     (criterio_corredor_prerregistro.md §4, verificado el 7-sep). Acá toda
#     orden lleva exchange="SMART", sin excepción.
#   · ejecuciones: `reqExecutions` + `execDetails` devuelven por defecto sólo
#     las de la sesión desde medianoche (executions_commissions.html).
#   · el prefijo «DU» de las cuentas de práctica aparece en salidas de
#     ejemplo de IBKR Campus (resumen de búsqueda); no se pudo leer la página
#     entera: NO VERIFICADO DIRECTAMENTE. La guardia lo exige igual, porque
#     negarse de más es barato y aceptar de más es el error caro.
# ============================================================
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_REPLICA = os.path.join(DIRECTORIO, "replica", "respuestas_practica.json")

# Puertos por defecto. Sólo los de PRÁCTICA están permitidos.
PUERTOS_PRACTICA = {7497: "TWS · cuenta de práctica (fuente oficial deprecada, leída)",
                    4002: "IB Gateway · cuenta de práctica (resumen de búsqueda, NO leído entero)"}
PUERTOS_REALES = {7496: "TWS · cuenta real", 4001: "IB Gateway · cuenta real"}
PREFIJO_CUENTA_PRACTICA = "DU"
RUTEO = "SMART"            # SmartRouting siempre: una orden dirigida por API pierde Tiered
MONEDA = "USD"
TIPO_MERCADO_DATOS_RETRASADOS = 3   # reqMarketDataType(3) = delayed (declarado, no verificado en vivo)
RETRASO_DECLARADO_MIN = 15          # lo que el corredor declara para datos retrasados


class ErrorCuentaNoPractica(RuntimeError):
    """Se intentó tocar algo que no es de práctica. No hay bypass."""


@dataclass(frozen=True)
class Orden:
    ticker: str
    cantidad: int
    lado: str                 # BUY | SELL
    tipo: str = "LMT"         # LMT | MKT
    precio_limite: float | None = None
    exchange: str = RUTEO
    moneda: str = MONEDA
    sec_type: str = "STK"


@dataclass
class Ejecucion:
    exec_id: str
    order_id: int
    ticker: str
    lado: str
    cantidad: float
    precio: float
    hora: str                 # marca de tiempo del CORREDOR, no de esta máquina
    cuenta: str
    exchange: str
    perm_id: int | None = None
    comision_usd: float | None = None
    leido_en_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class MarcaRetraso:
    """Todo dato leído del corredor viaja con la marca de retraso que el
    corredor declara (bloque 4.6): la pantalla la muestra."""
    tipo_dato: int
    retraso_min: int | None
    descripcion: str


# ------------------------------------------------------------
# Transportes: réplica (fixture) y ibapi (perezoso, NO EJECUTADO)
# ------------------------------------------------------------
class TransporteReplica:
    """Respuestas escritas desde la documentación, NO grabadas de una sesión
    real. Sirve para testear el adaptador y la guardia; NO es evidencia de
    C1 ni de C2 (pre-mortem 6 de la corrida 12)."""
    ORIGEN = "réplica escrita desde documentación, no grabada: NO es evidencia de C1/C2"

    def __init__(self, ruta: str = RUTA_REPLICA, cuentas: list | None = None):
        with open(ruta, encoding="utf-8") as f:
            self.datos = json.load(f)
        if cuentas is not None:               # para el test de la cuenta que finge ser real
            self.datos["managedAccounts"] = cuentas
        self.conectado = False
        self.ordenes_enviadas = []
        self._next_id = int(self.datos.get("nextValidId", 1))

    def conectar(self, host, puerto, client_id):
        self.conectado = True
        return list(self.datos["managedAccounts"])

    def desconectar(self):
        self.conectado = False

    def next_valid_id(self) -> int:
        i = self._next_id
        self._next_id += 1
        return i

    def place_order(self, order_id: int, orden: Orden) -> None:
        self.ordenes_enviadas.append((order_id, orden))

    def order_status(self, order_id: int) -> dict:
        plantilla = dict(self.datos["orderStatus"])
        plantilla["orderId"] = order_id
        return plantilla

    def executions(self) -> list:
        return [dict(e) for e in self.datos["execDetails"]]

    def commission_reports(self) -> dict:
        return {c["execId"]: c for c in self.datos["commissionReport"]}

    def positions(self) -> list:
        return [dict(p) for p in self.datos["positions"]]

    def account_summary(self) -> dict:
        return dict(self.datos["accountSummary"])

    def market_data_type(self) -> int:
        return int(self.datos.get("marketDataType", TIPO_MERCADO_DATOS_RETRASADOS))


class TransporteIbapi:
    """Transporte real por `ibapi` (TWS API). Importa la librería de forma
    PEREZOSA: no está en requirements.txt (licencia click-through de IB;
    instalarla es acto de Nicolás). NO EJECUTADO en la corrida 12: sin
    gateway ni credenciales no se pudo probar ni una conexión de lectura. Lo
    que sigue es la traducción de la documentación oficial a llamadas, y hay
    que tratarlo como tal hasta que E1 corra de verdad."""
    ORIGEN = "ibapi (TWS API oficial); NO EJECUTADO en la corrida 12"

    def __init__(self, espera_s: float = 10.0):
        try:
            from ibapi.client import EClient      # type: ignore
            from ibapi.wrapper import EWrapper    # type: ignore
        except ImportError as e:                  # pragma: no cover — depende del entorno
            raise ImportError(
                "ibapi no está instalado. Se instala desde el zip oficial de "
                "interactivebrokers.github.io (API 10.50, licencia no comercial de IB); "
                "es acto de Nicolás, no de un agente.") from e
        self._EClient, self._EWrapper, self.espera_s = EClient, EWrapper, espera_s
        self._app = None

    # Los métodos de abajo se completan cuando exista un gateway contra el que
    # probarlos; dejar código «que debería funcionar» sin haberlo ejecutado es
    # exactamente lo que el pre-mortem 6 prohíbe presentar como cableado.
    def conectar(self, host, puerto, client_id):      # pragma: no cover
        raise NotImplementedError("E1 no ejecutado: el transporte ibapi se completa con gateway a la vista")


# ------------------------------------------------------------
# El adaptador
# ------------------------------------------------------------
class ClienteIBKR:
    """Interfaz mínima (bloque 4.2): conectar, enviar orden con SmartRouting,
    leer estado, leer ejecuciones, leer posiciones y efectivo, desconectar.
    Y antes de todo eso, negarse si algo no es de práctica."""

    def __init__(self, host: str = "127.0.0.1", puerto: int = 4002, client_id: int = 12,
                 transporte=None):
        if puerto not in PUERTOS_PRACTICA:
            que = PUERTOS_REALES.get(puerto, "desconocido")
            raise ErrorCuentaNoPractica(
                f"puerto {puerto} ({que}) no es de práctica: sólo {sorted(PUERTOS_PRACTICA)} están permitidos")
        self.host, self.puerto, self.client_id = host, puerto, client_id
        self.transporte = transporte or TransporteReplica()
        self.cuenta: str | None = None
        self.bitacora: list = []      # (utc, evento, detalle) — sin credenciales, nunca

    def _anotar(self, evento: str, detalle: str = "") -> None:
        self.bitacora.append((datetime.now(timezone.utc).isoformat(), evento, detalle))

    @staticmethod
    def es_cuenta_practica(cuenta: str) -> bool:
        return isinstance(cuenta, str) and cuenta.upper().startswith(PREFIJO_CUENTA_PRACTICA)

    def conectar(self) -> str:
        cuentas = self.transporte.conectar(self.host, self.puerto, self.client_id)
        malas = [c for c in cuentas if not self.es_cuenta_practica(c)]
        if malas or not cuentas:
            self.transporte.desconectar()
            self._anotar("rechazo", f"{len(malas)} cuenta(s) no de práctica")
            raise ErrorCuentaNoPractica(
                f"la sesión expone cuentas que no son de práctica ({len(malas)}): desconectado sin operar")
        self.cuenta = cuentas[0]
        self._anotar("conectado", f"puerto {self.puerto} · cuenta {self.cuenta[:2]}…")
        return self.cuenta

    def _exigir_conexion_practica(self) -> None:
        if self.cuenta is None or not self.es_cuenta_practica(self.cuenta):
            raise ErrorCuentaNoPractica("sin conexión a una cuenta de práctica: no se opera")

    def enviar_orden(self, ticker: str, cantidad: int, lado: str, tipo: str = "LMT",
                     precio_limite: float | None = None) -> int:
        self._exigir_conexion_practica()
        if lado not in ("BUY", "SELL") or cantidad <= 0:
            raise ValueError("orden inválida")
        if tipo == "LMT" and precio_limite is None:
            raise ValueError("una orden límite exige precio")
        orden = Orden(ticker=ticker, cantidad=int(cantidad), lado=lado, tipo=tipo,
                      precio_limite=precio_limite)
        assert orden.exchange == RUTEO   # SmartRouting, sin excepción
        oid = self.transporte.next_valid_id()
        self.transporte.place_order(oid, orden)
        self._anotar("orden", f"{lado} {cantidad} {ticker} {tipo} @{precio_limite} id={oid}")
        return oid

    def estado_orden(self, order_id: int) -> dict:
        self._exigir_conexion_practica()
        return self.transporte.order_status(order_id)

    def ejecuciones(self) -> list:
        self._exigir_conexion_practica()
        comisiones = self.transporte.commission_reports()
        out = []
        for e in self.transporte.executions():
            if not self.es_cuenta_practica(e.get("acctNumber", "")):
                raise ErrorCuentaNoPractica("una ejecución no es de una cuenta de práctica")
            out.append(Ejecucion(
                exec_id=e["execId"], order_id=int(e["orderId"]), ticker=e["symbol"], lado=e["side"],
                cantidad=float(e["shares"]), precio=float(e["price"]), hora=e["time"],
                cuenta=e["acctNumber"], exchange=e.get("exchange", ""), perm_id=e.get("permId"),
                comision_usd=(comisiones.get(e["execId"]) or {}).get("commission")))
        return out

    def posiciones_y_efectivo(self) -> dict:
        self._exigir_conexion_practica()
        return {"posiciones": self.transporte.positions(),
                "efectivo": self.transporte.account_summary(),
                "marca_retraso": self.marca_retraso(),
                "cuenta_es_practica": True, "origen": getattr(self.transporte, "ORIGEN", "?")}

    def marca_retraso(self) -> MarcaRetraso:
        t = self.transporte.market_data_type()
        return MarcaRetraso(tipo_dato=t,
                            retraso_min=RETRASO_DECLARADO_MIN if t in (3, 4) else 0,
                            descripcion={1: "tiempo real", 2: "congelado", 3: "retrasado", 4: "retrasado-congelado"}.get(t, "desconocido"))

    def desconectar(self) -> None:
        self.transporte.desconectar()
        self._anotar("desconectado")
        self.cuenta = None


# ------------------------------------------------------------
# Conciliación (bloque 4.4): lo leído por API contra el reporte oficial
# ------------------------------------------------------------
CAMPOS_CONCILIACION = ("exec_id", "ticker", "lado", "cantidad", "precio")


def conciliar(ejecuciones_api: list, reporte_oficial: list) -> dict:
    """Compara las ejecuciones leídas por API con el reporte que el corredor
    genera (el que descarga el portal, no el que devuelve la misma llamada).
    Si difieren, C2 NO está cumplida aunque la llamada responda. Devuelve el
    detalle; no decide nada por su cuenta."""
    por_id = {e.exec_id if isinstance(e, Ejecucion) else e["exec_id"]: e for e in ejecuciones_api}
    ofi = {r["exec_id"]: r for r in reporte_oficial}
    faltan_en_api = sorted(set(ofi) - set(por_id))
    faltan_en_oficial = sorted(set(por_id) - set(ofi))
    difieren = []
    for k in sorted(set(ofi) & set(por_id)):
        a = por_id[k]
        a = a.__dict__ if isinstance(a, Ejecucion) else a
        for campo in CAMPOS_CONCILIACION:
            va, vo = a.get(campo), ofi[k].get(campo)
            if isinstance(va, float) or isinstance(vo, float):
                igual = abs(float(va) - float(vo)) < 1e-9
            else:
                igual = va == vo
            if not igual:
                difieren.append((k, campo, va, vo))
    return {"coinciden": not (faltan_en_api or faltan_en_oficial or difieren),
            "faltan_en_api": faltan_en_api, "faltan_en_oficial": faltan_en_oficial,
            "difieren": difieren, "n_api": len(por_id), "n_oficial": len(ofi),
            "C2": ("cumplida" if not (faltan_en_api or faltan_en_oficial or difieren) else "NO cumplida"),
            "nota": ("una conciliación contra la propia réplica NO es evidencia: C2 sólo se juzga "
                     "contra el reporte oficial de una cuenta de práctica real")}
