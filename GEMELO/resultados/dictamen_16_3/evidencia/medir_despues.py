"""«Después» sobre la base real: las seis cifras por la fuente nueva (código del
worktree, RUTA_SENALES = base real, mode=ro) contra las viejas de senales.py
leídas también en mode=ro (réplica SQL de medir_antes). Más el efecto que
tendría la deduplicación firmada sobre las cifras vivas (para la tarjeta)."""
import json, os, sqlite3, sys
from datetime import datetime, timezone
WT, REAL = sys.argv[1], sys.argv[2]
sys.path.insert(0, WT)
import pandas as pd
from backtest import linea_base as lb
lb.RUTA_SENALES = os.path.join(REAL, "senales.db")
print("instante UTC:", datetime.now(timezone.utc).isoformat(), "| lb desde", lb.__file__)
con = sqlite3.connect(f"file:{lb.RUTA_SENALES}?mode=ro", uri=True)
MV = lb.MODELO_VERSION
def inv(ts, av):
    return lb.sin_conocibilidad(ts, av)
# ---- nuevas
m = lb.metricas_apertura(dias=30); print("\nmetricas_apertura(30) NUEVA:", json.dumps(m))
c = lb.calibracion_intervalos(); print("calibracion NUEVA:", json.dumps(c))
ev = lb.evolucion_aciertos_apertura(); print("evolucion NUEVA: fechas", len(ev), "N total", int(ev["N"].sum()), "| columnas", ev.columns.tolist(), "| dtypes", [str(t) for t in ev.dtypes])
u50 = lb.ultimas_predicciones_apertura(limite=50); u100 = lb.ultimas_predicciones_apertura(limite=100)
print("ultimas(50) NUEVA:", len(u50), u50["Fecha"].min(), "..", u50["Fecha"].max(), "| ultimas(100):", len(u100), u100["Fecha"].min(), "..", u100["Fecha"].max(), "| columnas", u100.columns.tolist())
vd = lb.verificaciones_detalle(); print("detalle NUEVA: n", len(vd), "aciertos gap", int(vd["acierto_gap"].sum()), "| por exchange", vd.groupby("exchange").size().to_dict(), "| columnas", vd.columns.tolist())
a = lb.analisis_puntaje_ia(dias=90); print("puntaje NUEVA:", json.dumps({k: v for k, v in a.items() if k != "datos"}), "| datos columnas", a["datos"].columns.tolist())
# ---- orden de ultimas: ids observados por la consulta vieja (fecha DESC, LIMIT 100) vs nueva
viejo_ids = [r[0] for r in con.execute("SELECT v.id FROM verificacion_apertura v WHERE v.legacy=0 AND v.modelo_version=? ORDER BY v.fecha_senal DESC LIMIT 100", (MV,))]
viejo_sin_inv = [r for r in con.execute("""SELECT v.id, v.fecha_senal, v.ticker, s.timestamp_utc, s.available_at FROM verificacion_apertura v LEFT JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker WHERE v.legacy=0 AND v.modelo_version=? ORDER BY v.fecha_senal DESC""", (MV,))]
viejo_sin_inv = [r for r in viejo_sin_inv if not inv(r[3], r[4])][:100]
nuevo_pares = list(zip(u100["Fecha"], u100["Ticker"]))
print("ultimas(100): orden nuevo == orden viejo sin invertidas:", nuevo_pares == [(r[1], r[2]) for r in viejo_sin_inv])
# ---- detalle: orden
viejo_det = [(r[0], r[1]) for r in con.execute("""SELECT v.fecha_senal, v.ticker, s.timestamp_utc, s.available_at FROM verificacion_apertura v LEFT JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL ORDER BY v.fecha_senal""", (MV,)) if not inv(r[2], r[3])]
print("detalle: orden nuevo == orden viejo sin invertidas:", list(zip(vd["fecha_senal"], vd["ticker"])) == viejo_det)
# ---- las viejas, replicadas en mode=ro (como medir_antes), para la tabla
def metricas_vieja(dias):
    filas = con.execute("""SELECT acierto_gap, error_gap_pp, acierto_direccion, error_pp FROM verificacion_apertura WHERE legacy = 0 AND modelo_version = ? AND gap_pct IS NOT NULL AND fecha_senal >= date('now', ?)""", (MV, f"-{dias} days")).fetchall()
    n = len(filas)
    return {"suficiente": True, "n": n, "gap": {"pct_aciertos": round(100*sum(f[0] for f in filas)/n,1), "mae_pp": round(sum(f[1] for f in filas)/n,2)}, "retorno_sesion": {"pct_aciertos": round(100*sum(f[2] for f in filas)/n,1), "mae_pp": round(sum(f[3] for f in filas)/n,2)}}
print("\nmetricas VIEJA:", json.dumps(metricas_vieja(30)))
# ---- efecto de la deduplicación sobre las cifras vivas (tarjeta)
arb = lb.cargar()            # dedup=True (árbitro)
arb_sin = lb.cargar(dedup=False)
retiradas = set(zip(arb_sin["fecha"], arb_sin["ticker"])) - set(zip(arb["fecha"], arb["ticker"]))
print("\n=== deduplicación firmada aplicada a las cifras vivas (informativo, tarjeta) ===")
print("filas que la regla retira en toda la historia:", len(retiradas), "| fechas:", sorted({f for f, _ in retiradas}))
vivas = lb.cargar_vivas()
mask = [(f, t) not in retiradas for f, t in zip(vivas["fecha_senal"], vivas["ticker"])]
vd_dedup = vivas[mask]
print("calibracion n hoy", c["n"], "-> con dedup", int(vd_dedup["intervalo80_pp"].notna().sum()))
print("detalle n hoy", len(vd), "-> con dedup", len(vd_dedup))
v30 = lb.cargar_vivas(dias=30); m30 = [(f, t) not in retiradas for f, t in zip(v30["fecha_senal"], v30["ticker"])]
print("metricas(30) n hoy", m["n"], "-> con dedup", int(sum(m30)))
d_dedup = vd_dedup
n = len(d_dedup); print("detalle acierto gap % hoy", round(100*vd["acierto_gap"].mean(),1), "-> con dedup", round(100*d_dedup["acierto_gap"].mean(),1))
# ---- predicción para el lunes 12-oct: ventana desde 2026-09-12, sin filas nuevas
filas = con.execute("""SELECT v.acierto_gap, v.error_gap_pp, v.acierto_direccion, v.error_pp, s.timestamp_utc, s.available_at, v.fecha_senal FROM verificacion_apertura v LEFT JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL AND v.fecha_senal >= '2026-09-12' ORDER BY v.fecha_senal, v.ticker""", (MV,)).fetchall()
fl = [f for f in filas if not inv(f[4], f[5])]
n = len(fl)
print("\nlunes 12-oct, ventana >= 2026-09-12, SIN las verificaciones nuevas del lunes: n", n, "gap", round(100*sum(f[0] for f in fl)/n,1), "mae", round(sum(f[1] for f in fl)/n,2), "sesion", round(100*sum(f[2] for f in fl)/n,1), round(sum(f[3] for f in fl)/n,2))
pend = con.execute("SELECT fecha, ticker, sesion_objetivo, exchange FROM senales_ticker WHERE estado='pendiente' ORDER BY fecha, ticker").fetchall()
print("pendientes hoy (candidatas a verificarse el lunes 18:15):", len(pend), pend[:12])
print("fechas de señal pendientes:", sorted({p[0] for p in pend}))
con.close()
