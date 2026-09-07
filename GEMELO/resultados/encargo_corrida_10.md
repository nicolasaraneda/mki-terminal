# Encargo corrida 10: abrir el riel de dinero, la señal larga y la capa visual

Leé este archivo entero antes de ejecutar nada. Corrida nocturna sin supervisión; Nicolás revisa a la mañana. Nada se pushea: el push lo hace Nicolás después de leer el diff. Esta sesión NO dictamina: los dictámenes del guardián y del curador corren en una sesión aparte, con contexto limpio, leyendo `~/cierre.md`.

Esta corrida abre una línea nueva y hay que decir por qué. El proyecto construyó un instrumento que mide una noche: el cierre de Nueva York contra la apertura asiática, unas horas después. La intención original de Nicolás es otra y opera en semanas: reconocer un movimiento en un eslabón de la cadena de semiconductores antes de que se vea aguas abajo, y tomar posición con un presupuesto acotado. Las dos cosas son legítimas y no son la misma. Esta corrida las declara como dos rieles separados, y construye la maquinaria del segundo sin tocar nada del primero.

Restricción de realidad que ordena el diseño: el presupuesto inicial son 100 a 500 dólares y todavía no hay cuenta de corredora. Los papeles que el riel de medición predice están en Tokio, Taipéi y Seúl, con lotes mínimos que ese presupuesto no alcanza en la mayoría de los casos. El riel de dinero, entonces, opera sobre instrumentos listados en Estados Unidos. Eso no es una concesión: es la única forma en que el presupuesto y el horizonte encajan.

## 0. Orientación obligatoria

1. `orientador` reconstruye el estado. Orden de lectura: `ESTADO.md`, `GEMELO/resultados/estado_epistemico.md`, `espera_firma.md`, `cola_decisiones.md`, `bitacora_09.md`, `GEMELO/resultados/dictamen_09/`, y las actas 78 y 79 de `DECISIONES.md`.
2. Toda cifra se lee de la máquina (módulo árbitro o README renderizado), nunca de memoria ni de este archivo. Si este archivo y la máquina no coinciden, manda la máquina y se anota errata.
3. Suite completa antes de empezar; anotá el número. Si no está en verde, parás y reportás.
4. Ventana de sellado 17:50 a 20:30 hora de Chile en día hábil: nada pesado, y ninguna descarga. Si un frente cae ahí, se pausa.
5. El registro de intentos del DSR se incrementa por cada hipótesis probada esta noche, incluidas las descartadas. El bloque 6 declara cuántas va a probar antes de probarlas.
6. `director-programa` hace pre-mortem de este encargo antes del bloque 1 y deja escrito qué bloque considera más probable que falle y por qué. Si detecta que una instrucción de este archivo es ella misma un defecto, lo dice y no la ejecuta.

## 1. Límites duros

- No se tocan `motor.py`, `senales.py`, `snapshot.py`, `universo.py`, el modo de emisión, `.env` ni los timers. Lo que necesite tocarlos se entrega como `.diff` no aplicado con test y va a `espera_firma.md`.
- No se reescribe ninguna fila sellada. Errores históricos son erratas.
- Ninguna cifra publicada se mueve sola: si se mueve n, se mueven los doce bloques dependientes, o no se mueve.
- Ningún estimador puntual sin intervalo computado. Clúster de día o de semana según la unidad, siempre.
- Todo lo nuevo se etiqueta PROPUESTA hasta el dictamen de `estadistico-adversario`.
- Una verificación que usa el mismo mecanismo que produjo la cifra no es verificación.
- La corrección va al ejecutable antes que al texto.
- **Prohibido en esta corrida escribir código que envíe una orden real a una corredora, o que guarde credenciales de una.** Todo el riel de dinero es simulado. No hay cuenta abierta y no la va a haber esta noche.
- Todas las entradas del riel de dinero son datos públicos. Cualquier diseño que dependa de información no pública se rechaza y se anota por qué.

## 2. Bloque 0: la deuda que dejó la corrida 09

La suite toca la red: `motor._datos_crudos` llama a `yf.download` con caché sólo en memoria, y el hook la corrió a las 17:57 del 3 de septiembre, dentro de la ventana de sellado. El sello salió sano pero la regla se cruzó.

Marcá con un marcador de pytest los tests que tocan la red, y hacé que el hook de pre-commit se niegue a correrlos entre 17:50 y 20:30 de un día hábil, con un mensaje que diga qué regla está aplicando. Test de la guarda: que la guarda dispare con reloj falso dentro de la ventana y no dispare fuera. Acta corta en `DECISIONES.md`.

## 3. Bloque 1: el mapa de la cadena a instrumentos comprables

Objetivo: saber qué eslabón de la cadena de semiconductores se puede comprar de verdad desde Chile con 500 dólares, y qué eslabón no tiene representación.

Producí `docs/universo_operable.md` con una fila por eslabón. Los eslabones son: diseño de chips y software EDA, fabricación de vanguardia, memoria, litografía y equipamiento, materiales químicos y obleas, ensamblaje y prueba, materias primas y nodos maduros, y demanda final de IA y datacenter.

Para cada fila: qué empresa domina el eslabón, si cotiza en Estados Unidos y bajo qué forma (acción, ADR o ETF), el ticker, el precio de una acción al último cierre disponible, la comisión estimada de una orden mínima como fracción del monto invertido, y si el eslabón queda representado, sustituido o hueco.

Reglas de este bloque:

- Ningún ticker se escribe de memoria. Cada uno se verifica descargando al menos un precio con la fuente que el proyecto ya ingiere. El que no se pueda verificar no entra a la tabla: entra a una lista de no verificados con su razón.
- Los eslabones sin representación en Estados Unidos se declaran huecos explícitos. No se tapan con un sustituto. Donde haya sustituto, se escribe que es sustituto y en qué se diferencia del original.
- La empresa privada no es comprable. Si un eslabón está dominado por empresas que no cotizan, se dice y se lista a quién se le compra en su lugar.
- Salida ejecutable: un módulo nuevo, por ejemplo `dinero/universo_dinero.py`, con la lista y sus metadatos. **No toca `universo.py`.**

Al final del bloque, una frase con estatus evidencial: cuántos de los eslabones quedan cubiertos, cuántos sustituidos y cuántos huecos.

## 4. Bloque 2: el documento de visión

Producí `VISION.md` en la raíz (o actualizalo si ya existe; verificá primero con la máquina). Corto, menos de 120 líneas. Contenido obligatorio:

1. Qué persigue el proyecto en una frase, en los términos de Nicolás: una herramienta que reciba un presupuesto y tome decisiones de compra y venta cada vez más afinadas sobre la cadena de semiconductores.
2. Los dos rieles, declarados como separados:
   - **Riel de medición.** El gap asiático sellado. Horizonte de una noche. No mueve plata. Su función es demostrar que el proyecto puede emitir predicciones antes del hecho y medirse sin engañarse. Estado actual y su cifra, leída del árbitro.
   - **Riel de dinero.** Instrumentos listados en Estados Unidos, horizonte de semanas, presupuesto acotado. Estado actual: no existe todavía; esta corrida lo empieza.
3. Para cada riel: qué mide, en qué horizonte, contra qué vara, y **qué resultado lo mata**.
4. La pista de hardware, con su función real: plataforma de verificación y proyecto de Arquitectura de Computadores, no motor de backtesting ni ruta a microtrading. La ruta de latencia está medida y muerta desde casa: lo que la desbloquearía es colocación, no hardware.
5. La regla de legalidad: todas las entradas son públicas.
6. Qué NO es el proyecto: no es un vendedor, no promete retorno, y el monto inicial de plata real es costo de aprendizaje operativo, no una apuesta con retorno esperado positivo demostrado.

`curador-epistemico` juzga este documento en la sesión de cierre como texto publicado. Ninguna frase afirma más de lo que la cifra que la sostiene permite.

## 5. Bloque 3: la capa de decisión

Hoy el proyecto predice y mide, y no tiene nada que convierta una predicción en una orden. Esa es la pieza faltante.

Módulo nuevo bajo `dinero/`, con una función pura: entra el conjunto de señales del día, la cartera actual, el presupuesto disponible y el archivo de reglas; sale una lista de órdenes propuestas. Sin efectos laterales, sin red, sin escribir en `senales.db`.

Las reglas viven en un archivo de configuración versionado, no en el código:

- umbral mínimo de señal para que una orden valga la pena
- tamaño máximo de una posición como fracción del presupuesto
- tenencia mínima, para que el sistema no entre y salga contra el ruido
- presupuesto diario, semanal y mensual
- pérdida acumulada que apaga todo el riel y exige firma humana para reactivarlo

**No inventes los números.** Proponé tres juegos de parámetros, medí el costo de cada uno sobre la cuenta en papel del bloque 4, y dejalos en `espera_firma.md` para que Nicolás firme uno. Mientras no haya firma, la configuración por defecto es la más conservadora de las tres.

Tests de propiedad, no de ejemplo: que la suma de órdenes nunca exceda el presupuesto, que ninguna posición supere su tope, que con el interruptor apagado no salga ninguna orden, que sin señal por encima del umbral no se opere, y que la función sea determinista sobre la misma entrada.

## 6. Bloque 4: la cuenta en papel, con la línea base primero

Orden obligatorio dentro del bloque: **primero la línea base, después la estrategia.** Si se construye la estrategia antes de tener la vara, la vara se elige mirando el resultado.

**4a. La línea base aburrida.** Comprar un ETF del sector con un monto fijo cada semana, sin decidir nada. Esa es la vara que cualquier cosa inteligente tiene que superar.

**4b. El libro contable simulado.** Ejecuta las órdenes de la capa de decisión contra los precios ya guardados, sin descargas nuevas. Cobra comisión y deslizamiento de forma explícita, con barrido de sensibilidad de costo de 0 a 10 puntos básicos por lado más la comisión fija, porque para una estrategia de rotación frecuente el supuesto de costo es el resultado y no un detalle.

**4c. El reporte.** Resultado en dólares y en porcentaje, contra la línea base, con intervalo computado y agrupación por semana. Ningún estimador puntual suelto. Si la estrategia no supera a la línea base, se publica así, con la misma firmeza con que se publicaría lo contrario.

Todo lo que salga de este bloque se etiqueta SIMULADO. Ninguna cifra de la cuenta en papel entra al README ni a ninguna afirmación del proyecto sin pasar por el adversario.

## 7. Bloque 5: el pre-registro del riel de dinero

Documento `dinero/preregistro_dinero.md`, escrito antes de mirar cualquier resultado del bloque 6.

- Qué hipótesis persigue el riel: que un movimiento en un eslabón anticipa el de otro eslabón aguas abajo, con retardo medible.
- Qué autoriza pasar de papel a plata real: criterio numérico explícito contra la línea base, con cuántas semanas de papel y qué intervalo. Escribilo como número, no como intención.
- Qué mata la pista: qué resultado haría que Nicolás cierre el riel de dinero en vez de seguir ajustándolo.
- La declaración de que el primer monto real es costo de aprendizaje operativo y no una apuesta con retorno esperado demostrado.
- Qué haría ilegítima esta enmienda si se tocara después de ver resultados.

`estadistico-adversario` lo dictamina en la sesión de cierre: si es un criterio o si es una intención disfrazada de criterio.

## 8. Bloque 6: la primera señal larga

Este bloque tiene un orden que no se negocia. **Primero el pre-registro, commiteado. Después el cómputo.** Una señal diseñada mirando su propio resultado nace inválida y no sirve para nada.

**6a. Pre-registro.** Declaralo antes de correr nada, en `GEMELO/preregistro/senal_larga_v1.md`:

- La hipótesis, en términos económicos y no estadísticos: qué eslabón anticipa a cuál y por qué habría razón para que eso ocurra.
- Los horizontes a probar: 20 y 60 días hábiles. Nada más.
- Las especificaciones a probar: **máximo tres, declaradas por nombre antes de correr la primera.** Cada una incrementa el registro de intentos del DSR.
- La métrica primaria bajo D3: magnitud, con MAE y CRPS donde haya densidad. Dirección como secundaria, con la misma firmeza.
- Las dos varas: la línea base aburrida del bloque 4a, y predecir cero.
- Qué resultado refuta la hipótesis.

**6b. Cómputo.** Walk-forward con embargo, años de ajuste y prueba congelados antes de mirar. `auditor-lookahead` corre antes de la primera medición, no después. Sólo instrumentos y datos que el proyecto ya ingiere; si hace falta una fuente nueva, se declara como necesidad y el bloque se detiene ahí en vez de improvisar una descarga.

**6c. Publicación.** Con n, intervalo de clúster y estatus evidencial. Si ninguna de las tres especificaciones supera a las varas, la conclusión honesta es que los datos disponibles no traen señal larga detectable, y se escribe así. Ese es un resultado, no un fracaso del bloque.

## 9. Bloque 7: la capa visual

Sólo si los bloques 0 a 6 cerraron. Si no alcanzó, este bloque no se empieza y se declara no iniciado.

Primero descubrí con la máquina qué existe hoy como capa interactiva y dónde vive. No asumas.

Objetivo: que Nicolás vea el proyecto entero de un vistazo, no que la interfaz se vea moderna. Tres vistas:

1. **La cadena.** Cada eslabón, de materias primas a demanda de IA, con su instrumento comprable, su estado y sus huecos declarados. Esta vista es el mapa del bloque 1 hecho visible.
2. **El riel de dinero.** La cuenta en papel contra la línea base, con su intervalo, y el presupuesto disponible. Todo con la etiqueta SIMULADO visible sin hacer scroll.
3. **Los dos rieles.** El estado de cada uno: qué mide, cuánta muestra lleva, qué le falta para veredicto.

Reglas de honestidad visual, que son las mismas del resto del proyecto:

- Toda cifra aparece con su n y su intervalo. Un número solo, sin intervalo, no se muestra.
- Lo que no pasó por el adversario lleva etiqueta PROPUESTA.
- La palabra "confianza" sigue prohibida y el test que lo verifica debe cubrir también estos archivos nuevos.
- Ningún gráfico sugiere una tendencia que la cifra no sostiene. Si el intervalo cruza el cero, la vista lo dice con palabras, no sólo con una banda.

`curador-epistemico` dictamina esta capa como texto publicado, porque lo es.

## 10. Regla de corte

Los bloques van en el orden de este archivo. Si el tiempo o el presupuesto no alcanzan, se cierra limpiamente lo que esté abierto y lo restante se declara **no iniciado** en la bitácora, con la razón. Un frente a medias sin bitácora es peor que uno no empezado.

Prioridad si hay que elegir: bloques 0, 1, 2 y 3 son el piso de la corrida. El 4 es lo que la hace útil. El 5 y el 6 son lo que la hace ambiciosa. El 7 es lo que la hace visible.

## 11. Cierre de la sesión A

1. `GEMELO/resultados/bitacora_10.md`, por bloque: qué se hizo, qué se encontró con n e intervalo, qué quedó abierto, y errores propios de esta sesión.
2. Acta en `DECISIONES.md`, que incluya la declaración de los dos rieles como decisión de arquitectura.
3. `ESTADO.md` actualizado.
4. Lo que requiera firma humana, a `espera_firma.md`, incluidos los tres juegos de parámetros del bloque 3.
5. Commit en `main`, sin push. No corras los dictámenes en esta sesión: quedan para `~/cierre.md` con contexto limpio.
6. Suite completa al final. Anotá el número y compará con el del inicio.
