import sys,os,glob,math,json
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal"); os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd
from GEMELO.SECUENCIAL import autocorrelacion as ac
from GEMELO.SECUENCIAL.mirada import autocorrelacion_lag1, contribuciones_por_fecha
from backtest import linea_base as lb
s = ac.d_por_fecha_ventana_larga()
x = s.to_numpy()
print("fechas=%d  desde=%s hasta=%s"%(len(x),s.index.min(),s.index.max()))
print("AC1..AC5 =",[round(v,3) for v in ac.autocorrelaciones(x)])
a1,ee = autocorrelacion_lag1(x); print("AC1=%.3f  EE=1/sqrt(m)=%.3f"%(a1,ee))
lo,hi = ac.ic_ac1_bootstrap_bloques(x); print("IC95 bootstrap bloques(20) = [%.3f, %.3f]"%(lo,hi))
# centrado del bootstrap
rng=np.random.default_rng(20260902); n=len(x); nb=math.ceil(n/20); reps=[]
for _ in range(2000):
    ini=rng.integers(0,n,size=nb); idx=(ini[:,None]+np.arange(20)[None,:]).ravel()%n
    reps.append(autocorrelacion_lag1(x[idx[:n]])[0])
reps=np.array(reps); print("bootstrap: mediana=%.4f  punto=%.4f  sesgo=%.4f  sd=%.4f"%(np.median(reps),a1,np.median(reps)-a1,reps.std(ddof=1)))
# la sellada
sell=lb.aplicar_convencion(lb.cargar(hasta_sello=None),lb.CONVENCION_OFICIAL)
ds_=contribuciones_por_fecha(sell); a1s,ees=autocorrelacion_lag1(ds_)
print("sellada: fechas=%d AC1=%.3f EE=%.3f  IC95 aprox [%.3f, %.3f]"%(len(ds_),a1s,ees,a1s-1.96*ees,a1s+1.96*ees))
# --- contaminacion por conteo de filas
df=pd.read_csv(ac.RUTA_B2[-1]).drop_duplicates(subset=["ticker","sesion_objetivo"],keep="first")
df=df[df.gap_pct!=0]
cnt=df.groupby("fecha_emision").size().astype(float).to_numpy()
med=(s/pd.Series(cnt,index=s.index)).to_numpy()
print("\nAC1 del CONTEO de filas por fecha: %.3f (EE %.3f)"%autocorrelacion_lag1(cnt))
print("AC1 de la MEDIA por fecha (no la suma): %.3f (EE %.3f)"%autocorrelacion_lag1(med))
print("tam de fecha: min=%d max=%d media=%.2f  sd=%.2f"%(cnt.min(),cnt.max(),cnt.mean(),cnt.std()))
# regimen: AC1 de la larga restringida al mismo tramo calendario que la sellada
sub=s[(pd.to_datetime(s.index)>=pd.Timestamp("2026-07-05"))]
print("AC1 de la larga desde 2026-07-05 (%d fechas): %.3f (EE %.3f)"%((len(sub),)+autocorrelacion_lag1(sub.to_numpy())))
