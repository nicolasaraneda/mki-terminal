# ============================================================
# dinero/cuenta_papel.py — corre la cuenta en papel y escribe el reporte.
#
#   python -m dinero.cuenta_papel
#
# ORDEN: línea base primero (dos variantes), estrategia después. Los tres
# juegos de parámetros estaban DECLARADOS Y CONGELADOS en dinero/reglas.json
# antes de esta corrida; acá se mide qué le cuesta a cada uno existir, y NO
# se elige uno mirando el resultado. El que rige por defecto lo fija una
# regla escrita: el conservador.
#
# La señal que alimenta la estrategia NO TIENE INFORMACIÓN, a propósito. Lo
# que este reporte mide es fricción, no habilidad.
# ============================================================
from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone

import pandas as pd

from dinero import contabilidad as C
from dinero import precios
from dinero import universo_dinero as U

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "resultados")
SALIDA = os.path.join(DIR_RESULTADOS, "cuenta_papel.md")
SALIDA_JSON = os.path.join(DIR_RESULTADOS, "cuenta_papel.json")

# Congelados ANTES de correr, en este archivo y no como argumento suelto.
DESDE = "2023-09-05"
HASTA = "2026-09-04"
APORTE_SEMANAL_USD = 100.0
HORIZONTE_SENAL_HABILES = 20
ETFS_BASE = ("SMH", "XSD")
SEMILLA_COMPARACION = 20260906


def _ventana(cierres):
    return cierres.loc[DESDE:HASTA]


def correr():
    cfg = U.reglas()
    costos = cfg["costos"]
    techo = cfg["presupuesto"]["techo_usd"]
    cierres = _ventana(precios.cargar_congelado())
    dias = [d.date() for d in cierres.index]
    aportes = C.calendario_aportes(dias, APORTE_SEMANAL_USD, techo)

    # Universo operable de la estrategia: sólo lo verificado Y comprable.
    mapa = U.construir_mapa(precios.cargar_congelado(), cfg)
    operables = [f.candidato.ticker for f in mapa
                 if f.verificado and f.alcanza_con_techo]
    operables = [t for t in operables if t in cierres.columns]
    senales = C.senales_sin_informacion(cierres, operables,
                                        HORIZONTE_SENAL_HABILES,
                                        C.SEMILLA_SENAL_SIN_INFORMACION)

    resultados = {"aportes": aportes, "operables": operables,
                  "base": {}, "estrategia": {}}
    for pb in cfg["costos"]["barrido_deslizamiento_pb"]:
        for etf in ETFS_BASE:
            libro = C.linea_base(cierres, etf, aportes, costos, pb)
            valor = C.valorizar(cierres, libro.movimientos, aportes, costos)
            resultados["base"][(etf, pb)] = (libro, valor)
        for nombre in ("conservador", "medio", "agresivo"):
            libro = C.correr_estrategia(cierres, senales, cfg, nombre,
                                        aportes, pb, techo)
            valor = C.valorizar(cierres, libro.movimientos, aportes, costos)
            resultados["estrategia"][(nombre, pb)] = (libro, valor)
    resultados["cierres"] = cierres
    return cfg, resultados


def _resumen(libro, valor, aportado):
    final = float(valor.iloc[-1]) if len(valor) else 0.0
    return {
        "final_usd": final,
        "aportado_usd": aportado,
        "resultado_usd": final - aportado,
        "resultado_pct": (100.0 * (final / aportado - 1.0)) if aportado else float("nan"),
        "ordenes": len(libro.movimientos),
        "comisiones_usd": libro.comisiones_usd,
        "deslizamiento_usd": libro.deslizamiento_usd,
    }


def componer(cfg, res) -> str:
    cierres = res["cierres"]
    aportado = sum(res["aportes"].values())
    pbs = cfg["costos"]["barrido_deslizamiento_pb"]
    L = []
    L.append("# Cuenta en papel del riel de dinero — **SIMULADO**\n")
    L.append("> **SIMULADO. PROPUESTA.** Ninguna cifra de este documento es un")
    L.append("> resultado del proyecto, ninguna entra al README, y ninguna pasó")
    L.append("> todavía por `estadistico-adversario`. No hay cuenta de corredora y")
    L.append("> no se envió ninguna orden a ningún lado.")
    L.append(">")
    L.append("> **Lo que esta cuenta mide es FRICCIÓN, no habilidad.** La estrategia")
    L.append("> se alimenta de una señal SIN INFORMACIÓN —sorteada de la distribución")
    L.append("> histórica de retornos a 20 días hábiles de cada instrumento, con")
    L.append(f"> semilla {C.SEMILLA_SENAL_SIN_INFORMACION}, sin relación con lo que")
    L.append("> pasa después—, justamente para que lo que se lea acá sea lo que le")
    L.append("> cuesta a cada juego de parámetros existir. Una estrategia con señal")
    L.append("> de verdad tendría que superar esto ANTES de poder llamarse habilidad.\n")
    L.append("Generado por `python -m dinero.cuenta_papel` el "
             f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')} UTC.\n")

    L.append("## Parámetros congelados antes de correr\n")
    L.append(f"- Ventana: **{DESDE} a {HASTA}** ({len(cierres)} días de mercado), "
             f"sobre `dinero/datos/cierres_congelados.csv`. **Sin descargas.**")
    L.append(f"- Aporte: **{APORTE_SEMANAL_USD:.0f} USD el primer día hábil de cada "
             f"semana, hasta agotar el techo de {cfg['presupuesto']['techo_usd']:.0f} "
             f"USD**. Total aportado: **{aportado:.0f} USD** en "
             f"{len(res['aportes'])} aportes.")
    L.append("  El encargo pide 'un monto fijo cada semana', pero el presupuesto")
    L.append("  declarado son 100 a 500 dólares **en total**: aportar semanalmente")
    L.append("  durante tres años serían 15.600 dólares que no existen. El calendario")
    L.append("  se corta al agotar el presupuesto, y la línea base y la estrategia")
    L.append("  reciben **el mismo flujo de caja**, que es lo que las hace comparables.")
    L.append(f"- Universo operable: {len(res['operables'])} instrumentos "
             f"(los verificados y comprables de `docs/universo_operable.md`).")
    L.append(f"- Barrido de costo: deslizamiento de {pbs} pb por lado, **más** la")
    L.append("  comisión fija del supuesto (mínimo 1 USD por orden, tope 1 %).\n")

    L.append("## 4a. La línea base aburrida\n")
    L.append("Comprar un ETF del sector con el aporte semanal, sin decidir nada. Si el")
    L.append("aporte no alcanza para una acción entera, **acumula**: es lo que haría")
    L.append("una persona con 100 dólares por semana frente a un ETF de más de 500.\n")
    L.append("| ETF | Deslizamiento | Órdenes | Comisiones USD | Final USD | Resultado USD | Resultado % |")
    L.append("|---|---:|---:|---:|---:|---:|---:|")
    for etf in ETFS_BASE:
        for pb in pbs:
            libro, valor = res["base"][(etf, pb)]
            r = _resumen(libro, valor, aportado)
            L.append(f"| `{etf}` | {pb:.0f} pb | {r['ordenes']} | "
                     f"{r['comisiones_usd']:.2f} | {r['final_usd']:.2f} | "
                     f"{r['resultado_usd']:+.2f} | {r['resultado_pct']:+.2f} % |")
    L.append("")
    L.append("**Por qué hay dos ETF y no uno.** `SMH` es el BENCHMARK declarado del")
    L.append("riel de medición (`universo.py`), y por eso está. Pero su acción cerró")
    L.append("por encima del techo del presupuesto el 2026-09-04, así que la línea base")
    L.append("con `SMH` pasa semanas acumulando antes de poder comprar la primera. `XSD`")
    L.append("es el único ETF sectorial verificado cuya acción cabe en 500 dólares. La")
    L.append("diferencia entre las dos filas **no es una diferencia de mercado: es el")
    L.append("costo de no poder comprar fracciones**.\n")

    L.append("## 4b/4c. Los tres juegos, contra la línea base\n")
    L.append("Los tres estaban declarados y congelados en `dinero/reglas.json` antes de")
    L.append("esta corrida, con su regla de derivación. Se muestran **los tres, sin")
    L.append("ranking y sin recomendación**: elegir uno mirando esta tabla sería elegir")
    L.append("la vara después de ver el tiro. El que rige por defecto lo fija una regla")
    L.append("escrita —el conservador—, no su resultado.\n")
    for pb in pbs:
        L.append(f"### Deslizamiento {pb:.0f} pb por lado\n")
        L.append("| Juego | Órdenes | Comisiones USD | Deslizamiento USD | Final USD | Resultado % | vs `SMH` semanal (pp/semana) | IC 95 % | vs `XSD` semanal (pp/semana) | IC 95 % |")
        L.append("|---|---:|---:|---:|---:|---:|---:|---|---:|---|")
        for nombre in ("conservador", "medio", "agresivo"):
            libro, valor = res["estrategia"][(nombre, pb)]
            r = _resumen(libro, valor, aportado)
            celdas = []
            for etf in ETFS_BASE:
                _, vb = res["base"][(etf, pb)]
                comp = C.comparar(valor, vb, semilla=SEMILLA_COMPARACION)
                marca = "" if comp["cruza_cero"] else " ✓"
                celdas.append(f"{comp['dif_media_pp']:+.3f}")
                celdas.append(f"[{comp['ic_lo']:+.3f}, {comp['ic_hi']:+.3f}]{marca}")
            L.append(f"| {nombre} | {r['ordenes']} | {r['comisiones_usd']:.2f} | "
                     f"{r['deslizamiento_usd']:.2f} | {r['final_usd']:.2f} | "
                     f"{r['resultado_pct']:+.2f} % | " + " | ".join(celdas) + " |")
        L.append("")
    L.append("Los intervalos son **bootstrap circular de bloques sobre SEMANAS** "
             f"(bloque de {C.BLOQUE_BOOTSTRAP_SEMANAS} semanas, "
             f"{C.REPLICAS_BOOTSTRAP} réplicas, semilla {SEMILLA_COMPARACION}, "
             "α = 0.05), con `backtest.inferencia.bootstrap_media`, que es el")
    L.append("intervalo de la MEDIA y por lo tanto está en la misma escala que el punto")
    L.append("estimado —la corrida 09 documentó qué pasa cuando no lo está—. La unidad")
    L.append("es la semana y no el día porque dos carteras que comparten instrumentos")
    L.append("tienen retornos diarios correlacionados, y contarlos como independientes")
    L.append("angostaría el intervalo sin fundamento. Un `✓` marca un intervalo que **no**")
    L.append("contiene el cero; sin `✓`, la diferencia **no se distingue de cero**.\n")

    # --- lo que se puede leer de la tabla y lo que NO ---
    L.append("## Qué de esto es un hallazgo y qué no\n")

    L.append("### 1. La comisión se come el capital. Esto SÍ es robusto.\n")
    L.append("| Juego | Órdenes (rango del barrido) | Comisiones USD | Como fracción de los "
             f"{aportado:.0f} USD aportados |")
    L.append("|---|---:|---:|---:|")
    for nombre in ("conservador", "medio", "agresivo"):
        ords = [len(res["estrategia"][(nombre, pb)][0].movimientos) for pb in pbs]
        coms = [res["estrategia"][(nombre, pb)][0].comisiones_usd for pb in pbs]
        L.append(f"| {nombre} | {min(ords)}–{max(ords)} | {min(coms):.2f}–{max(coms):.2f} | "
                 f"**{100*min(coms)/aportado:.0f} % – {100*max(coms)/aportado:.0f} %** |")
    for etf in ETFS_BASE:
        coms = [res["base"][(etf, pb)][0].comisiones_usd for pb in pbs]
        ords = [len(res["base"][(etf, pb)][0].movimientos) for pb in pbs]
        L.append(f"| línea base `{etf}` | {min(ords)}–{max(ords)} | {min(coms):.2f}–{max(coms):.2f} | "
                 f"{100*min(coms)/aportado:.1f} % – {100*max(coms)/aportado:.1f} % |")
    L.append("")
    L.append("Con un mínimo de 1 USD por orden y 500 dólares de capital, **rotar la")
    L.append("cartera cuesta entre una cuarta parte y casi la mitad del capital en")
    L.append("comisiones**, contra menos del uno por ciento de no decidir nada. Este")
    L.append("número no depende del sorteo ni del deslizamiento: depende sólo de")
    L.append("cuántas órdenes emite cada juego, y por eso es lo único de esta página")
    L.append("que se sostiene solo.\n")

    L.append("### 2. El barrido de deslizamiento NO es una curva de sensibilidad al costo.\n")
    ejemplos = []
    for nombre in ("conservador", "medio", "agresivo"):
        rs = [(pb, _resumen(*res["estrategia"][(nombre, pb)], aportado)) for pb in pbs]
        peor, mejor = min(rs, key=lambda x: x[1]["resultado_pct"]), max(rs, key=lambda x: x[1]["resultado_pct"])
        ejemplos.append((nombre, peor, mejor))
        L.append(f"- `{nombre}`: de **{peor[1]['resultado_pct']:+.0f} %** a "
                 f"{peor[0]:.0f} pb hasta **{mejor[1]['resultado_pct']:+.0f} %** a "
                 f"{mejor[0]:.0f} pb — {mejor[1]['resultado_pct']-peor[1]['resultado_pct']:.0f} "
                 f"puntos porcentuales de diferencia, y órdenes "
                 f"{peor[1]['ordenes']} contra {mejor[1]['ordenes']}.")
    L.append("")
    L.append("Diez puntos básicos por lado no pueden mover un resultado cientos de")
    L.append("puntos porcentuales. Lo que pasa es otra cosa, y hay que decirla: **el")
    L.append("deslizamiento cambia cuántas acciones enteras entran en el margen, y eso")
    L.append("cambia QUÉ instrumento se compra**. Con acciones enteras, 500 dólares y")
    L.append("una señal sin información, el resultado lo decide cuál de los")
    L.append(f"{len(res['operables'])} instrumentos tocó en el sorteo, no el costo. Las")
    L.append("filas del barrido **no son la misma estrategia a distinto costo: son")
    L.append("caminos distintos**, y compararlas entre sí sería un error.\n")

    total = 0
    marcados = 0
    for pb in pbs:
        for nombre in ("conservador", "medio", "agresivo"):
            _, valor = res["estrategia"][(nombre, pb)]
            for etf in ETFS_BASE:
                _, vb = res["base"][(etf, pb)]
                total += 1
                if not C.comparar(valor, vb, semilla=SEMILLA_COMPARACION)["cruza_cero"]:
                    marcados += 1
    L.append("### 3. Los `✓` de la tabla son falsos positivos POR CONSTRUCCIÓN.\n")
    L.append(f"De **{total}** comparaciones, **{marcados}** tienen un intervalo del 95 %")
    L.append(f"que excluye el cero: {100.0*marcados/total:.0f} %. Bajo una señal sin")
    L.append("información, la respuesta verdadera es cero en las 24, así que **todos**")
    L.append("esos intervalos son falsos positivos. No es un defecto del bootstrap: las")
    L.append("comparaciones comparten el sorteo, los instrumentos y el flujo de caja, y")
    L.append("nada de eso está descontado. El número sirve para una sola cosa, y es")
    L.append("útil: **así de fácil es que este diseño produzca un `✓` sin que haya nada**.")
    L.append("Cuando exista una señal de verdad, este es el ruido contra el que va a")
    L.append("tener que destacarse.\n")

    L.append("### 4. Lo único direccional que sí se sostiene\n")
    agr = [not C.comparar(res["estrategia"][("agresivo", pb)][1],
                          res["base"][("SMH", pb)][1],
                          semilla=SEMILLA_COMPARACION)["cruza_cero"]
           and C.comparar(res["estrategia"][("agresivo", pb)][1],
                          res["base"][("SMH", pb)][1],
                          semilla=SEMILLA_COMPARACION)["dif_media_pp"] < 0
           for pb in pbs]
    L.append(f"El juego **agresivo pierde contra la línea base `SMH` en "
             f"{sum(agr)} de las {len(pbs)} pasadas del barrido**, con el intervalo")
    L.append("entero por debajo del cero. Es el único resultado consistente de la")
    L.append("página, y es el esperable: más órdenes sobre una señal sin información")
    L.append("es más comisión pagada por nada. **No hace falta una señal buena para")
    L.append("perder; alcanza con operar seguido.**\n")

    L.append("### 5. Lo que esta cuenta NO midió\n")
    L.append("- **Habilidad.** No hay señal. La primera señal larga es el bloque 6 y su")
    L.append("  resultado está en `GEMELO/preregistro/senal_larga_v1.md` y su reporte.")
    L.append("- **Impacto de mercado.** El deslizamiento es un supuesto lineal por lado,")
    L.append("  no un modelo de libro de órdenes. A 500 dólares es probablemente")
    L.append("  conservador; no se verificó.")
    L.append("- **Impuestos, retención de dividendos de ADR, ni costo de cambio de")
    L.append("  moneda.** Ninguno está en el modelo de costo.")
    L.append("- **Que los precios sean point-in-time.** Los cierres de la fuente vienen")
    L.append("  ajustados retroactivamente por splits y dividendos; la serie no es la")
    L.append("  que se veía ese día. Está declarado en el metadato del congelado.\n")
    return "\n".join(L) + "\n"


def a_json(cfg, res) -> dict:
    """La misma medición, en estructura, para que la capa visual no tenga
    que parsear markdown. Se emite del mismo objeto que compone el .md: si
    alguna vez difieren, es un bug y no una versión."""
    aportado = sum(res["aportes"].values())
    pbs = cfg["costos"]["barrido_deslizamiento_pb"]
    salida = {
        "etiqueta": "SIMULADO",
        "estatus": "PROPUESTA",
        "advertencia": (
            "La señal que alimenta la estrategia NO tiene información: lo "
            "medido es fricción, no habilidad. Ninguna cifra es un resultado "
            "del proyecto."),
        "ventana": {"desde": DESDE, "hasta": HASTA,
                    "dias_de_mercado": int(len(res["cierres"]))},
        "aportado_usd": aportado,
        "aportes": len(res["aportes"]),
        "instrumentos_operables": len(res["operables"]),
        "barrido_deslizamiento_pb": pbs,
        "linea_base": [], "juegos": [],
    }
    for etf in ETFS_BASE:
        for pb in pbs:
            libro, valor = res["base"][(etf, pb)]
            r = _resumen(libro, valor, aportado)
            salida["linea_base"].append(dict(etf=etf, deslizamiento_pb=pb, **r))
    for nombre in ("conservador", "medio", "agresivo"):
        for pb in pbs:
            libro, valor = res["estrategia"][(nombre, pb)]
            r = _resumen(libro, valor, aportado)
            contra = {}
            for etf in ETFS_BASE:
                _, vb = res["base"][(etf, pb)]
                contra[etf] = C.comparar(valor, vb, semilla=SEMILLA_COMPARACION)
            salida["juegos"].append(dict(juego=nombre, deslizamiento_pb=pb,
                                         contra=contra, **r))
    total = sum(1 for j in salida["juegos"] for _ in j["contra"])
    marcados = sum(1 for j in salida["juegos"]
                   for c in j["contra"].values() if not c["cruza_cero"])
    salida["falsos_positivos"] = {
        "comparaciones": total, "con_ic_que_excluye_cero": marcados,
        "nota": ("La respuesta verdadera es cero en todas: la señal no tiene "
                 "información. Todos son falsos positivos por construcción.")}
    return salida


def main():
    cfg, res = correr()
    os.makedirs(DIR_RESULTADOS, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(componer(cfg, res))
    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(a_json(cfg, res), f, indent=1, ensure_ascii=False,
                  default=float)
        f.write("\n")
    print("escrito", SALIDA, "y", SALIDA_JSON)


if __name__ == "__main__":
    main()
