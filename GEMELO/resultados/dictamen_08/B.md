# Dictamen del `estadistico-adversario` · Frente B (decaimiento como teoría) · 2-sep-2026

> Texto del agente, condensado por el orquestador sin cambiar cifras. Sobre `decaimiento_teoria.md`, `decaimiento_feriados.{py,md,json}` y `decaimiento_prediccion.{py,json}` (prueba abierta 12:24). La Enmienda 3 de `preregistro/frente_B.md` y la corrida posterior aplican los bloqueantes.

## VEREDICTO

**El aritmético reproduce; la interpretación no.** Los 46 contrastes de B1 y los 12 de B2 reproducen dígito a dígito desde los testigos (semilla 20260902, `gaps_v2` sha `34fe61082ea58282`). Pero **C1 no mide lo que dice medir**: con 100,0 % contra 0,0 % de determinismo, `n_ny = 0` significa «la sesión local anterior ya abrió con este mismo insumo», no «pasó más tiempo». **El control de |SOX| está mal especificado** (trunca sólo el grupo normal al p75 de la condición: invierte y agranda el desbalance; media |SOX| condición 1,40 vs normal truncado 0,88). **El entregable declara «692 fechas, sin las 37 selladas, con embargo» y el código no aplica ni lo uno ni lo otro** (las 37 están adentro; no hay embargo; el «37» y el «embargo» son del Frente D). **§2 cita cuatro puntos ancla que no son los de la curva** (dice 22,2 / 16,3 / 17,5 / 3,9; la curva usó 21,55 / 16,25 / 16,76 / 3,70 — con esos números a = 28,12 y τ = 4,65 no se obtienen). **«17 intentos» es un subtotal del frente presentado como N del DSR.** Las conclusiones negativas (C2/C3 no decide; Δ(h) no es una ley del margen) sobreviven todo; la positiva de C1 y la lectura de §3 no.

## Intervalo

Con **bloques de 20 días** (regla de la casa) en vez de fechas iid: C1 XTKS ajuste [−39,7, −7,0] aguanta; **C1 XTKS prueba pasa de [−34,05, −0,13] a [−30,10, +1,59]: CONTIENE EL CERO.** «La dirección replica fuera de muestra» colgaba de siete centésimas. C2/C3 aguantan.

## Denominador

Correcto (Δ contra «siempre al alza» sobre las mismas filas, `excluir_cero`). Hallazgo del denominador: sobre siete exchanges, el mejor predictor de Δ es la **tasa base**, no h ni la exposición al SOX: Δ ~ base r = **−0,887**; Δ ~ corr(gap, SOX) r = +0,684; Δ ~ h r = −0,551. India: base 75,5 %, Hong Kong 62,1 % (los otros 52,9–55,8 %). **XNSE tiene UN ticker con historia en el ajuste**, no «las small caps indias».

## Intentos

Declarados 17; contados **25** en el frente (23 contrastes publicados por ventana en B1 —los controles cuyo número se publica como hallazgo cuentan— + 2 formas de B2). B no está en `REGISTRO_INTENTOS` (100). N honesto tras B ≥ 125.

## Por punto

1. **C1 — NO SOSTIENE.** (a) El control de |SOX| no empareja: con truncado **simétrico** −20,20 [−36,95, −3,47] ajuste / −0,34 [−18,57, +17,01] prueba; con **estandarización por 4 estratos** −20,77 [−37,15, −3,81] / −14,36 [−32,45, +2,62]. «Se reduce a la mitad» es falso: −28 % con el control malo, −11 % con el bueno. (b) Confusión estructural 100 %/0 %: C1 contrasta «insumo no incorporado vs insumo YA incorporado por el propio mercado». El bullet «Acotado: un cierre de NY viejo vale menos» no está licenciado; la lectura «no se disipa con el reloj sino cuando el propio mercado abre» es la ÚNICA que el diseño admite. (c) Los cuatro C1: ajuste unión 46 / intersección 29; **prueba unión 25 = el propio XTKS** (los otros tres son subconjuntos). (d) Partición: secuencia correcta y una sola apertura, pero la declaración es falsa y no hay candado.
2. **C2/C3 — VERIFICADO** (aguanta bloques de 20). La potencia «10 veces más fechas» está dicha, no calculada: ×10 → semiancho 3,84 pp, refuta H_dis pero no H_abs; **decidir entre las dos exige ≈×23 (~3.335 fechas de feriado asiático: más de un siglo)**.
3. **Feriado local — el rótulo post-hoc SOSTIENE; el reporte NO.** Selectivo: omite XTAI +33,99 [+2,51, +63,59] y XETR +42,17 [+12,17, +73,42] en la prueba (4 de 16 contrastes fuera del cero, sin coherencia: multiplicidad). Tokio +14,1 [−1,6, +29,9] citado sin decir que contiene el cero. **Faltaba el McNemar pareado** (último cierre vs cierre viejo, mismas filas): XTKS ajuste 76,9 % vs 63,1 %, b = 84, c = 48, **p = 0,0022**: el cierre viejo conserva señal sobre la base pero **pierde contra el fresco**.
4. **B2 — VERIFICADO en los veredictos, NO SOSTIENE en la lectura positiva.** Propagando las dos incertidumbres, XHKG y XNSE siguen INCOMPATIBLES (refutan cualquier curva monótona decreciente por las anclas, no sólo la exponencial) y XAMS compatible. Pero el intervalo predicho es de confianza, no de predicción (omite la dispersión entre conjuntos de tickers: Seúl 16,25 vs Tokio 21,55 al MISMO h; DE 3,7 pp entre tickers > semiancho publicado ±2,3). **Ámsterdam no es un acierto de la curva**: está al mismo h que el ancla Fráncfort (3,70 [0,15, 7,26] vs 4,41 [−0,15, 8,97]): dos estimaciones que rozan el cero coincidiendo. h y el conjunto de tickers están perfectamente confundidos en el ajuste; sin XETR, τ pasa de 4,65 a 8,31. «Curva de un universo atado al SOX» nunca se midió; al medirla, la tasa base domina.
5. **Intentos — NO SOSTIENE** (17 → 25; ausente del registro).
6. **Higiene — NO SOSTIENE**: anclas mal citadas y sin IC (XTKS 21,55 [18,81, 24,33] · XKRX 16,25 [13,12, 19,40] · XTAI 16,76 [12,94, 20,50] · XETR 3,70 [0,15, 7,26]); IC con el nulo sin declarar (Tokio +14,1; XAMS prueba 4,4 [−0,2, 9,0]; XHKG prueba 3,1 [−1,5, 7,9]); columna «lectura» que rotula «no distingue» a IC que excluyen el cero; «±13 a ±20» es ±12,0 a ±22,9; **B2 sin testigo de fuente** (re-descarga a las 14:36: XAMS 6,53 → 6,90, XHKG 4,13 → 4,05, XNSE −12,74 → −13,35: los veredictos no cambian, las cifras no son reproducibles). En el haber: la Enmienda 1 es correcta (v1 tenía 4/101, 1/78, 2/64, 2/31 sesiones post-feriado) y su tamaño, que el frente no da: v1 → v2 mueve −0,32 / +0,09 / +0,09 / +0,38 pp por bolsa (+670 filas): **la n de la portada se mueve; las ventajas casi no.**

## Criterios

V1–V6, R1 NO EVALUABLE (sin retador; la vara sigue en +6,5 pp, p 0,1849, n 248) · V7 no gastado, pero la partición interna no tiene candado · R2 no aplicable (ninguna fecha C1 cae en 15–23 jul) · R3 PASA (sin imports del motor, `merge_asof` backward exclusivo, condiciones de `exchange_calendars`, `insumo_rancio` reproducida): sin fuga de futuro; la confusión de C1 es estructural, no temporal.

## DICTAMEN: NO SOSTIENE

| afirmación | dictamen |
|---|---|
| C2/C3 no separan disipación de absorción | SOSTIENE |
| Δ(h) no es ley del margen; HK e India la refutan | SOSTIENE (más fuerte: refutan cualquier curva monótona) |
| Ámsterdam prueba que el margen explica el escalón | NO SOSTIENE |
| «curva de un universo atado al SOX» | NO CONCLUYENTE (no medido; la tasa base explica más) |
| C1: el cierre viejo vale menos por el tiempo | NO SOSTIENE (confusión 100 %/0 %; control mal especificado) |
| C1 replica fuera de muestra | NO SOSTIENE (bloques 20: [−30,1, +1,6]; control correcto: [−32,5, +2,6]) |
| feriado local post-hoc no replica | rótulo SOSTIENE, reporte NO (selectivo; el McNemar lo matiza en contra) |
| 17 intentos | NO SOSTIENE (≥ 25; N ≥ 125) |
| Enmienda 1 | SOSTIENE (falta el tamaño: ≈0,3 pp) |

**Bloqueantes:** B-1 higiene de partición (excluir las selladas y embargar de verdad, re-correr UNA vez declarándolo); B-2 anclas de §2 con sus IC; B-3 control de |SOX| por estandarización por estratos o truncado simétrico, y borrar «a la mitad»; B-4 declarar la confusión estructural de C1 en pre-registro y entregable, reescribir «Acotado»; B-5 intentos 25 y alta en el registro; B-6 testigo de fuente para B2; B-7 IC con el nulo declarados y columna «lectura» arreglada.
**Exigidos:** E-1 barrido de bloque (20 d) junto al iid; E-2 tabla de MDE en vez de «10 veces»; E-3 McNemar pareado del feriado local; E-4 reporte simétrico del fuera de muestra; E-5 tasa base y exposición por exchange, XNSE un solo ticker; E-6 intervalo de predicción; E-7 candado; E-8 sellar el pre-registro (commit); E-9 encolar el recompute de la ventana larga con el tamaño medido (~0,3 pp, +670 filas).

Fragmento que sesga (`decaimiento_feriados.py:191-192`): `tope` del grupo condición aplicado sólo al grupo normal.
