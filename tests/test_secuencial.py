"""
Tests del diseño secuencial pre-registrado (`GEMELO/SECUENCIAL/`).

Dos cosas se prueban acá, y las dos importan por la misma razón: el plan
se ejecuta por primera vez en noviembre de 2026, y para entonces nadie va
a acordarse de nada.

1. **La máquina de fronteras reproduce la literatura.** Es la validación
   externa que la primera versión del diseño no tenía: verificaba su
   Monte Carlo contra sí mismo y por eso congeló un α de 0.05122 creyendo
   que era 0.05.
2. **`mirada.py` computa y decide bien**, sobre datos sintéticos. El
   camino de cómputo no se puede ejercitar contra la base porque todavía
   no hay filas nuevas — y ejercitarlo contra las viejas sería
   exactamente lo que el diseño prohíbe.

Nada acá abre `senales.db`.
"""
import math
import os
import sys

import numpy as np
import pandas as pd
import pytest

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAIZ, "GEMELO", "SECUENCIAL"))

import fronteras as F                      # noqa: E402
import mirada as M                         # noqa: E402
from diseno_secuencial import (            # noqa: E402
    inflacion_por_miradas, n_mcnemar, potencia_secuencial, z_futilidad,
)


# --------------------------------------------------------------------------
# 1. Validación externa de la máquina de fronteras
# --------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _registro_aislado(tmp_path, monkeypatch):
    """NINGÚN test toca el registro de auditoría real.

    Sin esto, dos tests de veredicto escribieron en
    `GEMELO/SECUENCIAL/miradas/registro.log` líneas sintéticas — una de
    ellas "CRUZA LA FRONTERA". Un registro de miradas contaminado por la
    suite es exactamente la clase de cosa que este diseño existe para
    impedir: el día que haya una mirada de verdad, nadie va a poder
    distinguir cuál línea es real. Es `autouse` a propósito, para que
    proteja también a los tests que alguien escriba después sin acordarse.
    """
    destino = tmp_path / "miradas"
    monkeypatch.setattr(M, "DIR_ACTAS", str(destino))
    monkeypatch.setattr(M, "RUTA_REGISTRO", str(destino / "registro.log"))
    yield


def test_ningun_test_escribe_en_el_registro_real():
    """El candado del candado: la ruta real no existe o está vacía de
    entradas sintéticas cuando corre la suite."""
    real = os.path.join(_RAIZ, "GEMELO", "SECUENCIAL", "miradas", "registro.log")
    if os.path.exists(real):
        contenido = open(real, encoding="utf-8").read()
        assert "n=200" not in contenido, (
            "el registro real tiene entradas de los datos sintéticos de los "
            "tests; borrarlo y revisar el aislamiento")


@pytest.mark.parametrize("K", [2, 3, 4, 5])
def test_fronteras_reproducen_jennison_turnbull(K):
    """Pocock y O'Brien-Fleming contra los valores publicados."""
    fr = [(i + 1) / K for i in range(K)]
    malla = F.Malla(fr)
    cp, _ = F.frontera_pocock(fr, malla=malla)
    co, _ = F.frontera_obf(fr, malla=malla)
    ref_p, ref_o = F.REFERENCIA[K]
    assert abs(cp - ref_p) < 0.002, f"Pocock K={K}: {cp} vs {ref_p}"
    assert abs(co - ref_o) < 0.002, f"OBF K={K}: {co} vs {ref_o}"


@pytest.mark.parametrize("K,ref", sorted(F.REFERENCIA_AMR.items()))
def test_inflacion_reproduce_armitage_mcpherson_rowe(K, ref):
    """El camino que calcula el PASIVO, contra la tabla 2 de 1969.

    Es un cómputo distinto al de las fronteras y por eso se valida aparte:
    un error en uno no aparece en el otro.
    """
    fr = [(i + 1) / K for i in range(K)]
    assert abs(F.tasa_error_nominal(fr) - ref) < 0.001


def test_frontera_del_plan_gasta_exactamente_alfa():
    """La familia congelada en DISEÑO.md §A3.4 tiene α global 0.05.

    Este es el test que la v1 no podía pasar: sus umbrales daban 0.05122.
    """
    fr = [0.25, 0.50, 0.75, 1.00]
    malla = F.Malla(fr)
    _, umbrales = F.frontera_obf(fr, malla=malla)
    congelados = [4.048, 2.862, 2.337, 2.024]
    for u, c in zip(umbrales, congelados):
        assert abs(u - c) < 0.005, f"umbral congelado {c} vs calculado {u}"
    alfa, _ = malla.prob_cruce(congelados)
    assert abs(alfa - 0.05) < 0.0015, f"α global {alfa}"


def test_n_max_congelado_da_potencia_080():
    """1.485 filas y no 1.450: el umbral final del plan es 2.024, no 1.96."""
    fr = [0.25, 0.50, 0.75, 1.00]
    malla = F.Malla(fr)
    umbrales = [4.048, 2.862, 2.337, 2.024]
    drift_fijo = 1.959963985 + 0.841621234
    pot_1450, _ = potencia_secuencial(malla, umbrales, drift_fijo)
    assert pot_1450 < 0.80, "el n de muestra fija NO alcanza potencia 0.80"
    pot_1485, _ = potencia_secuencial(malla, umbrales, drift_fijo * math.sqrt(1485 / 1450))
    assert abs(pot_1485 - 0.80) < 0.005


def test_pasivo_es_un_rango_y_el_piso_es_el_extremo_favorable():
    """Poblar el hueco 26-jul/25-ago solo puede SUBIR la inflación."""
    reconstruidas = [228, 228, 228, 223, 184, 223, 245, 240, 253, 253, 248, 248]
    piso = inflacion_por_miradas(reconstruidas)
    con_hueco = inflacion_por_miradas(reconstruidas + [80, 110, 140, 170])
    assert 0.05 < piso < con_hueco
    assert con_hueco > 0.12, "el hueco es el tramo que más infla"


def test_connor_reproduce_el_n_del_plan():
    assert round(n_mcnemar(0.10)) == 403


def test_futilidad_es_monotona():
    """Cuanta más información acumulada, más exigente la futilidad."""
    zs = [z_futilidad(t, 2.024, 2.8352) for t in (0.25, 0.50, 0.75)]
    assert zs[0] < zs[1] < zs[2]


# --------------------------------------------------------------------------
# 2. El camino de cómputo de mirada.py, sobre datos sintéticos
# --------------------------------------------------------------------------

def _df_sintetico(n_fechas: int, por_fecha: int, ventaja: int, semilla: int = 0):
    """Filas con la MISMA estructura que la base: varios tickers por fecha.

    `ventaja` = cuántas fechas son íntegramente a favor del modelo. El
    resto son íntegramente a favor de la base. Es el caso de clustering
    máximo (todos los tickers de una fecha coinciden), que es justamente
    el que un estadístico iid malinterpretaría.
    """
    rng = np.random.default_rng(semilla)
    filas = []
    for j in range(n_fechas):
        a_favor = j < ventaja
        for i in range(por_fecha):
            filas.append({
                "fecha": f"2026-09-{j % 28 + 1:02d}-{j:03d}",
                "ticker": f"T{i}",
                "acierto_gap": 1 if a_favor else 0,
                "base_acierto": 0 if a_favor else 1,
                "gap_pct": rng.normal(),
            })
    return pd.DataFrame(filas)


def test_varianza_cluster_no_revienta_con_varianza_nula():
    """El crash que el segundo dictamen reprodujo.

    Con todas las fechas del mismo signo la varianza remuestreada colapsa
    a cero y `z0/sqrt(0)` reventaba el script EL DÍA DE LA MIRADA. Ahora se
    declara degenerado.
    """
    df = _df_sintetico(n_fechas=8, por_fecha=7, ventaja=8)   # todas a favor
    var = M.varianza_cluster(df)
    assert var["degenerado"] is not None
    assert math.isnan(var["v_hat"])


def test_la_rama_degenerada_devuelve_todas_las_claves():
    """La rama que existía para manejar el caso raro era la única que fallaba.

    `ejecutar` leía `semilla`/`n_draws` de un dict que la rama temprana
    devolvía sin ellas: KeyError. Ningún test la tocaba.
    """
    df = _df_sintetico(n_fechas=1, por_fecha=7, ventaja=1)
    var = M.varianza_cluster(df)
    for clave in ("semilla", "n_draws", "bloques", "regla", "b", "c",
                  "fechas", "ac1", "v_hat", "degenerado"):
        assert clave in var, clave


def test_ejecutar_sobrevive_al_caso_degenerado(monkeypatch):
    df = _df_sintetico(n_fechas=60, por_fecha=7, ventaja=60)
    monkeypatch.setattr(M, "cargar_ventana_nueva", lambda: (df, 253))
    monkeypatch.setattr(M, "PLAN", {1: (100, 2.024, -1.662, "2026-11-19")})
    monkeypatch.setattr(M, "RUTA_REGISTRO", os.devnull)
    s = M.ejecutar(1)                       # no debe lanzar
    assert "NO COMPUTABLE" in s["veredicto"]
    M._formatear(s)                         # el acta tampoco


def test_guard_de_modelo_version(monkeypatch):
    """La cláusula 1 de §A3.7 hecha código: un relevo TERMINA el diseño."""
    monkeypatch.setattr(M, "MODELO_ESPERADO", "9.9.9")
    s = M.ejecutar(1)
    assert "DISEÑO TERMINADO" in s["veredicto"]
    assert "n" in s and s["n"] == 0
    assert "z" not in s


@pytest.mark.parametrize("semilla", [1, 2, 3, 4, 5])
def test_v_hat_domina_a_todos_los_bloques(semilla):
    """La PROPIEDAD que importa: V̂ ≥ V̂_b para todo bloque b, sobre datos
    sorteados. No es la definición del máximo repetida — es que la regla
    se aplique a los tres bloques declarados y a ninguno menos, que es lo
    que se puede romper al editar `BLOQUES_FECHAS` de un lado solo."""
    rng = np.random.default_rng(semilla)
    n_fechas = 60
    filas = []
    for j in range(n_fechas):
        a_favor = bool(rng.integers(0, 2))
        for i in range(7):
            filas.append({"fecha": f"2026-09-{j:03d}", "ticker": f"T{i}",
                          "acierto_gap": int(a_favor),
                          "base_acierto": int(not a_favor),
                          "gap_pct": float(rng.normal())})
    var = M.varianza_cluster(pd.DataFrame(filas))
    assert set(var["v_por_bloque"]) == set(M.BLOQUES_FECHAS)
    for bloque, v in var["v_por_bloque"].items():
        assert var["v_hat"] >= v, (bloque, v, var["v_hat"])


def test_el_acta_no_se_sobrescribe(tmp_path, monkeypatch):
    """Append-only, probado por COMPORTAMIENTO y no por grep del fuente.

    La versión anterior de este test escribía un fixture que no usaba y
    después buscaba dos substrings en el código: nunca ejercitaba la rama
    que dice proteger.
    """
    df = _df_sintetico(n_fechas=200, por_fecha=1, ventaja=140)
    monkeypatch.setattr(M, "cargar_ventana_nueva", lambda: (df, 253))
    monkeypatch.setattr(M, "PLAN", {1: (150, 2.024, -1.662, "2026-11-19")})
    monkeypatch.setattr(sys, "argv", ["mirada", "--mirada", "1", "--escribir"])
    M.main()
    acta = os.path.join(M.DIR_ACTAS, "mirada_1.md")
    primero = open(acta, encoding="utf-8").read()
    with pytest.raises(SystemExit):
        M.main()
    assert open(acta, encoding="utf-8").read() == primero, "el acta se pisó"


def test_la_simulacion_de_correlacion_serial_es_reproducible_y_trae_intervalo():
    """El único cómputo del paquete sin vara externa: si además no fuera
    reproducible ni trajera intervalo, sería el defecto que este documento
    le reprocha a su propia v1."""
    import diseno_secuencial as D
    a = D.alfa_plan_bajo_correlacion(0.20, n_rep=300, n_draws=200)
    b = D.alfa_plan_bajo_correlacion(0.20, n_rep=300, n_draws=200)
    assert a["alfa"] == b["alfa"], "no es determinista con semilla congelada"
    assert a["lo"] < a["alfa"] < a["hi"], a
    assert a["n_rep"] == 300 and a["bloques"] == (1, 5, 10)


def test_el_maximo_nunca_sube_el_alfa_sobre_el_bloque_1():
    """La afirmación que sostiene la regla, medida y no supuesta."""
    import diseno_secuencial as D
    solo1 = D.alfa_plan_bajo_correlacion(0.30, bloques=(1,), n_rep=400, n_draws=200)
    maxim = D.alfa_plan_bajo_correlacion(0.30, bloques=(1, 5, 10), n_rep=400, n_draws=200)
    assert maxim["alfa"] <= solo1["alfa"], (solo1, maxim)


def test_las_fechas_por_mirada_salen_del_calendario():
    """La v3 las puso a ojo en (53,102,153,204). Más fechas = mejor
    bootstrap = α simulado más bajo: el redondeo iba hacia el optimismo."""
    import diseno_secuencial as D
    esperado = tuple(round(t * 1485 / (D.FILAS_POR_DIA_HABIL / D.FECHAS_POR_DIA_HABIL))
                     for t in (0.25, 0.50, 0.75, 1.00))
    assert D.FECHAS_POR_MIRADA == esperado


def test_universo_esperado_esta_congelado():
    """Una constante de pre-registro que 'se completa después' no está
    congelada, y su guard es código muerto hasta entonces."""
    from version import UNIVERSO_VERSION
    assert M.UNIVERSO_ESPERADO == UNIVERSO_VERSION == "4.6.0"


def test_toda_corrida_que_computa_deja_registro(monkeypatch, tmp_path):
    registro = tmp_path / "registro.log"
    df = _df_sintetico(n_fechas=200, por_fecha=1, ventaja=140)
    monkeypatch.setattr(M, "cargar_ventana_nueva", lambda: (df, 253))
    monkeypatch.setattr(M, "PLAN", {1: (150, 2.024, -1.662, "2026-11-19")})
    monkeypatch.setattr(M, "DIR_ACTAS", str(tmp_path))
    monkeypatch.setattr(M, "RUTA_REGISTRO", str(registro))
    M.ejecutar(1)
    assert registro.exists(), "una mirada sin --escribir no dejaba huella"
    assert "mirada=1" in registro.read_text(encoding="utf-8")


def test_avisa_cuando_n_excede_el_plan(monkeypatch, tmp_path):
    df = _df_sintetico(n_fechas=400, por_fecha=1, ventaja=210)
    monkeypatch.setattr(M, "cargar_ventana_nueva", lambda: (df, 253))
    monkeypatch.setattr(M, "RUTA_REGISTRO", str(tmp_path / "r.log"))
    s = M.ejecutar(1)
    assert s["exceso_sobre_plan"] > 0
    assert "Aviso" in M._formatear(s)


def test_verificacion_mc_existe_y_contiene_al_exacto():
    """El documento decía tener una verificación por Monte Carlo y el
    módulo declaraba SEMILLA y N_SIM sin usarlas. Una verificación que no
    está en el repo es una afirmación sobre una verificación."""
    fr = [0.25, 0.50, 0.75, 1.00]
    umbrales = [4.048, 2.862, 2.337, 2.024]
    exacto, _ = F.Malla(fr).prob_cruce(umbrales)
    v = F.verificacion_mc(fr, umbrales)
    assert abs(v["p"] - exacto) < 4 * v["ee"], (v, exacto)


def test_varianza_cluster_detecta_el_agrupamiento():
    """Con todos los tickers de una fecha de acuerdo, V̂ ≈ el nº por fecha.

    Es el caso ρ=1: siete filas de una fecha son UNA observación. Un
    estadístico que ignorara esto inflaría Z por √7 y con eso el α real
    del plan pasaría de 0.05 a 0.19 (`DISEÑO.md` §A3.2).
    """
    por_fecha = 7
    df = _df_sintetico(n_fechas=40, por_fecha=por_fecha, ventaja=24)
    var = M.varianza_cluster(df)
    assert var["fechas"] == 40
    assert var["b"] + var["c"] == 40 * por_fecha
    # El bloque 1 aísla el agrupamiento DENTRO de la fecha: da ≈7.
    assert var["v_por_bloque"][1] == pytest.approx(por_fecha, rel=0.25), var
    # Y los bloques largos ven algo MÁS, porque este sintético es una función
    # escalón (24 fechas a favor y después 16 en contra): tiene, por
    # construcción, la dependencia entre fechas a la que el bloque 1 es
    # ciego. Que V̂ suba acá es el estimador funcionando, no un error.
    assert var["v_hat"] > var["v_por_bloque"][1]


def test_varianza_cluster_es_uno_sin_agrupamiento():
    """Una fila por fecha: no hay clúster que corregir, V̂ ≈ 1."""
    df = _df_sintetico(n_fechas=200, por_fecha=1, ventaja=120)
    var = M.varianza_cluster(df)
    assert var["v_hat"] == pytest.approx(1.0, rel=0.20), var


def test_veredicto_cruza_con_efecto_enorme(monkeypatch):
    df = _df_sintetico(n_fechas=200, por_fecha=1, ventaja=140)
    monkeypatch.setattr(M, "cargar_ventana_nueva", lambda: (df, 253))
    monkeypatch.setattr(M, "PLAN", {1: (150, 2.024, -1.662, "2026-11-19")})
    s = M.ejecutar(1)
    assert s["z"] > 2.024
    assert "CRUZA" in s["veredicto"]
    assert s["descartadas_antecedente"] == 253


def test_veredicto_futilidad_cuando_el_modelo_va_peor(monkeypatch):
    df = _df_sintetico(n_fechas=200, por_fecha=1, ventaja=80)   # base gana
    monkeypatch.setattr(M, "cargar_ventana_nueva", lambda: (df, 253))
    monkeypatch.setattr(M, "PLAN", {1: (150, 4.048, -1.662, "2026-11-19")})
    s = M.ejecutar(1)
    assert s["z"] < -1.662
    assert "FUTILIDAD" in s["veredicto"]


def test_no_computa_si_faltan_filas(monkeypatch):
    """El candado que impide adelantar una mirada."""
    df = _df_sintetico(n_fechas=10, por_fecha=7, ventaja=6)
    monkeypatch.setattr(M, "cargar_ventana_nueva", lambda: (df, 253))
    s = M.ejecutar(1)
    assert s["veredicto"] == "TODAVÍA NO"
    assert s["faltan"] == 371 - 70
    assert "z" not in s, "no debe computarse el estadístico antes de tiempo"


def test_la_ventana_antecedente_no_puede_entrar(monkeypatch):
    """El candado estructural, probado por COMPORTAMIENTO.

    La versión anterior hacía grep de una línea del fuente. Acá se le pasa
    un frame que MEZCLA fechas anteriores y posteriores al congelamiento y
    se verifica que las anteriores no sobrevivan.
    """
    assert M.FECHA_CONGELAMIENTO == "2026-08-31"
    assert M.CONVENCION == "excluir_cero"
    filas = []
    for fecha in ("2026-08-20", "2026-08-31", "2026-09-01", "2026-09-02"):
        for i in range(3):
            filas.append({"fecha": fecha, "ticker": f"T{i}", "gap_pct": 1.0,
                          "acierto_gap": 1, "retorno_real_pct": 0.5})
    monkeypatch.setattr(M, "cargar", lambda: pd.DataFrame(filas))
    df, descartadas = M.cargar_ventana_nueva()
    assert descartadas == 6, "las del 20 y del 31-ago tienen que caer"
    assert set(df["fecha"]) == {"2026-09-01", "2026-09-02"}
    assert (df["fecha"] > M.FECHA_CONGELAMIENTO).all()


def test_mirada_no_importa_el_motor():
    """La regla cero: la capa de investigación no toca la de sellado."""
    fuente = open(os.path.join(_RAIZ, "GEMELO", "SECUENCIAL", "mirada.py"),
                  encoding="utf-8").read()
    for prohibido in ("import motor", "from motor", "import snapshot",
                      "from snapshot", "import senales", "from senales"):
        assert prohibido not in fuente, prohibido
