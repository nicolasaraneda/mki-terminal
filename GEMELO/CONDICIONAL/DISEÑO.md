# GEMELO/CONDICIONAL — Diseño: ¿la ventaja de julio es una condición o es ruido?

**Estado:** PRE-REGISTRO. Congelado antes de correr una sola línea del
análisis de la §4/§5.
**Fecha:** 31-ago-2026 · **Campeón vigente:** modelo 4.6.0
**Insumos:** `GEMELO/resultados/dos_ventanas.md` §0 y §5 (clustering por
fecha, DEFF≈3.6, y el desglose que descubrió el bloque de julio) ·
`GEMELO/DISEÑO.md` §2.4 (zona muerta por quintil de magnitud), §2.8.2
(lección de bloques por rango de fecha, no por índice), §4.2 bis (protocolo
de conteo de intentos), §6.2 R2 (la regla del 15–23 jul aplicada al
campeón) · `GEMELO/relevo_asiatico.py` (`N_INTENTOS_WS5 = 25`, desglose
testeado) · `GEMELO/resultados/ventana_larga.md` (ventana larga: 2018-08-27
→ 2026-08-25, 2076 fechas de emisión, ~14.618–14.711 filas según
convención) · `backtest/baselines.py` (`EMBARGO_DIAS = 5`, `ContextoRun`) ·
`backtest/inferencia.py` (PSR, DSR, bootstrap circular, sin scipy) ·
`.claude/rules/backtest.md` · un scan statistic corrido esta noche sobre la
ventana sellada (evidencia adversa, ver §1) — no publicado aún en archivo
propio.

Este documento se escribe **antes** de construir nada, en la misma
tradición que `backtest/DISEÑO.md` en el GATE B, `GEMELO/DISEÑO.md` en la
etapa 6.0.0 y `GEMELO/MICRO/DISEÑO.md` en la pista de microtrading. Los
criterios de victoria y rechazo de las §4 y §5 se fijan aquí y no se tocan
después de ver resultados. Si esta hipótesis pierde bajo estos criterios,
pierde.

> **Regla cero:** `motor.py`, `senales.py`, `snapshot.py` y `universo.py` no
> se tocan por este análisis bajo ninguna circunstancia. El modelo 4.6.0
> sigue sellando en producción sin enterarse de que este documento existe.
> Esto es investigación, no un cambio de modelo: no releva nada, no decide
> nada sobre cómo se reporta el track record, y no autoriza ningún ajuste al
> verificador ni a la convención de empate ya congelada (`excluir_cero`,
> `GEMELO/DISEÑO.md` §2.8.1).

---

## 1. Por qué existe este documento, y por qué la hipótesis es POST-HOC

**Esta hipótesis nació DESPUÉS de ver el desglose de `dos_ventanas.md` §5.**
Nadie salió a buscar una condición de mercado que explicara la ventaja del
campeón: apareció mientras se auditaba el clustering por fecha del hallazgo
de las dos ventanas. Eso pone a este documento en la misma categoría que el
WS5 de `GEMELO/DISEÑO.md` §4.2 bis, que también formuló y probó una
hipótesis nacida de mirar datos, y con las mismas consecuencias que se
asumen ahí:

1. **Es exploratorio, no confirmatorio.** Ningún resultado de este análisis
   puede leerse como "confirmado". Como mucho, "no refutado".
2. **Cuenta como intentos nuevos para el DSR** — declarado en la §7, antes
   de correr nada.
3. Cualquier evidencia que confirme la hipótesis tiene que pesarse sabiendo
   que se buscó específicamente donde ya se había visto algo (la ventana
   larga se va a mirar sabiendo de antemano que julio 2026 fue el bloque
   alto). Un pre-registro honesto no esconde esto: lo declara antes de
   medir, no lo explica después si sale mal.

**La evidencia adversa ya existe, y se cita antes de empezar, no después.**
Sobre la ventana sellada (n=248, convención `excluir_cero`, 31-ago-2026), la
ventaja direccional del campeón sobre "siempre al alza" (+6.5 pp) se
concentra por completo en 6 fechas de emisión del 15 al 23 de julio de 2026
(n=44 filas, +40.9 pp, McNemar p=0.001); fuera de ese bloque (n=204, 28
fechas), la ventaja es −1.0 pp, p=0.92 — negativa, no positiva, y chica.

Un test formal corrido esta noche (**scan statistic**: máximo de la ventaja
sobre cualquier ventana contigua de fechas de emisión, anchos 3 a 10 fechas,
sobre las 34 fechas totales de la ventana sellada, contra una nula de
permutar el orden de esas 34 fechas, 5000 permutaciones) encontró que un
bloque tan extremo como el observado tiene **p≈0.55–0.65 bajo la nula de
"no hay clustering real, es la variación día a día normal"**. Es decir: la
concentración de julio, aislada, **no es distinguible** de lo que produciría
puro azar si uno tiene la libertad de elegir la mejor ventana entre 34
fechas.

Esto es evidencia **fuerte en contra** de que haya una condición real e
identificable detrás del bloque de julio, medida en la propia ventana
sellada. Pero la ventana sellada tiene muy poca potencia (34 fechas es poco
para detectar nada — el propio `dos_ventanas.md` §1 mide potencia de 44–59%
para un efecto bastante más grande que el que se busca acá), así que este
resultado **no cierra la pregunta, la vuelve más urgente de probar donde sí
hay potencia**: la ventana larga reconstruida de ocho años (2076 fechas de
emisión, n≈14.618 filas bajo `excluir_cero`).

---

## 2. La pregunta de investigación

**¿La ventaja direccional del modelo 4.6.0 es condicional a un conjunto
identificable de condiciones de mercado o del propio modelo — no
constante — tal que un candidato de condición, evaluado fuera de muestra
con purge y embargo sobre la ventana larga reconstruida, predice
significativamente en qué fechas la ventaja es alta vs. baja o negativa?**

Es la única pregunta que este documento intenta responder. No es "buscar
una condición hasta encontrar alguna que funcione": es esa frase, falsable,
con los umbrales de la §4 congelados antes de mirar el resultado.

---

## 3. Las condiciones candidatas

Cada una se mide **solo con información conocible al momento de emisión**
(`timestamp_utc` / `available_at`, en el sentido de la MASTER RULE de
`CLAUDE.md` y de la semántica de `available_at` de `GEMELO/datos.py`).
Ninguna candidata usa una sesión que todavía no cerró al momento de la
emisión que se está caracterizando — el auditor-lookahead revisa esto
después, así que cada definición es deliberadamente conservadora.

1. **Volatilidad realizada del SOX.** Desviación estándar (o rango) de los
   retornos diarios del SOX en una ventana rodante hacia atrás de 5 y de 10
   sesiones, terminando en la sesión de NY que generó la emisión (nunca
   incluye la sesión objetivo que se predice). Se prueban ambas ventanas
   como variantes de la misma condición.
2. **Magnitud del movimiento de la sesión de NY que generó la emisión.**
   |retorno del SOX de esa noche| — el mismo insumo que ya alimenta a
   `motor.py` (`sox_usado_pct`, ya sellado), usado aquí como condición, no
   como señal.
3. **Dispersión entre las bolsas asiáticas.** Spread o desviación estándar
   entre los retornos locales residualizados (vs. índice local + FX, mismo
   criterio de `motor.py`/`divergencias_al`) de Seúl (KS11), Taipéi (TWII) y
   Tokio (N225), medidos en la **sesión más reciente ya cerrada al momento
   de la emisión** — es decir, la sesión asiática del día anterior a la
   emisión, nunca la sesión objetivo que la emisión anticipa (esa sería el
   resultado que se quiere predecir, no un insumo).
4. **Densidad de noticias.** Conteo de titulares relevantes (`relevancia` de
   `noticias.db`, `tickers_estrictos`) en la ventana de decay vigente,
   filtrado a titulares cuyo timestamp de publicación sea **anterior o
   igual** al `timestamp_utc` de la emisión que se caracteriza — nunca
   noticias insertadas o publicadas después, aunque `noticias.db` las tenga
   ya cacheadas al momento de correr este análisis (la fecha de inserción en
   la base no es la fecha de conocibilidad).
5. **Distancia al cierre trimestral.** Días hábiles (calendario, sin
   ambigüedad de mercado) entre la fecha de emisión y el próximo cierre de
   trimestre calendario (31-mar, 30-jun, 30-sep, 31-dic). Es conocible con
   certeza total en cualquier fecha, por construcción.
6. **Magnitud predicha por el propio modelo.** `apertura_estimada_pct` /
   `intervalo80_pp` de la predicción sellada de esa fecha. Ya se sabe que
   discrimina por quintil de magnitud dentro de la ventana sellada: la
   "zona muerta" está documentada en `GEMELO/DISEÑO.md` §2.4 (el quintil más
   chico de |predicción| acierta 44.7%, por debajo de una moneda al aire;
   el más grande acierta razonable pero yerra la magnitud por 6.5 pp de
   MAE). **Esta cita no está en `DECISIONES.md`** — se dice así de explícito
   en vez de inventar una referencia que no existe ahí.

No se agregan candidatas adicionales a las seis obligatorias: cubren
mercado (1, 2, 3), información (4), calendario (5) y modelo (6), y agregar
una séptima sin una razón medida sería la misma tentación que el §1 ya
declaró como riesgo de sesgo de selección.

---

## 4. Criterios de victoria — CONGELADOS

Se fijan ahora, sin resultados a la vista.

**Definiciones previas, congeladas junto con los criterios:**

- **Unidad de análisis: la FECHA de emisión, nunca la fila/ticker** — la
  misma corrección que `dos_ventanas.md` §0 tuvo que introducir después de
  ser rechazado por `estadistico-adversario` (DEFF≈3.6). Cualquier prueba
  de esta sección que trate filas como independientes está mal construida
  por definición.
- **Variable objetivo (label) por fecha:** ventaja direccional de esa fecha
  = (aciertos del modelo − aciertos de "siempre al alza") / n de tickers de
  esa fecha, bajo la convención `excluir_cero` (`GEMELO/DISEÑO.md` §2.8.1),
  calculada sobre la ventana larga.
- **Corte "alto" vs. "bajo", congelado antes de correr:** la MEDIANA de esa
  variable a través de **todas** las 2076 fechas de la ventana larga,
  calculada una sola vez. Es un corte fijo, no un hiperparámetro que se
  ajuste por candidato — mover el corte para favorecer a una condición
  particular invalidaría el resultado.
- **Purge y embargo:** se usa la maquinaria ya existente
  (`backtest/baselines.py::ContextoRun`, `EMBARGO_DIAS = 5` por defecto,
  configurable) y el splitter walk-forward de `backtest/motorbt.py`. No se
  reimplementa purge ni embargo a mano, por regla de
  `.claude/rules/backtest.md`.
- **Intervalos y pruebas:** bootstrap de bloques circulares **por fecha**
  (nunca por fila), semilla declarada, usando `backtest/inferencia.py`
  (`_remuestrear_circular` / `bootstrap_media`) — el mismo mecanismo que
  corrigió el CI de `dos_ventanas.md` §3. Ningún estimador puntual sin
  intervalo (`.claude/rules/backtest.md`).
- **Fold que contiene julio 2026:** la estructura de folds del walk-forward
  tiene que dejar las fechas 15–23-jul-2026 en un fold de **prueba fuera de
  muestra**, nunca en entrenamiento. Si el diseño de folds las deja del
  lado de entrenamiento, el criterio (b) de abajo queda contaminado por
  construcción y el resultado no cuenta.

Con eso fijado, la hipótesis condicional gana **solo si se cumple todo**:

- **(a) Discriminación fuera de muestra significativa.** El candidato (o el
  modelo conjunto de la §7) predice, vía walk-forward con purge y embargo
  sobre la ventana larga, la pertenencia al bloque alto/bajo definido
  arriba, con **AUC cuyo intervalo de confianza al 95% (bootstrap circular
  por fecha) excluya 0.5**, o alternativamente una prueba de McNemar sobre
  la clasificación binaria alto/bajo con **p < 0.05**. Cualquiera de los
  dos umbrales alcanza; ninguno se relaja después de ver el número.
- **(b) El bloque de julio cae del lado correcto.** El bloque 15–23-jul-2026
  tiene que caer del lado "alto" que la condición (o el modelo conjunto)
  predijo para esas fechas — usando el valor de la condición en esas
  fechas específicas, evaluado en el fold de prueba fuera de muestra
  (nunca en entrenamiento, según la definición de arriba. Si la condición
  discrimina en general pero predice julio como bloque **bajo**, la
  hipótesis **falla igual**, aunque el modelo tenga poder predictivo
  abstracto: la pregunta no es "¿existe alguna condición con poder
  predictivo?", es "¿explica esta condición lo que ya se observó?".

---

## 5. Criterios de rechazo

La hipótesis condicional se descarta, o se declara en un estado más débil
que "refutada", si:

- **R1 — mata la hipótesis entera.** Si **ninguna** de las seis condiciones
  candidatas, ni el modelo conjunto, supera el umbral de discriminación de
  la §4(a) fuera de muestra, la hipótesis condicional se declara **"no
  identificable con lo que hay"** — explícitamente **NO** lo mismo que
  "refutada". Es un resultado más débil: significa que con las condiciones
  candidatas medidas y los datos disponibles no se encontró ninguna
  variable que explique el patrón, no que se demostró que ninguna
  condición real existe.
- **R2 — falla la §4(b) aunque alguna condición discrimine.** Si una o más
  condiciones superan el umbral de discriminación pero **ninguna** predice
  a julio 2026 como bloque alto (todas lo predicen bajo, o julio queda en
  el corte exacto de la mediana), la hipótesis se declara **refutada para
  explicar el hallazgo que la motivó**, aunque el modelo conjunto pudiera
  tener algún poder predictivo genérico sobre otras fechas. Esta distinción
  con R1 se mantiene por escrito en el reporte final: "discrimina en
  general pero no explica julio" es un resultado distinto de "no
  discrimina nada".
- **R3 — el desenlace más probable, declarado antes de medir.** Dado que el
  scan statistic de la ventana sellada ya dio p≈0.55–0.65 (evidencia de que
  el bloque de julio en sí es compatible con azar) **y** si además la
  ventana larga tampoco identifica ninguna condición (R1), eso apunta al
  desenlace más fuerte, y este documento lo declara **como el que
  reconoce más probable dado lo que ya se sabe**: la concentración
  observada en julio es simplemente ruido de muestra chica, y el track
  record sellado hoy no tiene potencia para decir nada sobre condicionalidad
  — ni a favor ni en contra. Declararlo así, en vez de forzar una lectura
  de "refutado" o "confirmado", es el resultado honesto si es lo que sale.
- **R4 — fuga detectada.** Cualquier fuga de información en el sentido del
  test de causalidad que ya rige `GEMELO/` y `backtest/` (una condición
  cuyo valor en `t` no es invariante a truncar el dataset en `t`) invalida
  el resultado de esa condición sin discusión y sin excepción. Se corrige
  la condición o se descarta, pero no se reporta un AUC sobre una condición
  con fuga.

---

## 6. Qué NO se hace en esta etapa

- **No se toca `motor.py` ni la lógica de señales**, bajo ninguna
  circunstancia. Esto es un análisis de investigación, no un cambio de
  modelo.
- **No se decide relevar nada.** Ningún resultado de este documento, gane o
  pierda la hipótesis, autoriza cambiar el campeón ni promover al retador
  de `GEMELO/DISEÑO.md`.
- **No se usa esto para justificar ningún cambio en cómo se reporta el
  track record** sin que Nicolás lo apruebe explícitamente — eso es el
  Frente C, un documento aparte, y este pre-registro no lo anticipa ni lo
  reemplaza.
- **No se ajusta la convención `excluir_cero`, el verificador, ni el corte
  "alto/bajo" de la §4** después de ver resultados parciales.
- **No se agrega ninguna condición candidata séptima** a mitad de análisis
  sin declararla aparte, con su propia fecha y su propio costo en el DSR.

---

## 7. El conteo de intentos para el DSR — declarado ANTES de correr

`N_INTENTOS_WS5 = 25` es el N acumulado vigente hoy
(`GEMELO/relevo_asiatico.py`, desglose ya testeado: 6 baselines B0–B5 + 3
configs WS2b + 3 WS3 + 1 campeón reconstruido + 12 del WS5).

Este documento agrega **7 intentos nuevos**, contados por la misma regla
congelada de `GEMELO/DISEÑO.md` §4.2 bis ("un intento = (configuración ×
ventana de evaluación) con resultado reportable"):

| Intento | Ventana de evaluación | Cuenta |
|---|---|---|
| Volatilidad SOX (5/10 sesiones) | ventana larga, walk-forward | 1 |
| Magnitud SOX de la sesión de emisión | ventana larga, walk-forward | 1 |
| Dispersión entre bolsas asiáticas | ventana larga, walk-forward | 1 |
| Densidad de noticias | ventana larga, walk-forward | 1 |
| Distancia al cierre trimestral | ventana larga, walk-forward | 1 |
| Magnitud predicha por el modelo | ventana larga, walk-forward | 1 |
| Modelo conjunto (las 6 combinadas) | ventana larga, walk-forward | 1 |
| **N nuevo** | | **7** |

**El N acumulado pasa de 25 a 32.** La variante de ventana rodante 5 vs. 10
sesiones de la condición 1 se cuenta como una sola configuración reportada
(la de mejor discriminación en validación interna, resuelta sin mirar el
fold de prueba, del mismo modo que `GEMELO/DISEÑO.md` §4.2 bis excluye la
búsqueda interna de `alpha` por CV temporal del conteo); si en la práctica
se reporta el resultado de ambas ventanas por separado, el N sube a 33 y se
declara en el reporte, no acá.

**Ningún intento adicional se agrega después sin declararlo aparte, con su
propia fecha.** Contarlos a conveniencia es exactamente el sesgo que el DSR
existe para corregir.

---

## 8. Riesgos declarados, antes de medir

**El más incómodo primero: el mismo problema de clustering intra-fecha que
ya invalidó la primera versión de `dos_ventanas.md`, aquí a mayor escala.**
Los ~7-8 tickers de una fecha comparten signo porque siguen al SOX de esa
noche — `dos_ventanas.md` §0 midió un DEFF (design effect) de 3.6 sobre la
ventana sellada. No hay razón para esperar que la ventana larga esté libre
de ese mismo efecto: aunque tenga n≈14.618 filas, el n **efectivo**
independiente es del orden de las **2076 fechas distintas**, no las filas,
y probablemente menos si el propio clustering por fecha tiene además
correlación serial entre fechas consecutivas (volatilidad que persiste
varios días). **Cualquier intervalo de confianza o prueba de significancia
de las §4/§5 tiene que usar bootstrap de bloques circulares por FECHA,
nunca por fila** — la misma corrección que se aplicó esta noche en
`dos_ventanas.md`. Un intervalo calculado fila por fila en este documento
sería el mismo error que ya se cometió y corrigió una vez.

Otros riesgos, declarados antes de que se materialicen:

1. **Ocho años de reconstrucción histórica pueden mezclar regímenes de
   mercado tan distintos que ninguna condición simple explique nada.**
   Sería indistinguible de "no identificable" (R1) — no hay forma de
   diferenciar, solo con este diseño, "no hay condición" de "hay condición
   pero cambia de forma entre 2018 y 2026 y una sola variable no la
   captura". Se declara así si ocurre, sin forzar una lectura más fuerte.
2. **Sesgo de selección por construcción, ya reconocido en la §1.** Se
   mira la ventana larga sabiendo que julio 2026 fue el bloque alto. El
   criterio (b) de la §4 existe específicamente para que esto no se
   convierta en "encontrar alguna condición que, mirada con suficiente
   libertad, dibuje a julio como alto" — pero ningún diseño elimina del
   todo el sesgo de haber visto el resultado antes de elegir las
   candidatas; por eso este documento las declaró en la §3 antes de correr,
   no después.
3. **Datos gratuitos y revisión silenciosa de la historia.** Igual que en
   `GEMELO/DISEÑO.md` §8: Yahoo revisa la historia sin avisar. Ocho años de
   reconstrucción dependen de que esa historia no haya cambiado desde que
   se sella cada tramo — riesgo compartido con toda la ventana larga, no
   nuevo de este documento, pero vigente igual.
4. **La densidad de noticias (condición 4) es la más frágil de definir sin
   fuga.** `noticias.db` no distingue de forma trivial "publicado antes de
   la emisión" de "insertado en la base antes de correr este análisis";
   construir mal el filtro temporal sería la fuga más fácil de cometer sin
   darse cuenta, y es la primera candidata que el auditor-lookahead debería
   revisar.

---

## 9. Lo primero que hay que hacer

Nada de esto lo corre este documento. El análisis de las §4/§5 lo corre
Nicolás (o quien él designe) aparte, en paralelo, sobre la maquinaria ya
existente de `backtest/` y `GEMELO/`. Lo primero, antes de tocar la ventana
larga, es construir el test de causalidad (invariancia a truncar en `t`)
para cada una de las seis condiciones candidatas de la §3 — la misma regla
que `.claude/rules/backtest.md` exige: "si no existe el test, escribirlo es
el primer entregable, antes que la feature". Ninguna condición entra al
walk-forward de la §4 sin haber pasado esa prueba primero.
