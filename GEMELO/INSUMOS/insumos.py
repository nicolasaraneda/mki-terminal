"""La copia congelada de insumos — arnés del diseño de `fuente_canonica.md` §5.

**NO está activado.** Nadie lo llama: ni `snapshot.py`, ni `mki`, ni un
timer. Es la contraprueba de que el diseño no es prosa, igual que
`GEMELO/SEGUNDO_SELLO/segundo_sello.py` lo es del segundo sello. Cablearlo
a la ruta de sellado toca `snapshot.py` y es decisión de Nicolás, con corte
de método y fecha (expediente §5.2 y §6).

Qué hace, en tres funciones puras respecto del sello:

  congelar(frames, fecha_sello, directorio)
      Escribe `directorio/<fecha_sello>.csv.gz` con TODAS las celdas de los
      frames tal como se recibieron (serie, fecha_barra, campo, valor) y
      devuelve el sha256 del CSV canónico en claro. Es ADITIVO: si el
      archivo de esa fecha ya existe, se niega y lo dice. Nunca escribe en
      `senales.db`. Nunca descarga nada: recibe los frames que el proceso
      que selló ya tenía en memoria (`motor._cache`), que es el único lugar
      donde están los bytes que se consumieron.

  leer(fecha_sello, directorio) → (panel de cierres, sha256)
      Reconstruye el panel fecha_barra × serie y verifica el hash.

  contrastar(fecha_a, fecha_b, directorio) → veredicto por serie
      Compara dos copias (a anterior a b) sobre las fechas ≤ última de a:
      PARIDAD | BARRA_RETIRADA | BARRA_APARECIDA | DIVERGENCIA_DE_VALOR |
      RETORNO_CAMBIADO, con la aritmética de `GEMELO.fuente_canonica`.

  intermitencia(fechas_sello, directorio) → barras que van y vienen
      Con tres o más copias: una barra presente en una copia, ausente en
      una posterior y presente otra vez es INTERMITENTE — la clase que el
      Frente A sólo pudo inferir (M6) y que con copias se lee.

Costo medido en `tests/test_insumos.py` (un panel sintético de 750 barras
× 32 series comprime a decenas de KB).
"""
from __future__ import annotations

import gzip
import hashlib
import io
import os
import sys

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from GEMELO.fuente_canonica import clasificar_celdas   # noqa: E402  (puro)

DIRECTORIO_DEFECTO = os.path.join(_RAIZ, "data", "insumos")
COLUMNAS = ("serie", "fecha_barra", "campo", "valor")
FORMATO_VALOR = "%.10g"     # 10 cifras: más que el float32 que sirve la fuente


class YaCongelado(Exception):
    """Ya existe una copia para esa fecha de sello: no se sobreescribe."""


def _canonico(frames: dict) -> pd.DataFrame:
    """Las celdas de todos los frames, en un orden único, sin NaN."""
    filas = []
    for nombre, df in frames.items():
        if df is None or len(df) == 0:
            continue
        if isinstance(df, pd.Series):
            df = df.to_frame(name=nombre)
        columnas = list(df.columns)
        if isinstance(df.columns, pd.MultiIndex):
            raise ValueError("los frames deben tener columnas simples (serie o campo)")
        for col in columnas:
            serie = df[col].dropna()
            if serie.empty:
                continue
            # un frame ancho (columna = ticker) es campo 'close'; un frame
            # OHLC de un ticker (columnas Open/Close) usa el nombre del frame
            # y un campo propio (`ohlc_*`), para que el cierre que bajó el
            # verificador no se confunda con el cierre del panel del motor:
            # son dos descargas y pueden diferir — eso es justo lo que se
            # quiere poder ver.
            if col in ("Open", "Close", "open", "close"):
                nombre_serie, campo = nombre, "ohlc_" + col.lower()
            else:
                nombre_serie, campo = col, "close"
            filas.append(pd.DataFrame({
                "serie": nombre_serie,
                "fecha_barra": pd.to_datetime(serie.index).strftime("%Y-%m-%d"),
                "campo": campo,
                "valor": serie.to_numpy(dtype=float),
            }))
    if not filas:
        return pd.DataFrame(columns=COLUMNAS)
    out = pd.concat(filas, ignore_index=True)
    return out.sort_values(list(COLUMNAS[:3]), kind="mergesort").reset_index(drop=True)


def _texto(df: pd.DataFrame) -> str:
    buf = io.StringIO()
    df.to_csv(buf, index=False, float_format=FORMATO_VALOR, lineterminator="\n")
    return buf.getvalue()


def sha256_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def ruta_de(fecha_sello: str, directorio: str = DIRECTORIO_DEFECTO) -> str:
    return os.path.join(directorio, f"{fecha_sello}.csv.gz")


def congelar(frames: dict, fecha_sello: str,
             directorio: str = DIRECTORIO_DEFECTO) -> dict:
    """Escribe la copia del día y devuelve {sha256, filas, bytes, ruta}.
    Aditivo: se niega a sobreescribir. No toca ninguna base."""
    ruta = ruta_de(fecha_sello, directorio)
    if os.path.exists(ruta):
        raise YaCongelado(f"ya existe {ruta}: una copia de insumos no se reescribe")
    canon = _canonico(frames)
    texto = _texto(canon)
    os.makedirs(directorio, exist_ok=True)
    with gzip.open(ruta, "wt", encoding="utf-8", compresslevel=9) as f:
        f.write(texto)
    return {"sha256": sha256_texto(texto), "filas": int(len(canon)),
            "bytes": os.path.getsize(ruta), "ruta": ruta}


def leer(fecha_sello: str, directorio: str = DIRECTORIO_DEFECTO,
         campo: str = "close") -> tuple:
    """(panel fecha_barra × serie del campo pedido, sha256 del CSV en claro)."""
    ruta = ruta_de(fecha_sello, directorio)
    with gzip.open(ruta, "rt", encoding="utf-8") as f:
        texto = f.read()
    df = pd.read_csv(io.StringIO(texto), dtype={"serie": str, "fecha_barra": str, "campo": str})
    df = df[df["campo"] == campo]
    panel = df.pivot(index="fecha_barra", columns="serie", values="valor")
    panel.index = pd.to_datetime(panel.index)
    return panel.sort_index(), sha256_texto(texto)


def contrastar(fecha_a: str, fecha_b: str,
               directorio: str = DIRECTORIO_DEFECTO) -> dict:
    """Compara la copia `a` (anterior) con la `b` (posterior) sobre las fechas
    de barra ≤ última de `a`. Un veredicto por serie."""
    pa, ha = leer(fecha_a, directorio)
    pb, hb = leer(fecha_b, directorio)
    hasta = pa.index.max().date().isoformat()
    celdas = clasificar_celdas(pa, pb, hasta)
    veredictos = {}
    for serie, c in celdas.items():
        if c.get("sin_serie_hoy"):
            v = "SERIE_AUSENTE"
        elif c["retirada"]:
            v = "BARRA_RETIRADA"
        elif c["retornos_cambiados"]:
            v = "RETORNO_CAMBIADO"
        elif c["aparecida"]:
            v = "BARRA_APARECIDA"
        elif c["no_proporcional"] or c["distinta"] and not c["proporcional"]:
            v = "DIVERGENCIA_DE_VALOR"
        elif c["distinta"]:
            v = "PARIDAD_REESCALADA"    # dividendos: niveles distintos, retornos iguales
        else:
            v = "PARIDAD"
        veredictos[serie] = {"veredicto": v, "detalle": c}
    return {"a": fecha_a, "b": fecha_b, "sha256_a": ha, "sha256_b": hb,
            "hasta": hasta, "series": veredictos,
            "conteo": {v: sum(1 for x in veredictos.values() if x["veredicto"] == v)
                       for v in sorted({x["veredicto"] for x in veredictos.values()})}}


def intermitencia(fechas_sello: list, directorio: str = DIRECTORIO_DEFECTO) -> list:
    """Barras (serie, fecha_barra) presentes en una copia, ausentes en una
    posterior y presentes de nuevo en otra posterior: INTERMITENTE."""
    if len(fechas_sello) < 3:
        return []
    paneles = [leer(f, directorio)[0] for f in fechas_sello]
    series = sorted(set().union(*[set(p.columns) for p in paneles]))
    fechas = sorted(set().union(*[set(p.index) for p in paneles]))
    out = []
    for s in series:
        presencia = np.array([[bool(s in p.columns and d in p.index and pd.notna(p.at[d, s]))
                               for d in fechas] for p in paneles])       # copias × barras
        for j, d in enumerate(fechas):
            col = presencia[:, j]
            # patrón 1 … 0 … 1 en el orden de las copias
            unos = np.where(col)[0]
            if len(unos) >= 2 and not col[unos[0]:unos[-1] + 1].all():
                ausentes = [fechas_sello[i] for i in range(unos[0], unos[-1] + 1) if not col[i]]
                out.append({"serie": s, "fecha_barra": d.date().isoformat(),
                            "ausente_en": ausentes,
                            "presente_en": [fechas_sello[i] for i in unos]})
    return out
