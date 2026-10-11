"""P3-P8 (auditor 16-2), todo en tmp."""
import glob, inspect, json, os, re, sqlite3, sys, tempfile
from datetime import datetime, timezone
import pandas as pd
sys.path.insert(0, os.environ["WT"])
from dinero import precios
from dinero import sello_dinero as S
UTC = timezone.utc; BASE_HASTA = "2026-09-04"
SES5 = ("2026-09-08","2026-09-09","2026-09-10","2026-09-11","2026-09-14")
base = precios.cargar_congelado()
def ext(ses, f, nan=()):
    u = base.iloc[-1]; e = pd.DataFrame({pd.Timestamp(s): u*1.01 for s in ses}).T
    e.iloc[-1] = u.values*f
    for t in nan: e.loc[pd.Timestamp(ses[-1]), t] = float("nan")
    e.index.name = "Date"; return e
def nuevo():
    d = tempfile.mkdtemp(); S.DIR_EXT = os.path.join(d,"s"); S.RUTA_DB = os.path.join(d,"s.db")
    S.DIR_BACKUP_EXT = os.path.join(d,"b"); S.RUTA_BACKUP_CSV = os.path.join(d,"c.csv"); return S.RUTA_DB
def q(db, sql, *a):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try: return con.execute(sql, a).fetchall()
    except sqlite3.OperationalError as e: return [("AUSENTE", str(e))]
    finally: con.close()

print("=== P3: discordancia INVERSA de relojes (congelar roto, sellar ok) ===")
db = nuevo()
# congelar justo ANTES del cierre nominal (20:00Z): avail no es < ahora -> roto
t_cong = datetime(2026, 9, 14, 19, 59, 55, tzinfo=UTC)
t_sell = datetime(2026, 9, 14, 20, 0, 5, tzinfo=UTC)   # 5 s despues del cierre: el reloj del sello diria ok
r, m = S.congelar_extension(ext(SES5, 0.98), BASE_HASTA, ahora_utc=t_cong)
print("congelar:", os.path.basename(r), "cupo_canonico" , m.get("cupo_canonico"))
tim = S.evaluar_timing((m.get("disponibilidad") or {}).get("por_ticker") or {}, "2026-09-14", t_sell)
print("evaluar_timing con el reloj del sello:", tim["timing_ok"], "| avail", tim["avail"], "| apertura", tim["apertura_obj"].isoformat())
o = S.sellar(r, m, ahora_utc=t_sell, ruta_db=db)
print("sellar ->", o["resultado"], "| estado_timing", o["estado_timing"], "| tabla", o.get("tabla"))
f = q(db, "SELECT DISTINCT available_at, timestamp_utc, apertura_objetivo_utc, estado, estado_timing FROM intentos_no_verificables")
print("la fila dice:", f)
if f and f[0][0] != "AUSENTE":
    a, ts, ap, _, _ = f[0]
    print("  regla maestra leida de la PROPIA fila:", a < ts < ap, "<- si es True, la fila se contradice")

print()
print("=== P4: ninguna ruta escribe en sellos_dinero con timing roto (runtime, 6 escenarios) ===")
casos = [("intradia sin nada previo", SES5, 0.98, datetime(2026,9,14,17,43,1,tzinfo=UTC), None),
         ("intradia con intento previo mismo sha", SES5, 0.98, datetime(2026,9,14,17,43,1,tzinfo=UTC), "mismo"),
         ("intradia con intento previo otro sha", SES5, 0.98, datetime(2026,9,14,17,43,1,tzinfo=UTC), "otro"),
         ("insumo atrasado una sesion", SES5[:4], 1.02, datetime(2026,9,14,17,43,1,tzinfo=UTC), None),
         ("insumo atrasado, fecha ya sellada", SES5[:4], 1.02, datetime(2026,9,14,17,43,1,tzinfo=UTC), "sellada"),
         ("discordancia inversa", SES5, 0.98, datetime(2026,9,14,20,0,5,tzinfo=UTC), "roto_al_congelar")]
for nombre, ses, fac, t, previo in casos:
    db = nuevo()
    t_c = datetime(2026,9,14,19,59,55,tzinfo=UTC) if previo == "roto_al_congelar" else t
    if previo == "sellada":
        rr, mm = S.congelar_extension(ext(ses, 1.5), BASE_HASTA, ahora_utc=datetime(2026,9,12,3,30,tzinfo=UTC))
        S.sellar(rr, mm, ahora_utc=datetime(2026,9,12,3,30,tzinfo=UTC), ruta_db=db)
    r, m = S.congelar_extension(ext(ses, fac), BASE_HASTA, ahora_utc=t_c)
    if previo in ("mismo", "otro"):
        S.sellar(r, m, ahora_utc=t, ruta_db=db)
        if previo == "otro":
            r, m = S.congelar_extension(ext(ses, 0.97), BASE_HASTA, ahora_utc=t_c)
    o = S.sellar(r, m, ahora_utc=t, ruta_db=db)
    rotas = q(db, "SELECT COUNT(*) FROM sellos_dinero WHERE estado_timing='roto' OR estado='no_verificable_timing'")
    canon = [os.path.basename(x) for x in glob.glob(os.path.join(S.DIR_EXT, "ext_*.csv")) if S.es_extension_sellable(x)]
    print(f"  {nombre:42s} -> {o['resultado']:28s} rotas_en_principal={rotas[0][0]} canonicos={canon}")

print()
print("=== P5: feriado de XNYS entre semana y sabado con insumo atrasado ===")
for nombre, ses, t in [("jueves feriado 26-nov, cierre del 25 (media sesion)", ("2026-11-23","2026-11-24","2026-11-25"), datetime(2026,11,27,4,30,tzinfo=UTC)),
                       ("sabado, cierre del viernes completo", SES5[:4], datetime(2026,9,12,14,0,tzinfo=UTC)),
                       ("sabado, fuente atrasada una sesion (jueves)", SES5[:3], datetime(2026,9,12,14,0,tzinfo=UTC))]:
    db = nuevo()
    try:
        r, m = S.congelar_extension(ext(ses, 1.02), BASE_HASTA if ses[0].startswith("2026-09") else "2026-11-20", ahora_utc=t)
        o = S.sellar(r, m, ahora_utc=t, ruta_db=db)
        print(f"  {nombre}\n     -> {o['resultado']} | fecha_insumo {o.get('fecha_insumo')} | timing_ok {o.get('timing_ok')} | estado {o.get('estado')} | estado_dia {o.get('estado_dia')} | sesion_obj {o.get('sesion_objetivo')} | N {o.get('cuenta_para_N')} | tabla {o.get('tabla')} | archivo {os.path.basename(r)}")
    except Exception as e:
        print(f"  {nombre} -> EXCEPCION {type(e).__name__}: {e}")

print()
print("=== P6: --sin-red sobre un canonico viejo nunca sellado, y sobre un .no_verificable ===")
db = nuevo()
r, m = S.congelar_extension(ext(SES5, 1.02), BASE_HASTA, ahora_utc=datetime(2026,9,15,3,30,tzinfo=UTC))
print("  canonico en disco:", os.path.basename(r), "| ultima_extension ve:", os.path.basename(S.ultima_extension()[0]))
t_tarde = datetime(2026,9,16,17,0,tzinfo=UTC)   # dos dias despues: la apertura del 15 ya paso
o = S.sellar(r, m, ahora_utc=t_tarde, ruta_db=db)
print("  sellar tarde sobre el canonico ->", o["resultado"], "| filas", o.get("filas_insertadas"), "| rotas", q(db,"SELECT COUNT(*) FROM sellos_dinero")[0][0], "| divergencias", q(db,"SELECT COUNT(*) FROM divergencias_sello")[0][0])
db2 = nuevo()
r2, m2 = S.congelar_extension(ext(SES5, 0.98), BASE_HASTA, ahora_utc=datetime(2026,9,14,17,43,1,tzinfo=UTC))
print("  nv en disco:", sorted(os.listdir(S.DIR_EXT)), "| ultima_extension:", S.ultima_extension())

print()
print("=== P7: paridad de columnas sobre una base creada ANTES de E0.3 ===")
d = tempfile.mkdtemp(); db3 = os.path.join(d, "vieja.db")
con = sqlite3.connect(db3)
ddl = S._ddl_filas("sellos_dinero").replace("            insumo_completo INTEGER,            -- E3: 1 si todos los operables tienen cierre en fecha_insumo\n", "")
con.executescript(ddl); con.commit(); con.close()
S.RUTA_DB = db3
con = sqlite3.connect(db3); S.init_db(con)
cs = [r[1] for r in con.execute("PRAGMA table_info(sellos_dinero)")]
ci = [r[1] for r in con.execute("PRAGMA table_info(intentos_no_verificables)")]
con.close()
print(f"  simulada una base vieja a la que le falta una columna: sellos={len(cs)} intentos={len(ci)}")
print("  init_db la agrego?", "SI" if len(cs) == len(ci) else f"NO -> divergen: {set(ci)-set(cs)}")

print()
print("=== P8: invariancia a truncar el futuro en el instante que decide tabla y nombre ===")
db4 = nuevo()
t = datetime(2026,9,14,17,43,1,tzinfo=UTC)
largo = ext(SES5, 0.98)
futuro = ext(SES5 + ("2026-09-15","2026-09-16"), 0.98)
futuro.loc[pd.Timestamp("2026-09-14")] = largo.loc[pd.Timestamp("2026-09-14")]
for nombre, e in (("insumo truncado en la fecha", largo), ("insumo CON sesiones posteriores", futuro)):
    db = nuevo()
    r, m = S.congelar_extension(e, BASE_HASTA, ahora_utc=t)
    tim = S.evaluar_timing((m.get("disponibilidad") or {}).get("por_ticker") or {}, str(e.index.max().date()), t)
    print(f"  {nombre:36s} -> nombre {os.path.basename(r):36s} fecha {e.index.max().date()} timing_ok {tim['timing_ok']} avail {tim['avail']}")
