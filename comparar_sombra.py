# ============================================================
# comparar_sombra.py — ¿sellaron lo mismo el titular y la sombra?
# (Etapa 5.0.3, Fase 3 de la reactivación)
#
# Durante la ventana de migración el Mac (TITULAR) y el PC (SOMBRA) sellan
# en paralelo las mismas fechas sobre la misma historia. Este script decide,
# día por día, si los dos sellos coinciden. Tres días hábiles con paridad
# habilitan el switch.
#
# CÓMO TRAE LOS SELLOS DEL TITULAR (pendiente #3 del acta de migración)
#   `git fetch` y después `git show origin/main:data/backups/<archivo>.csv`.
#   JAMÁS `git pull`: el árbol de trabajo es el código que los timers
#   ejecutan esta misma noche, y un merge lo alteraría bajo los pies. Nada
#   de lo que hace este script escribe en el árbol ni en el índice.
#
# EL LADO LOCAL sale de senales.db abierta en `mode=ro`. Es la base que va a
# convertirse en el track record; los CSV son su exportación. Se lee la
# fuente, no la copia.
#
#   python comparar_sombra.py                    → compara HOY
#   python comparar_sombra.py --fecha 2026-08-26
#   python comparar_sombra.py --desde 2026-08-26 --hasta 2026-08-28
#   python comparar_sombra.py --contador         → progreso de la ventana
#   python comparar_sombra.py --sin-fetch        → no toca la red
# ============================================================

import argparse
import io
import json
import os
import sqlite3
import subprocess
import sys
from datetime import date, datetime, timezone

import pandas as pd

DIRECTORIO = os.path.dirname(os.path.abspath(__file__))
DIR_SALIDA = os.path.join(DIRECTORIO, "data", "sombra")
RUTA_VEREDICTOS = os.path.join(DIR_SALIDA, "veredictos.jsonl")
REV_TITULAR = "origin/main"

# ------------------------------------------------------------
# FECHA DE CORTE — obligatoria, y la parte más fácil de hacer mal
# ------------------------------------------------------------
# Las bases del PC son copia por pendrive de las del Mac hasta el
# 2026-08-24 INCLUSIVE (Fase 0 de la reactivación: 35 snapshots, último
# sello 2026-08-24, 228 verificaciones). Para cualquier fecha <= ese día
# las dos máquinas no tienen datos "parecidos": tienen LITERALMENTE el
# mismo archivo. Compararlas da paridad perfecta y no significa nada — es
# comparar un archivo consigo mismo.
#
# Por eso el comparador se NIEGA a evaluar esas fechas y lo dice. Un
# comparador que reportara esa paridad trivial sin avisar sería peor que no
# tenerlo: produciría tres días verdes en una tarde y habilitaría un switch
# sobre evidencia vacía.
FECHA_CORTE = date(2026, 8, 24)

# ------------------------------------------------------------
# LOS TRES NIVELES DE TOLERANCIA — declarados ANTES de correr
# ------------------------------------------------------------
# La intuición ingenua ("son floats, pon tolerancia amplia") es justo el
# error: las dos máquinas corren pandas 3.0.3 y numpy 2.4.6 idénticos sobre
# la misma ventana de 120 sesiones. Con los mismos insumos los números
# deben salir iguales hasta el ruido de coma flotante. Una tolerancia
# amplia escondería exactamente lo que la ventana existe para detectar.
#
# Nota de precisión REAL: estos campos se sellan ya redondeados (beta y
# apertura a 2 decimales, R² a 4). Sobre valores redondeados una tolerancia
# relativa de 1e-9 equivale a exigir el MISMO valor almacenado. Es más
# estricto de lo que suena, y está bien que lo sea: la diferencia más
# pequeña representable en beta es 0.01, que no es ruido de float sino
# insumos distintos. La contracara honesta: un valor que caiga justo en el
# borde del redondeo podría inclinarse a un lado en una máquina y al otro
# en la otra. Por eso todo hallazgo de nivel 1 reporta ambos valores y su
# delta — un delta de exactamente una unidad del último decimal merece
# mirarse antes de tratarlo como evidencia dura, pero se reporta igual:
# jamás se silencia.
TOLERANCIA_RELATIVA = 1e-9

# NIVEL 1 — identidad numérica. Una diferencia mayor NO es ruido: es
# evidencia de que los insumos difieren. Se reporta como HALLAZGO.
NIVEL1_SNAPSHOT = ["sox_usado_pct"]
NIVEL1_TICKER = ["apertura_estimada_pct", "confianza_r2", "beta",
                 "intervalo80_pp", "puntaje_v0"]
# Los extremos del intervalo del 80% son apertura_estimada_pct ±
# intervalo80_pp (intervalo80_pp es el ± , no el ancho total: motor.py Z80).
# Comparar ambos constituyentes al nivel 1 ES comparar los extremos, sin
# reimplementar aquí una fórmula que vive en el motor.

# NIVEL 2 — igualdad exacta.
NIVEL2_SNAPSHOT = ["regimen", "roca_chip", "modelo_version", "feature_version",
                   "universo_version", "ventana_betas", "descarga_ok",
                   "descarga_total", "descarga_caidos", "sox_fecha"]
NIVEL2_TICKER = ["exchange", "sesion_objetivo", "available_at",
                 "modelo_version", "n_muestra"]

# NIVEL 3 — diferencia legítima ESPERADA. No cuenta como divergencia; se
# reporta aparte, informativa.
#   · plataforma_version: el Mac sella 5.0.2 y el PC 5.0.3. Registrado en
#     DECISIONES.md Etapa 5.0.3 §8: ese campo dejó de ser invariante de
#     validación y pasó a ser discriminador esperado durante la migración.
#   · timestamp_utc / creado_en: máquinas distintas sellan en segundos
#     distintos. Que difieran es lo normal; que coincidieran sería raro.
#   · origen: cómo se disparó la corrida (programado/manual/dashboard).
#   · estado: lo escribe el verificador DESPUÉS, en cada máquina por su
#     cuenta y en momentos distintos. Comparar estado sería comparar
#     relojes de verificación, no sellos.
#   · sentimiento_ia / puntaje_ia: dependen de las noticias, y los feeds RSS
#     responden distinto a las 17:50 en cada máquina.
NIVEL3_SNAPSHOT = ["plataforma_version", "timestamp_utc", "creado_en", "origen"]
NIVEL3_TICKER = ["timestamp_utc", "estado", "sentimiento_ia", "puntaje_ia"]
# (plataforma_version vive solo en `snapshots`, no en `senales_ticker`.)

# `id` es el rowid de SQLite: numeración local de cada máquina, sin
# significado compartido. Se excluye por completo de toda comparación.
EXCLUIDOS = ["id"]

VEREDICTO_PARIDAD = "PARIDAD"
VEREDICTO_DIVERGENCIA = "DIVERGENCIA"
VEREDICTO_NO_COMPUTABLE = "DIA_NO_COMPUTABLE"
VEREDICTO_PENDIENTE = "PENDIENTE_PUBLICACION"

# ------------------------------------------------------------
# CHEQUEO ESTRUCTURAL DE BASE COPIADA — cinturón y tirantes
# ------------------------------------------------------------
# La FECHA_CORTE es una constante que alguien tiene que acordarse de subir
# si las bases se vuelven a copiar del Mac. Depender de la memoria humana
# para el chequeo que evita la paridad falsa es exactamente el punto débil
# equivocado, así que hay además una defensa que no depende de nadie.
#
# Dos filas selladas INDEPENDIENTEMENTE en dos máquinas jamás comparten
# `creado_en` ni `timestamp_utc`: son marcas de tiempo con precisión de
# microsegundos, tomadas por procesos distintos en momentos distintos. Que
# coincidan al microsegundo no es coincidencia: es la MISMA fila copiada.
#
# Se exige que coincidan los tres campos (los dos timestamps y
# `plataforma_version`) para declararlo. Durante la ventana real el Mac
# sella 5.0.2 y el PC 5.0.3, así que la tercera condición sola ya impide el
# falso positivo; los timestamps solos ya bastarían. Se piden los tres para
# que la negativa sea inapelable cuando se dispara.
#
# Cinturón y tirantes: si CUALQUIERA de los dos mecanismos se dispara —la
# fecha de corte o esta huella— el comparador se niega.
CAMPOS_HUELLA_COPIA = ["creado_en", "timestamp_utc", "plataforma_version"]


# ------------------------------------------------------------
# Lectura de los dos lados
# ------------------------------------------------------------
def _git(*args, check: bool = False) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", DIRECTORIO, *args],
                       capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)} falló: {r.stderr.strip()}")
    return r


def fetch_titular() -> tuple:
    """`git fetch` — NUNCA pull. Devuelve (ok, detalle)."""
    r = _git("fetch", "origin", "--quiet")
    if r.returncode:
        return False, f"git fetch falló: {r.stderr.strip()}"
    return True, "fetch ok"


def rev_titular() -> str | None:
    r = _git("rev-parse", REV_TITULAR)
    return r.stdout.strip() if r.returncode == 0 else None


def leer_csv_titular(archivo: str, rev: str = REV_TITULAR) -> pd.DataFrame | None:
    """Lee data/backups/<archivo> desde el rev del titular SIN tocar el árbol."""
    r = _git("show", f"{rev}:data/backups/{archivo}")
    if r.returncode or not r.stdout.strip():
        return None
    return pd.read_csv(io.StringIO(r.stdout))


def leer_tabla_local(tabla: str, fecha: str) -> pd.DataFrame:
    """Lee la tabla local en modo SOLO LECTURA (no puede escribir ni migrar)."""
    ruta = os.path.join(DIRECTORIO, "senales.db")
    conn = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    try:
        return pd.read_sql_query(
            f"SELECT * FROM {tabla} WHERE fecha = ?", conn, params=(fecha,))
    finally:
        conn.close()


# ------------------------------------------------------------
# Comparadores
# ------------------------------------------------------------
def _falta(v) -> bool:
    return v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NA


def _igual_exacto(a, b) -> bool:
    """Igualdad exacta tolerante SOLO a la representación (int64 vs float64
    tras el ida y vuelta por CSV), nunca al valor. Dos ausencias son iguales."""
    if _falta(a) and _falta(b):
        return True
    if _falta(a) or _falta(b):
        return False
    try:
        fa, fb = float(a), float(b)
        return fa == fb
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def _identidad_numerica(a, b) -> tuple:
    """(iguales, delta). Tolerancia relativa TOLERANCIA_RELATIVA."""
    if _falta(a) and _falta(b):
        return True, 0.0
    if _falta(a) or _falta(b):
        return False, None
    try:
        fa, fb = float(a), float(b)
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip(), None
    delta = abs(fa - fb)
    escala = max(abs(fa), abs(fb))
    if escala == 0:
        return delta == 0, delta
    return (delta / escala) <= TOLERANCIA_RELATIVA, delta


def _hallazgo(nivel, ambito, clave, campo, val_titular, val_sombra, delta=None):
    h = {"nivel": nivel, "ambito": ambito, "clave": clave, "campo": campo,
         "titular": None if _falta(val_titular) else str(val_titular),
         "sombra": None if _falta(val_sombra) else str(val_sombra)}
    if delta is not None:
        h["delta"] = delta
    return h


def comparar_fecha(fecha: str, snaps_titular: pd.DataFrame,
                   tickers_titular: pd.DataFrame,
                   fecha_corte: date | None = FECHA_CORTE) -> dict:
    """Compara UN día. Devuelve el dicho completo: veredicto, motivo,
    hallazgos (niveles 1 y 2) y diferencias esperadas (nivel 3).

    `fecha_corte` es aditivo (docs/REPLICA.md §4): por defecto es
    `FECHA_CORTE`, así que ningún llamador existente (el CLI de este
    archivo, ni ningún test) cambia de comportamiento. Un llamador nuevo
    puede pasar `fecha_corte=None` para apoyarse ÚNICAMENTE en la defensa
    estructural (huella de base copiada, más abajo) — pensado para un uso
    de réplica permanente donde una constante de fecha fija ya no tiene
    sentido (no hay "un" corte, hay overlap todos los días). Retirar
    `FECHA_CORTE` como comportamiento POR DEFECTO del comparador sigue sin
    implementarse a propósito: docs/REPLICA.md §5 lo marca explícitamente
    como decisión de Nicolás, no de este cambio."""
    res = {"fecha": fecha, "hallazgos": [], "esperadas": [], "notas": []}

    # --- B.1: la fecha de corte manda sobre todo lo demás (si se pide) ---
    if fecha_corte is not None and date.fromisoformat(fecha) <= fecha_corte:
        res["veredicto"] = VEREDICTO_NO_COMPUTABLE
        res["motivo"] = (
            f"fecha <= FECHA_CORTE ({fecha_corte.isoformat()}): las bases del PC "
            "son copia de las del Mac hasta ese día inclusive, así que ambas "
            "máquinas tienen el MISMO archivo. La paridad sería trivial y no "
            "constituye evidencia. Comparación rechazada a propósito.")
        return res

    snap_t = snaps_titular[snaps_titular["fecha"] == fecha]
    snap_s = leer_tabla_local("snapshots", fecha)

    # --- B.3: "nada = nada" NUNCA es paridad ---
    if snap_t.empty:
        # La ausencia en origin/main es AMBIGUA: o el titular no selló, o
        # selló y todavía no pusheó (el push del Mac es manual y va después
        # de las 20:30). Tratarla como día perdido quemaría un día de la
        # ventana en silencio por un push que aún no llegó.
        #
        # Se desambigua sin reloj: si el titular ya publicó algún sello de
        # una fecha POSTERIOR, su historia está publicada más allá de este
        # día y la ausencia deja de ser ambigua — es definitiva.
        publico_mas_alla = bool(
            (snaps_titular["fecha"].astype(str) > fecha).any())
        if not publico_mas_alla:
            res["veredicto"] = VEREDICTO_PENDIENTE
            res["motivo"] = (
                "no hay fila del titular en origin/main para esta fecha, y "
                "tampoco hay sellos suyos de fechas posteriores: no se puede "
                "distinguir 'no selló' de 'selló y aún no pusheó'. NO es un "
                "día perdido — vuelve a correr después del push del Mac "
                "(manual, tras las 20:30) y el día se resuelve de verdad.")
            return res
        if snap_s.empty:
            res["veredicto"] = VEREDICTO_NO_COMPUTABLE
            res["motivo"] = (
                "el titular publicó sellos de fechas posteriores pero ninguno "
                "de esta, así que la ausencia es DEFINITIVA: no selló. Y la "
                "sombra tampoco. Sin sello del titular no hay contra qué "
                "comparar: día PERDIDO, no día bueno.")
            return res
        res["veredicto"] = VEREDICTO_NO_COMPUTABLE
        res["motivo"] = (
            "el titular publicó sellos de fechas posteriores pero ninguno de "
            "esta, así que la ausencia es DEFINITIVA: el TITULAR no selló. Un "
            "día solo cuenta si el titular selló de verdad esa noche.")
        return res
    if snap_s.empty:
        res["veredicto"] = VEREDICTO_DIVERGENCIA
        res["motivo"] = ("el titular selló y la SOMBRA no. No es un día no "
                         "computable: es la sombra fallando, que es justo lo "
                         "que la ventana existe para detectar.")
        return res

    st = snap_t.iloc[0].to_dict()
    ss = snap_s.iloc[0].to_dict()

    # --- B.1 bis: huella de base copiada (ver CAMPOS_HUELLA_COPIA) ---
    presentes = [c for c in CAMPOS_HUELLA_COPIA if c in st and c in ss]
    if len(presentes) == len(CAMPOS_HUELLA_COPIA) and all(
            _igual_exacto(st[c], ss[c]) for c in presentes):
        res["veredicto"] = VEREDICTO_NO_COMPUTABLE
        res["motivo"] = (
            "las dos filas coinciden en "
            + ", ".join(CAMPOS_HUELLA_COPIA)
            + ". Dos máquinas que sellan por separado NO comparten marcas de "
              "tiempo con precisión de microsegundos: esto no es paridad, es "
              "la MISMA fila copiada. Comparación rechazada. Si las bases se "
              f"recopiaron del Mac, sube FECHA_CORTE (hoy {FECHA_CORTE.isoformat()}) "
              "al nuevo día de copia.")
        return res

    # Una columna presente en una máquina y ausente en la otra es una
    # diferencia de ESQUEMA, no de valor: se reporta como tal en vez de
    # dejar que `.get()` devuelva None y parezca un valor distinto.
    for campo in NIVEL1_SNAPSHOT + NIVEL2_SNAPSHOT:
        if (campo in st) != (campo in ss):
            res["hallazgos"].append(
                _hallazgo(2, "esquema", fecha, campo,
                          "presente" if campo in st else "AUSENTE",
                          "presente" if campo in ss else "AUSENTE"))

    for campo in NIVEL1_SNAPSHOT:
        if campo not in st or campo not in ss:
            continue
        ok, delta = _identidad_numerica(st.get(campo), ss.get(campo))
        if not ok:
            res["hallazgos"].append(
                _hallazgo(1, "snapshot", fecha, campo, st.get(campo),
                          ss.get(campo), delta))
    for campo in NIVEL2_SNAPSHOT:
        if campo not in st or campo not in ss:
            continue
        if not _igual_exacto(st.get(campo), ss.get(campo)):
            res["hallazgos"].append(
                _hallazgo(2, "snapshot", fecha, campo, st.get(campo), ss.get(campo)))
    for campo in NIVEL3_SNAPSHOT:
        if not _igual_exacto(st.get(campo), ss.get(campo)):
            res["esperadas"].append(
                _hallazgo(3, "snapshot", fecha, campo, st.get(campo), ss.get(campo)))

    # --- tickers ---
    tt = tickers_titular[tickers_titular["fecha"] == fecha]
    ts = leer_tabla_local("senales_ticker", fecha)

    set_t, set_s = set(tt["ticker"]), set(ts["ticker"])
    if set_t != set_s:
        res["hallazgos"].append(
            _hallazgo(2, "conjunto", fecha, "tickers_sellados",
                      f"{len(set_t)} tickers", f"{len(set_s)} tickers"))
        for falta in sorted(set_t - set_s):
            res["hallazgos"].append(
                _hallazgo(2, "conjunto", fecha, "ticker_ausente_en_sombra",
                          falta, None))
        for sobra in sorted(set_s - set_t):
            res["hallazgos"].append(
                _hallazgo(2, "conjunto", fecha, "ticker_ausente_en_titular",
                          None, sobra))

    n_pred_t = int(tt["apertura_estimada_pct"].notna().sum())
    n_pred_s = int(ts["apertura_estimada_pct"].notna().sum())
    if n_pred_t != n_pred_s:
        res["hallazgos"].append(
            _hallazgo(2, "conjunto", fecha, "numero_de_predicciones",
                      n_pred_t, n_pred_s))
    if len(tt) != len(ts):
        res["hallazgos"].append(
            _hallazgo(2, "conjunto", fecha, "filas_selladas", len(tt), len(ts)))

    tt_i = tt.set_index("ticker")
    ts_i = ts.set_index("ticker")
    for ticker in sorted(set_t & set_s):
        ft, fs = tt_i.loc[ticker], ts_i.loc[ticker]
        if isinstance(ft, pd.DataFrame):
            ft, fs = ft.iloc[0], ts_i.loc[ticker].iloc[0]
        for campo in NIVEL1_TICKER:
            if campo not in ft.index or campo not in fs.index:
                res["hallazgos"].append(
                    _hallazgo(2, "esquema", ticker, campo,
                              "presente" if campo in ft.index else "AUSENTE",
                              "presente" if campo in fs.index else "AUSENTE"))
                continue
            ok, delta = _identidad_numerica(ft.get(campo), fs.get(campo))
            if not ok:
                res["hallazgos"].append(
                    _hallazgo(1, "ticker", ticker, campo, ft.get(campo),
                              fs.get(campo), delta))
        for campo in NIVEL2_TICKER:
            if campo not in ft.index or campo not in fs.index:
                continue
            if not _igual_exacto(ft.get(campo), fs.get(campo)):
                res["hallazgos"].append(
                    _hallazgo(2, "ticker", ticker, campo, ft.get(campo), fs.get(campo)))
        for campo in NIVEL3_TICKER:
            if campo in ft.index and not _igual_exacto(ft.get(campo), fs.get(campo)):
                res["esperadas"].append(
                    _hallazgo(3, "ticker", ticker, campo, ft.get(campo), fs.get(campo)))

    res["veredicto"] = VEREDICTO_PARIDAD if not res["hallazgos"] else VEREDICTO_DIVERGENCIA
    res["motivo"] = ("todos los campos de nivel 1 y 2 coinciden"
                     if not res["hallazgos"]
                     else f"{len(res['hallazgos'])} hallazgo(s) de nivel 1 o 2")
    return res


# ------------------------------------------------------------
# Salida: un reporte que se pueda releer en tres semanas
# ------------------------------------------------------------
def componer_reporte(res: dict, rev: str | None, hubo_fetch: bool) -> str:
    f = res["fecha"]
    L = [f"# Comparación de sombra — {f}", "",
         f"- **Veredicto: {res['veredicto']}**",
         f"- Motivo: {res['motivo']}",
         f"- Generado: {datetime.now(timezone.utc).isoformat()}",
         f"- Titular: `{REV_TITULAR}` = `{rev or '(no resuelto)'}`"
         + ("" if hubo_fetch else "  ⚠ sin `git fetch` (--sin-fetch)"),
         "- Sombra: `senales.db` local, abierta en `mode=ro`",
         f"- Fecha de corte: {FECHA_CORTE.isoformat()} "
         "(fechas <= corte se rechazan: bases idénticas por construcción)",
         "",
         "## Criterio aplicado", "",
         f"| Nivel | Regla | Campos |", "|---|---|---|",
         f"| 1 | identidad numérica, tolerancia relativa {TOLERANCIA_RELATIVA:g} | "
         f"snapshot: {', '.join(NIVEL1_SNAPSHOT)} · ticker: {', '.join(NIVEL1_TICKER)} |",
         f"| 2 | igualdad exacta | snapshot: {', '.join(NIVEL2_SNAPSHOT)} · "
         f"ticker: {', '.join(NIVEL2_TICKER)} · conjunto de tickers · "
         "nº de predicciones · filas selladas |",
         f"| 3 | diferencia legítima esperada, fuera del veredicto | "
         f"snapshot: {', '.join(NIVEL3_SNAPSHOT)} · ticker: {', '.join(NIVEL3_TICKER)} |",
         "",
         "Los extremos del intervalo del 80% son `apertura_estimada_pct ± "
         "intervalo80_pp`; ambos van al nivel 1, así que comparar los dos ES "
         "comparar los extremos.",
         f"Excluidos por completo: {', '.join(EXCLUIDOS)} (rowid local, sin "
         "significado compartido).", ""]

    if res["veredicto"] in (VEREDICTO_NO_COMPUTABLE, VEREDICTO_PENDIENTE):
        L += ["## Sin comparación", "", res["motivo"], ""]
        if res["veredicto"] == VEREDICTO_PENDIENTE:
            L += ["", "**Este día NO está cerrado.** Vuelve a correr el "
                  "comparador para esta fecha después del push del Mac; el "
                  "veredicto de un día pendiente se sobrescribe con el "
                  "definitivo (el contador usa la última corrida de cada "
                  "fecha).", ""]
    else:
        L += [f"## Hallazgos de nivel 1 y 2 — {len(res['hallazgos'])}", ""]
        if not res["hallazgos"]:
            L += ["Ninguno.", ""]
        else:
            L += ["| Nivel | Ámbito | Clave | Campo | Titular | Sombra | Delta |",
                  "|---|---|---|---|---|---|---|"]
            for h in res["hallazgos"]:
                d = f"{h['delta']:.10g}" if h.get("delta") is not None else ""
                L.append(f"| {h['nivel']} | {h['ambito']} | {h['clave']} | "
                         f"{h['campo']} | {h['titular']} | {h['sombra']} | {d} |")
            L.append("")

    L += [f"## Diferencias esperadas (nivel 3, informativas) — {len(res['esperadas'])}",
          "", "No cuentan para el veredicto.", ""]
    if res["esperadas"]:
        L += ["| Ámbito | Clave | Campo | Titular | Sombra |", "|---|---|---|---|---|"]
        for h in res["esperadas"][:200]:
            L.append(f"| {h['ambito']} | {h['clave']} | {h['campo']} | "
                     f"{h['titular']} | {h['sombra']} |")
        if len(res["esperadas"]) > 200:
            L.append(f"| … | … | (+{len(res['esperadas']) - 200} más, no listadas) | | |")
        L.append("")
    return "\n".join(L) + "\n"


def registrar_veredicto(res: dict, rev: str | None) -> None:
    os.makedirs(DIR_SALIDA, exist_ok=True)
    fila = {"ts": datetime.now(timezone.utc).isoformat(), "fecha": res["fecha"],
            "veredicto": res["veredicto"], "motivo": res["motivo"],
            "hallazgos": len(res["hallazgos"]), "esperadas": len(res["esperadas"]),
            "rev_titular": rev}
    with open(RUTA_VEREDICTOS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(fila, ensure_ascii=False) + "\n")


def contador() -> str:
    """Progreso de la ventana. Un DIA_NO_COMPUTABLE es un día PERDIDO: no
    suma ni rompe la racha (no es evidencia ni en contra ni a favor). Una
    DIVERGENCIA la vuelve a cero — así lo hizo el día 1 del 14-ago."""
    if not os.path.exists(RUTA_VEREDICTOS):
        return "Sin comparaciones registradas todavía."
    ultimo_por_fecha = {}
    with open(RUTA_VEREDICTOS, encoding="utf-8") as fh:
        for linea in fh:
            try:
                d = json.loads(linea)
            except json.JSONDecodeError:
                continue
            ultimo_por_fecha[d["fecha"]] = d  # la última corrida de esa fecha manda
    L = ["Progreso de la ventana de sombra (3 días hábiles con paridad):", ""]
    racha = 0
    pendientes = []
    for f in sorted(ultimo_por_fecha):
        v = ultimo_por_fecha[f]["veredicto"]
        if v == VEREDICTO_PARIDAD:
            racha += 1
        elif v == VEREDICTO_DIVERGENCIA:
            racha = 0
        if v == VEREDICTO_PENDIENTE:
            pendientes.append(f)
            L.append(f"  {f}  {v}  ← sin cerrar, re-ejecutable")
        else:
            L.append(f"  {f}  {v}")
    paridades = sum(1 for d in ultimo_por_fecha.values()
                    if d["veredicto"] == VEREDICTO_PARIDAD)
    L += ["", f"  días con PARIDAD: {paridades}",
          f"  racha actual: {racha}/3"]
    if pendientes:
        L += ["",
              f"  {len(pendientes)} día(s) SIN CERRAR a la espera del push del Mac:",
              "    " + ", ".join(pendientes),
              "    vuelve a correr:  python comparar_sombra.py --fecha "
              + pendientes[0]]
    L += ["", "  (PARIDAD suma. DIVERGENCIA vuelve la racha a cero.",
          "   DIA_NO_COMPUTABLE no suma ni rompe: es día perdido, y es FINAL.",
          "   PENDIENTE_PUBLICACION tampoco suma ni rompe, pero NO es final:",
          "   se resuelve re-ejecutando cuando llegue el push.)"]
    return "\n".join(L)


# ------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Compara los sellos del titular y la sombra.")
    ap.add_argument("--fecha", help="fecha a comparar (YYYY-MM-DD; por defecto HOY)")
    ap.add_argument("--desde", help="inicio de un rango")
    ap.add_argument("--hasta", help="fin de un rango")
    ap.add_argument("--sin-fetch", action="store_true",
                    help="no toca la red; usa el origin/main ya descargado")
    ap.add_argument("--contador", action="store_true",
                    help="muestra el progreso de la ventana y sale")
    args = ap.parse_args(argv)

    if args.contador:
        print(contador())
        return 0

    if args.desde or args.hasta:
        if not (args.desde and args.hasta):
            print("--desde y --hasta van juntos.", file=sys.stderr)
            return 2
        fechas = [d.date().isoformat() for d in
                  pd.date_range(args.desde, args.hasta, freq="D")]
    else:
        fechas = [args.fecha or date.today().isoformat()]

    hubo_fetch = False
    if not args.sin_fetch:
        ok, detalle = fetch_titular()
        hubo_fetch = ok
        if not ok:
            print(f"AVISO: {detalle}")
            print("  Se sigue con el origin/main que ya estaba descargado; el "
                  "reporte lo deja anotado.")
    rev = rev_titular()
    if rev is None:
        print(f"ERROR: no se pudo resolver {REV_TITULAR}. ¿Hay remoto configurado?",
              file=sys.stderr)
        return 1

    snaps = leer_csv_titular("senales_snapshots.csv")
    tickers = leer_csv_titular("senales_senales_ticker.csv")
    if snaps is None or tickers is None:
        print(f"ERROR: no se pudieron leer los CSV del titular en {REV_TITULAR}.",
              file=sys.stderr)
        return 1

    os.makedirs(DIR_SALIDA, exist_ok=True)
    salida = 0
    for f in fechas:
        res = comparar_fecha(f, snaps, tickers)
        reporte = componer_reporte(res, rev, hubo_fetch)
        destino = os.path.join(DIR_SALIDA, f"comparacion_{f}.md")
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(reporte)
        registrar_veredicto(res, rev)
        print(f"{f}  {res['veredicto']}  — {res['motivo']}")
        print(f"        reporte: {os.path.relpath(destino, DIRECTORIO)}")
        if res["veredicto"] == VEREDICTO_PENDIENTE:
            print("        → día SIN CERRAR: vuelve a correr esta fecha "
                  "después del push del Mac.")
        if res["veredicto"] == VEREDICTO_DIVERGENCIA:
            salida = 1
    return salida


if __name__ == "__main__":
    sys.exit(main())
