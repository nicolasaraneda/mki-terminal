# ============================================================
# dinero/registro_intentos.py — el registro de intentos del RIEL LARGO.
#
# POR QUÉ ES UN REGISTRO NUEVO Y NO UN INCREMENTO DEL QUE YA HAY.
#
# El proyecto ya lleva un registro de intentos para el Deflated Sharpe:
# `GEMELO/relevo_asiatico.N_INTENTOS_ACUMULADO`, que al abrir esta corrida
# valía 352, y del que cuelga `backtest/veredicto_51.N_INTENTOS_51` = 358.
# Ese registro cuenta las hipótesis probadas sobre el GAP ASIÁTICO DE UNA
# NOCHE. Sumarle acá las especificaciones de una señal de 20 y 60 días
# hábiles sobre instrumentos de EE.UU. haría dos cosas malas a la vez:
#
#   (a) mezclaría dos familias de hipótesis que no comparten estimando ni
#       horizonte ni universo, y el DSR deflacta por intentos SOBRE LA
#       MISMA búsqueda; y
#   (b) movería un entero del que dependen doce bloques publicados, y la
#       regla de la casa es que si se mueve n se mueven los doce bloques o
#       no se mueve.
#
# Así que el riel largo lleva su propia cuenta, con su vínculo declarado.
# **Si los dos registros deben o no fusionarse es una DECISIÓN PENDIENTE de
# Nicolás** (`GEMELO/resultados/espera_firma.md`): la respuesta depende de
# si se considera que ambas búsquedas exploran el mismo espacio de
# hipótesis, y esa es una pregunta de diseño, no de código.
#
# REGLA: cada especificación probada suma, incluidas las descartadas y las
# que salieron mal. Los intentos se cuentan honestamente o el DSR miente.
# ============================================================

# Familia hermana, para que el vínculo esté escrito y no en la memoria de
# nadie. NO se importa GEMELO: es una nota, no una dependencia.
FAMILIA_HERMANA = ("GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO = 352 al "
                   "6-sep-2026; backtest.veredicto_51.N_INTENTOS_51 = 358. "
                   "Cuentan el gap asiático de UNA NOCHE, no este riel.")

REGISTRO_INTENTOS = (
    # (tramo, cuántos, procedencia)
    ("senal_larga_v1 — bloque 6 de la corrida 10", 3,
     "Tres especificaciones DECLARADAS POR NOMBRE en "
     "GEMELO/preregistro/senal_larga_v1.md §3 antes de correr la primera: "
     "L1 (contagio directo del eslabón aguas arriba), L2 (impulso relativo "
     "del eslabón contra la cesta) y L3 (dispersión entre eslabones). "
     "Suman las tres, hayan servido o no."),
)

N_INTENTOS_RIEL_LARGO = sum(n for _, n, _ in REGISTRO_INTENTOS)
