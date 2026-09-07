# Aplicación de las exigencias de los cuatro dictámenes de la corrida 10

**7-sep-2026, sesión de cierre en contexto limpio.** Los cuatro dictámenes
están en este mismo directorio y **los cuatro rechazaron**. Una fila por
exigencia: **aplicada**, **rechazada con razón**, o **diferida** con el número
del ítem de `espera_firma.md` donde queda.

Dos reglas que gobernaron todo este paso y conviene decirlas antes de la tabla:

1. **La corrección va al ejecutable antes que al texto.** Arreglar la prosa de
   un reporte y dejar la función imprimiendo lo mismo no es una corrección.
   Donde una exigencia tocaba un generador, se corrigió el generador y se
   **regeneró** el artefacto: `dinero.senal_larga_reporte`, `dinero.cuenta_papel`
   y `dinero.mapa` se volvieron a correr, y el `.md` publicado es su salida, no
   un texto editado a mano.
2. **Un número retirado que sigue ofrecido desde el código vuelve a circular.**
   Por eso las cifras retiradas se retiraron **donde se generan** (generador,
   JSON, endpoint y vista), y se registraron en `GEMELO/cifras_retiradas.md`
   para que el árbitro las cace sola la próxima vez.

**Ninguna exigencia se ignoró en silencio.**

---

## Lo más importante que cambió, antes de la tabla

- **La cuenta en papel quedó RETIRADA.** El auditor demostró cuatro fugas
  temporales ejecutando código, y la cifra titular se mueve al quitarlas (el
  juego medio pasa de 27 % a 57 % a 5 pb). No se «arregló y republicó»: se
  retiró, porque reconstruirla exige el orden que el propio auditor fija —el
  test de truncación primero— y eso es trabajo de corrida, no de cierre. **Lo
  que sí se hizo acá es escribir ese test**, en su forma más útil.
- **La señal larga perdió su única celda positiva, y la perdió por su propia
  máquina.** El reporte ahora computa Holm sobre la familia completa de 30
  contrastes y la ablación anual, y publica las dos **salga lo que salga**.
  Resultado: ninguno de los 30 cruza α = 0,05, y la celda que ganaba sin
  corregir contiene el cero al sacar 2024. Todas esas cifras las reprodujo la
  máquina y coinciden dígito a dígito con las que el `estadistico-adversario`
  computó por su lado, con otra implementación.
- **Los tres xfail estrictos son el entregable más duradero de este cierre.**
  `tests/test_dinero.py` clava F1, F2 y F4. Hoy fallan porque las fugas
  existen. El día que alguien las arregle, van a pasar, `strict=True` va a
  convertir ese éxito inesperado en rojo, y quien las arregló va a tener que
  venir a sacar el marcador. **La fuga dejó de vivir en la memoria de nadie.**
- **Un error propio de esta sesión, que corresponde declarar.** Escribí un
  `mcnemar_exacto` en `backtest/inferencia.py`, encontré por mi cuenta el
  desbordamiento de `2.0**n` y lo arreglé en espacio logarítmico. Después vi
  que `evaluacion.mcnemar_exact` **ya existía**, ya estaba en logaritmos y ya
  documentaba ese mismo desbordamiento con fecha. Es exactamente lo que
  `.claude/rules/backtest.md` prohíbe. La copia se borró, el reporte importa la
  que existe, y quedó un test que impide que vuelva a aparecer.

---

## `guardian-constitucion` — RECHAZA, 10 exigencias

| # | Qué exigía | Destino |
|---|---|---|
| 1 | La cifra RETIRADA 91,4 % impresa desde `senal_larga_reporte.py:374` (bloqueante) | **Aplicada.** Corregido el generador, regenerado el artefacto, y errata §10 E7 en el pre-registro con marca inline. |
| 2 | Ampliar el patrón de la saturación del PSR a las formas conjugadas | **Aplicada.** Patrón `satur[oó]\|saturad[oa]s?` en `cifras_retiradas.md`; las cuatro apariciones marcadas o corregidas. |
| 3 | `cifras.reintroducciones()` dio falso verde: exigir marca contigua, con contraprueba | **Aplicada.** `MARCAS_FUERTES` exentan solas; las ambiguas sólo si el contexto nombra la cifra. Dos tests de contraprueba en `test_cifras_arbitro.py`, uno reproduce el falso verde exacto. |
| 4 | El acta dice 4 tests marcados, la máquina tiene 6 | **Aplicada.** Errata fechada en `DECISIONES.md` §80.2. |
| 5 | `mapa.py:164` lista MSFT como «cuesta más de 500» y cerró en 499,70 | **Aplicada.** El generador dice ahora «no entran en 500 USD» con el criterio precio + comisión, declara los casos al borde y regenera. |
| 6 | Cifras tipeadas a mano en `api/main.py` al lado del comentario que lo prohíbe | **Aplicada.** σ retirada (venía de la cuenta con fuga y sin intervalo); la cifra R2 corregida; las de fricción retiradas del `que_lo_mata`. |
| 7 | `VISION.md` es un sitio publicado sin correa del árbitro | **Aplicada.** Entra a `cifras.DOCUMENTOS_PUBLICADOS`. Verificado: 0 reintroducciones. |
| 8 | «Doce comparaciones» son seis | **Aplicada.** Errata §6 B de `preregistro_dinero.md`. |
| 9 | El §9 afirma que su orden «está verificable en git» y git no lo verifica | **Aplicada.** Errata §10 E9: git verifica el §8; el §9 lo corroboran mtimes, que son mutables. Y queda la regla para la próxima: una enmienda entra en su propio commit. |
| 10 | `ESTADO.md` cita la celda sin decir que la vara es POST-HOC | **Aplicada, y superada:** la celda ya no se cita como superviviente, porque no lo es. |

## `curador-epistemico` — RECHAZADO, 18 exigencias (9 tocan ejecutable)

| # | Qué exigía | Destino |
|---|---|---|
| 1 | `api/main.py`: R2 «la vuelve negativa» | **Aplicada.** Texto exacto del dictamen: no se distingue de cero en las tres convenciones, sin recomputar bajo la regla firmada. |
| 2 | `VISION.md`: la misma cifra R2 en dos lugares | **Aplicada**, con la nota de que el −3,3 pp del 26-ago está bajo convención `estricta` y ancla derogada. |
| 3 | «hoy descalifica al propio campeón» en reporte y pre-registro | **Aplicada.** «hoy el propio campeón no pasa», en los dos. |
| 4 | El 91,4 % impreso desde el código | **Aplicada** (ver guardián 1). |
| 5 | Lo mismo, como errata fechada en el §9 del pre-registro | **Aplicada.** §10 E7, sin tocar el §7: marca inline más errata. |
| 6 | Anotar en `cifras_retiradas.md` el falso negativo y el patrón conjugado | **Aplicada**, más un bloque que documenta los dos límites del instrumento. |
| 7 | Declarar que la segunda vara pre-registrada NO se evaluó | **Aplicada en cuatro lugares**: el reporte generado, `ESTADO.md`, la bitácora y la errata §10 E10 del pre-registro. |
| 8 | `Rieles.tsx`: renderizar la `nota` y la magnitud con su intervalo | **Aplicada, y el contenido cambió:** la vista ahora publica sin corregir / tras Holm / tras ablación, más la `nota`, más la segunda vara sin evaluar. |
| 9 | `CifraConIntervalo`: dejar de hablar del cero sobre proporciones | **Aplicada.** Prop `esDiferencia` sin default permisivo; la API declara cuál de las cuatro cifras es diferencia; el test de contrato lo exige. |
| 10 | Acta: 4 tests marcados contra 6 | **Aplicada** (ver guardián 4). |
| 11 | Acta: falta el cierre de la suite y la falla de siete tests | **Aplicada.** Errata fechada en la cabecera de §80. |
| 12 | `mapa.py`: el JSON decía MEDIDO donde el `.md` dice SIMULADO | **Aplicada.** Dos campos, `estatus` y `estatus_de_los_precios`; la vista muestra los dos. |
| 13 | El 21 % es de otro diseño y la tasa de tipo I de esa página no está medida | **Aplicada y superada:** el 21 % se retiró por completo, y lo que ocupa su lugar es la corrección de Holm computada sobre esta familia. |
| 14 | σ hardcodeada y sin intervalo | **Aplicada.** Retirada del endpoint, con su razón. |
| 15 | `CONTRATO.md` promete McNemar que el endpoint no sirve | **Aplicada.** Manda la máquina: se agregó `mcnemar_p_filas` con su caveat. |
| 16 | El `estatus` de la señal larga se descarta antes de llegar a la UI | **Aplicada.** Viaja, está tipado y se renderiza. |
| 17 | Bitácora: «dos commits», son tres | **Aplicada** como errata. |
| 18 | `senal_larga_v1.md` fuera del test de la palabra prohibida | **Aplicada.** |

## `estadistico-adversario` — NO SOSTIENE, 24 exigencias

| # | Qué exigía | Destino |
|---|---|---|
| 1–3 | Retirar «5 de 24 (21 %)»; corregir la nula; las 24 no son 24 pruebas | **Aplicadas.** Las tres razones, textuales, en el generador, en el artefacto, en la vista y en el acta. |
| 4 | Una tasa de falso positivo necesita K semillas | **Diferida al §42.** Requiere una cuenta sin fuga: correr K semillas sobre la actual sería medir la fuga K veces. Declarado «sin respuesta medida» donde se citaba. |
| 5 | Corregir las tres citas río abajo del número retirado | **Aplicada.** Pre-registro §6 A, §5 y el veredicto de la señal larga. |
| 6 | Las cifras de fricción son rangos de un sorteo, no intervalos | **Aplicada** en el generador; la cifra entera además quedó retirada por fuga. |
| 7 | La línea base descrita no es la implementada | **Aplicada.** Errata §6 C: rige lo implementado, y el flujo se declara antes de correr hacia adelante. |
| 8 | El JSON declara 24 contrastes y el código computa 30 | **Aplicada.** `contrastes` sale de la familia real. |
| 9 | Aplicar y publicar corrección de multiplicidad | **Aplicada, y computada por el ejecutable.** Holm sobre 30, tabla completa, publicada siempre. Reproduce los p ajustados del dictamen dígito a dígito (0,0900 / 0,1740 / 0,2340). |
| 10 | La simetría vale para el negativo | **Aplicada.** El −2,339 pp se publica con su p de Holm 0,2340 y se dice que tampoco es distinguible de cero. |
| 11 | Reportar b, c y McNemar en dirección | **Aplicada.** Tabla propia, con el caveat de por qué manda el IC de fecha. |
| 12 | El CRPS no declara unidad ni escala | **Aplicada.** Todo el CRPS va en pp, punto e intervalo. |
| 13 | Publicar los bloques efectivos | **Aplicada**, con la medición propia de cuánto varía el ancho del intervalo con pocos bloques (0,67 a 1,29 veces el que corresponde, sobre ruido iid). |
| 14 | Correr la ablación tipo R2 | **Aplicada.** La corre el reporte, para **todas** las celdas y no sólo las que convienen. Reproduce el hallazgo: sin 2024 el IC contiene el cero. |
| 15 | El registro del riel largo subcuenta | **Diferida al §45.** Un agente no mueve un registro de intentos. La familia real (30) queda declarada en el §11 del pre-registro. |
| 16 | Declarar si se computó alguna métrica sobre la v1 con fuga | **Aplicada.** Errata §10 E9: no se computó ninguna, la enmienda no suma, y la próxima entra en su propio commit. |
| 17 | La tabla de potencia no la produce ningún código | **Diferida al §42.** Sellarla como script tiene sentido recién sobre una σ sin fuga; hoy la cifra está retirada. |
| 18 | σ sin intervalo, y depende del camino del barrido | **Aplicada** por retiro: la σ no viaja más hasta recomputarse con su intervalo. |
| 19 | M2 compara 156 semanas contra un umbral de 52 | **Aplicada la corrección del hecho** (errata §6 E, con las cifras de la peor ventana móvil) y **diferida la decisión al §43**. |
| 20 | M4 no cierra nada | **Aplicada la declaración** (errata §6 F) y **diferida la reescritura al §44**. |
| 21 | Referencias colgantes §2.5 y §2.2 | **Aplicada.** Errata §6 D, y corregidas las tres citas. |
| 22 | El titular del mapa usa la variante permisiva y no declara casos al borde | **Aplicada.** Los casos al borde los declara el generador; `ESTADO.md` dice que el censo es de un solo día. |
| 23 | Nada se corrió contra `GEMELO/simulador/` | **Rechazada para este cierre, con razón.** Es una verificación de procedimiento que exige diseñar el caso con ventaja verdadera conocida; no es una corrección de una cifra publicada. Queda anotada como deuda en el traspaso, no como exigencia aplicada. |
| 24 | Distribución de k bajo la nula con el ICC medido | **Diferida al §42.** Mismo motivo que la 4: se mide sobre el diseño, y el diseño se está por reconstruir. |

## `auditor-lookahead` — HAY FUGA, 10 exigencias

| # | Qué exigía | Destino |
|---|---|---|
| E1 | Mover la selección del universo al inicio de la ventana | **Diferida al §42**, con el punto exacto marcado en el código y clavado por el xfail. |
| E2 | Escribir el test de truncación ANTES de volver a correr | **Aplicada. Es el entregable más importante de este cierre.** Tres tests `xfail(strict=True)` sobre `operables`, `senales_sin_informacion` y `correr_estrategia`. Verificados uno por uno con `--runxfail`: los tres fallan **por la fuga y no por otra cosa**. (Uno fallaba por un atributo mal escrito y lo habría escondido el xfail; se corrigió.) |
| E3 | Sortear la señal de datos anteriores a `DESDE` | **Diferida al §42.** Docstring corregida: decía «distribución HISTÓRICA» y no lo es. |
| E4 | Introducir `RETARDO_IMPLEMENTACION` en las dos patas | **Diferida al §42**, clavada por el xfail. |
| E5 | Recalcular el interruptor sin futuro | **Diferida al §42.** Materialidad medida nula, y aun así se corrige por el código, no por la cifra. |
| E6 | Cablear `ErrorLookAhead` al riel | **Diferida al §42.** |
| E7 | Ampliar `CORTES` con cortes dentro del período de ajuste | **Diferida al §42.** F5 tiene efecto nulo en este archivo, pero el mecanismo está demostrado. |
| E8 | Republicar la cuenta sin F1 y F2 | **Aplicada en su parte urgente, diferida en su parte cara.** Urgente: las cifras se retiraron del `.md`, del `.json`, del endpoint y de la vista. Cara: republicar sin fuga es el §42. |
| E9 | Contar la vara climatológica en el registro de intentos | **Diferida al §45.** La ablación que la acompañaba **sí** se corrió. |
| E10 | Que los endpoints declaren fecha y huella del artefacto | **Aplicada.** `meta.artefacto` con nombre, mtime y sha256, y el contrato enmendado. |

---

## Una edición a dos dictámenes, declarada

Los dictámenes no se editan para que dejen de exigir algo. **Esto no es eso, y
va declarado igual.** Al escribir las erratas fechadas que las propias
exigencias 4, 10, 11 y 13 pedían, `DECISIONES.md` creció y **las líneas que dos
dictámenes citaban por número quedaron desplazadas** — que es literalmente el
error crónico que el proyecto ya tiene registrado y que
`tests/test_epistemico.py` vigila: *el acta que las cita las desplaza*. La suite
se puso roja por eso y por nada más.

Se actualizaron **sólo los punteros numéricos** en
`curador_epistemico.md` y `guardian_constitucion.md`, con una nota fechada al
comienzo de cada uno. **Ni una cifra, ni una exigencia, ni una palabra de los
dictámenes cambió.** Donde el puntero no se podía verificar solo, pasó a citar
la sección, que es estable: es la regla que este mismo error dejó escrita.

## Lo que este paso NO hizo

- **No reconstruyó la cuenta en papel.** Es la deuda grande y va con orden
  obligatorio: el test primero, que ya está.
- **No corrió la segunda vara pre-registrada** de la señal larga, porque pasa
  por la cuenta retirada. Mientras tanto, la regla §6 no se puede dar por leída.
- **No movió ningún registro de intentos.** Ni el del riel largo ni el
  asiático (352 / 358 intactos).
- **No verificó las cifras del mapa operable contra una segunda fuente.** El
  censo sigue siendo de un solo día.
