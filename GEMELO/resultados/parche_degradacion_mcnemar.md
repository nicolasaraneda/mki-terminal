# El parche de la degradación del McNemar — ESCRITO, NO APLICADO

**Fecha:** 1-sep-2026 · Frente E (escriba) de la sexta corrida.
**Estado:** acta escrita en `DECISIONES.md` §61. **Ninguna cifra publicada
se movió.** Mover una cifra publicada lleva la firma de Nicolás.

**Qué cambia respecto de `parche_dedup.md`.** Aquel documento (1-sep,
mañana) preparaba el movimiento de n=248→238 y p=0,1849→0,0451 **sin tocar
qué estadístico se lee como principal**. Esta acta va un paso más allá: el
**estadístico principal de la ventana sellada deja de ser McNemar y pasa a
ser el intervalo que respeta el clúster de día**. Por eso cada bloque de
abajo lleva **dos** columnas de "bajo la regla": la que sólo mueve el
número (idéntica a `parche_dedup.md`) y la que además degrada la lectura.
Sólo la segunda es la que esta acta recomienda si se aplica.

**Verificación contra el repo, no copia de la lista original.** La lista
base es la de `GEMELO/resultados/mcnemar_dos_rutas.md`:172-190 (12 bloques,
escrita el 31-ago para el problema de las dos rutas de McNemar exacto vs
χ², no para esto). El Frente A de la mañana del 1-sep agregó 2 bloques más
en `parche_dedup.md` (el arnés de asserts de `evaluacion.py` y
`GEMELO/RELEVO.md`), con nota explícita de que no estaban en la lista
original. **Cada una de las 14 ubicaciones se releyó hoy contra el archivo
real** (no se copió el texto de los documentos anteriores) — los números
"hoy" de la tabla son los que están efectivamente en el repo en este
momento.

---

## Los catorce bloques verificados

| # | Bloque | Archivo:línea (verificado hoy) | Hoy, en el repo | Bajo la regla, sin degradar (= `parche_dedup.md`) | Bajo la regla, DEGRADADO (recomendado) |
|---|---|---|---|---|---|
| 1 | TL;DR inglés | `README.md`:16-17 | «On the point-in-time sealed window (n=248) the edge is +6.5 pp with p = 0.1849: still not distinguishable from zero.» | «n=238 … +9.7 pp with p = 0.0451» | «n=238 … the edge is +9.7 pp; its day-cluster 95% CI is [-7.2, +26.5] pp (effective n=67, not 238) — crossing McNemar's p=0.0451 is not evidence once rows are treated as clustered by emission day. Still not distinguishable from zero.» |
| 2 | Badge de la ventana sellada | `README.md`:30 | `+6.5 pp · p=0.18 · n=248` | `+9.7 pp · p=0.045 · n=238` | `+9.7 pp · IC95 clúster [-7.2,+26.5] · n=238` (el badge deja de mostrar el McNemar solo) |
| 3 | Tabla de resultados sellados | `README.md`:123-126 | 66.1% (164/248) · 59.7% (148/248) · +6.5 pp · McNemar p = 0.1849 | 67.6% (161/238) · 58.0% (138/238) · +9.7 pp · p = 0.0455/0.0451 | Igual en las tasas y Wilson; la fila «Ventaja» pasa a **+9.7 pp — IC95 de clúster de día [-7.2, +26.5] pp (n efectivo 67)**, con McNemar (b=72, c=49, p=0.0451) como nota secundaria, no como cifra de la fila |
| 4 | Párrafo de trayectoria | `README.md`:128-133 | «Todavía NO distinguible de cero» + serie 25-ago→hoy | reescritura completa: «cruza por primera vez, y la razón es una regla de deduplicación firmada, no filas nuevas» | reescritura completa y distinta de la anterior: el titular no es «cruza McNemar», es «el intervalo de clúster de día sigue conteniendo cero ([-7.2, +26.5] pp) — la ventana sellada, con n efectivo 67, no alcanza para juzgar al campeón en ninguna dirección. Cruzar α por la ruta que supone filas independientes no es tener evidencia.» La serie histórica (25-ago → hoy) se conserva y se le agrega esta lectura, no solo el escalón numérico |
| 5 | Otras métricas | `README.md`:134-139 | n=248 · retorno 60.9% · MAE 2.98/3.33 · cobertura 90.3% · 1.84× | n=238 · retorno 62.1% [55.9-68.0] · MAE 2.52/2.98 (-15.3%) · cobertura 92.9% · 2.19× | igual que la columna anterior, y se agrega una fila: **«10-6 en 17 días de 34 — toda la información discriminante de la ventana»**, porque es la lectura en enteros que no depende de ningún supuesto |
| 6 | Skill `cifras-canonicas` | `.claude/skills/cifras-canonicas/SKILL.md`:32-47 (verificado: la tabla vive en estas líneas, no en 32-43 como decía la cita original) | tabla de tres convenciones + «La ventaja sigue sin ser distinguible de cero» | tabla con la regla, párrafo retirado | tabla con la regla, **y el párrafo se reemplaza, no se retira**: «La ventaja sigue sin ser distinguible de cero — no porque McNemar no cruce (cruza, p=0.0451), sino porque el intervalo que respeta el clúster de emisión ([-7.2, +26.5] pp) todavía contiene cero. McNemar se reporta como cifra secundaria; el intervalo de clúster es la cifra canónica de esta sección.» |
| 7 | Skill `estadistica-evaluacion` | `.claude/skills/estadistica-evaluacion/SKILL.md`:73-79 | n=248, wilson [60.0,71.7]/[53.5,65.6], +6.5pp, McNemar p=0.1849, MAE 2.98/3.33, cobertura 90.3%/1.84× | n=238, wilson [61.5,73.3]/[51.6,64.1], +9.7pp, p=0.0451, MAE 2.52/2.98, cobertura 92.9%/2.19× | igual, y se agrega una línea a la tabla «Qué usar para cada pregunta» (línea 41, «¿La diferencia es real? `mcnemar_exact(b,c)` · Solo los desacuerdos aportan»): **«si las filas se agrupan por fecha de emisión (día de sello), McNemar por sí solo sobrestima la significancia — este proyecto midió DEFF≈3.6 sobre su propia ventana sellada; usar el estimador de clúster de `GEMELO/bifurcaciones.py`.»** Esto es una ADVERTENCIA nueva, no un cambio de función: `evaluacion.py` no tiene hoy una función de clúster (ver más abajo) |
| 8 | Arnés del módulo árbitro (asserts) | `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py`:417-436 (verificado hoy línea a línea) | `wilson_ci(164,248)`/`wilson_ci(148,248)`; `mcnemar_exact(72,56)` con `assert abs(p2-0.1849)<0.001`; comentario "acta: +6.5 pp" | `wilson_ci(161,238)`→[0.615,0.733]; `wilson_ci(138,238)`→[0.516,0.641]; `mcnemar_exact(72,49)`→0.0451 | mismos números que la columna anterior (el self-test verifica aritmética, no prosa) — **más un comentario nuevo junto al assert de McNemar** aclarando que 0.0451 ya NO se cita como cifra principal en README/skills, para que quien lea el self-test dentro de un año no interprete el assert como aval del McNemar-solo. El ancla histórica `mcnemar_exact(67,55)→0.319` no se toca |
| 9 | Agente `estadístico-adversario` | `.claude/agents/estadistico-adversario.md`:46-48 | «V1 … n=248: +6.5 pp con p=0.1849. Sigue sin ser distinguible de cero, y nadie la ha superado.» | «n=238: +9.7 pp con p=0.0451. La frase "sigue sin ser distinguible" se cae» | **V1 en `GEMELO/DISEÑO.md` §6.1 NO SE TOCA** (frozen: "McNemar p<0.05", pre-registrado, no se mueve después de ver resultados). Lo que sí cambia es la nota descriptiva de este agente: «Vara actual: n=238, +9.7 pp, p=0.0451 — el campeón satisface la letra de V1 por primera vez bajo la regla de deduplicación confirmada. Satisfacerla no es evidencia por sí sola: IC95 de clúster de día [-7.2, +26.5] pp, n efectivo 67. Un retador que sólo iguale este p sin que su propio intervalo de clúster excluya cero no habrá mostrado nada que la estructura de los datos no explique ya.» |
| 10 | `GEMELO/RELEVO.md` | `:15, :66-67, :87, :114-115, :164, :179, :316-319` (verificado: son más apariciones que las 2 citadas originalmente — ver nota abajo) | n=248 en seis sitios distintos, incluida la plantilla de relevo (`:316-319`, con `McNemar p = 0.1849` como placeholder) | las cifras de la regla en los seis sitios | las cifras de la regla, **y la plantilla de relevo (`:316-319`) gana una fila nueva**: `IC95 clúster de día | | IC95 clúster de día = [<lo>, <hi>], n efectivo = <n>` — para que evaluar un futuro relevo bajo el mismo error (leer sólo McNemar) quede estructuralmente más difícil, no sólo advertido en prosa |
| 11 | Pre-registro §2.8 | `GEMELO/DISEÑO.md`:223, :232, :440 | n=223, +4.0 pp, p=0.4633 (línea 440 es la vara descriptiva de V1, no la tabla de la §2.8) | **NO SE MUEVE** | **NO SE MUEVE**, por la misma razón reforzada: es un pre-registro congelado, anterior a la firma, y el harness lo reproduce contra `dedup=False`. Tampoco se le agrega el intervalo de clúster retroactivamente — eso sería enriquecer una cifra congelada después de verla, que es la misma clase de error que mover el punto |
| 12 | `backtest/linea_base.py` línea base oficial | `:147-155` (`LINEA_BASE_OFICIAL`, la tupla "McNemar p" vive en la línea 154) | n=223 … p=0.4633 | **NO SE MUEVE** | **NO SE MUEVE**, mismo motivo que el 11 |
| 13 | `ESTADO.md` | — | **verificado hoy: no contiene ninguna de estas cifras** (`grep` sin resultados) | acta + estado de la cola | sin acción hoy — se regenera al cierre de la corrida, y en ese momento debe reflejar «regla confirmada, McNemar degradado» como estado, no como pendiente |
| 14 | `.claude/rules/backtest.md` | `:15-16` (regla de estilo, no cifra) | «Ningún estimador puntual sin intervalo. Wilson para proporciones, **McNemar para comparaciones pareadas**, bootstrap de bloques de 20 días para diferencias.» | sin cambio (no citaba ninguna cifra) | **candidato a nota, no a reescritura**: la frase recomienda McNemar sin mencionar que supone independencia entre filas. No se cambia acá — es una regla de estilo del proyecto y tocarla es una decisión aparte — pero se señala en el acta §61 como el tercer lugar (además de `linea_base.duelo()` y `evaluacion.comparar_pareado()`) donde McNemar sigue siendo la única guía ofrecida |

**Nota sobre el bloque 10:** `mcnemar_dos_rutas.md` y `parche_dedup.md`
sólo citaban `:114-115` y `:316-319` de `GEMELO/RELEVO.md`. Al releer el
archivo completo hoy aparecen n=248 (o cifras derivadas: 253, 25) en
**seis** líneas distintas (15, 66-67, 87, 114-115, 164, 179), no dos. Se
declara la discrepancia con la lista heredada en vez de copiarla: **verificar
contra el repo, no contra el documento que lista el repo, es precisamente lo
que esta tarea pedía.**

---

## Lo que NO se toca en ningún escenario

- **`motor.py`, `senales.py`, `snapshot.py`, `universo.py`, `.env`, timers,
  `CLAUDE.md`.**
- **`GEMELO/DISEÑO.md` §6 (criterios V1–V7, R1–R3, congelados).** La
  degradación cambia cómo se LEE la satisfacción de V1, no la letra de V1.
- **El pre-registro §2.8 y `LINEA_BASE_OFICIAL`** (bloques 11 y 12):
  anteriores a la firma, no se enriquecen ni se mueven.
- **Ningún ejecutable de medición** (`backtest/linea_base.py`,
  `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py`,
  `GEMELO/control_lineal.py`) — ver la sección de defaults más abajo.
- **Ninguna cifra publicada** — este documento se queda escrito y sin
  aplicar, igual que `parche_dedup.md` y `mcnemar_dos_rutas.md` antes de él.

## McNemar como default en código — señalado, no corregido

Búsqueda pedida en los tres lugares indicados:

- **`backtest/linea_base.py:394-413`, función `duelo()`.** Es la función
  que arma toda cifra de comparación pareada del proyecto (README, GEMELO,
  `bifurcaciones.py`). Devuelve `mcnemar_p` como el **único** campo de
  significancia; no existe un parámetro ni una rama que devuelva un
  intervalo de clúster. Quien llama a `duelo()` recibe McNemar sin poder
  no recibirlo, y sin ninguna alternativa en la misma firma.
- **`.claude/skills/estadistica-evaluacion/scripts/evaluacion.py:193-213`,
  función `comparar_pareado()` (clase `ComparacionPareada`).** Es la
  función de comparación pareada de la skill **compartida** del proyecto.
  Expone `p_mcnemar` como único campo inferencial. El módulo entero no
  tiene ninguna función de intervalo por clúster de día — la corrección
  que sostiene toda esta acta vive únicamente en `GEMELO/bifurcaciones.py`,
  fuera de la skill árbitro.
- **`GEMELO/control_lineal.py:287`, función `_mcnemar()`.** El comparador
  usado por el WS2b (C1/C2/C3) para juzgar retadores lineales tiene el
  mismo problema: sin corrección de clúster. Si se evalúa un retador con
  este módulo tal como está, va a heredar la misma sobreestimación de
  significancia que esta acta mide hoy en el campeón.

**Ninguna de las tres se corrige en este documento.** Tocar `evaluacion.py`
o `linea_base.py` es una decisión de código con su propio ciclo de revisión
adversaria (`estadistico-adversario`, `auditor-lookahead`), no un efecto
colateral de un acta de prosa. Quedan señaladas con archivo y línea para que
la cuarta regla de la casa ("un número retirado que sigue ofrecido en el
código vuelve a circular") tenga dónde aplicarse cuando alguien decida
tocarlas.

## Barrido obligatorio antes de dar por cerrado cualquier aplicación futura

```
grep -rn "n=248\|n = 248\|+6.5 pp\|6,5 pp\|0\.1849\|0\.1847" \
  --include=*.md --include=*.py . | grep -v GEMELO/resultados/
```

y verificar además que ningún bloque quede citando **solo** un p de
McNemar como si fuera autosuficiente sin el intervalo de clúster al lado —
ese chequeo no lo hace un `grep` de cifras, lo hace una lectura humana de
cada bloque tocado.
