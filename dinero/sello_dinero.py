# ============================================================
# dinero/sello_dinero.py — E0: la primera fila sellada PROSPECTIVA del riel
# de dinero. Corrida 12 (9-sep-2026), acta §84.4 puntos 1 y 7, regla de
# aporte E0 (GEMELO/propuestas/regla_aporte_y_dimensionamiento.md §3).
#
#   python -m dinero.sello_dinero --sellar            # descarga la extensión, decide, sella
#   python -m dinero.sello_dinero --sellar --sin-red  # usa la última extensión ya congelada
#   python -m dinero.sello_dinero --estado            # cuenta filas y muestra la última
#
# QUÉ ES E0, dicho sin adorno: la máquina emite una decisión del riel de
# dinero ANTES de la apertura del mercado objetivo y la sella con tamaño
# nominal CERO. No mueve plata, no toca ninguna cuenta. Lo único que compra
# es lo que más cómputo no fabrica: filas cuya marca de tiempo la puso la
# máquina antes del evento, verificables por un tercero.
#
# QUÉ SEÑAL SELLA, dicho antes de que alguien lo lea mal: la del juego por
# defecto de `reglas.json` alimentado por la SONDA SIN INFORMACIÓN de la
# cuenta en papel (`contabilidad.senales_sin_informacion`, semilla declarada),
# porque el riel de dinero NO tiene ninguna señal con ventaja medida (L1
# refutada, WS2b negativo). Cada fila lleva `senal_fuente` diciéndolo. Estas
# filas prueban la MAQUINARIA del sellado prospectivo; no son un track record
# de habilidad y el contador que las publica lo dice. Qué señal debe sellar
# E0 en adelante es pregunta de firma (espera_firma.md §51).
#
# POR QUÉ NO PASA POR `cuenta_papel.correr`: esa función tiene la ventana
# congelada (DESDE/HASTA), acumula estado (posiciones, presupuestos) y su
# gate recorrió esa ventana y no otra (pre-mortem 2 de la corrida 12). E0 se
# construye sobre las mismas piezas PURAS que ese camino usa, con el día
# como argumento: membresía fijada en DESDE (E1/G6), sonda con `desde=DESDE`
# (E3), `decision.proponer_ordenes` con el cierre del día como `precios_ref`
# y una cartera VACÍA con efectivo igual al presupuesto declarado (E0 no
# acumula posiciones: tamaño nominal cero). Todo eso se verifica invariante
# al borrado del futuro (tests/test_sello_dinero.py) y el `auditor-lookahead`
# dictaminó antes del primer sello (GEMELO/resultados/dictamen_12/).
#
# EL INSUMO, sellado como dato y no como recuerdo: el congelado grande
# (`cierres_congelados.csv`, sha256 fijo) más una EXTENSIÓN chica con las
# sesiones posteriores (`dinero/datos/sello/ext_YYYY-MM-DD.csv` + `.meta.json`
# con la disponibilidad por ticker, G8, y el solape contra el congelado, E7).
# La fila guarda los dos sha256, el de `reglas.json` y el de este módulo (E6).
# `available_at` = el máximo `available_at_utc` de la extensión (cierre UTC
# por calendario de la última sesión con dato), NUNCA el reloj de pared; y
# se exige available_at < timestamp_utc < apertura objetivo, o la fila queda
# marcada `no_verificable_timing` (misma regla maestra del riel de medición).
#
# LO QUE EL AUDITOR EXIGIÓ ANTES DEL PRIMER SELLO (dictamen_12, E1–E5) y está
# acá: el gate NO puede ser vacuo (en el último día del insumo hay un solo
# corte, así que se vigila el penúltimo y 6 sesiones atrás, y se dice que el
# último no se puede vigilar); el «día» del sello se deriva del calendario de
# NUEVA YORK desde `timestamp_utc`, nunca del huso del host; la disponibilidad
# se sella POR TICKER y un ticker sin dato lo dice en su motivo (un día
# incompleto no cuenta para N); un segundo sello del mismo día con OTRO
# insumo se registra en `divergencias_sello` y no inserta nada; la extensión
# se respalda en data/backups/ (el sha tiene que apuntar a algo que exista
# mañana) y exportar desde una base temporal exige ruta explícita.
#
# LA BASE ES PROPIA (`dinero/sello_dinero.db`): `senales.db` sostiene la
# cadena de sellos viva del titular y ningún agente corre DDL sobre ella
# (pre-mortem 3). Las filas no se reescriben: triggers que abortan toda
# modificación o borrado, más export CSV a `data/backups/` que el job de
# backup versiona. La corrección de una fila sellada es una fila nueva o una
# errata fechada, nunca una modificación.
#
# AISLAMIENTO: nada de acá importa el camino de sellado del riel de medición
# (tests/test_dinero.py, sección 1). El calendario es `exchange_calendars`
# directo, como en `precios.py`; `version.py` se lee como texto.
# ============================================================
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone

import exchange_calendars as xcals
import pandas as pd

from dinero import contabilidad as C
from dinero import cuenta_papel as CP
from dinero import decision as D
from dinero import precios
from dinero import universo_dinero as U

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(DIRECTORIO)


def _plataforma_version() -> str:
    """`version.py` es camino de sellado y `dinero/` no lo importa (regla de
    aislamiento, tests/test_dinero.py). La fila necesita igual declarar qué
    plataforma la produjo, así que se lee el texto del archivo, no el módulo."""
    with open(os.path.join(RAIZ, "version.py"), encoding="utf-8") as f:
        m = re.search(r'^PLATAFORMA_VERSION\s*=\s*"([^"]+)"', f.read(), re.M)
    return m.group(1) if m else "?"


PLATAFORMA_VERSION = _plataforma_version()
RUTA_DB = os.path.join(DIRECTORIO, "sello_dinero.db")
DIR_EXT = os.path.join(DIRECTORIO, "datos", "sello")
RUTA_BACKUP_CSV = os.path.join(RAIZ, "data", "backups", "sello_dinero.csv")
DIR_BACKUP_EXT = os.path.join(RAIZ, "data", "backups", "sello_dinero_ext")
EXCHANGE = "XNYS"            # todo el universo operable cotiza en horario de Nueva York
SESIONES_EXTENSION = 15      # cuántas sesiones recientes trae la extensión (holgura para feriados y solape)
SENAL_FUENTE = ("sorteo sin información (contabilidad.senales_sin_informacion, semilla "
                f"{C.SEMILLA_SENAL_SIN_INFORMACION}, desde {CP.DESDE}): prueba de maquinaria, no track record")
ESTADO_PENDIENTE = "pendiente"
ESTADO_NO_VERIFICABLE = "no_verificable_timing"
ESTADO_SIN_SESION = "dia_sin_sesion"
ESTADO_INSUMO_INCOMPLETO = "insumo_incompleto"
VERSION_SELLO = "E0.2"       # E0.1 nunca selló una fila real; E0.2 = tras las exigencias E1–E8 del auditor
MINIMO_CORTES_GATE = 2
# N que cierra E0: fijado por Nicolás el 8-sep-2026 (acta §84.4.7) ANTES de la
# primera fila. No se mueve. Sólo cuentan las sesiones con `cuenta_para_N = 1`.
N_OBJETIVO_E0 = 40
N_OBJETIVO_FUENTE = "DECISIÓN firmada: acta §84.4.7 (8-sep-2026), fijado antes de la primera fila; no es un dato de la base"


# ------------------------------------------------------------
# Base propia, filas inmutables
# ------------------------------------------------------------
def conectar(ruta: str = RUTA_DB, solo_lectura: bool = False) -> sqlite3.Connection:
    if solo_lectura:
        return sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    con = sqlite3.connect(ruta)
    init_db(con)
    return con


_ABORTA_MODIFICAR = "SELECT RAISE(ABORT, 'las filas selladas del riel de dinero no se reescriben')"
_ABORTA_BORRAR = "SELECT RAISE(ABORT, 'las filas selladas del riel de dinero no se borran')"


def init_db(con: sqlite3.Connection) -> None:
    con.executescript(f"""
        CREATE TABLE IF NOT EXISTS sellos_dinero (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_sello TEXT NOT NULL,          -- día de la EMISIÓN en el calendario de Nueva York (E2)
            fecha_insumo TEXT NOT NULL,         -- última sesión con dato en el insumo
            timestamp_utc TEXT NOT NULL,        -- reloj de pared de la EMISIÓN (máquina)
            available_at TEXT,                  -- cierre UTC por calendario de fecha_insumo
            exchange TEXT NOT NULL,
            sesion_objetivo TEXT,               -- la sesión cuya apertura se anticipa
            apertura_objetivo_utc TEXT,
            ticker TEXT NOT NULL,
            decision TEXT NOT NULL,             -- compra | venta | nada
            acciones_regla INTEGER,             -- lo que la regla dimensionaría con el presupuesto declarado
            tamano_nominal INTEGER NOT NULL,    -- 0 en E0, siempre
            precio_ref_usd REAL,
            senal_magnitud_pp REAL,
            senal_banda_baja_pp REAL,
            senal_banda_alta_pp REAL,
            senal_fuente TEXT NOT NULL,
            juego TEXT NOT NULL,
            presupuesto_usd REAL NOT NULL,
            reglas_version TEXT NOT NULL,
            motivo TEXT,                        -- por qué «nada», cuando la decisión es nada
            ultimo_cierre_ticker TEXT,          -- E3: última sesión con dato DE ESTE ticker
            available_at_ticker TEXT,           -- E3: cierre UTC por calendario de esa sesión
            insumo_ext_sha256 TEXT NOT NULL,
            insumo_ext_archivo TEXT,
            insumo_base_sha256 TEXT NOT NULL,
            reglas_sha256 TEXT,                 -- E6: huella de dinero/reglas.json
            sellador_sha256 TEXT,               -- E6: huella del código de este módulo
            plataforma_version TEXT NOT NULL,
            version_sello TEXT NOT NULL,
            estado TEXT NOT NULL,               -- pendiente | no_verificable_timing | dia_sin_sesion | insumo_incompleto
            estado_timing TEXT,                 -- E8: ok | roto
            estado_dia TEXT,                    -- E8: sesion | sin_sesion
            insumo_completo INTEGER,            -- E3: 1 si todos los operables tienen cierre en fecha_insumo
            cuenta_para_N INTEGER NOT NULL,     -- 1 sólo si pendiente, día con sesión, insumo fresco y completo
            creado_en TEXT NOT NULL,
            UNIQUE (fecha_insumo, ticker, juego)
        );
        CREATE TRIGGER IF NOT EXISTS sellos_dinero_inmutable_1 BEFORE UPDATE ON sellos_dinero
            BEGIN {_ABORTA_MODIFICAR}; END;
        CREATE TRIGGER IF NOT EXISTS sellos_dinero_inmutable_2 BEFORE DELETE ON sellos_dinero
            BEGIN {_ABORTA_BORRAR}; END;
        -- E4: un segundo sello del MISMO fecha_insumo con OTRO insumo no se ignora en
        -- silencio: queda registrado acá, y las filas originales no se tocan.
        CREATE TABLE IF NOT EXISTS divergencias_sello (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_insumo TEXT NOT NULL,
            timestamp_utc TEXT NOT NULL,
            sha_sellado TEXT NOT NULL,
            sha_nuevo TEXT NOT NULL,
            decisiones_distintas INTEGER,
            detalle TEXT,
            creado_en TEXT NOT NULL
        );
        CREATE TRIGGER IF NOT EXISTS divergencias_sello_inmutable_1 BEFORE UPDATE ON divergencias_sello
            BEGIN {_ABORTA_MODIFICAR}; END;
        CREATE TRIGGER IF NOT EXISTS divergencias_sello_inmutable_2 BEFORE DELETE ON divergencias_sello
            BEGIN {_ABORTA_BORRAR}; END;
    """)
    con.commit()


# ------------------------------------------------------------
# Calendario (exchange_calendars directo: calendarios.py es camino de sellado)
# ------------------------------------------------------------
def _cal():
    return xcals.get_calendar(EXCHANGE)


def cierre_utc(sesion) -> datetime:
    return _cal().session_close(pd.Timestamp(sesion)).tz_convert("UTC").to_pydatetime()


def proxima_sesion_despues_de(instante_utc: datetime) -> tuple:
    """(sesión, apertura_utc): la primera sesión cuya APERTURA es estrictamente
    posterior al instante. Misma semántica que calendarios.proxima_sesion_despues_de,
    reimplementada acá por la regla de aislamiento."""
    cal = _cal()
    ts = pd.Timestamp(instante_utc)
    ts = ts.tz_convert("UTC") if ts.tzinfo else ts.tz_localize("UTC")
    fecha_local = ts.tz_convert(cal.tz).normalize().tz_localize(None)
    sesion = cal.date_to_session(fecha_local, direction="next")
    while cal.session_open(sesion).tz_convert("UTC") <= ts:
        sesion = cal.next_session(sesion)
    return str(sesion.date()), cal.session_open(sesion).tz_convert("UTC").to_pydatetime()


def es_sesion(fecha) -> bool:
    return bool(_cal().is_session(pd.Timestamp(fecha)))


def dia_en_calendario_del_exchange(instante_utc: datetime) -> str:
    """E2: la fecha de la emisión en la zona del EXCHANGE, no del host."""
    ts = pd.Timestamp(instante_utc)
    ts = ts.tz_convert("UTC") if ts.tzinfo else ts.tz_localize("UTC")
    return str(ts.tz_convert(_cal().tz).normalize().date())


# ------------------------------------------------------------
# Insumo: congelado grande + extensión chica, los dos con sha256
# ------------------------------------------------------------
def _sha256(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(65536), b""):
            h.update(trozo)
    return h.hexdigest()


def descargar_extension(tickers, sesiones: int = SESIONES_EXTENSION) -> pd.DataFrame:
    """La ÚNICA función de este módulo que toca la red. Trae los cierres de
    las últimas `sesiones` sesiones (holgura) para recortarlos después a lo
    posterior al congelado grande, guardando el solape como evidencia (E7)."""
    import yfinance as yf
    datos = yf.download(list(tickers), period=f"{sesiones * 2}d", interval="1d",
                        auto_adjust=True, progress=False)
    if datos.empty:
        return pd.DataFrame()
    cierres = datos["Close"] if isinstance(datos.columns, pd.MultiIndex) else datos[["Close"]]
    return cierres.reindex(columns=[t for t in tickers if t in cierres.columns])


def _solape_contra_congelado(cierres_ext: pd.DataFrame, base_hasta: str, tolerancia_rel: float = 1e-6) -> dict:
    """E7: las sesiones de la descarga que ya están en el congelado grande son
    la única evidencia de un reajuste retroactivo (split/dividendo) entre las
    dos mitades del insumo. Se comparan y el resultado va al meta. NO se
    corrige nada: se detecta y se declara."""
    try:
        base = precios.cargar_congelado()
    except FileNotFoundError:
        return {"sesiones": 0, "reajuste_detectado": None, "nota": "sin congelado grande contra el que comparar"}
    comunes = cierres_ext.index.intersection(base.index)
    comunes = comunes[comunes <= pd.Timestamp(base_hasta)]
    if len(comunes) == 0:
        return {"sesiones": 0, "reajuste_detectado": None,
                "nota": "la descarga no trae sesiones que solapen con el congelado: reajuste NO verificable"}
    cols = [c for c in cierres_ext.columns if c in base.columns]
    a = cierres_ext.loc[comunes, cols].astype(float)
    b = base.loc[comunes, cols].astype(float)
    dif = ((a - b).abs() / b.abs().where(b.abs() > 0)).stack().dropna()
    peor = float(dif.max()) if len(dif) else 0.0
    fuera = sorted({t for (_, t), v in dif.items() if v > tolerancia_rel})
    return {"sesiones": int(len(comunes)), "desde": str(comunes.min().date()), "hasta": str(comunes.max().date()),
            "dif_rel_max": peor, "tolerancia_rel": tolerancia_rel,
            "reajuste_detectado": bool(fuera), "tickers_con_reajuste": fuera}


def congelar_extension(cierres_ext: pd.DataFrame, base_hasta: str) -> tuple:
    """Escribe la extensión recortada a las sesiones POSTERIORES a `base_hasta`
    y su metadato con disponibilidad por ticker (G8) y solape (E7).
    Devuelve (ruta_csv, meta)."""
    os.makedirs(DIR_EXT, exist_ok=True)
    idx = pd.to_datetime(cierres_ext.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    cierres_ext = cierres_ext.copy()
    cierres_ext.index = idx
    ext = cierres_ext.loc[cierres_ext.index > pd.Timestamp(base_hasta)].copy()
    ext.index.name = "Date"
    if ext.empty:
        raise RuntimeError(f"la descarga no trae ninguna sesión posterior a {base_hasta}: no hay insumo nuevo que sellar")
    solape = _solape_contra_congelado(cierres_ext, base_hasta)
    hasta = str(ext.index.max().date())
    ruta = os.path.join(DIR_EXT, f"ext_{hasta}.csv")
    ext.to_csv(ruta)
    meta = {
        "congelado_en_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "motivo": "extensión del congelado para el sellado prospectivo E0 (dinero/sello_dinero.py)",
        "fuente": "yfinance (mismo proveedor que ya ingiere el proyecto)",
        "extiende_a": {"archivo": os.path.basename(precios.RUTA_CIERRES), "hasta": base_hasta},
        "tickers": list(ext.columns), "filas": int(len(ext)),
        "desde": str(ext.index.min().date()), "hasta": hasta,
        "sha256": _sha256(ruta),
        "disponibilidad": {"exchange": EXCHANGE, "por_ticker": precios.disponibilidad_por_ticker(ext)},
        "solape_con_congelado": solape,
        "advertencia": "cierres ajustados retroactivamente por yfinance: no point-in-time (declarado, no corregido)",
    }
    with open(os.path.splitext(ruta)[0] + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return ruta, meta


def ultima_extension() -> tuple | None:
    if not os.path.isdir(DIR_EXT):
        return None
    csvs = sorted(a for a in os.listdir(DIR_EXT) if a.startswith("ext_") and a.endswith(".csv"))
    if not csvs:
        return None
    ruta = os.path.join(DIR_EXT, csvs[-1])
    with open(os.path.splitext(ruta)[0] + ".meta.json", encoding="utf-8") as f:
        return ruta, json.load(f)


def insumo(ruta_ext: str) -> pd.DataFrame:
    """Congelado grande + extensión, sin solapamiento, ordenado."""
    base = precios.cargar_congelado()
    ext = pd.read_csv(ruta_ext, index_col=0, parse_dates=True)
    ext = ext.loc[ext.index > base.index.max()]
    return pd.concat([base, ext.reindex(columns=base.columns)], axis=0, sort=True)


# ------------------------------------------------------------
# La decisión del día: función PURA del insumo hasta `dia`
# ------------------------------------------------------------
def decidir(cierres: pd.DataFrame, dia, cfg: dict | None = None,
            juego: str | None = None, presupuesto: float | None = None) -> dict:
    """Decisión del juego por defecto para la apertura siguiente a `dia`, con
    datos <= `dia` únicamente: membresía al DESDE (E1/G6), sonda con
    desde=DESDE (E3), cartera VACÍA con efectivo = presupuesto, sin estado
    entre días. Es lo que el gate de invariancia recorre (tests).

    Dependencia declarada (auditor, H2): la sonda avanza un rng por sesión
    desde DESDE, así que la decisión de `dia` depende del NÚMERO de sesiones
    en el insumo entre DESDE y `dia`. No es fuga de futuro (es pasado), pero
    una sesión que la fuente omita o reponga corre el sorteo: por eso el
    insumo se sella con sha256 y la extensión se respalda (E5)."""
    cfg = cfg or U.reglas()
    juego = juego or cfg["juego_activo"]
    presupuesto = cfg["presupuesto"]["techo_usd"] if presupuesto is None else presupuesto
    dia_ts = pd.Timestamp(dia)
    hasta = cierres.loc[:dia_ts]
    if hasta.empty or hasta.index.max().date() != dia_ts.date():
        raise ValueError(f"el insumo no tiene la sesión {dia_ts.date()}: no se decide sobre un día sin dato")
    operables = CP.universo_operable(hasta, cfg, hasta=CP.DESDE)
    senales = C.senales_sin_informacion(hasta, operables, CP.HORIZONTE_SENAL_HABILES,
                                        C.SEMILLA_SENAL_SIN_INFORMACION, desde=CP.DESDE)
    fila = hasta.iloc[-1]
    precios_ref = {t: float(fila[t]) for t in hasta.columns if not pd.isna(fila.get(t))}
    cartera = D.Cartera(efectivo_usd=float(presupuesto), posiciones=())
    dec = D.proponer_ordenes(senales.get(dia_ts.date(), []), cartera, float(presupuesto), cfg,
                             dia_ts.date(), precios_ref, D.EstadoRiel(), juego)
    por_ticker = {}
    for o in dec.ordenes:
        por_ticker[o.ticker] = {"decision": o.lado, "acciones_regla": int(o.acciones),
                                "precio_ref_usd": float(o.precio_ref_usd), "motivo": None}
    motivos = {t: m for (t, m) in dec.descartes}
    sen_por_ticker = {s.ticker: s for s in senales.get(dia_ts.date(), [])}
    disp = precios.disponibilidad_por_ticker(hasta[operables])
    filas = []
    for t in operables:
        s = sen_por_ticker.get(t)
        d = por_ticker.get(t, {"decision": "nada", "acciones_regla": 0,
                               "precio_ref_usd": precios_ref.get(t), "motivo": motivos.get(t, motivos.get("*"))})
        # E3: si el ticker NO tiene cierre en `dia`, la fila lo dice; el motivo no
        # puede atribuir a la señal lo que fue falta de dato
        if d["precio_ref_usd"] is None:
            d = dict(d, decision="nada", acciones_regla=0,
                     motivo=f"sin dato en el insumo para la sesión {dia_ts.date()} (último cierre: {disp[t]['ultimo_cierre']})")
        filas.append({"ticker": t, **d,
                      "ultimo_cierre_ticker": disp[t]["ultimo_cierre"],
                      "available_at_ticker": disp[t]["available_at_utc"],
                      "senal_magnitud_pp": (s.magnitud_pp if s else None),
                      "senal_banda_baja_pp": (s.banda_baja_pp if s else None),
                      "senal_banda_alta_pp": (s.banda_alta_pp if s else None)})
    completo = all(f["ultimo_cierre_ticker"] == str(dia_ts.date()) for f in filas)
    return {"dia": str(dia_ts.date()), "juego": juego, "presupuesto_usd": float(presupuesto),
            "reglas_version": cfg.get("version_reglas", "?"), "operables": operables,
            "riel_apagado": bool(dec.riel_apagado), "insumo_completo": completo,
            "sin_dato": [f["ticker"] for f in filas if f["ultimo_cierre_ticker"] != str(dia_ts.date())],
            "filas": filas}


def huella_decision(dec: dict) -> list:
    """Lo que el gate compara: (ticker, decisión, acciones, precio, señal) por fila."""
    return [(f["ticker"], f["decision"], f["acciones_regla"],
             round(f["precio_ref_usd"], 8) if f["precio_ref_usd"] is not None else None,
             round(f["senal_magnitud_pp"], 8) if f["senal_magnitud_pp"] is not None else None)
            for f in dec["filas"]]


def verificar_invariancia_decision(cierres: pd.DataFrame, dia, futuros: int = 5, cfg: dict | None = None,
                                   minimo_cortes: int = MINIMO_CORTES_GATE) -> dict:
    """La decisión de `dia` no puede cambiar según existan o no las sesiones
    posteriores. Se compara la decisión con el insumo entero contra la del
    insumo cortado en `dia` y en cada uno de los `futuros` días siguientes que
    existan. Si algo se mueve: ErrorLookAhead.

    E1 del auditor: en el ÚLTIMO día del insumo hay un solo corte y el gate
    comparaba la decisión consigo misma — vacuo justo donde se lo invocaba.
    Ahora exige `minimo_cortes` (≥ 2) y revienta si no los hay."""
    from backtest.datos import ErrorLookAhead
    cfg = cfg or U.reglas()
    con_futuro = huella_decision(decidir(cierres, dia, cfg))
    cortes = [d for d in cierres.index if d >= pd.Timestamp(dia)][:futuros + 1]
    if len(cortes) < minimo_cortes:
        raise ErrorLookAhead(
            f"gate VACUO: sólo {len(cortes)} corte(s) para {pd.Timestamp(dia).date()} (mínimo {minimo_cortes}); "
            f"comparar la decisión consigo misma no vigila nada")
    comparados = 0
    for corte in cortes:
        sin = huella_decision(decidir(cierres.loc[:corte], dia, cfg))
        if sin != con_futuro:
            raise ErrorLookAhead(f"la decisión de {pd.Timestamp(dia).date()} cambia según exista o no "
                                 f"lo posterior a {corte.date()}")
        comparados += 1
    return {"resultado": "INVARIANTE", "dia": str(pd.Timestamp(dia).date()), "cortes": comparados}


def gate_previo_al_sello(cierres: pd.DataFrame, cfg: dict | None = None) -> list:
    """Lo que corre ANTES de cada sello real: el gate sobre el penúltimo día
    (2 cortes) y sobre 6 sesiones atrás (6 cortes). El último día no se puede
    vigilar por construcción (un solo corte) y eso se declara en vez de
    fingirlo (E1)."""
    idx = cierres.index
    dias = [idx[-2]] + ([idx[-6]] if len(idx) >= 6 else [])
    return [verificar_invariancia_decision(cierres, d, futuros=5, cfg=cfg) for d in dias]


# ------------------------------------------------------------
# Sellar
# ------------------------------------------------------------
def sellar(ruta_ext: str, meta_ext: dict, ahora_utc: datetime | None = None,
           ruta_db: str = RUTA_DB, cfg: dict | None = None) -> dict:
    """Decide con el insumo (congelado + extensión) y sella una fila por
    instrumento operable. Idempotente por (fecha_insumo, ticker, juego) SÓLO
    si el insumo es el mismo (mismo sha): un segundo sello del mismo día con
    OTRO insumo queda en `divergencias_sello` y no inserta nada (E4). El
    resumen dice lo que PASÓ, no lo que habría pasado.

    No exporta nada: el export a data/backups/ lo hace `main()` sobre la base
    real, explícitamente (E5/H8)."""
    cfg = cfg or U.reglas()
    cierres = insumo(ruta_ext)
    fecha_insumo = str(cierres.index.max().date())
    ahora = ahora_utc or datetime.now(timezone.utc)
    if ahora.tzinfo is None:
        raise ValueError("ahora_utc tiene que traer zona horaria")
    ahora = ahora.astimezone(timezone.utc)
    ts_emision = ahora.isoformat()
    disp = ((meta_ext.get("disponibilidad") or {}).get("por_ticker") or {})
    avail = max((v["available_at_utc"] for v in disp.values() if v.get("available_at_utc")), default=None)
    if avail is None:
        avail = cierre_utc(fecha_insumo).isoformat()
    sesion_obj, apertura_obj = proxima_sesion_despues_de(datetime.fromisoformat(avail))
    # E2: el «día» del sello en el calendario del exchange, nunca el huso del host
    fecha_sello = dia_en_calendario_del_exchange(ahora)
    estado_dia = "sesion" if es_sesion(fecha_sello) else "sin_sesion"
    # regla maestra: available_at < timestamp_utc < apertura objetivo
    timing_ok = datetime.fromisoformat(avail) < ahora < apertura_obj
    estado_timing = "ok" if timing_ok else "roto"
    sesion_previa_a_obj = str(_cal().previous_session(pd.Timestamp(sesion_obj)).date())
    insumo_fresco = (fecha_insumo == sesion_previa_a_obj)
    dec = decidir(cierres, fecha_insumo, cfg)
    insumo_completo = bool(dec["insumo_completo"])
    if not timing_ok:
        estado = ESTADO_NO_VERIFICABLE
    elif estado_dia == "sin_sesion":
        estado = ESTADO_SIN_SESION
    elif not insumo_completo:
        estado = ESTADO_INSUMO_INCOMPLETO
    else:
        estado = ESTADO_PENDIENTE
    cuenta_para_N = int(estado == ESTADO_PENDIENTE and insumo_fresco)
    base_sha = precios.meta_congelado().get("sha256")
    reglas_sha = _sha256(U.RUTA_REGLAS)
    sellador_sha = _sha256(os.path.abspath(__file__))
    creado = datetime.now(timezone.utc).isoformat()
    con = conectar(ruta_db)
    try:
        previas = con.execute("SELECT DISTINCT insumo_ext_sha256, timestamp_utc FROM sellos_dinero "
                              "WHERE fecha_insumo = ? AND juego = ?", (fecha_insumo, dec["juego"])).fetchall()
        if previas:
            shas = {p[0] for p in previas}
            if meta_ext["sha256"] in shas:
                return {"resultado": "ya_sellada", "fecha_insumo": fecha_insumo,
                        "timestamp_utc_original": previas[0][1], "filas_insertadas": 0,
                        "insumo_ext_sha256": meta_ext["sha256"]}
            filas_prev = con.execute("SELECT ticker, decision, acciones_regla FROM sellos_dinero WHERE fecha_insumo = ? "
                                     "AND juego = ? ORDER BY ticker", (fecha_insumo, dec["juego"])).fetchall()
            ahora_por_t = {f["ticker"]: (f["decision"], f["acciones_regla"]) for f in dec["filas"]}
            distintas = sum(1 for (t, d, n) in filas_prev if ahora_por_t.get(t) != (d, n))
            con.execute("INSERT INTO divergencias_sello (fecha_insumo, timestamp_utc, sha_sellado, sha_nuevo, "
                        "decisiones_distintas, detalle, creado_en) VALUES (?,?,?,?,?,?,?)",
                        (fecha_insumo, ts_emision, sorted(shas)[0], meta_ext["sha256"], distintas,
                         f"segundo sello del {fecha_insumo} con otro insumo; {distintas} decisión(es) distinta(s); "
                         f"las filas selladas no se tocan", creado))
            con.commit()
            return {"resultado": "divergencia_registrada", "fecha_insumo": fecha_insumo, "filas_insertadas": 0,
                    "sha_sellado": sorted(shas)[0], "sha_nuevo": meta_ext["sha256"], "decisiones_distintas": distintas}
        insertadas = 0
        for f in dec["filas"]:
            cur = con.execute("""
                INSERT INTO sellos_dinero
                (fecha_sello, fecha_insumo, timestamp_utc, available_at, exchange, sesion_objetivo,
                 apertura_objetivo_utc, ticker, decision, acciones_regla, tamano_nominal, precio_ref_usd,
                 senal_magnitud_pp, senal_banda_baja_pp, senal_banda_alta_pp, senal_fuente, juego,
                 presupuesto_usd, reglas_version, motivo, ultimo_cierre_ticker, available_at_ticker,
                 insumo_ext_sha256, insumo_ext_archivo, insumo_base_sha256, reglas_sha256, sellador_sha256,
                 plataforma_version, version_sello, estado, estado_timing, estado_dia, insumo_completo,
                 cuenta_para_N, creado_en)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (fecha_sello, fecha_insumo, ts_emision, avail, EXCHANGE, sesion_obj,
                 apertura_obj.isoformat(), f["ticker"], f["decision"], f["acciones_regla"], 0,
                 f["precio_ref_usd"], f["senal_magnitud_pp"], f["senal_banda_baja_pp"], f["senal_banda_alta_pp"],
                 SENAL_FUENTE, dec["juego"], dec["presupuesto_usd"], dec["reglas_version"], f["motivo"],
                 f["ultimo_cierre_ticker"], f["available_at_ticker"],
                 meta_ext["sha256"], os.path.basename(ruta_ext), base_sha, reglas_sha, sellador_sha,
                 PLATAFORMA_VERSION, VERSION_SELLO, estado, estado_timing, estado_dia, int(insumo_completo),
                 cuenta_para_N, creado))
            insertadas += cur.rowcount
        con.commit()
    finally:
        con.close()
    return {"resultado": "sellada", "fecha_sello_ny": fecha_sello, "fecha_insumo": fecha_insumo,
            "timestamp_utc": ts_emision, "available_at": avail, "sesion_objetivo": sesion_obj,
            "apertura_objetivo_utc": apertura_obj.isoformat(),
            "estado": estado, "estado_timing": estado_timing, "estado_dia": estado_dia, "timing_ok": timing_ok,
            "insumo_fresco": insumo_fresco, "insumo_completo": insumo_completo, "sin_dato": dec["sin_dato"],
            "cuenta_para_N": cuenta_para_N, "riel_apagado": dec["riel_apagado"],
            "filas_insertadas": insertadas, "filas_decididas": len(dec["filas"]),
            "compras": sum(1 for f in dec["filas"] if f["decision"] == "compra"),
            "juego": dec["juego"], "presupuesto_usd": dec["presupuesto_usd"],
            "insumo_ext_sha256": meta_ext["sha256"], "insumo_base_sha256": base_sha,
            "reglas_sha256": reglas_sha, "sellador_sha256": sellador_sha}


def exportar_csv(ruta_db: str = RUTA_DB, ruta_csv: str | None = None) -> str:
    """Toda la tabla (y las divergencias) a CSV en data/backups/, que el job de
    backup versiona. H8: exportar desde una base que NO es la real exige decir
    a dónde, para que un test jamás pise el CSV versionado."""
    if ruta_csv is None:
        if os.path.abspath(ruta_db) != os.path.abspath(RUTA_DB):
            raise ValueError("exportar desde una base que no es la real exige ruta_csv explícita")
        ruta_csv = RUTA_BACKUP_CSV
    con = conectar(ruta_db, solo_lectura=True)
    try:
        for tabla, ruta in (("sellos_dinero", ruta_csv),
                            ("divergencias_sello", os.path.splitext(ruta_csv)[0] + "_divergencias.csv")):
            cur = con.execute(f"SELECT * FROM {tabla} ORDER BY id")
            cols = [d[0] for d in cur.description]
            filas = cur.fetchall()
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerows(filas)
    finally:
        con.close()
    return ruta_csv


def respaldar_extension(ruta_ext: str, destino: str = DIR_BACKUP_EXT) -> list:
    """E5: el sha sellado tiene que apuntar a algo que exista mañana. La
    extensión y su meta se copian a data/backups/, que `mki_backup.py`
    commitea; `dinero/datos/sello/` no lo versiona ningún job."""
    import shutil
    os.makedirs(destino, exist_ok=True)
    salidas = []
    for r in (ruta_ext, os.path.splitext(ruta_ext)[0] + ".meta.json"):
        d = os.path.join(destino, os.path.basename(r))
        shutil.copyfile(r, d)
        salidas.append(d)
    return salidas


# ------------------------------------------------------------
# Estado: lo que la API y la pantalla leen (solo lectura)
# ------------------------------------------------------------
_CLAVES_ULTIMO = ("fecha_sello", "fecha_insumo", "timestamp_utc", "available_at", "sesion_objetivo",
                  "apertura_objetivo_utc", "estado", "estado_timing", "estado_dia", "insumo_completo",
                  "cuenta_para_N", "juego", "presupuesto_usd", "insumo_ext_sha256", "insumo_ext_archivo",
                  "insumo_base_sha256", "reglas_sha256", "sellador_sha256", "plataforma_version",
                  "version_sello", "creado_en")


def estado(ruta_db: str = RUTA_DB) -> dict:
    vacio = {"filas": 0, "sesiones_selladas": 0, "sesiones_que_cuentan_para_N": 0,
             "N_objetivo": N_OBJETIVO_E0, "N_objetivo_fuente": N_OBJETIVO_FUENTE,
             "fuente_conteos": ("dinero/sello_dinero.db" if os.path.exists(ruta_db) else "aún sin base: 0 filas"),
             "ultimo": None, "filas_ultimo_sello": [],
             "divergencias_registradas": 0, "senal_fuente": SENAL_FUENTE, "estatus": "PROPUESTA"}
    if not os.path.exists(ruta_db):
        return vacio
    con = conectar(ruta_db, solo_lectura=True)
    try:
        filas = con.execute("SELECT COUNT(*) FROM sellos_dinero").fetchone()[0]
        sesiones = con.execute("SELECT COUNT(DISTINCT fecha_insumo) FROM sellos_dinero").fetchone()[0]
        cuentan = con.execute("SELECT COUNT(DISTINCT fecha_insumo) FROM sellos_dinero WHERE cuenta_para_N = 1").fetchone()[0]
        ult = con.execute(f"SELECT {', '.join(_CLAVES_ULTIMO)} FROM sellos_dinero ORDER BY id DESC LIMIT 1").fetchone()
        ultimo, detalle = None, []
        if ult:
            ultimo = dict(zip(_CLAVES_ULTIMO, ult))
            cur = con.execute("SELECT ticker, decision, acciones_regla, tamano_nominal, precio_ref_usd, senal_magnitud_pp, "
                              "senal_banda_baja_pp, senal_banda_alta_pp, motivo, ultimo_cierre_ticker, available_at_ticker "
                              "FROM sellos_dinero WHERE fecha_insumo = ? AND timestamp_utc = ? ORDER BY ticker",
                              (ultimo["fecha_insumo"], ultimo["timestamp_utc"]))
            detalle = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
        divergencias = con.execute("SELECT COUNT(*) FROM divergencias_sello").fetchone()[0]
    finally:
        con.close()
    return {**vacio, "filas": filas, "sesiones_selladas": sesiones, "sesiones_que_cuentan_para_N": cuentan,
            "ultimo": ultimo, "filas_ultimo_sello": detalle, "divergencias_registradas": divergencias}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="E0: sellado prospectivo de tamaño cero del riel de dinero")
    ap.add_argument("--sellar", action="store_true")
    ap.add_argument("--sin-red", action="store_true", help="no descarga: usa la última extensión congelada")
    ap.add_argument("--estado", action="store_true")
    a = ap.parse_args(argv)
    if a.estado or not a.sellar:
        print(json.dumps(estado(), indent=1, ensure_ascii=False, default=str))
        return 0
    if a.sin_red:
        u = ultima_extension()
        if u is None:
            print("no hay extensión congelada y --sin-red impide descargar")
            return 2
        ruta, meta = u
    else:
        base_meta = precios.meta_congelado()
        ext = descargar_extension(base_meta["tickers"])
        ruta, meta = congelar_extension(ext, base_meta["hasta"])
    cierres = insumo(ruta)
    gates = gate_previo_al_sello(cierres)
    print("gate de la decisión (penúltimo día y 6 sesiones atrás; el último no se puede vigilar por construcción):", gates)
    if (meta.get("solape_con_congelado") or {}).get("reajuste_detectado"):
        print("AVISO: reajuste retroactivo detectado entre la extensión y el congelado:",
              meta["solape_con_congelado"].get("tickers_con_reajuste"))
    r = sellar(ruta, meta)
    print(json.dumps(r, indent=1, ensure_ascii=False, default=str))
    if r.get("resultado") == "sellada":
        exportar_csv(RUTA_DB)
        respaldar_extension(ruta)
        print("export:", RUTA_BACKUP_CSV, "| extensión respaldada en", DIR_BACKUP_EXT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
