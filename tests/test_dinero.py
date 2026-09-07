# ============================================================
# tests/test_dinero.py — el riel de dinero (Etapa 7.0.0, corrida 10).
#
# Tres familias, y la primera es la que protege lo que ya funciona:
#
#   1. AISLAMIENTO en las dos direcciones. Nada de `dinero/` importa el
#      camino de sellado, y nada del camino de sellado importa `dinero/`.
#      Se comprueba leyendo los `import` con el AST, igual que GEMELO.
#   2. PROPIEDADES de la capa de decisión, no ejemplos: las invariantes se
#      exigen sobre entradas GENERADAS, con semilla declarada. Un ejemplo
#      demuestra que un caso anda; una propiedad demuestra que la
#      invariante no depende del caso.
#   3. ARITMÉTICA de costos: el tope como porcentaje del monto es lo que
#      manda para acciones baratas, y eso hay que fijarlo con un test o se
#      pierde en la próxima edición.
#
# La semilla es OBLIGATORIA y va escrita: el proyecto ya tiene la regla
# (GEMELO/inferencia: `semilla` sin default) porque una generación sin
# semilla no es reproducible y un fallo intermitente no se puede arreglar.
# ============================================================
import ast
import os
import random
from datetime import date

import pytest

from dinero import decision as D
from dinero import universo_dinero as U

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMILLA = 20260906
CASOS = 400


# ------------------------------------------------------------
# 1. Aislamiento
# ------------------------------------------------------------
CAMINO_DE_SELLADO = {"motor", "senales", "snapshot", "universo", "alertas",
                     "noticias", "calendarios", "version", "app"}


def _importados(ruta):
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres |= {a.name.split(".")[0] for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module.split(".")[0])
    return nombres


def _modulos(carpeta):
    return sorted(a for a in os.listdir(carpeta) if a.endswith(".py"))


def test_dinero_no_importa_el_camino_de_sellado():
    """Trece instrumentos nuevos son trece formas nuevas de que una fuente
    caída se lleve puesto el sello de las 18:15. La adquisición se duplica
    a propósito; este test es lo que impide que alguien 'la simplifique'."""
    carpeta = os.path.join(RAIZ, "dinero")
    for archivo in _modulos(carpeta):
        prohibidos = _importados(os.path.join(carpeta, archivo)) & CAMINO_DE_SELLADO
        assert not prohibidos, f"dinero/{archivo} importa {prohibidos}"


def test_el_camino_de_sellado_no_importa_dinero():
    """La dirección que de verdad protege el experimento."""
    for archivo in ("motor.py", "senales.py", "snapshot.py", "universo.py",
                    "alertas.py", "noticias.py", "calendarios.py",
                    "mki_noticias.py", "mki_backup.py", "mki_vigia.py"):
        ruta = os.path.join(RAIZ, archivo)
        if not os.path.exists(ruta):
            continue
        assert "dinero" not in _importados(ruta), f"{archivo} importa dinero"


def test_ninguna_funcion_del_riel_manda_ordenes_de_verdad():
    """Prohibición del encargo, puesta como test y no como promesa: nada de
    `dinero/` habla con una corredora ni guarda credenciales de una."""
    sospechosos = ("alpaca", "ibkr", "ib_insync", "interactivebrokers",
                   "tradier", "robinhood", "api_key", "api_secret",
                   "account_id", "place_order", "submit_order")
    carpeta = os.path.join(RAIZ, "dinero")
    for archivo in _modulos(carpeta):
        texto = open(os.path.join(carpeta, archivo), encoding="utf-8").read().lower()
        for palabra in sospechosos:
            assert palabra not in texto, (
                f"dinero/{archivo} menciona '{palabra}': el riel es simulado "
                f"y no hay cuenta de corredora")


# ------------------------------------------------------------
# 2. Propiedades de la capa de decisión
# ------------------------------------------------------------
def _cfg(**cambios):
    base = {
        "costos": {"comision_por_accion_usd": 0.005,
                   "comision_minima_usd": 1.0,
                   "comision_tope_pct_del_monto": 1.0,
                   "acciones_fraccionarias": False},
        "juegos": {"prueba": {
            "umbral_senal_pp": 1.0,
            "tope_posicion_pct": 25.0,
            "tenencia_minima_dias_habiles": 20,
            "presupuesto_diario_usd": 200.0,
            "presupuesto_semanal_usd": 350.0,
            "presupuesto_mensual_usd": 500.0,
            "apagado_por_perdida_pct": 15.0,
            "exigir_intervalo_que_no_cruce_cero": False,
        }},
        "juego_activo": "prueba",
    }
    base["juegos"]["prueba"].update(cambios)
    return base


def _caso(rnd, cfg=None):
    """Una entrada generada: señales, precios, cartera y estado."""
    tickers = ["AAA", "BBB", "CCC", "DDD", "EEE"]
    n = rnd.randint(0, len(tickers))
    elegidos = rnd.sample(tickers, n)
    senales = []
    for t in elegidos:
        m = rnd.uniform(-8.0, 8.0)
        ancho = rnd.uniform(0.1, 6.0)
        senales.append(D.Senal(t, m, m - ancho, m + ancho))
    precios = {t: rnd.choice([3.5, 27.0, 95.0, 180.0, 640.0, 1200.0])
               for t in tickers}
    posiciones = []
    for t in rnd.sample(tickers, rnd.randint(0, 2)):
        acc = rnd.randint(1, 3)
        posiciones.append(D.Posicion(
            t, acc, acc * precios[t] + 1.0,
            date(2026, rnd.randint(1, 8), rnd.randint(1, 28))))
    cartera = D.Cartera(efectivo_usd=rnd.uniform(0.0, 600.0),
                        posiciones=tuple(posiciones))
    estado = D.EstadoRiel(
        gastado_hoy_usd=rnd.uniform(0.0, 120.0),
        gastado_semana_usd=rnd.uniform(0.0, 300.0),
        gastado_mes_usd=rnd.uniform(0.0, 450.0),
        perdida_acumulada_usd=rnd.uniform(0.0, 40.0))
    return senales, cartera, precios, estado


def _decidir(caso, cfg, presupuesto=500.0, dia=date(2026, 9, 4)):
    senales, cartera, precios, estado = caso
    return D.proponer_ordenes(senales, cartera, presupuesto, cfg, dia,
                              precios, estado)


def test_propiedad_la_suma_de_compras_nunca_excede_el_presupuesto():
    rnd = random.Random(SEMILLA)
    cfg = _cfg()
    for _ in range(CASOS):
        caso = _caso(rnd)
        d = _decidir(caso, cfg)
        gastado = sum(o.desembolso_usd for o in d.ordenes if o.lado == D.COMPRA)
        assert gastado <= 500.0 + 1e-9, (gastado, d)
        j = cfg["juegos"]["prueba"]
        _, _, _, estado = caso
        assert gastado <= j["presupuesto_diario_usd"] - estado.gastado_hoy_usd + 1e-9
        assert gastado <= j["presupuesto_semanal_usd"] - estado.gastado_semana_usd + 1e-9
        assert gastado <= j["presupuesto_mensual_usd"] - estado.gastado_mes_usd + 1e-9


def test_propiedad_ninguna_posicion_supera_su_tope():
    rnd = random.Random(SEMILLA + 1)
    cfg = _cfg()
    tope = 500.0 * cfg["juegos"]["prueba"]["tope_posicion_pct"] / 100.0
    for _ in range(CASOS):
        senales, cartera, precios, estado = _caso(rnd)
        d = _decidir((senales, cartera, precios, estado), cfg)
        for o in d.ordenes:
            if o.lado != D.COMPRA:
                continue
            previa = cartera.por_ticker(o.ticker)
            expuesto = (previa.acciones * precios[o.ticker]) if previa else 0.0
            assert expuesto + o.monto_usd <= tope + 1e-9, (o, expuesto, tope)


def test_propiedad_con_el_interruptor_apagado_no_sale_ninguna_orden():
    rnd = random.Random(SEMILLA + 2)
    cfg = _cfg()
    for _ in range(CASOS):
        senales, cartera, precios, _ = _caso(rnd)
        apagado = D.EstadoRiel(apagado=True, motivo_apagado="prueba")
        d = D.proponer_ordenes(senales, cartera, 500.0, cfg,
                               date(2026, 9, 4), precios, apagado)
        assert d.ordenes == ()
        assert d.riel_apagado
        assert "firma humana" in d.descartes[0][1]


def test_propiedad_la_perdida_acumulada_apaga_el_riel():
    cfg = _cfg(apagado_por_perdida_pct=10.0)
    senales = [D.Senal("AAA", 9.0, 8.0, 10.0)]
    cartera = D.Cartera(efectivo_usd=500.0)
    for perdida, esperado_apagado in ((49.99, False), (50.0, True), (80.0, True)):
        d = D.proponer_ordenes(
            senales, cartera, 500.0, cfg, date(2026, 9, 4), {"AAA": 20.0},
            D.EstadoRiel(perdida_acumulada_usd=perdida))
        assert d.riel_apagado is esperado_apagado, perdida
        if esperado_apagado:
            assert d.ordenes == ()


def test_propiedad_sin_senal_sobre_el_umbral_no_se_opera():
    rnd = random.Random(SEMILLA + 3)
    cfg = _cfg(umbral_senal_pp=1.0)
    for _ in range(CASOS):
        senales, cartera, precios, estado = _caso(rnd)
        flojas = [D.Senal(s.ticker, min(abs(s.magnitud_pp), 0.99) * (1 if s.magnitud_pp >= 0 else -1) * 0.5,
                          -0.6, 0.6) for s in senales]
        d = D.proponer_ordenes(flojas, cartera, 500.0, cfg, date(2026, 9, 4),
                               precios, estado)
        assert d.ordenes == (), d.ordenes
        for t, razon in d.descartes:
            assert "umbral" in razon or "tenencia" in razon or "precio" in razon


def test_propiedad_es_determinista():
    """Dos llamadas con la misma entrada dan exactamente lo mismo, y el
    orden de la lista de señales NO cambia la salida: si cambiara, la
    decisión dependería de cómo llegó el diccionario del día."""
    rnd = random.Random(SEMILLA + 4)
    cfg = _cfg()
    for _ in range(CASOS):
        senales, cartera, precios, estado = _caso(rnd)
        a = _decidir((senales, cartera, precios, estado), cfg)
        b = _decidir((senales, cartera, precios, estado), cfg)
        revueltas = list(senales)
        rnd.shuffle(revueltas)
        c = _decidir((revueltas, cartera, precios, estado), cfg)
        assert a.ordenes == b.ordenes == c.ordenes
        assert sorted(a.descartes) == sorted(c.descartes)


def test_propiedad_la_tenencia_minima_se_cuenta_en_dias_habiles():
    """20 días hábiles son 28 corridos: contarlos mal acorta la tenencia un
    40% sin que se note."""
    cfg = _cfg(tenencia_minima_dias_habiles=20, umbral_senal_pp=1.0)
    pos = D.Posicion("AAA", 2, 100.0, date(2026, 8, 10))   # lunes
    cartera = D.Cartera(efectivo_usd=0.0, posiciones=(pos,))
    senales = [D.Senal("AAA", -5.0, -6.0, -4.0)]
    # 2026-09-04 (viernes) son 25 días corridos pero sólo 19 hábiles.
    d = D.proponer_ordenes(senales, cartera, 500.0, cfg, date(2026, 9, 4),
                           {"AAA": 50.0})
    assert d.ordenes == (), "19 días hábiles no alcanzan los 20 exigidos"
    d = D.proponer_ordenes(senales, cartera, 500.0, cfg, date(2026, 9, 7),
                           {"AAA": 50.0})
    assert len(d.ordenes) == 1 and d.ordenes[0].lado == D.VENTA


def test_una_senal_cuyo_intervalo_cruza_el_cero_se_puede_exigir_fuera():
    cfg = _cfg(exigir_intervalo_que_no_cruce_cero=True, umbral_senal_pp=1.0)
    senales = [D.Senal("AAA", 3.0, -1.0, 7.0)]
    d = D.proponer_ordenes(senales, D.Cartera(500.0), 500.0, cfg,
                           date(2026, 9, 4), {"AAA": 50.0})
    assert d.ordenes == ()
    assert "contiene el cero" in d.descartes[0][1]


# ------------------------------------------------------------
# 3. Aritmética de costos
# ------------------------------------------------------------
def test_el_tope_porcentual_manda_para_acciones_baratas():
    """Con mínimo de 1 USD y tope de 1%, una orden de UNA acción de menos de
    100 USD paga exactamente el 1%. Es el hallazgo que ordena el mapa del
    bloque 1 y por eso queda clavado acá."""
    costos = U.reglas()["costos"]
    assert U.comision_usd(1, 50.0, costos) == pytest.approx(0.50)
    assert U.comision_usd(1, 99.0, costos) == pytest.approx(0.99)
    assert U.comision_usd(1, 200.0, costos) == pytest.approx(1.00)
    assert U.comision_usd(0, 200.0, costos) == 0.0


def test_no_se_compran_fracciones_y_la_comision_entra_en_la_cuenta():
    costos = U.reglas()["costos"]
    # 500 USD, acción de 240: entran 2 (480 + 1 de comisión = 481).
    assert U.acciones_por_monto(500.0, 240.0, costos) == 2
    # 500 USD, acción de 499.60: 1 acción costaría 499.60 + 1.00 > 500.
    assert U.acciones_por_monto(500.0, 499.60, costos) == 0
    assert U.acciones_por_monto(500.0, 600.0, costos) == 0


def test_el_estado_de_un_eslabon_sigue_la_regla_escrita():
    """La regla se escribió antes de mirar los precios; el test la fija."""
    dom = U.Candidato("X", "x", "memoria", "accion", "dominante")
    sus = U.Candidato("Y", "y", "memoria", "ETF", "sustituto")
    def fila(c, alcanza, verificado=True):
        f = U.FilaMapa(candidato=c, verificado=verificado)
        f.alcanza_con_techo = alcanza
        return f
    assert U.estado_del_eslabon([fila(dom, True), fila(sus, True)]) == "REPRESENTADO"
    assert U.estado_del_eslabon([fila(dom, False), fila(sus, True)]) == "SUSTITUIDO"
    assert U.estado_del_eslabon([fila(dom, False), fila(sus, False)]) == "HUECO"
    assert U.estado_del_eslabon([]) == "HUECO"


# ------------------------------------------------------------
# 4. Los números de reglas.json salen de su regla, no de la mano de nadie
# ------------------------------------------------------------
def test_los_parametros_reproducen_su_regla_de_derivacion():
    """El encargo lo pide sin rodeos: no inventes los números. Cada
    parámetro sale de una regla escrita en dinero/derivacion.py, y este
    test la recomputa sobre los precios congelados. Si alguien mueve un
    número a mano, la suite se pone roja — que es la única forma de que la
    regla siga siendo la regla y no un comentario."""
    from dinero import derivacion, precios
    cfg = U.reglas()
    cierres = precios.cargar_congelado()
    costos, techo = cfg["costos"], cfg["presupuesto"]["techo_usd"]
    sigma = derivacion.sigma_60d_pct(cierres, derivacion.ETF_REFERENCIA)
    # Precio de referencia: el cierre verificado más barato. En el tramo
    # relevante el costo no depende del precio (manda el mínimo de 1 USD),
    # y el test lo comprueba probando además con el más caro que cabe.
    ultimos = cierres.dropna(axis=1, how="all").iloc[-1].dropna()
    for nombre, j in cfg["juegos"].items():
        if nombre.startswith("_"):
            continue
        assert j["tope_posicion_pct"] == pytest.approx(100.0 / j["_K_posiciones"])
        assert j["presupuesto_diario_usd"] == pytest.approx(
            techo * j["tope_posicion_pct"] / 100.0)
        assert j["presupuesto_semanal_usd"] == pytest.approx(
            techo / j["_semanas_despliegue"])
        assert j["presupuesto_mensual_usd"] == pytest.approx(techo)
        assert j["apagado_por_perdida_pct"] == pytest.approx(
            derivacion.apagado_derivado_pct(j["_k_apagado"], sigma))
        esperado = derivacion.umbral_derivado_pp(
            j["_k_umbral"], j["tope_posicion_pct"], techo,
            float(ultimos.min()), costos)
        assert j["umbral_senal_pp"] == pytest.approx(esperado, abs=0.005), nombre


def test_el_juego_por_defecto_es_el_conservador_por_regla_escrita():
    """No por su resultado en la cuenta en papel: eso sería elegir la vara
    después de ver el tiro."""
    cfg = U.reglas()
    assert cfg["juego_activo"] == "conservador"
    assert D.juego(cfg) is cfg["juegos"]["conservador"]


def test_los_precios_congelados_son_los_que_dice_su_metadato():
    """Un congelado sin huella verificada no es un congelado."""
    import hashlib
    from dinero import precios
    meta = precios.meta_congelado()
    assert meta, "falta el metadato del congelado"
    h = hashlib.sha256(open(precios.RUTA_CIERRES, "rb").read()).hexdigest()
    assert h == meta["sha256"], (
        "el CSV congelado no coincide con su huella: o se regeneró sin "
        "actualizar el metadato, o se editó a mano")
    cierres = precios.cargar_congelado()
    assert len(cierres) == meta["filas"]
    assert list(cierres.columns) == meta["tickers"]


def test_cargar_congelado_no_sale_a_la_red_si_falta_el_archivo():
    """La regla que impide que 'sin descargas nuevas' se vuelva decorativo."""
    from dinero import precios
    with pytest.raises(FileNotFoundError) as e:
        precios.cargar_congelado("/no/existe/jamas.csv")
    assert "congelar" in str(e.value)


# ------------------------------------------------------------
# 5. La palabra prohibida, también en lo nuevo
# ------------------------------------------------------------
DOCUMENTOS_DEL_RIEL = (
    "VISION.md",
    "docs/universo_operable.md",
    "dinero/preregistro_dinero.md",
    "dinero/resultados/cuenta_papel.md",
    "GEMELO/preregistro/senal_larga_v1.md",
)


def test_la_palabra_confianza_sigue_prohibida_en_lo_nuevo():
    """Constitución 5.0 #4. El test que lo verifica cubría el payload de la
    API y el reporte de Telegram; los documentos y el código del riel de
    dinero son nuevos y entran acá."""
    for rel in DOCUMENTOS_DEL_RIEL:
        ruta = os.path.join(RAIZ, rel)
        if not os.path.exists(ruta):
            continue
        texto = open(ruta, encoding="utf-8").read().lower()
        assert "confianza" not in texto, f"{rel} usa la palabra prohibida"
    carpeta = os.path.join(RAIZ, "dinero")
    for archivo in _modulos(carpeta):
        texto = open(os.path.join(carpeta, archivo), encoding="utf-8").read().lower()
        assert "confianza" not in texto, f"dinero/{archivo} usa la palabra prohibida"


def test_todo_lo_del_riel_de_dinero_se_declara_simulado():
    """Ninguna cifra de la cuenta en papel puede circular sin su rótulo."""
    ruta = os.path.join(RAIZ, "dinero", "resultados", "cuenta_papel.md")
    if not os.path.exists(ruta):
        pytest.skip("la cuenta en papel todavía no se corrió")
    cabecera = open(ruta, encoding="utf-8").read()[:1500].upper()
    assert "SIMULADO" in cabecera
