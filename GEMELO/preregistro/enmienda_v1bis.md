# Enmienda V1-bis al pre-registro de GEMELO — bajo la decisión D3 (3-sep-2026) — v2 tras el dictamen

**Estatus: PROPUESTA para firma, etiquetada como lo que el adversario dictaminó: un CAMBIO DE PREGUNTA (qué demuestra el proyecto), no un cambio de vara.** La v1 (01:20) decía «cambio de vara que sólo endurece»; el dictamen (§6, 01:05) la desmontó y las cinco correcciones exigidas están aplicadas abajo, marcadas «(v2)». Documento SEPARADO: `GEMELO/DISEÑO.md`
§6 no se edita (los criterios V1–V7 y R1–R3 están congelados desde el
25-ago-2026 y «no se editan para que calcen con los datos»). Esta enmienda
se firma o se rechaza; si se firma, se agrega DEBAJO del §6.1 como adición
fechada, y un test fija que el texto original de V1 no cambió. Sustituye a
la propuesta I de la octava corrida (`GEMELO/propuestas/I_enmienda_V1.md`),
que sólo cambiaba la unidad (fila → día) y no la métrica. Dictamen del
`estadistico-adversario` al pie: «¿cambio de vara o cambio de pregunta?».

## 1. Qué decide D3 y qué reemplaza a V1

**D3 (Nicolás, encargo 09):** la métrica primaria del veredicto pasa de
acierto direccional a **magnitud** —MAE contra predecir cero, y CRPS donde
haya densidad—. La dirección se sigue publicando como métrica secundaria,
con la misma firmeza.

**V1 vigente (congelado):** «Ventaja sobre "siempre al alza" evaluada en la
misma ventana, con McNemar p < 0,05».

**V1-bis (propuesta), que REEMPLAZA a V1 como barrera de entrada PRIMARIA y
lo conserva como secundaria:**

> **V1-bis (magnitud, primaria; v2).** Sobre las mismas filas selladas
> (convención `excluir_cero`, regla de deduplicación firmada), el retador
> reduce el error absoluto del gap frente a la **climatología causal**
> —la constante μ estimada sólo con el pasado de cada emisión; ganancia
> m = |g − μ| − |p − g| por fila— con media **positiva** cuyo **IC95 de
> clúster de día** (t de clúster, gl = k−1; **clave del día = fecha de
> EMISIÓN**, k = 34 en la ventana canónica) excluye el cero **y** p de
> permutación de signo por día < 0,05; **y** su densidad predictiva mejora el
> CRPS frente a la climatología causal N(μ, σ) con el mismo criterio. La
> ganancia contra **predecir cero** (lo que D3 nombra) se publica al lado,
> pero **no decide**: bajo ventaja verdadera cero el simulador calibrado da
> m > 0 el 54 % [51, 57] de las veces a 73 días — mide la deriva del gap,
> no la habilidad (§6, exigido 1; `corrida09/tipo1_conjuncion_v1bis.json`).
> **V1 (dirección) SIGUE SIENDO BLOQUEANTE:** la entrada es la CONJUNCIÓN
> V1-bis ∧ V1, con V1 juzgado en su unidad de día (permutación de signo por
> día e IC de día al lado del McNemar de filas, propuesta I). Así no hay
> caso «primaria pasa y secundaria falla» que decidir después: si discrepan,
> no entra (§6, observación a). Los dos números quedan, para siempre, uno
> junto al otro.

**Error tipo I de la conjunción, con verdad conocida (v2, exigido 4).**
Simulador calibrado del Frente A, generador con ventaja verdadera −0,01 pp,
1.000 réplicas, permutación de día, α = 0,05 por prueba
(`corrida09/tipo1_conjuncion_v1bis.json`):

| días | MAE contra cero | CRPS contra clim. en muestra | DIR | **MAE ∧ CRPS** | **MAE ∧ DIR** |
|---|---|---|---|---|---|
| 73 | 0,039 [0,029, 0,053] | 0,049 [0,037, 0,064] | 0,045 [0,034, 0,060] | **0,021 [0,014, 0,032]** | **0,009 [0,005, 0,017]** |
| 250 | 0,050 [0,038, 0,065] | **0,075 [0,060, 0,093]** | 0,043 [0,032, 0,057] | 0,022 [0,015, 0,033] | 0,007 [0,003, 0,014] |

Lectura: (i) la conjunción MAE ∧ CRPS NO es «casi un solo test» (0,021,
no 0,04): el dictamen E tenía razón en que comparten la media, pero no
son redundantes al nivel de decisión; (ii) el CRPS contra una climatología
estimada EN MUESTRA infla el tipo I a 250 días (0,075): por eso V1-bis
exige la climatología **causal**, y el juez lineal la usa; (iii) la
conjunción con V1 (0,009) es conservadora: la vara real de entrada es
~0,01, no 0,05, y eso se declara como precio de exigir las dos.

Nada más cambia: umbral 0,05, ventana, convención, gatillo del 25-oct,
comparador «siempre al alza» para la dirección.

## 2. Por qué es legítimo si se firma ANTES de ver resultados del retador

1. **La pregunta la fija el que aún no vio la respuesta.** No hay retador
   construido (encargo 09 §7: el retador jerárquico viene después, con
   V1-bis firmada). El juez lineal de esta misma corrida (`juez_lineal_d3.md`)
   se corre con V1-bis ya escrita, y su pre-registro declara antes de mirar
   qué se publica pase lo que pase.
2. **La magnitud estaba en el diseño congelado como V2 y V4.** D3 no
   inventa una métrica: reordena cuál es la barrera de ENTRADA. V4 (MAE del
   gap menor que el del campeón) y V2 (CRPS mejor que el campeón) ya
   existían; V1-bis añade la vara de D3 (contra predecir cero y contra la
   climatología causal), que es MÁS exigente para un retador que sólo
   iguale al campeón en dirección.
3. **La evidencia de que la dirección no tiene potencia es anterior y
   externa al retador:** `potencia_por_metrica.md` (octava corrida, dictamen
   E) midió con el simulador calibrado que a 73 días la potencia direccional
   es ~0,3 y la de magnitud ~0,9; 19 de 35 fechas contribuyen exactamente
   cero al estadístico direccional (dictamen F). Cambiar la métrica por esa
   evidencia, antes de que exista un retador, es diseñar; cambiarla después
   sería ajustar.
4. **(v2) La v1 decía «sólo endurece o mantiene». Era falso** (§6, exigido
   2): «magnitud contra cero» y «dirección contra siempre-al-alza» no son
   cantidades ordenables, y un retador que ganara en magnitud y perdiera en
   dirección habría PASADO bajo la v1 y no bajo V1. Por eso la v2 conserva
   V1 como bloqueante: sólo así la entrada endurece de verdad. No puede
   favorecer a ningún candidato concreto porque ninguno existe.
5. **(v2) El endpoint se eligió mirando la ventana del veredicto, y se
   declara** (exigido 3): los z (DIR 1,11 / MAE 1,69 / CRPS 1,76) se
   midieron sobre las mismas filas selladas que seguirán puntuando. Dos
   salidas, y la firma elige una: (α) el veredicto bajo V1-bis se evalúa
   **sólo sobre sellos posteriores al 3-sep-2026** (limpio; cuesta ~35
   días de ventana); (β) se evalúa sobre toda la ventana y la
   contaminación queda declarada en el veredicto. Recomendación: (α).
6. **(v2) Esta enmienda suma 1 al registro de intentos** (elección de
   familia de endpoint tras medir tres z sobre la ventana sellada).

## 3. Qué la haría ILEGÍTIMA

- Firmarla **después** de ver el resultado de un retador en magnitud (o de
  este mismo juez lineal, si el resultado se mirara antes de firmar): sería
  elegir la vara que el candidato ya pasa. Por eso la firma va antes del
  dictamen sobre `juez_lineal_d3.md`, o se declara que se firmó después y
  el juez no cuenta como evidencia de entrada.
- Elegir entre MAE-contra-cero, MAE-contra-campeón y CRPS **según cuál
  salga mejor**: V1-bis exige las dos (MAE contra cero Y CRPS contra
  climatología), declaradas ahora.
- Mover el umbral (0,05), la unidad (el día) o la ventana después de un
  resultado.
- Retirar la dirección de la publicación: D3 la conserva «con la misma
  firmeza»; una enmienda que la escondiera cambiaría la pregunta, no la
  vara.
- Aplicarla retroactivamente al WS2b para «rescatar» a C3: el WS2b ya fue
  negativo bajo V1 y R2; V1-bis no lo reabre.
- (v2) Firmarla **después** de la primera corrida del juez lineal de la
  corrida 09 sin etiquetar ese juez como exploratorio: la enmienda redefine
  sobre qué métrica se adjudica R1 y la evidencia de R1 sería ese mismo
  juez (circularidad, §6 observación c). Por eso `juez_lineal_d3.md` lleva
  la etiqueta **EXPLORATORIO: no computa como evidencia de entrada de R1**
  mientras esta enmienda no esté firmada, y su pre-registro exhibe el
  sha256 del documento y el `HEAD` anteriores a la primera corrida.
- (v2) Usar el plan secuencial v5 (Frente F) tal cual: sus fronteras se
  calibraron para el endpoint direccional y no valen para MAE; un plan
  secuencial bajo V1-bis es un diseño nuevo.

## 4. Criterios V2–V7 y R1–R3 afectados por el cambio de métrica

| criterio | texto congelado | efecto de V1-bis | qué se propone |
|---|---|---|---|
| **V2** CRPS mejor que el campeón, IC de bloques excluye cero | pasa de «adicional» a **co-primario** (CRPS es parte de V1-bis, pero V2 compara contra el CAMPEÓN y V1-bis contra la climatología: son dos varas) | conservar V2 tal cual; declarar que su IC pasa a **clúster de día por fecha de emisión** (el bootstrap de bloques de filas es el estimador que el Frente A midió mal calibrado: cobertura 0,69) |
| **V3** cobertura 80% en [76, 84] | sin cambio; el campeón está en 92,9% (2,19× [1,71, 2,78]) | sin cambio |
| **V4** MAE del gap < 3,064 pp del campeón (§2.5, n = 228), con igual o mayor cobertura de emisiones | la cifra congelada es de una ventana ya movida (hoy 2,52 pp sobre n = 238 con la regla firmada) | (v2) **no editar** el 3,064 ni reinterpretarlo caso por caso: firmar la regla **general y direccional** «todo nivel numérico del §6 es descriptivo; la comparación es siempre pareada sobre las mismas filas, con clúster de día», registrando que hoy **aprieta** (2,52 < 3,064). La segunda cláusula (cobertura de emisiones) sigue vigente |
| **V5** DSR ≥ 0,95 contando todos los intentos | sin cambio de texto; N = 286 hoy (322 si el juez lineal corre como está declarado) | sin cambio; anotar que con esta N ningún Sharpe positivo la pasa (cola §28) |
| **V6** SMH neto de 25 pb | (v2) **éste es el cambio de pregunta en una línea:** la métrica primaria pasa a una cantidad (la magnitud del gap) que el propio proyecto declaró NO capturable (9b del estado epistémico; acta §59). V6 no cambia de texto y seguirá sin pasar | sin cambio de texto; firmar sabiendo que un retador puede pasar V1-bis y no poder convertirlo en dinero, y que eso es lo que el proyecto pasa a demostrar |
| **V7** holdout una sola vez | sin cambio | sin cambio; el holdout se juzga con V1-bis y V1 secundario |
| **R1** el control lineal le gana | **cambia de métrica**: «gana» se decide por V1-bis (magnitud, clúster de día), no por McNemar | declarar: R1 se aplica sobre MAE y CRPS pareados con IC de día |
| **R2** sin 15–23 jul la ventaja desaparece | el dictamen E midió que R2 **también dispara sobre la magnitud** (MAE +0,44 → +0,34 pp; CRPS +0,29 → +0,21) | (v2) regla operativa para una métrica continua, congelada ahora: **«el IC95 de día del subconjunto sin 15–23 jul sigue excluyendo el cero»** (una atenuación no es «desaparece»). Con esa regla hoy no pasa nadie, ni en la ventana completa. Publicar siempre el par completo/R2 |
| **R3** fuga por el test de causalidad | sin cambio | sin cambio |
| **Plan secuencial v5** (Frente F, quinto rechazo) | (v2) sus fronteras se simularon sobre contribuciones DIRECCIONALES de día | no vale para V1-bis; un plan secuencial de magnitud es diseño nuevo y cuenta como tal |

## 5. Lo que espera firma

1. **Adoptar V1-bis** como adición fechada bajo `DISEÑO.md` §6.1 (con la
   skill `/acta-decision`; test que fija que el texto original de V1 no cambió).
2. Las tres declaraciones de la tabla: V2 e IC de día; V4 pareado sobre las
   mismas filas; R1 y R2 sobre la métrica primaria.
3. Si se rechaza: la alternativa honesta es la propuesta I (V1 con unidad de
   día), que no cambia la métrica y deja la potencia donde está (~0,3 el 25-oct).

## 6. Dictamen del `estadistico-adversario` sobre la v1 (3-sep-2026, 01:05 Chile), pegado sin editar

**VEREDICTO: es un cambio de PREGUNTA, no de vara** — porque cambia el *denominador* (de «siempre al alza», una baseline real, a «predecir cero», que en magnitud es el análogo del 50%), cambia la familia de endpoint, y saca a la dirección del *gating*; un cambio de vara sólo aprieta sobre el MISMO endpoint (eso era la propuesta I, y sí era vara). Es **firmable igual**, pero sólo si se firma como lo que es: una redefinición de qué demuestra el proyecto, con las cinco correcciones de abajo.

**CIFRA VERIFICADA** (ventana canónica D1, `cifras.CORTE_README`=2026-08-28, `excluir_cero`+dedup firmada, n=238): ganancia MAE del campeón contra predecir cero = **+0,4547 pp**; t de clúster de día gl=k−1: **[−0,082, +0,992]** (k=36, clave = sesión objetivo) y **[−0,087, +0,996]** (k=34, clave = fecha de emisión); bootstrap de día 4.000 réplicas [−0,037, +0,977]; permutación de signo por día **p = 0,099 / 0,101**. **DENOMINADOR**: la constante μ=0,841 in-sample recupera **7,2 %** de la ganancia (concuerda con `potencia_por_metrica.md` «7,3 %»; **el dictamen E dice 93 % y esa cifra no reproduce** — errata en `dictamen_08/E.md`). Aun así, contra la constante el modelo gana 0,42 pp con IC de día **[−0,98, +0,13]**: contiene el cero. **INTENTOS**: 286 verificado; +36 declarados por `juez_lineal_d3.md` → 322; la enmienda misma suma **1**.

**CRITERIOS:** V1 NO PASA hoy (McNemar filas p=0,0455 pero IC de día [−7,2, +26,6], permutación p=0,294) · V1-bis **tampoco la pasa el campeón**: IC de día del MAE contiene cero, p=0,10 · V2 NO EVALUABLE · V3 NO PASA (92,9 %, 2,19× [1,71, 2,78]) · V4 NO EVALUABLE · V5 NO PASA con N=286 · V6/V7 NO EVALUABLE · R1 NO EVALUABLE (el juez lineal no ha corrido) · R2 se activa también sobre magnitud · R3 sin fuga en este documento.

**CAMBIOS EXIGIDOS (bloqueantes):** (1) el denominador primario no puede ser «predecir cero»: pareá contra la climatología causal; (2) borrar «sólo endurece o mantiene»: es falso y la comparación es indecidible; si la intención es conjunción, escribirla («V1 sigue siendo bloqueante»), si no, decir que afloja; (3) declarar que el endpoint se eligió mirando la ventana del veredicto: o el veredicto se evalúa sólo sobre sellos posteriores al 3-sep, o se declara la contaminación; (4) verdad conocida antes que observada: correr la conjunción MAE∧CRPS contra el simulador con ventaja cero y medir su tipo I; (5) fijar la clave del día (emisión k=34 / sesión objetivo k=36).

**OBSERVACIONES:** (a) falta la regla si primaria y secundaria discrepan, y el plan secuencial v5 se diseñó sobre el endpoint direccional; sumar la enmienda al registro. (b) La tabla es correcta donde cita e incompleta: falta la segunda cláusula de V4, una definición operativa de R2 sobre una métrica continua, y el Frente F; V4 «3,064» debe firmarse como regla general y direccional, no caso por caso (hoy aprieta); en V6 la prosa pre-juzga y la tabla dice «sin cambio»: ése es el cambio de pregunta en una línea. (c) La frontera es la primera CORRIDA del juez, no su dictamen; circularidad real con R1: firmar antes de correr, o etiquetar el juez de la 09 como exploratorio; exhibir el hash anterior a la primera corrida. (d) Pasa MÁS, no menos, salvo que V1 se declare bloqueante.

**DICTAMEN: NO SOSTIENE** la redacción v1. Sostiene el mecanismo: la dirección no tiene potencia a este horizonte y la magnitud sí, y eso justifica **diseñar** hacia magnitud. Firmable tras 1–5, y etiquetada como cambio de pregunta.

*(Aplicado en la v2: 1 → climatología causal decide, cero se publica al lado; 2 → conjunción V1-bis ∧ V1; 3 → §2.5 con salidas α/β; 4 → tabla de tipo I medida; 5 → clave = emisión. Observaciones a–d aplicadas en §3, §4 y §5. La errata del dictamen E está anotada al pie de `dictamen_08/E.md`.)*
