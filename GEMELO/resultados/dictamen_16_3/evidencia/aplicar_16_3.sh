#!/bin/bash
# Aplicación de la corrida 16-3 al árbol real: copia desde el worktree wt163 los archivos
# listados (nunca .db, nunca data/backups/, nunca .env). Se corre UNA vez, con los
# dictámenes y la suite del worktree a la vista. Imprime las horas (corte de método).
set -euo pipefail
WT=/tmp/claude-1000/-home-nicolasaraneda-dev-mki-terminal/74ee956a-2055-4ebb-81f1-c79c5ee891cf/scratchpad/wt163
REAL=/home/nicolasaraneda/dev/mki-terminal
ARCHIVOS=(
  backtest/linea_base.py
  alertas.py
  api/main.py
  api/CONTRATO.md
  app.py
  frontend/src/vistas/SellosDinero.tsx
  docs/readme/README.en.tmpl.md
  tests/conftest.py
  tests/bases_de_prueba.py
  tests/test_fuente_unica_16_3.py
  tests/test_higiene_bases_16_3.py
  tests/test_integridad_no_verificable_16_3.py
  tests/test_fallback_dashboard_16_3.py
  tests/test_api.py
  tests/test_reporte.py
  tests/test_linea_base.py
  tests/test_conocibilidad.py
  tests/test_frescura.py
  tests/test_guarda_puntaje.py
  tests/test_bifurcaciones.py
  tests/test_banco_clausulas.py
  tests/test_epistemico.py
  tests/test_importador_roundtrip.py
  tests/test_restaurar_backup.py
  tests/test_segundo_sello.py
  GEMELO/resultados/tesis.md
  GEMELO/resultados/espera_firma.md
  GEMELO/propuestas/parches/version_reglas_16_3.diff
  GEMELO/propuestas/parches/version_reglas_16_3.md
  ESTADO.md
  GEMELO/resultados/bitacora_16_3.md
)
echo "corte de método (primer archivo copiado):"; date
for a in "${ARCHIVOS[@]}"; do
  mkdir -p "$REAL/$(dirname "$a")"
  cp "$WT/$a" "$REAL/$a"
done
mkdir -p "$REAL/GEMELO/resultados/dictamen_16_3/evidencia"
cp -r "$WT/GEMELO/resultados/dictamen_16_3/." "$REAL/GEMELO/resultados/dictamen_16_3/"
echo "último archivo copiado:"; date
cd "$REAL" && for a in "${ARCHIVOS[@]}"; do stat -c '%y %n' "$a"; done | sort | sed -n '1p;$p'
echo "huellas:"; cd "$REAL" && sha256sum "${ARCHIVOS[@]}"
