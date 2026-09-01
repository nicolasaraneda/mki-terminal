# Etapa 5.1 — expediente del gatillo, conteo de intentos y verificación del arnés

**Escrito el 2026-09-01 a las 01:42 hora de Chile (05:42 UTC), commit
`06b50a1`, ANTES de ejecutar una sola línea del backtest.** Ése es el punto
del documento: el conteo de intentos del Deflated Sharpe declarado después
de ver los resultados es el conteo hecho a conveniencia, y un DSR con el N
mal contado **miente hacia arriba** (`GEMELO/DISEÑO.md` §4.2 bis).

Autorización de Nicolás, textual: *"Autorizo la etapa 5.1: ejecutá el
veredicto del backtest B0–B5 con los criterios congelados de
`backtest/DISEÑO.md`, sin tocarlos. Contá TODOS los intentos, incluidos los
de las cinco corridas anteriores, reconstruidos desde las actas y declarados
antes de calcular nada. Reportá cada baseline con intervalo. Escribí el
veredicto con la misma firmeza si es negativo."*

---

## 0. EL GATILLO NO ESTÁ CUMPLIDO — y la instrucción se contradice a sí misma

`backtest/DISEÑO.md`:226–233 congela el gatillo en el GATE B del
25-jul-2026. El backtest queda habilitado para ejecutarse **con veredicto**
cuando ocurra lo primero de:

- **(a)** N ≥ 150 verificaciones limpias en vivo **Y al menos un cambio de
  régimen del SOX observado** durante el track record, o
- **(b)** 3 meses de operación continua del sistema autónomo
  (25-jul-2026 → **25-oct-2026**).

### Estado medido hoy, 01-sep-2026

| Condición | Estado | Evidencia |
|---|---|---|
| (a1) N ≥ 150 verificaciones limpias | **CUMPLE** | 261 filas en `verificacion_apertura` con `legacy=0`, `modelo_version='4.6.0'` y `gap_pct` no nulo (256 bajo la convención `excluir_cero`). Consultado en `mode=ro`. |
| (a2) ≥ 1 cambio de régimen del SOX | **NO CUMPLE** | `select regimen, count(*) from snapshots group by 1` devuelve **una sola etiqueta**: `Alcista · vol alta` (38 filas) más 2 filas con `regimen` NULL. Las nulas son dato faltante, no un régimen distinto. La columna no tiene varianza en los 40 snapshots del track record (2026-07-04 → 2026-08-31). |
| (a) = a1 **Y** a2 | **NO CUMPLE** | la conjunción falla por a2 |
| (b) 3 meses continuos | **NO CUMPLE** | faltan **54 días** (hoy 01-sep; el gatillo cae el 25-oct-2026) |

**El gatillo no está cumplido por ninguna de las dos vías.**

### La contradicción, nombrada

Nicolás autorizó ejecutar el veredicto *"con los criterios congelados de
`backtest/DISEÑO.md`, sin tocarlos"*. **El gatillo ES uno de esos criterios
congelados**, y está en el mismo documento. Ejecutar hoy el veredicto pleno
violaría el documento que la propia instrucción manda respetar. No es una
desobediencia detectada: es una contradicción interna a la instrucción, que
Nicolás casi con seguridad no conocía al escribirla — el estado del régimen
no es visible sin consultar la base.

**Esa contradicción no se resuelve aquí y no la resuelve ningún agente.**
Se resuelve con una decisión escrita de Nicolás, y este archivo es el
expediente de esa decisión.

### Qué se ejecuta igual y qué NO

Lo **reversible** se ejecuta; lo **irreversible** no se toca.

| Se ejecuta | Motivo |
|---|---|
| El conteo de intentos (§1) | No gasta nada y hace falta igual |
| La verificación del arnés (§2) | No gasta nada y hace falta igual |
| El walk-forward completo B0–B5 con intervalos y DSR | **Reversible**: se puede volver a correr cuantas veces se quiera; sólo cuesta contar los intentos, que es lo que la §1 hace |

| NO se ejecuta | Motivo |
|---|---|
| **V7 — el holdout en cuarentena** | `GEMELO/DISEÑO.md`:462 lo define como **"evaluado una sola vez"**. Es un recurso de un solo uso. Gastarlo hoy, con el gatillo sin cumplir, lo quema para siempre y **no se puede deshacer**. Queda INTACTO y EN CUARENTENA. V7 se marca NO EVALUABLE por esta razón, no por falta de maquinaria. |

La corrida queda sellada por lo que realmente es: **una corrida de veredicto
completa, con el gatillo NO cumplido por la vía (a) y a 54 días de la (b), y
con el holdout sin gastar.** No se estampa `5.1` a secas, y el aviso va en la
primera pantalla del `resumen.md`, no en una nota al pie.

> **ACTUALIZACIÓN DE LAS 02:15 (después de la fase 2), añadida sin reescribir
> lo de arriba.** La etiqueta prevista aquí era
> `5.1-gatillo-incumplido`. La fase 2 encontró **fugas demostradas**, que es
> una cosa peor y distinta de "gatillo sin cumplir", así que la corrida se
> selló como **`5.1-invalidada-por-fuga`**. El párrafo original se conserva
> porque describe correctamente lo que se planeaba a las 01:42, que es
> justamente lo que un expediente escrito por adelantado tiene que preservar.

### La decisión que queda pendiente para Nicolás

Dos caminos, y sólo él puede elegir:

1. **Esperar al 25-oct-2026.** La vía (b) se cumple sola. Ese día el
   veredicto pleno —holdout incluido— se ejecuta sin desviación.
2. **Relevar por escrito la condición (a2)** —el cambio de régimen— dejando
   asentado por qué. Argumento disponible a favor: el track record vivo no
   ha visto un cambio de régimen, pero **la ventana del backtest sí**
   (medido abajo: cuatro cambios). Argumento en contra: (a2) existe
   precisamente para exigir que el *track record en vivo* haya visto más de
   un régimen, y el backtest no lo sustituye — es la diferencia entre
   potencia y validez que el proyecto ya escribió en `ventana_larga.md`.

**Dato que alimenta la decisión, medido y no citado de memoria:** sobre la
ventana de evaluación declarada abajo (2024-09-02 → 2026-08-28), el régimen
del SOX reconstruido con la misma regla del backtest (MA50/MA200, cortes
±1%) recorre **Alcista (79 sesiones) → Lateral (54) → Bajista (84) →
Lateral (3) → Alcista (289)**: **cuatro cambios de régimen**. Lo que el
track record vivo no tiene, el backtest sí lo tiene. Son dos cosas
distintas y este documento no las confunde.

---

## 1. EL CONTEO DE INTENTOS, DECLARADO ANTES DE COMPUTAR NADA

### 1.1 La regla que se aplica (congelada, no se toca)

`GEMELO/DISEÑO.md`:363-364 — **"Cuenta como UN intento cada par
(configuración × ventana de evaluación) cuyo resultado sea reportable."**
Re-evaluar la misma configuración sobre otra ventana **no es gratis**.
`.claude/rules/backtest.md` — **"Cada configuración evaluada se registra
como intento, incluidas las descartadas por malas."** `GEMELO/DISEÑO.md`:374-377
— **NO cuentan** la baseline "siempre al alza" (es la hipótesis nula) ni la
búsqueda interna de `alpha` por CV temporal.

`GEMELO/DISEÑO.md`:389-390 — *"Ser conservador aquí es gratis: un N de más
sube el umbral SR0 y hace al DSR más exigente. Un N de menos lo inutiliza."*

### 1.2 El hallazgo previo al conteo: hay TRES cifras vigentes y se contradicen

| Cifra | Dónde vive | Estado |
|---|---|---|
| **25** | `GEMELO/relevo_asiatico.py`:76 (`N_INTENTOS_WS5`), **fijada por test** en `tests/test_relevo_asiatico.py`:214-215 | Es la única que un evaluador leería del CÓDIGO — y es la más baja de las tres |
| **26** | `GEMELO/resultados/dos_ventanas.md`:178-180 | Declara subir a 26 por un experimento que **nunca se corrió** |
| **43** | `GEMELO/resultados/concentracion.md`:318-338 y `DECISIONES.md`:4082-4087 | Declarado en prosa como deuda; **la constante del código nunca se actualizó** |
| **32** | `GEMELO/CONDICIONAL/DISEÑO.md`:268-289 | Declara "el N acumulado pasa de 25 a 32", apoyándose en la base vieja |

Cuatro documentos del mismo repositorio dan cuatro números distintos, y el
único ejecutable dice el más bajo. **Ése es el estado real del conteo antes
de esta corrida.**

Nota que importa: la segunda corrida **retractó su conclusión**
(`concentracion.md`:190-278), no el hecho de que esos análisis se corrieron.
Por la regla del DSR **cuentan igual** — de hecho las configuraciones
descartadas por malas son las que más importa contar.

### 1.3 El conteo reconstruido, sumando por sumando

Cada fila cita su fuente. Nada se cuenta de memoria.

#### Estrato A — lo que la constante del código ya contiene (25)

| # | Configuración | Ventana | Fuente | n |
|---|---|---|---|---|
| 1–6 | B0, B1, B2, B3, B4, B5 | walk-forward de humo 2026-06-01 → 07-18 | `backtest/resultados/20260726-032635-humo-legacy/resumen.md` | 6 |
| 7–9 | C1, C2, C3 | ventana sellada (WS2b) | `GEMELO/resultados/control_lineal.md`:62-64 | 3 |
| 10–12 | C1, C2, C3 | ventana larga (WS3) | `GEMELO/resultados/ventana_larga.md`:124-126 | 3 |
| 13 | Campeón reconstruido (= B2) | ventana larga (WS3) | `GEMELO/DISEÑO.md`:386 | 1 |
| 14–25 | E1, E2, E3 × {XETR, ASIA} × {exploración, holdout} | WS5 | `GEMELO/resultados/relevo_asiatico.md`:149-160 | 12 |
| | **Subtotal A** | | `GEMELO/RELEVO.md`:146-148 | **25** |

#### Estrato B — declarado y no corrido (+1 → 26)

| # | Configuración | Fuente | n |
|---|---|---|---|
| 26 | Complemento ventana larga vs. sellada — **declarado por adelantado, NUNCA ejecutado** | `dos_ventanas.md`:178-184 | 1 |

Se conserva en el conteo aunque no se haya corrido: quitarlo sería bajar N,
y bajar N es lo único que el DSR no perdona.

#### Estrato C — declarado en prosa, nunca llevado al código (+18 → 44)

| # | Configuración | Fuente | n |
|---|---|---|---|
| 27–33 | 6 condiciones candidatas medidas + modelo conjunto del pre-registro condicional (la 7ª, densidad de noticias, se declaró NO MEDIBLE) — **retractadas** | `GEMELO/CONDICIONAL/DISEÑO.md`:268-289; resultados en `bitacora_02.md`:74-94; retractación en `concentracion.md`:190-278 | 7 |
| 34–36 | 3 scan-statistics sobre la ventana sellada (con corrección por búsqueda p=0.52; posición fija p=0.04; 6 fechas al azar p=0.04) | `concentracion.md`:85-89 | 3 |
| 37–44 | 8 McNemar por bolsa (XETR/XKRX/XTAI/XTKS × dentro/fuera del bloque) | `concentracion.md`:50-55 | 8 |
| | **Subtotal C** | aritmética explícita en `concentracion.md`:333 (25+7+3+8=43) | **18** |

#### Estrato D — reconstruidos en esta corrida, FIRMES (+32 → 76)

Ninguno de éstos está en 25, ni en 26, ni en 43. Todos son
(configuración × ventana) con resultado reportable.

| # | Configuración | Fuente | n | Por qué cuenta |
|---|---|---|---|---|
| 45–48 | Campeón desglosado por bolsa sobre la ventana larga (XTKS +19.1 / XTAI +16.8 / XKRX +15.4 / XETR +2.5, p=0.111) | `auditoria_ws3.md`:26-31 | 4 | **El WS4 entero aporta cero al desglose oficial** y produjo cuatro resultados reportables — y **el WS5 completo nació de mirarlos** (`preregistro_ws5.md`:12). Es el caso textual que obliga a subir N. |
| 49–50 | Campeón sobre ventana larga bajo convención `verificador` (+15.27) y `excluir_cero` (+15.66) | `auditoria_ws3.md`:131-135 | 2 | El intento nº13 contó sólo la convención `estricta` (+15.90). El +15.66 es la cifra canónica publicada hoy. |
| 51 | Scan-statistic de ancho fijo 6 sobre la **ventana larga** (máx +80 pp dic-2018, p=0.4255) | `bitacora_02.md`:64-67 | 1 | Ventana distinta de los 3 scans del estrato C. |
| 52–56 | Abstención por magnitud a umbrales 0.15 / 0.25 / 0.30 / 0.50 / 0.75 sobre la ventana sellada n=228 | `GEMELO/DISEÑO.md`:115-121 | 5 | La regla nombra literalmente *"otro criterio de abstención"* como configuración (`DISEÑO.md`:347-348). El umbral 0.00 es la mirada base y no se cuenta dos veces. |
| 57 | La misma abstención a 0.25 **re-evaluada** sobre la ventana sellada actual (+6.5 → +10.7 pp) | `GEMELO/RELEVO.md`:177-183 | 1 | Ventana nueva ⇒ intento nuevo. Y es decisoria: ancla el umbral de 5 pp de REL-V4. |
| 58–59 | Hipótesis del punto de giro: particiones SOX usado < 0 y ≥ 0 | `GEMELO/DISEÑO.md`:87-88 | 2 | "Se formuló y se refutó" — refutada cuenta igual. |
| 60–63 | Desglose por bolsa de la **ventana sellada completa** (XTKS +8.6 / XKRX +0.0 / XTAI +7.4 / XETR +9.1) | `dos_ventanas.md`:217-222 | 4 | Ventana distinta de los 8 McNemar del estrato C (dentro/fuera del bloque). |
| 64–67 | Recomputo de C1, C2, C3 y CAMPEÓN sobre la ventana sellada **nueva** (n=240) | `DECISIONES.md` §38.2 | 4 | Es literalmente el caso que hizo subir N de 9 a 13: mismas configuraciones, ventana distinta. |
| 68–69 | Reglas de deduplicación `keep="first"` (+6.64 pp, p=0.1847) y `keep="last"` (+9.96 pp, **p=0.0323**) | `cola_decisiones.md`:88-91 | 2 | Dos poblaciones de evaluación distintas y **una cruza p=0.05**. "Sin deduplicar" es el statu quo ya contado. |
| 70–76 | **El pasivo de las miradas al duelo campeón-vs-baseline**: 12 lecturas en 5 fechas con **7 valores distintos de n** (184/223/228/240/245/248/253) | `GEMELO/SECUENCIAL/DISEÑO.md`:207-225 | 7 | Se cuentan **7, no 12**, aplicando la regla que el propio documento fija: *"dos lecturas de la MISMA cifra no son dos oportunidades de cruzar un umbral"* (:223-225). El proyecto ya contabilizó esto como pasivo de multiplicidad α ∈ [0.09, 0.18] pero **nunca lo trasladó al N del DSR**, siendo el mismo sesgo medido con otro instrumento. La mirada nº11 (n=248, +6.5 pp, p=0.1849) **es la cifra que hoy vive en el README**. |
| | **Subtotal D** | | **32** | |

#### Estrato E — esta corrida (+6 → 82)

| # | Configuración | n | Por qué cuenta |
|---|---|---|---|
| 77–82 | B0, B1, B2, B3, B4, B5 sobre la **ventana de evaluación nueva** (2024-09-02 → 2026-08-28) | 6 | Los seis del estrato A vienen de la corrida de humo 2026-06-01→07-18. Por la regla congelada, ventana nueva ⇒ intentos nuevos. **No cuenta cero.** |

### 1.4 EL NÚMERO DECLARADO

> # N = 82
>
> **25 (A) + 1 (B) + 18 (C) + 32 (D) + 6 (E) = 82**
>
> Declarado el **2026-09-01 a las 01:42 hora de Chile**, commit `06b50a1`,
> **antes de ejecutar el backtest.**

El DSR de esta corrida se computa con **N = 82**, y se reporta además una
**banda de sensibilidad** sobre las cifras que otros documentos del proyecto
declaran, para que el veredicto no dependa de dónde se corte el conteo:

| N | De dónde sale |
|---|---|
| 26 | la declaración vigente más alta que existía antes de esta corrida (`dos_ventanas.md`) |
| 44 | los 43 declarados en prosa (`concentracion.md`:333) + el nº26 |
| **82** | **el declarado aquí — el que gobierna el veredicto** |
| 110 | 82 + los 28 candidatos DUDOSOS de la §1.5, si alguien decidiera contarlos |

### 1.5 Lo que NO se contó, y por qué — declarado, no escondido

Estos 28 candidatos aparecieron en la reconstrucción y **se dejaron fuera
del 82 a propósito**. Se listan para que la exclusión sea auditable, no para
que desaparezca. Contarlos subiría N a 110, y el veredicto se reporta
también a ese N.

| Candidatos | n | Por qué NO se contó |
|---|---|---|
| 6 bloques de 40 filas ("dónde está la ventaja en el tiempo", `GEMELO/DISEÑO.md`:66-78) | 6 | Es una partición descriptiva de UNA serie, no 6 modelos. **Atenuante en contra:** de ahí salió la ventana 15–23-jul que R2 congeló como vara permanente — una decisión SÍ se tomó mirándolo. |
| Predictores de magnitud "predecir 0.0" (MAE 3.423) y "media histórica" (3.395) | 2 | Se leen como hipótesis nula, que la regla excluye (`DISEÑO.md`:377-378). |
| Acierto por cuartil de `confianza_r2` (`GEMELO/DISEÑO.md`:149) | 4 | Descriptivo, sin selección posterior. |
| Desglose por bolsa de la ventana sellada n=228 (`GEMELO/DISEÑO.md`:154-158) | 4 | Se solapa con los intentos 60–63 (mismo desglose, otra n). |
| Recomputo de los 6 pares del WS3 sobre ventana larga con n movido (`DECISIONES.md` §38.3) | 4 | Podría leerse como "la misma ventana larga", ya contada en 10–13. |
| Desglose por bolsa del WS5 (E2 vs E1 × 3 bolsas × 2 ramas) | 6 | `relevo_asiatico.md`:212 afirma que **ninguna decisión se tomó mirándolo**, y el propio documento dice que si alguna se tomara, N sube de 25 a 31. |
| Criterio de "cierre previo rancio" (umbral 5%, 0/223 filas) | 1 | Es un filtro de calidad de dato, no una configuración predictiva. |
| Regresión ventaja-por-ticker ~ retorno (b=+0.60 pp, R²=0.051, n=7) | 1 | Cota auxiliar de sesgo de supervivencia, no un predictor del gap. |

Y estos **no cuentan bajo ninguna lectura**, aunque parezcan
configuraciones: los MDE a 10/25/50 pb × {simétrico, asimétrico}
(parámetros de diseño de potencia); las fronteras Pocock vs O'Brien-Fleming
(elección de función de gasto de α); `BLOQUES_FECHAS = (1, 5, 10)` con
V̂ = máximo (estimador de varianza); el RTL del frente MICRO (mide
*fidelidad* bit a bit al modelo congelado, no ventaja predictiva); y las
tres opciones A/B/C del McNemar (elección de método de test, Δ máximo
0.0003).

### 1.6 Regla de corrección

Si después de correr aparece un intento más, **se agrega como corrección
visible al pie de esta sección, con su fecha**, y el número original de la
§1.4 no se reescribe. Ésa es la regla de la casa para todo registro que ya
fue declarado.

---

## 2. PARÁMETROS DE LA CORRIDA — declarados aquí, antes de correr

Cambiar cualquiera de éstos después de ver los resultados sería elegir la
configuración favorable. Quedan fijados ahora y se sellan en el reporte.

| Parámetro | Valor | De dónde sale |
|---|---|---|
| **Ventana de evaluación** | **2024-09-02 → 2026-08-28** | `backtest/DISEÑO.md` §6: 3 años de datos (`ANIOS_DATOS=3`) menos burn-in de 250 sesiones. Medido: el ^SOX tiene 750 sesiones desde 2023-09-01; la sesión nº250 es **2024-08-29**, así que la primera emisión evaluable es el siguiente hábil, **2024-09-02**. El cierre en **2026-08-28** (viernes) garantiza que toda sesión objetivo tenga desenlace completo — los datos llegan al 2026-09-01, que es un día en curso. Resultado: **509 sesiones del SOX**, ~2 años de emisiones, lo que el §6 especifica. |
| Baselines | B0, B1, B2, B3, B4, B5 | `DISEÑO.md` §3 |
| Burn-in | 250 sesiones | `DISEÑO.md` §6 |
| Ventana de entrenamiento (B1, B3–B5) | 250 sesiones | `DISEÑO.md` §6 / `baselines.py`:31 |
| Re-ajuste | cada 7 días corridos | `baselines.py`:32 |
| **Embargo** | **`EMBARGO_DIAS = 5`, el valor del código sin tocar** | `baselines.py`:56 (López de Prado 2018 cap. 7). Ver el hallazgo H-3 de la §3: el código purga 5 días **corridos**, no 5 jornadas. Se corre con el valor del código y la discrepancia se declara; cambiarlo la víspera del veredicto sería mover el arnés después de haber visto el diseño. |
| Bootstrap | **circular de bloques** (Politis & Romano 1994), bloque **10 días**, **2.000 réplicas** | `DISEÑO.md` §8.5 — CONGELADOS, no se tocan |
| **Semilla del bootstrap** | **20260901** | Parámetro de la corrida desde la Etapa 6.0.0 WS1; se declara aquí y se sella en el reporte. Es la fecha de la corrida: no se probó ninguna otra. |
| **Nivel del IC del Sharpe** | **alpha = 0.05 → IC 95%** | El §8.5 fija bloque y réplicas pero **no** el nivel. Se elige 0.05 y no el 0.10 por defecto del código porque el IC95 es **más ancho** y por tanto **más exigente** para el criterio "el intervalo excluye el cero". Elegir la opción estricta antes de ver el resultado es lo contrario de elegir la favorable. |
| Costos | 25 pb por lado (caso base) con sensibilidad **obligatoria** a 10 / 25 / 50 | `DISEÑO.md` §7 |
| Benchmark | buy-and-hold de **SMH**, obligatorio en toda tabla | `DISEÑO.md` §7 (ajuste GATE B) |
| `N_intentos` del DSR | **82** (banda: 26 / 44 / 82 / 110) | §1.4 de este documento |
| Momentos del Sharpe para PSR/DSR | **primario: skew y curtosis EMPÍRICAS** de la serie de retornos; **secundario: (0, 3)** | La corrección de Lo (2002) existe justamente porque con asimetría negativa y colas gruesas la varianza del Sharpe es MAYOR (`inferencia.py`:80-83): usar los momentos reales es lo exigente. El (0, 3) se reporta al lado sólo para que la cifra sea comparable con el WS2b y el WS3, que lo usaron. Declarado antes de ver un solo Sharpe. |
| Umbral de interpretabilidad del Sharpe | **`MINIMO_DIAS_SHARPE = 60`** | `GEMELO/control_lineal.py`:81. Por debajo de 60 días de retornos, PSR y DSR se reportan **NO INTERPRETABLE**, jamás el número. Y un DSR de 1.0000 significa *"más allá de lo que la doble precisión distingue"*, **no** "certeza" (`Phi` satura sobre z≈8.3). |
| **Holdout (V7)** | **NO SE EVALÚA — queda en cuarentena, sin gastar** | `GEMELO/DISEÑO.md`:462: "evaluado una sola vez". Recurso irreversible; el gatillo no está cumplido. |

### Una mina conocida, declarada y NO republicada

`GEMELO/ventana_larga.py`:18 y :312 emiten la cifra **n=215 con p=0.36** como
tamaño de la ventana del WS2b. Esa cifra está **superada** por la línea base
corregida de `GEMELO/DISEÑO.md` §2.8, que congela **n=223, +4.0 pp,
p=0.4633** bajo la convención `excluir_cero`. El camino de esta corrida **no
pasa por `ventana_larga.py`** y **esta corrida no republica esa cifra**.

Sobre el test que supuestamente la exige: se verificó
`tests/test_ventana_larga.py` y **hoy ninguna aserción fija el 215** — la
línea 186 que se citaba contiene ahora
`assert "NO es point-in-time" in texto`. Es exactamente la deriva de líneas
que la memoria del proyecto ya registra ("las citas por número de línea se
desplazan; reverificar después de escribir"). La corrección del 215 en
`ventana_larga.py` queda como deuda declarada de otro frente, no de éste.

### El ensayo del arnés, declarado antes de correrlo

Antes de la corrida larga se ejecuta un **ensayo sobre un subconjunto
declarado**: las seis baselines sobre la **ventana sellada
2026-07-06 → 2026-08-28**, con el único fin de comprobar que el arnés
reproduce lo esperado — que **B2 reproduce las predicciones realmente
selladas por producción**, comparadas fila a fila contra `senales.db` en
`mode=ro`.

**El ensayo NO suma intentos al N, y la razón se declara ahora, no
después:** mide **fidelidad del arnés** contra filas ya selladas, no ventaja
predictiva, y su resultado no puede seleccionarse — el criterio de paso es
"reproduce el sello", no "gana". Es el mismo criterio con el que la §1.5
dejó fuera el frente MICRO, que reproduce bit a bit el modelo congelado.
**Si el ensayo se usara para elegir entre configuraciones, contaría; no se
va a usar así.**

---

## 3. FASE 2 — VERIFICACIÓN DEL ARNÉS: EL VEREDICTO ESPERA

**Resultado de la fase 2: el arnés tiene TRES fugas o defectos demostrados y
medidos. El veredicto de la Etapa 5.1 NO se emite.** No es una decisión de
prudencia ni una lectura amable de un resultado incómodo: es lo que dice el
criterio congelado.

> **R3** (`GEMELO/DISEÑO.md` §6.2) — *«cualquier fuga detectada por el test
> de causalidad. **Sin discusión y sin excepción**.»*

Y es lo que el propio encargo anticipó: *"Si algo del arnés está roto, ese es
el hallazgo y el veredicto espera."*

### 3.1 Lo que SÍ quedó verde, antes de nada

| Comprobación | Resultado |
|---|---|
| Suite completa | **372 passed** en 81 s (antes de tocar una línea) |
| Anti-look-ahead del **motor de producción** | `python tests/test_motor.py`: **18/18 OK** en 2026-08-02, 2026-06-03 y 2026-03-05 × 6 funciones |
| Regla maestra de emisión | **0 violaciones** en 172 emisiones × 4 bolsas (2026-01-01 → 08-28). Margen mínimo emisión→apertura: XKRX y XTKS **105 min**; ninguna apertura precede ni coincide con su emisión |
| Solo lectura de las bases | `datos.py:55` es el **único** `sqlite3.connect` del paquete y es `mode=ro`; cero `INSERT/UPDATE/DELETE/to_sql` en todo `backtest/`. Sonda sobre `senales.db` real: *«attempt to write a readonly database»* |
| Normalización train-only | `_medias`/`_stds` se fijan en `_entrenar` y sólo se **leen** en `predecir`; escaneo AST: ninguna asignación dentro de un `predecir`. **Sin fuga de normalización** |
| Operaciones no retrospectivas en `backtest/` | Cero `interpolate`, `bfill`, `center=True`, `expanding`, `qcut` o `shift` negativo. `pd.cut` del régimen usa bins **fijos**, no cuantiles globales |
| Purga de features en entrenamiento | Se purgan **etiqueta Y features**: `f_info` es estrictamente anterior a la etiqueta, que ya está recortada al corte |

**La fuga NO está en `motor.py`.** El modelo congelado 4.6.0 pasa su prueba
maestra. Está en la capa de datos del backtest, que es código de
investigación — y por eso esto se puede arreglar sin tocar el motor.

### 3.2 B-1 · BLOQUEANTE — el sentimiento usa juicios de IA que no existían

`backtest/datos.py` corta el sentimiento por **`titulares.fecha`**, la fecha
de **publicación del titular**. Pero el juicio que se usa como feature no es
el titular: es el análisis de Claude, que vive en `analisis` con su propio
`analizado_en` — y **ese campo no se consulta nunca**.

Medido por mí sobre `noticias.db` en `mode=ro`, no citado del auditor:

| Cifra | Valor |
|---|---|
| Análisis totales | 5.094 |
| Producidos **después** de las 22:15 UTC de su día de publicación | **3.407 (66.9 %)** |
| Producidos en un día calendario posterior | 2.439 (47.9 %) |
| Rezago máximo publicación → análisis | **320 días** |
| **Primer análisis de IA que existe en el sistema** | **2026-07-04T16:30:47Z** |
| Rango de fechas de titulares | 2025-09-09 → 2026-08-31 |

**La consecuencia sobre la ventana declarada es total.** La ventana empieza
el 2024-09-02 y el primer juicio de IA del sistema es del 2026-07-04: durante
**casi 22 de los 24 meses**, B4 y B5 se alimentan de sentimiento construido
**íntegramente** con juicios que no existían en ninguna parte el día de la
emisión. Eso es look-ahead de manual.

El código lo *declara* — marca esas filas como `grado B` — pero **declararlo
no lo neutraliza**: `grado_B_pct` es una columna informativa y **ninguna
métrica excluye grado B**. Y hay dos agravantes que el grado ni siquiera
cubre: `buzz` sale del mismo join y **no tiene grado ninguno** (un titular
sólo entra al buzz si fue analizado, y el 66.9 % lo fue tarde), y
`sentimiento_sector` promedia sobre todos los tickers mezclando grado A y B
en silencio.

### 3.3 B-2 · BLOQUEANTE — la guarda `ErrorLookAhead` es tautológica

Los dos únicos sitios donde se llama a la guarda en el camino de ejecución
son `backtest/baselines.py:182-184` y `:314-315`. Ambos tienen la misma
forma:

```python
corte = serie[serie.index.date <= fecha]   # recorta por <= fecha
validar_sin_futuro(corte, fecha)           # y comprueba que max() <= fecha
```

`validar_sin_futuro` revienta si `df.index.max().date() > fecha`, sobre un
frame que **acaba de recortarse con ese mismo predicado**. La condición de
disparo es **inalcanzable por construcción**. Medido con instrumentación
sobre un walk-forward completo: **401.184 invocaciones, cero capaces de
disparar**.

Peor: **una fuga real desplaza VALORES, no el índice.** Inyectando la fuga
canónica (`shift(-1)`) en distintas features, la guarda **no disparó en
ningún caso**; lo que detecta la fuga es el test de invariancia al truncado,
no la guarda. Y ese test —
`test_truncar_futuro_no_cambia_predicciones`— ejercita **una sola fecha y
tres baselines (B1, B2, B3)**. Comprobado: una fuga inyectada en `roca_pct`
evaluada con B1/B3 sale **invariante: True**. Es decir, **las cinco features
exclusivas de B4 y B5 —`roca_pct`, `upstream`, `sentimiento`,
`sentimiento_sector`, `buzz`— son invisibles para toda la suite actual**, y
son exactamente donde vive B-1.

Esto es la regla de la casa aplicada al propio proyecto: *una verificación
que usa el mismo mecanismo que produjo la cifra no es una verificación.* La
guarda validaba su propio recorte.

### 3.4 B-3 · BLOQUEANTE — el mismo desenlace cuenta hasta 8 veces

`emision.emisiones()` emite todos los días hábiles de Chile;
`sesion_objetivo()` devuelve la próxima apertura. En feriados largos,
**varias emisiones consecutivas apuntan a la MISMA sesión**, y `motorbt`
escribe una fila por emisión con el **outcome idéntico repetido**.

Medido por mí sobre la ventana declarada (2024-09-02 → 2026-08-28):

| | |
|---|---|
| Filas (emisión × ticker) con sesión objetivo | 4.160 |
| Pares (ticker, sesión objetivo) **únicos** | 3.897 |
| **Filas que son desenlaces duplicados** | **263 (6.3 %)** |
| Multiplicidad | 139 pares ×2 · 17 ×3 · 14 ×4 · 6 ×5 · 2 ×6 · **2 ×8** |
| Peores | `2330.TW` 2025-02-03 y 2026-02-23, **ocho emisiones cada una** |

No es fuga de futuro: es **contaminación de la unidad de observación**, y
descarrila los criterios igual de rápido. `rank_ic_diario` agrupa por fecha
de emisión, así que calcula hasta 8 ICs "diarios" contra los mismos gaps;
la n de Wilson cuenta el mismo acierto 8 veces y el intervalo sale
artificialmente angosto; `retornos_cartera` mete el mismo `capturable_pct`
como 8 días distintos de P&L. Y **`t_newey_west` usa `lag=5`, que no cubre
un bloque de 8 duplicados perfectos**: el t-stat del veredicto escalonado
sale inflado justo en el número que decide.

### 3.5 S-1 · SERIO — el embargo declarado no es el embargo aplicado

`baselines.py:313` hace `corte = fecha - timedelta(days=embargo_dias)`. El
comentario del propio archivo dice *"5 **días hábiles** cubren una semana
completa"* y la ayuda del CLI dice *"**jornadas** purgadas"*, pero
`timedelta(days=5)` son **5 días corridos**.

Sesiones realmente purgadas, medidas por bolsa: **mediana 3, mínimo 0
(feriado largo en XTKS), máximo 5**. Y el agravante que lo convierte en un
parámetro oculto: `DIAS_REAJUSTE = 7` días corridos hace que el reajuste
caiga **siempre el mismo día de la semana**, fijado por `--desde`. Dos
corridas idénticas salvo por el día de arranque tienen embargos efectivos
de **3 y de 5 sesiones**:

```
inicio lunes:  sesiones XNYS purgadas por reajuste = [2, 3, 3, 3, 3, 3, 3, 3]
inicio viernes: sesiones XNYS purgadas por reajuste = [5, 5, 5, 5, 5, 5, 5, 5]
```

El reporte sella `"embargo_dias": 5`, una cifra que con arranque en lunes
**no describe lo que ocurrió**. **La corrida no es reproducible a partir de
sus propios parámetros sellados** — que es justamente lo que sellarlos debía
garantizar.

Se corrió con el valor del código, como se declaró en la §2. Cambiarlo la
víspera habría sido mover el arnés después de ver el diseño.

### 3.6 S-2 · SERIO — B2 queda fuera del embargo y compite contra rivales penalizados

`B2Produccion.predecir` llama `motor.prediccion_apertura_al(fecha)` directo;
el embargo vive en `_BaselineAjustada`, del que heredan B1, B3, B4 y B5. **B2
no pasa por ahí en ningún punto.** Y no es que "no ajusta nada":
`motor.betas_al(fecha)` estima una regresión rodante de 120 sesiones que
**termina en `fecha`**, o sea toca la frontera exacta que el embargo existe
para purgar.

Resultado: el veredicto escalonado compara **B2 vs B1** y **B3 vs B2** con
reglas asimétricas — B1 y B3 entrenan con 3 a 5 sesiones menos de historia,
B2 con todas. El sesgo apunta a favor de B2 justo en la capa que pregunta
*"¿el contagio del SOX agrega sobre la inercia propia?"*. Es una decisión de
diseño pendiente de declarar, no un bug; pero hoy **no está declarada en el
reporte**, y por tanto esas dos capas no son veredictos.

### 3.7 S-3 · SERIO — desde el CLI, una corrida se autoproclama veredicto

`estado_gatillo` es un diccionario que **provee quien llama**: nada lo
computa ni lo verifica, y el `argparse` de `motorbt` **no expone bandera
alguna para él**. Por lo tanto `python -m backtest.motorbt --etiqueta 5.1 …`
cae en la rama sin gatillo y estampa *"✅ CORRIDA DE VEREDICTO — Etapa 5.1 ·
Gatillo cumplido"* **sin que nadie haya verificado nada**, y sin mencionar el
holdout.

**Éste es un defecto que introduje yo esta noche** al añadir los tres
estados del sello, y lo digo porque es exactamente el tipo de cosa que este
expediente existe para no dejar pasar. El arreglo correcto es que
`estado_gatillo` se **calcule** (N de verificaciones vivas + número de
etiquetas de régimen distintas + la fecha de los 3 meses) en vez de
recibirse, y que la rama de veredicto pleno sea inalcanzable sin gatillo
computado. Queda como deuda declarada, no ejecutada esta noche: tocar eso
ahora sería arreglar el arnés en medio de la corrida.

### 3.8 S-5 · SERIO — la fuente no es point-in-time, y ahora está MEDIDO

`FuenteCongelada.__enter__` descarga con `yf.download(period="3y")` **el día
de la corrida**. "Congelada" significa congelada *dentro* de la corrida, no
congelada *a la fecha de emisión*.

El ensayo del arnés lo midió, y el resultado es peor que "deriva":

| B2 vs los sellos reales (ventana sellada 2026-07-06 → 08-28) | |
|---|---|
| Predicciones comparadas | 260 |
| Diferencia **mediana** | **0.03 pp** |
| Diferencia p90 | 0.24 pp |
| Diferencia **media** | **0.166 pp** |
| Diferencia **máxima** | **5.30 pp** |
| Media **excluyendo la peor fecha** | **0.070 pp** (máx 0.61 pp) |

**Toda la discrepancia vive en UNA fecha: el 2026-08-28**, donde la
diferencia media es 3.62 pp y **el signo se invierte en las ocho acciones**.
La causa, verificada contra la fuente con rango explícito de fechas:

```
^SOX  : 08-24, 08-25, 08-26, 08-27,        08-31   ← falta el 28
SMH   : 08-24, 08-25, 08-26, 08-27,        08-31   ← falta el 28
^GSPC : 08-24, 08-25, 08-26, 08-27,        08-31   ← falta el 28
NVDA  : 08-24, 08-25, 08-26, 08-27, 08-28, 08-31
```

**Yahoo borró la sesión del 2026-08-28 para los índices y el ETF.**
Producción la vivió y la selló: el snapshot del 28-ago tiene
`sox_fecha = 2026-08-28` y `sox_usado_pct = -3.47`. Hoy esa barra no existe,
así que el backtest reconstruye la emisión de ese día con el SOX del 27
(**+2.33 %**) y predice al alza donde producción, que vio los datos reales,
predijo a la baja.

Dos consecuencias que hay que decir enteras: **(1)** la barra desaparecida es
del **benchmark obligatorio SMH**, así que la comparación del §7 del diseño
también se computa sobre una serie a la que le falta una sesión; **(2)** ésta
es la primera vez que la limitación *"no es point-in-time"* —hasta ahora
declarada en prosa en `ventana_larga.md`— aparece **medida sobre el camino
del backtest**, y su magnitud no es un decimal: **invierte el signo de una
sección transversal completa**.

### 3.9 B-4 · el McNemar canónico del proyecto desbordaba — CORREGIDO

Apareció al correr, no al auditar: `mcnemar_exact` de
`.claude/skills/estadistica-evaluacion/scripts/evaluacion.py` **reventó con
`OverflowError`** sobre las 4.151 filas del backtest.

La rama exacta calculaba `sum(comb(n,i)) / 2.0**n`. Ese denominador es un
`float` y **desborda en n = 1024** (2¹⁰²⁴ > 1.8·10³⁰⁸). El docstring
declaraba *"exacto hasta n = 2000; por encima usa la aproximación normal"*,
pero **todo el tramo 1024 ≤ n ≤ 2000 no caía en el fallback: reventaba**.
Ningún uso anterior había llegado a esa escala — los pares discordantes de
la ventana sellada rondan los 130, y `backtest/linea_base.py` usa su propia
χ² con corrección de continuidad, así que nunca se tocó el techo.

**Corregido en el código, no en prosa** (regla de la casa: una retractación
en prosa no es una retractación). La suma ahora va en espacio logarítmico
con `lgamma`, que no desborda para ningún n representable. **El umbral
declarado de 2000 no se movió: lo que se corrigió es que ahora se cumple.**
Verificado: las dos anclas históricas del `_self_test` siguen reproduciendo
(b=67,c=55 → 0.3193; b=72,c=56 → 0.1847), n=1024 y n=2000 ya devuelven
número, y el `_self_test` completo del módulo queda en verde.

### 3.10 Zonas ciegas que quedan abiertas

1. **`titulares` no tiene `available_at`.** El esquema es
   `(id, fecha, fuente, titular, url, tickers)`: **ninguna columna registra
   cuándo la fila entró a la base**. Con `analizado_en` se puede acotar el
   rezago del *juicio*; el rezago de la *ingesta* **no es medible con lo que
   hay**, y `buzz` depende enteramente de él.
2. **No existe un archivo histórico de las descargas de Yahoo**, así que no
   se puede medir cuánto de un resultado viene de revisiones posteriores —
   sólo acotarlo con la auditoría B2 contra sellos, como se hizo arriba.
3. **Fuga de especificación, declarada y no detectable:** las 16 features,
   los umbrales ±1 % del régimen, `VENTANA_ENTRENAMIENTO=250`,
   `DIAS_REAJUSTE=7`, `EMBARGO_DIAS=5`, `TOP_LONG=3` y los terciles de la
   cartera los eligió alguien que ya había visto esta ventana de datos.
   Ninguna prueba lo detecta. Queda escrito.
4. **`FuenteCongelada` muta `motor._datos_crudos` y `motor._cache` a nivel de
   módulo** y no hay guarda que impida correr un backtest en el mismo proceso
   que un sellado. En procesos separados es inocuo; no se probó lo otro.

### 3.11 Lo que hay que arreglar antes de que exista un veredicto

En este orden, y el primer entregable de cada punto es el **test**, no el
arreglo:

1. **B-1** — `SentimientoPIT` tiene que cortar por
   `min(titulares.fecha, analisis.analizado_en)` contra el instante de
   emisión (22:15 UTC), no por fecha de publicación. Con la base actual eso
   deja a B4/B5 **sin sentimiento antes del 2026-07-04**, y ésa es la verdad.
   `buzz` necesita el mismo corte y un grado propio. La alternativa honesta,
   si se prefiere no tocar la feature, es restringir toda ventana de
   veredicto a `>= 2026-07-05` y **excluir de las métricas** las filas de
   grado B en vez de sólo contarlas — pero eso reduce la ventana a ~40 días
   y hace que el Sharpe anualizado vuelva a ser NO INTERPRETABLE.
2. **B-2** — parametrizar `test_truncar_futuro_no_cambia_predicciones` sobre
   **B0–B5 × ≥10 fechas** con `noticias.db` sintética poblada, y añadir la
   contraprueba `shift(-1)` como test permanente: *que el test pueda fallar
   es parte del test*. Después, o `validar_sin_futuro` recibe la serie **sin
   recortar**, o deja de llamarse guarda.
3. **B-3** — deduplicar por `(ticker, sesion_objetivo)` antes de evaluar, o
   declarar la sesión objetivo como unidad de observación en
   `rank_ic_diario`, `hits_condicionados` y `retornos_cartera`. No es
   cosmético: cambia n, cambia Wilson y cambia el Sharpe.
4. **S-1** — contar **sesiones del calendario**, no días corridos, y sellar
   en el reporte las sesiones efectivamente purgadas (mín/mediana/máx), no el
   nominal.
5. **S-2** — declarar en el reporte que B2 es objeto de auditoría y no
   competidor con reglas simétricas, o aplicarle el mismo embargo.
6. **S-3** — computar `estado_gatillo` en vez de recibirlo, y exponerlo en el
   CLI.
7. **S-5** — subir la auditoría B2-vs-sellos del pie de página al encabezado
   de todo reporte, que es donde vive una limitación de primer orden.

### 3.12 El holdout: intacto

**V7 queda NO EVALUABLE y el holdout NO se gastó.** Además hay una razón de
fondo que se descubrió al auditar y que conviene que Nicolás sepa antes de
decidir nada: **no existe hoy un holdout material** — no hay split,
constante de fecha, archivo ni tabla que reserve datos. La cuarentena es
**procedimental**, como el propio `preregistro_ws5.md` dice, y ese mismo
documento reconoce que la decisión de qué configuraciones correr *"se midió
sobre la ventana completa, holdout incluido"*.

O sea: V7 no sólo no se evaluó — **hoy no es evaluable**, y lo que se llama
holdout ya está tocado por la especificación. Decirlo es correcto; lo que no
se puede es marcarlo aprobado ni "intacto" por autodeclaración. Construir un
holdout de verdad es trabajo previo al veredicto, no parte de él.

---

## 4. FASE 3 — EL VEREDICTO: NO HAY VEREDICTO, Y SE DICE ASÍ

**Corrida:** `backtest/resultados/20260901-061708-5.1-invalidada-por-fuga/`
(`resumen.md` versionado, `veredicto.md`, `veredicto.json`, seis CSV de
predicciones). Ventana **2024-09-02 → 2026-08-28**, **520 días** de
emisión, **4.151 pares** emisión-desenlace por baseline, 9 descartes sin
datos. Duración de la corrida: **20 minutos**.

### 4.1 El veredicto por criterio

| Criterio | Veredicto | Razón |
|---|---|---|
| **V1** — McNemar vs "siempre al alza" | PASA **sobre datos con fuga — no vale** | B2 +13.55 pp (69.0 % vs 55.4 %, Wilson95 [67.5, 70.4], p≈0), B3 +12.96, B4 +12.19, B5 +12.33; B1 **−1.90 pp** (p=0.0003, pierde contra la constante) |
| **V2** — CRPS vs el campeón | PASA **sobre datos con fuga — no vale** | ninguna capa mejora al campeón con IC que excluya el cero salvo por márgenes que la contaminación explica |
| **V3** — cobertura del 80 % en [76, 84] | PASA **sobre datos con fuga — no vale** | B1 82.6 %, B3 83.5 %, B4 83.1 %, B5 83.2 % dentro; **B2 92.1 %** fuera, coherente con el 89.5 % sellado |
| **V4** — MAE menor que el campeón | **NO PASA** | ninguna capa baja del 1.543 pp de B2 en ventana (B3 1.562, B4 1.575, B5 1.576) |
| **V5** — DSR ≥ 0.95 con N = 82 | **NO PASA** | **DSR = 0.0000** en las seis baselines y en los cuatro valores de N |
| **V6** — superar comprar SMH a 25 pb | **NO PASA** | SMH **+137.1 %**; la mejor cartera del conjunto, **−91.4 %** |
| **V7** — holdout | **NO EVALUABLE** | **deliberadamente no gastado**; y además hoy **no existe** un holdout material |
| **R1** — el control lineal le gana | **NO EVALUABLE** | R1 está escrito para un retador; aquí hay seis baselines, no un retador |
| **R2** — la ventaja sobrevive sin 15–23 jul | PASA | la ventana de 6 fechas es marginal sobre 520 días; no es donde vive nada |
| **R3** — cualquier fuga detectada | **NO PASA** | **tres defectos demostrados y medidos. Sin discusión y sin excepción.** |
| **Veredicto final del §8** | **NO AGREGA VALOR** | ninguna capa cumple las tres condiciones conjuntas |

**R3 gobierna.** Con fuga demostrada, ningún otro criterio de esta corrida
es un veredicto: V1 a V6 son referencia contaminada y nada más. **El
veredicto de la Etapa 5.1 espera.**

### 4.2 V6 con su barrido obligatorio de costos

**Comprar SMH y no hacer nada: +137.1 % acumulado, Sharpe 1.32, MDD −32.6 %.**

| B | LS 10 pb | LS 25 pb | LS 50 pb | Sharpe LS 25 pb [IC95 bootstrap circular] |
|---|---|---|---|---|
| B0 | −58.8 % | **−91.4 %** | −99.4 % | −5.44 [−7.00, −3.93] |
| B1 | −63.3 % | **−92.3 %** | −99.4 % | −6.02 [−7.51, −4.65] |
| B2 | −79.1 % | **−95.6 %** | −99.7 % | −6.98 [−8.38, −5.74] |
| B3 | −84.6 % | **−96.8 %** | −99.8 % | −7.99 [−9.30, −6.77] |
| B4 | −82.4 % | **−96.3 %** | −99.7 % | −8.08 [−9.54, −6.82] |
| B5 | −78.9 % | **−95.6 %** | −99.7 % | −7.67 [−9.08, −6.46] |

Intervalos por **bootstrap circular de bloques** (Politis & Romano 1994),
bloque 10 días, 2.000 réplicas, semilla **20260901**, IC 95 % — todo
declarado en la §2 antes de correr y sellado en el reporte. **Ningún
estimador puntual sin intervalo, y ningún intervalo cruza el cero: son
negativos con certeza estadística.**

El diseño advertía *«una estrategia que sólo vive con 10 pb no aprueba»*.
Aquí **no vive ninguna ni con 10 pb**.

### 4.3 El conteo de intentos no era la restricción, y eso también se dice

El DSR sale **0.0000** para las seis baselines a N = 26, 44, 82 y 110. Con
Sharpe entre −5.4 y −8.1, **ningún valor de N habría cambiado nada**. El
trabajo de reconstruir el conteo desde 25 hasta 82 no fue el que decidió el
resultado — y se declaró igual, antes de correr, porque su valor no depende
de que termine siendo decisivo. Si el Sharpe hubiera salido alto, ese
número era la única defensa contra leerlo como habilidad.

Los 520 días superan `MINIMO_DIAS_SHARPE = 60`, así que aquí el DSR **sí es
interpretable** y no hay que escribir NO INTERPRETABLE. (`V_intentos` =
1.1997; umbral deflactado `SR0` = 2.6944 a N = 82.)

### 4.4 Lo que sí se aprende, y es lo más importante de la noche

La contaminación conocida va en la dirección de **favorecer** al modelo, y
aun así:

| | |
|---|---|
| Acierto direccional del gap (B2) | **69.0 %** [67.5, 70.4] vs base 55.4 % — **+13.6 pp**, McNemar p ≈ 0 |
| Cartera long-short **bruta, sin un solo punto básico de costo** | **−40.7 %** acumulado, Sharpe **−1.08** |
| Cartera long-only bruta | −19.8 %, Sharpe −0.24 |
| Arrastre puro de costos a 25 pb/lado sobre 520 días | −92.6 % |

**El modelo acierta la dirección del gap siete de cada diez veces y la
cartera igual pierde el 41 % antes de tocar un solo punto básico de
costos.** No es un problema de costos: los costos rematan algo que ya venía
perdiendo. Es exactamente la distinción que el proyecto tiene escrita desde
la Etapa 4.6 —¿la señal EXISTE? ¿es CAPTURABLE?— medida por primera vez
sobre dos años de walk-forward: **el gap existe y no es capturable.**
Entrar en la subasta de apertura ya es tarde; el gap ya ocurrió.

Esto **no es un veredicto**, porque R3 lo prohíbe. Es la dirección en la que
el arreglo del arnés tendría que ser sorprendente para cambiar algo.

### 4.5 B-3 medido: la contaminación va al revés de lo que supuse

Releyendo las MISMAS filas con los desenlaces duplicados colapsados por
`(ticker, sesión objetivo)` — 4.151 → 3.888 filas:

| B | ventaja pp | IC medio | t(NW) | MAE |
|---|---|---|---|---|
| B1 | −1.90 → −1.78 | −0.0313 → −0.0399 | −1.48 → −1.91 | 1.847 → 1.784 |
| B2 | 13.55 → **14.29** | 0.2328 → 0.2457 | 11.21 → **11.65** | 1.543 → 1.470 |
| B3 | 12.96 → 13.53 | 0.2221 → 0.2436 | 9.77 → 11.03 | 1.562 → 1.486 |
| B4 | 12.19 → 12.83 | 0.2213 → 0.2403 | 9.92 → 10.93 | 1.575 → 1.495 |
| B5 | 12.33 → 12.96 | 0.2026 → 0.2244 | 8.79 → 10.05 | 1.576 → 1.496 |

**La auditoría predijo que los duplicados INFLABAN el t-stat. Medido, hacen
lo contrario:** al deduplicar, la ventaja sube, el IC sube y el t(NW) sube
en todas las capas. El defecto es real —la unidad de observación está mal y
hay que arreglarla igual— pero **su dirección no era la que supuse, y
decirlo es parte del trabajo**. Arreglar B-3 no va a rescatar el resultado
económico: lo empeora un poco más.

### 4.6 Lo que este frente NO hizo, dicho explícitamente

- **No se tocó ningún criterio** de `backtest/DISEÑO.md` ni de
  `GEMELO/DISEÑO.md`. V1–V7 y R1–R3 están como estaban.
- **No se tocó** `motor.py`, `senales.py`, `snapshot.py`, `universo.py`,
  `.env` ni los timers. `senales.db` y `noticias.db` se abrieron **sólo** en
  `mode=ro`.
- **No se reescribió ninguna fila sellada.** La corrida de humo
  `20260726-032635-humo-legacy` quedó intacta con su errata al pie.
- **No se gastó el holdout.**
- **No se commiteó ni se pusheó nada.**
- La suite quedó en **409 passed, 1 failed**, y el fallo **no es de este
  frente**: `tests/test_gemelo_datos.py::test_gemelo_no_escribe_en_ninguna_base`
  cae porque `GEMELO/bifurcaciones.py` —archivo nuevo, sin commitear, de
  otro frente de esta misma corrida— abre `sqlite3` directamente en vez de
  pasar por `backtest.linea_base`. Es una violación real del invariante de
  aislamiento del GEMELO y se deja señalada para su dueño, no arreglada por
  encima.
