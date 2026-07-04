# ============================================================
# Bot Comparador de Acciones - Etapa 4
# Historial de señales y verificador de aciertos, vista de detalle por
# acción, normalización a USD, y rediseño visual completo.
# Ejecutar con:  python -m streamlit run app.py
# ============================================================

import os

import anthropic
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
from dotenv import load_dotenv

import noticias
import senales

load_dotenv()  # lee la clave desde el archivo .env local, solo para este proceso

st.set_page_config(page_title="Comparador de Semiconductores", layout="wide")


def obtener_cliente_ia():
    """Devuelve un cliente de la API de Claude, o None si no hay clave configurada."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception:
        return None


# ------------------------------------------------------------
# Sistema de diseño: paleta estricta, tipografía y gráficos
#
# Dirección de arte: sobriedad de producto Apple + seriedad de terminal
# financiero. Un solo verde para lo positivo, un solo rojo para lo negativo,
# nada de arcoíris. Los heatmaps de correlación usan una escala monocromática
# (no la escala divergente verde/rojo, que se reserva para señales direccionales).
# ------------------------------------------------------------
FONDO = "#0A0A0B"
SUPERFICIE = "#131316"
BORDE = "#26262B"
TEXTO_PRINCIPAL = "#F5F5F7"
TEXTO_SECUNDARIO = "#8E8E93"
COLOR_POSITIVO = "#30D158"   # verde sobrio: único color de acento para lo positivo
COLOR_NEGATIVO = "#FF453A"   # rojo sobrio: único color de acento para lo negativo
COLOR_NEUTRO = BORDE
ACENTO = "#0A84FF"           # acento de interacción (botones, selección) — no es señal de dato

PALETA_CATEGORICA = ["#0A84FF", "#64D2FF", "#5E5CE6", "#BF5AF2",
                     "#FF9F0A", "#30D158", "#FF453A", "#8E8E93"]
ESCALA_DIVERGENTE = [[0, COLOR_NEGATIVO], [0.5, COLOR_NEUTRO], [1, COLOR_POSITIVO]]
# Escala monocromática (un solo tono azul) para heatmaps de correlación:
# de "casi invisible" en -1 a azul vívido en +1. Nunca verde/rojo ni arcoíris.
ESCALA_MONOCROMATICA = [[0, "#101014"], [0.5, "#1C3A57"], [1, "#0A84FF"]]


def template_grafico(fig, altura: int = 400, **layout_kwargs):
    """Aplica el estilo visual único de la app a un gráfico Plotly y lo muestra.

    Fondo transparente, sin gridlines verticales, gridlines horizontales sutiles,
    tipografía Inter, sin barra de herramientas de Plotly, márgenes compactos.
    Toda personalización adicional (títulos de ejes, rangos, etc.) se pasa por
    layout_kwargs y se aplica encima de estos valores por defecto.
    """
    fig.update_layout(
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                  color=TEXTO_PRINCIPAL, size=13),
        colorway=PALETA_CATEGORICA,
        xaxis=dict(showgrid=False, zeroline=False, linecolor=BORDE),
        yaxis=dict(showgrid=True, gridcolor="#1D1D20", zeroline=False, linecolor=BORDE),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=30, l=10, r=10, b=10),
    )
    if layout_kwargs:
        fig.update_layout(**layout_kwargs)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-feature-settings: "tnum" 1;
    font-variant-numeric: tabular-nums;
}}

/* Oculta el menú hamburguesa, el footer "Made with Streamlit", el botón Deploy
   y cualquier decoración del header — sin chrome de Streamlit visible. */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
header[data-testid="stHeader"] {{ background: transparent; }}

.block-container {{ padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1200px; }}

h1, h2, h3, h4, h5 {{
    font-family: 'Space Grotesk', 'Inter', -apple-system, sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: -0.02em;
}}
h1 {{ font-size: 2.75rem !important; font-weight: 600 !important; }}

/* Widgets nativos de Streamlit: números tabulares también en métricas y tablas */
[data-testid="stMetricValue"], [data-testid="stDataFrame"] {{
    font-feature-settings: "tnum" 1;
    font-variant-numeric: tabular-nums;
}}

/* Navegación por secciones (segmented control) sin decoración adicional */
div[data-testid="stApp"] [role="radiogroup"] p {{ font-weight: 500; }}

/* Tarjetas de métricas del hero */
.metric-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin: 28px 0 40px 0;
}}
.metric-card {{
    background: {SUPERFICIE};
    border: 1px solid {BORDE};
    border-radius: 12px;
    padding: 26px 28px;
    transition: border-color 0.15s ease;
}}
.metric-card:hover {{ border-color: #3A3A40; }}
.metric-label {{
    font-size: 0.72rem;
    color: {TEXTO_SECUNDARIO};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}}
.metric-value {{
    font-family: 'Space Grotesk', 'Inter', sans-serif;
    font-size: 34px;
    font-weight: 500;
    letter-spacing: -0.01em;
    color: {TEXTO_PRINCIPAL};
    font-feature-settings: "tnum" 1;
    font-variant-numeric: tabular-nums;
}}
.metric-value.positivo {{ color: {COLOR_POSITIVO}; }}
.metric-value.negativo {{ color: {COLOR_NEGATIVO}; }}
.metric-sub {{
    font-size: 0.78rem;
    color: {TEXTO_SECUNDARIO};
    margin-top: 6px;
}}
.resumen-dia {{
    font-size: 22px;
    font-weight: 400;
    line-height: 1.55;
    letter-spacing: -0.01em;
    color: {TEXTO_PRINCIPAL};
    max-width: 900px;
}}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Universo de acciones: la cadena global de semiconductores
# ------------------------------------------------------------
UNIVERSO = {
    "NVDA": ("NVIDIA", "EE.UU. - GPUs / IA"),
    "AMD": ("AMD", "EE.UU. - CPUs / GPUs"),
    "INTC": ("Intel", "EE.UU. - CPUs / fundición"),
    "QCOM": ("Qualcomm", "EE.UU. - chips móviles"),
    "AVGO": ("Broadcom", "EE.UU. - redes / custom IA"),
    "TXN": ("Texas Instruments", "EE.UU. - análogos"),
    "ARM": ("Arm Holdings", "R.Unido - arquitecturas (ADR)"),
    "MU": ("Micron", "EE.UU. - DRAM / NAND"),
    "005930.KS": ("Samsung Electronics", "Corea - DRAM / fundición"),
    "000660.KS": ("SK Hynix", "Corea - DRAM / HBM"),
    "TSM": ("TSMC (ADR)", "Taiwán - fundición (cotiza en NY)"),
    "2330.TW": ("TSMC (Taiwán)", "Taiwán - fundición (bolsa local)"),
    "UMC": ("UMC (ADR)", "Taiwán - fundición"),
    "ASML": ("ASML (ADR)", "Holanda - litografía EUV"),
    "8035.T": ("Tokyo Electron", "Japón - equipos"),
    "6857.T": ("Advantest", "Japón - testeo de chips"),
    "IFX.DE": ("Infineon", "Alemania - potencia / autos"),
}

# Índices de referencia de cada mercado
INDICES = {
    "^SOX": ("SOX Semiconductores", "EE.UU."),
    "^GSPC": ("S&P 500", "EE.UU."),
    "^IXIC": ("Nasdaq", "EE.UU."),
    "^KS11": ("KOSPI", "Corea"),
    "^N225": ("Nikkei 225", "Japón"),
    "^TWII": ("TAIEX", "Taiwán"),
    "^GDAXI": ("DAX", "Alemania"),
}

# Acciones que cotizan en bolsas que abren DESPUÉS del cierre de EE.UU.
MERCADOS_POR_ABRIR = ["005930.KS", "000660.KS", "2330.TW", "8035.T", "6857.T", "IFX.DE"]

DEFAULT = ["NVDA", "AMD", "INTC", "MU", "TSM", "ASML", "005930.KS", "000660.KS"]
PERIODOS = {"3 meses": "3mo", "6 meses": "6mo", "1 año": "1y", "2 años": "2y", "5 años": "5y"}

# Acciones que NO cotizan en USD, y el par de yfinance para convertirlas.
# El resto (EE.UU. y ADRs como TSM, UMC, ASML) ya cotiza en USD.
MONEDA_TICKER = {
    "005930.KS": "KRW=X", "000660.KS": "KRW=X",
    "2330.TW": "TWD=X",
    "8035.T": "JPY=X", "6857.T": "JPY=X",
    "IFX.DE": "EUR=X",
}
PARES_FX = tuple(sorted(set(MONEDA_TICKER.values())))


# ------------------------------------------------------------
# Descarga de datos (caché 15 min)
# ------------------------------------------------------------
@st.cache_data(ttl=900, show_spinner="Descargando precios de mercados globales...")
def descargar_precios(tickers: tuple, periodo: str) -> pd.DataFrame:
    data = yf.download(list(tickers), period=periodo, interval="1d",
                       auto_adjust=True, progress=False)
    if data.empty:
        return pd.DataFrame()
    precios = data["Close"] if isinstance(data.columns, pd.MultiIndex) else data[["Close"]]
    if isinstance(precios, pd.Series):
        precios = precios.to_frame(name=tickers[0])
    # Supuesto básico #1: si una bolsa está cerrada (feriado/huso horario),
    # asumimos vigente el último precio conocido para alinear las series.
    precios = precios.ffill()
    return precios.dropna(axis=1, how="all")


def convertir_a_usd(precios: pd.DataFrame, tipos_cambio: pd.DataFrame) -> pd.DataFrame:
    """Supuesto básico #2: convierte cada columna de precios de su moneda local a USD
    usando los tipos de cambio de yfinance. Sin esto, la depreciación del won (u otra
    moneda) puede disfrazar el rendimiento real de una acción: si Samsung sube 5% en
    KRW pero el won se deprecia 8% frente al USD, el retorno real en USD es negativo.
    En yfinance, KRW=X/JPY=X/TWD=X/EUR=X representan todas "unidades de esa moneda por
    1 USD", así que convertir siempre es una división. Las acciones ya denominadas en
    USD (EE.UU. y ADRs como TSM, UMC, ASML) quedan intactas."""
    if precios.empty or tipos_cambio.empty:
        return precios
    resultado = precios.copy()
    for ticker in resultado.columns:
        par = MONEDA_TICKER.get(ticker)
        if par is None or par not in tipos_cambio.columns:
            continue
        tasa = tipos_cambio[par].reindex(resultado.index).ffill().bfill()
        resultado[ticker] = resultado[ticker] / tasa
    return resultado


def convertir_ohlc_a_usd(datos: pd.DataFrame, ticker: str, tipos_cambio: pd.DataFrame) -> pd.DataFrame:
    """Igual que convertir_a_usd pero para un solo ticker con columnas OHLC (no Volume)."""
    par = MONEDA_TICKER.get(ticker)
    if par is None or datos.empty or par not in tipos_cambio.columns:
        return datos
    resultado = datos.copy()
    tasa = tipos_cambio[par].reindex(resultado.index).ffill().bfill()
    for col in ["Open", "High", "Low", "Close"]:
        if col in resultado.columns:
            resultado[col] = resultado[col] / tasa
    return resultado


@st.cache_data(ttl=900, show_spinner="Descargando datos de la acción...")
def descargar_ohlcv(ticker: str, periodo: str) -> pd.DataFrame:
    """Precio completo (Open/High/Low/Close/Volume) de una sola acción, para la vista de detalle."""
    data = yf.download(ticker, period=periodo, interval="1d", auto_adjust=True, progress=False)
    if data.empty:
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data.dropna(how="all")


def nombre(t: str) -> str:
    if t in UNIVERSO:
        return UNIVERSO[t][0]
    if t in INDICES:
        return INDICES[t][0]
    return t


def calcular_metricas(precios: pd.DataFrame) -> pd.DataFrame:
    retornos = precios.pct_change().dropna(how="all")
    filas = []
    for t in precios.columns:
        serie = precios[t].dropna()
        if len(serie) < 20:
            continue
        ret_total = (serie.iloc[-1] / serie.iloc[0] - 1) * 100
        vol_anual = retornos[t].std() * (252 ** 0.5) * 100
        dist_max = (serie.iloc[-1] / serie.max() - 1) * 100
        momentum = (serie.iloc[-1] / serie.iloc[-min(21, len(serie))] - 1) * 100
        nom, desc = UNIVERSO.get(t, (t, ""))
        filas.append({"Ticker": t, "Empresa": nom, "Segmento": desc,
                      "Retorno período %": round(ret_total, 1),
                      "Volatilidad anual %": round(vol_anual, 1),
                      "Dist. del máximo %": round(dist_max, 1),
                      "Momentum 20d %": round(momentum, 1)})
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    df["Puntaje v0"] = (df["Momentum 20d %"].rank(pct=True) * 0.4
                        + df["Retorno período %"].rank(pct=True) * 0.4
                        + (1 - df["Volatilidad anual %"].rank(pct=True)) * 0.2).round(2)
    return df.sort_values("Puntaje v0", ascending=False).reset_index(drop=True)


def ultimo_movimiento_no_cero(retornos: pd.Series, umbral: float = 1e-6):
    """Encuentra el último movimiento realmente distinto de cero de una serie de retornos.

    Cuando una bolsa está cerrada (feriado), el precio arrastrado (ffill) produce un
    retorno de exactamente 0%, lo que no representa un movimiento de mercado real.
    Devuelve (valor % o None, fecha de ese movimiento o None, hubo_feriado_hoy, fecha_mas_reciente).
    """
    retornos = retornos.dropna()
    if retornos.empty:
        return None, None, False, None
    fecha_reciente = retornos.index[-1].date()
    feriado_hoy = abs(retornos.iloc[-1]) < umbral
    no_cero = retornos[retornos.abs() >= umbral]
    if no_cero.empty:
        return None, None, feriado_hoy, fecha_reciente
    return round(no_cero.iloc[-1] * 100, 2), no_cero.index[-1].date(), feriado_hoy, fecha_reciente


# ------------------------------------------------------------
# Interfaz
# ------------------------------------------------------------
st.title("Comparador global de semiconductores")
st.caption("Datos de Yahoo Finance (retraso ~15 min) + análisis de noticias con IA. "
           "Herramienta de análisis, no constituye asesoría financiera.")

with st.sidebar:
    st.header("Configuración")
    opciones = {f"{v[0]} ({k})": k for k, v in UNIVERSO.items()}
    seleccion = st.multiselect("Acciones a comparar", list(opciones.keys()),
                               default=[f"{UNIVERSO[t][0]} ({t})" for t in DEFAULT])
    tickers = tuple(opciones[s] for s in seleccion)
    periodo_label = st.selectbox(
        "Ventana de historia", list(PERIODOS.keys()), index=2,
        help="Cuánto pasado quieres graficar. '1 año' = los últimos 12 meses hasta hoy.")
    periodo = PERIODOS[periodo_label]

    st.divider()
    moneda_usd = st.toggle(
        "Moneda: USD", value=True,
        help="Convierte los precios de acciones que no cotizan en USD (Corea, Taiwán, "
             "Japón, Alemania) usando el tipo de cambio del día. Desactívalo para ver "
             "cada acción en su moneda local.")
    st.caption(
        "Supuesto básico #2: sin normalizar a USD, la depreciación de una moneda local "
        "puede disfrazar el rendimiento real — ej. si Samsung sube 5% en wones pero el "
        "won se deprecia 8% frente al dólar, el retorno real en USD es negativo.")

if len(tickers) < 2:
    st.info("Selecciona al menos 2 acciones en la barra lateral.")
    st.stop()

precios = descargar_precios(tickers, periodo)
tipos_cambio = descargar_precios(PARES_FX, periodo)
if moneda_usd:
    precios = convertir_a_usd(precios, tipos_cambio)
indices = descargar_precios(tuple(INDICES.keys()), periodo)

if precios.empty:
    st.error("No se pudieron descargar datos. Revisa tu conexión o espera unos minutos.")
    st.stop()

metricas_df = calcular_metricas(precios)

# Retornos compartidos entre secciones (antes se calculaban dentro de cada `with tab:",
# que Streamlit ejecutaba siempre; con la navegación por secciones solo corre el bloque
# activo, así que estas variables deben quedar disponibles para todas las secciones).
ret_acc = precios.pct_change()
ret_idx = indices.pct_change()

# Predicción del anticipador de aperturas — se calcula siempre, sin importar qué
# sección esté activa, porque el snapshot diario de señales.py también la necesita.
# Siempre cubre TODOS los mercados por abrir, independiente de la selección del sidebar.
precios_apertura = descargar_precios(tuple(MERCADOS_POR_ABRIR), periodo)
# Siempre en USD (independiente del toggle): el contagio con el SOX debe medirse sin
# ruido cambiario, y así el historial de señales queda consistente día a día.
precios_apertura = convertir_a_usd(precios_apertura, tipos_cambio)
ret_apertura = precios_apertura.pct_change()
if "^SOX" in ret_idx.columns:
    sox_apertura = ret_idx["^SOX"]
    ult_mov_apertura, ult_fecha_apertura, feriado_hoy_apertura, fecha_reciente_apertura = (
        ultimo_movimiento_no_cero(sox_apertura)
    )
else:
    sox_apertura = pd.Series(dtype=float)
    ult_mov_apertura, ult_fecha_apertura = None, None
    feriado_hoy_apertura, fecha_reciente_apertura = False, None

_filas_apertura = []
if ult_mov_apertura is not None:
    for t in MERCADOS_POR_ABRIR:
        if t not in ret_apertura.columns:
            continue
        par = pd.concat([ret_apertura[t], sox_apertura.shift(1)], axis=1).dropna()
        if len(par) < 40:
            continue
        y, x = par.iloc[:, 0], par.iloc[:, 1]
        beta = x.cov(y) / x.var() if x.var() > 0 else 0.0
        r2 = x.corr(y) ** 2
        est = beta * (ult_mov_apertura / 100) * 100
        confianza = "Alta" if r2 > 0.25 else ("Media" if r2 > 0.10 else "Baja")
        _filas_apertura.append({
            "Ticker": t,
            "Acción": nombre(t),
            "Mercado": UNIVERSO.get(t, ("", ""))[1].split(" - ")[0],
            "Beta de contagio": round(beta, 2),
            "Apertura estimada %": round(est, 2),
            "R2": round(r2, 4),
            "Confianza (R²)": f"{confianza} ({r2:.2f})",
        })
df_ant = pd.DataFrame(_filas_apertura)
if not df_ant.empty:
    df_ant = df_ant.sort_values("Apertura estimada %", ascending=False)

# ------------------------------------------------------------
# Historial de señales: snapshot diario (máx. 1x/día) y verificador de
# aciertos (máx. 1x por sesión del navegador, para no golpear yfinance de más).
# ------------------------------------------------------------
if "verificacion_corrida" not in st.session_state:
    senales.verificar_pendientes()
    st.session_state.verificacion_corrida = True

if not senales.ya_existe_snapshot_hoy():
    precios_universo = descargar_precios(tuple(UNIVERSO.keys()), "6mo")
    tipos_cambio_universo = descargar_precios(PARES_FX, "6mo")
    precios_universo = convertir_a_usd(precios_universo, tipos_cambio_universo)  # siempre en USD
    metricas_universo = calcular_metricas(precios_universo)
    senales.guardar_snapshot_diario(
        metricas_universo, noticias.sentimiento_promedio_por_ticker(), df_ant
    )

# ------------------------------------------------------------
# Sección hero: métricas clave del día
# ------------------------------------------------------------
retorno_diario = precios.pct_change().iloc[-1] * 100
mejor_ticker = retorno_diario.idxmax() if not retorno_diario.empty else None
mejor_valor = retorno_diario.max() if mejor_ticker is not None else 0.0

sentimiento_sector = noticias.sentimiento_promedio_sector()

sox_mov, sox_fecha, sox_feriado_hoy, sox_fecha_reciente = None, None, False, None
if "^SOX" in indices.columns:
    sox_ret = indices["^SOX"].pct_change()
    sox_mov, sox_fecha, sox_feriado_hoy, sox_fecha_reciente = ultimo_movimiento_no_cero(sox_ret)

lider_puntaje = metricas_df.iloc[0] if not metricas_df.empty else None


def _tarjeta(label: str, valor: str, clase: str = "", sub: str = "") -> str:
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return (f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value {clase}">{valor}</div>{sub_html}</div>')


tarjetas = []
if mejor_ticker is not None:
    tarjetas.append(_tarjeta("Mejor acción del día", f"{nombre(mejor_ticker)}",
                              "positivo" if mejor_valor >= 0 else "negativo",
                              f"{mejor_valor:+.2f}% hoy"))
if sentimiento_sector is not None:
    tarjetas.append(_tarjeta("Sentimiento del sector (IA)", f"{sentimiento_sector:+.2f}",
                              "positivo" if sentimiento_sector >= 0 else "negativo",
                              "de -1 (negativo) a +1 (positivo)"))
else:
    tarjetas.append(_tarjeta("Sentimiento del sector (IA)", "—", "",
                              "analiza noticias en la pestaña IA"))
if sox_mov is not None:
    sub_sox = f"sesión del {sox_fecha}"
    if sox_feriado_hoy:
        sub_sox = f"mercado cerrado el {sox_fecha_reciente} · último real: {sox_fecha}"
    tarjetas.append(_tarjeta("Último movimiento del SOX", f"{sox_mov:+.2f}%",
                              "positivo" if sox_mov >= 0 else "negativo", sub_sox))
if lider_puntaje is not None:
    tarjetas.append(_tarjeta("Líder del ranking cuantitativo", f"{lider_puntaje['Empresa']}",
                              "", f"Puntaje v0 = {lider_puntaje['Puntaje v0']:.2f}"))

st.markdown(f'<div class="metric-grid">{"".join(tarjetas)}</div>', unsafe_allow_html=True)

SECCIONES = ["Comparador", "Mercados", "Aperturas", "Análisis IA", "Historial", "Detalle"]
if "seccion_activa" not in st.session_state:
    st.session_state.seccion_activa = SECCIONES[0]
_seccion_elegida = st.segmented_control(
    "Navegación", SECCIONES, default=st.session_state.seccion_activa,
    key="nav_principal", label_visibility="collapsed",
)
seccion = _seccion_elegida if _seccion_elegida is not None else st.session_state.seccion_activa
st.session_state.seccion_activa = seccion

# ============================================================
# SECCIÓN: Comparador (Etapa 1)
# ============================================================
if seccion == "Comparador":
    st.subheader("Rendimiento comparado (base 100)")
    st.caption("Todas parten en 100 al inicio del período elegido: si una línea "
               "termina en 200, esa acción duplicó su valor en la ventana mostrada.")
    base100 = precios / precios.iloc[0] * 100
    df_plot = base100.reset_index().melt(id_vars="Date", var_name="Ticker", value_name="Índice")
    df_plot["Empresa"] = df_plot["Ticker"].map(nombre)
    fig = px.line(df_plot, x="Date", y="Índice", color="Empresa")
    template_grafico(fig, altura=430, legend_title=None, xaxis_title=None, yaxis_title="Base 100")

    st.subheader("Correlación entre acciones")
    st.caption("1.0 = se mueven idéntico. Ojo: acciones de la misma bolsa correlacionan "
               "más alto entre sí por compartir horario, no solo por su negocio. Escala "
               "monocromática: mientras más vívido el azul, más alta la correlación.")
    retornos = precios.pct_change().dropna(how="all")
    corr = retornos.corr().round(2)
    noms = [nombre(t) for t in corr.columns]
    fig_corr = go.Figure(go.Heatmap(z=corr.values, x=noms, y=noms, zmin=-1, zmax=1,
                                    colorscale=ESCALA_MONOCROMATICA, text=corr.values,
                                    texttemplate="%{text}"))
    template_grafico(fig_corr, altura=500)

    st.subheader("Métricas y ranking preliminar")
    tabla_metricas = metricas_df.copy()
    sentimientos = noticias.sentimiento_promedio_por_ticker()
    if not tabla_metricas.empty and sentimientos:
        tabla_metricas["Sentimiento IA"] = tabla_metricas["Ticker"].map(sentimientos).round(2)
        sentimiento_normalizado = (tabla_metricas["Sentimiento IA"].fillna(0) + 1) / 2
        tabla_metricas["Puntaje IA"] = (
            tabla_metricas["Puntaje v0"] * 0.7 + sentimiento_normalizado * 0.3
        ).round(2)
        tabla_metricas = tabla_metricas.sort_values("Puntaje IA", ascending=False).reset_index(drop=True)
        st.dataframe(tabla_metricas, use_container_width=True, hide_index=True)
        st.caption(
            "Puntaje IA = 70% Puntaje v0 (cuantitativo: momentum, retorno y volatilidad) + "
            "30% sentimiento de noticias analizado por IA (de -1 a +1, normalizado a 0-1). "
            "Si una acción no tiene noticias analizadas todavía, se asume sentimiento neutro. "
            "Ve a la pestaña 'Análisis IA' para generar estos datos.")
    else:
        st.dataframe(tabla_metricas, use_container_width=True, hide_index=True)
        st.caption(
            "Aún no hay datos de sentimiento de noticias. Ve a la pestaña 'Análisis IA' "
            "y presiona 'Actualizar y analizar noticias' para sumar el Puntaje IA a esta tabla.")

# ============================================================
# SECCIÓN: Mercados (relación entre mercados globales)
# ============================================================
if seccion == "Mercados":
    st.subheader("¿Qué índice mueve a cada acción?")
    st.caption("Correlación de cada acción con los índices de referencia del mundo, "
               "comparando retornos del mismo día calendario.")

    juntos = ret_acc.join(ret_idx, how="inner").dropna(how="all")
    corr_cruzada = pd.DataFrame(index=precios.columns, columns=indices.columns, dtype=float)
    for a in precios.columns:
        for i in indices.columns:
            par = juntos[[a, i]].dropna()
            if len(par) > 30:
                corr_cruzada.loc[a, i] = par[a].corr(par[i])
    corr_cruzada = corr_cruzada.astype(float).round(2)
    fig_x = go.Figure(go.Heatmap(
        z=corr_cruzada.values,
        x=[nombre(i) for i in corr_cruzada.columns],
        y=[nombre(a) for a in corr_cruzada.index],
        zmin=-1, zmax=1, colorscale=ESCALA_MONOCROMATICA,
        text=corr_cruzada.values, texttemplate="%{text}"))
    template_grafico(fig_x, altura=480)

    st.subheader("El efecto del huso horario: contagio con un día de desfase")
    st.caption(
        "La clave de esta tabla: para las acciones de Asia y Europa, comparamos su "
        "correlación con el índice SOX de EE.UU. medida el MISMO día vs. con el SOX "
        "del DÍA ANTERIOR. Si la correlación 'desfasada' es mayor, significa que esa "
        "acción reacciona hoy a lo que EE.UU. hizo ayer: el contagio viaja con la "
        "rotación del planeta.")

    if "^SOX" in ret_idx.columns:
        sox = ret_idx["^SOX"]
        filas = []
        for t in precios.columns:
            par0 = pd.concat([ret_acc[t], sox], axis=1).dropna()
            par1 = pd.concat([ret_acc[t], sox.shift(1)], axis=1).dropna()
            if len(par0) > 30 and len(par1) > 30:
                c0 = par0.iloc[:, 0].corr(par0.iloc[:, 1])
                c1 = par1.iloc[:, 0].corr(par1.iloc[:, 1])
                filas.append({
                    "Acción": nombre(t),
                    "Mercado": UNIVERSO.get(t, ("", ""))[1].split(" - ")[0],
                    "Corr. mismo día": round(c0, 2),
                    "Corr. con SOX del día anterior": round(c1, 2),
                    "¿Reacciona con desfase?": "Sí" if c1 > c0 + 0.05 else "—",
                })
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
        st.info(
            "Cómo leerlo: las acciones de EE.UU. correlacionan alto el mismo día "
            "(cotizan junto al SOX). Las coreanas, japonesas y taiwanesas suelen "
            "correlacionar más con el SOX **del día anterior**: cuando Seúl abre, "
            "Nueva York ya cerró hace horas y esa información 'llega' a Asia recién "
            "en su apertura. Esta asimetría es la base del anticipador (pestaña 3).")

# ============================================================
# SECCIÓN: Aperturas (anticipador)
# ============================================================
if seccion == "Aperturas":
    st.subheader("¿Cómo debería abrir Asia y Europa según lo último de EE.UU.?")
    st.caption(
        "Medimos históricamente cuánto se mueve cada acción asiática/europea al día "
        "siguiente de un movimiento del índice SOX de EE.UU. (su 'beta de contagio'), y "
        "lo aplicamos al último movimiento REAL del SOX (ignorando feriados). Es una "
        "ESTIMACIÓN de tendencia, no una predicción garantizada. Este panel analiza "
        "siempre TODAS las acciones de mercados por abrir, sin importar tu selección "
        "de la barra lateral.")

    if "^SOX" not in ret_idx.columns:
        st.warning("No se pudo descargar el índice SOX. Intenta de nuevo más tarde.")
    else:
        c1, c2 = st.columns(2)
        if ult_mov_apertura is not None:
            c1.metric("Último movimiento real del SOX (EE.UU.)", f"{ult_mov_apertura:+.2f}%",
                      help=f"Sesión del {ult_fecha_apertura}")
        else:
            c1.metric("Último movimiento real del SOX (EE.UU.)", "Sin datos")
        c2.metric("Índice", "SOX (Filadelfia)",
                  help="Agrupa a los principales semiconductores que cotizan en EE.UU.")
        if feriado_hoy_apertura:
            st.caption(f"Mercado cerrado el {fecha_reciente_apertura} (feriado EE.UU.). "
                       f"Se usa el último movimiento real, del {ult_fecha_apertura}.")

        if df_ant.empty:
            st.warning("Sin datos suficientes para estimar. Prueba con período de 1 año o más.")
        else:
            fig_ant = px.bar(df_ant, x="Acción", y="Apertura estimada %",
                             color="Apertura estimada %",
                             color_continuous_scale=ESCALA_DIVERGENTE,
                             range_color=[-df_ant["Apertura estimada %"].abs().max(),
                                          df_ant["Apertura estimada %"].abs().max()],
                             text="Apertura estimada %")
            fig_ant.update_traces(texttemplate="%{text:+.2f}%", textposition="outside")
            template_grafico(fig_ant, altura=380, coloraxis_showscale=False, xaxis_title=None)
            st.dataframe(df_ant.drop(columns=["Ticker", "R2"]), use_container_width=True, hide_index=True)
            st.info(
                "Cómo leerlo: 'Beta de contagio' = cuánto se mueve históricamente esa "
                "acción por cada 1% que se movió el SOX el día anterior. 'Confianza (R²)' "
                "= qué parte de sus movimientos se explica por EE.UU. (el resto es su "
                "propia historia local). Con confianza Baja, tómalo como brisa, no viento.")

# ============================================================
# SECCIÓN: Análisis IA
# ============================================================
if seccion == "Análisis IA":
    st.subheader("Análisis de noticias con IA")
    cliente_ia = obtener_cliente_ia()

    if cliente_ia is None:
        st.warning("No se encontró una clave de la API de Claude configurada.")
        st.markdown(
            "Para activar esta pestaña necesitas una clave (API key) de Anthropic:\n\n"
            "1. Crea una cuenta y genera una clave gratis en "
            "[console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys).\n"
            "2. En la carpeta del proyecto, crea un archivo llamado **`.env`** "
            "(puedes copiar `.env.example` y renombrarlo).\n"
            "3. Dentro de ese archivo escribe: `ANTHROPIC_API_KEY=sk-ant-tu-clave-aqui`\n"
            "4. Guarda el archivo y vuelve a correr `python -m streamlit run app.py`.\n\n"
            "Esta clave solo se usa para pagar el análisis de noticias de este proyecto — "
            "no afecta ninguna otra suscripción o herramienta que uses."
        )
    else:
        resumen = noticias.obtener_resumen_guardado()
        st.markdown("#### Resumen del día")
        if resumen:
            # Quita encabezados y énfasis markdown que a veces agrega el modelo (a pesar
            # de pedirle texto plano) y sustituye "$" por un símbolo visualmente igual
            # para que Streamlit no lo confunda con una fórmula matemática (LaTeX).
            texto_limpio = "\n".join(
                l for l in resumen.splitlines() if not l.strip().startswith("#")
            ).strip()
            texto_limpio = texto_limpio.replace("**", "").replace("*", "").replace("_", "")
            texto_seguro = texto_limpio.replace("$", "＄")
            st.markdown(f'<div class="resumen-dia">{texto_seguro}</div>', unsafe_allow_html=True)
        else:
            st.info(
                "Aún no hay un resumen del día. Presiona el botón de abajo para "
                "descargar y analizar noticias."
            )

        if st.button("Actualizar y analizar noticias"):
            with st.spinner("Descargando titulares nuevos (RSS)..."):
                nuevos = noticias.actualizar_titulares()
            with st.spinner("Analizando titulares nuevos con IA..."):
                cantidad, costo = noticias.analizar_pendientes(cliente_ia)
            with st.spinner("Generando resumen del día..."):
                noticias.generar_resumen_dia(cliente_ia)
            st.success(
                f"Listo: {nuevos} titulares nuevos descargados, {cantidad} analizados "
                f"con IA. Costo estimado de este análisis: ${costo:.4f} USD."
            )
            st.rerun()

        st.divider()
        st.subheader("Termómetro de sentimiento por acción")
        st.caption("Sentimiento promedio de las noticias ya analizadas para cada acción, de -1 (muy negativo) a +1 (muy positivo).")
        sentimientos = noticias.sentimiento_promedio_por_ticker()
        sentimientos_universo = {t: v for t, v in sentimientos.items() if t in UNIVERSO}
        sentimientos_otros = {t: v for t, v in sentimientos.items() if t not in UNIVERSO}
        if not sentimientos_universo:
            st.info("Sin datos de sentimiento todavía. Actualiza y analiza noticias primero.")
        else:
            df_sent = pd.DataFrame(
                [{"Ticker": t, "Empresa": nombre(t), "Sentimiento": round(v, 2)}
                 for t, v in sentimientos_universo.items()]
            ).sort_values("Sentimiento", ascending=False)
            fig_sent = px.bar(
                df_sent, x="Empresa", y="Sentimiento", color="Sentimiento",
                color_continuous_scale=ESCALA_DIVERGENTE, range_color=[-1, 1], text="Sentimiento",
            )
            fig_sent.update_traces(texttemplate="%{text:+.2f}", textposition="outside")
            template_grafico(fig_sent, altura=380, coloraxis_showscale=False,
                             xaxis_title=None, yaxis_range=[-1.2, 1.2])

        if sentimientos_otros:
            with st.expander(f"Otros tickers mencionados en noticias ({len(sentimientos_otros)})"):
                st.caption(
                    "La IA a veces menciona empresas fuera del universo cubierto por este "
                    "proyecto (ej. clientes o competidores citados en un titular)."
                )
                df_otros = pd.DataFrame(
                    [{"Ticker": t, "Sentimiento": round(v, 2)} for t, v in sentimientos_otros.items()]
                ).sort_values("Sentimiento", ascending=False)
                st.dataframe(df_otros, use_container_width=True, hide_index=True)

        st.subheader("Titulares recientes analizados")
        titulares = noticias.obtener_titulares_analizados(limite=150)
        if not titulares:
            st.info("Sin titulares analizados todavía.")
        else:
            st.dataframe(pd.DataFrame(titulares), use_container_width=True, hide_index=True)

# ============================================================
# SECCIÓN: Historial (señales y verificador de aciertos)
# ============================================================
if seccion == "Historial":
    st.subheader("Historial de señales y verificador de aciertos")
    st.caption(
        "Cada día que se abre el dashboard se guarda una foto de las señales del "
        "universo completo (Puntaje v0, sentimiento IA, Puntaje IA y la predicción "
        "del anticipador). Más adelante se compara automáticamente contra lo que "
        "realmente pasó. Ningún número aquí se inventa: con pocas observaciones, "
        "se indica explícitamente 'datos insuficientes'.")

    metricas_ap = senales.metricas_apertura(dias=30)
    tarjetas_hist = []
    if metricas_ap["suficiente"]:
        tarjetas_hist.append(_tarjeta(
            "Aciertos de dirección (30d)", f"{metricas_ap['pct_aciertos']:.1f}%",
            "positivo" if metricas_ap["pct_aciertos"] >= 50 else "negativo",
            f"{metricas_ap['n']} predicciones evaluadas"))
        tarjetas_hist.append(_tarjeta(
            "Error promedio", f"{metricas_ap['error_promedio_pp']:.2f} pp", "",
            "diferencia absoluta vs. lo real"))
    else:
        tarjetas_hist.append(_tarjeta(
            "Aciertos de dirección (30d)", "Datos insuficientes", "",
            f"{metricas_ap['n']} predicción(es) evaluada(s) — se necesitan "
            f"al menos {senales.MINIMO_OBSERVACIONES}"))
        tarjetas_hist.append(_tarjeta("Error promedio", "—", "", "datos insuficientes"))
    st.markdown(f'<div class="metric-grid">{"".join(tarjetas_hist)}</div>', unsafe_allow_html=True)
    st.caption(
        "Las predicciones se verifican con un pequeño rezago: recién puede evaluarse "
        "una vez que pasó la sesión que el anticipador intentaba anticipar.")

    st.subheader("Evolución del % de aciertos en el tiempo")
    evolucion = senales.evolucion_aciertos_apertura()
    if len(evolucion) < 2:
        st.info("Todavía no hay suficientes días verificados para graficar una tendencia.")
    else:
        fig_evol = px.line(evolucion, x="Fecha", y="% Aciertos", markers=True)
        fig_evol.add_hline(y=50, line_dash="dot", line_color=TEXTO_SECUNDARIO,
                           annotation_text="azar (50%)", annotation_position="bottom right")
        template_grafico(fig_evol, altura=350, yaxis_range=[0, 100], xaxis_title=None)

    st.subheader("Últimas predicciones vs. realidad")
    ultimas = senales.ultimas_predicciones_apertura(limite=50)
    if ultimas.empty:
        st.info("Todavía no hay predicciones verificadas.")
    else:
        ultimas_mostrar = ultimas.copy()
        ultimas_mostrar["Ticker"] = ultimas_mostrar["Ticker"].map(nombre)
        ultimas_mostrar["Acierto"] = ultimas_mostrar["Acierto"].map({1: "Sí", 0: "No"})
        st.dataframe(ultimas_mostrar, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Puntaje IA: ¿anticipa rendimiento a 5 días?")
    st.caption(
        "Compara el retorno real de los 5 días hábiles siguientes a la señal entre "
        "el tercio de acciones con MEJOR Puntaje IA y el tercio con PEOR Puntaje IA.")
    analisis_pi = senales.analisis_puntaje_ia(dias=90)
    if not analisis_pi["suficiente"]:
        st.info(f"Datos insuficientes: solo {analisis_pi['n']} observación(es) verificada(s) "
                f"— se necesitan al menos {senales.MINIMO_OBSERVACIONES}.")
    else:
        colp1, colp2, colp3 = st.columns(3)
        colp1.metric("Retorno 5d - tercio mejor puntaje", f"{analisis_pi['retorno_tercio_alto']:+.2f}%")
        colp2.metric("Retorno 5d - tercio peor puntaje", f"{analisis_pi['retorno_tercio_bajo']:+.2f}%")
        if analisis_pi["correlacion"] is not None:
            colp3.metric("Correlación puntaje-retorno", f"{analisis_pi['correlacion']:+.2f}")
        fig_pi = px.scatter(analisis_pi["datos"], x="puntaje", y="retorno",
                           labels={"puntaje": "Puntaje IA en el momento de la señal",
                                   "retorno": "Retorno real a 5 días %"})
        template_grafico(fig_pi, altura=380)
        st.caption(f"Basado en {analisis_pi['n']} observaciones de los últimos 90 días.")

# ============================================================
# SECCIÓN: Detalle (ficha completa por acción)
# ============================================================
if seccion == "Detalle":
    st.subheader("Ficha de la acción")
    opciones_detalle = {f"{v[0]} ({k})": k for k, v in UNIVERSO.items()}
    seleccion_detalle = st.selectbox(
        "Elige una acción para ver su ficha completa",
        list(opciones_detalle.keys()),
    )
    ticker_d = opciones_detalle[seleccion_detalle]
    nombre_d = nombre(ticker_d)

    datos_d = descargar_ohlcv(ticker_d, periodo)
    if moneda_usd:
        datos_d = convertir_ohlc_a_usd(datos_d, ticker_d, tipos_cambio)
    if datos_d.empty:
        st.warning("No se pudieron descargar datos para esta acción.")
    else:
        precio_actual = datos_d["Close"].iloc[-1]
        retorno_dia_d = (datos_d["Close"].iloc[-1] / datos_d["Close"].iloc[-2] - 1) * 100 if len(datos_d) > 1 else 0.0

        metricas_d_df = calcular_metricas(datos_d[["Close"]].rename(columns={"Close": ticker_d}))
        fila_metricas = metricas_d_df.iloc[0] if not metricas_d_df.empty else None
        sentimiento_d = noticias.sentimiento_promedio_por_ticker().get(ticker_d)

        par_moneda_d = MONEDA_TICKER.get(ticker_d)
        unidad_d = "USD" if (moneda_usd or par_moneda_d is None) else par_moneda_d.replace("=X", "")
        tarjetas_d = [
            _tarjeta(f"Precio actual ({unidad_d})", f"{precio_actual:,.2f}",
                     "positivo" if retorno_dia_d >= 0 else "negativo", f"{retorno_dia_d:+.2f}% hoy"),
        ]
        if fila_metricas is not None:
            tarjetas_d.append(_tarjeta("Puntaje v0", f"{fila_metricas['Puntaje v0']:.2f}", "",
                                       f"Momentum 20d {fila_metricas['Momentum 20d %']:+.1f}%"))
            tarjetas_d.append(_tarjeta("Volatilidad anual", f"{fila_metricas['Volatilidad anual %']:.1f}%"))
        if sentimiento_d is not None:
            tarjetas_d.append(_tarjeta("Sentimiento IA", f"{sentimiento_d:+.2f}",
                                       "positivo" if sentimiento_d >= 0 else "negativo",
                                       "de -1 a +1"))
        st.markdown(f'<div class="metric-grid">{"".join(tarjetas_d)}</div>', unsafe_allow_html=True)

        st.subheader(f"{nombre_d} — precio y volumen")
        fig_vela = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                 row_heights=[0.72, 0.28], vertical_spacing=0.03)
        fig_vela.add_trace(go.Candlestick(
            x=datos_d.index, open=datos_d["Open"], high=datos_d["High"],
            low=datos_d["Low"], close=datos_d["Close"], name=nombre_d,
            increasing_line_color=COLOR_POSITIVO, decreasing_line_color=COLOR_NEGATIVO,
            increasing_fillcolor=COLOR_POSITIVO, decreasing_fillcolor=COLOR_NEGATIVO,
        ), row=1, col=1)
        colores_vol = [COLOR_POSITIVO if c >= o else COLOR_NEGATIVO
                      for o, c in zip(datos_d["Open"], datos_d["Close"])]
        fig_vela.add_trace(go.Bar(x=datos_d.index, y=datos_d["Volume"],
                                  marker_color=colores_vol, name="Volumen"), row=2, col=1)
        template_grafico(
            fig_vela, altura=560, showlegend=False, xaxis_rangeslider_visible=False,
            yaxis_title="Precio", yaxis2_title="Volumen",
            xaxis2=dict(showgrid=False, zeroline=False, linecolor=BORDE),
            yaxis2=dict(showgrid=True, gridcolor="#1D1D20", zeroline=False, linecolor=BORDE),
        )

        col_noticias, col_corr = st.columns([3, 2])
        with col_noticias:
            st.subheader("Noticias de esta acción")
            titulares_d = noticias.obtener_titulares_por_ticker(ticker_d, limite=20)
            if not titulares_d:
                st.info("Sin noticias analizadas todavía para esta acción.")
            else:
                cols_mostrar = ["Fecha", "Fuente", "Titular", "Sentimiento", "Impacto"]
                st.dataframe(pd.DataFrame(titulares_d)[cols_mostrar],
                            use_container_width=True, hide_index=True, height=320)

        with col_corr:
            st.subheader("Correlaciones principales")
            precios_universo_d = descargar_precios(tuple(UNIVERSO.keys()), periodo)
            if moneda_usd:
                precios_universo_d = convertir_a_usd(precios_universo_d, tipos_cambio)
            retornos_universo_d = precios_universo_d.pct_change().dropna(how="all")
            if ticker_d in retornos_universo_d.columns and retornos_universo_d.shape[1] > 1:
                corr_ticker = retornos_universo_d.corr()[ticker_d].drop(ticker_d).dropna()
                top_corr = corr_ticker.reindex(
                    corr_ticker.abs().sort_values(ascending=False).index
                ).head(6)
                df_corr_d = pd.DataFrame({
                    "Empresa": [nombre(t) for t in top_corr.index],
                    "Correlación": top_corr.values.round(2),
                })
                st.dataframe(df_corr_d, use_container_width=True, hide_index=True, height=250)
            else:
                st.info("Sin datos suficientes para calcular correlaciones.")

        st.divider()
        st.subheader("Explicación IA")
        st.caption(
            "Genera bajo demanda (modelo Haiku, costo bajo) una explicación breve de "
            "por qué esta acción está en su situación actual, combinando sus métricas "
            "con sus noticias recientes.")
        clave_explicacion = f"explicacion_{ticker_d}"
        if st.button("Explicación IA", key=f"btn_explicacion_{ticker_d}"):
            cliente_ia_d = obtener_cliente_ia()
            if cliente_ia_d is None:
                st.warning(
                    "Configura tu clave de la API de Claude (ver la sección 'Análisis IA') "
                    "para usar esta función.")
            else:
                with st.spinner("Generando explicación con IA..."):
                    metricas_dict = {}
                    if fila_metricas is not None:
                        metricas_dict = {
                            "retorno_pct": fila_metricas["Retorno período %"],
                            "momentum_pct": fila_metricas["Momentum 20d %"],
                            "volatilidad_pct": fila_metricas["Volatilidad anual %"],
                            "puntaje_v0": fila_metricas["Puntaje v0"],
                            "sentimiento_ia": sentimiento_d,
                        }
                    explicacion_d = noticias.explicar_accion(
                        cliente_ia_d, ticker_d, nombre_d, metricas_dict, titulares_d
                    )
                    st.session_state[clave_explicacion] = explicacion_d

        if clave_explicacion in st.session_state:
            texto_explicacion = st.session_state[clave_explicacion].replace("$", "＄")
            st.markdown(f'<div class="resumen-dia">{texto_explicacion}</div>',
                       unsafe_allow_html=True)

st.divider()
st.caption("Etapa 4: historial de señales, vista de detalle por acción y normalización "
           "a USD. Herramienta de análisis, no constituye asesoría financiera.")