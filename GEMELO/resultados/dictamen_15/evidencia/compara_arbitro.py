# Comparación clave por clave de los dos volcados del árbitro (scratchpad).
import json
import os

aqui = os.path.dirname(os.path.abspath(__file__))
antes = json.load(open(os.path.join(aqui, "arbitro_antes.json"), encoding="utf-8"))
despues = json.load(open(os.path.join(aqui, "arbitro_despues.json"), encoding="utf-8"))
assert set(antes) == set(despues), set(antes) ^ set(despues)
for clave in sorted(antes):
    igual = antes[clave] == despues[clave]
    print(f"{'IDENTICA' if igual else 'CAMBIA  '}  {clave}")
s = antes["sellada"]
print("sellada: n =", s["n"], "dias =", s["dias"], "hasta_sello =", s["hasta_sello"],
      "ventaja_pp =", s["ventaja_pp"], "ic_dia =", s["ventaja_ic_dia"],
      "mcnemar_p =", s["mcnemar_p"])
