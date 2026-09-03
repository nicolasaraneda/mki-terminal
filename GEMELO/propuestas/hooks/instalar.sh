#!/usr/bin/env bash
# instalar.sh — instala las dos extensiones de hooks del bundle de agentes v2.
# LO CORRE NICOLAS A MANO: el hook vigente se protege a si mismo (settings.json
# deniega Edit sobre .claude/hooks/ y el harness denego la escritura por Bash
# desde la sesion del 2-sep-2026). Muestra el diff, pide confirmacion, copia.
# bash 3.2 limpio (el Mac puede correrlo).
set -e
cd "$(dirname "$0")/../../.."
[ -f .claude/hooks/guardia-reglas.py ] || { echo "no estoy en la raiz del repo"; exit 1; }

echo "=== diff contexto-mki.sh (solo se agrega un bloque) ==="
diff -u .claude/hooks/contexto-mki.sh GEMELO/propuestas/hooks/contexto-mki.sh || true
echo
echo "=== diff guardia-reglas.py (solo se agrega el bloque 8) ==="
diff -u .claude/hooks/guardia-reglas.py GEMELO/propuestas/hooks/guardia-reglas.py || true
echo
printf 'Instalar los dos? [s/N] '
read -r r
case "$r" in
  s|S|si|SI|sí) ;;
  *) echo "no se instalo nada"; exit 1 ;;
esac
cp GEMELO/propuestas/hooks/contexto-mki.sh .claude/hooks/contexto-mki.sh
cp GEMELO/propuestas/hooks/guardia-reglas.py .claude/hooks/guardia-reglas.py
chmod +x .claude/hooks/contexto-mki.sh .claude/hooks/guardia-reglas.py
echo "instalado. Prueba: bash .claude/hooks/contexto-mki.sh | head -30"
echo "y: python3 -m pytest tests/test_hooks_propuestos.py -q"
