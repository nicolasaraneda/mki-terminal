---
name: acta-decision
description: Escribe una entrada en DECISIONES.md o un documento de diseño pre-registrado. Úsala cada vez que quede tomada una decisión de diseño, aparezca una asimetría entre el Mac y el PC, se declare una deuda técnica, se descubra una errata en una fila sellada, o haya que escribir un pre-registro antes de construir. Define los cuatro formatos de acta del proyecto y el estilo de la casa. Absorbe al agente escriba-decisiones, retirado el 2-sep-2026.
argument-hint: "[decision | asimetria | deuda | errata | preregistro]"
---

# Acta de decisión

Lo que no queda escrito se pierde. Este proyecto perdió cuatro commits con un
SSD y lo único que sobrevivió fue el acta de qué se construyó y por qué.

Esta skill escribe la memoria institucional del proyecto. Hasta el 2-sep-2026
lo hacía el agente `escriba-decisiones`; se retiró porque un agente cuesta
fichas en cada sesión por su `description` y una skill cuesta cero hasta que
se invoca. Su procedimiento completo vive acá, sin recortes.

## Estilo de la casa

- Español de Chile, directo, sin adornos.
- **Sin rayas ni guiones largos.** Usa comas, dos puntos o paréntesis.
- Toda afirmación cuantitativa lleva n, y lleva intervalo si es un estimador.
- Toda afirmación nueva lleva su etiqueta evidencial (MEDIDO, PROPUESTA,
  REFUTADO, RETIRADO, DECISIÓN PENDIENTE): es lo que el `curador-epistemico`
  va a exigir después.
- Los riesgos se declaran **antes**, no después de que se materializan.
- Los negativos se publican con la misma firmeza que los positivos. Un retador
  que no supera al campeón es un resultado.
- Nada de "se mejoró el rendimiento". Di cuánto, medido contra qué, con qué n.
- Si una decisión fue por conveniencia y no por evidencia, dilo así.
- Una cifra retirada (`GEMELO/cifras_retiradas.md`) sólo se cita con su marca
  de retiro a la vista («retirada», «errata», «era», «es falsa»).
- Antes del commit se corrige en su sitio; la errata fechada es para lo que ya
  está en HEAD. Un acta que se calumnia a sí misma es peor que un acta escueta.

## Decisión de diseño

```
## <fecha> — <título>

**Qué se decidió.** Una frase.

**Por qué.** El razonamiento, con los números que lo sostienen.

**Qué se descartó y por qué.** Las alternativas que se miraron.

**Qué queda abierto.** Lo que esta decisión no resuelve.

**Cómo se revierte.** Si se puede.
```

## Asimetría entre máquinas

Cuando las dos máquinas difieren en algo (intérprete, timeout, variable de
entorno, versión), se escribe aunque se decida no igualar. Igualar por omisión
también es igualar, y también se escribe. Los roles (titular, sombra, fuera de
servicio) se leen de la máquina con `modo.py`, no de la plantilla: hoy el
titular es el PC.

```
### Asimetría: <qué difiere>
<máquina A> (<rol>): <valor>    <máquina B> (<rol>): <valor>
Decisión: igualar / no igualar
Razón: <por qué>
Qué la haría revisar: <la observación que cambiaría la decisión>
```

Ejemplo vivo: Python 3.11.15 en el Mac contra 3.14.4 en el PC. Decisión: no
igualar. Razón: el PC perdido corrió 3.14.4 con este mismo `requirements.txt`
y dejó 79 tests en verde, las librerías del álgebra son idénticas, y ahora
existe un control más fuerte (las dos máquinas parten de la misma `senales.db`).
Qué la haría revisar: β sistemáticamente distintos en modo sombra.

## Deuda declarada

```
### Deuda: <qué>
Hoy es inofensivo porque: <el pin, la versión, la guarda que la contiene>
Se vuelve peligroso cuando: <el evento que la activa>
Bloquea: <qué no se puede hacer hasta resolverla>
Qué exigiría resolverla: <la demostración necesaria>
```

Ejemplo vivo: `pd.concat` y `Pandas4Warning` en `motor.py:215`. Contenida por
`pandas==3.0.3` en las dos máquinas. Peligrosa el día que alguien suba a
pandas 4: el default de `sort` cambia y los β se mueven en silencio. Bloquea
todo upgrade de pandas. Resolverla exige demostrar el cambio byte a byte,
porque `motor.py` es intocable.

## Errata en fila sellada

**La fila no se toca.** Nunca. Se documenta.

```
### Errata: <fecha de la fila> <ticker>
Qué dice la fila: <valor sellado>
Qué debería decir: <valor correcto> — <por qué se sabe>
Cómo se descubrió: <el procedimiento>
Efecto sobre las métricas publicadas: <cuantificado, o "ninguno" con razón>
Decisión: se deja sellada, se anota acá.
```

## Pre-registro

Un documento de diseño se escribe **antes** de construir y **antes** de ver el
primer resultado. Lleva: por qué existe la etapa, la línea base medida, las
decisiones de diseño con la medición que las justifica, los criterios de
victoria congelados, los criterios de rechazo, qué NO se hace, y los riesgos
declarados. Los criterios de victoria no se tocan después de ver resultados. Si
alguien te pide moverlos, tu respuesta es que eso se documenta como lo que es.
Un pre-registro lleva fecha y el hash del commit anterior a la primera corrida:
sin eso, el `estadistico-adversario` etiqueta el resultado como exploratorio.

## Dónde escribes

`DECISIONES.md` es la memoria institucional y vive en el repo. Los documentos
largos de diseño y los briefs de handoff van también al Proyecto de Claude, que
es lo que sobrevive a una pérdida de disco. Cuando escribas algo durable,
pregunta si va a las dos partes.

Toda cita a `DECISIONES.md` por número de línea se desplaza con el acta que la
cita: citá por sección (`§30.5`) y verificá los números después de escribir,
no antes.
