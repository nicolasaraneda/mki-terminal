# Dictamen del `director-programa` · octava corrida (2-sep-2026, cierre)

> Texto del agente, guardado por el orquestador. Sus dos correcciones concretas
> (la t de clúster es PROPUESTA, no «el estimador desde hoy»; `MINIMO_DIAS_SHARPE`
> es firma) se aplicaron a `ESTADO.md` y `estado_epistemico.md` antes de cerrar.

**Veredicto global: MOVIÓ LA AGUJA, y se pasó de largo.** Lo mejor de esta corrida es lo que el norte pide: puso a prueba el instrumento y el mecanismo, no un número de acierto. Lo peor es que gastó, en una tarde y de forma irreversible, un recurso escaso del proyecto para responder preguntas que no eran V1–V7.

## 1. Aguja y rama

**Aguja:** A (el defecto de unidades del PSR/DSR: V5 calibrado hacia el lado permisivo; el IC de clúster publicado cubre ~0,93); B (Δ(h) predicha antes de descargar y refutada por Hong Kong e India: lo que predice la ventaja por bolsa es la tasa base, no h — toca la portada, por eso vale); C (replica fuera de muestra, aguanta dejar-un-año y dejar-un-ticker, mata H2 y H3); G (`cifras.py`: regla de la casa ejecutable, riesgo cero); D a medias (lo publicable es el negativo: el orden del campeón da 0,18, bajo su vara, y no sobrevive a R2).

**Rama:** F (quinto rechazo; reintrodujo el defecto #1 de la v1; debió parar en el tercero: **no hay v6**); E en su parte entregable (el mecanismo —19 de 35 fechas contribuyen cero— es aguja; la «frase en dos versiones» es cambiar la pregunta después de ver que la primera no responde, y bajo R2 la magnitud tampoco habla); H2 (del ramo, no de la tesis).

## 2. Lo que no debía hacerse

**El daño mayor: `REGISTRO_INTENTOS` pasó de 100 a 286 en una tarde.** Bien contado y declarado — y con N = 286 ningún retador con Sharpe positivo pasa V5 en este siglo. El proyecto quemó su presupuesto de multiplicidad, irreversible, en preguntas de mecanismo. Publicar 107 intervalos en un frente es una decisión de programa, no de análisis; nadie preguntó «¿qué se rompe si esto sale bien?».

**Segundo, de firma:** `ESTADO.md` declaraba la t de clúster «el estimador desde hoy». Es un cambio de vara elegido después de ver la cobertura, sobre un criterio pre-registrado que no se cumple literalmente en la propia semilla: debe decir PROPUESTA. Lo mismo `MINIMO_DIAS_SHARPE = 60`, hoy lo único que separa a tres configuraciones del WS2b de «V5 superado».

**Bien hecho, y hay que decirlo:** motor, senales, snapshot, .env y timers intactos; ninguna fila sellada reescrita; ninguna cifra publicada movida; nada pusheado; el hook «que se extiende» no se ejecutó y se anotó.

## 3. Lo único que sigue, y lo que debe parar

**Lo único: decidir la rama del efecto** (§2a-ter + la regla de dedup firmada). **Lo que debe parar: ningún frente empírico nuevo ni un intervalo más hasta que la rama esté decidida** — cada intervalo quema N sobre un efecto indeterminado. F se archiva. Y el parche del O(n²) de `mki-noticias` y `.env` en 644 son nivel 1 (la cadena de sellos) y siguen esperando debajo de nueve frentes: que se queden arriba de `espera_firma.md`.

## 4. La contradicción de la rama: sí, la más urgente

El README publica +6,45 pp bajo una convención que el proyecto derogó el 1-sep (la regla firmada da +9,66 sobre la misma ventana): un documento público que afirma algo distinto de lo que la máquina ya decidió. Y todo lo que depende del tamaño del efecto está indeterminado por un factor ~5: días para 0,80 (~100 / ~229 / ~480), MDE, dimensionamiento, la frase del 25-oct — quedan menos de ocho semanas. Consecuencia del éxito, para escribir ANTES de decidir: las dos ramas vivas suben la portada; la defensa (la regla se firmó antes de esta corrida y de conocer su efecto) sólo sirve si la decisión se registra con esa fecha y el recompute mueve **los doce bloques a la vez**, incluido el n de la ventana larga del §24.

## 5. Las tres propuestas

- **I (V1-bis): ADELANTE** — sólo endurece, usa la unidad medida con verdad conocida; después de la rama.
- **H1 (sello verificable): AHORA NO** — la más alineada con el norte, y por eso protegerla: séptimo timer y segunda salida de red en la única máquina que emite; después del 25-oct, decisión de timers de Nicolás.
- **H2 (FPGA): RAMA** — lo firmable hoy son los cuatro criterios de muerte y la corrección del 8,79 ms. Firmar la mordaza, no el frente.
