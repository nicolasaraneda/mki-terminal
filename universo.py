# ============================================================
# Universo MKI Terminal — fuente única de verdad (Etapa 4.6)
#
# Este módulo NO importa Streamlit ni descarga datos: solo constantes.
# Lo consumen app.py (dashboard), motor.py (señales), snapshot.py
# (snapshot programado) y noticias.py (alias de empresas).
#
# Reglas de pertenencia:
#  - "nivel" (0-4 o None): eslabón en la cadena roca→chip→data center.
#    Las fabless (NVIDIA, AMD, ...) tienen nivel=None: participan de
#    rankings/anticipador/noticias pero no del flujo de cadena.
#  - "tipo" (accion/commodity/etf): solo las acciones entran al ranking,
#    al sidebar y al anticipador.
#  - "duplicado_de": el ADR TSM duplica a 2330.TW; sigue en el universo
#    para comparación, pero queda fuera de los promedios de eslabón y de
#    las divergencias (contaría dos veces la misma empresa).
#  - SMH es el benchmark oficial del sistema (BENCHMARK), no un eslabón:
#    un ETF del propio sector en "demanda final" era circular.
# ============================================================

NIVELES_CADENA = {
    0: "Materias primas",
    1: "Materiales",
    2: "Equipos",
    3: "Fabricación",
    4: "Demanda final",
}

BENCHMARK = "SMH"  # benchmark oficial: ETF sectorial VanEck Semiconductor

UNIVERSO = {
    # Nivel 0 — materias primas
    "HG=F": {"nombre": "Cobre (futuro)", "segmento": "Global - materia prima", "nivel": 0, "tipo": "commodity"},
    "SI=F": {"nombre": "Plata (futuro)", "segmento": "Global - materia prima", "nivel": 0, "tipo": "commodity"},
    "BHP": {"nombre": "BHP Group", "segmento": "Australia - minería (ADR)", "nivel": 0, "tipo": "accion"},
    "FCX": {"nombre": "Freeport-McMoRan", "segmento": "EE.UU. - minería de cobre", "nivel": 0, "tipo": "accion"},
    # Nivel 1 — materiales
    "4063.T": {"nombre": "Shin-Etsu Chemical", "segmento": "Japón - obleas de silicio", "nivel": 1, "tipo": "accion"},
    "3436.T": {"nombre": "SUMCO", "segmento": "Japón - obleas de silicio", "nivel": 1, "tipo": "accion"},
    # Nivel 2 — equipos
    "ASML": {"nombre": "ASML (ADR)", "segmento": "Holanda - litografía EUV", "nivel": 2, "tipo": "accion"},
    "8035.T": {"nombre": "Tokyo Electron", "segmento": "Japón - equipos", "nivel": 2, "tipo": "accion"},
    "6857.T": {"nombre": "Advantest", "segmento": "Japón - testeo de chips", "nivel": 2, "tipo": "accion"},
    # Nivel 3 — fabricación
    "2330.TW": {"nombre": "TSMC (Taiwán)", "segmento": "Taiwán - fundición (bolsa local)", "nivel": 3, "tipo": "accion"},
    "TSM": {"nombre": "TSMC (ADR)", "segmento": "Taiwán - fundición (cotiza en NY)", "nivel": 3, "tipo": "accion",
            "duplicado_de": "2330.TW"},
    "005930.KS": {"nombre": "Samsung Electronics", "segmento": "Corea - DRAM / fundición", "nivel": 3, "tipo": "accion"},
    "000660.KS": {"nombre": "SK Hynix", "segmento": "Corea - DRAM / HBM", "nivel": 3, "tipo": "accion"},
    "MU": {"nombre": "Micron", "segmento": "EE.UU. - DRAM / NAND", "nivel": 3, "tipo": "accion"},
    "INTC": {"nombre": "Intel", "segmento": "EE.UU. - CPUs / fundición", "nivel": 3, "tipo": "accion"},
    "UMC": {"nombre": "UMC (ADR)", "segmento": "Taiwán - fundición", "nivel": 3, "tipo": "accion"},
    # Nivel 4 — demanda final real (capex de data centers / hiperescaladores)
    "MSFT": {"nombre": "Microsoft", "segmento": "EE.UU. - proxy capex data centers", "nivel": 4, "tipo": "accion"},
    "GOOGL": {"nombre": "Alphabet", "segmento": "EE.UU. - proxy capex data centers", "nivel": 4, "tipo": "accion"},
    "META": {"nombre": "Meta Platforms", "segmento": "EE.UU. - proxy capex data centers", "nivel": 4, "tipo": "accion"},
    # Benchmark del sistema — fuera de la cadena (circularidad)
    "SMH": {"nombre": "SMH (ETF)", "segmento": "EE.UU. - ETF sectorial, benchmark", "nivel": None, "tipo": "etf"},
    # Diseño fabless — sin eslabón en la cadena (ver DECISIONES.md)
    "NVDA": {"nombre": "NVIDIA", "segmento": "EE.UU. - GPUs / IA", "nivel": None, "tipo": "accion"},
    "AMD": {"nombre": "AMD", "segmento": "EE.UU. - CPUs / GPUs", "nivel": None, "tipo": "accion"},
    "QCOM": {"nombre": "Qualcomm", "segmento": "EE.UU. - chips móviles", "nivel": None, "tipo": "accion"},
    "AVGO": {"nombre": "Broadcom", "segmento": "EE.UU. - redes / custom IA", "nivel": None, "tipo": "accion"},
    "TXN": {"nombre": "Texas Instruments", "segmento": "EE.UU. - análogos", "nivel": None, "tipo": "accion"},
    "ARM": {"nombre": "Arm Holdings", "segmento": "R.Unido - arquitecturas (ADR)", "nivel": None, "tipo": "accion"},
    "IFX.DE": {"nombre": "Infineon", "segmento": "Alemania - potencia / autos", "nivel": None, "tipo": "accion"},
}

# Subconjuntos derivados
ACCIONES = tuple(t for t, d in UNIVERSO.items() if d["tipo"] == "accion")
# La cadena excluye duplicados (TSM cuenta una sola vez, vía 2330.TW)
TICKERS_POR_NIVEL = {
    n: [t for t, d in UNIVERSO.items()
        if d["nivel"] == n and not d.get("duplicado_de")]
    for n in NIVELES_CADENA
}

# Índices de referencia de cada mercado
INDICES = {
    "^SOX": ("SOX Semiconductores", "EE.UU."),
    "^GSPC": ("S&P 500", "EE.UU."),
    "^IXIC": ("Nasdaq", "EE.UU."),
    "^KS11": ("KOSPI", "Corea"),
    "^N225": ("Nikkei 225", "Japón"),
    "^TWII": ("TAIEX", "Taiwán"),
    "^GDAXI": ("DAX", "Alemania"),
}

# Acciones que cotizan en bolsas que abren DESPUÉS del cierre de EE.UU.
MERCADOS_POR_ABRIR = ["005930.KS", "000660.KS", "2330.TW", "8035.T", "6857.T",
                      "IFX.DE", "4063.T", "3436.T"]

DEFAULT = ["NVDA", "AMD", "INTC", "MU", "TSM", "ASML", "005930.KS", "000660.KS"]
PERIODOS = {"3 meses": "3mo", "6 meses": "6mo", "1 año": "1y", "2 años": "2y", "5 años": "5y"}

# Acciones que NO cotizan en USD, y el par de yfinance para convertirlas.
MONEDA_TICKER = {
    "005930.KS": "KRW=X", "000660.KS": "KRW=X",
    "2330.TW": "TWD=X",
    "8035.T": "JPY=X", "6857.T": "JPY=X", "4063.T": "JPY=X", "3436.T": "JPY=X",
    "IFX.DE": "EUR=X",
}
PARES_FX = tuple(sorted(set(MONEDA_TICKER.values())))

# Pares de competidores directos para el detector de divergencias.
# Fundición usa 2330.TW (no el ADR TSM, que es duplicado).
PARES_COMPETIDORES = [
    ("Memoria", ["000660.KS", "MU", "005930.KS"]),
    ("Fundición", ["2330.TW", "UMC"]),
    ("Equipos", ["ASML", "8035.T"]),
    ("Minería", ["BHP", "FCX"]),
]

# Exchange de cada ticker (códigos ISO de exchange_calendars).
# Por defecto todo lo listado en EE.UU. es XNYS (para horarios de sesión,
# NYSE y NASDAQ comparten calendario y horario core 9:30-16:00 ET).
EXCHANGE_POR_TICKER = {}
for _t in UNIVERSO:
    if _t.endswith(".KS"):
        EXCHANGE_POR_TICKER[_t] = "XKRX"
    elif _t.endswith(".TW"):
        EXCHANGE_POR_TICKER[_t] = "XTAI"
    elif _t.endswith(".T"):
        EXCHANGE_POR_TICKER[_t] = "XTKS"
    elif _t.endswith(".DE"):
        EXCHANGE_POR_TICKER[_t] = "XETR"
    else:
        EXCHANGE_POR_TICKER[_t] = "XNYS"

# Índice local y par FX de cada exchange (para residualizar divergencias:
# separar lo idiosincrático de una acción del movimiento de su bolsa y su moneda)
INDICE_LOCAL_POR_EXCHANGE = {
    "XNYS": "^GSPC",
    "XKRX": "^KS11",
    "XTAI": "^TWII",
    "XTKS": "^N225",
    "XETR": "^GDAXI",
}
FX_POR_EXCHANGE = {
    "XKRX": "KRW=X",
    "XTAI": "TWD=X",
    "XTKS": "JPY=X",
    "XETR": "EUR=X",
}


def nombre(t: str) -> str:
    """Nombre legible de un ticker (empresa, índice, o el ticker mismo)."""
    if t in UNIVERSO:
        return UNIVERSO[t]["nombre"]
    if t in INDICES:
        return INDICES[t][0]
    return t
