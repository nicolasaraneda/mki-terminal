# ============================================================
# dinero/universo_dinero.py — el mapa de la cadena a instrumentos COMPRABLES.
#
# Pregunta del bloque 1 del encargo 10: qué eslabón de la cadena de
# semiconductores se puede comprar de verdad desde Chile con 500 dólares, y
# qué eslabón no tiene representación.
#
# NO TOCA universo.py. Son dos universos distintos y mezclarlos sería el
# error: `universo.py` es la cadena que el riel de MEDICIÓN observa (Tokio,
# Taipéi, Seúl incluidos, porque para mirar no hace falta poder comprar);
# esto es la lista de lo que el riel de DINERO puede efectivamente comprar
# desde Chile con una cuenta que todavía no existe.
#
# DOS CLASES DE AFIRMACIÓN, que este archivo no confunde:
#
#   (a) VERIFICADO POR LA MÁQUINA — que el ticker existe y devuelve precio.
#       Ningún ticker entra a la tabla escrito de memoria: entra sólo si la
#       descarga trajo al menos un cierre. Los que no, van a la lista de no
#       verificados con su razón.
#   (b) CONTEXTO NO VERIFICADO — quién domina cada eslabón. Es conocimiento
#       de fondo, no una medición de esta corrida, y va rotulado así en
#       todas partes. Un lector no tiene por qué distinguirlo solo.
#
# Todas las entradas son datos públicos: precios de cierre de instrumentos
# listados. Nada aquí depende de información no pública.
# ============================================================
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

from dinero import precios

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_REGLAS = os.path.join(DIRECTORIO, "reglas.json")


def reglas() -> dict:
    with open(RUTA_REGLAS, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# Los ocho eslabones (los del encargo, en orden de la cadena)
# ------------------------------------------------------------
@dataclass(frozen=True)
class Eslabon:
    clave: str
    nombre: str
    # CONTEXTO NO VERIFICADO: quién manda en el eslabón.
    dominante: str
    # Por qué el dominante puede no ser comprable desde acá.
    obstaculo: str


ESLABONES = (
    Eslabon("materias_primas", "Materias primas y nodos maduros",
            "Obleas de silicio y gases: Shin-Etsu y SUMCO (Tokio). Nodos "
            "maduros: UMC, GlobalFoundries, Tower.",
            "Los proveedores de materia prima pura cotizan en Tokio o son "
            "privados; los nodos maduros sí tienen listado en EE.UU."),
    Eslabon("materiales_obleas", "Materiales químicos y obleas",
            "Shin-Etsu y SUMCO en obleas; JSR y Tokyo Ohka en fotorresinas; "
            "Entegris y MKS en materiales y subsistemas.",
            "El grueso del eslabón cotiza en Tokio. Lo listado en EE.UU. es "
            "la capa de materiales de proceso, no la oblea."),
    Eslabon("litografia_equipos", "Litografía y equipamiento",
            "ASML en litografía EUV (monopolio de facto); Applied Materials, "
            "Lam Research, KLA y Tokyo Electron en el resto del equipo.",
            "ASML y varios pares tienen listado o ADR en EE.UU.; Tokyo "
            "Electron no tiene listado principal en EE.UU."),
    Eslabon("fabricacion_vanguardia", "Fabricación de vanguardia",
            "TSMC. Samsung Foundry e Intel Foundry como segundos.",
            "TSMC cotiza en Taipéi; en EE.UU. sólo hay ADR. Samsung no tiene "
            "listado principal en EE.UU."),
    Eslabon("memoria", "Memoria",
            "Samsung, SK Hynix y Micron en DRAM; Samsung, SK Hynix, Kioxia y "
            "Micron en NAND.",
            "De los cuatro, sólo Micron tiene listado principal en EE.UU. El "
            "eslabón queda representado por su tercer actor."),
    Eslabon("ensamblaje_prueba", "Ensamblaje y prueba (OSAT)",
            "ASE Technology, Amkor, JCET y las casas de empaquetado "
            "avanzado; parte del empaquetado avanzado lo hace la propia "
            "fundición.",
            "ASE tiene ADR y Amkor cotiza en EE.UU."),
    Eslabon("diseno_eda", "Diseño de chips y software EDA",
            "Diseño: NVIDIA, Broadcom, AMD, Qualcomm, Arm. EDA: Synopsys y "
            "Cadence (duopolio, con Siemens EDA tercero).",
            "Es el eslabón mejor representado en EE.UU. de toda la cadena."),
    Eslabon("demanda_final", "Demanda final de IA y datacenter",
            "Microsoft, Google, Meta y Amazon como compradores; Vertiv, "
            "Equinix y Digital Realty en la infraestructura física.",
            "Todos listados en EE.UU."),
)

ESLABONES_POR_CLAVE = {e.clave: e for e in ESLABONES}


# ------------------------------------------------------------
# Los candidatos. NINGUNO es un hecho hasta que la descarga lo confirme.
# ------------------------------------------------------------
@dataclass(frozen=True)
class Candidato:
    ticker: str
    nombre: str
    eslabon: str
    forma: str            # accion | ADR | ETF
    rol: str              # dominante | sustituto | complemento
    sustituye_a: str = ""  # qué original reemplaza, si es sustituto
    diferencia: str = ""   # en qué NO es el original
    nota: str = ""
    # Los ADR de mostrador (OTC) devuelven precio, y eso es lo único que
    # esta corrida verificó. Que una orden se llene a un diferencial
    # razonable NO está verificado y no se puede afirmar desde un cierre.
    liquidez_no_verificada: bool = False


CANDIDATOS = (
    # --- materias primas y nodos maduros ---
    Candidato("UMC", "United Microelectronics (ADR)", "materias_primas",
              "ADR", "dominante",
              "2303.TW, el listado principal en Taipéi",
              "Un ADR no es la acción: cotiza en el horario de Nueva York, "
              "trae riesgo de tipo de cambio TWD/USD y su precio puede "
              "separarse del local por prima o descuento.",
              "Es el par de 2330.TW en PARES_COMPETIDORES del riel de "
              "medición, así que el proyecto ya lo observa."),
    Candidato("GFS", "GlobalFoundries", "materias_primas",
              "accion", "complemento", nota="Nodos maduros, listado en EE.UU."),
    Candidato("TSEM", "Tower Semiconductor", "materias_primas",
              "accion", "complemento", nota="Nodos maduros y especialidad."),
    Candidato("GSM", "Ferroglobe", "materias_primas",
              "accion", "sustituto",
              "los productores de silicio metálico y cuarzo de grado "
              "semiconductor, casi todos privados (Sibelco, Quartz Corp)",
              "Ferroglobe vende silicio metálico y ferroaleaciones a muchos "
              "sectores; el semiconductor es una fracción menor de su "
              "demanda. Comprarlo no es comprar la materia prima del chip."),
    # --- materiales químicos y obleas ---
    Candidato("ENTG", "Entegris", "materiales_obleas",
              "accion", "sustituto",
              "Shin-Etsu (4063.T) y SUMCO (3436.T), los dos fabricantes de "
              "obleas de silicio",
              "Entegris vende materiales de proceso, filtración y manejo de "
              "obleas: es proveedor de la fábrica, no fabricante de la "
              "oblea. La correlación es de sector, no de producto."),
    Candidato("MKSI", "MKS Instruments", "materiales_obleas",
              "accion", "complemento",
              nota="Subsistemas de vacío, láser y control de proceso."),
    Candidato("LIN", "Linde", "materiales_obleas",
              "accion", "sustituto",
              "los gases de proceso de grado electrónico",
              "Linde es un gigante de gases industriales diversificado; el "
              "electrónico es una línea, no la empresa."),
    Candidato("SHECY", "Shin-Etsu Chemical (ADR OTC)", "materiales_obleas",
              "ADR", "dominante",
              "4063.T, el listado principal en Tokio",
              "ADR de mostrador (OTC), no listado en bolsa: liquidez baja y "
              "diferencial de compra-venta ancho. Verificar antes de creerle.",
              liquidez_no_verificada=True),
    # --- litografía y equipamiento ---
    Candidato("ASML", "ASML Holding", "litografia_equipos",
              "ADR", "dominante",
              "ASML.AS, el listado principal en Ámsterdam",
              "El ADR de ASML es de nivel III y cotiza en Nasdaq con "
              "liquidez propia; la diferencia con el original es horario y "
              "moneda, no profundidad."),
    Candidato("AMAT", "Applied Materials", "litografia_equipos",
              "accion", "complemento"),
    Candidato("LRCX", "Lam Research", "litografia_equipos",
              "accion", "complemento"),
    Candidato("KLAC", "KLA Corporation", "litografia_equipos",
              "accion", "complemento"),
    Candidato("TER", "Teradyne", "litografia_equipos",
              "accion", "complemento", nota="Equipo de prueba."),
    Candidato("TOELY", "Tokyo Electron (ADR OTC)", "litografia_equipos",
              "ADR", "sustituto",
              "8035.T, el listado principal en Tokio",
              "ADR de mostrador: liquidez baja. Verificar.",
              liquidez_no_verificada=True),
    # --- fabricación de vanguardia ---
    Candidato("TSM", "TSMC (ADR)", "fabricacion_vanguardia",
              "ADR", "dominante",
              "2330.TW, el listado principal en Taipéi",
              "El riel de medición usa 2330.TW y trata al ADR como "
              "DUPLICADO (universo.py, `duplicado_de`), justamente porque no "
              "son el mismo instrumento: distinto horario, distinta moneda, "
              "prima variable. Para comprar desde Chile con 500 dólares, el "
              "ADR es lo único disponible."),
    Candidato("INTC", "Intel", "fabricacion_vanguardia",
              "accion", "complemento",
              nota="Intel Foundry como segundo intento occidental."),
    # --- memoria ---
    Candidato("MU", "Micron Technology", "memoria", "accion", "dominante",
              nota="Tercero mundial en DRAM; el único de los grandes con "
                   "listado principal en EE.UU."),
    Candidato("SNDK", "SanDisk", "memoria", "accion", "complemento",
              nota="NAND, escindida de Western Digital. Verificar: si el "
                   "ticker no responde, no entra."),
    Candidato("WDC", "Western Digital", "memoria", "accion", "complemento"),
    # --- ensamblaje y prueba ---
    Candidato("ASX", "ASE Technology (ADR)", "ensamblaje_prueba",
              "ADR", "dominante",
              "3711.TW, el listado principal en Taipéi",
              "Mismas diferencias que cualquier ADR: horario, moneda, prima."),
    Candidato("AMKR", "Amkor Technology", "ensamblaje_prueba",
              "accion", "complemento"),
    # --- diseño y EDA ---
    Candidato("NVDA", "NVIDIA", "diseno_eda", "accion", "dominante"),
    Candidato("AVGO", "Broadcom", "diseno_eda", "accion", "complemento"),
    Candidato("AMD", "AMD", "diseno_eda", "accion", "complemento"),
    Candidato("QCOM", "Qualcomm", "diseno_eda", "accion", "complemento"),
    Candidato("ARM", "Arm Holdings (ADR)", "diseno_eda", "ADR", "complemento",
              "ARM.L / la matriz SoftBank",
              "El ADR de Arm es el vehículo listado tras la salida a bolsa "
              "de 2023; SoftBank retiene la mayoría."),
    Candidato("SNPS", "Synopsys", "diseno_eda", "accion", "dominante",
              nota="Mitad del duopolio de EDA."),
    Candidato("CDNS", "Cadence Design Systems", "diseno_eda",
              "accion", "dominante", nota="La otra mitad."),
    # --- demanda final ---
    Candidato("MSFT", "Microsoft", "demanda_final", "accion", "dominante",
              nota="Nivel 4 del riel de medición."),
    Candidato("GOOGL", "Alphabet", "demanda_final", "accion", "dominante",
              nota="Nivel 4 del riel de medición."),
    Candidato("META", "Meta Platforms", "demanda_final", "accion", "dominante",
              nota="Nivel 4 del riel de medición."),
    Candidato("AMZN", "Amazon", "demanda_final", "accion", "complemento"),
    Candidato("VRT", "Vertiv Holdings", "demanda_final", "accion",
              "complemento", nota="Energía y refrigeración de datacenter."),
    # --- cestas: el sustituto barato de un eslabón entero ---
    Candidato("SMH", "VanEck Semiconductor ETF", "diseno_eda",
              "ETF", "sustituto",
              "la cadena entera",
              "Una cesta no es un eslabón: pondera por capitalización y "
              "queda dominada por diseño y fabricación. Comprarla es "
              "comprar el sector, que es justo lo contrario de apostar a un "
              "eslabón contra otro.",
              "Es el BENCHMARK del riel de medición (universo.py)."),
    Candidato("SOXX", "iShares Semiconductor ETF", "diseno_eda",
              "ETF", "sustituto", "la cadena entera",
              "Mismo reparo que SMH."),
    Candidato("XSD", "SPDR S&P Semiconductor ETF", "diseno_eda",
              "ETF", "sustituto", "la cadena entera",
              "Ponderación igualitaria en vez de por capitalización: menos "
              "dominado por los tres grandes, más expuesto a los chicos."),
)

# CONTEXTO NO VERIFICADO: dominantes que NO se pueden comprar, y por qué.
# La empresa privada no es comprable y decirlo es parte del mapa.
NO_COMPRABLES = (
    ("materias_primas", "Sibelco, The Quartz Corp (cuarzo de alta pureza)",
     "PRIVADAS", "No cotizan en ninguna bolsa. Se le compra, en su lugar, a "
     "productores diversificados de silicio metálico."),
    ("materiales_obleas", "Shin-Etsu Chemical (4063.T), SUMCO (3436.T)",
     "COTIZAN FUERA DE EE.UU.",
     "Listado principal en Tokio. Sólo hay ADR de mostrador."),
    ("litografia_equipos", "Tokyo Electron (8035.T)", "COTIZA FUERA DE EE.UU.",
     "Listado principal en Tokio."),
    ("fabricacion_vanguardia", "TSMC (2330.TW)", "COTIZA FUERA DE EE.UU.",
     "Listado principal en Taipéi; en EE.UU. sólo el ADR."),
    ("memoria", "Samsung Electronics (005930.KS), SK Hynix (000660.KS)",
     "COTIZAN FUERA DE EE.UU.",
     "Listado principal en Seúl. Samsung tiene ADR de mostrador poco "
     "líquido; SK Hynix no tiene ADR utilizable."),
    ("memoria", "Kioxia", "COTIZA FUERA DE EE.UU.",
     "Listado en Tokio desde 2024."),
    ("ensamblaje_prueba", "JCET (600584.SS)", "COTIZA FUERA DE EE.UU.",
     "Listado en Shanghái."),
    ("diseno_eda", "Siemens EDA", "SEGMENTO DE UN CONGLOMERADO",
     "No cotiza por separado: es una división de Siemens AG."),
)


# ------------------------------------------------------------
# Costo de una orden — con el supuesto a la vista
# ------------------------------------------------------------
def comision_usd(n_acciones, precio: float, costos: dict,
                 fraccionarias: bool = False) -> float:
    """Comisión de una orden bajo el arancel de reglas.json (desde el 8-sep,
    el publicado del insumo §40). Enteras: máx(mínimo, por acción × n),
    topada en el % del monto — con mínimo 0,35 y tope 1 % el cruce está en
    35 USD por orden. Fraccionarias (`fraccionarias=True`, columna del
    insumo que esta cuenta NO usa): máx(mínimo, % del monto), que no se
    diluye nunca."""
    if n_acciones <= 0:
        return 0.0
    monto = n_acciones * precio
    if fraccionarias:
        f = costos["fraccionarias_no_usadas"]
        return max(f["comision_minima_usd"], f["comision_pct_del_monto"] / 100.0 * monto)
    bruta = max(costos["comision_minima_usd"],
                costos["comision_por_accion_usd"] * n_acciones)
    tope = costos["comision_tope_pct_del_monto"] / 100.0 * monto
    return min(bruta, tope)


def acciones_por_monto(monto: float, precio: float, costos: dict,
                       fraccionarias: bool = False):
    """Cuántas acciones entran en `monto`, comisión incluida. Enteras: un
    entero. Fraccionarias: un float (las unidades que compra `monto` neto
    de la comisión proporcional). El modo es un ARGUMENTO explícito, no una
    bandera escondida en reglas.json: el censo se computa en los dos."""
    if precio <= 0 or monto <= 0:
        return 0.0 if fraccionarias else 0
    if fraccionarias:
        f = costos["fraccionarias_no_usadas"]
        valor = monto / (1.0 + f["comision_pct_del_monto"] / 100.0)
        if valor - f["comision_minima_usd"] <= 0:
            return 0.0
        return valor / precio
    n = int(monto // precio)
    while n > 0 and n * precio + comision_usd(n, precio, costos) > monto:
        n -= 1
    return n


def friccion_ida_y_vuelta(monto: float, precio: float, costos: dict,
                          fraccionarias: bool = False) -> dict:
    """Qué cuesta entrar y salir con `monto` en un instrumento: comisión de
    compra más comisión de venta (sin deslizamiento), en USD y como % de la
    posición efectivamente tomada. Lo pide el bloque 10 de la corrida 11:
    la fricción al lado de cada instrumento, leída del arancel del §40."""
    n = acciones_por_monto(monto, precio, costos, fraccionarias)
    if not n:
        return {"unidades": 0, "posicion_usd": 0.0, "friccion_usd": None, "friccion_pct": None}
    posicion = n * precio
    ida_vuelta = 2.0 * comision_usd(n, precio, costos, fraccionarias)
    return {"unidades": n, "posicion_usd": posicion, "friccion_usd": ida_vuelta,
            "friccion_pct": 100.0 * ida_vuelta / posicion}


@dataclass
class FilaMapa:
    candidato: Candidato
    precio: float | None = None
    fecha_precio: str | None = None
    verificado: bool = False
    razon_no_verificado: str = ""
    acciones_con_techo: int = 0
    comision_orden_minima_pct: float | None = None
    comision_orden_techo_pct: float | None = None
    alcanza_con_techo: bool = False
    alcanza_con_piso: bool = False
    presupuesto_usd: float | None = None
    fraccionarias: bool = False
    friccion_ida_vuelta_usd: float | None = None
    friccion_ida_vuelta_pct: float | None = None


def construir_mapa(cierres, cfg: dict | None = None,
                   presupuesto: float | None = None,
                   fraccionarias: bool = False) -> list:
    """Cruza los candidatos con los precios efectivamente descargados.
    Función PURA respecto de la red: recibe el DataFrame, no lo baja.

    `presupuesto` (bloque 10, corrida 11) reemplaza al techo de reglas.json
    como «con cuánto se compra»; `fraccionarias` cambia el modo de compra.
    Con los dos por defecto reproduce el censo original (techo, enteras)."""
    cfg = cfg or reglas()
    costos = cfg["costos"]
    techo = cfg["presupuesto"]["techo_usd"] if presupuesto is None else presupuesto
    piso = cfg["presupuesto"]["piso_usd"]
    filas = []
    for c in CANDIDATOS:
        fila = FilaMapa(candidato=c)
        precio, fecha = precios.ultimo_cierre(cierres, c.ticker)
        if precio is None or not math.isfinite(precio) or precio <= 0:
            fila.razon_no_verificado = (
                "la fuente no devolvió ningún cierre para el símbolo"
                if c.ticker not in getattr(cierres, "columns", [])
                else "la columna existe pero llegó entera vacía")
            filas.append(fila)
            continue
        fila.verificado = True
        fila.precio = precio
        fila.fecha_precio = str(fecha)
        fila.presupuesto_usd = techo
        fila.fraccionarias = fraccionarias
        fila.acciones_con_techo = acciones_por_monto(techo, precio, costos, fraccionarias)
        c1 = comision_usd(1, precio, costos, fraccionarias)
        fila.comision_orden_minima_pct = 100.0 * c1 / precio
        n = fila.acciones_con_techo
        if n > 0:
            fila.comision_orden_techo_pct = (
                100.0 * comision_usd(n, precio, costos, fraccionarias) / (n * precio))
        fr = friccion_ida_y_vuelta(techo, precio, costos, fraccionarias)
        fila.friccion_ida_vuelta_usd = fr["friccion_usd"]
        fila.friccion_ida_vuelta_pct = fr["friccion_pct"]
        fila.alcanza_con_techo = n > 0
        fila.alcanza_con_piso = acciones_por_monto(piso, precio, costos, fraccionarias) > 0
        filas.append(fila)
    return filas


def estado_del_eslabon(filas_del_eslabon: list,
                       exigir_liquidez: bool = False) -> str:
    """REPRESENTADO / SUSTITUIDO / HUECO.

    Regla, escrita antes de mirar los precios: un eslabón está REPRESENTADO
    si tiene al menos un instrumento verificado con rol `dominante` que se
    pueda comprar con el techo del presupuesto; SUSTITUIDO si lo único
    comprable es un sustituto o un complemento; HUECO si no queda nada
    comprable. Un dominante que cotiza pero no alcanza con 500 dólares NO
    cuenta como representado: el mapa es de lo comprable, no de lo listado.
    """
    comprables = [f for f in filas_del_eslabon
                  if f.verificado and f.alcanza_con_techo
                  and not (exigir_liquidez and f.candidato.liquidez_no_verificada)]
    if not comprables:
        return "HUECO"
    if any(f.candidato.rol == "dominante" for f in comprables):
        return "REPRESENTADO"
    return "SUSTITUIDO"
