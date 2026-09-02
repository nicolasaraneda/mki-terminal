import sys,os
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
from GEMELO.SECUENCIAL import autocorrelacion as ac
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal/.claude/skills/estadistica-evaluacion/scripts")
from evaluacion import wilson_ci
for phi in (0.0,0.3):
    r=ac.cruces_plan(phi,0.0,n_rep=4000)
    print("phi=%.1f  "%phi + "  ".join("%s=%.4f %s"%(k,v,tuple(round(x,4) for x in wilson_ci(round(v*4000),4000))) for k,v in r.items()))
print("\nFECHAS_POR_MIRADA",ac.ds.FECHAS_POR_MIRADA,"UMBRALES",ac.ds.UMBRALES_OBF)
