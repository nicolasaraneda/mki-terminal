#!/bin/zsh
# ============================================================
# Instala (o reinstala) los 5 jobs automáticos de MKI Terminal.
#
#   zsh launchd/instalar.sh
#
# Qué hace: toma cada plantilla launchd/com.mki.*.plist, reemplaza
# __MKI_DIR__ por la ruta real del proyecto (deducida de la ubicación de
# este script — funciona en cualquier máquina y carpeta), la copia a
# ~/Library/LaunchAgents y la (re)activa con launchctl. Idempotente:
# correrlo de nuevo reinstala limpio.
# ============================================================
set -e

DIR_LAUNCHD="$(cd "$(dirname "$0")" && pwd)"
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
