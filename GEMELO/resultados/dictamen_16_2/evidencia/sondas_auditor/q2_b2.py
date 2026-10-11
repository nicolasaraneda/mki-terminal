"""Q2 (addendum 16-2): B2. (i) leer NO crea la tabla sobre una base E0.2
fabricada, verificado por sqlite_master y por mtime; (ii) ningun contador de
sellos se contamina con un intento; (iii) frases prohibidas."""
import json, os, sqlite3, sys, tempfile
from datetime import datetime, timezone
import pandas as pd
sys.path.insert(0, os.environ["WT"])
from dinero import precios
from dinero import sello_dinero as S
UTC=timezone.utc; BH="2026-09-04"
SES=("2026-09-08","2026-09-09","2026-09-10","2026-09-11","2026-09-14")
base=precios.cargar_congelado()
def ext(f):
    u=base.iloc[-1]; e=pd.DataFrame({pd.Timestamp(s):u*1.01 for s in SES}).T
    e.iloc[-1]=u.values*f; e.index.name="Date"; return e
def tablas(db):
    c=sqlite3.connect(f"file:{db}?mode=ro",uri=True)
    try: return {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally: c.close()

print("=== (i) una base E0.2 fabricada: estado() y la API no le crean la tabla ===")
d=tempfile.mkdtemp(); db=os.path.join(d,"vieja.db")
con=sqlite3.connect(db); con.executescript(S._ddl_filas("sellos_dinero")+S._DDL_DIVERGENCIAS); con.commit(); con.close()
antes=tablas(db); mt0=os.path.getmtime(db); sha0=S._sha256(db)
print("  tablas antes:", sorted(antes))
e=S.estado(db)
print("  estado():", {k:e[k] for k in ("filas","sesiones_selladas","intentos_no_verificables","ultimo_intento","ultimo")})
from fastapi.testclient import TestClient
from api.main import app
import api.main as AM
real=S.estado; S.estado=lambda ruta_db=db: real(ruta_db)
r=TestClient(app).get("/api/dinero/sellos"); j=r.json()
S.estado=real
print("  HTTP:", r.status_code, "| E0 claves:", sorted(j["datos"]["E0"]))
despues=tablas(db)
print("  tablas despues:", sorted(despues), "| iguales:", antes==despues)
print("  base intacta: mtime", os.path.getmtime(db)==mt0, "| sha", S._sha256(db)==sha0)

print()
print("=== (ii) con SOLO un intento: ningun contador de sellos se mueve ===")
d2=tempfile.mkdtemp(); S.DIR_EXT=os.path.join(d2,"s"); db2=os.path.join(d2,"s.db")
r1,m1=S.congelar_extension(ext(0.98),BH,ahora_utc=datetime(2026,9,14,17,43,1,tzinfo=UTC),ruta_db=db2)
o=S.sellar(r1,m1,ahora_utc=datetime(2026,9,14,17,43,1,tzinfo=UTC),ruta_db=db2)
e2=S.estado(db2)
print("  resultado:", o["resultado"], "| filas en intentos:", o["filas_insertadas"])
for k in ("filas","sesiones_selladas","sesiones_que_cuentan_para_N","divergencias_registradas","intentos_no_verificables"):
    print(f"    {k:32s} = {e2[k]}")
print("    ultimo (sello)                   =", e2["ultimo"])
print("    ultimo_intento.fecha_insumo      =", (e2["ultimo_intento"] or {}).get("fecha_insumo"),
      "| estado", (e2["ultimo_intento"] or {}).get("estado"), "| cuenta_para_N", (e2["ultimo_intento"] or {}).get("cuenta_para_N"))
print("    claves de ultimo_intento == _CLAVES_ULTIMO:", set(e2["ultimo_intento"])==set(S._CLAVES_ULTIMO))
S.estado=lambda ruta_db=db2: real(ruta_db)
j2=TestClient(app).get("/api/dinero/sellos").json()["datos"]
S.estado=real
print("  API con un intento: E0.estado=", j2["E0"]["estado"], "| sesiones_selladas", j2["E0"]["sesiones_selladas"],
      "| filas", j2["E0"]["filas"], "| ultimo_sello", j2["ultimo_sello"], "| decisiones_proxima_apertura", len(j2["decisiones_proxima_apertura"]),
      "| intentos", j2["E0"]["intentos_no_verificables"])

print()
print("=== (iii) frases prohibidas en el payload entero (con un intento adentro) ===")
txt=json.dumps(j2,ensure_ascii=False,default=str).lower()
BAN=("confianza","rentable","retorno esperado","ganancia esperada","sostiene casi toda","probable","seguro","garantiz","exito","promete","ventaja")
print("  encontradas:", [p for p in BAN if p in txt] or "NINGUNA")
print("  nota_intentos (texto literal):"); print("   ", AM.NOTA_INTENTOS_E0)
