---
name: estadistica-evaluacion
description: Herramientas de evaluación honesta para MKI Terminal. Úsala siempre que haya que calcular o juzgar un acierto, una ventaja sobre baseline, un intervalo de confianza, un Sharpe, un Deflated Sharpe, un CRPS, una cobertura o una partición walk-forward. Incluye un módulo Python probado con Wilson, McNemar exacto, bootstrap de bloques, PSR, DSR, CRPS, purge y embargo, y la prueba maestra de no fuga temporal.
---

# Estadística de evaluación

No calcules estas cosas a mano ni de memoria. Este proyecto ya publicó un
65.8% de acierto que resultó ser indistinguible de una constante. Usa el
módulo.

## El módulo

`${CLAUDE_SKILL_DIR}/scripts/evaluacion.py`. **Solo numpy y librería estándar.**
Sin scipy a propósito: este repo tiene `requirements.txt` fijado en dos máquinas
y el Mac está en producción, así que agregar una dependencia es una decisión con
acta, no un `pip install` de paso. La normal y el binomial exacto están
implementados en el módulo y validados contra scipy cifra por cifra.

Corre su self-test antes de confiar en él:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/evaluacion.py
```

El self-test reproduce las dos Wilson de la ventana sellada canónica: 164/248
da [60.0%, 71.7%] y 148/248 da [53.5%, 65.6%], ambas idénticas a las del acta
37.5. Si esas dos no salen, el módulo se rompió y no sigas.

Las anclas históricas (150/228 y b=67, c=55) siguen en el self-test como
validación de aritmética. **No son cifras vigentes del proyecto** y no se citan
como tales.

## Qué usar para cada pregunta

| Pregunta | Función | Regla |
|---|---|---|
| ¿Cuánto acierta? | `wilson_ci(k, n)` | Nunca reportes la proporción sin el IC |
| ¿Acierta más que la baseline? | `comparar_pareado(a, b)` | Sobre las mismas filas, siempre |
| ¿Cuál es la baseline honesta? | `baseline_siempre_alza(gap)` | El denominador es la constante, no el cero |
| ¿La diferencia es real? | `mcnemar_exact(b, c)` | Solo los desacuerdos aportan |
| ¿IC de una media o diferencia? | `block_bootstrap`, `diferencia_con_ic` | Bloque 20 días, nunca iid |
| ¿El Sharpe sobrevive al conteo de intentos? | `deflated_sharpe(...)` | Cuenta TODOS los intentos |
| ¿La densidad predictiva es mejor? | `crps_muestral`, `crps_normal` | Menor es mejor |
| ¿El intervalo está calibrado? | `cobertura`, `ancho_relativo` | 80% nominal debe dar [76%, 84%] |
| ¿La partición es limpia? | `walk_forward_purgado` | Purge y embargo, tamaño declarado |
| ¿Esta feature mira el futuro? | `prueba_causalidad` | Invariante a truncar en t |

## Ejemplo mínimo

```python
import sys; sys.path.insert(0, ".claude/skills/estadistica-evaluacion/scripts")
from evaluacion import comparar_pareado, baseline_siempre_alza

acierto_modelo = (np.sign(pred) == np.sign(gap_real))
acierto_base   = (baseline_siempre_alza(gap_real) == (gap_real > 0))
print(comparar_pareado(acierto_modelo, acierto_base))
```

## Las cinco reglas que el módulo hace cumplir

1. Ningún estimador puntual sin intervalo.
2. La comparación es contra la baseline, sobre las mismas filas, nunca contra
   50% ni contra cero.
3. Bootstrap de bloques, nunca iid: el clustering de volatilidad es real.
4. El DSR cuenta todos los intentos, incluidos los descartados por malos. Si
   no existe un registro de intentos, créalo antes de calcular.
5. Una feature es causal hasta que `prueba_causalidad` lo confirma, no porque
   se vea causal.

## Cifras de referencia

**No las cites de memoria.** Están en la skill `cifras-canonicas`, y la fuente
de verdad es el `README.md` del repo. Al 30-ago-2026 la ventana sellada
canónica (`excluir_cero`) va n=248, modelo 66.1% [60.0, 71.7], base 59.7%
[53.5, 65.6], ventaja +6.5 pp con McNemar p = 0.1849, MAE 2.98 contra 3.33,
cobertura 90.3% con ratio 1.84×.

Si lo que ves acá no coincide con el README, manda el README.
