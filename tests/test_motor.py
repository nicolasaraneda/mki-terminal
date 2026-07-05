# ============================================================
# Test de no-contaminación del motor (Etapa 4.6)
#
# Verifica LA garantía central del motor: el resultado de cada función
# *_al(fecha) NO cambia si se recortan los datos posteriores a esa fecha.
# Si una función mirara datos del futuro (look-ahead bias), el resultado
# con datos completos diferiría del resultado con datos recortados, y este
# test fallaría.
#
# Técnica: se parchea motor._datos_crudos (el ÚNICO punto de acceso a
# datos del módulo) para que entregue los datos recortados a la fecha, y
# se comparan los resultados contra la ejecución con datos completos.
#
# Ejecutar:  python tests/test_motor.py
# ============================================================

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

import motor

FECHAS_PRUEBA = [
    date.today() - timedelta(days=30),
    date.today() - timedelta(days=90),
    date.today() - timedelta(days=180),
]


def _con_datos_recortados(fecha, funcion, *args, **kwargs):
    """Ejecuta `funcion` con _datos_crudos parcheado para no entregar NADA
    posterior a `fecha` — simula estar parado en ese día."""
    original = motor._datos_crudos

    def recortado(tickers):
        df = original(tickers)
        if df.empty:
            return df
        return df[df.index.date <= fecha].copy()

    motor._datos_crudos = recortado
    try:
        return funcion(*args, **kwargs)
    finally:
        motor._datos_crudos = original


def _comparar(nombre_fn, completo, recortado) -> bool:
    if isinstance(completo, pd.DataFrame):
        iguales = completo.equals(recortado)
    elif isinstance(completo, dict) and completo is not None and "serie" in (completo or {}):
        # dicts con Series adentro (roca_chip): comparar campo a campo
        iguales = (completo["valor"] == recortado["valor"]
                   and completo["crudo_pct"] == recortado["crudo_pct"]
                   and completo["serie"].equals(recortado["serie"]))
    else:
        iguales = completo == recortado
    return iguales


def main() -> int:
    fallas = 0
    for fecha in FECHAS_PRUEBA:
        print(f"\n=== Fecha de prueba: {fecha} ===")
        casos = [
            ("regimen_al", lambda f=fecha: motor.regimen_al(f)),
            ("puntaje_v0_al", lambda f=fecha: motor.puntaje_v0_al(f)),
            ("roca_chip_al", lambda f=fecha: motor.roca_chip_al(f)),
            ("betas_al", lambda f=fecha: motor.betas_al(f)),
            ("prediccion_apertura_al", lambda f=fecha: motor.prediccion_apertura_al(f)),
            ("divergencias_al", lambda f=fecha: motor.divergencias_al(f)),
        ]
        for nombre_fn, llamada in casos:
            completo = llamada()
            recortado = _con_datos_recortados(fecha, llamada)
            if _comparar(nombre_fn, completo, recortado):
                print(f"  OK  {nombre_fn}({fecha}): idéntico con y sin datos futuros")
            else:
                fallas += 1
                print(f"  FALLA  {nombre_fn}({fecha}): el resultado CAMBIA al "
                      f"recortar datos futuros — hay look-ahead bias")
    print()
    if fallas == 0:
        print("RESULTADO: todas las funciones del motor pasan el test de "
              "no-contaminación (sin look-ahead bias).")
    else:
        print(f"RESULTADO: {fallas} caso(s) con contaminación de datos futuros.")
    return 1 if fallas else 0


if __name__ == "__main__":
    raise SystemExit(main())
