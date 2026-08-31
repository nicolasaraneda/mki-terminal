---
paths:
  - "backtest/**"
  - "GEMELO/**"
  - "tests/test_*look*"
---

# Reglas al tocar backtest/ y GEMELO/

Estas reglas se cargan solo cuando trabajas en estos archivos. El resto de las
sesiones no pagan su costo.

- Toda feature es **causal y estacionaria por construcción**: retornos, razones,
  distancias. Nunca niveles crudos.
- La prueba maestra: el valor en `t` es invariante a truncar el dataset en `t`.
  Si no existe el test, escribirlo es el primer entregable, antes que la feature.
- El splitter lleva **purge y embargo**, con el tamaño del embargo declarado.
- El **holdout se evalúa una sola vez**. Si el walk-forward y el holdout
  discrepan, gana el holdout.
- **Cada configuración evaluada se registra como intento**, incluidas las
  descartadas por malas. El DSR miente si el conteo se hace a conveniencia.
- Ningún estimador puntual sin intervalo. Wilson para proporciones, McNemar
  para comparaciones pareadas, bootstrap de bloques de 20 días para diferencias.
- La comparación es contra "siempre al alza" **sobre las mismas filas**, jamás
  contra 50% ni contra cero.
- Usa `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py`. No
  reimplementes Wilson, McNemar, DSR ni CRPS a mano.
- Los criterios V1 a V7 y R1 a R3 están **congelados**. No se mueven después de
  ver resultados. Si alguien lo pide, eso se documenta como lo que es.
- Un resultado negativo se publica igual. Es la etapa funcionando.

Antes de dar por buena cualquier cifra: `estadistico-adversario`.
Antes de aceptar cualquier feature: `auditor-lookahead`.
