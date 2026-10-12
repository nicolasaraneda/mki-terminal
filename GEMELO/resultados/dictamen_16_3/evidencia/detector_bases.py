"""Plugin de diagnóstico (corrida 16-3, Bloque D): qué test crea senales.db,
noticias.db o dinero/sello_dinero.db en un árbol que no las tiene. Tras cada
test, si el archivo apareció y no existía al arrancar la sesión, lo anota y lo
borra para que el siguiente culpable también quede a la vista."""
import os
import pytest

ARCHIVOS = ("senales.db", "noticias.db", os.path.join("dinero", "sello_dinero.db"))


def pytest_configure(config):
    config._mki_raiz = str(config.rootpath)
    config._mki_salida = os.environ["MKI_DETECTOR_SALIDA"]
    config._mki_existian = {a: os.path.exists(os.path.join(config._mki_raiz, a)) for a in ARCHIVOS}
    with open(config._mki_salida, "a") as f:
        f.write(f"# raiz={config._mki_raiz} existian={config._mki_existian}\n")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    yield
    raiz = item.config._mki_raiz
    for a in ARCHIVOS:
        ruta = os.path.join(raiz, a)
        if item.config._mki_existian[a]:
            continue
        if os.path.exists(ruta):
            with open(item.config._mki_salida, "a") as f:
                f.write(f"{a}\t{os.path.getsize(ruta)}\t{item.nodeid}\n")
            os.remove(ruta)
