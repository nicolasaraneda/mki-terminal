"""Q1 (addendum 16-2): recorro TODAS las ramas de `sellar` con la guarda R1
puesta y mido si pisa alguna legitima. Lo decisivo: otro juego con el MISMO
sha (insumo identico) tiene que seguir sellando, porque ahi `persistido` es
True y la cita apunta al canonico que existe."""
import os, sqlite3, sys, tempfile
from datetime import datetime, timedelta, timezone
import pandas as pd
sys.path.insert(0, os.environ["WT"])
from dinero import precios, universo_dinero as U
from dinero import sello_dinero as S
UTC=timezone.utc; BH="2026-09-04"
SES=("2026-09-08","2026-09-09","2026-09-10","2026-09-11","2026-09-14")
T_OK=datetime(2026,9,15,3,30,tzinfo=UTC)          # 23:30 NY: timing ok
T_ROTO=datetime(2026,9,14,17,43,1,tzinfo=UTC)     # 13:43 NY: timing roto
base=precios.cargar_congelado()
cfg_a=U.reglas(); cfg_b=dict(cfg_a, juego_activo="agresivo")
def ext(f, ses=SES):
    u=base.iloc[-1]; e=pd.DataFrame({pd.Timestamp(s):u*1.01 for s in ses}).T
    e.iloc[-1]=u.values*f; e.index.name="Date"; return e
def nuevo():
    d=tempfile.mkdtemp(); S.DIR_EXT=os.path.join(d,"s"); S.RUTA_DB=os.path.join(d,"s.db"); return S.RUTA_DB
def disparo(db,f,t,cfg=None,ses=SES):
    r,m=S.congelar_extension(ext(f,ses),BH,ahora_utc=t,ruta_db=db)
    try: return m, S.sellar(r,m,ahora_utc=t,ruta_db=db,cfg=cfg)
    finally:
        if not m.get("persistido",True) and os.path.exists(r): os.remove(r)
def cuenta(db,t):
    c=sqlite3.connect(f"file:{db}?mode=ro",uri=True)
    try: return c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    except sqlite3.OperationalError: return 0
    finally: c.close()
def integridad(db,tabla,dir_ext):
    c=sqlite3.connect(f"file:{db}?mode=ro",uri=True)
    try: filas=c.execute(f"SELECT DISTINCT insumo_ext_archivo, insumo_ext_sha256 FROM {tabla}").fetchall()
    except sqlite3.OperationalError: return "s/t"
    finally: c.close()
    if not filas: return "sin filas"
    mal=[a for a,sh in filas if not os.path.exists(os.path.join(dir_ext,a)) or S._sha256(os.path.join(dir_ext,a))!=sh]
    return "OK" if not mal else f"ROTA {mal}"
print(f"{'escenario':54s} {'resultado':34s} {'sel':4s}{'int':4s}{'div':4s} integridad")
casos=[]
# 1 normal
db=nuevo(); m,o=disparo(db,1.02,T_OK); casos.append(("1 sello normal (timing ok, fecha limpia)",o,db,m,S.DIR_EXT))
# 2 intento normal
db=nuevo(); m,o=disparo(db,0.98,T_ROTO); casos.append(("2 intento (timing roto, fecha limpia)",o,db,m,S.DIR_EXT))
# 3 mismo juego mismo sha
db=nuevo(); disparo(db,1.02,T_OK); m,o=disparo(db,1.02,T_OK+timedelta(minutes=1)); casos.append(("3 mismo juego, MISMO sha",o,db,m,S.DIR_EXT))
# 4 mismo juego otro sha
db=nuevo(); disparo(db,1.02,T_OK); m,o=disparo(db,1.03,T_OK+timedelta(minutes=1)); casos.append(("4 mismo juego, OTRO sha",o,db,m,S.DIR_EXT))
# 5 intento previo mismo sha
db=nuevo(); disparo(db,0.98,T_ROTO); m,o=disparo(db,0.98,T_ROTO+timedelta(minutes=1)); casos.append(("5 intento previo, MISMO sha",o,db,m,S.DIR_EXT))
# 6 intento previo otro sha
db=nuevo(); disparo(db,0.98,T_ROTO); m,o=disparo(db,0.97,T_ROTO+timedelta(minutes=1)); casos.append(("6 intento previo, OTRO sha",o,db,m,S.DIR_EXT))
# 7 timing roto con sello previo de OTRO juego
db=nuevo(); disparo(db,1.02,T_OK); m,o=disparo(db,0.98,T_ROTO+timedelta(days=1),cfg=cfg_b); casos.append(("7 timing roto, sello previo de OTRO juego",o,db,m,S.DIR_EXT))
# 8 evidencia canonica con timing roto (--sin-red tarde)
db=nuevo(); r,mm=S.congelar_extension(ext(1.02),BH,ahora_utc=T_OK,ruta_db=db); o=S.sellar(r,mm,ahora_utc=T_OK+timedelta(days=2),ruta_db=db); casos.append(("8 canonico con timing roto (--sin-red tarde)",o,db,mm,S.DIR_EXT))
# 9 F3: otro juego, OTRO sha  -> la guarda tiene que disparar
db=nuevo(); disparo(db,1.02,T_OK); m,o=disparo(db,1.03,T_OK+timedelta(minutes=1),cfg=cfg_b); casos.append(("9 OTRO juego, OTRO sha (F3)",o,db,m,S.DIR_EXT))
# 10 LEGITIMA: otro juego, MISMO sha -> tiene que SELLAR
db=nuevo(); disparo(db,1.02,T_OK); m,o=disparo(db,1.02,T_OK+timedelta(minutes=1),cfg=cfg_b); casos.append(("10 OTRO juego, MISMO sha (legitima)",o,db,m,S.DIR_EXT))
for n,o,db,m,de in casos:
    print(f"{n:54s} {o['resultado']:34s} {cuenta(db,'sellos_dinero'):<4d}{cuenta(db,'intentos_no_verificables'):<4d}{cuenta(db,'divergencias_sello'):<4d} "
          f"sellos={integridad(db,'sellos_dinero',de)} intentos={integridad(db,'intentos_no_verificables',de)} persistido={m.get('persistido',True)}")
