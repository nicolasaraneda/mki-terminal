"""P2 (auditor 16-2): la ZONA CIEGA declarada en la corrida 15. Dos instancias
entre congelar y sellar, con timing roto. Se corre con el modulo PARCHEADO
(E0.3) y con HEAD (E0.2) para decidir si la fuga es NUEVA o PREEXISTENTE.
Todo en tmp: ni la base real ni DIR_EXT real se tocan."""
import inspect, os, sqlite3, sys, tempfile
from datetime import datetime, timezone
import pandas as pd
sys.path.insert(0, os.environ["WT"])
from dinero import precios
from dinero import sello_dinero as S

UTC = timezone.utc
BASE_HASTA = "2026-09-04"
SES = ("2026-09-08", "2026-09-09", "2026-09-10", "2026-09-11", "2026-09-14")
T_ROTO = datetime(2026, 9, 14, 17, 43, 1, tzinfo=UTC)      # 13:43 NY, bolsa abierta
base = precios.cargar_congelado()

def ext(factor):
    ult = base.iloc[-1]
    e = pd.DataFrame({pd.Timestamp(s): ult * 1.01 for s in SES}).T
    e.iloc[-1] = ult.values * factor
    e.index.name = "Date"
    return e

def congelar(e, ahora):
    if "ahora_utc" in inspect.signature(S.congelar_extension).parameters:
        return S.congelar_extension(e, BASE_HASTA, ahora_utc=ahora)
    return S.congelar_extension(e, BASE_HASTA)

tmp = tempfile.mkdtemp()
S.DIR_EXT = os.path.join(tmp, "sello"); S.RUTA_DB = os.path.join(tmp, "s.db")
db = S.RUTA_DB
print("VERSION_SELLO =", S.VERSION_SELLO)
# A congela (barra intradia 0.98), B congela despues (barra intradia movida 0.97)
rA, mA = congelar(ext(0.98), T_ROTO)
rB, mB = congelar(ext(0.97), T_ROTO)
print("A congelo :", os.path.basename(rA), mA["sha256"][:12], "persistido", mA.get("persistido", True))
print("B congelo :", os.path.basename(rB), mB["sha256"][:12], "persistido", mB.get("persistido", True))
print("mismo path:", os.path.abspath(rA) == os.path.abspath(rB))
print("sha en disco de la ruta de A:", S._sha256(rA)[:12], "| la base citara", mA["sha256"][:12])
# A sella con SU meta, sobre el archivo que B dejo en disco
oA = S.sellar(rA, mA, ahora_utc=T_ROTO, ruta_db=db)
oB = S.sellar(rB, mB, ahora_utc=T_ROTO, ruta_db=db)
print("A sello   :", oA["resultado"], "tabla", oA.get("tabla"), "filas", oA["filas_insertadas"])
print("B sello   :", oB["resultado"], "tabla", oB.get("tabla"), "filas", oB["filas_insertadas"])
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
for t in ("sellos_dinero", "intentos_no_verificables"):
    try:
        print(f"  {t}:", con.execute(f"SELECT COUNT(*), substr(insumo_ext_sha256,1,12), insumo_ext_archivo FROM {t} GROUP BY insumo_ext_sha256").fetchall())
    except sqlite3.OperationalError:
        print(f"  {t}: AUSENTE")
print("  divergencias:", con.execute("SELECT COUNT(*) FROM divergencias_sello").fetchone()[0])
citado = con.execute("SELECT DISTINCT insumo_ext_sha256, insumo_ext_archivo FROM " + ("intentos_no_verificables" if oA.get("tabla", "sellos_dinero") != "sellos_dinero" else "sellos_dinero")).fetchall()
con.close()
print("FILAS CITAN:", [(s[:12], a) for s, a in citado])
for s, a in citado:
    p = os.path.join(S.DIR_EXT, a)
    real = S._sha256(p) if os.path.exists(p) else "NO EXISTE"
    print(f"  INTEGRIDAD -> {a}: disco {real[:12]} vs citado {s[:12]} => {'OK' if real == s else '*** ROTA ***'}")
print("disco:", sorted(os.listdir(S.DIR_EXT)))
