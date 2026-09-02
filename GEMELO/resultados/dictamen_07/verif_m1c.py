import pandas as pd, numpy as np
viejo = pd.read_csv("/home/nicolasaraneda/dev/mki-terminal/GEMELO/cache/cierres_853b6558513c5e9f.csv", index_col=0, parse_dates=True)
nuevo = pd.read_csv("/tmp/nuevo_27.csv", index_col=0, parse_dates=True)
ULT = viejo.index.max(); DESDE = max(viejo.index.min(), nuevo.index.min())
for t in ["000660.KS","005930.KS","6857.T","2330.TW","8035.T","HG=F"]:
    a=viejo[t].dropna(); b=nuevo[t].dropna()
    a=a[(a.index>=DESDE)]; b=b[(b.index>=DESDE)]
    c=a.index.intersection(b.index)
    f=(b[c]/a[c]).dropna()
    d=(a[c]-b[c]).abs()>1e-6*a[c].abs()
    fd=f[d]
    print(f"{t:12s} celdas_distintas={int(d.sum()):5d}  ult_fecha_distinta={bool(d.get(ULT,False))}")
    if len(fd):
        print(f"             factor: min={fd.min():.9f} max={fd.max():.9f} n_valores_unicos={fd.round(9).nunique()}")
        print(f"             rango relativo = {(fd.max()-fd.min())/abs(fd).max():.3e}   (tol del script = 1e-6)")
        # cuantos factores distintos y desde cuando
        vc=fd.round(8).value_counts()
        print("             top factores:", dict(list(vc.items())[:4]))
        # tramos
        ch=fd.round(8)
        cortes=ch[ch.ne(ch.shift())]
        print("             tramos:", [(str(i.date()),float(v)) for i,v in list(cortes.items())[:6]])
