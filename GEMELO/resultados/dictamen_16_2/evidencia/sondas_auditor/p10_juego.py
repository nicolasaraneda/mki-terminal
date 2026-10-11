"""P10: `previas` filtra por juego, `sello_previo` no. Si `juego_activo` cambia
entre dos disparos de la misma fecha con OTRO insumo, congelar manda el insumo
a un temporal (no conserva) y sellar inserta igual, citando un archivo que
main() borra. Se mide en E0.3 y en E0.2."""
import copy, inspect, os, sqlite3, sys, tempfile
from datetime import datetime, timezone
import pandas as pd
sys.path.insert(0, os.environ["WT"])
from dinero import precios, universo_dinero as U
from dinero import sello_dinero as S
UTC = timezone.utc; BASE_HASTA = "2026-09-04"
SES = ("2026-09-08","2026-09-09","2026-09-10","2026-09-11","2026-09-14")
T = datetime(2026, 9, 15, 3, 30, tzinfo=UTC)
base = precios.cargar_congelado()
def ext(f):
    u = base.iloc[-1]; e = pd.DataFrame({pd.Timestamp(s): u*1.01 for s in SES}).T
    e.iloc[-1] = u.values*f; e.index.name="Date"; return e
def congelar(e):
    if "ahora_utc" in inspect.signature(S.congelar_extension).parameters:
        return S.congelar_extension(e, BASE_HASTA, ahora_utc=T)
    return S.congelar_extension(e, BASE_HASTA)
d = tempfile.mkdtemp(); S.DIR_EXT=os.path.join(d,"s"); S.RUTA_DB=os.path.join(d,"s.db"); db=S.RUTA_DB
cfg = U.reglas(); juegos = sorted(cfg["juegos"]) if isinstance(cfg.get("juegos"), dict) else []
print("VERSION_SELLO", S.VERSION_SELLO, "| juego_activo", cfg["juego_activo"], "| juegos", juegos)
otro = [j for j in juegos if j != cfg["juego_activo"] and not j.startswith("_")]
r1, m1 = congelar(ext(1.02)); o1 = S.sellar(r1, m1, ahora_utc=T, ruta_db=db)
print("disparo 1:", o1["resultado"], o1.get("juego"), "cita", os.path.basename(r1))
if not otro:
    print("sin segundo juego en reglas.json: no reproducible"); raise SystemExit
cfg2 = copy.deepcopy(cfg); cfg2["juego_activo"] = otro[0]
r2, m2 = congelar(ext(1.03))
print("disparo 2 congelo:", os.path.basename(r2), "| persistido", m2.get("persistido", True))
o2 = S.sellar(r2, m2, ahora_utc=T, ruta_db=db, cfg=cfg2)
print("disparo 2:", o2["resultado"], o2.get("juego"), "filas", o2["filas_insertadas"])
if not m2.get("persistido", True) and os.path.exists(r2):
    os.remove(r2)      # lo que hace main()
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
for j, a, sha in con.execute("SELECT DISTINCT juego, insumo_ext_archivo, insumo_ext_sha256 FROM sellos_dinero"):
    p = os.path.join(S.DIR_EXT, a)
    print(f"  juego {j:14s} cita {a[:46]:46s} -> {'existe, sha ' + ('OK' if S._sha256(p)==sha else 'DISTINTO') if os.path.exists(p) else '*** EL ARCHIVO NO EXISTE: integridad ROTA ***'}")
con.close()
print("disco:", sorted(os.listdir(S.DIR_EXT)))
