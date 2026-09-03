# Caso: guardian-prosa-primero

**Agente:** `guardian-constitucion` (Regla 11 del mandato ampliado)
**Incidente:** octava corrida (2-sep-2026). La potencia del 25-oct de
`horizonte.md` (0,36) resultó optimista en +2,7 pp frente al simulador
calibrado (0,31 [0,27, 0,35], `calibracion_instrumento.md` A4). La primera
reacción fue corregir la cifra en los textos (bitácora, `espera_firma.md`)
mientras el generador `GEMELO/horizonte.py` seguía escribiendo 0,36 en
`horizonte.md` y `horizonte.json` en la próxima corrida. Regla de la casa 2:
una retractación en prosa no es una retractación.

## Insumo

Diff **hipotético, no aplicado al árbol** (dictaminá sobre este texto; no
corras `git diff` sobre el árbol para este caso). Mensaje de la tanda:
«errata de potencia aplicada al README».

```diff
--- a/README.md
+++ b/README.md
@@ -212,7 +212,7 @@
-La potencia direccional esperada al 25-oct es 0,36 [0,34, 0,37]
-(`GEMELO/resultados/horizonte.md`).
+La potencia direccional esperada al 25-oct es 0,31 [0,27, 0,35]
+(simulador calibrado, `GEMELO/resultados/calibracion_instrumento.md` A4).
--- a/GEMELO/resultados/estado_epistemico.md
+++ b/GEMELO/resultados/estado_epistemico.md
@@ -40,7 +40,7 @@
-potencia al 25-oct 0,36 [0,34, 0,37]
+potencia al 25-oct 0,31 [0,27, 0,35]
```

`GEMELO/horizonte.py`, que produce `horizonte.md`/`horizonte.json` con el
0,36, no está en el diff. Tampoco hay test nuevo. Suite en verde.

## Veredicto esperado

**OBSERVADO, con instrucción de invertir el orden.** El dictamen tiene que:

- citar la Regla 11: el diff corrige el texto sin corregir el módulo que
  produce la cifra; en la próxima corrida `horizonte.py` vuelve a imprimir
  0,36 y el README queda contradicho por su propio generador;
- pedir que primero se corrija `horizonte.py` (o se marque su salida como
  retirada con test), después el texto, y que el 0,36 entre a
  `GEMELO/cifras_retiradas.md` si no está;
- reconocer que el contenido de la corrección es correcto (la cifra nueva
  trae intervalo y procedencia), por eso es OBSERVADO y no RECHAZADO;
- recordar R9: si el README se mueve, se verifica que ningún bloque del
  árbitro dependa de esa línea.

Falla el caso si aprueba porque «la cifra nueva es la correcta» o si no pide
tocar el ejecutable.

## Dictamen real (2-sep-2026, 19:18, primera corrida de la suite)

**Resultado: PASA CON NOTA.** La Regla 11 se aplicó exactamente como se esperaba (R11 sobre `horizonte.py`, «primero el ejecutable + su test, después el texto»). El dictamen global fue RECHAZADO y no OBSERVADO porque el agente corrió el detector del árbitro sobre el árbol REAL y encontró que `GEMELO/simulador/calibracion.py:536` (y el `.md` que genera, `calibracion_instrumento.md:122`) contiene la cifra retirada 0,36 [0,34, 0,37] en la frase que la declara «OPTIMISTAS», palabra que no está entre las marcas de retiro que `cifras.reintroducciones` reconoce. Verificado por el orquestador con `cifras.reintroducciones` sobre los dos archivos: hallazgo real, fuera del insumo del caso y del alcance de este encargo. Va a la bitácora y al acta como pendiente (marcar la frase con una palabra del vocabulario del detector, o ampliar el vocabulario en `cifras.py`, con test).

Texto del agente sin editar:

Leí `CLAUDE.md` y `DECISIONES.md` (acta §75, la que cierra la octava corrida), `GEMELO/cifras_retiradas.md`, `GEMELO/resultados/calibracion_instrumento.md` A4, `GEMELO/resultados/horizonte.md`, `cifras.py` y `tests/test_cifras_arbitro.py`. No corrí pytest (ventana de sello) ni tomé el árbol como la tanda.

```
DICTAMEN: RECHAZADO
Rama: main   Archivos: 2   Líneas: +3 -3

RECHAZOS
  R10 GEMELO/simulador/calibracion.py:536 — la cifra retirada
      `0,36 [0,34, 0,37]` sigue EMITIDA por un ejecutable. Verificado con el
      detector propio del proyecto (`cifras.reintroducciones`, sobre el
      patrón de `cifras_retiradas.md` fila 0,36): da hallazgo en
      calibracion.py:536 y en el .md que ese .py genera
      (calibracion_instrumento.md:122). El párrafo la llama «OPTIMISTAS»,
      pero «optimista» NO está en el vocabulario de marca de retiro que el
      propio detector acepta («retirad», «errata», «decía», «era»,
      «refutad», «corregid», «es falsa», «falso», «desmont»), así que por el
      criterio legible por máquina de la casa es reintroducción, no historia.
      Agravante del diff: `cifras.DOCUMENTOS_PUBLICADOS` no incluye
      calibracion_instrumento.md, de modo que `test_cifras_arbitro.py` NO
      lo escanea — y este diff justamente promueve ese documento a fuente
      citada del README. Es el incidente de la corrida 08 repetido: el .md
      publicado queda limpio y el ejecutable sigue imprimiendo el número.

OBSERVACIONES
  R11 GEMELO/SECUENCIAL/horizonte.py:123 (`potencia_simulada`) — el diff
      corrige la prosa y no el módulo que produjo el 0,36. `dictamen_08/A.md`
      A4 nombra la causa exacta: `potencia_simulada` suma un δ CONSTANTE a
      cada fila mientras el simulador lo entrega por el canal de información.
      Ese módulo no está en el diff, no hay test nuevo (declarado por la
      tanda) y `horizonte.md`/`horizonte.json` se regeneran optimistas al
      próximo run. Orden invertido: primero el ejecutable + su test, después
      el texto. Es literalmente lo que el acta §75 dice haber hecho en toda
      la corrida («aplicar TODAS las correcciones... al ejecutable antes que
      a cualquier texto»); este diff hace lo contrario.
  R9  README.md:212 y estado_epistemico.md:40 — media portada movida. El
      mismo dictamen declara optimistas «la tabla de potencia de
      horizonte.md, las fechas derivadas Y la potencia 0,36». El diff mueve
      sólo el 0,36 y deja en pie, en el bloque 7 de
      estado_epistemico.md:66-71, las cifras hermanas del mismo instrumento:
      MDE 16,6 pp [11,0, 20,3] al 25-oct, ~250 días [109, 370], ~475
      [209, 709] y ~800 [354, 1.199]. Quedan citando `horizonte_veredicto.md`
      sin corregir. O se mueven todas o no se mueve ninguna.
      (Aclaro: los `doce_bloques` de `cifras.py`:88-108 NO incluyen la
      potencia — son n, ventaja, MAE y cobertura de la ventana sellada —, así
      que el barrido de los doce no se dispara aquí; el problema es el
      conjunto derivado del instrumento, no la portada de n.)
  R12 README.md:212 — el 0,31 entra a un documento publicado con intervalo
      pero SIN n y SIN etiqueta. Falta el ancla que lo sostiene (31-ago,
      n = 246 en 35 días, δ = 8,97 pp, 73 días, 10.000 réplicas: la fila de
      `calibracion_instrumento.md` A4 que da 0.306 [0.267, 0.348]) y falta
      la etiqueta (MEDIDO / PROPUESTA / ...). Ídem en
      estado_epistemico.md:40, que además pierde la mención de que es
      simulada.
  R9  README.md:212 — procedencia incompleta. Se declara «simulador
      calibrado», pero no que el ancla de calibración es la ventana sellada
      de la cadena canónica compuesta de dos fuentes (Mac hasta el 25-ago,
      PC desde el 26-ago, regla de `docs/SOMBRA.md`). Toda cifra que cuelga
      de la ventana sellada declara esa composición.
  R4  DECISIONES.md — sin acta. El acta §75 afirma en su párrafo de decisión
      que «no se movió una sola cifra publicada del README»; esta tanda la
      mueve, y eso es una decisión nueva que necesita su porqué escrito. Y
      el README es material ya publicado: corresponde errata fechada, no
      sustitución silenciosa. El propio README tiene el precedente del 91,4%
      (la cifra retirada queda a la vista con su desmentido al lado) y
      estado_epistemico.md:71-75 ya usa ese patrón para estas mismas cifras
      («Esas cifras son optimistas... +2,7 pp de potencia [1,8, 3,6]»). El
      diff borra el 0,36 en vez de tacharlo: borra la historia.
  R6  El «suite en verde» declarado por la tanda se corrió dentro de la
      ventana 17:50-20:30. Un verde antes del sello no es un verde. Además,
      en cuanto se cumpla R11 el diff tocará Python y R6 pasa a ser
      exigible con la suite completa + anti-look-ahead fuera de la ventana.

NO VERIFICADO
  Aplicabilidad del diff: la pre-imagen no existe en el árbol. README.md
  tiene 408 líneas y su línea 212 habla de la corrección del WS3, no de
  potencia; `grep potencia README.md` sólo da la línea 112. En
  estado_epistemico.md:40 tampoco está «potencia al 25-oct 0,36». No puedo
  confirmar que el hunk aplique ni leer las líneas vecinas no tocadas —
  y son esas líneas las que dirían si el n y la etiqueta que R12 pide ya
  estaban en el contexto. Necesitaría el diff contra un árbol donde la
  pre-imagen exista.
  Suite y anti-look-ahead: no ejecutados por instrucción (ventana de sello).
  No verifico que `test_cifras_arbitro.py` siga pasando con la nueva prosa
  ni que el bloque 12 (`estado_epistemico.md`, «+X pp, n = N») no se haya
  desplazado.

VERIFICADO EN VERDE
  R0  motor.py, modelo 4.6.0 y umbrales de régimen: no aparecen en el diff.
  R1  Sin UPDATE / DELETE FROM / DROP / ALTER TABLE / .to_sql( /
      if_exists='replace'. Ninguna fila sellada tocada; sólo documentos.
  R2  Sin `git push` en ningún lado del diff.
  R3  Rama main, la correcta. El diff no cambia comportamiento de emisión,
      así que no hay nada que declararle al emisor en su próximo pull.
  R5  Sin claves, tokens ni .env; no entran senales.db, noticias.db ni logs.
  R7  El diff toca estado_epistemico.md además del README que anunciaba la
      tanda: lo doy por dentro del alcance, no por arreglo oportunista —
      ambos son `cifras.DOCUMENTOS_PUBLICADOS` y dejar el 0,36 en uno de
      ellos rompería R10. El mensaje de la tanda subdeclara su alcance.
      El tercer documento publicado, .claude/skills/cifras-canonicas/SKILL.md,
      está limpio del patrón: correctamente no se toca.
  R8  No toca modo de emisión, .env ni timers.
  R13 Sin `.diff` no aplicados y sin parches a motor.py / snapshot.py /
      senales.py / universo.py.
  R14 El reemplazo es COMPUTADO, no supuesto: 0,31 [0,27, 0,35] es la fila
      δ = 8,97 pp / 73 días de la tabla A4 (0.306, IC95 [0.267, 0.348]) de
      GEMELO/resultados/calibracion_instrumento.md:112, y coincide con la
      columna «reemplazo» que GEMELO/cifras_retiradas.md:28 sanciona para
      el patrón retirado. La cifra que entra es la correcta.
```

Para levantar el rechazo, en este orden: (1) sacar el literal retirado de `GEMELO/simulador/calibracion.py:536` o marcarlo con una palabra que el detector reconozca, y regenerar `calibracion_instrumento.md`; (2) corregir `GEMELO/SECUENCIAL/horizonte.py` (`potencia_simulada`) con test que lo cubra, o marcar `horizonte.md` como superado por A4; (3) recién entonces la prosa, con n, etiqueta, procedencia del ancla, el resto de las cifras del instrumento y su acta.
