"""Ayudas de los tests sobre las bases reales (corrida 16-3, Bloque D; R5 del
dictamen 16-1 y hecho de entorno (ii) de la tarjeta §80, acta §102.2).

Hasta la 16-3 el marcador `solo_con_base` de cinco archivos preguntaba si el
ARCHIVO `senales.db` existía. En un árbol sin bases (un worktree) la propia
suite lo creaba vacío (`tests/test_api.py`: la API corre `init_db()` sobre la
ruta real) y, desde ese instante, los tests «con base» dejaban de saltarse y
corrían sobre una base vacía: tres rojos de `test_conocibilidad` que no
estaban en la línea base (medido en las corridas 16-1 y 16-2). La condición
pasa a ser «la tabla que el test lee tiene filas», leída en `mode=ro`, sin
crear nada. No es un test: no se recolecta (el nombre no empieza por
`test_`); los archivos lo importan porque `tests/` está en `sys.path` cuando
pytest los carga."""
import os
import sqlite3

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_SENALES = os.path.join(RAIZ, "senales.db")
RUTA_NOTICIAS = os.path.join(RAIZ, "noticias.db")
RUTA_SELLO_DINERO = os.path.join(RAIZ, "dinero", "sello_dinero.db")


def hay_filas(ruta: str, tabla: str) -> bool:
    """True sólo si `ruta` existe, tiene la tabla y la tabla tiene al menos
    una fila. Abre en `mode=ro` y no crea nada; un archivo vacío, una base
    sin la tabla o cualquier error de lectura cuentan como «sin base»."""
    if not os.path.exists(ruta) or os.path.getsize(ruta) == 0:
        return False
    try:
        con = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    except sqlite3.Error:
        return False
    try:
        return con.execute(f"SELECT 1 FROM {tabla} LIMIT 1").fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        con.close()


def razon_sin_base(ruta: str, tabla: str) -> str:
    return f"sin {os.path.basename(ruta)} con filas en {tabla}: no hay historia sellada que leer"
