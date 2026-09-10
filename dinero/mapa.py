# ============================================================
# dinero/mapa.py — genera docs/universo_operable.md desde los datos.
#
# El documento NO se escribe a mano. Se genera de los precios congelados y
# del catálogo, para que no pueda desincronizarse: si mañana un precio
# cambia de tramo, el documento cambia al regenerarlo y nadie tiene que
# acordarse de editarlo. Es la misma regla de la casa —la corrección va al
# ejecutable, no a la prosa— aplicada a un documento.
#
#   python -m dinero.mapa            # regenera docs/universo_operable.md
# ============================================================
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from dinero import derivacion, precios
from dinero import universo_dinero as U

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "docs", "universo_operable.md")
SALIDA_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "resultados", "universo_operable.json")

# Bloque 10 de la corrida 11: el censo se computa para estos presupuestos y
# en los DOS modos de compra, porque el presupuesto está sin decidir
# justamente porque el censo se había computado para otro rango (§82.7).
PRESUPUESTOS_USD = (100.0, 250.0, 500.0, 1000.0)
MODOS = (("enteras", False), ("fraccionarias", True))
# Segundo día de censo: otro congelado, con fecha y sha256 como el primero.
# Si no existe, la sección se declara no disponible; nunca se descarga acá.
RUTA_CIERRES_DIA2 = os.path.join(precios.DIR_DATOS, "cierres_congelados_dia2.csv")
RUTA_META_DIA2 = os.path.splitext(RUTA_CIERRES_DIA2)[0] + ".meta.json"


def censo(cierres, cfg) -> dict:
    """El censo por presupuesto × modo: cuántos instrumentos verificados se
    pueden comprar, el estado de cada eslabón, y la fricción de ida y vuelta
    por instrumento. Sale de `construir_mapa` con sus dos parámetros nuevos;
    no hay una segunda fuente de verdad."""
    salida = {"presupuestos_usd": list(PRESUPUESTOS_USD), "celdas": [], "instrumentos": {}}
    for presupuesto in PRESUPUESTOS_USD:
        for nombre_modo, frac in MODOS:
            filas = U.construir_mapa(cierres, cfg, presupuesto=presupuesto, fraccionarias=frac)
            por_eslabon = {e.clave: [f for f in filas if f.candidato.eslabon == e.clave]
                           for e in U.ESLABONES}
            estados = [U.estado_del_eslabon(por_eslabon[e.clave]) for e in U.ESLABONES]
            estrictos = [U.estado_del_eslabon(por_eslabon[e.clave], True) for e in U.ESLABONES]
            verificados = [f for f in filas if f.verificado]
            salida["celdas"].append({
                "presupuesto_usd": presupuesto, "modo": nombre_modo,
                "verificados": len(verificados),
                "alcanzables": sum(1 for f in verificados if f.alcanza_con_techo),
                "representados": estados.count("REPRESENTADO"),
                "sustituidos": estados.count("SUSTITUIDO"),
                "huecos": estados.count("HUECO"),
                "representados_exigiendo_liquidez": estrictos.count("REPRESENTADO"),
                "sustituidos_exigiendo_liquidez": estrictos.count("SUSTITUIDO"),
                "huecos_exigiendo_liquidez": estrictos.count("HUECO"),
                "al_borde": [f.candidato.ticker for f in verificados
                             if not frac and not f.alcanza_con_techo
                             and f.precio <= presupuesto],
            })
            for f in verificados:
                d = salida["instrumentos"].setdefault(f.candidato.ticker, {
                    "precio_usd": f.precio, "eslabon": f.candidato.eslabon,
                    "rol": f.candidato.rol, "celdas": {}})
                d["celdas"][f"{presupuesto:.0f}_{nombre_modo}"] = {
                    "unidades": f.acciones_con_techo,
                    "alcanza": f.alcanza_con_techo,
                    "friccion_ida_vuelta_usd": f.friccion_ida_vuelta_usd,
                    "friccion_ida_vuelta_pct": f.friccion_ida_vuelta_pct,
                }
    return salida


def _seccion_censo(cen: dict, cfg: dict) -> list:
    c = cfg["costos"]
    fr = c.get("fraccionarias_no_usadas", {})
    L = []
    L.append("## Censo por presupuesto y modo de compra (corrida 11, bloque 10)\n")
    L.append("El presupuesto del riel quedó sin decidir porque el censo original se computó")
    L.append("con piso de 100 USD y acciones enteras (§82.7). Acá el modo de compra y el")
    L.append("presupuesto son **parámetros explícitos** y el censo se produce para los")
    L.append(f"cuatro montos en discusión. Arancel del insumo §40: enteras "
             f"{c['comision_por_accion_usd']} USD/acción, mínimo {c['comision_minima_usd']:.2f} USD, "
             f"tope {c['comision_tope_pct_del_monto']} %; fraccionarias "
             f"{fr.get('comision_pct_del_monto', '?')} % del monto, mínimo {fr.get('comision_minima_usd', '?')} USD.")
    L.append("«Alcanzable» = con ese presupuesto entra al menos una unidad, comisión incluida.")
    L.append("Con fraccionarias todo instrumento con precio es alcanzable por construcción:")
    L.append("lo que separa los modos no es el alcance sino la **fricción**.\n")
    L.append("| Presupuesto | Modo | Alcanzables | Representados / sustituidos / huecos | Exigiendo liquidez | Casos al borde (enteras) |")
    L.append("|---:|---|---:|---|---|---|")
    for x in cen["celdas"]:
        L.append(f"| {x['presupuesto_usd']:.0f} USD | {x['modo']} | **{x['alcanzables']} de {x['verificados']}** | "
                 f"{x['representados']} / {x['sustituidos']} / {x['huecos']} | "
                 f"{x['representados_exigiendo_liquidez']} / {x['sustituidos_exigiendo_liquidez']} / "
                 f"{x['huecos_exigiendo_liquidez']} | {', '.join('`%s`' % t for t in x['al_borde']) or '—'} |")
    L.append("")
    L.append("### Fricción de ida y vuelta por instrumento\n")
    L.append("Comisión de compra más comisión de venta, sin deslizamiento, para una posición")
    L.append("que usa el presupuesto entero en ese instrumento. Enteras: «unidades (fricción %)».")
    L.append("Fraccionarias: la fricción es la misma a cualquier presupuesto y se muestra una vez.\n")
    cab = "| Ticker | Cierre USD | " + " | ".join(f"{p:.0f} USD enteras" for p in cen["presupuestos_usd"]) + " | fraccionarias |"
    L.append(cab)
    L.append("|---|---:|" + "---:|" * len(cen["presupuestos_usd"]) + "---:|")
    for t, d in sorted(cen["instrumentos"].items()):
        celdas = []
        for p in cen["presupuestos_usd"]:
            x = d["celdas"][f"{p:.0f}_enteras"]
            celdas.append(f"{x['unidades']} ({x['friccion_ida_vuelta_pct']:.2f} %)" if x["alcanza"] else "**0**")
        xf = d["celdas"][f"{cen['presupuestos_usd'][0]:.0f}_fraccionarias"]
        L.append(f"| `{t}` | {d['precio_usd']:,.2f} | " + " | ".join(celdas) +
                 f" | {xf['friccion_ida_vuelta_pct']:.2f} % |")
    L.append("")
    L.append("**Lectura, y lo que no se puede leer.** La fricción de enteras es un peaje fijo")
    L.append("(0,70 USD de ida y vuelta mientras la orden tenga menos de 100 acciones) y se")
    L.append("diluye con el tamaño; la de fraccionarias es proporcional y no se diluye. El")
    L.append("cruce está en 35 USD por orden (§40 §6). Esto es aritmética del arancel, no una")
    L.append("medición: las tarifas de terceros y de bolsa por venue no están, y la liquidez de")
    L.append("los ADR de mostrador sigue sin verificar. **La decisión del presupuesto se toma")
    L.append("con esta tabla a la vista y es de Nicolás**; este documento no la recomienda.\n")
    return L


def comparar_dias(cierres_dia1, cierres_dia2, cfg) -> dict:
    """Segundo día de censo: qué cambió entre los dos congelados. La
    comparación es el dato, no el segundo día solo."""
    salida = {"instrumentos": [], "cambios_de_alcance": []}
    for presupuesto in PRESUPUESTOS_USD:
        m1 = {f.candidato.ticker: f for f in U.construir_mapa(cierres_dia1, cfg, presupuesto=presupuesto)}
        m2 = {f.candidato.ticker: f for f in U.construir_mapa(cierres_dia2, cfg, presupuesto=presupuesto)}
        for t in sorted(set(m1) & set(m2)):
            a, b = m1[t], m2[t]
            if a.verificado and b.verificado and a.alcanza_con_techo != b.alcanza_con_techo:
                salida["cambios_de_alcance"].append({
                    "ticker": t, "presupuesto_usd": presupuesto,
                    "dia1": a.alcanza_con_techo, "dia2": b.alcanza_con_techo,
                    "precio_dia1": a.precio, "precio_dia2": b.precio})
    m1 = {f.candidato.ticker: f for f in U.construir_mapa(cierres_dia1, cfg)}
    m2 = {f.candidato.ticker: f for f in U.construir_mapa(cierres_dia2, cfg)}
    for t in sorted(set(m1) & set(m2)):
        a, b = m1[t], m2[t]
        if a.verificado and b.verificado:
            salida["instrumentos"].append({
                "ticker": t, "precio_dia1": a.precio, "fecha_dia1": a.fecha_precio,
                "precio_dia2": b.precio, "fecha_dia2": b.fecha_precio,
                "variacion_pct": 100.0 * (b.precio / a.precio - 1.0)})
        elif a.verificado != b.verificado:
            salida["cambios_de_alcance"].append({"ticker": t, "presupuesto_usd": None,
                                                 "dia1": a.verificado, "dia2": b.verificado,
                                                 "nota": "cambió la VERIFICACIÓN, no el precio"})
    return salida


def _seccion_dia2(cfg, cierres_dia1) -> list:
    L = ["## El segundo congelado no aportó sesión: el censo sigue siendo de un solo día\n"]
    if not os.path.exists(RUTA_CIERRES_DIA2):
        L.append("**No disponible:** no hay segundo congelado en "
                 "`dinero/datos/cierres_congelados_dia2.csv`. El censo sigue siendo de un solo día.\n")
        return L
    cierres2 = precios.cargar_congelado(RUTA_CIERRES_DIA2)
    meta2 = precios.meta_congelado(RUTA_META_DIA2)
    meta1 = precios.meta_congelado()
    comp = comparar_dias(cierres_dia1, cierres2, cfg)
    if meta1.get("hasta") == meta2.get("hasta"):
        L.append(f"**Los dos congelados terminan en la MISMA sesión ({meta1.get('hasta')}): el segundo")
        L.append("congelado no aporta una sesión nueva y esto NO cuenta como segundo día de censo.**")
        L.append("Se deja registrado con su fecha y su sha256 para que la comparación se pueda")
        L.append("repetir cuando exista una sesión posterior; hasta entonces el censo sigue siendo")
        L.append("de un solo día.\n")
    L.append(f"Día 1: congelado {meta1.get('congelado_en_utc','?')} UTC, hasta {meta1.get('hasta','?')}, "
             f"sha256 `{meta1.get('sha256','?')[:16]}…`. Día 2: congelado {meta2.get('congelado_en_utc','?')} UTC, "
             f"hasta {meta2.get('hasta','?')}, sha256 `{meta2.get('sha256','?')[:16]}…`. "
             f"**La comparación entre los dos días es el dato, no el segundo día solo.**\n")
    if comp["cambios_de_alcance"]:
        L.append("| Ticker | Presupuesto | Día 1 | Día 2 | Precio día 1 | Precio día 2 |")
        L.append("|---|---:|---|---|---:|---:|")
        for x in comp["cambios_de_alcance"]:
            L.append(f"| `{x['ticker']}` | {x['presupuesto_usd'] or '—'} | {x['dia1']} | {x['dia2']} | "
                     f"{x.get('precio_dia1', float('nan')):,.2f} | {x.get('precio_dia2', float('nan')):,.2f} |")
        L.append("")
        L.append(f"**{len(comp['cambios_de_alcance'])} cambio(s) de alcance** entre los dos días: son los casos al "
                 "borde haciendo lo que se declaró que harían.\n")
    elif meta1.get("hasta") == meta2.get("hasta"):
        L.append("La comparación entre los dos congelados es **trivialmente idéntica** (misma sesión final) y")
        L.append("no verifica estabilidad de nada; se deja el sha256 para repetirla cuando exista una sesión")
        L.append("posterior.\n")
    else:
        L.append("**Ningún instrumento cambió de alcance** en ninguno de los cuatro presupuestos "
                 "(acciones enteras). Los casos al borde declarados no cruzaron.\n")
    vs = [x["variacion_pct"] for x in comp["instrumentos"]]
    if vs and meta1.get("hasta") != meta2.get("hasta"):
        L.append(f"Variación de precio entre los dos días sobre {len(vs)} instrumentos: mínima "
                 f"{min(vs):+.2f} %, máxima {max(vs):+.2f} %, mediana "
                 f"{sorted(vs)[len(vs)//2]:+.2f} %.\n")
    return L


def _tabla_eslabon(e, filas, cfg):
    out = []
    estado = U.estado_del_eslabon(filas)
    estricto = U.estado_del_eslabon(filas, exigir_liquidez=True)
    rotulo = estado if estado == estricto else f"{estado} · {estricto} exigiendo liquidez"
    out.append(f"### {e.nombre} — **{rotulo}**\n")
    out.append(f"*Quién domina (CONTEXTO NO VERIFICADO):* {e.dominante}  ")
    out.append(f"*Obstáculo:* {e.obstaculo}\n")
    out.append("| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |")
    out.append("|---|---|---|---|---:|:---:|:---:|---:|---:|")
    for f in sorted(filas, key=lambda f: (f.candidato.rol != "dominante",
                                          f.candidato.ticker)):
        c = f.candidato
        if not f.verificado:
            out.append(f"| `{c.ticker}` | {c.nombre} | {c.forma} | {c.rol} | "
                       f"**NO VERIFICADO** | — | — | — | — |")
            continue
        cabe1 = "sí" if f.alcanza_con_techo else "**no**"
        cabe500 = f"{f.acciones_con_techo}" if f.acciones_con_techo else "**0**"
        ct = (f"{f.comision_orden_techo_pct:.2f} %"
              if f.comision_orden_techo_pct is not None else "—")
        out.append(f"| `{c.ticker}` | {c.nombre} | {c.forma} | {c.rol} | "
                   f"{f.precio:,.2f} | {cabe1} | {cabe500} | "
                   f"{f.comision_orden_minima_pct:.2f} % | {ct} |")
    out.append("")
    for f in sorted(filas, key=lambda f: f.candidato.ticker):
        c = f.candidato
        if c.sustituye_a:
            out.append(f"- **`{c.ticker}` sustituye a {c.sustituye_a}.** {c.diferencia}")
        if c.liquidez_no_verificada:
            out.append(f"- **`{c.ticker}`: liquidez NO verificada.** Esta corrida "
                       f"comprobó que devuelve precio, nada más. Que una orden "
                       f"se llene a un diferencial razonable no se puede "
                       f"afirmar desde un cierre.")
        if c.nota:
            out.append(f"- `{c.ticker}`: {c.nota}")
    huecos = [x for x in U.NO_COMPRABLES if x[0] == e.clave]
    if huecos:
        out.append("")
        out.append("**Huecos declarados de este eslabón** (no se tapan con un sustituto):")
        for _, quien, clase, por_que in huecos:
            out.append(f"- *{quien}* — {clase}. {por_que}")
    out.append("")
    return out


def componer() -> str:
    cfg = U.reglas()
    cierres = precios.cargar_congelado()
    meta = precios.meta_congelado()
    filas = U.construir_mapa(cierres, cfg)
    por_eslabon = {e.clave: [f for f in filas if f.candidato.eslabon == e.clave]
                   for e in U.ESLABONES}
    techo = cfg["presupuesto"]["techo_usd"]
    piso = cfg["presupuesto"]["piso_usd"]

    estados = {e.clave: U.estado_del_eslabon(por_eslabon[e.clave]) for e in U.ESLABONES}
    estrictos = {e.clave: U.estado_del_eslabon(por_eslabon[e.clave], True)
                 for e in U.ESLABONES}
    def cuenta(d, v):
        return sum(1 for x in d.values() if x == v)

    verificados = [f for f in filas if f.verificado]
    no_verificados = [f for f in filas if not f.verificado]
    cabe_piso = [f for f in verificados if f.alcanza_con_piso]

    L = []
    L.append("# Universo operable — qué eslabón se puede comprar de verdad\n")
    L.append("> **SIMULADO / PROPUESTA.** No hay cuenta de corredora abierta y este")
    L.append("> documento no es una recomendación de compra. Es el mapa del **riel de")
    L.append("> dinero** (ver `VISION.md`): qué eslabón de la cadena se puede comprar")
    L.append("> desde Chile con el presupuesto declarado, y cuál no.")
    L.append(">")
    L.append("> **Generado por `python -m dinero.mapa`, no escrito a mano.** Los precios")
    L.append(f"> salen de `dinero/datos/cierres_congelados.csv` (congelado")
    L.append(f"> {meta.get('congelado_en_utc','?')} UTC, sha256 `{meta.get('sha256','?')[:16]}…`,")
    L.append(f"> {meta.get('filas','?')} filas, {meta.get('desde','?')} a {meta.get('hasta','?')}).")
    L.append(f"> Regenerado el {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.\n")

    L.append("## Las dos clases de afirmación de este documento\n")
    L.append("1. **VERIFICADO POR LA MÁQUINA** — que el ticker existe y devuelve precio.")
    L.append("   Ningún ticker de las tablas se escribió de memoria: entró sólo si la")
    L.append("   descarga trajo al menos un cierre. Los que no, están en la lista de no")
    L.append("   verificados con su razón.")
    L.append("2. **CONTEXTO NO VERIFICADO** — quién domina cada eslabón. Es conocimiento")
    L.append("   de fondo, no una medición de esta corrida, y va rotulado así en cada")
    L.append("   sección. Un lector no tiene por qué distinguirlo solo.\n")
    L.append("Una tercera cosa que este documento **no** afirma: que una orden se llene.")
    L.append("Un cierre demuestra que el instrumento cotiza, no que sea líquido.\n")

    L.append("## El supuesto de costo, a la vista\n")
    c = cfg["costos"]
    L.append(f"- Comisión: {c['comision_por_accion_usd']} USD por acción, mínimo")
    L.append(f"  {c['comision_minima_usd']:.2f} USD por orden, tope {c['comision_tope_pct_del_monto']} %")
    L.append(f"  del monto. Deslizamiento supuesto: {c['deslizamiento_pb_por_lado']} pb por lado.")
    L.append("- **Arancel PUBLICADO, no supuesto** (desde el 8-sep-2026): es la columna de")
    L.append("  acciones enteras del insumo del §40 (`GEMELO/propuestas/insumo_40_aranceles_*.md`,")
    L.append("  Pro Tiered, consultado el 7-sep-2026). El insumo es PROPUESTA y espera firma;")
    L.append("  hasta el 7-sep esto era un supuesto sin verificar (0,005 / 1,00 USD / 1 %).")
    L.append(f"- Consecuencia aritmética que ordena el mapa: **con mínimo de {c['comision_minima_usd']:.2f} USD y")
    L.append(f"  tope de {c['comision_tope_pct_del_monto']} %, el cruce está en "
             f"{100.0 * c['comision_minima_usd'] / c['comision_tope_pct_del_monto']:.0f} USD por orden**: por debajo")
    L.append("  manda el tope proporcional, por encima el mínimo fijo.")
    L.append("- Las tablas por eslabón asumen **acciones enteras** con el techo de reglas.json;")
    L.append("  el censo por presupuesto y modo de compra (más abajo) computa también")
    L.append("  fraccionarias.\n")

    L.append("## Resumen\n")
    L.append(f"- Presupuesto declarado: {piso:.0f} a {techo:.0f} USD.")
    L.append(f"- Instrumentos candidatos: {len(filas)}. **Verificados: {len(verificados)}.** "
             f"No verificados: {len(no_verificados)}.")
    L.append(f"- Instrumentos de los que alcanza para **una acción con {techo:.0f} USD**: "
             f"{sum(1 for f in verificados if f.alcanza_con_techo)} de {len(verificados)}.")
    L.append(f"- Con el **piso** de {piso:.0f} USD: {len(cabe_piso)} de {len(verificados)}.")
    L.append("")
    L.append("| Eslabón | Estado | Exigiendo liquidez verificada |")
    L.append("|---|---|---|")
    for e in U.ESLABONES:
        L.append(f"| {e.nombre} | **{estados[e.clave]}** | {estrictos[e.clave]} |")
    L.append("")
    L.append(f"**Frase con estatus evidencial (MEDIDO el {meta.get('hasta','?')}, "
             f"sobre {len(verificados)} instrumentos verificados):** de los "
             f"{len(U.ESLABONES)} eslabones, **{cuenta(estados,'REPRESENTADO')} quedan "
             f"representados, {cuenta(estados,'SUSTITUIDO')} sustituidos y "
             f"{cuenta(estados,'HUECO')} huecos a {cfg['presupuesto']['techo_usd']:.0f} USD en acciones enteras** "
             f"(censo de un solo día: a otros presupuestos el conteo es otro, ver la tabla por presupuesto). Exigiendo además que el instrumento "
             f"tenga liquidez verificada —que esta corrida NO verificó para los ADR de "
             f"mostrador— pasan a ser **{cuenta(estrictos,'REPRESENTADO')} representados, "
             f"{cuenta(estrictos,'SUSTITUIDO')} sustituidos y "
             f"{cuenta(estrictos,'HUECO')} huecos a {cfg['presupuesto']['techo_usd']:.0f} USD en acciones enteras**.\n")
    L.append("«Representado» significa aquí *un instrumento dominante comprable con el")
    L.append("techo del presupuesto*, no *un instrumento listado*: un dominante que")
    L.append("cotiza pero cuya acción cuesta más de lo que hay no representa nada. La")
    L.append("regla se escribió antes de mirar los precios y está fijada en un test")
    L.append("(`tests/test_dinero.py::test_el_estado_de_un_eslabon_sigue_la_regla_escrita`).\n")

    caros = sorted([f for f in verificados if not f.alcanza_con_techo],
                   key=lambda f: -f.precio)
    if caros:
        L.append("### Lo que el presupuesto deja afuera\n")
        L.append(f"Instrumentos verificados que **no entran en {techo:.0f} USD**. El")
        L.append("criterio es **precio más comisión**, no el precio solo: por eso hay")
        L.append("instrumentos acá cuyo precio está por debajo del techo.\n")
        for f in caros:
            borde = ""
            if f.precio <= techo:
                borde = (f" **Caso al borde:** su precio ({f.precio:,.2f}) está por"
                         f" DEBAJO del techo; lo que no entra es precio más comisión.")
            L.append(f"- `{f.candidato.ticker}` — {f.candidato.nombre}: "
                     f"{f.precio:,.2f} USD. Rol declarado: {f.candidato.rol}.{borde}")
        L.append("")
        L.append("**El censo es de un solo día** (los cierres del congelado) y por eso")
        L.append("los casos al borde van declarados: a centavos del techo, la respuesta")
        L.append("cambia con el cierre siguiente. Los que no están al borde sí son")
        L.append("afirmaciones estables.")
        L.append("")

    L.append("## Eslabón por eslabón\n")
    for e in U.ESLABONES:
        L.extend(_tabla_eslabon(e, por_eslabon[e.clave], cfg))

    L.append("## Dominantes que no se pueden comprar\n")
    L.append("La empresa privada no es comprable, y la que cotiza sólo fuera de Estados")
    L.append("Unidos tampoco lo es con este presupuesto y esta cuenta. Se declara a quién")
    L.append("se le compra en su lugar, y en qué se diferencia.\n")
    L.append("| Eslabón | Quién domina | Por qué no se compra | A quién se le compra en su lugar |")
    L.append("|---|---|---|---|")
    for clave, quien, clase, por_que in U.NO_COMPRABLES:
        sust = [f.candidato.ticker for f in por_eslabon[clave]
                if f.verificado and f.alcanza_con_techo]
        L.append(f"| {U.ESLABONES_POR_CLAVE[clave].nombre} | {quien} | {clase}: {por_que} | "
                 f"{', '.join('`%s`' % t for t in sust) or '**nada: hueco**'} |")
    L.append("")

    if no_verificados:
        L.append("## No verificados\n")
        L.append("No entran a las tablas de arriba. Se listan con su razón, que es la")
        L.append("única forma de que un candidato descartado no desaparezca sin dejar rastro.\n")
        for f in no_verificados:
            L.append(f"- `{f.candidato.ticker}` ({f.candidato.nombre}): "
                     f"{f.razon_no_verificado}")
        L.append("")
    else:
        L.append("## No verificados\n")
        L.append("**Ninguno.** Los %d candidatos devolvieron al menos un cierre.\n"
                 % len(filas))

    L.extend(_seccion_censo(censo(cierres, cfg), cfg))
    L.extend(_seccion_dia2(cfg, cierres))

    L.append("## Lo que este mapa NO resuelve\n")
    L.append("- **La liquidez de los ADR de mostrador** (`SHECY`, `TOELY`). Devuelven")
    L.append("  precio; el diferencial de compra-venta no se midió.")
    L.append("- **El arancel real, medido en una cuenta.** El costo de arriba es el arancel")
    L.append("  PUBLICADO del insumo §40, no el observado en una orden real: faltan tarifas de")
    L.append("  terceros y de bolsa por venue, y el insumo espera firma.")
    L.append("- **El tratamiento tributario** de dividendos de ADR para un residente")
    L.append("  chileno, que cambia el retorno neto y no es objeto de esta corrida.")
    L.append("- **Que comprar un eslabón sea buena idea.** Este documento dice qué se")
    L.append("  puede comprar, no qué conviene comprar. Lo segundo depende de una señal")
    L.append("  que el proyecto todavía no tiene.")
    return "\n".join(L) + "\n"


def a_json() -> dict:
    """El mismo mapa, en estructura, para la capa visual. Sale del mismo
    `construir_mapa` que el documento: no hay dos fuentes."""
    cfg = U.reglas()
    cierres = precios.cargar_congelado()
    meta = precios.meta_congelado()
    filas = U.construir_mapa(cierres, cfg)
    eslabones = []
    for e in U.ESLABONES:
        fe = [f for f in filas if f.candidato.eslabon == e.clave]
        eslabones.append({
            "clave": e.clave, "nombre": e.nombre,
            "dominante_contexto_no_verificado": e.dominante,
            "obstaculo": e.obstaculo,
            "estado": U.estado_del_eslabon(fe),
            "estado_exigiendo_liquidez": U.estado_del_eslabon(fe, True),
            "huecos": [{"quien": q, "clase": c, "por_que": p}
                       for cl, q, c, p in U.NO_COMPRABLES if cl == e.clave],
            "instrumentos": [{
                "ticker": f.candidato.ticker, "nombre": f.candidato.nombre,
                "forma": f.candidato.forma, "rol": f.candidato.rol,
                "sustituye_a": f.candidato.sustituye_a,
                "diferencia": f.candidato.diferencia,
                "liquidez_no_verificada": f.candidato.liquidez_no_verificada,
                "verificado": f.verificado,
                "razon_no_verificado": f.razon_no_verificado,
                "precio_usd": f.precio, "fecha_precio": f.fecha_precio,
                "alcanza_con_techo": f.alcanza_con_techo,
                "alcanza_con_piso": f.alcanza_con_piso,
                "acciones_con_techo": f.acciones_con_techo,
                "comision_orden_minima_pct": f.comision_orden_minima_pct,
                "comision_orden_techo_pct": f.comision_orden_techo_pct,
            } for f in sorted(fe, key=lambda f: (f.candidato.rol != "dominante",
                                                 f.candidato.ticker))],
        })
    estados = [e["estado"] for e in eslabones]
    estrictos = [e["estado_exigiendo_liquidez"] for e in eslabones]
    cen = censo(cierres, cfg)
    dia2 = None
    if os.path.exists(RUTA_CIERRES_DIA2):
        dia2 = {"meta": precios.meta_congelado(RUTA_META_DIA2),
                **comparar_dias(cierres, precios.cargar_congelado(RUTA_CIERRES_DIA2), cfg)}
    return {
        "censo_por_presupuesto_y_modo": cen,
        "segundo_dia": dia2,
        # Dos estatus, porque son dos afirmaciones distintas y el mismo
        # generador las escribía con una sola etiqueta: el .md decía
        # "SIMULADO / PROPUESTA" y el .json decía "MEDIDO", y era el
        # permisivo el que llegaba al badge de la vista /operable.
        # Exigencia 12 del `curador-epistemico`, corrida 10.
        "estatus": "SIMULADO",
        "estatus_de_los_precios": ("MEDIDO al %s sobre el archivo congelado"
                                   % meta.get("hasta", "?")),
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fuente": {"archivo": "dinero/datos/cierres_congelados.csv", **meta},
        "presupuesto": cfg["presupuesto"], "costos": cfg["costos"],
        "eslabones": eslabones,
        "resumen": {
            "candidatos": len(filas),
            "verificados": sum(1 for f in filas if f.verificado),
            "representados": estados.count("REPRESENTADO"),
            "sustituidos": estados.count("SUSTITUIDO"),
            "huecos": estados.count("HUECO"),
            "representados_exigiendo_liquidez": estrictos.count("REPRESENTADO"),
            "sustituidos_exigiendo_liquidez": estrictos.count("SUSTITUIDO"),
            "huecos_exigiendo_liquidez": estrictos.count("HUECO"),
        },
    }


def main():
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    os.makedirs(os.path.dirname(SALIDA_JSON), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(componer())
    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(a_json(), f, indent=1, ensure_ascii=False, default=float)
        f.write("\n")
    print(f"escrito {SALIDA} y {SALIDA_JSON}")


if __name__ == "__main__":
    main()
