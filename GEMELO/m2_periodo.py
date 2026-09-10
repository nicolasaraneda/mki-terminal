# ============================================================
# GEMELO/m2_periodo.py — §43: ¿M2 dispara?, recomputado sobre la cuenta v2
# (sin fuga) a 52, 104 y 156 semanas y en la peor ventana móvil de 52, con
# banda entre las K semillas del sorteo. Corrida 12, bloque 8.1.
#
# Ninguna cifra viene del encargo ni de la v1 RETIRADA (pre-mortem 9). M2:
# «la comisión acumulada supera el 25 % del capital aportado en el período».
# Se computan las cuatro lecturas y se publica cada una con su período al
# lado; cuál rige lo dice el acta (§84.4.5: el horizonte pre-registrado de
# la vara, 52 semanas, `preregistro_dinero.md` §2 punto 1), y si esa
# elección invalida M2 lo dictamina el adversario, no este módulo.
#   python -m GEMELO.m2_periodo
#
# Dictamen del adversario (dictamen_12/adversario_43_periodo_m2.md): la firma §84.4.5
# es NO APLICABLE; este módulo publica las cuatro lecturas sin elegir una y la tasa
# anualizada como lectura primaria (E1–E9 aplicadas).
# ============================================================
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from dinero import contabilidad as C
from dinero import cuenta_papel as CP
from dinero import precios
from dinero import universo_dinero as U

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "GEMELO", "resultados", "m2_periodo")
UMBRAL_M2_PCT = 25.0
HORIZONTES_SEMANAS = (52, 104, 156)


def _comisiones_acumuladas(libro, fechas: pd.DatetimeIndex) -> pd.Series:
    por_dia = {}
    for m in libro.movimientos:
        por_dia[pd.Timestamp(m.fecha)] = por_dia.get(pd.Timestamp(m.fecha), 0.0) + m.comision_usd
    s = pd.Series(por_dia).reindex(fechas).fillna(0.0)
    return s.cumsum()


def _aportado_acumulado(aportes: dict, fechas: pd.DatetimeIndex) -> pd.Series:
    s = pd.Series({pd.Timestamp(d): v for d, v in aportes.items()}).reindex(fechas).fillna(0.0)
    return s.cumsum()


def _deslizamiento_acumulado(libro, fechas: pd.DatetimeIndex, pb: float) -> pd.Series:
    """Deslizamiento por movimiento, reconstruido desde el precio de ejecución:
    en la compra precio = cierre × (1 + d) y en la venta precio = cierre × (1 − d),
    con d = pb / 10 000 (contabilidad.Libro.comprar/vender). El total por libro
    coincide con `libro.deslizamiento_usd`, y se verifica al construir."""
    d = pb / 10000.0
    por_dia, total = {}, 0.0
    for m in libro.movimientos:
        if m.lado == "compra":
            x = m.acciones * m.precio_ejecucion * d / (1.0 + d)
        else:
            x = m.acciones * m.precio_ejecucion * d / (1.0 - d)
        total += x
        por_dia[pd.Timestamp(m.fecha)] = por_dia.get(pd.Timestamp(m.fecha), 0.0) + x
    assert abs(total - float(libro.deslizamiento_usd)) < 1e-6 * max(1.0, abs(total)), (total, libro.deslizamiento_usd)
    return pd.Series(por_dia).reindex(fechas).fillna(0.0).cumsum()


def lecturas_m2(res: dict, cfg: dict, pb: float) -> dict:
    fechas = res["cierres"].index
    aport = _aportado_acumulado(res["aportes"], fechas)
    inicio = fechas[0]
    out = {}
    for juego in CP.JUEGOS:
        libro, _ = res["estrategia"][(juego, pb)]
        com = _comisiones_acumuladas(libro, fechas)
        des = _deslizamiento_acumulado(libro, fechas, pb)
        # E4 (dictamen §43): una cuenta que dejó de operar (sin caja para una acción
        # entera) acumula poca comisión por QUIEBRA operativa, no por baratura
        ultimo_mov = max((pd.Timestamp(m.fecha) for m in libro.movimientos), default=None)
        fila = {}
        for h in HORIZONTES_SEMANAS:
            corte = inicio + pd.Timedelta(weeks=h)
            sub = com.loc[:corte]
            if sub.empty or corte > fechas[-1] + pd.Timedelta(days=3):
                fila[f"pct_a_{h}_semanas"] = None
                fila[f"pct_anualizado_desde_{h}"] = None
                fila[f"pct_con_deslizamiento_a_{h}_semanas"] = None
                fila[f"congelada_antes_de_{h}"] = None
                continue
            den = float(aport.loc[:corte].iloc[-1])
            v = 100.0 * float(sub.iloc[-1]) / den
            fila[f"pct_a_{h}_semanas"] = round(v, 2)
            fila[f"pct_anualizado_desde_{h}"] = round(v * 52.0 / h, 2)          # E1: suma aritmética
            fila[f"pct_con_deslizamiento_a_{h}_semanas"] = round(100.0 * (float(sub.iloc[-1]) + float(des.loc[:corte].iloc[-1])) / den, 2)  # E5
            fila[f"congelada_antes_de_{h}"] = bool(ultimo_mov is not None and ultimo_mov < corte - pd.Timedelta(weeks=26))
        # peor ventana móvil de 52 semanas: comisión dentro de la ventana / aportado al final de la ventana
        peor = None
        for i, d in enumerate(fechas):
            fin = d + pd.Timedelta(weeks=52)
            if fin > fechas[-1]:
                break
            c_ini = float(com.iloc[i - 1]) if i > 0 else 0.0
            c_fin = float(com.loc[:fin].iloc[-1])
            v = 100.0 * (c_fin - c_ini) / float(aport.loc[:fin].iloc[-1])
            peor = v if peor is None or v > peor else peor
        fila["pct_peor_ventana_movil_52"] = round(peor, 2) if peor is not None else None
        out[juego] = fila
    return out


def correr(K: int = CP.K_SEMILLAS) -> dict:
    cfg = U.reglas()
    completo = precios.cargar_congelado()
    pb = cfg["costos"]["deslizamiento_pb_por_lado"]
    operables = CP.universo_operable(completo, cfg, hasta=CP.DESDE)
    por_semilla = []
    aportes_ref = None
    for i in range(K):
        sen = C.senales_sin_informacion(completo, operables, CP.HORIZONTE_SENAL_HABILES,
                                        C.SEMILLA_SENAL_SIN_INFORMACION + i, desde=CP.DESDE)
        _, res = CP.correr(completo, cfg, sen)
        aportes_ref = res["aportes"]
        por_semilla.append(lecturas_m2(res, cfg, pb))
    claves = ([f"pct_a_{h}_semanas" for h in HORIZONTES_SEMANAS] + ["pct_peor_ventana_movil_52"]
              + [f"pct_anualizado_desde_{h}" for h in HORIZONTES_SEMANAS]
              + [f"pct_con_deslizamiento_a_{h}_semanas" for h in HORIZONTES_SEMANAS])
    resumen = {}
    for juego in CP.JUEGOS:
        resumen[juego] = {}
        for k in claves:
            v = np.array([s[juego][k] for s in por_semilla if s[juego][k] is not None], dtype=float)
            if len(v) == 0:
                resumen[juego][k] = None
                continue
            # E4: banda como mín–máx además de percentiles; bimodalidad declarada por
            # el conteo de semillas congeladas cuando la clave tiene horizonte
            h = next((hh for hh in HORIZONTES_SEMANAS if f"_{hh}" in k), None)
            congeladas = (int(sum(1 for s in por_semilla if s[juego].get(f"congelada_antes_de_{h}")))
                          if h else None)
            resumen[juego][k] = {
                "mediana": round(float(np.median(v)), 2),
                "banda_p2_5_p97_5": [round(float(np.quantile(v, 0.025)), 2), round(float(np.quantile(v, 0.975)), 2)],
                "min_max": [round(float(v.min()), 2), round(float(v.max()), 2)],
                "dispara_M2_en_mediana": bool(np.median(v) > UMBRAL_M2_PCT),
                "semillas_que_disparan": int((v > UMBRAL_M2_PCT).sum()), "K": int(len(v)),
                "semillas_congeladas": congeladas,
                "advertencia_congeladas": ("una cuenta congelada (sin caja para una acción entera) acumula poca "
                                           "comisión por QUIEBRA operativa, no por baratura; su lectura de M2 baja "
                                           "por la razón equivocada" if congeladas else None),
            }
    return {
        "generado_en_utc": datetime.now(timezone.utc).isoformat(),
        "estatus": "PROPUESTA — hasta el dictamen del estadistico-adversario sobre el §43 (corrida 12)",
        "que_es": ("M2 recomputado sobre la cuenta en papel v2 (sin fuga demostrada, gate INVARIANTE), "
                   "señal sin información, arancel del §40 (PROPUESTA), K semillas del sorteo. Ninguna "
                   "cifra de la v1 RETIRADA se usa."),
        "umbral_pct": UMBRAL_M2_PCT, "deslizamiento_pb": pb, "K": K,
        "definiciones": {
            "pct_a_h_semanas": "comisión acumulada desde el inicio hasta h semanas / capital aportado hasta ahí",
            "pct_peor_ventana_movil_52": "máximo sobre ventanas de 52 semanas de (comisión dentro de la ventana / aportado al final de la ventana)",
            "banda": "percentiles 2,5 y 97,5 ENTRE SEMILLAS del sorteo (no un IC de cobertura nominal)",
        },
        # E2, E6, E7, E8, E9 del dictamen del adversario sobre el §43 (dictamen_12/adversario_43_periodo_m2.md)
        "denominador": {"denominador_usd": float(sum(aportes_ref.values())), "n_aportes": len(aportes_ref),
                        "aportes_terminan_en": str(max(aportes_ref)),
                        "nota": "el denominador NO crece después del último aporte; el numerador (comisión) es un flujo"},
        "una_sola_trayectoria": True, "n_historias_de_mercado": 1,
        "la_banda_no_cubre": "variación de trayectoria de mercado (una sola historia 2023-09-05 a 2026-09-04)",
        "deslizamiento_incluido_en_pct": False,
        "deslizamiento_nota": "las lecturas pct_con_deslizamiento_* lo incluyen; si cuenta para M2 sigue sin firma (preregistro §7 B (ii))",
        "pct_a_156_nota": "corta 156 semanas exactas desde el inicio (3 días antes del fin de la cuenta): NO es la cifra de vida entera de cuenta_papel.md",
        "juego_por_defecto": f"{cfg['juego_activo']} (reglas.json {cfg.get('version_reglas', '?')}, SIN FIRMA)",
        "lectura_primaria": "pct_anualizado_desde_h (suma aritmética v × 52/h): la única invariante al período",
        "convencion_anualizacion": "suma aritmética",
        "periodo": ("NO APLICABLE — la firma §84.4.5 (\u00abel horizonte pre-registrado de la vara\u00bb) invoca un horizonte "
                    "que el pre-registro no escribe (52 semanas es un piso prospectivo de duración, no una ventana de "
                    "acumulación de M2); se dispara su propia cláusula de escape y vuelve a espera_firma §43 "
                    "(dictamen_12/adversario_43_periodo_m2.md)"),
        "grado_de_libertad_declarado": ("se computaron 12 lecturas (3 juegos × 4 períodos) y la firma eligió 1 con los "
                                        "resultados a la vista (E12 del dictamen)"),
        "resumen": resumen, "por_semilla": por_semilla,
        "intentos_dsr": 0,
    }


def informe(r: dict) -> str:
    L = ["# M2, recomputado sobre la cuenta v2 — las cuatro lecturas, sin elegir una\n",
         f"**{r['estatus']}.** Generado {r['generado_en_utc']}. {r['que_es']}\n",
         f"Umbral M2: {r['umbral_pct']:.0f} % del capital aportado, **sin unidad de período declarada** (dictamen §43). "
         f"Deslizamiento {r['deslizamiento_pb']:.0f} pb, **NO incluido** en las lecturas `pct_a_*` (sí en `pct_con_deslizamiento_*`; "
         f"si cuenta para M2 sigue sin firma). K = {r['K']} semillas. **Una sola trayectoria de mercado**: la banda entre "
         f"semillas no cubre la variación de mercado. Denominador: {r['denominador']['denominador_usd']:.0f} USD en "
         f"{r['denominador']['n_aportes']} aportes que terminan el {r['denominador']['aportes_terminan_en']}; **el denominador "
         f"NO crece y el numerador es un flujo**, así que `pct_a_h` es proporcional a h. Juego por defecto: {r['juego_por_defecto']}.\n",
         "## Lectura primaria: tasa anualizada (suma aritmética v × 52/h), la única invariante al período\n",
         "| juego | anualizada desde 52 | desde 104 | desde 156 |", "|---|---|---|---|"]
    def c(f, k):
        x = f.get(k)
        return "no computado" if not x else f"{x['mediana']:.1f} % {x['banda_p2_5_p97_5']} (mín–máx {x['min_max']})"
    for j, f in r["resumen"].items():
        L.append(f"| {j} | {c(f, 'pct_anualizado_desde_52')} | {c(f, 'pct_anualizado_desde_104')} | {c(f, 'pct_anualizado_desde_156')} |")
    L.append("\n## Las lecturas acumuladas, con cuántas semillas cruzan el 25 % en CADA horizonte\n")
    L.append("| juego | a 52 semanas | cruzan | a 104 | cruzan | a 156 (corte exacto, no vida entera) | cruzan | congeladas antes de 156 | peor ventana móvil de 52 | con deslizamiento a 156 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for j, f in r["resumen"].items():
        def n(k):
            x = f.get(k) or {}
            return f"{x.get('semillas_que_disparan', '?')} de {x.get('K', '?')}"
        cong = (f.get("pct_a_156_semanas") or {}).get("semillas_congeladas")
        L.append(f"| {j} | {c(f, 'pct_a_52_semanas')} | {n('pct_a_52_semanas')} | {c(f, 'pct_a_104_semanas')} | {n('pct_a_104_semanas')} | "
                 f"{c(f, 'pct_a_156_semanas')} | {n('pct_a_156_semanas')} | {cong} | {c(f, 'pct_peor_ventana_movil_52')} | "
                 f"{c(f, 'pct_con_deslizamiento_a_156_semanas')} |")
    L.append(f"\n**Período:** {r['periodo']}\n")
    L.append(f"**Grado de libertad declarado (E12):** {r['grado_de_libertad_declarado']}.\n")
    L.append("**Semillas congeladas:** una cuenta que dejó de operar (sin caja para una acción entera) acumula poca comisión "
             "por quiebra operativa, no por baratura; su lectura de M2 baja por la razón equivocada (E4). La banda "
             "p2,5–p97,5 de una mezcla bimodal se lee con el mín–máx al lado.\n")
    L.append("Intentos del DSR: 0 (la nula es conocida por construcción). Grado de libertad de criterio: registrado en "
             "`espera_firma.md` §43 (contador de «lecturas de criterio», ubicación a decidir).\n")
    return "\n".join(L)


def main() -> dict:
    r = correr()
    with open(SALIDA + ".json", "w", encoding="utf-8") as f:
        json.dump(r, f, indent=1, ensure_ascii=False, default=float)
    with open(SALIDA + ".md", "w", encoding="utf-8") as f:
        f.write(informe(r))
    print(informe(r))
    return r


if __name__ == "__main__":
    main()
