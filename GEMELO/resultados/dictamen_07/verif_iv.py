import sys; sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal")
import os; os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import sqlite3,pandas as pd,numpy as np
from datetime import date
import motor
sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal/.claude/skills/estadistica-evaluacion/scripts")
from evaluacion import wilson_ci, mcnemar_exact

c=sqlite3.connect('file:/home/nicolasaraneda/dev/mki-terminal/senales.db?mode=ro',uri=True)
v=pd.read_sql("select * from verificacion_apertura where legacy=0 and modelo_version='4.6.0'",c)
sn=pd.read_sql("select fecha,sox_usado_pct,sox_fecha from snapshots order by fecha",c)
print(sn.tail(6).to_string(index=False))

d=motor._datos_crudos(("^SOX",)); s=d["^SOX"] if "^SOX" in d.columns else d.iloc[:,0]
print("\n^SOX barras hoy 25-ago..1-sep:", [str(x.date()) for x in s.loc["2026-08-25":"2026-09-01"].index])
r=(s.pct_change()*100).loc["2026-08-25":"2026-09-01"].round(3)
print(r.to_string())

nuevo=[]
for f in ["2026-08-28","2026-08-31"]:
    p=motor.prediccion_apertura_al(date.fromisoformat(f))
    p=p.rename(columns={c_:c_ for c_ in p.columns})
    print("\n== prediccion_apertura_al(%s) recomputada HOY"%f)
    print(p.to_string(index=False))
    nuevo.append((f,p))

# contrafactual sobre las 15 filas verificadas
sub=v[v.fecha_senal.isin(["2026-08-28","2026-08-31"])].copy()
mapa={}
for f,p in nuevo:
    col=[c_ for c_ in p.columns if "ticker" in c_.lower()][0]
    est=[c_ for c_ in p.columns if "apertura" in c_.lower() or "estim" in c_.lower()][0]
    for _,row in p.iterrows(): mapa[(f,row[col])]=float(row[est])
sub["est_hoy"]=[mapa.get((r_.fecha_senal,r_.ticker),np.nan) for r_ in sub.itertuples()]
sub["acierto_hoy"]=((np.sign(sub.est_hoy)==np.sign(sub.gap_pct))).astype(int)
sub["err_hoy"]=(sub.est_hoy-sub.gap_pct).abs()
print("\n== 15 filas: sellado vs recomputado hoy")
print(sub[["fecha_senal","ticker","apertura_estimada_pct","est_hoy","gap_pct","acierto_gap","acierto_hoy","error_gap_pp","err_hoy"]].round(4).to_string(index=False))
print("\nsellado acierta %d/%d ; recomputado hoy acierta %d/%d"%(sub.acierto_gap.sum(),len(sub),sub.acierto_hoy.sum(),len(sub)))

tot_ac=int(v.acierto_gap.sum()); n=len(v)
nuevo_ac=tot_ac-int(sub.acierto_gap.sum())+int(sub.acierto_hoy.sum())
print("\nglobal sellado  %d/%d = %.2f%%  Wilson %s"%(tot_ac,n,100*tot_ac/n,tuple(round(100*x,1) for x in wilson_ci(tot_ac,n))))
print("global Yahoo-hoy %d/%d = %.2f%%  Wilson %s"%(nuevo_ac,n,100*nuevo_ac/n,tuple(round(100*x,1) for x in wilson_ci(nuevo_ac,n))))
mae0=v.error_gap_pp.mean()
err=v.error_gap_pp.copy()
err.loc[sub.index]=sub.err_hoy
print("MAE sellado %.4f -> Yahoo-hoy %.4f"%(mae0,err.mean()))
b=int(((sub.acierto_gap==1)&(sub.acierto_hoy==0)).sum()); cc=int(((sub.acierto_gap==0)&(sub.acierto_hoy==1)).sum())
print("McNemar sellado vs Yahoo-hoy sobre las 276: b=%d c=%d p=%.4f"%(b,cc,mcnemar_exact(b,cc)))
