# ============================================================
# Job autónomo de noticias (Etapa 5.0 WS2.4) — com.mki.noticias, ~17:50
# hábiles, ANTES del snapshot de las 18:15 (así el sentimiento sellado
# refleja titulares del día, no un eco congelado).
#
# Entrypoint FINO sobre noticias.py: el RSS, la deduplicación, el matching
# estricto y el análisis por lotes son EXACTAMENTE los existentes — cero
# cambios de lógica interna. Lo que este script agrega:
#   · guardarraíl de presupuesto con freno duro ENTRE lotes + aviso Telegram,
#   · registro de costo por corrida y acumulado del día (costos.py),
#   · reintento breve del RSS (2 intentos, 60 s) — la red a medias del
#     DarkWake fue la causa raíz de la auditoría 13–24 jul,
#   · salida con timestamps → data/noticias.log (vía launchd).
# ============================================================

import os
import socket
import sys
import time
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

import costos  # noqa: E402
from seguridad import enmascarar_secretos  # noqa: E402

# Etapa 5.0.2 — un fetch jamás puede colgarse para siempre. El 3-ago un
# socket hacia Yahoo que nunca murió dejó este proceso vivo 4 días con la
# corrida a medias, y launchd no re-dispara un label mientras su proceso
# siga vivo: noticias "no corrió" del 4 al 7 de agosto. feedparser usa
# urllib SIN timeout — el default global del módulo socket es la única
# palanca que lo cubre sin tocar noticias.py. Anthropic (600 s) y Telegram
# (10 s) fijan su timeout explícito por socket y no se ven afectados.
TIMEOUT_RED_SEG = 30
socket.setdefaulttimeout(TIMEOUT_RED_SEG)

TAM_LOTE = 20
HOLGURA_RESUMEN_USD = 0.05     # el resumen del día solo si queda esta holgura
COSTO_RESUMEN_ESTIMADO = 0.01  # generar_resumen_dia no expone usage: estimación conservadora


def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def _avisar_telegram(texto: str) -> None:
    import alertas
    ok, detalle = alertas.enviar_mensaje(texto)
    _log(f"aviso Telegram: {'enviado' if ok else 'NO enviado — ' + detalle}")


def main() -> int:
    from registro import rotar_log
    rotar_log(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "noticias.log"))
    import alertas  # noqa: F401 (carga temprana: falla visible si falta requests)
    import noticias

    estado = costos.estado_presupuesto()
    _log(f"mki_noticias.py — gasto hoy {estado['gasto_usd']:.4f} / "
         f"tope {estado['tope_usd']:.2f} USD")

    # 1) RSS (gratis) con reintento breve
    nuevos = None
    for intento in (1, 2):
        try:
            nuevos = noticias.actualizar_titulares()
            break
        except Exception as e:
            _log(f"RSS falló (intento {intento}/2): {enmascarar_secretos(str(e))}")
            if intento == 1:
                time.sleep(60)
    if nuevos is None:
        costos.registrar_corrida("noticias", 0.0, {"resultado": "rss_fallo"})
        return 1
    _log(f"titulares nuevos guardados: {nuevos}")

    # 2) freno duro ANTES de gastar un centavo
    if estado["agotado"]:
        _log(f"FRENO: presupuesto diario ya agotado — no se analiza nada")
        _avisar_telegram(
            f"⛔ <b>MKI — freno de presupuesto</b>\n"
            f"El análisis de noticias no corrió: ya se gastaron "
            f"{estado['gasto_usd']:.2f} de {estado['tope_usd']:.2f} USD hoy. "
            f"El tope vive en .env (NOTICIAS_PRESUPUESTO_USD_DIA).")
        costos.registrar_corrida("noticias", 0.0, {
            "resultado": "freno_presupuesto", "titulares_nuevos": nuevos})
        return 0

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        _log("sin ANTHROPIC_API_KEY en .env — solo RSS, sin análisis")
        costos.registrar_corrida("noticias", 0.0, {
            "resultado": "sin_clave", "titulares_nuevos": nuevos})
        return 0
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    # 3) análisis por lotes con freno duro ENTRE lotes. Mismo cuerpo que
    #    noticias.analizar_pendientes(), desplegado aquí SOLO para poder
    #    chequear el presupuesto entre lote y lote sin cambiar la lógica
    #    interna de noticias.py (decisión documentada en DECISIONES.md).
    conn = noticias.get_connection()
    pendientes = noticias.obtener_titulares_sin_analizar(conn)
    costo_corrida, analizados, freno = 0.0, 0, False
    for i in range(0, len(pendientes), TAM_LOTE):
        if estado["gasto_usd"] + costo_corrida >= estado["tope_usd"]:
            freno = True
            break
        lote = pendientes[i:i + TAM_LOTE]
        try:
            resultados, usage = noticias._analizar_lote(client, lote)
        except Exception as e:
            _log(f"análisis falló en el lote {i // TAM_LOTE + 1}: "
                 f"{enmascarar_secretos(str(e))}")
            break
        for r in resultados:
            noticias.guardar_analisis(conn, r)
        conn.commit()
        analizados += len(resultados)
        costo_corrida += noticias._costo_estimado(usage)
    conn.close()
    _log(f"analizados {analizados} de {len(pendientes)} pendientes · "
         f"costo {costo_corrida:.4f} USD")

    # 4) resumen del día (una llamada corta), solo con holgura de presupuesto
    costo_resumen = 0.0
    restante = estado["tope_usd"] - estado["gasto_usd"] - costo_corrida
    if not freno and analizados and restante >= HOLGURA_RESUMEN_USD:
        try:
            noticias.generar_resumen_dia(client)
            costo_resumen = COSTO_RESUMEN_ESTIMADO
            _log("resumen del día regenerado")
        except Exception as e:
            _log(f"resumen del día falló: {enmascarar_secretos(str(e))}")

    registro = costos.registrar_corrida("noticias", costo_corrida + costo_resumen, {
        "resultado": "freno_presupuesto" if freno else "ok",
        "titulares_nuevos": nuevos, "analizados": analizados,
        "pendientes_restantes": len(pendientes) - analizados})
    _log(f"gasto acumulado hoy: {registro['acumulado_dia_usd']:.4f} / "
         f"{registro['tope_usd']:.2f} USD")

    if freno:
        _avisar_telegram(
            f"⛔ <b>MKI — freno de presupuesto</b>\n"
            f"Análisis de noticias DETENIDO a mitad de corrida: "
            f"{registro['acumulado_dia_usd']:.2f} de {registro['tope_usd']:.2f} "
            f"USD gastados hoy. Quedaron {len(pendientes) - analizados} "
            f"titulares sin analizar (se retoman mañana).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        _log(f"ERROR no manejado: {enmascarar_secretos(str(e))}")
        sys.exit(1)
