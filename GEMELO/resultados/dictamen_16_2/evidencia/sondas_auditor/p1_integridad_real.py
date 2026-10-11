"""P1 (auditor 16-2): los cuatro tests de integridad permanente de la seccion 4
corridos a mano contra la base REAL en mode=ro con el modulo PARCHEADO, porque
en el worktree se saltaron todos por falta de .db. Solo lectura: nunca
conectar(solo_lectura=False) sobre la base real."""
import os, sqlite3, sys
REAL = "/home/nicolasaraneda/dev/mki-terminal"
sys.path.insert(0, os.environ["WT"])
from dinero import sello_dinero as S
from dinero import precios

S.RUTA_DB = os.path.join(REAL, "dinero", "sello_dinero.db")
S.DIR_EXT = os.path.join(REAL, "dinero", "datos", "sello")
S.DIR_BACKUP_EXT = os.path.join(REAL, "data", "backups", "sello_dinero_ext")
print("RUTA_DB:", S.RUTA_DB)

def citas(tabla):
    con = S.conectar(S.RUTA_DB, solo_lectura=True)
    try:
        return con.execute(f"SELECT DISTINCT fecha_insumo, insumo_ext_archivo, insumo_ext_sha256 FROM {tabla} ORDER BY fecha_insumo").fetchall()
    except sqlite3.OperationalError as e:
        return ("AUSENTE", str(e))
    finally:
        con.close()

def verificar(directorio, filas):
    fallas, por_fecha = [], {}
    for fecha, archivo, sha in filas:
        por_fecha.setdefault(fecha, set()).add(sha)
        ruta = os.path.join(directorio, archivo or f"ext_{fecha}.csv")
        if not os.path.exists(ruta):
            fallas.append(f"{fecha}: FALTA {ruta}")
        elif S._sha256(ruta) != sha:
            fallas.append(f"{fecha}: {os.path.basename(ruta)} sha {S._sha256(ruta)[:12]} vs base {sha[:12]}")
    fallas += [f"{f}: {len(s)} shas distintos" for f, s in por_fecha.items() if len(s) != 1]
    return fallas

sellos = citas("sellos_dinero")
intentos = citas("intentos_no_verificables")
print("filas de intentos:", intentos)
print(f"fechas en sellos_dinero: {len(sellos)}")
print("A. integridad en DIR_EXT      :", verificar(S.DIR_EXT, sellos) or "SIN FALLAS")
print("B. integridad en DIR_BACKUP_EXT:", verificar(S.DIR_BACKUP_EXT, sellos) or "SIN FALLAS")
clase = [f"{f}: sellos_dinero cita {a}" for f, a, _ in sellos if S.es_extension_no_verificable(a or f"ext_{f}.csv")]
print("C. clase de evidencia (5.2)   :", clase or "SIN FALLAS")
con = S.conectar(S.RUTA_DB, solo_lectura=True)
rotas = con.execute("SELECT DISTINCT fecha_insumo, estado, estado_timing, version_sello FROM sellos_dinero WHERE estado = 'no_verificable_timing' OR estado_timing = 'roto' ORDER BY fecha_insumo").fetchall()
bases = [r[0] for r in con.execute("SELECT DISTINCT insumo_base_sha256 FROM sellos_dinero").fetchall()]
con.close()
_v = lambda v: tuple(int(x) for x in v.lstrip("E").split("."))
print("rotas en la principal:", rotas)
print("D. regla del corte (<E0.3)    :", [r for r in rotas if _v(r[3]) >= (0, 3)] or "SIN FALLAS")
print("E. congelado grande citado    :", "SIN FALLAS" if bases == [S._sha256(precios.RUTA_CIERRES)] else f"FALLA {bases} vs {S._sha256(precios.RUTA_CIERRES)}")
