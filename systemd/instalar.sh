#!/usr/bin/env bash
# ============================================================
# Instala (o reinstala) los 6 jobs automáticos de MKI Terminal en systemd
# de usuario. Equivalente Linux/WSL2 de launchd/instalar.sh.
#
#   bash systemd/instalar.sh                # instala o reinstala
#   bash systemd/instalar.sh --desinstalar  # quita todo
#
# Toma cada plantilla systemd/mki-*.{service,timer}, reemplaza __MKI_DIR__
# por la ruta real del proyecto (deducida de la ubicación de este script),
# la copia a ~/.config/systemd/user y la activa. Idempotente.
#
# NO usa sudo. NO toca units del sistema. Todo vive bajo el usuario.
# ============================================================
set -euo pipefail

DIR_SYSTEMD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIR_MKI="$(dirname "$DIR_SYSTEMD")"
DESTINO="$HOME/.config/systemd/user"

JOBS=(mki-noticias mki-snapshot mki-reporte mki-backup mki-vigia mki-vigia-rechequeo)

if ! command -v systemctl >/dev/null 2>&1; then
  echo "ERROR: no hay systemctl. En WSL2 esto significa que systemd no está activo." >&2
  echo "       Revisa /etc/wsl.conf → [boot] systemd=true y corre 'wsl --shutdown'" >&2
  echo "       desde Windows para reiniciar la VM." >&2
  exit 1
fi

if [[ "$(ps -p 1 -o comm=)" != "systemd" ]]; then
  echo "ERROR: PID 1 no es systemd (es '$(ps -p 1 -o comm=)')." >&2
  echo "       Mismo remedio: [boot] systemd=true en /etc/wsl.conf + wsl --shutdown." >&2
  exit 1
fi

# --- desinstalación -----------------------------------------------------
if [[ "${1:-}" == "--desinstalar" ]]; then
  for job in "${JOBS[@]}"; do
    systemctl --user disable --now "$job.timer" 2>/dev/null || true
    rm -f "$DESTINO/$job.timer" "$DESTINO/$job.service"
    echo "  quitado: $job"
  done
  systemctl --user daemon-reload
  echo ""
  echo "Los 6 jobs fueron desinstalados. El linger del usuario NO se tocó:"
  echo "  quitarlo a mano con:  loginctl disable-linger $USER"
  exit 0
fi

# --- instalación --------------------------------------------------------
echo "Proyecto: $DIR_MKI"

if [[ ! -x "$DIR_MKI/venv/bin/python" ]]; then
  echo "ERROR: no existe $DIR_MKI/venv/bin/python" >&2
  echo "       Crea el venv antes de instalar los timers:" >&2
  echo "         python -m venv venv && source venv/bin/activate" >&2
  echo "         pip install -r requirements.txt" >&2
  exit 1
fi

mkdir -p "$DESTINO" "$DIR_MKI/data"

for job in "${JOBS[@]}"; do
  for tipo in service timer; do
    plantilla="$DIR_SYSTEMD/$job.$tipo"
    [[ -f "$plantilla" ]] || { echo "ERROR: falta $plantilla" >&2; exit 1; }
    sed "s|__MKI_DIR__|$DIR_MKI|g" "$plantilla" > "$DESTINO/$job.$tipo"
  done
done

systemctl --user daemon-reload

for job in "${JOBS[@]}"; do
  systemctl --user reenable "$job.timer" >/dev/null
  systemctl --user restart "$job.timer"
  echo "  instalado y activado: $job.timer"
done

# El linger es lo que permite que los timers de usuario corran sin sesión
# abierta. Sin esto, cerrar la terminal mata los jobs.
if ! loginctl show-user "$USER" -p Linger --value 2>/dev/null | grep -q yes; then
  loginctl enable-linger "$USER"
  echo ""
  echo "  linger activado para $USER (los timers corren sin sesión abierta)"
fi

echo ""
echo "Timers registrados (deben aparecer los 6, con NEXT en el próximo hábil):"
systemctl --user list-timers 'mki-*' --all --no-pager
