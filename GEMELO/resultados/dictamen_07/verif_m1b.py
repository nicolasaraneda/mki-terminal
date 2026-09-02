import sys
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd
viejo = pd.read_csv("/home/nicolasaraneda/dev/mki-terminal/GEMELO/cache/cierres_853b6558513c5e9f.csv", index_col=0, parse_dates=True)
nuevo = pd.read_csv("/tmp/nuevo_27.csv", index_col=0, parse_dates=True)
ULT = viejo.index.max()
DESDE = max(viejo.index.min(), nuevo.index.min())
TOL = 5e-6
tot = dict(pares_viejo=0, pares_comparables=0, pares_no_comparables=0, cambiados=0,
           celdas=0, dist=0, prop=0, noprop=0, ret=0, apar=0)
peor = 0.0
det=[]
for t in viejo.columns:
    a = viejo[t].dropna(); b = nuevo[t].dropna()
    a = a[(a.index>=DESDE)&(a.index<ULT)]   # excluye la ultima fecha de la cache
    b = b[(b.index>=DESDE)&(b.index<ULT)]
    ret_ = a.index.difference(b.index); apar_ = b.index.difference(a.index)
    ra = a.pct_change(); rb = b.pct_change()
    # pares realmente comparables: misma fecha Y misma fecha previa en ambos
    prev_a = pd.Series(a.index).shift(1).values
    prev_b = pd.Series(b.index).shift(1).values
    pa = pd.DataFrame({"r":ra.values,"prev":prev_a}, index=a.index)
    pb = pd.DataFrame({"r":rb.values,"prev":prev_b}, index=b.index)
    j = pa.join(pb, how="inner", rsuffix="_n")
    mismo_par = (j["prev"]==j["prev_n"]) & j["r"].notna() & j["r_n"].notna()
    dif = (j["r"]-j["r_n"]).abs()
    camb = (mismo_par & (dif>TOL))
    comun = a.index.intersection(b.index)
    d = (a[comun]-b[comun]).abs() > 1e-6*a[comun].abs()
    tot["pares_viejo"] += int(ra.notna().sum())
    tot["pares_comparables"] += int(mismo_par.sum())
    tot["pares_no_comparables"] += int(ra.notna().sum()-mismo_par.sum())
    tot["cambiados"] += int(camb.sum())
    tot["celdas"] += int(len(a.index.union(b.index)))
    tot["dist"] += int(d.sum()); tot["ret"]+=len(ret_); tot["apar"]+=len(apar_)
    if mismo_par.any(): peor=max(peor, float(dif[mismo_par].max()))
    if int(d.sum())>0 or len(ret_) or len(apar_) or int(camb.sum()):
        det.append((t,int(d.sum()),len(ret_),len(apar_),int(camb.sum()),
                    int(ra.notna().sum()-mismo_par.sum())))
print("TOTALES (ruta independiente, retornos sobre indice PROPIO de cada ticker):")
for k,v in tot.items(): print(f"  {k:22s} {v}")
print("  max|dif retorno| comparable  %.3e"%peor)
print("\nticker | niveles distintos | barras retiradas | aparecidas | retornos cambiados | pares NO comparables")
for r in det: print("  %-10s %6d %6d %6d %6d %8d"%r)
