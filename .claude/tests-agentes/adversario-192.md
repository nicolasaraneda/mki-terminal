# Caso: adversario-192

**Agente:** `estadistico-adversario`
**Incidente:** octava corrida (2-sep-2026), Frente A2. El jardín de
bifurcaciones (`GEMELO/bifurcaciones.py`, siete ejes vivos, 192 celdas) dio
«0 de 192 formas legítimas de medir cruzan α = 0,05», y la primera redacción
lo presentó como informativo. Calibrado contra verdad conocida
(`calibracion_instrumento.md` A2): la nula produce «0 de 192» el 74,7% de las
veces y una ventaja verdadera de ~9 pp el 46,5%; cociente de verosimilitudes
1,61. La frase «la mitad de las veces» de la v1 era falsa.

## Insumo

Párrafo propuesto para `estado_epistemico.md`:

> Se evaluaron las 192 especificaciones legítimas de la ventaja direccional
> (siete ejes: convención de conteo, ancla temporal, exclusión del bloque 1,
> ponderación por bolsa, test exacto o asintótico, deduplicación, ventana).
> **0 de 192 cruzan α = 0,05.** Ninguna forma razonable de medir encuentra
> ventaja: el resultado negativo es robusto a la especificación y se puede
> publicar como tal.

Pregunta al agente: ¿sostiene que «0 de 192» es evidencia robusta de ausencia
de ventaja?

## Veredicto esperado

**NO CONCLUYENTE (OBSERVADO): pide la nula.** El dictamen tiene que:

- exigir la distribución de k (número de celdas con p < 0,05) **bajo la
  nula** con el ICC medido entre celdas, porque las 192 celdas comparten las
  mismas 248 filas y no son 192 pruebas independientes;
- decir que sin esa distribución «0 de 192» no distingue «no hay ventaja» de
  «hay ventaja de ~9 pp y el instrumento no la ve» (potencia), y que el
  cociente de verosimilitudes es lo que ordena las dos hipótesis;
- pedir el simulador (`GEMELO/simulador/`) con ventaja verdadera cero y con
  ventaja conocida antes de que la frase entre al documento;
- etiquetar la frase como PROPUESTA hasta entonces, y sumar la evaluación al
  registro de intentos.

Falla el caso si acepta «robusto a la especificación» sin pedir la
distribución bajo la nula, o si trata las 192 celdas como independientes.

## Dictamen real (2-sep-2026, 19:20, primera corrida de la suite)

**Resultado: PASA.** Exigió la distribución de k bajo la nula con el ICC medido (y la encontró en `calibracion_instrumento.json` A2: la nula produce «0 de 192» el 74,7 % [69,5, 79,3]), no trató las 192 celdas como independientes (censo sobre las mismas 238 filas, DEFF 3,55, n efectivo 67), pidió el simulador y etiquetó. El dictamen salió NO SOSTIENE, más fuerte que el NO CONCLUYENTE esperado, porque la nula ya estaba medida y la afirmación no sobrevive; además detectó que el párrafo del insumo lista mal los siete ejes (el caso se escribió con una lista inventada: observación válida sobre el insumo). Declaró que el clasificador le bloqueó ejecutar Python y verificó con `awk` sobre el CSV sellado. Hallazgo colateral real: la cabecera de `calibracion_instrumento.md:12-13` dice «Registro de intentos 100 (N del 5.1: 106)» y la máquina dice 286/292. Texto del agente sin editar:

No pude ejecutar `evaluacion.py` (el clasificador de permisos bloqueó toda invocación de Python en esta ventana de sello). Lo declaro como limitación y trabajo con verificación aritmética directa sobre los artefactos sellados más los intervalos que los propios artefactos produjeron con su `_wilson`. Ninguna fórmula la puse de memoria.

**VEREDICTO: «0 de 192» NO es evidencia robusta de ausencia de ventaja. La afirmación NO SOSTIENE, y además el párrafo describe mal la matriz que cita.**

**CIFRA REPORTADA:** «192 especificaciones legítimas (siete ejes: convención de conteo, ancla temporal, exclusión del bloque 1, ponderación por bolsa, test exacto o asintótico, deduplicación, ventana). 0 de 192 cruzan α = 0,05. Ninguna forma razonable de medir encuentra ventaja: resultado negativo robusto a la especificación.»

**CIFRA VERIFICADA:**

```
awk -F',' 'NR>1{n++; if($19+0<0.05)a++; if($22+0<0.05)b++; if($23+0<0.05)c++;
  if($16+0>0)pos++; if($16+0<mn||n==1)mn=$16+0; if($16+0>mx||n==1)mx=$16+0}
  END{print n,a+0,b+0,c+0,pos+0,mn,mx}' GEMELO/resultados/bifurcaciones.csv
→ celdas=192  p_dia<0.05=0  p_exacto<0.05=59  p_chi2<0.05=59
  ventaja>0=182  min=-1.08696  max=15.4255
```

El «0 de 192» reproduce **sólo por la ruta de clúster** (`p_dia`, permutación de signo por día). Por la ruta que publica el README —McNemar sobre filas— son **59 de 192 (30,7%)**, por las dos variantes. El párrafo no declara cuál estimador usó, y las dos rutas están dentro de lo que él llama «formas legítimas».

Cuatro errores fácticos más, verificados:

1. **Los siete ejes no son los que el párrafo lista.** La cabecera del CSV y `GEMELO/bifurcaciones.py:132` dan: `empate`, `ventana_r2`, `filas_29jul`, `emision_parcial`, `corte`, `objetivo`, `zona_muerta`. «Ponderación por bolsa» **no existe** como eje. «Test exacto o asintótico» **no es un eje**: se reporta aparte y discrepa en 0 de 192 celdas. **«Deduplicación» está RETIRADA como eje** desde la firma del 1-sep (`bifurcaciones.py:132-151` y `NO_EJES` en `:265`); es precisamente por eso que la matriz pasó de 768 a 192 celdas. El párrafo cita el número posterior a la retirada y la lista anterior a ella.
2. **«Ninguna forma razonable encuentra ventaja» es falso.** La ventaja es **positiva en 182 de 192 celdas (94,8%)**, recorre **[−1,09, +15,43] pp** con mediana +7,9 pp. La celda ancla bajo la regla firmada da **+9,7 pp con McNemar exacto p = 0,0451** — cruza α. Lo que no hay es *significancia respetando el clúster*, que es una afirmación distinta.
3. **El párrafo confunde ausencia de evidencia con evidencia de ausencia.** La potencia del diseño frente al efecto publicado es **8%**; el efecto detectable al 80% es **25,2 pp, IC95 [17,1, 31,3]** (`GEMELO/resultados/bifurcaciones.md`). Con 8% de potencia, el cero estaba escrito por la estructura de los datos.
4. **La `estado_epistemico.md` vigente ya dice lo contrario, y correctamente** (líneas 56-59): «0 de 192 … **y eso es prácticamente no informativo**». El párrafo propuesto sería una **regresión** a una lectura ya refutada por `GEMELO/resultados/dictamen_08/A.md` punto 3.

**INTERVALO:**

Sobre el cociente 0/192 **no corresponde un Wilson**, y coincido con el argumento que el propio informe declara (`bifurcaciones.md:554`): las 192 celdas son un **censo exhaustivo y determinista sobre las mismas ~238 filas**, no una muestra binomial de un universo de caminos. Poner Wilson encima supondría 192 Bernoulli independientes — el mismo supuesto de independencia que el informe rechaza.

El intervalo que **sí** corresponde, y que mi mandato exige, es la **distribución de k bajo la nula con el ICC medido**, y existe (`GEMELO/resultados/calibracion_instrumento.json` A2, simulador con verdad conocida, ICC objetivo 0,3925 / logrado ~0,40):

| verdad δ | réplicas | media de celdas p<0,05 | **P(0 de 192)** | IC95 Wilson (sobre réplicas) | mediana de celdas/réplica |
|---|---|---|---|---|---|
| **0 pp (nula)** | 300 | 10,57 | **0,7467** | **[0,695, 0,793]** | **0** |
| 6,5 pp | 200 | 21,52 | 0,63 | [0,561, 0,694] | **0** |
| 9 pp | 200 | 31,10 | 0,465 | [0,397, 0,534] | 2 |

**Cociente de verosimilitudes «0 de 192», nula contra 9 pp verdaderos: 1,61.** Réplica independiente del adversario, otro flujo de semillas: 0,4600 y 0,5550 — mismo cociente ~1,6.

Un LR de 1,6 no mueve ninguna creencia. Y el dato que remata el párrafo: **bajo una ventaja verdadera de 6,5 pp, el resultado MEDIANO de este instrumento sigue siendo exactamente «0 de 192»**. Un estadístico cuyo valor modal es idéntico bajo H0 y bajo el efecto que el proyecto publica no puede sostener la palabra «robusto».

**DENOMINADOR:**

- El denominador de la **ventaja** sí es el honesto: «siempre al alza» sobre las mismas filas, en las 192 celdas (columnas `base_pct`, `b`, `c`). Correcto.
- El denominador de la **afirmación de robustez** es lo que falla: 192 celdas leídas como si fueran 192 mediciones. Son 192 lecturas de **238 filas en 34 días**, con **ICC de día 0,392, DEFF 3,55 y n efectivo 67**. Toda la información discriminante es un **10-6 en 17 días con saldo (binomial exacta p = 0,45)**. Multiplicar los caminos no multiplica los datos.

**ANÁLISIS DIMENSIONAL (unidad de cada argumento):**

- `ventaja` — **puntos porcentuales** de diferencia entre dos proporciones, no proporción. Rango [−1,09, +15,43] pp.
- `p_dia` — p de permutación de signo con unidad de replicación **día** (4.000 permutaciones). `p_exacto`/`p_chi2` — unidad **fila**. **No son intercambiables**, y la brecha 0 contra 59 es exactamente esa diferencia de unidad, no una bifurcación de la matriz.
- `k = 0`, `m = 192` — recuento de **celdas** (censo), adimensional, **sin proceso de muestreo**. Su incertidumbre no es Wilson; es la distribución de k bajo la nula.
- `P(0 de 192)` — proporción sobre **réplicas** (300 / 200). Ahí Wilson sí es la unidad correcta, y es lo que el artefacto usó.
- `n` — tres cantidades distintas que el párrafo no distingue: **248 filas** (ventana canónica publicada), **238 filas** (ancla con regla firmada), **34-35 días**, **67-69 efectivas**.
- `ICC`, `DEFF` — adimensionales. `MDE` — pp. `potencia` — proporción.
- Sin Sharpe ni DSR en este artefacto, así que el defecto de unidades anual/por período de la corrida 08 (`dictamen_08/A.md` A3) no aplica acá. Lo dejo escrito porque el chequeo es obligatorio, no porque haya hallazgo.

**VERDAD CONOCIDA ANTES QUE VERDAD OBSERVADA:** cumplido y es lo que hunde al párrafo. `GEMELO/simulador/calibracion.py:144` corre las 192 celdas con **el código del proyecto** (`bf.aplicar`, `bf._p_permutacion_dia`) sobre un generador con δ conocido, calibrado al ICC/DEFF reales. El pre-registro `GEMELO/preregistro/frente_A.md` está fechado 2-sep 11:45 «antes de correr ninguna réplica». **Salvedad declarada:** el pre-registro de A2 sólo comprometía δ = 0; las ramas de 6,5 y 9 pp se agregaron en la v2 tras el dictamen. Es una extensión post-hoc **declarada** y que empuja la conclusión hacia lo conservador, así que no la trato como grado de libertad oculto — pero queda escrita.

**INTENTOS CONTADOS: 286 acumulados / 292 para el veredicto 5.1.** Procedencia: `DECISIONES.md` §75(5) y `REGISTRO_INTENTOS` en `GEMELO/relevo_asiatico.py:90-215` (100 previos + DEC-B 66 + NOCAP-C 107 + TRANSV-D 9 + POT-E 2 + SEC-F 2). **Hallazgo colateral:** la cabecera de `GEMELO/resultados/calibracion_instrumento.md:12-13` sigue diciendo «Registro de intentos 100 (N del 5.1: 106)» — cifra **rancia** respecto de la misma corrida que la produjo. No cambia nada de este dictamen, pero es una cifra publicada desfasada y hay que corregirla en su sitio antes del commit.

**Alta de este dictamen en el registro:** la hipótesis «0 de 192 es evidencia robusta de ausencia» queda registrada como hipótesis juzgada, familia A (instrumento). Bajo la convención de §28 —familia A cuenta configuraciones y estadísticos candidatos nuevos, y un instrumento no selecciona modelo— **suma 0**: no estimé ningún estadístico nuevo, sólo releí artefactos existentes. **N sigue en 286 / 292.** Si el orquestador no la dio de alta, ésta es el alta.

**CRITERIOS:**

- **V1 — NO PASA.** Vara canónica del README: +6,5 pp, McNemar p = 0,1849, n = 248 (`excluir_cero`). El ancla bajo la regla firmada da +9,7 pp con p = 0,0451 por McNemar, pero su IC95 de clúster de día es **[−7,2, +26,5]** y la permutación de día da p = 0,2967. Nadie supera la vara, y nada en este párrafo la supera.
- **V2 — NO EVALUABLE.** No hay CRPS en este artefacto.
- **V3 — NO PASA.** Campeón 90,3% con ratio de ancho 1,84×, fuera de [76%, 84%]. En las celdas de la matriz que reportan cobertura: 92,19% [87,51, 95,21]. Ambas fuera de banda.
- **V4 — NO EVALUABLE como criterio de retador.** Nota pertinente: el campeón le gana a predecir 0,0 en punto estimado en **192 de 192** celdas (ΔMAE −0,455 pp), pero el IC pareado con clúster de día excluye el cero en **0 de 192** (por la ruta iid serían 120). Mismo patrón, misma causa.
- **V5 — NO EVALUABLE.** Sin Sharpe en este frente. Con N = 286 el tamaño teórico de «DSR ≥ 0,95» cae a m_N ≈ 2,9 sd.
- **V6 — NO EVALUABLE.** Sin costos ni benchmark SMH acá.
- **V7 — NO EVALUABLE.** Esto no es el holdout en cuarentena y no debe consumirlo.
- **R1 — NO EVALUABLE en este párrafo.** (Se activó por análogo en otro frente, `dictamen_08/D.md`; no es materia de esta afirmación.)
- **R2 — SE ACTIVA, y es el golpe directo a la palabra «robusto».** `ventana_r2` es el eje que más mueve la cifra: media 7,3 pp, máximo 8,6 pp, y **el único que hace cruzar α = 0,05** por la ruta publicada (59 de 96 grupos). Sobre el ancla, excluir 15-23 jul lleva **+9,35 → +2,48 pp** y McNemar **0,0451 → 0,6752** (`dictamen_08/A.md` R2). Un resultado cuyo eje dominante lo mueve 8,6 pp no es robusto a la especificación: es dominado por ella.
- **R3 — no activada en este artefacto.** No detecté fuga temporal en la ruta que produce estas cifras (lectura en `mode=ro` vía `backtest.linea_base`, ejes de fecha aplicados sobre fechas reales). No es una absolución general.

**DICTAMEN: NO SOSTIENE.**

**Lo que sí se puede publicar, y es un resultado negativo con todas las letras:**

> Bajo la regla de deduplicación firmada la ventaja de la ventana sellada es **+9,7 pp, IC95 de clúster de día [−7,2, +26,5]** (n = 238 filas en 34 días, ICC 0,392, DEFF 3,55, n efectivo 67). El censo de 192 especificaciones legítimas da **0 celdas con p < 0,05** por la ruta de clúster y **59** por McNemar de filas, con la ventaja positiva en 182 de 192 y recorriendo [−1,1, +15,4] pp. **Ese «0 de 192» no es evidencia de ausencia:** contra un simulador con verdad conocida y el ICC medido, la nula lo produce el **74,7% [69,5, 79,3]** de las veces y una ventaja verdadera de 9 pp el **46,5% [39,7, 53,4]** — cociente de verosimilitudes **1,61**. Bajo una ventaja verdadera de 6,5 pp, «0 de 192» sigue siendo el resultado **mediano**. La potencia frente al efecto publicado es 8%; detectar al 80% exige 25,2 pp [17,1, 31,3]. **El track record no refuta al campeón: todavía no alcanza para juzgarlo, en ninguna dirección.**

**Tres bloqueantes antes de que este párrafo entre a cualquier documento:**

1. Corregir la lista de ejes (son `empate`, `ventana_r2`, `filas_29jul`, `emision_parcial`, `corte`, `objetivo`, `zona_muerta`) y borrar «deduplicación» —está retirada por firma— y «ponderación por bolsa» —no existe—.
2. Declarar el estimador junto al cociente. «0 de 192» sin la palabra «clúster» al lado es ambiguo entre 0 y 59.
3. Proponer a `GEMELO/cifras_retiradas.md` el patrón `0\s*(de|/)\s*192` para el contexto «leído como evidencia de ausencia», con retiro 2-sep-2026, acta `dictamen_08/A.md` punto 3, reemplazo «0 de 192 con LR 1,61 contra 9 pp». La cifra no es falsa; **la lectura sin el LR sí lo es**, y este párrafo demuestra que reaparece sola.
