# ============================================================
# dinero/senal_larga_reporte.py — mide y publica la señal larga v1.
#
#   python -m dinero.senal_larga_reporte
#
# Las tres especificaciones estaban declaradas por nombre en
# GEMELO/preregistro/senal_larga_v1.md, commiteado ANTES que el cómputo. Se
# reportan LAS TRES y los DOS horizontes, sin elegir el que salió mejor: la
# agregación es sobre todos los pares adyacentes de la cadena, declarada por
# adelantado en el §3 del pre-registro.
#
# Las dos métricas —magnitud y dirección— se reportan con la misma firmeza y
# esta corrida NO elige cuál es primaria: la enmienda V1-bis que lo decide
# está esperando la firma de Nicolás (espera_firma.md §30).
#
# Intervalos: bootstrap circular de bloques sobre FECHAS DE EMISIÓN, con
# bloque igual al horizonte. Las etiquetas de h días se solapan, así que dos
# fechas a menos de h días comparten casi toda su ventana; tratarlas como
# independientes angostaría el intervalo hasta volverlo mentira.
#
# ------------------------------------------------------------
# ENMIENDA DEL 7-SEP-2026 — dictámenes de cierre de la corrida 10
# ------------------------------------------------------------
# La primera versión de este reporte publicaba «sobrevive una celda de seis»
# sin corregir por multiplicidad y sin la ablación que el pre-registro del
# riel exige. Esa lectura está RETIRADA (`GEMELO/cifras_retiradas.md`,
# 7-sep-2026). Los dictámenes de cierre (`GEMELO/resultados/dictamen_10/`)
# mostraron que las dos cosas dan vuelta la lectura, así que el reporte
# ahora las COMPUTA él mismo en vez de que las compute un dictamen:
#
#   - `multiplicidad()`  — Holm sobre la familia COMPLETA de contrastes.
#     La familia son 30, no 24: `medir()` produce cinco intervalos por
#     celda y la cuenta vieja dejaba los seis de dirección afuera de su
#     propia corrección (exigencias 8 y 9 del `estadistico-adversario`).
#   - `ablacion_anual()` — saca un año calendario del período de prueba a
#     la vez, que es la forma exacta del R2 que el pre-registro del riel
#     exige antes de que un positivo cuente (exigencia 14).
#   - b, c y McNemar exacto en toda métrica de dirección (exigencia 11), y
#     los bloques efectivos del bootstrap (exigencia 13).
#
# Las tres se publican SIEMPRE, salga lo que salga, y no sólo cuando hay
# algo que celebrar: ésa es la única forma en que una corrección de
# multiplicidad significa algo.
# ============================================================
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude", "skills", "estadistica-evaluacion", "scripts"))
import evaluacion as ev  # noqa: E402

from backtest import inferencia
from GEMELO.control_lineal import crps_normal
from dinero import registro_intentos
from dinero import senal_larga as S

DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados")
SALIDA = os.path.join(DIR_RESULTADOS, "senal_larga_v1.md")
SALIDA_JSON = os.path.join(DIR_RESULTADOS, "senal_larga_v1.json")
SEMILLA = 20260907
REPLICAS = 2000
ALPHA = 0.05


def _ic_por_fecha(valores_por_fila: np.ndarray, fechas: np.ndarray,
                  bloque: int) -> dict:
    """Promedia por fecha de emisión y saca el IC de la media con bootstrap
    circular de bloques sobre esas fechas."""
    s = pd.Series(valores_por_fila, index=pd.to_datetime(fechas))
    por_fecha = s.groupby(s.index).mean().sort_index()
    ic = inferencia.bootstrap_media(por_fecha.to_numpy(), semilla=SEMILLA,
                                    n_draws=REPLICAS, bloque=bloque,
                                    alpha=ALPHA)
    ic["fechas"] = int(len(por_fecha))
    return ic


def medir(res: pd.DataFrame, h: int) -> dict:
    """De las predicciones walk-forward a las métricas del pre-registro."""
    if res.empty:
        return {"vacio": True}
    pred = res["pred"].to_numpy()
    real = res["real"].to_numpy()
    sigma = res["sigma"].to_numpy()
    sigma0 = res["sigma_cero"].to_numpy()
    clima = res["clima"].to_numpy()
    fechas = res["fecha"].to_numpy()

    ae_modelo = np.abs(pred - real)
    ae_cero = np.abs(real)
    crps_modelo = crps_normal(real, pred, sigma)
    crps_cero = crps_normal(real, np.zeros_like(real), sigma0)
    clima_media = res["clima_media"].to_numpy()
    ae_clima = np.abs(real - clima_media)
    crps_clima = crps_normal(real, clima_media, res["sigma_clima"].to_numpy())
    # Dirección: se EXCLUYEN las filas con retorno real exactamente cero.
    # `sign(0) == sign(0)` contaba como acierto y regalaba puntos a los dos
    # lados; el proyecto ya congeló esta convención por el mismo artefacto
    # (GEMELO/DISEÑO.md §2.8, `excluir_cero`).
    no_cero = real != 0.0
    acierto = (np.sign(pred) == np.sign(real)).astype(float)
    # Climatología causal: predecir siempre el signo mayoritario del ajuste.
    signo_clima = np.where(clima >= 0.5, 1.0, -1.0)
    acierto_clima = (signo_clima == np.sign(real)).astype(float)

    out = {
        "vacio": False,
        "filas": int(len(res)),
        "pares": int(res["par"].nunique()),
        "mae_modelo_pp": float(np.mean(ae_modelo) * 100.0),
        "mae_cero_pp": float(np.mean(ae_cero) * 100.0),
        "crps_modelo": float(np.mean(crps_modelo) * 100.0),
        "crps_cero": float(np.mean(crps_cero) * 100.0),
        "mae_clima_pp": float(np.mean(ae_clima) * 100.0),
        "crps_clima": float(np.mean(crps_clima) * 100.0),
        "clima_media_pp": float(np.mean(clima_media) * 100.0),
        "pred_sd_pp": float(np.std(pred, ddof=1) * 100.0),
        "pred_cambia_de_signo": bool(len(np.unique(np.sign(pred))) > 1),
        "acierto_pct": float(np.mean(acierto[no_cero]) * 100.0),
        "clima_pct": float(np.mean(acierto_clima[no_cero]) * 100.0),
        "filas_direccion": int(no_cero.sum()),
        "n_ajuste": int(res["n_ajuste"].iloc[0]),
        "corte_ajuste": str(res["corte_ajuste"].iloc[0]),
        "pendiente": float(res["b"].iloc[0]),
    }
    # Ganancias, con su intervalo de clúster de fecha.
    out["ic_mae"] = _ic_por_fecha((ae_cero - ae_modelo) * 100.0, fechas, h)
    out["ic_crps"] = _ic_por_fecha((crps_cero - crps_modelo) * 100.0,
                                   fechas, h)
    out["ic_mae_clima"] = _ic_por_fecha((ae_clima - ae_modelo) * 100.0, fechas, h)
    out["ic_crps_clima"] = _ic_por_fecha((crps_clima - crps_modelo) * 100.0,
                                         fechas, h)
    out["ic_dir"] = _ic_por_fecha(
        ((acierto - acierto_clima) * 100.0)[no_cero], fechas[no_cero], h)

    # --- b, c y McNemar exacto de la direccion (exigencia 11) ---
    # Un p de FILAS al lado de un IC de fecha que contiene el cero es el
    # sintoma que el riel de medicion ya conoce: la fila miente porque las
    # filas de una misma fecha no son observaciones independientes. Se
    # publican los tres numeros juntos para que se vea el desacuerdo.
    a_mod = acierto[no_cero].astype(bool)
    a_cli = acierto_clima[no_cero].astype(bool)
    b_dis = int(np.sum(a_mod & ~a_cli))
    c_dis = int(np.sum(~a_mod & a_cli))
    out["dir_b"] = b_dis
    out["dir_c"] = c_dis
    out["dir_mcnemar_p"] = ev.mcnemar_exact(b_dis, c_dis)

    # --- bloques efectivos del bootstrap (exigencia 13) ---
    # A h = 60 quedan once bloques y pico, y toda la inferencia de la celda
    # que la v1 llamo superviviente descansaba sobre esos once.
    out["bloques_efectivos"] = float(out["ic_mae"]["fechas"]) / float(h)

    # --- p bilateral por contraste, mismo sorteo que el intervalo ---
    def _p(v, f):
        s_ = pd.Series(v, index=pd.to_datetime(f))
        por_fecha = s_.groupby(s_.index).mean().sort_index()
        return inferencia.p_bootstrap_media(por_fecha.to_numpy(),
                                            semilla=SEMILLA,
                                            n_draws=REPLICAS, bloque=h)
    out["p_mae"] = _p((ae_cero - ae_modelo) * 100.0, fechas)
    out["p_crps"] = _p((crps_cero - crps_modelo) * 100.0, fechas)
    out["p_mae_clima"] = _p((ae_clima - ae_modelo) * 100.0, fechas)
    out["p_crps_clima"] = _p((crps_clima - crps_modelo) * 100.0, fechas)
    out["p_dir"] = _p(((acierto - acierto_clima) * 100.0)[no_cero],
                      fechas[no_cero])
    return out


# ============================================================
# CONTRASTES: la familia entera, nombrada. Son 30, no 24.
# ============================================================
CONTRASTES = (
    ("MAE vs cero", "ic_mae", "p_mae"),
    ("CRPS vs cero", "ic_crps", "p_crps"),
    ("MAE vs climatologia", "ic_mae_clima", "p_mae_clima"),
    ("CRPS vs climatologia", "ic_crps_clima", "p_crps_clima"),
    ("direccion vs climatologia", "ic_dir", "p_dir"),
)


def multiplicidad(todo: dict) -> dict:
    """Holm sobre la familia COMPLETA de contrastes de esta pagina.

    La familia no la elige este codigo: la define el pre-registro §3, que
    declara tres especificaciones por dos horizontes, y `medir()` produce
    cinco contrastes por celda. Son 30. La lectura RETIRADA de la v1
    —«una celda de seis gana»— es la forma mas comun de encontrar algo
    donde no hay nada: publicar el maximo de una familia sin corregirla.
    """
    crudos = {}
    for (espec, h), m in sorted(todo.items()):
        if m["vacio"]:
            continue
        for etiqueta, _clave_ic, clave_p in CONTRASTES:
            p = m[clave_p]
            if p != p:      # NaN: contraste sin muestra
                continue
            crudos["%s h=%d %s" % (espec, h, etiqueta)] = float(p)
    ajustados = inferencia.holm(crudos)
    pasan = sorted(n for n, p in ajustados.items() if p < ALPHA)
    return {"familia": len(crudos), "p_crudo": crudos,
            "p_holm": ajustados, "pasan": pasan, "alpha": ALPHA}


def ablacion_anual(res, h: int, ganancia_por_fila) -> dict:
    """Saca un ano calendario del periodo de prueba a la vez y recomputa.

    Es la forma exacta del R2 de `GEMELO/DISENO.md`, que en el riel de
    medicion ya golpeo al campeon: si la ventaja cabalga una ventana, sacar
    esa ventana la hace desaparecer. `dinero/preregistro_dinero.md` la exige
    antes de que un positivo cuente, y la v1 de este reporte admitia no
    haberla corrido.
    """
    fechas = pd.to_datetime(res["fecha"].to_numpy())
    ganancia = np.asarray(ganancia_por_fila, dtype=float)
    anos = sorted({int(f.year) for f in fechas})
    salida = {}
    for ano in anos:
        fuera = np.array([f.year != ano for f in fechas])
        dentro = ~fuera
        if int(fuera.sum()) < h:
            salida[str(ano)] = {"sin_muestra": True}
            continue
        ic = _ic_por_fecha(ganancia[fuera], fechas[fuera].to_numpy(), h)
        s_ = pd.Series(ganancia[dentro], index=fechas[dentro])
        solo = s_.groupby(s_.index).mean()
        salida[str(ano)] = {
            "sin_ese_ano": {"media": ic["media"], "lo": ic["lo"],
                            "hi": ic["hi"], "fechas": ic["fechas"],
                            "cruza_cero": _cruza(ic)},
            "solo_ese_ano": {"media": float(solo.mean()),
                             "fechas": int(len(solo))},
        }
    return salida


def _cruza(ic) -> bool:
    return bool(np.isnan(ic["lo"]) or ic["lo"] <= 0.0 <= ic["hi"])


def correr() -> dict:
    cierres = S.cargar_cierres()
    todo = {}
    for h in S.HORIZONTES:
        paneles = S.construir_paneles(cierres, h)
        for espec in S.ESPECIFICACIONES:
            res = S.evaluar(paneles[espec], espec, h)
            m = medir(res, h)
            # La ablacion anual se corre para TODAS las celdas, no solo para
            # las que dan positivo. Correrla solo donde conviene seria elegir
            # la prueba mirando el tiro, que es exactamente lo que el R2
            # existe para impedir.
            if not m["vacio"]:
                real = res["real"].to_numpy()
                pred = res["pred"].to_numpy()
                clima_media = res["clima_media"].to_numpy()
                ganancia_clima = (np.abs(real - clima_media)
                                  - np.abs(pred - real)) * 100.0
                m["ablacion_mae_clima"] = ablacion_anual(res, h, ganancia_clima)
            todo[(espec, h)] = m
    return todo


def _fila(espec, h, m):
    if m["vacio"]:
        return f"| **{espec}** | {h} | — | — | — | — | — | sin datos suficientes |"
    def celda(ic, punto, unidad):
        marca = "" if _cruza(ic) else " ✓"
        return (f"{punto:+.3f} {unidad}<br>[{ic['lo']:+.3f}, {ic['hi']:+.3f}]{marca}")
    return (f"| **{espec}** | {h} | {m['filas']} filas / "
            f"{m['ic_mae']['fechas']} fechas | "
            f"{m['mae_modelo_pp']:.3f} vs {m['mae_cero_pp']:.3f} | "
            f"{celda(m['ic_mae'], m['mae_cero_pp'] - m['mae_modelo_pp'], 'pp')} | "
            f"{celda(m['ic_crps'], m['crps_cero'] - m['crps_modelo'], 'pp')} | "
            f"{m['acierto_pct']:.1f} % vs {m['clima_pct']:.1f} %<br>"
            f"({m['filas_direccion']} filas)"
            f"{'' if m['pred_cambia_de_signo'] else '<br>**signo constante**'} | "
            f"{celda(m['ic_dir'], m['acierto_pct'] - m['clima_pct'], 'pp')} |")


def _fila_clima(espec, h, m):
    if m["vacio"]:
        return f"| **{espec}** | {h} | — | — | — |"
    def celda(ic, punto, unidad):
        marca = "" if _cruza(ic) else (" ✓" if punto > 0 else " ✗")
        return (f"{punto:+.3f} {unidad}<br>[{ic['lo']:+.3f}, {ic['hi']:+.3f}]{marca}")
    return (f"| **{espec}** | {h} | {m['mae_modelo_pp']:.3f} vs "
            f"{m['mae_clima_pp']:.3f} ({m['clima_media_pp']:+.2f} pp) | "
            f"{celda(m['ic_mae_clima'], m['mae_clima_pp'] - m['mae_modelo_pp'], 'pp')} | "
            f"{celda(m['ic_crps_clima'], m['crps_clima'] - m['crps_modelo'], 'pp')} |")


def componer(todo: dict, mult: dict) -> str:
    L = []
    L.append("# Señal larga v1 — resultado\n")
    L.append("> **PROPUESTA hasta el dictamen de `estadistico-adversario`.** Ninguna")
    L.append("> cifra de esta página entra al README ni sostiene ninguna afirmación")
    L.append("> del proyecto. No hay ninguna fila SELLADA de este riel: el track")
    L.append("> record prospectivo es del riel de medición, no de éste.\n")
    L.append("Pre-registrado en `GEMELO/preregistro/senal_larga_v1.md`, **commiteado")
    L.append("antes del cómputo** (commit `e368dad`). Tres especificaciones declaradas")
    L.append("por nombre, dos horizontes, agregación sobre todos los pares adyacentes")
    L.append("de la cadena. Registro de intentos del riel largo: "
             f"**{registro_intentos.N_INTENTOS_RIEL_LARGO}**.\n")
    L.append(f"Generado {datetime.now(timezone.utc).strftime('%Y-%m-%d')} UTC por "
             "`python -m dinero.senal_larga_reporte`.\n")

    L.append("## Procedimiento\n")
    L.append(f"- Ajuste **{S.AJUSTE_DESDE} → {S.AJUSTE_HASTA}**, prueba "
             f"**{S.PRUEBA_DESDE} → {S.PRUEBA_HASTA}**, congelados antes de mirar.")
    L.append("- **Un solo ajuste y una sola evaluación**, no walk-forward "
             "expansivo:")
    L.append("  la auditoría mostró que el expansivo metía hasta el 36 % del último")
    L.append("  ajuste dentro del período de prueba mientras el reporte afirmaba lo")
    L.append("  contrario. Errata E2 del pre-registro, escrita antes de medir.")
    L.append(f"- Embargo: **{S.EMBARGO_DIAS} días MÁS el horizonte MÁS el retardo "
             f"de implementación**. Con etiquetas de *h* días solapadas, ajustar con")
    L.append("  un par cuya etiqueta llega más allá del inicio de la prueba es leer el")
    L.append("  futuro sin que ninguna guarda de «datos ≤ t» se queje.")
    L.append(f"- **Retardo de implementación: {S.RETARDO_IMPLEMENTACION} día.** Se")
    L.append("  decide con el cierre de *t* y se entra al cierre de *t+1*. El auditor")
    L.append("  midió que este día mueve la etiqueta 3,6–4,0 pp de media, del mismo")
    L.append("  orden que el umbral de señal del juego conservador (3,49 pp).")
    L.append("- Composición de los eslabones: por **cobertura ≥ 98 % del período de")
    L.append("  ajuste**, decidida al principio de la muestra. La v1 la decidía con el")
    L.append("  último precio del archivo y eso era fuga de selección demostrada")
    L.append("  (errata E1: cambiaba el 42,9 % de las filas del panel).")
    L.append("- Sólo `dinero/datos/cierres_congelados.csv`. **Ninguna descarga.**")
    L.append("- Intervalos: bootstrap circular de bloques sobre **fechas de emisión**,")
    L.append(f"  bloque = horizonte, {REPLICAS} réplicas, semilla {SEMILLA}, "
             f"α = {ALPHA}.")
    bloques = ", ".join(
        f"h={h}: **{todo[('L1', h)]['bloques_efectivos']:.1f} bloques**"
        for h in S.HORIZONTES if not todo[("L1", h)]["vacio"])
    L.append(f"- **Bloques efectivos del bootstrap** ({bloques}). Se declara porque")
    L.append("  un bootstrap de bloques con once bloques y pico no tiene la cobertura")
    L.append("  que su etiqueta del 95 % promete: medido sobre ruido iid con esta")
    L.append("  misma máquina, el ancho del intervalo varía entre 0,67 y 1,29 veces")
    L.append("  el que corresponde. Toda la inferencia a 60 días descansa sobre esos")
    L.append("  once bloques.\n")

    L.append("## Resultado\n")
    L.append("Las dos métricas van con **la misma firmeza**: cuál es la primaria")
    L.append("depende de la enmienda V1-bis, que espera firma. `✓` marca un intervalo")
    L.append("que **no** contiene el cero.\n")
    L.append("| Espec. | h | muestra | MAE modelo vs cero (pp) | Ganancia de MAE | Ganancia de CRPS | Dirección vs climatología | Ganancia de dirección |")
    L.append("|---|---:|---|---|---|---|---|---|")
    for espec in S.ESPECIFICACIONES:
        for h in S.HORIZONTES:
            L.append(_fila(espec, h, todo[(espec, h)]))
    L.append("")

    # --- la tercera vara, POST-HOC y rotulada como tal ---
    L.append("## La tercera vara: climatología causal — **AGREGADA DESPUÉS DE VER "
             "EL RESULTADO**\n")
    L.append("Hay que decirlo primero y sin adorno: **esta sección se agregó después**")
    L.append("de leer la tabla de arriba. El pre-registro §5 declaraba dos varas de")
    L.append("MAGNITUD —predecir cero y la línea base aburrida— y la de arriba es la")
    L.append("primera. **La segunda no se corrió en esta corrida** (ver la conclusión).")
    L.append("El §5 declaraba además, en su último párrafo, la climatología **para")
    L.append("DIRECCIÓN**: eso estaba pre-registrado. Lo que se agrega post-hoc acá es")
    L.append("la climatología de **magnitud**. Se agrega una tercera porque la de arriba es débil por una")
    L.append("razón que el propio adversario del proyecto ya había dictaminado antes de")
    L.append("esta corrida (`espera_firma.md` §30): **«predecir cero» no es neutro en un")
    L.append("mercado que sube**. Cero está sistemáticamente por debajo de la media")
    L.append("incondicional, así que cualquier modelo que aprenda el intercepto le gana")
    L.append("sin saber nada de la cadena.\n")
    L.append("La climatología causal es esa media: el promedio de la etiqueta **en el")
    L.append("período de ajuste**, en el espacio propio de cada especificación")
    L.append("(residual para L2, crudo para L1 y L3). Es una constante, no mira el")
    L.append("futuro, y es la vara que hay que ganarle para poder decir «la cadena")
    L.append("anticipa».\n")
    L.append("Se agrega una vara MÁS DIFÍCIL después de ver un resultado favorable. La")
    L.append("dirección de la enmienda importa: endurecer la prueba tras un positivo no")
    L.append("es lo mismo que ablandarla tras un negativo, y por eso se publica en vez")
    L.append("de reescribir el pre-registro. `✗` marca un intervalo enteramente por")
    L.append("DEBAJO del cero: el modelo pierde contra la constante.\n")
    L.append("| Espec. | h | MAE modelo vs climatología (constante) | Ganancia de MAE | Ganancia de CRPS |")
    L.append("|---|---:|---|---|---|")
    for espec in S.ESPECIFICACIONES:
        for h in S.HORIZONTES:
            L.append(_fila_clima(espec, h, todo[(espec, h)]))
    L.append("")

    # --- veredicto, mecánico ---
    L.append("## Veredicto\n")

    L.append("### Lo que dice la regla pre-registrada §6, aplicada tal cual\n")
    l1 = [todo[("L1", h)] for h in S.HORIZONTES]
    l1_gana = [not _cruza(m["ic_mae"]) and
               (m["mae_cero_pp"] - m["mae_modelo_pp"]) > 0 for m in l1]
    if not any(l1_gana):
        L.append("**L1 queda REFUTADA.** La regla dice: «si L1 no le gana a predecir")
        L.append("cero en MAE, con intervalo que excluya el cero, en ninguno de los dos")
        L.append("horizontes, la forma simple de la hipótesis queda refutada». Es")
        L.append("exactamente lo que pasó:")
        for h, m in zip(S.HORIZONTES, l1):
            L.append(f"- L1 a {h} días: ganancia "
                     f"{m['mae_cero_pp'] - m['mae_modelo_pp']:+.3f} pp, IC "
                     f"[{m['ic_mae']['lo']:+.3f}, {m['ic_mae']['hi']:+.3f}] — "
                     f"contiene el cero.")
        L.append("")
        L.append("El contagio directo entre eslabones adyacentes, que es la forma más")
        L.append("simple de la hipótesis y la que había que descartar antes de")
        L.append("complicar nada, **no aparece**.")
    else:
        L.append("L1 le gana a predecir cero en al menos un horizonte con intervalo que")
        L.append("excluye el cero. La forma simple de la hipótesis NO queda refutada por")
        L.append("esta regla.")
    L.append("")

    L.append("### Lo que sobrevive a la vara dura\n")
    sobreviven = []
    for espec in S.ESPECIFICACIONES:
        for h in S.HORIZONTES:
            m = todo[(espec, h)]
            for nombre, ic, punto in (
                    ("MAE", m["ic_mae_clima"],
                     m["mae_clima_pp"] - m["mae_modelo_pp"]),
                    ("CRPS", m["ic_crps_clima"],
                     m["crps_clima"] - m["crps_modelo"])):
                if not _cruza(ic) and punto > 0:
                    sobreviven.append((espec, h, nombre, punto, ic))
    pierden = []
    for espec in S.ESPECIFICACIONES:
        for h in S.HORIZONTES:
            m = todo[(espec, h)]
            for nombre, ic, punto in (
                    ("MAE", m["ic_mae_clima"],
                     m["mae_clima_pp"] - m["mae_modelo_pp"]),
                    ("CRPS", m["ic_crps_clima"],
                     m["crps_clima"] - m["crps_modelo"])):
                if not _cruza(ic) and punto < 0:
                    pierden.append((espec, h, nombre))
    if sobreviven:
        L.append("Antes de nombrar ninguna: **estos intervalos son SIN corregir por")
        L.append("multiplicidad**, y la sección siguiente muestra qué queda de ellos")
        L.append("cuando se corrige. Se listan igual, porque esconderlos sería elegir")
        L.append("qué mostrar según el resultado.\n")
        for espec, h, nombre, punto, ic in sobreviven:
            L.append(f"- **{espec} a {h} días en {nombre}:** {punto:+.3f}, IC "
                     f"[{ic['lo']:+.3f}, {ic['hi']:+.3f}] (sin corregir).")
    else:
        L.append("**Nada.** Ninguna especificación le gana a la constante con un")
        L.append("intervalo que excluya el cero, en ningún horizonte.")
    L.append("")
    if pierden:
        L.append("Y pierden contra la constante, con intervalo enteramente por debajo")
        L.append("del cero: " + ", ".join(f"{e} a {h} días en {n}" for e, h, n in pierden)
                 + ".")
        L.append("")

    # --- multiplicidad, siempre, salga lo que salga ---
    L.append("### Multiplicidad: la familia completa son "
             f"{mult['familia']} contrastes, no 24\n")
    L.append("La cuenta vieja de esta página decía 24 (3 especificaciones × 2")
    L.append("horizontes × 2 varas × 2 métricas) y dejaba **los seis contrastes de")
    L.append("dirección fuera de su propia corrección de multiplicidad**. `medir()`")
    L.append(f"produce cinco intervalos por celda: la familia son {mult['familia']}.")
    L.append("Con Holm sobre esa familia, que no supone independencia entre")
    L.append("contrastes —y acá no la hay, comparten filas, fechas y")
    L.append("especificaciones—:\n")
    L.append("| Contraste | p crudo | p de Holm | ¿cruza α = 0,05? |")
    L.append("|---|---:|---:|---|")
    for nombre, p_crudo in sorted(mult["p_crudo"].items(),
                                  key=lambda kv: kv[1]):
        p_h = mult["p_holm"][nombre]
        veredicto = "**sí**" if p_h < mult["alpha"] else "no"
        L.append(f"| {nombre} | {p_crudo:.4f} | {p_h:.4f} | {veredicto} |")
    L.append("")
    if mult["pasan"]:
        L.append("Pasan la corrección: " + ", ".join(mult["pasan"]) + ".")
    else:
        L.append(f"**Ninguno de los {mult['familia']} contrastes cruza α = 0,05 bajo")
        L.append("Holm.** Ni los positivos ni los negativos. Es el resultado que")
        L.append("gobierna esta página y va antes que cualquier celda suelta.")
    L.append("")
    L.append("Un p de bootstrap con "
             f"{REPLICAS} réplicas no puede bajar de {1.0/REPLICAS:.4f}: un p que")
    L.append("aparece en ese piso quiere decir «ninguna réplica cruzó», no cero.\n")

    # --- ablacion anual, la que el pre-registro del riel exige ---
    L.append("### Ablación anual, la que el pre-registro del riel exige\n")
    L.append("`dinero/preregistro_dinero.md` exige que un positivo sobreviva a sacar")
    L.append("la ventana que lo sostiene. Es la forma exacta del **R2** de")
    L.append("`GEMELO/DISEÑO.md`. La v1 de esta página admitía no haberla corrido;")
    L.append("acá está corrida, sobre la ganancia de MAE contra la climatología, para")
    L.append("**todas** las celdas y no sólo para las que convienen.\n")
    L.append("| Espec. | h | año sacado | ganancia sin ese año | ¿excluye el cero? | sólo ese año |")
    L.append("|---|---:|---|---|---|---|")
    for espec in S.ESPECIFICACIONES:
        for h in S.HORIZONTES:
            m = todo[(espec, h)]
            if m["vacio"]:
                continue
            for ano, d in sorted(m.get("ablacion_mae_clima", {}).items()):
                if d.get("sin_muestra"):
                    L.append(f"| **{espec}** | {h} | {ano} | sin muestra | — | — |")
                    continue
                sa = d["sin_ese_ano"]
                so = d["solo_ese_ano"]
                marca = "no, **contiene el cero**" if sa["cruza_cero"] else "sí"
                L.append(f"| **{espec}** | {h} | {ano} | "
                         f"{sa['media']:+.3f} pp [{sa['lo']:+.3f}, {sa['hi']:+.3f}] "
                         f"({sa['fechas']} fechas) | {marca} | "
                         f"{so['media']:+.3f} pp ({so['fechas']} fechas) |")
    L.append("")
    fragiles = []
    for espec, h, nombre, punto, ic in sobreviven:
        if nombre != "MAE":
            continue
        for ano, d in sorted(todo[(espec, h)].get("ablacion_mae_clima", {}).items()):
            if not d.get("sin_muestra") and d["sin_ese_ano"]["cruza_cero"]:
                fragiles.append((espec, h, ano))
    if fragiles:
        L.append("**Y ahí se cae.** " + "; ".join(
            f"sacando {ano} del período de prueba, la ganancia de {e} a {h} días "
            f"pasa a contener el cero" for e, h, ano in fragiles) + ".")
        L.append("Es la misma forma que el R2 tiene en el riel de medición: la")
        L.append("significancia cabalga una ventana. **Una celda que necesita un año")
        L.append("concreto para excluir el cero no es un hallazgo, es esa ventana.**")
        L.append("")

    L.append("### Lo que hay que decir de la métrica de dirección\n")
    degeneradas = [(e, h) for e in S.ESPECIFICACIONES for h in S.HORIZONTES
                   if not todo[(e, h)]["vacio"]
                   and not todo[(e, h)]["pred_cambia_de_signo"]]
    if degeneradas:
        L.append("En " + ", ".join(f"{e} a {h} días" for e, h in degeneradas) +
                 " **la predicción nunca cambia de signo**: el modelo dice «sube»")
        L.append("todos los días del período de prueba. Su acierto direccional es")
        L.append("idéntico al de la climatología por construcción, y la ganancia de")
        L.append("+0,000 pp con intervalo [0, 0] **no es un empate: es una métrica")
        L.append("vacía**. Publicar ese cero como si fuera un resultado sería el")
        L.append("mismo error que el proyecto ya cometió una vez al publicar un PSR")
        L.append("saturado como si fuera certeza. (Nota de precisión: ese diagnóstico")
        L.append("está **RETIRADO** —`dictamen_08/A.md` A3—: la saturación resultó ser")
        L.append("un **defecto de unidades**, no un hecho de muestra corta, y con la")
        L.append("unidad correcta daba 0,95–0,96. La lección sobrevive; la explicación")
        L.append("que se le ponía, no.)")
        L.append("")
    L.append("Y van los discordantes con su McNemar exacto, que la v1 no publicaba.")
    L.append("La regla de la casa pide **b, c y p siempre**, porque un p de filas al")
    L.append("lado de un intervalo de fecha que contiene el cero es el síntoma de que")
    L.append("las filas de un mismo día no son observaciones independientes: es")
    L.append("exactamente lo que le pasa al riel de medición.\n")
    L.append("| Espec. | h | b (gana el modelo) | c (gana la climatología) | McNemar exacto (filas) | IC de fecha |")
    L.append("|---|---:|---:|---:|---:|---|")
    for e in S.ESPECIFICACIONES:
        for h in S.HORIZONTES:
            m = todo[(e, h)]
            if m["vacio"]:
                continue
            ic = m["ic_dir"]
            det = ("**contiene el cero**" if _cruza(ic) else "excluye el cero")
            L.append(f"| **{e}** | {h} | {m['dir_b']} | {m['dir_c']} | "
                     f"{m['dir_mcnemar_p']:.4g} | "
                     f"[{ic['lo']:+.3f}, {ic['hi']:+.3f}] — {det} |")
    L.append("")
    desacuerdo = [(e, h, todo[(e, h)]) for e in S.ESPECIFICACIONES
                  for h in S.HORIZONTES
                  if not todo[(e, h)]["vacio"]
                  and todo[(e, h)]["dir_mcnemar_p"] < 0.05
                  and _cruza(todo[(e, h)]["ic_dir"])]
    for e, h, m in desacuerdo:
        L.append(f"**{e} a {h} días es el caso a mirar:** McNemar de filas "
                 f"{m['dir_mcnemar_p']:.4g} contra un intervalo de fecha que")
        L.append("contiene el cero. Manda el intervalo de fecha. La fila no es la")
        L.append("unidad de observación de este diseño.")
        L.append("")
    peores = [(e, h, todo[(e, h)]) for e in S.ESPECIFICACIONES for h in S.HORIZONTES
              if not todo[(e, h)]["vacio"] and not _cruza(todo[(e, h)]["ic_dir"])
              and (todo[(e, h)]["acierto_pct"] - todo[(e, h)]["clima_pct"]) < 0]
    for e, h, m in peores:
        p_h = mult["p_holm"].get(f"{e} h={h} direccion vs climatologia")
        L.append(f"Y **{e} a {h} días acierta MENOS que la climatología**: "
                 f"{m['acierto_pct']:.1f} % contra {m['clima_pct']:.1f} %, "
                 f"{m['acierto_pct'] - m['clima_pct']:+.3f} pp con IC "
                 f"[{m['ic_dir']['lo']:+.3f}, {m['ic_dir']['hi']:+.3f}], que no")
        L.append("contiene el cero **sin corregir**. Pero la simetría vale para el")
        L.append("negativo igual que para el positivo: bajo Holm sobre la familia")
        L.append(f"completa su p ajustado es {p_h:.4f}, o sea que **tampoco es")
        L.append("distinguible de cero**. La refutación de L1 no depende de este")
        L.append("número: depende de la regla §6, que sólo mira MAE contra cero y se")
        L.append("cumple sola.")
    L.append("")

    L.append("### La conclusión\n")
    if len(sobreviven) == 0:
        L.append("**Los datos disponibles no traen señal larga detectable entre")
        L.append("eslabones de la cadena a 20 y 60 días hábiles.** Es lo que el")
        L.append("pre-registro §6 obliga a escribir tal cual, y es un resultado.")
    else:
        cuantos = len(set((e, h) for e, h, *_ in sobreviven))
        total_celdas = len(S.ESPECIFICACIONES) * len(S.HORIZONTES)
        L.append("La forma simple de la hipótesis —el contagio directo, L1— **está")
        L.append("refutada por su propia regla pre-registrada**. Eso se sostiene solo")
        L.append("y no depende de nada de lo que sigue.")
        L.append("")
        L.append(f"De las {total_celdas} celdas, **{cuantos} le gana a la climatología")
        L.append("causal con el intervalo sin corregir**. Y esa celda **no sobrevive**")
        L.append("a las dos pruebas que esta misma página le corre:")
        L.append("")
        if not mult["pasan"]:
            L.append(f"1. **Multiplicidad.** Sobre la familia completa de "
                     f"{mult['familia']} contrastes, ninguno cruza α = 0,05 bajo")
            L.append("   Holm. El positivo tampoco.")
        else:
            L.append(f"1. **Multiplicidad.** Sobre {mult['familia']} contrastes, "
                     "pasan Holm: " + ", ".join(mult["pasan"]) + ".")
        if fragiles:
            L.append("2. **Ablación anual.** Sacando " + "; sacando ".join(
                f"{ano} del período de prueba, {e} a {h} días pasa a contener "
                "el cero" for e, h, ano in fragiles) +
                ". La ventaja cabalga una ventana,")
            L.append("   que es la forma exacta del R2.")
        else:
            L.append("2. **Ablación anual.** Ningún año calendario, sacado del período")
            L.append("   de prueba, hace que el intervalo pase a contener el cero.")
        L.append("")
        L.append("Así que la lectura correcta de esta página **no es «sobrevive una")
        L.append("celda»**: es que, corregido por su propia familia y sometido a la")
        L.append("ablación que el pre-registro del riel exige, **no queda ninguna")
        L.append("afirmación positiva en pie**. La magnitud, además, es del orden del")
        L.append("2 % relativo, y la dirección de esa misma celda no se distingue del")
        L.append("cero ni siquiera sin corregir.")
        L.append("")
        L.append("**Esto no autoriza nada.** Cuatro razones, todas medidas en esta")
        L.append("misma corrida:")
        L.append("")
        L.append(f"1. La familia de esta página son **{mult['familia']} contrastes**,")
        L.append("   y ninguno pasa Holm. La cuenta vieja decía 24 y dejaba los seis")
        L.append("   de dirección fuera de su propia corrección.")
        L.append("2. La ablación anual, corrida acá y no diferida, muestra de qué")
        L.append("   ventana depende el único positivo sin corregir.")
        L.append("3. **La segunda vara pre-registrada NO se evaluó.** El §5 del")
        L.append("   pre-registro declara dos: predecir cero (la de arriba) y **la")
        L.append("   línea base aburrida, aporte semanal a `SMH`, a la que se llega")
        L.append("   pasando la señal por `dinero/decision.py` y la cuenta en papel**.")
        L.append("   Esa segunda no se corrió en esta corrida, y mientras no se corra")
        L.append("   la regla de refutación del §6 («si ninguna de las tres supera a")
        L.append("   ninguna de las dos varas») y el criterio M4 del pre-registro del")
        L.append("   riel **no se pueden dar por leídos**. Se agrega que hoy la cuenta")
        L.append("   en papel está RETIRADA por fuga demostrada, así que esa vara no")
        L.append("   se puede correr hasta que la cuenta se reconstruya.")
        L.append("4. Los sesgos que no se pudieron corregir —supervivencia, la fuente")
        L.append("   no point-in-time, `VRT` como SPAC durante el 17,8 % de la")
        L.append("   muestra— **empujan todos en dirección optimista**, y son del")
        L.append("   orden de la mejora medida.")
        L.append("")
        L.append("Sobre la tasa de falsos positivos: la v1 de esta página citaba acá")
        L.append("el «21 % de los casos» de la cuenta en papel. Se retira por dos")
        L.append("razones. Primera, era de **otro diseño** (24 comparaciones")
        L.append("semanales de carteras que comparten sorteo y flujo de caja, con")
        L.append("bloques de 4 semanas), no de esta página, que son "
                 f"{mult['familia']} contrastes con bloques por fecha de emisión;")
        L.append("la tasa de tipo I de ESTE diseño **no está medida**. Segunda, la")
        L.append("cuenta en papel tiene **fuga temporal demostrada**")
        L.append("(`dictamen_10/auditor_lookahead.md`, F1 a F4) y ninguna de sus")
        L.append("cifras se puede citar. Lo que ocupa su lugar no es una tasa")
        L.append("prestada: es la corrección de Holm, computada sobre esta familia.")
    L.append("")

    L.append("## Lo que este bloque NO puede concluir, declarado antes de correrlo\n")
    L.append("- **El DSR sale NO INTERPRETABLE pase lo que pase.** A 60 días hábiles")
    L.append("  sobre 8 años quedan del orden de 33 observaciones no solapadas por par;")
    L.append("  no hay potencia. Se declara y no se imprime un número que mentiría.")
    L.append("- **Los datos no son point-in-time.** La fuente reajusta la historia")
    L.append("  hacia atrás por splits y dividendos. El proyecto midió esa")
    L.append("  contaminación en el riel de medición y, con la clave correcta")
    L.append("  (`sesion_objetivo`), dio **100 % de coincidencia sobre 214 filas, 0")
    L.append("  diferencias**. La cifra de «91,4 % sobre 198 filas» que")
    L.append("  `ventana_larga.md` todavía publica está **RETIRADA desde el")
    L.append("  1-sep-2026** (`GEMELO/cifras_retiradas.md`, `espera_firma.md` §11a):")
    L.append("  salía de cruzar por `[fecha, ticker]` en vez de por la sesión")
    L.append("  objetivo. Eso **no** prueba que la fuente no revise su historia: sólo")
    L.append("  que no la revisó en el tramo auditable de 2026. El sesgo sigue")
    L.append("  declarado y sigue yendo en dirección optimista.")
    L.append("- **Supervivencia, NO corregida.** Los 36 tickers son los que existen")
    L.append("  hoy: ninguna deslistada, ninguna adquirida, ninguna quebrada. El sesgo")
    L.append("  de SELECCIÓN por precio sí se corrigió (errata E1); éste no se puede")
    L.append("  con este archivo.")
    L.append("- **Identidad del instrumento.** `VRT` fue el SPAC GS Acquisition hasta")
    L.append("  feb-2020: durante 358 sesiones (17,8 % de la muestra) su σ diaria fue")
    L.append("  0,59 % contra 3,86 % después. Un tercio de «demanda final» es, en el")
    L.append("  primer quinto del ajuste, un fideicomiso.")
    L.append("- **Fuga por el analista.** Los ocho eslabones, su orden, los pares y las")
    L.append("  tres especificaciones los diseñó alguien que ya vio 2018–2026. Ninguna")
    L.append("  prueba de este repositorio lo detecta; la única defensa es el sellado")
    L.append("  en vivo, y este riel tiene **cero filas selladas**.")
    return "\n".join(L) + "\n"


def a_json(todo: dict, mult: dict) -> dict:
    """La misma medición, en estructura. Sale del mismo `todo` que compone
    el .md: si alguna vez difieren, es un bug y no una versión."""
    celdas = []
    for (espec, h), m in todo.items():
        if m["vacio"]:
            continue
        celdas.append({
            "especificacion": espec, "horizonte_dias_habiles": h,
            "filas": m["filas"], "fechas": m["ic_mae"]["fechas"],
            "n_ajuste": m["n_ajuste"], "corte_ajuste": m["corte_ajuste"],
            "prediccion_cambia_de_signo": m["pred_cambia_de_signo"],
            "mae_modelo_pp": m["mae_modelo_pp"],
            "vara_cero": {
                "estatus": "PRE-REGISTRADA",
                "mae_pp": m["mae_cero_pp"],
                "ganancia_mae_pp": m["mae_cero_pp"] - m["mae_modelo_pp"],
                "intervalo": [m["ic_mae"]["lo"], m["ic_mae"]["hi"]],
                "cruza_cero": _cruza(m["ic_mae"])},
            "vara_climatologia": {
                "estatus": "POST-HOC, agregada tras ver el resultado",
                "constante_pp": m["clima_media_pp"],
                "mae_pp": m["mae_clima_pp"],
                "ganancia_mae_pp": m["mae_clima_pp"] - m["mae_modelo_pp"],
                "intervalo": [m["ic_mae_clima"]["lo"], m["ic_mae_clima"]["hi"]],
                "cruza_cero": _cruza(m["ic_mae_clima"])},
            "direccion": {
                "acierto_pct": m["acierto_pct"],
                "climatologia_pct": m["clima_pct"],
                "filas": m["filas_direccion"],
                "ganancia_pp": m["acierto_pct"] - m["clima_pct"],
                "intervalo": [m["ic_dir"]["lo"], m["ic_dir"]["hi"]],
                "cruza_cero": _cruza(m["ic_dir"]),
                "discordantes_b": m["dir_b"],
                "discordantes_c": m["dir_c"],
                "mcnemar_exacto_filas": m["dir_mcnemar_p"],
                "vacia": not m["pred_cambia_de_signo"]},
            "bloques_efectivos_bootstrap": m["bloques_efectivos"],
            "ablacion_anual_mae_climatologia": m.get("ablacion_mae_clima", {}),
        })
    ganan = [c for c in celdas
             if not c["vara_climatologia"]["cruza_cero"]
             and c["vara_climatologia"]["ganancia_mae_pp"] > 0]
    # Las que ganan SIN corregir y ademas sobreviven a la ablacion anual.
    ganan_tras_ablacion = []
    for c in ganan:
        ab = c.get("ablacion_anual_mae_climatologia") or {}
        frag = [a for a, d in ab.items()
                if not d.get("sin_muestra") and d["sin_ese_ano"]["cruza_cero"]]
        if not frag:
            ganan_tras_ablacion.append(c)
    return {
        "estatus": "PROPUESTA",
        "advertencia": ("Ninguna cifra entra al README ni sostiene ninguna "
                        "afirmación del proyecto. Cero filas selladas."),
        "preregistro": "GEMELO/preregistro/senal_larga_v1.md (commit e368dad)",
        "intentos_riel_largo": registro_intentos.N_INTENTOS_RIEL_LARGO,
        "celdas": celdas,
        "multiplicidad": {
            "familia_contrastes": mult["familia"],
            "metodo": "Holm-Bonferroni sobre la familia completa",
            "alpha": mult["alpha"],
            "p_crudo": mult["p_crudo"],
            "p_holm": mult["p_holm"],
            "pasan": mult["pasan"],
        },
        "resumen": {
            "celdas": len(celdas),
            "ganan_a_la_climatologia_sin_corregir": len(ganan),
            "ganan_tras_multiplicidad": len(mult["pasan"]),
            "ganan_tras_ablacion_anual": len(ganan_tras_ablacion),
            "L1_refutada": all(
                _cruza(todo[("L1", h)]["ic_mae"]) for h in S.HORIZONTES),
            "contrastes": mult["familia"],
            "segunda_vara_preregistrada_evaluada": False,
            "nota": ("La forma simple de la hipótesis (L1, contagio directo) "
                     "queda refutada por su propia regla pre-registrada. "
                     "Ninguna celda sobrevive a la corrección de "
                     "multiplicidad sobre su propia familia de %d "
                     "contrastes, y la única que gana sin corregir tampoco "
                     "sobrevive a la ablación anual que el pre-registro del "
                     "riel exige. La segunda vara pre-registrada no se "
                     "evaluó. Nada de esta página autoriza nada."
                     % mult["familia"]),
        },
    }


def main():
    todo = correr()
    mult = multiplicidad(todo)
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(componer(todo, mult))
    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(a_json(todo, mult), f, indent=1, ensure_ascii=False,
                  default=float)
        f.write("\n")
    print("escrito", SALIDA, "y", SALIDA_JSON)


if __name__ == "__main__":
    main()
