---
name: acta-decision
description: Escribe una entrada en DECISIONES.md. Úsala cada vez que quede tomada una decisión de diseño, aparezca una asimetría entre el Mac y el PC, se declare una deuda técnica, o se descubra una errata en una fila sellada. Define los cuatro formatos de acta del proyecto.
argument-hint: "[decision | asimetria | deuda | errata]"
---

# Acta de decisión

Lo que no queda escrito se pierde. Este proyecto perdió cuatro commits con un
SSD y lo único que sobrevivió fue el acta de qué se construyó y por qué.

Estilo: español directo, sin rayas ni guiones largos, toda cifra con su n, los
riesgos declarados antes y no después.

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

Se escribe aunque se decida no igualar. Igualar por omisión también es igualar.

```
### Asimetría: <qué difiere>
Mac (titular): <valor>    PC (sombra): <valor>
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
Hoy es inofensivo porque: <el pin, la guarda que la contiene>
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
