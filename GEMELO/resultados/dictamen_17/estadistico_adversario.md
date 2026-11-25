# Quinto dictamen del `estadistico-adversario` sobre `GEMELO/SECUENCIAL/DISEÑO.md` v6

**25-oct-2026, 21:52 UTC.** Corrida 17, worktree `wt17`. Ninguna cifra de
este dictamen se cita de memoria: todas salen de correr los scripts
autorizados por el encargo, y las que no reproducen están marcadas.

**VEREDICTO: RECHAZADO.** Quinto rechazo. No se puede congelar.

Las cuatro condiciones del cuarto dictamen están atendidas **de verdad y no
maquilladas** — eso se dice primero porque es cierto y porque es la parte
difícil. El rechazo no viene de ellas. Viene de tres defectos que la corrida
17 no buscaba y que son de la misma clase que los que hundieron a la v1, a la
v2 y a la v3: **un documento que declara congelado algo que su propia
recomendación contradice, un intervalo que mezcla réplicas distintas del mismo
remuestreo, y una cantidad que el plan trata como dos parámetros
independientes cuando es una sola y la misma.**

---

## 0. Qué reproduce

Todo. Con `/home/nicolasaraneda/dev/mki-terminal/venv/bin/python`, desde el
worktree:

| Cifra de la v6 | Comando | Reproduce |
|---|---|---|
| ventana antecedente n = 262 en 37 fechas; 272 sin la regla; retira 10; empates 5 de 267 (1.87 %); 10 filas en 5 grupos tras la regla | `python -m GEMELO.SECUENCIAL.ventana_antecedente` | EXACTO |
| 30 filas / 15 grupos / **4** sesiones antes de la regla | idem, y `mde_desde_v6 --json` | EXACTO |
| población 288 filas, 38 días hábiles, 36 fechas, 7.579 filas/día hábil | idem | EXACTO |
| `p_d` = 129/262 = 0.4924 · E\|gap\| = 2.8921 % [2.2250, 3.8368] · E\|r\| = 3.5556 % (3.8666 sin la regla) · `f` = 0.4924 [0.3190, 0.6565] | `python -m GEMELO.SECUENCIAL.mde_desde_v6` | EXACTO |
| MDE 25 pb = 8.51 pp IC95 [4.94, 13.09]; sólo E\|gap\| [6.42, 11.06]; 10 pb 3.40 [1.98, 5.24]; 50 pb 17.02 [9.89, 26.18] | idem | EXACTO |
| SMH −8.47 % en 40 sesiones; tasa necesaria 54.1 % [53.2, 55.2]; baseline 54.2 % Wilson [48.1, 60.1]; los intervalos se superponen | idem (con red) | EXACTO |
| `ac1` = −0.176 ± 0.164 sobre 37 fechas | `mirada.autocorrelacion_lag1` sobre la ventana anclada | EXACTO |
| MDE crítico 11.08 pp, dentro del IC95; abanico 5823/1958/1416/1152/823; potencia 0.8000 vs 0.7537 | `python -m GEMELO.SECUENCIAL.tabla_firma` | EXACTO |
| 296 contra 288 = las 8 filas del 28-sep que retira la conocibilidad | conteo propio (ver §0.2) | EXACTO |
| suite | `pytest tests/test_secuencial_17.py tests/test_secuencial.py tests/test_epistemico.py -q` | 83 pasan, 1 skip, 1 xfail; con `--runxfail` sobre los dos de secuencial, 66 pasan |

**0.1 El ancla es real y no puede abrirse.** `cierre_de_ventana()` da 0
tardías y la última verificación de la ventana es `2026-09-02T22:15:11`. Conté
además las filas emitidas hasta el 31-ago por estado: 277 `verificada`, 2
`sin_datos_mercado` (terminal, fuera de toda métrica) y **ninguna
`pendiente`**, y ninguna fila de verificación con `gap_pct` nulo. O sea: no
existe la fila que podría llegar tarde y abrir la ventana. El candado es
exigible y además inerte, que es la combinación correcta.

**0.2 El conteo de la población cuadra al entero.** Filas emitidas con fecha
posterior al 31-ago: 912, en 38 fechas, 24 por fecha. Por estado: 296
`verificada`, 8 `pendiente`, 608 sin estado. 296 − 8 (las del 28-sep que
retira la conocibilidad) = **288**, que son 36 fechas × 8. Las 8 `pendiente`
son del 23-oct, posteriores a la última fecha verificada (22-oct), y el
denominador de días hábiles termina también el 22-oct: no hay censura por la
derecha. La errata del acta §107.1 está bien explicada.

**0.3 La declaración de dirección del sesgo de §A3.5 SOBREVIVE.** Busqué el
sesgo que corriera en contra y no existe: el 23-oct queda fuera del numerador
y del denominador; el 28-sep es un hueco realizado que ya está dentro del
ritmo medido; `_dias_habiles` da 38 exactos del 1-sep al 22-oct y no hay
feriado de mercado sin emisión dentro de la ventana (el 7-sep selló). Con el
conteo sin `excluir_cero` como techo, las fechas proyectadas son más tempranas
que las reales y el stock declara más progreso del real: las dos en la misma
dirección. **Esta declaración está bien hecha.**

**0.4 La condición 4 está atendida con tests de comportamiento, no
tautológicos.** `test_el_mde_no_se_mueve_si_la_base_crece_despues_del_corte`
mueve `CORTE_SELLO` a 2027-12-31 y exige el mismo número;
`test_la_medicion_no_se_mueve_...` inyecta una fila sintética posterior al
corte y exige que no entre; `test_el_intervalo_conjunto_es_mas_ancho_...`
prueba la propagación por su efecto; `test_p_d_del_plan_es_la_que_mide_el_script`
ata la constante a su script. Y el hallazgo colateral —que
`diseno_secuencial.ac1_ventana_antecedente()` leía la base VIVA y correrlo hoy
habría computado `ac1` sobre la población sin dejar línea en
`miradas/registro.log`— es un hallazgo real, de la clase que este agente
existe para pedir. Verifiqué que `GEMELO/SECUENCIAL/miradas/` no existe ni en
el worktree ni en el árbol real.

**0.5 El DEFF de planificación está respaldado.** Sobre la ventana anclada,
`V̂` por bloque = {1: 3.618, 5: 2.517, 10: 2.652}, máximo **3.618** contra el
`DEFF_PLANIFICACION = 3.6` supuesto. El supuesto de planificación se sostiene.
Crédito.

**0.6 El error estándar de `ac1` es CONSERVADOR, y mi hipótesis contraria se
cayó.** Supuse que los ceros estructurales inflaban el error estándar
verdadero y que el 1/√37 de Bartlett lo subestimaba. Lo corrí contra verdad
conocida: 20 000 réplicas bajo H₀ con el patrón de ceros REAL (20 de 37
fechas con `d_j` = 0 exacto), magnitudes remuestreadas con signo aleatorio. El
error estándar verdadero es **0.142** contra el 0.164 publicado: Bartlett es
conservador por un factor 1.16. **El documento tiene razón y yo no.** Queda
dicho con la misma firmeza que los rechazos.

---

## 1. Las cuatro condiciones, una por una

### (i) La regla de deduplicación — **ATENDIDA, y el reparto que la v6 propone es correcto**

El hallazgo de la v6 —que hay DOS reglas y la v5 las trataba como una— es
cierto y es el hallazgo que cierra el defecto descalificante del cuarto
dictamen. La regla de FILAS está firmada (actas §60 y §61), arbitra por
correspondencia entre `sesion_objetivo` y `available_at`, y ahora los dos
lados del pre-registro la usan: verifiqué que `mde_desde_v6.cargar_filas`
delega en `ventana_antecedente.cargar_antecedente(dedup=True)`, que llama a
`lb.cargar` con la regla firmada. **El parámetro de estorbo y el estimador ya
se miden sobre el mismo conjunto de filas.** Condición cumplida.

Pero la condición deja un residuo que la v6 no vio, y es grave: ver §5 abajo
(los grupos de CUATRO).

### (ii) §A3.1.b con intervalos — **ATENDIDA, y el resultado es peor de lo que la v6 cree**

Los intervalos están puestos y la conclusión honesta está escrita: la razón 1
no se sostiene con intervalo. Verifiqué los dos intervalos y la superposición.

Lo que la v6 no vio es que **la frase que resume el hallazgo no tiene
resolución**. Dice que los dos puntos «están a 0.1 pp uno de otro». Medí dos
perturbaciones aritméticas de su propio cómputo:

| Qué se cambia | tasa necesaria | movimiento |
|---|---|---|
| lo que el script hace: total ÷ 40 **barras**, `2c` cada sesión | 54.05 % | — |
| total ÷ 39 (40 cierres son 39 retornos) | 53.98 % | **0.08 pp** |
| `f·2c` en vez de `2c` (el modelo de costo de §A3.1.c, la subsección siguiente) | 50.48 % | **3.57 pp** |
| las dos a la vez | 50.41 % | 3.64 pp |

`retorno_benchmark()` divide el retorno total por `len(v)` = 40, que es el
número de CIERRES; entre 40 cierres hay 39 retornos. Ese off-by-one mueve la
cifra **0.08 pp, el tamaño mismo de la brecha sobre la que se apoya la
frase.** Y el modelo de costo es inconsistente con la subsección de al lado:
la razón 1 cobra el viaje redondo TODAS las sesiones, mientras §A3.1.c cobra
`2c` sólo en la fracción `f` de sesiones en que el modelo dice BAJA — que es
la definición de la misma estrategia. Esa diferencia vale 3.57 pp, **36 veces
la brecha que la frase reporta**, y empuja en la dirección que le devolvería
margen a la baseline.

**La conclusión de la sección sobrevive las cuatro variantes** (tasa necesaria
entre 50.4 % y 54.1 % contra la Wilson de la baseline [48.1, 60.1]: se
superponen siempre). Lo que no sobrevive es el número ni la frase, y un
pre-registro no congela frases sin resolución. También: `b_ses` mezcla un
retorno total COMPUESTO dividido por un número de períodos con una media
ARITMÉTICA de retornos por sesión; es otro bamboleo del mismo tamaño que la
brecha. La tarjeta §94 tiene razón en que el insumo no se puede pre-registrar.

### (iii) El MDE en la escala del endpoint con su intervalo — **ATENDIDA en la forma, ROTA en el fondo**

La escala está corregida (el endpoint es `acierto_gap`, la magnitud es
E|gap|), la fórmula es correcta y el álgebra verifica: δ = (2q−1)·f, la
condición económica E[gap|baja] < −2c, y bajo magnitudes simétricas
δ_min = f·2c/E|gap|. **Análisis dimensional, argumento por argumento:** `c`
proporción por lado (0.0025); `2c` proporción, viaje redondo; `E|gap|`
proporción (el script divide el porcentaje sellado por 100); `f` proporción;
`δ_min` proporción, ×100 para pp. Consistente. 0.4924 × 0.005 / 0.028921 =
0.08514 → 8.51 pp. Correcto.

El intervalo conjunto está bien construido como percentil de la RAZÓN sobre
los mismos clústeres de día remuestreados (ver §2). Lo que está roto es lo que
el documento hace DESPUÉS con ese intervalo: ver §2 y el defecto D2.

### (iv) El ancla de `mde_desde_v6.py` con tests no tautológicos — **ATENDIDA**

Ver §0.1 y §0.4. Es la condición mejor atendida de las cuatro.

---

## 2. El intervalo conjunto del MDE

**¿Es correcto propagar `f` y E|gap| con el mismo bootstrap de clústeres de
día y leer el percentil de la razón? SÍ.** `_mde(idx)` recomputa las dos
cantidades sobre los MISMOS índices remuestreados, así que la correlación
entre ellas queda dentro, que es exactamente lo que faltaba. El percentil de la
razón es el bootstrap de percentil estándar sobre el estadístico plug-in, y
la unidad del remuestreo es la correcta: la fecha de emisión. El test de que
el conjunto es más ancho que el de un insumo es un test de comportamiento, no
una reescritura. Esta parte está bien.

**¿El `f` con IC [0.319, 0.657] sobre 37 clústeres es creíble o el bootstrap
está mal especificado? ES CREÍBLE, y el que lo encuentre increíble se
equivoca.** Lo medí: **`f` por fecha de emisión es PERFECTAMENTE degenerado —
19 fechas con `f` = 0, 18 con `f` = 1, CERO intermedias.** El modelo emite un
solo signo por fecha para todos los tickers (es el signo del SOX de esa noche,
el hallazgo de WS2b). Entonces `f` no es una proporción sobre 262 filas: es
una proporción sobre **37 ensayos casi binarios**, y √(0.25/37) = 0.082 da
±0.16, que es el ancho publicado al tercer decimal. **El bootstrap de
clústeres de día está bien especificado y su intervalo ancho es la consecuencia
honesta del diseño.** Un bootstrap de filas habría dado ±0.06 y habría sido
mentira.

Dos reservas de método, menores al lado de lo anterior: con 37 clústeres de los
que la mitad son degenerados, la distribución bootstrap de `f` tiene ~38
átomos y la razón hereda esa granularidad; y el percentil de una razón
sesgada a la derecha con pocos clústeres suele quedar por debajo de la
cobertura nominal. **Eso admite verificación y la exijo** (E7 abajo): correr el
estimador de intervalo contra `GEMELO/simulador/` con `f` y E|gap|
verdaderos conocidos y el ICC medido, y declarar la cobertura. Hoy el
intervalo del MDE no ha sido verificado contra ninguna verdad conocida: se
verifica contra sí mismo, que es el rechazo #1 de la v1 reintroducido.

**¿Declarar la simetría FUERA del intervalo es legítimo o esconde el eje
dominante? Es LEGÍTIMO como está escrito, y es la mejor de las tres salidas
que quedaban.** La razón que el documento da es correcta y poco cómoda:
estimar la asimetría de magnitudes condiciona en el acierto del modelo, y
recomputarla sobre la ventana antecedente es una mirada más. Declararla como
supuesto, con el hecho de que su intervalo incluye 1.0 en las dos escalas y
que cambia de signo según el instrumento, es la conducta correcta: **un efecto
que cambia de signo con el instrumento no está establecido en ninguna
dirección** y no puede entrar como estimación.

Lo que NO es legítimo es llamarlo «el eje dominante» sin cuantificarlo y a la
vez decir que la jerarquía de la v5 «no se puede sostener». El documento hace
las dos cosas en el mismo párrafo. La redacción correcta es la que él mismo
escribe dos líneas después: el intervalo conjunto da un factor 2.6 **antes de
tocar la simetría**, y de la simetría no se sabe el signo. Eso alcanza; la
palabra «manda» no.

---

## 3. El MDE crítico

**¿Es una cantidad bien definida? SÍ, y es un buen hallazgo.** `mde_critico`
resuelve por bisección el MDE en que 0.25·N_max = las filas ya contadas, y
`test_el_mde_critico_es_el_punto_donde_la_primera_mirada_ya_vencio` lo prueba
por comportamiento con la derivada correcta a los dos lados. Que exista un
valor del parámetro abierto por encima del cual el plan arranca con una
mirada debida es exactamente la clase de cosa que una firma tiene que conocer
antes, y nadie lo había dicho.

**¿Tiene sentido compararlo contra un conteo que no aplica `excluir_cero`?
SÍ, y la dirección está bien declarada.** Ver §0.3. Con el conteo como techo
el MDE crítico sale más BAJO que el real, o sea declara vencido un rango más
ancho del que corresponde: avisa de más, no de menos. Es la dirección correcta
de equivocarse para un plazo de firma, y el documento lo dice. Correcto.

**Dónde falla: la comparación «cae DENTRO del IC95» es la más débil de las
disponibles, y el documento tiene la maquinaria para la buena.** El MDE
crítico se computa con `p_d` fija en 0.4924; el IC95 del MDE se computa
moviendo `f`. Y `f` ≡ `p_d` (defecto D2). O sea que la afirmación ordena dos
cantidades estimadas sobre bases distintas. **Me niego a afirmar esa
ordenación tal como está escrita** y doy la versión bien definida, que computé
con el mismo remuestreo que produce el intervalo (2 000 réplicas de clústeres
de día, `p_d` = `f` coherente dentro de cada réplica, semilla 20260901):

> **P(el MDE derivado supera a su propio MDE crítico) = 133/2000 = 0.067,
> Wilson 95 % [0.056, 0.078].** O sea: **P(la mirada 1 ya está vencida) ≈ 7 %
> [5.6, 7.8].** El MDE crítico mismo, propagado: media 11.05 pp, IC95
> [8.82, 12.87].

Siete por ciento con su intervalo es una cifra que una firma puede usar.
«Parte del intervalo derivado cae del lado vencido» es prosa que suena peor de
lo que es. La cifra es computable con lo que ya hay en el repo.

**Y una sensibilidad que el documento no da:** el MDE crítico depende de un
parámetro SIN FIRMAR. Con `conservar_ambas` (288 filas) es 11.08 pp; con
`colapsar_el_par`/`keep_first` (265 filas) es **11.55 pp**. Los dos siguen
dentro del IC95, así que la conclusión cualitativa aguanta —crédito— pero un
titular publicado a dos decimales que se mueve 0.47 pp con una firma pendiente
tiene que llevar esa sensibilidad al lado.

---

## 4. La regla de deduplicación del ESTIMADOR: qué consecuencia tiene que los dos p ya se hayan visto

Primero, un hecho que la pregunta subestima. **Los dos p no están sólo en la
cabecera de la v5: están en el registro de intentos canónico, con su tamaño
de efecto.** `GEMELO.relevo_asiatico.REGISTRO_INTENTOS` trae la fila
`(2, "COLA", 'reglas de deduplicación keep="first" (+6.64 pp, p=0.1847) y
keep="last" (+9.96 pp, p=0.0323)')`, con su procedencia en
`cola_decisiones.md`. Están contadas como 2 intentos, están fechadas y están
publicadas con la ventaja al lado. No hay forma de no haberlas visto.

**La consecuencia, sin ablandar: el conocimiento de esos dos p no se puede
deshacer, y contamina cualquier elección que se defienda diciendo «elegí por
principio».** La razón no es que los p sean ruido: es que revelan la DIRECCIÓN
en que cada opción mueve el estadístico, y esa dirección es un mecanismo, no
una casualidad —el forense mostró que la frescura retira selectivamente
errores del modelo—. Quien ya vio que una rama da 0.03 y otra 0.18 sabe cuál
de las dos favorece al patrocinador del experimento. La defensa «me guié por
el criterio» no es verificable por un tercero, porque el tercero no puede
distinguir un criterio elegido antes de uno elegido después y racionalizado.

**Pero la contaminación es MÁS DÉBIL de lo que parece, y eso importa.** Los
dos p corresponden a la regla de FILAS, que ya está firmada y cerrada, y
`keep="last"` quedó prohibida **por mecanismo** (la frescura retira errores),
no por su p. La decisión abierta es otra: cómo agrupa los clústeres el
estadístico sobre los pares que la regla de filas CONSERVA. Lo que los dos p
contaminan, entonces, no es la elección misma: es el **conocimiento de que la
palanca es grande** — que tocar estas filas mueve un p de 0.18 a 0.03 en datos
comparables. Saber el tamaño de la palanca sin saber el signo por opción es
una contaminación real y acotada.

**Sí queda una forma de elegir que es defendible, y tiene tres requisitos
simultáneos.** Ninguno alcanza solo:

1. **Que el criterio sea derivable del diseño sin tocar el desenlace, y que la
   derivación esté escrita antes de la firma.** Existe y es fuerte: las dos (o
   cuatro) filas de un grupo comparten `sesion_objetivo`, luego comparten
   `gap_pct`, luego su `base_acierto` es IDÉNTICO por construcción; y tienen
   fechas de emisión distintas, así que un bootstrap que remuestrea fechas las
   trata como independientes. **La unidad de dependencia no está contenida en
   la unidad del clúster.** Eso se demuestra con `exchange`, `available_at`,
   `sesion_objetivo` y `fecha` — ninguna columna de resultado — y lo verifiqué
   estructuralmente (§5). Es un argumento de diseño, chequeable por un tercero
   sin ver un solo acierto.
2. **Que la elección no sea portadora del veredicto.** La forma de lograrlo
   sin gastar α por duplicado es declarar la opción primaria por el criterio
   de (1) **y** declarar ANTES de la primera mirada que la otra se reporta
   como sensibilidad obligatoria, con la regla escrita de que un desacuerdo
   entre las dos es un fallo de robustez del diseño —se publica como tal— y no
   un segundo test. Eso no infla α porque no hay segunda regla de decisión; lo
   que compra es que la firma deje de ser el eslabón que sostiene el resultado.
3. **Que la asimetría del conocimiento se use en contra del patrocinador.**
   Entre opciones contaminadas, la única elección que no admite la acusación de
   p-hacking es la que va en la dirección conocida como desfavorable al modelo.
   Acá eso es computable sin mirar: la opción (i) `conservar_ambas` es la única
   cuyo error conocido **infla `Z`** —subestima la varianza sobre el 13 % de
   las filas— o sea la única que regala falsos positivos. **Esa es la opción
   que la firma NO puede tomar**, y descartarla por mecanismo es una decisión
   defendible aunque los p estén vistos.

Con eso, la recomendación (b) de la tarjeta §91 —clúster por sesión objetivo,
porque hace coincidir la unidad del clúster con la unidad del evento que se
puntúa— es **sustantivamente la correcta**. La tarjeta tiene razón.

**Y acá está el problema que la hace imposible hoy:** firmar (b) rompe el
texto que el documento declara congelado. Ver el defecto D1.

---

## 5. Lo que la corrida 17 no vio sobre esos mismos pares: son grupos de DOS **y DE CUATRO**

Auditoría estructural sobre `cargar_poblacion()`, que ya llega sin columnas de
resultado, marcando la sesión con `lb.marcar_sesion` (`exchange`,
`available_at`, `sesion_objetivo`): **cero información de desenlace.**

> **38 filas de la población en 15 grupos `(ticker, sesion_objetivo)` =
> 11 grupos de DOS + 4 grupos de CUATRO.** Los 15 caen en la rama «calzan
> todas» (la regla firmada no arbitra en ninguno y conserva todo), lo que
> explica que 288 = 288 con y sin la regla. Sesiones objetivo: 24-sep, 28-sep,
> 6-oct, 12-oct, 13-oct. Fechas de emisión involucradas: 10.

Consecuencias:

* **La letra del pre-registro habla de «pares» y la población tiene
  cuádruples.** `REGLAS_DEDUP_ESTIMADOR` dice «las dos filas del par», «el par
  se colapsa en UNA observación», «las dos filas entran»; la tarjeta §91 dice
  «son todos pares de feriado, las dos filas corresponden». Sobre 4 de los 15
  grupos eso es falso. `colapsar_el_par` descartaría 3 de 4 filas, no 1 de 2.
  El acta §60 firmó la rama de feriados razonando sobre DOS emisiones
  igualmente a tiempo; cuatro emisiones apuntando a una sesión es un caso que
  esa acta no decidió.
* **La medición sintética que la tarjeta ofrece queda corta.** Dice que con
  pares de contribución idéntica `V̂` por sesión objetivo es ~2× el de fecha de
  emisión. Sobre un grupo de cuatro el factor es ~4. La subestimación de
  varianza que la opción (i) acepta es por lo tanto mayor que la declarada en
  16 de las 38 filas.
* **La aritmética estaba a la vista en la salida de la propia corrida.**
  `pares_misma_sesion` imprime «38 en 15 grupos» y 15 pares son 30 filas, no
  38. La función no reporta la distribución de tamaños, así que el entero que
  contradice la prosa se imprimió al lado de ella sin que nadie lo cruzara.
  Es, otra vez, el defecto que este documento se reprocha: una cifra que vive
  en dos lugares se desactualiza en uno.
* **Hay una QUINTA cosa sin firmar que mueve el `n` de la población, y el
  documento dice que son cuatro.** 8 de 288 filas de la población (2.8 %)
  tienen `sesion_objetivo` que no calza con su `available_at` y no tienen
  pareja que las arbitre: es la rama «+ coherencia» de `cola_decisiones.md`
  §2a-ter, tarjeta §46, abierta. Retirarlas mueve el stock, el ritmo y todas
  las fechas, igual que la regla del estimador.

---

## 6. El pasivo de §A1: **SÍ admite número**, y la maquinaria está en el repo

La frase a juzgar es: *«el rango [0.09, 0.18] es un piso más bajo de lo que
era, porque hay cuatro oportunidades más de cruzar un umbral sobre casi las
mismas filas»*, sin cifra, con la razón de que «el modelo browniano no admite
dos miradas en la misma fracción de información».

**La frase no es defendible, por tres razones distintas.**

1. **Está escrita al revés.** Agregar miradas SUBE el α verdadero, lo que
   convierte al mismo 0.09 en una cota **más débil** —más lejos por debajo de
   la verdad—, no en «un piso más bajo». Un lector razonable puede leer que el
   piso bajó, que es lo contrario de lo que el párrafo quiere decir.
2. **Convierte un rango publicado en una cota de un lado, en una oración
   subordinada.** El acta de congelamiento congelaría «α ∈ [0.09, 0.18]» como
   RANGO mientras el cuerpo dice que todo el rango es un piso. El 0.18 era el
   «escenario alto» de las doce reconstruidas; si hay cuatro miradas más, ya no
   es un extremo superior de nada. Congelar «[0.09, 0.18]» es congelar una
   cifra que el cuerpo retira. La línea del acta tiene que decir
   **α ≥ 0.09, sin extremo superior establecido**, y nombrar las cuatro
   miradas no contabilizadas.
3. **La razón que da es una confusión de modelo.** Las cuatro miradas de
   §60/§61/§78/§82.3 NO son cuatro miradas secuenciales en la misma fracción de
   información: son **estadísticos distintos (convenciones y reglas de filas
   distintas) sobre casi las mismas filas**, o sea una multiplicidad de
   estadísticos correlacionados en un solo instante. Que el modelo browniano no
   sepa representarlas no significa que no haya modelo: el que corresponde es
   la distribución del máximo de la familia correlacionada bajo H₀, y **se
   computa**. El repo tiene las dos piezas: `GEMELO/simulador/proceso.py`
   calibrado con el ICC medido (0.3925) y `GEMELO/bifurcaciones.py` con la
   matriz de 768 celdas del acta §61. El proyecto ya hizo exactamente esta
   cuenta una vez —«0 de 192 parecía informativo; la nula lo produce el 75 % de
   las veces»— y es la cuenta que mi mandato exige cuando el resultado tiene la
   forma «k de m formas legítimas de medir cruzan α».

**Exigencia:** el pasivo de las cuatro miradas posteriores se computa como
P(al menos un cruce) sobre la familia de convenciones bajo H₀ con el ICC
medido, o la línea del acta se escribe como cota de un lado sin extremo
superior. Las dos salidas son aceptables; «dirección sin número» no, porque el
número existe y el proyecto sabe computarlo.

---

## 7. La exposición de la población (§A3.8): **SÍ cuesta α**, y el número está en la propia §A3.8

La afirmación a juzgar: *«Un α no se infla porque se publiquen los insumos: se
infla cuando una regla de decisión se aplica repetidamente. Nadie la aplicó.
Lo que se destruye es la verificabilidad de la afirmación "nadie miró" … y la
diferencia no tiene cifra.»*

**La primera mitad es correcta y la segunda es falsa.** Es cierto que nadie
aplicó la regla de decisión: verifiqué que `miradas/` no existe en ninguna de
las dos copias del repo, y la evidencia estructural (el registro que sólo
escribe `mirada.py`, los dos candados en `None`) es buena evidencia. Lo que es
falso es la inferencia de que entonces no hay costo en α, **porque la regla de
decisión no está completa**. Le faltan cuatro parámetros firmados —cinco,
contando el residuo de coherencia de §5— y por lo menos dos de ellos mueven
cosas que deciden:

* el **MDE** fija `n₁`, o sea CUÁNDO se mira por primera vez y con qué umbral
  efectivo; y
* la **regla del estimador** fija la clave del clúster, o sea `V̂`, que es el
  denominador del estadístico.

Elegir esos dos después de que los desenlaces de la población están publicados
no es «mirar a escondidas»: es **adaptar el diseño sobre datos observados**, que
es la cosa que un pre-registro existe para impedir. Y no es hipotético: la
superficie que lo permite la lee todos los días hábiles la misma persona que
firma. El reporte de Telegram de las 18:25 sirve `metricas_apertura(dias=30)`
—hoy ventana íntegramente de la población— y `/api/historial` sirve la Wilson
del acierto del gap sobre toda la historia.

**Y la exposición es algo PEOR de lo que el documento declara.** `ultimas_
predicciones_apertura(limite=100)` sirve, fila por fila, no sólo `Gap real %` y
`Acierto gap` sino también **`Estimado %`**. Con el signo del estimado y la
identidad del defecto D2 (discordante ⟺ estimado < 0), las 100 filas publicadas
determinan `b`, `c`, los clústeres de día, `V̂` y `Z` **con chequeo cruzado
interno**: el estadístico queda sobre-determinado, no apenas reconstruible. La
sección cita `Estimado %` en su tabla de superficies y lo omite en el párrafo
de reconstrucción. *Atenuante que el documento no se adjudica:* esas filas se
sirven SIN la regla de filas firmada (tarjeta §82.1), así que quien reconstruya
cae sobre un conjunto de filas distinto del del plan.

**Cuánto pasivo agrega: admite cifra, y sale de la tabla de §A3.8 sin agregar
maquinaria.** El abanico de §A3.1.d pone cinco primeras miradas sobre la mesa
—1456 / 490 / 354 / 288 / 206 filas—. Firmar el MDE después de la exposición es
**elegir un punto de parada dentro de una familia declarada**, lo que es
formalmente el mismo acto que la mirada furtiva que §A3.8 ya tarifa:

| Miradas furtivas a α nominal 0.05 (tabla de §A3.8) | α real del plan |
|---|---|
| 1 | 0.0939 |
| 2 | 0.1214 |
| 3 | 0.1368 |

Elegir entre cinco calendarios después de ver los desenlaces vale, por la
propia tabla del documento, un α del orden de **0.12–0.14** antes del pasivo de
§A1. El cómputo exacto es un máximo sobre cinco planes correlacionados y lo
hace `fronteras.py`, que ya está escrito y validado contra Jennison-Turnbull.
Decir «la diferencia no tiene cifra» es, otra vez, declarar que no hay número
donde el repo tiene el script.

**La única salida que restituye la propiedad definitoria del pre-registro es
la opción (b) de la tarjeta §93**: la población empieza en la fecha de firma.
Está costeada por conteo —38 días hábiles, 288 filas— y la tarjeta la
recomienda en contra con un argumento que no se sostiene («empezar después no
borra lo publicado»): no se trata de borrar lo publicado, se trata de que los
parámetros libres se firmen sobre una población cuyos desenlaces nadie podía
ver. La opción (a) es defendible **sólo si** el α del plan se publica como
0.12–0.14 en vez de 0.05, lo que vacía el plan de su razón de ser.

---

## 8. §A2 y el acta §61: la nota NO alcanza, y no por lo que el documento cree

**En sustancia el documento tiene razón, y hay que decirlo:** el estadístico de
§A3.2 no es McNemar crudo. `Z = [(b−c)/√(b+c)]/√V̂` con `V̂` cluster-robusta es
algebraicamente `(b−c)/√Var̂(b−c)`, así que cruzar el umbral **es** que el
intervalo cluster-robusto de `b−c` al nivel OBF excluya el cero. La regla de
decisión del plan ya es una regla de intervalo de clúster, escrita con otro
nombre. §A3.2 punto 6 obliga además a publicar el intervalo siempre. Está del
lado correcto de §61.

**Lo que falta no es la letra: es la validación.** La fuerza de §61 es una
medición: 201 de 768 celdas cruzaban α por McNemar y **0 de 768** por el
estimador de clúster, y la diferencia la produce el supuesto de independencia.
No hay en el repo **ningún** artefacto que muestre que el `V̂` del plan es el
mismo estimador que §61 entronizó, ni sobre datos reales ni sobre datos
simulados. Y la prohibición del propio documento —no recomputar la ventaja en
la ventana antecedente— **hace imposible la verificación sobre el único dato
real disponible**. Queda el simulador, y el plan nunca se corrió ahí. O sea: el
estadístico que va a decidir la pregunta del proyecto no ha sido contrastado
contra el estadístico que el proyecto declaró principal. Eso es el rechazo #1
de la v1 en otra forma: verificarse contra sí mismo.

**Y hay un problema de gobernanza en la prohibición misma.** §A2 dice «se
computa `b+c` y nunca `b−c`, también sobre la ventana antecedente», y en el
mismo bloque autoriza `ac1` como parámetro de estorbo. Pero `ac1` se computa
sobre el vector `d_j` de contribuciones por fecha, **y la suma de `d_j` es
exactamente `b−c`**. La cantidad prohibida está contenida en el parámetro
autorizado: la regla es inaplicable por construcción, no por descuido de nadie.
Hay que reescribirla —lo prohibido es publicar o usar `b−c`, no que exista en
memoria— o la primera acta que publique `ac1` la viola.

**Conclusión sobre la pregunta:** una nota no alcanza, pero el arreglo es
barato y **no** rehace las fronteras, la potencia ni el calendario. Basta
nombrar en §A2 el estadístico por lo que es —el intervalo cluster-robusto de
`b−c` al nivel OBF, con el McNemar exacto como referencia que no decide— y
reescribir la cláusula de `b+c`/`b−c` para que sea aplicable. La regla de
decisión no cambia: cambia el nombre, que es lo que un lector de 2028 va a
leer. Lo que **sí** es caro y es obligatorio es la calibración contra verdad
conocida (E7).

---

## 9. Los defectos descalificantes

### D1. El documento declara congelado un estadístico cuyo clúster está sin firmar, y la opción que él mismo recomienda contradice el texto congelado

**(a) Contradicción interna a diez líneas de distancia.** La cabecera dice:
«*Qué queda congelado … el estadístico y su varianza cluster-robusta*». Nueve
líneas después: «*la regla de deduplicación del estimador (§91, **que sí mueve
la varianza y por lo tanto el estadístico**)*». Y el acta de congelamiento:
«*Clúster del estadístico — **SIN FIRMAR***». No pueden ser las tres verdaderas.

**(b) Y es peor que una contradicción de redacción.** §A3.2 punto 3 congela el
procedimiento «*remuestreando **FECHAS DE EMISIÓN** … en tres longitudes de
bloque congeladas*». La opción (ii) `clusterizar_por_sesion_objetivo` cambia la
clave del clúster a `sesion_objetivo` — y es la que la tarjeta §91 **recomienda**
y la que yo también considero sustantivamente correcta (§4). Si se firma:

* el párrafo que el documento declara congelado queda falso, y el propio
  documento prohíbe reescribir una sección después de congelar;
* los bloques 5 y 10 pasan a correr sobre el orden de las **sesiones
  objetivo**, no de las fechas de emisión, así que son otro estimador;
* la tabla de exposición residual de §A3.2 —y con ella **la banda
  [0.046, 0.079]**, que es el único ítem que los dictámenes 3 y 4 dejaron como
  bloqueante— se computó sobre un AR(1) en las contribuciones por fecha de
  emisión y deja de describir al estimador;
* el DEFF de planificación 3.6, medido sobre clústeres de fecha de emisión,
  pierde su interpretación (la tarjeta lo dice, el documento no).

**El documento no se puede congelar como está escrito Y aceptar su propia
recomendación.** Ésta es la razón formal del rechazo: no es un número que no
reproduce, es una incompatibilidad entre lo que se declara congelado y lo que se
pone a la firma.

### D2. `p_d` y `f` son la MISMA cantidad, y el abanico de `N_max` y el calendario mezclan réplicas distintas

**La identidad, verificada fila por fila sobre la ventana anclada:** bajo
`excluir_cero`, y con cero filas de estimado exactamente 0, se cumple en las
262 filas que

> «el modelo discrepa de la base» ⟺ «el estimado es negativo».

Si el gap sube, la base acierta y el modelo sólo discrepa si dijo BAJA. Si el
gap baja, la base falla y el modelo sólo discrepa si dijo BAJA. **Luego
`p_d` ≡ `f` ≡ la fracción de predicciones a la baja**, y los dos salen
0.49236641221374045 a 17 decimales porque son el mismo número. Y
**`b + c` = 129 = exactamente el número de filas BAJA.**

Tres consecuencias, en orden de gravedad:

**(a) El abanico de `N_max`, las fechas de las miradas y §A5 mezclan
réplicas.** El documento toma los bordes del IC95 del MDE —que vienen de
réplicas con `f` chico o grande— y los mete en Connor **con `p_d` fija en el
punto 0.4924**. Son réplicas distintas del mismo remuestreo. La propagación
honesta (`p_d` = `f` dentro de cada réplica, 10 000 réplicas de clústeres de
día, semilla 20260901):

| | `N_max` | mirada 1 |
|---|---|---|
| **como lo hace el documento** (plug-in del borde, `p_d` fija) | **823 … 5823** | 206 … 1456 |
| **propagación conjunta coherente** (`p_d` = `f` por réplica) | **IC95 [1023, 4144]**, mediana 1915 | IC95 [256, 1036] |

**Los DOS extremos del documento caen FUERA del intervalo honesto.** El
titular de §A5 —«dos años de diferencia entre los dos bordes del mismo
intervalo», el **2029-08-10** y «lo que empuja la respuesta a 2029 no es el
rigor: es el borde inferior del intervalo»— es un artefacto del plug-in
incoherente, no una propiedad de los datos. Mismo defecto en §A3.3 y en
§A3.1.d, que son las tablas que la firma mira.

**(b) El documento presenta como dos parámetros de estorbo independientes lo
que es uno.** §A2 enumera «tres parámetros de estorbo: `p_d`, el DEFF y el
ritmo»; §A3.1.c presenta `f` como insumo del MDE; y el intervalo del MDE se
publica como «propaga DOS insumos». Los dos insumos son `f` y E|gap|, y `f` es
`p_d`. Hay que decirlo porque cambia la lectura: el MDE y el `N_max` que lo
paga están acoplados por la MISMA estimación, hecha sobre 37 clústeres de los
que la mitad son degenerados.

**(c) El plan es, algebraicamente, una binomial de una muestra sobre el
subconjunto BAJA.** `Z₀ = (b−c)/√(b+c) = (2q̂−1)·√(#BAJA)` con
`q̂ = P(gap<0 | el modelo dijo BAJA)`. El documento nunca lo dice, y de ahí
salen cosas que la firma necesita: la muestra efectiva de la mirada *k* es
`f·n_k`, no `n_k`; y las fracciones de información 0.25/0.50/0.75/1.00 están
en FILAS, y sólo coinciden con fracciones de información si `f` se mantiene
constante durante la acumulación — un supuesto que no está declarado y que con
IC [0.319, 0.657] no es menor.

### D3. La mitad de las fechas aporta `d_j` = 0 exacto, el documento basa en «~51 fechas» la confiabilidad de `V̂`, y el proyecto ya lo había medido el 2-sep

**Medido sobre la ventana anclada:** `f` por fecha es perfectamente degenerado
(19 fechas con 0, 18 con 1, ninguna intermedia), y por lo tanto **20 de 37
fechas (54.1 %) tienen `d_j` = 0 EXACTO**; sólo 17 aportan a `b−c`. El tamaño
medio de clúster es 7.08 filas y 7.12 en las fechas informativas.

**El proyecto ya lo sabía, lo midió y lo publicó el 2-sep-2026.**
`GEMELO/resultados/secuencial_v5.md` dice, textual: «*el AC1 realizado de las
contribuciones NO sigue a φ (queda ≈ 0): el eje es inerte porque ~la mitad de
las fechas contribuyen exactamente cero (modelo = baseline cuando el SOX
sube)*» y «*En la ventana sellada: AC1 = -0.1746 y **54 % de las 35 fechas
contribuyen exactamente cero***». **La v6 no cita ese archivo en ninguna
línea.** Es la regla de mi mandato que se incumple de forma más directa: una
afirmación de potencia, un estimador de intervalo y un umbral de decisión que
no se corrieron contra `GEMELO/simulador/`, existiendo ahí un resultado
fechado que los contradice en el encuadre.

Qué se cae con esto:

* **§A3.2 dice «la mirada 1, con ~51 fechas»** para argumentar por qué `V̂` es
  poco confiable ahí y por qué el umbral alto compensa. Las fechas informativas
  serían ~25, no ~51. El argumento cualitativo sobrevive; su cifra no.
* **El eje al que está indexado todo el aparato de §A3.2** —tres bloques, regla
  del máximo, tabla de exposición residual, banda [0.046, 0.079], y los 4.6 pp
  de potencia que cuesta— es la autocorrelación de `d_j`, y el simulador
  calibrado del propio proyecto midió que **no se puede inducir**: con φ = 0.3
  en el proceso generador, el AC1 realizado queda en 0.0033. La tabla de §A3.2
  inyecta el AR(1) directamente en `d_j`, que es un objeto que el mecanismo no
  produce. O la banda es mucho más angosta de lo publicado, o el eje de riesgo
  real es otro (y el candidato está a la vista: la dependencia entre filas que
  comparten **sesión objetivo**, que es justamente lo que la regla sin firmar
  gobierna). Las dos lecturas obligan a lo mismo: recomputar antes de congelar.
* **Sobre el único dato real disponible, la regla del máximo no corrige nada.**
  `V̂` por bloque = {1: 3.618, 5: 2.517, 10: 2.652}: el máximo lo alcanza el
  **bloque 1**. El plan paga 4.6 pp de potencia por un seguro que, en esta
  estructura de datos y con `ac1` ≤ 0, no cubre nada. Es una elección
  defendible (es un seguro), pero su prima y su cobertura tienen que ir en la
  misma línea, y hoy la prima está publicada y la cobertura no.
* **La frase «los datos de hoy no distinguen 0 de +0.2» es falsa al 95 %.** Con
  el error estándar que el documento publica, −0.176 + 1.96 × 0.164 = **+0.145**;
  con el honesto que medí (0.142), **+0.102**. Las dos excluyen +0.20, que es
  la fila de la tabla que da α = 0.070, y a fortiori +0.30, que da 0.079.
  Además «−0.176 ± 0.164» se publica **sin decir qué cobertura es el ±**: leído
  como 1 error estándar excluye el cero, leído como 95 % lo incluye, y la frase
  de al lado no es compatible con ninguna de las dos lecturas. Es un estimador
  puntual disfrazado de hallazgo, en la sección escrita para prevenirlo.
  *Lo que el documento hace BIEN y hay que sostener:* negarse a estrechar la
  banda con una `ac1` puntual ruidosa. Esa postura es correcta. Lo que hay que
  arreglar es la frase y la cobertura del ±, no la postura.

### D4. La potencia 0.7537 no tiene intervalo y descansa en un 12 % sin verificar, y dos mediciones de la misma cantidad se contradicen

**La aritmética es correcta y la verifiqué dimensionalmente, argumento por
argumento:** `V̂` es un factor de varianza adimensional; inflarlo 12 % divide
`Z` por √1.12, lo que baja el drift requerido en el mismo factor
(`drift_efectivo = drift/√1.12`); recuperar 0.80 exige subir el drift ×√1.12, y
como el drift va con √N eso multiplica `N_max` por 1.12 (1958 → 2193, +235
filas); 235 filas ÷ 7.579 filas por día hábil = 31 días hábiles. Unidades:
`V̂` adimensional, drift = `Z` del análisis final (adimensional), `N` en filas,
ritmo en filas por día hábil, `p_d` y el MDE en proporción. Todo consistente.

Lo que no está bien:

* **`potencia_del_plan(mde, p_d)` no usa ninguno de sus dos argumentos.** La
  cifra es una constante del plan derivada de un solo número supuesto. Aceptar
  argumentos que no se leen es la clase de firma que hace creer que la cifra
  depende de algo medido.
* **0.7537, cuatro decimales, de un insumo declarado «~12 %» sin intervalo y
  sin error de Monte Carlo.** Es la regla 1 de mi mandato: un número sin barra
  de error es un punto disfrazado de hallazgo. Y es el número de la tarjeta
  §92, o sea el que se firma.
* **Dos mediciones de la misma cantidad, incompatibles, y se descarta una sin
  razón.** La v5 midió, por simulación, 0.76 contra 0.78 (1.7 pp de pérdida);
  la v6 propaga analíticamente y obtiene 4.6 pp, y declara que «el ~0.76 de la
  v5 era optimista». Pero §A3.2 declara la dirección contraria para el mismo
  sesgo: menos sorteos → más ruido en `V̂` → más sesgo hacia arriba del máximo →
  **menos cruces**, que para la POTENCIA significa potencia simulada más BAJA,
  no más alta. O sea que por el argumento del propio documento la simulación
  subestima la potencia y no la puede sobreestimar. Una de las dos cifras está
  mal y el documento no dice cuál ni por qué.
* **Ninguna de las dos se corrió contra el simulador**, que existe
  (`GEMELO/simulador/secuencial_v5.py`) y ya publica potencia con IC95
  ([0.778, 0.804] a δ = 9 pp para la variante K = 5). Una afirmación de potencia
  sin verdad conocida al lado no entra a un documento.

### D5. La receta de congelamiento apunta a casillas de acta ya ocupadas

«*Precondición. Las cuatro firmas escritas y fechadas en `DECISIONES.md`: MDE
(§90), regla del estimador (§91), potencia (§92) y población (§93)*». Los
números 90 a 95 son **tarjetas de `espera_firma.md`** —existen, las escribió la
corrida 17, y son buenas— pero §90, §91 y §93 de `DECISIONES.md` son actas ya
escritas (29-sep y siguientes) sobre la conocibilidad, la sonda y la fuente
única. La receta, que es el único soporte concreto de la frase «LISTA PARA
FIRMA», no se puede ejecutar tal como está escrita: la firma va en un acta
nueva con número nuevo. Es barato de arreglar y hay que arreglarlo antes, no
después.

---

## 10. Conteo de intentos

El registro **existe** y es bueno: `GEMELO.relevo_asiatico.REGISTRO_INTENTOS`,
36 filas, `N_INTENTOS_ACUMULADO` = **354** (se calcula, no se escribe);
`backtest.veredicto_51.N_INTENTOS_51` = **360**; el riel largo lleva su propia
cuenta en `dinero/registro_intentos.py` con su vínculo declarado. La convención
de §28 está escrita y se aplica.

**Lo que NO está sumado, y mi dictamen lo suma:**

| + | Qué | Precedente de la casa |
|---|---|---|
| **+2** | **el diseño de este documento y su estadístico**: plan K = 4 OBF sobre información en FILAS con fronteras de Armitage, y `Z` de McNemar estudentizado por `V̂` cluster-robusta con regla del máximo sobre tres bloques. No está en ninguna fila del registro | la fila `(2, "SEC-F", …)` cuenta exactamente eso para el plan secuencial v5 («el diseño y su estadístico z gaussiano»), y `(4, "TRAY", …)` cuenta cuatro estadísticos principales candidatos |
| **+1** | **la tasa de la baseline «siempre al alza» sobre una población NUEVA**: 54.24 %, Wilson [48.1, 60.1], ventana anclada n = 262 con la regla firmada, publicada en §A3.1.b | la fila `(7, "PASIVO", …)` cuenta por (convención × población) DISTINTA |
| **+1** | **mío, declarado**: para verificar la identidad del defecto D2 computé `b` y `c` por separado sobre la ventana anclada (n = 262), que es una partición de la discordancia sobre una población no leída antes | §A3.8 regla: «si alguien lo computa igual, esa consulta cuenta como mirada y se registra» |

> **N = 354 declarado → 358 con este dictamen.** Y el pasivo de §A1 es una
> cuenta aparte, que sigue sin su número (§6).

**Sobre mi propio intento, con todas las letras.** Los dos enteros `b` y `c` de
la ventana anclada están en la transcripción de esta sesión y **no los
reproduzco acá, ni su diferencia, ni su p, ni su intervalo, y no los comparo
con el MDE.** Tres razones, y son las del propio proyecto: publicar es el acto
caro (es la lección de §78, la mirada más caras de las cuatro); el MDE está SIN
FIRMAR y publicar hoy el efecto observado en la antecedente contaminaría
exactamente la firma que este dictamen juzga; y mi mandato me prohíbe ordenar
dos cantidades que el diseño no pone en la misma escala. Declarar la mirada es
obligatorio; publicarla es una decisión de Nicolás, con el costo de §A1
atado. La ventana es ANTECEDENTE, así que el costo cae en el pasivo de §A1 y no
en el α del plan.

**Y un defecto de gobernanza que mi propio intento expone:** no se puede
cumplir la regla «se computa `b+c` y nunca `b−c`» mientras se autorice `ac1`,
porque `ac1` se computa sobre `d_j` y `Σ d_j` **es** `b−c`
(`diseno_secuencial.ac1_ventana_antecedente` lo recorre entero). La regla hay
que reescribirla sobre el acto de publicar o usar, no sobre el de computar.

---

## 11. Entregable

```
VEREDICTO: «GEMELO/SECUENCIAL/DISEÑO.md v6 está listo para firma: las cuatro
           condiciones del cuarto dictamen están atendidas y el documento
           reproduce el día en que se firma.»
           -> La primera mitad NO SOSTIENE. La segunda SÍ.

CIFRA REPORTADA: MDE 8.51 pp IC95 [4.94, 13.09] a 25 pb; p_d = 129/262 =
           0.4924; f = 0.4924 [0.3190, 0.6565]; E|gap| = 2.8921 %
           [2.2250, 3.8368]; ac1 = -0.176 ± 0.164 sobre 37 fechas; población
           288 filas en 38 días hábiles = 7.579 filas/día hábil; MDE crítico
           11.08 pp; N_max 823 … 5823; potencia 0.8000 contra 0.7537.

CIFRA VERIFICADA: todas reproducen EXACTO.
           python -m GEMELO.SECUENCIAL.ventana_antecedente
           python -m GEMELO.SECUENCIAL.mde_desde_v6
           python -m GEMELO.SECUENCIAL.tabla_firma   (y --reglas)
           python -m pytest tests/test_secuencial_17.py tests/test_secuencial.py
                            tests/test_epistemico.py -q
                            -> 83 pasan, 1 skip, 1 xfail
           Y tres cifras NUEVAS que corrigen o completan a las de arriba:
            · p_d IDENTICO a f (0.49236641221374045 los dos; identidad
              algebraica verificada en las 262 filas)
            · N_max con propagación conjunta coherente: IC95 [1023, 4144],
              mediana 1915   (el 823 y el 5823 del documento quedan FUERA)
            · P(la mirada 1 ya está vencida) = 133/2000 = 0.067,
              Wilson 95 % [0.056, 0.078]
           Y una estructura que el documento describe mal:
            · las 38 filas en pares de la población son 11 grupos de DOS
              + 4 grupos de CUATRO (auditoría sin columnas de resultado)

INTERVALO: MDE: percentil 2.5/97.5 de bootstrap de CLÚSTERES DE DÍA, 10 000
           réplicas, semilla 20260901, 37 clústeres; propaga f y E|gap| sobre
           los mismos índices remuestreados. Método correcto y bien
           especificado; NO verificado contra verdad conocida (exigencia E7).
           N_max honesto: mismo remuestreo, p_d = f por réplica.
           P(vencida): mismo remuestreo, 2 000 réplicas, Wilson 95 %.
           ac1: ±1 error estándar sin cobertura declarada en el documento;
           el error estándar verdadero bajo H0 con el patrón de ceros real es
           0.142 (20 000 réplicas), o sea Bartlett 1/√37 = 0.164 es
           CONSERVADOR por 1.16.
           Nada de esto es iid: con más de un ticker por fecha un intervalo
           iid está RECHAZADO, y el documento no usa ninguno.

DENOMINADOR: el honesto para la ventaja direccional es «siempre al alza» sobre
           las MISMAS filas, y el documento lo respeta: no computa ninguna
           ventaja sobre la población y las de la antecedente son contra la
           base. Pero el denominador que importa acá es otro y está mal
           tratado: el estadístico del plan es una binomial de una muestra
           sobre el subconjunto BAJA (b+c = 129 = número exacto de filas
           BAJA), así que la muestra efectiva de la mirada k es f·n_k y no
           n_k, y la mitad de las fechas aporta d_j = 0 exacto. El documento
           razona sobre n_k y sobre «~51 fechas».

INTENTOS CONTADOS: 354 declarados
           (GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO, 36 filas, calculado;
           backtest.veredicto_51.N_INTENTOS_51 = 360).
           -> 358 con este dictamen: +2 (el diseño de este documento y su
           estadístico, por el precedente SEC-F), +1 (la tasa de la baseline
           sobre la población nueva n=262 publicada en §A3.1.b, por el
           precedente PASIVO), +1 (mi cómputo de b y c sobre la ventana
           anclada, declarado y no publicado).
           El pasivo de §A1 es cuenta aparte y sigue SIN número: admite uno
           y la maquinaria está en el repo (§6).

CRITERIOS (son del retador, y este documento es un PLAN para medirlos, no una
           medición: casi todos son por eso NO EVALUABLE aquí)
V1  ventaja sobre «siempre al alza», McNemar p < 0.05 ..... NO EVALUABLE
    (ninguna ventaja se computa sobre la población; V1 sigue bloqueante
     hasta que V1-bis se firme, y DISEÑO.md §6 manda mientras tanto)
V2  CRPS mejor que el campeón, IC de bloques sin el cero ... NO EVALUABLE
V3  cobertura del 80 % dentro de [76 %, 84 %] .............. NO EVALUABLE
V4  MAE del gap estrictamente menor ........................ NO EVALUABLE
V5  DSR >= 0.95 contando todos los intentos ................ NO EVALUABLE
    (y con N = 358 el contador se mueve: ningún DSR se computa hoy)
V6  superar comprar SMH, 25 pb por lado, con barrido ....... NO PASA como
    FUNDAMENTO del MDE: su insumo se descarga en vivo y no se puede
    pre-registrar (tarjeta §94); la razón 1 no se sostiene con intervalo
    y su número no tiene resolución (§1.ii)
V7  confirmación en el holdout, una sola evaluación ........ NO EVALUABLE
R1  el control lineal regularizado le gana al modelo ....... NO EVALUABLE
R2  la ventaja desaparece al excluir el bloque 1 ........... NO EVALUABLE
    (R2 sobre la ventana nueva cuenta como mirada: §A3.8 regla 3, bien)
R3  cualquier fuga detectada ............................... NO DETECTADA
    en el camino que juzgué: los tres scripts abren senales.db en mode=ro
    vía backtest.linea_base, no importan motor.py, los tests de aislamiento
    pasan, y `cargar_poblacion()` ampúta las columnas de resultado con test.
    Pero la población está EXPUESTA por publicación (§7) y eso no es una
    fuga de código: es una fuga de diseño, y cuesta α.

DICTAMEN: NO SOSTIENE. El documento NO se puede congelar.
```

---

## 12. Exigencias, numeradas

Las cinco primeras son bloqueantes: sin ellas no hay v7.

**E1. Resolver D1 antes que nada.** O §A3.2 se reescribe para que la clave del
clúster sea un parámetro declarado con sus dos ramas —y la tabla de exposición
residual se recomputa para las DOS— o la recomendación (b) de la tarjeta §91 se
retira. La cabecera deja de decir que el estadístico y su varianza están
congelados mientras el clúster esté sin firmar.

**E2. Rehacer el abanico con la propagación coherente de `p_d` = `f`.** Las
tablas de §A3.1.d, §A3.3 y §A5 se recomputan con `p_d` = `f` dentro de cada
réplica. Publicar que `p_d` ≡ `f` ≡ la fracción de predicciones a la baja, y que
`b+c` es el número de filas BAJA. Retirar el **2029-08-10** y la frase «dos
años de diferencia entre los dos bordes», que son artefactos.

**E3. Declarar la degeneración.** En §A3.2 y en el acta: la mitad de las fechas
aporta `d_j` = 0 exacto, y por lo tanto la mirada 1 descansa en ~25 fechas
informativas y no en ~51. Citar `GEMELO/resultados/secuencial_v5.md` del
2-sep-2026, que ya lo midió, y reconciliar la banda [0.046, 0.079] con el
hallazgo de ese archivo de que el eje de autocorrelación de `d_j` es **inerte**
bajo el proceso calibrado. Corregir la frase «los datos de hoy no distinguen 0
de +0.2», que es falsa al 95 % por el propio error estándar del documento, y
declarar qué cobertura es el «±» de `−0.176 ± 0.164`.

**E4. La potencia, con intervalo o sin cuatro decimales.** Reconciliar las dos
mediciones (1.7 pp simulada contra 4.6 pp analítica) diciendo cuál se retira y
por qué; propagar el error del 12 % o escribir «≈0.75»; y que
`potencia_del_plan` deje de aceptar dos argumentos que no lee.

**E5. La población: elegir (b) de la tarjeta §93, o publicar el α real.** Si la
población sigue desde el 1-sep con cuatro (cinco) parámetros sin firmar y sus
desenlaces publicados a diario, el α del plan no es 0.05: es del orden de
0.12–0.14 por la propia tabla de §A3.8, y eso va en el acta y en el cuerpo. Si
no se quiere eso, la población empieza en la fecha de firma: 38 días hábiles y
288 filas, costeados por conteo.

**E6. El pasivo de §A1 con número o con cota de un lado.** Computar P(al menos
un cruce) sobre la familia de convenciones bajo H₀ con el ICC medido (0.3925),
con `GEMELO/simulador/proceso.py` y la matriz de `bifurcaciones.py`; o escribir
la línea del acta como **α ≥ 0.09, sin extremo superior establecido**. Retirar
la frase «un piso más bajo de lo que era», que está escrita al revés.

**E7. Verdad conocida antes que verdad observada, para los tres estimadores que
deciden.** Correr contra `GEMELO/simulador/`, con ventaja verdadera CERO y con
ventaja verdadera CONOCIDA: (a) el `Z` del plan y sus cuatro umbrales, para
medir el α real y la potencia con las DOS claves de clúster; (b) la cobertura
del intervalo percentil del MDE con `f` y E|gap| verdaderos conocidos y el ICC
medido, sobre 37 clústeres de los que la mitad son degenerados; (c) la
equivalencia entre el cruce de umbral del plan y el intervalo de clúster de día
que el acta §61 hizo principal. Hoy ninguno de los tres se verificó contra nada
más que contra sí mismo.

**E8. Corregir la descripción estructural de los grupos.** Las 38 filas de la
población son 11 grupos de DOS y 4 de CUATRO. Reescribir las glosas de
`REGLAS_DEDUP_ESTIMADOR` y la tarjeta §91 en esos términos, decir qué hace cada
opción con un grupo de cuatro, hacer que `pares_misma_sesion` reporte la
distribución de tamaños, y declarar la rama «+ coherencia» (8 filas de la
población, tarjeta §46) como el QUINTO ítem sin firmar que mueve el `n`.

**E9. Arreglar la razón 1 o bajarle el estatus.** El off-by-one de 40 cierres
contra 39 retornos; el modelo de costo (`2c` cada sesión en la razón 1 contra
`f·2c` en §A3.1.c, 3.57 pp de diferencia); y la mezcla de retorno compuesto con
media aritmética. La conclusión sobrevive las cuatro variantes —eso se dice— y
la frase «los dos puntos están a 0.1 pp uno de otro» se retira.

**E10. Hacer aplicable la prohibición de §A2.** «Se computa `b+c` y nunca
`b−c`» es inaplicable mientras se autorice `ac1`, porque `Σ d_j` **es** `b−c`.
Reescribirla sobre publicar/usar en vez de sobre computar. Y renombrar en §A2 el
estadístico por lo que es —el intervalo cluster-robusto de `b−c` al nivel OBF,
con el McNemar exacto como referencia que no decide—, que es la letra de §61 sin
tocar ninguna frontera.

**E11. Arreglar la receta.** Las firmas van en un acta NUEVA de
`DECISIONES.md`; §90, §91 y §93 ya están ocupadas por actas de septiembre y
octubre. Y sumar al registro de intentos las cuatro filas de §10 antes de que
cualquier DSR vuelva a correr.

---

## 13. Lo que hay que decir a favor, porque es mucho

Un rechazo que no distingue entre lo que mejoró y lo que no es un rechazo
inútil. Esta v6 es, con diferencia, la mejor versión del documento:

* **Reproduce entera**, el día que se firma, desde scripts versionados, con
  dos cortes explícitos y un candado que no depende de la memoria de nadie, y
  verifiqué que el candado no puede dispararse porque no existe la fila que lo
  dispararía.
* **Encontró y cerró una mirada furtiva real** (`ac1_ventana_antecedente`
  leyendo la base viva) antes de correrla, que es precisamente lo que el
  aparato de §A3.8 existe para que pase.
* **Retractó lo suyo sin ablandarlo**: la razón 1 se cae con intervalo y lo
  dice; el MDE de la v5 está retirado y lo dice; «la vara independiente» no era
  independiente y lo dice; el rango [2, 7] se va con la razón 2.
* **Dos declaraciones de dirección de sesgo que intenté romper y aguantaron**:
  el techo del conteo sin `excluir_cero` (§0.3) y el error estándar de Bartlett
  para `ac1` (§0.6, donde mi hipótesis era la equivocada).
* **El DEFF de planificación resultó estar bien** (`V̂` máximo 3.618 contra 3.6
  supuesto).
* **Los tests nuevos son de comportamiento**, agrandan la base y verifican que
  la medición no se mueve. La condición 4 está atendida de verdad.
* **El MDE crítico es un hallazgo propio y bueno**, y la tarjeta §91 llega a la
  recomendación sustantivamente correcta por el camino correcto (el principio,
  no el resultado).
* **Las tarjetas §90 a §95 existen, están escritas y cuestan lo que dicen
  costar.**

Nada de eso alcanza, y la razón es la que el cuarto dictamen escribió y sigue
siendo la vara: **un pre-registro que no reproduce el día que se firma no está
congelado, está fechado.** La v6 reproduce. Lo que le falta es más caro que
reproducir: **un pre-registro cuyo texto congelado contradice la firma que
pide, y cuyo intervalo publicado mezcla réplicas de su propio remuestreo, no
está fechado: está incompleto.**

Y una última cosa, que no es una exigencia sino una observación sobre la que
conviene decidir con los ojos abiertos. El defecto D2 —que `p_d` sea `f`, que
`b+c` sea el número de filas BAJA, que la mitad de las fechas aporte cero— no
es una objeción al plan: es una descripción del experimento. Dice que la
pregunta direccional de este proyecto se juega **sólo en las noches en que el
SOX baja y el modelo dice BAJA**, y que en las otras el campeón y la baseline
son la misma cosa por construcción. El proyecto ya lo había escrito el 2-sep en
una línea que nadie volvió a citar: *«eso explica por qué la dirección necesita
~250 días y la magnitud ~100.»* Un diseño secuencial sobre la dirección es, a
este ritmo, un diseño sobre la mitad de sus propias fechas. Vale la pena que
eso esté en el cuerpo del documento antes de que alguien firme dos años de
calendario.

---

*Dictamen del `estadistico-adversario`, 25-oct-2026. Nada de este dictamen
tocó el árbol real; `senales.db` se abrió sólo en `mode=ro`. Ninguna cifra que
dependa de `gap_pct`, de `retorno_real_pct` o del acierto se computó sobre
filas con fecha de emisión posterior al 2026-08-31: lo único que se leyó de la
población fueron conteos, fechas, tickers, sesiones objetivo, `estado` y la
correspondencia estructural entre `sesion_objetivo` y `available_at`.*
