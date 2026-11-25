# Dictamen del `curador-epistemico` sobre la v6 — RECHAZADO, y atendido

**25-oct-2026, corrida 17.** Revisión del texto de
`GEMELO/SECUENCIAL/DISEÑO.md` versión 6, sobre la **primera redacción** de
esa versión. Barrido: 482 oraciones de prosa y 212 filas de tabla; 54
afirmaciones sin etiqueta o con etiqueta incorrecta, **25 de ellas
bloqueantes agrupadas en 12 hallazgos**.

> **Veredicto textual: RECHAZADO.** «Doce bloqueantes. Uno solo ya daba
> RECHAZADO. La v6 es muy superior a la v5 y la mayor parte de sus
> correcciones son reales y verificables; lo que sigue es lo que todavía
> dice más que la cifra.»

**Los doce bloqueantes están atendidos en el árbol que esta corrida aplica.**
Tres de ellos (B3, B4, B5) ya lo estaban cuando el dictamen se entregó: el
curador leyó el documento mientras la corrida le ponía las marcas de retiro
en su sitio, y `cifras.reintroducciones()` devuelve `[]` sobre el documento
final. Lo mismo con la cabecera de B1, que ya estaba condicionada.

| # | Qué dijo el curador | Qué se hizo |
|---|---|---|
| B1 | «LISTA PARA FIRMA» se adelanta a un dictamen que no existe | La cabecera ya decía «NO CONGELADA» con la etiqueta explicada; se corrigió además la fila del acta, que daba el quinto dictamen por existente, y la fila F1 del registro |
| B2 | la cláusula 6 de §A3.7, que se propone congelar, estaba cableada a `p_d = 0.516`, de la rama derogada | corregida a 0.4924 |
| B3 | `−3.3 pp` sin marca y fuera del alcance de la marca de «filas 7 a 12» | marca en la misma fila (ya aplicada antes del dictamen) |
| B4 | `0.1849` y `+6.5 pp` con la marca a 14 y 23 líneas | marcas en la misma celda (ya aplicadas) |
| B5 | `3.64×` dos veces sin marca al lado | marcas en la misma línea (ya aplicadas) |
| B6 | **bloqueante de código**: el comentario de `mirada.py` pegado a `MDE_FIRMADO` ofrecía una cifra retirada, un valor objetado, y decía «el único parámetro sin firmar» siendo dos | bloque reescrito entero; ningún valor se ofrece, y dice «uno de los dos» |
| B7 | el candado se describía con «descarta las 253 y computa sobre 0», refutado por §A3.5 del mismo documento | «descartaría las 262 y tendría 288 de población, y aun así no computa» |
| B8 | §A3.1.a mantenía en presente que «el parámetro que manda es E\|r\|» y el par 4.02 / 3.72 que F8 declara reemplazado | premisa fechada por escala, cifras vigentes, y el par viejo citado como la medición superada |
| B9 | el párrafo de conclusión de §A3.1.b reinstalaba la razón 1 que la cabecera de la sección acababa de tumbar | reescrito: la razón 1 no se sostiene con intervalo, y lo que sostiene la conclusión es el argumento estructural |
| B10 | la comparación de la razón 1 sigue mezclando ventanas, y su IC no dice qué propaga | declarado: cada pata con su ventana, el IC propaga sólo E\|r\|, y la cercanía de los puntos pasa a ser ilustrativa |
| B11 | **el más importante**: el MDE crítico publicado como punto y comparado contra un punto, teniendo el documento el intervalo de `f` | el crítico pasa a **11.09 pp, IC95 [8.93, 12.81]** (el valor se movió después, al computar el factor secuencial), con la identidad `p_d ≡ f` declarada. Se conserva lo que sí está medido: por encima de 12.81 pp la mirada 1 está vencida para todo el intervalo de `f`. **ERRATA de esta tabla, 25-oct más tarde:** esta fila decía que el intervalo estaba «en el documento, en `tabla_firma.py`, en la tarjeta y en la bitácora», y el `guardian-constitucion` midió que estaba en dos de los cuatro — la tarjeta y la bitácora publicaban el punto desnudo. **Corregido en los cuatro** antes del commit; la fila se deja con su errata porque declaraba atendido lo que no estaba |
| B12 | las tres frases que prohíben la palabra «congelado» eran falsas: cuatro líneas la predicaban del propio pre-registro, más el encabezado de `mirada.py` | las cuatro corregidas a «se propone congelar» / «fuera del alcance de su firma»; el encabezado de `mirada.py` reescrito; las frases pasan a «ninguna línea PREDICA «congelado» de este pre-registro» |

**Las 22 observaciones también se atendieron**, todas menos ninguna: O1
(fecha de una tabla retirada), O2 (§A4 al ritmo superado, ahora declarado
con su dirección), O3 (la tabla de §A3.6 sin la etiqueta «idealizado»), O4
(el cuerpo con «~0.76» y «~1.7 pp», corregidos a 0.7537 y 4.6 pp), O5 («400
fechas son 8 años», retirado), O6 (`ac1` con el par de la v5), O7 (la banda
del α en dos versiones), O8 (el pasivo comparado contra su piso sin
decirlo), O9 (la matriz previa a la firma citada como vigente: ahora 59 de
192 con la de 768 entre paréntesis), O10 (la atribución del hueco 296 → 288,
ahora verificada por conteo), O11 (cada denominador con su receta), O12 (la
identidad `p_d ≡ f`, que B11 necesita), O13 (**la asimetría de
reproducción**: la ventana antecedente reproduce, el calendario no y no
debe; se sella `tabla_firma_17.json` con su instante), O14 y O15 (el
intervalo de un insumo y las réplicas y semilla del IC del MDE, ahora
impresos), O16 (el bloque de la era v3 y una remisión a una sección
inexistente), O17 (sólo dos de los cuatro parámetros tienen candado), O18
(«nadie computó la ventaja» → «nadie corrió `mirada.py`», y la ausencia de
la carpeta establece una cosa y no la otra), O19 (`/api/rieles` es un
subconjunto estricto), O20 («iba a congelar»), O21 (el pasivo como PISO
incompleto), O22 («suele pasar temprano» como expectativa).

**Lo que el curador verificó como BIEN HECHO y no hay que tocar:** que la
frontera de futilidad es genuinamente independiente del MDE; que la tabla de
exposición residual de §A3.2, declarada NO recomputada, está bien tratada
(fila en el registro, dirección del error argumentada, recomputación a la
cola); que conservar las filas 7 a 12 de §A1 con su marca es la decisión
correcta porque la tabla registra qué se miró, no cuánto valía; que
`MDE_PROPUESTO = None` cuadra con la máquina; que el reparto entre regla de
FILAS firmada y regla del ESTIMADOR abierta es real y es «la corrección más
valiosa de la versión»; que las tarjetas §90 a §95 existen y la §90 es
honesta; y que `DECISIONES.md` §107.4 y §107.5 confirman que los cuatro
parámetros están sin firmar.

**Zonas ciegas que el curador declaró**, y que quedan como tales: no corrió
los scripts que leen `senales.db` (fuera de su mandato), así que tomó como
declaradas las cifras medidas y verificó sólo la aritmética que las une
—Connor, DEFF, el factor secuencial, las cinco filas de `N_max`, los cuatro
n de mirada, el calendario día a día, 288/38, 129/262, el MDE simétrico y la
bisección del crítico, todo al 0.2%—; no auditó la bitácora; su barrido de
cifras retiradas es un PISO por los dos límites declarados del instrumento;
y señaló dos reintroducciones **preexistentes y fuera del diff de esta
corrida**, `GEMELO/SECUENCIAL/horizonte.py`:63 y
`GEMELO/SECUENCIAL/trayectoria.py`:8, que narran historia y que esta corrida
**no tocó** — quedan declaradas acá para que no se pierdan.
