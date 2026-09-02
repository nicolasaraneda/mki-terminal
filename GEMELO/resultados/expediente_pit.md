# Expediente: ¿hace falta comprar datos point-in-time?

Frente E de la tercera corrida autónoma (31-ago-2026). **Documento
solamente.** No se tocó código, ni `senales.db`, ni ninguna fila sellada,
ni se commiteó nada.

**Esto no decide nada.** Comprar o no comprar datos es una decisión de
Nicolás. Lo que sigue es el expediente que permite tomarla: qué se sabe,
qué no, cuánto puede valer el sesgo, qué venden los proveedores y qué
seguiría roto aunque se compre.

---

## Resumen ejecutivo, con el hallazgo incómodo primero

**La razón por la que este expediente existe fue refutada por el propio
proyecto hace cinco días, y la refutación todavía no llegó al documento
que la motivó.**

`GEMELO/DISEÑO.md:533` congeló, el 25-ago, el Riesgo declarado #5:

> "**Datos gratuitos.** Yahoo revisa la historia en silencio. Un proveedor
> con datos point-in-time es un requisito para cualquier conclusión
> fuerte, y hoy no lo hay."

Ese riesgo se midió el 26-ago (`ventana_larga.md:39-45`: 8.6% de filas
contaminadas) y **se desmontó el mismo día** (`auditoria_ws3.md:213-236`:
la cifra era un artefacto del join; la contaminación real es **0.00% sobre
223 filas**). `DECISIONES.md` §33.4 ("Y el 91.4% del §32.4 era un
artefacto del join") lo registra.

Como `GEMELO/DISEÑO.md` es un pre-registro congelado, su §8.5 **no se
edita**: la corrección se documenta aparte y con fecha posterior. Este
documento es esa corrección.

**Corrección fechada al Riesgo #5 (31-ago-2026):** para el canal de
*precios*, la premisa es falsa y está medida. Para el canal de
*composición del universo*, la premisa sigue en pie — pero **datos
point-in-time de precios no lo resuelven**, porque es otro producto.

**Y hay un segundo hallazgo, del lado de afuera.** Se consultaron diez
proveedores el 31-ago-2026 (§3). **Ninguno vende datos point-in-time de
grado (a) para precios de las cuatro bolsas, y ninguno vende
constituyentes históricos del ^SOX.** El "point-in-time" que promocionan
LSEG, FactSet y Sharadar es exclusivamente de *fundamentales*. La única
pregunta que sigue abierta —la composición del universo— **no tiene
producto que la responda a ningún precio**.

**Recomendación (§5), marcada como recomendación: NO COMPRAR NADA HOY.**
No porque sea caro: porque el problema medible está cerrado por un
teorema y el problema abierto no está a la venta.

---

## 1. Qué preguntas del proyecto quedan hoy sin respuesta SOLO por esto

**Respuesta corta: para precios, ninguna. Para composición del universo,
una — y no la arregla comprar datos de precios.**

### 1.1 El canal de precios: CERRADO, con dos evidencias independientes

**Evidencia empírica.** `auditoria_ws3.md:98-108` (Amenaza 2) despejó el
cierre de referencia que el verificador usó en cada una de las **223 filas
selladas** y lo comparó contra la historia descargada hoy:

> **"Desviación máxima: 0.00%. En las 223 filas."** (`auditoria_ws3.md:103`)

**Evidencia estructural, que es la que importa más.** El factor de ajuste
de un split o un dividendo escala **por igual** todos los precios
anteriores a la fecha ex. El objetivo del proyecto es un **cociente**:

```
gap = open(t) / close(t−1) − 1
```

Si la fecha ex es posterior a `t`, numerador y denominador se multiplican
por el mismo `k` y **el cociente no cambia**. Este argumento no depende
del tamaño de la muestra: **vale para las 14.618 filas, no solo para las
223 verificables.** La medición empírica confirma un teorema, no
extrapola una tasa.

### 1.2 La segunda frase de `ventana_larga.md:26` sigue publicada y nadie la revisó

La auditoría del WS4 corrigió la cifra del 8.6%. **No corrigió esta otra
afirmación, que sigue viva en el reporte publicado:**

> "Una reconstrucción a años vista está contaminada por esa revisión, y
> **la contaminación va en la dirección optimista**." (`ventana_larga.md:26`)

**Esa dirección nunca se justificó, y con lo que se sabe hoy es, si
acaso, la contraria.** El razonamiento:

- El canal multiplicativo (splits, dividendos) **se cancela en el
  cociente**: no aporta sesgo en ninguna dirección.
- El canal que sobrevive es la **corrección de datos erróneos** (un
  `open` mal impreso que la fuente arregla después). Esa corrección es
  **idiosincrática y no es función del modelo**: no tiene por qué
  alinearse con la predicción βᵢ·SOX.
- Ruido no correlacionado con la predicción **atenúa** la ventaja
  medida hacia la tasa base. No la infla.

Para que la contaminación fuera "optimista" tendría que estar
**correlacionada con la predicción del modelo**, y la predicción se
computa desde la misma serie revisada — pero el único canal que las
correlaciona es el multiplicativo, que ya se demostró que se cancela.

**Esto es un hallazgo de este frente, no una cifra medida.** Se declara
como argumento, no como medición.

### 1.3 El canal que SÍ sigue abierto — y no es de precios

`auditoria_ws3.md:297-301` lo declara **NO EVALUABLE**, no acotado:

> "Sin una lista histórica de constituyentes de la cadena no se puede
> reconstruir el universo real de 2018."

Y `auditoria_ws3.md:306-308` separa las dos cosas con precisión:

> "La ventana larga **sigue sin ser point-in-time** en lo que respecta a
> la *composición* del universo, aunque sí lo sea en los precios
> (Amenaza 2). Son dos cosas distintas y solo una quedó cerrada."

**La pregunta abierta, en una frase:** *¿la ventaja de +15.66 pp
sobreviviría si el universo de 2018 incluyera a las empresas de la cadena
que desde entonces quebraron, fueron absorbidas o dejaron de ser
relevantes?*

El mecanismo que preocupa está nombrado en `auditoria_ws3.md:86-89`: una
empresa en dificultades **se desacopla del sector** porque su noticia
idiosincrática domina — y ése es justamente el régimen donde el contagio
del SOX fallaría. La regresión no puede capturarlo.

**El punto crítico de todo este expediente:** eso NO se arregla con datos
point-in-time de precios. Requiere (a) valores deslistados con historia
completa y (b) una lista histórica de quién estaba en la cadena. Y (b)
**no se compra**, porque la cadena de valor de `universo.py` no es un
índice: es un mapa construido a mano, con criterio propio
(`UNIVERSO_VERSION`). Ningún proveedor vende "los constituyentes de la
cadena rock→chip→data center al 27-ago-2018", porque esa categoría es del
proyecto.

Lo más cerca que se puede comprar es la membresía histórica de un índice
sectorial (^SOX, SOXX, SMH) como **aproximación declarada** al universo de
cada año. Es un sustituto legítimo, y hay que decir que es un sustituto.

### 1.4 Un canal residual identificado en este frente y NO medido por nadie

El argumento del cociente (§1.1) tiene una excepción exacta: **cuando la
fecha ex cae sobre la sesión objetivo `t`**. Ahí `close(t−1)` se escala
por `k` y `open(t)` no, y el cociente **sí cambia** entre lo que se selló
esa noche y lo que se reconstruye hoy.

`auditoria_ws3.md:196-209` (Amenaza 6) verificó los **splits** (3 en la
ventana, ninguno coincide con un gap extremo). **Los dividendos no se
verificaron.** Con 8 tickers objetivo, 1-2 fechas ex por año y 8 años, el
orden de magnitud es ~100-130 de las 15.033 filas del panel (≈0.9%), con
un error por fila del orden del rendimiento del dividendo (~0.5-1.5 pp)
sobre un |gap| mediano de 0.90 pp (`auditoria_ws3.md:209`).

**Se declara como canal identificado y no medido.** Medirlo es gratis
—`yfinance` publica el calendario de acciones corporativas— y **no
requiere comprar nada**. Deliberadamente no se midió acá: el proyecto
acaba de retractar un análisis por haberse corrido en comandos sueltos
que se perdieron (`concentracion.md:248-254`), y este frente no va a
repetir ese error citando una cifra sin código versionado.

### 1.5 Una landmine operativa que conviene registrar

`GEMELO/ventana_larga.py:314-345` **sigue emitiendo el texto refutado**:
la prosa del 8.6% y el `merge` sobre `["fecha", "ticker"]`
(`ventana_larga.py:213-215`) que la auditoría demostró que es el join
equivocado. Peor: `tests/test_ventana_larga.py:185-194` **exige por test**
que esa sección exista.

**Consecuencia:** volver a correr el WS3 hoy **republicaría la cifra
falsa**, y el test la protegería. No es urgente (nadie está corriendo el
WS3), pero es deuda con nombre.

---

## 2. Qué tan grande puede ser el sesgo

### 2.1 El canal de precios, acotado con las cifras del repo

| Magnitud | Valor | Fuente |
|---|---|---|
| Ventaja publicada, ventana larga | **+15.66 pp** sobre n = 14.618 | `auditoria_ws3.md:135`, README |
| Filas de diferencia que la sostienen | **≈ 2.289** | aritmética: 0.1566 × 14.618 |
| Fracción de filas que tendrían que estar contaminadas **a favor del modelo** para explicarla entera | **15.7%** | ídem |
| Tasa de discrepancia medida | **0 de 223** | `auditoria_ws3.md:103` |
| Cota superior 95% sobre esa tasa (regla de tres, 0/223) | **≤ 1.35%** | 3/223 |
| Distancia entre lo necesario y la cota | **≈ 11.6×** | 15.7 / 1.35 |

**Y la cota de la regla de tres es la débil de las dos.** La fuerte es el
argumento estructural de §1.1, que no depende de n.

**La honestidad que corresponde:** las 223 filas tienen entre 2 días y 2
meses de antigüedad. Acotan la tasa de revisión **a corto plazo**, no a
ocho años, y las revisiones se acumulan con la edad. Extrapolar 2 meses a
8 años no es válido y no se hace acá. Lo que sostiene la conclusión es el
teorema del cociente, no la extrapolación.

### 2.2 Por bolsa: dónde la cota es holgada y dónde no

| Bolsa | n | Ventaja | Filas que la sostienen | Contaminación necesaria para borrarla |
|---|---|---|---|---|
| XTKS (Tokio) | 7.230 | +19.1 pp | ≈1.381 | **19.1%** |
| XTAI (Taipéi) | 1.807 | +16.8 pp | ≈304 | **16.8%** |
| XKRX (Seúl) | 3.626 | +15.4 pp | ≈558 | **15.4%** |
| **XETR (Fráncfort)** | 1.955 | +2.5 pp | ≈49 | **2.5%** |

(Ventajas de `auditoria_ws3.md:26-31`; filas por aritmética.)

Fráncfort es el único donde la contaminación necesaria (2.5%) está en el
mismo orden que la cota de la regla de tres (1.35%). **Pero eso no importa
para ninguna conclusión publicada**, porque el resultado de Fráncfort ya
se publica como *no distinguible de cero* (p = 0.111). Comprar datos para
distinguir un +2.5 pp contaminado de un +2.5 pp limpio no cambiaría el
veredicto: sigue siendo "no distinguible de cero".

Y el hallazgo central del README **no es ninguna de esas cuatro cifras por
separado: es el escalón entre ellas** (+19.1 a 1.75 h contra +2.5 a 8.75
h). Para que la revisión de precios lo fabricara, tendría que estar
**correlacionada con el margen de horas hasta la apertura** — un mecanismo
que nadie ha propuesto y que no tiene por qué existir.

### 2.3 El canal de composición: NO SE PUEDE ACOTAR, y hay que decir por qué

`auditoria_ws3.md:64-89` intentó acotarlo por regresión (ventaja del
ticker contra su retorno en la ventana) y llegó a "menos de 0.2 pp incluso
suponiendo que el 30% del universo hubieran sido salidas". **El propio
documento declara esa cota frágil:**

> "n = 7, R² = 0.05, y **todos los retornos observados son positivos**
> (+105% a +5948%): predecir en −90% es extrapolación pura."
> (`auditoria_ws3.md:84-86`)

**Qué haría falta para acotarlo de verdad, en orden de dificultad:**

1. Una lista de valores deslistados de XTKS/XKRX/XTAI/XETR con historia de
   precios completa (**esto sí se compra** — ver §3).
2. Un criterio de pertenencia a la cadena aplicable hacia atrás
   (**esto no se compra**: es una decisión de diseño de Nicolás, la misma
   clase de decisión que produjo `UNIVERSO_VERSION`).
3. Rehacer la ventana larga con el universo reconstruido por año, y
   declararlo como un intento nuevo del DSR (el acumulado ya va en ≥43,
   `concentracion.md:318-338`).

El paso 2 es el que no tiene proveedor. **Sin él, comprar el paso 1 no
produce ninguna respuesta.**

---

## 3. La tabla de proveedores

*(Anexo de referencia. Se incluye porque se pidió y porque sirve si en el
futuro se decide atacar el canal de composición — no porque la evidencia
de §1 y §2 lo justifique hoy.)*

Diez proveedores consultados el **31-ago-2026** en sus propias páginas
(precios, docs y FAQ). Donde el parseo automático fue inconsistente entre
corridas, se dice. Donde no se pudo verificar, dice **no verificado** — no
se completó nada por inferencia.

### 3.0 La convención de grados, que es lo que hace útil la tabla

Casi todos los proveedores usan la frase "point-in-time". Casi ninguno la
usa para precios.

| Grado | Qué significa | Sirve para el problema |
|---|---|---|
| **(a)** | Snapshots fechados / vintages: la base **tal como existía** en la fecha X | **Sí** |
| **(b)** | `unadjusted` + tabla de acciones corporativas fechada → permite **reconstruir** lo que se veía | **Sí, con trabajo propio** |
| **(c)** | Histórico ya ajustado retroactivamente, como Yahoo | **No. No resuelve nada.** |

### 3.1 El hallazgo transversal, antes de la tabla

**Ninguno de los diez vende (a) para precios de acciones de las cuatro
bolsas.** Cero. El "point-in-time" que promocionan LSEG, FactSet y
Sharadar es exclusivamente de **fundamentales** (balances *as-reported*),
que es justamente la confusión contra la que había que ir con cuidado.

**Y ninguno de los diez vende constituyentes históricos del ^SOX.** El
producto que atacaría el canal abierto de §1.3 **no existe en ninguno de
los diez**, a ningún precio.

**Deslistados fuera de EEUU:** solo dos lo afirman (LSEG DataScope Plus,
"80 millones de valores activos y deslistados", 178 exchanges; Databento,
"310.000+ listados y deslistados", 215 exchanges). Ambos son enterprise
sin precio público. Los cinco de bajo costo son **EEUU (y Norgate,
además, AU/CA)**.

### 3.2 Tabla principal — las cuatro bolsas y el ^SOX

| Proveedor | Precio verificado (31-ago-2026) | XKRX | XTAI | XTKS | XETR | ^SOX | Grado PIT de PRECIOS | Deslistados no-EEUU |
|---|---|---|---|---|---|---|---|---|
| **EODHD** | EOD All World **$19.99/mes · $199/año**; EOD+Intraday $29.99/mes; Fundamentals $59.99/mes; ALL-IN-ONE $99.99/mes | Sí | Sí | **dudoso** | Sí | **no verificado** (404) | **(b)** | No |
| **Norgate** | Silver $270/año · Gold $360 · Platinum $630 · Diamond $787.50 (12 m, EEUU) | **No** | **No** | **No** | **No** | **No** | (b) para EEUU/AU/CA | No (EEUU/AU/CA) |
| **Sharadar / Nasdaq DL** | Prices $9–39/mes ($99–299/año); Bundle $29–69/mes | **No** | **No** | **No** | **No** | **No** | **(b)**, EEUU | No (EEUU) |
| **Tiingo** | Free $0; Power **$30/mes · $300/año**; comercial $50/mes · $499/año | **No** | **No** | **No** | **No** | **No, declarado** | (b), EEUU+China | no verificado |
| **LSEG / Refinitiv** | **sin precio público** ("contact us"). Único oficial: **+9% admin fee** sobre el fee del exchange + $1/$20 mes por keystation | Sí (indirecto) | Sí | **Sí** (EOD desde 1984) | Sí | no verificado (RIC `.SOX` existe) | **(b)** vía UP + AF/AX fechado | **Sí** (80 M, 178 exchanges) |
| **FactSet** | **sin precio público** | no verificado | no verificado | no verificado | no verificado | no verificado | **(b)** (el (a) es solo de fundamentales, desde feb-1999) | parcial (180.000+ activos e inactivos, geografía no verificada) |
| **Polygon.io / Massive** | $0 · $29 · $79 · $199 · $2.499/mes | **No** | **No** | **No** | **No** | no verificado | (b), EEUU | No |
| **Databento** | Standard $199/mes; Plus $1.750/mes; Unlimited $4.500/mes (anual) | **No** (ausente del catálogo) | **No** (ausente) | **No** (`active:false`) | **No** (solo Eurex, derivados) | no verificado (SOX es de Nasdaq, no Cboe) | (b), EEUU | Sí (afirmado, 215 exchanges) |
| **QuantRocket** | pricing **tras login, no verificado**; tercero no oficial menciona "desde $19.99/mes" | vía EDI, no confirmado | vía EDI, no confirmado | vía EDI (MIC XJPX, confirmado por un cliente) | vía EDI, no confirmado | **No** | Sharadar **(b)** pero EEUU; **EDI ≈ (c)** — ya ajustado, sin campo unadjusted | No |
| **FirstRate Data** | $49.95 por ticker EEUU; $29.95 FX | **No, declarado** | **No** | **No** | **No** | **Sí**, producto de índice propio (parcialmente verificado) | (b) | No |
| **Algoseek** | $600–$3.750/mes según dataset | **No** | **No** | **No** | **No** | **No** | (b); el (a) es de constituyentes EEUU | No |

### 3.3 Notas por proveedor, donde el detalle cambia la lectura

**EODHD** — el único de bajo costo con cobertura real de tres de las
cuatro bolsas, y el más citado en el repo (`DECISIONES.md` §P0, "El
Roca→Chip del terminal es exclusivamente el sellado", como integración
futura para **intradía**, que es otra cosa).
- Tickers verificados: **TSMC `2330.TW`** ✓, **Infineon `IFX.XETRA`** ✓,
  **Samsung `005930.KO`** ✓ — nótese: `.KO`, **no `.KS`**, así que un
  empalme con la serie de Yahoo exige mapear símbolos.
- **Tokio no verificado y con evidencia contradictoria:** el MIC `XTKS`
  aparece en la API de horarios, pero no hay página de exchange y
  `8035.T` / `6857.T` dan 404. Tokio es **la bolsa que más pesa** en el
  hallazgo central (7.230 de 14.618 filas, +19.1 pp): un proveedor que no
  la cubra no sirve para nada de lo que interesa.
- Grado **(b)**, cita literal: *"The OHLC values are raw — adjusted for
  neither splits nor dividends. The adjusted_close field is adjusted for
  both"*.
- Constituyentes: **solo familia S&P**, y *"survivorship-bias-free
  reconstruction is reliable from April 2012"*. Nada de ^SOX.
- El plan exacto que incluye constituyentes fue **inconsistente entre dos
  parseos** — verificar a mano antes de citarlo.

**Norgate** — descartado por dos motivos, cualquiera de los dos basta.
1. *"No packages exist for Japan, Korea, Taiwan, or Germany"*: vende
   **precios de índices** mundiales, no acciones individuales de esas
   bolsas. Los ocho tickers objetivo **no están**.
2. Licencia: *"our data service can only be licensed for personal use by
   individuals. **There is no alternative business/commercial
   licensing**"*. MKI Terminal publica su track record en un portafolio
   público — si eso cuenta como comercial, el producto es inutilizable
   por contrato, no por precio.

**Databento** — el caso donde el marketing y el catálogo se contradicen, y
conviene registrarlo. Promociona "50+ venues" incluyendo las cuatro
bolsas; la verificación empírica contra el catálogo JSON y las URLs de
dataset (`XKRX.ITCH`, `XTKS.ITCH`, `XTAI.ITCH`, `XETR.EOBI`) muestra que
**ninguno es comprable hoy**: Tokio figura con `"active": false`
("próximamente"), y Corea, Taiwán y Xetra ni aparecen. Solo existe
`XEUR.EOBI` (Eurex, derivados). **Comprar por la página de marketing, en
este caso, sería comprar aire.**

**LSEG / Refinitiv** — el único con cobertura geográfica creíble de las
cuatro bolsas y deslistados globales. Y también:
- **Sin precio público.** Lo único oficial es el mecanismo de cobro:
  *"a 9% LSEG administration charge on the price offered by the
  exchange"* — es decir, **los fees de exchange se pasan al cliente**, más
  el 9%. Cuatro bolsas asiáticas/europeas son cuatro licencias.
- Cifras de terceros ($1.000–$2.500/usuario/mes para Datastream, contratos
  anuales de seis y siete cifras) **no verificadas** y no se citan como
  precio.
- Grado **(b)**: el mecanismo real es `UP` (precio sin ajustar) + `AF`/`AX`
  (factor de ajuste fechado) — *"AX indicates at which date the adjustment
  has been made and by how much"*. El "point-in-time" de su marketing es
  Compustat / I/B/E/S / Worldscope: **fundamentales**.
- Constituyentes históricos: el propio LSEG documenta que *"users have to
  reconstruct the constituent lists manually"* — no es (a), es (b).

**QuantRocket** — su valor sería revender un bundle con Asia. Ese bundle
es **EDI**, y EDI entrega precios *"split- and dividend-adjusted"* **sin
campo sin ajustar** documentado: es **grado (c)**, que por definición no
resuelve nada. Además EDI se cobra **por exchange** (*"Purchase multiple
times for additional exchanges"*): cuatro bolsas, cuatro compras.

**FirstRate Data** — la curiosidad útil de la tanda: es el único que vende
**^SOX** como producto propio, a precio de un ticker. Pero declara
textualmente *"We do not cover international (non-US) stocks"*, así que no
aporta ninguno de los ocho objetivos.

### 3.4 Qué costaría, en el mejor de los casos, y por qué no alcanza

La combinación **más barata que cubriría algo parecido a lo que el
proyecto usa** sería un empalme de tres proveedores:

| Pieza | Proveedor | Costo verificado |
|---|---|---|
| Acciones de XKRX, XTAI, XETR (Tokio **sin verificar**) | EODHD EOD All World | **$199/año** |
| ^SOX | FirstRate Data | **$49.95** (una vez) |
| ^VIX3M, ^KS11, ^TWII, ^N225, ^GDAXI, ES=F, NQ=F, 4 pares FX | **ningún proveedor único verificado** | **no cotizable** |

Y el resultado de ese empalme sería **grado (b)**, no (a); no cubriría
Tokio con certeza; requeriría mapear símbolos (`005930.KO` vs `005930.KS`);
y **no incluiría ni un solo deslistado asiático ni un constituyente
histórico del ^SOX**, que son las dos cosas que responderían la única
pregunta abierta.

**Es decir: el gasto mínimo no compra la respuesta.** Compra una segunda
fuente de precios para un canal que ya está cerrado por un teorema.

---

## 4. Qué se podría reconstruir con datos PIT, y qué no

### 4.1 Lo que SÍ se desbloquearía comprando

| Se desbloquea | Qué producto hace falta | Nota |
|---|---|---|
| Acotar el canal de **salida** del sesgo de supervivencia | valores deslistados de las 4 bolsas, con historia completa | solo **LSEG** y **Databento** lo afirman, ambos **sin precio público** (§3.1); y requiere además el criterio de pertenencia (§2.3, paso 2), que no se compra |
| Reconstruir el universo por año con un índice sectorial como sustituto declarado | constituyentes históricos del ^SOX | **no lo vende ninguno de los diez** (§3.1). Ni siquiera es cuestión de precio. |
| Verificar la revisión de precios **en fechas viejas** (2018-2021), no solo en las 223 recientes | una segunda fuente independiente de OHLC diario | mejora la §2.1 de "teorema + 223 filas" a "teorema + muestra de 8 años"; **no cambia ninguna conclusión, porque el teorema ya la sostiene** |
| Medir el canal residual de fechas ex (§1.4) | nada: es gratis con `yfinance` | **no requiere comprar** |
| Reemplazar `^VIX3M`, descartado por cobertura (0.0, `ventana_larga.md:117`) | historia de índices Cboe | es el único insumo de GEMELO que hoy se cae por falta de datos |

### 4.2 Lo que NO arregla ningún proveedor

1. **El track record sellado tiene 248 filas y no hay forma de comprar
   más.** Es la única evidencia point-in-time del proyecto
   (`README.md:114`), crece ~8 filas por día hábil, y su ventaja
   (+6.5 pp, p = 0.1849) sigue sin ser distinguible de cero. **Ningún
   dato histórico convierte una predicción de 2019 en una predicción
   sellada**, porque el sello no es un dato: es un timestamp emitido antes
   del hecho. Esto es la MASTER RULE del proyecto y es inmune al dinero.
2. **La concentración de julio.** `concentracion.md:280-316` deja abierto
   si el +6.5 pp es real o una racha en 6 fechas. Eso se resuelve con
   **más filas selladas**, es decir con **tiempo**, no con datos.
3. **El régimen único.** 39 snapshots, una sola etiqueta de régimen, la
   columna no tiene varianza. Se resuelve cuando el mercado cambie de
   régimen.
4. **El criterio de pertenencia a la cadena hacia atrás** (§2.3, paso 2).
5. **El sesgo de especificación** que `GEMELO/DISEÑO.md:526-528` ya
   declara: "estas features las diseña alguien que ya vio esta ventana.
   La única defensa real es el sellado en vivo".
6. **El gatillo de la Etapa 5.1** (N ≥ 150 en vivo + cambio de régimen, o
   3 meses). Es una condición sobre datos que todavía no existen.

**El patrón:** todo lo que bloquea al proyecto hoy se desbloquea con
**tiempo de sellado**, no con dinero. Es una posición cómoda: el recurso
escaso es el que se acumula solo mientras los seis timers corran.

### 4.3 Y un costo de comprar que no es el precio

El catálogo de GEMELO son **15 series** (`GEMELO/datos.py:127-141`): 7
índices de 5 familias distintas (PHLX/Nasdaq, Cboe ×2, KRX, TWSE, Nikkei,
Deutsche Börse), 2 futuros CME, 2 ETFs y 4 pares FX — más los 28 tickers
de `universo.py` en 5 bolsas.

Ningún proveedor de bajo costo licencia esa combinación completa. En
particular las **licencias de índice** (Nikkei 225 es el caso conocido de
licenciamiento restrictivo) se cobran aparte y por familia. Comprar por
partes significa **empalmar fuentes**, y un empalme mete su propia
inconsistencia — exactamente la clase de defecto que la Amenaza 6
(`auditoria_ws3.md:190-209`) declara evaluada solo parcialmente:

> "Un cambio de símbolo que Yahoo hubiera empalmado silenciosamente **no
> dejaría rastro** en ninguna de las dos pruebas."
> (`auditoria_ws3.md:302-305`)

**Cambiar de fuente no es gratis aunque el dato sea gratis:** obligaría a
revalidar las 223 filas selladas contra la fuente nueva, y cualquier
discrepancia sería una errata a documentar, no un dato a corregir (las
filas selladas jamás se reescriben).

---

## 5. Recomendación

**Marcada como recomendación. La decisión es de Nicolás.**

### RECOMENDACIÓN: no comprar nada hoy. Cero dólares.

Los cinco motivos, en orden de fuerza:

1. **El producto que resolvería la única pregunta abierta no existe.**
   Ninguno de los diez proveedores consultados vende constituyentes
   históricos del ^SOX, y solo dos afirman deslistados fuera de EEUU —
   ambos enterprise, sin precio público. Esto no es "caro": es que **no
   está en el catálogo de nadie**. Y ninguno vende grado (a) de precios
   para las cuatro bolsas. La decisión de compra, tal como estaba
   planteada, **no tiene objeto que comprar**.

2. **El problema que motivaba la compra está cerrado por un teorema, no
   por una muestra.** El cociente `open(t)/close(t−1)` es invariante al
   factor de ajuste. Comprar datos PIT de precios compraría certeza sobre
   algo que ya es cierto por construcción.
3. **El problema que sigue abierto no se resuelve con este producto.** El
   sesgo de composición necesita un criterio de pertenencia histórico que
   **no está en venta**, porque la cadena de valor es una construcción del
   proyecto. Comprar deslistados sin ese criterio deja el trabajo a mitad
   de camino y ya se pagó.
4. **La cota es 11.6× holgada** (15.7% de contaminación necesaria contra
   ≤1.35% de cota superior sobre lo medido), y el hallazgo central no es
   una cifra sino **un escalón entre cuatro bolsas** — que la revisión de
   precios tendría que estar correlacionada con el huso horario para
   fabricar.
5. **Nada de lo que hoy bloquea al proyecto es un problema de datos.** Las
   248 filas selladas, la concentración de julio, el régimen único y el
   gatillo de la 5.1 se resuelven todos con tiempo, y el tiempo ya está
   corriendo.

### Lo que sí recomiendo hacer, y es gratis

Cuatro cosas, ninguna cuesta dinero, ordenadas por relación
valor/esfuerzo:

1. **Medir el canal de fechas ex** (§1.4), con código versionado en el
   repo. Cierra el último resquicio del argumento del cociente. Coste:
   una sesión.
2. **Corregir la landmine de `ventana_larga.py`** (§1.5) — el generador y
   su test todavía protegen la cifra refutada. Es una errata fechada, en
   el estilo de la casa. Se agrupa naturalmente con el ítem 5 de
   `cola_decisiones.md` (las cinco preguntas del WS4).
3. **Retirar o corregir la frase "la contaminación va en la dirección
   optimista"** (`ventana_larga.md:26`), que sobrevivió a la auditoría sin
   que nadie la revisara y que, con lo que se sabe hoy, apunta al lado
   equivocado.
4. **Registrar la corrección fechada al Riesgo #5 de
   `GEMELO/DISEÑO.md:533`.** El pre-registro no se edita; la corrección va
   aparte y con fecha posterior — que es lo que este documento es. Si
   Nicolás lo acepta, corresponde un acta en `DECISIONES.md`.

### Cuándo reabrir esta decisión

Escrito ahora, antes de que haya un resultado que lo tiente:

- **Si se decide atacar el canal de composición del universo** — y solo
  entonces —, el orden correcto es: (1) Nicolás fija el criterio de
  pertenencia histórico a la cadena; (2) recién ahí se piden cotizaciones
  a **LSEG** y **Databento**, los dos únicos que afirman deslistados
  globales, ambos sin precio público. Nunca al revés: sin el criterio, el
  dato no responde nada, y pedir precio antes es comprometerse con un
  gasto para una pregunta que todavía no está formulada.
- **Si aparece un caso de revisión de precios que el teorema no explique**
  (una discrepancia en el cociente, no en el nivel), entonces la §1.1 está
  incompleta y esta recomendación se cae.
- **Si el proyecto empieza a usar datos intradía** — ya anotado en
  `DECISIONES.md` §P0 como integración futura de EODHD, "donde se
  etiquetará como fuente distinta" —, esa compra se justifica por una
  razón completamente distinta (Yahoo no da intradía histórico), y este
  expediente no la evalúa.

### La opción que NO recomiendo, dicha explícitamente

Comprar "el plan barato de alguno, por si acaso". Un proveedor que cubre
tres de las cuatro bolsas y ninguno de los siete índices no cierra ninguna
pregunta, cuesta plata todos los meses, y **agrega la obligación de
revalidar las filas selladas contra una segunda fuente** — es decir, crea
trabajo sin cerrar nada.

---

## Qué NO se hizo

No se tocó `motor.py`, `senales.py`, `snapshot.py`, `universo.py`,
`GEMELO/ventana_larga.py` ni ningún test. No se leyó ni se escribió
`senales.db` (no existe en esta máquina; los conteos salen de los CSV
versionados de `data/backups/`). No se corrigió `ventana_larga.md` ni
`GEMELO/DISEÑO.md` — ambas correcciones están **propuestas**, no
aplicadas. No se commiteó nada. No se decidió ninguna compra.

## Trazabilidad

Todas las cifras del repo se citan con archivo:línea. Las cifras
aritméticas de §2 (2.289 filas, 15.7%, regla de tres 1.35%, 11.6×) se
derivan de las citadas, con la operación escrita al lado para que
cualquiera la rehaga con una calculadora.

Los diez proveedores de §3 se consultaron el **31-ago-2026** en sus
propias páginas de precios, documentación y FAQ, por dos investigaciones
independientes. Todo precio citado se leyó en la página del proveedor;
donde no hay precio público, dice **sin precio público** y no se cita
ninguna cifra de terceros como si fuera oficial. Donde el parseo
automático de una tabla fue inconsistente entre corridas (el plan de
Fundamentals de EODHD, los niveles Platinum/Diamond de Norgate), **se
señala y se recomienda verificación manual antes de usar esa cifra para
firmar nada**. Donde no se pudo verificar, dice **no verificado** — no se
completó ningún casillero por inferencia.

---
Herramienta de análisis — no constituye asesoría financiera.
