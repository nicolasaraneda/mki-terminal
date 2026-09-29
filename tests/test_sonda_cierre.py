"""Corrida 13, bloque 3 — la sonda del cierre (GEMELO/sonda_cierre.py) y su
resumen (GEMELO/sonda_cierre_resumen.py).

Sin red: la «respuesta grabada» es una extensión real del sellador
(`dinero/datos/sello/ext_2026-09-18.csv`, la matriz Close que yfinance
devolvió el 19-sep a las 03:30 UTC y que dejó a TOELY sin cierre), leída del
disco. La sonda no sella, no escribe en dinero/, no abre ninguna base, y no
importa nada del camino de sellado ni de dinero/: hay test para cada cosa."""
import ast
import csv
import os
import shutil
import subprocess
from datetime import datetime, timezone

import pandas as pd
import pytest

from GEMELO import sonda_cierre as SC
from GEMELO import sonda_cierre_resumen as SR

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UTC = timezone.utc
EXT_18 = os.path.join(RAIZ, "dinero", "datos", "sello", "ext_2026-09-18.csv")


def _respuesta_grabada():
    if not os.path.exists(EXT_18):
        pytest.skip("la extensión del 18-sep no está en este checkout")
    return pd.read_csv(EXT_18, index_col=0, parse_dates=True)


# ------------------------------------------------------------
# 1. observar(): función pura de (respuesta, instante)
# ------------------------------------------------------------
def test_la_respuesta_del_18_sep_deja_a_TOELY_sin_cierre_de_hoy():
    """Lo que el timer vio el 19-sep 03:30 UTC (18-sep 23:30 NY): 35 de 36
    con el cierre del 18-sep; TOELY con último cierre el 17-sep."""
    filas = SC.observar(_respuesta_grabada(), datetime(2026, 9, 19, 3, 30, 2, tzinfo=UTC))
    assert len(filas) == 36 and {f["sesion_ny"] for f in filas} == {"2026-09-18"}
    assert {f["hora_ny"] for f in filas} == {"23:30"}
    sin_hoy = [f for f in filas if not f["es_sesion_de_hoy"]]
    assert [f["ticker"] for f in sin_hoy] == ["TOELY"]
    assert sin_hoy[0]["ultima_fecha_close"] == "2026-09-17"
    assert all(f["ultima_fecha_close"] == "2026-09-18" for f in filas if f["es_sesion_de_hoy"])
    assert all(f["n_filas_respuesta"] == 9 for f in filas)
    assert all(f["close_ultimo"] and float(f["close_ultimo"]) > 0 for f in filas)


def test_la_misma_respuesta_a_otra_hora_dice_otra_hora_y_la_misma_sesion():
    """La hora es un dato de la sonda, no de la respuesta: 17:05 NY del
    18-sep sobre la misma matriz da la misma sesión y otra hora."""
    filas = SC.observar(_respuesta_grabada(), datetime(2026, 9, 18, 21, 5, tzinfo=UTC))
    assert {f["hora_ny"] for f in filas} == {"17:05"} and {f["sesion_ny"] for f in filas} == {"2026-09-18"}
    assert sum(f["es_sesion_de_hoy"] for f in filas) == 35


def test_en_fin_de_semana_o_feriado_no_hay_sesion_de_hoy():
    """`sesion_de_hoy()` sigue contestando lo que su nombre dice: la sesión del
    DÍA del calendario, o None. Lo que cambió en la corrida 14 es que
    `observar()` ya no la usa (ver `sesion_atribuida`)."""
    sabado = datetime(2026, 9, 19, 20, 0, tzinfo=UTC)            # sábado 16:00 NY
    assert SC.sesion_de_hoy(sabado) is None
    assert SC.sesion_de_hoy(datetime(2026, 9, 7, 20, 0, tzinfo=UTC)) is None      # Labor Day
    assert SC.sesion_de_hoy(datetime(2026, 9, 18, 23, 59, tzinfo=UTC)) == "2026-09-18"
    # 03:30 UTC del 19-sep todavía es 18-sep en Nueva York
    assert SC.sesion_de_hoy(datetime(2026, 9, 19, 3, 30, tzinfo=UTC)) == "2026-09-18"


# ------------------------------------------------------------
# 1-bis. La atribución de sesión pasada la medianoche (corrida 14, bloque 1.2)
# ------------------------------------------------------------
def test_una_observacion_anterior_a_la_apertura_pertenece_a_la_sesion_anterior():
    """La regla nueva, a los dos lados de la medianoche y a los dos lados de
    la apertura. Sin red: `sesion_atribuida` es función pura del instante.

    2026-09-25 es viernes; 26 sábado; 27 domingo; 28 lunes; 29 martes.
    El lunes 7-sep-2026 fue Labor Day, así que la madrugada del martes 8
    tiene que caer en el viernes 4."""
    def s(iso):
        return SC.sesion_atribuida(datetime.fromisoformat(iso))

    # madrugada del martes → lunes (los dos extremos de la franja propuesta)
    assert s("2026-09-29T04:35:00+00:00") == "2026-09-28"       # 00:35 NY
    assert s("2026-09-29T07:35:00+00:00") == "2026-09-28"       # 03:35 NY
    # madrugada del lunes → viernes anterior, no «el lunes todavía sin cierre»
    assert s("2026-09-28T04:35:00+00:00") == "2026-09-25"
    # sábado de madrugada y domingo → viernes
    assert s("2026-09-26T05:05:00+00:00") == "2026-09-25"       # sáb 01:05 NY
    assert s("2026-09-27T06:05:00+00:00") == "2026-09-25"       # dom 02:05 NY
    # sábado por la tarde: ya no se pierde la observación, habla del viernes
    assert s("2026-09-19T20:00:00+00:00") == "2026-09-18"
    # la tarde/noche de un día hábil sigue siendo su propia sesión
    assert s("2026-09-26T00:05:00+00:00") == "2026-09-25"       # vie 20:05 NY
    assert s("2026-09-28T17:42:55+00:00") == "2026-09-28"       # lun 13:42 NY
    # el corte es la apertura, minuto a minuto
    assert s("2026-09-28T13:29:00+00:00") == "2026-09-25"       # 09:29 NY
    assert s("2026-09-28T13:30:00+00:00") == "2026-09-28"       # 09:30 NY
    # feriado: la madrugada del martes 8-sep cae en el viernes 4 (Labor Day)
    assert s("2026-09-08T05:05:00+00:00") == "2026-09-04"
    # nunca devuelve None: eso es lo que hacía perder la observación
    for iso in ("2026-09-26T05:05:00+00:00", "2026-09-19T20:00:00+00:00"):
        assert SC.sesion_atribuida(datetime.fromisoformat(iso))


def test_sesion_atribuida_exige_zona_horaria():
    with pytest.raises(ValueError):
        SC.sesion_atribuida(datetime(2026, 9, 29, 4, 35))


def test_observar_de_madrugada_atribuye_el_cierre_a_la_sesion_anterior():
    """La MISMA matriz del 18-sep, mirada a las 00:35 NY del sábado 19: antes
    daba sesión vacía y cero información; ahora dice lo que de verdad dice —
    el cierre del viernes 18 está para 35 de 36 y le falta TOELY."""
    filas = SC.observar(_respuesta_grabada(), datetime(2026, 9, 19, 4, 35, tzinfo=UTC))
    assert {f["sesion_ny"] for f in filas} == {"2026-09-18"}
    assert {f["hora_ny"] for f in filas} == {"00:35"}
    assert sum(f["es_sesion_de_hoy"] for f in filas) == 35
    assert [f["ticker"] for f in filas if not f["es_sesion_de_hoy"]] == ["TOELY"]


def test_la_regla_nueva_reproduce_el_sesion_ny_de_todas_las_filas_ya_escritas():
    """Por qué el esquema NO cambia y ninguna fila se reescribe: sobre el CSV
    real, la regla nueva devuelve exactamente el `sesion_ny` grabado en cada
    fila. Todas las filas escritas hasta la corrida 14 son sondas de
    20:05–23:35 NY en días con sesión, donde las dos reglas coinciden. Si
    algún día este test falla, hay filas de dos semánticas en el mismo archivo
    y el resumen necesita leer dos formatos."""
    ruta = SC.RUTA_CSV
    if not os.path.exists(ruta):
        pytest.skip("sin CSV de la sonda en este checkout")
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    if not filas:
        pytest.skip("CSV de la sonda vacío")
    distintas = [x for x in filas
                 if SC.sesion_atribuida(datetime.fromisoformat(x["timestamp_utc"])) != x["sesion_ny"]]
    assert not distintas, (len(distintas), distintas[:3])


def test_un_ticker_ausente_de_la_respuesta_queda_registrado_sin_fecha():
    r = _respuesta_grabada().drop(columns=["NVDA"])
    filas = SC.observar(r, datetime(2026, 9, 19, 3, 30, tzinfo=UTC), tickers=["NVDA", "AMD"])
    por = {f["ticker"]: f for f in filas}
    assert por["NVDA"]["ultima_fecha_close"] == "" and por["NVDA"]["es_sesion_de_hoy"] == 0
    assert por["AMD"]["es_sesion_de_hoy"] == 1


def test_observar_exige_zona_horaria():
    with pytest.raises(ValueError, match="zona horaria"):
        SC.observar(_respuesta_grabada(), datetime(2026, 9, 19, 3, 30))


def test_los_tickers_salen_del_meta_del_congelado_como_texto():
    t = SC.tickers_operables()
    assert len(t) == 36 and "TOELY" in t and "SHECY" in t
    assert list(_respuesta_grabada().columns) == t


# ------------------------------------------------------------
# 2. registrar(): append, cabecera una sola vez
# ------------------------------------------------------------
def test_registrar_agrega_filas_y_la_cabecera_una_sola_vez(tmp_path):
    ruta = str(tmp_path / "sonda.csv")
    r = _respuesta_grabada()
    SC.registrar(SC.observar(r, datetime(2026, 9, 18, 21, 5, tzinfo=UTC)), ruta)
    SC.registrar(SC.observar(r, datetime(2026, 9, 19, 3, 30, tzinfo=UTC)), ruta)
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert len(filas) == 72 and list(filas[0].keys()) == list(SC.COLUMNAS)
    assert sum(1 for l in open(ruta, encoding="utf-8") if l.startswith("timestamp_utc")) == 1


def test_main_sin_red_observa_un_csv_grabado(tmp_path, capsys):
    """El camino de `--desde-csv`: sin red, escribe al CSV que se le indica."""
    ruta = str(tmp_path / "s.csv")
    if not os.path.exists(EXT_18):
        pytest.skip("la extensión del 18-sep no está en este checkout")
    assert SC.main(["--desde-csv", EXT_18, "--csv", ruta, "--ahora-utc", "2026-09-19T03:30:02+00:00"]) == 0
    salida = capsys.readouterr().out
    assert "35/36" in salida and "TOELY" in salida
    assert sum(1 for _ in open(ruta, encoding="utf-8")) == 37


# ------------------------------------------------------------
# 3. El resumen, con un CSV sintético de tres noches
# ------------------------------------------------------------
def _csv_sintetico(ruta):
    """Tres noches (16, 17 y 18-sep), sondas cada media hora de 17:05 a 23:35 NY,
    tres tickers: A aparece siempre a las 17:05; B a las 19:35, 20:05 y 19:35;
    C a las 22:05 las dos primeras noches y NUNCA la tercera. Más una sonda de
    sábado (sin sesión) que el resumen tiene que ignorar."""
    horas = [f"{h:02d}:{m:02d}" for h in range(17, 24) for m in (5, 35)]
    aparece = {"A": ["17:05", "17:05", "17:05"], "B": ["19:35", "20:05", "19:35"], "C": ["22:05", "22:05", None]}
    filas = []
    for i, noche in enumerate(("2026-09-16", "2026-09-17", "2026-09-18")):
        for h in horas:
            for t, ap in aparece.items():
                vio = ap[i] is not None and h >= ap[i]
                filas.append({"timestamp_utc": f"{noche}T{h}:00+00:00", "hora_ny": h, "sesion_ny": noche, "ticker": t,
                              "ultima_fecha_close": noche if vio else "2026-09-15", "es_sesion_de_hoy": int(vio),
                              "close_ultimo": "1.0", "n_filas_respuesta": 5})
    filas.append({"timestamp_utc": "2026-09-19T20:00:00+00:00", "hora_ny": "16:00", "sesion_ny": "", "ticker": "A",
                  "ultima_fecha_close": "2026-09-18", "es_sesion_de_hoy": 0, "close_ultimo": "1.0", "n_filas_respuesta": 5})
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(SC.COLUMNAS))
        w.writeheader()
        w.writerows(filas)
    return ruta


def test_el_resumen_da_mediana_y_maxima_por_ticker_y_la_hora_de_todos_por_noche(tmp_path):
    r = SR.resumen(SR.cargar(_csv_sintetico(str(tmp_path / "s.csv"))))
    assert r["noches"] == 3 and r["noches_con_todos"] == 2
    assert r["tickers"]["A"] == {"noches": 3, "noches_con_cierre": 3, "noches_sin_cierre_hasta_la_ultima_sonda": 0,
                                 "hora_mediana_ny": "17:05", "hora_maxima_ny": "17:05", "hora_minima_ny": "17:05"}
    assert r["tickers"]["B"]["hora_mediana_ny"] == "19:35" and r["tickers"]["B"]["hora_maxima_ny"] == "20:05"
    assert r["tickers"]["C"]["noches_con_cierre"] == 2 and r["tickers"]["C"]["noches_sin_cierre_hasta_la_ultima_sonda"] == 1
    assert r["tickers"]["C"]["hora_maxima_ny"] == "22:05"
    assert r["por_noche"]["2026-09-16"]["hora_todos_ny"] == "22:05" and r["por_noche"]["2026-09-16"]["faltan_hasta_la_ultima_sonda"] == []
    assert r["por_noche"]["2026-09-17"]["hora_todos_ny"] == "22:05"
    assert r["por_noche"]["2026-09-18"]["hora_todos_ny"] is None and r["por_noche"]["2026-09-18"]["faltan_hasta_la_ultima_sonda"] == ["C"]
    assert r["por_noche"]["2026-09-18"]["ultima_sonda_ny"] == "23:35" and r["por_noche"]["2026-09-18"]["sondas"] == 14
    assert r["hora_todos_mediana_ny"] == "22:05" and r["hora_todos_maxima_ny"] == "22:05"
    assert "PROPUESTA" in r["estatus"]


def test_el_resumen_escribe_md_y_json_y_declara_las_noches(tmp_path):
    csvp = _csv_sintetico(str(tmp_path / "s.csv"))
    salida = str(tmp_path / "res")
    assert SR.main(["--csv", csvp, "--salida", salida]) == 0
    md = open(salida + ".md", encoding="utf-8").read()
    assert "Noches con sesión: **3**" in md and "| C | 3 | 2 | 1 |" in md and "| 2026-09-18 | 14 | 23:35 | 2/3 | — | C |" in md
    assert os.path.exists(salida + ".json")


def test_la_noche_es_una_unidad_al_cruzar_la_medianoche(tmp_path):
    """Bloque 1.3. CSV sintético de UNA noche (viernes 25-sep) con sondas de
    20:05 a 23:35 NY y de 00:05 a 03:35 NY del sábado, todas con
    `sesion_ny=2026-09-25`. El ticker LENTO recién aparece a las 01:05 NY, ya
    pasada la medianoche.

    Sin el reloj monótono, `min` tomaba 01:05 (65 minutos) como la PRIMERA
    sonda de la noche y la aparición de LENTO se leía como la más temprana de
    todas, más temprana que la de las 20:05. Ahora 01:05 vale 1.505 y el
    informe lo muestra como «01:05 (+1d)»."""
    ruta = str(tmp_path / "noche.csv")
    tarde = [(f"2026-09-{25 if h >= 20 else 26}T{(h + 4) % 24:02d}:{m:02d}:00+00:00", f"{h:02d}:{m:02d}")
             for h in list(range(20, 24)) + [0, 1, 2, 3] for m in (5, 35)]
    filas = []
    for ts, hora in tarde:
        for t, desde in (("PRONTO", "20:05"), ("LENTO", "01:05")):
            # «visto» si ya pasó su hora de aparición en el reloj de la noche
            orden = (lambda h: (int(h[:2]) + (24 if int(h[:2]) < 12 else 0)) * 60 + int(h[3:]))
            vio = orden(hora) >= orden(desde)
            filas.append({"timestamp_utc": ts, "hora_ny": hora, "sesion_ny": "2026-09-25", "ticker": t,
                          "ultima_fecha_close": "2026-09-25" if vio else "2026-09-24",
                          "es_sesion_de_hoy": int(vio), "close_ultimo": "1.0", "n_filas_respuesta": 7})
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(SC.COLUMNAS))
        w.writeheader()
        w.writerows(filas)

    r = SR.resumen(SR.cargar(ruta))
    # UNA sola noche, no dos: la madrugada no abre una noche nueva
    assert r["noches"] == 1 and list(r["por_noche"]) == ["2026-09-25"]
    assert r["por_noche"]["2026-09-25"]["sondas"] == 16
    # el reloj de la noche es monótono: la madrugada es lo ÚLTIMO, no lo primero
    assert SR.minutos_de_la_noche("2026-09-26T00:05:00+00:00", "2026-09-25", "20:05") == 1205
    assert SR.minutos_de_la_noche("2026-09-26T05:05:00+00:00", "2026-09-25", "01:05") == 1505
    assert SR.minutos_de_la_noche("2026-09-26T07:35:00+00:00", "2026-09-25", "03:35") == 1655
    # y las apariciones se leen en ese orden
    assert r["tickers"]["PRONTO"]["hora_minima_ny"] == "20:05"
    assert r["tickers"]["LENTO"]["hora_minima_ny"] == "01:05 (+1d)"
    assert r["por_noche"]["2026-09-25"]["hora_todos_ny"] == "01:05 (+1d)"
    assert r["por_noche"]["2026-09-25"]["ultima_sonda_ny"] == "03:35 (+1d)"
    assert r["por_noche"]["2026-09-25"]["faltan_hasta_la_ultima_sonda"] == []
    assert r["hora_todos_maxima_ny"] == "01:05 (+1d)"
    md = SR.informe(r, ruta)
    assert "01:05 (+1d)" in md


def test_el_hhmm_de_la_noche_marca_el_dia_y_no_cambia_lo_de_siempre():
    """Por debajo de la medianoche el informe sale byte a byte como antes."""
    assert SR._hhmm(1205) == "20:05" and SR._hhmm(1415) == "23:35"
    assert SR._hhmm(1445) == "00:05 (+1d)" and SR._hhmm(1505) == "01:05 (+1d)"
    assert SR._hhmm(None) is None


def test_el_resumen_sin_sondas_con_sesion_lo_dice(tmp_path):
    ruta = str(tmp_path / "v.csv")
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(SC.COLUMNAS)); w.writeheader()
        w.writerow({"timestamp_utc": "2026-09-19T20:00:00+00:00", "hora_ny": "16:00", "sesion_ny": "", "ticker": "A",
                    "ultima_fecha_close": "", "es_sesion_de_hoy": 0, "close_ultimo": "", "n_filas_respuesta": 0})
    r = SR.resumen(SR.cargar(ruta))
    assert r["noches"] == 0 and "sin sondas" in r["nota"]


# ------------------------------------------------------------
# 4. Aislamiento: no sella, no toca dinero/, no abre bases
# ------------------------------------------------------------
def _importados(ruta):
    arbol = ast.parse(open(ruta, encoding="utf-8").read())
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres |= {a.name.split(".")[0] for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module.split(".")[0])
    return nombres


def test_la_sonda_no_importa_dinero_ni_el_camino_de_sellado_ni_bases():
    for modulo in (SC, SR):
        imp = _importados(modulo.__file__)
        assert not (imp & {"dinero", "motor", "senales", "snapshot", "universo", "alertas", "calendarios",
                           "sqlite3", "noticias", "mki_backup", "mki_vigia"}), (modulo.__name__, imp)
        # ninguna RUTA del código (constantes de texto, no comentarios) apunta a la base ni a dinero/
        arbol = ast.parse(open(modulo.__file__, encoding="utf-8").read())
        literales = [n.value for n in ast.walk(arbol) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        assert not [s for s in literales if ".db" in s], (modulo.__name__, [s for s in literales if ".db" in s])
        assert not [s for s in literales if s.startswith("dinero/") or s.endswith("sello_dinero.py")]
    assert not SC.__file__.startswith(os.path.join(RAIZ, "dinero"))
    assert SC.RUTA_CSV == os.path.join(RAIZ, "data", "sonda_cierre.csv")


def test_la_sonda_no_escribe_en_dinero_al_observar_ni_al_registrar(tmp_path):
    carpeta = os.path.join(RAIZ, "dinero", "datos", "sello")
    if not os.path.isdir(carpeta):
        pytest.skip("sin carpeta de extensiones en este checkout")
    antes = {a: os.stat(os.path.join(carpeta, a)).st_mtime_ns for a in os.listdir(carpeta)}
    SC.registrar(SC.observar(_respuesta_grabada(), datetime(2026, 9, 19, 3, 30, tzinfo=UTC)), str(tmp_path / "s.csv"))
    assert {a: os.stat(os.path.join(carpeta, a)).st_mtime_ns for a in os.listdir(carpeta)} == antes


# ------------------------------------------------------------
# 5. La unidad de systemd propuesta: expresión válida y que no pisa al sellador
# ------------------------------------------------------------
def _directivas(ruta):
    """Las directivas de una unidad, con las repetidas (OnCalendar) en lista."""
    d = {}
    for l in open(ruta, encoding="utf-8").read().splitlines():
        if "=" in l and not l.startswith("#"):
            k, v = l.split("=", 1)
            d.setdefault(k, []).append(v)
    return d


def test_la_unidad_propuesta_no_coincide_con_el_sellador_y_no_es_persistente():
    """Corrida 14: la plantilla lleva DOS franjas. La de tarde queda alineada
    con la que Nicolás instaló al firmar §88.1 (`20..23:05,35`, no la
    `17..23:05,35` que nunca se instaló) y la de madrugada
    (`Tue..Sat 00..03:05,35`) es la propuesta de esta corrida."""
    ruta = os.path.join(RAIZ, "GEMELO", "propuestas", "systemd", "mki-sonda-cierre.timer")
    d = _directivas(ruta)
    assert d["OnCalendar"] == ["Mon..Fri 20..23:05,35 America/New_York",
                              "Tue..Sat 00..03:05,35 America/New_York"]
    assert d["Persistent"] == ["false"]
    assert d["Unit"] == ["mki-sonda-cierre.service"]
    servicio = open(ruta.replace(".timer", ".service"), encoding="utf-8").read()
    assert "__MKI_DIR__/venv/bin/python -m GEMELO.sonda_cierre" in servicio and "__MKI_DIR__" in servicio
    assert "--sellar" not in servicio
    # la franja de madrugada termina seis horas antes de la apertura de NYSE
    assert "00..03:05,35" in d["OnCalendar"][1]
    # ninguna de las dos pisa el minuto en que el sellador baja su insumo
    assert not [e for e in d["OnCalendar"] if ":00,30" in e or "23:30" in e]
    if shutil.which("systemd-analyze") is None:
        pytest.skip("sin systemd-analyze en esta máquina")
    for expresion, normalizada in zip(d["OnCalendar"], ("20..23:05,35:00", "00..03:05,35:00")):
        r = subprocess.run(["systemd-analyze", "calendar", expresion], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert normalizada in r.stdout             # nunca :30 en punto


def test_la_plantilla_declara_que_persistent_false_no_frena_un_despertar():
    """La plantilla decía que `Persistent=false` bastaba para que un despertar
    no dispare lo atrasado. El 28-sep-2026 la unidad instalada disparó a las
    14:42:52 con la bolsa abierta llevando `Persistent=false`: la directiva
    sólo gobierna los disparos perdidos mientras el manager no corría, y el
    manager no se cayó. La advertencia medida tiene que quedar escrita."""
    ruta = os.path.join(RAIZ, "GEMELO", "propuestas", "systemd", "mki-sonda-cierre.timer")
    texto = open(ruta, encoding="utf-8").read()
    assert "ADVERTENCIA MEDIDA" in texto
    assert "suspend" in texto.lower() or "SUSPENDIDA" in texto
    assert "14:42:52" in texto
