# ============================================================
# Rotación de logs (Etapa 5.0 WS6) — los logs no crecen infinito.
#
# Los jobs de launchd escriben por redirección de stdout (launchd mantiene
# el descriptor abierto), así que la rotación clásica por renombre no
# sirve: se usa copy-truncate — copiar el contenido a .1 y truncar el
# archivo en el lugar. Como launchd abre en modo append, el siguiente
# write cae limpio al inicio del archivo truncado.
#
# Cada entrypoint la llama para SU PROPIO log al arrancar: la rotación
# ocurre como mucho una vez por corrida, sin demonios ni sudo.
# ============================================================

import os
import shutil

MAX_BYTES_DEFAULT = 2 * 1024 * 1024   # 2 MB por log
COPIAS_DEFAULT = 2                    # .1 y .2 (≈ 6 MB máx por familia)


def rotar_log(ruta: str, max_bytes: int = MAX_BYTES_DEFAULT,
              copias: int = COPIAS_DEFAULT) -> bool:
    """Rota `ruta` si supera `max_bytes`. Devuelve True si rotó."""
    try:
        if not os.path.exists(ruta) or os.path.getsize(ruta) <= max_bytes:
            return False
        for i in range(copias - 1, 0, -1):
            origen, destino = f"{ruta}.{i}", f"{ruta}.{i + 1}"
            if os.path.exists(origen):
                os.replace(origen, destino)
        shutil.copyfile(ruta, f"{ruta}.1")
        with open(ruta, "w"):
            pass  # truncar en el lugar: el fd de launchd sigue siendo válido
        return True
    except OSError:
        return False  # un log que no rota no puede tumbar un job
