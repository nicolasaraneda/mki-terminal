# ============================================================
# EL GATE DE CAUSALIDAD DEL ARNÉS (B-2, corregido el 2026-09-01).
#
# Por qué existe
# --------------
# `validar_sin_futuro` se llamaba sobre frames que el propio llamador
# acababa de recortar con el MISMO predicado (`index.date <= fecha`): su
# condición de disparo era inalcanzable por construcción. Medido con
# instrumentación sobre un walk-forward completo: **401.184 invocaciones,
# cero capaces de disparar**. Y una fuga real desplaza VALORES sin tocar el
# índice (`shift(-1)`), así que no la habría visto ni aunque pudiera.
#
# Una verificación que usa el mismo mecanismo que produjo la cifra no es una
# verificación. La única guarda con dientes es la INVARIANCIA AL TRUNCADO:
# reconstruir el arnés entero con la fuente cortada en D y exigir que las
# predicciones de D salgan idénticas. Eso sí depende de los valores.
#
# Y una guarda sin contraprueba tampoco es una guarda: `tests/test_backtest.py`
# inyecta un `shift(-1)` en cada feature —incluidas las cinco exclusivas de
# B4/B5— y exige que este gate DISPARE. Es la misma disciplina que
# `GEMELO/features.py` ya aplicaba a su test de causalidad.
#
# Qué se trunca
# -------------
# Precios, OHLC **y la base de noticias**. Truncar sólo los precios dejaba
# sin probar exactamente la mitad del arnés donde vivía B-1.
# ============================================================

from datetime import date

import pandas as pd

from backtest import baselines as bl
from backtest.datos import ErrorLookAhead, FuenteCongelada, SentimientoPIT

# Las features exclusivas de B4/B5, que la suite anterior no tocaba: si la
# contraprueba no las cubre, una fuga ahí sigue siendo invisible.
FEATURES_EXCLUSIVAS_B4_B5 = ("roca_pct", "upstream", "sentimiento",
                             "sentimiento_sector", "buzz")

DECIMALES = 8   # las predicciones se comparan redondeadas a esto


def truncar_fuente(fuente: FuenteCongelada, fecha: date) -> FuenteCongelada:
    """Copia de la fuente sin una sola fila posterior a `fecha`."""
    series = fuente._series
    series = series[series.index.date <= fecha]
    ohlc = {t: d[d.index.date <= fecha] for t, d in (fuente._ohlc or {}).items()}
    return FuenteCongelada(series=series, ohlc=ohlc)


def _predicciones(fuente: FuenteCongelada, fecha: date, cuales: tuple,
                  embargo_dias: int, truncar_noticias: date | None,
                  fabrica_ctx=None) -> dict:
    """Predicciones de todas las baselines en `fecha` sobre esta fuente."""
    fabrica_ctx = fabrica_ctx or bl.ContextoRun
    with fuente:
        ctx = fabrica_ctx(fuente, embargo_dias=embargo_dias,
                          sentimiento=SentimientoPIT(truncar_en=truncar_noticias))
        salida = {}
        for nombre, modelo in bl.construir_baselines(ctx, cuales).items():
            pred = modelo.predecir(fecha)
            if pred is None or pred.empty:
                salida[nombre] = []
                continue
            filas = pred.round(DECIMALES).to_dict("records")
            salida[nombre] = sorted(
                ({k: (None if (isinstance(v, float) and pd.isna(v)) else v)
                  for k, v in f.items()} for f in filas),
                key=lambda f: str(f.get("Ticker")))
    return salida


def comparar_en_fecha(fuente: FuenteCongelada, fecha: date, cuales: tuple,
                      embargo_dias: int = bl.EMBARGO_DIAS,
                      fabrica_ctx=None) -> list:
    """Diferencias entre emitir con la fuente ENTERA y con la fuente
    truncada en `fecha`. Lista vacía = invariante."""
    completa = _predicciones(
        FuenteCongelada(series=fuente._series, ohlc=fuente._ohlc),
        fecha, cuales, embargo_dias, None, fabrica_ctx)
    recortada = _predicciones(
        truncar_fuente(fuente, fecha),
        fecha, cuales, embargo_dias, fecha, fabrica_ctx)
    diferencias = []
    for nombre in cuales:
        a, b = completa.get(nombre, []), recortada.get(nombre, [])
        if a != b:
            diferencias.append({"fecha": fecha.isoformat(), "baseline": nombre,
                                "con_futuro": a, "sin_futuro": b})
    return diferencias


def gate(fuente: FuenteCongelada, fechas, cuales: tuple,
         embargo_dias: int = bl.EMBARGO_DIAS, fabrica_ctx=None) -> dict:
    """Corre el gate sobre `fechas` × `cuales`. Si algo se mueve, REVIENTA
    con ErrorLookAhead — R3 no admite excepciones, y menos una que el propio
    arnés detectó."""
    fechas = tuple(fechas)
    for f in fechas:
        diferencias = comparar_en_fecha(fuente, f, cuales, embargo_dias,
                                        fabrica_ctx)
        if diferencias:
            d = diferencias[0]
            raise ErrorLookAhead(
                f"invariancia al truncado ROTA en {d['fecha']} · "
                f"{d['baseline']}: la predicción cambia según existan o no "
                f"los datos posteriores a la emisión. Con futuro: "
                f"{d['con_futuro']} · sin futuro: {d['sin_futuro']}")
    return {
        "ejecutado": True,
        "metodo": "invariancia al truncado: se reconstruye el arnés entero "
                  "(precios, OHLC y noticias) con la fuente cortada en D y "
                  "se exige predicción idéntica a la de la fuente completa",
        "fechas": [f.isoformat() for f in fechas],
        "n_fechas": len(fechas),
        "baselines": list(cuales),
        "n_comparaciones": len(fechas) * len(cuales),
        "resultado": "INVARIANTE",
        "contraprueba": "tests/test_backtest.py inyecta shift(-1) en cada "
                        "feature (incluidas roca_pct, upstream, sentimiento, "
                        "sentimiento_sector y buzz) y exige que este gate "
                        "dispare; sin esa contraprueba el gate no sería una "
                        "guarda.",
    }


# ------------------------------------------------------------
# La contraprueba, como código de producción y no sólo de test: quien
# quiera convencerse de que el gate puede fallar, lo corre.
# ------------------------------------------------------------
def fabrica_con_fuga(feature: str):
    """Devuelve una fábrica de ContextoRun que inyecta la fuga canónica
    (`shift(-1)`: el valor de mañana ocupa el lugar de hoy) en `feature`.

    No desplaza el índice — desplaza los VALORES —, que es exactamente la
    fuga que la guarda vieja no podía ver."""

    class ContextoConFuga(bl.ContextoRun):
        def __init__(self, fuente, embargo_dias=bl.EMBARGO_DIAS,
                     sentimiento=None):
            super().__init__(fuente, embargo_dias=embargo_dias,
                             sentimiento=sentimiento)
            if feature == "roca_pct":
                self.roca_pct = self.roca_pct.shift(-1)
            elif feature == "mom20":
                self.mom20 = self.mom20.shift(-1)
            elif feature == "beta_sox":
                self.sox_ultimo_real = self.sox_ultimo_real.shift(-1)
            elif feature == "mom20_idx":
                self.mom20_idx = {k: v.shift(-1)
                                  for k, v in self.mom20_idx.items()}
            elif feature == "regimen_alcista":
                self.regimen = self.regimen.shift(-1)
            elif feature == "z_divergencia":
                self.z_divergencia = {k: v.shift(-1)
                                      for k, v in self.z_divergencia.items()}
            elif feature == "upstream":
                self.mom_nivel = {k: v.shift(-1)
                                  for k, v in self.mom_nivel.items()}
            elif feature in ("sentimiento", "sentimiento_sector", "buzz"):
                self.sentimiento = _sentimiento_con_fuga(self.sentimiento,
                                                         feature)
            else:
                raise ValueError(f"feature desconocida: {feature}")

    return ContextoConFuga


def _sentimiento_con_fuga(base: SentimientoPIT, feature: str) -> SentimientoPIT:
    """El equivalente de shift(-1) en la capa de noticias: mirar un día MÁS
    allá de la emisión. Es la fuga que B-1 tenía de verdad, sólo que ésta
    dura un día en vez de 320."""
    original_valor, original_buzz = base.valor, base.buzz

    def valor(ticker, fecha):
        return original_valor(ticker, fecha + pd.Timedelta(days=1).to_pytimedelta())

    def buzz(ticker, fecha):
        return original_buzz(ticker, fecha + pd.Timedelta(days=1).to_pytimedelta())

    if feature == "buzz":
        base.buzz = buzz
    else:
        base.valor = valor
        base._memo_buzz = {}
    return base
