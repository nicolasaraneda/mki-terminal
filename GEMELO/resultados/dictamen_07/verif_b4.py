import sys,os
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd
from backtest import linea_base as lb
from GEMELO import bifurcaciones as bf
df = lb.aplicar_convencion(lb.cargar(hasta_sello=lb.CORTE_REGLA_FIRMADA), lb.CONVENCION_OFICIAL)
d=(df["acierto_gap"]-df["base_acierto"]).to_numpy(float)
grupos=bf._por_dia(df,d)
fechas=list(pd.factorize(df["fecha"].to_numpy())[1])
h=len(grupos)//2
print("primera mitad:",fechas[0],"->",fechas[h-1],"(%d dias)"%h)
print("segunda mitad:",fechas[h],"->",fechas[-1],"(%d dias)"%(len(grupos)-h))
print("VENTANA_R2 =",lb.VENTANA_R2)
print("R2 (excluyendo el bloque 1):",lb.duelo_excluyendo(df,*lb.VENTANA_R2))
# ventaja de dia excluyendo R2
fuera=df[(df.fecha<lb.VENTANA_R2[0])|(df.fecha>lb.VENTANA_R2[1])]
g2=bf._por_dia(fuera,(fuera["acierto_gap"]-fuera["base_acierto"]).to_numpy(float))
p,lo,hi=bf._bootstrap_dia(g2,10000)
print("ventaja de DIA sin bloque 1: %.2f pp IC95 [%.2f, %.2f]  (dias=%d, n=%d)"%(100*p,100*lo,100*hi,len(g2),len(fuera)))
print("p permutacion de dia sin bloque 1: %.4f"%bf._p_permutacion_dia(g2,4000))
print("p permutacion de dia CON todo:    %.4f"%bf._p_permutacion_dia(grupos,4000))
# cuantos dias del bloque 1 caen en la primera mitad
b1=[f for f in fechas if lb.VENTANA_R2[0]<=f<=lb.VENTANA_R2[1]]
print("dias del bloque 1 en la ventana:",b1)
print("de ellos en la primera mitad:",[f for f in b1 if f in fechas[:h]])
