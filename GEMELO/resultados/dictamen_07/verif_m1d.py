import pandas as pd, numpy as np
viejo = pd.read_csv("/home/nicolasaraneda/dev/mki-terminal/GEMELO/cache/cierres_853b6558513c5e9f.csv", index_col=0, parse_dates=True)
nuevo = pd.read_csv("/tmp/nuevo_27.csv", index_col=0, parse_dates=True)
DESDE = max(viejo.index.min(), nuevo.index.min())
t="000660.KS"
a=viejo[t].dropna(); b=nuevo[t].dropna(); c=a.index.intersection(b.index); c=c[c>=DESDE]
f=(b[c]/a[c])
g=f.round(6)
cortes=g[g.ne(g.shift())]
print("cambios de nivel del factor (redondeado a 1e-6):", len(cortes))
for i,v in cortes.items(): print("  ",i.date(), "%.9f"%f[i])
print("\nfactor por anio (mediana):")
print(f.groupby(f.index.year).median().round(9).to_string())
# retornos: comprobacion directa de que el cambio es proporcional POR TRAMO
ra=a.pct_change(); rb=b.pct_change()
j=(ra-rb).abs().dropna()
print("\nmax |dif retorno| 000660.KS = %.3e   n=%d"%(j.max(), len(j)))
