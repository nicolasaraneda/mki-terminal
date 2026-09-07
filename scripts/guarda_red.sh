#!/usr/bin/env bash
# ============================================================
# scripts/guarda_red.sh — ¿estamos dentro de la ventana de sellado?
#
# LA REGLA: entre las 17:50 y las 20:30 de Chile de un día hábil el sistema
# sella (noticias 17:50 · snapshot 18:15 · reporte 18:25 · backup 18:40 ·
# vigía 19:00 · re-chequeo 20:30). Durante esa franja no corre nada pesado
# y, sobre todo, ninguna descarga: la suite de tests toca la red
# (`motor._datos_crudos` → `yf.download`, caché sólo en memoria) y competir
# con el snapshot por la misma fuente es la forma de romper un sello.
#
# El 3-sep-2026 el hook de pre-commit corrió la suite a las 17:57. El sello
# salió sano; la regla se cruzó igual. Esto es la corrección al ejecutable.
#
# CÓDIGO DE SALIDA (al revés de lo habitual, para que el `if` se lea):
#   0 → SÍ, estamos dentro de la ventana (la guarda dispara)
#   1 → no, estamos fuera
#
# RELOJ FALSO, para poder probarlo: MKI_AHORA_PRUEBA="YYYY-MM-DDTHH:MM",
# en hora de Chile. Sin la variable se lee el reloj real con TZ explícito,
# nunca la zona horaria de la máquina (el PC corre bajo WSL en UTC).
#
# ALCANCE DECLARADO: "día hábil" es lunes a viernes. No se consultan
# feriados. El error posible es bloquear un feriado en que no había sello:
# conservador por diseño, nunca al revés.
#
# PORTABILIDAD (5.0.3): bash-3.2-clean — el Mac corre este mismo archivo.
# El día de la semana del reloj falso se calcula con Zeller en aritmética
# de shell y no con `date -d`, que es de GNU y no existe en macOS.
# ============================================================
set -u

INICIO_MIN=$(( 17 * 60 + 50 ))   # 17:50
FIN_MIN=$((   20 * 60 + 30 ))    # 20:30

if [ -n "${MKI_AHORA_PRUEBA:-}" ]; then
  AHORA="$MKI_AHORA_PRUEBA"
  A_ANIO=$(( 10#${AHORA:0:4} ))
  A_MES=$((  10#${AHORA:5:2} ))
  A_DIA=$((  10#${AHORA:8:2} ))
  A_HORA=$(( 10#${AHORA:11:2} ))
  A_MIN=$((  10#${AHORA:14:2} ))
  # Zeller (Gregoriano) → 0 = domingo
  z_a=$(( (14 - A_MES) / 12 ))
  z_y=$(( A_ANIO - z_a ))
  z_m=$(( A_MES + 12 * z_a - 2 ))
  z=$(( (A_DIA + z_y + z_y/4 - z_y/100 + z_y/400 + (31 * z_m) / 12) % 7 ))
  DIA_SEMANA=$(( z == 0 ? 7 : z ))   # ISO: 1=lunes … 7=domingo
else
  DIA_SEMANA=$(TZ=America/Santiago date +%u)
  A_HORA=$(( 10#$(TZ=America/Santiago date +%H) ))
  A_MIN=$((  10#$(TZ=America/Santiago date +%M) ))
fi

MINUTOS=$(( A_HORA * 60 + A_MIN ))

if [ "$DIA_SEMANA" -ge 6 ]; then
  exit 1                      # fin de semana: no hay sello que proteger
fi
if [ "$MINUTOS" -ge "$INICIO_MIN" ] && [ "$MINUTOS" -le "$FIN_MIN" ]; then
  exit 0
fi
exit 1
