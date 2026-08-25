#!/usr/bin/env bash
# ============================================================
# Instala (o reinstala) los 6 jobs automáticos de MKI Terminal en launchd.
#
#   bash launchd/instalar.sh          (antes: zsh launchd/instalar.sh)
#
# Qué hace: toma cada plantilla launchd/com.mki.*.plist, reemplaza
# __MKI_DIR__ por la ruta real del proyecto (deducida de la ubicación de
# este script — funciona en cualquier máquina y carpeta), la copia a
# ~/Library/LaunchAgents y la (re)activa con launchctl. Idempotente:
# correrlo de nuevo reinstala limpio.
#
# PORTABILIDAD (Etapa 5.0.3): este instalador es SOLO macOS por naturaleza
# (launchd no existe en Linux). El equivalente Linux/WSL2 es
# systemd/instalar.sh. `./mki instalar` elige el correcto por `uname -s`;
# la guarda de abajo protege al que lo invoque a mano en la máquina errónea.
# ============================================================
set -eu

if [ "$(uname -s)" != "Darwin" ]; then
  echo "ERROR: launchd/instalar.sh es solo para macOS (uname -s = $(uname -s))." >&2
  echo "       En Linux/WSL2 el equivalente es:  bash systemd/instalar.sh" >&2
  exit 1
fi

DIR_LAUNCHD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIR_MKI="$(dirname "$DIR_LAUNCHD")"
DESTINO="$HOME/Library/LaunchAgents"
mkdir -p "$DESTINO" "$DIR_MKI/data"

echo "Proyecto: $DIR_MKI"
for plantilla in "$DIR_LAUNCHD"/com.mki.*.plist; do
  nombre="$(basename "$plantilla")"
  sed "s|__MKI_DIR__|$DIR_MKI|g" "$plantilla" > "$DESTINO/$nombre"
  launchctl unload "$DESTINO/$nombre" 2>/dev/null || true
  launchctl load "$DESTINO/$nombre"
  echo "  instalado y activado: $nombre"
done

echo ""
echo "Jobs registrados:"
launchctl list | grep com.mki
