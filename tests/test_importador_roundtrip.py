"""
Round trip del respaldo: CSV de data/backups/ -> base nueva -> comparación
fila por fila contra senales.db REAL (corrida 09, frente 2a).

Lo que este archivo demuestra, y que `tests/test_restaurar_backup.py` no
demostraba: que CADA fila de CADA tabla de senales.db (por clave natural,
no por hash agregado) reaparece en la restauración con CADA columna
idéntica — mismo valor, misma clase de almacenamiento (int/float/str/NULL)
y, para REAL, mismo `repr` (igualdad exacta de float, no tolerancia).
`plataforma_version` se verifica como cualquier otra columna y además en
un test propio, porque el criterio de aceptación del frente la nombra.

Reglas duras:
  - senales.db real se abre SOLO en `mode=ro`. Si no existe, la parte que
    compara contra ella se salta limpiamente (escenario "se perdió el disco").
  - La restauración va a un directorio temporal de pytest. Cualquier
    corrupción deliberada (la contraprueba) se hace sobre ESA copia, nunca
    sobre la base real.

Clase de discrepancia tolerada (declarada, no silenciosa): filas que la
base viva tiene y el CSV todavía no, POSTERIORES al instante del respaldo
(la base viva puede crecer entre el export de las 18:15 y la próxima
corrida; nunca al revés). Se reporta como warning con la lista de claves.
Cualquier otra discrepancia — fila del CSV ausente en la base, fila de la
base ausente del CSV pero anterior al respaldo, o cualquier columna que no
coincida — hace fallar el test con la lista de filas y la razón.
"""
from __future__ import annotations

import csv
import os
import sqlite3
import sys
import warnings
from dataclasses import dataclass, field

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

import restaurar_backup as rb  # noqa: E402

ORIGEN = os.path.join(RAIZ, "data", "backups")
SENALES_REAL = os.path.join(RAIZ, "senales.db")

# Clave natural por tabla (los `id` AUTOINCREMENT son surrogados y se
# comparan aparte, en su propio test, para que una discrepancia de id no se
# confunda con una discrepancia de contenido sellado).
CLAVES_NATURALES: dict[str, tuple[str, ...]] = {
    "snapshots": ("fecha",),
    "senales_ticker": ("fecha", "ticker"),
    "verificacion_apertura": ("fecha_senal", "ticker"),
    "verificacion_puntaje": ("fecha_senal", "ticker"),
    "divergencias": ("fecha", "par"),
}

# Columna que fecha cada fila para decidir si una fila SOLO en la base viva
# es "posterior al respaldo" (tolerada) o una pérdida real (falla).
COLUMNA_INSTANTE: dict[str, str] = {
    "snapshots": "creado_en",
    "senales_ticker": "timestamp_utc",   # NULL en filas legacy -> cae a `fecha`
    "verificacion_apertura": "verificado_en",
    "verificacion_puntaje": "verificado_en",
    "divergencias": "fecha",              # no tiene timestamp propio
}

SURROGADOS = {"id"}

requiere_base_real = pytest.mark.skipif(
    not os.path.isfile(SENALES_REAL),
    reason="senales.db no existe en este checkout — exactamente el escenario "
           "de 'se perdió el disco', no hay contra qué comparar",
)


# ------------------------------------------------------------ comparación

@dataclass
class ResultadoTabla:
    tabla: str
    n_real: int
    n_restaurada: int
    columnas_comparadas: int
    celdas_comparadas: int = 0
    # (clave, razón) — cualquiera de estas hace fallar
    discrepancias: list[tuple[tuple, str]] = field(default_factory=list)
    # (clave, razón) — filas solo en la base viva, posteriores al respaldo
    posteriores_al_respaldo: list[tuple[tuple, str]] = field(default_factory=list)
    # (clave, id_real, id_restaurado) — surrogados que no coinciden
    ids_distintos: list[tuple[tuple, object, object]] = field(default_factory=list)


def _abrir_ro(ruta: str) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)


def _leer_por_clave(conn: sqlite3.Connection, tabla: str, columnas: list[str],
                    clave: tuple[str, ...]) -> dict[tuple, dict]:
    cols = ", ".join(columnas)
    filas = conn.execute(f"SELECT {cols} FROM {tabla}").fetchall()
    idx = [columnas.index(c) for c in clave]
    out: dict[tuple, dict] = {}
    for fila in filas:
        k = tuple(fila[i] for i in idx)
        assert k not in out, f"{tabla}: clave natural repetida {k} en una misma base"
        out[k] = dict(zip(columnas, fila))
    return out


def _celda_identica(a, b) -> tuple[bool, str]:
    """Igualdad EXACTA de celda: misma clase de almacenamiento (el tipo
    Python que devuelve sqlite3 es la clase de almacenamiento: int, float,
    str, bytes o None) y mismo valor. Para float se exige además `repr`
    idéntico (distingue -0.0 de 0.0 y deja el criterio explícito: no hay
    tolerancia numérica en ninguna parte de esta comparación)."""
    if type(a) is not type(b):
        return False, f"clase de almacenamiento {type(a).__name__} vs {type(b).__name__}"
    if isinstance(a, float):
        if repr(a) != repr(b) or a != b:
            return False, f"float {a!r} vs {b!r}"
        return True, ""
    if a != b:
        return False, f"{a!r} vs {b!r}"
    return True, ""


def _instante_respaldo(conn_rest: sqlite3.Connection) -> tuple[str, str]:
    """El instante del respaldo se lee del propio respaldo: el mayor
    `creado_en` de snapshots (y su `fecha`). Nada de relojes ni memoria."""
    fila = conn_rest.execute(
        "SELECT MAX(creado_en), MAX(fecha) FROM snapshots"
    ).fetchone()
    return fila[0] or "", fila[1] or ""


def _es_posterior_al_respaldo(tabla: str, fila: dict, instante: str, fecha: str) -> bool:
    col = COLUMNA_INSTANTE[tabla]
    v = fila.get(col)
    if v is None:
        v = fila.get("fecha") or fila.get("fecha_senal")
        return bool(v) and v > fecha
    if col == "fecha":
        return v > fecha
    return v > instante


def comparar_tabla(conn_real: sqlite3.Connection, conn_rest: sqlite3.Connection,
                   tabla: str) -> ResultadoTabla:
    _csv, _ddl, columnas_tipadas, _pk = rb.ESQUEMA_SENALES[tabla]
    columnas = [c for c, _t in columnas_tipadas]
    clave = CLAVES_NATURALES[tabla]
    contenido = [c for c in columnas if c not in SURROGADOS]

    real = _leer_por_clave(conn_real, tabla, columnas, clave)
    rest = _leer_por_clave(conn_rest, tabla, columnas, clave)
    instante, fecha = _instante_respaldo(conn_rest)

    r = ResultadoTabla(tabla, len(real), len(rest), len(contenido))

    for k in sorted(rest.keys() - real.keys(), key=str):
        r.discrepancias.append((k, "fila en la restauración que la base real no tiene"))

    for k in sorted(real.keys() - rest.keys(), key=str):
        if _es_posterior_al_respaldo(tabla, real[k], instante, fecha):
            r.posteriores_al_respaldo.append(
                (k, f"fila de la base viva posterior al respaldo ({instante})"))
        else:
            r.discrepancias.append((k, "fila sellada ausente del CSV (no restaurable)"))

    for k in sorted(real.keys() & rest.keys(), key=str):
        fr, fs = real[k], rest[k]
        for c in contenido:
            r.celdas_comparadas += 1
            ok, razon = _celda_identica(fr[c], fs[c])
            if not ok:
                r.discrepancias.append((k, f"columna {c}: {razon}"))
        for c in SURROGADOS & set(columnas):
            if fr[c] != fs[c]:
                r.ids_distintos.append((k, fr[c], fs[c]))
    return r


def _formatear(items: list, limite: int = 25) -> str:
    lineas = [f"  {k}: {razon}" for k, razon in items[:limite]]
    if len(items) > limite:
        lineas.append(f"  ... y {len(items) - limite} más")
    return "\n".join(lineas)


# ---------------------------------------------------------------- fixtures

@pytest.fixture(scope="module")
def restauracion(tmp_path_factory):
    destino = tmp_path_factory.mktemp("roundtrip")
    ruta_senales, _ruta_noticias, reportes = rb.restaurar(ORIGEN, str(destino))
    hallazgos = [h for rep in reportes for h in rep.hallazgos]
    assert hallazgos == [], f"el importador reportó hallazgos al restaurar: {hallazgos}"
    return ruta_senales


@pytest.fixture(scope="module")
def resultados(restauracion):
    if not os.path.isfile(SENALES_REAL):
        pytest.skip("senales.db no existe en este checkout")
    conn_real = _abrir_ro(SENALES_REAL)
    conn_rest = _abrir_ro(restauracion)
    try:
        return {t: comparar_tabla(conn_real, conn_rest, t) for t in CLAVES_NATURALES}
    finally:
        conn_real.close()
        conn_rest.close()


# ------------------------------------------------------------------- tests

@requiere_base_real
@pytest.mark.parametrize("tabla", list(CLAVES_NATURALES))
def test_cada_fila_sellada_vuelve_identica(resultados, tabla):
    """Fila por fila, columna por columna, sin tolerancia. Falla listando
    las filas y la razón; las filas posteriores al respaldo se toleran y
    se declaran como warning."""
    r = resultados[tabla]
    if r.posteriores_al_respaldo:
        warnings.warn(
            f"{tabla}: {len(r.posteriores_al_respaldo)} fila(s) de la base viva "
            f"posteriores al respaldo, no comparables todavía:\n"
            f"{_formatear(r.posteriores_al_respaldo)}",
            stacklevel=1,
        )
    assert r.discrepancias == [], (
        f"{tabla}: {len(r.discrepancias)} discrepancia(s) entre la base real "
        f"(n={r.n_real}) y la restauración (n={r.n_restaurada}), "
        f"{r.celdas_comparadas} celdas comparadas:\n{_formatear(r.discrepancias)}"
    )
    assert r.celdas_comparadas == min(r.n_real, r.n_restaurada) * r.columnas_comparadas


@requiere_base_real
def test_ningun_sello_queda_sin_comparar(resultados):
    """Que el test anterior no pase por comparar cero filas: todas las
    tablas tienen filas y ninguna quedó fuera de la comparación."""
    for tabla, r in resultados.items():
        assert r.n_real > 0 and r.n_restaurada > 0, f"{tabla}: sin filas"
        # Contabilidad cerrada: cada fila de la base real está o comparada
        # (idéntica, si el test anterior pasó) o declarada posterior al
        # respaldo. No hay una tercera categoría silenciosa.
        assert r.n_real == r.n_restaurada + len(r.posteriores_al_respaldo), (
            f"{tabla}: n_real={r.n_real} n_restaurada={r.n_restaurada} "
            f"posteriores={len(r.posteriores_al_respaldo)} — no cierra"
        )


@requiere_base_real
def test_toda_tabla_con_filas_selladas_esta_en_el_respaldo(restauracion):
    """Lo ÚNICO de senales.db que el CSV no lleva es `sqlite_sequence`
    (el contador interno de AUTOINCREMENT: no es una fila sellada). Si
    algún día senales.py crea una tabla nueva y snapshot.TABLAS_BACKUP_SENALES
    no la exporta, este test es el que lo dice."""
    conn_real = _abrir_ro(SENALES_REAL)
    conn_rest = _abrir_ro(restauracion)
    try:
        tablas_real = {f[0] for f in conn_real.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        tablas_rest = {f[0] for f in conn_rest.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn_real.close()
        conn_rest.close()
    assert tablas_real - tablas_rest == {"sqlite_sequence"}, (
        f"tablas de la base real sin camino de vuelta: {tablas_real - tablas_rest}")
    assert tablas_rest - tablas_real == set()


@requiere_base_real
def test_esquema_de_columnas_identico_salvo_autoincrement_declarado(restauracion):
    """Las filas no bastan si vuelven a otro esquema: `PRAGMA table_info`
    (nombre, tipo, NOT NULL, DEFAULT, PK) tiene que ser idéntico tabla por
    tabla. La única diferencia de DDL declarada y tolerada: la base real
    dice `INTEGER PRIMARY KEY AUTOINCREMENT` y la restaurada `INTEGER
    PRIMARY KEY` (sin AUTOINCREMENT no hay `sqlite_sequence`; el próximo
    id sigue siendo max+1 — medido en test_id_siguiente_tras_restaurar_no_colisiona)."""
    conn_real = _abrir_ro(SENALES_REAL)
    conn_rest = _abrir_ro(restauracion)
    try:
        for tabla in CLAVES_NATURALES:
            info_real = conn_real.execute(f"PRAGMA table_info({tabla})").fetchall()
            info_rest = conn_rest.execute(f"PRAGMA table_info({tabla})").fetchall()
            assert info_real == info_rest, f"{tabla}: table_info difiere\n{info_real}\n{info_rest}"
            ddl_real = conn_real.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabla,)).fetchone()[0]
            ddl_rest = conn_rest.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabla,)).fetchone()[0]
            # Sin blancos: la base real creció por ALTER TABLE ADD COLUMN
            # (migraciones aditivas de senales.py), que deja las columnas
            # nuevas pegadas al cierre del paréntesis en el DDL guardado.
            norm = lambda s: "".join(s.replace(" AUTOINCREMENT", "").split())  # noqa: E731
            assert norm(ddl_real) == norm(ddl_rest), (
                f"{tabla}: el DDL difiere en algo más que AUTOINCREMENT\n{ddl_real}\n{ddl_rest}")
    finally:
        conn_real.close()
        conn_rest.close()


@requiere_base_real
def test_plataforma_version_de_cada_snapshot_vuelve_identica(restauracion):
    """El criterio de aceptación la nombra, así que tiene su propio test:
    para cada `fecha` sellada, `plataforma_version` (incluido NULL, que es
    el valor sellado de los snapshots anteriores a 5.0.0) es idéntica."""
    conn_real = _abrir_ro(SENALES_REAL)
    conn_rest = _abrir_ro(restauracion)
    try:
        real = dict(conn_real.execute("SELECT fecha, plataforma_version FROM snapshots"))
        rest = dict(conn_rest.execute("SELECT fecha, plataforma_version FROM snapshots"))
    finally:
        conn_real.close()
        conn_rest.close()
    distintas = [(f, real[f], rest.get(f, "<ausente>")) for f in sorted(real)
                 if f not in rest or real[f] != rest[f]
                 or type(real[f]) is not type(rest[f])]
    assert distintas == [], f"plataforma_version difiere en {len(distintas)} snapshot(s): {distintas}"
    assert len(real) == len(rest)


@requiere_base_real
def test_ids_surrogados_tambien_coinciden(resultados):
    """Los `id` AUTOINCREMENT no son contenido sellado, pero el CSV los
    trae y el importador los inserta explícitos: se declara aparte si
    coinciden. Hoy coinciden; si dejaran de hacerlo, es un hallazgo sobre
    el surrogado, no sobre la fila sellada."""
    con_id = [t for t in CLAVES_NATURALES if "id" in
              [c for c, _t in rb.ESQUEMA_SENALES[t][2]]]
    assert con_id, "ninguna tabla con id — el esquema cambió"
    for tabla in con_id:
        r = resultados[tabla]
        assert r.ids_distintos == [], (
            f"{tabla}: {len(r.ids_distintos)} id(s) surrogado(s) distintos "
            f"(clave, id_real, id_restaurado): {r.ids_distintos[:25]}"
        )


def test_los_reales_del_csv_son_el_repr_exacto_del_float():
    """La razón por la que la comparación puede ser exacta y no tolerante:
    pandas escribe cada REAL con `repr`, que es round-trip exacto en
    Python. Se verifica sobre TODAS las celdas REAL de los CSV de senales,
    no sobre una muestra."""
    total, distintos = 0, []
    for tabla, (csv_nombre, _ddl, columnas, _pk) in rb.ESQUEMA_SENALES.items():
        with open(os.path.join(ORIGEN, csv_nombre), encoding="utf-8", newline="") as f:
            for i, fila in enumerate(csv.DictReader(f)):
                for col, tipo in columnas:
                    v = fila[col]
                    if tipo == "REAL" and v != "":
                        total += 1
                        if repr(float(v)) != v:
                            distintos.append((tabla, i, col, v))
    assert total > 0
    assert distintos == [], f"{len(distintos)}/{total} celdas REAL no son repr exacto: {distintos[:10]}"


def test_id_siguiente_tras_restaurar_no_colisiona(tmp_path):
    """docs/RESTAURAR.md decía que esto 'no se verificó explícitamente':
    la base restaurada no trae `sqlite_sequence`, así que se mide que el
    próximo id que asignaría SQLite es max(id)+1 en las cuatro tablas con
    id. Se inserta en la COPIA temporal y se hace rollback."""
    ruta_senales, _n, _r = rb.restaurar(ORIGEN, str(tmp_path / "r"))
    conn = sqlite3.connect(ruta_senales)
    try:
        casos = {
            "senales_ticker": ("(fecha, ticker)", "('9999-01-01', 'ZZZ')"),
            "verificacion_apertura": (
                "(fecha_senal, ticker, apertura_estimada_pct, retorno_real_pct, "
                "acierto_direccion, error_pp, verificado_en)",
                "('9999-01-01', 'ZZZ', 0, 0, 0, 0, 'x')"),
            "verificacion_puntaje": (
                "(fecha_senal, ticker, puntaje_ia, retorno_5d_pct, verificado_en)",
                "('9999-01-01', 'ZZZ', 0, 0, 'x')"),
            "divergencias": ("(fecha, par, spread_20d_pct, z_score)",
                             "('9999-01-01', 'ZZZ', 0, 0)"),
        }
        for tabla, (cols, vals) in casos.items():
            maximo = conn.execute(f"SELECT MAX(id) FROM {tabla}").fetchone()[0]
            cur = conn.execute(f"INSERT INTO {tabla} {cols} VALUES {vals}")
            assert cur.lastrowid == maximo + 1, (
                f"{tabla}: id nuevo {cur.lastrowid} != max+1 ({maximo + 1})")
    finally:
        conn.rollback()
        conn.close()


# ------------------------------------------------------------ contraprueba

def _corromper(ruta_db: str, sql: str, params: tuple = ()) -> None:
    conn = sqlite3.connect(ruta_db)  # copia temporal de pytest, nunca la real
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


@requiere_base_real
def test_contraprueba_detecta_un_valor_corrompido_en_la_copia(tmp_path):
    """La comparación tiene que poder fallar. Se restaura a tmp, se
    corrompe en la COPIA (a) un REAL en el último decimal, (b) una
    `plataforma_version`, (c) se borra una fila, (d) se cambia un id, y se
    verifica que cada una aparece con su clave y su razón."""
    ruta_senales, _n, _r = rb.restaurar(ORIGEN, str(tmp_path / "r"))
    conn = _abrir_ro(ruta_senales)
    try:
        fecha_a, roca = conn.execute(
            "SELECT fecha, roca_chip FROM snapshots WHERE roca_chip IS NOT NULL "
            "ORDER BY fecha LIMIT 1").fetchone()
        fecha_b = conn.execute(
            "SELECT fecha FROM snapshots WHERE plataforma_version IS NOT NULL "
            "ORDER BY fecha DESC LIMIT 1").fetchone()[0]
        fs, tk = conn.execute(
            "SELECT fecha_senal, ticker FROM verificacion_apertura ORDER BY id LIMIT 1").fetchone()
        id_div, fecha_d, par_d = conn.execute(
            "SELECT id, fecha, par FROM divergencias ORDER BY id DESC LIMIT 1").fetchone()
    finally:
        conn.close()

    # (a) un ulp de diferencia: si la comparación fuera tolerante, no lo vería
    roca_corrupto = roca + 1e-12 if roca + 1e-12 != roca else roca * (1 + 1e-15)
    assert roca_corrupto != roca
    _corromper(ruta_senales, "UPDATE snapshots SET roca_chip = ? WHERE fecha = ?", (roca_corrupto, fecha_a))
    # (b) plataforma_version cambiada a otra etiqueta
    _corromper(ruta_senales, "UPDATE snapshots SET plataforma_version = '9.9.9' WHERE fecha = ?", (fecha_b,))
    # (c) una fila sellada desaparece de la restauración
    _corromper(ruta_senales, "DELETE FROM verificacion_apertura WHERE fecha_senal = ? AND ticker = ?", (fs, tk))
    # (d) un id surrogado distinto (contenido intacto)
    _corromper(ruta_senales, "UPDATE divergencias SET id = ? WHERE id = ?", (id_div + 100000, id_div))

    conn_real = _abrir_ro(SENALES_REAL)
    conn_rest = _abrir_ro(ruta_senales)
    try:
        r_snap = comparar_tabla(conn_real, conn_rest, "snapshots")
        r_va = comparar_tabla(conn_real, conn_rest, "verificacion_apertura")
        r_div = comparar_tabla(conn_real, conn_rest, "divergencias")
    finally:
        conn_real.close()
        conn_rest.close()

    razones_snap = {(k, razon.split(":")[0]) for k, razon in r_snap.discrepancias}
    assert ((fecha_a,), "columna roca_chip") in razones_snap, r_snap.discrepancias
    assert ((fecha_b,), "columna plataforma_version") in razones_snap, r_snap.discrepancias
    assert len(r_snap.discrepancias) == 2, r_snap.discrepancias

    assert [(k, razon) for k, razon in r_va.discrepancias] == [
        ((fs, tk), "fila sellada ausente del CSV (no restaurable)")], r_va.discrepancias

    assert r_div.discrepancias == [], "cambiar un id no debe contarse como discrepancia de contenido"
    assert r_div.ids_distintos == [((fecha_d, par_d), id_div, id_div + 100000)]


@requiere_base_real
def test_contraprueba_detecta_cambio_de_clase_de_almacenamiento(tmp_path):
    """Un 120 guardado como 120.0 (mismo valor, otra clase) también se
    detecta: la comparación es de clase + valor, no solo de valor."""
    ruta_senales, _n, _r = rb.restaurar(ORIGEN, str(tmp_path / "r"))
    conn = _abrir_ro(ruta_senales)
    try:
        fecha, vb = conn.execute(
            "SELECT fecha, ventana_betas FROM snapshots WHERE ventana_betas IS NOT NULL "
            "ORDER BY fecha LIMIT 1").fetchone()
    finally:
        conn.close()
    assert isinstance(vb, int)
    # sqlite guarda 120.0 como REAL en una columna INTEGER solo si no es
    # convertible sin pérdida; forzamos vía texto para que quede como TEXT.
    _corromper(ruta_senales, "UPDATE snapshots SET ventana_betas = CAST(? AS TEXT) || 'x' WHERE fecha = ?", (vb, fecha))
    conn_real = _abrir_ro(SENALES_REAL)
    conn_rest = _abrir_ro(ruta_senales)
    try:
        r = comparar_tabla(conn_real, conn_rest, "snapshots")
    finally:
        conn_real.close()
        conn_rest.close()
    assert len(r.discrepancias) == 1
    assert r.discrepancias[0][0] == (fecha,)
    assert "clase de almacenamiento int vs str" in r.discrepancias[0][1], r.discrepancias


@requiere_base_real
def test_contraprueba_detecta_una_fila_de_mas_en_la_copia(tmp_path):
    """La dirección inversa también falla: una fila que la restauración
    tiene y la base real no (un CSV con una fila inventada o de otra
    máquina) se lista con su clave y su razón."""
    ruta_senales, _n, _r = rb.restaurar(ORIGEN, str(tmp_path / "r"))
    _corromper(ruta_senales,
               "INSERT INTO verificacion_puntaje (fecha_senal, ticker, puntaje_ia, "
               "retorno_5d_pct, verificado_en) VALUES ('1999-01-01', 'ZZZ', 0.0, 0.0, 'x')")
    conn_real = _abrir_ro(SENALES_REAL)
    conn_rest = _abrir_ro(ruta_senales)
    try:
        r = comparar_tabla(conn_real, conn_rest, "verificacion_puntaje")
    finally:
        conn_real.close()
        conn_rest.close()
    assert r.discrepancias == [
        (("1999-01-01", "ZZZ"), "fila en la restauración que la base real no tiene")]
    assert r.n_restaurada == r.n_real + 1


@requiere_base_real
def test_limite_declarado_un_csv_que_perdio_el_ultimo_dia_solo_avisa(tmp_path):
    """LÍMITE DECLARADO, no virtud: si el CSV perdiera el ÚLTIMO día
    sellado entero, la comparación no puede distinguirlo de "la base viva
    creció después del respaldo" (el instante del respaldo se lee del propio
    CSV — sin reloj ni memoria externos no hay otra referencia). Ese caso
    queda como WARNING con la lista de claves, no como fallo. Se mide acá
    para que el límite sea visible y no se descubra el día que importe.
    Cualquier día que NO sea el último sí falla (ver test_contraprueba_
    detecta_un_valor_corrompido_en_la_copia, caso c). Todo esto ocurre
    sobre la COPIA temporal de pytest; la base real solo se lee en ro."""
    ruta_senales, _n, _r = rb.restaurar(ORIGEN, str(tmp_path / "r"))
    conn = _abrir_ro(ruta_senales)
    try:
        ultima = conn.execute("SELECT MAX(fecha) FROM snapshots").fetchone()[0]
        n_st = conn.execute("SELECT COUNT(*) FROM senales_ticker WHERE fecha = ?", (ultima,)).fetchone()[0]
    finally:
        conn.close()
    assert n_st > 0
    quitar = "DELETE FROM {} WHERE fecha = ?"  # sobre la copia temporal
    _corromper(ruta_senales, quitar.format("snapshots"), (ultima,))
    _corromper(ruta_senales, quitar.format("senales_ticker"), (ultima,))
    conn_real = _abrir_ro(SENALES_REAL)
    conn_rest = _abrir_ro(ruta_senales)
    try:
        r_snap = comparar_tabla(conn_real, conn_rest, "snapshots")
        r_st = comparar_tabla(conn_real, conn_rest, "senales_ticker")
    finally:
        conn_real.close()
        conn_rest.close()
    assert r_snap.discrepancias == [] and r_st.discrepancias == []
    assert [k for k, _ in r_snap.posteriores_al_respaldo] == [(ultima,)]
    assert len(r_st.posteriores_al_respaldo) == n_st
    assert all(k[0] == ultima for k, _ in r_st.posteriores_al_respaldo)
