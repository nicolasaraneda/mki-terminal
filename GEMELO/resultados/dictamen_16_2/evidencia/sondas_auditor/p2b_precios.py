"""P2b: en la carrera, la fila de A ?lleva los precios de A o los de B?
`sellar` lee el CSV del disco, no el DataFrame que A descargo."""
import inspect, os, sqlite3, sys, tempfile
from datetime import datetime, timezone
import pandas as pd
sys.path.insert(0, os.environ["WT"])
from dinero import precios
from dinero import sello_dinero as S
UTC = timezone.utc; BASE_HASTA = "2026-09-04"
SES = ("2026-09-08","2026-09-09","2026-09-10","2026-09-11","2026-09-14")
T = datetime(2026, 9, 14, 17, 43, 1, tzinfo=UTC)
base = precios.cargar_congelado()
def ext(f):
    u = base.iloc[-1]; e = pd.DataFrame({pd.Timestamp(s): u*1.01 for s in SES}).T
    e.iloc[-1] = u.values*f; e.index.name="Date"; return e
tmp = tempfile.mkdtemp(); S.DIR_EXT=os.path.join(tmp,"s"); S.RUTA_DB=os.path.join(tmp,"s.db")
rA, mA = S.congelar_extension(ext(0.98), BASE_HASTA, ahora_utc=T)
rB, mB = S.congelar_extension(ext(0.97), BASE_HASTA, ahora_utc=T)
S.sellar(rA, mA, ahora_utc=T, ruta_db=S.RUTA_DB)
con = sqlite3.connect(f"file:{S.RUTA_DB}?mode=ro", uri=True)
p = con.execute("SELECT precio_ref_usd FROM intentos_no_verificables WHERE ticker='AMD'").fetchone()[0]
con.close()
u = float(base.iloc[-1]["AMD"])
print(f"AMD cierre congelado={u:.6f}  A(x0.98)={u*0.98:.6f}  B(x0.97)={u*0.97:.6f}  fila de A={p:.6f}")
print("la fila de A lleva los precios de:", "B (el que piso el archivo)" if abs(p-u*0.97)<1e-6 else "A")
