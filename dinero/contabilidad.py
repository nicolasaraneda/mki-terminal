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
#
# ============================================================
# RECONSTRUCCIÓN — corrida 11 (8-sep-2026), acta §82.4 opción A
# ============================================================
# El dictamen de cierre de la corrida 10 (`dictamen_10/auditor_lookahead.md`)
# demostró cuatro fugas temporales ejecutando código, y la página quedó
# RETIRADA. El orden de la reconstrucción lo fijó el auditor: el test de
# truncación primero (tests/test_dinero.py, sección 6, escrito el 7-sep),
# las correcciones después, y republicar al final. Lo que cambió acá:
#
#   E3  `senales_sin_informacion` sortea de la distribución de retornos a
#       `horizonte` días de datos ANTERIORES a `desde`, nunca de la ventana
#       que después se mide. Antes salía de `shift(-horizonte)` sobre la
#       ventana simulada entera (F2: 755 de 756 señales cambiaban al
#       truncar).
#   E4  RETARDO DE IMPLEMENTACIÓN = 1 en las DOS patas: se decide con el
#       cierre de d y se ejecuta contra el cierre de d+1, tanto en la
#       estrategia como en la línea base. Antes se decidía y ejecutaba
#       contra el mismo cierre (F4). Cada `Movimiento` lleva ahora la fecha
#       en que se decidió y las acciones decididas, aparte de las
#       ejecutadas: si la caja no alcanza al precio de d+1, la orden se
#       reduce o se cae, y eso queda registrado en vez de disimulado.
#   E6  `ErrorLookAhead` cableado: `cuenta_papel.verificar_invariancia`
#       reconstruye la cuenta con la fuente truncada y revienta si un solo
#       movimiento cambia. `cuenta_papel.main` lo corre antes de escribir.
#
# La membresía acotada por fecha (E1) y la sigma del interruptor sin futuro
# (E5) viven en `cuenta_papel.py` y `derivacion.py` respectivamente.
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
# Se decide con el cierre de d y se entra al cierre de d + RETARDO. Es el
# mismo valor que usa `senal_larga.RETARDO_IMPLEMENTACION`; un test exige
# que sigan iguales, porque dos retardos distintos en el mismo riel es
# exactamente lo que el auditor encontró (F4).
RETARDO_IMPLEMENTACION = 1
# Mínimo de retornos históricos para sortear una señal: menos que esto es
# sortear de casi nada y se prefiere reventar a fingir una distribución.
MINIMO_HISTORIA_SENAL = 60


# ------------------------------------------------------------
# El libro
# ------------------------------------------------------------
@dataclass
class Movimiento:
    fecha: date                  # cuándo se EJECUTÓ (cierre de d + retardo)
    ticker: str
    lado: str
    acciones: int                # las que efectivamente se ejecutaron
    precio_ejecucion: float
    comision_usd: float
    efectivo_despues: float
    decidida_el: date | None = None      # cuándo se DECIDIÓ (cierre de d)
    acciones_decididas: int | None = None  # las que se decidieron en d


@dataclass
class Libro:
    efectivo_usd: float = 0.0
    aportado_usd: float = 0.0
    posiciones: dict = field(default_factory=dict)     # ticker -> (acciones, abierta_el)
    movimientos: list = field(default_factory=list)
    # (decidida_el, ticker, lado, acciones): TODA decisión, se haya ejecutado
    # o no. El gate de invariancia compara esto además de los movimientos,
    # porque una decisión tomada en D se ejecuta en D+1 y si D+1 es el
    # borde del corte nunca llega a ser movimiento.
    decisiones: list = field(default_factory=list)
    comisiones_usd: float = 0.0
    deslizamiento_usd: float = 0.0

    def aportar(self, monto: float) -> None:
        self.efectivo_usd += monto
        self.aportado_usd += monto

    def comprar(self, dia: date, ticker: str, n: int, cierre: float,
                costos: dict, desliz_pb: float,
                decidida_el: date | None = None) -> int:
        """Ejecuta una compra decidida en `decidida_el` contra el cierre de
        `dia`. Si al precio de ejecución la caja no alcanza para las `n`
        decididas, ejecuta las que alcanzan (puede ser cero) y lo deja
        registrado en `acciones` contra `acciones_decididas`. Devuelve las
        acciones ejecutadas."""
        if n <= 0:
            return 0
        precio = cierre * (1.0 + desliz_pb / 10000.0)
        n_dec = n
        while n > 0 and n * precio + _comision(n, precio, costos) > self.efectivo_usd + 1e-9:
            n -= 1
        if n <= 0:
            return 0
        com = _comision(n, precio, costos)
        self.efectivo_usd -= n * precio + com
        self.comisiones_usd += com
        self.deslizamiento_usd += n * (precio - cierre)
        acc, abierta = self.posiciones.get(ticker, (0, dia))
        self.posiciones[ticker] = (acc + n, abierta if acc else dia)
        self.movimientos.append(Movimiento(dia, ticker, D.COMPRA, n, precio,
                                           com, self.efectivo_usd,
                                           decidida_el or dia, n_dec))
        return n

    def vender(self, dia: date, ticker: str, n: int, cierre: float,
               costos: dict, desliz_pb: float,
               decidida_el: date | None = None) -> int:
        acc, abierta = self.posiciones.get(ticker, (0, dia))
        if n <= 0 or acc <= 0:
            return 0
        n_dec = n
        n = min(n, acc)
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
                                           com, self.efectivo_usd,
                                           decidida_el or dia, n_dec))
        return n

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
               costos: dict, desliz_pb: float,
               retardo: int = RETARDO_IMPLEMENTACION) -> Libro:
    """Comprar un ETF del sector con un monto fijo cada semana, sin decidir
    nada. Si el aporte no alcanza para una acción entera, ACUMULA: es lo que
    haría una persona con 100 dólares por semana y un ETF de 567, y fingir
    fracciones sería inventarse un corredor que no existe.

    Con retardo (E4): el día d se decide cuántas acciones enteras entran con
    la caja y el cierre de d; la orden se ejecuta contra el cierre de
    d + retardo. Es la misma regla que la estrategia, para que la
    comparación no tenga un retardo de un lado y cero del otro."""
    libro = Libro()
    pendientes = []   # (dia_ejecucion_idx, decidida_el, n)
    fechas = list(cierres.index)
    for i, dia in enumerate(fechas):
        fila = cierres.iloc[i]
        d = dia.date()
        # 1. ejecutar lo decidido `retardo` sesiones atrás, contra el cierre de hoy
        cierre = fila.get(ticker)
        hay_precio = cierre is not None and not pd.isna(cierre)
        for (j, decidida, n) in [p for p in pendientes if p[0] == i]:
            if hay_precio:
                libro.comprar(d, ticker, n, float(cierre), costos, desliz_pb,
                              decidida_el=decidida)
        pendientes = [p for p in pendientes if p[0] > i]
        # 2. aportar
        if d in aportes:
            libro.aportar(aportes[d])
        # 3. decidir con el cierre de hoy, para ejecutar en d + retardo
        if not hay_precio:
            continue
        comprometido = sum(n * float(cierre) * (1.0 + desliz_pb / 10000.0)
                           for _, _, n in pendientes)
        caja = libro.efectivo_usd - comprometido
        precio = float(cierre) * (1.0 + desliz_pb / 10000.0)
        n = int(caja // precio) if caja > 0 else 0
        while n > 0 and n * precio + _comision(n, precio, costos) > caja:
            n -= 1
        if n > 0:
            libro.decisiones.append((d, ticker, D.COMPRA, n))
            if retardo == 0:
                libro.comprar(d, ticker, n, float(cierre), costos, desliz_pb, decidida_el=d)
            elif i + retardo < len(fechas):
                pendientes.append((i + retardo, d, n))
    return libro


# ------------------------------------------------------------
# Señal SIN INFORMACIÓN — la sonda que mide fricción
# ------------------------------------------------------------
def senales_sin_informacion(cierres: pd.DataFrame, tickers, horizonte: int,
                            semilla: int, desde: str):
    """Devuelve fecha -> [Senal] para cada día de `cierres` desde `desde`.

    La magnitud se sortea de la distribución de retornos a `horizonte`
    días hábiles del propio instrumento, medida SÓLO con datos anteriores o
    iguales a `desde` (E3, corrida 11): toda ventana de retorno que entra a
    la distribución cierra en `desde` o antes, así que truncar el archivo
    en cualquier fecha posterior a `desde` no puede cambiar una señal. Si
    la historia previa es más corta que MINIMO_HISTORIA_SENAL, revienta:
    fingir una distribución es peor que no tener una.

    Historia que se deja escrita: la versión de la corrida 10 sorteaba de
    `shift(-horizonte)` sobre la ventana simulada entera, o sea de los
    retornos FUTUROS de esa misma ventana (F2, demostrada: 755 de 756
    señales cambiaban al truncar). La señal sigue sin información sobre la
    DIRECCIÓN de lo que pasa después; lo que estaba contaminado era la
    ESCALA, y la escala decide cuántas órdenes se disparan.

    Es una sonda, no un modelo. Sirve para responder una sola pregunta: qué
    le cuesta a cada juego de parámetros existir."""
    rng = np.random.default_rng(semilla)
    historia = cierres.loc[:desde]
    dist, sigma = {}, {}
    for t in tickers:
        s = historia[t].dropna()
        r = ((s.shift(-horizonte) / s - 1.0).dropna() * 100.0).to_numpy()
        if len(r) < MINIMO_HISTORIA_SENAL:
            raise ValueError(
                f"{t}: sólo {len(r)} retornos a {horizonte} días antes de "
                f"{desde}; la señal sin información necesita al menos "
                f"{MINIMO_HISTORIA_SENAL} para sortear de algo")
        dist[t] = r
        sigma[t] = float(np.std(r, ddof=1))
    por_dia = {}
    for dia in cierres.loc[desde:].index:
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
                      desliz_pb: float, techo_usd: float,
                      retardo: int = RETARDO_IMPLEMENTACION) -> Libro:
    """El libro de la estrategia, día por día.

    Orden dentro de cada sesión d (E4):
      1. se EJECUTAN, contra el cierre de d, las órdenes decididas en
         d − retardo (si el ticker no tiene cierre en d, la orden se cae y
         no se reintenta: nadie ejecuta a ciegas);
      2. se aporta lo que toque;
      3. se DECIDE con las señales y el cierre de d, y lo decidido queda
         pendiente para d + retardo.
    Con retardo = 0 se recupera el comportamiento de la corrida 10, que es
    el que el test de truncación clava como defecto."""
    costos = cfg["costos"]
    j = D.juego(cfg, nombre_juego)
    libro = Libro()
    gasto_dia = gasto_semana = gasto_mes = 0.0
    semana_actual = mes_actual = None
    apagado, motivo = False, ""
    pendientes = []   # (idx_ejecucion, decidida_el, Orden)
    fechas = list(cierres.index)
    for i, dia in enumerate(fechas):
        fila = cierres.iloc[i]
        d = dia.date()
        iso = d.isocalendar()
        if semana_actual != (iso.year, iso.week):
            semana_actual, gasto_semana = (iso.year, iso.week), 0.0
        if mes_actual != (d.year, d.month):
            mes_actual, gasto_mes = (d.year, d.month), 0.0
        gasto_dia = 0.0

        # 1. ejecutar lo decidido `retardo` sesiones atrás
        for (_, decidida, o) in [p for p in pendientes if p[0] == i]:
            cierre = fila.get(o.ticker)
            if cierre is None or pd.isna(cierre):
                continue
            if o.lado == D.VENTA:
                libro.vender(d, o.ticker, o.acciones, float(cierre), costos,
                             desliz_pb, decidida_el=decidida)
            else:
                n = libro.comprar(d, o.ticker, o.acciones, float(cierre), costos,
                                  desliz_pb, decidida_el=decidida)
                if n:
                    desembolso = n * float(cierre) * (1.0 + desliz_pb / 10000.0)
                    gasto_dia += desembolso
                    gasto_semana += desembolso
                    gasto_mes += desembolso
        pendientes = [p for p in pendientes if p[0] > i]

        # 2. aportar
        if d in aportes:
            libro.aportar(aportes[d])

        # 3. decidir con el cierre de hoy
        valor = libro.valor(fila)
        perdida = max(0.0, libro.aportado_usd - valor)
        estado = D.EstadoRiel(gasto_dia, gasto_semana, gasto_mes, perdida,
                              apagado, motivo)
        precios_ref = {t: float(fila[t]) for t in cierres.columns
                       if not pd.isna(fila.get(t))}
        # la caja comprometida por órdenes pendientes no está disponible.
        # Misma convención que `linea_base`: n × precio de decisión con
        # deslizamiento (exigencia G4 del auditor). Con retardo = 1 esta
        # cantidad es siempre cero (lo pendiente se ejecuta en el paso 1 del
        # mismo día); existe para retardo > 1.
        comprometido = sum(o.acciones * o.precio_ref_usd * (1.0 + desliz_pb / 10000.0)
                           for _, _, o in pendientes if o.lado == D.COMPRA)
        cartera = D.Cartera(
            efectivo_usd=max(0.0, libro.efectivo_usd - comprometido),
            posiciones=tuple(D.Posicion(t, acc, 0.0, abierta)
                             for t, (acc, abierta) in libro.posiciones.items()))
        dec = D.proponer_ordenes(senales_por_dia.get(d, []), cartera,
                                 techo_usd, cfg, d, precios_ref, estado,
                                 nombre_juego)
        if dec.riel_apagado and not apagado:
            apagado = True
            motivo = dec.descartes[0][1] if dec.descartes else "sin motivo"
        for o in dec.ordenes:
            libro.decisiones.append((d, o.ticker, o.lado, o.acciones))
            if retardo == 0:
                if o.lado == D.VENTA:
                    libro.vender(d, o.ticker, o.acciones, o.precio_ref_usd,
                                 costos, desliz_pb, decidida_el=d)
                else:
                    n = libro.comprar(d, o.ticker, o.acciones, o.precio_ref_usd,
                                      costos, desliz_pb, decidida_el=d)
                    if n:
                        gasto_dia += o.desembolso_usd
                        gasto_semana += o.desembolso_usd
                        gasto_mes += o.desembolso_usd
            elif i + retardo < len(fechas):
                pendientes.append((i + retardo, d, o))
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
