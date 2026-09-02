import sys, os
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd, math
from backtest import linea_base as lb
from backtest.inferencia import Phi, Phi_inv
from GEMELO import bifurcaciones as bf
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal/.claude/skills/estadistica-evaluacion/scripts")
from evaluacion import wilson_ci

df = lb.aplicar_convencion(lb.cargar(hasta_sello=lb.CORTE_REGLA_FIRMADA), lb.CONVENCION_OFICIAL)
d = (df["acierto_gap"]-df["base_acierto"]).to_numpy(float)
grupos = bf._por_dia(df, d)
k=len(grupos); n=int(sum(len(g) for g in grupos))
print("ANCLA: n=%d  dias=%d  primera=%s ultima=%s"%(n,k,df.fecha.min(),df.fecha.max()))
print("duelo:", lb.duelo(df))
p,lo,hi = bf._bootstrap_dia(grupos, n_boot=10000)
z=Phi_inv(0.975)
se_int=(hi-lo)/(2*z)
print("ventaja=%.4f pp IC95=[%.2f,%.2f]  SE_del_IC=%.4f pp"%(100*p,100*lo,100*hi,100*se_int))

# SE por DESVIACION ESTANDAR del bootstrap (ruta alternativa)
sumas=np.array([g.sum() for g in grupos]); cuentas=np.array([len(g) for g in grupos],float)
rng=np.random.default_rng(20260902)
idx=rng.integers(0,k,size=(20000,k))
reps=sumas[idx].sum(1)/cuentas[idx].sum(1)
print("SE bootstrap (sd) = %.4f pp   asimetria del IC: (hi-p)/(p-lo) = %.3f"%(100*reps.std(ddof=1),(hi-p)/(p-lo)))
# incertidumbre DEL PROPIO SE: bootstrap doble sobre dias
ses=[]
for _ in range(400):
    j=rng.integers(0,k,size=k)
    g2=[grupos[t] for t in j]
    s2=np.array([g.sum() for g in g2]); c2=np.array([len(g) for g in g2],float)
    ii=rng.integers(0,k,size=(600,k))
    r2=s2[ii].sum(1)/c2[ii].sum(1)
    ses.append(r2.std(ddof=1))
ses=np.array(ses)
print("SE del SE: IC95 del SE de dia = [%.3f, %.3f] pp (bootstrap doble, 400x600)"%(100*np.quantile(ses,.025),100*np.quantile(ses,.975)))
# lo que eso hace a D
def D_de(se,delta): 
    zt=Phi_inv(0.975)+Phi_inv(0.80); return k*(zt*se/delta)**2
for dpp in (9.0,6.5,5.0):
    lo_,hi_=np.quantile(ses,[.025,.975])
    print("  delta=%.1f pp -> D punto %.0f ; IC95 por incertidumbre del SE: [%.0f, %.0f] dias"%(
        dpp, D_de(se_int,dpp/100), D_de(lo_,dpp/100), D_de(hi_,dpp/100)))
