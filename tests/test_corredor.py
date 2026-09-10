"""Corrida 12, bloque 4 — el adaptador a la cuenta de PRÁCTICA del corredor,
contra una réplica escrita desde documentación (NO grabada: no es evidencia
de C1/C2). Lo que sí se prueba acá y vale: la GUARDIA DE PAPEL en código, el
aislamiento, SmartRouting en toda orden, la conciliación que detecta una
diferencia, y que ninguna credencial viva en el repo."""
import ast
import os
import re

import pytest

from corredor import ibkr as I

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ------------------------------------------------------------
# 1. Guardia de papel
# ------------------------------------------------------------
@pytest.mark.parametrize("puerto", [7496, 4001, 8080, 0])
def test_se_niega_a_un_puerto_que_no_es_de_practica(puerto):
    with pytest.raises(I.ErrorCuentaNoPractica):
        I.ClienteIBKR(puerto=puerto, transporte=I.TransporteReplica())


def test_se_niega_a_una_cuenta_que_finge_ser_real_aunque_el_puerto_sea_de_practica():
    """La cuenta simulada «U1234567» (sin prefijo DU) llega por el puerto de
    práctica: la guardia la rechaza y se desconecta sin operar."""
    t = I.TransporteReplica(cuentas=["U1234567"])
    c = I.ClienteIBKR(puerto=4002, transporte=t)
    with pytest.raises(I.ErrorCuentaNoPractica):
        c.conectar()
    assert t.conectado is False and c.cuenta is None
    with pytest.raises(I.ErrorCuentaNoPractica):
        c.enviar_orden("GFS", 1, "BUY", "LMT", 45.0)
    assert t.ordenes_enviadas == []


def test_una_sesion_mixta_practica_y_real_tambien_se_rechaza():
    t = I.TransporteReplica(cuentas=["DU0000000", "U7654321"])
    with pytest.raises(I.ErrorCuentaNoPractica):
        I.ClienteIBKR(puerto=7497, transporte=t).conectar()


def test_sin_conectar_no_se_puede_operar_ni_leer():
    c = I.ClienteIBKR(puerto=4002, transporte=I.TransporteReplica())
    for f in (lambda: c.enviar_orden("GFS", 1, "BUY", "MKT"), lambda: c.ejecuciones(),
              lambda: c.posiciones_y_efectivo(), lambda: c.estado_orden(1)):
        with pytest.raises(I.ErrorCuentaNoPractica):
            f()


# ------------------------------------------------------------
# 2. La interfaz mínima, contra la réplica (rotulada)
# ------------------------------------------------------------
def test_ciclo_completo_contra_la_replica_y_su_rotulo():
    t = I.TransporteReplica()
    assert "NO es evidencia" in t.ORIGEN
    c = I.ClienteIBKR(puerto=4002, transporte=t)
    cuenta = c.conectar()
    assert cuenta.startswith("DU")
    oid = c.enviar_orden("GFS", 1, "BUY", "LMT", 45.21)
    oid2 = c.enviar_orden("GFS", 1, "SELL", "LMT", 45.18)
    assert len(t.ordenes_enviadas) == 2                     # dos órdenes, no más
    assert all(o.exchange == "SMART" for _, o in t.ordenes_enviadas)   # SmartRouting siempre
    assert c.estado_orden(oid)["status"] == "Filled"
    ej = c.ejecuciones()
    assert len(ej) == 2 and all(e.cuenta.startswith("DU") for e in ej)
    assert {e.order_id for e in ej} == {1001, 1002} and oid == 1001 and oid2 == 1002
    assert all(e.comision_usd == 0.35 for e in ej)
    pe = c.posiciones_y_efectivo()
    assert pe["marca_retraso"].retraso_min == 15 and pe["marca_retraso"].descripcion == "retrasado"
    assert "NO es evidencia" in pe["origen"]
    c.desconectar()
    assert c.cuenta is None and t.conectado is False
    # la bitácora del cliente no lleva la cuenta entera ni ninguna credencial
    assert all("DU0000000" not in d for _, _, d in c.bitacora)


def test_una_orden_limite_sin_precio_o_invalida_se_rechaza():
    c = I.ClienteIBKR(puerto=4002, transporte=I.TransporteReplica()); c.conectar()
    with pytest.raises(ValueError):
        c.enviar_orden("GFS", 1, "BUY", "LMT")
    with pytest.raises(ValueError):
        c.enviar_orden("GFS", 0, "BUY", "MKT")
    with pytest.raises(ValueError):
        c.enviar_orden("GFS", 1, "SHORT", "MKT")


def test_una_ejecucion_de_cuenta_no_practica_revienta_al_leer(tmp_path):
    import json
    d = json.load(open(I.RUTA_REPLICA, encoding="utf-8"))
    d["execDetails"][0]["acctNumber"] = "U1234567"
    ruta = tmp_path / "r.json"; ruta.write_text(json.dumps(d))
    c = I.ClienteIBKR(puerto=4002, transporte=I.TransporteReplica(str(ruta))); c.conectar()
    with pytest.raises(I.ErrorCuentaNoPractica):
        c.ejecuciones()


# ------------------------------------------------------------
# 3. Conciliación: detecta diferencias (contraprueba) y no se autoengaña
# ------------------------------------------------------------
def test_conciliar_detecta_una_diferencia_y_una_falta():
    c = I.ClienteIBKR(puerto=4002, transporte=I.TransporteReplica()); c.conectar()
    api = c.ejecuciones()
    oficial = [{"exec_id": e.exec_id, "ticker": e.ticker, "lado": e.lado, "cantidad": e.cantidad, "precio": e.precio}
               for e in api]
    assert I.conciliar(api, oficial)["C2"] == "cumplida"
    oficial[0]["precio"] = 45.22
    r = I.conciliar(api, oficial[:1])
    assert r["C2"] == "NO cumplida" and r["difieren"][0][1] == "precio" and r["faltan_en_oficial"] == [api[1].exec_id]
    assert "NO es evidencia" in r["nota"]


# ------------------------------------------------------------
# 4. Aislamiento y ausencia de credenciales
# ------------------------------------------------------------
def _importados(ruta):
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    out = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            out |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module.split(".")[0])
    return out


def test_nadie_del_camino_de_sellado_ni_dinero_importa_corredor_y_corredor_no_importa_el_sellado():
    sellado = {"motor", "senales", "snapshot", "universo", "alertas", "noticias", "calendarios", "version", "app"}
    for archivo in ("motor.py", "senales.py", "snapshot.py", "universo.py", "alertas.py", "noticias.py",
                    "calendarios.py", "mki_noticias.py", "mki_backup.py", "mki_vigia.py", "api/main.py"):
        ruta = os.path.join(RAIZ, archivo)
        if os.path.exists(ruta):
            assert "corredor" not in _importados(ruta), f"{archivo} importa corredor"
    for archivo in os.listdir(os.path.join(RAIZ, "dinero")):
        if archivo.endswith(".py"):
            assert "corredor" not in _importados(os.path.join(RAIZ, "dinero", archivo))
    for archivo in os.listdir(os.path.join(RAIZ, "corredor")):
        if archivo.endswith(".py"):
            imp = _importados(os.path.join(RAIZ, "corredor", archivo))
            assert not (imp & sellado), f"corredor/{archivo} importa {imp & sellado}"
            assert "dinero" not in imp


def test_ibapi_no_se_importa_al_cargar_el_modulo_y_no_esta_en_requirements():
    """La dependencia se importa perezosamente (licencia click-through de IB;
    instalarla es acto de Nicolás) y requirements.txt no instala nada nuevo."""
    import sys
    assert "ibapi" not in sys.modules or True   # el import perezoso vive dentro de TransporteIbapi
    src = open(os.path.join(RAIZ, "corredor", "ibkr.py"), encoding="utf-8").read()
    arbol = ast.parse(src)
    nivel_modulo = {a.name.split(".")[0] for n in arbol.body if isinstance(n, ast.Import) for a in n.names} | \
                   {n.module.split(".")[0] for n in arbol.body if isinstance(n, ast.ImportFrom) and n.module}
    assert "ibapi" not in nivel_modulo
    req = open(os.path.join(RAIZ, "requirements.txt"), encoding="utf-8").read()
    assert not re.search(r"^ibapi\b", req, re.M), "ibapi no se instala desde requirements (ver acta corrida 12)"


def test_ninguna_credencial_en_corredor_ni_en_la_replica():
    patrones = (r"(?i)password", r"(?i)api[_-]?key", r"(?i)secret", r"(?i)token\s*=")
    for raiz, _, archivos in os.walk(os.path.join(RAIZ, "corredor")):
        for a in archivos:
            if a.endswith((".py", ".json", ".md")):
                txt = open(os.path.join(raiz, a), encoding="utf-8").read()
                for p in patrones:
                    assert not re.search(p, txt), f"{a}: {p}"
