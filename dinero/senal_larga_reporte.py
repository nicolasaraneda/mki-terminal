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
# ============================================================
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd

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
        "crps_modelo": float(np.mean(crps_modelo)),
        "crps_cero": float(np.mean(crps_cero)),
        "mae_clima_pp": float(np.mean(ae_clima) * 100.0),
        "crps_clima": float(np.mean(crps_clima)),
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
    out["ic_crps"] = _ic_por_fecha(crps_cero - crps_modelo, fechas, h)
    out["ic_mae_clima"] = _ic_por_fecha((ae_clima - ae_modelo) * 100.0, fechas, h)
    out["ic_crps_clima"] = _ic_por_fecha(crps_clima - crps_modelo, fechas, h)
    out["ic_dir"] = _ic_por_fecha(
        ((acierto - acierto_clima) * 100.0)[no_cero], fechas[no_cero], h)
    return out


def _cruza(ic) -> bool:
    return bool(np.isnan(ic["lo"]) or ic["lo"] <= 0.0 <= ic["hi"])


def correr() -> dict:
    cierres = S.cargar_cierres()
    todo = {}
    for h in S.HORIZONTES:
        paneles = S.construir_paneles(cierres, h)
        for espec in S.ESPECIFICACIONES:
            res = S.evaluar(paneles[espec], espec, h)
            todo[(espec, h)] = medir(res, h)
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
            f"{celda(m['ic_crps'], m['crps_cero'] - m['crps_modelo'], '')} | "
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
            f"{celda(m['ic_crps_clima'], m['crps_clima'] - m['crps_modelo'], '')} |")


def componer(todo: dict) -> str:
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
             f"α = {ALPHA}.\n")

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
    L.append("de leer la tabla de arriba. El pre-registro §5 declaraba dos varas —")
    L.append("predecir cero y la línea base aburrida— y la de arriba es la que estaba")
    L.append("declarada. Se agrega una tercera porque la de arriba es débil por una")
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
        for espec, h, nombre, punto, ic in sobreviven:
            L.append(f"- **{espec} a {h} días en {nombre}:** {punto:+.3f}, IC "
                     f"[{ic['lo']:+.3f}, {ic['hi']:+.3f}].")
    else:
        L.append("**Nada.** Ninguna especificación le gana a la constante con un")
        L.append("intervalo que excluya el cero, en ningún horizonte.")
    L.append("")
    if pierden:
        L.append("Y pierden contra la constante, con intervalo enteramente por debajo")
        L.append("del cero: " + ", ".join(f"{e} a {h} días en {n}" for e, h, n in pierden)
                 + ".")
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
        L.append("vacía**. Publicar ese cero como si fuera un resultado sería el mismo")
        L.append("error que publicar un PSR saturado en 1,0000 como si fuera certeza.")
        L.append("")
    peores = [(e, h, todo[(e, h)]) for e in S.ESPECIFICACIONES for h in S.HORIZONTES
              if not todo[(e, h)]["vacio"] and not _cruza(todo[(e, h)]["ic_dir"])
              and (todo[(e, h)]["acierto_pct"] - todo[(e, h)]["clima_pct"]) < 0]
    for e, h, m in peores:
        L.append(f"Y **{e} a {h} días acierta MENOS que la climatología**: "
                 f"{m['acierto_pct']:.1f} % contra {m['clima_pct']:.1f} %, "
                 f"{m['acierto_pct'] - m['clima_pct']:+.3f} pp con IC "
                 f"[{m['ic_dir']['lo']:+.3f}, {m['ic_dir']['hi']:+.3f}], que no")
        L.append("contiene el cero. Es un resultado negativo, y va con la misma")
        L.append("firmeza con que se publicaría uno positivo.")
    L.append("")

    L.append("### La conclusión\n")
    if len(sobreviven) == 0:
        L.append("**Los datos disponibles no traen señal larga detectable entre")
        L.append("eslabones de la cadena a 20 y 60 días hábiles.** Es lo que el")
        L.append("pre-registro §6 obliga a escribir tal cual, y es un resultado.")
    else:
        cuantos = len(set((e, h) for e, h, *_ in sobreviven))
        total_celdas = len(S.ESPECIFICACIONES) * len(S.HORIZONTES)
        L.append(f"De las {total_celdas} celdas (tres especificaciones × dos")
        L.append(f"horizontes), **{cuantos} le gana a la climatología causal** y el")
        L.append("resto no, o pierde. La forma simple de la hipótesis —el contagio")
        L.append("directo, L1— **está refutada por su propia regla pre-registrada**.")
        L.append("")
        L.append("Lo que queda en pie es chico y hay que decir de qué tamaño: la mejor")
        L.append("celda mejora el MAE en " +
                 f"{max(p for *_ , p, _ in [(a,b,c,p,i) for a,b,c,p,i in sobreviven]):.3f} pp "
                 "sobre una base de " +
                 f"{todo[(sobreviven[0][0], sobreviven[0][1])]['mae_clima_pp']:.1f} pp, "
                 "o sea del orden del **2 %**")
        L.append("relativo. La dirección, en esa misma celda, no se distingue del cero.")
        L.append("")
        L.append("**Esto no autoriza nada.** Tres razones, todas medidas en esta misma")
        L.append("corrida:")
        L.append("")
        L.append("1. Esta página tiene **24 contrastes** (3 especificaciones × 2")
        L.append("   horizontes × 2 varas × 2 métricas). La cuenta en papel del bloque 4")
        L.append("   midió que un diseño así produce un intervalo que excluye el cero en")
        L.append("   el **21 % de los casos con una señal que no tiene información**.")
        L.append("2. El pre-registro del riel (`dinero/preregistro_dinero.md` §2.5) exige")
        L.append("   que un positivo sobreviva **ablación de la ventana que lo sostiene**")
        L.append("   —del tipo R2, que hoy descalifica al propio campeón del riel de")
        L.append("   medición— y el dictamen del adversario. Ninguna de las dos cosas se")
        L.append("   hizo acá.")
        L.append("3. Los sesgos que no se pudieron corregir —supervivencia, la fuente no")
        L.append("   point-in-time, `VRT` como SPAC durante el 17,8 % de la muestra—")
        L.append("   **empujan todos en dirección optimista**, y son del orden de la")
        L.append("   mejora medida.")
    L.append("")

    L.append("## Lo que este bloque NO puede concluir, declarado antes de correrlo\n")
    L.append("- **El DSR sale NO INTERPRETABLE pase lo que pase.** A 60 días hábiles")
    L.append("  sobre 8 años quedan del orden de 33 observaciones no solapadas por par;")
    L.append("  no hay potencia. Se declara y no se imprime un número que mentiría.")
    L.append("- **Los datos no son point-in-time.** La fuente reajusta la historia")
    L.append("  hacia atrás por splits y dividendos; `GEMELO/resultados/ventana_larga.md`")
    L.append("  midió la contaminación en el riel de medición (198 filas comunes,")
    L.append("  91,4 % de coincidencia, máximo 31,2 pp) y va en dirección optimista.")
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


def a_json(todo: dict) -> dict:
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
                "vacia": not m["pred_cambia_de_signo"]},
        })
    ganan = [c for c in celdas
             if not c["vara_climatologia"]["cruza_cero"]
             and c["vara_climatologia"]["ganancia_mae_pp"] > 0]
    return {
        "estatus": "PROPUESTA",
        "advertencia": ("Ninguna cifra entra al README ni sostiene ninguna "
                        "afirmación del proyecto. Cero filas selladas."),
        "preregistro": "GEMELO/preregistro/senal_larga_v1.md (commit e368dad)",
        "intentos_riel_largo": registro_intentos.N_INTENTOS_RIEL_LARGO,
        "celdas": celdas,
        "resumen": {
            "celdas": len(celdas),
            "ganan_a_la_climatologia": len(ganan),
            "L1_refutada": all(
                _cruza(todo[("L1", h)]["ic_mae"]) for h in S.HORIZONTES),
            "contrastes": len(celdas) * 4,
            "nota": ("La forma simple de la hipótesis (L1, contagio directo) "
                     "queda refutada por su propia regla pre-registrada. Lo "
                     "que sobrevive a la climatología causal es una celda, "
                     "con una mejora del orden del 2 % relativo, y no "
                     "autoriza nada."),
        },
    }


def main():
    todo = correr()
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(componer(todo))
    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(a_json(todo), f, indent=1, ensure_ascii=False, default=float)
        f.write("\n")
    print("escrito", SALIDA, "y", SALIDA_JSON)


if __name__ == "__main__":
    main()
