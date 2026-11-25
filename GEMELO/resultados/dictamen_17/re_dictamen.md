# Re-dictamen del `estadistico-adversario` — el delta de la segunda pasada

**25-oct-2026, 22:35 UTC.** Una sola pasada, sobre el mismo worktree `wt17`.
**Esto es un delta: no re-litigo nada de lo que ya juzgué** en
`estadistico_adversario.md` (977 líneas, intacto: lo verifiqué). Verifico
cada «ATENDIDA», busco defectos **nuevos** introducidos por las
correcciones, y juzgo si el documento describe su propio estado con
honestidad. **E6 y E7 no se revisan**, por instrucción.

**VEREDICTO DEL DELTA: sigue RECHAZADO, y el rechazo se estrechó mucho.**
Seis exigencias quedaron atendidas de verdad y una de ellas (E8) está
cerrada sin reservas. Pero **la corrección de E2 no llegó a tres copias de
su propia afirmación, ni al script, ni al artefacto sellado**; **E1 sigue
incompatible en el texto normativo**, que es la pregunta que el coordinador
hace; y **esta ronda introdujo cuatro defectos nuevos**, uno de ellos un
test tautológico dentro de la función que E4 venía a arreglar.

---

## 1. Verificación de cada «ATENDIDA»

### E2 — se declara ATENDIDA; está **ATENDIDA EN PARTE**

**El cómputo reproduce EXACTO**, y es mejor de lo que pedí:

```
python -c "from GEMELO.SECUENCIAL import tabla_firma as T; T.propagacion_conjunta()"
  réplicas útiles 10000 · n_boot 10000 · semilla 20260901 · clústeres 37
  N_max mediana 1915.4   IC95 [1023, 4144]
  t=0.25  n mediana  478.8  IC95 [ 256, 1036]  fecha de la mediana 2026-11-27
  t=0.50  n mediana  957.7  IC95 [ 511, 2072]  fecha de la mediana 2027-02-24
  t=0.75  n mediana 1436.5  IC95 [ 767, 3108]  fecha de la mediana 2027-05-24
  t=1.00  n mediana 1915.4  IC95 [1023, 4144]  fecha de la mediana 2027-08-19
  P(mirada 1 ya vencida) = 0.0625
```

Coincide fila por fila con mi propia propagación independiente, y el 0.0625
cae dentro del Wilson [0.056, 0.078] que yo medí sobre 2.000 réplicas.
`mde_desde_v6.replicas()` es la pieza correcta y su filtro es inocuo (verifiqué
que la condición de Connor `p_d > δ²` nunca puede binder acá: δ² = f²k² con
k ≈ 0.173, así que `f·k² < 1` siempre).

**§A3.1.d y §A5 quedaron ejemplares.** §A5 en particular: «(1) el rango
HONESTO» primero, «(2) la respuesta CONDICIONAL» después, con la retractación
escrita y la razón del artefacto. Es la mejor sección del documento.

**Y la identidad `p_d ≡ f` quedó publicada con su derivación** en §A2 («la
baseline siempre dice al alza, así que el modelo sólo puede discordar donde
dice BAJA»). Eso era la mitad conceptual de D2 y está bien hecho.

**Pero la corrección no llegó a tres copias de la misma afirmación, y una de
ellas es la que el documento llama «el hallazgo que hay que decir con todas
las letras»:**

1. **`DISEÑO.md`:1050-1051, punto 3 de §A3.1.d** — a **cuarenta líneas** de su
   propia retractación, dice textual: «*Lo que empuja lejos es el **borde
   inferior** del intervalo, que lleva el final a 2029. La tensión es entre el
   punto y su propio intervalo*». Eso **es** «dos años de diferencia entre los
   dos bordes», reinstalado. La línea 1012 de la misma subsección declara que
   el 5.823 y el 2029-08-10 «quedan **RETIRADOS como intervalo**» y que «no son
   bordes de nada». Las dos no pueden ser verdaderas.
2. **`DISEÑO.md`:1338-1342, la tabla de §A3.3** — sigue etiquetando las filas
   «4.94 pp (**borde inferior del IC95**)» → `N_max` 5.823 y «13.09 pp (**borde
   superior del IC95**)» → 823, sin marca CONDICIONAL y sin referencia al
   [1.023, 4.144]. Y la nota de abajo sigue diciendo «*Ahora el abanico es el
   **intervalo** del MDE completo*», que es exactamente el encuadre retirado.
3. **La fila E2 de la tabla de estado** (`DISEÑO.md`:2043) dice «**Las dos
   frases retiradas**». El artefacto la contradice en los dos puntos de arriba.

**Es, letra por letra, el defecto que el propio documento narra sobre sí mismo
en §A3.1.a**: la ERRATA del 1-sep corrigió «cinco sesiones» a «cuatro» y «la
corrección no alcanzó a esta copia», doce líneas más abajo, durante dos meses.
Acá son cuarenta líneas y el mismo día.

### E8 — **ATENDIDA, sin reservas.** Es la exigencia mejor cerrada

```
pares_misma_sesion(cargar_poblacion()):
  filas_en_pares 38 · grupos 15 · reparto_por_tamano {2: 11, 4: 4} · grupo_mas_grande 4
tests/test_secuencial_17.py:367  assert r["reparto_por_tamano"] == {2: 1, 4: 1}
```

El test planta un grupo de dos y uno de cuatro: es de comportamiento y falla si
la función vuelve a mentir. El quinto ítem sin firmar («+ coherencia», 8 de 288)
está declarado. Y la observación de que el acta §60 razonó sobre DOS emisiones y
no decidió el caso de cuatro está escrita. Nada que objetar.

### E4 — se declara ATENDIDA EN PARTE; lo está, pero **es cosmética en el único
lugar que se firma**, y la ronda introdujo dos defectos nuevos acá

**Lo que sí está hecho, y con test real:**

```
inspect.signature(T.potencia_del_plan) == ()      # ya no acepta lo que no lee
T.potencia_del_plan(0.10, 0.49)  ->  TypeError     # tests/test_secuencial_17.py:424
```

**Lo que no:** el `0.7537` de cuatro decimales **sigue circulando desde tres
lugares versionados**, y el primero es el que se firma:

| Dónde | Qué dice |
|---|---|
| **`DISEÑO.md`:286 — la fila «Potencia» del ACTA DE CONGELAMIENTO** | «0.80 con la varianza conocida, **0.7537** descontando el sesgo de la regla del máximo» |
| `tabla_firma.markdown()`:314 | `f"**{p['potencia_con_regla_del_maximo']:.4f}**"` → imprime **0.7537** |
| `GEMELO/resultados/tabla_firma_17.json` (sellado) | `potencia_con_regla_del_maximo: 0.7537…` |

El cuerpo cita «≈0.75»; **el acta, que es la tabla que Nicolás firma y que
alguien lee en 2028, sigue diciendo 0.7537.** Mismo patrón en la fila «MDE» del
acta (`:285`), que sigue diciendo «el **MDE crítico de 11.08 pp cae dentro del
intervalo**» —la ordenación que me negué a afirmar— **sin** el IC [8.92, 12.79]
y **sin** el P(vencida) que §A3.1.d ya tiene. El cuerpo se arregló; las filas
del acta no.

### E10 — **ATENDIDA la prohibición, y bien**

§A2 pasa a «**se PUBLICA y se USA `b+c`, nunca `b−c`**», con mi argumento
escrito entero (`Σ d_j` **es** `b−c`, así que prohibir computarla y autorizar
`ac1` era una contradicción) y con la razón correcta de por qué la prohibición
exigible es sobre publicar y usar: «*que es donde está el costo en α*». No
renombrar el estadístico es **defendible** y está bien argumentado: toca la
sección que el acta propone congelar y mi propia exigencia pedía además una
validación que no existe. Queda en §97 con su costo. Correcto.

### E9 — **ATENDIDA bajándole el estatus, y es la salida correcta**

La frase «los dos puntos están a 0.1 pp uno de otro» está retirada y los tres
defectos de resolución quedan declarados con sus magnitudes (0.08 pp el
off-by-one, 3.57 pp el modelo de costo, y la mezcla compuesto/aritmético). Que
la conclusión sobreviva las cuatro variantes está dicho. No arreglar el cómputo
y mandarlo a §94 es proporcionado: la razón 1 ya no sostiene nada.

### E11 — **ATENDIDA**

La receta manda las firmas a un acta NUEVA y declara que §90/§91/§93 de
`DECISIONES.md` están ocupadas por actas de sept-oct. Las cuatro filas del
registro (354 → **358**) van al acta de cierre. Verifiqué que las tarjetas
§90-§97 existen en `espera_firma.md` y que los números de acta que colisionaban
están nombrados como tales.

### E1 — se declara ATENDIDA EN PARTE; lo está, y **la parte que falta es la
que importa**. Respuesta directa a tu pregunta: **SÍ, sigue incompatible**

La cabecera y el acta están corregidas: ya no dicen congelado «el estadístico y
su varianza» sino «**la FORMA del estadístico**», la fila «Clúster del
estadístico» sigue en SIN FIRMAR, y mi D1 está escrito entero en la cabecera
(bloques 5 y 10, DEFF, banda). Esa mitad está bien.

**Pero el texto normativo no se tocó.** `DISEÑO.md`:1094-1100, dentro del bloque
encabezado «*Lo que se pre-registra en cambio es la **fórmula**, no el valor*»,
el punto 3 sigue diciendo, en mayúsculas:

> «`V̂ₖ` … se re-estima con los datos de esa mirada, **remuestreando FECHAS DE
> EMISIÓN** con `backtest.inferencia._remuestrear_circular` … en tres
> longitudes de bloque congeladas»

Y no hay nota adjacente: verifiqué el bloque entero y el apartado que le sigue.
**Un lector del punto 3 lee que la clave del clúster es parte de la fórmula
pre-registrada, que es lo contrario de lo que la cabecera aclara.** La
aclaración vive en la cabecera y la norma vive en §A3.2; manda la norma.

Y la incompatibilidad con §91 es la misma que señalé: la opción que la tarjeta
**recomienda** (y que yo también considero sustantivamente correcta) pone la
clave en `sesion_objetivo`. Firmarla deja falso el punto 3.

**El arreglo mínimo no toca ninguna frontera, ni el α, ni la futilidad, ni el
calendario** —ninguno depende de la clave—: en el punto 3, sustituir «FECHAS DE
EMISIÓN» por «los CLÚSTERES que define `REGLA_DEDUP_ESTIMADOR` (SIN FIRMAR,
tarjeta §91; hoy `fecha` de emisión o `sesion_objetivo`)», decir que las tres
longitudes de bloque se definen sobre el orden de la clave que se firme, y
declarar que la tabla de exposición de §A3.2 se computó **sólo** para la clave
por fecha de emisión. Con eso E1 queda atendida salvo la corrida de §97.

### E3 — **ATENDIDA EN PARTE, y el auto-reporte es exacto**

Verifiqué lo declarativo en §A3.2:1216-1225: la degeneración (20 de 37 fechas
con `d_j` = 0, ~25 informativas y no ~51), la cita de `secuencial_v5.md` del
2-sep con sus dos frases, el eje medido como **inerte**, y `V̂` por bloque
{1: **3.618**, 5: 2.517, 10: 2.652} con el máximo en el bloque 1. La frase falsa
está corregida (+0.145 al 95 %) y la cobertura del ± declarada como error
estándar. Falta reconciliar la banda, y está en §97. Bien.

### E5 — **ATENDIDA como declaración.** El cambio de recomendación es
**correcto**, y la premisa es más fuerte de lo que hace falta

§A3.8 publica el α del orden de 0.12–0.14 con el razonamiento completo, declara
que el valor exacto no está computado, y agrega lo del `Estimado %` y la
sobre-determinación con su atenuante (§82.1). Todo correcto.

**Sobre tu preocupación por haber cambiado la recomendación de §93 sobre una
cifra mía que es «del orden de» y no exacta: el cambio es defendible y lo
sostengo.** La recomendación no depende del valor: depende de un hecho
cualitativo que es seguro —elegir el MDE de una familia declarada de cinco
después de que los desenlaces están publicados hace α estrictamente mayor que
0.05, y por la propia tarifa de §A3.8 ya **una** selección equivalente lo pone
en **0.0939**—. Y el argumento que la tarjeta agrega es el mejor de la ronda:
«*elegir (a) hoy es hacer por omisión, y peor, lo que entonces se rechazó por
decisión*», más la salida que yo no había escrito y que es la correcta: «*la
alternativa honesta a (b) no es (a) a secas: es (a) con «α 0,12–0,14» escrito en
el acta de congelamiento y en el cuerpo*».

**Lo único que pido acá** es que la premisa se escriba en su forma débil, para
que la recomendación no se caiga si E5 se computa y da 0.11: «α > 0.0939 ya con
UNA selección equivalente, por la tabla de §A3.8, y del orden de 0.12–0.14 con
las cinco; el exacto no está computado». Así la recomendación queda robusta a
su propio cómputo pendiente.

---

## 2. Defectos NUEVOS que introdujeron las correcciones

### N1. El documento se arregló; **el script y el artefacto sellado no**

`tabla_firma.tabla()` **no incluye** la propagación conjunta
(claves: `deff_planificacion, factor_secuencial, filas, hoy, mde,
mde_critico_dentro_del_ic, mde_critico_ic_pp, mde_critico_pp, p_d, potencia,
ritmo`), `markdown()` **no menciona** «CONDICIONAL», ni `1023`, ni `4144`, ni
`0.0625`, ni la palabra «propagación» —lo verifiqué por búsqueda sobre la
cadena que produce—, y no hay flag de CLI que la exponga (`--json`, `--reglas`,
`--sellar`). Correr hoy

```bash
python -m GEMELO.SECUENCIAL.tabla_firma
```

—el script cuyo docstring dice «*la tabla que Nicolás necesita para firmar el
MDE*» y al que §A3.1.d remite— imprime **el abanico mal emparejado como tabla
titular, sin marca CONDICIONAL, con el 2029-08-10 adentro**, y debajo el
`0.7537`. Y **`GEMELO/resultados/tabla_firma_17.json`**, sellado a
`2026-10-25T21:55:44+00:00` y citado en la cabecera como «su instante
declarado», **no contiene ni la propagación conjunta ni `p_mirada1_vencida`**:
el artefacto que sella la mitad-calendario del documento sella la versión
retirada.

Es el defecto que el documento se reprocha —«una tabla que vive en dos lugares
se desactualiza en uno»— con los papeles invertidos, y en la dirección peor: el
texto se corrigió y la **fuente citada** quedó con el encuadre retirado.

### N2. El «13 a 92 días hábiles» de §A3.3 es una cifra **nueva** construida
sobre el emparejamiento retirado

`DISEÑO.md`:1402-1404 agrega: «*El costo NO es parejo entre MDE … va de **13
días hábiles** con el borde superior del intervalo a **92** con el borde
inferior*». Los dos números salen de los dos extremos del plug-in:

```
0.12 × 823/7.579  = 13.0 días hábiles      <- plug-in, "no es borde de nada"
0.12 × 5823/7.579 = 92.2 días hábiles      <- plug-in, "no es borde de nada"
0.12 × 1023/7.579 = 16.2                   <- honesto (IC inferior de N_max)
0.12 × 4144/7.579 = 65.6                   <- honesto (IC superior de N_max)
```

El rango honesto es **16 a 66 días hábiles**. La ronda que retiró el
emparejamiento publicó, en otra sección, un número nuevo derivado de él, con un
error de un factor 1.4 en los dos extremos.

### N3. `FACTOR_SECUENCIAL = 1.0241` **ya no reproduce desde el script del
propio repo**, y la potencia idealizada no es 0.80

```
drift del plan, computado hoy por diseno_secuencial.drift_para_potencia ... 2.8383
drift de muestra fija  norm_ppf(0.975)+norm_ppf(0.80) ...................... 2.8016
factor en N implicado = (2.8383/2.8016)^2 .................................. 1.02638
FACTOR_SECUENCIAL cableado en tabla_firma.py ............................... 1.02410
drift que implica el cableado .............................................. 2.8351
potencia REAL con el N_max que da el factor cableado ....................... 0.7991
```

`DISEÑO.md`:1335 dice «el factor **1.0241** (drift requerido 2.8352…)» y
`:1346` «*Con eso la potencia del plan es **0.80 exacta***». Con el factor
cableado la potencia idealizada es **0.7991**. La magnitud es trivial (0.09 pp);
**la clase no lo es**: es una constante de pre-registro que el script versionado
del mismo repo contradice, que es literalmente la vara del cuarto dictamen. Y
es el parámetro que E4 venía a auditar.

### N4. El test de potencia es **TAUTOLÓGICO**, y por eso N3 es invisible

`potencia_del_plan()` despeja el drift que da 0.80 y después evalúa la potencia
**en ese mismo drift**:

```python
drift = D.drift_para_potencia(malla, umbrales, objetivo=0.80)
ideal, _ = D.potencia_secuencial(malla, umbrales, drift)   # == 0.800001, por construcción
```

`potencia_idealizada` es 0.80 **por construcción**, independiente de
`FACTOR_SECUENCIAL`, de `N_max`, de `p_d` y del MDE. El test
`test_la_potencia_con_la_regla_del_maximo_es_menor_que_la_idealizada` afirma
`potencia_idealizada ≈ 0.80 (abs=5e-3)`: **no puede fallar**, y lo que prueba es
que la bisección converge. Es el defecto **N8 del tercer dictamen** («cuatro
tests tautológicos») reintroducido dentro de la función que E4 arreglaba.

El test no tautológico es el que acabo de correr: evaluar la potencia en el
drift que `FACTOR_SECUENCIAL` **compra** y exigir 0.80. Hoy da 0.7991 y falla.

### N5. Dos cifras nuevas sin test, y una sin intervalo

* **`propagacion_conjunta` no tiene ningún test** (búsqueda en `tests/`: cero
  apariciones), y `mde_critico_ic_pp` tampoco. Son las dos cifras que esta ronda
  produjo y las dos que el documento ahora publica como titulares. El test
  obvio y de comportamiento es el que fija la afirmación publicada: que los
  extremos del plug-in (823 y 5.823) caen **fuera** de `n_max_ic`. Sin él, la
  frase «los dos extremos caen fuera del intervalo honesto» es prosa que nada
  sujeta.
* **`P(la primera mirada ya está vencida hoy) = 0.0625` se publica desnuda**, en
  el mismo párrafo que acaba de argumentar —correctamente, y citando al
  `curador-epistemico`— que «*un umbral sin intervalo, en el documento cuya
  lección es que no se publica un punto sin intervalo, era el error en el sitio
  escrito para prevenirlo*». Es una proporción sobre 10.000 réplicas: Wilson
  95 % **[0.0579, 0.0674]**. Y su nombre promete más de lo que es: si está
  vencida o no es una función determinista del MDE **firmado**, que no está
  firmado; lo que 0.0625 mide es la fracción de remuestreos de los días de la
  ventana antecedente en que el MDE derivado dejaría la mirada 1 debida. La
  frase correcta lleva «si se firma la regla del punto derivado».

### N6. Dos filas de la tabla de estado se auto-reportan de más

* Fila **E2**: «Las dos frases retiradas». No: sobreviven en §A3.1.d punto 3 y
  en la tabla de §A3.3 (N2/§1).
* Fila **E6**: «la línea del acta pasa a «PISO, **sin extremo superior
  establecido**»». La frase «sin extremo superior» aparece **sólo en esa fila**:
  la línea del acta (`:288`) dice «**PISO: α ∈ [0.09, 0.18]** … Se propone
  congelar como PISO, no como el pasivo». Es una mejora real —ya no congela el
  rango *como el pasivo*— pero sigue publicando un intervalo donde pedí una
  cota de un lado, y el auto-reporte declara hecho lo que no está escrito.

### Lo que verifiqué y NO introdujo defecto

* **El intervalo del MDE crítico es un acierto propio de la ronda**, no mío:
  [8.92, 12.79] reproduce mi [8.82, 12.87] dentro del ruido de Monte Carlo, y el
  párrafo que lo acompaña está **mejor ordenado que mi exigencia**: «cuál de las
  opciones arranca vencida está **indeterminado** entre 8.92 y 12.79 pp», y sólo
  afirma la ordenación donde el diseño la soporta («por encima de 12.79 la
  mirada 1 está vencida para TODO el intervalo de `f`»). Eso es exactamente
  cómo se escribe una comparación entre cantidades que el diseño no ordena.
* **Los dos efectos «de unas décimas en direcciones opuestas» son correctos y
  están cuantificados**, y los verifiqué: crítico con 283 filas (aplicando
  `excluir_cero`) = **11.18 pp**; con 288 = **11.08**; con 296 (una jornada
  hábil más) = **10.93**. Van en direcciones opuestas y son décimas. Y **no**
  contradicen la declaración de §A3.5 que ya había verificado: son cantidades
  distintas (el stock y el crítico, contra las fechas proyectadas).
* **La declaración de asimetría de reproducibilidad es una mejora que yo no
  había pedido** y es correcta: la mitad del documento que vive en la ventana
  antecedente reproduce porque está anclada; la mitad que vive en el calendario
  es una **medición puntual** que no reproduce mañana y no debe, y lo que
  necesita es su instante declarado. Eso está bien pensado — con la salvedad de
  que el instante sellado es el artefacto de N1.
* **Suite: 85 pasan, 1 skip, 1 xfail** (eran 83). Los dos tests nuevos que
  verifiqué son de comportamiento.
* **Mi dictamen anterior está intacto** (encabezado, 14 secciones, cierre).

---

## 3. ¿El documento describe su propio estado con honestidad?

**En lo esencial, SÍ, y con una franqueza que hay que registrar.** La cabecera
abre con «**versión 6 — NO CONGELADA. QUINTO RECHAZO**» antes que cualquier otra
cosa, dice que el rechazo era la condición del congelamiento y que por lo tanto
no se congela, resume mis tres defectos sin ablandarlos, declara que el
`curador-epistemico` rechazó además la primera redacción de esta misma v6 con
doce bloqueantes, y reproduce mi lista de verdes **incluida la que me contradice
a mí** (el error estándar de Bartlett resultó conservador después de que yo
apostara lo contrario). La tabla de estado de las once exigencias etiqueta
honestamente ATENDIDA EN PARTE en E1, E3, E4 y E5 y NO ATENDIDA en E6 y E7, con
el costo de cada una en su tarjeta.

**Las excepciones son dos filas de esa tabla (N6) y el acta.** La tabla de estado
sobre-reporta en E2 y E6; y **el acta de congelamiento —la única tabla que se
firma— se quedó atrás del cuerpo en dos filas**: «Potencia» sigue con 0.7537 y
«MDE» sigue con «el MDE crítico de 11.08 pp cae dentro del intervalo» sin su
intervalo ni su probabilidad. En un documento cuya tesis es que lo que vale es
lo que queda escrito para dentro de dos años, el acta es el peor lugar donde
dejar la versión vieja.

---

## 4. Respuestas directas a tus dos preguntas

**¿El abanico condicional sigue siendo una invitación a leerlo como
intervalo?** En §A3.1.d y en §A5, **no**: están bien construidas, el honesto va
primero, el condicional está rotulado, y la retractación es explícita. **Pero la
invitación sigue viva en tres sitios** y por una asimetría concreta: el abanico
condicional da **fechas** (2029-08-10, 2027-01-29) y el intervalo honesto da
**filas** ([1.023, 4.144]) y sólo la **fecha de la mediana**. Quien busque «¿cuán
largo puede salir el plan?» en una fecha encuentra únicamente la retirada.
**Publicá la fecha del borde superior honesto** (4.144 filas al ritmo medido) y
la invitación se cierra sola. Más: borrar el punto 3 de §A3.1.d y rotular la
tabla de §A3.3, que son los tres sitios de §1.

**¿La aclaración de E1 alcanza?** **No.** Mientras §A3.2 punto 3 diga
«remuestreando **FECHAS DE EMISIÓN**» dentro del bloque que el documento
presenta como la fórmula pre-registrada, el documento sigue siendo incompatible
con la recomendación de §91, y la aclaración de la cabecera no alcanza porque
manda la norma. El arreglo es de una frase y no toca ninguna frontera, ningún
umbral, la futilidad ni el calendario.

---

## 5. Exigencias del delta — mecánicas, todas, salvo la última

Ninguna pide una corrida de simulación. **E6 y E7 siguen abiertas y no se
cuentan acá.**

1. **F1.** Borrar el punto 3 de §A3.1.d, o reescribirlo sobre el intervalo
   honesto. Hoy reinstala lo que su propia subsección retira cuarenta líneas
   arriba.
2. **F2.** Rotular la tabla de §A3.3 como CONDICIONAL, quitarle «borde
   inferior/superior del IC95» a las dos filas de los extremos, y cambiar
   «*Ahora el abanico es el intervalo del MDE completo*».
3. **F3.** Recomputar el «13 a 92 días hábiles» sobre el IC honesto: **16 a 66**.
4. **F4.** Llevar la propagación conjunta y `p_mirada1_vencida` a `tabla()`, a
   `markdown()`, al `--json` y al JSON **sellado**; y que `markdown()` no
   imprima el abanico sin su rótulo ni la potencia con cuatro decimales.
5. **F5.** Actualizar las dos filas del acta: «Potencia» a ≈0.75 y «MDE» con el
   IC del crítico y el P(vencida). El acta es lo que se firma.
6. **F6.** Reconciliar `FACTOR_SECUENCIAL` con el drift que el script computa
   (1.02638, drift 2.8383) o declarar que la potencia idealizada del plan es
   **0.7991** y no «0.80 exacta».
7. **F7.** Reemplazar el test tautológico de potencia por el que evalúa la
   potencia en el drift que `FACTOR_SECUENCIAL` compra.
8. **F8.** Test de comportamiento para `propagacion_conjunta` que fije la
   afirmación publicada: 823 y 5.823 **fuera** de `n_max_ic`.
9. **F9.** `P(vencida)` con su Wilson **[0.0579, 0.0674]** y con el nombre
   condicionado a la regla del punto derivado.
10. **F10.** Corregir las dos filas sobre-reportadas de la tabla de estado (E2 y
    E6) y escribir la línea del acta del pasivo como **α ≥ 0.09**.
11. **F11.** §A3.2 punto 3: la clave del clúster pasa a ser el parámetro SIN
    FIRMAR que ya es en el acta, con la nota de que la tabla de exposición se
    computó sólo para la clave por fecha de emisión. **Es la única de las once
    que levanta un bloqueante** (D1), y sigue sin tocar ninguna frontera.

---

## 6. Conteo de intentos — sin cambios

**N = 354 declarado → 358** con las cuatro filas de mi dictamen anterior, que
esta ronda acepta y manda al acta de cierre. **Esta pasada no agrega intentos:**
todo lo que computé acá es propagación de parámetros de estorbo sobre la ventana
antecedente anclada (`f`, E|gap|, `N_max`, el crítico, la potencia) y conteos
estructurales sobre la población sin una sola columna de resultado. **No volví a
computar `b` ni `c`**, ni sobre la antecedente ni sobre la población, y sigo sin
publicar los dos enteros del dictamen anterior.

---

*Re-dictamen del `estadistico-adversario`, 25-oct-2026. No modifiqué ningún
archivo del proyecto. `senales.db` sólo en `mode=ro`. Ninguna cifra que dependa
de `gap_pct`, de `retorno_real_pct` o del acierto se computó sobre filas
emitidas después del 2026-08-31. No revisé E6, E7 ni el dictamen del
`curador-epistemico`.*
