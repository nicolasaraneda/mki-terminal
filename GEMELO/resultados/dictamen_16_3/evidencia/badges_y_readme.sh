#!/bin/bash
# Fase B.5 del encargo (§90.4): badges releídos de la máquina, los TRES valores juntos, y regeneración de los README.
set -euo pipefail
cd /home/nicolasaraneda/dev/mki-terminal
echo "collect-only (árbol real, con los tests nuevos):"; date
N=$(venv/bin/python -m pytest tests/ --collect-only -q -p no:cacheprovider 2>/dev/null | tail -1)
echo "$N"
NUM=$(echo "$N" | grep -oE '^[0-9]+')
PLAT=$(venv/bin/python -c "from version import PLATAFORMA_VERSION; print(PLATAFORMA_VERSION)")
HOY=$(date +%F)
venv/bin/python - "$NUM" "$PLAT" "$HOY" <<'PY'
import json, sys
n, plat, hoy = int(sys.argv[1]), sys.argv[2], sys.argv[3]
ruta = "docs/readme/badges_congelados.json"
b = json.load(open(ruta, encoding="utf-8"))
print("antes:", {k: b[k] for k in ("tests_recolectados", "plataforma_version", "leido_el")})
b["tests_recolectados"], b["plataforma_version"], b["leido_el"] = n, plat, hoy
json.dump(b, open(ruta, "w", encoding="utf-8"), indent=2, ensure_ascii=False); open(ruta, "a").write("\n")
print("después:", {k: b[k] for k in ("tests_recolectados", "plataforma_version", "leido_el")})
PY
venv/bin/python scripts/generar_readme.py
venv/bin/python scripts/generar_readme.py --verificar
git diff --stat README.md README.es.md docs/readme/badges_congelados.json
echo "=== tsc ==="; (cd frontend && node_modules/.bin/tsc --noEmit -p tsconfig.app.json && echo "tsc exit 0")
echo "=== test_motor ==="; venv/bin/python tests/test_motor.py 2>&1 | tail -4
date
