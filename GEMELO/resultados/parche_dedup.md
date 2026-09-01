# El parche de la regla de deduplicación — ESCRITO, NO APLICADO

**Fecha:** 1-sep-2026 · Frente A de la segunda tanda de la quinta corrida.
**Estado:** la regla está **aplicada en el ejecutable** (regla 2 de la
casa: la corrección va al código antes que al texto). **Ninguna cifra
publicada se movió.** Mover una cifra publicada lleva la firma de Nicolás,
y él firmó la regla, no el parche.

---

## 0. Lo que hay que leer antes de mirar los números

**La regla firmada produjo un TERCER desenlace.** Nicolás firmó conociendo
dos: **p = 0,1847** sin deduplicar y **p = 0,0323** con `keep="last"`, la
rama que quedó prohibida. Su regla da **p = 0,0451**, que **cruza
α = 0,05** y no era ninguno de los dos. La firma sigue siendo el criterio
correcto —corrección de la sesión, nunca frescura— pero el desenlace no
estaba a la vista al firmar, y eso queda escrito.

**El mecanismo, con la misma claridad.** `b` queda en **72, sin cambio**;
`c` baja de **56 a 49**. Las 10 filas retiradas contenían **7 pares
discordantes, y los 7 favorecían a la baseline. Cero favorecían al
modelo.** Es la **misma asimetría** que motivó prohibir `keep="last"`.

**La diferencia sustantiva, que también hay que escribir.** Acá el retiro
**no** es por frescura sino por **no-correspondencia demostrable**: esas
10 filas tienen una `sesion_objetivo` que no corresponde a su
`available_at`, así que se puntúan contra una sesión que su insumo no
podía predecir — el cierre del SOX que las alimenta está una sesión
entera más atrás. Es una justificación real y distinta de "quedarse con
la más nueva". **Pero el lector tiene que poder ver las dos cosas juntas
y juzgar**, y por eso están las dos en este mismo párrafo.

**La opción que NO se puede tomar, y por qué.** Lo más completo sería
**re-verificar** esas 10 filas contra su sesión objetivo correcta en vez
de descartarlas. Eso exige recomputar valores sellados, y **las filas
selladas no se reescriben nunca** (Constitución 5.0, punto 3).
**Descartarlas es la única salida disponible: se eligió por restricción y
no por preferencia.**

**Un hueco de la firma que apareció después, y no se resuelve acá.**
Recomputando la sesión sobre TODAS las filas —no sólo las duplicadas— hay
**25 que no calzan**, y **15 no tienen pareja**. La regla firmada arbitra
entre filas que compiten; esas 15 están solas. Quedan **dentro** y la
pregunta está abierta en `cola_decisiones.md` §2a-ter. Su cifra está en la
§3 de este documento, para que se decida con los dos números a la vista.

---

## 1. Las cifras, recomputadas

Todas sobre el **mismo corte publicado** (`verificado_en <= 2026-08-28`),
misma fuente (`senales.db` en `mode=ro` vía `backtest.linea_base.cargar`),
mismo módulo. Lo único que cambia es la regla.

### 1.1 La tabla de las tres convenciones

| convención | n | modelo | base | ventaja | b/c | p (χ²cc) | p (exacta) |
|---|---|---|---|---|---|---|---|
| **PUBLICADO — sin deduplicar** | | | | | | | |
| `estricta` | 253 | 66,0% (167/253) | 58,5% | +7,5 pp | 75/56 | 0,1158 | 0,1155 |
| `verificador` | 253 | 66,0% (167/253) | 60,5% | +5,5 pp | 72/58 | 0,2542 | 0,2541 |
| **`excluir_cero`** | **248** | **66,1%** (164/248) | **59,7%** | **+6,5 pp** | **72/56** | **0,1849** | **0,1847** |
| **CON LA REGLA FIRMADA** | | | | | | | |
| `estricta` | 243 | 67,5% (164/243) | 56,8% | +10,7 pp | 75/49 | **0,0248** | **0,0244** |
| `verificador` | 243 | 67,5% (164/243) | 58,8% | +8,6 pp | 72/51 | 0,0713 | 0,0709 |
| **`excluir_cero`** | **238** | **67,6%** (161/238) | **58,0%** | **+9,7 pp** | **72/49** | **0,0455** | **0,0451** |

Wilson 95% bajo la regla, convención canónica: modelo **[61,5 – 73,3]**,
base **[51,6 – 64,1]**. Los dos intervalos siguen solapándose, que es
información que el p no da.

**Dos convenciones de tres cruzan α**, no sólo la canónica. La
`verificador` no lo hace: la elección de empate sigue valiendo un
veredicto, exactamente como el jardín de bifurcaciones venía diciendo.

### 1.2 Las otras métricas de la ventana

| métrica | publicado (n=248) | con la regla (n=238) |
|---|---|---|
| Acierto del retorno de sesión | 60,9% · [54,7 – 66,7] (n=253) | 62,1% · [55,9 – 68,0] (n=243) |
| MAE del gap | 2,98 pp contra 3,33 de predecir cero (**−10,5%**) | **2,52** pp contra **2,98** (**−15,3%**) |
| Cobertura del intervalo 80% | 90,3% | **92,9%** |
| Ratio ancho/error | 1,84× | **2,19×** |
| Régimen | 1 etiqueta en 39 snapshots | sin cambio |

El MAE baja **porque salen las filas de gaps enormes** (+28,4%, +24,2%,
+17,5%, +16,5%, +13,4% — las del 29-jul). Eso no es el modelo mejorando:
es el denominador perdiendo sus peores casos. **La mejora relativa sube de
−10,5% a −15,3% por la misma razón que sube la ventaja**, y hay que
decirlo con las mismas letras en los dos sitios.

La cobertura **empeora** (se aleja más de su nominal del 80%) y el ratio
de ancho sube a 2,19×. Es el único indicador que la regla mueve en
contra, y por eso va en la tabla.

---

## 2. El parche de los doce bloques — bajo la regla firmada

**Nada de esto está aplicado.** Cada fila da el archivo, la línea y el
texto que reemplazaría al actual.

| # | Bloque | Archivo:línea | Hoy | Bajo la regla firmada |
|---|---|---|---|---|
| 1 | TL;DR inglés | `README.md`:16-17 | «n=248 … +6.5 pp with p = 0.1849: still not distinguishable from zero» | «n=238 … **+9.7 pp with p = 0.0451**», y la frase final **ya no es cierta**: hay que reescribirla, no ajustarle el número. Propuesta: «the edge is +9.7 pp, p = 0.0451 — it crosses the 5% line for the first time, on 34 clustered days and with a day-cluster interval that still includes zero» |
| 2 | Badge de la ventana sellada | `README.md`:30 | `+6.5 pp · p=0.18 · n=248` | `+9.7 pp · p=0.045 · n=238` |
| 3 | Tabla de resultados sellados | `README.md`:123-126 | 66.1% (164/248) · 59.7% (148/248) · +6.5 pp · p = 0.1849 | **67.6% (161/238) · 58.0% (138/238) · +9.7 pp · p = 0.0455** (χ²cc) / **0.0451** (exacta), Wilson [61.5–73.3] y [51.6–64.1] |
| 4 | Párrafo de trayectoria | `README.md`:128-133 | «Todavía NO distinguible de cero» + la serie 25-ago → hoy | **Hay que reescribirlo entero.** El titular deja de ser «no distinguible» y pasa a ser «cruza por primera vez, y la razón por la que cruza es una regla de deduplicación firmada el 1-sep, no filas nuevas». La serie histórica se conserva y se le agrega el escalón, con su causa |
| 5 | Otras métricas | `README.md`:134-139 | n=248 · retorno 60.9% · MAE 2.98/3.33 · cobertura 90.3% · 1.84× | n=238 · retorno **62.1% [55.9–68.0]** · MAE **2.52/2.98 (−15.3%)** · cobertura **92.9%** · **2.19×** |
| 6 | Skill `cifras-canonicas` | `.claude/skills/cifras-canonicas/SKILL.md`:32-43 | la tabla de tres convenciones y el párrafo de abajo | la tabla **CON LA REGLA** de §1.1, y el párrafo «la ventaja sigue sin ser distinguible de cero» **retirado**: dejó de ser verdad bajo la convención canónica |
| 7 | Skill `estadistica-evaluacion` | `.claude/skills/estadistica-evaluacion/SKILL.md`:73-79 | n=248, 66.1% [60.0, 71.7], 59.7% [53.5, 65.6], +6.5 pp, p = 0.1849, MAE 2.98/3.33, cobertura 90.3%, 1.84× | n=238, **67.6% [61.5, 73.3]**, **58.0% [51.6, 64.1]**, **+9.7 pp**, **p = 0.0451**, MAE **2.52/2.98**, cobertura **92.9%**, **2.19×** |
| 8 | Arnés del módulo árbitro | `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py`:417-437 | `wilson_ci(164, 248)` / `wilson_ci(148, 248)`, `+6.5 pp`, `mcnemar_exact(72, 56)`, y **tres asserts** sobre [0.600, 0.717], [0.535, 0.656] y `abs(p2 - 0.1849) < 0.001` | `wilson_ci(161, 238)` → **[0.615, 0.733]**, `wilson_ci(138, 238)` → **[0.516, 0.641]**, **+9.7 pp**, `mcnemar_exact(72, 49)` → **0.0451**. **Ojo: son asserts.** Si el parche mueve el README sin mover esto, el módulo árbitro falla su propio autotest — y el ancla de aritmética `mcnemar_exact(67, 55) → 0.319` **no se toca**, es histórica y valida la aritmética, no una cifra vigente |
| 9 | Agente `estadistico-adversario` | `.claude/agents/estadistico-adversario.md`:47 | «V1 … n=248: +6.5 pp con p = 0.1849. Sigue sin ser distinguible de cero, y nadie la ha superado» | n=238: +9.7 pp con p = 0.0451. **La frase «sigue sin ser distinguible» se cae**, y con ella la vara que el agente le pone a los retadores: V1 pasa a exigir superar una ventaja que YA cruza α |
| 10 | `GEMELO/RELEVO.md` | `:114-115` y `:316-319` | n=248, 66.1%, 59.7%, +6.5 pp, p=0.1849; la plantilla de relevo | las cifras de §1.1 con la regla. **Este bloque no estaba en la lista original de doce** y se agrega acá: es el umbral con el que se juzgaría a un retador |
| 11 | Pre-registro §2.8 | `GEMELO/DISEÑO.md`:223, :232, :440 | n=223, +4.0 pp, p=0.4633 | **NO SE MUEVE.** Es un pre-registro congelado y su instante es el 26-ago, anterior a la firma. El harness ya lo contrasta contra `hasta_sello=CORTE_SECCION_2` **y `dedup=False`**, y sigue reproduciendo 7 de 7. Si alguien quisiera la línea base bajo la regla, sería una cifra NUEVA con su fecha, no una corrección de aquélla |
| 12 | `backtest/linea_base.py` línea base oficial | `:154` (`LINEA_BASE_OFICIAL`) | n=223 … p=0.4633 | **NO SE MUEVE**, por lo mismo que el 11. Ya está anclada a la rama histórica y el test lo verifica |
| 13 | `ESTADO.md` + acta en `DECISIONES.md` | — | — | acta de la regla (escrita) + el estado de la cola |

**Bloque 11-bis, informativo y no accionable:** la línea base congelada
**bajo** la regla sería n=213, +7,5 pp, 64/48, p = 0,1564 (χ²cc). Se
computa acá una sola vez para que nadie tenga que hacerlo mirando la
tabla, y **no se publica en ningún lado**: publicarla como "la §2.8
corregida" sería mover un pre-registro.

**Barrido obligatorio antes de dar por cerrado el parche:**

```
grep -rn "n=248\|n = 248\|+6.5 pp\|6,5 pp\|0\.1849\|0\.1847\|0\.1158\|0\.2542" \
  --include=*.md --include=*.py . | grep -v GEMELO/resultados/
```

y verificar que no sobreviva ninguna ocurrencia invalidada. **Media
portada movida es peor que ninguna** — y esta vez el riesgo es mayor que
en el parche de McNemar, porque acá la conclusión cambia de signo
cualitativo y no sólo el cuarto decimal.

---

## 3. La rama que NO se aplicó — para la §2a-ter de la cola

Retirando **además** las 15 filas sin pareja cuya `sesion_objetivo` no
calza (criterio de COHERENCIA, no de deduplicación), sobre el mismo corte:

| rama | n | ventaja | b/c | p (χ²cc) | p (exacta) |
|---|---|---|---|---|---|
| sin deduplicar (publicado) | 248 | +6,5 pp | 72/56 | 0,1849 | 0,1847 |
| **regla firmada** (aplicada) | **238** | **+9,7 pp** | **72/49** | **0,0455** | **0,0451** |
| regla + coherencia (**no aplicada**) | 223 | **+14,3 pp** | 69/37 | **0,0026** | **0,0024** |
| `keep="last"` (**prohibida**) | 233 | +10,3 pp | 70/46 | 0,0327 | 0,0323 |
| `keep="first"` | 233 | +6,9 pp | 72/56 | 0,1849 | 0,1847 |

**La rama de coherencia baja `c` de 49 a 37 y `b` de 72 a 69.** Otra vez
el retiro es asimétrico y otra vez a favor del modelo. Con eso a la
vista, y no sin eso, se decide.

Y el detalle que muestra el sistema funcionando: en las 8 filas del 5-jul
la sesión correcta (**07-03**) **ya había cerrado** cuando se selló, así
que con el ancla temporal buena esas filas caerían en
`no_verificable_timing`. **No las descartaría un criterio nuevo: las
descartaría la regla maestra que el proyecto ya tiene desde la Etapa 4.6.**

---

## 4. Qué se hizo y qué no

**Se hizo:**

- La regla vive en `backtest/linea_base.py`
  (`sesion_correcta`, `marcar_sesion`, `deduplicar_por_sesion`,
  `auditar_dedup`) y `cargar()` la aplica **por defecto** — un número
  retirado que sigue ofrecido en el código vuelve a circular.
- Se implementa **sola**, sin ninguna lista de fechas: el criterio es
  `sesion_objetivo == proxima_sesion_despues_de(exchange, available_at)`.
- `GEMELO/bifurcaciones.py`: `dedup` **dejó de ser un eje**. La matriz
  pasó de **768 a 192 celdas** y se recomputó.
- Diez tests nuevos entre `tests/test_linea_base.py` y
  `tests/test_bifurcaciones.py`, incluido uno que fija el hallazgo
  (`test_la_regla_firmada_cruza_alfa_y_eso_queda_fijado`) y otro que
  fija la asimetría de las 7 filas.

**No se hizo, a propósito:**

- **No se movió ninguna cifra publicada** — ni en el README, ni en las
  skills, ni en los agentes, ni en los pre-registros.
- No se decidió qué hacer con las 15 filas sin pareja.
- No se tocó `motor.py`, `senales.py`, `snapshot.py`, `universo.py`,
  `calendarios.py`, `.env`, los timers ni `CLAUDE.md`.
- No se commiteó ni se pusheó nada.
