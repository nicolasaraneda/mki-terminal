#!/usr/bin/env bash
# contexto-mki.sh — hook SessionStart de MKI Terminal.
# Imprime el estado real de la maquina al abrir sesion, para que ninguna
# sesion tenga que adivinar si esta maquina emite o no.
# Todo defensivo: nada de esto puede hacer fallar el arranque.

set +e
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null

echo "=== ESTADO MKI TERMINAL ==="

case "$(uname -s)" in
  Darwin) MAQ="Mac" ;;
  Linux)
    if grep -qi microsoft /proc/version 2>/dev/null; then MAQ="PC Windows/WSL2"
    else MAQ="Linux"; fi ;;
  *) MAQ="$(uname -s)" ;;
esac
echo "Maquina   : $MAQ"
echo "Rama      : $(git branch --show-current 2>/dev/null || echo 'sin git')"
echo "HEAD      : $(git log --oneline -1 2>/dev/null || echo '-')"
sucio=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo "Arbol     : ${sucio} archivo(s) sin commitear"
echo "Python    : $(python3 --version 2>&1 | head -1)"

# --- modo de emision: se le PREGUNTA a modo.py, no se adivina -------------
# Leccion del 30-ago: inferir el modo del .env o de una acta da respuestas
# opuestas. modo.py es la fuente de verdad y es lo unico que se consulta.
PY=""
[ -x venv/bin/python ] && PY="venv/bin/python"
[ -z "$PY" ] && command -v python3 >/dev/null 2>&1 && PY="python3"
MODO=""
[ -n "$PY" ] && MODO=$("$PY" -c "import modo; print(modo.modo_actual())" 2>/dev/null | tail -1)

if [ -n "$MODO" ]; then
  echo "Modo      : $MODO   (segun modo.py)"
  case "$MODO" in
    titular) echo "            -> esta maquina EMITE. Es el titular." ;;
    sombra)  echo "            -> esta maquina NO emite." ;;
  esac
else
  echo "Modo      : no se pudo preguntar a modo.py"
  echo "            NO lo deduzcas del .env ni de las actas: dan respuestas"
  echo "            opuestas. Corre: python -c 'import modo; print(modo.modo_actual())'"
fi

if command -v systemctl >/dev/null 2>&1; then
  t=$(systemctl --user list-timers 'mki-*' --no-legend 2>/dev/null | wc -l | tr -d ' ')
  echo "Timers    : ${t} timer(s) mki-* instalado(s)"
fi

if [ -f senales.db ] && command -v sqlite3 >/dev/null 2>&1; then
  sello=$(sqlite3 -readonly senales.db "SELECT MAX(fecha) FROM verificacion_apertura;" 2>/dev/null)
  n=$(sqlite3 -readonly senales.db "SELECT COUNT(*) FROM verificacion_apertura;" 2>/dev/null)
  [ -n "$sello" ] && echo "Ultimo sello: ${sello}   N verificaciones: ${n:-?}"
fi

if [ -f ESTADO.md ]; then
  echo
  echo "--- ESTADO.md (primeras 40 lineas) ---"
  sed -n '1,40p' ESTADO.md
else
  echo
  echo "AVISO: no hay ESTADO.md. Usa el agente 'orientador' para saber donde"
  echo "quedaste, y crealo al cerrar con la skill /cierre-sesion."
fi

cat <<'AVISOS'

SWITCH COMPLETO: este PC es el titular, trabaja en main, emite y sella. El
Mac quedo fuera. Las actas 36 y 37 describen el estado ANTERIOR al segundo
movimiento: donde una acta y la maquina no coincidan, MANDA LA MAQUINA, y la
discrepancia se registra como errata.

Cambiar el modo de emision o tocar timers es operacion de Nicolas, nunca de
un agente, ni de paso dentro de otra tarea.

Reglas duras activas por hook: motor.py intocable, filas selladas jamas
reescritas, sin git push (pushea Nicolas), sin git pull sobre el arbol.
Cifras: no se citan de memoria, se leen del README. Skill `cifras-canonicas`.
Antes de cerrar cualquier tanda: agente `guardian-constitucion`.
===========================
AVISOS
exit 0
