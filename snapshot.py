# ============================================================
# Snapshot programado (Etapa 4.6) — el historial no depende de abrir
# el dashboard.
#
# Script independiente (SIN Streamlit) que:
#   1) Toma el snapshot diario completo (señales, régimen, divergencias,
#      Roca→Chip, predicciones del anticipador) usando motor.py — la misma
#      fuente de verdad que el dashboard. Idempotente: si ya existe el
#      snapshot del día, no duplica.
#   2) Corre el verificador de outcomes (todas las predicciones cuyas
#      sesiones objetivo ya cerraron).
#   3) Exporta las tablas clave de senales.db y noticias.db a CSVs en
#      data/backups/ (sobrescribe el export del día).
#
# Uso:
#   python snapshot.py                 → origen "programado" (launchd)
#   python snapshot.py --origen manual → origen "manual"
#
# El dashboard también lo importa para su fallback (origen "dashboard").
# ============================================================

import argparse
import os
import sqlite3
import sys
import time
from datetime import date, datetime, timezone

import pandas as pd

import calendarios
import motor
import noticias
import senales
from universo import EXCHANGE_POR_TICKER, UNIVERSO
from version import MODELO_VERSION, PLATAFORMA_VERSION

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
DIR_BACKUPS = os.path.join(DIRECTORIO, "data", "backups")

TABLAS_BACKUP_SENALES = ["snapshots", "senales_ticker", "verificacion_apertura",
                         "verificacion_puntaje", "divergencias"]
TABLAS_BACKUP_NOTICIAS = ["titulares", "analisis", "resumen_dia"]

# Resiliencia de descarga (Etapa 4.7.3): si la fuente no entrega datos
# ("sin datos de mercado" — la semana del 06-jul Yahoo falló 2 días con el
# Mac encendido), el camino launchd reintenta con backoff: 3 intentos en
# ~60 min. Las esperas superan el TTL de la caché del motor (15 min), así
# cada reintento descarga de verdad. Solo aplica en main(); el fallback del
# dashboard llama ejecutar_snapshot() directo y jamás espera.
ESPERAS_REINTENTO_SEG = (20 * 60, 40 * 60)

# Reintento PARCIAL (Etapa 5.0 WS2.3 — excepción quirúrgica #2): si el lote
# bajó INCOMPLETO (algunos tickers caídos, el patrón DarkWake de la auditoría
# 13–24 jul), se reintenta la descarga hasta 2 veces con espera corta ANTES
# de sellar, limpiando la caché del motor para que el reintento descargue de
# verdad. Nota de diseño (ver DECISIONES.md): el reintento re-descarga el
# lote completo — "solo los caídos" exigiría inyectar columnas en la caché
# interna del motor, y motor.py es intocable; el efecto neto es el mismo
# (los caídos obtienen otra oportunidad) sin cirugía en el motor.
ESPERAS_REINTENTO_PARCIAL_SEG = (60, 120)


def salud_descarga(fecha: date) -> dict:
    """Salud de la descarga del día: qué tickers esperados (universo + ^SOX)
    entregaron datos recientes (≤7 días hasta `fecha`).

    SOLO OBSERVA los mismos DataFrames que el motor ya descargó (misma caché,
    mismo punto único _datos_crudos): no crea una vía de datos nueva ni toca
    ninguna señal. Excepción quirúrgica #1 de la constitución 5.0."""
    tickers_universo = tuple(UNIVERSO.keys())
    frame_universo = motor._datos_crudos(tickers_universo)
    frame_sox = motor._datos_crudos(("^SOX",))
    limite = pd.Timestamp(fecha) - pd.Timedelta(days=7)
    ok, caidos = [], []
    for t in list(tickers_universo) + ["^SOX"]:
        df = frame_sox if t == "^SOX" else frame_universo
        serie = df[t].dropna() if (not df.empty and t in df.columns) else pd.Series(dtype=float)
        (ok if (not serie.empty and serie.index.max() >= limite) else caidos).append(t)
    return {"ok_n": len(ok), "total": len(ok) + len(caidos),
            "caidos": caidos, "completa": not caidos}


def ejecutar_snapshot(origen: str, ventana_betas: int = motor.VENTANA_BETAS_DEFAULT,
                      reintentos_parciales: int = 0) -> dict:
    """Toma el snapshot del día si no existe. Sella cada predicción con:
    timestamp_utc (ahora), exchange, sesion_objetivo (la próxima sesión de esa
    bolsa cuya apertura es posterior a la emisión) y available_at (el cierre
    UTC de la última sesión del SOX usada — cuándo era conocible el insumo).
    Con `reintentos_parciales` > 0 (solo el camino launchd; el fallback del
    dashboard jamás espera), una descarga incompleta se reintenta antes de
    sellar. Devuelve un dict con lo que hizo."""
    if senales.ya_existe_snapshot_hoy():
        return {"snapshot": False, "motivo": "ya existe snapshot de hoy"}

    hoy = date.today()

    # WS2.3: reintento parcial ANTES de computar/sellar nada.
    salud = salud_descarga(hoy)
    for intento in range(reintentos_parciales):
        if salud["completa"]:
            break
        espera = ESPERAS_REINTENTO_PARCIAL_SEG[
            min(intento, len(ESPERAS_REINTENTO_PARCIAL_SEG) - 1)]
        print(f"  descarga parcial ({salud['ok_n']}/{salud['total']}, caídos: "
              f"{', '.join(salud['caidos'])}) — reintento en {espera}s", flush=True)
        time.sleep(espera)
        motor._cache.clear()  # sin esto el reintento leería la caché a medias
        salud = salud_descarga(hoy)

    ahora_utc = datetime.now(timezone.utc)
    ts_emision = ahora_utc.isoformat()

    metricas = motor.puntaje_v0_al(hoy)
    if metricas.empty:
        return {"snapshot": False, "motivo": "sin datos de mercado",
                "descarga": f"{salud['ok_n']}/{salud['total']}"}
    regimen = motor.regimen_al(hoy)
    roca_chip = motor.roca_chip_al(hoy)
    divergencias = motor.divergencias_al(hoy)
    pred = motor.prediccion_apertura_al(hoy, ventana=ventana_betas)

    # available_at: cierre UTC de la sesión del SOX cuyo movimiento alimenta
    # la predicción — el instante desde el cual esa información era conocible.
    available_at = ts_emision
    predicciones = []
    sox_usado_pct, sox_fecha = None, None
    if not pred.empty:
        sox_usado_pct = float(pred.iloc[0]["SOX usado %"])
        sox_fecha = pred.iloc[0]["SOX fecha"]
        if sox_fecha:
            try:
                available_at = calendarios.cierre_utc("XNYS", sox_fecha).isoformat()
            except Exception:
                pass
        for _, fila in pred.iterrows():
            t = fila["Ticker"]
            exchange = EXCHANGE_POR_TICKER.get(t, "XNYS")
            try:
                sesion_obj, _, _ = calendarios.proxima_sesion_despues_de(exchange, ahora_utc)
            except Exception:
                continue
            predicciones.append({
                "Ticker": t,
                "Apertura estimada %": float(fila["Apertura estimada %"]),
                "R2": float(fila["R2"]),
                "Intervalo80 pp": float(fila["Intervalo80 pp"]),
                "N muestra": int(fila["N muestra"]),
                # WS3: la beta viaja al sello — el reporte solo dice lo sellado
                "Beta": float(fila["Beta de contagio"]),
                "exchange": exchange,
                "sesion_objetivo": sesion_obj,
            })

    guardado = senales.guardar_snapshot(
        fecha=hoy.isoformat(), timestamp_utc=ts_emision, origen=origen,
        metricas_df=metricas, sentimientos=noticias.sentimiento_promedio_por_ticker(),
        predicciones=predicciones,
        regimen=regimen["etiqueta"] if regimen else None,
        roca_chip=roca_chip.get("valor") if roca_chip else None,
        divergencias=divergencias, ventana_betas=ventana_betas,
        available_at=available_at, salud_descarga=salud,
        sox_usado_pct=sox_usado_pct, sox_fecha=sox_fecha,
    )
    return {"snapshot": guardado, "predicciones": len(predicciones),
            "regimen": regimen["etiqueta"] if regimen else None,
            "roca_chip": roca_chip.get("valor") if roca_chip else None,
            "divergencias_activas": sum(1 for d in divergencias if d["activa"]),
            "descarga": f"{salud['ok_n']}/{salud['total']}",
            "caidos": salud["caidos"]}


def respaldar_a_csv() -> list:
    """Exporta las tablas clave a data/backups/*.csv (sobrescribe el export del
    día — un respaldo plano y versionable en git por si SQLite se corrompe)."""
    os.makedirs(DIR_BACKUPS, exist_ok=True)
    exportados = []
    fuentes = [(senales.DB_PATH, TABLAS_BACKUP_SENALES, "senales"),
               (noticias.DB_PATH, TABLAS_BACKUP_NOTICIAS, "noticias")]
    for db_path, tablas, prefijo in fuentes:
        if not os.path.exists(db_path):
            continue
        conn = sqlite3.connect(db_path)
        for tabla in tablas:
            try:
                df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
            except Exception:
                continue
            destino = os.path.join(DIR_BACKUPS, f"{prefijo}_{tabla}.csv")
            df.to_csv(destino, index=False)
            exportados.append(os.path.basename(destino))
        conn.close()
    return exportados


def main() -> int:
    parser = argparse.ArgumentParser(description="Snapshot diario MKI Terminal")
    parser.add_argument("--origen", default="programado",
                        choices=["programado", "manual"])
    args = parser.parse_args()

    print(f"[{datetime.now(timezone.utc).isoformat()}] snapshot.py "
          f"(origen={args.origen}, modelo={MODELO_VERSION}, "
          f"plataforma={PLATAFORMA_VERSION})")

    resultado = ejecutar_snapshot(args.origen, reintentos_parciales=2)
    print(f"  snapshot: {resultado}")

    # Reintento SOLO ante fallo TOTAL de descarga: cualquier otro resultado
    # (sellado, "ya existe") sigue de largo. Un sello logrado en el
    # reintento lleva su timestamp real de emisión — el verificador de
    # timing decide después, como siempre (la regla maestra no se toca).
    for espera in ESPERAS_REINTENTO_SEG:
        if resultado.get("motivo") != "sin datos de mercado":
            break
        print(f"  la fuente no entregó datos — reintento en {espera // 60} min",
              flush=True)
        time.sleep(espera)
        print(f"[{datetime.now(timezone.utc).isoformat()}] reintento de descarga",
              flush=True)
        resultado = ejecutar_snapshot(args.origen, reintentos_parciales=2)
        print(f"  snapshot: {resultado}", flush=True)

    if resultado.get("caidos"):
        print(f"  ⚠ descarga degradada {resultado['descarga']} — caídos: "
              f"{', '.join(resultado['caidos'])} (sellado igual, salud visible)")

    verif_apertura, verif_puntaje = senales.verificar_pendientes()
    print(f"  verificador apertura: {verif_apertura}")
    print(f"  verificador puntaje: {verif_puntaje} verificadas")

    exportados = respaldar_a_csv()
    print(f"  respaldos CSV: {len(exportados)} tablas → data/backups/")

    salud = motor.salud_datos_al(date.today())
    if salud["ok"]:
        print(f"  salud de datos: OK ({salud['tickers_revisados']} tickers)")
    else:
        print(f"  salud de datos: {len(salud['problemas'])} problema(s):")
        for p in salud["problemas"]:
            print(f"    - {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
