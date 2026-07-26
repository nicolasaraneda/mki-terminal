# ============================================================
# Tests de humo de la API (Etapa 4.7 F1) — PARIDAD.
#
# La regla: la API sirve exactamente los números de motor.py y de los
# helpers de senales.py/noticias.py. Si Streamlit y la API difieren, el
# bug es de la capa API por definición (CONTRATO.md).
#
# Correr:  source venv/bin/activate && python -m pytest tests/test_api.py -v
# ============================================================

from datetime import date

import pytest
from fastapi.testclient import TestClient

import motor
import senales
from api.main import app
from universo import UNIVERSO
from version import MODELO_VERSION

cliente = TestClient(app)


# ------------------------------------------------------------
# Envelope común
# ------------------------------------------------------------
def test_envelope_en_todos_los_endpoints():
    for ruta in ["/api/salud", "/api/hoy", "/api/aperturas", "/api/mercados",
                 "/api/cadena", "/api/noticias", "/api/historial",
                 "/api/detalle/NVDA"]:
        r = cliente.get(ruta)
        assert r.status_code == 200, f"{ruta} -> {r.status_code}"
        cuerpo = r.json()
        assert set(cuerpo.keys()) == {"meta", "datos"}, ruta
        meta = cuerpo["meta"]
        assert meta["fecha_datos"] == date.today().isoformat()
        assert meta["modelo_version"] == MODELO_VERSION


# ------------------------------------------------------------
# Paridad con motor.py
# ------------------------------------------------------------
def test_paridad_regimen():
    esperado = motor.regimen_al(date.today())
    servido = cliente.get("/api/hoy").json()["datos"]["regimen"]
    if esperado is None:
        assert servido is None
    else:
        assert servido["etiqueta"] == esperado["etiqueta"]
        assert servido["ratio_ma_pct"] == esperado["ratio_ma_pct"]


def test_paridad_roca_chip_contra_snapshot():
    """P0 (4.7.1): el Roca→Chip servido es EXACTAMENTE el valor sellado del
    último snapshot en senales.db — la API no recalcula el índice en vivo."""
    conn = senales.get_connection()
    fila = conn.execute("""
        SELECT fecha, roca_chip FROM snapshots
        WHERE roca_chip IS NOT NULL ORDER BY fecha DESC LIMIT 1
    """).fetchone()
    conn.close()
    servido = cliente.get("/api/hoy").json()["datos"]["roca_chip"]
    if fila is None:
        assert servido is None
    else:
        assert servido["valor"] == round(float(fila[1]))
        assert servido["fecha"] == fila[0]
        # la historia del sparkline también es sellada (un punto por snapshot)
        assert servido["historia"][-1] == round(float(fila[1]), 1)


def test_roca_chip_identico_entre_vistas():
    """Una sola fuente de verdad: /api/hoy y /api/cadena sirven el MISMO
    valor sellado, con la misma fecha."""
    en_hoy = cliente.get("/api/hoy").json()["datos"]["roca_chip"]
    en_cadena = cliente.get("/api/cadena").json()["datos"]["roca_chip"]
    if en_hoy is None:
        assert en_cadena is None
    else:
        assert en_cadena["valor"] == en_hoy["valor"]
        assert en_cadena["fecha"] == en_hoy["fecha"]


def test_paridad_betas():
    esperado = motor.betas_al(date.today())
    servido = cliente.get("/api/mercados").json()["datos"]["betas"]
    assert len(servido) == len(esperado)
    por_ticker = {f["ticker"]: f for f in servido}
    for _, fila in esperado.iterrows():
        s = por_ticker[fila["Ticker"]]
        assert s["beta"] == round(float(fila["beta"]), 2)
        assert s["r2_historico"] == round(float(fila["r2"]), 2)
        assert s["n_muestra"] == int(fila["n_muestra"])


def test_paridad_predicciones_apertura():
    """Los números de /api/aperturas salen del motor (o del sello del snapshot
    de hoy, que a su vez fue emitido por el mismo motor)."""
    datos = cliente.get("/api/aperturas").json()["datos"]
    assert datos["ventana_betas"] == motor.VENTANA_BETAS_DEFAULT
    vivas = motor.prediccion_apertura_al(date.today())
    if vivas.empty:
        assert datos["predicciones"] == []
        return
    esperadas = {f["Ticker"]: f for _, f in vivas.iterrows()}
    for p in datos["predicciones"]:
        assert p["ticker"] in esperadas
        e = esperadas[p["ticker"]]
        assert p["beta"] == float(e["Beta de contagio"])
        assert p["r2_historico"] == float(e["R2"])
        # incertidumbre SIEMPRE presente junto a la cifra
        assert p["intervalo80_pp"] is not None
        assert p["n_muestra"] > 0
        # 4.7.1: la etiqueta de señal deriva SOLO de umbrales de R² histórico
        r2 = p["r2_historico"]
        assert p["senal"] == ("fuerte" if r2 > 0.25
                              else "moderada" if r2 > 0.10 else "debil")
        assert "confianza" not in p  # el concepto no existe en el producto
        if not p["sellada"]:
            assert p["estimado_pct"] == float(e["Apertura estimada %"])
        else:
            assert p["emitida_utc"] is not None  # garantía anti look-ahead


def test_paridad_divergencias():
    esperado = motor.divergencias_al(date.today())
    servido = cliente.get("/api/cadena").json()["datos"]["divergencias"]
    assert len(servido) == len(esperado)
    for e, s in zip(esperado, servido):
        assert s["par"] == e["par"]
        assert s["z"] == e["z"]
        assert s["spread"] == e["spread"]
        assert s["activa"] == e["activa"]


def test_paridad_salud_datos():
    esperado = motor.salud_datos_al(date.today())
    servido = cliente.get("/api/salud").json()["datos"]["salud_datos"]
    assert servido["ok"] == esperado["ok"]
    assert servido["tickers_revisados"] == esperado["tickers_revisados"]


# ------------------------------------------------------------
# Paridad con senales.py (track record)
# ------------------------------------------------------------
def test_paridad_metricas_apertura():
    esperado = senales.metricas_apertura(dias=30)
    servido = cliente.get("/api/historial").json()["datos"]["metricas"]
    assert servido["suficiente"] == esperado["suficiente"]
    assert servido["n"] == esperado["n"]
    assert servido["minimo"] == senales.MINIMO_OBSERVACIONES
    if esperado["suficiente"]:
        assert servido["gap"] == esperado["gap"]
        assert servido["retorno_sesion"] == esperado["retorno_sesion"]


def test_paridad_calibracion():
    esperado = senales.calibracion_intervalos()
    servido = cliente.get("/api/historial").json()["datos"]["calibracion"]
    assert servido["suficiente"] == esperado["suficiente"]
    assert servido["n"] == esperado["n"]


def test_paridad_estados():
    esperado = senales.conteo_por_estado()
    servido = cliente.get("/api/historial").json()["datos"]["estados"]
    assert len(servido) == len(esperado)


# ------------------------------------------------------------
# Contrato: comparador y errores
# ------------------------------------------------------------
def test_comparador_base100():
    r = cliente.get("/api/comparador?tickers=NVDA,AMD")
    assert r.status_code == 200
    datos = r.json()["datos"]
    for t in ["NVDA", "AMD"]:
        serie = datos["series"][t]
        assert len(serie["fechas"]) == len(serie["valores"])
        assert serie["valores"][0] == pytest.approx(100.0)
    assert datos["benchmark"]["ticker"] == "SMH"


def test_errores_parametros():
    assert cliente.get("/api/comparador?tickers=NVDA").status_code == 400
    assert cliente.get("/api/comparador?tickers=NVDA,FALSO").status_code == 400
    assert cliente.get("/api/comparador?tickers=NVDA,AMD&base=eur").status_code == 400
    assert cliente.get("/api/detalle/FALSO").status_code == 404


def test_detalle_perfil():
    datos = cliente.get("/api/detalle/2330.TW").json()["datos"]
    assert datos["perfil"]["nombre"] == UNIVERSO["2330.TW"]["nombre"]
    assert datos["perfil"]["exchange"] == "XTAI"
    assert datos["perfil"]["moneda"] == "TWD"


def test_noticias_solo_cache():
    """El endpoint de noticias nunca dispara análisis: responde rápido y sin
    tocar la API de Anthropic (solo lee noticias.db)."""
    r = cliente.get("/api/noticias")
    assert r.status_code == 200
    datos = r.json()["datos"]
    assert "titulares" in datos and "sentimiento_por_ticker" in datos


def test_universo_expuesto():
    datos = cliente.get("/api/universo").json()["datos"]
    assert len(datos["instrumentos"]) == len(UNIVERSO)
    tickers = {i["ticker"] for i in datos["instrumentos"]}
    assert {"NVDA", "AMD", "2330.TW"} <= tickers


def test_husos_cinta():
    husos = cliente.get("/api/hoy").json()["datos"]["husos"]
    exchanges = {h["exchange"] for h in husos}
    assert {"XKRX", "XTKS", "XTAI", "XETR", "XNYS"} <= exchanges
    for h in husos:
        assert h["estado"] in ("abierta", "proxima", "cerrada")
        assert h["apertura_utc"] < h["cierre_utc"]
    # al menos una sesión "proxima" cuando ninguna está abierta; puede haber
    # empate real (KRX 09:00 KST y TSE 09:00 JST abren al mismo instante UTC)
    abiertas = [h for h in husos if h["estado"] == "abierta"]
    proximas = [h for h in husos if h["estado"] == "proxima"]
    if not abiertas:
        assert len(proximas) >= 1
        assert len({h["apertura_utc"] for h in proximas}) == 1


# ------------------------------------------------------------
# Enmienda 5.0: bloque operacional, Wilson, calibración, desgloses
# ------------------------------------------------------------
def test_meta_versionado_dual():
    from version import PLATAFORMA_VERSION
    meta = cliente.get("/api/salud").json()["meta"]
    assert meta["plataforma_version"] == PLATAFORMA_VERSION
    assert meta["modelo_version"] == MODELO_VERSION  # el modelo sigue congelado


def test_salud_operacion():
    datos = cliente.get("/api/salud").json()["datos"]
    op = datos["operacion"]
    assert {j["job"] for j in op["jobs"]} == {"noticias", "snapshot", "reporte",
                                              "backup", "vigia"}
    for j in op["jobs"]:
        assert isinstance(j["ok"], bool) and j["detalle"]
    assert isinstance(op["es_dia_habil"], bool)
    assert op["presupuesto"]["tope_usd"] > 0
    assert any(d["nombre"] == "senales.db" for d in op["dbs"])
    assert datos["versiones"]["plataforma"]


def test_historial_wilson_contra_formula():
    """El Wilson servido corresponde a los aciertos reales de la DB."""
    from api.utilidades import intervalo_wilson
    datos = cliente.get("/api/historial").json()["datos"]
    df = senales.verificaciones_detalle()
    if df.empty:
        assert datos["wilson"] is None
        return
    k, n = int(df["acierto_gap"].sum()), len(df)
    lo, hi = intervalo_wilson(k, n)
    w = datos["wilson"]["gap"]
    assert (w["pct"], w["lo_pct"], w["hi_pct"], w["n"]) == (
        round(100 * k / n, 1), lo, hi, n)
    assert w["lo_pct"] < w["pct"] < w["hi_pct"]


def test_historial_curva_y_desgloses():
    datos = cliente.get("/api/historial").json()["datos"]
    curva = datos["calibracion_curva"]
    if curva is not None:
        assert curva["nominal_pct"] == sorted(curva["nominal_pct"])
        # la cobertura empírica es monótona no-decreciente con el nominal
        assert all(a <= b for a, b in zip(curva["real_pct"], curva["real_pct"][1:]))
        # y en 80% nominal debe coincidir con la calibración clásica servida
        idx80 = curva["nominal_pct"].index(80)
        if datos["calibracion"].get("suficiente"):
            assert abs(curva["real_pct"][idx80]
                       - datos["calibracion"]["cobertura_pct"]) < 0.11
    # los desgloses recomponen el total
    df = senales.verificaciones_detalle()
    for clave in ("por_region", "por_regimen"):
        assert sum(f["n"] for f in datos[clave]) == len(df)
        for f in datos[clave]:
            assert f["wilson_lo_pct"] <= f["gap_pct"] <= f["wilson_hi_pct"]
