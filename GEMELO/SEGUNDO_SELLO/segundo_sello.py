# ============================================================
# GEMELO/SEGUNDO_SELLO/segundo_sello.py — el arnés del SEGUNDO SELLO.
#
# El diseño, con sus siete restricciones y lo que espera firma, vive en
# `docs/SEGUNDO_SELLO.md`. Este archivo implementa SOLO la parte que se
# puede construir sin la firma de Nicolás: el mecanismo que OBSERVA la
# fuente más tarde, REGISTRA lo que vio, y CONTRASTA contra el sello — y
# la CONTRAPRUEBA que demuestra que puede discrepar.
#
# QUÉ NO HACE ESTE ARCHIVO (a propósito, igual que `replica.py`):
#   - No decide cuál fila es canónica. La regla candidata ("gana siempre
#     la primera") está PROPUESTA en `docs/SEGUNDO_SELLO.md` §3 y NO
#     implementada: `contrastar` devuelve un veredicto descriptivo y
#     `canonica` queda SIEMPRE en NULL.
#   - No escribe en `senales.db` ni en `noticias.db`. Vive en su propia
#     base, `data/segundo_sello.db`, nueva y propia de este frente.
#   - No corre sola: ni timer, ni cron, ni `mki`. Es código que existe y
#     se prueba, no que se ejecuta.
#   - No toca `motor.py`, `snapshot.py`, `senales.py` ni `universo.py`.
#     Nada de la ruta de sellado importa este módulo (hay un test).
#
# LAS DOS PROPIEDADES QUE HACEN QUE ESTO SEA UNA VERIFICACIÓN
# ------------------------------------------------------------
# (1) CEGUERA (restricción B2). La fase que produce el número —`observar`
#     y su proveedor— NO puede leer lo que selló la primera. No abre
#     `senales.db`, no importa `senales`, `snapshot` ni `motor`, y ni
#     siquiera recibe la lista de fechas selladas: recibe fechas. Un test
#     de AST lo verifica sobre el árbol sintáctico, no sobre la intención.
#     Si la observación pudiera mirar el sello antes de producir su
#     número, esto sería una confirmación, no una verificación (regla 1
#     de la casa, `DECISIONES.md` §52).
# (2) ADITIVIDAD (restricción B1). `registrar` solo hace INSERT. Nunca
#     UPDATE, nunca DELETE, nunca sobre `senales.db`. Una observación
#     posterior no corrige a la anterior: se suma. La primera fila sellada
#     queda intacta para siempre.
#
# LO QUE SE MANTIENE FIJO A PROPÓSITO, Y POR QUÉ NO VIOLA LA REGLA 1
# ------------------------------------------------------------
# `contrastar` deriva su número con la MISMA función de la producción
# (`motor._ultimo_mov_no_cero`, importada tarde y pura: no descarga nada).
# Eso es deliberado y es lo que hace válida la comparación: el objeto bajo
# prueba es el DATO, no el mecanismo. Si el mecanismo también cambiara, una
# diferencia no sería atribuible. La consecuencia, dicha con todas las
# letras en `docs/SEGUNDO_SELLO.md` §6: este arnés NO puede decirte si el
# modelo está bien; solo si sus insumos siguen siendo los mismos.
# ============================================================

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import date, datetime, timezone

import pandas as pd

DIRECTORIO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUTA_DB = os.path.join(DIRECTORIO, "data", "segundo_sello.db")
RUTA_SENALES = os.path.join(DIRECTORIO, "senales.db")

# --- Parámetros CONGELADOS antes de la primera fila (docs/SEGUNDO_SELLO.md §7) ---

# Media unidad del último decimal que la producción sella: `sox_usado_pct`
# se guarda con `round(..., 2)`, así que cualquier diferencia > 0.005 pp no
# puede ser redondeo. No es una intuición: 23 de 25 fechas selladas
# reproducen con diferencia EXACTAMENTE 0.00 (medición del 1-sep-2026).
TOLERANCIA_PP = 0.005

# La escalera de horizontes de la FASE DE MEDICIÓN (§5). No es la hora
# definitiva: es el instrumento con el que se mide cuándo asienta la
# fuente, porque hoy nadie lo sabe. Congelar una hora con n=1 sería
# inventar precisión.
HORIZONTES_SESIONES = (1, 3, 7, 30)

TICKER_INSUMO = "^SOX"

# --- Vocabulario de veredictos ---
# Hereda la lección de `comparar_sombra.py`: "nada = nada" NUNCA es
# paridad. Las dos ausencias tienen nombre propio y no son finales.
PARIDAD = "PARIDAD"
DIVERGENCIA_DE_VALOR = "DIVERGENCIA_DE_VALOR"
BARRA_RETIRADA = "BARRA_RETIRADA"
BARRA_APARECIDA = "BARRA_APARECIDA"
SIN_SEGUNDA_OBSERVACION = "SIN_SEGUNDA_OBSERVACION"   # no final
SIN_SELLO = "SIN_SELLO"                               # no final
VEREDICTOS = (PARIDAD, DIVERGENCIA_DE_VALOR, BARRA_RETIRADA, BARRA_APARECIDA,
              SIN_SEGUNDA_OBSERVACION, SIN_SELLO)
VEREDICTOS_FINALES = (PARIDAD, DIVERGENCIA_DE_VALOR, BARRA_RETIRADA,
                      BARRA_APARECIDA)


# ============================================================
# FASE 1 — OBSERVAR.  CIEGA al sello por construcción.
# ============================================================

def proveedor_yahoo(tickers: tuple, anios: int = 3) -> pd.DataFrame:
    """El ÚNICO punto de este módulo que toca la red. Devuelve cierres
    diarios indexados por fecha, una columna por ticker.

    Descarga DUPLICADA a propósito respecto de `motor._datos_crudos`: si
    este módulo compartiera la caché del motor, observaría el mismo objeto
    en memoria que la producción ya usó y no vería nada. La duplicación es
    el punto, no un descuido (misma disciplina que `GEMELO/datos.py`)."""
    import yfinance as yf   # import tardío: el módulo se importa sin red
    data = yf.download(list(tickers), period=f"{anios}y", interval="1d",
                       auto_adjust=True, progress=False)
    if data.empty:
        return pd.DataFrame()
    cierres = (data["Close"] if isinstance(data.columns, pd.MultiIndex)
               else data[["Close"]])
    if isinstance(cierres, pd.Series):
        cierres = cierres.to_frame(name=tickers[0])
    return cierres


def id_corrida(observado_en: str, horizonte: int | None = None) -> str:
    """Identificador estable de una corrida de observación. Entra en la
    clave de la tabla para que dos observaciones del mismo día se sumen en
    vez de pisarse."""
    crudo = json.dumps([observado_en, horizonte], sort_keys=True)
    return hashlib.sha256(crudo.encode()).hexdigest()[:16]


def observar(fechas, proveedor, tickers: tuple = (TICKER_INSUMO,),
             observado_en: str | None = None, horizonte: int | None = None,
             corrida: str | None = None) -> list[dict]:
    """Qué sirve la fuente HOY para cada una de `fechas`.

    CIEGA: no abre ninguna base, no conoce ningún valor sellado y ni
    siquiera sabe qué fechas están selladas — `fechas` es un argumento.
    `proveedor` es inyectable justamente para que la contraprueba pueda
    alimentarla con una serie perturbada de forma conocida.

    Devuelve una fila por (fecha, ticker) con:
      - `cierre`: el cierre que la fuente sirve hoy, o None,
      - `hay_barra`: si la fuente tiene una barra para esa fecha.
    La distinción importa: `hay_barra=False` NO es `cierre=0`. El único
    incidente medido hasta hoy (2026-08-28) es una barra que desapareció,
    no un precio que cambió — y un diseño que solo compare precios no lo
    ve."""
    marca = observado_en or datetime.now(timezone.utc).isoformat()
    cid = corrida or id_corrida(marca, horizonte)
    cierres = proveedor(tuple(tickers))
    filas = []
    indice = set()
    if cierres is not None and not cierres.empty:
        indice = {i.date() if hasattr(i, "date") else i for i in cierres.index}
    for f in fechas:
        f = date.fromisoformat(f) if isinstance(f, str) else f
        for t in tickers:
            valor, hay = None, False
            if f in indice and cierres is not None and t in cierres.columns:
                bruto = cierres[t].loc[[i for i in cierres.index
                                        if (i.date() if hasattr(i, "date") else i) == f][0]]
                if pd.notna(bruto):
                    valor, hay = float(bruto), True
            filas.append({
                "corrida": cid, "fecha_observada": f.isoformat(), "ticker": t,
                "cierre": valor, "hay_barra": int(hay),
                "horizonte_sesiones": horizonte, "observado_en": marca,
            })
    return filas


# ============================================================
# FASE 2 — REGISTRAR.  ADITIVA: solo INSERT, jamás UPDATE ni DELETE.
# ============================================================

def _conectar(ruta_db: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(ruta_db)), exist_ok=True)
    return sqlite3.connect(ruta_db)


def _asegurar_tabla(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS observaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corrida TEXT NOT NULL,
            fecha_observada TEXT NOT NULL,
            ticker TEXT NOT NULL,
            cierre REAL,
            hay_barra INTEGER NOT NULL,
            horizonte_sesiones INTEGER,
            observado_en TEXT NOT NULL,
            UNIQUE (corrida, fecha_observada, ticker)
        )
    """)
    conn.commit()


def registrar(observaciones: list, ruta_db: str = RUTA_DB) -> int:
    """Persiste observaciones. Devuelve cuántas filas NUEVAS entraron.

    `INSERT OR IGNORE`: una corrida repetida no pisa nada, se abstiene. El
    único modo de que un valor de esta tabla cambie sería borrarlo, y este
    módulo no tiene una sola sentencia que borre."""
    if not observaciones:
        return 0
    conn = _conectar(ruta_db)
    try:
        _asegurar_tabla(conn)
        antes = conn.execute("SELECT COUNT(*) FROM observaciones").fetchone()[0]
        conn.executemany(
            """INSERT OR IGNORE INTO observaciones
               (corrida, fecha_observada, ticker, cierre, hay_barra,
                horizonte_sesiones, observado_en)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [(o["corrida"], o["fecha_observada"], o["ticker"], o["cierre"],
              o["hay_barra"], o.get("horizonte_sesiones"), o["observado_en"])
             for o in observaciones])
        conn.commit()
        despues = conn.execute("SELECT COUNT(*) FROM observaciones").fetchone()[0]
    finally:
        conn.close()
    return despues - antes


def leer_observaciones(corrida: str, ruta_db: str = RUTA_DB,
                       ticker: str = TICKER_INSUMO) -> pd.DataFrame:
    if not os.path.exists(ruta_db):
        return pd.DataFrame()
    conn = sqlite3.connect(f"file:{ruta_db}?mode=ro", uri=True)
    try:
        return pd.read_sql_query(
            "SELECT fecha_observada, cierre, hay_barra, horizonte_sesiones, "
            "observado_en FROM observaciones WHERE corrida = ? AND ticker = ? "
            "ORDER BY fecha_observada", conn, params=(corrida, ticker))
    finally:
        conn.close()


# ============================================================
# FASE 3 — CONTRASTAR.  La única fase que abre `senales.db`, y en mode=ro.
# ============================================================

def _sellado(fecha: str, ruta_senales: str) -> dict | None:
    if not os.path.exists(ruta_senales):
        return None
    conn = sqlite3.connect(f"file:{ruta_senales}?mode=ro", uri=True)
    try:
        fila = conn.execute(
            "SELECT sox_usado_pct, sox_fecha, timestamp_utc, plataforma_version "
            "FROM snapshots WHERE fecha = ?", (fecha,)).fetchone()
    finally:
        conn.close()
    if fila is None or fila[0] is None:
        return None
    return {"sox_usado_pct": float(fila[0]), "sox_fecha": fila[1],
            "timestamp_utc": fila[2], "plataforma_version": fila[3]}


def sesiones_xnys(desde: str, hasta: str) -> list:
    """Las sesiones de XNYS del rango, como lista de 'YYYY-MM-DD'.

    Existe por una razón medida, no por prolijidad: la primera corrida de
    este arnés (1-sep-2026) observó SOLO las fechas selladas y reportó el
    2026-08-07 como divergencia de 0.34 pp. Era un artefacto — faltaba la
    barra del 08-06, que no está sellada porque ese día no hubo snapshot,
    y el retorno derivado abarcó dos sesiones en vez de una. Es el MISMO
    error de índice mutilado que produce el 3.47 de
    `GEMELO/CONDICIONAL/condicional.py` vía ffill. Un mecanismo que
    compara series tiene que cubrir el calendario, no la muestra."""
    import exchange_calendars as xc   # import tardío: no hace falta al observar
    cal = xc.get_calendar("XNYS")
    return [str(pd.Timestamp(s).date())
            for s in cal.sessions_in_range(desde, hasta)]


def _derivar(obs: pd.DataFrame, hasta: str) -> tuple:
    """El mismo número que la producción selló, derivado de lo que la
    fuente sirve HOY. Usa la función de producción, sin red.

    Devuelve (valor_pct, fecha_del_movimiento, fecha_previa_del_par): el
    tercer elemento importa porque un retorno depende de DOS barras, y la
    que desapareció el 28-ago fue la previa, no la del movimiento."""
    from motor import _ultimo_mov_no_cero   # puro; import tardío a propósito
    if obs.empty:
        return None, None, None
    d = obs[obs["fecha_observada"] <= hasta]
    d = d[d["hay_barra"] == 1].dropna(subset=["cierre"])
    if len(d) < 2:
        return None, None, None
    serie = pd.Series(d["cierre"].to_numpy(float),
                      index=pd.to_datetime(d["fecha_observada"]))
    valor, fecha_mov = _ultimo_mov_no_cero(serie.pct_change())
    if fecha_mov is None:
        return None, None, None
    fechas = [i.date() for i in serie.index]
    previa = fechas[fechas.index(fecha_mov) - 1] if fechas.index(fecha_mov) else None
    return valor, fecha_mov, previa


def contrastar(fecha: str, corrida: str, ruta_db: str = RUTA_DB,
               ruta_senales: str = RUTA_SENALES,
               tolerancia_pp: float = TOLERANCIA_PP,
               sesiones: list | None = None) -> dict:
    """Contrasta el sello de `fecha` contra lo observado en `corrida`.

    `sesiones` es el calendario esperado (`sesiones_xnys`). Pasarlo es lo
    que separa un hallazgo de un artefacto: sin él, una sesión que falta
    en la MUESTRA se confunde con una sesión que falta en la FUENTE, y el
    contraste reporta una divergencia de valor que no existe. Se admite
    None para poder probar el módulo sin calendario, y en ese caso el
    resultado sale marcado `cobertura_verificada=False`.

    NO decide nada: `canonica` sale SIEMPRE en None. La regla del §3 de
    `docs/SEGUNDO_SELLO.md` ("gana siempre la primera") es una PROPUESTA
    razonada que espera la firma de Nicolás; fijarla acá sería
    implementarla como si ya estuviera decidida."""
    sello = _sellado(fecha, ruta_senales)
    obs = leer_observaciones(corrida, ruta_db)
    base = {"fecha": fecha, "corrida": corrida, "canonica": None,
            "tolerancia_pp": tolerancia_pp,
            "cobertura_verificada": sesiones is not None}

    def _fin(veredicto, final, valor=None, dif=None, **extra):
        return base | {"veredicto": veredicto, "final": final,
                       "sellado_pct": sello["sox_usado_pct"] if sello else None,
                       "observado_pct": valor, "dif_pp": dif} | extra

    if obs.empty:
        return _fin(SIN_SEGUNDA_OBSERVACION, False,
                    detalle="no hay observación para esa corrida — "
                            "ausencia, no paridad")
    if sello is None:
        return _fin(SIN_SELLO, False,
                    detalle="la fecha no tiene sello con sox_usado_pct — "
                            "ausencia, no paridad")

    observadas = set(obs["fecha_observada"])

    # --- GUARDIA DE COBERTURA. Va PRIMERO, y a propósito. ---
    if sesiones is not None:
        minima = min(observadas)
        requeridas = [s for s in sesiones if minima <= s <= fecha]
        faltantes = sorted(set(requeridas) - observadas)
        if len(requeridas) < 2 or faltantes:
            return _fin(SIN_SEGUNDA_OBSERVACION, False,
                        sesiones_no_observadas=faltantes[:10],
                        detalle="la observación no cubre todas las sesiones del "
                                "rango: cualquier diferencia sería un artefacto "
                                "de muestreo, no un hallazgo")

    valor, fecha_mov, previa = _derivar(obs, fecha)
    dif = None if valor is None else round(abs(sello["sox_usado_pct"] - valor), 4)
    usada = sello.get("sox_fecha")

    if valor is None:
        return _fin(SIN_SEGUNDA_OBSERVACION, False,
                    detalle="la observación no alcanza para derivar el número "
                            "— ausencia, no paridad")

    # --- BARRA RETIRADA. Se nombra aparte del cambio de precio porque son
    #     dos fenómenos distintos, y el único medido hasta hoy es éste.
    #     Un retorno depende de DOS barras: se miran las dos, y además
    #     todas las sesiones que hoy quedaron entre medio.
    retiradas = []
    if usada and usada in observadas:
        fila = obs[obs["fecha_observada"] == usada].iloc[0]
        if not bool(fila["hay_barra"]):
            retiradas.append(usada)
    if sesiones is not None and previa is not None:
        entre = [s for s in sesiones
                 if previa.isoformat() < s < fecha_mov.isoformat()]
        for s in entre:
            fila = obs[obs["fecha_observada"] == s]
            if len(fila) and not bool(fila.iloc[0]["hay_barra"]):
                retiradas.append(s)
    if retiradas:
        return _fin(BARRA_RETIRADA, True, valor, dif,
                    barra_usada_por_el_sello=usada,
                    sesiones_retiradas=sorted(set(retiradas)),
                    par_usado_hoy=[previa.isoformat() if previa else None,
                                   fecha_mov.isoformat()],
                    detalle="la fuente ya no sirve una barra que el sello sí "
                            "tuvo: el sello no es reproducible, lo cual NO "
                            "significa que esté mal")

    if usada and fecha_mov.isoformat() != usada:
        return _fin(BARRA_APARECIDA, True, valor, dif,
                    barra_usada_por_el_sello=usada,
                    barra_usada_hoy=fecha_mov.isoformat(),
                    detalle="hoy el último movimiento no-cero cae en otra "
                            "sesión que la que el sello usó")

    if dif > tolerancia_pp:
        return _fin(DIVERGENCIA_DE_VALOR, True, valor, dif,
                    par_usado_hoy=[previa.isoformat() if previa else None,
                                   fecha_mov.isoformat()],
                    detalle="mismo par de sesiones, distinto precio: la fuente "
                            "revisó el valor")

    return _fin(PARIDAD, True, valor, dif,
                detalle="el sello reproduce dentro de tolerancia")


# ============================================================
# LA CONTRAPRUEBA (restricción B2)
# ============================================================
# Un mecanismo que nunca discrepa no verifica nada: solo confirma. Esto
# inyecta una diferencia CONOCIDA en la serie que ve la observación y
# comprueba que el contraste la reporta con la magnitud correcta — y, como
# control negativo, que sin inyección da PARIDAD. Las dos ramas hacen
# falta: sin el control negativo, un mecanismo que gritara "divergencia"
# siempre pasaría la prueba positiva.

def contraprueba(cierres: pd.DataFrame, fecha: str, ruta_db: str,
                 ruta_senales: str, perturbacion_pp: float = 1.00,
                 ticker: str = TICKER_INSUMO, sesiones: list | None = None) -> dict:
    """Corre las dos ramas y devuelve el informe. `cierres` es la serie de
    control (la que reproduce el sello); la rama perturbada la deriva
    escalando el cierre de `fecha` para mover el retorno en
    `perturbacion_pp` puntos porcentuales exactos."""
    fechas = [str(i.date() if hasattr(i, "date") else i) for i in cierres.index]

    control = observar(fechas, lambda t: cierres, tickers=(ticker,),
                       observado_en="CONTRAPRUEBA-control", horizonte=0)
    registrar(control, ruta_db)
    r_control = contrastar(fecha, control[0]["corrida"], ruta_db, ruta_senales,
                           sesiones=sesiones)

    tocado = cierres.copy()
    idx = [i for i in tocado.index
           if str(i.date() if hasattr(i, "date") else i) == fecha][0]
    pos = list(tocado.index).index(idx)
    previo = float(tocado[ticker].iloc[pos - 1])
    actual = float(tocado[ticker].iloc[pos])
    nuevo = previo * (1.0 + (actual / previo - 1.0) + perturbacion_pp / 100.0)
    tocado.iloc[pos, tocado.columns.get_loc(ticker)] = nuevo

    perturbado = observar(fechas, lambda t: tocado, tickers=(ticker,),
                          observado_en="CONTRAPRUEBA-perturbada", horizonte=0)
    registrar(perturbado, ruta_db)
    r_pert = contrastar(fecha, perturbado[0]["corrida"], ruta_db, ruta_senales,
                        sesiones=sesiones)

    return {
        "perturbacion_pp": perturbacion_pp,
        "control": r_control,
        "perturbada": r_pert,
        "detecta": (r_control["veredicto"] == PARIDAD
                    and r_pert["veredicto"] == DIVERGENCIA_DE_VALOR),
        "magnitud_reportada_pp": r_pert.get("dif_pp"),
    }
