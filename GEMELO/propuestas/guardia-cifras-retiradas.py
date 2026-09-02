#!/usr/bin/env python3
"""
guardia-cifras-retiradas.py — extensión PROPUESTA del hook PreToolUse.

NO ESTÁ INSTALADA. El hook vigente (`.claude/hooks/guardia-reglas.py`) se
protege a sí mismo y a `.claude/settings.json`: sólo Nicolás los edita. Este
archivo es la extensión lista para que la instale, si la firma: bloquea
cualquier Edit/Write sobre un documento publicado (README.md,
GEMELO/resultados/estado_epistemico.md, la skill cifras-canonicas) cuya
nueva versión REINTRODUZCA una cifra retirada (`GEMELO/cifras_retiradas.md`)
sin marca de retiro a ±2 líneas.

Instalación (Nicolás, a mano): en `.claude/settings.json`, agregar un
segundo comando al mismo matcher `Edit|Write|...` del hook PreToolUse:
    "command": "python3 \\"${CLAUDE_PROJECT_DIR}/GEMELO/propuestas/guardia-cifras-retiradas.py\\""
El hook se EXTIENDE, no se reemplaza. Test de la lógica compartida:
`tests/test_cifras_arbitro.py::test_contraprueba_el_detector_caza_una_reintroduccion`.

Salida: JSON de denegación en stdout, motivo en stderr, exit 2. Exit 0 sin
salida cuando no hay nada que bloquear.
"""
import json
import os
import sys

RAIZ = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
try:
    import cifras
except Exception:            # sin el árbitro no hay qué comprobar: no bloquear
    sys.exit(0)

PUBLICADOS = tuple(cifras.DOCUMENTOS_PUBLICADOS)


def denegar(motivo: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": "deny",
                                              "permissionDecisionReason": motivo}}, ensure_ascii=False))
    print(motivo, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        entrada = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    herramienta = entrada.get("tool_name", "")
    args = entrada.get("tool_input", {}) or {}
    if herramienta not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)
    ruta = (args.get("file_path") or "").replace("\\", "/")
    if not any(ruta.endswith(p) for p in PUBLICADOS):
        sys.exit(0)
    nuevo = args.get("content") or args.get("new_string") or ""
    if not nuevo:
        sys.exit(0)
    hallazgos = cifras.reintroducciones(nuevo)
    if hallazgos:
        lista = "\n".join(f"  línea {i}: [{pat}] {txt}" for i, pat, txt in hallazgos[:5])
        denegar("BLOQUEADO por guardia-cifras-retiradas: la edición reintroduce una cifra "
                f"retirada en {ruta} sin marca de retiro (GEMELO/cifras_retiradas.md):\n{lista}")
    sys.exit(0)


if __name__ == "__main__":
    main()
