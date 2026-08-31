# La cola de decisiones — todo en una pantalla

Frente E de la segunda corrida autónoma. Consolida cada "decisión de
Nicolás" que hoy vive repartida en `DECISIONES.md`, `expedientes.md`,
`RELEVO.md`, `REPLICA.md`, `MICRO/`, `ESTADO.md` y lo nuevo de esta noche
(`concentracion.md`, `parche_documental.md`). Ninguna se resuelve acá.

**Orden: por costo de postergarla un mes, no por tamaño del documento que
la sostiene.** Una decisión de una frase puede costar más cara de demorar
que un documento de treinta páginas que no bloquea nada.

---

## 1. Activar la réplica, y con qué máquina

**Qué decidir, en una frase:** si se activa `docs/REPLICA.md` como
mecanismo permanente, y qué máquina hace de réplica del PC (¿el Mac,
ahora que quedó fuera del rol de titular?).

**Expediente:** `docs/REPLICA.md` completo. Las piezas ejecutables (el
comparador adaptado a rol permanente, el registro de divergencias, los
tests de los tres casos) se construyeron esta misma noche — Frente D — sin
necesitar esta firma; lo único pendiente ES la firma.

**Qué se bloquea mientras esté abierta:** el proyecto sigue con **una sola
máquina emitiendo, la misma cuyo disco de sistema ya falló una vez**
(la reactivación 5.0.3 completa nació de esa falla). No hay ninguna
protección activa contra que se repita.

**Costo de postergarla un mes:** es el único ítem de esta lista con un
costo de postergación que no es hipotético — ya se materializó una vez.
Un mes más sin réplica no es "una decisión de diseño pendiente", es un
mes más de exposición a perder el disco otra vez sin nada corriendo en
paralelo. La pieza técnica dejó de ser el cuello de botella esta noche;
lo único que falta es la firma.

**Recomendación, marcada como tal:** de todo lo que espera en esta cola,
esto es lo que yo priorizaría primero — no porque las otras no importen,
sino porque es la única cuyo costo de espera ya tiene precedente real.

---

## 2. Qué hacer con la lectura del track record sellado

**Qué decidir, en una frase:** si se publica un parche documental que
declare que la evidencia de hoy no alcanza para decidir si la ventaja
sellada es real o es una racha de azar concentrada en 6 fechas de julio
(`GEMELO/resultados/concentracion.md`, ya revisado y corregido dos veces).

**Expediente:** `GEMELO/resultados/concentracion.md` v2 (revisado por
`estadistico-adversario` y `auditor-lookahead`; el veredicto de fondo
cambió respecto a la v1 — ya NO dice "es azar", dice "no se puede
decidir con esta evidencia"). `GEMELO/resultados/parche_documental.md`
quedó **desactualizado por esta corrección** — su propuesta de criterio
R4 se apoya en un scan-statistic que resultó estar mal construido en su
versión de anchos 3-10; hay que revisarlo contra la v2 antes de
proponérselo a Nicolás, no aplicarlo tal cual.

**Qué se bloquea mientras esté abierta:** el README y tres archivos vivos
de referencia (`cifras-canonicas`, `estadistica-evaluacion`,
`estadistico-adversario.md`) siguen citando +6.5pp sin la advertencia de
concentración. Cualquiera que lea el proyecto hoy —incluida una sesión
futura de este mismo agente— cita la cifra sin el matiz que la vuelve
honesta.

**Costo de postergarla un mes:** técnicamente cero (nada se rompe). El
costo real es de integridad pública: cuanto más tiempo pase el README sin
esta advertencia, más se acumula la lectura "el modelo tiene una ventaja
chica pero constante" en cualquiera que lo mire — que es exactamente lo
que esta auditoría encontró que no sostiene la evidencia.

**Recomendación, marcada como tal:** el parche ya está escrito y no
cambia ninguna cifra, solo agrega contexto — es barato de aplicar en
cuanto la revisión adversaria de `concentracion.md` cierre en verde (o se
corrija según lo que pida). Yo lo aplicaría en cuanto eso pase, sin
esperar a que se acumule más.

---

## 3. Los umbrales de `GEMELO/RELEVO.md`

**Qué decidir, en una frase:** si el margen mínimo de 5pp, el n≥150
filas/60 días, y el criterio R4 propuesto en esta corrida son los
correctos, o si Nicolás fija otros.

**Expediente:** `GEMELO/RELEVO.md` completo (corregido esta noche tras un
RECHAZO adversario) + la propuesta de R4 en `parche_documental.md`.

**Qué se bloquea mientras esté abierta:** nada hoy — no hay ningún
retador corriendo que necesite evaluarse contra estos umbrales.

**Costo de postergarla un mes:** bajo hoy, pero no lineal — el día que
GEMELO 6.0.0 produzca un candidato serio, esta decisión pasa de "no
urgente" a "bloqueante" de un día para el otro. No es agua bajo el puente
mientras tanto, pero tampoco hay apuro de calendario.

**Recomendación:** no es urgente resolverla ahora, pero conviene no
dejarla para el mismo día que aparezca un candidato — para entonces, un
pre-registro fijado bajo presión deja de ser un pre-registro.

---

## 4. Placa FPGA y alcance de `GEMELO/MICRO/`

**Qué decidir, en una frase:** Nandland Go Board (iCE40HX1K) o Arty
A7-100T, y si el pipeline replica al 4.6.0 (simplificado, F≤3) o una
versión propia declarada aparte.

**Expediente:** `GEMELO/MICRO/fpga.md` §5 y `GEMELO/MICRO/RTL.md` §6
(nuevo esta noche, con el presupuesto de recursos medido por etapa).

**Qué se bloquea mientras esté abierta:** literalmente escribir la primera
línea de RTL — `RTL.md` es explícito en que el diseño se revisa antes de
codificar, y elegir placa determina qué cabe.

**Costo de postergarla un mes:** depende enteramente de un calendario que
este documento no conoce (el cronograma de la materia de Nicolás). Si el
proyecto final tiene fecha de entrega dentro del mes, el costo es alto; si
no, es cero. **Este documento no puede estimarlo — es dato que falta, no
indecisión.**

**Recomendación:** ninguna sin saber la fecha de entrega. Si hay que
elegir con la información de hoy: el presupuesto de recursos de `RTL.md`
§2 dice que F≤3 (una combinación ponderada chica) ya se aprieta contra el
iCE40HX1K — si el plan es demostrar algo más que un umbral simple, la
Arty A7 quita esa restricción con margen de sobra.

---

## 5. Las cinco preguntas del WS4 (§33.8)

**Qué decidir, en una frase:** si se corrige la ventana larga a la
convención congelada, cómo se reconcilia el §32.5 refutado, cómo se
reporta Fráncfort, y si las 8 filas del 29-jul (sesión saltada) siguen en
las métricas — la abstención pendiente desde 5.0.2.

**Expediente:** `DECISIONES.md` §33.8.

**Qué se bloquea:** nada operativo — son preguntas de curaduría de
reporte, no de funcionamiento.

**Costo de postergarla un mes:** bajo, con precedente — llevan abiertas
desde antes del 26-ago sin romper nada. Es deuda acumulada, no una bomba.

**Recomendación:** agruparlas con la decisión del ítem 2 (el parche
documental) cuando se toque el README — es más barato resolver varias
preguntas de reporte en una sola pasada que una por una.

---

## 6. Expedientes 6B — visibilidad de `ts_emision`, estampida de timers

**Qué decidir, en una frase:** (a) si agregar un campo `commiteado_en`
aditivo (recomendado en el expediente, bajo riesgo); (b) si auditar la
idempotencia de los 6 jobs systemd ante un disparo simultáneo tras una
caída (nadie lo investigó nunca, ni siquiera se sabe si es un problema
real).

**Expediente:** `GEMELO/resultados/expedientes.md` §6B.1 y §6B.3.

**Qué se bloquea:** nada hoy — son huecos de auditoría, no fallas
observadas.

**Costo de postergarla un mes:** bajo. El riesgo de la estampida de
timers es hipotético y sin evidencia de haber ocurrido nunca.

**Recomendación:** la opción 2 del §6B.3 (auditar la idempotencia, sin
tocar ningún timer) es barata y de solo lectura — se podría hacer en
cualquier sesión futura sin esperar nada.

---

## 7. El alcance del pin de pandas (expediente 6C)

**Qué decidir, en una frase:** si escribir el test de estabilidad de los
5 sitios de `pd.concat` (recomendado, no toca producción) antes de decidir
si el pin sigue con el mismo alcance ahora que el Mac quedó fuera.

**Expediente:** `GEMELO/resultados/expedientes.md` §6C. Nueva evidencia de
esta noche: `pytest` ya emite `Pandas4Warning` en los 3 archivos exactos
de la deuda, con la versión pineada — la deuda es real y ya está avisada.

**Qué se bloquea:** ningún upgrade de pandas mientras tanto — que de
todos modos nadie está pidiendo hacer.

**Costo de postergarla un mes:** muy bajo.

**Recomendación:** escribir el test primero (opción 3 del expediente) es
casi gratis y convierte la pregunta en medible.

---

## 8. Si `.claude/` se versiona o queda local a esta máquina

**Qué decidir, en una frase:** exactamente lo que dice el título.

**Expediente:** mencionado en `ESTADO.md`, sin expediente propio todavía
— es la decisión más chica de esta lista.

**Qué se bloquea:** nada.

**Costo de postergarla un mes:** ninguno detectado.

**Recomendación:** ninguna — es una preferencia, no un riesgo.

---

## Lo que esta lista NO incluye, a propósito

El segundo movimiento del switch (apagar los timers del Mac, quitar
`MKI_MODO` en el PC) no entra en esta cola con su propio ítem porque ya
tiene su lugar establecido: es "el segundo movimiento", vive en la skill
`switch-titular`, y esa skill ya es su propio expediente completo — no
hacía falta duplicarlo acá. Si Nicolás quiere verlo priorizado junto con
el resto, decirlo y se agrega.
