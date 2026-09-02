# Dictamen del `estadistico-adversario` · Frente C (no capturabilidad) · 2-sep-2026

> Texto del agente, guardado por el orquestador. Sobre la primera apertura
> de la prueba (14:15). La Enmienda 2 de `preregistro/frente_C.md` y la
> corrida con `--enmienda` (14:35) aplican los diez bloqueantes y los
> exigidos 11–16; lo que no se resuelve queda declarado allí.

**VEREDICTO:** el núcleo de H1 **VERIFICADO y robusto**; H2 **REFUTADA en su sustancia** (el informe la rotula «no aplica», lo que la subdeclara); H3 **NO SOSTIENE tal como está escrita** (la afirmación de irrelevancia es frágil al bloque y falsa en el ajuste); la **afirmación de conjunto NO SOSTIENE tal como está redactada** — «estructural» no está medido, y el conteo de intentos está mal.

## Cifra reportada / verificada

H1 prueba: ventaja gap +15,6 [12,3, 18,9] pp · sesión −3,0 [−5,7, −0,3] · cartera −0,12 [−0,22, −0,04] pp/día · gap «operable» +1,02 [0,85, 1,21]. H2: razón 0,60 [0,04, 2,08]. H3: −0,036 [−0,096, +0,021]; sesión~gap −0,052 [−0,096, −0,007]. **Las 59 cifras reproducen bit a bit** (módulo importado en memoria, sin reabrir). Candado íntegro (sha256 = `_hash_apertura()`), 8/8 tests.

## Intervalo

Bootstrap circular de fechas, 4.000 réplicas, 0 no finitas, clúster = fecha: correcto. **Pero el bloque es 10 y la vara de la casa (`.claude/rules/backtest.md`) es 20.** Barrido:

| bloque | ventaja gap | ventaja sesión | E[q] | pendiente sesión~gap |
|---|---|---|---|---|
| 1 | [+12,12, +18,96] | [−5,61, −0,38] | [−0,219, −0,026] | [−0,108, **+0,004**] |
| 5 | [+12,22, +18,87] | [−5,51, −0,21] | [−0,210, −0,029] | [−0,105, **+0,003**] |
| 10 | [+12,30, +18,93] | [−5,67, −0,27] | [−0,216, −0,036] | [−0,096, −0,006] |
| 20 | [+12,25, +18,78] | [−5,72, −0,23] | [−0,204, −0,041] | [−0,090, −0,013] |
| 60 | [+12,19, +18,86] | [−6,08, **+0,10**] | [−0,197, −0,046] | [−0,088, −0,017] |

H1 aguanta a 20. La ventaja de sesión pierde el cero a bloque 60 y la pendiente sesión~gap contiene el cero a bloque 1 y 5: «la reversión que replica» depende de haber elegido 10.

## Denominador

Correcto («siempre al alza» sobre las mismas filas). **Falta el McNemar** (regla 3): PRUEBA gap 71,2 % vs 55,6 %, b = 1396, c = 648, p ≈ 0; sesión 47,0 % vs 50,0 %, b = 951, c = 1093, p = 0,002. Advertencia: p y Wilson de filas son optimistas por clustering — la Wilson de filas [69,87, 72,43] contra bootstrap de 20 fechas [68,93, 73,53]: **1,80× más ancho**.

## Intentos contados

**El 14 no se sostiene ni por su propio criterio:** el artefacto publica **59 intervalos** (ajuste 30, prueba 29); el 14 olvidó los 16 de la tabla por exchange. Y `REGISTRO_INTENTOS` (N = 100) no contiene a C. Nada de C se publica hasta que la tupla esté en la máquina: 29 (prueba) o 59 (ambas).

## Dictamen por punto

1. **H1 — VERIFICADO.** Aguanta dejar-un-año-fuera (E[q] −0,128/−0,149/−0,099, todos excluyen el cero), dejar-un-ticker-fuera (−0,105 a −0,140, los ocho), winsorizado 0,5 % (−0,120 [−0,200, −0,040]), vejez del SOX (0 filas > 4 días), cronología (margen mínimo 3 h). Reparos: `excluir_cero` se aplicó a un solo lado (95 filas con retorno total exactamente 0 aportan −0,011 de los −0,123: sin ellas E[q] = −0,114); E[q] heterogéneo (sólo 3 de 8 tickers excluyen el cero); el +1,02 «operable» es un contrafactual **no ejecutable** con DSR 1,0000 saturado: va con rótulo o no va.
2. **H2 — NO SOSTIENE la redacción.** El criterio literal `|E[q|error]| ≥ 1,5·E[q|acierto]` con E[q|acierto] = −0,139 habría dado un **falso positivo** (0,083 ≥ −0,208). «No aplica» lo impidió, bien. Pero el dato refuta la premisa: **los aciertos pierden más que los errores** (−0,139 [−0,231, −0,051] vs −0,083 [−0,225, +0,056]; aportan −0,099 de −0,123). La diferencia que H2 pregunta: **−0,056 [−0,178, +0,075]** a bloque 20 — contiene el cero. La razón 0,60 [0,037, 2,075] contiene 1 y 1,5 y el `.md` la anota «contiene el cero» (nulo equivocado). Y el §7 de la Enmienda 1 se escribió después de ver el ajuste: regla de lectura post-resultado, va escrita como tal.
3. **H3 — NO SOSTIENE «no hay sobrerreacción medible».** (a) En el AJUSTE el IC de sesión~gap contiene −0,10 a todo bloque ([−0,118, −0,048] a 10; [−0,113, −0,051] a 20): la irrelevancia no está probada; (b) la identidad (1+g)(1+r) es exacta a 2,2e−16: sesión ≡ total − gap, y con ruido ε en el gap (dos añadas de testigos) la pendiente es mecánicamente −Var(ε)/Var(g): **una reversión del 5 % y un ruido de medición del 5 % son el mismo número**; (c) tres terciles sin contrastar: alto − bajo = −0,028 [−0,181, +0,130] prueba, −0,072 [−0,174, +0,027] ajuste. Defendible: «no se detecta relación con la sorpresa respecto de β».
4. **Conjunto — NO SOSTIENE «estructural».** Es una afirmación de horarios no medida (consistente con, no es). **Costos: cero en todo el frente**, y H1 implica una CONTRARIA no evaluada: shortear el signo del SOX en la apertura rinde +0,123 pp/día bruto, SR/día 0,098 [0,022, 0,174]; punto muerto ≈ 6,1 pb por lado; a 25 pb −0,377 [−0,459, −0,296]; DSR 0,49 con N = 100. **Esa es la mitad que cierra el argumento.** Identidad tautológica declarada; testigos de dos añadas (gaps 2-sep, cierres 26-ago); IFX.DE ve 2 h de NY y la sesión asiática completa; **colisión de procedencia**: XETR +4,60 pp p = 0,0025 sobre la ventana completa contra el README +2,5 pp p = 0,111 (otro predictor, otra población — hay que escribirlo); multiplicidad de 16 IC por exchange (XETR gap sobrevive Bonferroni de 4 por poco); «Seúl −6,7 pp» es déficit de acierto, no pérdida (la pérdida es −0,204 pp/día).
5. **Intentos — NO SOSTIENE** (14 → 29/59; ausente de la máquina).
6. **Puntos sin intervalo:** fracción de aciertos ([68,93, 73,53] prueba), contribución de aciertos ([−0,158, −0,042]), contribución de errores (**[−0,063, +0,015], contiene el cero**); β sin error estándar. Nulos ocultos en la razón (1) y las pendientes (±0,1).

## Criterios

V1 NO EVALUABLE (predictor = signo crudo del SOX, otra población; la vara sigue en +6,5 pp, p = 0,1849, n = 248) · V2/V3/V4/R1 NO EVALUABLE · V5 NO PASA (contraria DSR 0,49 con N = 100; el operable saturado no es aprobado) · V6 NO PASA (sin costos ni SMH; a 25 pb la direccional −0,623 y la contraria −0,377) · V7 PASA en el mecanismo (apertura única, sellada excluida y embargada en los dos bordes: la prueba termina 2026-06-26) · R2 NO APLICA / PASA por análogo: **es el primer frente de esta corrida cuya ventaja no cabalga una ventana afortunada** · R3 PASA con reservas: sin fuga nueva; el candado no cubría los datos; dos añadas de testigos.

## Dictamen

**NO SOSTIENE** como afirmación de conjunto tal como está redactada. Lo que el dato SÍ sostiene: **el signo del SOX no compra nada en la sesión asiática, ni al derecho ni al revés, y eso replica fuera de muestra.**

**Bloqueantes:** (1) intentos en la máquina, 29 o 59, el 14 se retira; (2) McNemar b/c/p con la advertencia de clustering y el factor 1,80×; (3) IC para los tres puntos desnudos; (4) `_v()` con el nulo correcto (1 y 1,5 para la razón; ±0,1 para las pendientes); (5) H2 «REFUTADA en su premisa» con el IC de la diferencia y la declaración del falso positivo y del §7 post-resultado; (6) H3 reescrita (ajuste contiene −0,10; signo depende del bloque; atenuación por error de medición); (7) costear 0/5/10/25 pb la direccional y la contraria, punto muerto y DSR con N acumulado; (8) rotular el +1,02 NO EJECUTABLE; (9) declarar la colisión de procedencia con el README; (10) `excluir_cero` a los dos lados o justificar.
**Exigidos:** (11) resolver bloque 10 vs 20 y publicar el barrido; (12) candado con sha256 de los testigos; (13) multiplicidad de la tabla por exchange; (14) unidades de «Seúl −6,7 pp»; (15) heterogeneidad por ticker; (16) publicar las pruebas de robustez.
