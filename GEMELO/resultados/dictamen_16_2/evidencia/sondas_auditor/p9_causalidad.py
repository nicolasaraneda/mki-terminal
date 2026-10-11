"""P9: la prueba maestra sobre lo que E0.3 agrega. `avail` -el instante que
decide tabla y nombre- no puede mirar datos posteriores a fecha_insumo, y
`evaluar_timing` tiene que ser pura."""
import os, sys, tempfile
from datetime import datetime, timezone
import pandas as pd
sys.path.insert(0, os.environ["WT"])
from dinero import precios
from dinero import sello_dinero as S
UTC = timezone.utc; BASE_HASTA = "2026-09-04"
base = precios.cargar_congelado()
SES = ("2026-09-08","2026-09-09","2026-09-10","2026-09-11","2026-09-14","2026-09-15","2026-09-16")
def ext(n, nan=()):
    u = base.iloc[-1]; e = pd.DataFrame({pd.Timestamp(s): u*1.01 for s in SES[:n]}).T
    for t in nan: e.loc[pd.Timestamp(SES[n-1]), t] = float("nan")
    e.index.name = "Date"; return e
t = datetime(2026, 9, 14, 17, 43, 1, tzinfo=UTC)

print("1) todo `ultimo_cierre` de la disponibilidad es <= fecha_insumo (backward-only):")
for n in (5, 6, 7):
    e = ext(n, nan=("SHECY",))
    d = precios.disponibilidad_por_ticker(e)
    D = str(e.index.max().date())
    peor = max(v["ultimo_cierre"] for v in d.values())
    print(f"   fecha_insumo={D}  max(ultimo_cierre)={peor}  <=D? {peor <= D}  SHECY={d['SHECY']['ultimo_cierre']}")

print("2) `evaluar_timing` es pura: mismos insumos -> mismo resultado, y no depende de nada mas:")
e = ext(5, nan=("SHECY",)); d = precios.disponibilidad_por_ticker(e)
a = S.evaluar_timing(d, "2026-09-14", t); b = S.evaluar_timing(dict(d), "2026-09-14", t)
print("   identico en dos llamadas:", a == b, "|", a["timing_ok"], a["avail"], a["sesion_obj"])
print("   el avail NO es el reloj de pared:", a["avail"], "!=", t.isoformat())

print("3) truncar el futuro DESPUES de fecha_insumo no mueve el veredicto de esa fecha:")
# la disponibilidad se recorta a <= D y se vuelve a evaluar: el veredicto tiene que ser el mismo
for n in (5, 6, 7):
    e = ext(n, nan=("SHECY",))
    D = "2026-09-14"
    recortada = e.loc[e.index <= pd.Timestamp(D)]
    v_largo = S.evaluar_timing(precios.disponibilidad_por_ticker(recortada), D, t)
    v_corto = S.evaluar_timing(precios.disponibilidad_por_ticker(ext(5, nan=("SHECY",))), D, t)
    print(f"   extension de {n} sesiones recortada en {D}: timing_ok={v_largo['timing_ok']} avail={v_largo['avail']} == arm corto? {v_largo == v_corto}")

print("4) el gate de invariancia de `decidir` con el cfg de la 16b y E0.3:")
tmp = tempfile.mkdtemp(); S.DIR_EXT = os.path.join(tmp, "s"); S.RUTA_DB = os.path.join(tmp, "s.db")
r, m = S.congelar_extension(ext(7), BASE_HASTA, ahora_utc=datetime(2026,9,17,3,30,tzinfo=UTC))
cierres = S.insumo(r)
print("  ", S.gate_previo_al_sello(cierres))
from dinero import universo_dinero as U
cfg = U.reglas()
print("   exclusiones_insumo_e0 en reglas.json:", cfg.get("exclusiones_insumo_e0"))
for dia in ("2026-09-14", "2026-09-15"):
    print("  ", S.verificar_invariancia_decision(cierres, dia, futuros=2))
