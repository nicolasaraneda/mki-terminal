import sys,os,json,math
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd
from backtest import linea_base as lb
from GEMELO import bifurcaciones as bf
from GEMELO.SECUENCIAL import trayectoria as tr

df = lb.aplicar_convencion(lb.cargar(hasta_sello=None), lb.CONVENCION_OFICIAL)
fechas=sorted(df.fecha.unique())
print("ancla viva: dias=%d filas=%d ultimo=%s"%(len(fechas),len(df),fechas[-1]))
tray=[]
for i in range(tr.MIN_DIAS,len(fechas)+1):
    sub=df[df.fecha<=fechas[i-1]]; e=tr.estadisticos(sub); e["hasta"]=fechas[i-1]; tray.append(e)
for c in tr.CANDIDATOS:
    dec=[t[f"{c}_decide"] for t in tray]
    print("%s cruces=%d decidiendo=%d/%d decide_hoy=%d"%(c,sum(1 for a,b in zip(dec,dec[1:]) if a!=b),sum(dec),len(dec),dec[-1]))
u=tray[-1]
print("\nHOY:",{k:u[k] for k in ("dias","filas","ventaja_pp","MCN_p","ICD_lo_pp","ICD_hi_pp","PSD_p","TDM_p","BAY_p_gt0","BAY_p_gt9pp","AVS_capital","SGN_pos","SGN_neg")})

# ---- metrica de estabilidad LIBRE DE POTENCIA: z estandarizado dia a dia
from backtest.inferencia import Phi_inv
def z_de_p(p): return abs(Phi_inv(1-max(min(p,1-1e-9),1e-9)/2))
zs={"MCN":[z_de_p(t["MCN_p"]) for t in tray],
    "PSD":[z_de_p(t["PSD_p"]) for t in tray],
    "TDM":[abs(t["TDM_t"]) for t in tray],
    "ICD":[ (t["ICD_lo_pp"]+t["ICD_hi_pp"])/2 / max(1e-9,(t["ICD_hi_pp"]-t["ICD_lo_pp"])/(2*1.96)) for t in tray],
    "BAY":[t["BAY_mu_pp"]/max(1e-9,t["BAY_sd_pp"]) for t in tray]}
print("\nestabilidad libre de potencia (|Δz| de un dia al siguiente, sobre 27 saltos):")
print("%-5s %8s %8s %8s"%("est","mediana","p90","max"))
for k,v in zs.items():
    dz=np.abs(np.diff(np.array(v,float)))
    print("%-5s %8.3f %8.3f %8.3f"%(k,np.median(dz),np.percentile(dz,90),dz.max()))
print("\ndistancia al umbral hoy (en z): umbral=1.96")
for k,v in zs.items(): print("  %-5s z_hoy=%.3f"%(k,v[-1]))
