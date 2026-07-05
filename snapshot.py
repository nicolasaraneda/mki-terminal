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
from datetime import date, datetime, timezone

import pandas as pd

import calendarios
import motor
import noticias
import senales
from universo import EXCHANGE_POR_TICKER
from version import MODELO_VERSION

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
DIR_BACKUPS = os.path.join(DIRECTORIO, "data", "backups")

TABLAS_BACKUP_SENALES = ["snapshots", "senales_ticker", "verificacion_apertura",
                         "verificacion_puntaje", "divergencias"]
TABLAS_BACKUP_NOTICIAS = ["titulares", "analisis", "resumen_dia"]


def ejecutar_snapshot(origen: str, ventana_betas: int = motor.VENTANA_BETAS_DEFAULT) -> dict:
    """Toma el snapshot del día si no existe. Sella cada predicción con:
    timestamp_utc (ahora), exchange, sesion_objetivo (la próxima sesión de esa
    bolsa cuya apertura es posterior a la emisión) y available_at (el cierre
    UTC de la última sesión del SOX usada — cuándo era conocible el insumo).
    Devuelve un dict con lo que hizo."""
    if senales.ya_existe_snapshot_hoy():
        return {"snapshot": False, "motivo": "ya existe snapshot de hoy"}

    hoy = date.today()
    ahora_utc = datetime.now(timezone.utc)
    ts_emision = ahora_utc.isoformat()

    metricas = motor.puntaje_v0_al(hoy)
    if metricas.empty:
        return {"snapshot": False, "motivo": "sin datos de mercado"}
    regimen = motor.regimen_al(hoy)
    roca_chip = motor.roca_chip_al(hoy)
    divergencias = motor.divergencias_al(hoy)
    pred = motor.prediccion_apertura_al(hoy, ventana=ventana_betas)

    # available_at: cierre UTC de la sesión del SOX cuyo movimiento alimenta
    # la predicción — el instante desde el cual esa información era conocible.
    available_at = ts_emision
    predicciones = []
    if not pred.empty:
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
        available_at=available_at,
    )
    return {"snapshot": guardado, "predicciones": len(predicciones),
            "regimen": regimen["etiqueta"] if regimen else None,
            "roca_chip": roca_chip.get("valor") if roca_chip else None,
            "divergencias_activas": sum(1 for d in divergencias if d["activa"])}


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
          f"(origen={args.origen}, modelo={MODELO_VERSION})")

    resultado = ejecutar_snapshot(args.origen)
    print(f"  snapshot: {resultado}")

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
