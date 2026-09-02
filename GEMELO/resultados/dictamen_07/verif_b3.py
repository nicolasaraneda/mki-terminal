import sys, os
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np
from backtest import linea_base as lb
from GEMELO import bifurcaciones as bf
from GEMELO.SECUENCIAL import horizonte as hz
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal/.claude/skills/estadistica-evaluacion/scripts")
from evaluacion import wilson_ci
df, grupos = hz.cargar_grupos()
print("bf.SEMILLA",bf.SEMILLA,"hz.SEMILLA",hz.SEMILLA)
# reproduccion EXACTA de la celda alfa D=35 del informe
a=hz.potencia_simulada(grupos,0.0,35)
print("reproduccion exacta alfa(D=35, n_sim=300) =",a, " informe: 0.083")
print("  Wilson95 sobre 300:",tuple(round(x,4) for x in wilson_ci(round(a*300),300)))
# y con n_sim mayor, MISMA funcion
for ns in (1000,3000):
    a2=hz.potencia_simulada(grupos,0.0,35,n_sim=ns)
    print("misma funcion, n_sim=%d -> alfa=%.4f  Wilson95 %s"%(ns,a2,tuple(round(x,4) for x in wilson_ci(round(a2*ns),ns))))
