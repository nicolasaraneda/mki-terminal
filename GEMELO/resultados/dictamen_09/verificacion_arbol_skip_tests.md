# Verificación del árbol sobre el que se saltaron los tests

**Fecha:** 6-Sep-2026 18:21 (hora de Chile, leída del reloj).
**Pregunta:** ¿el árbol de los tres commits que se hicieron con `SKIP_TESTS=1`
es idéntico al árbol que corrió los 649 verdes?
**Quién:** esta sesión. **No es un dictamen**: es la evidencia que los dos
dictámenes de esta carpeta pueden usar o refutar.

## Lo que pasó el 3-sep

Los cuatro commits de la corrida 09 se hicieron desde un solo árbol de trabajo,
en dos tandas:

| commit | hora (Chile) | tests |
|---|---|---|
| `e0179b7` | 18:03:05 | suite completa por el hook: **649 passed, 2 xfailed** |
| `7d13f5e` | 18:08:52 | `SKIP_TESTS=1` |
| `1b638cf` | 18:08:52 | `SKIP_TESTS=1` |
| `4feb32e` | 18:08:52 | `SKIP_TESTS=1` |

El hook `scripts/pre-commit` corre `python -m pytest tests/` sobre el **árbol de
trabajo**, no sobre el índice. Por eso la pregunta tiene respuesta: si los
archivos de los tres commits posteriores ya estaban en disco, en su contenido
final, cuando el hook corrió, entonces se probaron.

## Evidencia

```
git diff --name-only e0179b7 4feb32e        # 51 archivos de los tres commits
```

Ninguno tiene `mtime` posterior a las 18:03:05 del 3-sep. El más tardío es
`GEMELO/resultados/bitacora_09.md`, a las **18:02:46**, diecinueve segundos
antes. Ningún archivo figura como ausente, así que no hubo borrados.

Queda un hueco de diecinueve segundos: la suite tarda unos cinco minutos y medio,
de modo que la bitácora se escribió **mientras** corría. Está cerrado por
inspección: `grep -rn bitacora tests/` no devuelve nada. Ningún test la lee.
Los tres documentos que sí lee `test_epistemico.py` (`README.md`, `ESTADO.md`,
`estado_epistemico.md`) tienen `mtime` de las 00:33, 12:52 y 12:51.

Nada quedó fuera de los cuatro commits: `git status --porcelain -uall` está
vacío. La única deriva del árbol desde `4feb32e` es `data/backups/`, que el
propio hook exime por diseño para no bloquear el job de respaldo.

## Verificación empírica, hoy

La suite completa se volvió a correr sobre el árbol actual:

```
inicio 18:10:49 · fin 18:16:26 · 327,88 s
1 failed, 648 passed, 2 xfailed
tests/test_motor.py: 18/18 OK (no contaminación)
```

## El fallo, y por qué no es de la corrida 09

`tests/test_linea_base.py::test_senales_db_conserva_su_scoring_original`,
`assert 6 == 5`.

- El archivo **no está** en el diff de la corrida 09.
- La aserción entró el 25-ago-2026 (`78c83ea`).
- Contaba las filas de gap cero sobre la base **viva**, sin corte. Eran cinco.
  El sello del 2-sep-2026 verificó 2330.TW con gap 0,00 y son seis.
- Hasta cualquier ventana congelada —24-ago, 28-ago, 31-ago— siguen siendo cinco.
- El invariante que el test dice proteger **no se rompió**: las cinco filas
  originales conservan su `acierto_gap`, y la sexta también cumple la regla.

Era un censo clavado como constante. Corregido: el conteo se fija sobre la
ventana congelada y el invariante se afirma sobre todas las filas, incluidas las
que todavía no existen.

Dos tests verdes tenían el mismo defecto y habrían caído en el próximo par de
sesión duplicada: `test_la_regla_retira_exactamente_diez_filas_y_separa_los_dos_grupos`
y `test_las_diez_filas_retiradas_favorecian_todas_a_la_baseline`. Los nueve
valores de la auditoría son hoy idénticos en las cuatro ventanas —congelada y
viva—, así que fijarlos no cambia lo que los tests afirman. Se les agregó
además el invariante que sí vale sobre la base viva: un par nuevo sin criterio
es un hallazgo, y el censo del hueco sólo puede crecer.

## Verdicto

**El árbol sobre el que se saltaron los tests es el mismo que corrió los 649
verdes**, salvo `data/backups/`, que el hook exime. El único fallo de hoy lo
produjo el paso del tiempo sobre un test escrito el 25-ago, no el diff de la
corrida 09.

## Lo que esta verificación NO cubre

- No dictamina sobre el contenido del diff: eso es del `guardian-constitucion`.
- No juzga la prosa publicada: eso es del `curador-epistemico`.
- La igualdad se prueba por `mtime` y por el estado del repositorio, no por una
  copia byte a byte del árbol del 3-sep, que no se conservó.
