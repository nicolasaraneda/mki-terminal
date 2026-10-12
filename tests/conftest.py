# ============================================================
# tests/conftest.py — el marcador `red` y su guarda ejecutable.
#
# Deuda de la corrida 09 (encargo 10 §2): la suite toca la red —
# `motor._datos_crudos` llama a `yf.download` con caché sólo en memoria— y
# el hook de pre-commit la corrió a las 17:57 del 3-sep-2026, DENTRO de la
# ventana de sellado (17:50–20:30 de Chile en día hábil). El sello salió
# sano, pero la regla se cruzó.
#
# La corrección va al ejecutable, no a la prosa. Dos piezas:
#
#   1. Este archivo: cada test que abre una conexión saliente queda
#      OBLIGADO a llevar `@pytest.mark.red`. La verificación no confía en
#      que la excepción se propague —yfinance se traga los errores de red y
#      devuelve un DataFrame vacío, así que bloquear el socket no basta
#      para detectar nada—: se REGISTRA el intento y se falla en el
#      teardown. Un test que toca la red y no lo declara es un test que
#      miente sobre su superficie.
#
#      DÓNDE SE ESCUCHA, y esto no es un detalle de implementación: la
#      PRIMERA versión de esta guarda espiaba sólo `socket.socket.connect`
#      y el censo de la suite entera salió VACÍO — cero tests tocando la
#      red, en una suite que sabemos que descarga de Yahoo. La razón es que
#      **yfinance 1.5.1 habla por `curl_cffi`, o sea libcurl, en C**: abre
#      sus sockets adentro de la biblioteca nativa y el módulo `socket` de
#      Python no se entera nunca. Un instrumento que mide donde el tráfico
#      no pasa informa paz. Por eso se escucha en DOS niveles: los sockets
#      de Python (urllib y feedparser, httpx y el cliente de Anthropic) y
#      la sesión de curl_cffi (yfinance).
#
#   2. `scripts/guarda_red.sh` + el hook: dentro de la ventana, los tests
#      marcados `red` no se corren (`-m "not red"`), con un mensaje que
#      nombra la regla.
#
# Interruptores (por variable de entorno, para no tener que editar código):
#   MKI_RED_LIBRE=1      desactiva la guarda entera.
#   MKI_RED_INFORME=ruta modo censo: no falla, sólo anota los nodeid que
#                        tocaron la red. Es el modo con el que se descubrió
#                        qué marcar, en vez de decidirlo por grep.
# ============================================================
import os
import socket

import pytest

_LOCALES = {"127.0.0.1", "::1", "localhost", "0.0.0.0", ""}

# Se guarda una sola vez, al importar, para que dos instalaciones de la
# guarda no se envuelvan entre sí.
_connect_real = socket.socket.connect
_connect_ex_real = socket.socket.connect_ex

# nodeid del test en curso -> lista de destinos contactados.
_intentos: dict = {}
_actual = {"nodeid": None}


def _anotar(direccion):
    nodeid = _actual["nodeid"]
    if nodeid is None:
        return
    host = direccion[0] if isinstance(direccion, tuple) and direccion else direccion
    if isinstance(host, str) and host in _LOCALES:
        return
    if not isinstance(host, (str, bytes)):
        return  # sockets unix y familias raras: no son salida a internet
    _intentos.setdefault(nodeid, set()).add(
        host.decode() if isinstance(host, bytes) else host)


def _connect_espia(self, direccion):
    _anotar(direccion)
    return _connect_real(self, direccion)


def _connect_ex_espia(self, direccion):
    _anotar(direccion)
    return _connect_ex_real(self, direccion)


def _anotar_url(url):
    """Para los clientes HTTP que no pasan por el socket de Python."""
    texto = str(url)
    host = texto.split("//")[-1].split("/")[0].split(":")[0]
    _anotar((host, 0))


def _instalar_curl_cffi():
    """yfinance habla por libcurl: sin este gancho, la guarda es ciega
    justo en la biblioteca que motiva la regla. Devuelve True si quedó
    instalado, para que un test pueda comprobarlo sin salir a la red."""
    try:
        from curl_cffi import requests as ccr
    except Exception:
        return False
    if getattr(ccr.Session.request, "_es_espia_mki", False):
        return True
    real = ccr.Session.request

    def espia(self, method, url, *a, **k):
        _anotar_url(url)
        return real(self, method, url, *a, **k)

    espia._es_espia_mki = True
    espia._real = real
    ccr.Session.request = espia
    return True


def curl_cffi_vigilado() -> bool:
    try:
        from curl_cffi import requests as ccr
    except Exception:
        return False
    return getattr(ccr.Session.request, "_es_espia_mki", False)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "red: el test abre conexiones salientes (Yahoo, RSS). Queda fuera "
        "de la corrida durante la ventana de sellado 17:50-20:30 de Chile "
        "en día hábil — ver scripts/guarda_red.sh.")
    if os.environ.get("MKI_RED_LIBRE") == "1":
        return
    socket.socket.connect = _connect_espia
    socket.socket.connect_ex = _connect_ex_espia
    _instalar_curl_cffi()


def pytest_unconfigure(config):
    socket.socket.connect = _connect_real
    socket.socket.connect_ex = _connect_ex_real
    try:
        from curl_cffi import requests as ccr
        real = getattr(ccr.Session.request, "_real", None)
        if real is not None:
            ccr.Session.request = real
    except Exception:
        pass
    informe = os.environ.get("MKI_RED_INFORME")
    if informe:
        with open(informe, "w", encoding="utf-8") as f:
            for nodeid in sorted(_intentos):
                f.write(f"{nodeid}\t{','.join(sorted(_intentos[nodeid]))}\n")


@pytest.fixture(autouse=True)
def _vigilar_red(request):
    """Registra la salida a la red del test y exige el marcador `red`."""
    if os.environ.get("MKI_RED_LIBRE") == "1":
        yield
        return
    nodeid = request.node.nodeid
    _actual["nodeid"] = nodeid
    try:
        yield
    finally:
        _actual["nodeid"] = None
    destinos = _intentos.get(nodeid)
    if not destinos or os.environ.get("MKI_RED_INFORME"):
        return
    if request.node.get_closest_marker("red") is None:
        pytest.fail(
            f"REGLA de la ventana de sellado: este test abrió conexiones "
            f"salientes ({', '.join(sorted(destinos))}) y no lleva "
            f"@pytest.mark.red. Un test que toca la red sin declararlo no "
            f"puede quedar fuera de la corrida entre 17:50 y 20:30 de Chile, "
            f"que es cuando el sistema sella. Marcalo, o quitale la red.")


# ------------------------------------------------------------
# Corrida 16-3 (Bloque D; R5 del dictamen 16-1 y hecho (ii) de la tarjeta §80,
# acta §102.2): LA SUITE NO CREA BASES EN LA RAÍZ DEL REPO.
#
# Medido en las corridas 16a, 16-1 y 16-2 y confirmado con un detector el
# 11-oct-2026: en un árbol sin bases, los tests de `tests/test_api.py` que
# pegan a la API hacían que `senales.init_db()` y `noticias.init_db()`
# crearan `senales.db` y `noticias.db` vacías en la raíz, y desde ese instante
# los tests «con base» corrían sobre una base vacía en vez de saltarse. Este
# fixture convierte eso en un error que nombra al test: si al terminar un
# test existe una base que no existía al empezarlo, el test escribió en la
# ruta real sin parchear `DB_PATH` (o la ruta del sellador). En el árbol real,
# donde las tres bases existen, no hace nada. No borra nada: la limpieza es
# del autor del test, que tiene que apuntarlo a una base temporal.
# ------------------------------------------------------------
BASES_DEL_REPO = ("senales.db", "noticias.db", os.path.join("dinero", "sello_dinero.db"))
# Misma regla para la evidencia versionada: el 11-oct-2026 un test sintético de
# esta misma corrida dejó un par `ext_2026-09-14.no_verificable.*` en
# `data/backups/sello_dinero_ext/` porque `respaldar_extension` tiene la carpeta
# real ligada como argumento por defecto y el monkeypatch no la alcanza. Un
# archivo nuevo bajo data/backups/ durante un test es un test que escribió en
# el árbol; el job de backup lo habría commiteado esa misma noche.
CARPETA_RESPALDOS = os.path.join("data", "backups")
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def existencia_bases(raiz: str = _RAIZ) -> dict:
    return {b: os.path.exists(os.path.join(raiz, b)) for b in BASES_DEL_REPO}


def bases_creadas(existian: dict, raiz: str = _RAIZ) -> list:
    """Las bases que existen ahora y NO existían cuando se tomó `existian`."""
    return [b for b, habia in existian.items() if not habia and os.path.exists(os.path.join(raiz, b))]


def archivos_de_respaldo(raiz: str = _RAIZ) -> set:
    carpeta = os.path.join(raiz, CARPETA_RESPALDOS)
    if not os.path.isdir(carpeta):
        return set()
    return {os.path.relpath(os.path.join(d, n), raiz)
            for d, _, archivos in os.walk(carpeta) for n in archivos}


def respaldos_creados(habia: set, raiz: str = _RAIZ) -> list:
    return sorted(archivos_de_respaldo(raiz) - habia)


@pytest.fixture(autouse=True)
def _ninguna_base_nueva_en_el_repo():
    antes = existencia_bases()
    respaldos_antes = archivos_de_respaldo()
    yield
    nuevas = bases_creadas(antes)
    if nuevas:
        pytest.fail(
            f"REGLA de la corrida 16-3: este test creó {', '.join(nuevas)} en la raíz del repo. "
            f"Escribió en la ruta real de una base sin parchearla (senales.DB_PATH, noticias.DB_PATH o "
            f"la ruta del sellador de dinero): en un árbol sin bases eso deja una base vacía que los tests "
            f"«con base» leerían como historia. Apuntalo a una base temporal.")
    nuevos = respaldos_creados(respaldos_antes)
    if nuevos:
        pytest.fail(
            f"REGLA de la corrida 16-3: este test creó {', '.join(nuevos)} bajo data/backups/, la "
            f"evidencia versionada que el job de backup commitea. Un argumento por defecto ligado a la "
            f"carpeta real (respaldar_extension) no se parchea con monkeypatch: pasá `destino=` explícito.")
