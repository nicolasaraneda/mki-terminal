# El McNemar publicado: dos rutas, ninguna equivocada

**Fecha:** 31-ago-2026 · Frente D de la cuarta corrida.
**Estado:** hallazgo cerrado. **Ningún cambio aplicado.** El parche de los
doce bloques está escrito abajo y no ejecutado: mover una cifra publicada
lleva la firma de Nicolás.

> **Corrección de lo que dije en la corrida anterior.** En
> `DECISIONES.md` §47 escribí que el 0.1849 «se arrastró desde la medición
> de n=240». **Eso es falso, y la evidencia que parecía sostenerlo dice
> otra cosa.** La errata va fechada porque §47 ya está commiteada
> (`09054cb`).
>
> El indicio era `DECISIONES.md`:3493-3494: el track record pasa de
> «n=240 · +6.7 pp · p=0.1849» a «n=248 · +6.5 pp · p=0.1849» — mismo p
> con n y ventaja distintos, que parece la firma de un número copiado.
> **No lo es.** El p de McNemar depende **sólo del par de discordantes
> (b, c)**, no de n ni de la ventaja. Reconstruyendo (b−c) desde los
> porcentajes publicados de cada acta:
>
> | Acta | modelo | base | b−c |
> |---|---|---|---|
> | 30-ago `excluir_cero` n=240 | 163/240 | 147/240 | **16** |
> | 30-ago `excluir_cero` n=248 | 164/248 | 148/248 | **16** |
> | 30-ago `estricta` n=245 | 166/245 | 147/245 | **19** |
> | 30-ago `estricta` n=253 | 167/253 | 148/253 | **19** |
>
> Y medido hoy sobre la base viva: `excluir_cero` n=256 → b=72, c=56
> (b−c=16); `estricta` n=261 → b=75, c=56 (b−c=19). **Las filas que se
> fueron agregando fueron todas acuerdos**, así que el par de discordantes
> no se movió nunca. El p idéntico no es un número copiado: es el mismo
> par recomputado, tres veces, dando lo mismo porque tiene que dar lo
> mismo.
>
> Lo dejo escrito con este detalle porque el error que cometí es
> instructivo: **vi una coincidencia, la leí como evidencia de descuido, y
> no verifiqué la explicación aburrida antes de acusar.**

## 1. Qué pasa, en una línea

El README publica **p = 0.1849**; el módulo árbitro devuelve **0.1847**.
**Las dos cifras son aritméticamente correctas.** Son dos tests distintos
sobre el mismo par de discordantes:

| Ruta | Qué es | p sobre b=72, c=56 |
|---|---|---|
| `backtest/linea_base.py:126` `mcnemar()` | χ² de 1 gl **con corrección de continuidad** | **0.184898** → 0.1849 |
| `evaluacion.mcnemar_exact()` | **binomial exacta** bilateral, p=0.5 | **0.184683** → 0.1847 |

No difieren por redondeo, ni por un par (b, c) distinto, ni por un n
distinto. Difieren **por método**, y ambos métodos son legítimos.

## 2. Verificación contra varas independientes

Regla de la casa: una verificación que usa el mismo mecanismo que produjo
la cifra no es una verificación. Las dos rutas se validaron contra una
vara de **otra familia de método**, no contra sí mismas.

**La binomial exacta**, recomputada con **aritmética racional exacta**
(`fractions.Fraction`, sin un solo float) — familia distinta de la suma
en punto flotante que usa el módulo:

```
Σ C(128,i)/2^128 para i=0..56, por 2  =  0.1846826271
mcnemar_exact(72, 56)                 =  0.1846826271   idénticas
```

**El χ² con corrección de continuidad**, por dos caminos que no comparten
código: la función de supervivencia vía `erfc`, y la normal vía
`2·(1−Φ(√x))`:

```
estadístico = (|72−56| − 1)² / 128 = 225/128 = 1.7578125
vía erfc          : 0.1848975990
vía 2·(1−Φ(√x))   : 0.1848975990   idénticas
```

`scipy` no está instalado, y no se instaló para esto: agregar una
dependencia es una decisión con acta. Las dos varas de arriba son
suficientes y no requieren ninguna.

## 3. El hallazgo real: no es una cifra, son TRES, y es una regla rota

El 0.1849 no está solo. **Las tres cifras de McNemar de la ventana sellada
salen de la misma ruta no-árbitro**, computadas sobre la base viva:

| Convención | n | b | c | χ²+cc (publicado) | exacta | Δ |
|---|---|---|---|---|---|---|
| estricta | 261 | 75 | 56 | **0.1158** | 0.1155 | −0.0003 |
| verificador | 261 | 72 | 58 | **0.2542** | 0.2541 | −0.0001 |
| **excluir_cero** (canónica) | 256 | 72 | 56 | **0.1849** | 0.1847 | −0.0002 |

Y una cuarta, la de la línea base congelada del 26-ago (n=223, b=64,
c=55): publicada **0.4633**, exacta **0.4635**.

> **Nota sobre el n:** la tabla usa la base viva (261/256 filas tras el
> sello del 31-ago) y reproduce **exactamente** los p publicados, que se
> midieron sobre 253/248. Eso no es casualidad ni error: el p de McNemar
> depende sólo de (b, c), y las filas nuevas fueron todas acuerdos. Las
> cifras publicadas no se movieron.

**La regla que esto rompe está escrita, y es literal.**
`.claude/rules/backtest.md:26-27`:

> Usa `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py`. **No
> reimplementes Wilson, McNemar, DSR ni CRPS a mano.**

`backtest/linea_base.py:126` reimplementa McNemar a mano. **Ese es el
hallazgo**, y es de proceso, no de aritmética: el proyecto tiene **dos
árbitros** para la misma pregunta y publica por el que su propia regla
descarta.

**Atenuante que corresponde decir:** `linea_base.py` es del **25-ago**
(`78c83ea`) y la regla y el módulo son del **30-ago** (`55a99c4`). El
código no desobedeció una regla: **la regla llegó después y nadie volvió a
mirar el código que ya estaba**. Es deuda por orden de llegada, no
negligencia.

## 4. Por qué esto no se arregla solo, y por qué la decisión es de Nicolás

El arreglo obvio —que `linea_base.mcnemar()` llame a `mcnemar_exact`— tiene
una consecuencia que lo bloquea:

**`GEMELO/DISEÑO.md` §2.8 CONGELÓ `McNemar p = 0.4633` como parte de un
pre-registro** (`GEMELO/DISEÑO.md:223`, `:232`, `:440`). Cambiar el método
cambia esa cifra a 0.4635. Y la constitución del proyecto dice que los
criterios congelados **no se mueven después de ver resultados**.

O sea: hay un choque entre dos reglas del propio proyecto.

- Si manda "usá el módulo árbitro", se mueve una cifra de un
  pre-registro congelado.
- Si manda "un pre-registro no se toca", queda publicada una cifra
  computada por la ruta que la regla descarta.

**Ninguna de las dos salidas la toma un agente.** Las tres opciones, con
su consecuencia:

| Opción | Qué implica | Costo |
|---|---|---|
| **A. Declarar el método y no mover nada** | El README dice, al lado de cada p, «χ² de McNemar con corrección de continuidad». Las cifras quedan. `linea_base` queda como excepción documentada a la regla. | Cero cifras movidas. El pre-registro intacto. Queda una excepción viva a una regla escrita. |
| **B. Migrar al árbitro y mover las cuatro cifras** | 0.1158→0.1155, 0.2542→0.2541, 0.1849→0.1847, 0.4633→0.4635. Doce bloques. Errata en §2.8 documentando que una cifra congelada se corrigió por cambio de método. | Coherencia total con la regla. Precedente incómodo: un pre-registro que se mueve. |
| **C. Migrar hacia adelante, congelar hacia atrás** | `linea_base` pasa a usar el árbitro; las cifras ya publicadas se mantienen con su método declarado y fecha. | Sin errata sobre el pre-registro. Convive un corte de método con fecha, que hay que explicar cada vez. |

**Recomendación, marcada como tal: la A.** Tres razones:

1. **Ninguna conclusión cambia.** El mayor Δ es 0.0003, sobre p ≈ 0.12–0.46.
   Ningún veredicto, ningún criterio V o R, ninguna afirmación del README
   se mueve. Mover cuatro cifras publicadas para ganar el cuarto decimal
   es exactamente el tipo de churn que la regla de los doce bloques existe
   para desalentar.
2. **El χ² con corrección de continuidad no es el método malo.** Es un test
   estándar y, a n=128, coincide con el exacto en tres decimales. El
   problema no es que esté mal: es que no está **dicho**.
3. **Lo que falta es una palabra, no un número.** Publicar «p = 0.1849»
   sin decir qué test es, es lo que permitió que esto pasara inadvertido
   cinco días. Declarar el método cierra el agujero sin tocar el
   pre-registro.

**Lo que la opción A obliga igual:** escribir la excepción en
`.claude/rules/backtest.md` —«`backtest/linea_base.py` usa χ² con
corrección de continuidad por precedencia histórica; toda medición NUEVA
usa el módulo»— porque una regla con una excepción no escrita es una regla
que se va a volver a romper.

## 5. El parche de los doce bloques — ESCRITO, NO APLICADO

Sólo si Nicolás elige **B**. Bajo la opción A el parche es mucho más
chico: son las mismas ubicaciones pero agregando el nombre del test, sin
tocar ningún dígito.

| # | Bloque | Archivo:línea | Bajo A (declarar) | Bajo B (mover) |
|---|---|---|---|---|
| 1 | TL;DR inglés | `README.md`:16-17 | «p = 0.1849 (McNemar χ², continuity-corrected)» | 0.1849 → 0.1847 |
| 2 | Badge de la ventana sellada | `README.md`:30 | sin cambio (el badge dice p=0.18) | sin cambio |
| 3 | Tabla de resultados sellados | `README.md`:126 | nota de método bajo la tabla | 0.1849 → 0.1847 |
| 4 | Párrafo de trayectoria | `README.md`:129 | íd. | 0.4633 → 0.4635 |
| 5 | Tabla comparativa de convenciones | `README.md` (donde aparezcan 0.1158 / 0.2542) | íd. | → 0.1155 / 0.2541 |
| 6 | Skill `cifras-canonicas` | `.claude/skills/cifras-canonicas/SKILL.md`:36-43 | agregar el método a la tabla | tres p nuevas |
| 7 | Skill `estadistica-evaluacion` | `.claude/skills/estadistica-evaluacion/SKILL.md`:75-76 | íd. | íd. |
| 8 | Agente `estadistico-adversario` | `.claude/agents/estadistico-adversario.md`:47 | íd. | íd. |
| 9 | Pre-registro §2.8 | `GEMELO/DISEÑO.md`:223, :232, :440 | sin cambio | 0.4633 → 0.4635 **+ errata fechada** |
| 10 | Línea base oficial (test) | `backtest/linea_base.py`:108 | sin cambio | tupla y tolerancia |
| 11 | Regla de backtest | `.claude/rules/backtest.md`:26-27 | **agregar la excepción** | quitar la excepción, ya no aplica |
| 12 | `ESTADO.md` + acta en `DECISIONES.md` | — | acta de la decisión | acta + errata |

**Barrido obligatorio antes de dar por cerrado cualquiera de los dos:**
`grep -rn "0\.1849\|0\.1158\|0\.2542\|0\.4633" --include=*.md --include=*.py .`
y verificar que no sobreviva ninguna ocurrencia invalidada. Media portada
movida es peor que ninguna.

## 6. Qué NO se hizo acá

- **No se cambió ninguna cifra**, en ningún archivo.
- **No se tocó `backtest/linea_base.py`.** Su `mcnemar()` sigue como está,
  y sus tests siguen en verde.
- **No se decidió entre A, B y C.** Eso es de Nicolás.
- No se instaló `scipy` para «desempatar»: no hacía falta, y habría sido
  fabricar una tercera vara cuando las dos que hay ya coinciden consigo
  mismas por caminos independientes.
