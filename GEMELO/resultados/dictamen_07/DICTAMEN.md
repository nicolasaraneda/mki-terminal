# DICTAMEN — séptima corrida, Frentes A–E

> Texto íntegro del `estadistico-adversario`, 2-sep-2026 (~02:45 Chile),
> transcrito por la corrida sin editar. Sus scripts están en esta carpeta.

He verificado la skill `cifras-canonicas` contra el `README.md` (líneas 16-17, 30, 120-138): coinciden — ventana sellada canónica `excluir_cero`, n=248, +6.5 pp, p=0.1849, MAE 2.98, cobertura 90.3%, ratio 1.84×. El self-test del módulo (`venv/bin/python .claude/skills/estadistica-evaluacion/scripts/evaluacion.py`) sale TODO EN VERDE y reproduce 164/248 → [60.0, 71.7] y 148/248 → [53.5, 65.6]. Trabajo con eso.

---

## FRENTE A — `fuente_canonica.md`

### (i) «0 retornos cambiados sobre 8 años × 27 tickers» — **VERIFICADO**

Por ruta distinta a la del script. El script compara sobre el índice **unión** del panel, donde `pct_change` deja NaN en toda celda que sigue a un hueco (feriado local). Yo comparé sobre el **índice propio de cada ticker**, que cierra ese hueco, y exigí además que el par (fecha, fecha previa) sea el mismo en las dos descargas antes de comparar el retorno:

```
52.452 pares de retorno comparados · 0 pares NO comparables · 0 cambiados
max |Δr| comparable = 1.092e-06   (tolerancia 5e-6)
0 barras retiradas · 1 aparecida (IFX.DE)
```

Comando: `venv/bin/python /tmp/verif_m1b.py` sobre `GEMELO/cache/cierres_853b6558513c5e9f.csv` vs descarga fresca con `usar_cache=False` (verifiqué en `GEMELO/datos.py:222` que ese flag no reescribe la caché). La afirmación central se sostiene y con **mejor cobertura** que la que su propio artefacto documenta.

### (ii) La clasificación proporcional/no proporcional — **OBSERVADO, la prosa no reproduce**

La conclusión sobrevive; los tres números que la sostienen, no.

**a) «Cambió niveles en 1.962 celdas, todas el reescalado proporcional de un dividendo».** El propio `fuente_canonica.json` dice `distinta: 1962`, `proporcional: 1862`, `no_proporcional: 0`, `ultima_fecha_parcial_o_nueva: 27`. Sobran 73 celdas sin clasificar. **«Todas» no está soportado por el artefacto que se cita.** Mi ruta las clasifica y sí son proporcionales — o sea la conclusión es correcta y el respaldo está mal, que es la peor combinación porque nadie lo va a revisar de nuevo.

**b) El conteo honesto de celdas históricas distintas es 1.953, no 1.962.** La máscara `ultima` (línea 124) se aplica a `no_prop` y a `aparecida` pero **no** a `distinta` ni a `prop`. Las 9 de diferencia son la barra parcial del 2026-08-26 de 8 tickers más la de 000660.KS. Y `tests/test_fuente_canonica.py::test_la_ultima_fecha_parcial_se_separa_de_la_historia` afirma `no_proporcional == 0` y `ultima == 1`, pero **no** afirma `distinta == 0` ni `factor_reescalado is None`: la contraprueba está muda exactamente donde el clasificador falla.

**c) Los factores citados en la prosa no son factores de reescalado.** «el factor es constante por ticker (005930.KS 0,986792; 6857.T 1,014781; 2330.TW 0,997934…)» — esos tres tickers tienen **`distinta = 1`, y esa única celda es la última fecha de la caché**. Es la barra viva moviéndose, no un dividendo. Prueba directa, con un testigo que el expediente tiene y no usó: las dos cachés se capturaron con **95 segundos de diferencia** (04:22:04Z y 04:23:39Z, Tokio abierto) y difieren en el 2026-08-26:

```
000660.KS  -1000.0    8035.T  -70.0    6857.T  -10.0    4063.T  +1.0
```

Por eso el mismo ticker 6857.T aparece con factor 1,014781 en un testigo y 1,014493 en el otro: la prosa mezcla los dos testigos. **El único ticker que sí reescaló historia es 000660.KS**, 1.953 celdas, factor real **0,999783** constante a ~4e-7 sobre los 8 años — y `factor_reescalado` le devuelve `None`, porque el test de constancia de la línea 142 mete la barra parcial (ratio 0,9789) en el rango. El clasificador está exactamente al revés: reporta factor donde no lo hay y calla donde sí.

**Condición para entrar a un documento de resultados:** corregir (b) y (c), separar un contador `distinta_historica`, calcular `factor_reescalado` excluyendo la última fecha, y citar 0,999783/000660.KS en vez de los tres que no lo son. Y agregar al test `assert r["AAA"]["distinta"] == 0` y `assert factor_reescalado is None`.

### (iii) M6 — **VERIFICADO como argmin; la unicidad es cierta y NO está en el artefacto; sigue siendo hipótesis, y ahora con la vara puesta**

Re-corrí la búsqueda completa guardando el **perfil de las 130 barras**, que es lo que el JSON tira (sólo guarda `mejor`). La afirmación «es la única barra de 130 que lo hace» **se sostiene**:

| fecha | maxdif hoy | 1ª (Δ) | 2ª | 3ª | barras con ≤0,05 | brecha 1ª–2ª |
|---|---|---|---|---|---|---|
| 12-ago | 0,254 | **31-jul (0,035)** | 31-mar (0,080) | 08-jun (0,084) | **1 de 130** | 0,0449 |
| 14-ago | 0,274 | **31-jul (0,036)** | 08-jun (0,081) | 31-mar (0,094) | **1 de 130** | 0,0454 |
| 19-ago | 0,269 | **31-jul (0,042)** | 08-jun (0,077) | 31-mar (0,099) | **1 de 130** | 0,0352 |
| 20-ago | 0,258 | **31-jul (0,026)** | 08-jun (0,084) | 31-mar (0,085) | **1 de 130** | 0,0572 |

Y el control que faltaba: las noches vecinas (13, 18, 21-ago) reproducen **con la serie entera** a 0,004–0,007, y ahí 97–99 de 130 retiros dejan ≤0,05 — o sea la prueba sólo discrimina donde hay anomalía, que es lo correcto. Mecanismo verificado contra los datos: `^SOX` 30-jul **+8,189%**, 31-jul +0,072%; 000660.KS 31-jul **+29,955%**, 3-ago **−8,789%**. Las dos barras son puntos de palanca enormes; el reapareo las intercambia. Comando: `venv/bin/python /tmp/verif_m6.py`.

**El residuo la deja como hipótesis, y ahora se puede decir cuánto.** El piso de reproducción en noches sanas es 0,004–0,007 y el redondeo a dos decimales acota en 0,005. El residuo de M6 es 0,026–0,042: **4 a 8 veces el piso**. «Compatible con un segundo estado menor» es más blando de lo que el dato permite: el retiro de una barra explica ~87% del desvío y deja un resto que no es redondeo. Hipótesis con residuo declarado, no hipótesis casi confirmada.

**Lo que no se probó (la pregunta explícita):**
1. **Un cierre del 31-jul revisado, no ausente.** Es el modo de falla más natural de un índice en vivo y el espacio de búsqueda no lo contiene: sólo se prueba borrar.
2. **Retirar dos o más barras.** El espacio es de cardinalidad 1.
3. **Perturbar cualquier serie que no sea `^SOX`.** El parche (línea 452) filtra sólo `if "^SOX" in tickers`: la barra propia del ticker objetivo, el índice local y el FX nunca se tocan, y las tres mueven la beta.
4. **Un desfase por barra sobrante al final** en vez de faltante al medio (`ret_sox.shift(1)`); parcialmente cubierto porque el índice de búsqueda llega hasta la fecha, pero no se separó del resto.
5. **La fuerza de la evidencia está sobreestimada por dependencia.** Las cuatro fechas comparten ventanas de 120 días solapadas: no son cuatro votos independientes, y cualquier cuenta tipo (1/130)³ es cota superior, no la fuerza.

### (iv) Las 15 filas del 28/31-ago — **VERIFICADO por otra ruta, salvo un decimal del MAE**

No usé la consulta ad hoc del expediente: recomputé `motor.prediccion_apertura_al(2026-08-28)` y `(2026-08-31)` contra la fuente de hoy y comparé signo contra `gap_pct` sellado (`venv/bin/python /tmp/verif_iv.py`). Coincide con `m4.apertura_hoy` fila por fila.

```
sellado 8/8 (28-ago) → 0/8 reconstruido      sellado 0/7 (31-ago) → 7/7 reconstruido
global sellado    179/276 = 64.86 %   Wilson [59.1, 70.2]
global Yahoo-hoy  178/276 = 64.49 %   Wilson [58.7, 69.9]
```

**Lo que el expediente no dice y es el hallazgo:** el par McNemar de esa sustitución es **b = 8, c = 7, p = 1.0000**. La pregunta constitucional del §6.1 —cuál es el campeón, el sello o su reconstrucción— **mueve la cifra viva en una cantidad indistinguible de cero**. Eso no la hace menos importante (importa por reproducibilidad, no por el número), pero hay que escribirlo así, porque «15 filas cambian de acierto» suena a que la cifra está en juego y no lo está.

**Cifra que no reproduce:** MAE «2,827 → 2,897». Mi ruta de 15 filas da **2,8274 → 2,8919**. El 2,897 sólo sale sustituyendo **las 87 filas verificadas con veredicto DIVERGENCIA**, no las 15. Es una frase con **dos denominadores**: el acierto es la sustitución de 15, el MAE es la de 87. Las dos son defendibles por separado; juntas sin declarar, no. Condición: declarar el denominador de cada una, o reportar 2,892.

**Frente A: VERIFICADO en (i), (iii) y (iv). OBSERVADO en (ii) y en el MAE de (iv).** El expediente entra a documento de resultados con las cinco correcciones de (ii) y (iv) hechas en su sitio (no como errata: todavía no está publicado — vale la nota de memoria «la frontera de la errata es el commit»).

---

## FRENTE B — `horizonte_veredicto.md`

### El ancla y la ruta analítica — **VERIFICADO exacto**

`venv/bin/python /tmp/verif_b1.py`: n=246, 35 días, 2026-07-05→08-27, ventaja **9,3496 pp**, IC95 de día **[−7,20, +26,32]**, SE 8,5502 pp, ICC 0,3925, DEFF 3,5595, n efectivo 69,11 → 1,97 obs/día; D = **248 / 475 / 803**; MDE 24,0 / 16,6 / 12,7 / 9,0 / 6,3. Todo reproduce.

### **RECHAZADO: «α empírico de la permutación de signo por día = 0,083 a 35 días»**

Es el número más citado de la noche —vive en `horizonte_veredicto.md:39`, `horizonte.md:33` y `propuestas_cde.md:62`— y **no sobrevive a la réplica**. Usando la función del proyecto sin tocar nada, sólo subiendo `n_sim`:

| n_sim | α empírico | Wilson 95% |
|---|---|---|
| 300 (el publicado) | 0,0833 | [0,057, 0,120] |
| 1.000 | 0,0590 | [0,046, 0,075] |
| **3.000** | **0,0557** | **[0,048, 0,065]** |

Comando: `venv/bin/python /tmp/verif_b3.py` (reproduce 0,0833 exacto a n_sim=300 antes de escalar). **El 0,083 es ruido de Monte Carlo.** La lectura honesta es α ≈ 0,056 [0,048, 0,065] a 35 días: a lo sumo medio punto sobre el nominal, con IC que contiene 0,05. La narrativa «con pocos días es levemente anticonservador» **no está establecida**, y la frase que la acompaña —«0,047–0,063 desde 73 días»— tampoco distingue nada: a n_sim=300 toda esa columna es ±0,03 y ninguna celda separa 0,05 de 0,08.

**Defecto secundario que lo produjo, y que hay que arreglar aunque el número se caiga:** `bifurcaciones._p_permutacion_dia` (línea 718) re-siembra con `SEMILLA = 0` en **cada** llamada, así que las 300 réplicas comparten **una sola matriz de signos**. El estimador de α no es consistente en `n_sim` con `n_perm` fijo. Medido: con semilla de permutación variable por réplica el α a 35 días baja a **0,0440 [0,037, 0,052]**; a 73 y 250 días las dos rutas coinciden (0,046/0,046 y 0,050/0,051). La semilla fija está bien justificada en su docstring para comparar celdas de una tabla; dentro de un estudio de α es un error. Condición: `_p_permutacion_dia` debe aceptar `semilla` como argumento.

### **OBSERVADO: estimadores puntuales sin intervalo (parcialmente corregido durante la auditoría)**

`horizonte.md` cambió en disco a las **06:44Z, con la auditoría en curso**, y agregó los IC que yo estaba calculando. Lo hago constar: el artefacto se movió bajo auditoría, y este dictamen juzga la versión de las 06:44Z. Mi bootstrap anidado (400×600 sobre días) da **SE de día ∈ [6,09, 10,06] pp**, y de ahí:

```
9,0 pp → 248 días  IC95 [126, 343]      (la re-corrida publica [109, 370])
6,5 pp → 475 días  IC95 [241, 657]      ( [209, 709] )
5,0 pp → 803 días  IC95 [407, 1111]     ( [354, 1199] )
```

Mismo orden de magnitud; acepto los de la re-corrida. **«jul-2027» era, y en la tabla vieja seguía siendo, un punto disfrazado de calendario.** Falta todavía la incertidumbre de la **cadencia**: 0,897 = 35/39 sellos por día hábil, Wilson [0,76, 0,96], y `fecha_a_dias` usa `pd.offsets.BDay`, que ignora feriados de mercado. Eso agrega ±2 meses sobre los rangos de arriba.

### «Potencia 0,36 frente a 9 pp el 25-oct» — **VERIFICADO en la derivación, OBSERVADO en el reporte**

Bien derivado: con SE(73) = 8,55·√(35/73) = 5,92 pp, la potencia analítica es 0,33; la simulación da 0,36. Las dos rutas coinciden. Pero es 108/300 → **Wilson [0,31, 0,42]**, y arrastrando el IC del SE, **[0,25, 0,57]**. La frase que el veredicto pide escribir antes del 25-oct («su potencia frente al efecto relevante es ~0,36») tiene que llevar ese intervalo o repite el pecado que denuncia.

### ¿Es admisible la extrapolación 1/√D? ¿Es honesto el DGP de la simulación?

**1/√D: sí, como proyección; no, como calendario.** Requiere (a) días intercambiables, (b) estructura de clúster estable, (c) normalidad asintótica del cociente de sumas. (c) está bien con clústeres de ~7. (a) es el Frente D. (b) nadie la verificó — la composición de bolsas puede cambiar. Con el IC del SE puesto, es admisible y el documento ya lo dice bien: «no es estructuralmente subpotente, pero el tiempo suficiente es de años».

**El DGP de la simulación: sí, con una salvedad.** Remuestrear días enteros de residuos centrados y sumar δ preserva tamaños de clúster reales, ICC real y no supone normalidad. Correcto. La salvedad: centra por la media **agrupada de filas** (`todo.mean()`), mientras el estimador principal (ICD) es cociente de sumas y AVS es media no ponderada de medias diarias. Con tamaños 7-8 la diferencia es de segundo orden y el control de α a 73+ días lo confirma. Lo declaro suficiente.

### ¿Falta el gasto de α del diseño secuencial? — **sí, y el documento lo dice mal a su favor**

`horizonte_veredicto.md` lo declara en «Lo que NO dice» y cita `SECUENCIAL/DISEÑO.md` §A3.3 como si dijera «~3–5% mayor». §A3.3 (líneas 774-775) dice **factor 1,0241 = 2,4%**, no 3-5%. Sobre 248 días son 254. Irrelevante al lado de [126, 343], pero la cita no reproduce su propia fuente.

### **HALLAZGO NO DECLARADO: R2 dispara sobre el ancla misma del Frente B**

El documento presenta «primera mitad +19,17 pp / segunda mitad 0,0 pp» como chequeo mínimo de estacionariedad y lo suaviza con «los intervalos se solapan — no es evidencia de cambio». **Los seis días del bloque 1 (15, 16, 17, 21, 22, 23-jul) están enteros en la primera mitad.** Es R2 con otro nombre. Medido sobre el mismo ancla (`/tmp/verif_b4.py`):

```
con todo:        n=246  +9,3 pp   McNemar filas p=0,0455  IC de día [−7,20, +26,32]  perm. de día p=0,2967
sin el bloque 1: n=202  +2,5 pp   McNemar filas p=0,675   IC de día [−13,64, +19,23] perm. de día p=0,8248
```

**R2 es una vara de rechazo pre-registrada, no un caveat de estacionariedad, y está cumplida.** Tiene que aparecer como «R2: la ventaja desaparece al excluir el bloque 1», con esos cuatro números, no como «las mitades se solapan».

**Frente B: VERIFICADO el ancla y la ruta analítica. RECHAZADO el α = 0,083. OBSERVADO el gasto de α mal citado, la cadencia sin intervalo y la potencia 0,36 sin intervalo. Y R2 disparando sin ser nombrada.** El veredicto entra a documento de resultados si (1) se retira el 0,083 de los tres archivos y se reemplaza por 0,056 [0,048, 0,065] a n_sim ≥ 3.000, (2) se nombra R2 como R2, (3) la potencia y la cadencia llevan intervalo.

---

## FRENTE C — `propuestas_cde.md` §C

### Reproducción — **VERIFICADO exacto, celda por celda**

`venv/bin/python /tmp/verif_c1.py`: 37 días, 261 filas, cruces 3/0/0/2/0/0/0, MCN decide en 21 de 28 prefijos, y hoy MCN p=0,0063 · ICD [−4,09, 28,28] · PSD 0,183 · TDM 0,0676 · BAY 0,828/0,124 · AVS K=3,031 · SGN 11-6. Todo.

### `proceso_apuestas` — **VERIFICADO como e-proceso válido, con dos declaraciones que faltan**

- **λ predecible: correcto.** En la iteración `t` usa `s2_prev` construido con las `t−1` primeras observaciones; arranca en σ̂²₀ = 1/4 como WSR. La forma `min(c, √(2 log(1/α)/(σ̂² t log(1+t))))` es la plug-in predecible del paper.
- **Cota c = 0,5: válida y conservadora.** La validez exige `1 + λ(x−μ₀) > 0` ∀x∈[0,1], o sea λ < 1/μ₀ = 2. Con c = 0,5 sobra margen; el costo es potencia, no validez.
- **Reescalado a [0,1]: correcto.** x = (media diaria + 1)/2 ∈ [0,1] porque d ∈ {−1,0,1} por fila; μ₀ = 0,5 ⟺ H0: E[media diaria] ≤ 0.
- **Desviación respecto de WSR, que hay que declarar:** el update usa `ΣX² − (t+1)m̂ₜ²`, desviaciones respecto de la media **terminal**, donde WSR usa `Σ(Xᵢ − μ̂ᵢ)²` con medias corrientes. Sobreestima σ̂², achica λ: **conservador, no invalida**. Pero el docstring dice «predictable plug-in» a secas y no es literalmente esa fórmula.
- **Estimando distinto del principal, no declarado:** AVS testea la media **no ponderada** de medias diarias; ICD es el **cociente de sumas** (ponderado por tamaño de día). Con días de 7-8 filas es poco, pero son dos estimandos.
- **Argumento a favor de C-2 que el documento no usa y debería:** el e-proceso sólo exige `E[Xₜ|F_{t−1}] ≤ μ₀`, que es una condición de martingala, **más débil que independencia entre días**. AVS es válido bajo exactamente la autocorrelación que el Frente D no logra acotar. Ése es el mejor argumento de C-2, mejor que «absorbe el pasivo de miradas».

### La cuenta de cruces — **OBSERVADO: confundida con potencia**

Seis candidatos cruzaron cero veces porque **nunca se acercaron al umbral**. Un estadístico que jamás decide no puede cruzar; el propio docstring lo admite y la prosa del §C.0 lo olvida al escribir «el hallazgo: la fragilidad vive en la fila como unidad». Le construí una métrica libre de potencia: |Δz| de un día al siguiente sobre los 27 saltos de la trayectoria.

| | mediana | p90 | máx | z hoy |
|---|---|---|---|---|
| MCN | 0,000 | 0,840 | **1,061** | 2,732 |
| ICD | 0,041 | 0,452 | 0,656 | 1,465 |
| PSD | 0,034 | 0,379 | 0,540 | 1,332 |
| TDM | 0,012 | 0,378 | 0,540 | 1,828 |
| BAY | 0,029 | 0,118 | 0,272 | 0,946 |

En términos absolutos MCN sí salta ~1,6× más. **Pero no porque la fila sea una unidad más ruidosa: porque su escala está inflada.** Medido: `z_MCN / z_ICD = 1,865` contra `√DEFF = 1,941` (ICC 0,4242, DEFF 3,7664 sobre la ventana viva de 37 días). MCN **es** ICD multiplicado por √DEFF, y sus saltos también. En relativo los cinco son indistinguibles.

**Eso cambia el argumento de C-3, y lo mejora.** El problema del McNemar de filas no es que sea frágil: es que **su tamaño real no es 5%**. Un test que rechaza a |z_naive| > 1,96 cuando el SE verdadero es √3,77 veces mayor rechaza en realidad a |z_true| > 1,010, o sea **α real ≈ 0,31**. Ése es el número que C-3 tiene que citar, no «cruzó tres veces». Y explica sin misterio el p = 0,0063 de hoy.

### Sensibilidad al Frente A — **VERIFICADO robusto** (chequeo que el documento no hizo)

Las conclusiones de C descansan sobre filas cuyo estatus canónico el Frente A deja abierto (el salto lo produce el 28-ago, justo el día que la fuente retiró). Sustituí las 15 filas por la reconstrucción de hoy (`/tmp/verif_c2.py`): MCN p 0,0063 → 0,0080; ICD [−4,09, 28,28] → [−4,26, 27,62]; PSD 0,183 → 0,189; TDM, AVS y SGN **idénticos**. **C no es rehén del Frente A.** Conviene que lo diga.

**Veredicto de las tres propuestas:**

- **C-1 (ratificar ICD; no publicar decisiones binarias hasta MDE firmado): ENTRA.** Es lo único de la noche que no necesita condición. Es además la única propuesta consistente con que hoy el instrumento tiene MDE de 24 pp (Frente B).
- **C-2 (AVS como secundario): ENTRA CON CONDICIONES.** (a) declarar que el estimando es la media no ponderada de medias diarias, distinta del ICD; (b) declarar la desviación del σ̂² respecto de WSR y su dirección (conservadora); (c) declarar que es de **una cola** mientras ICD y MCN son bilaterales; (d) declarar λ, c = 0,5 y α **antes**, en `DISEÑO.md`, no en el script; (e) **cuenta como intento** y hoy no está en el registro. Con eso, se publica al lado del ICD como capital acumulado, sin decidir nada.
- **C-3 (sacar el p de McNemar de filas de `duelo()`, `comparar_pareado()` y `control_lineal` como salida por defecto): ENTRA, con la justificación cambiada.** El motivo es α real ≈ 0,31 bajo DEFF 3,77, no la cuenta de cruces. `b` y `c` se siguen reportando siempre (regla 3 de la casa). Y hay que revisar que sacarlo no rompa la reproducción de cifras congeladas anteriores: `LINEA_BASE_OFICIAL` (`backtest/linea_base.py:161-169`) fija `McNemar p = 0,4633` como valor congelado de la §2.8, así que la función tiene que seguir **calculándolo** aunque deje de ofrecerlo por defecto.

---

## FRENTE D — `propuestas_cde.md` §D

### Salida 1 — **VERIFICADO exacto** (`/tmp/verif_d1.py`)

518 fechas (2024-09-02→2026-08-28), AC1…AC5 = [−0,042, −0,020, +0,012, −0,018, **+0,051**], AC1 = −0,042 con EE 1/√m = 0,044, IC95 bootstrap de bloques(20) = **[−0,122, +0,041]**; sellada 37 fechas, AC1 = −0,176 ± 0,164. El bootstrap está bien centrado (mediana −0,0438 vs punto −0,0423, sesgo −0,0015) y su sd 0,0421 no promete más que el 1/√518 = 0,0439 ingenuo: honesto.

**Errata menor:** la prosa dice «Nada por encima de 0,05 en ningún rezago»; su propio artefacto trae AC5 = **0,051**.

### La pregunta que me hacen: ¿una autocorrelación medida sobre datos RECONSTRUIDOS es evidencia admisible sobre los SELLADOS?

**Mi respuesta: como medición de referencia sí; como «cota externa» que estreche una banda firmada, no.** Tres razones, la primera a favor del proponente.

**1. Corrí el chequeo que decide la pregunta y que el documento no hizo, y sale a su favor.** Restringí la ventana larga al mismo tramo de calendario que la sellada (desde 2026-07-05, 40 fechas): **AC1 = −0,180 ± 0,158**, contra la sellada **−0,176 ± 0,164**. En el único tramo donde los dos objetos existen, la reconstrucción reproduce el sello **a 0,004**. Ése es el argumento que D-1 necesitaba y no tenía, y vale más que los tres que enumera.

**2. La objeción de mecanismo se mantiene, aunque debilitada.** La reconstrucción es **una sola descarga congelada** y por construcción no puede ver la dependencia inducida por **intermitencia de la fuente** — el mecanismo que M6 acaba de descubrir esta misma noche, en cuatro noches de agosto que caen dentro de ese tramo de 40 fechas. El chequeo del punto 1 sugiere que no dejó huella, pero con 40 fechas y EE 0,16 no resuelve un AC1 de ±0,15. La objeción no queda refutada: queda **no medible**.

**3. «Cota externa» es la palabra equivocada, y ahí está el rechazo.** [−0,122, +0,041] es un **intervalo de confianza sobre un punto estimado**, no una cota. Evaluar el α del plan exactamente en +0,041 trata el extremo de un IC como certeza. Y hay una segunda fuente de error que la propuesta descarta: cada α sale de 2.000 réplicas. Sumando las dos honestamente —`autocorrelacion_alfa_plan_prior.json`, Wilson incluida— el α del plan bajo la cota está en **[0,031, 0,065]**, no en [0,039, 0,055]. El extremo que importa sube de 0,055 a **0,065**. Sigue por debajo del 0,079 de la banda firmada, así que la propuesta conserva su contenido, pero **estrecha bastante menos de lo que anuncia**.

**Contaminación que revisé y que no bite** (queda en el acta para que no se descubra después como hallazgo): el AC1 se mide sobre la **suma** por fecha, y el conteo de filas por fecha tiene AC1 = **+0,242 ± 0,044** en la ventana larga (los feriados se agrupan). Como d_j es suma de términos de media ~0, eso induce heterocedasticidad y no autocorrelación de la media: el AC1 de la **media** por fecha es −0,028 contra −0,042 de la suma. Inmaterial.

**Detalle no declarado:** D.1 simula d_j **discretizado** (`np.round(d·7/2)` en `alfa_plan_bajo_correlacion`) y D.2 simula normales **continuas** (`cruces_plan`). Dos DGP en la misma sección sin decirlo.

### Salida 2 (D.2) — **VERIFICADO, la conclusión negativa se sostiene**

`venv/bin/python /tmp/verif_d2.py`, n_rep=4.000 con Wilson:

| φ | DIA | BLQ10 | BLQ20 | HAC5 | HAC10 |
|---|---|---|---|---|---|
| 0,0 | 0,0520 [0,046, 0,059] | 0,0895 | 0,1158 | 0,0635 | 0,0775 |
| 0,3 | 0,1678 | 0,1013 | 0,1215 | 0,0835 | 0,0955 |

Reproduce la tabla publicada dentro del ruido. **DIA = 0,052 a φ = 0 valida los umbrales OBF**, que es el autocontrol que hacía falta. Los bloques inflan desde φ=0 por grados de libertad (a 51 fechas, B=20 da 2 bloques y `_z_bloque` devuelve 0 — la primera mirada literalmente no puede cruzar), Newey-West es lo mejor y sigue sin dar 0,05 plano. **La conclusión de D.2 —a 51-203 fechas no hay estadístico que entregue α = 0,05 plano bajo φ desconocida— está verificada y se publica tal cual.** Un resultado negativo es un resultado.

**Veredicto D-1: NO ENTRA COMO ESTÁ.** Entra reescrita como **medición de referencia**, no como cota: (a) borrar «cota externa» y decir «AC1 estimada sobre la reconstrucción, IC95 [−0,122, +0,041]»; (b) incorporar el chequeo del tramo solapado (−0,180 ± 0,158 vs −0,176 ± 0,164), que es la mejor evidencia que tiene; (c) declarar que la reconstrucción es ciega a la intermitencia de M6 y que 40 fechas no lo resuelven; (d) el α del plan bajo esa referencia se publica como **[0,031, 0,065]**, con las dos fuentes de error; (e) corregir el AC5; (f) declarar los dos DGP. **La banda firmada [0,046, 0,079] no se toca — y con (d) tampoco habría por qué.** El α = 0,05 nominal con banda no se re-discute y no lo re-discuto.

---

## FRENTE E — `propuestas_cde.md` §E

Todo reproduce (`/tmp/verif_e.py`): E4 larga = **−1,608** pp/h exacto; `por_bolsa` sellada exacto (XTKS +14,18/134, XTAI +14,29/28, XKRX +6,25/64, XETR +11,43/35). La aritmética está bien. El problema es de unidad de replicación.

### E-2 (decaimiento como afirmación de mecanismo) — **RECHAZADO**

**Primer motivo: la unidad de replicación del mecanismo es la BOLSA, no la fecha.** Hay **4 bolsas y sólo 2 valores distintos de h** (XTKS y XKRX comparten 1,75). El IC [−2,45, −0,77] sale de remuestrear **fechas** con las 4 bolsas fijas: es pseudorreplicación. Con la bolsa como unidad:

```
permutación EXACTA de las 12 asignaciones distintas de h a las 4 bolsas:
    p = 0,231     p mínimo alcanzable = 1/13 = 0,077
bootstrap de bolsas (4 clústeres):  IC95 [−5,42, −1,37]   (3× más ancho que el publicado)
```

**Ningún test a nivel de bolsa puede alcanzar 0,05 con 4 bolsas.** El intervalo que «excluye la horizontal» excluye la horizontal porque mide la variabilidad equivocada.

**Segundo motivo, y es el que manda: el `README.md` ya lo dice, publicado, en la línea 60.** «Con **n = 4 bolsas no se puede ajustar una curva**. Esto es un **escalón**.» `E4` ajusta exactamente esa curva (`_pendiente(df, "h", "E0")`) y le pone intervalo. Ante discrepancia, manda el README. **Mi permutación es la versión cuantitativa de esa frase: p_mínimo = 0,077.**

**Tercer motivo: el orden no replica fuera de muestra.**

```
larga    XKRX(1,75) +17,6   XTKS(1,75) +14,1   XTAI(2,75) +12,2   XETR(8,75) +4,0   ← monótona
sellada  XKRX(1,75)  +6,2   XTKS(1,75) +14,2   XTAI(2,75) +14,3   XETR(8,75) +11,4  ← la más cercana es la peor
```

**Consecuencia sobre «~4× menos señal por día (D80 284 vs 75)»: la afirmación no está mal medida, está mal definida.** El 284 sale de un z cuya unidad de replicación es la fecha para un parámetro cuya unidad es la bolsa. El cociente no tiene interpretación, y por lo tanto **la contradicción con la recomendación 1b de `tesis.md` no queda establecida por esta medición.** Si el director condicionó 1b a este número, sigue sin resolverse.

Lo que **sí** puede publicarse del Frente E sobre el decaimiento: la tabla por bolsa con Wilson por bolsa, el contraste Asia−Fráncfort con clúster de fecha **declarado como contraste de 4 bolsas**, y la frase de que en la ventana sellada el orden se invierte. Sin pendiente por hora y sin su IC.

### E-1 (pendiente de calibración como endpoint secundario) — **OBSERVADO; entra sólo con tres condiciones**

`1,421 [0,648, 2,193] z=3,44 D80=25` en la sellada reproduce, y es cierto que es el único estimando que excluye el cero con clúster de día. Pero:

**(a) La ventaja de señal que lo justifica no existe en la ventana sellada.** Bootstrap **pareado** de fechas del cociente D80(E0)/D80(E3):

```
sellada   5,5×   IC95 [0,7, 1379,5]     ← contiene 1; tres órdenes de magnitud
larga     2,6×   IC95 [1,5, 4,8]        ← ahí sí es real
```

La propuesta cita la cifra sellada (25 vs 146) y el respaldo vive en la larga. Hay que decirlo así.

**(b) H0: b = 0 es un nulo que nadie sostiene, y b ≠ 0 no significa que el campeón le gane a nada.** «Siempre al alza» es una constante: su pendiente es 0 por construcción, así que b > 0 sólo dice que p correlaciona con g — y p = β·SOX(t−1). El propio WS2b ya estableció que **C1, el control de información, acierta la dirección en las MISMAS filas que el campeón (McNemar 0 vs 0)**. Un endpoint de calibración pre-registrado contra 0 repite exactamente el error que el proyecto se diagnosticó: comparar contra el cero en vez de contra el control. **Condición: pre-registrar E3 contra la pendiente de C1, no contra 0.**

**(c) Bundle de dos preguntas.** «H0: b = 0» (¿hay relación?) y «H0: b = 1» (¿está calibrado?) son endpoints distintos. Y el IC sellado [0,65, 2,19] **contiene 1**, así que hoy no distingue calibrado de subconfiado.

**E-1 entra como endpoint SECUNDARIO pre-registrado si y sólo si:** se declara contra la pendiente del control lineal; se separan las dos hipótesis; se cita el 2,6× [1,5, 4,8] de la larga como el respaldo real y se dice que en la sellada la ventaja no es distinguible; y se registra como intento antes de volver a mirarlo.

---

## Registro de intentos

**Existe** — `GEMELO/relevo_asiatico.REGISTRO_INTENTOS`, **21 tramos que suman 91** (el módulo `backtest/veredicto_51.py` congela `N_REGISTRO_AL_20260901_MEDIODIA = 86` y declaró 92 para la corrida `20260901-133154`, con test que ata las dos cifras). Bien construido y con procedencia por tramo.

**Y esta noche quedó desactualizado.** Sin registrar: los **7 candidatos a estadístico principal** del Frente C evaluados sobre la trayectoria real (BAY con prior sd = 0,05 elegida, AVS con c = 0,5 y α = 0,05, TDM y SGN son nuevos; MCN/ICD/PSD ya estaban como maquinaria) y los **6 estimandos** del Frente E evaluados sobre **dos** ventanas. Las simulaciones del Frente B y de D.2 no son intentos: no seleccionan sobre datos reales. **Ninguna configuración nueva puede alimentar un DSR ni habilitar V5 hasta que el registro las absorba, con su tramo y su archivo:línea.**

---

# ENTREGABLE

```
VEREDICTO: las cinco tandas de la séptima corrida, juzgadas una por una.

CIFRA REPORTADA / CIFRA VERIFICADA (con comando)

A(i)  0 retornos cambiados, 8 años × 27 tickers, tol 5e-6
      → VERIFICADO. 52.452 pares comparados, 0 no comparables, 0 cambiados,
        max |Δr| = 1,092e-6; 0 retiradas, 1 aparecida.
        venv/bin/python /tmp/verif_m1b.py  (retornos sobre el índice PROPIO
        de cada ticker, no sobre el índice unión del script)

A(ii) «1.962 celdas, TODAS reescalado proporcional; factor constante por
      ticker: 005930.KS 0,986792 · 6857.T 1,014781 · 2330.TW 0,997934»
      → NO REPRODUCE. Celdas históricas distintas = 1.953, todas de
        000660.KS, factor real 0,999783 (constante a 4e-7). Las otras 9 son
        la barra parcial del 26-ago. Los tres factores citados son esa barra
        viva: dos cachés a 95 s de distancia difieren en 000660.KS (−1000),
        8035.T (−70), 6857.T (−10), 4063.T (+1).  /tmp/verif_m1c.py, /tmp/verif_m1d.py

A(iii) M6: 31-jul es la única barra de 130; desvío 0,25–0,27 → 0,026–0,042
      → VERIFICADO, y ahora con el perfil completo que el JSON no guarda:
        1 de 130 con ≤0,05 en cada una de las 4 fechas, siempre 31-jul,
        brecha al 2º 0,035–0,057. Noches de control reproducen a 0,004–0,007.
        venv/bin/python /tmp/verif_m6.py
      → SIGUE SIENDO HIPÓTESIS: el residuo es 4–8× el piso de reproducción,
        no es redondeo. No se probó: cierre REVISADO (no ausente), ≥2 barras,
        perturbar series distintas de ^SOX, ni la dependencia entre las 4
        ventanas de 120 días solapadas.

A(iv) 8→0, 0→7, 64,86% → 64,49%, MAE 2,827 → 2,897
      → VERIFICADO salvo el MAE. Recomputando motor.prediccion_apertura_al
        hoy: 179/276 = 64,86% → 178/276 = 64,49%. MAE 2,8274 → 2,8919 con
        las 15 filas; el 2,897 sólo sale sustituyendo las 87 divergentes.
        Una frase, dos denominadores.  venv/bin/python /tmp/verif_iv.py

B     α empírico de la permutación de signo por día = 0,083 a 35 días
      → RECHAZADO. Misma función, sólo subiendo n_sim: 300→0,0833;
        1.000→0,0590; 3.000→0,0557 [0,048, 0,065]. Con semilla de permutación
        variable, 0,0440 [0,037, 0,052]. Es ruido de Monte Carlo.
        venv/bin/python /tmp/verif_b3.py
B     9 pp → 248 días; 6,5 → 475; 5 → 803; MDE 16,6 pp al 25-oct; potencia 0,36
      → VERIFICADOS como puntos. n=246, 35 días, +9,3496 pp, SE 8,5502 pp,
        ICC 0,3925, DEFF 3,5595.  venv/bin/python /tmp/verif_b1.py

C     3/0/0/2/0/0/0 cruces; MCN p=0,0063; ICD [−4,09; 28,28]; AVS K=3,031
      → VERIFICADO exacto.  venv/bin/python /tmp/verif_c1.py

D     518 fechas, AC1=−0,042, IC95 [−0,122, +0,041]; α del plan [0,039, 0,055]
      → AC1 VERIFICADO exacto. α: NO REPRODUCE como rango — con el error de
        Monte Carlo de las 2.000 réplicas es [0,031, 0,065].
        venv/bin/python /tmp/verif_d1.py ; /tmp/verif_d2.py
D.2   ningún estadístico da α=0,05 plano a 51–203 fechas
      → VERIFICADO (DIA 0,052 a φ=0 valida los umbrales OBF).

E     E3 sellada 1,42 [0,65, 2,19]; E4 −1,61 pp/h [−2,45, −0,77]; 4× (284 vs 75)
      → E3 y E4 reproducen exacto. El IC de E4 y el «4×» NO son admisibles:
        unidad de replicación equivocada.  venv/bin/python /tmp/verif_e.py

INTERVALO
  Wilson (módulo de la skill) para toda proporción: 64,86% [59,1; 70,2] y
  64,49% [58,7; 69,9] sobre 276; α empírico 0,0557 [0,048; 0,065] sobre 3.000.
  Bootstrap de CLÚSTER DE DÍA (no de bloques de 20 filas: con 35–37 días hay
  clústeres de sobra y el bloque de filas mezclaba días parciales — cambio ya
  firmado en el acta §61, lo acepto) para toda diferencia: ventaja de día
  +9,35 pp [−7,20; +26,32].
  Bootstrap ANIDADO para el SE del SE: SE de día [6,09; 10,06] pp →
  D(9 pp) = 248 [126, 343].
  PERMUTACIÓN EXACTA a nivel de bolsa para el mecanismo: p = 0,231,
  p mínimo alcanzable 0,077.
  McNemar exacto para todo pareado, con b y c: sello vs Yahoo-hoy b=8 c=7
  p=1,0000; ancla del Frente B b=72 c=49 p=0,0455; sin bloque 1 b=48 c=43
  p=0,675.

DENOMINADOR
  «Siempre al alza» sobre las MISMAS filas, convención excluir_cero, nunca 50%
  ni cero. Verificado en linea_base.aplicar_convencion:385-391 y en el duelo.
  Para el mecanismo (E4) el denominador honesto NO es la fecha: es la bolsa,
  y hay cuatro. Ése es el rechazo de E-2.
  Para el McNemar de filas el denominador de varianza está mal por DEFF 3,77:
  z_MCN/z_ICD = 1,865 contra √DEFF = 1,941, y el α real de un nominal 5% es
  ≈ 0,31. Ése es el motivo correcto de C-3.

INTENTOS CONTADOS
  91, en 21 tramos, de GEMELO/relevo_asiatico.REGISTRO_INTENTOS, con
  procedencia archivo:línea por tramo y test que lo ata a
  backtest/veredicto_51.N_INTENTOS_51. NO incluye lo de esta noche: los 7
  candidatos del Frente C sobre la trayectoria real ni los 6 estimandos del
  Frente E sobre dos ventanas. Sin eso registrado, ningún DSR y ninguna
  evaluación de V5.

CRITERIOS
  V1  NO PASA. Vara vigente n=248, +6,5 pp, McNemar p=0,1849. Nadie la superó
      y nada de esta noche la mueve. El p=0,0063 de trayectoria.md NO es un
      V1: es otra ventana (n=261, 37 días, vivo) y es el estadístico de filas,
      cuyo IC de día es [−4,09; +28,28] e incluye el cero.
  V2  NO EVALUABLE. No se midió CRPS en esta corrida.
  V3  NO PASA (campeón). 90,3%, fuera de [76, 84], ratio de ancho 1,84×. Sin
      retador medido: NO EVALUABLE del lado del retador.
  V4  NO EVALUABLE. La vara sigue en 2,98 pp sobre n=248; el 2,827/2,892 de
      esta noche es el campeón sobre la ventana VIVA, no un retador.
  V5  NO EVALUABLE, y bloqueado: el registro de intentos no absorbió las
      configuraciones de los Frentes C y E.
  V6  NO EVALUABLE. Sin barrido de sensibilidad ni benchmark SMH esta noche.
  V7  NO EVALUABLE, y correctamente no gastado (veredicto_51.py:13-16).
  R1  NO EVALUABLE esta noche. Vigente de WS2b: C1 acierta dirección en las
      MISMAS filas que el campeón (McNemar 0 vs 0), que no es R1 disparado
      pero tampoco es R1 despejado.
  R2  DISPARADO, y sin nombrar en el documento que lo contiene. Sobre el
      ancla del Frente B: +9,3 → +2,5 pp al excluir 15–23 jul; McNemar filas
      p=0,675; IC de día [−13,64; +19,23]; permutación de día p=0,8248. Los
      seis días del bloque 1 están enteros en la «primera mitad» que
      horizonte_veredicto.md presenta como chequeo de estacionariedad.
  R3  NO DISPARADO esta noche. Los cinco scripts leen senales.db en mode=ro,
      no reescriben GEMELO/cache/ (usar_cache=False no escribe: datos.py:222)
      y consumen la corrida 20260901-133154 (arnés corregido), no la
      20260901-061708 invalidada por fuga. Sin look-ahead nuevo.

DICTAMEN POR FRENTE
  A   VERIFICADO en (i), (iii) y (iv) · OBSERVADO en (ii) y en el MAE de (iv).
      Entra a documento de resultados con las correcciones en su sitio.
  B   RECHAZADO el α = 0,083 (vivo hoy en horizonte_veredicto.md:39,
      horizonte.md:33 y propuestas_cde.md:62) · OBSERVADO el gasto de α mal
      citado, la cadencia y la potencia sin intervalo · y R2 sin nombrar.
      El resto VERIFICADO. Entra con las tres condiciones.
  C   VERIFICADO. C-1 ENTRA sin condición. C-2 ENTRA con cinco declaraciones.
      C-3 ENTRA con el motivo cambiado (α real ≈ 0,31, no la cuenta de cruces).
  D   Salida 1 VERIFICADA como medición; D-1 NO ENTRA como «cota externa».
      Entra reescrita como medición de referencia, con el chequeo del tramo
      solapado (−0,180 ± 0,158 vs −0,176 ± 0,164) incorporado y el α en
      [0,031, 0,065]. D.2 VERIFICADO y se publica tal cual. La banda firmada
      no se toca.
  E   E-1 OBSERVADO: entra como secundario sólo pre-registrado contra la
      pendiente del control lineal, con las dos hipótesis separadas y con el
      2,6× [1,5; 4,8] de la larga como respaldo declarado.
      E-2 RECHAZADO: no entra a ningún documento de resultados con pendiente
      por hora ni con su IC. Puede publicarse la tabla por bolsa y el
      contraste Asia−Fráncfort, declarados como comparación de 4 bolsas.

DICTAMEN GLOBAL: NO CONCLUYENTE — y hacia el lado negativo.
  Nada de esta noche acerca a nadie a V1. Dos cifras publicables se caen
  (α = 0,083; el IC del decaimiento por hora), una tercera no reproduce su
  propio respaldo (la clasificación proporcional de M1), y R2 —una vara de
  RECHAZO congelada— está cumplida sobre el ancla del Frente B sin que el
  documento la nombre. Lo que sí queda en pie, y es el resultado de la noche:
  el sello guardó un dato que la fuente retiró y esa diferencia mueve el
  track record en b=8, c=7, p=1,0000; el instrumento no es estructuralmente
  subpotente pero su MDE hoy es de 24 pp y al 25-oct de 16,6; el McNemar de
  filas tiene α real ≈ 0,31 bajo el agrupamiento de día; y a 51–203 fechas
  no existe estadístico con α = 0,05 plano bajo φ desconocida.
  Que nadie gane sigue siendo el resultado. Se publica igual.
```

**Nota de proceso, para la bitácora:** `GEMELO/resultados/horizonte.md` y `horizonte_veredicto.md` cambiaron en disco a las 06:44–06:48Z **durante** esta auditoría, agregando los IC de D y del SE que yo estaba calculando en paralelo (su bootstrap anidado da [5,67; 10,45] pp de SE contra mis [6,09; 10,06] — mismo orden, acepto el suyo). El cambio va en la dirección correcta y no lo revierto, pero **este dictamen juzga la versión de las 06:48Z**, y en ella el α = 0,083 sigue en pie en los tres archivos. Ningún archivo fue escrito por mí; los scripts de verificación quedaron en `/tmp/verif_*.py` y son desechables — todo lo que importa está reproducido arriba con su comando.
