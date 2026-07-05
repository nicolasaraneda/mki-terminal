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

