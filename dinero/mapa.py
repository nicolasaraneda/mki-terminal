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

import os
from datetime import datetime, timezone

from dinero import derivacion, precios
from dinero import universo_dinero as U

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "docs", "universo_operable.md")


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
    L.append("- **SUPUESTO NO VERIFICADO.** No hay cuenta abierta, así que no hay")
    L.append("  tarifario que leer. Confirmarlo contra el arancel público del corredor")
    L.append("  que se abra es un ítem de firma (`GEMELO/resultados/espera_firma.md`).")
    L.append("- Consecuencia aritmética que ordena todo el mapa: **con mínimo de 1 USD y")
    L.append("  tope de 1 %, una orden de UNA acción de menos de 100 USD paga")
    L.append("  exactamente el 1 %.** La comisión no es un detalle a este tamaño de")
    L.append("  cuenta: es el primer obstáculo.")
    L.append("- Se asumen **acciones enteras**. Las fraccionarias dependen del corredor y")
    L.append("  no hay corredor.\n")

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
             f"{cuenta(estados,'HUECO')} huecos**. Exigiendo además que el instrumento "
             f"tenga liquidez verificada —que esta corrida NO verificó para los ADR de "
             f"mostrador— pasan a ser **{cuenta(estrictos,'REPRESENTADO')} representados, "
             f"{cuenta(estrictos,'SUSTITUIDO')} sustituidos y "
             f"{cuenta(estrictos,'HUECO')} huecos**.\n")
    L.append("«Representado» significa aquí *un instrumento dominante comprable con el")
    L.append("techo del presupuesto*, no *un instrumento listado*: un dominante que")
    L.append("cotiza pero cuya acción cuesta más de lo que hay no representa nada. La")
    L.append("regla se escribió antes de mirar los precios y está fijada en un test")
    L.append("(`tests/test_dinero.py::test_el_estado_de_un_eslabon_sigue_la_regla_escrita`).\n")

    caros = sorted([f for f in verificados if not f.alcanza_con_techo],
                   key=lambda f: -f.precio)
    if caros:
        L.append("### Lo que el presupuesto deja afuera\n")
        L.append(f"Instrumentos verificados cuya **acción sola cuesta más de {techo:.0f} USD**:\n")
        for f in caros:
            L.append(f"- `{f.candidato.ticker}` — {f.candidato.nombre}: "
                     f"{f.precio:,.2f} USD. Rol declarado: {f.candidato.rol}.")
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

    L.append("## Lo que este mapa NO resuelve\n")
    L.append("- **La liquidez de los ADR de mostrador** (`SHECY`, `TOELY`). Devuelven")
    L.append("  precio; el diferencial de compra-venta no se midió.")
    L.append("- **El arancel real.** Todo el costo de arriba es un supuesto declarado.")
    L.append("- **El tratamiento tributario** de dividendos de ADR para un residente")
    L.append("  chileno, que cambia el retorno neto y no es objeto de esta corrida.")
    L.append("- **Que comprar un eslabón sea buena idea.** Este documento dice qué se")
    L.append("  puede comprar, no qué conviene comprar. Lo segundo depende de una señal")
    L.append("  que el proyecto todavía no tiene.")
    return "\n".join(L) + "\n"


def main():
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(componer())
    print(f"escrito {SALIDA}")


if __name__ == "__main__":
    main()
