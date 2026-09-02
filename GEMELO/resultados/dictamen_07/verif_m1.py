import sys, os
sys.path.insert(0, "/home/nicolasaraneda/dev/mki-terminal")
import numpy as np, pandas as pd
import GEMELO.datos as gd
from universo import UNIVERSO

cache = "/home/nicolasaraneda/dev/mki-terminal/GEMELO/cache/cierres_853b6558513c5e9f.csv"
viejo = pd.read_csv(cache, index_col=0, parse_dates=True)
nuevo = gd.descargar_cierres(tuple(UNIVERSO), gd.ANIOS_DATOS, usar_cache=False)
nuevo.to_csv("/tmp/nuevo_27.csv")
print("viejo", viejo.shape, viejo.index.min().date(), viejo.index.max().date())
print("nuevo", nuevo.shape, nuevo.index.min().date(), nuevo.index.max().date())
