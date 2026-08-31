# ============================================================
# replica.py — registro de divergencias titular/réplica (Frente D)
#
# docs/REPLICA.md es el diseño (§3 propone la tabla, §5 marca qué necesita
# la firma de Nicolás). Este módulo implementa SOLO la parte ejecutable sin
# esa firma: persistir, como dato de auditoría, lo que ya calcula
# `comparar_sombra.comparar_fecha` — nunca decide nada, nunca reescribe
# nada.
#
# QUÉ NO HACE ESTE ARCHIVO (a propósito):
#   - No decide "quién gana" ante una discrepancia. `resuelto_como` queda
#     SIEMPRE en NULL: la regla del §2 de REPLICA.md ("la titular gana
#     siempre") es una PROPUESTA razonada, no una decisión adoptada. Fijar
#     ese valor acá sería implementar el §2 como si ya estuviera resuelto.
#   - No retira `FECHA_CORTE` de `comparar_sombra.py` como comportamiento
#     por defecto — eso es una decisión de Nicolás (REPLICA.md §5). Lo
#     único que se tocó ahí es un parámetro ADITIVO (`fecha_corte=None`)
#     con el mismo valor por defecto que antes; ver el comentario en
#     `comparar_sombra.comparar_fecha`.
#   - No escribe en `senales.db` ni en `noticias.db`. Vive en su propia
#     base, `data/divergencias_replica.db`, nueva y propia de este frente.
#   - No corre sola: nadie la invoca todavía (ni timer, ni cron, ni `mki`).
#     Es código que existe y se prueba, no que se ejecuta.
#
# INMUTABILIDAD: mismo espíritu que el resto del proyecto con los sellos
# — esta tabla no es un sello de predicción, pero es igual de aditiva:
# solo INSERT, nunca UPDATE ni DELETE sobre una fila ya escrita. Cada fila
# es un HALLAZGO de una comparación, nunca una corrección de otra fila (ni
# de esta tabla ni, mucho menos, de `senales.db`).
# ============================================================

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(DIRECTORIO, "data", "divergencias_replica.db")

VEREDICTO_DIVERGENCIA = "DIVERGENCIA"  # mismo vocabulario que comparar_sombra.py

# --- Las tres clases del §1 de REPLICA.md ---
CLASE_INSUMOS = "insumos"
CLASE_COMPUTO = "computo"
CLASE_EXISTENCIA = "existencia"
CLASES_VALIDAS = (CLASE_INSUMOS, CLASE_COMPUTO, CLASE_EXISTENCIA)

# Campos que reflejan disponibilidad/calidad de los datos de mercado (una
# discrepancia ahí es "el mundo siendo asíncrono", REPLICA.md §1), no un
# desacuerdo del motor sobre los mismos insumos.
CAMPOS_INSUMOS = {
    "sox_usado_pct", "sox_fecha",
    "descarga_ok", "descarga_total", "descarga_caidos",
    "n_muestra",
}
# Ámbitos que por construcción son de existencia en comparar_sombra.py:
# columnas presentes en una máquina y ausentes en la otra ("esquema"), o
# conjuntos/conteos de filas distintos ("conjunto").
AMBITOS_EXISTENCIA = {"esquema", "conjunto"}

# Marcador sintético para el caso sin hallazgos de campo: una máquina no
# selló la fecha en absoluto (comparar_fecha devuelve DIVERGENCIA con
# `hallazgos == []` cuando el titular selló y la sombra no, rama B.3).
CAMPO_SELLO_AUSENTE = "sello_ausente"


def _clasificar(hallazgo: dict) -> str:
    """insumos / computo / existencia — ver docs/REPLICA.md §1.

    Es una categorización auxiliar para la auditoría (§3): no resuelve
    nada, solo ayuda a leer después "¿sube la tasa de insumos o la de
    cómputo?". Si algún caso no encaja claramente en insumos o existencia,
    cae en cómputo por default (es la clase "resultado del motor con los
    mismos insumos", la más amplia de las tres)."""
    if hallazgo.get("campo") == CAMPO_SELLO_AUSENTE:
        return CLASE_EXISTENCIA
    if hallazgo.get("ambito") in AMBITOS_EXISTENCIA:
        return CLASE_EXISTENCIA
    if hallazgo.get("campo") in CAMPOS_INSUMOS:
        return CLASE_INSUMOS
    return CLASE_COMPUTO


def _conectar(ruta_db: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(ruta_db)), exist_ok=True)
    return sqlite3.connect(ruta_db)


def _asegurar_tabla(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS divergencias_replica (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            nivel INTEGER,
            ambito TEXT,
            clave TEXT,
            campo TEXT NOT NULL,
            valor_titular TEXT,
            valor_sombra TEXT,
            clase TEXT NOT NULL CHECK (clase IN ('insumos', 'computo', 'existencia')),
            tolerancia_excedida INTEGER NOT NULL,
            resuelto_como TEXT,
            detectado_en TEXT NOT NULL
        )
    """)
    conn.commit()


def registrar_comparacion(res: dict, ruta_db: str = RUTA_DB) -> int:
    """Persiste, como filas de auditoría ADITIVAS, los hallazgos de UNA
    comparación (el dict que devuelve `comparar_sombra.comparar_fecha`, o
    una estructura equivalente con las mismas claves: `fecha`, `veredicto`,
    `hallazgos`).

    Solo escribe algo si el veredicto es DIVERGENCIA:
      - PARIDAD, DIA_NO_COMPUTABLE, PENDIENTE_PUBLICACION → 0 filas. Una
        ausencia legítima (corte, huella de copia, titular sin publicar
        aún, sombra no cerrada) NUNCA es una divergencia — registrarla
        como tal sería ruido, exactamente lo que REPLICA.md §3 pide evitar.
      - DIVERGENCIA con `hallazgos` → una fila por hallazgo (niveles 1 y 2
        únicamente; las diferencias de nivel 3 en `esperadas` son, por
        diseño, legítimas y no se registran acá).
      - DIVERGENCIA sin `hallazgos` (una máquina no selló la fecha en
        absoluto) → una fila sintética `sello_ausente`, clase existencia.

    `resuelto_como` se deja SIEMPRE en NULL — ver el bloque de arriba.
    Devuelve el número de filas insertadas."""
    if res.get("veredicto") != VEREDICTO_DIVERGENCIA:
        return 0

    fecha = res["fecha"]
    detectado_en = datetime.now(timezone.utc).isoformat()
    hallazgos = res.get("hallazgos") or []

    filas = []
    if hallazgos:
        for h in hallazgos:
            filas.append((
                fecha,
                h.get("nivel"),
                h.get("ambito"),
                h.get("clave"),
                h["campo"],
                h.get("titular"),
                h.get("sombra"),
                _clasificar(h),
                1,      # tolerancia_excedida: todo hallazgo de nivel 1/2 la excedió
                None,   # resuelto_como: nunca se decide acá
                detectado_en,
            ))
    else:
        filas.append((
            fecha, None, "sello", fecha, CAMPO_SELLO_AUSENTE,
            None, None, CLASE_EXISTENCIA, 1, None, detectado_en,
        ))

    conn = _conectar(ruta_db)
    try:
        _asegurar_tabla(conn)
        conn.executemany(
            """INSERT INTO divergencias_replica
               (fecha, nivel, ambito, clave, campo, valor_titular, valor_sombra,
                clase, tolerancia_excedida, resuelto_como, detectado_en)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            filas,
        )
        conn.commit()
    finally:
        conn.close()
    return len(filas)


def leer_divergencias(ruta_db: str = RUTA_DB, fecha: str | None = None) -> list[dict]:
    """Lectura de solo auditoría — jamás se usa para decidir nada (§3). Si
    la base todavía no existe o la tabla todavía no se creó, devuelve []."""
    if not os.path.exists(ruta_db):
        return []
    conn = sqlite3.connect(f"file:{ruta_db}?mode=ro", uri=True)
    try:
        conn.row_factory = sqlite3.Row
        if fecha is not None:
            cur = conn.execute(
                "SELECT * FROM divergencias_replica WHERE fecha = ? ORDER BY id",
                (fecha,))
        else:
            cur = conn.execute("SELECT * FROM divergencias_replica ORDER BY id")
        return [dict(r) for r in cur.fetchall()]
    except sqlite3.OperationalError:
        return []   # tabla aún no creada: cero divergencias registradas
    finally:
        conn.close()
