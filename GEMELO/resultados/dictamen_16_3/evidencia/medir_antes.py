"""Medición «antes» de las seis cifras publicadas sobre la base real en mode=ro,
replicando el SQL EXACTO de senales.py (HEAD ad4b829), más: cuántas filas saca
la exclusión de conocibilidad en cada una, cuántas sacaría la deduplicación,
filas con gap NULL, e igualdad v.apertura_estimada_pct == s.apertura_estimada_pct."""
import os, sqlite3, sys, json
from datetime import datetime, timezone
import pandas as pd
RAIZ = sys.argv[1]
sys.path.insert(0, RAIZ)
from version import MODELO_VERSION
MV = MODELO_VERSION
con = sqlite3.connect(f"file:{os.path.join(RAIZ,'senales.db')}?mode=ro", uri=True)
print("instante UTC:", datetime.now(timezone.utc).isoformat(), "| date('now') sqlite:", con.execute("select date('now')").fetchone()[0], "| modelo:", MV)
MIN = 5
def q(sql, p=()):
    return con.execute(sql, p).fetchall()
def inv(ts, av):
    if ts is None or av is None or not str(av) or not str(ts): return False
    t = datetime.fromisoformat(str(ts)); a = datetime.fromisoformat(str(av))
    if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
    if a.tzinfo is None: a = a.replace(tzinfo=timezone.utc)
    return a > t

# --- 1. metricas_apertura(30)
sql = """SELECT v.acierto_gap, v.error_gap_pp, v.acierto_direccion, v.error_pp, v.fecha_senal, v.ticker, s.timestamp_utc, s.available_at, v.gap_pct, v.id
         FROM verificacion_apertura v LEFT JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker
         WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL AND v.fecha_senal >= date('now', ?)"""
def metricas(filas):
    n = len(filas)
    if n < MIN: return {"suficiente": False, "n": n}
    return {"suficiente": True, "n": n,
            "gap": {"pct_aciertos": round(100*sum(f[0] for f in filas)/n,1), "mae_pp": round(sum(f[1] for f in filas)/n,2)},
            "retorno_sesion": {"pct_aciertos": round(100*sum(f[2] for f in filas)/n,1), "mae_pp": round(sum(f[3] for f in filas)/n,2)}}
filas = q(sql, (MV, "-30 days"))
filas_sin = [f for f in filas if not inv(f[6], f[7])]
print("\n=== metricas_apertura(30) ===")
print("ANTES :", json.dumps(metricas(filas)))
print("DESPUES:", json.dumps(metricas(filas_sin)))
print("excluidas:", [(f[4], f[5], "gap", f[8], "acierto_gap", f[0], "acierto_dir", f[2], "err_gap", f[1], "err", f[3]) for f in filas if inv(f[6], f[7])])
# ventana del lunes 12-oct (date('now') = 2026-10-12 a las 18:25 Chile = 21:25Z)
filas_lun = q(sql.replace("date('now', ?)", "date('2026-10-12', ?)"), (MV, "-30 days"))
filas_lun_sin = [f for f in filas_lun if not inv(f[6], f[7])]
print("ventana del lunes (fecha_senal >= 2026-09-12), hoy sin filas nuevas: ANTES", json.dumps(metricas(filas_lun)), "DESPUES", json.dumps(metricas(filas_lun_sin)))
print("filas con fecha_senal = 2026-09-11 (salen de la ventana el lunes):", len([f for f in filas if f[4]=="2026-09-11"]))

# --- 2. calibracion_intervalos
sql2 = """SELECT v.gap_pct, s.apertura_estimada_pct, s.intervalo80_pp, s.timestamp_utc, s.available_at, v.fecha_senal, v.ticker, v.apertura_estimada_pct
          FROM verificacion_apertura v JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker
          WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL AND s.intervalo80_pp IS NOT NULL"""
def calib(filas):
    n = len(filas)
    if n < MIN: return {"suficiente": False, "n": n}
    dentro = sum(1 for f in filas if abs(f[0]-f[1]) <= f[2])
    return {"suficiente": True, "n": n, "cobertura_pct": round(100*dentro/n,1)}
f2 = q(sql2, (MV,)); f2s = [f for f in f2 if not inv(f[3], f[4])]
print("\n=== calibracion_intervalos ===")
print("ANTES :", json.dumps(calib(f2))); print("DESPUES:", json.dumps(calib(f2s)))
print("excluidas (fecha,ticker,dentro):", [(f[5], f[6], abs(f[0]-f[1]) <= f[2]) for f in f2 if inv(f[3], f[4])])
print("v.apertura_estimada_pct != s.apertura_estimada_pct:", sum(1 for f in f2 if (f[7] is None) != (f[1] is None) or (f[7] is not None and f[1] is not None and abs(f[7]-f[1])>1e-12)), "de", len(f2))

# --- 3. evolucion
df3 = pd.read_sql_query("""SELECT v.fecha_senal AS Fecha, v.acierto_gap, v.acierto_direccion, s.timestamp_utc, s.available_at
    FROM verificacion_apertura v LEFT JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker
    WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL""", con, params=(MV,))
ev_antes = pd.read_sql_query("""SELECT fecha_senal AS Fecha, AVG(acierto_gap)*100 AS "% Aciertos gap", AVG(acierto_direccion)*100 AS "% Aciertos sesión", COUNT(*) AS N
    FROM verificacion_apertura WHERE legacy=0 AND modelo_version=? AND gap_pct IS NOT NULL GROUP BY fecha_senal ORDER BY fecha_senal""", con, params=(MV,))
m = [inv(t,a) for t,a in zip(df3.timestamp_utc, df3.available_at)]
d3 = df3[[not x for x in m]]
ev_desp = d3.groupby("Fecha").agg(**{"% Aciertos gap": ("acierto_gap", lambda s: s.mean()*100), "% Aciertos sesión": ("acierto_direccion", lambda s: s.mean()*100), "N": ("acierto_gap","size")}).reset_index()
print("\n=== evolucion_aciertos_apertura ===")
print("ANTES : filas(fechas)=", len(ev_antes), "N total=", int(ev_antes.N.sum()))
print("DESPUES: filas(fechas)=", len(ev_desp), "N total=", int(ev_desp.N.sum()))
dif = ev_antes.merge(ev_desp, on="Fecha", how="outer", suffixes=("_a","_d"), indicator=True)
print("fechas que cambian o desaparecen:"); print(dif[(dif._merge!="both") | (dif["N_a"]!=dif["N_d"])].to_string())

# --- 4. ultimas (sin filtro gap NOT NULL)
u = pd.read_sql_query("""SELECT v.id, v.fecha_senal AS Fecha, v.ticker AS Ticker, v.gap_pct, s.timestamp_utc, s.available_at
    FROM verificacion_apertura v LEFT JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker
    WHERE v.legacy=0 AND v.modelo_version=? ORDER BY v.fecha_senal DESC""", con, params=(MV,))
print("\n=== ultimas_predicciones_apertura ===")
print("total filas sin LIMIT:", len(u), "| gap_pct NULL:", int(u.gap_pct.isna().sum()))
mi = [inv(t,a) for t,a in zip(u.timestamp_utc, u.available_at)]
print("invertidas en el total:", sum(mi))
for lim in (50, 100):
    top = u.head(lim); print(f"LIMIT {lim}: ANTES fechas {top.Fecha.min()}..{top.Fecha.max()}, invertidas dentro: {sum(inv(t,a) for t,a in zip(top.timestamp_utc, top.available_at))}")
    us = u[[not x for x in mi]].head(lim); print(f"LIMIT {lim}: DESPUES fechas {us.Fecha.min()}..{us.Fecha.max()}")
# orden observado dentro de una fecha: ids
print("orden observado ids en la última fecha:", u[u.Fecha==u.Fecha.max()].id.tolist())
u2 = pd.read_sql_query("""SELECT v.id FROM verificacion_apertura v WHERE v.legacy=0 AND v.modelo_version=? ORDER BY v.fecha_senal DESC LIMIT 100""", con, params=(MV,))
u3 = pd.read_sql_query("""SELECT v.id FROM verificacion_apertura v WHERE v.legacy=0 AND v.modelo_version=? ORDER BY v.fecha_senal DESC, v.id LIMIT 100""", con, params=(MV,))
u4 = pd.read_sql_query("""SELECT v.id FROM verificacion_apertura v WHERE v.legacy=0 AND v.modelo_version=? ORDER BY v.fecha_senal DESC, v.id DESC LIMIT 100""", con, params=(MV,))
print("orden observado == (fecha DESC, id ASC):", u2.id.tolist()==u3.id.tolist(), "| == (fecha DESC, id DESC):", u2.id.tolist()==u4.id.tolist())

# --- 5. verificaciones_detalle
vd = pd.read_sql_query("""SELECT v.id, v.fecha_senal, v.ticker, v.acierto_gap, s.exchange, snap.regimen, s.timestamp_utc, s.available_at
    FROM verificacion_apertura v LEFT JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker LEFT JOIN snapshots snap ON snap.fecha=v.fecha_senal
    WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL ORDER BY v.fecha_senal""", con, params=(MV,))
mv = [inv(t,a) for t,a in zip(vd.timestamp_utc, vd.available_at)]
print("\n=== verificaciones_detalle ===")
print("ANTES n=", len(vd), "aciertos gap=", int(vd.acierto_gap.sum()), "| DESPUES n=", len(vd)-sum(mv), "aciertos gap=", int(vd[[not x for x in mv]].acierto_gap.sum()))
print("por exchange ANTES:", vd.groupby("exchange").size().to_dict(), "| DESPUES:", vd[[not x for x in mv]].groupby("exchange").size().to_dict())
print("por regimen ANTES:", vd.groupby(vd.regimen.fillna("sin")).size().to_dict())
vd_ids_obs = pd.read_sql_query("""SELECT v.id FROM verificacion_apertura v WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL ORDER BY v.fecha_senal""", con, params=(MV,))
vd_ids_2 = pd.read_sql_query("""SELECT v.id FROM verificacion_apertura v WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL ORDER BY v.fecha_senal, v.id""", con, params=(MV,))
print("orden observado detalle == (fecha, id):", vd_ids_obs.id.tolist()==vd_ids_2.id.tolist())
m_ids_obs = pd.read_sql_query("""SELECT v.id FROM verificacion_apertura v WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL AND v.fecha_senal >= date('now','-30 days')""", con, params=(MV,))
m_ids_2 = pd.read_sql_query("""SELECT v.id FROM verificacion_apertura v WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL AND v.fecha_senal >= date('now','-30 days') ORDER BY v.id""", con, params=(MV,))
print("orden observado metricas (sin ORDER BY) == id:", m_ids_obs.id.tolist()==m_ids_2.id.tolist())

# --- 6. analisis_puntaje_ia(90)
pz = pd.read_sql_query("""SELECT v.puntaje_ia AS puntaje, v.retorno_5d_pct AS retorno, s.timestamp_utc, s.available_at, v.fecha_senal, v.ticker
    FROM verificacion_puntaje v JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker
    WHERE v.fecha_senal >= date('now', ?) AND s.timestamp_utc IS NOT NULL AND s.modelo_version = ?""", con, params=("-90 days", MV))
def apia(df):
    n = len(df)
    if n < MIN: return {"suficiente": False, "n": n}
    df = df.sort_values("puntaje"); corte = max(1, n//3)
    corr = df["puntaje"].corr(df["retorno"]) if n >= 3 else None
    return {"suficiente": True, "n": n, "retorno_tercio_alto": round(df.iloc[-corte:]["retorno"].mean(),2), "retorno_tercio_bajo": round(df.iloc[:corte]["retorno"].mean(),2), "correlacion": round(corr,2) if corr is not None else None}
mp = [inv(t,a) for t,a in zip(pz.timestamp_utc, pz.available_at)]
print("\n=== analisis_puntaje_ia(90) ===")
print("ANTES :", json.dumps(apia(pz[["puntaje","retorno"]]))); print("DESPUES:", json.dumps(apia(pz[[not x for x in mp]][["puntaje","retorno"]]))); print("invertidas dentro:", sum(mp))
print("igualdad av==ts dentro:", sum(1 for t,a in zip(pz.timestamp_utc, pz.available_at) if a is not None and t is not None and a==t), "| av NULL:", int(pz.available_at.isna().sum()))

# --- 7. dedup: cuántos pares (ticker, sesion_objetivo) con >1 fila en el conjunto vivo (gap not null)
dd = pd.read_sql_query("""SELECT v.fecha_senal, v.ticker, s.sesion_objetivo, s.exchange, s.available_at, s.timestamp_utc
    FROM verificacion_apertura v LEFT JOIN senales_ticker s ON s.fecha=v.fecha_senal AND s.ticker=v.ticker
    WHERE v.legacy=0 AND v.modelo_version=? AND v.gap_pct IS NOT NULL""", con, params=(MV,))
g = dd.groupby(["ticker","sesion_objetivo"]).size()
print("\n=== deduplicación (informativo) ===")
print("pares (ticker,sesion_objetivo) con >1 fila:", int((g>1).sum()), "| filas en esos pares:", int(g[g>1].sum()))
print("fechas de esos pares:", sorted(dd.merge(g[g>1].rename("k").reset_index(), on=["ticker","sesion_objetivo"]).fecha_senal.unique().tolist()))
dd30 = dd[dd.fecha_senal >= (pd.Timestamp.utcnow().normalize() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")]
g30 = dd30.groupby(["ticker","sesion_objetivo"]).size()
print("en la ventana de 30 días: pares con >1 fila:", int((g30>1).sum()))
# --- 8. totales por estado y filas invertidas
print("\n=== totales ===")
print("verificacion_apertura total:", q("select count(*) from verificacion_apertura")[0][0], "| no legacy mv:", q("select count(*) from verificacion_apertura where legacy=0 and modelo_version=?", (MV,))[0][0])
print("verificacion_puntaje total:", q("select count(*) from verificacion_puntaje")[0][0])
print("senales_ticker invertidas (texto):", q("select count(*), min(fecha), max(fecha) from senales_ticker where available_at > timestamp_utc")[0])
print("max fecha_senal verificacion_apertura:", q("select max(fecha_senal), max(verificado_en) from verificacion_apertura")[0])
print("snapshots max fecha:", q("select max(fecha) from snapshots")[0])
con.close()
