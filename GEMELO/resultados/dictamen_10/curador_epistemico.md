# Dictamen del curador epistémico sobre la prosa de la corrida 10

> **Nota de la sesión de cierre, 7-sep-2026.** Al aplicar las exigencias de
> este mismo dictamen se escribieron erratas fechadas en `DECISIONES.md`, y eso
> **desplazó las líneas que este documento citaba por número** — que es
> exactamente el error crónico que el proyecto ya tiene registrado ("el acta que
> las cita las desplaza") y que `tests/test_epistemico.py` vigila. Se
> actualizaron **sólo los punteros numéricos**, dejando intactos el texto, las
> cifras y todas las exigencias: dos líneas del acta corrieron unas decenas de
> líneas hacia abajo, y las citas que apuntaban a ellas se movieron con ellas.
> Donde el puntero no se podía verificar solo, pasa a citar la **sección**, que
> es estable, que es justamente la regla que este error dejó escrita. Queda
> anotado en `aplicacion.md`.

Fecha y hora (reloj, `TZ=America/Santiago date`): 2026-09-07 00:51 -03.
Estado revisado: `main` en 8dd0e0d, 3 commits por delante de `origin/main`
(e368dad, 062287f, 8dd0e0d). Árbol limpio. Nada pusheado.

Documentos revisados (toda prosa nueva o modificada del diff):
  VISION.md · ESTADO.md · DECISIONES.md §80 (líneas 8138-8473)
  GEMELO/resultados/bitacora_10.md · GEMELO/resultados/espera_firma.md §39-41
  GEMELO/preregistro/senal_larga_v1.md · dinero/preregistro_dinero.md
  dinero/resultados/{cuenta_papel,senal_larga_v1}.md · docs/universo_operable.md
  api/CONTRATO.md enmienda 7.0.0
  Capa visual como texto publicado: frontend/src/vistas/{Rieles,RielDinero,Operable}.tsx,
  frontend/src/componentes/CifraConIntervalo.tsx, frontend/src/lib/tipos.ts,
  cadenas de api/main.py:875-1038
  Generadores: dinero/{senal_larga_reporte,cuenta_papel,mapa}.py

**VEREDICTO: RECHAZADO** (ocho bloqueantes; cinco tocan un ejecutable).

DICTAMEN: RECHAZADO
Documento: los de arriba   Oraciones revisadas: ~1.170 (conteo automático,
tablas y bloques de código excluidos; DECISIONES y espera_firma sólo en sus
líneas nuevas)   Sin etiqueta o con etiqueta que la cifra no sostiene: 14

## Lo que dice la máquina, contra lo que se contrastó todo

- `cifras.sellada()` (corte 28-ago, `excluir_cero`, dedup=True): n 238, 34 días,
  modelo 67,6 % [61,5, 73,3], base 58,0 % [51,6, 64,1], ventaja +9,7 pp (9,66)
  IC de día [-7,2, +26,6], t de clúster [-8,1, +27,4], p de permutación de día
  0,294, ICC 0,392, DEFF 3,55, n efectivo 67, McNemar 0,0455 (b 72, c 49),
  MAE 2,5204 vs 2,9751, ganancia +0,4547 [-0,087, +0,996] p de día 0,101,
  cobertura 92,9 %, ratio 2,19× [1,71, 2,78].
- El árbitro **no computa R2**. No hay función ni campo. La única fuente de la
  cifra R2 del campeón es `GEMELO/DISEÑO.md`:477-481 y `DECISIONES.md` §25.3,
  ambas del 26-ago, y `GEMELO/resultados/concentracion.md`:165-176 ya publicó su
  corrección (ver B1).
- `modo.py`: **titular**. Rama `main`, 3 por delante de `origin/main`.
  `systemctl --user`: 6 timers mki. Coincide con ESTADO:7-9.
- `GEMELO/relevo_asiatico.N_INTENTOS_ACUMULADO` 352, `backtest/veredicto_51.
  N_INTENTOS_51` 358, `dinero/registro_intentos.N_INTENTOS_RIEL_LARGO` 3.
  Coincide con ESTADO:44, bitácora:14 y DECISIONES §80.7.
- `pytest --collect-only`: **750 recolectados**, coherente con los "748 passed,
  2 xfailed" que declaran bitácora:8 y cierre:265.
- `@pytest.mark.red` sobre tests de producción: **6 en 2 archivos** (5 en
  `test_api.py`, 1 en `test_backtest.py`). Coincide con ESTADO:42-43 y
  bitácora:57; **no** con DECISIONES §80.2 (ver B6).
- `dinero/datos/cierres_congelados.csv`: 2011 filas más cabecera, sha256
  `69ca7283ae18fd37…` idéntico al del metadato y al citado en
  `docs/universo_operable.md`:9-11. Verificado.
- `cifras.reintroducciones()` sobre los diez documentos del diff: limpio salvo
  `GEMELO/preregistro/senal_larga_v1.md`:113. Sobre los `.py` del riel:
  `dinero/senal_larga_reporte.py`:374 (ver B2).
- La palabra **"confianza" no aparece** en ninguno de los archivos del alcance,
  ni en prosa ni en las cadenas de la API ni en la capa visual. Verificado uno a
  uno. Cumple.
- El camino de sellado no fue tocado: `motor.py`, `senales.py`, `snapshot.py`,
  `universo.py`, `version.py`, `alertas.py` no están en el diff. ESTADO:9 dice
  la verdad.

## Un punto por documento

**VISION.md.** Es el mejor documento de la corrida en estatus evidencial: la
cabecera declara que es INTENCIÓN, la §1 separa lo que Nicolás quiere de lo que
el proyecto hace, y las cifras de la §2.1 coinciden **una a una** con
`cifras.sellada()`, intervalo incluido. Falla en un solo lugar y es grave: la
cifra R2 de la §2.1 y la frase "bajo R2 se vuelve negativa" de la §5 (B1).

**ESTADO.md.** Coincide con la máquina en modo, rama, timers, registros de
intentos, tests marcados y cifras del árbitro. Aprendió la lección de la 09: no
clava el sello ("se lee de `./mki estado`, no de aquí"). Los negativos ocupan
más líneas que los positivos y la celda sobreviviente lleva su "**No autoriza
nada.**" pegado. No tengo bloqueante contra este archivo.

**DECISIONES.md §80.** Bien estructurada y con estatus por resultado. Dos fallas
de historia: publica "4 tests en 2 archivos" cuando la máquina tiene 6 (B6) y no
registra ni la suite de cierre ni la falla de siete tests que sí está en la
bitácora (B7). El acta es el documento de historia de la casa; que la bitácora
sepa algo que el acta no sabe invierte el orden.

**bitacora_10.md.** Cumple regla 3 con holgura: sección propia de "Errores
propios", sección propia para la falla no reproducida, y declara sin adorno que
el censo de red se quedó corto, que la fuga de selección la cazó el auditor y no
el orquestador, y que la vara del bloque 6 estaba mal elegida en el pre-registro
que el propio orquestador escribió horas antes. Falla en una errata menor
("dos commits", son tres; O5).

**GEMELO/preregistro/senal_larga_v1.md.** El orden pre-registro antes del cómputo
es verificable en git y se verificó. La errata §9 está fechada, dice qué cambia,
no borra lo anterior y declara que dos de las seis correcciones endurecen la
vara. Falla en dos citas: la cifra retirada 91,4 % (B2) y la saturación del PSR
en 1,0000 usada como diagnóstico y no como historia (O6).

**dinero/preregistro_dinero.md.** El criterio está escrito como número y la §2.1
publica la aritmética que lo vuelve incómodo antes de que nadie se la pida. La
cláusula 5 ("si el criterio se cumple, la primera reacción no es poner plata")
es la clase de frase que este rol existe para proteger. Falla en heredar la
cifra R2 (B1).

**dinero/resultados/cuenta_papel.md.** SIMULADO en el título, en el bloque de
cita y en la primera pantalla de la vista. Declara que lo medido es fricción y
no habilidad, declara que las filas del barrido no son comparables entre sí, y
la sección 3 publica su propia tasa de falsos positivos como la cifra más útil
de la página. Sin bloqueante.

**dinero/resultados/senal_larga_v1.md.** Publica el negativo con la misma
firmeza que un positivo: "L1 queda REFUTADA" es un encabezado, no una nota al
pie; "acierta MENOS que la climatología" está en negrita con su intervalo; las
tres celdas de dirección vacía se declaran vacías en vez de contarse como
empates; y "**Esto no autoriza nada**" viene con tres razones medidas. Falla en
tres lugares: la cifra retirada (B2), la vara pre-registrada que no se corrió y
no se declara (B3) y la cifra R2 heredada (B1).

**docs/universo_operable.md.** Separa explícitamente VERIFICADO POR LA MÁQUINA
de CONTEXTO NO VERIFICADO, y declara una tercera cosa que no afirma (que una
orden se llene). Falla por el estatus que su propio generador escribe en el JSON
hermano (B8).

**Capa visual.** `CifraConIntervalo` es el movimiento correcto: la regla dejó de
ser disciplina y pasó a ser un ejecutable que no puede renderizar un número sin
intervalo. `/dinero` lleva SIMULADO en el primer bloque con test que lo fija.
Falla en dos: la vista de rieles amputa la nota que el propio artefacto trae
(B4) y el componente afirma sobre proporciones algo que el diseño no ordena (B5).

## BLOQUEANTES

**B1. La cifra R2 del campeón circula como estado vigente bajo una convención
que el propio proyecto ya corrigió. TOCA DOS EJECUTABLES.**
Oraciones textuales:
- `VISION.md`:46-50: "La más dura ya golpeó al titular: **R2** —excluir la
  ventana 15–23 jul, que sostiene casi toda la ventaja— deja al campeón en
  n = 184, modelo 62.0 %, base 65.2 %, **ventaja −3.3 pp (p = 0.60)**: no
  pierde la ventaja, la vuelve negativa."
- `VISION.md`:96-97: "La única ventaja medida tiene un intervalo que contiene el
  cero, y bajo R2 se vuelve negativa."
- `api/main.py`:982-986 (cadena servida a `/api/rieles`, campo `que_lo_mata`,
  renderizada por `Rieles.tsx`:106-108): "R2 —excluir la ventana 15–23 jul— ya
  deja al campeón en ventaja −3,3 pp (p = 0,60): no pierde la ventaja, la vuelve
  negativa."
- `dinero/preregistro_dinero.md`:72-74: "una ablación de la ventana que sostiene
  la ventaja —del mismo tipo que R2 en `GEMELO/DISEÑO.md`, que hoy descalifica al
  propio campeón—".
- `dinero/senal_larga_reporte.py`:357-359 y su salida
  `dinero/resultados/senal_larga_v1.md`:140-142: "del tipo R2, que hoy
  descalifica al propio campeón del riel de medición".
Cifra del árbitro: **no existe**. `cifras.sellada()` no tiene R2. La fuente es
`GEMELO/DISEÑO.md`:477-481 y `DECISIONES.md` §25.3, ambas del 26-ago-2026.
Y `GEMELO/resultados/concentracion.md`:165-176 ya publicó la corrección, en el
propio repositorio: esa cifra está bajo convención **`estricta`**, no bajo la
publicada `excluir_cero`; comparando convención por convención, al 31-ago la
misma ablación da **+0,5 pp (n = 209, p = 1,000) bajo `estricta`** (el signo se
dio vuelta), −1,0 pp (n = 204) bajo `excluir_cero` y −1,9 pp (n = 209) bajo
`verificador`. El mismo documento escribe: "**«Mismo signo» —lo que decía la
versión anterior— es falso bajo `estricta`**" y "lo que SÍ sobrevive en las tres
convenciones, sin excepción: la cifra sigue sin ser distinguible de cero (ningún
p se acerca a 0.05)". Además, tras D1 (3-sep, regla de deduplicación firmada,
ancla n = 238) la ablación **nunca se recomputó**.
Etiqueta correcta: el punto −3,3 pp es MEDIDO el 26-ago bajo convención
`estricta` y ancla derogada, **RETIRADO como descripción del estado vigente**;
lo afirmable hoy es "la ventaja del campeón excluyendo 15–23 jul no se distingue
de cero en ninguna de las tres convenciones, y bajo la regla firmada no está
recomputada". Los verbos "la vuelve negativa" y "descalifica" dicen más que la
cifra: p = 0,60. Es exactamente el patrón que creó este rol.

**B2. Cifra RETIRADA reintroducida, y ofrecida desde un ejecutable. TOCA UN
EJECUTABLE.**
Oraciones textuales:
- `dinero/senal_larga_reporte.py`:373-374 (EJECUTABLE, genera el reporte
  publicado): `L.append("  midió la contaminación en el riel de medición (198
  filas comunes,")` / `L.append("  91,4 % de coincidencia, máximo 31,2 pp) y va
  en dirección optimista.")`
- Su salida, `dinero/resultados/senal_larga_v1.md`:154-157.
- `GEMELO/preregistro/senal_larga_v1.md`:111-116: "sobre 198 filas comunes con
  el track record sellado, la reconstrucción de hoy coincide en el **91.4 %** y
  difiere en **17**, con un máximo de **31.2 pp**".
Registro: `GEMELO/cifras_retiradas.md`, patrón `91[,.]4\s?%`, retirada el
**2026-09-01**, acta §68 y `espera_firma.md` §11a, reemplazo **100 % sobre 214
filas, 0 diferencias** con la clave correcta (`sesion_objetivo`, no
`["fecha","ticker"]`). El propio §11 la llama "una cifra ya refutada".
Etiqueta correcta: RETIRADA (1-sep-2026). Un número retirado que sigue ofrecido
en el código vuelve a circular en cada corrida del reporte: es la regla de la
casa y es bloqueante por sí sola.
**Nota sobre el guardián mecánico, que hay que anotar aparte:**
`cifras.reintroducciones()` **no caza** la del `.md` de resultados. La exención
de ±2 líneas de `cifras._tiene_marca_de_retiro` se dispara por la palabra
"corregida" de la línea 158, que habla de otro tema (supervivencia). Es un falso
negativo del instrumento, no una marca de retiro. La hipótesis de la ventana de
±2 líneas es que la marca habla de la cifra que está al lado; acá no.

**B3. Una de las dos varas pre-registradas no se evaluó, y ningún documento lo
dice. TOCA UN EJECUTABLE.**
`GEMELO/preregistro/senal_larga_v1.md`:76-82 declara **dos** varas: (1) predecir
cero y (2) "**La línea base aburrida del bloque 4a:** aporte fijo semanal a
`SMH`. La vara económica, a la que se llega pasando la señal por
`dinero/decision.py` y la cuenta en papel". La segunda **no se corrió**:
`grep` sobre `dinero/senal_larga.py` y `dinero/senal_larga_reporte.py` no
devuelve una sola evaluación contra la línea base, y las "24 comparaciones" de
la página son 3 especificaciones × 2 horizontes × 2 varas (**cero y
climatología**) × 2 métricas.
Oración textual que lo tapa, `dinero/senal_larga_reporte.py`:214-215
(EJECUTABLE) y su salida `dinero/resultados/senal_larga_v1.md`:55-56: "El
pre-registro §5 declaraba dos varas — predecir cero y la línea base aburrida — y
la de arriba es la que estaba declarada." Dice cuál está; no dice que la otra no
se corrió.
Por qué importa y no es cosmético: la regla de refutación
`preregistro/senal_larga_v1.md` §6 tercera viñeta ("**Si ninguna de las tres
supera a ninguna de las dos varas**") y el criterio **M4** de
`dinero/preregistro_dinero.md`:93-96 están escritos sobre las dos varas. Con una
sin correr, ni la refutación ni M4 se pueden leer como leídos.
Etiqueta correcta: la vara 2 es **PENDIENTE, no corrida en esta corrida**, y
tiene que decirlo el reporte generado, no sólo un lector atento del §5.

**B4. La capa visual publica la única celda sobreviviente sin su tamaño, sin su
intervalo y sin la nota que el propio artefacto trae. TOCA UN EJECUTABLE.**
Oración textual, `frontend/src/vistas/Rieles.tsx`:59-68: "{ganan_a_la_
climatologia} de {celdas} celdas le ganan a la climatología causal, sobre
{contrastes} contrastes." seguido de "L1 —el contagio directo, la forma simple
de la hipótesis— queda REFUTADA por su propia regla pre-registrada."
Cifra que la sostiene: L2 a 60 días, ganancia de MAE **+0,229 pp
[+0,054, +0,424]** sobre una base de 11,9 pp, es decir del orden del **2 %
relativo**, contra una vara **agregada después de ver el resultado**, en una
página de 24 contrastes.
El artefacto ya trae la frase correcta:
`dinero/resultados/senal_larga_v1.json`, `resumen.nota` = "Lo que sobrevive a la
climatología causal es una celda, con una mejora del orden del 2 % relativo, y
no autoriza nada." `frontend/src/lib/tipos.ts`:467 declara el campo `nota`. La
vista **no lo renderiza**. Idéntico con `cuenta_en_papel.advertencia`
(tipos.ts:460), que tampoco se renderiza aunque su contenido se reescribió a
mano al lado.
Etiqueta correcta: PROPUESTA, post-hoc, con la magnitud y el intervalo a la
vista. Un lector de `/rieles` se lleva "1 de 6 le ganan" y el "REFUTADA" de L1
en la misma frase, sin saber de qué tamaño es el 1.

**B5. El componente de honestidad ordena dos cantidades que el diseño no ordena.
TOCA UN EJECUTABLE.**
Oración textual, `frontend/src/componentes/CifraConIntervalo.tsx`:75-79: el
componente emite, **sin condición sobre el tipo de cifra**, "El intervalo
contiene el cero: la diferencia no se distingue de cero." o "**El intervalo no
contiene el cero.**"
`api/main.py`:952-957 le pasa "acierto del modelo" 67,6 % [61,5, 73,3] y
"acierto de la base" 58,0 % [51,6, 64,1], que son **proporciones con Wilson**.
El intervalo de Wilson de una tasa de acierto no puede contener el cero nunca;
que no lo contenga no es información. La pantalla queda diciendo, debajo del
67,6 % del modelo, "El intervalo no contiene el cero", que es exactamente lo que
un lector va a leer como "el efecto existe" en la misma tarjeta donde la ventaja
de verdad, +9,7 pp [-7,2, +26,6], dice que sí lo contiene.
La regla 5 de esta casa se escribió por esto y el orquestador ya la rompió dos
veces. Y `tests/test_dinero.py`:455-459 fija la cadena por contrato, así que la
corrección va al ejecutable y al test en la misma pasada.
Etiqueta correcta: la frase sólo corresponde a **diferencias**; sobre una
proporción, o no va, o dice contra qué se compara (la base, no el cero).

**B6. El acta publica un censo que la máquina desmiente y no lleva errata.**
Oración textual, `DECISIONES.md` §80.2, líneas 8218-8226: "**Lo medido, con el
instrumento arreglado:** tocan la red **4 tests en 2 archivos** —
`test_api.py::{test_comparador_base100, test_detalle_perfil,
test_envelope_en_todos_los_endpoints}` y
`test_backtest.py::test_la_corrida_sella_semilla_y_alpha_del_bootstrap`. Dos
censos independientes (suite completa y archivo por archivo) coinciden."
Máquina: `@pytest.mark.red` sobre tests de producción son **6 en 2 archivos**
(`test_api.py`:28, 45, 87, 177, 196 y `test_backtest.py`:595). Los dos nuevos
llevan comentario propio: "censo del 7-sep-2026: el auditor los cazó; el de la
suite completa no". `ESTADO.md`:42-43 y `bitacora_10.md`:57 ya dicen 6.
El acta es el documento de historia y quedó con la cifra anterior al hallazgo,
sin errata fechada. Donde el documento y la máquina no coinciden, manda la
máquina.

**B7. El acta no registra el cierre de la suite ni la falla de siete tests que
la bitácora sí registra.**
`DECISIONES.md` §80 abre (línea 8140) con "Suite al abrir: **650 passed, 2
xfailed** en 323,63 s" y **no vuelve a mencionar la suite**: ni los 748 del
cierre, ni las siete fallas del primer intento de commit. `grep` sobre las 336
líneas nuevas no devuelve "748" ni "7 fallas" ni "no se reprodujo".
`bitacora_10.md`:232-249 lo declara completo, incluida la deuda de que el
listado se perdió. El commit 8dd0e0d agregó esas 19 líneas **sólo a la
bitácora**.
Regla 3: el negativo tiene que ocupar el mismo lugar que el positivo, y el lugar
del positivo ("650 passed") es el encabezado del acta. Etiqueta correcta:
OBSERVADO y no reproducido, con su fecha, en §80.

**B8. El mismo generador rotula el mismo artefacto con dos estatus
incompatibles, y el permisivo es el que llega al público. TOCA UN EJECUTABLE.**
`dinero/mapa.py`:95 escribe en el `.md`: "> **SIMULADO / PROPUESTA.** No hay
cuenta de corredora abierta y este documento no es una recomendación de compra."
`dinero/mapa.py`:250 escribe en el JSON hermano: `"estatus": "MEDIDO"`.
`api/main.py`:917-925 sirve ese JSON tal cual y
`frontend/src/vistas/Operable.tsx`:151 lo renderiza como **badge de estatus de
toda la vista `/operable`**: el lector ve la palabra MEDIDO arriba de una
pantalla titulada "La cadena, y qué parte de ella se puede comprar".
La vista sí dice "no es una recomendación de compra y no hay cuenta de corredora
abierta" (:157) y eso ayuda, pero el rótulo evidencial que la encabeza
contradice al del documento fuente. El encargo pide que el riel de dinero se
declare SIMULADO en todo lugar donde un lector pueda entender otra cosa.
Etiqueta correcta: partir la afirmación. Los precios y los 36 tickers son
MEDIDO al 2026-09-04 (el `.md` ya lo dice bien en su "Frase con estatus
evidencial"); el mapa como objeto del riel de dinero es SIMULADO / PROPUESTA. El
JSON tiene que llevar los dos campos y la vista tiene que mostrar el segundo.

## OBSERVACIONES

O1. `dinero/senal_larga_reporte.py`:352-355 (EJECUTABLE) y su salida
`dinero/resultados/senal_larga_v1.md`:135-138, más `DECISIONES.md` §80.8:
"La cuenta en papel del bloque 4 midió que **un diseño así** produce un
intervalo que excluye el cero en el **21 % de los casos** con una señal que no
tiene información." Los dos diseños no son el mismo: el 21 % se midió sobre 24
comparaciones semanales de carteras que comparten sorteo, instrumentos y flujo
de caja, con bootstrap de bloques de 4 semanas; la página de la señal larga son
24 contrastes sobre 5.131 y 4.851 filas con bootstrap de bloques por fecha de
emisión. La tasa de tipo I de esa página **no está medida**. El error empuja en
dirección conservadora (se usa contra el propio resultado), pero sigue siendo
una cantidad que el diseño no ordena. En `dinero/preregistro_dinero.md`:38-40 y
:123-125 el mismo 21 % se usa **bien**, porque ahí sí se habla de la cuenta en
papel. Etiqueta: PROPUESTA, con la frase "una tasa medida en otro diseño, no en
éste".

O2. `api/main.py`:1020-1022 (EJECUTABLE) sirve `"sigma_dif_semanal_pp": 2.54`
como literal escrito a mano, no leído de `cuenta_papel.json`, y **sin
intervalo**. La propia enmienda que esta corrida escribió,
`api/CONTRATO.md`:317-321, dice: "cuando lleva un estimador puntual, **lleva su
intervalo en el mismo objeto**. Un número sin intervalo no viaja por esta API si
es un estimador." Una σ medida sobre 156 semanas es un estimador. Y un literal
duplicado se desincroniza en la próxima corrida de la cuenta.

O3. `api/CONTRATO.md`:344-347 dice que `/api/rieles` sirve del árbitro "n, días,
ventaja con su IC de clúster de día, **McNemar**, cobertura". `api/main.py`:
940-980 **no sirve McNemar**: el dict `medicion` tiene `muestra`, cuatro
`cifras`, `cobertura_80_pct`, `n_efectivo`, `icc`, `deff` y nada más. Manda la
máquina: errata en el contrato, o falta el campo.

O4. `api/main.py`:1009 pasa `larga.get("resumen")` y descarta
`larga["estatus"]`, que vale **"PROPUESTA"**. El contrato recién enmendado
(`api/CONTRATO.md`:317-319) promete "**cada objeto lleva su `estatus`**". El
estatus de la señal larga no llega nunca a la UI: la vista sólo hereda el
"SIMULADO" del riel entero, que no es lo mismo.

O5. `GEMELO/resultados/bitacora_10.md`:267: "Árbol commiteado en `main`, en
**dos commits**". Máquina: tres (e368dad, 062287f, 8dd0e0d), y el tercero
modifica la propia bitácora en la que está escrita la frase. Errata.

O6. `GEMELO/preregistro/senal_larga_v1.md`:109-110 ("igual que el proyecto hizo
en el WS2b cuando el PSR saturó en 1.0000 a 30 días") y
`dinero/resultados/senal_larga_v1.md`:113-115 / `senal_larga_reporte.py`:314
("el mismo error que publicar un PSR saturado en 1,0000 como si fuera certeza").
`GEMELO/cifras_retiradas.md` retiró el 2-sep el patrón `satura[n]? en 1,0000`:
`dictamen_08/A.md` A3 estableció que la saturación era **defecto de unidades**,
no un hecho de muestra corta, y con la unidad correcta da 0,95-0,96. La lección
que se cita ("no publicar un número saturado como certeza") sobrevive; el
diagnóstico que se cita como razón, no. El regex no lo caza por la conjugación
("saturó", "saturado"), así que el guardián mecánico no lo va a atrapar.

O7. `dinero/resultados/senal_larga_v1.md`:54-56 y `senal_larga_reporte.py`:
214-215: "El pre-registro §5 declaraba dos varas — predecir cero y la línea base
aburrida". El §5 declaró además, en su último párrafo (:84-86), la **climatología
para DIRECCIÓN**. Lo agregado post-hoc es la climatología de **magnitud** (la
media de la etiqueta en el ajuste). La frase mete las dos en la misma bolsa y
hace parecer post-hoc algo que estaba pre-registrado, lo que confunde en la
dirección opuesta a la habitual pero confunde igual.

O8. `tests/test_dinero.py`:371-377, tupla `DOCUMENTOS_DEL_RIEL` del test de la
palabra prohibida: incluye VISION, universo_operable, preregistro_dinero,
cuenta_papel y el pre-registro de la señal larga, y **no incluye
`dinero/resultados/senal_larga_v1.md`**, que es el documento más consecuente que
produjo la corrida. Hoy está limpio (verificado a mano); mañana no hay quien lo
verifique.

O9. `frontend/src/vistas/Rieles.tsx`:41-52 y
`CifraConIntervalo.tsx`:55: el componente antepone `+` a todo valor positivo, así
que las tasas de acierto se muestran como "**+67.6 %**" y "**+58.0 %**". Un
signo de más sobre una proporción se lee como diferencia.

O10. `dinero/cuenta_papel.py`:146 escribe en duro la fecha "el 2026-09-04" en la
prosa generada ("su acción cerró por encima del techo del presupuesto el
2026-09-04"), mientras el resto del bloque toma las fechas del congelado. Es una
fecha, no una cifra, pero es la misma clase de literal que se desincroniza.

## EXIGENCIAS

Numeradas y aplicables sin interpretar. **[EJ]** marca la que toca un ejecutable.
Las que tocan un ejecutable van al ejecutable **antes** que al texto, y el texto
se regenera.

1. **[EJ] `api/main.py`:982-986.** Sobra "R2 —excluir la ventana 15–23 jul— ya
   deja al campeón en ventaja −3,3 pp (p = 0,60): no pierde la ventaja, la vuelve
   negativa." Poner: "R2, excluir la ventana 15–23 jul, ya golpeó al titular: la
   ventaja del campeón sin esa ventana **no se distingue de cero en ninguna de
   las tres convenciones** (`concentracion.md` A3; al 31-ago: +0,5 pp n = 209
   bajo `estricta`, −1,0 pp n = 204 bajo `excluir_cero`, −1,9 pp n = 209 bajo
   `verificador`; ningún p cerca de 0,05). Bajo la regla de deduplicación firmada
   el 1-sep **no está recomputada**. La valla no se bajó." (B1)

2. **`VISION.md`:46-50.** Sobra "deja al campeón en n = 184, modelo 62.0 %, base
   65.2 %, **ventaja −3.3 pp (p = 0.60)**: no pierde la ventaja, la vuelve
   negativa. Ese resultado está publicado y la valla no se bajó." Poner el mismo
   texto de la exigencia 1, más la nota de que la cifra de −3,3 pp que el
   proyecto publicó el 26-ago está bajo convención `estricta` y ancla derogada.
   Y `VISION.md`:96-97: sobra "y bajo R2 se vuelve negativa"; poner "y bajo R2
   deja de distinguirse de cero en las tres convenciones, sin recomputar bajo la
   regla firmada". (B1)

3. **[EJ] `dinero/senal_larga_reporte.py`:357-359** y `dinero/preregistro_
   dinero.md`:72-74. Sobra "que hoy descalifica al propio campeón". Poner "que
   hoy el propio campeón no pasa: sin esa ventana su ventaja deja de
   distinguirse de cero (`concentracion.md` A3; sin recomputar bajo la regla
   firmada)". Regenerar `dinero/resultados/senal_larga_v1.md`. (B1)

4. **[EJ] `dinero/senal_larga_reporte.py`:372-374.** Sobra "midió la
   contaminación en el riel de medición (198 filas comunes, / 91,4 % de
   coincidencia, máximo 31,2 pp) y va en dirección optimista." Poner: "midió esa
   contaminación en el riel de medición y con la clave correcta
   (`sesion_objetivo`) dio **100 % de coincidencia sobre 214 filas, 0
   diferencias**; el 91,4 % que ese documento todavía publica está **RETIRADO**
   desde el 1-sep-2026 (`cifras_retiradas.md`, `espera_firma.md` §11a) y el
   artefacto quedó stale. Eso **no** prueba que la fuente no revise su historia:
   sólo que no la revisó en el tramo auditable de 2026." Regenerar el reporte.
   (B2)

5. **`GEMELO/preregistro/senal_larga_v1.md`:111-116.** Mismo reemplazo que la
   exigencia 4, en prosa, con marca de retiro inline. El archivo es un
   pre-registro congelado: la corrección va como **errata fechada** en el §9, no
   reescribiendo el §7. (B2)

6. **`GEMELO/cifras_retiradas.md`.** Añadir a la fila del `91[,.]4\s?%` la nota
   de que la exención de ±2 líneas de `cifras._tiene_marca_de_retiro` produjo un
   falso negativo en `dinero/resultados/senal_larga_v1.md`:157 (la marca
   "corregida" de :158 habla de otro tema). Y anotar el patrón conjugado de la
   saturación del PSR ("saturó", "saturado"), que hoy no se caza. (B2, O6)

7. **[EJ] `dinero/senal_larga_reporte.py`:213-216.** Falta, después de "y la de
   arriba es la que estaba declarada", la oración: "**La segunda vara declarada
   en el §5 —la línea base aburrida, aporte fijo semanal a `SMH`, a la que se
   llega pasando la señal por `dinero/decision.py` y la cuenta en papel— NO se
   evaluó en esta corrida.** Mientras no se evalúe, la regla de refutación del
   §6 («si ninguna de las tres supera a ninguna de las dos varas») y el criterio
   M4 de `dinero/preregistro_dinero.md` **no se pueden dar por leídos**." La
   misma oración va en `ESTADO.md`:45, junto a la ablación R2 que ya está
   declarada como no hecha, y en `bitacora_10.md`:255-256. (B3)

8. **[EJ] `frontend/src/vistas/Rieles.tsx`:56-70.** Falta renderizar
   `r.senal_larga.nota` (que ya viaja y ya está tipada en `tipos.ts`:467) y falta
   la magnitud con su intervalo. Bloque nuevo: la frase de L1 REFUTADA se
   conserva textual; debajo, "La celda que sobrevive es L2 a 60 días: ganancia de
   MAE **+0,229 pp [+0,054, +0,424]** sobre una base de 11,9 pp, del orden del
   2 % relativo, contra una vara **agregada después de ver el resultado**." y
   después `{r.senal_larga.nota}`. Renderizar también
   `r.cuenta_en_papel.advertencia` en vez de reescribirla a mano. (B4)

9. **[EJ] `frontend/src/componentes/CifraConIntervalo.tsx`:54, :75-79.** Sobra
   que la frase se emita para toda cifra. Agregar una prop explícita (por
   ejemplo `esDiferencia?: boolean`, sin valor por defecto permisivo) y emitir
   "El intervalo contiene el cero…" / "El intervalo no contiene el cero." **sólo
   cuando la cifra es una diferencia**. Para una proporción, emitir en su lugar
   contra qué se compara, o nada. `api/main.py`:948-961 marca cuáles de las
   cuatro cifras del riel de medición son diferencias (las dos últimas) y cuáles
   no (las dos primeras). `tests/test_dinero.py`:455-459 se corrige en la misma
   pasada: dejar el código corregido con el test viejo es peor que el estado
   actual. (B5)

10. **`DECISIONES.md` §80.2, líneas 8218-8226.** Sobra "tocan la red **4 tests en
    2 archivos**" con su lista de cuatro. Poner: "tocan la red **6 tests en 2
    archivos**: cuatro los halló el censo del 6-sep
    (`test_api.py::{test_comparador_base100, test_detalle_perfil,
    test_envelope_en_todos_los_endpoints}` y
    `test_backtest.py::test_la_corrida_sella_semilla_y_alpha_del_bootstrap`) y
    **dos más los halló el `auditor-lookahead` el 7-sep corriendo la suite en
    otro orden** (`test_api.py`:45 y :87), que es exactamente el «piso, no
    techo» que el propio bloque declaró." (B6)

11. **`DECISIONES.md` §80, después de la línea 8143.** Falta el párrafo de
    cierre de la suite: "**Suite al cerrar: 748 passed, 2 xfailed** en 332,74 s.
    **Y un episodio que hay que dejar escrito: el primer intento del commit de
    cierre disparó el hook y la suite salió con 7 fallas, entre ellas
    `test_vigia.py::test_epilogo_retracta_tras_sello_tardio`. NO se
    reprodujeron** en cuatro corridas completas posteriores. No se conoce la
    causa y no se inventa una; la hipótesis más probable es la misma limitación
    que motiva el bloque 0 (la suite toca la red, y esa noche la fuente devolvió
    series vacías de forma intermitente al menos dos veces). **El listado
    completo se perdió** porque el hook escribe a la salida estándar del `git
    commit`: queda como deuda." (B7)

12. **[EJ] `dinero/mapa.py`:248-252.** Sobra `"estatus": "MEDIDO"` como estatus
    único del JSON. Poner dos campos: `"estatus": "SIMULADO / PROPUESTA"` (el
    del artefacto como objeto del riel de dinero, igual que el `.md` que el mismo
    módulo escribe en :95) y `"estatus_de_los_precios": "MEDIDO al {hasta}"`.
    `frontend/src/vistas/Operable.tsx`:151 muestra el primero en el badge de la
    vista y el segundo junto a la tabla de precios. Regenerar el mapa. (B8)

13. **[EJ] `dinero/senal_larga_reporte.py`:352-355.** Sobra "La cuenta en papel
    del bloque 4 midió que un diseño así produce un intervalo que excluye el cero
    en el **21 % de los casos con una señal que no tiene información**." Poner:
    "La cuenta en papel del bloque 4 midió, **sobre otro diseño** (24
    comparaciones semanales de carteras que comparten sorteo, instrumentos y
    flujo de caja), que un intervalo excluye el cero el 21 % de las veces con una
    señal sin información. **La tasa de tipo I de ESTA página, con bloques por
    fecha de emisión sobre 5.131 y 4.851 filas, no está medida.** El 21 % se cita
    como orden de magnitud, no como su tasa." Misma corrección en
    `DECISIONES.md`:8482. (O1)

14. **[EJ] `api/main.py`:1020-1022.** Sobra el literal `"sigma_dif_semanal_pp":
    2.54`. Leerlo del artefacto (`cuenta_papel.json`) y **acompañarlo de su
    intervalo**, como exige la enmienda del propio contrato; si el artefacto no
    lo trae, computarlo en `dinero/cuenta_papel.py` y sellarlo ahí. Mientras no
    haya intervalo, el campo no viaja: es un estimador. (O2)

15. **`api/CONTRATO.md`:344-347.** Sobra "McNemar" de la lista de lo que
    `/api/rieles` sirve del árbitro, o se agrega `mcnemar_p` a
    `api/main.py`:948-961. Manda la máquina; elegir una de las dos y declarar
    cuál. (O3)

16. **[EJ] `api/main.py`:1009.** Sobra `larga.get("resumen")` a secas. Poner
    `{"estatus": larga.get("estatus"), **(larga.get("resumen") or {})}` y
    extender `tipos.ts`:462-468 con `estatus: EstatusEvidencial`, para que la
    promesa del contrato ("cada objeto lleva su estatus") sea cierta también para
    la señal larga. (O4)

17. **`GEMELO/resultados/bitacora_10.md`:267.** Sobra "en dos commits". Poner "en
    tres commits: el pre-registro del bloque 6 antes del cómputo (`e368dad`), el
    resto después (`062287f`), y un tercero (`8dd0e0d`) que agrega a esta misma
    bitácora la falla de siete tests que no se reprodujo". (O5)

18. **`tests/test_dinero.py`:371-377.** Falta
    `"dinero/resultados/senal_larga_v1.md"` en `DOCUMENTOS_DEL_RIEL`. Y falta,
    en `dinero/resultados/senal_larga_v1.md`:54-56 y en
    `senal_larga_reporte.py`:214, aclarar que el §5 también declaró la
    climatología **para dirección**: lo post-hoc es la climatología de
    **magnitud**. (O7, O8)

## ZONAS CIEGAS

- **No regeneré ninguno de los tres artefactos.** `python -m dinero.mapa`,
  `dinero.cuenta_papel` y `dinero.senal_larga_reporte` escriben en el árbol y el
  primero descarga. No puedo afirmar que los `.md` y `.json` publicados sean la
  salida actual del código: comparé prosa contra las cadenas de los generadores,
  no salida contra salida.
- **Las cifras de la señal larga no tienen árbitro.** Los MAE, CRPS, tasas de
  dirección e intervalos de bloques de las dos tablas (incluida la celda
  sobreviviente +0,229 [+0,054, +0,424]) los acepté del propio JSON y del
  reporte. `cifras.py` no cubre este riel y no recomputé nada. Toda mi lectura de
  la §6 es sobre coherencia interna y etiqueta, no sobre la aritmética.
- **Las cifras de la cuenta en papel, igual.** Verifiqué que los 5 de 24 se
  cuentan en la tabla y que los rangos de comisión coinciden con sus filas; no
  recorrí la contabilidad ni el bootstrap.
- **No corrí la suite.** Sólo `pytest --collect-only`: 750 recolectados, que es
  coherente con "748 passed, 2 xfailed". No sé si está verde hoy, y la corrida
  declara una falla de siete tests que no se reprodujo, así que el verde de anoche
  no me sirve de garantía. Tampoco corrí `npm run build`.
- **No verifiqué la ausencia de fuga de la señal larga.** El gate de 56 tests del
  `auditor-lookahead` existe; que las seis correcciones de la errata §9 sean
  suficientes es dictamen del auditor, no mío, y las acepté.
- **No revisé línea por línea** `dinero/decision.py`, `contabilidad.py`,
  `precios.py`, `universo_dinero.py` ni `derivacion.py`: sólo grepeé sus cadenas
  de salida y sus literales numéricos. Un overclaim dentro de una docstring que
  nadie publica se me pasa.
- **Las horas de la bitácora no las contrasté contra mtimes.** Los artefactos de
  la corrida están todos commiteados, así que sus mtimes son del checkout y no
  sirven de testigo. Verifiqué sólo la afirmación estructural: el 6-sep-2026 fue
  domingo (`date`), así que "fuera de la ventana" es cierto.
- **El piso de latencia (p50 8,79 ms / p99 36,76 ms) de VISION §3** lo leí de
  `GEMELO/MICRO/piso_de_latencia.md`:34-42 y `DECISIONES.md`:3785. No lo remedí y
  no puedo decir bajo qué condiciones se midió.
- **El registro de intentos del riel largo (3)** lo leí del módulo. No hay libro
  mayor independiente que confirme que fueron tres configuraciones y no más;
  descansa en la declaración del pre-registro.
- **El curador no escribe en el árbol.** El dictamen lo volcó la sesión de cierre
  el 7-sep-2026, textual, sin editar ninguna exigencia.
