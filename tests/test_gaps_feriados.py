"""El gap de la sesión posterior a un feriado local existe (octava corrida,
Frente B1). Contraprueba de `GEMELO.datos.gaps_desde_ohlc`."""
import numpy as np
import pandas as pd

from GEMELO import datos as gd


def test_el_gap_post_feriado_se_calcula_contra_la_sesion_local_anterior():
    idx = pd.to_datetime(["2024-01-05", "2024-01-08", "2024-01-09", "2024-01-10"])
    # el ticker NO operó el 8 (feriado local): en el panel unión la fila existe con NaN
    ci = pd.Series([100.0, np.nan, 104.0, 106.0], index=idx)
    ap = pd.Series([99.0, np.nan, 102.0, 105.0], index=idx)
    g = gd.gaps_desde_ohlc(ap, ci)
    assert "2024-01-09" in g.index.strftime("%Y-%m-%d")
    assert g.loc["2024-01-09"] == (102.0 / 100.0 - 1) * 100      # contra el cierre del 5, no NaN
    assert g.loc["2024-01-10"] == (105.0 / 104.0 - 1) * 100
    assert len(g) == 2                                            # la primera sesión no tiene previa


def test_contraprueba_la_version_vieja_perdia_la_sesion_post_feriado():
    idx = pd.to_datetime(["2024-01-05", "2024-01-08", "2024-01-09", "2024-01-10"])
    ci = pd.Series([100.0, np.nan, 104.0, 106.0], index=idx)
    ap = pd.Series([99.0, np.nan, 102.0, 105.0], index=idx)
    vieja = ((ap / ci.shift(1) - 1.0) * 100.0).dropna()
    assert "2024-01-09" not in vieja.index.strftime("%Y-%m-%d")
