# Dictamen del `estadistico-adversario` — séptima corrida (2-sep-2026, ~02:45)

`DICTAMEN.md` es el texto íntegro del dictamen sobre los Frentes A–E,
transcrito sin editar. Los `verif_*.py` son los scripts con los que el
adversario reprodujo o refutó cada cifra, copiados de `/tmp` tal cual
(eran desechables; se preservan porque son el mecanismo INDEPENDIENTE de
verificación, y un mecanismo que se pierde no se puede volver a correr).
Dependen de rutas relativas al repo; algunos escriben en `/tmp`.

| script | qué verifica |
|---|---|
| `verif_m1.py`, `verif_m1b.py`, `verif_m1c.py`, `verif_m1d.py` | M1: retornos sobre el índice propio de cada ticker; celdas históricas distintas; factor real de 000660.KS; las dos cachés a 95 s |
| `verif_m6.py` | M6: perfil completo de las 130 barras, unicidad del 31-jul, noches de control |
| `verif_iv.py`, `verif_sox.py` | las 15 filas del 28/31-ago; McNemar b=8, c=7 |
| `verif_b1.py` … `verif_b4.py` | ancla del Frente B; α empírico a n_sim 1.000/3.000; R2 sobre el ancla |
| `verif_c1.py`, `verif_c2.py` | trayectoria celda a celda; sensibilidad de C al Frente A |
| `verif_d1.py`, `verif_d2.py` | AC1 y su bootstrap; α por estadístico con Wilson |
| `verif_e.py` | estimandos; permutación exacta a nivel de bolsa (p mínimo 1/13) |
