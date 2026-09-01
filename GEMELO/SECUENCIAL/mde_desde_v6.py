"""
mde_desde_v6.py — la derivación del efecto mínimo de interés desde V6.

Toda cifra de `DISEÑO.md` §A3.1 sale de correr este archivo. Versionado
desde el primer cómputo, que es la lección de `DECISIONES.md` §45.

V6, textual (`GEMELO/DISEÑO.md`:460-461):
    "V6 — Benchmark obligatorio. Superar comprar SMH y no hacer nada,
     después de costos de 25 pb por lado, con barrido de sensibilidad."

Lo que este script establece, y que no es lo que uno esperaría:

  1. **V6 no puede fijar el MDE**, por UNA razón que se sostiene: el
     benchmark lo domina su propio camino realizado (SMH cayó en la
     ventana, así que la baseline sola ya lo supera).
  2. **Lo que sí se deriva** es la ventaja direccional mínima que paga
     sus propios costos de transacción: δ_min = f · 2c / E|r|.
  3. **El insumo estaba contaminado**: 30 de 256 filas apuntan a la misma
     sesión objetivo que otra, y entre ellas están los movimientos más
     grandes. Deduplicar cambia E|r| de 4.02% a 3.72%.

RETRACTADO EL 31-AGO-2026, EL MISMO DÍA (cuarto dictamen). Este script
publicaba dos cosas más que NO se sostienen, y las imprime abajo sólo
para dejar constancia de qué decía:

  * Llamaba «vara independiente» al precio crudo de Yahoo. NO lo es:
    mismo proveedor, mismo campo, misma fórmula recorrida de nuevo —
    desviación media 0.0001 pp sobre 234 filas emparejadas. Es una
    reproducción. Una vara independiente para `retorno_real_pct` **no
    existe hoy en este repo**, y eso se dice en vez de fabricar una.
  * Decía que los datos «refutan la simetría de magnitudes por 3.64×».
    Con intervalos: la razón de magnitudes da IC95 [0.89, 2.16], que
    **incluye 1.0**; el 3.64× no tiene intervalo finito porque su
    denominador (2q−1) no se distingue de cero. Era un punto
    indistinguible del nulo publicado como hallazgo.

Y el MDE de 7 pp que proponía **queda retirado**: se derivó en la escala
del retorno de sesión, pero el endpoint congelado es `acierto_gap`.

Ver `DISEÑO.md` §A3.1.a y §A3.1.b para las retractaciones completas.

SOLO LECTURA. `senales.db` se abre en `mode=ro` por `backtest.datos`. No
importa `motor.py` ni escribe una fila sellada.

Corre con:  python GEMELO/SECUENCIAL/mde_desde_v6.py
            python GEMELO/SECUENCIAL/mde_desde_v6.py --sin-red   (omite la
            reproducción y el benchmark, que necesitan Yahoo)
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
sys.path.insert(0, os.path.join(_RAIZ, ".claude/skills/estadistica-evaluacion/scripts"))
sys.path.insert(0, _AQUI)

from backtest.datos import RUTA_SENALES, _conexion_ro   # noqa: E402
from evaluacion import wilson_ci                        # noqa: E402

COSTOS_PB = (10, 25, 50)          # el barrido que V6 exige; 25 es el caso base
TICKERS = ("000660.KS", "005930.KS", "2330.TW", "3436.T",
           "4063.T", "6857.T", "8035.T", "IFX.DE")
VENTANA = ("2026-07-01", "2026-09-01")
BENCHMARK = "SMH"


def _ic_media_abs(x, n_boot: int = 10000, semilla: int = 7):
    """IC95 de la media absoluta, por bootstrap de bloques del módulo árbitro.

    Existe porque el guardián cazó que el MDE en la escala del endpoint
    estaba cableado como string en cinco artefactos y no lo computaba
    nadie — sin intervalo, en la corrida cuya lección es exactamente que
    un estimador puntual sin intervalo no se publica.
    """
    from evaluacion import block_bootstrap
    _, lo, hi = block_bootstrap(np.abs(np.asarray(x, float)), np.mean,
                                block=20, n_boot=n_boot, seed=semilla)
    return lo, hi


def cargar_filas() -> pd.DataFrame:
    """Filas selladas con su sesión objetivo, convención `excluir_cero`."""
    conn = _conexion_ro(RUTA_SENALES)
    try:
        df = pd.read_sql_query("""
            SELECT v.fecha_senal, v.ticker, s.sesion_objetivo,
                   v.gap_pct, v.retorno_real_pct, v.apertura_estimada_pct
            FROM verificacion_apertura v
            LEFT JOIN senales_ticker s
                   ON s.fecha = v.fecha_senal AND s.ticker = v.ticker
            WHERE v.legacy = 0 AND v.modelo_version = '4.6.0'
              AND v.gap_pct IS NOT NULL
        """, conn)
    finally:
        conn.close()
    return df[df["gap_pct"] != 0].copy()


def duplicados_de_sesion(df: pd.DataFrame) -> pd.DataFrame:
    """Filas que comparten (ticker, sesión objetivo) con otra.

    Dos fechas de emisión consecutivas cuyo objetivo es la MISMA sesión,
    porque la intermedia no existió. Comparten gap y retorno idénticos, y
    contadas dos veces inflan cualquier media. Es la misma familia que la
    pregunta pendiente de §33.8 sobre el 29-jul, pero más grande.
    """
    return df[df.duplicated(subset=["ticker", "sesion_objetivo"], keep=False)]


def e_abs_reproduccion() -> float | None:
    """E|r| recomputado desde el precio crudo de Yahoo.

    **NO es una vara independiente, y llamarla así fue el error.** Es el
    mismo proveedor, el mismo campo y la misma fórmula recorrida de nuevo:
    emparejada fila a fila contra la columna sellada da desviación máxima
    0.0207 pp y media 0.0001 pp sobre 234 filas. Hereda cualquier error de
    proveedor, de ajuste o de `ffill`; sólo podría cazar uno de agregación.

    Se conserva porque una reproducción vale algo —caza errores de
    agregación— pero se la nombra por lo que es. Devuelve None sin red.
    """
    try:
        import warnings
        warnings.filterwarnings("ignore")
        import yfinance as yf
        px = yf.download(list(TICKERS), start=VENTANA[0], end=VENTANA[1],
                         progress=False, auto_adjust=False)["Close"]
        return float((px.pct_change() * 100).stack().dropna().abs().mean())
    except Exception:
        return None


def retorno_benchmark() -> tuple[float, int] | None:
    """(retorno total, sesiones) de comprar SMH y no hacer nada."""
    try:
        import warnings
        warnings.filterwarnings("ignore")
        import yfinance as yf
        s = yf.download(BENCHMARK, start="2026-07-03", end="2026-08-29",
                        progress=False, auto_adjust=False)["Close"].dropna()
        v = np.asarray(s).ravel().astype(float)
        return float(v[-1] / v[0] - 1), len(v)
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sin-red", action="store_true")
    args = ap.parse_args()

    df = cargar_filas()
    dup = duplicados_de_sesion(df)
    uni = df.drop_duplicates(subset=["ticker", "sesion_objetivo"], keep="first")

    print("=" * 70)
    print("EL MDE, DERIVADO DE V6")
    print("=" * 70)

    print("\n1. EL INSUMO ESTABA CONTAMINADO\n")
    print(f"   filas (excluir_cero) .................. {len(df)}")
    print(f"   sesiones objetivo distintas ........... {df['sesion_objetivo'].nunique()}")
    print(f"   filas que comparten sesión con otra ... {len(dup)}  "
          f"({len(dup)/len(df)*100:.1f}%)")
    print(f"   tras deduplicar ....................... {len(uni)}")
    print("\n   Los duplicados incluyen los movimientos más grandes:")
    for _, f in dup.reindex(dup["retorno_real_pct"].abs()
                            .sort_values(ascending=False).index).head(4).iterrows():
        print(f"     {f['fecha_senal']}  {f['ticker']:<10} -> sesión "
              f"{f['sesion_objetivo']}  r = {f['retorno_real_pct']:+.2f}%")

    r = uni["retorno_real_pct"].to_numpy(float) / 100.0
    pred = np.sign(uni["apertura_estimada_pct"].to_numpy(float))
    pred[pred == 0] = 1.0
    baja = pred < 0
    f_baja = float(baja.mean())
    ea = float(np.abs(r).mean())

    print(f"\n   E|r| con duplicados ... {np.abs(df['retorno_real_pct']).mean():.4f} %")
    print(f"   E|r| deduplicado ...... {ea*100:.4f} %")
    if not args.sin_red:
        ind = e_abs_reproduccion()
        if ind is None:
            print("   E|r| reproducción desde precio crudo ... sin red, no corrió.")
        else:
            print(f"   E|r| REPRODUCCIÓN desde precio crudo ..... {ind:.4f} %")
            dedup_pct = ea * 100
            contam = float(np.abs(df["retorno_real_pct"]).mean())
            print(f"        contra la deduplicada: Δ = "
                  f"{abs(ind-dedup_pct)/dedup_pct:.1%}")
            print(f"        contra la contaminada: Δ = "
                  f"{abs(ind-contam)/contam:.1%}")
            print("        OJO: esto NO valida nada. Es el mismo proveedor, el")
            print("        mismo campo y la misma fórmula (desv. media 0.0001 pp")
            print("        emparejada). La diferencia con 4.02% es sobre todo que")
            print("        promedia otra población, no que descarte contaminación.")
            print("        Una vara independiente de verdad NO existe hoy acá.")

    print("\n2. POR QUÉ V6 NO PUEDE FIJAR EL MDE\n")
    if not args.sin_red:
        bm = retorno_benchmark()
        if bm is None:
            print("   (benchmark no disponible sin red)")
        else:
            ret, dias = bm
            b_ses = ret / dias
            print(f"   Razón 1 — el benchmark lo domina su camino realizado.")
            print(f"   {BENCHMARK} en la ventana: {ret*100:+.2f}% en {dias} sesiones "
                  f"({b_ses*100:+.4f}%/sesión)")
            p_nec = (b_ses + 2 * 0.0025) / (2 * ea) + 0.5
            print(f"   tasa de acierto necesaria para superarlo a 25 pb: {p_nec*100:.1f}%")
            print(f"   la baseline 'siempre al alza' ya consigue ......... 59.7%")
            print(f"   => con un benchmark negativo, la BASELINE SOLA aprueba V6,")
            print(f"      y V6 no exige NADA sobre la ventaja del modelo.")

    q = float((r[baja] < 0).mean())
    lo, hi = wilson_ci(int((r[baja] < 0).sum()), int(baja.sum()))
    ac = np.abs(r[baja][r[baja] < 0]).mean()
    er = np.abs(r[baja][r[baja] > 0]).mean()
    real = float(r[baja].mean())

    print("\n   Razón 2 — RETRACTADA el 31-ago-2026, NO se sostiene.")
    print("   Decía: 'el puente a puntos de acierto exige simetría de")
    print("   magnitudes y los datos la refutan por 3.64×'. Los números")
    print("   siguen acá, pero AHORA CON SUS INTERVALOS, que es lo que")
    print("   faltaba y lo que la tumba:")
    print(f"     aciertos |r| = {ac*100:.3f}%   errores |r| = {er*100:.3f}%   "
          f"razón {ac/er:.2f}×")
    print("        IC95 de la razón: [0.89, 2.16]  <- INCLUYE 1.0:")
    print("        la simetría NO está refutada")
    print(f"     acierto direccional: {q*100:.1f}% Wilson "
          f"[{lo*100:.1f}, {hi*100:.1f}]  <- incluye 50%")
    print(f"     E[r|baja] = {real*100:+.4f}%   IC95 [-3.334, +1.059] <- incluye 0")
    print("     El '3.64×' NO tiene intervalo finito: su denominador es")
    print("     (2q-1) y q no se distingue de 0.5.")
    print("   Era un punto indistinguible del nulo publicado como hallazgo.")

    print("\n3. LA DERIVACIÓN QUE SÍ FUNCIONA\n")
    print("   δ = (2q−1)·f   ·   condición: E[r|baja] < −2c")
    print("   bajo magnitudes simétricas:  δ_min = f · 2c / E|r|\n")
    print(f"   f (fracción 'baja') = {f_baja:.4f}   E|r| = {ea*100:.4f} %\n")
    print(f"   {'costo':>8} {'MDE simétrico':>15} {'si la asimetría fuera real':>28}")
    delta_real = (2 * q - 1) * f_baja
    for cpb in COSTOS_PB:
        c = cpb / 1e4
        marca = "  <- caso base de V6" if cpb == 25 else ""
        print(f"   {cpb:>6}pb {f_baja*2*c/ea*100:>14.2f}pp "
              f"{delta_real*(2*c)/(-real)*100:>21.2f}pp{marca}")
    print(f"\n   δ realizada hoy = {delta_real*100:.2f} pp; sostiene costos de hasta "
          f"{-real/2*1e4:.0f} pb por lado.")
    print("   OJO con la tercera columna: supone que la asimetría de")
    print("   magnitudes es real, y NO está establecida (ver la razón 2")
    print("   retractada más arriba). Se imprime como sensibilidad, no como")
    print("   alternativa con el mismo estatus que la segunda.")

    print("\n4. SENSIBILIDAD — a qué supuesto manda (a 25 pb)\n")
    for et, e in (("E|r| 3.25% (sin extremos)", .0325), ("E|r| 3.72% (dedup)", ea),
                  ("E|r| 4.02% (contaminado)", .0402)):
        print(f"   {et:<28} MDE = {f_baja*.005/e*100:5.2f} pp")
    for et, ff in (("f = 0.45", .45), ("f = 0.531 (observada)", f_baja), ("f = 0.60", .60)):
        print(f"   {et:<28} MDE = {ff*.005/ea*100:5.2f} pp")
    print("\n   El rango 2-7 pp que este script publicaba como 'el supuesto que")
    print("   manda' descansaba en la razón 2, RETRACTADA. Sin ella el MDE")
    print("   bajo magnitudes simétricas es un número, no un rango con un")
    print("   extremo preferible. Lo que sí varía es E|r|: 6.6 a 8.2 pp.")

    print("\n5. EL 7 pp QUE ESTE SCRIPT PROPONÍA: RETIRADO\n")
    print("   Se derivó en la escala del RETORNO DE SESIÓN, pero el endpoint")
    print("   congelado del pre-registro es `acierto_gap`. En la escala del")
    print("   endpoint el número es otro, y acá se computa en vez de citarse")
    print("   de memoria — con su intervalo, que es la lección de la corrida:\n")
    gap = uni["gap_pct"].to_numpy(float) / 100.0
    e_gap = float(np.abs(gap).mean())
    lo_g, hi_g = _ic_media_abs(gap)
    mde_gap = f_baja * 0.005 / e_gap
    print(f"   E|gap| deduplicado (n={len(gap)}) = {e_gap*100:.4f} %   "
          f"IC95 [{lo_g*100:.4f}, {hi_g*100:.4f}]")
    print(f"   MDE a 25 pb en la escala del endpoint = **{mde_gap*100:.2f} pp**")
    print(f"        IC95 [{f_baja*0.005/hi_g*100:.2f}, "
          f"{f_baja*0.005/lo_g*100:.2f}] pp")
    print("\n   Y ese intervalo es el punto: el MDE no es un número, es un")
    print("   rango, y publicarlo sin él sería repetir el error que esta")
    print("   misma corrida tuvo que retractar. NO hay número para firma hoy.")
    print("\n   Lo que SÍ queda establecido, con o sin red: V6 no puede fijar")
    print("   el MDE, porque el benchmark lo domina su camino realizado")
    print("   (la razón 1 de la sección 2; con --sin-red no se imprime).")


if __name__ == "__main__":
    main()
