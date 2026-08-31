#!/usr/bin/env python3
# ============================================================
# ensayo_replica.py — ensayo general de la réplica, en entorno aislado
# (Frente D, tercera corrida autónoma).
#
# QUÉ HACE: simula el escenario COMPLETO de una réplica funcionando sin
# tocar nada vivo. Construye DOS fuentes de datos sintéticas — una que hace
# de "titular" (DataFrames, como si vinieran de `git show
# origin/main:data/backups/*.csv`) y una que hace de "réplica" (una base
# sqlite real, propia de este ensayo, nunca `senales.db`) — y hace pasar
# una cadena de varios días por `comparar_sombra.comparar_fecha` +
# `replica.registrar_comparacion`, exactamente el camino que recorrería el
# mecanismo real el día que se active.
#
# QUÉ NO HACE (a propósito, ver límites duros del frente):
#   - No lee ni escribe `senales.db` ni `noticias.db`. La base "réplica" es
#     un archivo sqlite temporal, creado y borrado en cada corrida.
#   - No escribe en `data/divergencias_replica.db` (la ruta real de
#     producción de `replica.py`) — usa una ruta temporal propia.
#   - No decide "quién gana": igual que `replica.py`, esto es un ensayo de
#     REGISTRO, no de resolución.
#   - No activa nada: no toca `modo.py`, `.env`, `systemd/`, `motor.py`,
#     `senales.py`, `snapshot.py`.
#
# POR QUÉ ES UN SCRIPT Y NO COMANDOS SUELTOS: DECISIONES.md §45 documenta
# un análisis completo que vivió en comandos sueltos de una sesión de
# trabajo y se perdió al cerrarse — solo se pudo auditar porque unos
# archivos intermedios sobrevivieron por casualidad. Este ensayo es
# ejecutable, versionado y re-corrible: `python scripts/ensayo_replica.py`.
#
# La salida se imprime Y se guarda en data/replica_ensayo/reporte_ensayo.md
# (versionado, mismo criterio que data/sombra/*.md) para poder citarla
# textualmente en docs/REPLICA.md §6 en vez de parafrasearla.
# ============================================================

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import comparar_sombra as cs  # noqa: E402
import replica  # noqa: E402

RUTA_REPORTE = os.path.join(RAIZ, "data", "replica_ensayo", "reporte_ensayo.md")

# ------------------------------------------------------------
# Fixtures sintéticas — mismo espíritu que tests/test_replica.py, pero acá
# se materializan en una base sqlite real para el lado "réplica" (en vez de
# monkeypatchear comparar_sombra.leer_tabla_local con un DataFrame en
# memoria), porque el ensayo quiere probar la cadena completa: sqlite real
# -> pandas -> comparador -> registrador -> sqlite real de divergencias.
# ------------------------------------------------------------

def snap_titular(fecha: str, **cambios) -> dict:
    base = {
        "fecha": fecha,
        "creado_en": f"{fecha}T22:00:00.100000+00:00",
        "timestamp_utc": f"{fecha}T22:00:00.100000+00:00",
        "origen": "programado",
        "regimen": "Alcista · vol alta",
        "roca_chip": 50.0,
        "modelo_version": "4.6.0",
        "feature_version": "4.6.0",
        "universo_version": "4.6.0",
        "ventana_betas": 120.0,
        "descarga_ok": 28.0,
        "descarga_total": 28.0,
        "descarga_caidos": 0.0,
        "plataforma_version": "5.0.3",
        "sox_usado_pct": -1.5,
        "sox_fecha": fecha,
    }
    base.update(cambios)
    return base


def snap_replica(fecha: str, **cambios) -> dict:
    base = snap_titular(fecha)
    base["creado_en"] = f"{fecha}T22:00:05.700000+00:00"
    base["timestamp_utc"] = f"{fecha}T22:00:05.700000+00:00"
    base.update(cambios)
    return base


def ticker_titular(fecha: str, ticker: str = "2330.TW", **cambios) -> dict:
    base = {
        "fecha": fecha,
        "ticker": ticker,
        "puntaje_v0": 0.57,
        "sentimiento_ia": 0.42,
        "puntaje_ia": 0.61,
        "apertura_estimada_pct": -1.03,
        "confianza_r2": 0.28,
        "timestamp_utc": f"{fecha}T22:00:00.100000+00:00",
        "exchange": "XTAI",
        "sesion_objetivo": fecha,
        "available_at": f"{fecha}T20:00:00+00:00",
        "estado": "pendiente",
        "intervalo80_pp": 2.66,
        "n_muestra": 120.0,
        "modelo_version": "4.6.0",
        "beta": 0.38,
    }
    base.update(cambios)
    return base


def ticker_replica(fecha: str, ticker: str = "2330.TW", **cambios) -> dict:
    base = ticker_titular(fecha, ticker)
    base["timestamp_utc"] = f"{fecha}T22:00:05.700000+00:00"
    base.update(cambios)
    return base


# ------------------------------------------------------------
# Los siete días de la cadena — cada uno ensaya una rama distinta.
# ------------------------------------------------------------
D_PARIDAD = "2026-09-01"
D_DIV_COMPUTO = "2026-09-02"
D_DIV_INSUMOS = "2026-09-03"
D_DIV_SELLO_AUSENTE = "2026-09-04"
D_DIV_CONJUNTO = "2026-09-05"
D_NO_COMPUTABLE = "2026-09-08"   # el titular no selló, pero SÍ publicó 09-09
D_PARIDAD_ANCLA = "2026-09-09"   # ancla que desambigua 09-08 (fecha posterior)
D_PENDIENTE = "2026-09-10"       # el titular no selló nada, ni posterior


def construir_datos():
    """Devuelve (snaps_titular_df, tickers_titular_df, snaps_replica,
    tickers_replica) — los dos primeros como los entregaría
    `leer_csv_titular` (DataFrames con TODAS las fechas), los dos últimos
    como listas de dict para volcar a la base sqlite de la réplica."""
    snaps_t, tick_t = [], []
    snaps_r, tick_r = [], []

    # 1) PARIDAD: mismos insumos, mismo cómputo.
    snaps_t.append(snap_titular(D_PARIDAD))
    snaps_r.append(snap_replica(D_PARIDAD))
    tick_t.append(ticker_titular(D_PARIDAD))
    tick_r.append(ticker_replica(D_PARIDAD))

    # 2) DIVERGENCIA de cómputo: mismos insumos declarados (sox_usado_pct,
    #    sox_fecha), beta distinto -> según replica._clasificar, "computo".
    snaps_t.append(snap_titular(D_DIV_COMPUTO))
    snaps_r.append(snap_replica(D_DIV_COMPUTO))
    tick_t.append(ticker_titular(D_DIV_COMPUTO, beta=0.38))
    tick_r.append(ticker_replica(D_DIV_COMPUTO, beta=0.41))

    # 3) DIVERGENCIA de insumos: sox_fecha distinto (cada máquina alcanzó a
    #    leer el cierre del SOX de una sesión distinta) -> "insumos".
    snaps_t.append(snap_titular(D_DIV_INSUMOS, sox_fecha="2026-09-02"))
    snaps_r.append(snap_replica(D_DIV_INSUMOS, sox_fecha="2026-09-03"))
    tick_t.append(ticker_titular(D_DIV_INSUMOS))
    tick_r.append(ticker_replica(D_DIV_INSUMOS))

    # 4) DIVERGENCIA de existencia, sub-caso "sello ausente": el titular
    #    selló, la réplica NO -- no se agrega nada a snaps_r/tick_r para
    #    esta fecha.
    snaps_t.append(snap_titular(D_DIV_SELLO_AUSENTE))
    tick_t.append(ticker_titular(D_DIV_SELLO_AUSENTE))

    # 5) DIVERGENCIA de existencia, sub-caso "conjunto de tickers distinto":
    #    las dos sellaron el snapshot IDÉNTICO, pero el conjunto de
    #    tickers sellados difiere.
    snaps_t.append(snap_titular(D_DIV_CONJUNTO))
    snaps_r.append(snap_replica(D_DIV_CONJUNTO))
    tick_t.append(ticker_titular(D_DIV_CONJUNTO, ticker="2330.TW"))
    tick_t.append(ticker_titular(D_DIV_CONJUNTO, ticker="005930.KS"))
    tick_r.append(ticker_replica(D_DIV_CONJUNTO, ticker="2330.TW"))

    # 6) DIA_NO_COMPUTABLE: el titular NO selló 09-08 (y tampoco la
    #    réplica -- ninguna corrió esa noche, ej. feriado no calendarizado).
    #    No se agrega nada a ningún lado para esta fecha; la desambiguación
    #    depende de que el titular SÍ haya publicado 09-09 (más abajo).

    # 6-ancla) PARIDAD, y de paso la fecha posterior que vuelve DEFINITIVA
    #    la ausencia de 09-08.
    snaps_t.append(snap_titular(D_PARIDAD_ANCLA))
    snaps_r.append(snap_replica(D_PARIDAD_ANCLA))
    tick_t.append(ticker_titular(D_PARIDAD_ANCLA))
    tick_r.append(ticker_replica(D_PARIDAD_ANCLA))

    # 7) PENDIENTE_PUBLICACION: la réplica YA selló 09-10 -- corrió su
    #    noche normalmente -- pero el titular todavía no aparece en
    #    origin/main para esa fecha NI para ninguna posterior (su push
    #    manual, tras las 20:30, todavía no llegó). Ambiguo por diseño.
    snaps_r.append(snap_replica(D_PENDIENTE))
    tick_r.append(ticker_replica(D_PENDIENTE))

    return (pd.DataFrame(snaps_t), pd.DataFrame(tick_t), snaps_r, tick_r)


def crear_base_replica(ruta: str, snaps_r: list[dict], tick_r: list[dict]) -> None:
    conn = sqlite3.connect(ruta)
    try:
        pd.DataFrame(snaps_r).to_sql("snapshots", conn, index=False, if_exists="replace")
        pd.DataFrame(tick_r).to_sql("senales_ticker", conn, index=False, if_exists="replace")
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------
# Los tres casos del enunciado -> qué se espera de cada fecha.
# ------------------------------------------------------------
CASOS = [
    ("Caso 1 — coinciden", D_PARIDAD, cs.VEREDICTO_PARIDAD, 0, None),
    ("Caso 2 — difieren (cómputo)", D_DIV_COMPUTO, cs.VEREDICTO_DIVERGENCIA, 1, replica.CLASE_COMPUTO),
    ("Caso 2 — difieren (insumos)", D_DIV_INSUMOS, cs.VEREDICTO_DIVERGENCIA, 1, replica.CLASE_INSUMOS),
    ("Caso 2 — difieren (existencia, sello ausente)", D_DIV_SELLO_AUSENTE,
     cs.VEREDICTO_DIVERGENCIA, 1, replica.CLASE_EXISTENCIA),
    ("Caso 2 — difieren (existencia, conjunto de tickers)", D_DIV_CONJUNTO,
     cs.VEREDICTO_DIVERGENCIA, None, replica.CLASE_EXISTENCIA),  # nº de filas variable
    ("Caso 3 — no selló (DIA_NO_COMPUTABLE)", D_NO_COMPUTABLE, cs.VEREDICTO_NO_COMPUTABLE, 0, None),
    ("(ancla) PARIDAD que desambigua el caso anterior", D_PARIDAD_ANCLA, cs.VEREDICTO_PARIDAD, 0, None),
    ("Caso 3 — no selló (PENDIENTE_PUBLICACION)", D_PENDIENTE, cs.VEREDICTO_PENDIENTE, 0, None),
]


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="ensayo_replica_")
    ruta_db_replica = os.path.join(tmp, "replica_sintetica.db")
    ruta_db_divergencias = os.path.join(tmp, "divergencias_replica_ensayo.db")

    snaps_titular_df, tickers_titular_df, snaps_r, tick_r = construir_datos()
    crear_base_replica(ruta_db_replica, snaps_r, tick_r)

    # Redirige leer_tabla_local hacia la base sqlite sintética de la
    # réplica en vez de senales.db real -- ES el único punto de acoplamiento
    # con datos "vivos" en comparar_sombra.py y se reemplaza por completo.
    original_leer_tabla_local = cs.leer_tabla_local

    def leer_local_sintetico(tabla: str, fecha: str) -> pd.DataFrame:
        conn = sqlite3.connect(f"file:{ruta_db_replica}?mode=ro", uri=True)
        try:
            try:
                return pd.read_sql_query(
                    f"SELECT * FROM {tabla} WHERE fecha = ?", conn, params=(fecha,))
            except pd.errors.DatabaseError:
                # tabla vacía / no creada porque construir_datos() no le
                # dio ninguna fila a la réplica (ningún día de este ensayo
                # cae en ese extremo, pero se cubre por completitud).
                return pd.DataFrame(columns=["fecha"])
        finally:
            conn.close()

    lineas: list[str] = []

    def out(s: str = "") -> None:
        print(s)
        lineas.append(s)

    hallazgos_del_ensayo: list[str] = []  # cosas que NO salieron como se creía

    cs.leer_tabla_local = leer_local_sintetico
    try:
        out("# Ensayo general de la réplica — Frente D")
        out("")
        out(f"Generado: {datetime.now(timezone.utc).isoformat()}")
        out(f"Base sintética 'réplica' (sqlite real, temporal): {ruta_db_replica}")
        out("Base sintética 'titular' (DataFrames, como si vinieran de "
            "`git show origin/main:...`): en memoria, construida por "
            "`construir_datos()`.")
        out(f"Base de divergencias del ensayo (temporal, NUNCA la de "
            f"producción): {ruta_db_divergencias}")
        out("")
        out("Ninguna de estas rutas es `senales.db`, `noticias.db` ni "
            "`data/divergencias_replica.db` — se crean en un directorio "
            "temporal y se borran al final de esta corrida.")
        out("")

        for nombre, fecha, veredicto_esperado, n_esperado, clase_esperada in CASOS:
            out(f"## {nombre} — {fecha}")
            out("")
            res = cs.comparar_fecha(fecha, snaps_titular_df, tickers_titular_df)
            n_registradas = replica.registrar_comparacion(res, ruta_db=ruta_db_divergencias)
            filas = replica.leer_divergencias(ruta_db_divergencias, fecha=fecha)

            out(f"- Veredicto obtenido: **{res['veredicto']}**  "
                f"(esperado: {veredicto_esperado})")
            out(f"- Motivo: {res['motivo']}")
            out(f"- Hallazgos nivel 1/2 de `comparar_fecha`: {len(res['hallazgos'])}")
            out(f"- Filas insertadas por `registrar_comparacion`: {n_registradas}")
            if filas:
                for f in filas:
                    out(f"    - campo={f['campo']} clase={f['clase']} "
                        f"titular={f['valor_titular']!r} sombra={f['valor_sombra']!r} "
                        f"resuelto_como={f['resuelto_como']!r}")

            # --- autochequeo: no interrumpe el ensayo si falla, lo anota ---
            if res["veredicto"] != veredicto_esperado:
                hallazgo = (f"HALLAZGO en {fecha} ({nombre}): se esperaba "
                            f"veredicto {veredicto_esperado}, se obtuvo "
                            f"{res['veredicto']}.")
                hallazgos_del_ensayo.append(hallazgo)
                out(f"- **{hallazgo}**")
            if n_esperado is not None and n_registradas != n_esperado:
                hallazgo = (f"HALLAZGO en {fecha} ({nombre}): se esperaban "
                            f"{n_esperado} fila(s) registradas, se obtuvieron "
                            f"{n_registradas}.")
                hallazgos_del_ensayo.append(hallazgo)
                out(f"- **{hallazgo}**")
            if clase_esperada is not None:
                clases_obtenidas = {f["clase"] for f in filas}
                if clases_obtenidas != {clase_esperada}:
                    hallazgo = (f"HALLAZGO en {fecha} ({nombre}): se esperaba "
                                f"clase {{{clase_esperada}}} en todas las filas, "
                                f"se obtuvo {clases_obtenidas}.")
                    hallazgos_del_ensayo.append(hallazgo)
                    out(f"- **{hallazgo}**")
            if veredicto_esperado in (cs.VEREDICTO_NO_COMPUTABLE, cs.VEREDICTO_PENDIENTE,
                                       cs.VEREDICTO_PARIDAD) and filas:
                hallazgo = (f"HALLAZGO en {fecha} ({nombre}): un veredicto sin "
                            f"divergencia real ({res['veredicto']}) dejó filas "
                            f"registradas ({len(filas)}) -- esto sería ruido, "
                            f"exactamente lo que REPLICA.md §3 pide evitar.")
                hallazgos_del_ensayo.append(hallazgo)
                out(f"- **{hallazgo}**")

            out("")

        out("## Resumen")
        out("")
        todas = replica.leer_divergencias(ruta_db_divergencias)
        out(f"- Fechas ensayadas: {len(CASOS)}")
        out(f"- Filas totales en `divergencias_replica` (base temporal del "
            f"ensayo): {len(todas)}")
        out(f"- `resuelto_como` NULL en todas las filas: "
            f"{all(f['resuelto_como'] is None for f in todas)}")
        out("")
        if hallazgos_del_ensayo:
            out(f"### HALLAZGOS ({len(hallazgos_del_ensayo)}) — algo no salió "
                "como se creía, documentado en vez de arreglado en silencio")
            out("")
            for h in hallazgos_del_ensayo:
                out(f"- {h}")
        else:
            out("### Sin hallazgos")
            out("")
            out("Los tres casos se comportaron exactamente como predice "
                "`docs/REPLICA.md`: paridad sin ruido, divergencia con "
                "procedencia completa y clase correcta, ausencia legítima "
                "sin filas falsas.")
        out("")

    finally:
        cs.leer_tabla_local = original_leer_tabla_local
        shutil.rmtree(tmp, ignore_errors=True)

    os.makedirs(os.path.dirname(RUTA_REPORTE), exist_ok=True)
    with open(RUTA_REPORTE, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lineas) + "\n")
    print(f"\nReporte guardado en: {os.path.relpath(RUTA_REPORTE, RAIZ)}")

    return 1 if hallazgos_del_ensayo else 0


if __name__ == "__main__":
    sys.exit(main())
