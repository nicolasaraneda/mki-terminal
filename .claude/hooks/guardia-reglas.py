#!/usr/bin/env python3
"""
guardia-reglas.py — hook PreToolUse de MKI Terminal.

Convierte las reglas duras del proyecto en una barrera, no en una instruccion
que el modelo pueda olvidar o que un prompt pueda persuadir.

Bloquea, sin excepcion:
  1. Editar o escribir motor.py y la logica de señales.
  2. Editar las bases selladas, los backups CSV y los snapshots.
  3. Editar este hook o el settings.json que lo instala (auto-proteccion).
  4. git push. Nicolas pushea a mano al cierre, despues de revisar el diff.
  5. git pull sobre el arbol de trabajo. Se usa git fetch y se lee origin/main.
  6. Historia destructiva: reset --hard, clean -fd, checkout --, filter-branch.
  7. SQL que reescriba filas selladas.

Para desactivarlo a conciencia hay que editar .claude/settings.json a mano.
Esa friccion es deliberada: la regla cero de este proyecto es que motor.py no
se toca, y una barrera que el agente puede abrir sola no es una barrera.

Salida: JSON de denegacion en stdout, motivo en stderr, exit 2.
Exit 0 sin salida cuando no hay nada que bloquear.
"""

import json
import os
import re
import sys

MOTIVOS = []


def denegar(motivo: str) -> None:
    salida = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": motivo,
        }
    }
    print(json.dumps(salida, ensure_ascii=False))
    print(motivo, file=sys.stderr)
    sys.exit(2)


# ------------------------------------------------------------------ archivos

RUTAS_PROHIBIDAS = [
    (r"(^|/)motor\.py$",
     "motor.py es intocable (regla cero). El campeon 4.6.0 sella en produccion "
     "durante toda la etapa 6.0.0. Si el cambio es una preservacion de "
     "comportamiento, hay que demostrarla byte a byte y desactivar este hook a "
     "mano en .claude/settings.json, con acta en DECISIONES.md."),

    (r"(^|/)(senales|noticias)\.db$",
     "Las bases selladas no se editan con herramientas de archivo. Un error "
     "historico se documenta como errata en DECISIONES.md; la fila no se toca."),

    (r"(^|/)data/backups/",
     "data/backups/ son los CSV de respaldo de filas selladas. No se reescriben."),

    (r"(^|/)data/snapshots?/",
     "Los snapshots sellados no se reescriben. Nunca."),

    (r"(^|/)\.claude/(settings\.json|hooks/)",
     "El guardia no se desactiva a si mismo. Si de verdad hay que levantarlo, "
     "lo edita Nicolas a mano."),

    (r"(^|/)\.env$",
     ".env tiene las 3 claves reales y vive en chmod 600, fuera de git."),
]


def revisar_archivo(ruta: str) -> None:
    if not ruta:
        return
    norm = ruta.replace("\\", "/")
    for patron, motivo in RUTAS_PROHIBIDAS:
        if re.search(patron, norm):
            denegar(f"BLOQUEADO por guardia-reglas: {ruta}\n{motivo}")


# ---------------------------------------------------------------------- bash

COMANDOS_PROHIBIDOS = [
    (r"\bgit\s+push\b",
     "Claude no pushea. Nicolas pushea a mano al cierre de cada sesion, "
     "despues de revisar el diff. Esa cadencia se acordo a raiz de la perdida "
     "del SSD, que se llevo 4 commits nunca pusheados. En el PC la rama es "
     "migracion-wsl, jamas main."),

    (r"\bgit\s+pull\b",
     "git pull altera el arbol de trabajo, que es el codigo que los timers "
     "ejecutan. Usa git fetch y lee desde origin/main."),

    (r"\bgit\s+reset\s+--hard\b",
     "reset --hard destruye trabajo no commiteado. Este proyecto ya perdio "
     "4 commits una vez."),

    (r"\bgit\s+clean\s+-[a-z]*[fd]",
     "git clean borra archivos no rastreados sin vuelta atras."),

    (r"\bgit\s+checkout\s+--\s",
     "checkout -- descarta cambios locales sin confirmacion."),

    (r"\bgit\s+(filter-branch|rebase\s+-i|push\s+--force)",
     "Reescribir historia no es una operacion de agente en este repo."),

    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r",
     "rm -rf no se corre desde el agente en este repo."),

    (r"(?is)\b(update|delete\s+from|drop\s+table|alter\s+table)\b.{0,80}"
     r"\b(senales|snapshot|sellad|verificacion|titular)",
     "Eso reescribe filas selladas. Las filas selladas jamas se reescriben: "
     "un error historico se documenta como errata."),

    (r"if_exists\s*=\s*['\"]replace['\"]",
     "to_sql con if_exists='replace' borra la tabla entera."),
]


def revisar_bash(cmd: str) -> None:
    if not cmd:
        return
    for patron, motivo in COMANDOS_PROHIBIDOS:
        if re.search(patron, cmd):
            denegar(f"BLOQUEADO por guardia-reglas: {cmd.strip()[:200]}\n{motivo}")


# ---------------------------------------------------------------------- main

def main() -> None:
    try:
        datos = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # ante duda, no interfiere

    herramienta = datos.get("tool_name", "")
    entrada = datos.get("tool_input", {}) or {}

    if herramienta in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        for clave in ("file_path", "notebook_path", "path"):
            revisar_archivo(str(entrada.get(clave, "") or ""))
        for edicion in entrada.get("edits", []) or []:
            if isinstance(edicion, dict):
                revisar_archivo(str(edicion.get("file_path", "") or ""))

    elif herramienta in ("Bash", "BashOutput"):
        revisar_bash(str(entrada.get("command", "") or ""))

    sys.exit(0)


if __name__ == "__main__":
    main()
