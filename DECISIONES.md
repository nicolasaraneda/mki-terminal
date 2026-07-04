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
