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


## 26. WS1 — la maquinaria de juzgar va ANTES que lo juzgado

`backtest/inferencia.py` implementa la §5 del pre-registro: PSR, DSR,
error estándar del Sharpe y bootstrap circular de bloques. Verificado por
grep que nada de eso existía en el repo.

**Por qué primero.** Si el retador se construyera antes que los
instrumentos para juzgarlo, su primer resultado se evaluaría con las
herramientas que ya sabemos que no alcanzan — y esa primera lectura
contamina todo lo que viene después: fija una expectativa, y a partir de
ahí cada instrumento nuevo se compara contra ella en vez de contra la
teoría. Construir el juez antes que el acusado no es orden estético, es lo
que impide que el primer número mande.

**Sin `scipy`.** La normal sale de `math.erfc` y su inversa de una
bisección de 400 iteraciones. Se prefirió la bisección a una aproximación
racional a propósito: no tiene coeficientes mágicos y se audita contra
valores tabulados. En el módulo que decide si un modelo gana, poder
verificar a mano importa más que la velocidad. Los 14 valores de
referencia del encargo reproducen **exactos a 10 decimales**.

### 26.1 `N_intentos` sin valor por defecto

`sr0_deflacionado(N_intentos, V_intentos)` y `dsr(...)` **no tienen
default para N**, y hay un test que falla si alguien se lo pone. Un DSR
calculado con un N que alguien olvidó actualizar **miente, y miente hacia
arriba**: declara habilidad donde solo hubo búsqueda. Obligar a escribir
el número en cada llamada es la única defensa barata contra ese olvido, y
es coherente con V5 del diseño, que exige contar **todos** los intentos —
las seis baselines B0→B5 más cada configuración del retador evaluada.

Con `N < 2` no hay selección que deflactar: `SR0 = 0` por definición y el
DSR se reduce al PSR contra cero. Está documentado y testeado.

### 26.2 El bootstrap: circular, con semilla obligatoria

Se implementó **circular** (Politis & Romano). El `bootstrap_sharpe` que
ya existía en `metricas.py` **no lo es**: sus bloques arrancan en
`[0, n - bloque)`, así que las últimas `bloque-1` observaciones no pueden
iniciar ninguno y la cola queda submuestreada. Además su semilla es una
constante de módulo, su IC está fijo al 90% y redondea a 2 decimales.

El nuevo es de propósito general: semilla **obligatoria** como argumento
—nada de estado global de `numpy`—, `alpha` configurable, y `bloque=1`
degenera exactamente en el bootstrap iid, lo que hace trivial comparar uno
contra otro. **No se tocó `metricas.bootstrap_sharpe`**: está fuera del
alcance de este WS y cambiarlo movería números de corridas ya escritas.
Queda anotado como candidato a migrar.

**El test que de verdad prueba el bootstrap** no es un valor de
referencia: es que sobre un AR(1) con φ alto el IC de bloques salga
**estrictamente más ancho** que el iid sobre la misma serie. Si no sale
más ancho, el bloque no está haciendo nada. Medido: φ=0.8 da un IC 2.6×
más ancho; sobre una serie iid el IC de bloques queda a 1.00× del
analítico.

### 26.3 Hallazgo: `Phi` satura, y un DSR de 1.000 no es certeza

Tres tests de propiedad fallaron al escribirlos, todos por la misma causa:
**por encima de z ≈ 8.3, `Phi` devuelve 1.0 EXACTO en doble precisión**,
así que la monotonía estricta se pierde en esa zona. No es un defecto de
la implementación sino un límite del punto flotante, pero tiene una
consecuencia de lectura que conviene tener escrita: **un PSR o un DSR que
salga 1.000 significa "más allá de lo que el doble distingue", no
"certeza"**. Los tests se reescribieron para probar la monotonía en la
zona informativa —que es donde caen los casos reales con n=228— y se
añadió uno que **documenta la saturación como comportamiento esperado**,
para que nadie la "arregle" más adelante creyendo que es un bug.

## 27. El embargo: la guarda de look-ahead no bastaba

`backtest/` ya impedía el look-ahead duro (`validar_sin_futuro` revienta
si entra una fila posterior a la emisión). Pero **la frontera entre
entrenamiento y prueba seguía contaminada**, que es un problema distinto y
más sutil: las features son rodantes (medias, momentum, residuales a
20/50/200 sesiones), así que la etiqueta del día anterior a la emisión se
construyó con una ventana que se solapa casi entera con la ventana de las
features con que se predice hoy. El modelo entrena sobre información que
es, en la práctica, la misma que va a usar para predecir, y su error sale
optimista **sin que ninguna guarda se queje** — es exactamente el caso del
capítulo 7 de López de Prado.

`EMBARGO_DIAS = 5` purga las últimas jornadas antes de cada emisión. Se
paga en datos y se cobra en honestidad. Configurable por
`ContextoRun(..., embargo_dias=)`, por `motorbt.correr(...)` y por
`--embargo-dias` en la CLI; `0` lo desactiva.

**Por qué 5:** cubren una semana hábil completa, que es el ciclo de
reajuste (`DIAS_REAJUSTE = 7` corridos) y el horizonte de las features más
cortas. Es una **elección nueva**, no un valor recuperado — misma familia
que los `TimeoutStartSec` de systemd. A revisar contra las primeras
corridas reales.

**Por qué ahora y no después:** ninguna corrida con veredicto se ha
ejecutado todavía, así que cambiarlo hoy no invalida ningún resultado
publicado. Después del primer veredicto, tocar esto sería cambiar las
reglas a mitad del experimento — y entonces habría que tratarlo como un
cambio de modelo, con su propia versión.

**Los parámetros de la corrida ahora van SELLADOS en el reporte**
(`parametros`: embargo, ventana de entrenamiento y días de reajuste), y
aparecen en la cabecera de `resumen.md`. Una corrida cuyo embargo no queda
escrito no es reproducible, y el embargo cambia los resultados.

**No se ejecutó ningún backtest con veredicto.** El gatillo de la 5.1
sigue sin cumplirse (N=228 sí, cambio de régimen no) y es decisión humana.
Construir la maquinaria no es ejecutarla.


## 28. Migración del bootstrap: de bloques no circulares a circulares

`metricas.bootstrap_sharpe` tenía su propio remuestreo y **no era
circular**: los inicios de bloque salían de `[0, n - bloque)`, así que las
últimas `bloque-1` observaciones **no podían iniciar ningún bloque** y
quedaban submuestreadas.

**Por qué ese defecto es el que importa.** En una serie financiera la cola
es **lo más reciente**: el tramo que más pesa al juzgar si una estrategia
sirve hoy. Un intervalo que la subrepresenta describe mejor el pasado
lejano que el presente, que es justo al revés de lo que hace falta.

Medido con una serie construida para aislarlo —200 observaciones en cero
salvo las 5 últimas, media real 0.25—: el bootstrap **circular** recupera
0.246; el **no circular**, 0.0535. Pierde el 79% de la señal de la cola.
Ese contraste quedó como test.

Los otros dos defectos eran menores pero reales: semilla en una constante
de módulo que ningún reporte declaraba, y nivel del IC fijo al 90% dentro
de la función.

### 28.1 Por qué AHORA es el momento correcto

**Ninguna corrida con veredicto se ha ejecutado.** No hay conclusión
publicada que dependa del método viejo. Después del primer veredicto,
cambiar el estimador del intervalo sería cambiar la regla de medición a
mitad del experimento — y entonces habría que tratarlo como una versión
nueva, no como un arreglo.

### 28.2 Qué NO cambió: los parámetros congelados

`backtest/DISEÑO.md` §8.5 congela **bloques de 10 días y 2.000 réplicas**.
**Se conservan.** La migración cambió el **método**, no la
parametrización: mezclar las dos cosas habría hecho imposible atribuir
cualquier diferencia futura a una u otra.

Nota de coherencia entre ámbitos: `inferencia.bootstrap_bloques` usa
`bloque=20` por defecto porque es lo que especifica `GEMELO/DISEÑO.md` §5
para la maquinaria del retador; `metricas.bootstrap_sharpe` le pasa 10,
que es lo congelado para el backtest B0→B5. Son dos ámbitos distintos con
dos diseños congelados distintos, y cada uno respeta el suyo.

### 28.3 Semilla y alpha: parámetros sellados, no constantes escondidas

`SEMILLA_BOOTSTRAP` desapareció de `metricas.py`. Ahora `semilla` es
**argumento obligatorio** —sin default, igual que en `inferencia`— y
`alpha` es configurable. Ambos se sellan en `parametros.bootstrap` del
reporte junto al método, el largo de bloque y las réplicas, y aparecen en
la cabecera de `resumen.md`.

El `DISEÑO.md` §9 pide determinismo: "mismo commit + mismos datos → mismos
resultados". Eso se consigue **pasando la semilla y declarándola**, no
escondiéndola donde ningún resultado la menciona. Un número irreproducible
y un número reproducible cuya semilla nadie sabe son igual de inútiles
para auditar.

El campo `sharpe_ic90` pasó a llamarse `sharpe_ic`: con el nivel
configurable, un nombre que fija el 90% mentiría en cuanto alguien pase
otro alpha. La cabecera del resumen calcula la etiqueta desde el alpha
real.

### 28.4 El redondeo se fue a presentación

`bootstrap_sharpe` ya no redondea: devuelve el intervalo completo, que es
lo que se guarda en `metricas.json`. El recorte a 2 decimales vive en
`motorbt._ic()`, que es la capa que arma la tabla. Una métrica redondeada
en origen pierde precisión para siempre; una redondeada al imprimir, no.

### 28.5 Qué corridas quedaron con el método viejo

**Una sola: `backtest/resultados/20260726-032635-humo-legacy/`.** Es la
única corrida que existe en el repo, y ya estaba marcada **NO-CONCLUYENTE
desde su origen** — era humo para probar que la maquinaria arranca, no un
veredicto.

**Su `resumen.md` NO se recalculó ni se reescribió.** Se le añadió una
**nota al pie** que declara que sus `[IC90]` salieron del bootstrap no
circular, que sus intervalos no son directamente comparables con los de
corridas posteriores, y que además es anterior al embargo y a los
parámetros sellados. Errata documentada, no corrección retroactiva: es la
misma regla que rige las filas selladas de `senales.db`, aplicada a un
artefacto de backtest. El diff sobre ese archivo es de **34 inserciones y
cero borrados**, y hay un test que verifica que sus cifras originales
siguen ahí.


## 29. WS2a — la capa de datos del retador, aislada del sello

`GEMELO/datos.py` y `GEMELO/features.py` construyen el conjunto de
información de la §4.1 del pre-registro: quince series en seis bloques
—contagio, overnight US, divisa, mercado local, volatilidad, crédito— y
dieciséis features causales y estacionarias. **No hay modelo**: eso es
WS2b.

### 29.1 Aislamiento: se duplica la descarga a propósito

`GEMELO/` **no importa** `snapshot.py`, `senales.py`, `alertas.py`,
`noticias.py` ni `motor.py`, y no escribe en ninguna base. Hay tres tests
que lo verifican recorriendo el AST de cada archivo del paquete.

**Trece feeds nuevos son trece formas nuevas de que Yahoo falle a las
18:15**, y el sello nocturno del campeón no puede depender de ninguna. Eso
obligó a **duplicar** la lógica de descarga de `motor._datos_crudos` en
vez de reutilizarla. Es duplicación deliberada: el acoplamiento cuesta más
que la copia cuando lo que está en juego es que el titular selle.

### 29.2 La asincronía de las barras diarias, sellada como dato

Dos barras de yfinance con la misma etiqueta de fecha pueden estar
separadas por **catorce horas**: ^KS11 del día D cerró a las 06:30 UTC y
^SOX del día D a las 21:00 UTC, bajo el mismo rótulo. Es la vía por la que
entra look-ahead sin que ninguna guarda se queje — la misma familia del
problema que cerró el embargo (§27).

Cada serie lleva su hora de cierre y su `available_at` **calculado**, no
asumido, y `verificar_conocibles()` es la guarda dura. La tabla vive como
**dato** (`tabla_disponibilidad()`) y no solo como comentario, que es lo
que permite testearla.

**Se sella el peor caso, no el habitual.** El UTC de cada cierre usa el
offset más tardío del año — horario de invierno para ET (EST, UTC-5) y CET
(UTC+1) — para que la afirmación "conocible a las 22:15" valga los 365
días y no solo en verano. KST, TWT y JST no tienen horario de verano.

**Los futuros son la serie más ajustada del conjunto:** ES=F y NQ=F
cierran 17:00 ET, que en invierno son las 22:00 UTC — **quince minutos**
antes de la emisión. Es holgura real pero mínima. No se retrocedió a la
barra D-1 porque eso vaciaría de sentido justo el bloque que más aporta:
los futuros valen precisamente por moverse entre el cierre del SOX y la
apertura asiática, que es la información que hoy se tira. Queda declarado
como el punto frágil a vigilar en las primeras corridas reales.

### 29.3 Hallazgo: el margen de 2 h es criterio de verificación, no de insumo

Al escribir la guarda apareció una tensión con `calendarios.sesion_ya_cerro`,
que exige **2 h** de margen de publicación. Con ese criterio aplicado a los
insumos caerían **11 de las 15 series, incluido ^SOX** — que es el insumo
primario que el campeón usa hoy a las 22:15.

La lectura correcta es que **son dos criterios distintos para dos
preguntas distintas**: las 2 h responden "¿ya se puede saber cómo cerró la
sesión objetivo?" (verificación de un resultado), mientras que el insumo
solo necesita que su barra haya cerrado — y así lo sella producción, con
`available_at` = cierre UTC de la sesión de SOX usada, sin sumarle margen.
Aplicar el criterio de verificación a los insumos descalificaría al propio
campeón.

`MARGEN_PUBLICACION_H = 0.0` deja el parámetro a la vista y un test declara
exactamente qué series caen con cada margen: la tensión queda **medida**,
no como nota al pie.

### 29.4 Las dos compuertas de robustez

- **ffill acotado a 5 días.** Un ffill sin tope alimenta para siempre el
  último valor de una serie muerta y el modelo nunca se entera: la feature
  sigue existiendo, constante, aparentando dato.
- **Cobertura mínima del 80%, con aviso.** ^VIX3M arranca ~2017; sin esta
  compuerta un `dropna()` posterior alinearía por la serie más corta y
  **borraría años de todas las demás en silencio**. Se descarta la serie
  corta nombrándola, no el histórico de las buenas.

Ambas se incorporan de `vcalderone/equity-direction-research` (MIT, §24),
junto con la caché en disco con TTL — sin la cual cada iteración de
investigación vuelve a bajar años de historia y Yahoo acaba limitando.

### 29.5 El GATE: causalidad feature por feature

El test de propiedad de `tests/test_motor.py` se extendió a **cada feature
nueva**: el valor en t debe ser invariante a borrar todo dato posterior a
t. Se prueba en las mismas tres fechas que el motor, y además en su forma
fuerte —truncar no puede alterar **ningún** valor anterior, no solo el del
corte—.

**Y hay una contraprueba del propio test**: se inyecta una feature con
`shift(-1)` y se verifica que el criterio la detecta. Un test de fuga que
no puede fallar no prueba nada.

`construir(series)` es una **función pura** de la matriz de series a la
matriz de features. Ese diseño es lo que permite al test truncar la
entrada sin parchear nada — el equivalente al punto único
`motor._datos_crudos` que hace testeable al campeón.

Se añadió además un test de **estacionariedad operativa**: ninguna feature
puede correlacionar más de 0.85 con el índice temporal. Un nivel deriva
monótonamente y el modelo lo usa como proxy del calendario — aprende "más
adelante en el tiempo" en vez de "más riesgo", y eso no generaliza.

### 29.6 `credit_ratio` es la feature menos estacionaria, y está anotada

`credit_ratio = ln(HYG/LQD)` se implementa **como lo especifica la §4.1**,
pero es una razón de dos NIVELES y puede derivar — es la única exceptuada
del test de correlación con el calendario. Queda anotada como candidata a
pasar a forma de distancia (separación de su mediana móvil) si el control
lineal de WS2b la muestra derivando. **No se cambió por cuenta propia**:
la especificación está congelada y corregirla exige medirla primero.

### 29.7 El conteo de intentos, declarado antes de correr

Se añadió la §4.2 bis al pre-registro: **cada configuración evaluada en
WS2b cuenta como un intento para el DSR**, el número se declara **antes**
de correr ninguna, y los intentos se **suman** a las seis baselines B0→B5
ya evaluadas sobre los mismos folds. Un DSR con el N mal contado miente
hacia arriba, que es el sesgo exacto que el instrumento existe para
corregir: subestimar N no lo degrada, lo inutiliza.


## 30. WS2b — el control lineal: resultado NEGATIVO, publicado tal cual

Las tres configuraciones se declararon **antes** de correr ninguna, con su
N para el DSR: **N = 9** (3 configuraciones + las 6 baselines B0→B5 ya
evaluadas sobre los mismos folds), según el §4.2 bis.

- **C1** — ridge agrupada, SOLO el SOX (t y t−1): el **control de
  información**.
- **C2** — ridge agrupada, catálogo completo (16 features).
- **C3** — ridge por ticker, catálogo completo.

### 30.1 Por qué C1 no era opcional

Correr solo C2 y verlo ganar al campeón no habría respondido nada: podría
ser la información nueva, o podría ser que ridge con walk-forward expansivo
y embargo sea mejor **maquinaria** que una OLS rodante de 120 sesiones. Son
dos explicaciones distintas y la diferencia lo es todo — una dice que la
tesis tiene dónde crecer, la otra que el campeón está mal implementado.

C1 usa el mismo insumo que el campeón con la maquinaria nueva, así que
**la comparación que responde la pregunta real es C2 contra C1**.

### 30.2 El hallazgo que hizo el control: el campeón ES el signo del SOX

**C1 y el campeón aciertan la dirección en las MISMAS filas de las 215
comparables: McNemar `0 vs 0`.** Cero
desacuerdos.

No es un error: la predicción del campeón es βᵢ·SOX con βᵢ>0, así que su
signo **es** el signo del retorno del SOX; y una ridge agrupada sobre el
mismo insumo lo reproduce exactamente. Lo que el campeón aporta sobre "el
SOX subió, todo abrirá al alza" no está en la dirección.

Consecuencia metodológica: **cualquier diferencia direccional entre C2/C3 y
el campeón es INFORMACIÓN, no maquinaria**. Es exactamente lo que C1
existía para separar, y lo separó.

### 30.3 El resultado: la información expandida no aporta

| Comparación | Ventaja dir. | McNemar p | ΔMAE | IC del ΔMAE |
|---|---|---|---|---|
| C2 vs C1 | 2.8 pp | 0.3613 | 0.1559 | [-0.0389, 0.4232] |
| C3 vs C1 | 5.1 pp | 0.1273 | 0.2702 | [0.0665, 0.4729] |
| C3 vs C2 | 2.3 pp | 0.3588 | 0.1143 | [0.0564, 0.3071] |

**C2 vs C1 no da nada**: el IC del ΔMAE incluye el cero y la dirección no
es significativa. Con el mismo motor y la misma ventana, **añadir las
catorce features nuevas a las dos del SOX no produce una mejora
detectable**.

Lo único que mueve la aguja es la **estructura por ticker** (C3), y **solo
en magnitud**: su IC del ΔMAE contra C1 excluye el cero, pero la dirección
no es significativa. Coincide con la §2.5 — la contribución medible está
en la magnitud, no en el signo.

### 30.4 El único p<0.05 no sobrevive a R2

C3 contra la baseline sobre la ventana completa marca
**11.2 pp con p=0.0298** — por
debajo del 0.05 de V1. Aplicando R2 (excluir 15–23 jul) cae a
**1.8 pp con p=0.8321**.

**La significancia venía de la misma ventana afortunada que sostiene la del
campeón**, que es literalmente lo que R2 fue escrito para detectar. Bajo
R2 pierden su ventaja C1, C2 y el propio CAMPEÓN; C3 sobrevive con
+1.8 pp y p=0.8321, que no es
superar una valla sino rozarla sin evidencia.

**Nadie supera V1 con R2 aplicado.** El resultado es NEGATIVO.

### 30.5 Hallazgo: el DSR no aplica a 30 días, y decirlo importa

Las tres configuraciones y el campeón dieron Sharpe anualizados en torno a
**5.5** sobre **30 días** de retornos. Ese número no es una estimación: es
un artefacto de multiplicar por √252 una muestra diminuta. Y el PSR y el
DSR salieron **1.0000** — la saturación de Phi documentada en §26.3.

El riesgo de lectura es grave y concreto: **un DSR de 1.000 se leería como
que V5 (DSR ≥ 0.95) está superado**, cuando lo que significa es que el
instrumento no aplica a esta muestra. Por eso se añadió
`MINIMO_DIAS_SHARPE = 60` y por debajo de ese umbral el PSR y el DSR se
reportan como **NO INTERPRETABLE** en vez de emitir el número. Un
instrumento que se niega vale más que uno que emite una cifra que no
sostiene.

También queda declarado que **`V_intentos` está subestimada** —los Sharpe
de las seis baselines vienen de una corrida legacy no comparable (§28.5)—
y que por tanto el SR0 sale bajo y el DSR sería, de aplicar, una cota
optimista.

### 30.6 Lo que se declaró y no se supuso

- **La asimetría de ventana**, en el reporte y no en una suposición: el
  retador entrena sobre años con ventana expansiva y el campeón usa 120
  sesiones rodantes. Es parte de lo que se mide.
- **El CRPS usa una predictiva NORMAL**, declarado como primera pasada:
  ridge da punto más varianza residual, pero la §2.7 ya mostró colas más
  gruesas, así que es una cota optimista. La Student-t es Nivel 4 del
  retador, no de este control.
- **El proxy económico no tiene costos**: `sharpe_ls_sin_costos` es
  long-short equiponderado y NO es la prueba del benchmark obligatorio
  (V6, que exige SMH y 25 pb por lado).
- **La búsqueda de alpha no suma a N**: se resuelve por CV temporal dentro
  de cada ventana de entrenamiento sin tocar filas de evaluación. Lo que el
  DSR debe contar son las decisiones tomadas MIRANDO el resultado de
  evaluación, y ésta no lo es. Los alphas efectivamente elegidos van
  sellados en el reporte.
- **El reporte se sella como NO-veredicto de la 5.1** en su primera línea,
  con un test que lo verifica.

### 30.7 No se probó una cuarta variante

Las tres primeras no dieron positivo. **No se buscó la configuración que sí
diera**: esa tentación es exactamente el sesgo que el DSR mide, y habría
subido N a 10 con obligación de recalcular todo. El §6.3 del pre-registro
ya dice que un negativo no es un fracaso de la etapa sino la etapa
funcionando, y así se publica.

El aislamiento se refinó respecto del WS2a: `datos.py`, `features.py` y
`control_lineal.py` siguen sin importar nada de producción, mientras que
`experimento.py` —el runner— importa `backtest.linea_base` (solo lectura,
`mode=ro`) y `universo` (constantes puras). La dirección que protege el
sello es la contraria y ahora tiene su propio test: **nada del camino de
sellado importa GEMELO**.


## 31. El README se actualiza entero, no solo con el negativo del WS2b

Publicar el resultado negativo del retador mientras la portada seguía
diciendo **78.8% con n=80** habría sido **honestidad selectiva**: contar
el fracaso del experimento nuevo y callar que el número estrella del
titular estaba viejo y sin denominador. El cambio es más grande que WS2b
a propósito.

### 31.1 Qué se corrigió

- **El track record al día.** 78.8% con n=80 era cierto el 25-jul; hoy son
  **65.9% con n=223** bajo la convención congelada en la §2.8. La sección
  dice explícitamente que el número anterior era correcto en su momento y
  que bajó al crecer la muestra — no se borra el pasado, se fecha.
- **El denominador, al lado del número y no en una nota.** "Siempre al
  alza" saca **61.9%** sobre las mismas filas: ventaja **+4.0 pp con
  McNemar p = 0.4633**, no significativa. Va en la misma tabla, en negrita,
  antes que cualquier otra métrica.
- **Qué aporta el modelo y qué no.** La dirección la pone el SOX: C1 y el
  campeón aciertan en las mismas 215 filas, McNemar 0 vs 0. La regresión
  de betas aporta a la **magnitud**, no a la dirección.
- **El conjunto de información expandido no mejora nada detectable**
  (C2 vs C1, p = 0.3613, IC del ΔMAE incluye cero), y el único p<0.05 del
  experimento **no sobrevive a R2** (1.8 pp, p = 0.8321).
- **La magnitud sí aporta**: MAE 3.12 pp contra 3.50 de predecir cero.
- **El caveat de régimen se endureció.** Decía "casi entera de un solo
  régimen"; la medición dice que es **entera** —una sola etiqueta en 35
  snapshots— y que la etiqueta no detecta la variación que sí existe.

### 31.2 Convenciones sin mezclar

El encargo citaba el MAE de **3.064 vs 3.423**, que son cifras de n=228
(convención original), mientras el titular es n=223 (convención congelada
§2.8). Presentarlas juntas habría mezclado denominadores en la misma
tabla. Se resolvió publicando las de n=223 (**3.12 vs 3.50**) como
titulares y las de n=228 en una nota, señalando que la mejora relativa es
**−10.7% y −10.5%**: la conclusión es **robusta a cómo se traten los
empates**, y decirlo la refuerza en vez de diluirla.

### 31.3 Badges

`tests` 49 → **236**; `plataforma` 5.0.0 → **5.0.3**. Y uno nuevo, que es
el que más dice: **`ventaja sobre la base · +4.0 pp · p=0.46`**. Un badge
de acierto sin denominador es publicidad; éste es medición.

### 31.4 El tono: no es una retractación

Queda escrito en el propio README que esto **no es una disculpa sino el
instrumento funcionando**: un sistema que mide su ventaja contra el
denominador correcto y responde "todavía no distinguible de cero" dice más
sobre su calidad que cualquier tasa de acierto. Es el argumento del README
desde el WS7 —liderar con la integridad, no con los aciertos— y esta
versión lo cumple mejor que la anterior, que lideraba con un 78.8% sin
rival contra el cual leerlo.

Se enlazan [`GEMELO/DISEÑO.md`](GEMELO/DISEÑO.md) y
[`GEMELO/resultados/control_lineal.md`](GEMELO/resultados/control_lineal.md)
para que cualquiera audite, y se declara que toda la sección se reproduce
con `python -m backtest.linea_base`. Una afirmación de integridad que no se
puede recomputar es una afirmación de marketing.


## 32. WS3 — la ventana larga: la potencia cambia las respuestas

El WS2b concluyó que el conjunto de información expandido no aporta, pero
esa conclusión estaba **sub-potenciada**: +2.8 pp con p=0.36 sobre 215
filas no distingue "no hay señal" de "la señal no se ve". El cuello de
botella no era información: era muestra.

La ventana larga pasa de **215 a 14.711 filas de evaluación**
(2018-08-27 → 2026-08-25, 2.076 fechas de emisión).

### 32.1 El N se declaró antes, y subió de 9 a 13

Regla escrita en `GEMELO/DISEÑO.md` §4.2 bis **antes de correr nada**:
**cuenta como un intento cada par (configuración × ventana de evaluación)
con resultado reportable.**

Re-evaluar las mismas tres configuraciones sobre otra ventana no es
gratis: produce un segundo conjunto de resultados publicables entre los
cuales se puede elegir, y elegir entre resultados es lo que el DSR
deflacta. Una regla que contara "3 configuraciones" sin importar cuántas
ventanas se prueben permitiría buscar la ventana favorable sin coste — la
misma trampa por otra puerta.

6 (B0–B5) + 3 (WS2b) + 3 (WS3) + 1 (campeón sobre la ventana larga) =
**13**. No cuenta la baseline "siempre al alza" —es la hipótesis nula, no
un modelo ajustado— ni la búsqueda interna de alpha.

### 32.2 El campeón se reconstruye, no se imita

Se llama a `motor.prediccion_apertura_al` vía `B2Produccion`. Lo único que
cambia es la **profundidad de la serie que se le sirve**, inyectada por
`FuenteCongelada(series=..., ohlc=...)`, que es su punto de extensión
declarado. Como `betas_al` usa una ventana rodante de 120 sesiones, **el
cómputo en cada fecha es idéntico al que haría en vivo**; solo se amplía
el rango de fechas computables. `motor.py` no se toca.

### 32.3 Las tres respuestas

**1. La ventaja del campeón sobre la tasa base SÍ sobrevive.** Sobre
14.711 filas: 70.1% contra una base de 54.2%, **+15.9 pp con McNemar
p≈0**. En la ventana sellada eran +4.0 pp con p=0.4633.

La diferencia no es que el modelo cambie: es que la ventana sellada tenía
una **tasa base del 61.9%** (siete semanas de deriva alcista fuerte)
mientras que sobre ocho años la base cae al 54.2%. Con 223 filas y un
rival inflado por la deriva, el efecto real quedaba enterrado en el ruido.

**2. C2 vs C1 SE REVIERTE.** Con 12.628 filas: **+1.3 pp con p=0.0003**, y
el IC del ΔMAE excluye el cero. El efecto **encogió** respecto del +2.8 pp
del WS2b —el patrón clásico: una muestra chica sobreestima el tamaño del
efecto— pero ahora es detectable. **La información expandida sí aporta, y
aporta poco.**

Ambas cosas importan: el WS2b acertó al no declarar victoria, y se
equivocó al leer "no significativo" como "no hay nada".

**3. R2 con potencia: la ventaja está REPARTIDA, no concentrada.** Medida
como distribución sobre sub-ventanas de 200 filas, el campeón tiene
ventaja positiva en el **90.4%** de sus 73 sub-ventanas; quitando la mejor
pasa de 15.90 a 15.61 pp, y quitando el mejor decil, a 13.98. En la
ventana corta, excluir una semana la volvía negativa. **Con siete semanas,
R2 era casi una anécdota; con ocho años es una medición.**

### 32.4 La limitación, MEDIDA en vez de declarada

Yahoo reescribe la historia y sus precios ajustados se recalculan con
dividendos y splits posteriores, así que **una reconstrucción a años vista
NO es point-in-time**. En vez de dejarlo como prosa, se midió: sobre las
198 filas comunes con el track record sellado, la reconstrucción de hoy
**coincide en el 91.4%** (a menos de 0.01 pp) y **difiere en 17**, con un
máximo de **31.2 pp**.

Ése es el número que hay que tener delante al leer el resto: la ventana
larga da **potencia**; la ventana sellada da **validez**. Ninguna
reemplaza a la otra, y la evidencia fuera de muestra de verdad siguen
siendo las 223 filas selladas.

### 32.5 HALLAZGO NO BUSCADO: el 29-jul huele a sello corrupto

Las mayores discrepancias no están repartidas: **se concentran en
2026-07-29**, y ese día es uno de los de **sello tardío con descarga
parcial de Yahoo** que la auditoría de julio ya documentó (§ de la Etapa
5.0.1: sellos a las 21:23 tras el re-sleep del Mac).

Las ocho filas selladas de ese día tienen **|gap| medio de 13.68 pp contra
3.12 del resto** —4.4× la magnitud normal, en los ocho tickers a la vez— y
el modelo acertó 1 de 8. La reconstrucción de hoy da para ese día gaps
normales (−2.9%, +2.6%, −0.1%…). El patrón es el de un **cierre previo
rancio**: si la descarga trajo un `close` viejo, el gap calculado se
dispara en todos los tickers simultáneamente.

**No se toca nada.** Las filas selladas jamás se reescriben; si se
confirma, es una **errata documentada**, y la decisión de cómo tratarla en
las métricas es humana. Queda escrito aquí porque esas ocho filas están
dentro de las 223 que producen el 65.9% publicado, y porque el hallazgo
salió de una validación que existía para otra cosa.

### 32.6 El Sharpe de esta etapa es ficción económica, y se marca

Las cuatro configuraciones dieron Sharpe anualizados de **9 a 10.6**. No
es un hallazgo: `sharpe_ls_sin_costos` se construye sobre el **gap**, y el
gap es precisamente lo que **no se puede capturar** — es el salto entre el
cierre previo y la apertura, y nadie transa a ese precio. El propio
proyecto lo sabe: por eso su verificador mide el **doble objetivo**
(`gap_pct` = ¿existe la señal?, `retorno_real_pct` = ¿es capturable?).

Se reporta porque el PSR y el DSR necesitan una serie de retornos, y se
marca con un aviso propio para que nadie lo lea como rendimiento. La
prueba económica de verdad es V6 (SMH, 25 pb por lado) y no está hecha.

Consecuencia sobre el DSR: con 1.500–2.000 días **sí** es interpretable
(supera `MINIMO_DIAS_SHARPE`), pero saturó en 1.0000 por la razón de
§26.3. Un DSR de 1.000 construido sobre un Sharpe no capturable **no
demuestra nada sobre V5**.

### 32.7 La línea con la 5.1, defendida por código

El reporte se sella en su primera línea, y la distinción se escribe
completa: el veredicto de la 5.1 es el criterio **escalonado
capa-contra-capa sobre B0→B5**, con reglas propias del GATE B y ejecución
humana. Aquí **no se calcula el veredicto escalonado ni se emite juicio
sobre B0→B5**; el campeón reconstruido aparece solo como término de
comparación. Hay tests que verifican que el módulo no importa
`backtest.motorbt` ni `backtest.cartera` y que no invoca
`veredicto_escalonado`.

### 32.8 No se modeló nada nuevo

Las tres configuraciones son las del WS2b sin un solo cambio, y hay un
test que falla si el módulo del WS3 redefine o extiende `CONFIGURACIONES`.
No se añadió una cuarta.


## 33. WS4 — auditoría adversarial del WS3: el +15.9 pp sobrevive, con dos correcciones

Trabajo hecho con la postura invertida: **no verificar que el cálculo
estuviera bien, sino buscar por qué podría estar inflado.** Informe completo
en `GEMELO/resultados/auditoria_ws3.md`. **No se modificó ninguna conclusión
previa ni ninguna fila; esta sección se añade, no reescribe.**

**Veredicto: sobrevive.** +15.90 → **+15.66 pp** bajo la convención
congelada, p≈0. Pero con una limitación estructural que el WS3 no declaró.

### 33.1 La corrección: el WS3 no aplicó su propia convención congelada

`cl.evaluar` puntúa al modelo con `(pred>=0)==(gap>=0)` y a la baseline con
`gap > 0`: las filas con `gap == 0.00` se le **regalan al campeón y se le
niegan a la baseline**. Es el sesgo exacto que la §2.8 congeló para la
ventana sellada, reintroducido en la ventana larga sin que nadie lo notara —
yo incluido, al escribir el WS3.

105 filas de 15.033 (0.70%). Efecto: **+0.24 pp de inflación**. Pequeño, real,
y de la clase que más importa: **una corrección que ya estaba escrita y que
igual se saltó.**

### 33.2 El hallazgo que el WS3 no vio: el efecto es asiático

| Bolsa | n | Ventaja | p | Margen emisión→apertura |
|---|---|---|---|---|
| XTKS | 7.230 | +19.1 pp | ≈0 | 1.75 h |
| XTAI | 1.807 | +16.8 pp | ≈0 | 2.75 h |
| XKRX | 3.626 | +15.4 pp | ≈0 | 1.75 h |
| **XETR** | **1.955** | **+2.5 pp** | **0.111** | **8.75 h** |

**En Fráncfort la ventaja no es distinguible de cero**, y la explicación es
mecánica y medida: cuanto más tiempo pasa entre la emisión y la apertura,
menos queda del contagio. Publicar "+15.9 pp" sin este desglose es promediar
un efecto fuerte con uno ausente.

### 33.3 REFUTADA: mi propia hipótesis del §32.5

El §32.5 propuso que el 29-jul olía a **sello corrupto**. El criterio objetivo
se declaró por escrito **antes** de correrlo —con el sesgo nombrado: excluir
esas filas SUBE el 65.9% publicado— y el resultado es inequívoco:

> **0 filas de 223 superan el umbral del 5%. Desviación máxima: 0.00%.**

Los gaps sellados se reproducen **exactamente**. No hubo cierre rancio. Lo que
pasó el 29-jul es una **predicción emitida tarde cuya sesión objetivo saltó
una sesión** — el fenómeno que el acta de la 5.0.2 ya documentó y para el que
ya existe una regla de abstención propuesta. Los +28% y +24% de esa noche son
movimientos reales de mercado.

**Efecto sobre el número publicado: ninguno.** No hay nada que excluir.

### 33.4 Y el 91.4% del §32.4 era un artefacto del join

La "contaminación por revisión medida" era falsa. Las 17 filas discrepantes no
eran revisiones de Yahoo: el panel emparejaba cada emisión con la **siguiente
sesión de calendario** mientras el verificador usa la siguiente sesión **al
sello real**, que en un sello tardío se salta una. Alineando por
`sesion_objetivo`, la coincidencia es del **100%** con desviación **0.00%**.

Doble lección: la contaminación por precios ajustados es **cero** (el factor de
ajuste escala numerador y denominador por igual, así que la razón se conserva),
y **una medición puede fabricar el hallazgo que va a buscar** si el
emparejamiento no se audita.

### 33.5 Supervivencia: un canal en cero, el otro NO EVALUABLE

**Entrada tardía: cero, medido.** Los 8 tickers objetivo tienen historia
completa desde el inicio de la ventana. El único que empieza tarde es ARM
(OPV 2023) y no es objetivo. La comparación "restringida a historia completa"
es idéntica a la completa: no hay nada que restringir.

**Salida: cota frágil.** Ajustando ventaja contra retorno del ticker y
quitando el confusor de bolsa, la relación es **plana** (b=+0.60 pp por unidad
de log-retorno, R²=0.051, n=7). Incluso suponiendo que el **30%** del universo
hubieran sido salidas, la ventaja bajaría a 15.7 pp — **menos de 0.2 pp**.

**Pero la cota se declara frágil:** n=7, todos los retornos observados son
positivos, y extrapolar a −90% es extrapolación pura. Sobre todo, **no captura
el mecanismo**: una empresa en dificultades se desacopla del sector porque su
noticia idiosincrática domina, que es justo el régimen donde el contagio
fallaría. **Esa parte queda NO EVALUABLE**, no acotada.

### 33.6 Tres amenazas inofensivas, con el número que lo demuestra

- **Precios ajustados:** desviación máxima **0.00%** en las 223 filas selladas.
- **Calendarios a ocho años:** **0 violaciones** en 15.033 pares contra los
  calendarios históricos reales; margen mínimo 1.75 h, **estable los nueve
  años** en las cuatro bolsas. Ni el cambio de cierre del TSE de nov-2024 lo
  movió.
- **Cambios de instrumento:** 3 splits en la ventana, **ninguno coincide** con
  un gap extremo; solo 4 filas de 15.033 (0.03%) superan |20 pp| y las cuatro
  son eventos reales.

### 33.7 Fuga en el camino largo: cerrada con contraprueba

Truncar el panel en T no altera **ninguna** predicción de fecha < T (igualdad
exacta del frame), y el emparejamiento sesión→emisión es estrictamente
anterior en el 100% de los casos. **Contraprueba:** con embargo **negativo**
—que mete futuro en el entrenamiento— el mismo criterio sí detecta la
diferencia. El test puede fallar, luego prueba algo.

### 33.8 Las preguntas que quedan para Nicolás

Cinco, en el informe: si se corrige la ventana larga a la convención
congelada; si se corrige la sección de contaminación del WS3; cómo se
reconcilia el §32.5 refutado; cómo se reporta el hallazgo de Fráncfort; y si
las 8 filas del 29-jul (sesión saltada) deben seguir en las métricas — que es
la decisión de abstención pendiente desde la 5.0.2, ahora con un caso concreto
dentro de las 223.

**No se decidió ninguna.** Nada de estado, ninguna fila, ninguna métrica
publicada fue tocada.

---

## 34. WS5 — la hipótesis del relevo asiático: REFUTADA, y era mía

**Fecha:** 30-ago-2026 · **Estatus:** POST-HOC, exploratorio.
**Reporte:** `GEMELO/resultados/relevo_asiatico.md`.
**Pre-registro:** `GEMELO/resultados/preregistro_ws5.md`, escrito y dejado en
el árbol **antes** de correr nada.

### 34.1 El origen es post-hoc y eso se declara arriba, no en una nota al pie

La hipótesis nació del §33: el campeón gana +15 a +19 pp en las bolsas que
abren dentro de 3 h de la emisión y solo +2.5 pp (p=0.111) en Fráncfort, que
abre 8.75 h después. La explicación candidata no era solo «el contagio decae»,
sino que para Europa el SOX de hace nueve horas **no es la información más
fresca**: entre medio Asia operó una sesión entera, y la cadena real sería
NY → Asia → Europa.

Todo lo anterior de la 6.0.0 declaró sus configuraciones antes de mirar sus
datos. **El WS5 no puede hacer eso: su pregunta nació de un resultado.** Las
consecuencias se asumieron por escrito antes de correr —cuenta como intentos
nuevos, es exploratorio, el techo alcanzable es «NO REFUTADA»— porque una
hipótesis construida sobre un patrón ya visto no se confirma con los datos que
la sugirieron.

### 34.2 El N sube de 13 a 25, aplicando la regla mecánicamente

Regla congelada (§4.2 bis): un intento = (configuración × ventana de
evaluación) con resultado reportable. Tres configuraciones × dos estratos
(XETR, ASIA) × dos porciones (exploración, holdout) = **12 nuevos**, y las
doce son reportables.

Contarlas de otro modo —«las porciones son la misma ventana», «los estratos
son un desglose»— habría dado un N menor y un DSR más benévolo. Elegir el N
que favorece al DSR es exactamente lo que el DSR existe para castigar. **No se
probó una cuarta configuración.**

El desglose por bolsa dentro de ASIA se publica como **descriptivo y no
decisorio**: el ajuste tiene que ser por bolsa (§34.3), pero el resultado
reportable es el del estrato. Si alguna decisión se tomara mirándolo, N sube a
31 y hay que decirlo.

### 34.3 La trampa, que habría dado el resultado contrario

Para un objetivo asiático **su propio índice local es casi circular**: Samsung
está dentro del KOSPI, TSMC dentro del TWSE. Alimentar `ks11_ret` a
`005930.KS` no es «el relevo asiático»: es una parte del propio retorno del
objetivo entrando por la puerta de atrás.

Sin la exclusión, E2 habría lucido espectacular en Asia **por la razón
equivocada**, la prueba de simetría habría dado «E2 mejora en las dos» y la
conclusión publicada habría sido la contraria a la que los datos sostienen.

Se excluye siempre el índice de la bolsa del objetivo (XKRX→`ks11_ret`,
XTAI→`twii_ret`, XTKS→`n225_ret`), lo que obliga a **ajustar por bolsa**. Va
como test y **con contraprueba**: se reconstruye el conjunto sin la regla y se
verifica que ahí el índice propio sí aparece — luego la regla hace trabajo.

### 34.4 EL HALLAZGO ESTRUCTURAL: la sesión que el relato describe no es conocible

Antes de mirar un solo resultado, la disponibilidad se **midió** contra
`calendarios.apertura_utc` (calendarios históricos reales) y los cierres
sellados en `datos.CATALOGO`:

| Barra | Cierre UTC | h antes de la emisión | h antes de la apertura de XETR |
|---|---|---|---|
| `^SOX` día D | 21:00 D | **+1.25** | 10.00 |
| `^KS11` día D | 06:30 D | **+15.75** | 24.50 |
| `^KS11` día **D+1** | 06:30 D+1 | **−8.25 (NO conocible)** | **0.50** |

De ahí salen dos hechos que gobiernan la lectura de todo el WS5:

1. **La sesión asiática fresca —la del día D+1, que cierra media hora antes de
   que Fráncfort abra— NO existe a la emisión.** El relato del relevo describe
   exactamente esa sesión. Este experimento no puede probarla sin mover la
   hora de emisión, y mover la hora de emisión es territorio del modelo
   congelado.
2. **El insumo asiático que sí es conocible es el MÁS VIEJO de los dos.** A
   las 22:15 UTC el `^SOX` de D tiene 1.25 h y el `^KS11` de D tiene 15.75 h.
   Peor: el `^KS11` de D cerró **antes** que el `^SOX` de D, así que reacciona
   al SOX de D−1 — que E1 ya lleva dentro como `sox_t1`.

Es la trampa de la asincronía del §29 en su forma más pura, y **le cambia el
significado a un resultado nulo**: lo que se prueba aquí es la versión débil y
compatible con el sistema de la hipótesis.

### 34.5 El resultado: REFUTADA (ausencia)

Regla de decisión declarada en el pre-registro §6, aplicada mecánicamente por
código: «E2 mejora a E1» ⟺ ventaja direccional > 0 **y** McNemar p < 0.05,
sobre el **holdout**.

| Estrato (holdout) | n | E2 | E1 | Ventaja | McNemar | p |
|---|---|---|---|---|---|---|
| XETR | 393 | 53.4% | 59.0% | **−5.6 pp** | 85 vs 107 | 0.1296 |
| ASIA | 2.548 | 55.3% | 72.7% | **−17.5 pp** | 321 vs 766 | ≈0 |

**E2 no mejora a E1 en ninguna parte: es peor en las dos.** Cae la rama
«REFUTADA (ausencia)»: el relevo no aporta donde el mecanismo lo exige.

Y no es que E2 sea simplemente débil — **está por debajo de la tasa base**:
55.3% contra 56.7% en Asia (p=0.0306) y 53.4% contra 55.2% en Fráncfort.

### 34.6 La lectura precisa: el SOX decae; Asia nunca llevó nada

El desglose separa dos explicaciones que el promedio confunde:

| Holdout | E1 (solo SOX) | E2 (solo Asia) | Base |
|---|---|---|---|
| ASIA | **72.5%** | 55.3% | 56.6% |
| XETR | **58.6%** | 53.4% | 55.1% |

**El SOX pierde 13.9 pp de acierto al pasar de Asia a Fráncfort. Asia se
queda plana en la tasa base en las dos.** La debilidad de Fráncfort del §33
**no** se explica porque Asia haya tomado el relevo: se explica porque el SOX
se degrada con la distancia temporal, **y nada lo reemplaza**.

Dicho de otro modo: el §33 midió correctamente el decaimiento; el §34 refuta
la explicación que yo le puse encima.

### 34.7 El holdout hizo su trabajo, y se puede señalar dónde

E3 (SOX + Asia) contra E1 en ASIA:

- **Exploración:** +1.2 pp con **p < 0.0001** — parecía un aporte real.
- **Holdout:** **+0.0 pp con p = 1.0000** — desaparece por completo.

Es el caso de libro de una mejora que no replica, cazada por el único
mecanismo que puede cazarla. Con 9.481 filas de exploración, «significativo»
no bastó.

### 34.8 La tentación, declarada y NO tomada

En el holdout de XETR, **E3 marca 62.1% contra una base de 55.2%: +6.9 pp con
p = 0.0380.** Es el único p<0.05 contra la base de todo el experimento y sería
el titular obvio.

**No se toma, y por tres razones que estaban escritas antes:**

1. El criterio primario declarado es **E2 vs E1**, no E3 vs la base.
2. Contra E1 —la comparación que separa información de maquinaria— E3 da
   +3.1 pp con **p = 0.2188**: no distinguible.
3. **En exploración E3 era PEOR que E1 en XETR** (59.0% vs 60.3%). El signo se
   da vuelta entre porciones sobre 393 filas: es la firma del ruido, no la de
   un hallazgo.

Quedarse con ese número sería elegir el resultado después de verlo, sobre el
estrato más pequeño, con la comparación que más favorece. Queda registrado
**como tentación descartada**, que es la única forma honesta de que aparezca.

### 34.9 Hallazgo colateral: el IC del ΔMAE venía en otra escala

`cl.comparar` —escrita en el WS2b, heredada por el WS3— acompaña un
`delta_mae` en **pp** con un intervalo salido de `inf.bootstrap_bloques`, que
es el IC del **Sharpe** (media/desv). Son escalas distintas y se ve a simple
vista: **en 8 de los 12 pares de esta corrida el punto estimado caía FUERA de
su propio intervalo.**

**Ninguna conclusión previa cambia.** Las decisiones se tomaron con
`ic_excluye_cero`, que es **exactamente** equivalente en ambas escalas: como
`sd > 0` conserva el signo réplica a réplica, el evento «el cuantil α/2 está
sobre cero» depende solo de la proporción de réplicas sobre cero, y ésa es
idéntica para la media y para media/desv. Lo que estaba mal era el **número
impreso**, no el veredicto.

Se añadió `inferencia.bootstrap_media` (IC de la media, **compartiendo sorteo
y semilla** con `bootstrap_bloques`, para que dos intervalos del mismo dato
sigan siendo comparables), y el WS5 publica los dos con nombres que dicen qué
es cada uno: `ic_sharpe_dmae` e `ic_delta_mae_pp`. Los 43 valores de
referencia del WS1 siguen reproduciendo exactos tras la extracción del
remuestreo compartido.

**Los reportes del WS2b y del WS3 NO se corrigieron** — es criterio humano y
queda como pregunta abierta.

### 34.10 La §2 perdió su instante «a la fecha»: el GATE 1 se puso rojo solo

Al correr el GATE 1 del WS5, **cinco tests de `test_linea_base.py` fallaban
sin que nadie hubiera tocado una línea de código.** No eran del WS5 y no los
rompió el WS5: los rompió **el propio experimento avanzando**.

Las cifras de la §2 son una medición **puntual** del 25-ago sobre n=228. El
30-ago la base tiene **245** verificaciones y **38** snapshots. Contrastar una
afirmación congelada contra un denominador que se mueve solo puede terminar
en rojo, y terminó:

| Afirmación | Documento | Base viva 30-ago |
|---|---|---|
| n (verificaciones 4.6.0) | 228 | 245 |
| modelo: acierto de gap % | 65.8 | 67.8 |
| ventaja pp | 5.3 | 7.8 |
| McNemar p | 0.3193 | 0.1158 |
| snapshots sellados | 35 | 38 |

**La corrección NO toca ninguna cifra del documento: le devuelve su
instante.** Es la misma disciplina que el proyecto ya aplica en todas partes
—un dato sin su `available_at` no significa nada— aplicada por primera vez a
una *afirmación* en vez de a un precio.

`backtest.linea_base.CORTE_SECCION_2 = "2026-08-24"`, el último sello anterior
al congelamiento, reproduce **las tres familias de cifras a la vez**:

- verificaciones con `verificado_en` ≤ 24-ago → **228 exactas** (223 bajo
  `excluir_cero`),
- snapshots con `fecha` ≤ 24-ago → **35**,
- betas con `fecha` ≤ 24-ago → **|Δβ| 0.0427** (documento 0.043 ± 0.001).

**21 de 21 vuelven a reproducir.**

Un detalle que no es detalle: el corte va sobre **`verificado_en`, no sobre
`fecha_senal`**. El 21-ago tiene filas verificadas a **ambos lados** del
congelamiento, así que ningún corte por fecha de señal reproduce las 228. Si
me hubiera conformado con un corte por fecha de señal habría tenido que
«ajustar» alguna cifra para que cuadrara — es decir, editar el pre-registro
para que encajara con los datos, que es justo lo prohibido.

**El corte es OPT-IN.** `cargar()` sin argumentos sigue leyendo el track
record VIVO, que es lo correcto para la plataforma; `contrastar()` sí viene
pinchado por defecto, porque contrasta afirmaciones congeladas. Los runners
del WS2b y del WS3 quedan **sin pinchar a propósito**: re-correrlos hoy sobre
más filas es una evaluación distinta y mejor, no un error — sus reportes
llevan su propia fecha y su propio n.

**Nota para la lectura del track record vivo:** el 30-ago la ventaja del
campeón sobre la constante es **+7.8 pp con p = 0.1158**, contra +5.3 pp y
p = 0.3193 en el congelado. Sigue **sin ser distinguible de cero** al 5%, así
que la conclusión de la §2 no cambia — pero se mueve en la dirección del
campeón y conviene que quede anotado con su fecha en vez de descubrirse dentro
de tres meses.

### 34.11 Lo que no se tocó

`universo.py` intacto: sacar IFX.DE porque aporta poco sería quitar el dato
incómodo, y además es cambio de universo → `UNIVERSO_VERSION` → territorio del
modelo congelado. `motor.py`, `senales.py`, `snapshot.py` y el camino de
sellado, intactos; hay un test que verifica la dirección que protege el sello
(**nada del camino de sellado importa el WS5**). No se corrió el veredicto
escalonado de la 5.1. Ninguna fila sellada, ninguna base, ningún reporte
anterior ni ninguna conclusión previa fue modificada.

El único cambio fuera de `GEMELO/` es aditivo y retrocompatible:
`cl.correr_configuracion` acepta una `cfg` explícita (el conjunto de features
depende de la bolsa y no puede vivir en un diccionario fijo), con un test que
fija que `cfg=None` reproduce **exactamente** el comportamiento anterior.

### 34.12 Preguntas abiertas — requieren criterio de Nicolás

1. **¿Se corrigen los IC del ΔMAE de los reportes del WS2b y del WS3?** Están
   en otra escala (§34.9). Ninguna conclusión cambia, pero los intervalos
   publicados no son los de la columna que acompañan.
2. **¿Vale la pena medir la versión FUERTE del relevo?** Exigiría usar el
   cierre asiático del día D+1, que no es conocible a las 22:15 UTC. Sería un
   experimento sobre **otra hora de emisión** —territorio del modelo
   congelado— y solo tiene sentido como pregunta de diseño, nunca como
   modificación del 4.6.0.
3. **¿Cómo se reporta ahora Fráncfort en el README?** El §33 dejó abierto cómo
   publicar el +2.5 pp; el §34 añade que la explicación del relevo **no es** la
   respuesta, y que E1 (solo SOX) rinde 58.6% ahí contra 72.5% en Asia.
4. **Las cinco preguntas abiertas del §33 siguen abiertas.** Ninguna se
   decidió aquí.

---

## 35. El README se rehace entero: el hallazgo central ya no era el track record

**Fecha:** 30-ago-2026. El README llevaba modificado sin commitear desde el
25-ago y su contenido se había quedado atrás: se escribió cuando lo único
medido era la ventana sellada. Cuatro workstreams después hay material
mejor, y el hallazgo central del proyecto **no estaba en la portada**.

### 35.1 Qué pasa a liderar, y por qué

La versión anterior lideraba con *«el resultado titular es negativo, y ése
es el punto»*: +4.0 pp con p=0.4633 sobre 223 filas. Era honesto pero
incompleto — el WS3 y el WS4 ya habían medido algo que ningún número de la
ventana sellada podía mostrar.

**El efecto se disipa con la distancia**, y eso es cualitativamente
distinto de una tasa de acierto:

| Bolsa | n | Ventaja | p | Margen emisión→apertura |
|---|---|---|---|---|
| Tokio | 7.230 | +19.1 pp | ≈0 | 1.75 h |
| Taipéi | 1.807 | +16.8 pp | ≈0 | 2.75 h |
| Seúl | 3.626 | +15.4 pp | ≈0 | 1.75 h |
| Fráncfort | 1.955 | +2.5 pp | 0.111 | 8.75 h |

**Un artefacto estadístico no tiene por qué desvanecerse con el tiempo
transcurrido; una propagación de información sí.** Por eso el README pasa
de reportar un marcador a reportar un mecanismo — y con la cautela puesta
en el texto y no en una nota: **con n=4 bolsas no se ajusta una curva**, es
un **escalón medido**, no un gradiente estimado.

Y va **pegada** a esa sección, no en un apartado de descargo, la hipótesis
del relevo asiático que el WS5 **refutó**. Publicar el hallazgo sin la
explicación fallida sería contar solo la mitad que favorece.

### 35.2 La discrepancia del encargo: convención `estricta` vs congelada

**El encargo pedía publicar «n=245 al 30-ago · +7.8 pp · p=0.1158».** Esas
cifras son correctas, pero salen de la convención **`estricta`**. Bajo la
convención **congelada en la §2.8** (`excluir_cero`, la oficial del
proyecto) las mismas filas dan:

| Convención | n | Modelo | Base | Ventaja | p |
|---|---|---|---|---|---|
| `estricta` | 245 | 67.8% | 60.0% | +7.8 pp | 0.1158 |
| **`excluir_cero` (congelada)** | **240** | **67.9%** | **61.3%** | **+6.7 pp** | **0.1849** |

**Se publica la congelada.** Poner el +7.8 en la portada habría sido
exactamente la asimetría del empate que el WS4 acaba de cazarle al WS3 —
regalarle los `gap == 0.00` al campeón y negárselos a la baseline— tres
secciones antes de contar que el proyecto se corrigió por hacer eso mismo.
La cifra más favorable, publicada con la convención equivocada, habría
desmentido la sección que la acompaña.

Por la misma razón la comparación temporal va **like-for-like**: 25-ago
+4.0 pp / p=0.4633 → 30-ago +6.7 pp / p=0.1849, las dos bajo la congelada.
Y el multiplicador de muestra baja de 66× a **61×** (14.618/240), porque el
denominador correcto es 240 y no 223.

### 35.3 El matiz que el WS4 corrigió, publicado como corrección

El WS3 declaró una *«contaminación por revisión»* del 91.4% como
limitación de la ventana larga. **Es falsa**, y el README lo dice con esa
palabra: la desviación real es **0.00% en las 223 filas**, porque el factor
de ajuste de Yahoo escala el *open* y el *close* previo por igual y la
razón se conserva. **La ventana larga es más válida de lo que su propio
autor creyó** — que es una frase incómoda de escribir y por eso está.

Lo que sí la limita se publica entero: es reconstrucción con el código y el
universo de hoy aplicados hacia atrás; el canal de entrada tardía es
**cero**, el de salida está acotado en **menos de 0.2 pp incluso con un 30%
de salidas**, y el tercero se declara **NO EVALUABLE** con sus palabras
exactas — *una empresa en dificultades se desacopla del sector, y ése es
justamente el régimen donde el contagio fallaría*.

### 35.4 WS3 revisó a WS2b, y el README no se queda con la versión vieja

| | Muestra | C2 vs C1 |
|---|---|---|
| WS2b | 223 filas | +2.8 pp, p=0.3613, IC del ΔMAE incluye cero |
| WS3 | 12.628 filas | **+1.3 pp, p=0.0003**, IC excluye cero |

El efecto **encogió y se volvió significativo** a la vez: el patrón de una
muestra chica sobreestimando el tamaño de un efecto que no podía detectar.
La conclusión publicada es **«la información expandida sí aporta, y aporta
poco»**, con la lección explícita: *«no significativo» no es lo mismo que
«no hay nada»*. Dejar la versión del WS2b habría sido publicar una
conclusión que el propio proyecto ya había revisado.

Se conserva el hallazgo de C1 = campeón (McNemar 0 vs 0) pero **acotado a
la ventana sellada**, porque sobre la ventana larga C1 y el campeón sí
divergen (+0.5 pp, p=0.0355). Una afirmación sin su ventana es una
afirmación sin denominador.

### 35.5 Y la corrección que la auditoría le hizo al proyecto

El WS3 publicó +15.90 pp puntuando al modelo con `>=` y a la baseline con
`>`: 105 filas de 15.033 (0.70%) tienen `gap == 0.00`. Bajo la convención
congelada son **+15.66 pp**. Infló 0.24 pp por no seguir su propia regla, y
**una auditoría encargada de derrumbar el hallazgo fue la que lo cazó**.

Va en el README con sección propia. Es la clase de cosa que un README suele
omitir, y es justo la que sostiene el resto de sus afirmaciones.

### 35.6 Badges y barrido de cifras viejas

`tests` 236 → **299**. El badge de ventaja se **desdobla en dos**, porque
una sola cifra ya no representa al proyecto: `ventana sellada · +6.7 pp ·
p=0.18 · n=240` y `ventana larga · +15.66 pp · n=14.618`. Etiquetar la
ventana en el badge impide leer el 15.66 como si fuera point-in-time.

Barrido con script de las cifras obsoletas: no quedó ninguna de las 16
buscadas (236, 78.8%, n=80, 3.12/3.50, 89.2%, 1.76×, «35 snapshots», «5
jobs», «al 24-ago», y las cuatro cifras del WS2b que el WS3 revisó), y las
53 que deben estar, están. **Hallazgo del barrido:** el README decía «los 5
jobs de launchd» y el diagrama mostraba cinco — son **seis** desde la 5.0.1
(el re-chequeo del vigía de las 20:30). Corregido en los dos sitios.

Los 26 enlaces relativos se verificaron uno a uno contra el árbol: ninguno
roto. Se añade una tabla **«Auditar cada cifra»** con los siete documentos
de `GEMELO/` más DECISIONES.md, para que cada número del README tenga su
fuente a un clic.

### 35.7 El tono

No es una retractación ni una disculpa: **es un instrumento funcionando.**
Mide un efecto, encuentra su firma mecánica, se corrige dos veces, refuta
una hipótesis propia y declara qué no puede evaluar. El argumento del WS7
—liderar con la integridad y no con los aciertos— se cumple mejor así que
con la versión anterior: aquella lideraba con un negativo, ésta lidera con
un mecanismo **y** con las tres veces que el proyecto se desmintió a sí
mismo para llegar a él.

---

## 36. La regla canónica del switch, y por qué la composición se detuvo

**Fecha:** 30-ago-2026. Reporte completo:
`data/sombra/switch_20260830.md`.

### 36.1 La regla, escrita ANTES de ejecutarla

Decidida por Nicolás y escrita en `docs/SOMBRA.md` **antes** de tocar una
sola fila — que es la mitad del valor de tenerla:

```
fecha <= 2026-08-25   →   canónico el MAC
fecha >= 2026-08-26   →   canónico el PC
```

**Ninguna fila se modifica.** La cadena canónica se **COMPONE** desde dos
fuentes; las copias del Mac quedan intactas como registro histórico y vía
de rollback. «Las filas selladas jamás se reescriben» se cumple
literalmente: no se reescribe ninguna, se elige de cuál de las dos
historias viene cada tramo.

No es preferencia. Desde el 26-ago el PC selló en horario (22:15:07 /
22:15:03 / 22:15:03, descarga 28/28) y el Mac llegó **1 h 51 y 31 min
tarde** y **no selló el 28**. La regla **cubre el 28-ago**, que el Mac dejó
vacío; **excluye la fila espuria del sábado 29-ago** sin excepción ad hoc
—una regla que necesita una excepción para el caso incómodo no es una
regla—; y **recupera el 25-ago**, que el PC no tiene. Los sellos del Mac no
son inválidos, solo tardíos, y se conservan íntegros en su propia base.

### 36.2 El criterio de 3 días con paridad NO se cumplió: 0/3

Queda escrito con todas las letras. **El switch se hace por fundamento
operativo, no por paridad alcanzada.** El criterio suponía **un titular
estable contra el cual medir**, y el Mac dejó de serlo: no se puede medir
paridad contra una referencia que sella 1 h 51 tarde, se salta un viernes y
sella un sábado. **El criterio se volvió inaplicable** — no se incumplió
por descuido ni se relajó por conveniencia.

**Riesgo aceptado:** queda **sin verificar** que las dos máquinas no
discrepen **computacionalmente** bajo alguna condición no observada.
**Evidencia en contra:** en ~40 predicciones selladas por ambas, la única
diferencia de nivel 1 fue **0.0001 en el R² de `6857.T` el 27-ago**,
atribuible a que el Mac descargó 31 min más tarde.

### 36.3 La trampa que casi compone mal: `titulares.fecha` es un TIMESTAMP

**`noticias.titulares.fecha` no es una fecha: es un ISO completo**
(`2026-08-25T00:10:51+00:00`). Un `fecha <= '2026-08-25'` literal —el
predicado que la regla dice, aplicado tal cual— manda **todo el 25-ago al
lado equivocado**, porque como cadena `'2026-08-25T00:10:51+00:00' >
'2026-08-25'`. Con el predicado ingenuo la partición daba 4.128/779; con
`substr(fecha,1,10)`, **4.336/571**.

Es la única columna del sistema con esa forma y **la trampa es silenciosa:
no falla, compone mal**. Queda escrita en la tabla de predicados de
`docs/SOMBRA.md` para que la próxima composición no la pise.

### 36.4 Lo único que cambia: los `id` surrogados

Los `id` son claves autoincrementales, **no contenido sellado**. Componer
dos historias produce colisiones inevitables (24, 6 y 8 en `senales.db`;
**139** en `titulares`). Se resolvió conservando **idénticos** los `id` del
Mac y desplazando los del PC: offset constante en `senales.db` —queda una
continuación contigua, exactamente lo que habría pasado si esas filas se
hubieran añadido a la base del Mac en su momento— y **remapeo explícito**
en `titulares`, con el mapa **arrastrado a `analisis.titular_id`**.

**Fidelidad verificada: TOTAL.** Comparando todas las columnas excepto el
`id`, cada región del compuesto es **idéntica** a su fuente, tabla por
tabla. Ningún valor medido fue tocado.

### 36.5 ⛔ DETENIDA: el invariante 4 falla, y falla en las tres bases

De las nueve invariantes, **ocho pasan y la 4 falla**: 10 de 36 snapshots
con `fecha <= 2026-08-25` no tienen `plataforma_version` 5.0.2 ni NULL.

**No es un defecto de la composición: es la historia real de la
plataforma.**

| `plataforma_version` | n | Rango |
|---|---|---|
| `(NULL)` | 14 | 04-jul → 24-jul |
| **`5.0.0`** | **5** | **27-jul → 31-jul** |
| **`5.0.1`** | **5** | **03-ago → 07-ago** |
| `5.0.2` | 12 | 10-ago → 25-ago |

La plataforma evolucionó `NULL → 5.0.0 → 5.0.1 → 5.0.2 → 5.0.3` y cada
snapshot **selló la versión vigente esa noche**, que es exactamente lo que
el versionado dual existe para hacer. La prueba de que la composición no lo
introdujo es que **las tres bases dan 10 violaciones**: el Mac, el PC antes
de componer, y el compuesto. **El invariante, tal como está redactado,
nunca lo cumplió ninguna base del proyecto.**

**No se tocó el invariante y no se reemplazó nada.** El protocolo dice
«restaurar el respaldo y reportar; no se arregla nada sobre la marcha», y
reescribir un invariante que acaba de fallar es el ejemplo de manual de
arreglar sobre la marcha. En una operación cuyo objeto es la integridad del
track record, ese atajo vale menos que el retraso.

Como la composición se construyó **en un archivo aparte** y solo se iba a
reemplazar el árbol tras pasar las nueve, **no hubo nada que restaurar**:
`senales.db` y `noticias.db` están **byte a byte idénticos** al respaldo
(SHA-256 verificado). **El PC sigue en sombra.**

### 36.6 El invariante 9 pasó, y es el que importaba

El bloque anclado en `CORTE_SECCION_2 = 2026-08-24` es **idéntico byte a
byte** antes y después: `estricta` n=228 +5.3 pp p=0.3193 · `verificador`
n=228 +3.1 pp p=0.5854 · `excluir_cero` n=223 +4.0 pp p=0.4633. Contraste
de la §2: **21/21 reproducen** en ambos lados.

Ese ancla existe gracias al §34.10 —el instante «a la fecha» que el WS5
tuvo que devolverle a la §2 cuatro horas antes—. Sin él, esta verificación
habría sido imposible: el número de referencia se habría movido solo y no
se habría podido distinguir «la composición rompió algo» de «el track
record creció».

### 36.7 Consecuencia que hay que resolver en el mismo movimiento

La base canónica gana el 25-ago y el 28-ago y pierde los dos días tardíos
del Mac: las verificaciones pasan de **245 a 253**, y el track record vivo
bajo la convención congelada pasa de **n=240 · +6.7 pp · p=0.1849** a
**n=248 · +6.5 pp · p=0.1849**.

**El README publica las cifras viejas.** Hay que actualizarlo **en el mismo
movimiento** que el switch, no después: publicar una portada que dice 240
mientras la base canónica dice 248 es la clase de desfase que este proyecto
documenta como errata en vez de cometer.

### 36.8 Lo que NO se hizo

No se tocó `motor.py`, `senales.py` ni `snapshot.py`. **No se cambió
`PLATAFORMA_VERSION`**: el cambio de modo es configuración, no código, y
5.0.3 quedó congelada al sellarla la primera fila el 26-ago (§12) — no
corresponde bump, y si correspondiera sería decisión humana. **No se quitó
`MKI_MODO`.** No se fusionó a `main`. No se pusheó.

---

## 37. El invariante 4 se corrigió, y la composición se ejecutó

**Fecha:** 30-ago-2026, mismo día que el §36. Reporte:
`data/sombra/switch_20260830.md`.

### 37.1 El invariante estaba mal formulado, no era exigente de más

El original decía:

> *Toda fila con `fecha <= 2026-08-25` tiene `plataforma_version` 5.0.2 o
> NULL.*

**Afirmaba un VALOR cuando lo que había que verificar era PROCEDENCIA.** La
región anterior al corte recorre `NULL → 5.0.0 → 5.0.1 → 5.0.2` porque cada
snapshot **selló la versión vigente esa noche** — es `version.py`
funcionando exactamente como está documentado, no un defecto de los datos.
El invariante **contradecía el diseño del propio proyecto**.

**Ninguna base lo cumplió jamás:** el Mac, el PC antes de componer y la
base compuesta daban **10 «violaciones» las tres, idénticas**. Un
invariante que ninguna instancia válida del sistema puede satisfacer no
está midiendo el sistema: está midiendo su propia redacción.

### 37.2 La corrección: 4a + 4b

| | |
|---|---|
| **4a** | Toda fila con `fecha >= 2026-08-26` tiene `plataforma_version = 5.0.3` |
| **4b** | La región `fecha <= 2026-08-25` es **idéntica a su fuente del Mac** en `plataforma_version`, **fila por fila**, sin afirmar ningún valor concreto |

**La distinción que importa: no se relajó porque falló, se corrigió porque
estaba mal formulado.** No son lo mismo y la diferencia es todo el valor
del procedimiento:

- **4a es igual de estricta** que la mitad correcta del original: exige un
  valor exacto donde ese valor sí está definido, la región nueva.
- **4b verifica fidelidad a la fuente**, que es **lo que el invariante
  quería decir desde el principio**. Es más fuerte que enumerar valores: no
  hay que acertarle a la lista histórica, hay que reproducirla entera.

Resultado: **4a, 0 violaciones · 4b, 0 discrepancias sobre 36 filas.**

### 37.3 Por qué esto no fue «arreglar sobre la marcha»

Porque **la corrección no la hizo quien encontró el fallo, y no se hizo en
el momento del fallo.** La secuencia quedó en dos commits separados:

1. **§36 (`3fea7c4`)** — la composición se **detiene**, se reporta el
   diagnóstico y **no se toca nada**. El árbol queda byte a byte idéntico.
2. **§37** — Nicolás decide la nueva redacción, y **recién entonces** se
   recompone y se ejecuta.

Si hubiera reescrito el invariante al verlo fallar, el registro no
distinguiría «estaba mal formulado» de «estorbaba». Con la parada de por
medio, el registro **es** la distinción.

### 37.4 La ejecución

Recomposición desde cero, **nueve invariantes en verde**, reemplazo del
árbol y **re-verificación contra el árbol real** (no contra la copia del
scratchpad). SHA-256 antes y después en
`~/mki-switch/respaldo-pc-20260830/`.

El **invariante 9** volvió a pasar **byte a byte**: el bloque anclado en
`CORTE_SECCION_2 = 2026-08-24` es idéntico —`excluir_cero` n=223, +4.0 pp,
p=0.4633— y el contraste de la §2 reproduce **21/21**. La composición no
movió la §2 ni un decimal, que era exactamente lo que había que demostrar.

**Fidelidad de la composición: TOTAL.** Cada región es idéntica a su fuente
en todas las columnas salvo el `id` surrogado.

### 37.5 El track record canónico, y qué cambió

| Convención | n | Modelo | Base | Ventaja | McNemar p |
|---|---|---|---|---|---|
| `estricta` | 253 | 66.0% | 58.5% | +7.5 pp | 0.1158 |
| `verificador` | 253 | 66.0% | 60.5% | +5.5 pp | 0.2542 |
| **`excluir_cero`** | **248** | **66.1%** | **59.7%** | **+6.5 pp** | **0.1849** |

La base gana el **25-ago** (que el PC no tenía) y el **28-ago** (que el Mac
dejó vacío), y pierde los dos días tardíos del Mac y el sábado espurio.
**La conclusión no se mueve: la ventaja sigue sin ser distinguible de
cero.** +6.7 pp con la base del PC sola, **+6.5 pp** con la canónica.

### 37.6 El README se actualizó en el MISMO movimiento

Publicar una portada invalidada por la operación que la acompaña es
exactamente la clase de desfase que este proyecto documenta como errata en
vez de cometer. **Doce bloques**, no solo el titular — porque varias cifras
dependen de `n` y moverlas a medias es peor que no moverlas:

| Qué | Antes | Ahora |
|---|---|---|
| Duelo sellado | 67.9% (163/240) vs 61.3% · +6.7 pp | **66.1% (164/248) vs 59.7% · +6.5 pp** |
| Wilson modelo / base | [61.8–73.5] / [55.0–67.2] | **[60.0–71.7] / [53.5–65.6]** |
| Retorno de sesión | 60.4% [54.1–66.4] | **60.9% [54.7–66.8]** |
| MAE del gap | 3.02 vs 3.41 (−11.4%) | **2.98 vs 3.33 (−10.5%)** |
| Cobertura 80% · ratio | 90.0% · 1.82× | **90.3% · 1.84×** |
| Snapshots (régimen) | 38 | **39** |
| Ventana larga / sellada | 61× | **59×** |
| Trayectoria desde el 25-ago | 17 filas, +2.7 pp | **25 filas, +2.5 pp** |

Además, la sección de la ventana sellada declara ahora su **procedencia**:
que es la **cadena canónica** compuesta bajo la regla de `docs/SOMBRA.md`.
Un número sin su procedencia, en una base que acaba de componerse de dos
fuentes, sería un número sin denominador.

Barrido con script: **ninguna de las 16 cifras invalidadas sobrevive** y
las 17 nuevas están. (El único «17 filas» que queda es el del artefacto del
join del §33, que no depende de `n`.)

### 37.7 Lo que sigue pendiente, a propósito

**`MKI_MODO=sombra` sigue puesto.** Componer la base canónica y cambiar el
modo son **dos operaciones distintas**, y esta fue solo la primera: la
máquina tiene ya la historia correcta, pero todavía no emite. Quitar
`MKI_MODO` —y apagar antes los timers del Mac, nunca al revés— es el
segundo movimiento, y es de Nicolás.

No se tocó `motor.py`, `senales.py` ni `snapshot.py`. **No se cambió
`PLATAFORMA_VERSION`**: 5.0.3 quedó congelada al sellarla la primera fila
el 26-ago (§12). No se fusionó a `main`. No se pusheó.
