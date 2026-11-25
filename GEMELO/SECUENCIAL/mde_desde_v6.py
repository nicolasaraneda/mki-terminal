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
     sus propios costos de transacción: δ_min = f · 2c / E|gap|.
  3. **El insumo estaba contaminado**: hay filas que apuntan a la misma
     sesión objetivo que otra, y entre ellas están los movimientos más
     grandes. La regla de deduplicación firmada el 1-sep-2026 retira las
     del defecto de `snapshot.py` y conserva las dos de cada par de
     feriado; eso baja E|r| y E|gap|.

LO QUE CAMBIÓ EN LA CORRIDA 17 (25-oct-2026), y es la **condición 4** del
cuarto dictamen:

  * **Este script ya no escribe su propio SQL.** La ventana antecedente la
    define `GEMELO/SECUENCIAL/ventana_antecedente.py`, con DOS cortes
    explícitos (emisión hasta el 2026-08-31, sello hasta el 2026-09-02) y
    pasando por la misma exclusión de conocibilidad que las cifras
    publicadas. Antes no había ancla temporal: el MDE de hoy era un número
    distinto del de mañana, y el pre-registro lo citaba como parámetro. Esa
    era la causa raíz que el dictamen nombró, y la frase con la que lo
    resumió: *un pre-registro que no reproduce el día que se firma no está
    congelado, está fechado.*
  * **Se aplica la REGLA FIRMADA de deduplicación**, no `keep="first"`.
    La versión anterior deduplicaba con `drop_duplicates(keep="first")`,
    que no es la regla que Nicolás firmó: la firmada conserva la fila cuya
    `sesion_objetivo` coincide con `calendarios.proxima_sesion_despues_de`
    y deja las DOS cuando las dos calzan. Un parámetro de estorbo medido
    con una regla distinta de la del estimador es el defecto descalificante
    del cuarto dictamen, visto del otro lado.
  * **El intervalo del MDE propaga `f` y `E|gap|` juntos**, por bootstrap
    de clústeres de día. El intervalo que este script publicaba era el de
    `E|gap|` invertido —un insumo de tres— y el Frente D del 1-sep ya lo
    había medido (`GEMELO/resultados/mde_vs_observado.md` D1c). El tercer
    eje, la simetría de magnitudes, queda declarado FUERA del intervalo con
    su sensibilidad al lado, que es una de las tres salidas que ese
    documento admitía.
  * **La razón 1 de §A3.1.b lleva intervalo** (condición 2): la tasa de
    acierto necesaria para superar el benchmark se propaga desde E|r|, y la
    tasa de la baseline lleva su Wilson. El camino realizado de SMH no
    lleva intervalo y se dice por qué: es un hecho, no una estimación.

RETRACTADO EL 31-AGO-2026 y conservado acá sólo para dejar constancia de
qué decía este script:

  * Llamaba «vara independiente» al precio crudo de Yahoo. NO lo es:
    mismo proveedor, mismo campo, misma fórmula recorrida de nuevo —
    desviación media 0.0001 pp sobre 234 filas emparejadas. Es una
    reproducción. Una vara independiente para `retorno_real_pct` **no
    existe hoy en este repo**, y eso se dice en vez de fabricar una.
  * Decía que los datos «refutan la simetría de magnitudes». La cifra que
    lo cuantificaba está RETIRADA (`GEMELO/cifras_retiradas.md`, acta §56):
    con intervalos, la razón de magnitudes incluye 1.0 y el cociente que la
    resumía no tiene intervalo finito, porque su denominador (2q−1) no se
    distingue de cero. Era un punto indistinguible del nulo publicado como
    hallazgo.

Ver `DISEÑO.md` §A3.1.a y §A3.1.b para las retractaciones completas.

SOLO LECTURA. `senales.db` se abre en `mode=ro` a través de
`backtest.linea_base`. No importa `motor.py` ni escribe una fila sellada.

Corre con:  python -m GEMELO.SECUENCIAL.mde_desde_v6
            python -m GEMELO.SECUENCIAL.mde_desde_v6 --sin-red   (omite la
            reproducción y el benchmark, que necesitan Yahoo)
            python -m GEMELO.SECUENCIAL.mde_desde_v6 --json      (para que
            los demás scripts no vuelvan a consultar la base)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

_AQUI = os.path.dirname(os.path.abspath(__file__))
_RAIZ = os.path.dirname(os.path.dirname(_AQUI))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)
sys.path.insert(0, os.path.join(_RAIZ, ".claude/skills/estadistica-evaluacion/scripts"))

from GEMELO.SECUENCIAL import ventana_antecedente as va   # noqa: E402
from evaluacion import wilson_ci                          # noqa: E402

COSTOS_PB = (10, 25, 50)          # el barrido que V6 exige; 25 es el caso base
COSTO_BASE_PB = 25
TICKERS = ("000660.KS", "005930.KS", "2330.TW", "3436.T",
           "4063.T", "6857.T", "8035.T", "IFX.DE")
VENTANA = ("2026-07-01", "2026-09-01")
BENCHMARK = "SMH"

# El bootstrap del intervalo del MDE. Clústeres de día, 10.000 réplicas,
# semilla congelada: los tres valen lo mismo acá y en
# `mde_vs_observado.py`, que es el otro lugar donde se mide esta cantidad.
N_BOOT = 10_000
SEMILLA_DIA = 20260901


def _ic(x, p=(2.5, 97.5)) -> tuple[float, float]:
    return float(np.percentile(x, p[0])), float(np.percentile(x, p[1]))


def cargar_filas(dedup: bool = True):
    """La ventana antecedente, anclada, convención `excluir_cero`.

    Delega en `ventana_antecedente`: este script ya no sabe SQL, y por eso
    ya no puede perder el ancla. Es la condición 4.
    """
    return va.cargar_antecedente(convencion=va.CONVENCION, dedup=dedup)


def mde_simetrico(f: float, e_abs: float, c: float) -> float:
    """δ_min = f · 2c / E|gap|, en pp. La fórmula de §A3.1.c.

    `c` es el costo POR LADO en proporción (0.0025 = 25 pb).
    """
    return f * 2 * c / e_abs * 100


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
    """(retorno total, sesiones) de comprar SMH y no hacer nada.

    **Sin intervalo, a propósito.** Es el camino REALIZADO del benchmark en
    la ventana, no una estimación de su retorno esperado: no hay un
    parámetro poblacional del que éste sea una muestra. Ponerle un
    intervalo supondría que la ventana es un sorteo de un proceso
    estacionario, que es justamente lo que la razón 1 niega.
    """
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


def medir(dedup: bool = True, c_pb: int = COSTO_BASE_PB) -> dict:
    """Los parámetros de estorbo de §A2 y el MDE, con sus intervalos.

    Todo lo que sale de acá es un parámetro de estorbo o un umbral: ninguna
    ventaja del modelo contra la baseline y ningún p se computan en este
    módulo, en la ventana antecedente ni en ninguna otra. §A2 lo exige y
    «Qué NO se hace» lo repite.
    """
    df = cargar_filas(dedup=dedup)
    crudo = cargar_filas(dedup=False)
    c = c_pb / 1e4

    gap = df["gap_pct"].to_numpy(float) / 100.0
    r = df["retorno_real_pct"].to_numpy(float) / 100.0
    est = df["apertura_estimada_pct"].to_numpy(float)
    baja = est < 0

    # p_d, la tasa de discordancia que fija el n de Connor. Se computa la
    # SUMA de los discordantes, nunca su diferencia: b+c es el parámetro de
    # estorbo que §A2 autoriza, b−c es la ventaja y no se computa acá.
    mod = df["acierto_gap"].to_numpy(int)
    base = df["base_acierto"].to_numpy(int)
    discordantes = int((mod != base).sum())

    f = float(baja.mean())
    e_gap = float(np.abs(gap).mean())
    e_r = float(np.abs(r).mean())

    # El intervalo del MDE, con los DOS insumos que son estimaciones
    # propagados JUNTOS sobre los mismos clústeres de día. Que vayan juntos
    # importa: `f` y `E|gap|` se estiman sobre las mismas filas y están
    # correlacionados, así que sumar sus intervalos por separado —como
    # hacía la tabla de D1c— no da el intervalo conjunto.
    def _mde(idx):
        return mde_simetrico(float(baja[idx].mean()),
                             float(np.abs(gap[idx]).mean()), c)

    reps_mde = va.boot_dias(df, _mde, n_boot=N_BOOT, semilla=SEMILLA_DIA)
    reps_f = va.boot_dias(df, lambda i: float(baja[i].mean()),
                          n_boot=N_BOOT, semilla=SEMILLA_DIA)
    reps_eg = va.boot_dias(df, lambda i: float(np.abs(gap[i]).mean()),
                           n_boot=N_BOOT, semilla=SEMILLA_DIA)

    mde = mde_simetrico(f, e_gap, c)
    lo, hi = _ic(reps_mde)
    lo_f, hi_f = _ic(reps_f)
    lo_g, hi_g = _ic(reps_eg)

    # La tasa de la baseline «siempre al alza»: cuántas veces el gap es
    # positivo. Es una propiedad del MERCADO, no una tasa de acierto del
    # modelo ni una ventaja; entra sólo en la razón 1 de §A3.1.b, que la
    # compara contra la tasa que el benchmark exige.
    alza = int((gap > 0).sum())
    tasa_base = alza / len(gap)
    lo_b, hi_b = wilson_ci(alza, len(gap))

    pares = va.pares_misma_sesion(cargar_filas(dedup=False))
    pares_post = va.pares_misma_sesion(df)

    return {
        "cortes": {"emision": va.CORTE_EMISION, "sello": va.CORTE_SELLO,
                   "convencion": va.CONVENCION, "dedup_regla_firmada": dedup},
        "n": len(df), "fechas": int(df["fecha"].nunique()),
        "n_sin_dedup": len(crudo),
        "retiradas_por_la_regla": len(crudo) - len(df),
        "pares_antes": pares, "pares_despues": pares_post,
        "p_d": discordantes / len(df), "discordantes": discordantes,
        "f": f, "f_ic": (lo_f, hi_f),
        "e_gap_pct": e_gap * 100, "e_gap_ic_pct": (lo_g * 100, hi_g * 100),
        "e_r_pct": e_r * 100,
        "e_r_sin_dedup_pct": float(np.abs(
            crudo["retorno_real_pct"].to_numpy(float)).mean()),
        "e_gap_sin_dedup_pct": float(np.abs(
            crudo["gap_pct"].to_numpy(float)).mean()),
        "costo_pb": c_pb,
        "mde_pp": mde, "mde_ic_pp": (lo, hi),
        "mde_ic_solo_e_gap_pp": (mde_simetrico(f, hi_g, c),
                                 mde_simetrico(f, lo_g, c)),
        "tasa_baseline": tasa_base, "tasa_baseline_wilson": (lo_b, hi_b),
        "bootstrap": {"metodo": "clusteres de dia", "n_boot": N_BOOT,
                      "semilla": SEMILLA_DIA,
                      "dias": int(df["fecha"].nunique())},
    }


def replicas(dedup: bool = True, c_pb: int = COSTO_BASE_PB) -> dict:
    """Las réplicas CRUDAS del bootstrap de clústeres de día: `f`, E|gap| y el
    MDE, replica por replica y alineadas entre sí.

    Existe porque `p_d` **ES** `f` (identidad estructural, §A2 y §D2 del
    quinto dictamen: bajo `excluir_cero` el conjunto discordante es el
    conjunto BAJA), así que cualquier cosa que combine el MDE con `N_max`
    tiene que usar **la misma réplica** de `f` en los dos lados. Tomar el
    borde del IC del MDE y meterlo en Connor con `p_d` en su punto mezcla
    réplicas distintas del mismo remuestreo, y los dos extremos que salen de
    ahí caen FUERA del intervalo honesto.

    `tabla_firma.py` las consume; acá se exponen y no se interpretan.
    """
    df = cargar_filas(dedup=dedup)
    c = c_pb / 1e4
    gap = df["gap_pct"].to_numpy(float) / 100.0
    baja = df["apertura_estimada_pct"].to_numpy(float) < 0

    def _par(idx):
        f = float(baja[idx].mean())
        e = float(np.abs(gap[idx]).mean())
        return f, e

    reps = [_par(i) for i in _indices_boot(df)]
    f_rep = np.array([r[0] for r in reps])
    e_rep = np.array([r[1] for r in reps])
    return {"f": f_rep, "e_gap": e_rep,
            "mde_pp": f_rep * 2 * c / e_rep * 100,
            "costo_pb": c_pb, "n_boot": N_BOOT, "semilla": SEMILLA_DIA,
            "clusteres": int(df["fecha"].nunique())}


def _indices_boot(df):
    """Los índices de cada réplica del bootstrap de clústeres de día, en el
    mismo orden y con la misma semilla que `va.boot_dias`."""
    import pandas as pd
    fecha = df["fecha"].to_numpy()
    dias = pd.unique(fecha)
    idx = {d: np.where(fecha == d)[0] for d in dias}
    rng = np.random.default_rng(SEMILLA_DIA)
    for _ in range(N_BOOT):
        sel = rng.choice(dias, size=len(dias), replace=True)
        yield np.concatenate([idx[d] for d in sel])


def razon_1(m: dict, bm: tuple[float, int] | None) -> dict | None:
    """Razón 1 de §A3.1.b, CON intervalo. Condición 2 del cuarto dictamen.

    El benchmark de V6 lo domina su propio camino realizado: con un
    benchmark negativo la tasa de acierto necesaria para superarlo cae por
    debajo de la que la baseline «siempre al alza» ya consigue, y entonces
    V6 no impone ninguna exigencia sobre la ventaja direccional del modelo.

    Lo que lleva intervalo y lo que no:
      * el retorno de SMH en la ventana: NO. Es un camino realizado.
      * la tasa necesaria: SÍ, propagada desde E|r| por los mismos
        clústeres de día.
      * la tasa de la baseline: SÍ, Wilson sobre las mismas filas.

    La razón se sostiene si el intervalo de la tasa necesaria queda ENTERO
    por debajo del intervalo de la tasa de la baseline. Si los dos se
    superponen, la razón vale como punto y no como afirmación, y eso se
    dice.
    """
    if bm is None:
        return None
    ret, dias = bm
    b_ses = ret / dias
    df = cargar_filas()
    r = np.abs(df["retorno_real_pct"].to_numpy(float) / 100.0)
    c = m["costo_pb"] / 1e4

    def _p_nec(idx):
        return (b_ses + 2 * c) / (2 * float(r[idx].mean())) + 0.5

    reps = va.boot_dias(df, _p_nec, n_boot=N_BOOT, semilla=SEMILLA_DIA)
    p_nec = (b_ses + 2 * c) / (2 * float(r.mean())) + 0.5
    lo, hi = _ic(reps)
    return {
        "benchmark": BENCHMARK, "retorno_ventana": ret, "sesiones": dias,
        "retorno_por_sesion": b_ses,
        "tasa_necesaria": p_nec, "tasa_necesaria_ic": (lo, hi),
        "tasa_baseline": m["tasa_baseline"],
        "tasa_baseline_wilson": m["tasa_baseline_wilson"],
        "se_sostiene": hi < m["tasa_baseline_wilson"][0],
        "intervalos_se_superponen": not (hi < m["tasa_baseline_wilson"][0]),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sin-red", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--costo-pb", type=int, default=COSTO_BASE_PB)
    args = ap.parse_args()

    m = medir(c_pb=args.costo_pb)
    bm = None if args.sin_red else retorno_benchmark()
    r1 = razon_1(m, bm)

    if args.json:
        print(json.dumps({"medicion": m, "razon_1": r1}, indent=2,
                         default=str, ensure_ascii=False))
        return

    print("=" * 70)
    print("EL MDE, DERIVADO DE V6")
    print("=" * 70)
    ct = m["cortes"]
    print(f"\nventana antecedente ANCLADA: emisión <= {ct['emision']}, "
          f"sello <= {ct['sello']},")
    print(f"convención {ct['convencion']}, regla de deduplicación firmada "
          f"aplicada: {ct['dedup_regla_firmada']}")

    print("\n1. EL INSUMO ESTABA CONTAMINADO\n")
    print(f"   filas ({ct['convencion']}, regla firmada) ... {m['n']}  "
          f"en {m['fechas']} fechas de emisión")
    print(f"   filas sin la regla de deduplicación ........ {m['n_sin_dedup']}")
    print(f"   la regla firmada retira .................... "
          f"{m['retiradas_por_la_regla']}")
    pa, pp = m["pares_antes"], m["pares_despues"]
    print(f"   filas que comparten sesión objetivo con otra:")
    print(f"     antes de la regla ... {pa['filas_en_pares']} en "
          f"{pa['grupos']} grupos, {len(pa['sesiones'])} sesiones")
    print(f"     después de la regla . {pp['filas_en_pares']} en "
          f"{pp['grupos']} grupos, {len(pp['sesiones'])} sesiones")
    print("     (las que quedan son los pares de feriado: las dos calzan con")
    print("      su `available_at`, así que la regla firmada conserva las dos)")
    print(f"\n   E|r|   sin la regla ... {m['e_r_sin_dedup_pct']:.4f} %      "
          f"con la regla ... {m['e_r_pct']:.4f} %")
    print(f"   E|gap| sin la regla ... {m['e_gap_sin_dedup_pct']:.4f} %      "
          f"con la regla ... {m['e_gap_pct']:.4f} %")
    print(f"   p_d (discordantes/n) .. {m['p_d']:.4f}   "
          f"({m['discordantes']}/{m['n']})")
    print("   OJO: se computa b+c y NUNCA b−c. b+c es el parámetro de "
          "estorbo que")
    print("   §A2 autoriza; b−c es la ventaja, y este módulo no la computa.")

    if not args.sin_red:
        ind = e_abs_reproduccion()
        if ind is None:
            print("\n   E|r| reproducción desde precio crudo ... sin red, no "
                  "corrió.")
        else:
            print(f"\n   E|r| REPRODUCCIÓN desde precio crudo ..... {ind:.4f} %")
            print("        OJO: esto NO valida nada. Es el mismo proveedor, el")
            print("        mismo campo y la misma fórmula. Una vara "
                  "independiente de")
            print("        verdad NO existe hoy acá, y se dice en vez de "
                  "fabricarla.")

    print("\n2. POR QUÉ V6 NO PUEDE FIJAR EL MDE\n")
    if r1 is None:
        print("   (benchmark no disponible sin red; la razón 1 no se imprime)")
    else:
        print(f"   Razón 1 — el benchmark lo domina su camino realizado.")
        print(f"   {r1['benchmark']} en la ventana: "
              f"{r1['retorno_ventana']*100:+.2f}% en {r1['sesiones']} sesiones "
              f"({r1['retorno_por_sesion']*100:+.4f}%/sesión)")
        print("   SIN intervalo, y por qué: es el camino REALIZADO, no una")
        print("   estimación de un retorno esperado. No hay parámetro del que "
              "sea muestra.")
        print(f"   tasa de acierto necesaria para superarlo a "
              f"{m['costo_pb']} pb: {r1['tasa_necesaria']*100:.1f}%"
              f"   IC95 [{r1['tasa_necesaria_ic'][0]*100:.1f}, "
              f"{r1['tasa_necesaria_ic'][1]*100:.1f}]")
        print(f"   la baseline 'siempre al alza' consigue ..... "
              f"{r1['tasa_baseline']*100:.1f}%"
              f"   Wilson [{r1['tasa_baseline_wilson'][0]*100:.1f}, "
              f"{r1['tasa_baseline_wilson'][1]*100:.1f}]")
        if r1["se_sostiene"]:
            print("   => los dos intervalos NO se superponen: la razón 1 se")
            print("      sostiene COMO AFIRMACIÓN, no sólo como punto.")
        else:
            print("   => los dos intervalos SE SUPERPONEN. La razón 1 se "
                  "sostiene")
            print("      como punto estimado y NO como afirmación con "
                  "intervalo.")
            print("      Lo que queda en pie se dice en §A3.1.b de DISEÑO.md, "
                  "y es")
            print("      más chico que lo que la v5 afirmaba.")

    print("\n   Razón 2 — RETRACTADA el 31-ago-2026, NO se sostiene.")
    print("   Decía que los datos refutaban la simetría de magnitudes. La "
          "cifra")
    print("   que lo cuantificaba está RETIRADA (acta §56): con intervalos la")
    print("   razón de magnitudes incluye 1.0 y el cociente que la resumía no")
    print("   tiene intervalo finito, porque su denominador (2q−1) no se")
    print("   distingue de cero. Era un punto indistinguible del nulo "
          "publicado")
    print("   como hallazgo, y por eso no vuelve a imprimirse acá.")

    print("\n3. LA DERIVACIÓN QUE SÍ FUNCIONA\n")
    print("   δ = (2q−1)·f   ·   condición: E[gap|baja] < −2c")
    print("   bajo magnitudes simétricas:  δ_min = f · 2c / E|gap|\n")
    print(f"   f = {m['f']:.4f}  IC95 [{m['f_ic'][0]:.4f}, "
          f"{m['f_ic'][1]:.4f}]")
    print(f"   E|gap| = {m['e_gap_pct']:.4f} %  IC95 "
          f"[{m['e_gap_ic_pct'][0]:.4f}, {m['e_gap_ic_pct'][1]:.4f}]\n")
    print(f"   {'costo':>8} {'MDE (escala del endpoint, acierto_gap)':>42}")
    for cpb in COSTOS_PB:
        mm = medir(c_pb=cpb) if cpb != m["costo_pb"] else m
        marca = "  <- caso base de V6" if cpb == COSTO_BASE_PB else ""
        print(f"   {cpb:>6}pb {mm['mde_pp']:>10.2f} pp   IC95 "
              f"[{mm['mde_ic_pp'][0]:.2f}, {mm['mde_ic_pp'][1]:.2f}]{marca}")

    print(f"\n4. EL MDE EN LA ESCALA DEL ENDPOINT, CON SU INTERVALO\n")
    print(f"   El endpoint congelado de §A2 es `acierto_gap`, así que el MDE")
    print(f"   va en la escala del gap y no del retorno de sesión.\n")
    print(f"   MDE a {m['costo_pb']} pb = **{m['mde_pp']:.2f} pp**   "
          f"IC95 [{m['mde_ic_pp'][0]:.2f}, {m['mde_ic_pp'][1]:.2f}]")
    print(f"        (clústeres de día, {m['bootstrap']['n_boot']} réplicas, "
          f"semilla {m['bootstrap']['semilla']}, "
          f"{m['bootstrap']['dias']} días)")
    sol = m["mde_ic_solo_e_gap_pp"]
    print(f"\n   Para comparar con lo que la v5 publicaba: propagando SÓLO")
    print(f"   E|gap| el intervalo sale [{sol[0]:.2f}, {sol[1]:.2f}] pp. Ése")
    print(f"   es el intervalo de UN insumo de tres, y es el que la v5 citaba")
    print(f"   como «el intervalo del MDE». El de arriba propaga DOS.")
    print("\n   EL TERCER EJE QUEDA DECLARADO FUERA DEL INTERVALO: la simetría")
    print("   de magnitudes entra como supuesto, no como estimación. §A3.1.c")
    print("   dice que es «el supuesto que manda», y su sensibilidad está")
    print("   medida en `GEMELO/resultados/mde_vs_observado.md` D1c, que es")
    print("   donde vive. No se recomputa acá: su estimación condiciona en el")
    print("   acierto del modelo, y esta corrida no recomputa ninguna cifra")
    print("   que dependa del acierto, tampoco en la ventana antecedente.")
    print("\n   Y el punto sigue siendo el de la v5: el MDE no es un número,")
    print("   es un rango. Lo que cambia es que ahora el rango es el correcto.")


if __name__ == "__main__":
    main()
