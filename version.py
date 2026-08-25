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
# 5.0.2: cierre de heridas pre-migración — timeout global de red en el job
#   de noticias (un fetch jamás cuelga el label de launchd) y retractación
#   que distingue emisión de confirmación (la discrepancia del 06-ago).
# 5.0.3: reactivación en PC — scripts portados de zsh a bash con ramificación
#   por `uname -s` (launchd en macOS / systemd en Linux). El campo sellado
#   `plataforma_version` es una afirmación de PROCEDENCIA: dice qué código
#   produjo la fila, y las filas selladas jamás se reescriben. Durante la
#   ventana de sombra el Mac sellará 5.0.2 y el PC 5.0.3; esa diferencia es
#   LEGÍTIMA (el código difiere mientras `migracion-wsl` no se funda con
#   `main`) y `comparar_sombra.py` debe esperarla, no reportarla como
#   divergencia. Detalle en DECISIONES.md, Etapa 5.0.3 §8.
PLATAFORMA_VERSION = "5.0.3"
