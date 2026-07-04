# ============================================================
# Bot Comparador de Acciones - Etapa 2
# Nuevo: relación entre mercados globales (con desfase horario)
#        y anticipador de aperturas de Asia/Europa
# Ejecutar con:  python -m streamlit run app.py
# ============================================================

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Comparador de Semiconductores", layout="wide")

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


# ------------------------------------------------------------
# Interfaz
# ------------------------------------------------------------
st.title("Comparador global de semiconductores")
st.caption("Etapa 2 - Datos de Yahoo Finance (retraso ~15 min). "
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

if len(tickers) < 2:
    st.info("Selecciona al menos 2 acciones en la barra lateral.")
    st.stop()

precios = descargar_precios(tickers, periodo)
indices = descargar_precios(tuple(INDICES.keys()), periodo)

if precios.empty:
    st.error("No se pudieron descargar datos. Revisa tu conexión o espera unos minutos.")
    st.stop()

tab1, tab2, tab3 = st.tabs([
    "📊 Comparador", "🌏 Relación entre mercados", "🌅 Anticipador de aperturas"])

# ============================================================
# TAB 1 - Comparador (Etapa 1)
# ============================================================
with tab1:
    st.subheader("Rendimiento comparado (base 100)")
    st.caption("Todas parten en 100 al inicio del período elegido: si una línea "
               "termina en 200, esa acción duplicó su valor en la ventana mostrada.")
    base100 = precios / precios.iloc[0] * 100
    df_plot = base100.reset_index().melt(id_vars="Date", var_name="Ticker", value_name="Índice")
    df_plot["Empresa"] = df_plot["Ticker"].map(nombre)
    fig = px.line(df_plot, x="Date", y="Índice", color="Empresa")
    fig.update_layout(height=430, legend_title=None, xaxis_title=None, yaxis_title="Base 100")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Correlación entre acciones")
    st.caption("1.0 = se mueven idéntico. Ojo: acciones de la misma bolsa correlacionan "
               "más alto entre sí por compartir horario, no solo por su negocio.")
    retornos = precios.pct_change().dropna(how="all")
    corr = retornos.corr().round(2)
    noms = [nombre(t) for t in corr.columns]
    fig_corr = go.Figure(go.Heatmap(z=corr.values, x=noms, y=noms, zmin=-1, zmax=1,
                                    colorscale="RdBu_r", text=corr.values,
                                    texttemplate="%{text}"))
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("Métricas y ranking preliminar")
    st.dataframe(calcular_metricas(precios), use_container_width=True, hide_index=True)

# ============================================================
# TAB 2 - Relación entre mercados globales
# ============================================================
with tab2:
    st.subheader("¿Qué índice mueve a cada acción?")
    st.caption("Correlación de cada acción con los índices de referencia del mundo, "
               "comparando retornos del mismo día calendario.")

    ret_acc = precios.pct_change()
    ret_idx = indices.pct_change()

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
        zmin=-1, zmax=1, colorscale="RdBu_r",
        text=corr_cruzada.values, texttemplate="%{text}"))
    fig_x.update_layout(height=480)
    st.plotly_chart(fig_x, use_container_width=True)

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
                    "¿Reacciona con desfase?": "✅ Sí" if c1 > c0 + 0.05 else "—",
                })
        st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
        st.info(
            "💡 Cómo leerlo: las acciones de EE.UU. correlacionan alto el mismo día "
            "(cotizan junto al SOX). Las coreanas, japonesas y taiwanesas suelen "
            "correlacionar más con el SOX **del día anterior**: cuando Seúl abre, "
            "Nueva York ya cerró hace horas y esa información 'llega' a Asia recién "
            "en su apertura. Esta asimetría es la base del anticipador (pestaña 3).")

# ============================================================
# TAB 3 - Anticipador de aperturas
# ============================================================
with tab3:
    st.subheader("¿Cómo debería abrir Asia y Europa según lo último de EE.UU.?")
    st.caption(
        "Modelo estadístico simple (Etapa 2): medimos históricamente cuánto se mueve "
        "cada acción asiática/europea al día siguiente de un movimiento del índice SOX "
        "de EE.UU. (su 'beta de contagio'), y lo aplicamos al último cierre americano. "
        "Es una ESTIMACIÓN de tendencia, no una predicción garantizada: las noticias "
        "locales pueden dominar cualquier día. En la Etapa 3, la IA sumará ese contexto.")

    if "^SOX" not in ret_idx.columns:
        st.warning("No se pudo descargar el índice SOX. Intenta de nuevo más tarde.")
    else:
        sox = ret_idx["^SOX"].dropna()
        ult_fecha = sox.index[-1].date()
        ult_mov = sox.iloc[-1] * 100
        c1, c2 = st.columns(2)
        c1.metric("Último movimiento del SOX (EE.UU.)", f"{ult_mov:+.2f}%",
                  help=f"Sesión del {ult_fecha}")
        c2.metric("Índice", "SOX - Semiconductores de Filadelfia",
                  help="Agrupa a los principales semiconductores que cotizan en EE.UU.")

        filas = []
        for t in MERCADOS_POR_ABRIR:
            if t not in ret_acc.columns:
                continue
            par = pd.concat([ret_acc[t], ret_idx["^SOX"].shift(1)], axis=1).dropna()
            if len(par) < 40:
                continue
            y, x = par.iloc[:, 0], par.iloc[:, 1]
            beta = x.cov(y) / x.var() if x.var() > 0 else 0.0
            r2 = x.corr(y) ** 2
            est = beta * (ult_mov / 100) * 100
            confianza = "Alta" if r2 > 0.25 else ("Media" if r2 > 0.10 else "Baja")
            filas.append({
                "Acción": nombre(t),
                "Mercado": UNIVERSO.get(t, ("", ""))[1].split(" - ")[0],
                "Beta de contagio": round(beta, 2),
                "Apertura estimada %": round(est, 2),
                "Confianza (R²)": f"{confianza} ({r2:.2f})",
            })
        df_ant = pd.DataFrame(filas)
        if df_ant.empty:
            st.warning("Sin datos suficientes para estimar. Prueba con período de 1 año o más.")
        else:
            df_ant = df_ant.sort_values("Apertura estimada %", ascending=False)
            fig_ant = px.bar(df_ant, x="Acción", y="Apertura estimada %",
                             color="Apertura estimada %",
                             color_continuous_scale="RdYlGn", text="Apertura estimada %")
            fig_ant.update_traces(texttemplate="%{text:+.2f}%", textposition="outside")
            fig_ant.update_layout(height=380, coloraxis_showscale=False, xaxis_title=None)
            st.plotly_chart(fig_ant, use_container_width=True)
            st.dataframe(df_ant, use_container_width=True, hide_index=True)
            st.info(
                "💡 Cómo leerlo: 'Beta de contagio' = cuánto se mueve históricamente esa "
                "acción por cada 1% que se movió el SOX el día anterior. 'Confianza (R²)' "
                "= qué parte de sus movimientos se explica por EE.UU. (el resto es su "
                "propia historia local). Con confianza Baja, tómalo como brisa, no viento.")

st.divider()
st.caption("Próxima etapa: capa de IA con análisis de noticias en tiempo real "
           "y explicación en lenguaje natural de cada señal.")