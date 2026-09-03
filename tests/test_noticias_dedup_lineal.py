"""Corrida 09 (3-sep-2026), frente 2c — el dedup retroactivo de noticias ya no
es O(n²) sobre el historial completo.

Hasta el 2-sep `noticias.migrar_noticias_v2()` comparaba cada titular contra
TODOS los anteriores en cada corrida (acta §73: ~7.16e-5·n² s; el 1-sep systemd
mató el job a los 1800 s). Ahora una marca en la tabla `meta` recuerda hasta
qué id se procesó y cada candidata se compara solo con su ventana de
±VENTANA_DEDUP_RETRO_DIAS días. Estos tests prueban:

1. el costo por corrida (comparaciones SequenceMatcher) NO crece con el
   historial: N y 2N filas → mismas comparaciones por corrida;
2. equivalencia con la migración completa dentro de la ventana, y el caso
   DECLARADO que ya no se detecta (réplica que reaparece fuera de la ventana);
3. "el más antiguo sobrevive" en las dos direcciones (una candidata con fecha
   más antigua desplaza a la réplica posterior ya procesada);
4. idempotencia y esquema aditivo.

Todo sobre bases sintéticas en tmp (noticias.DB_PATH parcheado); nunca la real.
"""
import difflib
import inspect
import random
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

import noticias

AHORA = datetime.now(timezone.utc).replace(microsecond=0)
# Vocabulario de letras al azar (semilla fija): dos titulares construidos con
# él quedan lejos del umbral 0.85. Un prefijo común ("palabraNNN") no sirve:
# difflib los ve parecidos y aparecen duplicados accidentales en cadena.
_rng_vocab = random.Random(20260903)
VOCAB = ["".join(_rng_vocab.choice("abcdefghijklmnopqrstuvwxyz")
                 for _ in range(_rng_vocab.randint(4, 9))) for _ in range(400)]


# ------------------------------------------------------------
# Utilería
# ------------------------------------------------------------
@pytest.fixture
def base(tmp_path, monkeypatch):
    ruta = tmp_path / "noticias_sintetica.db"
    monkeypatch.setattr(noticias, "DB_PATH", str(ruta))
    noticias.init_db()
    return ruta


def _fecha(dias_atras: float) -> str:
    return (AHORA - timedelta(days=dias_atras)).isoformat()


def _titular_distinto(rng: random.Random) -> str:
    # 7 palabras de un vocabulario de 400: dos titulares al azar quedan muy por
    # debajo del umbral 0.85 de difflib.
    return " ".join(rng.choice(VOCAB) for _ in range(7)) + " nvidia"


def _insertar(ruta, fecha, titular, url=None) -> int:
    conn = sqlite3.connect(ruta)
    _insertar.contador += 1
    cur = conn.execute(
        "INSERT INTO titulares (fecha, fuente, titular, url, tickers) VALUES (?, ?, ?, ?, '')",
        (fecha, "test", titular, url or f"http://t/{_insertar.contador}"),
    )
    conn.commit()
    id_ = cur.lastrowid
    conn.close()
    return id_


_insertar.contador = 0


def _poblar_historial(ruta, dias: int, por_dia: int, semilla: int) -> list:
    """`dias` días hacia atrás (1..dias), `por_dia` titulares distintos por día,
    insertados en orden cronológico. Devuelve los ids."""
    rng = random.Random(semilla)
    ids = []
    for d in range(dias, 0, -1):
        for k in range(por_dia):
            ids.append(_insertar(ruta, _fecha(d + k / (por_dia * 10)), _titular_distinto(rng)))
    return ids


def _ids(ruta) -> set:
    conn = sqlite3.connect(ruta)
    r = {f[0] for f in conn.execute("SELECT id FROM titulares")}
    conn.close()
    return r


def _dedup_completa_4_6(ruta) -> tuple:
    """Referencia: el bucle EXACTO de la migración completa de la Etapa 4.6
    (vigente hasta el 2-sep-2026) — cada titular contra TODOS los anteriores
    supervivientes, en orden (fecha, id). Solo calcula, no borra.
    Devuelve (ids_duplicados, comparaciones)."""
    conn = sqlite3.connect(ruta)
    filas = conn.execute(
        "SELECT id, titular FROM titulares ORDER BY fecha ASC, id ASC").fetchall()
    conn.close()
    vistos, duplicados, comparaciones = [], [], 0
    for id_, titular in filas:
        normalizado = noticias._normalizar_titular(titular)
        if not normalizado:
            continue
        es_dup = False
        for previo in vistos:
            comparaciones += 1
            if difflib.SequenceMatcher(None, normalizado, previo).ratio() > noticias.UMBRAL_SIMILITUD_DUP:
                es_dup = True
                break
        if es_dup:
            duplicados.append(id_)
        else:
            vistos.append(normalizado)
    return set(duplicados), comparaciones


class _ContadorSequenceMatcher:
    """Reemplazo de difflib.SequenceMatcher que cuenta instancias y decide por
    igualdad exacta (ratio 1.0 / 0.0): el conteo es lo que importa."""
    llamadas = 0

    def __init__(self, isjunk, a, b):
        type(self).llamadas += 1
        self._igual = a == b

    def ratio(self):
        return 1.0 if self._igual else 0.0


# ------------------------------------------------------------
# 1. Costo por corrida: lineal en las candidatas, independiente del historial
# ------------------------------------------------------------
def test_comparaciones_por_corrida_no_crecen_con_el_historial(tmp_path, monkeypatch):
    monkeypatch.setattr(difflib, "SequenceMatcher", _ContadorSequenceMatcher)
    POR_DIA, NUEVAS = 20, 20
    medido = {}
    for dias in (20, 40):  # N = 400 y 2N = 800 filas de historial
        ruta = tmp_path / f"h{dias}.db"
        monkeypatch.setattr(noticias, "DB_PATH", str(ruta))
        noticias.init_db()
        _poblar_historial(ruta, dias, POR_DIA, semilla=dias)
        n = len(_ids(ruta))
        assert n == dias * POR_DIA

        _ContadorSequenceMatcher.llamadas = 0
        r1 = noticias.migrar_noticias_v2()  # primera corrida: sin marca
        boot = _ContadorSequenceMatcher.llamadas
        assert r1["primera_corrida"] is True
        assert r1["comparaciones"] == boot  # el contador interno coincide con el externo

        rng = random.Random(1000 + dias)
        for _ in range(NUEVAS):
            _insertar(ruta, _fecha(0.01), _titular_distinto(rng))
        _ContadorSequenceMatcher.llamadas = 0
        r2 = noticias.migrar_noticias_v2()  # corrida diaria: solo las NUEVAS
        dia = _ContadorSequenceMatcher.llamadas
        assert r2["primera_corrida"] is False
        assert r2["candidatos"] == NUEVAS

        vieja_dups, vieja_comp = _dedup_completa_4_6(ruta)
        medido[dias] = {"n": n, "boot": boot, "dia": dia, "vieja": vieja_comp}

    a, b = medido[20], medido[40]
    # Corrida diaria: duplicar el historial NO cambia el trabajo (misma ventana).
    assert b["dia"] == a["dia"], medido
    # Cada nueva se compara como mucho con la ventana (10 días × 20/día + las nuevas):
    assert a["dia"] <= NUEVAS * (10 * POR_DIA + NUEVAS), medido
    # Primera corrida (sin marca): todas las filas son candidatas, cada una
    # contra su ventana → crece LINEALMENTE con el historial: cada fila extra
    # cuesta como mucho una ventana (10 días × 20/día), y 2N cuesta < 2.5× N…
    assert b["boot"] - a["boot"] <= (b["n"] - a["n"]) * (10 * POR_DIA), medido
    assert b["boot"] / a["boot"] < 2.5, medido
    # …mientras que la migración completa crecía cuadráticamente (≈4× con 2N):
    assert b["vieja"] / a["vieja"] > 3.5, medido
    assert a["boot"] < a["vieja"] and b["boot"] < b["vieja"] / 2, medido


# ------------------------------------------------------------
# 2. Equivalencia con la migración completa dentro de la ventana + caso declarado
# ------------------------------------------------------------
def test_equivalencia_dentro_de_la_ventana_y_caso_declarado(base):
    ruta = base
    _poblar_historial(ruta, dias=30, por_dia=4, semilla=7)
    V = noticias.VENTANA_DEDUP_RETRO_DIAS
    assert V == 10, "la ventana pactada es la misma del dedup de inserción (10 días)"

    # A) réplica dentro de la ventana: original hace 3 días, réplica hace 1.
    a_orig = _insertar(ruta, _fecha(3.5), "Nvidia unveils Rubin GPU roadmap at GTC keynote")
    a_rep = _insertar(ruta, _fecha(1.5), "Nvidia unveils Rubin GPU roadmap at GTC keynote - Reuters")
    # C) réplica FUERA de la ventana: original hace 20 días, réplica hace 2.
    c_orig = _insertar(ruta, _fecha(20.5), "TSMC posts record quarterly revenue on AI demand")
    c_rep = _insertar(ruta, _fecha(2.5), "TSMC posts record quarterly revenue on AI demand")
    # D) la réplica se insertó ANTES (id menor) pero con fecha posterior: el
    #    más antiguo por fecha sobrevive, igual que en la migración completa.
    d_rep = _insertar(ruta, _fecha(4.0), "Samsung wins HBM4 qualification from Nvidia")
    d_orig = _insertar(ruta, _fecha(5.0), "Samsung wins HBM4 qualification from Nvidia: report")

    vieja, _ = _dedup_completa_4_6(ruta)
    assert {a_rep, c_rep, d_rep} <= vieja

    antes = _ids(ruta)
    res = noticias.migrar_noticias_v2()
    nueva = antes - _ids(ruta)
    assert res["duplicados_borrados"] == len(nueva)

    # Dentro de la ventana: el MISMO conjunto que la migración completa.
    assert nueva <= vieja
    assert {a_rep, d_rep} <= nueva
    assert {a_orig, c_orig, d_orig} <= _ids(ruta)
    # COMPORTAMIENTO DECLARADO: la réplica que reaparece más de V días después
    # de su original ya no se detecta (parche_timeout_noticias.md §d, riesgo
    # aceptado a cambio de un costo por corrida que no crece con el historial).
    assert vieja - nueva == {c_rep}
    assert c_rep in _ids(ruta)


def test_candidata_mas_antigua_desplaza_a_replica_ya_procesada(base):
    """Paso (2) del algoritmo: tras la primera corrida (marca puesta), entra una
    fila con fecha MÁS ANTIGUA que una ya procesada y similar a ella. La
    migración completa habría conservado la más antigua y borrado la procesada
    (con su análisis); la incremental hace lo mismo dentro de la ventana."""
    ruta = base
    _poblar_historial(ruta, dias=12, por_dia=3, semilla=11)
    procesada = _insertar(ruta, _fecha(5.0), "Micron raises guidance as HBM shipments accelerate")
    noticias.migrar_noticias_v2()
    conn = sqlite3.connect(ruta)
    conn.execute(
        "INSERT INTO analisis (titular_id, sentimiento, tickers_afectados, impacto_estimado,"
        " explicacion, analizado_en) VALUES (?, 0.5, 'MU', 'alto', 'x', ?)",
        (procesada, AHORA.isoformat()))
    conn.commit()
    conn.close()

    mas_antigua = _insertar(ruta, _fecha(6.0), "Micron raises guidance as HBM shipments accelerate")
    vieja, _ = _dedup_completa_4_6(ruta)
    assert procesada in vieja and mas_antigua not in vieja

    res = noticias.migrar_noticias_v2()
    assert res["candidatos"] == 1 and res["duplicados_borrados"] == 1
    assert procesada not in _ids(ruta) and mas_antigua in _ids(ruta)
    conn = sqlite3.connect(ruta)
    assert conn.execute("SELECT COUNT(*) FROM analisis WHERE titular_id = ?",
                        (procesada,)).fetchone()[0] == 0, "el análisis del duplicado se borra"
    conn.close()


def test_se_borra_el_analisis_de_la_replica_y_queda_el_del_original(base):
    ruta = base
    orig = _insertar(ruta, _fecha(2.0), "Intel to spin off foundry unit, sources say")
    rep = _insertar(ruta, _fecha(1.0), "Intel to spin off foundry unit, sources say - Bloomberg")
    conn = sqlite3.connect(ruta)
    for id_ in (orig, rep):
        conn.execute(
            "INSERT INTO analisis (titular_id, sentimiento, tickers_afectados, impacto_estimado,"
            " explicacion, analizado_en) VALUES (?, -0.2, 'INTC', 'medio', 'x', ?)",
            (id_, AHORA.isoformat()))
    conn.commit()
    conn.close()
    noticias.migrar_noticias_v2()
    conn = sqlite3.connect(ruta)
    vivos = {f[0] for f in conn.execute("SELECT titular_id FROM analisis")}
    conn.close()
    assert vivos == {orig}


# ------------------------------------------------------------
# 3. Idempotencia y esquema
# ------------------------------------------------------------
def test_idempotente_y_marca_en_meta(base):
    ruta = base
    ids = _poblar_historial(ruta, dias=15, por_dia=5, semilla=3)
    _insertar(ruta, _fecha(2.0), "AMD launches MI400 accelerators")
    _insertar(ruta, _fecha(1.0), "AMD launches MI400 accelerators")
    r1 = noticias.migrar_noticias_v2()
    assert r1["duplicados_borrados"] == 1 and r1["primera_corrida"] is True
    despues_1 = _ids(ruta)

    r2 = noticias.migrar_noticias_v2()
    assert r2 == {**r2, "duplicados_borrados": 0, "candidatos": 0, "comparaciones": 0,
                  "primera_corrida": False}
    assert _ids(ruta) == despues_1

    conn = sqlite3.connect(ruta)
    marca = conn.execute("SELECT valor FROM meta WHERE clave = ?",
                         (noticias._META_DEDUP_ULTIMO_ID,)).fetchone()[0]
    conn.close()
    assert int(marca) == max(ids) + 2  # el id máximo visto, borrado o no


def test_esquema_meta_es_aditivo_e_idempotente(tmp_path, monkeypatch):
    ruta = tmp_path / "vieja.db"
    monkeypatch.setattr(noticias, "DB_PATH", str(ruta))
    # Base "vieja": las tres tablas de la 4.6, sin `meta`.
    conn = sqlite3.connect(ruta)
    conn.execute("CREATE TABLE titulares (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL,"
                 " fuente TEXT NOT NULL, titular TEXT NOT NULL, url TEXT NOT NULL UNIQUE,"
                 " tickers TEXT NOT NULL DEFAULT '')")
    conn.execute("CREATE TABLE analisis (titular_id INTEGER PRIMARY KEY REFERENCES titulares(id),"
                 " sentimiento REAL NOT NULL, tickers_afectados TEXT NOT NULL DEFAULT '',"
                 " impacto_estimado TEXT NOT NULL, explicacion TEXT NOT NULL, analizado_en TEXT NOT NULL)")
    conn.execute("CREATE TABLE resumen_dia (fecha TEXT PRIMARY KEY, resumen TEXT NOT NULL,"
                 " generado_en TEXT NOT NULL)")
    conn.commit()
    columnas_antes = {t: [c[1] for c in conn.execute(f"PRAGMA table_info({t})")]
                      for t in ("titulares", "resumen_dia")}
    conn.close()

    noticias.init_db()
    noticias.init_db()
    noticias.migrar_noticias_v2()  # base vacía: no falla, deja la tabla meta
    conn = sqlite3.connect(ruta)
    tablas = {f[0] for f in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "meta" in tablas
    for t, cols in columnas_antes.items():
        assert [c[1] for c in conn.execute(f"PRAGMA table_info({t})")] == cols
    conn.close()


def test_actualizar_titulares_sigue_pasando_por_la_migracion():
    """El punto de entrada del job no cambió: la migración (ahora incremental)
    sigue corriendo antes de descargar RSS. Sin red: solo se lee el código."""
    fuente = inspect.getsource(noticias.actualizar_titulares)
    assert "migrar_noticias_v2()" in fuente
    assert noticias.VENTANA_DEDUP_RETRO_DIAS == 10
