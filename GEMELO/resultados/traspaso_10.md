# Traspaso — MKI Terminal, después del cierre de la corrida 10

**Escrito el 7-sep-2026 a las 02:00 de Chile**, al terminar la sesión de cierre.
Está hecho para pegarse entero en un chat nuevo que no sabe nada del proyecto.
**Todas las cifras de acá se leyeron de la máquina en esta misma sesión**,
ninguna de memoria.

---

## 1. Qué es el proyecto

**MKI Terminal** es una plataforma de investigación que se corre sola y estudia
la cadena de valor de los semiconductores, de la roca al chip al centro de
datos. Lo que la distingue de un dashboard es que lleva un **track record
sellado con marca de tiempo**: cada predicción se guarda en una base con la hora
exacta en que se emitió, y **sólo se evalúa si esa hora es anterior a la
apertura del mercado que intentaba predecir**. Las que llegan tarde quedan
guardadas para auditoría y fuera de toda métrica. Las filas selladas **no se
reescriben jamás**; un error histórico se documenta como errata, no se corrige
en su lugar.

Desde la corrida 10 el proyecto declara que persigue **dos cosas distintas**, y
que confundirlas era el problema:

- **Riel de medición.** El de siempre. Mide si el cierre del índice de
  semiconductores de EE.UU. (SOX) anticipa la **apertura de la mañana siguiente
  en Tokio, Taipéi y Seúl**. Horizonte: una noche. **No mueve dinero.** Es el
  único riel con filas selladas.
- **Riel de dinero** (`dinero/`, nuevo). Pregunta si se podría operar sobre eso
  con instrumentos de EE.UU. a horizonte de **semanas**, con 100 a 500 dólares.
  **Todo simulado, cero filas selladas, ninguna cuenta de corredora, ninguna
  orden enviada a ningún lado.** Está aislado del camino de sellado en las dos
  direcciones, con tests que lo verifican.

La plataforma va en versión 5.0.3 y el **modelo de señal está congelado en
4.6.0**. Son dos versionados distintos a propósito: la plataforma evoluciona, el
modelo no. Mover `MODELO_VERSION` reinicia el track record limpio y es una
decisión humana.

---

## 2. Dónde está el estado, en orden de lectura

1. **`ESTADO.md`** — dónde está el proyecto hoy. 52 líneas, se regenera en cada
   cierre. Empezá por acá.
2. **`README.md`** — es la **fuente de verdad de las cifras publicadas**. Ningún
   número se cita de memoria: se lee de acá o del módulo árbitro `cifras.py`.
3. **`VISION.md`** — qué persigue el proyecto y qué NO es. Los dos rieles, con
   qué mata a cada uno.
4. **`CLAUDE.md`** — las reglas de la casa y la arquitectura, para trabajar en
   el repositorio.
5. **`DECISIONES.md`** — la historia larga: 81 actas con cada decisión de diseño
   y su razón. **Consultalo antes de "arreglar" algo que parezca arbitrario.**
   La 80 es la corrida 10; la 81 es este cierre.
6. **`GEMELO/resultados/bitacora_10.md`** — qué hizo la corrida.
7. **`GEMELO/resultados/dictamen_10/`** — los cuatro dictámenes de este cierre,
   más `aplicacion.md`, que dice qué se hizo con cada una de las 62 exigencias.
8. **`GEMELO/resultados/espera_firma.md`** — lo que espera la firma de Nicolás.

---

## 3. Cómo trabajamos

**El método es por encargos.** Nicolás escribe un encargo con bloques
numerados; una sesión larga los ejecuta; después, **en una sesión limpia y
separada**, se corre el ritual de cierre (`~/cierre.md`). Que el que dictamina
no tenga en contexto el razonamiento que produjo el trabajo es a propósito:
**una verificación que usa el mismo mecanismo que produjo la cifra no es una
verificación.**

**Los agentes de rigor** viven en `.claude/agents/` y son de sólo lectura:

- `orientador` — al abrir sesión o retomar.
- `director-programa` — antes de abrir un frente nuevo o elegir entre dos cosas.
  Es el que dice que no.
- `guardian-constitucion` — antes de cerrar cualquier tanda. Verifica las reglas
  duras con evidencia propia.
- `curador-epistemico` — toda prosa que salga del repositorio, incluida la
  interfaz, que es texto publicado.
- `estadistico-adversario` — toda cifra y todo pre-registro.
- `auditor-lookahead` — parte del supuesto de que hay fuga temporal y trata de
  demostrarla.

**Las reglas duras**, algunas aplicadas por hook y no negociables:

- `motor.py` no se toca. El modelo sigue en 4.6.0.
- Las filas selladas no se reescriben nunca.
- **Claude no pushea.** El push es acto manual de Nicolás, después de leer el
  diff. Y tampoco se traen cambios sobre el árbol de trabajo, porque ese árbol
  es el código que los timers ejecutan: se usa `fetch` y se lee desde
  `origin/main`.
- Ninguna cifra se cita de memoria: se lee del README o de `cifras.py`.
- Toda predicción se publica con su incertidumbre (n, intervalo, régimen), y la
  palabra "confianza" está **prohibida en todo el sistema**, con un test que lo
  verifica.
- No se reimplementan Wilson, McNemar, DSR ni CRPS: existen en
  `.claude/skills/estadistica-evaluacion/scripts/evaluacion.py`.
- La suite **no puede correr en la ventana de sellado** (17:50 a 20:30, días
  hábiles, hora de Chile), porque toca la red y compite con el sello.
- Un resultado negativo se publica con la misma firmeza que uno positivo.

**Esta máquina es el titular:** un PC con Windows/WSL2, en la rama `main`, con
seis timers de systemd instalados que emiten y sellan. Lo confirma `modo.py`,
que dice `titular`. **Cambiar el modo o tocar los timers es operación de
Nicolás, nunca de un agente.** Donde un documento y la máquina no coincidan,
**manda la máquina**, y la discrepancia se registra como errata.

---

## 4. El estado científico, en números

### Riel de medición — la cifra publicada

Leída de `cifras.sellada()` en esta sesión:

| | Valor |
|---|---|
| Muestra | **n = 238 filas, 34 días**, hasta el sello del **2026-08-28** |
| Acierto del modelo | **67,6 %**, Wilson 95 % [61,5 · 73,3] |
| Acierto de la base ("siempre al alza") | **58,0 %**, Wilson 95 % [51,6 · 64,1] |
| **Ventaja** | **+9,7 pp**, **IC95 de clúster de día [−7,2 · +26,6]** |
| McNemar de filas | p = 0,0455 |
| Por qué manda el IC de día | ICC 0,392 · DEFF 3,55 · **n efectivo 67** |
| Cobertura del intervalo del 80 % | 92,9 % (nominal 80 %), intervalos 2,19× más anchos de lo necesario |

**Lo que hay que entender de esta tabla, y es lo más importante del proyecto:**
el McNemar de filas da p = 0,0455, que parece significativo, **pero las ocho
filas de un mismo día no son observaciones independientes**. Corregido por el
clúster de día, el intervalo de la ventaja **contiene el cero**. La cifra
honesta es: *hay una ventaja aparente de casi diez puntos y no se distingue del
azar con la muestra que hay.* El proyecto publica las dos y explica por qué
manda la segunda.

### Riel de dinero — hoy

**Cero filas selladas, cero semanas corridas hacia adelante, cero dinero.** Y
después de este cierre, además:

- **La cuenta en papel está RETIRADA** por fuga temporal demostrada. Ninguna de
  sus cifras se puede citar.
- **La señal larga v1 no tiene ninguna afirmación positiva en pie.**
- **El mapa operable sigue en pie:** 36 de 36 tickers verificados, 6 eslabones
  representados / 2 sustituidos / 0 huecos (5/3/0 si se exige liquidez
  verificada). `SMH`, el benchmark del proyecto, **no cabe en 500 dólares**. Con
  el piso de 100 dólares alcanzan **7 de 36** instrumentos. Es un censo de **un
  solo día**, con los casos al borde declarados.

### Qué NO sobrevivió

- **L1, el contagio directo entre eslabones adyacentes** —la forma más simple de
  la hipótesis del riel de dinero— quedó **REFUTADA por su propia regla
  pre-registrada**. Esa refutación se sostiene sola.
- **La "celda superviviente"** que la corrida 10 había publicado (L2 a 60 días,
  +0,229 pp de MAE) **no sobrevive**: no pasa la corrección por multiplicidad de
  su propia familia de 30 contrastes (p de Holm 0,1740) ni la ablación anual
  (sacando 2024 del período de prueba, el intervalo pasa a contener el cero).
- **La tasa de "21 % de falsos positivos"** de la cuenta en papel está retirada:
  cuatro de los cinco casos que contaba eran el resultado verdadero de fricción
  que la misma página celebraba.
- **RETIRADA la cifra de que la ablación R2 "deja al campeón en −3,3 pp"**, que
  circulaba como estado vigente: bajo R2 la ventaja **no se distingue de cero**
  en las tres convenciones de conteo, que es menos dramático y es lo que la
  cifra sostiene.

---

## 5. Qué hizo la corrida 10, bloque por bloque

Ocho bloques, todos cerrados, en una sesión nocturna sin supervisión.

- **Bloque 0 — la deuda de la corrida anterior.** La suite ya no puede correr en
  la ventana de sellado: marcador `red`, `scripts/guarda_red.sh` con reloj
  falso, aplicado en el hook y en `./mki tests`. **El hallazgo del bloque es un
  error propio corregido a tiempo:** la primera guarda espiaba el módulo
  `socket` y el censo salió **vacío**, en una suite que sí descarga. La causa:
  `yfinance` habla por `curl_cffi`, o sea libcurl en C, y `socket` no ve nada.
  Un instrumento que mide donde el tráfico no pasa informa paz. Total marcado:
  **6 tests en 2 archivos** — cuatro los halló el censo y **dos más aparecieron
  después**, corriendo la suite en otro orden.
- **Bloque 1 — el mapa operable.** `docs/universo_operable.md` se **genera**,
  no se escribe. Precios congelados con fecha y huella sha256.
- **Bloque 2 — `VISION.md`.** Los dos rieles declarados y separados.
- **Bloque 3 — la capa de decisión.** `dinero/decision.py`: función pura, sin
  red, sin escritura, sin reloj. Tests de propiedad con semilla declarada.
- **Bloque 4 — la cuenta en papel.** **Es el bloque que este cierre retiró.**
- **Bloque 5 — el pre-registro del riel de dinero.** Criterio escrito como
  número, con la aritmética que lo vuelve incómodo publicada al lado.
- **Bloque 6 — la primera señal larga.** El pre-registro entró en un commit
  **anterior** al cómputo, y eso es verificable en git. El `auditor-lookahead`
  corrió **antes de la primera medición** y encontró una fuga y tres sesgos, que
  se corrigieron **sin haber calculado un solo MAE**.
- **Bloque 7 — la capa visual.** Tres endpoints de sólo lectura y tres vistas
  nuevas. Lo que vale la pena: la regla "ningún estimador sin intervalo" dejó de
  ser disciplina y pasó a ser un componente, `CifraConIntervalo`, que **no puede
  renderizar un número sin su intervalo**.

**Lo que la corrida NO hizo, y quedó anotado por ella misma:** la ablación tipo
R2 de la señal larga (hecha en este cierre) y la segunda vara pre-registrada
(sigue sin hacerse).

---

## 6. Los cuatro dictámenes de este cierre

| Dictamen | Veredicto | Exigencias |
|---|---|---|
| `guardian-constitucion` | **RECHAZA** | 10, una bloqueante |
| `curador-epistemico` | **RECHAZADO** | 18, nueve tocan un ejecutable |
| `estadistico-adversario` | **NO SOSTIENE** | 24 |
| `auditor-lookahead` | **HAY FUGA** | 10, cuatro bloqueantes |

**62 exigencias. Ninguna se ignoró en silencio.** El destino de cada una está en
`dictamen_10/aplicacion.md`. Las sustantivas:

1. **El auditor demostró cuatro fugas temporales en la cuenta en papel,
   ejecutando código y no leyéndolo.** El universo operable de una ventana de
   tres años se elegía con el cierre del **último día de esa misma ventana**; la
   señal "sin información" se sorteaba de la distribución de retornos
   **futuros** de la ventana simulada (755 de 756 señales cambian al truncar);
   el interruptor de pérdida se calibraba con futuro; y se decidía y ejecutaba
   contra el **mismo cierre**, con retardo cero, mientras el otro módulo del
   mismo riel usa un día. **La cifra titular se mueve al quitar la fuga:** el
   juego medio pasa de 27 % a **57 %** del capital en comisiones.
2. **El adversario mostró que la familia de contrastes de la señal larga son 30
   y no 24** —la cuenta vieja dejaba los seis de dirección fuera de su propia
   corrección— y que **con Holm ninguno cruza α = 0,05**; y corrió la ablación
   anual, encontrando que sin 2024 el intervalo contiene el cero.
3. **El curador encontró que el componente de honestidad afirmaba de más:**
   decía "el intervalo no contiene el cero" debajo de una tasa de acierto con
   Wilson, cuando un Wilson de una proporción **no puede** contener el cero. La
   frase sólo significa algo sobre una diferencia.
4. **El guardián encontró la cifra retirada del 91,4 % impresa desde un
   ejecutable**, y que el árbitro de cifras retiradas había dado **falso verde**
   sobre ella.

---

## 7. Qué espera la firma de Nicolás, en orden de urgencia

Todo esto está en `GEMELO/resultados/espera_firma.md`, con opciones y
consecuencias. **Ninguno lo puede decidir un agente.**

1. **§42 — ¿la cuenta en papel se reconstruye o se descarta?** Es el más caro de
   postergar de todos los abiertos, porque hoy bloquea tres cosas: la segunda
   vara pre-registrada de la señal larga, el criterio M2 del riel, y la σ de la
   tabla de potencia. Recomendación escrita: reconstruir, con el orden del
   auditor (el test de truncación va primero, y ya está escrito).
2. **El parche de `snapshot.py:140`** (ítem viejo, §26). Es el único que **sigue
   haciendo daño hoy**: agrega una fila mal etiquetada cada vez que un sello se
   atrasa, y las filas selladas no se reescriben nunca.
3. **§30 — la enmienda V1-bis**, que decide cuál métrica es primaria. La corrida
   10 tropezó exactamente con ese problema.
4. **§45 — ¿el registro de intentos del riel largo pasa de 3 a 30?** Hay que
   decidirlo **antes** de que este riel calcule cualquier DSR: un DSR con un N
   desactualizado miente hacia arriba.
5. **§43 el período de M2**, **§44 M4 reescrita bajo multiplicidad**, **§39** qué
   juego de parámetros rige, **§40** el arancel real del corredor, **§41** si los
   dos registros de intentos se fusionan.

---

## 8. Por dónde seguir

**La ruta natural es reconstruir la cuenta en papel sin fuga**, y el orden es
obligatorio y ya está fijado por el auditor:

1. El test de truncación **primero**. Ya está escrito: `tests/test_dinero.py`
   tiene tres `xfail(strict=True)` que clavan F1, F2 y F4. Hoy fallan porque las
   fugas existen. **El día que se arreglen, van a pasar, el modo estricto va a
   volver eso rojo, y va a obligar a volver a sacar el marcador.**
2. Después las correcciones: membresía acotada por fecha, sorteo desde datos
   anteriores a la ventana, retardo de implementación en las **dos** patas de la
   comparación, sigma del interruptor sin futuro, y cablear `ErrorLookAhead` al
   riel.
3. Después republicar, y recién ahí volver a tener M2 y la vara económica.

**Lo que bloquea esa ruta:** la decisión §42, que es de Nicolás. Y mientras la
cuenta esté retirada, la regla de refutación §6 del pre-registro de la señal
larga **no se puede dar por leída**, porque una de sus dos varas pasa por ahí.

**Estado del árbol ahora mismo:** rama `main`, árbol limpio, **cuatro commits
sin pushear**. El push es de Nicolás.

---

## 9. Cómo quiero que trabajes

- **En español**, directo, sin rayas ni guiones largos.
- **Toda cifra va con su n y su intervalo.** Un estimador puntual solo no se
  publica.
- **Ninguna cifra de memoria.** Se lee del README o de `cifras.py`. Si vas a
  citar un número, andá a buscarlo.
- **Manda la máquina sobre el documento.** Si un acta y el repositorio no
  coinciden, la máquina tiene razón y la discrepancia se registra como errata
  fechada.
- **Los resultados negativos se dicen con la misma firmeza que los positivos.**
  Un "no encontramos nada" bien medido es un resultado, no un fracaso.
- **Los pasos de terminal se explican uno por uno**, sin dar por sabido nada.
- **Nunca pushees.** Nunca toques los timers ni el modo de emisión.

---

## 10. Lo que esta corrida NO verificó

Es la sección más útil y la que más se olvida.

- **No se reconstruyó la cuenta en papel.** Las cuatro fugas siguen en el
  código, marcadas y clavadas por tests, pero **sin corregir**.
- **No se corrió la segunda vara pre-registrada** de la señal larga, porque pasa
  por la cuenta retirada.
- **No se midió la tasa de falsos positivos del diseño de la señal larga.** Se
  retiró la que se citaba, que era de otro diseño, y **no se reemplazó por una
  medida sobre éste**: hace falta correr K semillas.
- **No se corrió nada contra `GEMELO/simulador/`.** El proyecto tiene la regla de
  verificar el instrumento contra una verdad conocida antes de creerle sobre una
  desconocida, y **la mitad con ventaja verdadera distinta de cero no se
  corrió**. La tabla de potencia del riel de dinero es aritmética sin validar.
- **No se verificó el mapa operable contra una segunda fuente ni en un segundo
  día.** Sigue siendo un censo de un solo día.
- **No se auditó la liquidez real de ningún instrumento.** Un cierre demuestra
  que cotiza, no que se pueda ejecutar. Dos miembros de los paneles de la señal
  larga están en esa situación.
- **El supuesto de costos no está contrastado contra ningún tarifario real.**
  Es la mitad de la cifra que sostenía todo el bloque 4, y es el ítem §40.
- **La suite verde no cubre por causalidad** ni `cuenta_papel.py` ni
  `contabilidad.py`. Un verde de `pytest` hoy **no es evidencia de ausencia de
  fuga** en el riel de dinero, y no debe leerse así.
- **Nada del riel de dinero es prospectivo.** Cero filas selladas. Todas sus
  cifras salen de mirar ocho años de una vez, un domingo a la noche. La única
  defensa contra la fuga por el analista es el sellado en vivo, y este riel no
  tiene ninguno.
