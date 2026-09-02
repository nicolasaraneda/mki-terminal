import sys, os
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np
from backtest import linea_base as lb
from GEMELO import bifurcaciones as bf
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal/.claude/skills/estadistica-evaluacion/scripts")
from evaluacion import wilson_ci

df = lb.aplicar_convencion(lb.cargar(hasta_sello=lb.CORTE_REGLA_FIRMADA), lb.CONVENCION_OFICIAL)
d = (df["acierto_gap"]-df["base_acierto"]).to_numpy(float)
grupos = bf._por_dia(df, d)
todo=np.concatenate(grupos); cent=[g-todo.mean() for g in grupos]; k=len(cent)

def p_perm(gr, n_perm, rng):
    S=np.array([g.sum() for g in gr],float)
    obs=abs(float(S.sum()))
    signos=rng.choice(np.array([-1.,1.]),size=(n_perm,len(S)))
    nulos=np.abs(signos@S)
    return (1+int((nulos>=obs-1e-12).sum()))/(n_perm+1)

def alfa(D,n_sim,n_perm,semilla_fija,seed=20260902):
    rng=np.random.default_rng(seed); rech=0
    for _ in range(n_sim):
        idx=rng.integers(0,k,size=D)
        m=[cent[j] for j in idx]
        r = np.random.default_rng(bf.SEMILLA) if semilla_fija else rng
        if p_perm(m,n_perm,r)<0.05: rech+=1
    return rech,n_sim

for D in (35,73,250):
    for fija in (True,False):
        r,ns=alfa(D,3000,800,fija)
        lo,hi=wilson_ci(r,ns)
        print("D=%4d  semilla_perm %-8s  alfa=%.4f  Wilson95 [%.4f, %.4f]  (n_sim=%d)"%(
            D,"FIJA" if fija else "variable",r/ns,lo,hi,ns))
