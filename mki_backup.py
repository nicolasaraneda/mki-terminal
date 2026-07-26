# ============================================================
# Red de seguridad git REAL (Etapa 5.0 WS2.5) — com.mki.backup, 18:40
# hábiles, después del snapshot (18:15) que refresca los CSV.
#
# Hace UNA cosa: si data/backups/ cambió, lo commitea. La auditoría 13–24
# jul encontró que los CSV se commitearon una sola vez (5-jul) — la "red de
# seguridad versionada" no existía de verdad hasta este job.
#
# Alcance estricto: SOLO los paths de data/backups (el commit lleva pathspec,
# así que nada más entra aunque hubiera otras cosas staged). Jamás push:
# publicar es un acto manual del usuario.
# ============================================================

import os
import subprocess
import sys
from datetime import date, datetime, timezone

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))


def _git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", DIRECTORIO, *args],
                          capture_output=True, text=True)


def main() -> int:
    from registro import rotar_log
    rotar_log(os.path.join(DIRECTORIO, "data", "backup.log"))
    print(f"[{datetime.now(timezone.utc).isoformat()}] mki_backup.py", flush=True)
    r = _git("add", "--", "data/backups")
    if r.returncode:
        print(f"  git add falló: {r.stderr.strip()}")
        return 1
    if _git("diff", "--cached", "--quiet", "--", "data/backups").returncode == 0:
        print("  sin cambios en data/backups — nada que commitear")
        return 0
    mensaje = f"Backup diario {date.today().isoformat()}"
    r = _git("commit", "-m", mensaje, "--", "data/backups")
    if r.returncode:
        print(f"  git commit falló: {r.stderr.strip() or r.stdout.strip()}")
        return 1
    print(f"  commit creado: {mensaje}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
