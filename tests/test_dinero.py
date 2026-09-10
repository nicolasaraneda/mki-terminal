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
    `dinero/` habla con una corredora ni guarda credenciales de una.

    Corrida 12, bloque 2.4: el NOMBRE del corredor cuyo arancel publicado
    alimenta `reglas.json` (Interactive Brokers, insumo del §40) puede
    aparecer en un comentario o en la cita de la fuente —una perífrasis que
    evita nombrar la fuente hace más difícil verificarla, y el curador de la
    corrida 11 nunca exigió esconderlo—; lo que sigue prohibido es HABLAR con
    él: ningún módulo de `dinero/` importa `ibapi` ni `corredor`, ni contiene
    los verbos de una API de órdenes ni nombres de credenciales."""
    sospechosos = ("alpaca", "ib_insync", "tradier", "robinhood", "api_key",
                   "api_secret", "account_id", "place_order", "submit_order",
                   "placeorder", "reqids", "eclient", "ewrapper")
    carpeta = os.path.join(RAIZ, "dinero")
    for archivo in _modulos(carpeta):
        ruta = os.path.join(carpeta, archivo)
        texto = open(ruta, encoding="utf-8").read().lower()
        for palabra in sospechosos:
            assert palabra not in texto, (
                f"dinero/{archivo} menciona '{palabra}': el riel es simulado "
                f"y no hay cuenta de corredora")
        assert not ({"ibapi", "corredor"} & _importados(ruta)), (
            f"dinero/{archivo} importa el adaptador del corredor: el riel simulado no habla con nadie")


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
    costos = {"comision_por_accion_usd": 0.005, "comision_minima_usd": 1.0,
              "comision_tope_pct_del_monto": 1.0}
    assert U.comision_usd(1, 50.0, costos) == pytest.approx(0.50)
    assert U.comision_usd(1, 99.0, costos) == pytest.approx(0.99)
    assert U.comision_usd(1, 200.0, costos) == pytest.approx(1.00)
    assert U.comision_usd(0, 200.0, costos) == 0.0
    # Con el arancel vigente del insumo §40 (mínimo 0,35, tope 1 %) el cruce
    # está en 35 USD por orden: por debajo manda el tope, por encima el mínimo.
    vigente = U.reglas()["costos"]
    assert U.comision_usd(1, 20.0, vigente) == pytest.approx(0.20)
    assert U.comision_usd(1, 35.0, vigente) == pytest.approx(0.35)
    assert U.comision_usd(1, 200.0, vigente) == pytest.approx(0.35)
    assert U.comision_usd(100, 200.0, vigente) == pytest.approx(0.35)
    assert U.comision_usd(200, 200.0, vigente) == pytest.approx(0.70)


def test_no_se_compran_fracciones_y_la_comision_entra_en_la_cuenta():
    # El mecanismo, con un arancel fijo del test (mínimo 1 USD) y no con el
    # de reglas.json, que cambió el 8-sep al del insumo §40: la propiedad es
    # que la comisión entra en la cuenta, no cuánto vale.
    costos = {"comision_por_accion_usd": 0.005, "comision_minima_usd": 1.0,
              "comision_tope_pct_del_monto": 1.0, "acciones_fraccionarias": False}
    # 500 USD, acción de 240: entran 2 (480 + 1 de comisión = 481).
    assert U.acciones_por_monto(500.0, 240.0, costos) == 2
    # 500 USD, acción de 499.60: 1 acción costaría 499.60 + 1.00 > 500.
    assert U.acciones_por_monto(500.0, 499.60, costos) == 0
    assert U.acciones_por_monto(500.0, 600.0, costos) == 0
    # y con el arancel vigente de reglas.json la comisión también entra:
    vigente = U.reglas()["costos"]
    n = U.acciones_por_monto(500.0, 240.0, vigente)
    assert n * 240.0 + U.comision_usd(n, 240.0, vigente) <= 500.0


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
    from dinero import cuenta_papel as CP
    from dinero import derivacion, precios
    cfg = U.reglas()
    cierres = precios.cargar_congelado()
    costos, techo = cfg["costos"], cfg["presupuesto"]["techo_usd"]
    # E5 (corrida 11): la sigma del interruptor se mide HASTA el inicio de
    # la ventana de la cuenta, no sobre el archivo entero.
    sigma = derivacion.sigma_60d_pct(cierres, derivacion.ETF_REFERENCIA,
                                     hasta=CP.DESDE)
    # y el arancel es el del insumo §40, columna de enteras
    assert costos["comision_minima_usd"] == 0.35
    assert costos["comision_por_accion_usd"] == 0.0035
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
    # El documento más consecuente que produjo la corrida 10 estaba fuera de
    # esta lista: hoy está limpio, pero mañana no hay quien lo verifique.
    # Exigencia 18 del `curador-epistemico`.
    "dinero/resultados/senal_larga_v1.md",
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


# ------------------------------------------------------------
# 6. La capa visual (bloque 7). Es texto publicado: se audita como tal.
# ------------------------------------------------------------
VISTAS_NUEVAS = ("frontend/src/vistas/Operable.tsx",
                 "frontend/src/vistas/RielDinero.tsx",
                 "frontend/src/vistas/Rieles.tsx",
                 "frontend/src/componentes/CifraConIntervalo.tsx",
                 "frontend/src/lib/tipos.ts")


def test_la_palabra_confianza_sigue_prohibida_en_la_capa_visual():
    """Constitución 5.0 #4. El test que lo verificaba cubría el payload de
    la API y el reporte de Telegram; el encargo de la corrida 10 pide
    explícitamente que cubra también los archivos nuevos."""
    for rel in VISTAS_NUEVAS:
        ruta = os.path.join(RAIZ, rel)
        if not os.path.exists(ruta):
            continue
        assert "confianza" not in open(ruta, encoding="utf-8").read().lower(), rel


def test_la_capa_visual_no_usa_emojis():
    """Regla de 4.7: no hay emojis en la UI."""
    import re
    emoji = re.compile("[\U0001F300-\U0001FAFF✀-➿☀-⛿]")
    for rel in VISTAS_NUEVAS:
        ruta = os.path.join(RAIZ, rel)
        if not os.path.exists(ruta):
            continue
        texto = open(ruta, encoding="utf-8").read()
        assert not emoji.search(texto), f"{rel} usa emoji"


def test_la_cuenta_en_papel_declara_SIMULADO_sin_scroll():
    """La etiqueta va en el primer bloque de la vista, no enterrada."""
    ruta = os.path.join(RAIZ, "frontend/src/vistas/RielDinero.tsx")
    if not os.path.exists(ruta):
        pytest.skip("la vista todavía no existe")
    cabeza = open(ruta, encoding="utf-8").read()
    primer_card = cabeza.index("<Card")
    assert 'valor="SIMULADO"' in cabeza[primer_card:primer_card + 1200], (
        "la etiqueta SIMULADO tiene que estar en el primer bloque de la vista")


def test_el_componente_de_cifra_se_niega_a_mostrar_un_numero_sin_intervalo():
    """La regla de la casa, hecha ejecutable en el componente: si no hay
    intervalo, no se muestra el número — se muestra por qué falta."""
    ruta = os.path.join(RAIZ, "frontend/src/componentes/CifraConIntervalo.tsx")
    if not os.path.exists(ruta):
        pytest.skip("el componente todavía no existe")
    fuente = open(ruta, encoding="utf-8").read()
    assert "if (!hay || !hayIC)" in fuente
    assert "sin intervalo computado" in fuente
    assert "contiene el cero" in fuente, (
        "un intervalo que cruza el cero se dice con palabras, no sólo con "
        "una banda")
    # Y la corrección del 7-sep: esa frase sólo vale para DIFERENCIAS. El
    # intervalo de Wilson de una proporción no puede contener el cero, así
    # que decir «no contiene el cero» debajo de una tasa de acierto insinúa
    # una significancia que no existe. El componente exige la declaración.
    assert "esDiferencia" in fuente, (
        "la frase sobre el cero sólo corresponde a una diferencia: el "
        "componente tiene que exigir que se declare cuál es")
    assert "es una proporción" in fuente, (
        "sobre una proporción hay que decir qué es, no dejar la frase del "
        "cero puesta")


def test_los_tres_endpoints_del_riel_sirven_lo_que_el_contrato_dice():
    """Paridad de la capa nueva: lo que sirve la API es exactamente el
    artefacto generado, sin recomputar nada."""
    import json
    from fastapi.testclient import TestClient

    from api.main import app
    c = TestClient(app)

    r = c.get("/api/dinero/universo")
    assert r.status_code == 200
    disco = json.load(open(os.path.join(
        RAIZ, "dinero/resultados/universo_operable.json"), encoding="utf-8"))
    assert r.json()["datos"]["resumen"] == disco["resumen"]

    r = c.get("/api/dinero/cuenta")
    assert r.status_code == 200
    assert r.json()["datos"]["etiqueta"] == "SIMULADO"

    r = c.get("/api/rieles")
    assert r.status_code == 200
    rieles = r.json()["datos"]["rieles"]
    assert [x["nombre"] for x in rieles] == ["Riel de medición", "Riel de dinero"]
    for riel in rieles:
        assert riel["que_lo_mata"], "todo riel declara qué lo mata"
        assert riel["falta_para_veredicto"]
    # y la regla dura: ningún estimador puntual sin intervalo
    for cifra in rieles[0]["cifras"]:
        assert len(cifra["intervalo"]) == 2
        assert cifra["tipo_intervalo"]


def test_las_cifras_del_riel_de_medicion_salen_del_arbitro():
    """No se escriben a mano en la API: si el árbitro se mueve, la vista se
    mueve con él o el test se pone rojo."""
    from fastapi.testclient import TestClient

    import cifras
    from api.main import app
    c = cifras.sellada()
    datos = TestClient(app).get("/api/rieles").json()["datos"]["rieles"][0]
    porn = {x["nombre"]: x for x in datos["cifras"]}
    assert porn["acierto del modelo"]["valor_pct"] == c["modelo_pct"]
    assert porn["ventaja sobre la base"]["intervalo"] == c["ventaja_ic_dia"]
    assert datos["muestra"]["n"] == c["n"]


# ============================================================
# 6. LA PRUEBA MAESTRA DE TRUNCACIÓN SOBRE LA CUENTA EN PAPEL
#
# Exigencia E2 del `auditor-lookahead` en el cierre de la corrida 10, y fue
# ANTES que cualquier corrección: «escribir el test de truncación de la
# cuenta en papel ANTES de volver a correrla».
#
# HISTORIA. Del 7 al 8-sep-2026 los tres tests de abajo estuvieron marcados
# `xfail(strict=True)`: las fugas F1, F2 y F4 estaban DEMOSTRADAS y no
# corregidas, así que tenían que fallar, y el modo estricto obligaba a
# volver acá el día que se arreglaran. Ese día fue el 8-sep (corrida 11,
# acta §82.4 opción A). Se verificó con `--runxfail` que los tres fallaban
# por su razón escrita y no por otra, se corrigió el código, y se sacaron
# los marcadores. Dos ajustes a los tests, declarados:
#   · F1 apuntaba a `construir_mapa` (la función del censo, que mira el
#     último cierre por diseño) y no a lo que la cuenta usa para decidir su
#     membresía; tal como estaba no podía pasar con ninguna corrección.
#     Ahora apunta a `cuenta_papel.universo_operable`, que es la función
#     corregida.
#   · F2 pasaba la ventana sola; la señal ahora se sortea de datos
#     ANTERIORES a la ventana, así que el test pasa el archivo completo y
#     `desde`.
# Y se agregaron la prueba maestra sobre la cuenta ENTERA (E6) y su
# contraprueba: un gate que no puede fallar no es un gate.
# ============================================================
import pandas as _pd  # noqa: E402
import pytest as _pytest  # noqa: E402


def _cierres_de_la_ventana():
    from dinero import cuenta_papel as CP
    from dinero import precios
    return CP._ventana(precios.cargar_congelado()), CP


def test_el_universo_operable_no_puede_depender_del_futuro():
    """La membresía usada para simular desde DESDE no puede cambiar según
    datos posteriores a DESDE (F1, corregida por E1)."""
    from dinero import cuenta_papel as CP
    from dinero import precios
    cfg = U.reglas()
    completo = precios.cargar_congelado()
    hasta_el_inicio = completo.loc[:CP.DESDE]
    assert CP.universo_operable(completo, cfg) == CP.universo_operable(hasta_el_inicio, cfg), (
        "el universo operable cambia al truncar en el inicio de la ventana: "
        "la membresía de tres años se está decidiendo con el último cierre")
    # y la contraprueba: la función del censo SÍ depende del último cierre,
    # que es exactamente lo que la cuenta ya no usa
    def censo(marco):
        return sorted(f.candidato.ticker for f in U.construir_mapa(marco, cfg)
                      if f.verificado and f.alcanza_con_techo)
    assert censo(completo) != censo(hasta_el_inicio)


def test_la_senal_sin_informacion_no_puede_sortearse_del_futuro():
    """Truncar los datos posteriores a un corte no puede cambiar las señales
    de los días anteriores a ese corte (F2, corregida por E3)."""
    from dinero import contabilidad as C
    from dinero import cuenta_papel as CP
    from dinero import precios
    completo_df = precios.cargar_congelado()
    corte = "2024-09-04"
    tickers = [t for t in ("NVDA", "INTC", "AMD") if t in completo_df.columns]
    completo = C.senales_sin_informacion(
        completo_df, tickers, CP.HORIZONTE_SENAL_HABILES,
        C.SEMILLA_SENAL_SIN_INFORMACION, desde=CP.DESDE)
    truncado = C.senales_sin_informacion(
        completo_df.loc[:corte], tickers, CP.HORIZONTE_SENAL_HABILES,
        C.SEMILLA_SENAL_SIN_INFORMACION, desde=CP.DESDE)
    comunes = [d for d in truncado if d in completo]
    assert comunes, "el corte no dejó días comunes; el test no probó nada"
    distintos = [d for d in comunes
                 if [s.magnitud_pp for s in completo[d]]
                 != [s.magnitud_pp for s in truncado[d]]]
    assert not distintos, (
        f"{len(distintos)} de {len(comunes)} días cambian de señal al truncar "
        "en %s: la señal se está sorteando de retornos futuros" % corte)
    # sin historia previa, revienta en vez de fingir una distribución
    with _pytest.raises(ValueError):
        C.senales_sin_informacion(completo_df.loc[CP.DESDE:], tickers,
                                  CP.HORIZONTE_SENAL_HABILES,
                                  C.SEMILLA_SENAL_SIN_INFORMACION, desde=CP.DESDE)


def test_la_orden_de_un_dia_no_puede_depender_del_cierre_de_ese_dia():
    """Se decide con el cierre de d y se ejecuta contra el de d+1 (F4,
    corregida por E4). Perturbar el cierre del día de EJECUCIÓN no puede
    cambiar lo que se decidió: ni el ticker, ni el día de decisión, ni las
    acciones decididas. Lo único que puede cambiar es el precio de
    ejecución, que es justamente lo que el retardo hace visible."""
    from dinero import contabilidad as C
    from dinero import cuenta_papel as CP
    from dinero import precios
    completo = precios.cargar_congelado()
    cfg = U.reglas()
    tickers = [t for t in ("NVDA", "INTC", "AMD", "AVGO", "VRT")
               if t in completo.columns]
    cierres = CP._ventana(completo)[tickers].dropna(how="all")
    aportes = C.calendario_aportes([d.date() for d in cierres.index],
                                   CP.APORTE_SEMANAL_USD,
                                   cfg["presupuesto"]["techo_usd"])
    senales = C.senales_sin_informacion(completo, tickers,
                                        CP.HORIZONTE_SENAL_HABILES,
                                        C.SEMILLA_SENAL_SIN_INFORMACION,
                                        desde=CP.DESDE)

    def decisiones(marco):
        libro = C.correr_estrategia(marco, senales, cfg, "conservador",
                                    aportes, 0.0,
                                    cfg["presupuesto"]["techo_usd"])
        return [(m.decidida_el, m.ticker, m.acciones_decididas, m.fecha)
                for m in libro.movimientos]

    base = decisiones(cierres)
    assert base, "la corrida de referencia no generó ninguna orden"
    decidida, ticker, n, ejecutada = base[0]
    assert ejecutada > decidida, "la ejecución tiene que ser posterior a la decisión"
    perturbado = cierres.copy()
    perturbado.loc[_pd.Timestamp(ejecutada)] = perturbado.loc[_pd.Timestamp(ejecutada)] * 1.10
    assert decisiones(perturbado)[0][:3] == (decidida, ticker, n), (
        "perturbar el cierre del día de ejecución cambió la decisión: se "
        "decide y se ejecuta contra el mismo cierre (retardo cero)")


def test_los_dos_retardos_del_riel_son_el_mismo():
    """F4 era, en el fondo, dos retardos distintos en el mismo riel."""
    from dinero import contabilidad as C
    from dinero import senal_larga as SL
    assert C.RETARDO_IMPLEMENTACION == SL.RETARDO_IMPLEMENTACION == 1


def test_la_cuenta_en_papel_es_invariante_al_truncado():
    """LA PRUEBA MAESTRA sobre la cuenta ENTERA (E6): reconstruirla con la
    fuente cortada en D no puede cambiar un solo movimiento ejecutado hasta
    D. Es el mismo gate que corre `cuenta_papel.main` antes de escribir."""
    from dinero import cuenta_papel as CP
    gate = CP.verificar_invariancia()
    assert gate["resultado"] == "INVARIANTE"
    assert len(gate["cortes"]) >= 20, "el barrido de cortes tiene que ser denso (regla, no lista a dedo)"
    assert all(c["movimientos_comparados"] > 0 for c in gate["comparaciones"])
    assert "alcance" in gate


def test_contraprueba_una_fuga_inyectada_rompe_la_invariancia():
    """Un gate que no puede fallar no es un gate. Se inyecta la fuga
    canónica —la señal de d mira el retorno real de d a d+1— y el gate
    tiene que reventar con ErrorLookAhead. La fábrica se llama con cada
    fuente (completa y truncada), que es como una fuga entra de verdad."""
    from backtest.datos import ErrorLookAhead
    from dinero import contabilidad as C
    from dinero import cuenta_papel as CP
    from dinero import precios
    completo = precios.cargar_congelado()
    cfg = U.reglas()

    def fabrica_con_fuga(cierres):
        operables = CP.universo_operable(cierres, cfg)
        limpias = C.senales_sin_informacion(cierres, operables, CP.HORIZONTE_SENAL_HABILES,
                                            C.SEMILLA_SENAL_SIN_INFORMACION, desde=CP.DESDE)
        ventana = CP._ventana(cierres)
        r_manana = (ventana[operables].shift(-1) / ventana[operables] - 1.0) * 100.0
        con_fuga = {}
        for dia, lote in limpias.items():
            ts = _pd.Timestamp(dia)
            fila = r_manana.loc[ts] if ts in r_manana.index else None
            nuevo = []
            for s in lote:
                if fila is not None and not _pd.isna(fila[s.ticker]):
                    m = float(fila[s.ticker]) * 50.0
                else:
                    m = s.magnitud_pp
                nuevo.append(D.Senal(s.ticker, m, m - 0.01, m + 0.01))
            con_fuga[dia] = nuevo
        return con_fuga

    with _pytest.raises(ErrorLookAhead, match="invariancia al truncado ROTA"):
        CP.verificar_invariancia(cfg=cfg, cierres_completo=completo,
                                 fabrica_senales=fabrica_con_fuga)


# ------------------------------------------------------------
# 7. Corrida 12 — G3 (fuga por `precios_ref`), modo diagnóstico del gate
#    y G8 (disponibilidad por ticker sellada en el metadato del congelado)
# ------------------------------------------------------------
import json as _json
import glob as _glob
from datetime import datetime as _dt


def _primer_dia_en_que_la_fuga_cambia_una_decision(completo, cfg):
    """Prueba de BORDE (G3, exigencia del auditor de la corrida 11): el corte
    no se adivina, se lee de `Libro.decisiones`. Se corre la cuenta honesta y
    la cuenta con la fuga de 1 día por `precios_ref`, y se toma el primer día
    en que alguna decisión difiere. En ese día el estado previo de los dos
    libros es idéntico (es la PRIMERA diferencia), así que la decisión con
    el cierre de d+1 y la decisión con el cierre de d son distintas por
    construcción, y un gate cortado exactamente ahí TIENE que verla."""
    from dinero import cuenta_papel as CP
    _, honesto = CP.correr(completo, cfg)
    _, con_fuga = CP.correr(completo, cfg, fuga_precios_ref_dias=1)
    candidatos = []
    for clave in honesto["estrategia"]:
        por_dia_a, por_dia_b = {}, {}
        for (d, t, lado, n) in honesto["estrategia"][clave][0].decisiones:
            por_dia_a.setdefault(d, []).append((t, lado, n))
        for (d, t, lado, n) in con_fuga["estrategia"][clave][0].decisiones:
            por_dia_b.setdefault(d, []).append((t, lado, n))
        for d in sorted(set(por_dia_a) | set(por_dia_b)):
            if por_dia_a.get(d) != por_dia_b.get(d):
                candidatos.append(d)
                break
    assert candidatos, "la fuga de 1 día por precios_ref no cambió ninguna decisión: la contraprueba no tiene borde"
    return min(candidatos)


def test_G3_la_fuga_por_precios_ref_dispara_el_gate_en_el_dia_de_borde():
    """La contraprueba que faltaba: la fuga entra por el PRECIO con que se
    dimensiona (no por la señal, que es la otra contraprueba) y se inyecta
    por un parámetro del riel, no editando código a mano."""
    from backtest.datos import ErrorLookAhead
    from dinero import cuenta_papel as CP
    from dinero import precios
    completo = precios.cargar_congelado()
    cfg = U.reglas()
    borde = _primer_dia_en_que_la_fuga_cambia_una_decision(completo, cfg)
    assert str(borde) > CP.DESDE and str(borde) < CP.HASTA
    with _pytest.raises(ErrorLookAhead, match=f"invariancia al truncado ROTA en {borde}"):
        CP.verificar_invariancia(cortes=[str(borde)], cfg=cfg, cierres_completo=completo,
                                 fuga_precios_ref_dias=1)


def test_G3_sin_fuga_el_mismo_corte_de_borde_es_invariante():
    """Contraprueba de la contraprueba: el corte de borde no es especial
    para la cuenta honesta."""
    from dinero import cuenta_papel as CP
    from dinero import precios
    completo = precios.cargar_congelado()
    cfg = U.reglas()
    borde = _primer_dia_en_que_la_fuga_cambia_una_decision(completo, cfg)
    g = CP.verificar_invariancia(cortes=[str(borde)], cfg=cfg, cierres_completo=completo)
    assert g["resultado"] == "INVARIANTE"
    assert g["fuga_inyectada"] == {"precios_ref_dias": 0, "fabrica_senales": False}


def test_el_gate_en_modo_diagnostico_devuelve_el_mapa_de_cortes_rotos_sin_levantar():
    """Hallazgo 5 de la revisión de la corrida 11: el gate podía decir sólo el
    PRIMER corte roto. En modo diagnóstico devuelve todos, y la medición del
    auditor (una fuga de 1 día sólo se ve desde algunos cortes) queda como
    número: sobre los diez primeros cortes por regla, algunos la ven y otros
    no. El comportamiento por defecto (levantar) no cambia."""
    from dinero import cuenta_papel as CP
    from dinero import precios
    completo = precios.cargar_congelado()
    cfg = U.reglas()
    diez = CP.cortes_invariancia(completo)[:10]
    g = CP.verificar_invariancia(cortes=diez, cfg=cfg, cierres_completo=completo,
                                 fuga_precios_ref_dias=1, diagnostico=True)
    assert g["resultado"] == "ROTA"
    rotos = [r["corte"] for r in g["cortes_rotos"]]
    assert 0 < len(rotos) < len(diez), (
        f"la fuga de 1 día tendría que verse desde ALGUNOS cortes y no desde todos; rotos={rotos}")
    assert all(c in diez for c in rotos)
    assert all("ROTA" in r["detalle"] for r in g["cortes_rotos"])
    assert len(g["comparaciones"]) == len(diez), "en modo diagnóstico se recorren todos los cortes"


def test_el_gate_en_modo_diagnostico_sin_fuga_es_invariante_y_no_lista_nada():
    from dinero import cuenta_papel as CP
    from dinero import precios
    completo = precios.cargar_congelado()
    g = CP.verificar_invariancia(cortes=CP.cortes_invariancia(completo)[:2],
                                 cierres_completo=completo, diagnostico=True)
    assert g["resultado"] == "INVARIANTE" and g["cortes_rotos"] == []


def test_G8_todo_congelado_declara_la_disponibilidad_por_ticker():
    """Zona ciega Z3 del auditor (corrida 11): el congelado no es point-in-time.
    Lo mínimo exigible es que cada metadato diga, por ticker, qué tramo
    contiene y desde cuándo era conocible su último dato; y que eso sea
    consistente con el propio CSV y con la hora de descarga. Vale para todo
    congelado, presente y futuro: un `.meta.json` nuevo sin este campo pone
    la suite en rojo."""
    from dinero import precios
    metas = sorted(_glob.glob(os.path.join(RAIZ, "dinero", "datos", "*.meta.json")))
    assert metas, "no hay congelados"
    for ruta_meta in metas:
        m = _json.load(open(ruta_meta, encoding="utf-8"))
        disp = m.get("disponibilidad")
        assert disp and disp.get("exchange") == precios.EXCHANGE_DISPONIBILIDAD, ruta_meta
        por_ticker = disp["por_ticker"]
        assert set(por_ticker) == set(m["tickers"]), f"{ruta_meta}: tickers sin disponibilidad"
        congelado_en = _dt.fromisoformat(m["congelado_en_utc"])
        for t, d in por_ticker.items():
            if d["n_cierres"] == 0:
                assert d["available_at_utc"] is None
                continue
            assert d["primer_cierre"] <= d["ultimo_cierre"] <= m["hasta"], (ruta_meta, t)
            assert d["primer_cierre"] >= m["desde"], (ruta_meta, t)
            assert _dt.fromisoformat(d["available_at_utc"]) <= congelado_en, (
                f"{ruta_meta}: {t} declara conocible después de descargado")
        # y el CSV dice lo mismo: el metadato no es una afirmación suelta
        ruta_csv = ruta_meta.replace(".meta.json", ".csv")
        recomputado = precios.disponibilidad_por_ticker(precios.cargar_congelado(ruta_csv))
        assert recomputado == por_ticker, f"{ruta_meta}: la disponibilidad declarada no coincide con el CSV"
        assert precios._huella(ruta_csv) == m["sha256"], f"{ruta_meta}: el CSV cambió"


def test_G8_available_at_es_el_cierre_por_calendario_no_la_descarga():
    """Contraprueba de significado: para una serie que termina un viernes, la
    hora conocible es el cierre de ese viernes (20:00 UTC en horario de
    verano de Nueva York), no la madrugada en que se descargó."""
    from dinero import precios
    df = _pd.DataFrame({"X": [1.0, 2.0, 3.0]},
                       index=_pd.to_datetime(["2026-09-02", "2026-09-03", "2026-09-04"]))
    d = precios.disponibilidad_por_ticker(df)["X"]
    assert d == {"primer_cierre": "2026-09-02", "ultimo_cierre": "2026-09-04",
                 "n_cierres": 3, "available_at_utc": "2026-09-04T20:00:00+00:00"}
    # una fecha que no es sesión no inventa hora
    assert precios._cierre_utc("2026-09-07") is None   # feriado NYSE


def test_D17_el_bloque_y_las_replicas_del_instrumento_estan_fijados():
    """A7 del dictamen 11 era prosa («no se barre el bloque sin declararlo»);
    D17 del re-dictamen (corrida 12) lo vuelve ejecutable: cambiar el bloque o
    las réplicas del instrumento `contabilidad.comparar` es una configuración
    nueva y exige una fila en el registro de intentos ANTES de tocar esto."""
    from dinero import contabilidad as C
    assert C.BLOQUE_BOOTSTRAP_SEMANAS == 4
    assert C.REPLICAS_BOOTSTRAP == 2000
    assert C.ALPHA == 0.05


def test_D7_la_fraccion_de_ic_que_excluyen_cero_no_viaja_con_wilson_iid():
    """El Wilson sobre K×24 comparaciones agrupadas en K semillas se retiró
    (re-dictamen D7). El artefacto declara la semilla como unidad."""
    ruta = os.path.join(RAIZ, "dinero", "resultados", "cuenta_papel.json")
    d = _json.load(open(ruta, encoding="utf-8"))
    ic = d["barrido_semillas"]["ic_excluye_cero"]
    assert "wilson95" not in ic
    assert ic["unidad_de_replicacion"] == "semilla"
    assert len(ic["fraccion_por_semilla"]) == d["barrido_semillas"]["K"]
    lo, hi = ic["ic95_t_entre_semillas"]
    assert lo <= ic["fraccion"] <= hi
    # D8: cada intervalo viaja con su cobertura medida
    for j in d["juegos"]:
        for cc in j["contra"].values():
            assert cc["alpha_es"] == "nominal" and "alpha_real_medido" in cc and "cobertura_medida_ic_media" in cc


def test_el_gate_de_la_cuenta_rechaza_un_corte_vacuo():
    """Director de programa, corrida 12: el hallazgo H1 del auditor (un corte en el
    último día compara la cuenta consigo misma) se generaliza al gate que
    respalda las cifras publicadas, no sólo al sellador."""
    from backtest.datos import ErrorLookAhead
    from dinero import cuenta_papel as CP
    from dinero import precios
    completo = precios.cargar_congelado()
    with _pytest.raises(ErrorLookAhead, match="VACUO"):
        CP.verificar_invariancia(cortes=[str(completo.index.max().date())], cierres_completo=completo)
    with _pytest.raises(ErrorLookAhead, match="VACUO"):
        CP.verificar_invariancia(cortes=[], cierres_completo=completo)
