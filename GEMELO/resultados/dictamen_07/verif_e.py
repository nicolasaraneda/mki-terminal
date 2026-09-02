import sys,os,itertools,math
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd
from GEMELO.SECUENCIAL import estimandos as es
from backtest import linea_base as lb
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal/.claude/skills/estadistica-evaluacion/scripts")
from evaluacion import wilson_ci

larga = es._preparar(es.ventana_larga())
sell  = es._preparar(lb.aplicar_convencion(lb.cargar(hasta_sello=None), lb.CONVENCION_OFICIAL))
print("larga: %d filas %d fechas ; sellada: %d filas %d fechas"%(len(larga),larga.fecha.nunique(),len(sell),sell.fecha.nunique()))
print("pendiente E4 larga = %.3f pp/h (reporte -1.608)"%(100*es._pendiente(larga,"h","E0")))

# --- 1. la unidad de replicacion del MECANISMO es la BOLSA, no la fecha
print("\n== E4 con la BOLSA como unidad de replicacion ==")
por = larga.groupby("exchange").agg(h=("h","first"), e0=("E0","mean"), n=("E0","size"))
print(por.assign(e0_pp=lambda d:(100*d.e0).round(2)).to_string())
# bootstrap de BOLSAS (4 clusters)
rng=np.random.default_rng(20260902); ex=list(por.index); reps=[]
grupos={e:g for e,g in larga.groupby("exchange")}
for _ in range(4000):
    j=rng.integers(0,4,size=4)
    d=pd.concat([grupos[ex[t]] for t in j])
    if d.h.nunique()<2: continue
    reps.append(100*es._pendiente(d,"h","E0"))
reps=np.array(reps)
print("bootstrap de BOLSAS (4 clusters, %d replicas utiles de 4000):"%len(reps))
print("  punto=-1.608  IC95=[%.2f, %.2f]   (el reporte, con bootstrap de FECHAS: [-2.45, -0.77])"%tuple(np.quantile(reps,[.025,.975])))
# permutacion exacta de las etiquetas h entre las 4 bolsas
e0=por.e0.to_numpy(); hs=por.h.to_numpy(); ns=por.n.to_numpy()
def pend(hv):
    x=np.repeat(hv,ns); y=np.concatenate([np.repeat(por.e0.iloc[i],ns[i]) for i in range(4)])
    return ((x-x.mean())*(y-y.mean())).mean()/x.var()
obs=pend(hs); nulos=[pend(np.array(p)) for p in set(itertools.permutations(hs))]
p=(1+sum(1 for v in nulos if abs(v)>=abs(obs)-1e-12))/(len(nulos)+1)
print("  permutacion EXACTA de las %d asignaciones distintas de h a bolsas: p = %.3f  (p minimo alcanzable = %.3f)"%(len(nulos),p,1/(len(nulos)+1)))

# --- 2. la sellada invierte el orden
print("\n== ordenamiento por h ==")
for nom,d in (("larga",larga),("sellada",sell)):
    t=d.groupby("exchange").agg(h=("h","first"),e0=("E0","mean"),n=("E0","size")).sort_values("h")
    print("  %-8s "%nom + "  ".join("%s(h=%.2f) %+.1f pp n=%d"%(i,r.h,100*r.e0,r.n) for i,r in t.iterrows()))

# --- 3. E3 vs E0: la diferencia de D80 con bootstrap PAREADO de fechas
print("\n== E3 vs E0: la ventaja de senal, pareada ==")
for nom,d in (("sellada",sell),("larga",larga)):
    fechas=d.fecha.unique(); gr={f:g for f,g in d.groupby("fecha")}
    rng=np.random.default_rng(7)
    z0=[];z3=[]
    p0=100*d.E0.mean(); p3=es._pendiente(d,"p","g")
    for _ in range(2000):
        j=rng.integers(0,len(fechas),size=len(fechas))
        dd=pd.concat([gr[fechas[t]] for t in j])
        z0.append(100*dd.E0.mean()); z3.append(es._pendiente(dd,"p","g"))
    z0=np.array(z0); z3=np.array(z3)
    zz0=p0/z0.std(ddof=1); zz3=p3/z3.std(ddof=1)
    d80_0=len(fechas)*(2.80/zz0)**2; d80_3=len(fechas)*(2.80/zz3)**2
    # IC de la RAZON D80(E0)/D80(E3) = (z3/z0)^2, con bootstrap pareado del cociente de z
    rat=[]
    for _ in range(2000):
        j=rng.integers(0,len(fechas),size=len(fechas))
        dd=pd.concat([gr[fechas[t]] for t in j])
        a=100*dd.E0.mean(); b=es._pendiente(dd,"p","g")
        rat.append((b/z3.std(ddof=1))**2/max(1e-9,(a/z0.std(ddof=1))**2))
    rat=np.array(rat); rat=rat[np.isfinite(rat)]
    print("  %-8s z_E0=%.2f z_E3=%.2f  D80 %d vs %d  razon=%.1f×  IC95 de la razon [%.1f, %.1f]"%(
        nom,zz0,zz3,round(d80_0),round(d80_3),d80_0/d80_3,*np.quantile(rat,[.025,.975])))
