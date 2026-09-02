import sys; sys.path.insert(0,"/home/nicolasaraneda/dev/mki-terminal")
import os; os.chdir("/home/nicolasaraneda/dev/mki-terminal")
import motor, pandas as pd
d = motor._datos_crudos(("^SOX",))
s = d["^SOX"] if "^SOX" in d.columns else d.iloc[:,0]
r = s.pct_change()*100
print(r.loc["2026-07-27":"2026-08-05"].round(3).to_string())
print("\n^SOX bares presentes 2026-07-28..2026-08-05:", [str(x.date()) for x in s.loc["2026-07-28":"2026-08-05"].index])
d2 = motor._datos_crudos(("000660.KS",))
r2 = (d2["000660.KS"] if "000660.KS" in d2.columns else d2.iloc[:,0]).pct_change()*100
print("\n000660.KS:"); print(r2.loc["2026-07-29":"2026-08-05"].round(3).to_string())
