import sys; sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal")
import os; os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd, sqlite3
from datetime import date
from unittest import mock
import motor

con = sqlite3.connect("file:/home/nicolasaraneda/dev/mki-terminal/senales.db?mode=ro", uri=True)
sel = pd.read_sql("SELECT fecha,ticker,beta FROM senales_ticker WHERE beta IS NOT NULL AND modelo_version='4.6.0'", con)
orig = motor._datos_crudos
sox_hoy = orig(("^SOX",))
FECHAS = ["2026-08-12","2026-08-14","2026-08-19","2026-08-20","2026-08-13","2026-08-18","2026-08-21"]
for f in FECHAS:
    fecha = date.fromisoformat(f)
    s = sel[sel.fecha==f].set_index("ticker")["beta"]
    if len(s)<4: print(f,"pocas filas",len(s)); continue
    hoy = motor.betas_al(fecha).set_index("Ticker")["beta"].reindex(s.index)
    d0 = float(np.abs(hoy-s).max())
    idx = sox_hoy.index[sox_hoy.index.date<=fecha][-130:]
    res=[]
    for d in idx:
        def parche(tickers, d=d):
            df = orig(tickers)
            return df[df.index!=d] if "^SOX" in tickers else df
        with mock.patch.object(motor,"_datos_crudos",parche):
            b = motor.betas_al(fecha).set_index("Ticker")["beta"].reindex(s.index)
        res.append((float(np.abs(b-s).max()), d.date().isoformat()))
    res.sort()
    arr=np.array([r[0] for r in res])
    print(f"\n=== {f}  n_filas={len(s)}  maxdif con fuente de hoy = {d0:.3f}")
    print("   top-6 barras cuyo retiro mas acerca:", [(b,round(v,3)) for v,b in res[:6]])
    print(f"   perfil de las 130: min={arr.min():.3f} p05={np.percentile(arr,5):.3f} mediana={np.median(arr):.3f} max={arr.max():.3f}")
    print(f"   cuantas barras dejan maxdif <= 0.05: {(arr<=0.05).sum()} de {len(arr)}")
    print(f"   cuantas dejan maxdif <= 0.10: {(arr<=0.10).sum()}")
    print(f"   brecha 1o vs 2o: {res[1][0]-res[0][0]:.4f}")
