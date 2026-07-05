# ============================================================
# MKI Terminal - Etapa 4.6
# Integridad de medición (timestamps UTC y regla maestra de timing,
# doble objetivo del anticipador, snapshot programado, versionado,
# motor de funciones puras sin look-ahead) + interfaz at-a-glance
# (sidebar rail, grilla bento, portada Hoy sin scroll).
# Ejecutar con:  python -m streamlit run app.py
# ============================================================

import os
from datetime import date, datetime

import anthropic
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
from dotenv import load_dotenv

import alertas
import calendarios
import motor
import noticias
import senales
import snapshot as snapshot_mod
from universo import (ACCIONES, BENCHMARK, DEFAULT, INDICES, MERCADOS_POR_ABRIR,
                      MONEDA_TICKER, NIVELES_CADENA, PARES_FX, PERIODOS,
                      TICKERS_POR_NIVEL, UNIVERSO, nombre)
from version import MODELO_VERSION

load_dotenv()  # lee la clave desde el archivo .env local, solo para este proceso

st.set_page_config(page_title="MKI Terminal", layout="wide",
                   initial_sidebar_state="expanded")


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
# Sistema de diseño "neon fintech": terminal financiero del futuro.
#
# Fondo azul-negro profundo, datos que brillan, sobriedad estructural con
# acentos neón. CYAN y MAGENTA son colores de DATOS y protagonismo (series,
# highlights, gradientes); el violeta es el tercer color de serie. La
# semántica financiera es intocable: ganancia siempre verde, pérdida siempre
# rojo — el neón jerarquiza, nunca reemplaza esa semántica.
# Regla de oro: máximo 2 elementos con glow simultáneo por vista.
# ------------------------------------------------------------
FONDO = "#0B0D12"
SUPERFICIE = "#141826"
BORDE = "#232A3D"
TEXTO_PRINCIPAL = "#F2F4F8"
TEXTO_SECUNDARIO = "#8A93A6"
CYAN = "#22D3EE"             # acento neón principal: datos, highlights
MAGENTA = "#F472B6"          # acento neón secundario: datos, contraste
VIOLETA = "#818CF8"          # tercer color de serie
COLOR_POSITIVO = "#34D399"   # semántica financiera: ganancia (intocable)
COLOR_NEGATIVO = "#F87171"   # semántica financiera: pérdida (intocable)
COLOR_NEUTRO = BORDE
GRIDLINE = "#1A2030"

PALETA_CATEGORICA = [CYAN, MAGENTA, VIOLETA, "#67E8F9", "#F9A8D4",
                     "#A5B4FC", "#2DD4BF", "#8A93A6"]
# Plotly Express asigna colores por traza desde su propia secuencia por defecto
# (ignora layout.colorway), así que la paleta debe imponerse también aquí.
px.defaults.color_discrete_sequence = PALETA_CATEGORICA
ESCALA_DIVERGENTE = [[0, COLOR_NEGATIVO], [0.5, COLOR_NEUTRO], [1, COLOR_POSITIVO]]
# Heatmaps: azul profundo → cyan neón. Nunca verde/rojo ni arcoíris.
ESCALA_MONOCROMATICA = [[0, "#0B0D12"], [0.5, "#164E63"], [1, CYAN]]


def template_grafico(fig, altura: int = 400, **layout_kwargs):
    """Aplica el estilo visual único de la app a un gráfico Plotly y lo muestra.

    Fondo transparente, sin gridlines verticales, gridlines horizontales sutiles,
    series con líneas de 2.5px, hover labels sobre superficie de tarjeta, sin
    barra de herramientas de Plotly, márgenes compactos. Toda personalización
    adicional se pasa por layout_kwargs encima de estos valores por defecto.
    """
    fig.update_layout(
        height=altura,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                  color=TEXTO_PRINCIPAL, size=13),
        colorway=PALETA_CATEGORICA,
        xaxis=dict(showgrid=False, zeroline=False, linecolor=BORDE),
        yaxis=dict(showgrid=True, gridcolor=GRIDLINE, zeroline=False, linecolor=BORDE),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=SUPERFICIE, bordercolor=BORDE,
                        font=dict(family="Inter, sans-serif", color=TEXTO_PRINCIPAL)),
        margin=dict(t=30, l=10, r=10, b=10),
    )
    fig.update_traces(line_width=2.5, selector=dict(type="scatter"))
    if layout_kwargs:
        fig.update_layout(**layout_kwargs)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def badge(texto: str, tono: str = "cyan") -> str:
    """Pill de estado: fondo del acento al 12%, texto del acento, borde al 40%.
    Tonos: cyan | magenta | violeta | pos | neg | neutro."""
    colores = {"cyan": CYAN, "magenta": MAGENTA, "violeta": VIOLETA,
               "pos": COLOR_POSITIVO, "neg": COLOR_NEGATIVO, "neutro": TEXTO_SECUNDARIO}
    c = colores.get(tono, CYAN)
    return (f'<span class="badge" style="color:{c};border-color:{c}66;'
            f'background:{c}1F;">{texto}</span>')


def sparkline_svg(valores, color: str = CYAN, ancho: int = 130, alto: int = 34) -> str:
    """Mini-gráfico de línea inline (SVG puro, sin ejes) para tarjetas."""
    serie = [float(v) for v in valores if v == v]  # descarta NaN
    if len(serie) < 2:
        return ""
    mn, mx = min(serie), max(serie)
    rango = (mx - mn) or 1.0
    n = len(serie)
    puntos = " ".join(
        f"{i * ancho / (n - 1):.1f},{alto - 3 - (v - mn) / rango * (alto - 6):.1f}"
        for i, v in enumerate(serie)
    )
    return (f'<svg class="spark" width="{ancho}" height="{alto}" '
            f'viewBox="0 0 {ancho} {alto}" preserveAspectRatio="none">'
            f'<polyline points="{puntos}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'opacity="0.9"/></svg>')


st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-feature-settings: "tnum" 1;
    font-variant-numeric: tabular-nums;
}}

/* Chrome de Streamlit completamente oculto */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stStatusWidget"] {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* Scrollbar estilizada */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {BORDE}; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: #2E3750; }}
* {{ scrollbar-width: thin; scrollbar-color: {BORDE} transparent; }}

.block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px; }}

h1, h2, h3, h4, h5 {{
    font-family: 'Space Grotesk', 'Inter', -apple-system, sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: -0.02em;
}}

/* Wordmark del producto */
.wordmark {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: {TEXTO_PRINCIPAL};
    text-transform: uppercase;
    margin-bottom: 2px;
}}
.wordmark .punto {{ color: {CYAN}; }}
.titulo-hero {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: {TEXTO_PRINCIPAL};
    line-height: 1.1;
    margin: 0 0 4px 0;
}}
.subtitulo-hero {{
    font-size: 0.85rem;
    color: {TEXTO_SECUNDARIO};
    margin-bottom: 6px;
}}

/* Widgets nativos: números tabulares también en métricas y tablas */
[data-testid="stMetricValue"], [data-testid="stDataFrame"] {{
    font-feature-settings: "tnum" 1;
    font-variant-numeric: tabular-nums;
}}

div[data-testid="stApp"] [role="radiogroup"] p {{ font-weight: 500; }}

/* Tarjetas de métricas: borde superior con gradiente cyan→magenta */
.metric-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin: 24px 0 36px 0;
}}
.metric-card {{
    position: relative;
    overflow: hidden;
    background: {SUPERFICIE};
    border: 1px solid {BORDE};
    border-radius: 12px;
    padding: 24px 26px;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}
.metric-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {CYAN}, {MAGENTA});
    opacity: 0.55;
    transition: opacity 0.2s ease;
}}
.metric-card:hover {{ border-color: #2E3750; box-shadow: 0 0 22px rgba(34,211,238,0.07); }}
.metric-card:hover::before {{ opacity: 1; }}
.metric-label {{
    font-size: 0.72rem;
    color: {TEXTO_SECUNDARIO};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}}
.metric-value {{
    font-family: 'Space Grotesk', 'Inter', sans-serif;
    font-size: 33px;
    font-weight: 500;
    letter-spacing: -0.01em;
    color: {TEXTO_PRINCIPAL};
    font-feature-settings: "tnum" 1;
    font-variant-numeric: tabular-nums;
}}
.metric-value.positivo {{ color: {COLOR_POSITIVO}; }}
.metric-value.negativo {{ color: {COLOR_NEGATIVO}; }}
/* Glow: sal, no plato — máximo 2 elementos con glow por vista */
.metric-value.glow-cyan {{ color: {CYAN}; text-shadow: 0 0 24px rgba(34,211,238,0.35); }}
.metric-value.glow-magenta {{ color: {MAGENTA}; text-shadow: 0 0 24px rgba(244,114,182,0.35); }}
.metric-value.glow-pos {{ color: {COLOR_POSITIVO}; text-shadow: 0 0 24px rgba(52,211,153,0.35); }}
.metric-value.glow-neg {{ color: {COLOR_NEGATIVO}; text-shadow: 0 0 24px rgba(248,113,113,0.35); }}
.metric-sub {{
    font-size: 0.78rem;
    color: {TEXTO_SECUNDARIO};
    margin-top: 6px;
}}
.metric-card .spark {{ display: block; margin-top: 10px; }}

/* Badges pill (régimen, ZONA EARNINGS, ALTO BUZZ, divergencias) */
.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1px solid;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    vertical-align: middle;
    margin-right: 6px;
}}

/* Tarjetas de señal (portada Hoy) */
.senal-card {{
    position: relative;
    overflow: hidden;
    background: {SUPERFICIE};
    border: 1px solid {BORDE};
    border-radius: 12px;
    padding: 20px 22px;
    margin-bottom: 12px;
}}
.senal-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 3px;
}}
.senal-card.senal-pos::before {{ background: {COLOR_POSITIVO}; }}
.senal-card.senal-neg::before {{ background: {COLOR_NEGATIVO}; }}
.senal-card.senal-neutra::before {{ background: {CYAN}; }}
.senal-titulo {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.02rem;
    font-weight: 600;
    color: {TEXTO_PRINCIPAL};
    margin-bottom: 4px;
}}
.senal-porque {{
    font-size: 0.84rem;
    color: {TEXTO_SECUNDARIO};
    line-height: 1.45;
}}
.senal-meta {{
    font-size: 0.72rem;
    color: {TEXTO_SECUNDARIO};
    margin-top: 8px;
}}

.resumen-dia {{
    font-size: 21px;
    font-weight: 400;
    line-height: 1.55;
    letter-spacing: -0.01em;
    color: {TEXTO_PRINCIPAL};
    max-width: 900px;
}}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# CSS Etapa 4.6 — "at a glance": sidebar-rail de navegación con iconos SVG
# (mask CSS por nth-of-type sobre el st.radio del sidebar), grilla bento y
# densidad SaaS. Técnica del sidebar: ancho 64px forzado con !important y
# expansión a 220px en :hover (transition 0.2s); el contenido interno tiene
# ancho fijo 220px y se recorta con overflow hidden, así los labels no
# reflowan durante la transición. Ítem activo vía :has(input:checked).
# ------------------------------------------------------------
_ICONOS_NAV = [
    # 1 Hoy (casa)
    "M3 10.5 12 3l9 7.5 M5 9.5V21h14V9.5",
    # 2 Comparador (gráfico)
    "M3 3v18h18 M7 14l4-4 4 3 5-6",
    # 3 Mercados (globo)
    "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M3 12h18 M12 3c3 3.5 3 14.5 0 18 M12 3c-3 3.5-3 14.5 0 18",
    # 4 Cadena (eslabones)
    "M10 14a4.5 4.5 0 0 0 6.4 0l2-2a4.5 4.5 0 0 0-6.4-6.4l-1.1 1.1 M14 10a4.5 4.5 0 0 0-6.4 0l-2 2a4.5 4.5 0 0 0 6.4 6.4l1.1-1.1",
    # 5 Aperturas (amanecer)
    "M12 3v5 M8 6.5l1.5 1.5 M16 6.5 14.5 8 M5.5 19a6.5 6.5 0 0 1 13 0 M3 19h18",
    # 6 Análisis IA (destello)
    "M12 3l2 5.5L20 10.5l-5.5 2L12 18l-2-5.5L4 10.5l6-2z",
    # 7 Historial (reloj)
    "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 7.5V12l3 3",
    # 8 Detalle (lupa)
    "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z M16.5 16.5 21 21",
]


def _icono_data_uri(path: str) -> str:
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' "
           f"fill='none' stroke='black' stroke-width='2' stroke-linecap='round' "
           f"stroke-linejoin='round'><path d='{path}'/></svg>")
    return "url(\"data:image/svg+xml;utf8," + svg.replace("<", "%3C").replace(">", "%3E").replace("#", "%23") + "\")"


_css_iconos = "\n".join(
    f'section[data-testid="stSidebar"] [role="radiogroup"] '
    f'label:nth-of-type({i + 1})::before {{ -webkit-mask-image: {_icono_data_uri(p)}; '
    f'mask-image: {_icono_data_uri(p)}; }}'
    for i, p in enumerate(_ICONOS_NAV)
)

st.markdown(f"""
<style>
/* ---------- Sidebar rail de navegación ----------
   El rail debe ser SIEMPRE visible: Streamlit "colapsa" el sidebar bajo
   ~768px de ancho (o por estado recordado) poniéndole aria-expanded="false"
   y transform: translateX(-300px) — lo saca de pantalla. Como además
   ocultamos su control nativo de expandir, eso dejaba la app sin navegación
   (bug reportado). Neutralizamos el estado colapsado por completo: el
   selector incluye explícitamente [aria-expanded="false"] y anula el
   transform. El botón de COLAPSAR interno sí se oculta (el rail no debe
   poder esconderse), pero el control nativo de EXPANDIR queda como red de
   seguridad por si alguna versión futura de Streamlit escapa del override. */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"][aria-expanded="false"] {{
    width: 64px !important;
    min-width: 64px !important;
    max-width: 64px !important;
    transform: none !important;
    visibility: visible !important;
    margin-left: 0 !important;
    left: 0 !important;
    display: block !important;
    transition: width 0.2s ease, min-width 0.2s ease, max-width 0.2s ease;
    overflow: hidden !important;
    background: #0E1119 !important;
    border-right: 1px solid {BORDE};
}}
section[data-testid="stSidebar"]:hover {{
    width: 220px !important;
    min-width: 220px !important;
    max-width: 220px !important;
}}
section[data-testid="stSidebar"] > div {{
    width: 220px !important;
    padding-top: 0.6rem;
}}
/* Contenido interno visible incluso si Streamlit lo marcó colapsado */
section[data-testid="stSidebar"][aria-expanded="false"] > div {{
    visibility: visible !important;
    opacity: 1 !important;
}}
/* Sin botón de colapsar (el rail no debe poder esconderse)... */
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
/* ...pero el control de EXPANDIR del header queda visible como fallback. */
[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
}}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
    padding: 0.4rem 0.6rem;
}}

/* Wordmark: "M." colapsado, "MKI TERMINAL." expandido (superpuestos) */
.sidebar-wordmark {{
    position: relative;
    height: 34px;
    margin: 4px 0 14px 8px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.0rem;
    letter-spacing: 0.02em;
    color: {TEXTO_PRINCIPAL};
    text-transform: uppercase;
    white-space: nowrap;
}}
.sidebar-wordmark .wm-mini, .sidebar-wordmark .wm-full {{
    position: absolute; left: 0; top: 4px; transition: opacity 0.15s ease;
}}
.sidebar-wordmark .wm-full {{ opacity: 0; }}
section[data-testid="stSidebar"]:hover .wm-full {{ opacity: 1; }}
section[data-testid="stSidebar"]:hover .wm-mini {{ opacity: 0; }}
.sidebar-wordmark .punto {{ color: {CYAN}; }}

/* Radio de navegación → lista de ítems con icono + label */
section[data-testid="stSidebar"] [role="radiogroup"] {{ gap: 2px; }}
section[data-testid="stSidebar"] [role="radiogroup"] label {{
    position: relative;
    display: flex;
    align-items: center;
    padding: 9px 10px 9px 14px;
    margin: 0;
    border-radius: 8px;
    cursor: pointer;
}}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.04);
}}
/* ocultar el círculo nativo del radio */
section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{
    display: none;
}}
/* icono monocromo */
section[data-testid="stSidebar"] [role="radiogroup"] label::before {{
    content: "";
    flex: 0 0 20px;
    height: 20px;
    margin-right: 12px;
    background-color: {TEXTO_SECUNDARIO};
    -webkit-mask-repeat: no-repeat; -webkit-mask-position: center;
    -webkit-mask-size: contain;
    mask-repeat: no-repeat; mask-position: center; mask-size: contain;
    transition: background-color 0.15s ease;
}}
{_css_iconos}
/* labels: invisibles colapsado, visibles al expandir */
section[data-testid="stSidebar"] [role="radiogroup"] label p {{
    color: {TEXTO_SECUNDARIO};
    font-size: 0.88rem;
    font-weight: 500;
    white-space: nowrap;
    opacity: 0;
    transition: opacity 0.15s ease, color 0.15s ease;
}}
section[data-testid="stSidebar"]:hover [role="radiogroup"] label p {{ opacity: 1; }}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover p {{ color: {TEXTO_PRINCIPAL}; }}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover::before {{ background-color: {TEXTO_PRINCIPAL}; }}
/* ítem activo: barra cyan de 3px + texto claro */
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked)::after {{
    content: "";
    position: absolute; left: 0; top: 8px; bottom: 8px; width: 3px;
    background: {CYAN}; border-radius: 2px;
}}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{
    color: {TEXTO_PRINCIPAL};
}}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked)::before {{
    background-color: {CYAN};
}}

/* ---------- Densidad at-a-glance ---------- */
.block-container {{
    padding: 1.1rem 26px 2.2rem 26px !important;
    max-width: none !important;
}}
h3 {{ font-size: 1.18rem !important; }}
h4 {{ font-size: 1.0rem !important; }}
.metric-grid {{ gap: 12px; margin: 14px 0 20px 0; }}
.metric-card {{ padding: 16px 18px; }}
.metric-value {{ font-size: 26px; }}
.metric-label {{ margin-bottom: 6px; }}
.metric-card .spark {{ margin-top: 6px; }}
.senal-card {{ padding: 14px 16px; margin-bottom: 0; height: 100%; }}

/* Título de vista + fila utilitaria */
.vista-titulo {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.55rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: {TEXTO_PRINCIPAL};
    line-height: 1.15;
}}
.vista-sub {{ font-size: 0.78rem; color: {TEXTO_SECUNDARIO}; margin-top: 1px; }}

/* Mini-encabezado de bloque (reemplaza subheaders en Hoy) */
.mini-label {{
    font-size: 0.72rem;
    color: {TEXTO_SECUNDARIO};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 10px 0 8px 0;
}}

/* Resumen IA recortado a ~4 líneas (el texto completo va en un expander) */
.resumen-clamp {{
    font-size: 0.92rem;
    line-height: 1.5;
    color: {TEXTO_PRINCIPAL};
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
</style>
""", unsafe_allow_html=True)

# (El universo y sus subconjuntos viven en universo.py — fuente única de verdad.)


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
        info = UNIVERSO.get(t, {})
        nom, desc = info.get("nombre", t), info.get("segmento", "")
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


@st.cache_data(ttl=86400, show_spinner=False)
def dias_a_proximos_earnings(tickers: tuple) -> dict:
    """Días calendario al próximo reporte de resultados por acción, vía
    yfinance ticker.calendar. Cacheado 24 h (una consulta de red por acción).
    Si Yahoo no publica fecha para una acción, simplemente no aparece."""
    hoy = date.today()
    resultado = {}
    for t in tickers:
        try:
            cal = yf.Ticker(t).calendar
            fechas = cal.get("Earnings Date") if isinstance(cal, dict) else None
            if not fechas:
                continue
            futuras = []
            for f in fechas:
                if isinstance(f, datetime):
                    f = f.date()
                if isinstance(f, date) and f >= hoy:
                    futuras.append(f)
            if futuras:
                resultado[t] = (min(futuras) - hoy).days
        except Exception:
            continue
    return resultado


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
# Interfaz: navegación lateral (rail de iconos) + fila utilitaria.
# El sidebar SOLO navega; la configuración vive en un popover arriba a la
# derecha para no robarle ancho permanente a los datos.
# ------------------------------------------------------------
SECCIONES = ["Hoy", "Comparador", "Mercados", "Cadena", "Aperturas",
             "Análisis IA", "Historial", "Detalle"]
DESCRIPCION_SECCION = {
    "Hoy": "Cabina de mando — el estado del día en un vistazo",
    "Comparador": "Rendimiento, correlaciones y ranking de la selección",
    "Mercados": "Contagio entre bolsas y viento macro",
    "Cadena": "El flujo roca→chip→data center, divergencias y desfases",
    "Aperturas": "Anticipador de aperturas de Asia y Europa",
    "Análisis IA": "Noticias analizadas con Claude y sentimiento",
    "Historial": "Track record verificado y auditoría de timing",
    "Detalle": "Ficha completa por instrumento",
}

with st.sidebar:
    st.markdown(
        '<div class="sidebar-wordmark">'
        '<span class="wm-mini">M<span class="punto">.</span></span>'
        '<span class="wm-full">MKI Terminal<span class="punto">.</span></span>'
        '</div>', unsafe_allow_html=True)
    seccion = st.radio("Navegación", SECCIONES, key="nav_radio",
                       label_visibility="collapsed")

col_titulo, col_conf = st.columns([6, 1])
with col_titulo:
    st.markdown(
        f'<div class="vista-titulo">{seccion}</div>'
        f'<div class="vista-sub">{DESCRIPCION_SECCION[seccion]} · Yahoo Finance '
        f'(retraso ~15 min) · no constituye asesoría financiera</div>',
        unsafe_allow_html=True)
with col_conf:
    with st.popover("Ajustes", use_container_width=True):
        opciones = {f"{UNIVERSO[t]['nombre']} ({t})": t for t in ACCIONES}
        seleccion = st.multiselect(
            "Acciones a comparar", list(opciones.keys()),
            default=[f"{UNIVERSO[t]['nombre']} ({t})" for t in DEFAULT])
        periodo_label = st.selectbox(
            "Ventana de historia", list(PERIODOS.keys()), index=2,
            help="Cuánto pasado quieres graficar. '1 año' = los últimos 12 meses hasta hoy.")
        moneda_usd = st.toggle(
            "Moneda: USD", value=True,
            help="Convierte a USD las acciones que no cotizan en dólares (Supuesto "
                 "básico #2): sin normalizar, la depreciación de una moneda local "
                 "puede disfrazar el rendimiento real.")
tickers = tuple(opciones[s] for s in seleccion)
periodo = PERIODOS[periodo_label]

if len(tickers) < 2:
    st.info("Selecciona al menos 2 acciones en Ajustes (arriba a la derecha).")
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

# ------------------------------------------------------------
# Señales del día — TODAS salen de motor.py (funciones puras por fecha,
# la misma fuente de verdad que snapshot.py y el futuro backtest).
# ------------------------------------------------------------
dias_earnings = dias_a_proximos_earnings(ACCIONES)


@st.cache_data(ttl=900, show_spinner="Calculando señales del motor...")
def senales_del_motor(hoy_iso: str, dias_earnings_: dict):
    """Envoltorio cacheado de las funciones puras del motor para el día de hoy."""
    hoy_f = date.fromisoformat(hoy_iso)
    return {
        "regimen": motor.regimen_al(hoy_f),
        "cadena": motor.datos_cadena_al(hoy_f),
        "roca_chip": motor.roca_chip_al(hoy_f),
        "pares": motor.divergencias_al(hoy_f),
        "prediccion": motor.prediccion_apertura_al(hoy_f, dias_earnings=dias_earnings_),
        "salud": motor.salud_datos_al(hoy_f),
    }


_motor_hoy = senales_del_motor(date.today().isoformat(), dias_earnings)
regimen = _motor_hoy["regimen"]
indice_roca_chip = _motor_hoy["roca_chip"]
analisis_pares = _motor_hoy["pares"]
divergencias_activas = [p for p in analisis_pares if p["activa"]]
salud_datos = _motor_hoy["salud"]
series_nivel = _motor_hoy["cadena"]["series_nivel"]
ret_nivel = _motor_hoy["cadena"]["ret_nivel"]
precios_cadena = _motor_hoy["cadena"]["precios"]

# Último movimiento real del SOX (para el hero y los textos de Aperturas)
if "^SOX" in ret_idx.columns:
    ult_mov_apertura, ult_fecha_apertura, feriado_hoy_apertura, fecha_reciente_apertura = (
        ultimo_movimiento_no_cero(ret_idx["^SOX"])
    )
else:
    ult_mov_apertura, ult_fecha_apertura = None, None
    feriado_hoy_apertura, fecha_reciente_apertura = False, None

# df_ant: la predicción del motor + etiquetas de presentación.
# "Confianza (R²)" pasa a mostrar la muestra y el R² histórico sin disfrazarlos
# de certeza: la calibración real la dirá el verificador con el tiempo.
pred_motor = _motor_hoy["prediccion"]
_filas_apertura = []
if pred_motor is not None and not pred_motor.empty:
    for _, p in pred_motor.iterrows():
        t = p["Ticker"]
        etiqueta_muestra = f"muestra: {int(p['N muestra'])} sesiones · R² histórico: {p['R2']:.2f}"
        if p["Zona earnings"]:
            etiqueta_muestra += f" · degradada: earnings en {p['Dias earnings']}d"
        _filas_apertura.append({
            "Ticker": t,
            "Acción": nombre(t),
            "Mercado": UNIVERSO.get(t, {}).get("segmento", "").split(" - ")[0],
            "Beta de contagio": p["Beta de contagio"],
            "Apertura estimada %": p["Apertura estimada %"],
            "Intervalo80 pp": p["Intervalo80 pp"],
            "R2": p["R2"],
            "Confianza": p["Confianza"],
            "Muestra · R²": etiqueta_muestra,
            "Earnings": f"{p['Dias earnings']}d" if p["Zona earnings"] else "—",
        })
df_ant = pd.DataFrame(_filas_apertura)
if not df_ant.empty:
    df_ant = df_ant.sort_values("Apertura estimada %", ascending=False)

# ------------------------------------------------------------
# Snapshot de respaldo al abrir el dashboard (P3.3): si el job programado no
# corrió hoy (Mac apagado, launchd no instalado), se toma aquí con origen
# "dashboard" y su timestamp real — el verificador de timing decidirá después,
# predicción por predicción, si fue emitida a tiempo para ser evaluable.
# El verificador corre 1x por sesión del navegador.
# ------------------------------------------------------------
if "verificacion_corrida" not in st.session_state:
    senales.verificar_pendientes()
    st.session_state.verificacion_corrida = True

if not senales.ya_existe_snapshot_hoy():
    snapshot_mod.ejecutar_snapshot("dashboard")

# Alertas Telegram automáticas (1x por sesión; sin configurar, no hace nada;
# el registro anti-duplicados evita repetir la misma alerta entre sesiones).
if "alertas_evaluadas" not in st.session_state:
    st.session_state.alertas_evaluadas = True
    if alertas.esta_configurado():
        alertas.alertar_si_corresponde(
            regimen_actual=regimen["etiqueta"] if regimen else None,
            regimen_anterior=senales.regimen_snapshot_anterior(),
            divergencias=divergencias_activas,
            sentimientos={t: v for t, v in noticias.sentimiento_promedio_por_ticker().items()
                          if t in UNIVERSO},
            buzz=noticias.buzz_por_ticker(),
            nombres={t: d["nombre"] for t, d in UNIVERSO.items()},
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


def _tarjeta(label: str, valor: str, clase: str = "", sub: str = "",
             badges: str = "", spark: str = "") -> str:
    """Tarjeta de métrica. `clase` acepta positivo/negativo o glow-cyan/glow-magenta/
    glow-pos/glow-neg (glow con moderación: máx. 2 por vista). `badges` y `spark`
    reciben HTML ya construido con badge() / sparkline_svg()."""
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    badges_html = f'<div style="margin-top:8px">{badges}</div>' if badges else ""
    return (f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value {clase}">{valor}</div>{sub_html}'
            f'{badges_html}{spark}</div>')


# Fila hero global (visible en todas las secciones): régimen, Roca→Chip,
# último SOX real, sentimiento del sector. Glow solo en régimen y Roca→Chip
# (regla de oro: máximo 2 glows por vista).
tarjetas = []
if regimen is not None:
    clase_regimen = {"Alcista": "glow-pos", "Bajista": "glow-neg"}.get(regimen["tendencia"], "")
    tono_regimen = {"Alcista": "pos", "Bajista": "neg"}.get(regimen["tendencia"], "cyan")
    tarjetas.append(_tarjeta(
        "Régimen del SOX", regimen["tendencia"], clase_regimen,
        f"MA50 vs MA200: {regimen['ratio_ma_pct']:+.1f}%",
        badges=badge(f"VOL {regimen['vol'].upper()}", tono_regimen)))
else:
    tarjetas.append(_tarjeta("Régimen del SOX", "—", "", "sin historia suficiente"))

if indice_roca_chip is not None:
    tarjetas.append(_tarjeta(
        "Salud de cadena Roca→Chip", f"{indice_roca_chip['valor']:.0f}", "glow-cyan",
        "0 = cadena fría · 100 = cadena caliente",
        spark=sparkline_svg(indice_roca_chip.get("historia", []), CYAN)))

if sox_mov is not None:
    sub_sox = f"sesión del {sox_fecha}"
    if sox_feriado_hoy:
        sub_sox = f"mercado cerrado el {sox_fecha_reciente} · último real: {sox_fecha}"
    tarjetas.append(_tarjeta("Último movimiento del SOX", f"{sox_mov:+.2f}%",
                              "positivo" if sox_mov >= 0 else "negativo", sub_sox))

if sentimiento_sector is not None:
    tarjetas.append(_tarjeta("Sentimiento del sector (IA)", f"{sentimiento_sector:+.2f}",
                              "positivo" if sentimiento_sector >= 0 else "negativo",
                              "de -1 (negativo) a +1 (positivo)"))
else:
    tarjetas.append(_tarjeta("Sentimiento del sector (IA)", "—", "",
                              "analiza noticias en la pestaña IA"))

if seccion == "Hoy":
    metricas_ap_hero = senales.metricas_apertura(dias=30)
    if metricas_ap_hero["suficiente"]:
        tarjetas.append(_tarjeta(
            "Track record gap (30d)",
            f"{metricas_ap_hero['gap']['pct_aciertos']:.0f}%",
            "positivo" if metricas_ap_hero["gap"]["pct_aciertos"] >= 50 else "negativo",
            f"MAE {metricas_ap_hero['gap']['mae_pp']:.1f} pp · n={metricas_ap_hero['n']}"))
    else:
        tarjetas.append(_tarjeta(
            "Track record", "insuf.", "",
            f"{metricas_ap_hero['n']}/{senales.MINIMO_OBSERVACIONES} verificaciones — "
            "acumulando historia"))

st.markdown(f'<div class="metric-grid">{"".join(tarjetas)}</div>', unsafe_allow_html=True)

def tarjeta_senal(titulo: str, direccion: str, magnitud: str, confianza: str,
                  porque: str, regimen_str: str) -> str:
    """Tarjeta estándar de señal para la portada Hoy: dirección (pos/neg/neutra),
    magnitud, confianza, el porqué en una línea, y el régimen vigente como contexto."""
    return (
        f'<div class="senal-card senal-{direccion}">'
        f'<div class="senal-titulo">{titulo}</div>'
        f'<div class="senal-porque">{porque}</div>'
        f'<div class="senal-meta">Magnitud: {magnitud} · Confianza: {confianza} · '
        f'Régimen: {regimen_str}</div></div>')


# ============================================================
# SECCIÓN: Hoy (portada — síntesis en 30 segundos)
# ============================================================
if seccion == "Hoy":
    # ---- Fila 2 del bento: las 3 señales del día, lado a lado ----
    st.markdown(
        '<div class="mini-label" title="Lo más fuerte que el terminal ve ahora '
        'mismo entre divergencias, aperturas de alta confianza, sentimiento '
        'extremo y buzz. Las demás vistas son las salas de profundización.">'
        'Las 3 señales del día</div>', unsafe_allow_html=True)

    regimen_str = regimen["etiqueta"] if regimen else "sin datos"
    candidatas = []  # (fuerza, tarjeta_html) — fuerza 1.0 = justo en el umbral

    for p in divergencias_activas:
        candidatas.append((abs(p["z"]) / 2, tarjeta_senal(
            f"Divergencia: {p['par']}", "neutra",
            f"{p['spread']:+.1f} pp de spread 20d (z={p['z']:+.1f})",
            "Alta" if abs(p["z"]) > 3 else "Media",
            p["explicacion"], regimen_str)))

    if not df_ant.empty:
        for _, fila_s in df_ant[df_ant["Confianza"] == "Alta"].iterrows():
            est_s = fila_s["Apertura estimada %"]
            candidatas.append((abs(est_s) / 2, tarjeta_senal(
                f"Apertura estimada: {fila_s['Acción']} {est_s:+.2f}%",
                "pos" if est_s >= 0 else "neg",
                f"{est_s:+.2f}% (± {fila_s['Intervalo80 pp']:.1f} pp)", fila_s["Muestra · R²"],
                f"El SOX se movió {ult_mov_apertura:+.2f}% en su última sesión real y "
                f"esta acción históricamente replica ese movimiento con beta "
                f"{fila_s['Beta de contagio']:.2f} al día siguiente.", regimen_str)))

    sentimientos_hoy = noticias.sentimiento_promedio_por_ticker()
    for t_s, s_val in sentimientos_hoy.items():
        if t_s in UNIVERSO and abs(s_val) > 0.6:
            candidatas.append((abs(s_val) / 0.6, tarjeta_senal(
                f"Sentimiento extremo: {nombre(t_s)} {s_val:+.2f}",
                "pos" if s_val >= 0 else "neg",
                f"{s_val:+.2f} (umbral ±0.60)", "Media (noticias)",
                f"Las noticias recientes de {nombre(t_s)} tienen un sentimiento "
                f"inusualmente {'positivo' if s_val > 0 else 'negativo'}, ponderado "
                f"hacia lo más nuevo.", regimen_str)))

    buzz_hoy = noticias.buzz_por_ticker()
    for t_b, b_info in buzz_hoy.items():
        if b_info["buzz"] and t_b in UNIVERSO:
            ratio_b = (b_info["hoy"] / b_info["promedio_diario"]
                       if b_info["promedio_diario"] > 0 else 3.0)
            candidatas.append((ratio_b / 3, tarjeta_senal(
                f"Alto buzz: {nombre(t_b)}", "neutra",
                f"{b_info['hoy']} titulares hoy vs {b_info['promedio_diario']:.1f}/día",
                "Media (volumen de noticias)",
                f"El flujo de noticias de {nombre(t_b)} triplica su ritmo habitual: "
                f"el mercado está hablando de esta acción.", regimen_str)))

    top3 = [html for _, html in sorted(candidatas, key=lambda x: -x[0])[:3]]
    if top3:
        cols_senales = st.columns(len(top3), gap="small")
        for col_s, html_senal in zip(cols_senales, top3):
            with col_s:
                st.markdown(html_senal, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="senal-card senal-neutra" style="height:auto">'
            '<div class="senal-titulo">Sin señales fuertes hoy</div>'
            '<div class="senal-porque">Sin divergencias activas, sin predicciones '
            'de alta confianza, sin sentimiento extremo ni buzz inusual. Eso también '
            'es información: día de mantenimiento, no de acción.</div></div>',
            unsafe_allow_html=True)

    # ---- Fila 3 del bento: resumen IA (4 líneas) · estado del sistema · Telegram ----
    col_resumen, col_estado, col_tg = st.columns([5, 3, 2], gap="small")

    with col_resumen:
        st.markdown('<div class="mini-label">Resumen IA del día</div>',
                    unsafe_allow_html=True)
        resumen_hoy = noticias.obtener_resumen_guardado()
        if resumen_hoy:
            texto_hoy = "\n".join(
                l for l in resumen_hoy.splitlines() if not l.strip().startswith("#")
            ).strip()
            texto_hoy = texto_hoy.replace("**", "").replace("*", "").replace("_", "")
            texto_hoy = texto_hoy.replace("$", "＄")
            st.markdown(f'<div class="resumen-clamp">{texto_hoy}</div>',
                        unsafe_allow_html=True)
            with st.expander("ver más"):
                st.markdown(f'<div style="font-size:0.92rem;line-height:1.55">'
                            f'{texto_hoy}</div>', unsafe_allow_html=True)
        else:
            st.caption("Aún no hay resumen del día — genera uno en Análisis IA.")

    with col_estado:
        st.markdown('<div class="mini-label" title="Trazabilidad: cuándo y desde '
                    'dónde se emitió el snapshot del día, con qué versión del '
                    'modelo, y si los datos pasaron los chequeos de integridad.">'
                    'Estado del sistema</div>', unsafe_allow_html=True)
        info_snap = senales.info_snapshot_hoy()
        if info_snap:
            hora_snap = (info_snap["timestamp_utc"] or "")[11:16]
            linea_snap = (f"Snapshot de hoy: <b>{info_snap['origen']}</b> · "
                          f"{hora_snap} UTC · modelo v{info_snap['modelo_version'] or '—'}")
        else:
            linea_snap = "Sin snapshot hoy todavía"
        salud_txt = ("datos OK" if salud_datos["ok"]
                     else f"{len(salud_datos['problemas'])} problema(s) de datos")
        tono_salud = "pos" if salud_datos["ok"] else "neg"
        st.markdown(
            f'<div class="senal-card senal-neutra" style="height:auto">'
            f'<div class="senal-porque">{linea_snap}</div>'
            f'<div style="margin-top:8px">{badge(salud_txt, tono_salud)} '
            f'{badge(f"v{MODELO_VERSION}", "violeta")}</div>'
            f'<div class="senal-meta">Detalle completo en Historial → Salud de datos</div>'
            f'</div>', unsafe_allow_html=True)

    with col_tg:
        st.markdown('<div class="mini-label">Telegram</div>', unsafe_allow_html=True)
        if alertas.esta_configurado():
            if st.button("Enviar reporte matinal", use_container_width=True):
                sox_texto_alerta = (f"{ult_mov_apertura:+.2f}% (sesión del {ult_fecha_apertura})"
                                    if ult_mov_apertura is not None else "sin datos")
                lineas_ap = []
                if not df_ant.empty:
                    lineas_ap = [
                        f"• {f['Acción']}: {f['Apertura estimada %']:+.2f}% ({f['Confianza']})"
                        for _, f in df_ant.iterrows()]
                ok_rep, detalle_rep = alertas.enviar_reporte_matinal(
                    regimen=regimen["etiqueta"] if regimen else None,
                    roca_chip=indice_roca_chip.get("valor") if indice_roca_chip else None,
                    sox_texto=sox_texto_alerta,
                    sentimiento_sector=sentimiento_sector,
                    lineas_apertura=lineas_ap,
                    divergencias=divergencias_activas,
                )
                if ok_rep:
                    st.success("Reporte enviado.")
                else:
                    st.error(f"No se pudo enviar: {detalle_rep}")
            st.caption("Alertas automáticas activas (régimen, divergencias, "
                       "sentimiento, buzz).")
        else:
            with st.popover("Configurar", use_container_width=True):
                st.markdown(alertas.INSTRUCCIONES)


# ============================================================
# SECCIÓN: Comparador (Etapa 1)
# ============================================================
if seccion == "Comparador":
    tarjetas_comp = []
    if mejor_ticker is not None:
        tarjetas_comp.append(_tarjeta("Mejor acción del día", f"{nombre(mejor_ticker)}",
                                      "positivo" if mejor_valor >= 0 else "negativo",
                                      f"{mejor_valor:+.2f}% hoy"))
    if lider_puntaje is not None:
        tarjetas_comp.append(_tarjeta("Líder del ranking cuantitativo",
                                      f"{lider_puntaje['Empresa']}", "",
                                      f"Puntaje v0 = {lider_puntaje['Puntaje v0']:.2f}"))
    if tarjetas_comp:
        st.markdown(f'<div class="metric-grid">{"".join(tarjetas_comp)}</div>',
                    unsafe_allow_html=True)

    st.subheader("Rendimiento comparado")
    col_vista, col_log = st.columns([3, 1])
    with col_vista:
        vista_comp = st.radio(
            "Vista", ["Base 100", f"Relativo al benchmark ({BENCHMARK})"],
            horizontal=True, label_visibility="collapsed")
    with col_log:
        escala_log = st.toggle("Escala log", value=False,
                               help="Escala logarítmica: una duplicación ocupa la misma "
                                    "distancia vertical en cualquier nivel de precio.")

    base100 = precios / precios.iloc[0] * 100
    if vista_comp.startswith("Relativo"):
        precios_bench = descargar_precios((BENCHMARK,), periodo)
        if not precios_bench.empty and BENCHMARK in precios_bench.columns:
            bench_alineado = precios_bench[BENCHMARK].reindex(precios.index).ffill()
            bench100 = bench_alineado / bench_alineado.iloc[0] * 100
            datos_plot = base100.div(bench100, axis=0) * 100
            titulo_y = f"Relativo a {BENCHMARK} (100 = igual al ETF)"
            st.caption(
                f"100 = rinde igual que {BENCHMARK} (el ETF sectorial, benchmark "
                "oficial del sistema). Sobre 100 le gana al sector; bajo 100, pierde "
                "contra el sector aunque suba en términos absolutos.")
        else:
            datos_plot, titulo_y = base100, "Base 100"
            st.warning(f"No se pudo descargar {BENCHMARK}; se muestra base 100.")
    else:
        datos_plot, titulo_y = base100, "Base 100"
        st.caption("Todas parten en 100 al inicio del período elegido: si una línea "
                   "termina en 200, esa acción duplicó su valor en la ventana mostrada.")
    df_plot = datos_plot.reset_index().melt(id_vars="Date", var_name="Ticker", value_name="Índice")
    df_plot["Empresa"] = df_plot["Ticker"].map(nombre)
    fig = px.line(df_plot, x="Date", y="Índice", color="Empresa")
    template_grafico(fig, altura=430, legend_title=None, xaxis_title=None,
                     yaxis_title=titulo_y,
                     yaxis_type="log" if escala_log else "linear")

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
                    "Mercado": UNIVERSO.get(t, {}).get("segmento", "").split(" - ")[0],
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

    st.divider()
    st.subheader("Panel macro: el viento de fondo")
    st.caption(
        "Hipótesis de trabajo: el contagio EE.UU.→Asia se amplifica según el viento "
        "macro. Con la tasa de 10 años subiendo y las monedas asiáticas depreciándose, "
        "un golpe del SOX suele pegar más fuerte en Seúl y Taipéi; con viento a favor, "
        "el mismo golpe se amortigua. El cobre es el pulso de demanda industrial que "
        "alimenta la cadena desde la roca.")

    # El histórico del bono usa IEF (ETF de bonos del Tesoro 7-10 años) como
    # proxy: Yahoo no entrega histórico confiable de ^TNX, pero sí de IEF.
    # Ojo con la dirección: IEF es PRECIO de bonos — sube cuando las tasas BAJAN.
    # El nivel puntual del yield sigue saliendo de ^TNX si está disponible.
    MACRO_TICKERS = {
        "IEF": "Bonos 7-10 años EE.UU. (IEF)",
        "KRW=X": "Won coreano (KRW por USD)",
        "TWD=X": "Dólar taiwanés (TWD por USD)",
        "HG=F": "Cobre (futuro)",
    }
    precios_macro = descargar_precios(tuple(MACRO_TICKERS.keys()), "1y")
    ret_sox_largo = motor._datos_crudos(('^SOX',)).iloc[:, 0].pct_change()

    tarjetas_macro = []

    # Nivel puntual del yield 10 años (si Yahoo lo entrega): tarjeta aparte,
    # porque ^TNX no trae histórico confiable — la serie histórica del bono
    # es el proxy IEF de abajo.
    tnx = descargar_precios(("^TNX",), "5d")
    if not tnx.empty and "^TNX" in tnx.columns and tnx["^TNX"].dropna().size:
        tarjetas_macro.append(_tarjeta(
            "Yield 10 años EE.UU. (^TNX)", f"{tnx['^TNX'].dropna().iloc[-1]:.2f}%", "",
            "nivel puntual — el histórico del bono usa el proxy IEF"))

    for tk, nombre_macro in MACRO_TICKERS.items():
        if tk not in precios_macro.columns:
            continue
        serie_m = precios_macro[tk].dropna()
        if len(serie_m) < 66:
            continue
        valor_m = serie_m.iloc[-1]
        ret_m = serie_m.pct_change()
        par_m = pd.concat([ret_m, ret_sox_largo], axis=1).dropna()
        corr60 = None
        if len(par_m) >= 60:
            corr60 = par_m.iloc[:, 0].rolling(60).corr(par_m.iloc[:, 1]).iloc[-1]
        valor_str = f"{valor_m:,.2f}"
        var5 = (serie_m.iloc[-1] / serie_m.iloc[-6] - 1) * 100
        sub_m = f"{var5:+.2f}% en 5 días"
        if tk == "IEF":
            sub_m += " · precio de bonos: sube cuando las tasas BAJAN"
        badge_corr = ""
        if corr60 is not None and corr60 == corr60:
            badge_corr = badge(f"corr 60d SOX {corr60:+.2f}",
                               "cyan" if abs(corr60) < 0.5 else "magenta")
        tarjetas_macro.append(_tarjeta(
            nombre_macro, valor_str, "", sub_m, badges=badge_corr,
            spark=sparkline_svg(serie_m.tail(30), CYAN)))

    if tarjetas_macro:
        st.markdown(f'<div class="metric-grid">{"".join(tarjetas_macro)}</div>',
                    unsafe_allow_html=True)
    else:
        st.info("No se pudieron descargar los datos macro. Intenta más tarde.")

# ============================================================
# SECCIÓN: Cadena (flujo roca→chip, divergencias, correlaciones con desfase)
# ============================================================
if seccion == "Cadena":
    st.subheader("La cadena de valor, de la roca al data center")
    st.caption(
        "Cada eslabón muestra el rendimiento 20d promedio de sus integrantes "
        "(en USD). Las empresas de diseño fabless (NVIDIA, AMD, etc.) no forman "
        "parte del flujo físico de la cadena y se analizan en las demás pestañas.")

    tarjetas_niveles = []
    for nivel_c, nombre_nivel in NIVELES_CADENA.items():
        if nivel_c not in series_nivel:
            continue
        mom_serie = series_nivel[nivel_c].dropna()
        if mom_serie.empty:
            continue
        val_nivel = mom_serie.iloc[-1] * 100
        cols_nivel = [t for t in TICKERS_POR_NIVEL[nivel_c] if t in precios_cadena.columns]
        integrantes = " · ".join(nombre(t) for t in cols_nivel)
        base_nivel = precios_cadena[cols_nivel].dropna(how="all")
        prom_norm = (base_nivel / base_nivel.iloc[0]).mean(axis=1)
        tarjetas_niveles.append(_tarjeta(
            f"Nivel {nivel_c} · {nombre_nivel}", f"{val_nivel:+.1f}%",
            "positivo" if val_nivel >= 0 else "negativo",
            integrantes, spark=sparkline_svg(prom_norm.tail(30), CYAN)))
    st.markdown(f'<div class="metric-grid">{"".join(tarjetas_niveles)}</div>',
                unsafe_allow_html=True)

    if indice_roca_chip is not None:
        st.subheader("Índice Roca→Chip")
        st.caption(
            "Salud de la cadena completa en una cifra 0-100: momentum 20d promedio "
            "de los eslabones (peso igual por eslabón), expresado como percentil "
            "dentro de su propio último año. 50 = un día normal; 100 = la cadena "
            "más caliente del año; 0 = la más fría.")
        col_rc1, col_rc2 = st.columns([1, 3])
        with col_rc1:
            st.metric("Roca→Chip hoy", f"{indice_roca_chip['valor']:.0f}",
                      help=f"Momentum 20d crudo de la cadena: {indice_roca_chip['crudo_pct']:+.1f}%")
        with col_rc2:
            df_rc = indice_roca_chip["serie"].reset_index()
            df_rc.columns = ["Fecha", "Momentum de cadena %"]
            fig_rc = px.line(df_rc, x="Fecha", y="Momentum de cadena %")
            fig_rc.add_hline(y=0, line_dash="dot", line_color=TEXTO_SECUNDARIO)
            template_grafico(fig_rc, altura=260, xaxis_title=None)

    st.divider()
    st.subheader("Divergencias entre competidores directos")
    st.caption(
        "Cuando dos competidores del mismo negocio se separan mucho más de lo "
        "habitual (|z| > 2 contra su propia historia de 1 año), algo específico "
        "está pasando en uno de los dos: o hay una historia real, o hay una "
        "brecha que tiende a cerrarse.")
    if not analisis_pares:
        st.info("Sin datos suficientes para analizar pares de competidores.")
    else:
        for p in analisis_pares:
            if p["activa"]:
                st.markdown(
                    f'<div class="senal-card senal-neutra">'
                    f'<div class="senal-titulo">{p["par"]} '
                    f'{badge("DIVERGENCIA ACTIVA", "magenta")}</div>'
                    f'<div class="senal-porque">{p["explicacion"]}</div>'
                    f'<div class="senal-meta">Grupo: {p["grupo"]} · spread 20d '
                    f'{p["spread"]:+.1f} pp · z = {p["z"]:+.2f}</div></div>',
                    unsafe_allow_html=True)
        df_pares = pd.DataFrame([{
            "Par": p["par"], "Grupo": p["grupo"], "Spread 20d (pp)": p["spread"],
            "Z-score": p["z"], "Divergencia": "ACTIVA" if p["activa"] else "—",
        } for p in analisis_pares]).sort_values("Z-score", key=abs, ascending=False)
        st.dataframe(df_pares, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("¿Quién anticipa a quién? Correlaciones con desfase")
    st.caption(
        "Correlación entre el retorno de un eslabón HOY y el del eslabón siguiente "
        "5, 10 o 20 días DESPUÉS. Si el cobre de hoy correlaciona con las obleas de "
        "dentro de 10 días, la roca anticipa al chip. La última fila mira la cadena "
        "al revés: la demanda final (Microsoft, SMH) como anticipador de las "
        "fundiciones — el capex de data centers se anuncia antes de fabricarse.")
    PARES_DESFASE = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 3)]
    LAGS = [5, 10, 20]
    filas_desfase, etiquetas_desfase = [], []
    for niv_a, niv_b in PARES_DESFASE:
        if niv_a not in ret_nivel or niv_b not in ret_nivel:
            continue
        fila_vals = []
        for lag in LAGS:
            par_lag = pd.concat([ret_nivel[niv_a].shift(lag), ret_nivel[niv_b]],
                                axis=1).dropna()
            fila_vals.append(round(par_lag.iloc[:, 0].corr(par_lag.iloc[:, 1]), 2)
                             if len(par_lag) > 60 else None)
        filas_desfase.append(fila_vals)
        etiquetas_desfase.append(
            f"{NIVELES_CADENA[niv_a]} → {NIVELES_CADENA[niv_b]}")
    if filas_desfase:
        fig_desfase = go.Figure(go.Heatmap(
            z=filas_desfase,
            x=[f"{lag} días" for lag in LAGS],
            y=etiquetas_desfase,
            zmin=-0.5, zmax=0.5, colorscale=ESCALA_MONOCROMATICA,
            text=filas_desfase, texttemplate="%{text}"))
        template_grafico(fig_desfase, altura=330)
        st.caption(
            "Con retornos diarios estas correlaciones suelen ser bajas: valores "
            "sobre ~0.15 ya son señal de que el eslabón anterior lleva la batuta.")

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

        # Badge de calibración: qué dice el verificador sobre los intervalos.
        calib = senales.calibracion_intervalos()
        if calib["suficiente"]:
            st.markdown(badge(
                f"CALIBRACIÓN: {calib['cobertura_pct']:.0f}% de los gaps reales "
                f"cayó dentro del intervalo 80% (n={calib['n']})",
                "pos" if 70 <= calib["cobertura_pct"] <= 90 else "magenta"),
                unsafe_allow_html=True)
        else:
            st.markdown(badge(
                f"CALIBRACIÓN: PENDIENTE ({calib['n']} de "
                f"{senales.MINIMO_OBSERVACIONES} verificaciones mínimas)", "neutro"),
                unsafe_allow_html=True)

        if df_ant.empty:
            st.warning("Sin datos suficientes para estimar. Prueba con período de 1 año o más.")
        else:
            fig_ant = px.bar(df_ant, x="Acción", y="Apertura estimada %",
                             color="Apertura estimada %",
                             color_continuous_scale=ESCALA_DIVERGENTE,
                             range_color=[-df_ant["Apertura estimada %"].abs().max(),
                                          df_ant["Apertura estimada %"].abs().max()],
                             error_y="Intervalo80 pp",
                             text="Apertura estimada %")
            fig_ant.update_traces(texttemplate="%{text:+.2f}%", textposition="outside",
                                  error_y_color=TEXTO_SECUNDARIO)
            template_grafico(fig_ant, altura=400, coloraxis_showscale=False, xaxis_title=None)
            st.caption(
                "Las barras de error muestran el intervalo central del 80%: si el modelo "
                "está bien calibrado, 8 de cada 10 gaps reales deberían caer dentro de la "
                "barra (±1.28 × la desviación de los residuos históricos de cada regresión). "
                "Un intervalo que cruza el cero significa que la dirección misma es incierta.")
            st.dataframe(df_ant.drop(columns=["Ticker", "R2", "Confianza"]),
                         use_container_width=True, hide_index=True)
            if (df_ant["Earnings"] != "—").any():
                st.caption(
                    "ZONA EARNINGS: cuando una acción reporta resultados en menos de 5 "
                    "días, su confianza se degrada un nivel — cerca del reporte manda "
                    "la noticia del reporte, no la estadística del contagio.")
            st.info(
                "Cómo leerlo: 'Beta de contagio' = cuánto se mueve históricamente esa "
                "acción por cada 1% que se movió el SOX el día anterior. 'Muestra · R²' "
                "= con cuántas sesiones se estimó la beta (ventana rodante de "
                f"{motor.VENTANA_BETAS_DEFAULT} días hábiles) y qué parte de los "
                "movimientos explica históricamente EE.UU. La calibración REAL del "
                "intervalo la dicta el verificador, no el R².")

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
        st.caption(
            "Sentimiento con decaimiento temporal: cada noticia pesa según su edad "
            "(hoy = 1.0, cada día le quita 30%, piso 0.1). Lo de esta mañana manda; "
            "lo del mes pasado apenas suma. Escala de -1 (muy negativo) a +1 (muy positivo).")

        buzz_info = noticias.buzz_por_ticker()
        tickers_en_buzz = [t for t, b in buzz_info.items() if b["buzz"] and t in UNIVERSO]
        if tickers_en_buzz:
            badges_buzz = " ".join(
                badge(f"ALTO BUZZ · {nombre(t)} ({buzz_info[t]['hoy']} titulares hoy)", "cyan")
                for t in tickers_en_buzz)
            st.markdown(badges_buzz, unsafe_allow_html=True)
            st.caption(
                "ALTO BUZZ = una acción con al menos el triple de titulares que su "
                "promedio diario de dos semanas: el mercado está hablando de ella.")
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
        f"Track record limpio desde la Etapa 4.6 (modelo v{MODELO_VERSION}): cada "
        "predicción queda sellada con su timestamp UTC de emisión y solo se evalúa "
        "si fue emitida ANTES de la apertura de su sesión objetivo. Lo emitido tarde "
        "queda como 'no verificable' (auditable, fuera de métricas), y lo anterior a "
        "la 4.6 quedó como legacy. Las métricas nunca mezclan versiones del modelo. "
        "Con pocas observaciones se dice 'datos insuficientes' — nada se inventa.")

    metricas_ap = senales.metricas_apertura(dias=30)
    tarjetas_hist = []
    if metricas_ap["suficiente"]:
        g, r = metricas_ap["gap"], metricas_ap["retorno_sesion"]
        tarjetas_hist.append(_tarjeta(
            "Aciertos GAP de apertura (30d)", f"{g['pct_aciertos']:.1f}%",
            "positivo" if g["pct_aciertos"] >= 50 else "negativo",
            f"MAE {g['mae_pp']:.2f} pp · {metricas_ap['n']} predicciones"))
        tarjetas_hist.append(_tarjeta(
            "Aciertos RETORNO de sesión (30d)", f"{r['pct_aciertos']:.1f}%",
            "positivo" if r["pct_aciertos"] >= 50 else "negativo",
            f"MAE {r['mae_pp']:.2f} pp · {metricas_ap['n']} predicciones"))
    else:
        tarjetas_hist.append(_tarjeta(
            "Aciertos GAP de apertura (30d)", "Datos insuficientes", "",
            f"{metricas_ap['n']} evaluada(s) — mínimo {senales.MINIMO_OBSERVACIONES}"))
        tarjetas_hist.append(_tarjeta(
            "Aciertos RETORNO de sesión (30d)", "—", "", "datos insuficientes"))
    calib_h = senales.calibracion_intervalos()
    if calib_h["suficiente"]:
        tarjetas_hist.append(_tarjeta(
            "Cobertura del intervalo 80%", f"{calib_h['cobertura_pct']:.0f}%",
            "", f"objetivo: ~80% · n={calib_h['n']}"))
    else:
        tarjetas_hist.append(_tarjeta(
            "Cobertura del intervalo 80%", "Pendiente", "",
            f"{calib_h['n']} de {senales.MINIMO_OBSERVACIONES} verificaciones mínimas"))
    st.markdown(f'<div class="metric-grid">{"".join(tarjetas_hist)}</div>', unsafe_allow_html=True)
    st.caption(
        "El GAP (apertura vs cierre anterior) mide si la señal EXISTE; el RETORNO de "
        "sesión (cierre vs cierre anterior) ayuda a saber si es CAPTURABLE operando "
        "en la apertura. Un anticipador puede acertar el gap y aún así no ser "
        "operable si el gap ya se comió todo el movimiento.")

    st.subheader("Evolución del % de aciertos en el tiempo")
    evolucion = senales.evolucion_aciertos_apertura()
    if len(evolucion) < 2:
        st.info("Todavía no hay suficientes días verificados para graficar una tendencia.")
    else:
        df_evol = evolucion.melt(id_vars=["Fecha", "N"], var_name="Métrica",
                                 value_name="% Aciertos")
        fig_evol = px.line(df_evol, x="Fecha", y="% Aciertos", color="Métrica", markers=True)
        fig_evol.add_hline(y=50, line_dash="dot", line_color=TEXTO_SECUNDARIO,
                           annotation_text="azar (50%)", annotation_position="bottom right")
        template_grafico(fig_evol, altura=350, yaxis_range=[0, 100], xaxis_title=None,
                         legend_title=None)

    st.subheader("Últimas predicciones vs. realidad")
    ultimas = senales.ultimas_predicciones_apertura(limite=50)
    if ultimas.empty:
        st.info("Todavía no hay predicciones verificadas con el modelo actual "
                f"(v{MODELO_VERSION}). El track record limpio empieza a acumularse "
                "desde hoy: cada sesión asiática/europea que cierre irá sumando filas.")
    else:
        ultimas_mostrar = ultimas.copy()
        ultimas_mostrar["Ticker"] = ultimas_mostrar["Ticker"].map(nombre)
        for col in ["Acierto gap", "Acierto sesión"]:
            ultimas_mostrar[col] = ultimas_mostrar[col].map({1: "Sí", 0: "No"})
        st.dataframe(ultimas_mostrar, use_container_width=True, hide_index=True)

    st.subheader("Snapshots y auditoría de timing")
    col_snap, col_estados = st.columns([3, 2])
    with col_snap:
        st.caption("Origen y hora de emisión de cada snapshot (programado = launchd, "
                   "manual = snapshot.py a mano, dashboard = respaldo al abrir la app).")
        st.dataframe(senales.historial_snapshots(30), use_container_width=True,
                     hide_index=True, height=240)
    with col_estados:
        st.caption("Estados de las predicciones: lo no verificable y lo legacy se "
                   "conserva para auditoría pero jamás entra a las métricas.")
        st.dataframe(senales.conteo_por_estado(), use_container_width=True,
                     hide_index=True, height=240)

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

    st.divider()
    with st.expander("Salud de datos"):
        st.caption(
            "Chequeos automáticos de integridad: saltos diarios anómalos (>40% sin "
            "split conocido), cobertura del mapeo de monedas y auto_adjust activo. "
            "También la tabla de horarios UTC vigentes por bolsa que usa el "
            "verificador de timing.")
        if salud_datos["ok"]:
            st.success(f"Sin problemas detectados en {salud_datos['tickers_revisados']} "
                       f"tickers (auto_adjust=True en todas las descargas).")
        else:
            for p in salud_datos["problemas"]:
                st.warning(p)
        st.dataframe(calendarios.tabla_horarios(), use_container_width=True, hide_index=True)

# ============================================================
# SECCIÓN: Detalle (ficha completa por acción)
# ============================================================
if seccion == "Detalle":
    st.subheader("Ficha de la acción")
    opciones_detalle = {f"{d['nombre']} ({t})": t for t, d in UNIVERSO.items()}
    lista_detalle = list(opciones_detalle.keys())
    indice_nvda = next((i for i, k in enumerate(lista_detalle) if "(NVDA)" in k), 0)
    seleccion_detalle = st.selectbox(
        "Elige una acción para ver su ficha completa",
        lista_detalle, index=indice_nvda,
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

        # El Puntaje v0 es un percentil DENTRO del universo de acciones: hay que
        # calcularlo contra todas las acciones, no con esta sola (el ranking de un
        # universo de 1 elemento siempre daría el mismo número).
        precios_universo_d = descargar_precios(ACCIONES, periodo)
        if moneda_usd:
            precios_universo_d = convertir_a_usd(precios_universo_d, tipos_cambio)
        metricas_universo_d = calcular_metricas(precios_universo_d)
        fila_universo = metricas_universo_d[metricas_universo_d["Ticker"] == ticker_d]
        fila_metricas = fila_universo.iloc[0] if not fila_universo.empty else None
        sentimiento_d = noticias.sentimiento_promedio_por_ticker().get(ticker_d)

        par_moneda_d = MONEDA_TICKER.get(ticker_d)
        unidad_d = "USD" if (moneda_usd or par_moneda_d is None) else par_moneda_d.replace("=X", "")
        dias_e_d = dias_earnings.get(ticker_d)
        badge_earnings_d = (badge(f"ZONA EARNINGS · {dias_e_d}d", "magenta")
                            if dias_e_d is not None and dias_e_d < 5 else "")
        tarjetas_d = [
            _tarjeta(f"Precio actual ({unidad_d})", f"{precio_actual:,.2f}",
                     "positivo" if retorno_dia_d >= 0 else "negativo",
                     f"{retorno_dia_d:+.2f}% hoy", badges=badge_earnings_d),
        ]
        if fila_metricas is not None:
            tarjetas_d.append(_tarjeta("Puntaje v0", f"{fila_metricas['Puntaje v0']:.2f}",
                                       "", f"Momentum 20d {fila_metricas['Momentum 20d %']:+.1f}%"))
            tarjetas_d.append(_tarjeta("Volatilidad anual", f"{fila_metricas['Volatilidad anual %']:.1f}%"))
        if sentimiento_d is not None:
            buzz_d = noticias.buzz_por_ticker().get(ticker_d, {})
            badge_buzz_d = (badge(f"ALTO BUZZ · {buzz_d.get('hoy', 0)} titulares hoy", "cyan")
                            if buzz_d.get("buzz") else "")
            tarjetas_d.append(_tarjeta("Sentimiento IA", f"{sentimiento_d:+.2f}",
                                       "positivo" if sentimiento_d >= 0 else "negativo",
                                       "de -1 a +1, con decaimiento temporal",
                                       badges=badge_buzz_d))
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
            yaxis2=dict(showgrid=True, gridcolor=GRIDLINE, zeroline=False, linecolor=BORDE),
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
            # Reutiliza los precios del universo ya descargados para el Puntaje v0.
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
st.caption(f"Etapa 4.6 · modelo v{MODELO_VERSION}: integridad de medición (timestamps "
           "UTC, doble objetivo del anticipador, snapshot programado, motor de "
           "funciones puras) e interfaz at-a-glance. Herramienta de análisis, "
           "no constituye asesoría financiera.")