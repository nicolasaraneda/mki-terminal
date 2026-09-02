import sys,os
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd, json, math
from backtest import linea_base as lb
from GEMELO import bifurcaciones as bf
from GEMELO.SECUENCIAL import trayectoria as tr
df = lb.aplicar_convencion(lb.cargar(hasta_sello=None), lb.CONVENCION_OFICIAL)
d=(df["acierto_gap"]-df["base_acierto"]).to_numpy(float); g=bf._por_dia(df,d)
icc=bf.icc_y_deff(g); print("ICC/DEFF ventana viva:",{k:(round(v,4) if isinstance(v,float) else v) for k,v in icc.items()})
print("sqrt(DEFF) =",round(math.sqrt(icc['deff']),3))
e=tr.estadisticos(df)
from backtest.inferencia import Phi_inv
zm=abs(Phi_inv(1-e["MCN_p"]/2)); zi=((e["ICD_lo_pp"]+e["ICD_hi_pp"])/2)/((e["ICD_hi_pp"]-e["ICD_lo_pp"])/(2*1.96))
print("z_MCN=%.3f  z_ICD=%.3f  cociente=%.3f  vs sqrt(DEFF)=%.3f"%(zm,zi,zm/zi,math.sqrt(icc['deff'])))

# --- sensibilidad al Frente A: filas del 28 y 31-ago bajo Yahoo-de-hoy
m4=pd.DataFrame(json.load(open("GEMELO/resultados/fuente_canonica.json"))["m4"]["filas"])
mp=m4.set_index(["fecha","ticker"])["apertura_hoy"]
alt=df.copy()
k=list(zip(alt.fecha,alt.ticker))
alt["ap_hoy"]=[mp.get(x,np.nan) for x in k]
mask=alt.fecha.isin(["2026-08-28","2026-08-31"]) & alt.ap_hoy.notna()
alt.loc[mask,"acierto_gap"]=(np.sign(alt.loc[mask,"ap_hoy"])==np.sign(alt.loc[mask,"gap_pct"])).astype(int)
print("\nfilas sustituidas:",int(mask.sum()))
for nombre,dd in (("SELLADO (statu quo)",df),("YAHOO-DE-HOY (C1)",alt)):
    ee=tr.estadisticos(dd)
    print("%-20s ventaja=%.2f pp  MCN p=%.4f  ICD=[%.2f, %.2f]  PSD p=%.4f  TDM p=%.4f  AVS K=%.2f  SGN %d-%d"%(
        nombre,ee["ventaja_pp"],ee["MCN_p"],ee["ICD_lo_pp"],ee["ICD_hi_pp"],ee["PSD_p"],ee["TDM_p"],ee["AVS_capital"],ee["SGN_pos"],ee["SGN_neg"]))
