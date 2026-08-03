# ============================================================
# Versionado del sistema (Etapa 4.6)
#
# Estas constantes se guardan en cada snapshot de señales.db para que las
# métricas del Historial nunca mezclen predicciones de lógicas distintas.
# Se incrementan MANUALMENTE:
#  - MODELO_VERSION: cuando cambia la lógica de una señal (betas, régimen,
#    divergencias, puntajes, umbrales, ventanas por defecto).
#  - FEATURE_VERSION: cuando cambia cómo se construye un insumo (p. ej.
#    sentimiento con decaimiento, filtro de noticias, residualización).
#  - UNIVERSO_VERSION: cuando entra/sale un ticker o cambia su rol
#    (nivel, tipo, duplicado_de, benchmark).
# ============================================================

MODELO_VERSION = "4.6.0"
FEATURE_VERSION = "4.6.0"
UNIVERSO_VERSION = "4.6.0"

# Etapa 5.0: versionado DUAL. La plataforma (infraestructura, jobs, UI,
# reporte) evoluciona; el MODELO sigue congelado en 4.6.0 — el track record
# limpio está encadenado a esa versión y las métricas jamás mezclan
# versiones. Subir MODELO_VERSION es una decisión aparte (Etapa 5.1+).
# 5.0.1: vigía con retractación (una alerta jamás queda sin epílogo).
PLATAFORMA_VERSION = "5.0.1"
