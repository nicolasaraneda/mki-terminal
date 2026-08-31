#!/usr/bin/env python3
"""
restaurar_backup.py — el camino de vuelta desde data/backups/*.csv.

Reglas duras, sin excepción:
  - NUNCA abre senales.db ni noticias.db en modo escritura. La reconstrucción
    siempre va a una base NUEVA, en una ruta temporal (por defecto un
    directorio bajo tempfile, nunca dentro del repo).
  - El esquema de las tablas está DUPLICADO acá a propósito, no importado de
    senales.py/noticias.py: este script tiene que poder correr aunque esos
    módulos no importen limpio (una restauración de emergencia no debería
    depender de que el resto del proyecto esté sano), y tiene que poder leer
    senales.db en modo `ro` sin abrir jamás una conexión de escritura a la
    base real — importar senales.py conectaría, vía su DB_PATH de módulo, a
    la base real.
  - Este script SOLO reconstruye. No corrige, no reordena, no imputa filas
    faltantes. Si algo no vuelve idéntico, el hallazgo es qué se pierde en
    el viaje de ida y vuelta — no se disimula redondeando a favor.

Uso:
    python scripts/restaurar_backup.py                    # restaura a un
                                                            # directorio temporal, imprime reporte
    python scripts/restaurar_backup.py --destino DIR       # restaura ahí
    python scripts/restaurar_backup.py --verificar         # además compara
                                                            # contra senales.db/noticias.db reales (solo lectura)
    python scripts/restaurar_backup.py --origen DIR        # CSVs de origen
                                                            # (por defecto data/backups/)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sqlite3
import sys
import tempfile
from dataclasses import dataclass, field

RAIZ_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN_POR_DEFECTO = os.path.join(RAIZ_REPO, "data", "backups")

# Tipo declarado por columna: "TEXT", "INTEGER", "REAL". El orden de la
# lista es el orden real de columnas en el CSV (SELECT * de la tabla).
# Duplicado a propósito desde el esquema vigente de senales.db/noticias.db
# (verificado en modo lectura el 31-ago-2026) — NO se importa desde
# senales.py/noticias.py, ver docstring del módulo.

TablaSpec = tuple[str, str, list[tuple[str, str]], list[str]]
# (csv, ddl_columnas, columnas_tipadas, claves_de_orden)

ESQUEMA_SENALES: dict[str, TablaSpec] = {
    "snapshots": (
        "senales_snapshots.csv",
        """
        CREATE TABLE snapshots (
            fecha TEXT PRIMARY KEY,
            creado_en TEXT NOT NULL,
            regimen TEXT,
            roca_chip REAL,
            timestamp_utc TEXT,
            origen TEXT,
            modelo_version TEXT,
            feature_version TEXT,
            universo_version TEXT,
            ventana_betas INTEGER,
            descarga_ok INTEGER,
            descarga_total INTEGER,
            descarga_caidos TEXT,
            plataforma_version TEXT,
            sox_usado_pct REAL,
            sox_fecha TEXT
        )
        """,
        [
            ("fecha", "TEXT"), ("creado_en", "TEXT"), ("regimen", "TEXT"),
            ("roca_chip", "REAL"), ("timestamp_utc", "TEXT"), ("origen", "TEXT"),
            ("modelo_version", "TEXT"), ("feature_version", "TEXT"),
            ("universo_version", "TEXT"), ("ventana_betas", "INTEGER"),
            ("descarga_ok", "INTEGER"), ("descarga_total", "INTEGER"),
            ("descarga_caidos", "TEXT"), ("plataforma_version", "TEXT"),
            ("sox_usado_pct", "REAL"), ("sox_fecha", "TEXT"),
        ],
        ["fecha"],
    ),
    "senales_ticker": (
        "senales_senales_ticker.csv",
        """
        CREATE TABLE senales_ticker (
            id INTEGER PRIMARY KEY,
            fecha TEXT NOT NULL,
            ticker TEXT NOT NULL,
            puntaje_v0 REAL,
            sentimiento_ia REAL,
            puntaje_ia REAL,
            apertura_estimada_pct REAL,
            confianza_r2 REAL,
            timestamp_utc TEXT,
            exchange TEXT,
            sesion_objetivo TEXT,
            available_at TEXT,
            estado TEXT,
            intervalo80_pp REAL,
            n_muestra INTEGER,
            modelo_version TEXT,
            beta REAL,
            UNIQUE(fecha, ticker)
        )
        """,
        [
            ("id", "INTEGER"), ("fecha", "TEXT"), ("ticker", "TEXT"),
            ("puntaje_v0", "REAL"), ("sentimiento_ia", "REAL"), ("puntaje_ia", "REAL"),
            ("apertura_estimada_pct", "REAL"), ("confianza_r2", "REAL"),
            ("timestamp_utc", "TEXT"), ("exchange", "TEXT"), ("sesion_objetivo", "TEXT"),
            ("available_at", "TEXT"), ("estado", "TEXT"), ("intervalo80_pp", "REAL"),
            ("n_muestra", "INTEGER"), ("modelo_version", "TEXT"), ("beta", "REAL"),
        ],
        ["id"],
    ),
    "verificacion_apertura": (
        "senales_verificacion_apertura.csv",
        """
        CREATE TABLE verificacion_apertura (
            id INTEGER PRIMARY KEY,
            fecha_senal TEXT NOT NULL,
            ticker TEXT NOT NULL,
            apertura_estimada_pct REAL NOT NULL,
            retorno_real_pct REAL NOT NULL,
            acierto_direccion INTEGER NOT NULL,
            error_pp REAL NOT NULL,
            verificado_en TEXT NOT NULL,
            gap_pct REAL,
            acierto_gap INTEGER,
            error_gap_pp REAL,
            modelo_version TEXT,
            legacy INTEGER,
            UNIQUE(fecha_senal, ticker)
        )
        """,
        [
            ("id", "INTEGER"), ("fecha_senal", "TEXT"), ("ticker", "TEXT"),
            ("apertura_estimada_pct", "REAL"), ("retorno_real_pct", "REAL"),
            ("acierto_direccion", "INTEGER"), ("error_pp", "REAL"),
            ("verificado_en", "TEXT"), ("gap_pct", "REAL"), ("acierto_gap", "INTEGER"),
            ("error_gap_pp", "REAL"), ("modelo_version", "TEXT"), ("legacy", "INTEGER"),
        ],
        ["id"],
    ),
    "verificacion_puntaje": (
        "senales_verificacion_puntaje.csv",
        """
        CREATE TABLE verificacion_puntaje (
            id INTEGER PRIMARY KEY,
            fecha_senal TEXT NOT NULL,
            ticker TEXT NOT NULL,
            puntaje_ia REAL NOT NULL,
            retorno_5d_pct REAL NOT NULL,
            verificado_en TEXT NOT NULL,
            UNIQUE(fecha_senal, ticker)
        )
        """,
        [
            ("id", "INTEGER"), ("fecha_senal", "TEXT"), ("ticker", "TEXT"),
            ("puntaje_ia", "REAL"), ("retorno_5d_pct", "REAL"), ("verificado_en", "TEXT"),
        ],
        ["id"],
    ),
    "divergencias": (
        "senales_divergencias.csv",
        """
        CREATE TABLE divergencias (
            id INTEGER PRIMARY KEY,
            fecha TEXT NOT NULL,
            par TEXT NOT NULL,
            spread_20d_pct REAL NOT NULL,
            z_score REAL NOT NULL,
            explicacion TEXT NOT NULL DEFAULT '',
            spread_simple_pct REAL,
            z_simple REAL,
            UNIQUE(fecha, par)
        )
        """,
        [
            ("id", "INTEGER"), ("fecha", "TEXT"), ("par", "TEXT"),
            ("spread_20d_pct", "REAL"), ("z_score", "REAL"), ("explicacion", "TEXT"),
            ("spread_simple_pct", "REAL"), ("z_simple", "REAL"),
        ],
        ["id"],
    ),
}

ESQUEMA_NOTICIAS: dict[str, TablaSpec] = {
    "titulares": (
        "noticias_titulares.csv",
        """
        CREATE TABLE titulares (
            id INTEGER PRIMARY KEY,
            fecha TEXT NOT NULL,
            fuente TEXT NOT NULL,
            titular TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            tickers TEXT NOT NULL DEFAULT ''
        )
        """,
        [
            ("id", "INTEGER"), ("fecha", "TEXT"), ("fuente", "TEXT"),
            ("titular", "TEXT"), ("url", "TEXT"), ("tickers", "TEXT"),
        ],
        ["id"],
    ),
    "analisis": (
        "noticias_analisis.csv",
        """
        CREATE TABLE analisis (
            titular_id INTEGER PRIMARY KEY,
            sentimiento REAL NOT NULL,
            tickers_afectados TEXT NOT NULL DEFAULT '',
            impacto_estimado TEXT NOT NULL,
            explicacion TEXT NOT NULL,
            analizado_en TEXT NOT NULL,
            relevancia REAL
        )
        """,
        [
            ("titular_id", "INTEGER"), ("sentimiento", "REAL"),
            ("tickers_afectados", "TEXT"), ("impacto_estimado", "TEXT"),
            ("explicacion", "TEXT"), ("analizado_en", "TEXT"), ("relevancia", "REAL"),
        ],
        ["titular_id"],
    ),
    "resumen_dia": (
        "noticias_resumen_dia.csv",
        """
        CREATE TABLE resumen_dia (
            fecha TEXT PRIMARY KEY,
            resumen TEXT NOT NULL,
            generado_en TEXT NOT NULL
        )
        """,
        [
            ("fecha", "TEXT"), ("resumen", "TEXT"), ("generado_en", "TEXT"),
        ],
        ["fecha"],
    ),
}


# Columnas TEXT NOT NULL DEFAULT '' — acá, y solo acá, un campo vacío del
# CSV significa la cadena vacía real, NUNCA NULL. Es la única forma de
# resolver la ambigüedad que el propio CSV introduce (ver docstring de
# `_coaccionar`): en el resto de las columnas TEXT nullable, un campo vacío
# se interpreta como NULL porque es la lectura correcta para "todavía no
# calculado", que es lo que casi siempre significa un blank en este esquema.
TEXTO_DEFECTO_VACIO = {
    ("divergencias", "explicacion"),
    ("titulares", "tickers"),
    ("analisis", "tickers_afectados"),
}


@dataclass
class ReporteTabla:
    tabla: str
    filas_csv: int
    filas_importadas: int
    hallazgos: list[str] = field(default_factory=list)


def _coaccionar(valor: str | None, tipo: str, hallazgos: list[str], contexto: str,
                 defecto_vacio: bool = False):
    """Convierte el string crudo del CSV al tipo Python que corresponde a la
    columna. Documenta (no oculta) cualquier artefacto del viaje ida/vuelta.

    El hallazgo conocido: pandas, al exportar `SELECT *` a CSV, sube de
    INTEGER a float64 cualquier columna entera que tenga al menos una fila
    NULL (ej. "120.0" en vez de "120" para `n_muestra`, `ventana_betas`,
    `descarga_ok`). Es un artefacto YA PRESENTE en el CSV versionado, no algo
    que este importador introduce. Se recupera sin pérdida cuando el valor es
    un entero exacto (120.0 -> 120); si alguna vez apareciera una fracción
    real en una columna declarada INTEGER, eso NO se trunca en silencio: se
    registra como hallazgo y se guarda igual (fiel al CSV, no a lo que
    "debería" ser).
    """
    if valor is None or valor == "":
        return "" if defecto_vacio else None
    if tipo == "TEXT":
        return valor
    if tipo == "REAL":
        return float(valor)
    if tipo == "INTEGER":
        f = float(valor)
        if f != int(f):
            hallazgos.append(
                f"{contexto}: valor '{valor}' en columna INTEGER con parte "
                "fraccionaria real (no es el artefacto conocido de pandas) "
                "— se conserva como float, no se trunca."
            )
            return f
        entero = int(f)
        if valor != str(entero):
            # Es el artefacto conocido (ej. "120.0"); no se cuenta como
            # hallazgo de pérdida real porque el valor se recupera exacto.
            pass
        return entero
    raise ValueError(f"tipo de columna desconocido: {tipo}")


def _crear_esquema(conn: sqlite3.Connection, esquema: dict[str, TablaSpec]) -> None:
    for _tabla, (_csv, ddl, _cols, _pk) in esquema.items():
        conn.execute(ddl)
    conn.commit()


def _importar_tabla(
    conn: sqlite3.Connection, tabla: str, spec: TablaSpec, dir_origen: str
) -> ReporteTabla:
    csv_nombre, _ddl, columnas, _pk = spec
    ruta_csv = os.path.join(dir_origen, csv_nombre)
    hallazgos: list[str] = []
    filas_csv = 0
    filas_a_insertar = []

    if not os.path.isfile(ruta_csv):
        return ReporteTabla(tabla, 0, 0, [f"CSV no encontrado: {ruta_csv}"])

    with open(ruta_csv, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        encabezado_csv = lector.fieldnames or []
        esperado = [c for c, _t in columnas]
        if encabezado_csv != esperado:
            hallazgos.append(
                f"encabezado del CSV difiere del esquema esperado: "
                f"csv={encabezado_csv} esquema={esperado}"
            )
        for i, fila in enumerate(lector):
            filas_csv += 1
            valores = []
            for col, tipo in columnas:
                crudo = fila.get(col, "")
                defecto_vacio = (tabla, col) in TEXTO_DEFECTO_VACIO
                valores.append(
                    _coaccionar(crudo, tipo, hallazgos, f"{tabla}[fila {i}].{col}",
                                defecto_vacio=defecto_vacio)
                )
            filas_a_insertar.append(tuple(valores))

    nombres_cols = ", ".join(c for c, _t in columnas)
    marcadores = ", ".join("?" for _ in columnas)
    conn.executemany(
        f"INSERT INTO {tabla} ({nombres_cols}) VALUES ({marcadores})",
        filas_a_insertar,
    )
    conn.commit()

    filas_importadas = conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    if filas_importadas != filas_csv:
        hallazgos.append(
            f"conteo no coincide: {filas_csv} filas en el CSV, "
            f"{filas_importadas} filas terminaron insertadas "
            "(revisar UNIQUE/PRIMARY KEY duplicados en el propio CSV)"
        )
    return ReporteTabla(tabla, filas_csv, filas_importadas, hallazgos)


def restaurar(
    dir_origen: str, dir_destino: str
) -> tuple[str, str, list[ReporteTabla]]:
    """Reconstruye senales.db y noticias.db NUEVOS en dir_destino a partir de
    los CSV de dir_origen. Nunca toca ninguna base existente."""
    os.makedirs(dir_destino, exist_ok=True)
    ruta_senales = os.path.join(dir_destino, "senales_restaurado.db")
    ruta_noticias = os.path.join(dir_destino, "noticias_restaurado.db")

    if os.path.exists(ruta_senales) or os.path.exists(ruta_noticias):
        raise FileExistsError(
            "el destino ya tiene una base restaurada; usa un directorio "
            "vacío para no confundir corridas distintas"
        )

    reportes: list[ReporteTabla] = []

    conn_s = sqlite3.connect(ruta_senales)
    try:
        _crear_esquema(conn_s, ESQUEMA_SENALES)
        for tabla, spec in ESQUEMA_SENALES.items():
            reportes.append(_importar_tabla(conn_s, tabla, spec, dir_origen))
    finally:
        conn_s.close()

    conn_n = sqlite3.connect(ruta_noticias)
    try:
        _crear_esquema(conn_n, ESQUEMA_NOTICIAS)
        for tabla, spec in ESQUEMA_NOTICIAS.items():
            reportes.append(_importar_tabla(conn_n, tabla, spec, dir_origen))
    finally:
        conn_n.close()

    return ruta_senales, ruta_noticias, reportes


def hash_tabla(conn: sqlite3.Connection, tabla: str, columnas: list[str], pk: list[str]) -> str:
    """Hash determinístico del CONTENIDO de una tabla: ordena por clave
    primaria y serializa cada fila de forma estable. No es un hash del
    archivo .db (el formato de página de SQLite no es determinístico entre
    bases construidas de formas distintas — freelist, orden físico de
    inserción — así que hashear el archivo compararía la implementación de
    SQLite, no los datos)."""
    orden = ", ".join(pk)
    cols = ", ".join(columnas)
    filas = conn.execute(f"SELECT {cols} FROM {tabla} ORDER BY {orden}").fetchall()
    h = hashlib.sha256()
    for fila in filas:
        partes = []
        for v in fila:
            if v is None:
                partes.append("␀")  # sentinel de NULL, no confundible con texto real
            elif isinstance(v, float):
                partes.append(repr(v))
            else:
                partes.append(str(v))
        h.update("\x1f".join(partes).encode("utf-8"))
        h.update(b"\x1e")
    return h.hexdigest()


@dataclass
class DiferenciaTabla:
    tabla: str
    conteo_original: int
    conteo_restaurado: int
    hash_original: str
    hash_restaurado: str

    @property
    def identica(self) -> bool:
        return (
            self.conteo_original == self.conteo_restaurado
            and self.hash_original == self.hash_restaurado
        )


def comparar_con_original(
    ruta_original: str, ruta_restaurada: str, esquema: dict[str, TablaSpec]
) -> list[DiferenciaTabla]:
    """Compara, tabla por tabla, la base RESTAURADA contra la ORIGINAL.
    Abre la original en modo `ro` (solo lectura) — nunca en modo escritura."""
    uri_original = f"file:{ruta_original}?mode=ro"
    conn_orig = sqlite3.connect(uri_original, uri=True)
    conn_rest = sqlite3.connect(f"file:{ruta_restaurada}?mode=ro", uri=True)
    resultados = []
    try:
        for tabla, (_csv, _ddl, columnas, pk) in esquema.items():
            nombres = [c for c, _t in columnas]
            n_orig = conn_orig.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            n_rest = conn_rest.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            h_orig = hash_tabla(conn_orig, tabla, nombres, pk)
            h_rest = hash_tabla(conn_rest, tabla, nombres, pk)
            resultados.append(DiferenciaTabla(tabla, n_orig, n_rest, h_orig, h_rest))
    finally:
        conn_orig.close()
        conn_rest.close()
    return resultados


def _ultimo_sello(ruta_db: str) -> str | None:
    conn = sqlite3.connect(f"file:{ruta_db}?mode=ro", uri=True)
    try:
        fila = conn.execute("SELECT MAX(fecha) FROM snapshots").fetchone()
        return fila[0] if fila else None
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origen", default=ORIGEN_POR_DEFECTO, help="directorio con los CSV de data/backups/")
    ap.add_argument("--destino", default=None, help="directorio destino (por defecto: uno temporal nuevo)")
    ap.add_argument("--verificar", action="store_true",
                     help="además compara contra senales.db/noticias.db reales del repo (solo lectura)")
    args = ap.parse_args()

    dir_destino = args.destino or tempfile.mkdtemp(prefix="mki_restaurado_")

    print(f"Origen : {args.origen}")
    print(f"Destino: {dir_destino}\n")

    ruta_senales, ruta_noticias, reportes = restaurar(args.origen, dir_destino)

    huno = False
    for r in reportes:
        estado = "ok" if not r.hallazgos and r.filas_csv == r.filas_importadas else "AVISO"
        print(f"[{estado}] {r.tabla}: {r.filas_csv} filas CSV -> {r.filas_importadas} importadas")
        for h in r.hallazgos:
            huno = True
            print(f"         hallazgo: {h}")

    print(f"\nÚltimo sello en la base restaurada: {_ultimo_sello(ruta_senales)}")

    if args.verificar:
        print("\n--- comparación contra las bases reales del repo (solo lectura) ---")
        ruta_senales_real = os.path.join(RAIZ_REPO, "senales.db")
        ruta_noticias_real = os.path.join(RAIZ_REPO, "noticias.db")

        if os.path.isfile(ruta_senales_real):
            diffs = comparar_con_original(ruta_senales_real, ruta_senales, ESQUEMA_SENALES)
            for d in diffs:
                marca = "IDÉNTICA" if d.identica else "DIFIERE"
                print(f"  senales.{d.tabla}: {marca}  (n original={d.conteo_original} "
                      f"n restaurada={d.conteo_restaurado})")
                if not d.identica:
                    huno = True
            print(f"  último sello original : {_ultimo_sello(ruta_senales_real)}")
            print(f"  último sello restaurado: {_ultimo_sello(ruta_senales)}")
        else:
            print("  senales.db no existe en este checkout — nada que comparar "
                  "(exactamente el escenario de 'se perdió el disco')")

        if os.path.isfile(ruta_noticias_real):
            diffs = comparar_con_original(ruta_noticias_real, ruta_noticias, ESQUEMA_NOTICIAS)
            for d in diffs:
                marca = "IDÉNTICA" if d.identica else "DIFIERE"
                print(f"  noticias.{d.tabla}: {marca}  (n original={d.conteo_original} "
                      f"n restaurada={d.conteo_restaurado})")
                if not d.identica:
                    huno = True
        else:
            print("  noticias.db no existe en este checkout — nada que comparar")

    return 1 if huno else 0


if __name__ == "__main__":
    sys.exit(main())
