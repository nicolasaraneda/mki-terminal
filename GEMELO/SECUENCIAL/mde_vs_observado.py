"""mde_vs_observado.py — ¿el MDE y la ventaja publicada son comparables?

Toda cifra de `GEMELO/resultados/mde_vs_observado.md` sale de correr este
archivo. Existe porque la regla 2 de la casa dice que una corrección va al
código antes que a la prosa, y la regla 3 dice que el intervalo se computa,
no se estima de memoria.

Lo que establece, en orden:

  D1a  EL PUENTE, verificado por un mecanismo distinto del que produjo el
       MDE. El lado izquierdo de la desigualdad del MDE es la identidad
       δ = f·(2q−1). Se contrasta contra (b−c)/n de la tabla de McNemar y
       contra la diferencia cruda de tasas. Ni b, ni c, ni las tasas
       entran en el cómputo del MDE: si las tres coinciden a 10 decimales,
       las dos cantidades viven en la MISMA escala. No es recorrer la misma
       conversión otra vez.

  D1b  EL DENOMINADOR, que NO coincide. El 8.96 pp publicado se computa
       sobre filas deduplicadas y SIN ancla temporal (`mde_desde_v6.py`
       escribe su propio SQL). La ventaja publicada se computa sobre las
       248 filas ancladas a `verificado_en <= 2026-08-28`. Acá se recomputa
       el MDE sobre EL MISMO conjunto de filas.

  D1c  EL INTERVALO DEL MDE PROPAGA UN SOLO INSUMO. [6.67, 11.32] es el
       intervalo de E|gap| invertido; `f` entra como punto y el supuesto de
       simetría de magnitudes —que §A3.1.c declara "el supuesto que
       manda"— entra como certeza. Acá se propagan los tres.

  D2   LA COMPARACIÓN PAREADA. δ_obs y el MDE se estiman sobre las MISMAS
       filas, así que su diferencia admite un bootstrap pareado de
       clústeres de día. Es la única forma honesta de preguntar si el
       efecto observado cae por debajo del umbral de relevancia.

SOLO LECTURA. `senales.db` se abre en `mode=ro` vía `backtest.linea_base`.
No importa `motor.py` y no escribe ninguna fila sellada.

Corre con:  python GEMELO/SECUENCIAL/mde_vs_observado.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
sys.path.insert(0, os.path.join(_RAIZ, ".claude/skills/estadistica-evaluacion/scripts"))

from backtest.datos import RUTA_SENALES, _conexion_ro          # noqa: E402
from backtest.linea_base import aplicar_convencion, cargar     # noqa: E402
from evaluacion import block_bootstrap, mcnemar_exact, wilson_ci  # noqa: E402

# El corte `publicado` del ancla de `GEMELO/bifurcaciones.py`: el conjunto
# exacto de 248 filas sobre el que el README publica +6.5 pp. Anclado a
# propósito — sin esto la cifra se mueve con el reloj, que es el defecto
# que el cuarto dictamen le encontró a `mde_desde_v6.py` y que sigue vivo.
CORTE_PUBLICADO = "2026-08-28"
COSTO_LADO = 0.0025          # 25 pb, el caso base de V6
BLOQUE = 20                  # bloque de la casa para bootstrap de filas
N_BOOT = 10_000
SEMILLA_BLOQUE = 7
SEMILLA_DIA = 20260901

# Lo que `DISEÑO.md` §A3.1 publica hoy, para contrastar y NO para citar.
MDE_PUBLICADO = (8.96, 6.67, 11.32)


def ancla() -> pd.DataFrame:
    """Las 248 filas de la ventana sellada canónica, convención excluir_cero."""
    return aplicar_convencion(
        cargar(hasta_sello=CORTE_PUBLICADO), "excluir_cero"
    ).reset_index(drop=True)


def mde_simetrico(f: float, e_abs: float, c: float = COSTO_LADO) -> float:
    """δ_min = f · 2c / E|gap|, en pp. La fórmula de §A3.1.c."""
    return f * 2 * c / e_abs * 100


def mde_general(f: float, a: float, w: float, c: float = COSTO_LADO) -> float:
    """δ_min sin suponer simetría de magnitudes, en pp.

    `a` = E[|gap| | el modelo dijo baja y acertó]; `w` = el mismo con error.
    Con a = w = E|gap| se reduce exactamente a `mde_simetrico`; el test lo
    comprueba. La forma general importa porque §A3.1.c declara que la
    simetría es "el supuesto que manda" y el intervalo publicado no la
    propaga.
    """
    return 2 * f * (2 * c - (a - w) / 2) / (a + w) * 100


def dedup_por_sesion(df: pd.DataFrame) -> pd.DataFrame:
    """Una fila por (ticker, sesión objetivo). La regla de §A3.1.a."""
    conn = _conexion_ro(RUTA_SENALES)
    try:
        ses = pd.read_sql_query(
            "SELECT fecha, ticker, sesion_objetivo FROM senales_ticker", conn)
    finally:
        conn.close()
    m = df.merge(ses, on=["fecha", "ticker"], how="left")
    return m.drop_duplicates(subset=["ticker", "sesion_objetivo"], keep="first")


def _boot_dias(df: pd.DataFrame, fn, n_boot: int = N_BOOT,
               semilla: int = SEMILLA_DIA):
    """Bootstrap de CLÚSTERES DE DÍA. La unidad real de este experimento.

    Las ~7.3 filas de una sesión son βᵢ·SOX sobre el MISMO movimiento del
    SOX: aciertan y fallan casi todas juntas (ICC 0.403, deff 3.63, n
    efectivo 68). Un bootstrap de filas produce intervalos falsamente
    angostos; uno de bloques de 20 filas, menos falsos pero todavía
    angostos, porque el bloque no respeta el borde del día.
    """
    fecha = df["fecha"].to_numpy()
    dias = pd.unique(fecha)
    idx = {d: np.where(fecha == d)[0] for d in dias}
    rng = np.random.default_rng(semilla)
    out = []
    for _ in range(n_boot):
        sel = rng.choice(dias, size=len(dias), replace=True)
        out.append(fn(np.concatenate([idx[d] for d in sel])))
    return np.array(out)


def _ic(x, p=(2.5, 97.5)):
    return float(np.percentile(x, p[0])), float(np.percentile(x, p[1]))


def main() -> None:
    df = ancla()
    gap = df["gap_pct"].to_numpy(float) / 100
    est = df["apertura_estimada_pct"].to_numpy(float)
    mod = df["acierto_gap"].to_numpy(int)
    base = df["base_acierto"].to_numpy(int)
    n = len(df)

    print("=" * 72)
    print("EL MDE CONTRA LA VENTAJA OBSERVADA")
    print("=" * 72)
    print(f"\nancla: n={n}  días={df['fecha'].nunique()}  "
          f"corte verificado_en <= {CORTE_PUBLICADO}  convención excluir_cero")

    # ---------- D1a. El puente ----------
    print("\n" + "-" * 72)
    print("D1a. ¿MISMA ESCALA? — el puente, por tres caminos distintos")
    print("-" * 72)
    b = int(((mod == 1) & (base == 0)).sum())
    c_ = int(((mod == 0) & (base == 1)).sum())
    via_tasas = (mod.mean() - base.mean()) * 100
    via_mcnemar = (b - c_) / n * 100
    baja = est < 0
    f_obs = float(baja.mean())
    q_obs = float((gap[baja] < 0).mean())
    via_identidad = f_obs * (2 * q_obs - 1) * 100

    print(f"  [A] diferencia de tasas ....... {via_tasas:.10f} pp   "
          f"(modelo {mod.mean()*100:.4f}%  base {base.mean()*100:.4f}%)")
    print(f"  [B] (b−c)/n de McNemar ........ {via_mcnemar:.10f} pp   "
          f"(b={b}, c={c_}, p exacto {mcnemar_exact(b, c_):.4f})")
    print(f"  [C] identidad del MDE f·(2q−1)  {via_identidad:.10f} pp   "
          f"(f={f_obs:.6f}, q={q_obs:.6f})")
    assert abs(via_tasas - via_identidad) < 1e-9
    assert abs(via_mcnemar - via_identidad) < 1e-9
    disidencia = int((mod != base).sum())
    print(f"\n  filas donde modelo != baseline: {disidencia}   "
          f"filas 'baja': {int(baja.sum())}   idénticas: "
          f"{disidencia == int(baja.sum())}")
    print("  => el lado izquierdo de la desigualdad del MDE ES la ventaja")
    print("     publicada. MISMA ESCALA, verificada con b, c y las tasas,")
    print("     que no entran en el cómputo del MDE.")
    lo, hi = wilson_ci(int((gap[baja] < 0).sum()), int(baja.sum()))
    print(f"  q Wilson95 = [{lo*100:.1f}, {hi*100:.1f}]  "
          f"— incluye 50%: {lo < 0.5 < hi}")

    # ---------- D1b. El denominador ----------
    print("\n" + "-" * 72)
    print("D1b. ¿MISMO DENOMINADOR? — no")
    print("-" * 72)
    e_gap = float(np.abs(gap).mean())
    _, lo_g, hi_g = block_bootstrap(np.abs(gap), np.mean, block=BLOQUE,
                                    n_boot=N_BOOT, seed=SEMILLA_BLOQUE)
    print(f"  sobre las MISMAS {n} filas:  f={f_obs:.4f}  "
          f"E|gap|={e_gap*100:.4f}%  IC95 bloque{BLOQUE} "
          f"[{lo_g*100:.4f}, {hi_g*100:.4f}]")
    m_mismas = mde_simetrico(f_obs, e_gap)
    print(f"  MDE sobre las mismas filas ......... {m_mismas:.2f} pp   "
          f"IC95 (sólo E|gap|) [{mde_simetrico(f_obs, hi_g):.2f}, "
          f"{mde_simetrico(f_obs, lo_g):.2f}]")

    uni = dedup_por_sesion(df)
    gu = uni["gap_pct"].to_numpy(float) / 100
    fu = float((uni["apertura_estimada_pct"].to_numpy(float) < 0).mean())
    eu = float(np.abs(gu).mean())
    _, lo_u, hi_u = block_bootstrap(np.abs(gu), np.mean, block=BLOQUE,
                                    n_boot=N_BOOT, seed=SEMILLA_BLOQUE)
    print(f"  dedup POR SESIÓN y anclado (n={len(uni)}): f={fu:.4f}  "
          f"E|gap|={eu*100:.4f}%")
    print(f"  MDE dedup+anclado .................. "
          f"{mde_simetrico(fu, eu):.2f} pp   IC95 "
          f"[{mde_simetrico(fu, hi_u):.2f}, {mde_simetrico(fu, lo_u):.2f}]")
    print(f"  MDE publicado (dedup, SIN ancla) ... {MDE_PUBLICADO[0]:.2f} pp   "
          f"IC95 [{MDE_PUBLICADO[1]:.2f}, {MDE_PUBLICADO[2]:.2f}]")
    print("  => tres números distintos. El publicado se computa sobre un")
    print("     conjunto que se mueve con el reloj; el ancla no.")

    # ---------- D1c. El intervalo propaga un solo insumo ----------
    print("\n" + "-" * 72)
    print("D1c. EL INTERVALO DEL MDE PROPAGA UN SOLO INSUMO DE TRES")
    print("-" * 72)
    f_lo, f_hi = wilson_ci(int(baja.sum()), n)
    print(f"  eje 1 — E|gap| (el único propagado):  "
          f"[{mde_simetrico(f_obs, hi_g):.2f}, "
          f"{mde_simetrico(f_obs, lo_g):.2f}] pp")
    print(f"  eje 2 — f, Wilson [{f_lo:.4f}, {f_hi:.4f}]: "
          f"sumado da [{mde_simetrico(f_lo, hi_g):.2f}, "
          f"{mde_simetrico(f_hi, lo_g):.2f}] pp")
    a = float(np.abs(gap[baja & (gap < 0)]).mean())
    w = float(np.abs(gap[baja & (gap > 0)]).mean())
    sub = df[baja]["gap_pct"].to_numpy(float)

    def razon(x):
        neg, pos = np.abs(x[x < 0]), np.abs(x[x > 0])
        if len(neg) == 0 or len(pos) == 0:
            return np.nan
        return neg.mean() / pos.mean()

    _, r_lo, r_hi = block_bootstrap(sub, razon, block=BLOQUE,
                                    n_boot=N_BOOT, seed=SEMILLA_BLOQUE)
    print(f"\n  eje 3 — SIMETRÍA DE MAGNITUDES, no propagado en absoluto.")
    print(f"    |gap| cuando acierta la baja  A = {a*100:.4f}%")
    print(f"    |gap| cuando se equivoca      W = {w*100:.4f}%")
    print(f"    razón A/W = {a/w:.3f}×   IC95 bloque{BLOQUE} "
          f"[{r_lo:.3f}, {r_hi:.3f}]  incluye 1.0: {r_lo < 1 < r_hi}")
    print(f"    MDE con las magnitudes OBSERVADAS = "
          f"{mde_general(f_obs, a, w):.2f} pp   (simétrico: {m_mismas:.2f})")
    for r in (r_lo, 1.0, r_hi):
        wx = 2 * e_gap / (1 + r)
        print(f"      razón {r:.3f} -> MDE {mde_general(f_obs, r*wx, wx):>7.2f} pp")
    print("  => el eje que §A3.1.c llama 'el supuesto que manda' es el único")
    print("     que el intervalo publicado NO propaga. Y en la escala del")
    print("     endpoint la asimetría apunta al lado CONTRARIO del que la")
    print("     razón 2 retractada suponía: el modelo se equivoca más grande")
    print("     de lo que acierta.")

    # ---------- D2. La comparación pareada ----------
    print("\n" + "-" * 72)
    print("D2. LA COMPARACIÓN PAREADA — δ_obs contra el MDE, MISMAS filas")
    print("-" * 72)

    def par(i):
        d_obs = (mod[i] - base[i]).mean() * 100
        d_min = mde_simetrico(float((est[i] < 0).mean()),
                              float(np.abs(gap[i]).mean()))
        return d_obs, d_min

    reps = _boot_dias(df, lambda i: par(i))
    O, M = reps[:, 0], reps[:, 1]
    D = O - M
    o_lo, o_hi = _ic(O)
    m_lo, m_hi = _ic(M)
    d_lo, d_hi = _ic(D)
    print(f"  δ_obs = {via_tasas:.2f} pp   IC95 clúster-día "
          f"[{o_lo:.2f}, {o_hi:.2f}]  (ancho {o_hi-o_lo:.1f} pp)")
    print(f"  MDE   = {m_mismas:.2f} pp   IC95 clúster-día "
          f"[{m_lo:.2f}, {m_hi:.2f}]")
    print(f"  δ_obs − MDE = {via_tasas-m_mismas:+.2f} pp   IC95 PAREADO "
          f"[{d_lo:+.2f}, {d_hi:+.2f}]   contiene el cero: "
          f"{d_lo < 0 < d_hi}")
    print(f"  P(δ_obs < MDE) en el remuestreo = {np.mean(D < 0):.3f}  "
          "— una moneda")
    for u in MDE_PUBLICADO[:2] + (m_mismas,):
        print(f"    P(δ_obs < {u:.2f} pp) = {np.mean(O < u):.3f}")
    print("\n  => el experimento NO ORDENA las dos cantidades. Afirmar que el")
    print("     efecto observado cae por debajo del umbral de relevancia es")
    print("     una comparación punto contra punto disfrazada de hallazgo.")

    # ---------- D4. La matriz ----------
    ruta = os.path.join(_RAIZ, "GEMELO/resultados/bifurcaciones.csv")
    if os.path.exists(ruta):
        print("\n" + "-" * 72)
        print("D4. LAS 768 CELDAS CONTRA EL MDE")
        print("-" * 72)
        bif = pd.read_csv(ruta)
        print(f"  {'umbral':>8} {'punto>u':>9} {'IC entero >u':>13} "
              f"{'IC entero <u':>13} {'IC contiene u':>14}")
        for u in (MDE_PUBLICADO[1], m_mismas, MDE_PUBLICADO[0],
                  MDE_PUBLICADO[2]):
            print(f"  {u:>7.2f}pp {int((bif.ventaja_pp > u).sum()):>6}/768 "
                  f"{int((bif.ventaja_lo > u).sum()):>10}/768 "
                  f"{int((bif.ventaja_hi < u).sum()):>10}/768 "
                  f"{int(((bif.ventaja_lo <= u) & (bif.ventaja_hi >= u)).sum()):>11}/768")
        print("  => por punto, cientos de celdas superan el MDE. Por intervalo,")
        print("     NINGUNA lo supera y NINGUNA queda por debajo: las 768 lo")
        print("     contienen. La matriz no separa 'irrelevante' de 'relevante'")
        print("     en ninguna de sus celdas.")
    print()


def _self_test() -> None:
    """Se corre siempre: la forma general debe reducirse a la simétrica."""
    a = mde_general(0.5161, 0.033347, 0.033347)
    b = mde_simetrico(0.5161, 0.033347)
    assert abs(a - b) < 1e-10, (a, b)


if __name__ == "__main__":
    _self_test()
    main()
