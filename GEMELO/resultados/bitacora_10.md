# Bitácora de la décima corrida — el riel de dinero

**6/7-sep-2026, nocturna y sin supervisión.** Encargo en `~/encargo.md`. Los
dictámenes del guardián y del curador NO corren en esta sesión: quedan para
`~/cierre.md` con contexto limpio.

- Suite al abrir: **650 passed, 2 xfailed** en 323,63 s (6-sep 22:19).
- Suite al cerrar: **748 passed, 2 xfailed** en 332,74 s. **+98 tests**: 16 de
  la guarda de red, 26 del riel de dinero y la capa visual, 56 del gate de
  causalidad que escribió el auditor. Ninguno preexistente se volvió rojo.
- Ventana de sellado: **no se cruzó**. La corrida arrancó domingo 22:18 hora de
  Chile —día no hábil, fuera de la franja 17:50–20:30— y la hora se leyó de
  `date`, no se estimó.
- Registro de intentos del gap asiático: **NO se tocó** (352 / 358).
- Nada se pusheó.

## Pre-mortem del `director-programa`, antes del bloque 1

Predijo que el **bloque 4** sería el que fallara, y acertó el mecanismo exacto:
«el proyecto no guarda precios; el modo de falla es que un agente redefina "ya
guardados" como "el cache que yo mismo creé" y lo llame riel de dinero». Se
resolvió declarándolo (§Bloque 4). Marcó además cuatro instrucciones del propio
encargo como defectuosas; **tres se acataron y una se acató en parte**:

| Objeción | Qué se hizo |
|---|---|
| El hook que corre una suite mutilada y la reporta verde | Acatada: el commit se **rechaza** dentro de la ventana; el opt-out declara VERIFICACIÓN PARCIAL |
| Medir los tres juegos sobre la cuenta en papel es elegir la vara mirando el tiro | Acatada: los tres se congelaron antes, se publican sin ranking, el default lo fija una regla escrita |
| Mover `N_INTENTOS_ACUMULADO` mezcla familias y dispara los doce bloques | Acatada: registro propio del riel largo, vínculo declarado, decisión de fusión a firma (§41) |
| «Suite completa antes de empezar» contradice «ninguna descarga en la ventana» | Acatada de hecho: se arrancó fuera de la ventana |
| La frase de `VISION.md` se publica como capacidad | Acatada: va rotulada como INTENCIÓN, con el estado real al lado |

Consideró el bloque 2 «rama lateral cómoda» y recomendó cerrar en 0-1-3. **Se
hizo el encargo completo, 0 a 7.** Queda anotado que el director habría cortado
antes, y que la corrida no lo siguió en eso.

## Bloque 0 — la deuda de la 09. **Cerrado.**

Marcador `red` (`tests/conftest.py`), `scripts/guarda_red.sh` con reloj falso,
y la regla aplicada en el hook y en `./mki tests`. 16 tests de la guarda.

**El hallazgo, y es un error propio corregido a tiempo:** la primera versión de
la guarda espiaba `socket.socket.connect` y el censo de la suite entera salió
**vacío** — cero tests tocando la red, en una suite que descarga de Yahoo. La
causa: **yfinance 1.5.1 habla por `curl_cffi`, o sea libcurl, en C**, y el
módulo `socket` de Python no ve nada. Un instrumento que mide donde el tráfico
no pasa informa paz. Se agregó el gancho sobre `curl_cffi.Session.request`.

**Medido con el instrumento arreglado:** 4 tests en 2 archivos, en dos censos
independientes (suite completa y archivo por archivo).

**Y el censo era un piso, no un techo, exactamente como se declaró.** Horas
después el `auditor-lookahead`, corriendo la suite en otro orden, encontró
**dos más** —`test_paridad_regimen` y `test_paridad_betas`— que mis dos censos
no vieron porque yfinance cachea en memoria dentro del proceso y el orden los
enmascaró. La guarda permanente los cazó y los nombró, que es para lo que está.
Total marcado: **6 tests en 2 archivos**.

## Bloque 1 — el mapa operable. **Cerrado.**

`docs/universo_operable.md`, **generado** por `python -m dinero.mapa`, no
escrito a mano. 36 candidatos, **36 verificados** (ninguno de memoria: cada uno
tuvo que devolver un cierre). Precios congelados con fecha y huella en
`dinero/datos/cierres_congelados.csv` (2011 filas, 2018-09-05 → 2026-09-04).

**MEDIDO al 2026-09-04:** 6 eslabones representados, 2 sustituidos, 0 huecos;
exigiendo liquidez verificada, 5 / 3 / 0. Con el techo de 500 USD alcanzan 29
de 36 instrumentos; con el piso de 100 USD, **7 de 36**.

Dos hallazgos que ordenan el resto de la corrida:

1. **`SMH`, el benchmark declarado del proyecto, cerró a 567,01 USD: no cabe
   entero en el presupuesto.** Tampoco `ASML` (1714,88), `SNDK`, `MU`, `META`,
   `MSFT` ni `SOXX`.
2. Con comisión mínima de 1 USD y tope de 1 %, **una orden de una acción de
   menos de 100 USD paga exactamente el 1 %**.

**Verificación cruzada que vale la pena anotar:** `AMD` y `LIN` cerraron ambos
en 477,57 —idéntico al centavo—, que es la firma típica de un desalineamiento
de columnas. Se comprobó por **otro camino** (`Ticker.history` de a un ticker,
no la descarga en lote) y los dos valores son reales. Verificar con el mismo
mecanismo no habría sido verificar.

## Bloque 2 — `VISION.md`. **Cerrado.** 105 líneas.

Los dos rieles declarados como separados, cada uno con qué mide, horizonte,
vara y **qué lo mata**. La frase de intención va rotulada como intención. La
pista de hardware queda como plataforma de verificación y proyecto de ramo, con
el piso de latencia medido (p50 8,79 ms contra cientos de nanosegundos de una
colocación: cuatro órdenes de magnitud) y la conclusión de que lo que
desbloquea esa ruta es colocación, no hardware.

## Bloque 3 — la capa de decisión. **Cerrada.**

`dinero/decision.py`: función pura, sin red, sin escritura, sin reloj, con los
descartes y su razón. Tests de **propiedad** sobre entradas generadas con
semilla declarada, 400 casos por invariante.

**Los tres juegos no se inventaron:** cada número sale de una regla en
`dinero/derivacion.py` y un test la recomputa. Están en `espera_firma.md` §39;
rige el conservador por regla escrita.

## Bloque 4 — la cuenta en papel. **Cerrada, con dos desviaciones declaradas.**

**Desviación 1.** El encargo pedía correr «contra los precios ya guardados, sin
descargas nuevas» y **el proyecto no guardaba precios**. Se bajó una vez, se
congeló con fecha y huella, y todo lo que mide lee el congelado. Llamar «ya
guardados» a lo que uno bajó hace diez minutos habría sido la trampa que el
pre-mortem anticipó.

**Desviación 2.** El flujo de caja se acotó al presupuesto: 100 USD por semana
**hasta agotar los 500**, no por tres años. Línea base y estrategia reciben el
mismo flujo.

**Qué se midió, y con qué:** una señal **sin información** (sorteada, semilla
20260906). Lo medido es fricción.

- **Robusto:** las comisiones se comen **14–25 % (conservador), 27–31 % (medio)
  y 43 % (agresivo)** del capital, contra 0,4–0,6 % de no decidir nada.
- **Advertencia sobre el método:** el barrido de deslizamiento **no** es una
  curva de sensibilidad al costo — el conservador va de +158 % a 5 pb a +357 %
  a 10 pb, con 227 órdenes contra 133. Diez puntos básicos no mueven un
  resultado 199 pp: lo que cambia es **qué** instrumento entra en el margen.
  Son caminos distintos, no la misma estrategia a distinto costo.
- **La cifra más útil de la página:** **5 de 24** comparaciones (21 %) dan un
  intervalo del 95 % que excluye el cero, con una señal cuya respuesta
  verdadera es cero en las 24. Todos falsos positivos por construcción.
- **Direccional:** el juego agresivo pierde contra `SMH` en **4 de 4** pasadas,
  con el intervalo entero bajo cero. No hace falta una señal buena para perder.

## Bloque 5 — el pre-registro del riel. **Cerrado.**

`dinero/preregistro_dinero.md`. Criterio escrito como número: 52 semanas, UNA
comparación declarada, una sola mirada, intervalo que excluya el cero.

**Y el número que lo vuelve incómodo:** con σ = 2,54 pp/semana medida, 52
semanas sólo alcanzan para una ventaja de **≈ +1,00 pp/semana** (+0,25 pediría
809 semanas, 16 años). Una ventaja así no es plausible. De ahí la cláusula §2.5:
**si el criterio se cumple, la primera reacción no es poner plata, es sospechar
un error.** M2 —comisión sobre el 25 % del capital— **está a punto de
dispararse antes de empezar**, y eso es información sobre el tamaño de la
cuenta, no sobre la señal.

## Bloque 6 — la primera señal larga. **Cerrado.**

**El orden se respetó y es verificable en git:** el pre-registro
(`GEMELO/preregistro/senal_larga_v1.md`) entró en el commit `e368dad`; el
módulo y el reporte, después. `git log --all -- dinero/senal_larga_reporte.py`
salía vacío cuando el auditor corrió.

### La auditoría, antes de la primera medición

`auditor-lookahead` encontró **una fuga demostrada (R3) y tres sesgos con
signo**, y todo se corrigió **sin haber calculado un solo MAE**:

- **F1, fuga de selección.** La composición de los eslabones salía de un filtro
  de «¿entra una acción en 500 USD?» que usa el **último** cierre del archivo.
  Fijaba la membresía de ocho años con el renglón del 2026-09-04 y **expulsaba
  a los que subieron** (excluidos: retorno mediano 847 % contra 547 %).
  Microsoft quedaba fuera de «demanda final» durante ocho años **por setenta
  centavos**. Medido: truncar en 2025-12-31 cambiaba el **42,9 %** de las filas.
- **S1**: el protocolo ejecutado no era el pre-registrado (walk-forward
  expansivo metía 36 % del último ajuste dentro de la prueba mientras el
  reporte afirmaba lo contrario). **Ganó el pre-registro.**
- **S2**: L2 no quitaba la beta común (beta pooleada; residuos con beta de
  −0,20 a +0,14). **S3**: L3 medía su propio objetivo (corr hasta +0,57).
- **S7**: retardo de implementación cero — un día mueve la etiqueta 3,6–4,0 pp,
  **del mismo orden que el umbral del juego conservador (3,49 pp)**.
- **S8**: `sign(0)==sign(0)` contaba como acierto.

Las seis correcciones están como **errata fechada §9** del pre-registro, y
**dos de ellas endurecen la vara**. Ninguna suma al registro de intentos: son
las mismas L1, L2 y L3 sin la fuga. El gate del auditor (56 tests) pasa.

### El resultado

- **L1 (contagio directo) queda REFUTADA por su propia regla pre-registrada:**
  no le gana a predecir cero con intervalo que excluya el cero en ninguno de
  los dos horizontes (+0,299 [−0,122, +0,697] a 20 días; +1,931 [−0,511,
  +4,150] a 60).
- **Y peor: L1 a 20 días acierta MENOS que la climatología** (63,4 % contra
  65,7 %, −2,339 pp con IC [−4,522, −0,429], que no contiene el cero).
- **La vara pre-registrada resultó débil, y hubo que decirlo:** «predecir cero»
  no es neutro en un mercado que sube. Se agregó una tercera vara —climatología
  causal— **DESPUÉS de ver el resultado**, rotulada como post-hoc. Contra ella,
  L1 y L3 pierden o empatan; sobrevive **una sola celda**: L2 a 60 días, con
  +0,229 pp de MAE [+0,054, +0,424] — del orden del **2 % relativo**.
- **Tres celdas tienen la métrica de dirección VACÍA**: la predicción nunca
  cambia de signo, así que el +0,000 pp con IC [0, 0] no es un empate.

**Conclusión publicada:** una celda de seis le gana a la vara dura, sobre 24
contrastes, en una página cuyo propio diseño produce un falso positivo el 21 %
de las veces. **No autoriza nada.**

## Bloque 7 — la capa visual. **Cerrada.**

Se descubrió primero qué existía (`api/` FastAPI de solo lectura, `frontend/`
Vite+React con 11 vistas). `api/CONTRATO.md` se enmendó **antes** de tocar
endpoints. Tres endpoints nuevos de solo lectura sobre artefactos ya generados,
y tres vistas: `/rieles`, `/operable`, `/dinero`.

Lo que vale la pena anotar del diseño: la regla «ningún estimador sin
intervalo» dejó de ser disciplina y pasó a ser un componente,
`CifraConIntervalo`, que **no puede** renderizar un número sin su intervalo —
si no lo recibe, muestra por qué falta. Y cuando el intervalo cruza el cero, lo
dice **con palabras**. El test de la palabra prohibida cubre ahora los archivos
nuevos, y hay un test de que la etiqueta SIMULADO está en el primer bloque de
la vista de la cuenta. `npm run build` en verde.

## Errores propios de esta sesión

1. **La guarda de red nació ciega.** Espiaba `socket` mientras yfinance habla
   por libcurl, y el primer censo salió vacío. Si no hubiera desconfiado de un
   censo vacío sobre una suite que sé que descarga, habría marcado cero tests y
   declarado la deuda pagada.
2. **El censo se quedó corto igual.** Marcó 4 de 6 tests; los otros dos
   aparecieron cuando otro proceso corrió la suite en otro orden. La limitación
   estaba declarada, pero declararla no es lo mismo que medirla bien.
3. **La señal larga nació con una fuga de selección** que yo mismo introduje al
   reutilizar `construir_mapa` para componer los eslabones. Era cómodo —ya
   estaba escrito— y el filtro de presupuesto no tiene nada que hacer en la
   construcción de un índice histórico. La cazó el auditor, no yo.
4. **La vara del bloque 6 estaba mal elegida en el pre-registro que yo escribí
   horas antes**, aunque el adversario del proyecto ya había dictaminado en
   agosto que «predecir cero» no es neutro. Tuve que agregar la vara buena
   después de ver el resultado, que es la peor manera de agregarla.
5. **El primer intento de test del componente de intervalo** afirmaba que
   perturbar el cierre de *t* movía la etiqueta; con el retardo aplicado, no la
   mueve. La aserción estaba mal y la corregí a la inversa, que es lo que
   prueba que el retardo existe.

## Lo que queda abierto

- **`espera_firma.md` §39, §40, §41**: qué juego rige, el arancel real del
  corredor, y si los dos registros de intentos se fusionan.
- **La ablación tipo R2 de la señal larga no se hizo.** El pre-registro del
  riel la exige antes de cualquier monto, y esta corrida no la corrió.
- **`GEMELO/preregistro/senal_larga_v1.md` quedó con seis erratas** en su §9,
  todas anteriores a la medición. Un lector futuro tiene que leer el §9 junto
  con el §8, no el §8 solo.
- Lo que ya estaba: firmar V1-bis y el parche `snapshot.py:140`. **Esta corrida
  no las tocó y las alarga**, como el director advirtió.

## Cierre

- **Suite: 650 → 748 passed, 2 xfailed.** Verde al abrir y al cerrar.
- `npm run build` del frontend en verde (tsc + vite).
- Árbol commiteado en `main`, en dos commits: el pre-registro del bloque 6 **antes**
  del cómputo, y el resto después. **Nada se pusheó**: el push es acto manual de
  Nicolás, después de leer el diff.
- `.git/hooks/pre-commit` se refrescó con la copia nueva de `scripts/pre-commit`, para
  que la regla de la ventana esté de verdad instalada y no sólo escrita. Se declara
  porque es un cambio fuera del árbol versionado.
- **Los dictámenes del `guardian-constitucion` y del `curador-epistemico` NO se
  corrieron acá**, por instrucción del encargo: van en sesión aparte con contexto
  limpio leyendo `~/cierre.md`. Esta corrida entrega el diff sin dictaminar sobre sí
  misma.
