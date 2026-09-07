# ============================================================
# dinero/contabilidad.py — la CUENTA EN PAPEL del riel de dinero.
#
# ORDEN OBLIGATORIO, y es del encargo: primero la línea base, después la
# estrategia. Si se construye la estrategia antes de tener la vara, la vara
# se elige mirando el resultado. Por eso `linea_base` está escrita arriba y
# no depende de nada de la estrategia.
#
# TODO ES SIMULADO. Se ejecuta contra `dinero/datos/cierres_congelados.csv`
# y NO se descarga nada: `precios.cargar_congelado` revienta si el archivo
# no está, en vez de salir a buscarlo.
#
# EL SUPUESTO DE COSTO ES EL RESULTADO, no un detalle: para una estrategia
# que rota seguido, mover el deslizamiento de 0 a 10 pb por lado cambia el
# signo de la respuesta. Por eso el reporte BARRE el costo en vez de elegir
# uno, y por eso la comisión mínima de 1 USD —que a 125 dólares por orden es
# 0.8 % por lado— se ve en cada línea.
#
# LO QUE ESTA CUENTA NO ES: no es evidencia de habilidad. En esta corrida la
# estrategia se alimenta de una señal SIN INFORMACIÓN (sorteada de la
# distribución histórica de retornos, con semilla declarada), justamente
# para que lo que se mida sea el COSTO DE FRICCIÓN de cada juego de
# parámetros y no una ventaja inexistente. Lo que sobre por encima de esto,
# el día que haya señal de verdad, es lo único que podría llamarse
# habilidad.
# ============================================================
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

from backtest import inferencia
from dinero import decision as D
from dinero import precios

SEMILLA_SENAL_SIN_INFORMACION = 20260906
BLOQUE_BOOTSTRAP_SEMANAS = 4
REPLICAS_BOOTSTRAP = 2000
ALPHA = 0.05


# ------------------------------------------------------------
# El libro
# ------------------------------------------------------------
@dataclass
class Movimiento:
    fecha: date
    ticker: str
    lado: str
    acciones: int
    precio_ejecucion: float
    comision_usd: float
    efectivo_despues: float


@dataclass
class Libro:
    efectivo_usd: float = 0.0
    aportado_usd: float = 0.0
    posiciones: dict = field(default_factory=dict)     # ticker -> (acciones, abierta_el)
    movimientos: list = field(default_factory=list)
    comisiones_usd: float = 0.0
    deslizamiento_usd: float = 0.0

    def aportar(self, monto: float) -> None:
        self.efectivo_usd += monto
        self.aportado_usd += monto

    def comprar(self, dia: date, ticker: str, n: int, cierre: float,
                costos: dict, desliz_pb: float) -> bool:
        if n <= 0:
            return False
        precio = cierre * (1.0 + desliz_pb / 10000.0)
        com = _comision(n, precio, costos)
        costo = n * precio + com
        if costo > self.efectivo_usd + 1e-9:
            return False
        self.efectivo_usd -= costo
        self.comisiones_usd += com
        self.deslizamiento_usd += n * (precio - cierre)
        acc, abierta = self.posiciones.get(ticker, (0, dia))
        self.posiciones[ticker] = (acc + n, abierta if acc else dia)
        self.movimientos.append(Movimiento(dia, ticker, D.COMPRA, n, precio,
                                           com, self.efectivo_usd))
        return True

    def vender(self, dia: date, ticker: str, n: int, cierre: float,
               costos: dict, desliz_pb: float) -> bool:
        acc, abierta = self.posiciones.get(ticker, (0, dia))
        if n <= 0 or n > acc:
            return False
        precio = cierre * (1.0 - desliz_pb / 10000.0)
        com = _comision(n, precio, costos)
        self.efectivo_usd += n * precio - com
        self.comisiones_usd += com
        self.deslizamiento_usd += n * (cierre - precio)
        if acc - n == 0:
            del self.posiciones[ticker]
        else:
            self.posiciones[ticker] = (acc - n, abierta)
        self.movimientos.append(Movimiento(dia, ticker, D.VENTA, n, precio,
                                           com, self.efectivo_usd))
        return True

    def valor(self, fila_cierres) -> float:
        v = self.efectivo_usd
        for t, (acc, _) in self.posiciones.items():
            p = fila_cierres.get(t)
            if p is not None and not pd.isna(p):
                v += acc * float(p)
        return v


def _comision(n: int, precio: float, costos: dict) -> float:
    if n <= 0:
        return 0.0
    monto = n * precio
    bruta = max(costos["comision_minima_usd"],
                costos["comision_por_accion_usd"] * n)
    return min(bruta, costos["comision_tope_pct_del_monto"] / 100.0 * monto)


# ------------------------------------------------------------
# Calendario de aportes: acotado por el PRESUPUESTO, no por el horizonte
# ------------------------------------------------------------
def calendario_aportes(dias, aporte_semanal: float, techo_usd: float):
    """{fecha: monto}. Aporta `aporte_semanal` el primer día hábil de cada
    semana HASTA AGOTAR el techo del presupuesto, y después nada.

    Esto es lo que separa esta cuenta de un backtest de fantasía: el
    encargo pide 'un monto fijo cada semana', pero el presupuesto declarado
    son 100 a 500 dólares en total, no por semana. Aportar semanalmente
    durante tres años serían 78.000 dólares que no existen."""
    calendario = {}
    restante = techo_usd
    vista = set()
    for d in dias:
        semana = (d.isocalendar().year, d.isocalendar().week)
        if semana in vista or restante <= 0:
            continue
        vista.add(semana)
        monto = min(aporte_semanal, restante)
        calendario[d] = monto
        restante -= monto
    return calendario


# ------------------------------------------------------------
# 4a. LA LÍNEA BASE ABURRIDA — se escribe y se mide PRIMERO
# ------------------------------------------------------------
def linea_base(cierres: pd.DataFrame, ticker: str, aportes: dict,
               costos: dict, desliz_pb: float) -> Libro:
    """Comprar un ETF del sector con un monto fijo cada semana, sin decidir
    nada. Si el aporte no alcanza para una acción entera, ACUMULA: es lo que
    haría una persona con 100 dólares por semana y un ETF de 567, y fingir
    fracciones sería inventarse un corredor que no existe."""
    libro = Libro()
    for dia, fila in cierres.iterrows():
        d = dia.date()
        if d in aportes:
            libro.aportar(aportes[d])
        cierre = fila.get(ticker)
        if cierre is None or pd.isna(cierre):
            continue
        precio = float(cierre) * (1.0 + desliz_pb / 10000.0)
        n = int(libro.efectivo_usd // precio)
        while n > 0 and n * precio + _comision(n, precio, costos) > libro.efectivo_usd:
            n -= 1
        if n > 0:
            libro.comprar(d, ticker, n, float(cierre), costos, desliz_pb)
    return libro


# ------------------------------------------------------------
# Señal SIN INFORMACIÓN — la sonda que mide fricción
# ------------------------------------------------------------
def senales_sin_informacion(cierres: pd.DataFrame, tickers, horizonte: int,
                            semilla: int):
    """Devuelve fecha -> [Senal]. La magnitud se sortea de la distribución de
    retornos a `horizonte` días hábiles del propio instrumento.

    FUGA F2, DEMOSTRADA Y NO CORREGIDA (7-sep-2026,
    `GEMELO/resultados/dictamen_10/auditor_lookahead.md`): esa distribución
    NO es histórica, que es lo que esta docstring afirmaba. Sale de
    `shift(-horizonte)` sobre el marco que se le pasa, y `cuenta_papel`
    le pasa la ventana simulada entera, así que la escala de la señal está
    calibrada con el futuro de la propia ventana que después se mide.
    Medido: 755 de 756 señales cambian al truncar; P(sorteo > umbral) pasa
    de 0,310 a 0,447 en INTC. La corrección es sortear de datos anteriores
    al inicio de la ventana, o de una paramétrica declarada en reglas.json.
    `tests/test_dinero.py` la tiene clavada con un xfail estricto.

    La señal sigue sin tener información sobre la DIRECCIÓN de lo que pasa
    después; lo contaminado es la ESCALA, y la escala es la que decide
    cuántas órdenes se disparan.

    Es una sonda, no un modelo. Sirve para responder una sola pregunta: qué
    le cuesta a cada juego de parámetros existir."""
    rng = np.random.default_rng(semilla)
    dist, sigma = {}, {}
    for t in tickers:
        s = cierres[t].dropna()
        r = ((s.shift(-horizonte) / s - 1.0).dropna() * 100.0).to_numpy()
        dist[t] = r if len(r) else np.array([0.0])
        sigma[t] = float(np.std(dist[t], ddof=1)) if len(dist[t]) > 1 else 1.0
    por_dia = {}
    for dia in cierres.index:
        d = dia.date()
        lote = []
        for t in tickers:
            m = float(rng.choice(dist[t]))
            ancho = 1.2816 * sigma[t]
            lote.append(D.Senal(t, m, m - ancho, m + ancho))
        por_dia[d] = lote
    return por_dia


# ------------------------------------------------------------
# 4b. EL LIBRO CONTABLE SIMULADO
# ------------------------------------------------------------
def correr_estrategia(cierres: pd.DataFrame, senales_por_dia: dict,
                      cfg: dict, nombre_juego: str, aportes: dict,
                      desliz_pb: float, techo_usd: float) -> Libro:
    costos = cfg["costos"]
    j = D.juego(cfg, nombre_juego)
    libro = Libro()
    gasto_dia = gasto_semana = gasto_mes = 0.0
    semana_actual = mes_actual = None
    apagado, motivo = False, ""
    for dia, fila in cierres.iterrows():
        d = dia.date()
        iso = d.isocalendar()
        if semana_actual != (iso.year, iso.week):
            semana_actual, gasto_semana = (iso.year, iso.week), 0.0
        if mes_actual != (d.year, d.month):
            mes_actual, gasto_mes = (d.year, d.month), 0.0
        gasto_dia = 0.0
        if d in aportes:
            libro.aportar(aportes[d])

        valor = libro.valor(fila)
        perdida = max(0.0, libro.aportado_usd - valor)
        estado = D.EstadoRiel(gasto_dia, gasto_semana, gasto_mes, perdida,
                              apagado, motivo)
        precios_ref = {t: float(fila[t]) for t in cierres.columns
                       if not pd.isna(fila.get(t))}
        cartera = D.Cartera(
            efectivo_usd=libro.efectivo_usd,
            posiciones=tuple(D.Posicion(t, acc, 0.0, abierta)
                             for t, (acc, abierta) in libro.posiciones.items()))
        dec = D.proponer_ordenes(senales_por_dia.get(d, []), cartera,
                                 techo_usd, cfg, d, precios_ref, estado,
                                 nombre_juego)
        if dec.riel_apagado and not apagado:
            apagado = True
            motivo = dec.descartes[0][1] if dec.descartes else "sin motivo"
        for o in dec.ordenes:
            if o.lado == D.VENTA:
                libro.vender(d, o.ticker, o.acciones, o.precio_ref_usd,
                             costos, desliz_pb)
            else:
                if libro.comprar(d, o.ticker, o.acciones, o.precio_ref_usd,
                                 costos, desliz_pb):
                    gasto_dia += o.desembolso_usd
                    gasto_semana += o.desembolso_usd
                    gasto_mes += o.desembolso_usd
    return libro


# ------------------------------------------------------------
# Valuación semanal y comparación con intervalo
# ------------------------------------------------------------
def valorizar(cierres: pd.DataFrame, movimientos, aportes: dict,
              costos: dict) -> pd.Series:
    """Valor de la cuenta al cierre de cada día, a partir de los movimientos
    ya ejecutados. Función pura sobre datos ya producidos."""
    por_dia = {}
    for m in movimientos:
        por_dia.setdefault(m.fecha, []).append(m)
    efectivo, pos = 0.0, {}
    valores = []
    for dia, fila in cierres.iterrows():
        d = dia.date()
        efectivo += aportes.get(d, 0.0)
        for m in por_dia.get(d, ()):
            if m.lado == D.COMPRA:
                efectivo -= m.acciones * m.precio_ejecucion + m.comision_usd
                pos[m.ticker] = pos.get(m.ticker, 0) + m.acciones
            else:
                efectivo += m.acciones * m.precio_ejecucion - m.comision_usd
                pos[m.ticker] = pos.get(m.ticker, 0) - m.acciones
                if pos[m.ticker] == 0:
                    del pos[m.ticker]
        v = efectivo + sum(a * float(fila[t]) for t, a in pos.items()
                           if not pd.isna(fila.get(t)))
        valores.append(v)
    return pd.Series(valores, index=cierres.index)


def retornos_semanales(valor: pd.Series) -> pd.Series:
    semanal = valor.resample("W-FRI").last().dropna()
    return (semanal.pct_change() * 100.0).dropna()


def comparar(valor_estrategia: pd.Series, valor_base: pd.Series,
             semilla: int, bloque: int = BLOQUE_BOOTSTRAP_SEMANAS,
             replicas: int = REPLICAS_BOOTSTRAP, alpha: float = ALPHA) -> dict:
    """Diferencia de retorno semanal, con intervalo por bootstrap circular
    de bloques sobre SEMANAS. La unidad es la semana porque los retornos
    diarios de dos carteras que comparten instrumentos están correlacionados
    y contarlos como independientes angostaría el intervalo sin fundamento.

    `semilla` es obligatoria, como en el resto del proyecto."""
    re_ = retornos_semanales(valor_estrategia)
    rb = retornos_semanales(valor_base)
    comun = re_.index.intersection(rb.index)
    dif = (re_.loc[comun] - rb.loc[comun]).dropna()
    ic = inferencia.bootstrap_media(dif.to_numpy(), semilla=semilla,
                                    n_draws=replicas, bloque=bloque,
                                    alpha=alpha)
    return {
        "semanas": int(len(dif)),
        "dif_media_pp": float(dif.mean()) if len(dif) else float("nan"),
        "ic_lo": ic["lo"], "ic_hi": ic["hi"],
        "cruza_cero": bool(np.isnan(ic["lo"]) or ic["lo"] <= 0.0 <= ic["hi"]),
        "bloque_semanas": bloque, "replicas": replicas, "alpha": alpha,
        "semilla": semilla,
    }
