# ============================================================
# GEMELO — capa de INVESTIGACIÓN de la Etapa 6.0.0.
#
# AISLAMIENTO (regla del WS2a): este paquete NO importa snapshot.py,
# senales.py, alertas.py ni nada del camino de sellado, y no escribe en
# ninguna base. Una falla aquí —trece feeds nuevos son trece formas nuevas
# de que Yahoo falle a las 18:15— jamás puede afectar el sello nocturno del
# campeón. Donde eso obligue a duplicar lógica de descarga en vez de
# reutilizarla, se duplica: el acoplamiento cuesta más que la duplicación.
#
# Hay un test que falla si este paquete importa el camino de sellado.
# ============================================================
