# DECISIONES.md — Etapa 4.5 ULTRA

Registro de decisiones tomadas de forma autónoma durante la construcción de la
Etapa 4.5 (el usuario estaba desconectado). Criterio: ante la duda, la opción
más conservadora — la que menos contradice instrucciones explícitas y menos
rompe lo que ya funcionaba.

## G — Wordmark del producto

Opciones consideradas (solo tipografía, Space Grotesk, punto final en cyan):

1. **MKI Terminal.** — conecta con la identidad ya existente del proyecto
   (la carpeta se llama StockScreenerMKI), suena a producto financiero serio.
2. **Fundición.** — evocador del sector (foundry), pero puede confundirse con
   una app de metalurgia y pierde la conexión con el nombre del proyecto.
3. **RocaChip.** — literal con el concepto roca→chip de esta etapa, pero
   demasiado atado a UNA pestaña y algo infantil para un terminal.

**Elegida: "MKI Terminal."** — la más sobria, la que envejece mejor si el
producto crece más allá de la cadena de semiconductores, y la única que
conserva identidad previa del proyecto.

## A — Nivel de la cadena para las empresas de diseño (NVDA, AMD, QCOM, AVGO, TXN, ARM, IFX.DE)

La instrucción define 5 eslabones (0 materias primas, 1 materiales, 2 equipos,
3 fabricación, 4 demanda final) y lista explícitamente qué empresas existentes
pertenecen a los niveles 2 y 3. Las empresas de diseño fabless (NVIDIA, AMD,
Qualcomm, Broadcom, Texas Instruments, Arm, Infineon) **no aparecen en ninguna
lista**. Opciones: (a) inventar un eslabón extra "Diseño" (contradice el flujo
0→4 explícito), (b) meterlas en nivel 3 "Fabricación" (contamina la señal de
las fundiciones — NVIDIA no fabrica), (c) dejarlas sin nivel (nivel=None):
siguen en rankings, anticipador, sentimiento y detalle como siempre, pero no
entran al flujo de la cadena ni al índice Roca→Chip.

**Elegida: (c) nivel=None.** Es la lectura literal de la instrucción (curación
deliberada de qué entra a la cadena) y la que no distorsiona ninguna señal.

## A — Anticipador y acciones japonesas nuevas (4063.T Shin-Etsu, 3436.T SUMCO)

Son acciones (no commodities/ETF) que cotizan en Tokio — un mercado "por
abrir". La restricción explícita solo excluye commodities y ETF del
anticipador. **Se agregan a MERCADOS_POR_ABRIR y a MONEDA_TICKER (JPY=X)**:
consistente con el diseño del anticipador ("analiza SIEMPRE todas las acciones
de mercados por abrir") sin violar ninguna regla.

## A — Sidebar y ranking

"Commodities y ETF no entran al ranking de acciones ni al anticipador".
El multiselect del sidebar alimenta directamente el ranking del Comparador,
así que **el sidebar solo ofrece acciones** (tipo="accion"; incluye BHP, FCX y
MSFT, que sí son acciones). El cobre, la plata y SMH viven en la pestaña
Cadena y el panel macro como contexto.

## B/E — Una sola fila hero global

La Parte B pide un "badge permanente en el hero" (régimen) y la Parte E pide
una "fila hero (régimen, Roca→Chip, último SOX real, sentimiento sector)" en
la portada Hoy. Tener dos filas hero distintas (una global + una de Hoy)
duplicaría la misma información en la misma pantalla. **Decisión: la fila
hero global (visible en todas las secciones) pasa a ser exactamente la de la
Parte E** — régimen, Roca→Chip, último SOX real, sentimiento del sector — y
las tarjetas anteriores ("Mejor acción del día" y "Líder del ranking") se
mudan al inicio de la sección Comparador, que es su contexto natural.

## B — Umbral de régimen lateral

La instrucción define alcista/bajista/lateral por medias móviles 50/200 pero
no da el umbral de "lateral". **Decisión: si |MA50/MA200 − 1| < 1%, el
régimen es lateral**; sobre +1% alcista, bajo −1% bajista. Es el umbral más
usado en la literatura de cruces de medias para filtrar el ruido del cruce.

## B — Panel macro: unidades del bono 10 años

La convención histórica de ^TNX era "yield × 10" (42.5 = 4.25%), pero el dato
actual de Yahoo llega en puntos porcentuales directos (4.485 = 4.49% — se
verificó empíricamente: 44.85% sería absurdo). Se muestra tal cual con "%", y
la variación de 5 días en puntos base (1 pp = 100 pb), porque así se habla de
bonos. El resto (KRW, TWD, cobre) muestra variación porcentual 5d.

## B — ^TNX sin histórico en yfinance

Al construir el panel macro, Yahoo devolvió UN solo dato del bono a 10 años
(^TNX), sin histórico, en cualquier período consultado (3mo/1y/2y/max). En vez
de sustituirlo por un proxy no pedido (ZN=F, IEF) o inventar variación,
**la tarjeta del bono muestra el nivel actual con la nota explícita de que
Yahoo no entrega histórico ahora mismo** — sin variación 5d ni correlación.
Si Yahoo restituye el histórico, la tarjeta completa aparece sola.

## D — Fix del bug del Puntaje v0 en Detalle (preexistente)

El Puntaje v0 de la ficha de Detalle se calculaba con la acción sola, y el
percentil de un universo de 1 elemento es constante: siempre daba 0.80, para
cualquier acción. Ahora se calcula contra el universo completo de acciones
(la misma descarga que ya usaban las correlaciones, reutilizada).

## D — Buzz exige historia mínima de la base

Con la base de noticias recién creada (2 días de vida), el "promedio diario de
14 días" da casi cero y TODAS las acciones aparecían en ALTO BUZZ — un badge
que grita en todas partes no dice nada. **Decisión: el buzz solo se declara si
la base tiene al menos 7 días de historia**; antes de eso, se reporta el
conteo pero sin badge. Mismo principio de honestidad estadística que el
"datos insuficientes" del Historial.

## D — La limpieza retroactiva respeta el veredicto de la IA

Al borrar titulares irrelevantes ya guardados, se conservan los que la IA ya
analizó marcando tickers del universo como afectados, aunque el titular no
contenga keywords (ej. "Jim Cramer believes..." sin nombrar la empresa en el
texto exacto). El filtro de keywords es la primera línea; el juicio de la IA,
que ya se pagó, no se tira a la basura.

## E — Cómo se eligen "Las 3 señales del día"

La instrucción pide "las más fuertes" entre cuatro familias de señales sin
definir cómo compararlas entre sí. **Decisión: cada señal se puntúa como
distancia relativa a su propio umbral de activación** — divergencia: |z|/2;
apertura de alta confianza: |estimado|/2; sentimiento extremo: |s|/0.6;
buzz: ratio/3. Así, 1.0 significa "justo en el umbral" en cualquier familia y
los valores son comparables; se muestran las 3 de mayor puntaje. Es simple,
explicable y no requiere calibración histórica que aún no existe.

## F — Reporte matinal sin anti-duplicados

Las alertas automáticas usan registro anti-duplicados en SQLite (una alerta
por evento). El botón "Enviar reporte matinal" es una acción manual explícita:
si el usuario lo aprieta dos veces, recibe el reporte dos veces — no se
bloquea, porque bloquear una acción manual explícita confunde más de lo que
protege.

## A — Noticias para tickers nuevos

Se agregan a EMPRESAS de noticias.py: BHP, FCX, Shin-Etsu, SUMCO y MSFT.
Los futuros (HG=F, SI=F) y el ETF SMH no tienen "empresa" que buscar por
nombre — su contexto de noticias llega vía keywords del sector ("copper",
"silver", etc.) del filtro de relevancia de la Parte D.

---

# Etapa 4.6 — Integridad de medición

## P1 — available_at: el cierre de la sesión del SOX usada

"Cuándo era conocible la información usada" se materializa como el cierre UTC
de la sesión de NYSE cuyo movimiento del SOX alimenta la predicción (ej.: una
predicción emitida el sábado usa el SOX del jueves si el viernes fue feriado →
available_at = jueves 20:00 UTC). Es la cota inferior honesta: antes de ese
instante, la señal era incomputable.

## P1 — Exchange de los listados estadounidenses

Todos los tickers listados en EE.UU. (NYSE y NASDAQ) usan el calendario XNYS:
comparten feriados y horario core 9:30–16:00 ET, que es lo único que el
verificador de timing necesita. Distinguir NASDAQ de NYSE no cambia ninguna
decisión del sistema.

## P3 — El fallback del dashboard siempre sella, el verificador decide

La spec dice "si no existe snapshot del día y el timing es válido, se toma
uno". Interpretación conservadora: el dashboard SIEMPRE toma el snapshot
faltante (con origen 'dashboard' y su timestamp real), y es el verificador
quien decide después, predicción por predicción, si fue emitida antes de la
apertura de su sesión objetivo. Un "validador de timing" a priori en el
dashboard duplicaría la regla maestra en dos lugares — y la regla debe vivir
en un solo lugar.

## P5 — universo.py nació con la estructura de la P7

El orden pedido era 1→5→2→3→4→6→7, pero construir universo.py (P5) con la
estructura vieja y reescribirlo en P7 habría duplicado trabajo y commits
intermedios inconsistentes. universo.py se creó directamente con los cambios
estructurales de la P7 (TSM duplicado_de, GOOGL/META en nivel 4, SMH como
BENCHMARK fuera de la cadena). El test de no-contaminación es independiente
de la composición del universo, así que la garantía de P5 no se ve afectada.

## P6 — La relevancia pre-4.6 vale 1.0

Los análisis antiguos no tienen campo relevancia (la IA no lo devolvía). Se
tratan como 1.0 (sin castigo retroactivo) en vez de re-analizarlos pagando de
nuevo: la limpieza de asignación (matching estricto) ya corrigió el problema
grave (titulares mal atribuidos); la relevancia fina solo existirá hacia
adelante.

## P6 — La deduplicación conserva la entrada más antigua

Mismo evento desde dos fuentes = una entrada; sobrevive la de fecha de
publicación más antigua (la "primicia") y se borran las réplicas junto con su
análisis. El orden es determinista (fecha ASC, id ASC), así que la migración
es idempotente.

## P7 — IEF como proxy del bono: dirección documentada

IEF es PRECIO de bonos (sube cuando las tasas bajan) — la dirección opuesta
al yield que mostraba ^TNX. La tarjeta lo dice explícitamente y el nivel
puntual del yield se mantiene vía ^TNX cuando Yahoo lo entrega. No se invierte
la serie artificialmente: los datos se muestran como son, con su leyenda.

## P8 — Técnica del sidebar-rail y límites de Streamlit encontrados

**Técnica que funcionó** (verificada con Playwright: 64px colapsado → 220px
en hover): forzar el ancho de `section[data-testid="stSidebar"]` con
`!important` (64px) y expandirlo en `:hover` (220px) con `transition 0.2s`;
el contenedor interno queda fijo en 220px con `overflow: hidden`, así los
labels no reflowan durante la transición. La navegación es un `st.radio`
re-estilizado: círculos nativos ocultos, iconos SVG monocromos inyectados
como `mask-image` (data-URI) vía `label:nth-of-type(k)::before`, ítem activo
detectado con `label:has(input:checked)` (barra cyan 3px + icono/texto
claros). El estado de la vista persiste porque el radio tiene `key` fijo.

**Límites de Streamlit encontrados (documentados, no bloqueantes):**
- La expansión del hover reflowa el contenido principal ~156px (el sidebar
  participa del flex layout); es visible pero suave gracias a la transición.
- `st.dataframe` renderiza en canvas (glide-data-grid): el tamaño de fuente
  de las celdas NO es estilizable por CSS, así que la densidad "tipo
  terminal" en tablas se logra por altura del contenedor y columnas, no por
  tipografía.
- `:has()` requiere navegadores 2022+ (Chrome 105+/Safari 15.4+); en un
  navegador más viejo el ítem activo pierde su resaltado pero la navegación
  sigue funcionando.

## P8 — La configuración vive en un popover, no en el sidebar

El sidebar pasó a ser exclusivamente navegación (el rail). El multiselect de
acciones, la ventana de historia y el toggle de moneda se movieron a un
popover "Ajustes" arriba a la derecha, visible en todas las vistas: la
configuración se usa poco y no merece ancho de pantalla permanente en una
interfaz at-a-glance.

## P8 — Fila 1 de Hoy = hero global + tarjeta de track record

El hero global (régimen, Roca→Chip, SOX, sentimiento) ya era exactamente la
fila 1 pedida para Hoy; en vez de duplicarlo, la vista Hoy le agrega la 5ª
tarjeta (track record del gap a 30 días, o "insuf." con el conteo de
verificaciones) a la misma grilla. Verificado en 1440×900: la portada Hoy
completa cabe sin scroll (contenido 900px = viewport 900px).

## P8 — Fix del sidebar invisible (bug reportado post-4.6)

**Síntoma:** la vista Hoy cargaba pero no había forma de navegar — ni rail de
iconos ni control para expandir el menú.

**Causa raíz (reproducida con Playwright):** bajo ~768px de ancho de ventana
(o si Streamlit recuerda un estado colapsado), el sidebar recibe
`aria-expanded="false"` y `transform: translateX(-300px)` — queda fuera de
pantalla. El CSS de la 4.6 además ocultaba el control nativo de expandir
(`stSidebarCollapsedControl`), así que no quedaba NINGUNA vía de navegación.
En las pruebas originales no se detectó porque las sesiones de test partían
con el sidebar expandido.

**Fix en tres capas (todas verificadas):**
1. `initial_sidebar_state="expanded"` en set_page_config — evita el colapso
   inicial.
2. El CSS del rail ahora incluye explícitamente el selector
   `[aria-expanded="false"]` y anula `transform`/`visibility`/`margin-left`:
   aunque Streamlit "colapse" el sidebar (p. ej. al achicar la ventana en
   vivo, verificado con resize a 640px), el rail de 64px permanece en x=0 y
   la navegación sigue operativa.
3. El control nativo de EXPANDIR ya no se oculta (red de seguridad si una
   versión futura de Streamlit escapa del override); el de COLAPSAR sigue
   oculto — el rail no debe poder esconderse.

Verificación: navegación entre 3+ vistas en ventana ancha (1440px, con hover
64→220px), ventana angosta (700px) y colapso dinámico real (resize a 640px
con aria-expanded="false" activo).

---

# Etapa 4.7 — "Fachada" (migración del frontend a React)

## F1 — API FastAPI de solo lectura

**Regla cero respetada:** `api/` solo IMPORTA funciones de motor.py y los
helpers de consulta de senales.py/noticias.py, y LEE las bases. Ni una línea
de motor.py, snapshot.py, noticias.py o alertas.py fue tocada. La API jamás
escribe en las bases ni llama a la API de Anthropic (noticias solo de cache).

**Decisiones autónomas de esta fase:**

1. **Contrato primero** (`api/CONTRATO.md`): los 9 endpoints, el envelope
   común `{meta, datos}` (meta lleva siempre timestamp, fecha de datos,
   régimen vigente y snapshot del día) y el formato de errores quedaron
   especificados antes de escribir main.py.

2. **Predicciones "selladas" vs "vivas":** /api/aperturas sirve como número
   vigente el SELLADO en senales.db (con su timestamp_utc real de emisión —
   la garantía anti look-ahead llega hasta la UI), complementado con beta/
   confianza/earnings de la salida viva del motor. Sin snapshot hoy:
   se sirven las vivas con `"sellada": false`, explícito en el JSON.

3. **NaN → null explícito:** los `.to_dict()` de pandas traen NaN (celdas
   vacías del track record en maduración) y JSON no los admite; el envelope
   pasa todo por un sanitizador recursivo. Una celda vacía es un null
   honesto, no un error 500.

4. **Empate real en la cinta:** KRX (09:00 KST) y TSE (09:00 JST) abren en
   el MISMO instante UTC (00:00). Ambas se marcan "proxima" — es la
   realidad, no un bug; el test de humo verifica que todo empate comparta
   apertura_utc.

5. **Cache TTL 5 min** por función del motor (presentación pura): datos
   diarios no ameritan recomputar la regresión por request, pero el cache
   nunca sobrevive más de 5 minutos por si llega un snapshot nuevo.

6. **pytest** se agregó al venv (dependencia solo de tests).

**Paridad verificada:** 15 tests en tests/test_api.py comparan los números
servidos contra motor.py y senales.py en vivo — betas, régimen, Roca→Chip,
divergencias, predicciones, métricas y calibración idénticos por definición.

## F2 — Base del frontend React

**Stack montado:** Vite 8 + React 19 + TypeScript + Tailwind 4 (tokens vía
`@theme` en `src/index.css`), TanStack Query (estado de servidor, cache 5
min), react-router 7, lightweight-charts 5, Recharts, fuentes self-hosted
via @fontsource (Space Grotesk / Inter / JetBrains Mono). El frontend habla
SOLO con la API (:8000) vía proxy de Vite — jamás con yfinance ni las bases.

**Decisiones autónomas de esta fase:**

1. **Cinta de husos con un micro-carril por bolsa, no por región.** La ADENDA
   pedía 3 carriles (Asia/Europa/EE.UU.), pero KRX, TSE y TWSE transan casi a
   la misma hora: en un carril compartido los bloques se tapaban entre sí
   (bug real detectado con Playwright: el hover de KRX era interceptado por
   TWSE). Se pasó a 5 micro-carriles de 8px que siguen descendiendo
   Asia → Europa → EE.UU. dentro de los 56px del presupuesto.

2. **El eje del día global arranca en el cierre de NY más reciente que ya
   pasó** (retrocediendo hasta 5 días por fines de semana), y "ahora" se
   satura en el borde si el eje quedó viejo — un domingo la cinta sigue
   siendo legible.

3. **Tooltip de la cinta:** hora Chile de la sesión, cuánto falta para abrir
   ("abre en 1h 35m"), qué cerró antes y la beta de contagio promedio del
   exchange — la narrativa del contagio en un hover.

4. **`/sistema`:** catálogo oculto (sin enlace en la nav) con los 9
   componentes base y la regla que gobierna a cada uno; verificado con
   captura a 1440px.

5. Vistas de negocio como placeholder "migración en curso" hasta F3–F5;
   Streamlit (:8501) sigue siendo el camino operativo.

Verificación: build TypeScript sin errores; capturas de /hoy (cinta con
KRX/TSE pulsando como próximas, flecha magenta de contagio, marcador "ahora")
y /sistema; hover de la cinta operativo tras el fix de carriles.

## F3 — Vistas /hoy y /aperturas

1. **/hoy como portal bento:** el estado del mundo en 4 cifras (régimen, SOX,
   Roca→Chip con sparkline, sentimiento sector), la próxima apertura como
   protagonista (con sus predicciones selladas y pie de emisión), track
   record en maduración mostrado tal cual (0/5), señales del día y noticias.

2. **/aperturas como tabla densa:** cada fila lleva estimado, ±80%, β, R²,
   n, confianza (con degradación por earnings visible) y el estado de
   emisión — "sellada {fecha hora} Chile" o "viva (sin sellar)" en ámbar.
   El pie de la tabla explica la garantía anti look-ahead y qué significa
   el intervalo del 80%.

3. **Bug corregido — fechas de calendario:** un `YYYY-MM-DD` parseado como
   `new Date()` es medianoche UTC, y mostrado en zona Chile retrocede un
   día (el cierre del SOX del 02-jul aparecía como 01-jul). `fechaCorta`
   ahora trata las fechas sin hora como fechas de calendario puras.

Verificación: capturas de ambas vistas con datos vivos del snapshot
sellado de hoy (8 predicciones, emitidas 06:06 UTC); los números de la
tabla son los mismos que sirve /api/aperturas (paridad garantizada por
tests de F1).

## F4 — Vistas /cadena, /mercados y /comparador

1. **/cadena:** 5 tarjetas de eslabón (momentum 20d + sparkline + tickers
   enlazados al detalle), la serie completa del Roca→Chip (Recharts, area
   sobria) y las divergencias como badges con AMBOS spreads (residual y
   simple) — ● marca las activas (|z| > 2).

2. **/mercados:** tabla de betas de contagio con lectura en prosa ("si el
   SOX cayó 1%, la acción tiende a abrir −β%"), el caso Samsung como 3
   StatTiles (KOSPI mismo día / SOX mismo día / SOX día anterior) y el
   heatmap de correlaciones con desfase entre eslabones.

3. **/comparador:** selección por chips, base USD/local con explicación de
   qué significa cada una, períodos 3M–2A, líneas base 100 con paleta sobria
   y SMH punteado gris como benchmark, tabla de métricas del período.

4. **Endpoint añadido — GET /api/universo** (documentado en CONTRATO.md):
   NVDA y AMD tienen `nivel: None` (los diseñadores cruzan eslabones) y por
   eso no aparecen en /api/cadena; el selector del comparador necesita el
   universo completo. Es exposición plana de universo.UNIVERSO — cero
   lógica. Con test de paridad (16 tests en verde).


## F5 — Vistas /historial, /analisis y /detalle

1. **/historial es la vista de integridad:** el 0/5 en maduración se muestra
   en grande con su fecha de primera verificación posible ("06 jul, cuando
   abra la sesión objetivo"), la auditoría de estados lista legacy y
   sin_prediccion sin esconderlos, y las horas de emisión se convierten a
   Chile. La evolución de aciertos aparecerá sola cuando existan datos.

2. **/analisis:** servido íntegramente del cache de noticias.db (la API no
   puede llamar a Anthropic por construcción). Filtro por entidad con
   matching estricto, sentimiento por acción como barras divergentes
   centradas en cero, buzz solo si cruza el umbral 3× con historia ≥7 días.

3. **/detalle/:ticker:** velas de 1 año en moneda local (lightweight-charts),
   señal de apertura vigente con su pie de emisión, métricas del ranking v0,
   correlaciones top y noticias estrictas. Los ADR muestran su aviso de
   duplicado con enlace a la acción original.

4. **Fix de paridad:** la ficha usaba nombres de columna inventados
   ("Momentum 6m %"); ahora usa los reales de motor.puntaje_v0_al
   ("Retorno período %", "Momentum 20d %", "Volatilidad anual %").

## F6 — Cierre de la Etapa 4.7

1. **Guardia responsive:** bajo 1024px el terminal muestra un mensaje
   ("pantallas de 1024px o más — la densidad no se sacrifica") en vez de
   degradar la información. Verificado a 900px con Playwright.

2. **Capturas de referencia** de las 8 vistas + /sistema en docs/capturas/
   (1440px, datos vivos del snapshot del 05-jul).

3. **README-DEV.md:** los tres procesos (API :8000, Vite :5173, Streamlit
   :8501) conviven sin conflicto de puertos; arquitectura, reglas y tests.

4. **CLAUDE.md actualizado** con la sección Etapa 4.7 (regla cero, contrato,
   reglas de diseño del frontend, comandos).

5. **Paridad final:** 16 tests de API en verde; el frontend no computa
   ningún número — todo sale de los mismos motor.py/senales.py que usa
   Streamlit, así que la paridad es por construcción.

**Estado al cierre:** experimento de track record intacto (motor.py,
snapshot.py, noticias.py, alertas.py y las bases sin un solo cambio);
8 predicciones selladas del 05-jul madurando; primera verificación posible
el 06-jul con la apertura de Seúl.

---

# Etapa 4.7.1 — Pulido post-revisión

## P0 — El Roca→Chip del terminal es exclusivamente el sellado

**Regla:** v1 muestra exclusivamente el snapshot sellado con su timestamp;
modo "en vivo" entre snapshots queda diferido a la futura integración de
datos intradía (EODHD), donde se etiquetará como fuente distinta.

La ruta que recalculaba (`_roca_chip_hoy` → `motor.roca_chip_al(hoy)` con
cache de 5 min) se eliminó; /api/hoy y /api/cadena sirven el valor de la
tabla `snapshots` de senales.db, con su fecha. Consecuencias deliberadas:

1. **El "crudo %" desapareció del terminal React:** el snapshot no lo sella
   (solo el percentil), y un número no sellable no se muestra — fue además
   el que más derivó en la revisión (+9.04 vs +10.55). Recuperarlo exigiría
   una columna nueva en senales.py (prohibido en 4.7.x).
2. **La historia del sparkline también es sellada** (un punto por snapshot):
   hoy son 2 puntos y crecerá un punto por día — un sparkline corto y
   honesto vale más que 30 puntos recalculados.
3. La **serie de /cadena** queda como contexto explícito, calculada ANCLADA
   a la fecha del sello (`roca_chip_al(fecha_sellada)` usa solo datos ≤ esa
   fecha): idéntica en cada visita, jamás contaminada por datos posteriores.
4. **Paridad redefinida para este número:** el test compara la API contra la
   tabla `snapshots`, no contra el recálculo vivo (que es lo que muestra el
   Streamlit de fallback — si difieren entre sí, la discrepancia es
   información: el mercado/los datos se movieron después del sello).

Hallazgo registrado durante el fix: el snapshot del 05-jul selló 46
mientras el recálculo estable del mismo día da 63 — los datos de Yahoo al
momento de la emisión (06:06 Chile) diferían de los de la tarde. Es
exactamente la clase de deriva que esta corrección hace visible en vez de
esconder: el terminal muestra 46 "sellado 05-jul", y punto.

El alcance del sello es lo que el snapshot registra (roca_chip,
predicciones — ya sellado desde F1 — y divergencias): los bloques de
contexto (betas de /mercados, correlaciones, comparador) siguen siendo
presentación calculada, como el contrato siempre los trató.

## P1 — La incertidumbre no lleva etiquetas subjetivas

La columna/etiqueta de niveles Alta/Media/Baja se reemplazó por `senal`,
derivada SOLO de umbrales de R² histórico de la regresión de contagio:
**débil (R² < 0.10) · moderada (0.10–0.25) · fuerte (> 0.25)** — los mismos
cortes que el motor ya usaba internamente, ahora explícitos y documentados
en el tooltip de la cabecera. La zona de earnings dejó de degradar la
etiqueta: viaja como marca aparte ("· earnings Nd"), porque mezcla dos
dimensiones distintas (calidad histórica de la regresión vs evento puntual
conocido). Las "señales del día" de portada conservan la semántica previa
con criterio explícito: R² > 0.25 y fuera de zona de earnings.

## P4 — La portada filtra el ruido; /analisis muestra todo

/hoy solo admite titulares con **relevancia ≥ 0.5** (la relevancia 0–1 que
asigna la IA por titular). Los análisis anteriores a la columna relevancia
(NULL en la base — hoy son todos) entran solo si el **matching estricto**
(helper existente `tickers_estrictos` de noticias.py) confirma una empresa
del universo nombrada de forma inequívoca en el texto: así el listicle
genérico etiquetado NVDA queda fuera de portada HOY, sin esperar a que se
re-analice nada. Máximo 5 titulares, los más frescos que pasen el filtro.
/api/noticias (vista /analisis) sigue sirviendo todo sin filtrar — ahí se
explora, en portada se decide. noticias.py y la base: intactos.

## P5 — Sparklines de contexto en gris; el color cruza umbrales

El Sparkline coloreaba verde/rojo según la dirección de la ventana visible
— junto a un índice en zona neutra, una mini-línea roja grita una alarma
que los datos no dicen. Ahora TODOS los sparklines de contexto van en gris
neutro (--color-text-3). El color queda reservado para la cifra principal
del Roca→Chip y solo al cruzar umbrales documentados: **frío < 30 (cian) ·
caliente > 70 (ámbar)**. Ni verde ni rojo: esos siguen reservados para
dirección (subió/bajó), y un percentil alto no es "bueno" ni "malo".

---

# Etapa 4.7.2 — alertas.py con CLI visible; el reporte es fiel al sello

**Contexto:** `python alertas.py` terminaba en silencio total — era una
biblioteca sin bloque de script, y además nadie cargaba `.env` en ese modo
(eso siempre lo hizo app.py), así que ni el token llegaba al entorno.

1. **CLI solo-visibilidad:** `python alertas.py` muestra el estado
   (configuración enmascarada, alertas ya registradas hoy) y explica por
   qué no envió nada; `python alertas.py reporte` fuerza el reporte matinal
   con confirmación "Reporte enviado HH:MM" o "NO enviado: razón";
   `--help` documenta todo. Como biblioteca (import desde app.py) nada de
   esto se ejecuta — la lógica de qué se envía y cuándo no cambió.

2. **El reporte de Telegram lleva el Roca→Chip SELLADO** del último
   snapshot, con la etiqueta "(sellado {fecha})" — igual que el terminal
   React (P0 de 4.7.1). Aplica al CLI y al botón de Streamlit: el mensaje
   de Telegram queda como registro escrito y debe ser fiel al sello, no a
   un recálculo del momento. El hero de Streamlit sigue mostrando el valor
   en vivo (es el fallback en vivo, y en pantalla se recalcula solo).

3. **Sin niveles subjetivos en Telegram:** las líneas de apertura pasan de
   "(Alta/Media/Baja)" a "(señal fuerte/moderada/débil)" con los mismos
   umbrales de R² de 4.7.1, vía `alertas.etiqueta_senal()` — una sola
   definición para el lado Telegram (CLI + botón); la API mantiene la suya
   propia (`_etiqueta_senal`), custodiada por test. La UI de Streamlit
   (columna del anticipador) queda como está: es el fallback congelado.

4. **El reporte programado sale a las 18:25 Chile (post-snapshot), no en
   la mañana** (launchd `com.mki.reporte`, 10 min después de
   `com.mki.snapshot`). Razones: (a) el reporte es fiel al sello — solo
   puede enviar lo que el snapshot de las 18:15 acaba de sellar, y los 10
   minutos dan margen a que el snapshot y el verificador terminen de
   escribir en senales.db; (b) las predicciones anticipan las sesiones de
   Asia, que abren desde las ~20:00 Chile: a las 18:25 el reporte llega
   ANTES de todas sus sesiones objetivo — un envío en la mañana de Chile
   llegaría cuando Asia y Europa ya abrieron y cerraron, con predicciones
   viejas disfrazadas de frescas (la confusión de timing que la regla
   maestra existe para impedir). El reporte es "matinal" respecto del día
   de mercado que comienza en Asia, no de la mañana chilena.

---

# Etapa 4.7.3 — Resiliencia de descarga

**Evidencia (auditoría de la semana 06–10 jul):** de 5 días hábiles solo se
sellaron 2. El viernes 10 fue el Mac apagado (único día perdido por
hardware), pero el lunes 06 y el martes 07 el job disparó puntual (18:16 y
18:22 Chile, Mac encendido) y Yahoo devolvió "possibly delisted / no price
data" para los 27 tickers: el snapshot abortó con "sin datos de mercado" —
correctamente, prefiriendo no sellar antes que sellar basura. El sábado 11,
al despertar el Mac, el reporte de recuperación falló por DNS (red aún
caída). El enemigo operativo demostrado no es el timing: es la fuente.

1. **Reintento del snapshot SOLO en el camino launchd** (`main()`), jamás
   dentro de `ejecutar_snapshot()` — el fallback del dashboard no puede
   quedarse bloqueado una hora. Criterio estricto: solo cuando el motivo
   es "sin datos de mercado"; un sello existente o logrado sigue de largo.
   3 intentos en ~60 min (esperas de 20 y 40 min): ambas esperas superan
   el TTL de 15 min de la caché del motor, así cada reintento descarga de
   verdad SIN tocar motor.py. Un sello logrado al segundo o tercer intento
   lleva su timestamp real de emisión — el verificador de timing sigue
   decidiendo predicción por predicción, como siempre.

2. **Reintento del reporte de Telegram sin fantasmas:** `enviar_mensaje`
   ahora distingue el error de CONEXIÓN (DNS caído, sin red — la petición
   nunca llegó al servidor, reenviar no puede duplicar) del resto. El CLI
   reintenta SOLO ese caso (2 reintentos: 60 s y 120 s), con los argumentos
   compuestos una sola vez — cada intento envía el mensaje idéntico.
   Timeouts y errores HTTP de Telegram NO se reintentan: el mensaje pudo
   haber llegado, y un reporte duplicado fantasma es peor que uno perdido.
   El botón del dashboard queda como estaba: un clic, un intento.

3. **Cero cambios en lógica de señales o sellado:** motor.py intacto;
   `ejecutar_snapshot` intacto; los reintentos solo repiten la misma
   llamada idempotente más tarde, con su hora real.

---

# Etapa 4.9 — "Alta costura" (elevación visual y de interacción)

100% frontend/; la API no cambió su contrato y la paridad numérica se
verificó hermética: el código pre-4.9 y el 4.9 servidos EN PARALELO
(worktree en :5174 vs :5173), mismo instante, mismos 72+60 tokens
numéricos en /hoy y /aperturas. Lighthouse sobre build de producción:
performance 91 · accesibilidad 100 · CLS 0 · TBT 0 ms.

## Decisiones de motion

1. **CSS puro, cero librerías** (sin framer-motion): tokens --dur-fast/
   base/slow (120/200/320 ms) y 3 easings en :root; TODO movimiento los
   usa. El "spring" (--ease-asentar) vive en exactamente DOS lugares:
   command palette y flash de números — la contención es la firma.
2. **Solo transform/opacity/color.** El marcador "ahora" de la cinta se
   mueve con translateX en px medidos por ResizeObserver — alineado al
   sistema de % de las píldoras sin animar `left` (layout). El colapso de
   la cinta (56→8px) es swap instantáneo: un cambio de layout no se
   disfraza animando layout.
3. **Entrada por capas keyed por ruta:** wrapper `.vista` remonta por
   pathname (una corrida por navegación, jamás en re-render); crossfade
   de entrada 150ms contra el chrome estable — sin árboles dobles ni
   AnimatePresence.
4. **NumeroVivo nunca anima el primer render** (un número sellado aparece
   quieto: es un registro) y reserva su ancho en `ch` con tabular-nums —
   el count-up y el flash son pintura pura, cero reflow en tablas
   (afinación pedida en la revisión del plan).
5. **La píldora espera al marcador:** cuando "ahora" cruza un borde de
   sesión, la píldora transiciona con 100ms de delay — las dos
   transiciones no compiten (afinación pedida). El estado abierta/cerrada
   entre refetches se deriva client-side de los timestamps del server:
   presentación pura, jamás una señal.
6. **Flecha de contagio:** pulso de dash-offset a 8s/ciclo SOLO cuando hay
   predicciones vigentes viajando a esa sesión; sin predicciones, la
   flecha queda estática.
7. **prefers-reduced-motion = un interruptor:** tokens a 0ms + kill global
   de animaciones/transiciones; verificado con Playwright
   (animationDuration 0.01ms).

## Decisiones de teclado

8. **Cmd+K sin dependencias:** palette propio (vistas, 27 tickers por
   nombre o símbolo con normalización de acentos, acciones rápidas);
   secuencias g+h/a/c/m/r/i/t con ventana de 1s; ? abre el mapa; nada
   escucha cuando se escribe en un input. Focus ring cyan 2px/offset 2px
   en todo elemento interactivo.

## Estados y detalle

9. **Skeletons con las proporciones del contenido real** (tiles/tabla/
   card) — CLS 0.0 medido; errores con causa visible y botón Reintentar
   (verificado: API bloqueada → banner → reintento recupera); espaciados
   normalizados a múltiplos de 4px (los valores de posicionamiento de la
   cinta no son espaciado y quedaron intactos); título de pestaña
   "MKI · {régimen} · {fecha snapshot}" y favicon SVG trazado como path
   (sin depender de fuentes).

---

# Etapa 5.0.0 — "Plataforma" (plataforma v5.0.0 · modelo congelado v4.6.0)

## ERRATA — sellos degradados por fallos parciales de descarga (8–24 jul)

Los snapshots de estas fechas se sellaron con descargas INCOMPLETAS de
Yahoo. Causa raíz (auditoría del 25-jul sobre el período autónomo 13–24
jul): los jobs de launchd corrieron en DarkWake — el despertador pmset de
las 18:10 solo despierta el Mac ~5 segundos con batería, launchd dispara
en la siguiente ventana (18:22–18:28) y en DarkWake la red funciona a
medias, así que yfinance devolvió lotes parciales. Fechas afectadas,
verificadas contra senales.db:

- **20-jul**: régimen sellado VACÍO (^SOX no descargó) y **0 predicciones**
  selladas (el lote de betas bajó vacío).
- **23-jul**: régimen sellado VACÍO (mismo síntoma; las 8 predicciones sí
  se sellaron).
- **21-jul**: Roca→Chip sellado **13**; la recomputación estable posterior
  del mismo día da **~16**.
- **22-jul**: Roca→Chip sellado **22** vs **~18** recomputado.
- **13-jul**: solo **4 de 8** predicciones selladas.
- **8–9 jul (pre-período)**: sellos tomados bajo la misma mecánica de
  DarkWake; posible afectación de la misma clase, sin recomputación
  concluyente que la cuantifique.

**Ningún valor sellado se corrige** (constitución 5.0: las filas selladas
jamás se reescriben; un error histórico es una errata documentada). Las
métricas del track record NO están contaminadas por esto: el verificador
solo evalúa predicciones efectivamente emitidas, y una predicción no
emitida simplemente no existe — el costo fue de COBERTURA (menos
predicciones, régimen vacío), no de veracidad. Nota: el colapso del
Roca→Chip de mediados de julio (≈50 → 2–5) es REAL — verificado por
recómputo — y no parte de esta errata.

Mitigación en esta etapa: salud de descarga sellada por snapshot (WS2.2),
reintento parcial antes de sellar (WS2.3) y el vigía nocturno (WS2.7).

## WS2 — Decisiones de autonomía de datos

1. **La salud de descarga OBSERVA, jamás descarga** (excepción quirúrgica
   #1). `snapshot.salud_descarga()` inspecciona los mismos DataFrames que
   el motor ya bajó por su punto único `_datos_crudos` (misma caché): no
   existe una segunda vía de datos. "Ok" = el ticker tiene algún dato en
   los últimos 7 días; lo esperado es universo + ^SOX. Se sella en columnas
   nuevas de `snapshots` (migración aditiva) junto a `plataforma_version`
   (versionado dual de la constitución). Tests: observar no cambia ninguna
   señal, y sellar la salud produce filas de predicción BYTE-idénticas a
   no sellarla.

2. **El reintento parcial re-descarga el lote completo, no "solo los
   caídos"** (excepción quirúrgica #2, letra vs espíritu). Descargar solo
   los caídos exigiría inyectar columnas en la caché interna del motor —
   cirugía en motor.py, que es intocable. Re-descargar el lote entero tras
   limpiar la caché logra el mismo efecto (los caídos obtienen 2 nuevas
   oportunidades con esperas de 60/120 s) sin tocar una línea del motor.
   Solo el camino launchd reintenta (`reintentos_parciales=2` en main());
   el fallback del dashboard sigue sin esperar jamás (test explícito). Si
   tras los reintentos aún faltan tickers, SE SELLA IGUAL con la salud
   degradada visible: un sello honesto con hueco documentado vale más que
   un día perdido.

3. **El estado terminal `sin_datos_mercado` exige 5 sesiones de paciencia**
   (WS2.6). Una verificación pasa de `pendiente` al estado terminal solo
   cuando ≥5 sesiones POSTERIORES del mismo exchange ya cerraron y Yahoo
   sigue sin publicar la sesión objetivo (`calendarios.sesiones_cerradas_
   desde`). Contado en sesiones del calendario real, no en días corridos:
   un feriado largo no puede gatillar el estado por error. Es terminal y
   auditable, queda fuera de TODAS las métricas, y jamás se inventa un
   resultado. Aplicado en producción: las 2 coreanas del 16-jul (sesión
   XKRX del 17-jul, que Yahoo nunca publicó) salieron de `pendiente`
   después de 6 sesiones atascadas.

4. **El presupuesto de IA se frena ENTRE lotes, con el bucle desplegado en
   el entrypoint** (WS2.4). `noticias.analizar_pendientes()` procesa todo
   de una vez y no tiene hook de presupuesto; cambiarle la firma violaba
   "cero cambios de lógica interna". El entrypoint `mki_noticias.py`
   despliega el mismo bucle (usando las MISMAS funciones de noticias.py:
   `obtener_titulares_sin_analizar`, `_analizar_lote`, `guardar_analisis`)
   y chequea el tope entre lote y lote. Un typo en la variable de entorno
   no desactiva el guardarraíl (cae al default 0.50). El resumen del día
   no expone `usage`: se registra con estimación conservadora fija de
   0.01 USD y solo corre con ≥0.05 USD de holgura. Primera corrida real:
   429 titulares del backlog congelado analizados por 0.224 USD — bajo el
   tope, capa de noticias viva de nuevo.

5. **El ledger de costos es un JSONL en data/costos_ia.log** — parseable
   para la vista /salud y el vigía, gitignoreado como todo log, y con el
   acumulado del día calculado al escribir. Una línea corrupta se ignora:
   el guardarraíl no puede caerse por un log dañado.

6. **El backup git commitea con pathspec** (WS2.5): `git commit -m
   "Backup diario {fecha}" -- data/backups` — aunque hubiera otras cosas
   staged (una etapa a medias, por ejemplo), SOLO los CSV de respaldo
   entran al commit del job.

7. **El vigía solo LEE y solo alerta** (WS2.7): cinco chequeos (sello,
   salud de descarga, corrida de noticias vía ledger, envío del reporte
   vía log, commit de backup vía git log) y UN mensaje de Telegram si algo
   falló — distinto del reporte diario. No corrige nada por su cuenta: un
   guardián que repara es otro sistema que puede fallar en silencio.

8. **Los plists son plantillas** (`__MKI_DIR__`) y `launchd/instalar.sh`
   genera e instala los 5 jobs con la ruta real deducida — el repo deja de
   contener rutas privadas de la máquina (decisión del GATE A) y la
   instalación baja a un comando. Horarios: noticias 17:50 → snapshot
   18:15 → reporte 18:25 → backup 18:40 → vigía 19:00 (hábiles, Chile).

## WS3 — Reporte de Telegram 2.0 (fiel al sello por construcción)

1. **Un solo compositor, tres puntos de envío.** `componer_reporte_sellado()`
   construye el mensaje COMPLETO desde senales.db (fila del snapshot +
   predicciones selladas + track record) y el cache de noticias.db. El job
   de launchd, el CLI y el botón del dashboard envían exactamente ese
   texto. El compositor no importa motor.py — y un test lo prueba
   dinamitando todas las funciones del motor y componiendo igual. El bug
   del 22-jul (el reporte "tapó" el hueco de régimen recalculando en vivo)
   es imposible por construcción: si el sello tiene un hueco, el reporte
   dice "sin dato sellado hoy ⚠".

2. **Para que el reporte diga SOX y β, SOX y β se sellan** (aditivo). El
   reporte 2.0 exige "solo lo sellado", pero el SOX usado y la beta de cada
   predicción no se sellaban — el motor siempre los calculó y viajaban
   hasta el frame de predicción, así que sellarlos es conservar, no
   computar: columnas `sox_usado_pct`/`sox_fecha` en snapshots y `beta` en
   senales_ticker. Los sellos pre-5.0 tienen NULL → el reporte muestra
   "SOX: sin dato sellado" y omite β (errata implícita, no backfill).

3. **El track record del reporte usa LAS MISMAS consultas que el dashboard**
   (`senales.metricas_apertura`, `calibracion_intervalos`) — el test compara
   el texto contra la salida de esas funciones, no contra números fijos.
   La palabra "confianza" tiene test negativo propio (constitución #4).

4. **Diversidad en la selección de noticias del reporte** (presentación
   pura): el mismo evento desde dos fuentes no ocupa dos de los 3 cupos.
   Umbral 0.55 (más laxo que el 0.85 del dedup de guardado, porque aquí
   descartar de más es barato) evaluado en AMBOS órdenes de
   SequenceMatcher — no es simétrico: el par real Samsung/Broadcom daba
   0.57 en un orden y 0.49 en el otro, y con un solo orden se colaba.
   El pipeline de guardado no se tocó.

5. **`enviar_reporte_matinal()` y `etiqueta_senal()` se eliminaron** de
   alertas.py: componían en vivo (régimen del motor, líneas con etiquetas
   derivadas) — exactamente lo que el 2.0 prohíbe. La API conserva su
   `_etiqueta_senal` propia (custodiada por test de contrato).

## WS4 — Vista /salud y calibración en /historial

1. **`/api/salud` se extendió aditivamente** (contrato enmendado ANTES de
   codear) con el bloque `operacion`: los 5 jobs evaluados por sus
   ARTEFACTOS reutilizando los MISMOS chequeos del vigía (una sola
   definición de "¿ocurrió el día?"), salud de descarga sellada de los
   últimos 10 snapshots, verificaciones por estado con las atascadas
   nombradas, presupuesto de IA con corridas del día, y tamaños de DB.
   `meta` ganó `plataforma_version` y el `snapshot_hoy` la salud sellada
   (versionado dual visible en footer y cabecera del reporte).

2. **Fin de semana no es falla**: el bloque lleva `es_dia_habil` y la
   vista pinta los jobs en gris neutro los sábados/domingos — un "NO se
   selló hoy" sabatino es lo esperado, no una alerta. El vigía ya
   descansaba los fines de semana; la vista respeta el mismo criterio.

3. **La curva de calibración re-escala el sigma SELLADO** — el sello
   guarda ±z80·sigma; la cobertura empírica a otros niveles nominales
   (20–95%) usa z_q/z80 sobre ese mismo sigma. Cero información nueva:
   presentación de números sellados. El test verifica monotonía de la
   curva y coincidencia exacta con la calibración clásica en el punto 80.
   Lectura del gráfico en la propia UI: sobre la diagonal = intervalos
   conservadores (hoy: muy sobre — cobertura 93.8% al nominal 80%).

4. **Wilson al 95% en todo acierto mostrado** (`intervalo_wilson` en
   api/utilidades): las tiles de /historial y los desgloses muestran
   "78.8% · IC95 [68.6–86.3]" — nunca un porcentaje desnudo con n
   pequeño. El desglose es por región (exchange → Corea/Japón/Taiwán/
   Europa/EE.UU.) y por régimen SELLADO del día de emisión; los 8 aciertos
   de días con régimen vacío (la errata del 20/23-jul) forman su propio
   bucket "sin régimen sellado" en vez de esconderse. La advertencia
   honesta (muestra de un solo régimen; el backtest B0–B5 decidirá) quedó
   fija en la tarjeta.

5. **Badge de descarga en la cinta**: extremo derecho, "descarga 27/28" en
   ámbar cuando el sello del día vino incompleto (gris neutro si completo,
   ausente si no hay dato) — el estado de la fuente visible sin salir de
   ninguna vista, con detalle en /salud. Presupuesto de cian intacto (el
   badge usa ámbar/gris).

## WS5 — Motor de backtest B0→B5 (construido, probado, en espera)

1. **La fuente se CONGELA al inicio de cada corrida** (`FuenteCongelada`):
   una descarga, y motor._datos_crudos pasa a servir esos frames por la
   duración del run. Sin esto, el TTL de 15 min de la caché del motor
   re-descargaría a mitad de corrida y los datos cambiarían bajo los pies
   — adiós determinismo. Mismo mecanismo de parcheo que usa
   tests/test_motor.py desde la 4.6: la vía ya auditada.

2. **Features vectorizadas retrospectivas, no llamadas `*_al` por día.**
   Llamar regimen_al/divergencias_al para cada una de ~500 emisiones ×
   250 filas de entrenamiento era inviable. Toda feature se construye UNA
   vez con operaciones exclusivamente hacia atrás (rolling/shift): el
   valor en d usa solo datos ≤ d — point-in-time por construcción, con la
   guardia dura `validar_sin_futuro` en cada acceso. DOS desviaciones
   documentadas respecto del motor: la residualización usa ventana
   RODANTE de 120 (el motor usa expansiva) y la beta·SOX de las features
   B3+ es la reconstrucción cov/var rodante — son features del backtest,
   jamás señales de producción.

3. **B2 es la excepción: llama a motor.prediccion_apertura_al tal cual.**
   Su rol es AUDITAR el modelo congelado, no imitarlo. La auditoría de
   reproducción del humo real: 50 predicciones selladas comparadas,
   diferencia media 0.053 pp, máxima 0.28 pp — el framework reproduce
   producción; el residuo es deriva de datos de la fuente (hallazgo
   4.7.1), y el resumen lo dice con esas palabras.

4. **IC de una predicción constante = 0** (no "sin dato"): así "B1 vs B0"
   del veredicto escalonado es literalmente "momentum vs nada" con series
   emparejadas por fecha, en vez de un hueco.

5. **El humo real (jun–jul, NO-CONCLUYENTE) ya enseñó cosas**: B2 aporta
   sobre B1 (ΔIC +0.38, t 2.57) — consistente con el track record vivo —,
   B3–B5 no demuestran nada en 35 días con 85% de evidencia grado B, y
   NINGUNA cartera capturable sobrevive a 25 pb en la ventana (SMH también
   cayó −7.1%). Exactamente la clase de honestidad que el diseño exige;
   veredicto real: Etapa 5.1.

6. **resultados/**: resumen.md versionable, datos crudos (CSV/JSON)
   gitignorados — se regeneran con el mismo commit (queda anotado el hash
   en cada resumen).

## WS6 — Calidad de ingeniería

1. **El hook pre-commit tiene un camino rápido para el backup diario**: un
   commit que SOLO toca data/backups/ pasa con el escaneo de secretos y
   sin tests — si no, un test rojo por cualquier otra razón bloquearía la
   red de seguridad de datos de las 18:40, que es exactamente lo que no
   puede pasar. `SKIP_TESTS=1` existe para emergencias conscientes y
   queda documentado. Los secretos FALSOS de tests/test_seguridad.py se
   excluyen del escaneo por pathspec (los patrones del hook exigen largo
   de secreto real, pero el fake del test lo cumple a propósito).

2. **Rotación de logs por copy-truncate, sin demonios**: launchd mantiene
   el descriptor del log abierto, así que renombrar no sirve; cada job
   rota SU log al arrancar (registro.rotar_log, 2 MB × 2 copias) copiando
   a .1 y truncando en el lugar — el siguiente write de launchd (append)
   cae limpio al inicio. Cero sudo, cero newsyslog.

3. **Errores homogéneos en la API**: {"detail", "codigo"} para 400/404 y
   un handler global de 500 cuya causa pasa SIEMPRE por
   enmascarar_secretos — un traceback no puede filtrar una clave.
   Contrato enmendado antes del código, con test.

4. **Versiones fijadas en ambos mundos**: requirements.txt es un pip
   freeze curado (solo dependencias directas, con secciones comentadas) y
   package.json quedó en versiones exactas (las instaladas del lock).
   Subir una versión pasa a ser una decisión visible en un diff.

5. **./mki reutiliza, no reimplementa**: `estado` y `auditoria` llaman a
   los MISMOS chequeos del vigía y helpers de senales/costos — una sola
   definición de "¿el sistema está bien?" en todo el proyecto.

## WS7 — Documentación y vitrina

1. **El README lidera con la integridad, no con los aciertos.** La sección
   central es "Integridad de medición" (regla maestra, errata documentada,
   Wilson, palabra prohibida) y TODO acierto aparece con su intervalo y su
   caveat de régimen único — incluso el número estrella (78.8% [68.6–86.3]).
   El humo del backtest se cita CON su parte incómoda (ninguna cartera
   sobrevivió a los costos en la ventana): "así se ve un experimento real"
   es la tesis de marketing Y la verdad.

2. **Los badges son estáticos** (shields.io sin CI): el repo no tiene
   remoto todavía y un badge dinámico mentiría. Tests contados a mano del
   último run local (49) — se actualiza con las etapas.

3. **La captura hero es /hoy de un sábado** — deliberado: muestra el
   sistema en reposo con el sello del viernes (SOX −4.25%, predicciones
   apuntando al lunes de Seúl, noticias del día analizadas) — el estado
   MÁS común en que un visitante lo encontraría.

4. **CLAUDE.md ganó la constitución 5.0 al inicio** (para futuras
   sesiones: las 6 reglas antes que cualquier arquitectura) y una sección
   Etapa 5.0 con los módulos nuevos; las secciones 4.6/4.7 quedan como
   referencia histórica vigente.

## Acta de cierre de la Etapa 5.0.0 (GATE C aprobado, 26-jul-2026)

- Los tres gates humanos ocurrieron y quedaron registrados: GATE A
  (pre-vuelo de seguridad: historia limpia, identidad reescrita con
  respaldo), GATE B (diseño del backtest congelado con tres ajustes del
  usuario: veredicto escalonado, benchmark SMH obligatorio, gatillo 5.1
  fijado) y GATE C (este cierre).
- Verificaciones finales: suite completa en verde (49 pytest + el
  anti-look-ahead del motor, re-ejecutada por el hook en cada commit);
  Lighthouse sobre build de producción móvil 92/100/100 con CLS 0
  (desktop 94/95/100 — el 95 es el contraste del token text-3 del sistema
  4.9, preexistente y deliberado); paridad de números SELLADOS verificada
  con Playwright contra senales.db (Roca→Chip y los 8 estimados);
  launchctl con los 5 jobs registrados.
- Fix de cierre: la guardia responsive (<1024px) pasó de <div> a <main> —
  Lighthouse móvil solo ve esa rama y el documento no tenía landmark. Es
  la única línea de código del commit de cierre.
- Pendientes FUERA del repo, del usuario: rotar el token de Telegram
  (BotFather) y el push manual a GitHub. La Etapa 5.1 (backtest con
  veredicto) espera su gatillo: N ≥ 150 verificadas en vivo + un cambio
  de régimen, o 3 meses continuos (25-oct-2026) — y su decisión.

## Etapa 5.0.1 — Vigía con retractación (03-ago-2026)

Motivación: las noches del 29 y 31-jul el vigía pasó lista a las 19:00
mientras snapshot.py seguía vivo reintentando; alertó "NO se selló hoy",
el sello llegó más tarde (21:23 y 19:40) y la alerta quedó abierta para
siempre. Regla nueva: **una alerta jamás queda sin epílogo.**

1. **El epílogo tiene tres caminos y un solo marcador.** Si a las 19:00
   el snapshot no está sellado, el vigía deja `data/vigia_pendiente.json`
   (fecha, fallas, si había reintentos activos — gitignorado, estado de
   runtime) y la alerta anuncia el re-chequeo. A las 20:30 el pase
   `--rechequeo`: sin marcador → silencio absoluto; sellado → retractación
   "recuperado: sellado HH:MM, descarga N/N"; sin sellar → epílogo "sigue
   sin sellar" y el marcador QUEDA. Si el sello llega aún más tarde (el
   caso real del 29-jul: 21:23), snapshot.py encuentra el marcador al
   terminar y envía la retractación él mismo (`_epilogo_vigia()`, blindado:
   jamás puede romper el camino del sello). Solo la retractación consume
   el marcador; un marcador de otra fecha se ignora (una alerta no cruza
   de día).
2. **"En curso" lo prueba el PROCESO, no el log.** El stdout de launchd
   viaja bufferizado (por eso los bloques del snapshot.log parecen
   desordenados); los anuncios de reintento sí llevan flush=True y sirven
   de detalle, pero la evidencia de "aún peleando" es `pgrep -f
   snapshot.py`, y el estado del sello viene SIEMPRE de senales.db.
3. **El re-chequeo es un job launchd diario (20:30), no un sleep de 90
   min.** El vigía del 27-jul murió con "database is locked": un sleep
   interno habría muerto con él. Y un sleep se congela si el Mac vuelve a
   dormir — exactamente las noches en que más se lo necesita. El sexto job
   es idempotente (sin marcador pendiente sale en silencio) y sobrevive a
   la muerte del proceso de las 19:00.
4. Alcance: el epílogo cubre la alerta con snapshot sin sellar (el
   artefacto central del día); las demás fallas (noticias, backup) siguen
   con la alerta única de las 19:00.
5. Versionado dual: plataforma 5.0.0 → 5.0.1; el modelo sigue en 4.6.0.
6. De paso: `test_verificador_marca_atascadas` usaba fechas FIJAS
   (16/23-jul) y se pudrió solo cuando el calendario avanzó (ambas filas
   pasaron a terminales). Ahora calcula sus sesiones contra el calendario
   XKRX real, relativas a hoy.

## Auditoría de sellos tardíos 29–31 jul (solo lectura, 03-ago-2026)

Verificado contra senales.db y los logs de los 5 jobs. Ninguna fila
sellada se toca (constitución); esto es una nota documentada.

- **29-jul**: launchd disparó el snapshot 18:21 (6 min tarde — despertar).
  Primer lote 27/28: solo ^SOX caído CON LA RED SANA (los otros 27 bajaron
  en el mismo lote) → fallo del lado de Yahoo. Los 2 reintentos parciales
  (60/120 s) fallaron igual, y ahí el proceso quedó CONGELADO — el Mac
  volvió a dormir — hasta ~21:23, cuando despertó, bajó 28/28 y selló con
  su timestamp honesto (01:23:34 UTC). Evidencia del congelamiento, no de
  Yahoo: noticias arrancó 18:05 y su fetch RSS murió a las 20:57 con
  "Remote end closed connection without response" (2h52m para un fetch =
  conexión cortada durante el sueño); su reintento de las 21:47 chocó con
  "database is locked" (el verificador tardío corriendo). El backup de las
  18:44 no tenía CSVs nuevos que commitear (se exportaron recién a las
  ~21:30) — por eso el vigía también acusó backup.
- **Costo en el track record del 29**: NINGUNA predicción quedó
  `no_verificable_timing` — al sellar 21:23, `proxima_sesion_despues_de`
  asignó honestamente la próxima sesión FUTURA: las sesiones asiáticas del
  30-jul ya habían abierto (20:00–21:00 Chile), así que las 7 predicciones
  XKRX/XTAI/XTKS saltaron a la sesión del **31-jul** con el SOX del 29
  (−5.33%) como insumo — dato de dos días para esa sesión; solo IFX.DE
  (XETR abre 03:00 Chile) conservó su objetivo natural 30-jul. Resultado
  verificado: las 7 asiáticas rancias predijeron caídas y el 31-jul abrió
  masivamente al alza (gaps +2.8 a +28.4 pp) → **0/7 en gap y 0/7 en
  dirección** (errores 4.8–33 pp). Las 7 frescas del sello del 30 (SOX
  +8.19%) para la MISMA sesión: 7/7 y 7/7. IFX.DE del 29 acertó su gap
  (error 0.43 pp). Doble consecuencia estructural: la sesión asiática del
  30-jul quedó SIN predicción, y la del 31-jul con DOS por ticker (una
  fresca y una rancia) — ambas legítimas bajo la regla maestra, ambas en
  las métricas.
- **31-jul**: launchd 18:20 (5 min tarde), lote 25/28 (TSM, SMH, IFX.DE —
  de nuevo Yahoo con red sana), un reintento parcial anunciado y de nuevo
  congelado: selló 19:40 (23:40:37 UTC). El vigía pasó lista TARDE también
  (19:16 — otra huella del sueño irregular) y alertó; 24 min después el
  día estaba recuperado, sin retractación. Al ser viernes, el sello de las
  19:40 apuntó a las sesiones del lunes 03-ago — el retraso no costó
  cobertura esta vez. Los CSVs exportados a las ~19:45 quedaron sin
  commitear todo el fin de semana (el backup había corrido 18:41): son los
  cambios pendientes en git de hoy; el job de hoy los recoge.
- **30-jul**: día sano de punta a punta (18:15:05 exacto, 28/28 a la
  primera, sellado 18:15:10) — la diferencia entre una tarde con el Mac
  despierto y una con DarkWake.
- **Veredicto red local vs Yahoo: ambos, en capas distintas.** Los caídos
  puntuales (^SOX; TSM/SMH/IFX.DE) fallaron con la red demostradamente
  funcional → Yahoo. Las HORAS de retraso no las explican los reintentos
  (máx. 3 min de esperas parciales): las explica el proceso congelado por
  el sueño del Mac — arranques tardíos de 4–16 min en todos los jobs de
  esas noches, un fetch RSS de casi 3 horas muerto por conexión cortada.
  El patrón DarkWake de la errata 8–24 jul sigue vivo; la 5.0.1 no lo cura
  (eso es energía/pmset, fuera del repo — ver INSTALACION.md), le pone
  epílogo.
- **Pregunta abierta para el usuario** (decisión de modelo — NO se toca
  sola): ¿debería un sello tardío abstenerse de emitir predicciones cuyo
  objetivo saltó una sesión completa (insumo de 2 días, fuera del diseño
  próxima-sesión de la regresión)? Cambiarlo toca la lógica de emisión;
  queda para la conversación de la 5.1.

---

# Etapa 5.0.2 — Cierre de heridas pre-migración (08-ago-2026)

Última etapa en este Mac antes de migrar los jobs a otra máquina. Solo
lectura salvo dos fixes explícitos (noticias y el mensaje de retractación).

## 1. Noticias muerto (03–07 ago): causa raíz y fix

**Síntoma:** el vigía reportó "noticias: el job NO corrió hoy" los 5 días
hábiles, pese a que com.mki.noticias quedó instalado en la 5.0.

**Causa raíz (con evidencia):** la corrida del lunes 03-ago disparó bien
(17:52:38, dos minutos tarde por el despertador pmset de las 17:48 —
launchd dispara TARDE los eventos perdidos, jamás los salta), registró su
línea de presupuesto en el log… y se colgó PARA SIEMPRE dentro de
`noticias.actualizar_titulares()`: `feedparser.parse()` usa urllib SIN
timeout, y un socket hacia Yahoo quedó ESTABLISHED sin que el otro lado
respondiera ni cortara jamás (verificado con `lsof` el 08-ago: la conexión
seguía viva tras 4 días y 7 horas, con una transacción de noticias.db a
medio camino — el `noticias.db-journal` visible en el árbol). Como
**launchd no re-dispara un label mientras su proceso siga vivo** (un label
= un proceso; `launchctl list` mostraba el PID 53783 ocupando el slot),
las 17:50 del 4 al 7 de agosto se saltaron en silencio. El patrón venía
de antes: las corridas del 27-jul, 29-jul y 31-jul también colgaron horas
en el fetch (la del 31-jul murió 42 HORAS después, el domingo 02-ago, con
"Remote end closed") — solo que sus sockets eventualmente murieron y el
proceso terminó; el del 03-ago nunca murió. Hipótesis descartadas: el
job SÍ estaba cargado en launchd; SÍ disparó; el ledger de costos es el
lugar correcto donde mirar (el job nunca llegó a escribirlo); y el margen
pmset 17:48/17:50 solo explica arranques tardíos de minutos, no la muerte.

**Decisiones del fix:**

1. **`socket.setdefaulttimeout(30)` en el ENTRYPOINT** (mki_noticias.py),
   no en noticias.py — misma doctrina del WS2.4 (cero cambios de lógica
   interna). Cubre feedparser/urllib Y requests (ambos heredan el default
   global cuando no fijan timeout propio); Anthropic (600 s) y Telegram
   (10 s) fijan el suyo explícito por socket y no se ven afectados. Con
   44 feeds y 30 s de peor caso por operación, el job termina SIEMPRE.
2. **El proceso colgado se mató a mano** (kill 53783). La transacción
   colgada de noticias.db se revirtió sola (journal frío, cabecera en
   ceros; `integrity_check` ok, 1514 titulares, último del 30-jul). Los
   titulares no commiteados del 03-ago se perdieron — irrecuperables, los
   feeds RSS rotaron. La semana 03–07 quedó sin capa de noticias: hueco
   documentado, no rellenado.
3. **El vigía ahora nombra el proceso colgado**: si el ledger está vacío
   Y hay un mki_noticias.py vivo, la alerta dice "proceso PID vivo desde
   {inicio}; launchd no re-dispara mientras siga vivo" en vez del ambiguo
   "NO corrió hoy" que estos 5 días no diagnosticaba nada.
4. **Verificación real:** corrida manual del 08-ago con el timeout activo:
   402 titulares en 2.5 min, 402 analizados por 0.2034 USD (bajo el tope),
   resumen regenerado, ledger escrito, chequeo del vigía en verde y el
   slot de launchd libre. Tests nuevos: timeout global fijado al importar
   el entrypoint; alerta del vigía con y sin proceso colgado.

## 2. Forense de sellos tardíos, semana 03–07 ago (solo lectura)

Verificado contra senales.db y los logs. Ninguna fila sellada se toca.

| Día | Disparo | Sello visible (Chile) | Descarga por intento | Predicciones |
|-----|---------|----------------------|----------------------|--------------|
| lun 03 | 18:15:16 | **22:57** | 0/28 → 22/28 → 28/28 | 4 de 8 (3 saltaron a la sesión del 05) |
| mar 04 | 18:19:45 | 18:19 | 28/28 a la primera | 8 frescas (→ 05) |
| mié 05 | 18:20:12 | **21:38** | 26/28 → 16/28 → 28/28 | 8 (7 saltaron a la sesión del 07) |
| jue 06 | 18:24:48 | **~19:08** (la fila dice 18:24) | 28/28 en 4 s; luego caché expirada y re-descarga caída | **0 de 8** |
| vie 07 | 18:21:48 | 18:21 | 28/28 a la primera | 8 frescas (→ lun 10) |

**Atribución red-dormida vs Yahoo-real, por capas (mismo veredicto que la
auditoría 29–31 jul):**

- **Red dormida / DarkWake**: el lote 0/28 del 03 (TODO caído, ^SOX y
  futuros incluidos), el 16/28 del segundo intento del 05 (la red
  degradándose al re-dormirse el Mac), y TODAS las horas de retraso — las
  esperas de 60/120 s se estiraron horas porque el proceso se congela con
  el sueño del Mac (pmset: `sleep 1`, powernap 1 — se duerme al minuto).
- **Yahoo con red sana**: los caídos puntuales — AMD/QCOM en el primer
  intento del 05 (los otros 26 bajaron en el mismo lote), y las descargas
  por-ticker caídas al COMPUTAR el 03 (000660.KS, 005930.KS, 8035.T,
  6857.T → por eso solo 4 predicciones ese día).
- **Anatomía del 06-ago** (el caso nuevo): el lote de salud bajó limpio
  28/28 en 4 segundos (18:24:48→52); el proceso se congeló ~44 minutos EN
  PLENO CÓMPUTO; al despertar (~19:08) el TTL de 15 min de la caché del
  motor había expirado y la re-descarga en la red a medias del despertar
  falló (12 tickers + ^KS11 + ^SOX) → `prediccion_apertura_al` devolvió
  vacío → **0 predicciones y sox_usado_pct NULL**, con régimen y
  Roca→Chip bien sellados (se computaron antes del congelamiento, con la
  caché sana). Hallazgo de honestidad: la salud sellada 28/28 describe el
  lote de las 18:24 que las predicciones nunca llegaron a usar.

**Saltos de sesión y cómo les fue (gap, el objetivo primario):**

- **Sesión del 05-ago** — rancias del 03 (insumo: SOX del 03, +1.05%):
  3/3 en dirección de gap pero **MAE 2.74 pp** (predijeron +0.4/+0.8/+0.4
  y abrió +2.8/+6.5/+0.3 — la dirección la salvó el rebote sostenido, la
  magnitud fue ciega). Frescas del 04 (SOX +6.55%): **8/8 con MAE 0.80
  pp**. Mismo objetivo, mismo mercado: el insumo fresco redujo el error
  3.4×.
- **Sesión del 07-ago** — rancias del 05 (SOX −1.40%): predijeron caídas
  y la sesión abrió mayormente al alza → **1/7 en gap, MAE 2.57 pp**. Y
  NO hubo frescas contra las cuales compararlas: el hueco del 06 dejó esa
  sesión cubierta SOLO por predicciones rancias — el peor de los dos
  mundos a la vez.
- **Acumulado con el precedente 29-jul** (0/7 con errores 4.8–33 pp):
  predicciones con salto de sesión **4/17 (23.5%)** en gap vs **15/15
  (100%)** de las frescas de esas mismas sesiones. Los IFX.DE de sellos
  tardíos que NO saltaron (XETR abre 03:00 Chile) acertaron su gap las
  dos veces (errores 3.21 y 0.03 pp) — el problema es el salto, no la
  hora del sello per se.

**Costo de cobertura de la semana:** 28 de 40 predicciones posibles; 10
de las 28 emitidas con salto de sesión; 12 perdidas (4 del 03 por
descargas caídas, 8 del 06 por el congelamiento).

## 3. La discrepancia del 06-ago: reconstrucción y fix

**Los dos mensajes:** la retractación dijo "recuperado: sellado 18:24";
el reporte de las 18:40 dijo "sin snapshot sellado hoy". La secuencia
real (logs + senales.db) muestra que **el reporte dijo la verdad y la
retractación mintió**:

1. 18:24:48 — snapshot.py arranca (tarde); baja el lote 28/28 en 4 s.
2. 18:24:52 — `ejecutar_snapshot` estampa `ts_emision` (será `creado_en`
   Y `timestamp_utc` de la fila) y empieza a computar. El Mac se
   re-duerme: el proceso queda CONGELADO ~44 minutos con el timestamp ya
   estampado y NADA escrito en la base.
3. 18:40:18 — el job del reporte (disparado tarde, en una ventana de
   DarkWake) lee senales.db: no hay fila → compone el reporte corto de
   400 caracteres "⚠ sin snapshot sellado hoy". **Verdad al momento de
   leer.**
4. 19:08:50 — el Mac despierta; launchd dispara el vigía atrasado (19:00).
   A las 19:08:51.21 lee senales.db: AÚN no hay fila → "FALLA snapshot:
   NO se selló hoy", escribe el marcador y envía la alerta.
5. ~19:08:52 — el snapshot.py descongelado termina de computar (con la
   caché expirada y la re-descarga caída: 0 predicciones), COMMITEA la
   fila y `_epilogo_vigia()` encuentra el marcador recién escrito — UN
   SEGUNDO antes — y envía la retractación 19:08:52.31: "recuperado:
   sellado 18:24, descarga 28/28".

**El bug exacto:** la retractación presentaba `timestamp_utc` (la emisión
estampada ANTES del cómputo) como si fuera el momento en que el sello
EXISTE. En operación normal ambos instantes difieren en segundos; con un
congelamiento entre el estampado y el commit divergen 44 minutos, y el
mensaje contradice a todo lector honesto de la base (el reporte de las
18:40). Ni timezone ni otro día: mismo campo, semántica equivocada.

**Fix (mki_vigia.enviar_retractacion_si_corresponde, con tests):** el
mensaje ahora distingue los dos instantes — "recuperado: snapshot sellado
(emisión 18:24, confirmada a las 19:08), descarga 28/28, predicciones 0
⚠ — el sello no trae ninguna: la próxima sesión queda sin cobertura".
La hora de confirmación es la del propio envío (la lectura que probó que
la fila existe); el conteo de predicciones se añadió porque el
"recuperado" del 06-ago también engañaba por omisión: un día con 0
predicciones no es un día recuperado. La conversión horaria usa la misma
`_hora_chile` del reporte (una sola definición de "hora local").

**Preguntas abiertas para el usuario (NO tocadas — semántica de medición):**

- `ts_emision` se estampa antes del cómputo y `creado_en = timestamp_utc`
  por construcción: ningún campo registra cuándo la fila se hizo VISIBLE.
  Si un congelamiento cruzara la apertura de una sesión objetivo, una
  predicción committeada DESPUÉS de esa apertura pasaría el chequeo de
  timing con su timestamp pre-congelamiento (el 06-ago no pasó: selló 0
  predicciones). ¿Debe estamparse la emisión justo antes de guardar?
  Interactúa con la regla maestra — decisión humana, no de plataforma.
- La retractación del 03-ago (23:44) murió con "Connection reset" y NO se
  reintenta (el reintento de conexión existe solo en el CLI del reporte):
  esa alerta quedó sin epílogo pese a la 5.0.1. ¿Merece la retractación
  el mismo reintento-solo-ante-error-de-conexión?

## 4. Propuesta formal: regla de abstención de sellos tardíos (NO implementada)

**Regla propuesta:** *un sello tardío se abstiene de emitir predicciones
cuya sesión objetivo saltó una sesión completa* — es decir, cuando entre
el cierre del SOX usado (`available_at`) y la apertura de la sesión
objetivo media una sesión entera de ese exchange que ya transó sin
predicción. La abstención se registra como estado auditable propio (p.
ej. `abstenida_timing`), fuera de todas las métricas, igual que
`no_verificable_timing`: el hueco se declara, jamás se rellena.

**Fundamento de diseño:** la regresión de contagio está especificada como
"próxima apertura tras el cierre del SOX". Con salto de sesión el insumo
tiene dos días de edad y el mercado objetivo ya absorbió una sesión
completa de información nueva (incluida la sesión de EE.UU. de en medio):
la predicción emitida está estructuralmente fuera de especificación, no
es simplemente "más incierta".

**Evidencia acumulada (29-jul + semana 03–07 ago):**

| Emisión | Saltadas | Gap acertado | Error | Frescas misma sesión |
|---------|----------|--------------|-------|----------------------|
| 29-jul (sello 21:23) | 7 | 0/7 | 4.8–33 pp | 7/7 (las del 30-jul) |
| 03-ago (sello 22:57) | 3 | 3/3 | MAE 2.74 pp | 8/8, MAE 0.80 pp (las del 04) |
| 05-ago (sello 21:38) | 7 | 1/7 | MAE 2.57 pp | no hubo (hueco del 06) |
| **Total** | **17** | **4/17 (23.5%)** | | **15/15 (100%)** |

Contras honestos, dichos con todas sus letras: n=17 es chico; toda la
ventana es un mismo régimen (rebote alcista fuerte — el caveat de régimen
único del Historial aplica entero); y el 03-ago muestra que la dirección
a veces sobrevive por inercia del mercado (3/3 con magnitud ciega — la
regla habría abstenido 3 aciertos). El costo de abstenerse es perder esos
aciertos de suerte direccional; el beneficio es no inyectar al track
record una clase de predicción que el diseño de la regresión no cubre.

**Qué NO se hace (explícito):** esta regla NO se implementa en el modelo
4.6.0. Cambia qué se emite → es lógica de emisión → regla cero: el modelo
está congelado y el track record limpio encadenado a esa versión. Es
**candidata a nacer en el modelo retador de la próxima etapa** (la
conversación de la 5.1), donde además el backtest puede simularla
marcando retrospectivamente las emisiones que habrían sido abstenidas
(B2 reproduce las selladas; el flag es presentación, no re-emisión) para
medir su efecto exacto sobre las métricas antes de adoptarla.

# Etapa 5.0.3 — Reactivación en PC: entorno y portabilidad (Fases 0–2, 25-ago-2026)

Contexto completo en `docs/REACTIVACION.md`. Tras la pérdida del SSD del
PC —y con ella los 4 commits locales de la migración, nunca pusheados— el
repo se reclonó limpio desde GitHub. **El Mac sigue siendo titular** y
sella todas las noches. Esta etapa toca solo entorno y plataforma:
`motor.py`, `snapshot.py`, `noticias.py`, `alertas.py`, `senales.py` y las
bases quedaron intactos (regla cero). Todo el trabajo vive en la rama
`migracion-wsl`; `main` es el carril del Mac, y si `main` avanzara con los
scripts portados el titular se los llevaría en su próximo pull.

Las secciones 1–3 registran hallazgos de las Fases 0 y 1 (entorno
restaurado); las 4–11, el port de la Fase 2.

## 1. Asimetría de intérprete, declarada ANTES de ver resultados

El Mac (titular) corre **Python 3.11.15**; el PC corre **3.14.4**, que es
el `python3` que trae esta Ubuntu y era también el del PC que se perdió.
Nunca se igualó al titular: **la migración introdujo esa diferencia desde
el día uno sin declararla**.

**Decisión: NO igualarla.** Tres razones:

1. El PC perdido corrió 3.14.4 con este mismo `requirements.txt` y dejó la
   suite en verde. No es territorio inexplorado.
2. Las librerías que hacen el álgebra son **idénticas** en ambas máquinas.
   Verificado en destino: `pandas 3.0.3`, `numpy 2.4.6`, `yfinance 1.5.1`,
   `exchange-calendars 4.13.2`. El intérprete no hace la aritmética; esas
   librerías sí, y están fijadas.
3. Existe ahora un control **más fuerte** que igualar intérpretes: las dos
   máquinas parten de la **misma `senales.db`**, copiada del Mac. Comparar
   sellos sobre la misma historia es una prueba mejor que suponer
   equivalencia por igualdad de versión.

Queda como **asimetría conocida**, de la misma familia que el
`TimeoutStartSec` finito del PC frente a launchd (que no tiene
equivalente). **Escalamiento definido de antemano:** si el modo sombra
vuelve a mostrar β sistemáticamente distintas, el siguiente experimento es
instalar `pyenv` con 3.11.15 — ya con hipótesis formada, no a ciegas.

**Por qué se escribe AHORA:** antes de que abra la ventana de sombra. Una
asimetría anotada *después* de ver resultados no vale lo mismo: deja de
ser una predicción sobre qué puede salir mal y pasa a ser una explicación
buscada para lo que ya salió. Es el mismo criterio que la regla maestra
aplica a las predicciones del modelo.

## 2. Pendiente #2 del acta 5.0.2: CERRADO

`NOTICIAS_PRESUPUESTO_USD_DIA` **tampoco está definida en el `.env` del
Mac.** El acta suponía que el PC caía al default de 0.50 mientras el Mac
tenía valor propio; resulta que **ambas máquinas estaban en 0.50**. No hay
nada que igualar.

Consecuencia para el diagnóstico pendiente: queda **descartada una de las
dos causas candidatas** de la divergencia del 14-ago. La otra —el desfase
de una sesión en los datos de precio, coherente con el `N=148 vs 147`—
sigue en pie y **pasa a ser la principal**.

Se dejó fuera del `.env` del PC **a propósito**: igualar por omisión
también es igualar, y añadir la variable con su propio default habría
introducido una diferencia de forma donde no hay diferencia de fondo.

## 3. Deuda declarada: `pd.concat` y el futuro pandas 4

La suite emite `Pandas4Warning` en dos lugares — `motor.py:215`, que es
**la regresión de betas**, y `api/main.py:666-668`:

> *Sorting by default when concatenating all DatetimeIndex is deprecated.
> In the future, pandas will respect the default of `sort=False`.*

**Hoy es inofensivo** porque `requirements.txt` fija `pandas==3.0.3` en
ambas máquinas, y para eso existe el pin. El riesgo aparece **el día que
alguien suba pandas a 4**: el `concat` cambia su default y las β pueden
moverse **en silencio**, sin que ningún test lo grite — el anti-look-ahead
prueba no-contaminación temporal, no estabilidad numérica entre versiones
de librería.

`motor.py` es intocable, así que hacer el `sort=` explícito **no es un fix
casual**: es preservación del comportamiento actual y hay que demostrarla
**byte-idéntica**, como el proyecto ya hizo con las dos excepciones
quirúrgicas del WS2. **NO se arregla ahora.**

Queda registrado como deuda y como **bloqueador explícito de cualquier
upgrade de pandas**: subir pandas sin esa demostración previa es una
operación prohibida.

## 4. Ramificar por `uname`, no reemplazar

Tres archivos eran `#!/bin/zsh`: `mki`, `scripts/pre-commit` y
`launchd/instalar.sh`. En la Ubuntu del PC **no hay zsh instalado**, así
que el port no era cosmético: los tres eran inejecutables aquí.

La tentación era escribir una versión Linux y listo. **Se descartó.** El
Mac corre en producción exactamente estos mismos archivos: si `main`
recibiera scripts Linux-only, el titular perdería sus jobs de launchd en
su próximo pull. La decisión es que **un solo archivo sirva a las dos
máquinas y ramifique por `uname -s`**:

| | macOS (titular) | Linux/WSL2 (sombra) |
|---|---|---|
| `./mki estado` | `launchctl list \| grep com.mki` | `systemctl --user list-timers 'mki-*'` |
| `./mki instalar` | `bash launchd/instalar.sh` | `bash systemd/instalar.sh` (con confirmación, §6) |

Lo demás (`arrancar`, `reporte`, `tests`, `auditoria`) no era específico
de plataforma y quedó **idéntico salvo los zsh-ismos**: el `echo "\n== ..."`
de zsh, que en bash imprime la barra invertida literal, se partió en un
`echo ""` más el `echo` del título. Mismo texto en pantalla, en las dos
máquinas.

**Compatibilidad hacia atrás con el titular — la línea exacta.** macOS
todavía trae **bash 3.2** (por licencia: las versiones 4+ son GPLv3). Los
tres portados se escribieron para ese piso. Lo que **sí** existe en 3.2 y
por tanto era usable: `[[ ]]` (desde 2.02) y los **arreglos indexados**
(desde 2.0). Lo que **no** existe hasta bash 4 y queda prohibido en estos
tres archivos: **arreglos asociativos** (`declare -A`), **`mapfile`/
`readarray`** y la **modificación de caso** (`${var,,}`, `${var^^}`).

En la práctica se fue más conservador que la línea real —tampoco se usan
`[[ ]]` ni arreglos— y no costó nada, pero la línea que importa es la de
arriba: es la que hay que verificar antes de tocar estos archivos.
(`systemd/instalar.sh` sí usa `[[ ]]` y arreglos, y puede: nunca se
ejecuta en macOS.)

Dos detalles menores del mismo criterio:

- El `export PATH="$HOME/.local/node/bin:$PATH"` era la convención del
  Mac (node sin brew/sudo). Ahora se antepone **solo si el directorio
  existe**; en Linux node viene del sistema (`/usr/bin/node`) y el PATH no
  se ensucia. El Mac no nota diferencia.
- `dirname "$0"` pasó a `dirname "${BASH_SOURCE[0]}"`.

## 5. `launchd/instalar.sh` sigue siendo de macOS, pero ahora lo dice

Este instalador no se "porta" en sentido fuerte: launchd no existe en
Linux, y su equivalente es `systemd/instalar.sh` (ya escrito y trackeado).
Lo que cambió es el shebang a bash y **una guarda al inicio**: si
`uname -s` no es `Darwin`, aborta con exit 1 y nombra el reemplazo. Es
para el humano que lo invoque a mano en la máquina equivocada; `./mki
instalar` ya elige bien solo.

## 6. `./mki instalar` bajo Linux pide confirmación — y cuándo se retira

**El riesgo:** instalar los 6 timers en el PC antes de que exista el modo
sombra (Fase 3) lo convierte esa misma noche en un **segundo titular**:
manda su propio reporte de Telegram duplicado, commitea backups y sella en
paralelo con el Mac. Es la advertencia central del brief de reactivación, y
es una acción hacia afuera (Telegram) difícil de deshacer.

Por eso, **solo en la rama Linux**, `./mki instalar` explica el riesgo y
pide escribir `si` antes de correr `systemd/instalar.sh`. Sin TTY no
instala salvo `MKI_INSTALAR_TIMERS=si` explícito. El hook pre-commit se
instala siempre, en las dos ramas — nunca fue el peligro.

**Condición de retiro (explícita, porque la guarda protege un estado
transitorio y su justificación caduca).** Se retira en dos tiempos:

1. **En la Fase 3 deja de ser una asimetría de plataforma.** La condición
   real de la guarda **no es "estoy en Linux"** sino **"el modo sombra no
   está configurado"**. Hoy las dos coinciden y por eso se codificó la
   primera —el modo sombra no existe todavía, así que preguntar por él
   sería circular—, pero la forma correcta es la segunda: es un chequeo de
   *estado*, válido en ambas máquinas, no un juicio sobre el sistema
   operativo. Ver §10.
2. **Se retira entera cuando termine la migración**: cuando el switch de
   la Fase 5 esté hecho, el PC sea titular y **el Mac haya dejado de
   sellar**. En ese momento ya no existe la posibilidad de dos titulares
   —que es lo único contra lo que la guarda protege— y quedaría como
   fricción que nadie recuerda por qué está.

Mientras tanto se queda. Este párrafo existe para que el retiro sea una
decisión con criterio escrito, y no un hallazgo arqueológico dentro de un
año.

## 7. El hook no ramifica, y el Mac no lo hereda solo

`scripts/pre-commit` no tenía nada específico de plataforma: solo el
shebang. Quedó en bash, sin ramas. Verificado en Linux que las tres rutas
siguen intactas: bloquea ante patrón de secreto real (exit 1), salta con
`SKIP_TESTS=1`, y salta los tests cuando lo stageado es *solo*
`data/backups/` (para que el backup diario jamás quede bloqueado).

**Detalle operativo que conviene tener escrito:** `./mki instalar` *copia*
`scripts/pre-commit` a `.git/hooks/pre-commit`. El Mac conserva su copia
zsh instalada —que sigue funcionando, allá zsh existe— hasta que alguien
corra `./mki instalar` en el Mac. No hay ventana de rotura: la versión
vieja funciona hasta ser reemplazada por una que también funciona.

## 8. `PLATAFORMA_VERSION` sube a 5.0.3

`version.py` pasa de `5.0.2` a **`5.0.3`**. `MODELO_VERSION` sigue en
**4.6.0**, intocado.

**Por qué subir y no renombrar la sección.** `plataforma_version` se sella
en cada snapshot (columna 14 de `senales_snapshots.csv`; hoy hay filas en
5.0.0 ×5, 5.0.1 ×5 y 5.0.2 ×11, más 14 pre-5.0 en blanco). Ese campo es
una **afirmación de procedencia**: dice qué código produjo la fila. El
código del PC genuinamente ya no es el que describe 5.0.2 —los tres
scripts cambiaron de intérprete y de comportamiento por plataforma—, así
que sellar 5.0.2 desde aquí sería una afirmación falsa. Y como **las filas
selladas jamás se reescriben**, la única oportunidad de que ese campo sea
correcto es en el momento de la emisión. Es exactamente el mecanismo para
el que existe el versionado dual: la plataforma evoluciona, el modelo no.

**Durante la ventana de sombra el Mac sellará `5.0.2` y el PC `5.0.3`.**
Esa diferencia es **LEGÍTIMA**: el código genuinamente difiere entre las
dos máquinas mientras `migracion-wsl` no se funda con `main`. No es una
divergencia a diagnosticar; es la etiqueta que dice qué máquina produjo
cada fila, y durante la migración eso es información útil, no ruido.

**Requisito para `comparar_sombra.py` (Fase 3):** debe **esperar** esa
diferencia en vez de reportarla. En la comparación del día 1 la plataforma
figuraba entre los campos que coincidían — **ese campo cambia de
significado durante la migración**: deja de ser un invariante que valida
la comparación y pasa a ser un discriminador esperado. Un comparador que
lo trate como antes va a gritar divergencia todas las noches y a enterrar
la señal que sí importa. Ver §10.

## 9. Lo que esta fase NO resuelve

- **Los timers NO se instalaron.** El PC no tiene jobs y no sella. El
  orden es sombra (Fase 3) → timers (Fase 4), nunca al revés.
- **Bloqueador de la Fase 4 — RESUELTO el 25-ago.** Cuando se escribió
  esta sección, en esta WSL **systemd no estaba activo como PID 1**
  (`ps -p 1 -o comm=` devolvía `init(Ubuntu)`) y `systemctl --user` no
  tenía bus al que hablar. Tras aplicar `[boot] systemd=true` en
  `/etc/wsl.conf` y `wsl --shutdown`, PID 1 es `systemd` y
  `systemctl --user list-timers` responde («0 timers listed» — sin
  instalar, que es lo correcto en esta fase). Se deja escrito el hallazgo
  y su cierre en vez de borrarlo: la próxima máquina va a tropezar con lo
  mismo. `systemd/instalar.sh` ya aborta con ese
  mensaje; ahora `./mki estado` también lo **distingue de "ninguno
  instalado"** — decir "ninguno instalado" cuando en realidad no se puede
  preguntar sería falsa tranquilidad justo en el chequeo de salud, y es el
  mismo criterio de honestidad que rige el resto del sistema ("pendiente"
  jamás se rellena con un número).
- Las asimetrías declaradas siguen en pie: intérprete 3.14.4 (PC) vs
  3.11.15 (Mac) (§1) y `TimeoutStartSec` finito en systemd frente a
  launchd, que no tiene equivalente.
- La deuda de `pd.concat` (§3) sigue abierta y sigue siendo bloqueador
  explícito de cualquier upgrade de pandas.

## 10. Requisitos que esta fase deja escritos para la Fase 3

1. **La guarda de `./mki instalar` cambia de condición**: de "estoy en
   Linux" a "el modo sombra no está configurado" (§6.1). Deja de ser
   asimetría de plataforma y pasa a ser chequeo de estado, correcto en
   ambas máquinas.
2. **`comparar_sombra.py` debe esperar `plataforma_version` distinta**
   entre Mac (5.0.2) y PC (5.0.3), no reportarla como divergencia (§8).

## 11. GATE 1 repetido tras el port

`python -m pytest tests/ -q` → **70 en verde**, y `python
tests/test_motor.py` → anti-look-ahead limpio en las tres fechas de
prueba. Ejecutados vía `./mki tests` ya portado, y además con el hook
portado en el camino real (`bash scripts/pre-commit` sobre lo stageado),
no solo a mano.


---

# Etapa 5.0.3 (continuación) — Fase 3: el modo sombra

Reconstrucción de lo que se perdió con el SSD: `MKI_MODO=sombra`,
`comparar_sombra.py` y `docs/SOMBRA.md`. `motor.py` y la lógica de señales,
sin tocar. Timers sin instalar (eso es la Fase 4).

## 12. Por qué esto NO abre una 5.0.4

`PLATAFORMA_VERSION` se queda en **5.0.3** y esta fase extiende esa etapa
en vez de abrir una nueva. Razón: **ninguna fila ha sellado jamás 5.0.3**.
El PC todavía no ha sellado nada y el Mac sigue en 5.0.2, así que 5.0.3 no
es todavía una afirmación hecha sobre filas existentes — es una **etiqueta
en definición**. Ampliar su alcance mientras nadie la ha usado no
contradice ninguna fila sellada; abrir una 5.0.4 antes de que la 5.0.3
sellara una sola vez habría dejado un número muerto en el historial de
versiones.

El criterio completo, para la próxima vez, tiene dos mitades y la segunda
importa más que la primera:

1. **Una versión de plataforma se congela en el momento en que la primera
   fila la sella.** Antes de eso sigue siendo editable: nadie ha afirmado
   nada todavía.
2. **Una vez congelada, no se reabre.** Desde el instante en que existe una
   fila sellada con la versión X, cualquier cambio posterior de plataforma
   —por pequeño que sea— exige una versión **nueva**. Ampliar el alcance de
   X después de que X ya etiquetó filas convertiría esas filas en
   afirmaciones falsas de forma retroactiva, y como las filas selladas
   jamás se reescriben, no habría manera de corregirlo: quedarían diciendo
   que las produjo un código que no es el que las produjo.

Es el mismo principio que ya rige las filas selladas, aplicado al
versionado que las etiqueta. La primera mitad es la que permitió esta
decisión; la segunda es la que impide abusar de ella la próxima vez. En
cuanto el PC selle su primera fila, la 5.0.3 queda cerrada y el siguiente
cambio de plataforma es 5.0.4 sin discusión.

Consecuencia práctica: lo escrito en §8 sigue vigente palabra por palabra
—el Mac sella 5.0.2, el PC 5.0.3, la diferencia es legítima y
`comparar_sombra.py` la espera—, y esa expectativa es también la que el
brief de la Fase 3 fijó.

## 13. `modo.py`: un solo lugar donde vive el modo

El modo no se lee con `os.environ.get("MKI_MODO")` esparcido por cuatro
archivos, sino en `modo.py`. Tres razones: el default correcto (titular)
tiene que estar en un solo sitio; `snapshot.py` y `mki_backup.py` **no
cargan `.env`** por su cuenta (sí lo hacen el vigía, noticias y el
dashboard), así que `modo.py` llama a `load_dotenv()` al importarse y el
modo se lee igual desde cualquier entrypoint; y el texto de estado
(`descripcion()`) es uno solo para logs y para `./mki estado`.

`load_dotenv()` no pisa lo que ya está en el entorno, así que
`MKI_MODO=sombra python ...` sigue mandando sobre el `.env`.

**Falla segura ante typo — la decisión que más importa aquí.** Un
`MKI_MODO=sombrra` que cayera silenciosamente a titular convertiría al PC
en un segundo titular esa misma noche: Telegram duplicado y commits en
paralelo. Por eso un valor **puesto pero ilegible cae a SOMBRA**, con
aviso ruidoso, nunca a titular. Ausente sigue siendo titular — el Mac no
define la variable y no debe tener que definirla, y ese es el caso que no
puede romperse. Es el mismo criterio del tope de gasto de `costos.py`, que
ante `.env` ilegible cae al valor conservador: **el error barato es
abstenerse, el caro es emitir.**

## 14. Telegram se intercepta en UN punto, y devuelve `ok=True`

`alertas.enviar_mensaje()` es el único punto de salida a la red del
sistema entero: el reporte, las alertas del vigía, las retractaciones y el
aviso de tope de gasto pasan todos por ahí. La interceptación va **solo**
en esa función. Una segunda vía de salida sería una fuga, y hay un test
que hace explotar `requests.post` para probar que en sombra nadie lo
llama.

Se intercepta **antes** del chequeo de configuración de Telegram: el log
de sombra debe registrar todo lo que la máquina habría emitido,
independientemente de si tenía credenciales.

**Devuelve `ok=True` a propósito.** Es contraintuitivo —el mensaje no
salió— pero es lo correcto: en sombra el resto del sistema debe
comportarse **exactamente** igual que en producción. Con `ok=True` el
anti-duplicados de `alertas.db` registra igual y el vigía consume su
marcador pendiente igual. Si devolviera `False`, la sombra ejercitaría los
caminos de error en vez de los caminos normales, y la ventana estaría
comparando dos sistemas que no hacen lo mismo. El detalle devuelto dice
`interceptado por MKI_MODO=sombra (no salió a la red)`, así que ningún log
afirma "enviado".

El texto pasa por `enmascarar_secretos()` antes de llegar al log, como
todo lo que puede terminar en un archivo (regla de `seguridad.py`), y el
registro nunca levanta: que falle el log no puede convertirse en un envío
real ni tumbar el job.

## 15. El backup en sombra no toca ni el índice de git

`mki_backup.py` en sombra registra el modo en su log y **retorna antes de
`git add`**. No es solo "no commitear": no se toca el índice. El árbol de
trabajo es el código que los timers ejecutan esa misma noche, y dejar
cosas stageadas es exactamente la clase de efecto lateral que la ventana
no puede permitirse.

**El bug conocido, corregido de entrada:** el vigía reportaba *"backup:
sin commit hoy"* como falla. En sombra, no commitear **es** el
comportamiento correcto, así que `chequear_backup()` devuelve OK con el
motivo explícito. Era una falsa alarma que habría sonado las tres noches
de la ventana —justo los días que hay que leer con cuidado— y habría
enseñado a ignorar al vigía. Hay contraprueba en los tests: en titular el
chequeo real sigue vivo, para que la corrección no lo apague para el Mac.

## 16. El comparador: qué se comparó, con qué criterio, y qué se negó a comparar

### La fecha de corte es lo primero que se evalúa

`FECHA_CORTE = 2026-08-24`, constante declarada arriba del archivo con su
justificación. Las bases del PC son copia por pendrive de las del Mac
hasta ese día **inclusive**: para cualquier fecha anterior las dos
máquinas no tienen datos parecidos, tienen **el mismo archivo**. El
comparador **se niega** y lo dice en el veredicto. Un comparador que
reportara esa paridad trivial sin avisar sería peor que no tenerlo:
produciría tres días verdes en una tarde y habilitaría un switch sobre
evidencia vacía.

Queda anotado en `docs/SOMBRA.md`: **si se recopian las bases del Mac
antes de abrir la ventana, hay que subir `FECHA_CORTE` al nuevo día de
copia.**

### La tolerancia amplia era la trampa

La intuición ingenua —"son floats, pon tolerancia amplia"— habría
escondido justo lo que la ventana existe para detectar. Las dos máquinas
corren pandas 3.0.3 y numpy 2.4.6 **idénticos** sobre la misma ventana de
120 sesiones: con los mismos insumos los números deben salir iguales.
Nivel 1 usa tolerancia relativa `1e-9`.

**Observación de precisión real, que hace el nivel 1 más fuerte de lo que
suena:** estos campos se sellan **ya redondeados** (beta y apertura a 2
decimales, R² a 4). Sobre valores redondeados, `1e-9` relativo equivale a
exigir el **mismo valor almacenado**. La diferencia más pequeña
representable en beta es `0.01`, que no es ruido de coma flotante sino
insumos distintos — y hay un test que lo fija: `beta 0.38 vs 0.39` rompe
la paridad.

**La contracara honesta:** un valor que caiga justo en el borde del
redondeo podría inclinarse a un lado en una máquina y al otro en la otra.
Por eso todo hallazgo de nivel 1 reporta ambos valores **y su delta**: un
delta de exactamente una unidad del último decimal merece mirarse antes de
tratarlo como evidencia dura. Pero se reporta igual — **jamás se
silencia**, que es la diferencia entre una tolerancia y una excusa.

### Tres campos añadidos al criterio del brief

El brief fijó las listas; se le agregaron tres campos, y conviene que
quede escrito por qué:

- **`puntaje_v0` al nivel 1.** Se deriva solo de precios, igual que beta y
  la apertura. Dejarlo fuera habría dejado una señal derivada de precios
  sin vigilar, justo la clase de cosa que el desfase de una sesión mueve.
- **`n_muestra` al nivel 2.** Es la **firma exacta** de la divergencia del
  14-ago (`N=148 vs 147`), que es la hipótesis principal viva tras
  cerrarse el pendiente #2. Es el campo más diagnóstico disponible.
- **`sox_fecha` al nivel 2.** Si las dos máquinas usaron cierres del SOX
  de días distintos, todo lo demás da igual: ahí está la causa.

Y tres exclusiones, también deliberadas: `id` (rowid local, sin
significado compartido) queda fuera por completo; `estado` va al nivel 3
porque lo escribe el verificador después, en cada máquina por su cuenta y
en momentos distintos —compararlo sería comparar relojes de verificación,
no sellos—; y `origen` al nivel 3 porque describe cómo se disparó la
corrida, no qué se calculó.

**Diferencia de esquema ≠ diferencia de valor.** Si una columna existe en
una máquina y no en la otra, se reporta como hallazgo de esquema en vez de
dejar que un `.get()` devuelva `None` y parezca un valor distinto.

### Los tres veredictos, y por qué no son dos

`PARIDAD` / `DIVERGENCIA` / `DIA_NO_COMPUTABLE`. El tercero existe porque
**"nada = nada" nunca es paridad**: si el titular no selló esa noche, no
hay contra qué comparar y el día es **perdido**, no bueno. El comparador
verifica explícitamente que exista fila del titular antes de evaluar nada.

La asimetría que importa: **si el titular selló y la sombra no, eso es
`DIVERGENCIA`, no día perdido.** Es la sombra fallando, que es exactamente
lo que la ventana existe para detectar; esconderlo como "no computable"
sería el mismo autoengaño que la paridad trivial.

**Racha:** `PARIDAD` suma; `DIVERGENCIA` la vuelve a cero (así se comportó
el día 1 del 14-ago); `DIA_NO_COMPUTABLE` no suma **ni rompe** — es un día
perdido, y no es evidencia ni a favor ni en contra. El contador muestra
las dos cifras (días con paridad y racha actual) para que un
`DIA_NO_COMPUTABLE` intercalado no se lea como progreso.

### Lectura sin `pull`, y salida a archivo

`git fetch` + `git show origin/main:data/backups/<archivo>.csv`. **Nunca
`git pull`** (pendiente #3 del acta): el árbol de trabajo es el código que
los timers ejecutan esa misma noche y un merge lo alteraría bajo los pies.
Hay un test que **falla si la cadena `pull` reaparece** en el archivo — la
regla se vigila sola, no depende de que alguien la recuerde.

El lado local sale de `senales.db` en `mode=ro`: es la base que va a
convertirse en el track record, y los CSV son su exportación. Se lee la
fuente, no la copia. Nada del comparador escribe en el árbol ni en el
índice.

La salida es un **reporte por fecha** en `data/sombra/comparacion_<fecha>.md`
que declara el criterio completo, la revisión de `origin/main` usada, la
procedencia de los dos lados y la fecha de corte — para que se pueda
releer en tres semanas y entender qué se comparó. El veredicto se acumula
además en `data/sombra/veredictos.jsonl` para el contador. Un veredicto en
pantalla y nada más habría sido inauditable.

## 17. `docs/SOMBRA.md` deja una pregunta SIN responder, a propósito

El checklist de switch plantea, y **no resuelve**, qué pasa con los días
de solapamiento: las dos máquinas sellan las mismas fechas, y al pasar el
PC a titular su base tendrá la historia copiada del Mac **más** sus
propios sellos de sombra para esos días. ¿Cuáles son canónicos? Las filas
selladas jamás se reescriben, así que no se puede sobreescribir — **¿y
borrar cuenta como reescribir?**

Es decisión humana y tiene que quedar resuelta y escrita **antes** del
switch; si no, el track record se corrompe en silencio. El documento
aporta el material para decidir (que las filas de un día en paridad
igualmente difieren en `plataforma_version`/`timestamp_utc`/`creado_en`, y
que el proyecto ya tiene precedente de estados terminales conservados y
fuera de todas las métricas) pero **no elige**. Está marcada **SIN
RESOLVER** y en el checklist como bloqueante.

## 18. La fecha de corte no puede depender de la memoria de nadie

`FECHA_CORTE` es una constante que alguien tiene que acordarse de subir si
las bases se vuelven a copiar del Mac. **Depender de la memoria humana
justo para el chequeo que evita la paridad falsa es apoyarse en el punto
débil equivocado**: el día que se recopien las bases es un día de trabajo
manual con pendrive, exactamente el contexto en que una constante en un
archivo se olvida.

Por eso hay además una defensa **estructural**, que no depende de nadie.
Dos filas selladas independientemente en dos máquinas **jamás comparten
`creado_en` ni `timestamp_utc`**: son marcas de tiempo con precisión de
microsegundos, tomadas por procesos distintos en momentos distintos. Que
coincidan al microsegundo no es una coincidencia asombrosa — es la MISMA
fila copiada. Si la fila local y la de `origin/main` coinciden en
`creado_en`, `timestamp_utc` **y** `plataforma_version`, el comparador se
niega, **aunque la fecha sea posterior al corte**, y el motivo apunta a
subir `FECHA_CORTE`.

**Por qué los tres campos y no solo los timestamps.** Los dos timestamps
solos ya bastarían: la probabilidad de colisión al microsegundo entre dos
procesos independientes es despreciable. Se exigen los tres para que la
negativa sea **inapelable** cuando se dispara — durante la ventana real el
Mac sella 5.0.2 y el PC 5.0.3, así que la tercera condición por sí sola ya
hace imposible el falso positivo. El precio de pedir de más aquí es cero;
el de un falso positivo sería negarse a comparar un día legítimo.

**Cinturón y tirantes:** los dos mecanismos son independientes y basta que
se dispare **uno**. La fecha de corte atrapa el caso conocido; la huella
atrapa el caso que nadie anticipó — incluida la copia hecha por una razón
distinta a la prevista. Hay test para cada uno por separado, y uno que
verifica que la huella NO se dispara cuando solo coinciden los timestamps
pero la plataforma difiere.

## 19. Un cuarto veredicto: `PENDIENTE_PUBLICACION`

El comparador lee del titular a través de `origin/main`, y **el push del
Mac es manual y va después de las 20:30**. Por eso la ausencia de fila ahí
es **ambigua**: o el titular no selló, o selló y todavía no publicó. Con
tres veredictos, esa ambigüedad se resolvía en el peor sentido posible —
el día caía en `DIA_NO_COMPUTABLE` y **se quemaba en silencio** por un push
que aún no había llegado. En una ventana de tres días, perder uno así es
perder un tercio de la evidencia por un artefacto de sincronización.

`PENDIENTE_PUBLICACION` es el estado honesto para eso: **no suma a la
racha, no la rompe, y NO ES FINAL**. Se resuelve re-ejecutando el
comparador para esa fecha cuando llegue el push. Ahí está la diferencia
con `DIA_NO_COMPUTABLE`, que es un veredicto **cerrado**: ese día ya no
puede dar otra cosa.

**Cómo se desambigua sin mirar el reloj.** Un veredicto que dependiera de
la hora sería frágil (zonas horarias, corridas tardías, re-ejecuciones al
día siguiente). En vez de eso se usa la evidencia que ya está en los
datos: **si el titular ya publicó algún sello de una fecha POSTERIOR, su
historia está publicada más allá de este día**, y entonces la ausencia
deja de ser ambigua — es definitiva, y el veredicto pasa a
`DIA_NO_COMPUTABLE`. Sin esto, un feriado quedaría marcado "pendiente"
para siempre.

El contador lista los días sin cerrar aparte, con el comando exacto para
re-ejecutarlos, y usa **la última corrida de cada fecha**: un pendiente
que se resuelve queda sobrescrito por su veredicto definitivo.

## 20. GATE 1 tras la Fase 3

`python -m pytest tests/ -q` → **107 en verde** (70 previos + 37 de
`tests/test_sombra.py`), y `python tests/test_motor.py` → anti-look-ahead
limpio en las tres fechas.


---

# Etapa 5.0.3 (continuación) — Fase 4: timers instalados y GATE A-bis

## 21. GATE A-bis APROBADO (25-ago-2026) — el pendiente de agosto, cerrado

El acta de migración dejó abierta la variante estricta del arranque en
frío: en agosto la prueba se hizo **iniciando sesión después del boot**, lo
que no distingue "el sistema arranca solo" de "el sistema arranca cuando
alguien entra". Con sesión iniciada, un keep-alive que en realidad
dependiera del login pasaría la prueba igual. La hipótesis quedó sin
verificar y así estaba escrita.

**Procedimiento de la prueba estricta:** reiniciar, **no iniciar sesión**,
esperar en la pantalla de bloqueo, y recién entonces entrar a mirar. Lo
que ocurra antes de ese login es lo único que prueba algo.

**Evidencia recogida (toda comprobable en la máquina):**

| Hecho | Evidencia |
|---|---|
| La VM arrancó sin login | `uptime -s` = `2026-08-25 20:14:12` |
| El keep-alive nació con la VM | `sleep infinity` con **PID 396**, `STARTED Tue Aug 25 20:14:25` — 13 s después del boot y PID de tres cifras |
| systemd es PID 1 | `ps -p 1 -o comm=` → `systemd` |
| Los 6 timers vivos | `systemctl --user list-timers 'mki-*'` → `6 timers listed` |
| Nadie logueado al disparar | `who` vacío |
| El timer disparó a su hora | `LastTriggerUSec` = `Tue 2026-08-25 20:30:00 -04` |

**El disparo de las 20:30, al milisegundo.** Conviene registrar la cadena
entera y no un solo número, porque son dos latencias distintas y la
próxima vez habrá que compararlas por separado:

```
20:30:00.156819  systemd: Starting mki-vigia-rechequeo.service   (+157 ms)
20:30:00.244073  primera línea de data/vigia.log del proceso     (+244 ms)
20:30:00.250213  systemd: Finished                               (+250 ms)
```

Los **157 ms** son la latencia de systemd, holgadamente dentro del
`AccuracySec=1s` declarado en la unit. Los **87 ms** siguientes son el
arranque del intérprete hasta su primera escritura al log. El total de
**244 ms** hasta que el job deja rastro propio es el número que el acta
recoge, y es la cifra correcta para "cuánto tarda el sistema en empezar a
trabajar" — pero no es el retraso de systemd, que es la mitad.

**Con esto el arranque en frío deja de ser hipótesis y pasa a ser hecho
medido.** El pendiente queda cerrado.

**Nota de coherencia con el modo sombra:** los timers corren con
`MKI_MODO=sombra` (línea 18 de `.env`), pese a que las units **no**
declaran `Environment=MKI_MODO`. Funciona porque `modo.py` llama
`load_dotenv()` al importarse — que es exactamente la razón por la que se
puso ahí (§13). Se decidió **no** duplicar la variable en las units:
tenerla en dos sitios reintroduce la posibilidad de que discrepen, y el
modo debe vivir en un solo lugar.

## 22. Dos hallazgos del blindaje, ambos de la familia "el indicador miente"

Los dos son de la misma clase que el `HiberbootEnabled` del acta: un
número que se lee como falla cuando el sistema está sano, o un blindaje
que se da por hecho cuando no está.

### `Last Result: 0x800710E0` NO es una falla

Con `MultipleInstances=IgnoreNew` en la tarea `MKI-WSL-KeepAlive`, el
estado de régimen no es el `267009` (`0x41301`, `SCHED_S_TASK_RUNNING`)
que documenta el acta, sino **`0x800710E0`** (`-2147020576`, Win32
**4320**): la repetición de 15 minutos intenta arrancar, encuentra la
instancia anterior viva y **se niega a lanzar otra**. Es precisamente lo
que `IgnoreNew` significa, y por tanto es **estado SANO**.

Se documenta porque el modo de fallo es humano y previsible: quien abra
`schtasks /query /v` y vea un código de error hexadecimal negativo va a
concluir que el keep-alive está roto, y va a "arreglar" algo que funciona.
**El campo que hay que mirar no es `Last Result` sino `Status: Running`.**

### `powercfg /h off` no basta: faltaba el standby

El acta daba el blindaje de energía por resuelto con `powercfg /h off`
verificado por `powercfg /a`. **No alcanza.** Esa orden desactiva la
hibernación y el Fast Startup, pero **S3 (standby) seguía disponible**: el
PC podía dormirse por inactividad a las 18:10 —en plena ventana de jobs—
y reproducir exactamente el patrón de DarkWake que en el Mac dejó los
sellos de las 21:23 y 19:40 en julio.

Se fijó `standby-timeout-ac 0`. Sin eso, todo el resto del blindaje es
irrelevante: no importa que la VM sobreviva al arranque si la máquina se
duerme sola cuarenta minutos antes del snapshot.

La lección que queda escrita: **hibernación y standby son dos blindajes
distintos y desactivar uno no desactiva el otro.** `powercfg /a` sigue
siendo el indicador autoritativo, pero hay que leerlo entero, no solo la
línea de hibernación.


---

# Etapa 6.0.0 — GEMELO: el pre-registro se congela antes del primer resultado

## 23. Por qué la 6.0.0 abre con un documento y no con código

`GEMELO/DISEÑO.md` es un **pre-registro**, y se commitea **antes** de
construir nada. Su valor entero depende de eso: unos criterios de victoria
publicados después de ver resultados no son criterios, son una descripción
de lo que pasó. El commit fechado es la prueba de anterioridad.

Es la misma tradición que `backtest/DISEÑO.md` en el GATE B —diseño
congelado, ejecución después— pero llevada un paso más lejos: allá se
congeló el procedimiento, acá se congelan además **las barras numéricas
que el retador tiene que superar** (§6.1 V1–V7 y §6.2 R1–R3).

**El documento no se edita para que cuadre.** Si el harness contradice
alguna cifra de su §2, manda el harness y la corrección se documenta como
tal, con fecha posterior y a la vista — jamás reescribiendo el
pre-registro. La §2 misma lo dice y la §9 lo ordena: reproducir esas
cifras dentro de `backtest/` es lo único autorizado a empezar.

**Lo que este documento hace con el campeón, y conviene no perder de
vista:** mide el 65.8% de acierto de gap contra una baseline de "siempre
al alza" que en la misma ventana marca 60.5%, y concluye que la ventaja de
+5.3 pp no es distinguible de cero (McNemar p = 0.32). Es el proyecto
midiendo su propio número publicado contra el denominador honesto y
publicando que no sale bien parado. La regla cero sigue intacta:
`motor.py` no se toca y el 4.6.0 sigue sellando durante toda la etapa
(§7).

## 24. Atribución: `vcalderone/equity-direction-research` (MIT)

La maquinaria de inferencia de la **§5** del pre-registro se incorpora de
**`vcalderone/equity-direction-research` v2.1.0**, bajo licencia **MIT**.
Ninguna de esas piezas existía en MKI antes de esta etapa.

Piezas tomadas: Deflated Sharpe Ratio, holdout libre de sesgo de
selección, PSR con error estándar del Sharpe, bootstrap de bloques,
embargo en el walk-forward, importancia por permutación y vol targeting.
De la misma fuente vienen tres elementos de la especificación: la
estructura temporal del VIX (`VIX3M/VIX`) y el spread de crédito
`ln(HYG/LQD)` como regresores prospectivos (§4.1), y el **control lineal
obligatorio** con sus tres afirmaciones falsables (§4.3).

**Obligación que queda escrita:** la licencia MIT exige conservar el aviso
de copyright. Cada archivo derivado de esa fuente lleva la atribución en
su encabezado, además de este registro. Un archivo derivado sin
encabezado es un incumplimiento de licencia, no un descuido de estilo.


## 25. La §2 reproducida: 21 de 21, y dos hallazgos que corrigen la línea base

`backtest/linea_base.py` recalcula la §2 del pre-registro desde
`senales.db` en `mode=ro` — la autoridad, no los CSV de respaldo. Es lo
único que la §9 autorizaba a empezar, y se hizo antes de escribir una
línea del retador.

**Reproducen 21 de 21 cifras titulares** bajo la convención con que se
escribieron: n, aciertos, McNemar, los tres MAE, cobertura, ratio de
ancho, R², zona muerta, régimen, β, y los cuatro cortes por bolsa dígito a
dígito. De paso quedó identificada la variante exacta del test: el
documento usó **chi-cuadrado con corrección de continuidad** (67 vs 55 →
0.3193; sin corrección habría dado 0.2773).

**Sin `scipy`.** Añadirlo habría roto la invariante de dependencias
idénticas entre el Mac y el PC (§1). χ² con 1 gl tiene forma cerrada:
`sf(x) = erfc(sqrt(x/2))`, y `math.erfc` es stdlib.

### 25.1 El campeón se medía con una regla y la baseline con otra

Hay 5 filas con `gap_pct == 0.00` exacto: apertura idéntica al cierre
previo, la firma del **ffill de feriados** (Supuesto #1). Cuatro de las
cinco son 2330.TW.

El verificador puntúa al campeón con `>=` (`senales.py:373`), así que en
esas filas le da el acierto. La baseline de la §2.1 usaba `>` estricto y
no se lo daba. **Los dos lados se puntuaban con reglas distintas, y la
diferencia favorecía al campeón.** No es un error de cálculo —las cifras
reproducen exactas— sino un sesgo de medición, que es peor: reproduce
perfectamente y aun así engaña.

| Convención | n | Ventaja | p |
|---|---|---|---|
| `estricta` (la original) | 228 | +5.3 pp | 0.3193 |
| `verificador` (simétrica) | 228 | +3.1 pp | 0.5854 |
| **`excluir_cero` (CONGELADA)** | **223** | **+4.0 pp** | **0.4633** |

**Se congeló `excluir_cero`** en `GEMELO/DISEÑO.md` §2.8. La razón no es
que una regla de empate sea mejor que la otra: es que **la apertura de un
feriado no informa sobre nada**. Excluir es la única salida que no obliga
a elegir a quién se le regala el empate.

**La exclusión vive en la capa de medición, y `senales.py` NO se toca.**
`acierto_gap` es un valor sellado; cambiar el scoring reescribiría el
significado de filas ya selladas. Un campeón cuyo histórico cambia de
valor cuando cambiamos de opinión sobre los empates no tiene track record.
Hay un test que fija que las filas de gap cero conservan su
`acierto_gap` original.

**La conclusión de fondo no se movió, se reforzó:** bajo las tres
convenciones la ventaja del campeón sobre una constante no es
distinguible de cero. Hay un test que lo exige en las tres — si alguna
diera p < 0.05, la corrección habría cambiado la conclusión y no solo la
cifra.

### 25.2 Un índice de bloque no puede sostener un criterio

Los límites de la tabla de la §2.2 reproducen exactos (seis fechas, seis
n) y los totales reconcilian (150 y 138 en ambas particiones). El
**reparto interno no reproduce**: se probaron cuatro órdenes de fila —por
`id`, por `(fecha, ticker)` y el `merge` de los dos CSV en ambas
direcciones— y ninguno da los bloques 0, 1, 4 y 5. Es la misma partición
cortada distinto: en las fechas que caen sobre una frontera, el orden
interno decide de qué lado quedan.

Por eso **R2 quedó operacionalizado por RANGO DE FECHAS** (15–23 jul), que
es estable, y no por índice de bloque.

### 25.3 R2 descalifica al campeón, y se mantiene igual

Aplicada al titular, esa misma prueba lo deja en **n = 184 · 62.0% contra
una base de 65.2% · ventaja −3.3 pp (p = 0.60)**: no pierde su ventaja, la
vuelve **negativa**.

**R2 se mantiene tal cual, deliberadamente.** Que el titular no pase una
valla es un resultado **sobre el titular**, no un defecto del criterio.
Bajarla para que el campeón entre sería exactamente lo que un pre-registro
existe para impedir: mover la barra hasta donde ya está el que queremos
aprobar.

Lo mismo con **V1**: se actualizó la vara **descriptiva** (+4.0 pp,
p = 0.4633, n = 223) y se dejó **escrito explícitamente que el criterio no
se movió** — sigue siendo McNemar p < 0.05. La tentación al corregir una
línea base es ajustar de paso la barra que esa línea no alcanza; queda
anotado que aquí no se hizo.

### 25.4 La corrección va en commit aparte, nunca en un amend

El pre-registro se commiteó en `e2e49f2` y la corrección va **después**,
en su propio commit. La historia tiene que mostrar la secuencia —
pre-registro primero, medición después— porque un amend borraría
justamente la prueba de anterioridad que le da valor al documento. La §2.8
lleva su fecha (26-ago) y dice de sí misma que es posterior; el encabezado
del documento también lo avisa.
