# Re-dictamen de la corrida 11 sobre las cifras RE-CORRIDAS

**8-sep-2026, 23:37 hora de Chile (2026-09-09T02:37:47Z), leído de `date`.**
Bloque 1 de la corrida 12. Juzga el estado ACTUAL de cada cifra, no la primera versión.
Dictaminó el `estadistico-adversario`; el orquestador lo archiva tal cual (sección «Aplicación» al final, agregada por el orquestador).

**Objeto del dictamen (sha256 verificado con `sha256sum GEMELO/resultados/dictamen_12/api_congelada/*.json`):**

| archivo | sha256 |
|---|---|
| `rieles.json` | `1de2a3a540303c8ae92bccacef30bd6821b7c394b884cf2bb14b5ebfb61107ad` |
| `dinero_cuenta.json` | `dd265401047eb17c5678837c967ef586a4b9aadee1e125782b34a4312eb24b90` |
| `dinero_universo.json` | `9ea50aa97cdf066bbd6ad5a1d6f8dad39834b9c9ec04a7e3e75a3ce9ed5415db` |

**Reproducción del payload.** `from api.main import _estado_rieles; _estado_rieles()` en proceso da
un JSON **idéntico** al congelado (`json.dumps(sort_keys=True)` comparado: `True`). Lo que juzgo es
lo que sirve la máquina, no una copia.

**Las 18 exigencias del dictamen 11: aplicadas en el ejecutable, verificadas una por una.**
A1 (`instrumento_dinero.md` §Calibración, declarada a posteriori), A2 (columnas MDE80 pp/sem y pp/año),
A3 (fila T=156), A4 (ρ AC1 mediana 0,000 [−0,190, +0,164]), A5 (potencia cerrada al α real),
A6/C6 (2,704 contra 2,336), A7 (regla escrita, **sólo prosa: sin test que fije `BLOQUE_SEMANAS`**),
B1 (§3b R2), B2 (§3 cuál IC está calibrado y con qué k), B3 (§3c Σ por día y el 2/0), B4 (§3c «otro
estimando»), B5 (§4 cablear = intento), C1 (§1b K=20 con banda), C2 (§1 el tope del 1 % nombrado),
C3 (§4b nota a 156 semanas), C4 (cobertura del IC de la sd medida), C5 (`preregistro_dinero.md` §7,
errata fechada 8-sep). **Todas están en los artefactos. Ninguna llegó al serializador de la API:**
ahí es donde se pierden C1, C3, C4 y A5.

---

## A. Riel de medición (`rieles.json`, bloque `Riel de medición`)

Verificado con `venv/bin/python -c "import cifras; print(cifras.sellada())"` — los 16 campos
coinciden dígito a dígito. McNemar exacta re-verificada con el módulo canónico
(`evaluacion.mcnemar_exact`): 72/49 → 0,0451; 69/37 → 0,0024; 48/43 → 0,6752; 45/31 → 0,1354.

| cifra | valor que sirve la máquina | dónde | verdicto | etiqueta exigida / razón |
|---|---|---|---|---|
| acierto modelo | 67,6 % [61,5, 73,3] Wilson | `cifras[0]` | **se sostiene** | — |
| acierto base | 58,0 % [51,6, 64,1] Wilson | `cifras[1]` | **se sostiene** | denominador honesto: «siempre al alza» sobre las mismas filas |
| ventaja | +9,7 pp, IC95 clúster de día [−7,2, +26,6], cruza cero | `cifras[2]` | **se sostiene** | manda el IC de día; el McNemar de filas es secundario |
| ganancia de MAE | +0,4547 pp, t de clúster [−0,087, +0,996], cruza cero | `cifras[3]` | **se sostiene** | — |
| McNemar de filas | p = 0,0455 con su caveat | `mcnemar_p_filas` | **se sostiene** | el caveat ya está y nombra ICC 0,39 / DEFF 3,55 |
| cobertura 80 % | 92,9 % | `cobertura_80_pct` | **se sostiene con etiqueta** | viaja **sin intervalo**: Wilson de 221/238 falta (V3 se juzga contra [76, 84]) |
| n 238 / 34 días / ICC 0,392 / DEFF 3,55 / n_ef 67 | — | `muestra`, `icc`, `deff` | **se sostiene** | falta la etiqueta de **un solo régimen** (39 snapshots): el bloque no la lleva |
| R2 del campeón | «+0,5 / −1,0 / −1,9 pp al 31-ago … bajo la regla firmada **NO está recomputada**» | `que_lo_mata` | **se retira la cláusula** | **es falsa desde el 8-sep**: el bloque 4 la recomputó, +2,6 pp, n=194, 28 días, t de clúster [−15,7, +20,9], permutación 0,821, exacta 0,6752 |

## B. Instrumento del riel de dinero (`instrumento_dinero.md/.json`, servido vía `potencia`)

Los seis Wilson que revisé reproducen exactos con `evaluacion.wilson_ci`: 172/2000 → [0,0745, 0,0991];
127/2000 → [0,0536, 0,0750]; 1873/2000 → [0,925, 0,946]; 1699/2000 → [0,833, 0,865]; 1566/2000 → [0,764, 0,801].
**Unidades:** δ y σ en pp por semana; T en semanas; proporciones sobre 2.000 réplicas iid (Wilson es
el estimador correcto acá: las réplicas del simulador SÍ son independientes).

| cifra | valor que sirve la máquina | dónde | verdicto | etiqueta exigida / razón |
|---|---|---|---|---|
| «discrimina» | detección 0,136 / 0,344 / 0,790 contra 0,046 bajo la nula | `.md` §Veredicto | **se sostiene con etiqueta** | «discrimina **y NO está calibrado**» en la misma frase, siempre |
| tamaño bilateral | 0,086 [0,074, 0,099] (52 sem); 0,064 [0,054, 0,075] (156) | `.json` calibración | **se sostiene** | es el hallazgo firme de la corrida |
| cobertura IC de la media | 0,914 / 0,933 / 0,936 | ídem | **se sostiene** | — |
| cobertura IC de la **sd** | 0,783 / 0,821 / **0,850 [0,833, 0,865]** | ídem | **se sostiene** | es la cifra que mata la etiqueta «95 %» de la API |
| MDE80 | 1,05 / 0,74 / **0,61** pp/semana | `.json`, y citado en `potencia.nota` | **se sostiene con etiqueta** | (i) está calculado a **z = 1,96 (α nominal)**, no al α real que la fila de al lado publica — al α real de 52 sem daría **0,96**; (ii) **viaja sin intervalo** aunque σ tiene banda: con la banda entre sorteos [1,911, 4,016] el MDE80 a 52 sem es **[0,74, 1,56]** |
| «≈ 55 pp/año» | 52 × 1,05 | `.json` `mde80_pp_anio_aprox` | **se sostiene con etiqueta** | es **suma aritmética**, no capitalización: `1,0105^52 − 1 ≈ +72 pp`. Decir cuál de las dos |
| σ ancla | 2,704, IC de la mediana [2,477, 2,895], banda [1,911, 4,016] | `.md` §Qué se prueba | **se sostiene con etiqueta** | manda la **banda**, no el IC de la mediana; un solo régimen (SMH +253 % en la ventana) |
| ρ medido | AC1 mediana 0,000 [−0,190, +0,164] | `.md` | **se sostiene** | — |
| `potencia.tipo_intervalo` | «bootstrap circular de bloques de semanas, **95 %**» | `api/main.py:1001` | **SE RETIRA** | la etiqueta miente: cobertura medida **0,850** a 156 semanas. El `.json` de la cuenta lo dice (`sigma_dif_semanal.advertencia`) y `_potencia_desde_artefacto` **descarta ese campo** |
| `potencia.nota` | «Con **esta σ**, 52 semanas … MDE80 del bloque 1» | `api/main.py:1009` | **SE RETIRA la atribución** | «esta σ» es 2,336; el MDE80 de 1,05 se computó con σ = 2,704. Con la σ servida el MDE80 a 52 sem es **0,91** |
| `potencia.nota` | «el simulador **validado**» | `api/main.py:1007` | **SE RETIRA la palabra** | el `curador-epistemico` retiró «validado» el 8-sep y la corrección no llegó al ejecutable: sobrevive en `api/main.py:1007`, `dinero/cuenta_papel.py:670`, `dinero/resultados/cuenta_papel.md:190` y `dinero/preregistro_dinero.md:240` |

## C. Cuenta en papel v2 (`dinero_cuenta.json`, y el escalar que sale por `rieles.json`)

| cifra | valor que sirve la máquina | dónde | verdicto | etiqueta exigida / razón |
|---|---|---|---|---|
| **fricción del juego activo** | **12,5** (escalar pelado) | `rieles.json` `cuenta_en_papel.comisiones_pct_del_aportado_juego_activo`; `api/main.py:969-982` | **SE RETIRA como cifra que viaja sola** | No es la mediana: es **la semilla de la página** (`conservador` a 5 pb = 12,4992 → `round(...,1)`). La bitácora dice 12,4 % = **mediana de 20 semillas**. Son dos objetos distintos. Viaja **sin intervalo** (violación de la regla 1) y **sin denominador ni período** (es 62,50 USD sobre 500 USD aportados a lo largo de **156 semanas**; anualizado son 4,2 %/año, y sobre el valor final 5,0 %). Debe viajar el objeto: **mediana 12,4 %, banda entre semillas [6,35, 13,2], K=20, 5 pb, 156 semanas, sobre 500 USD aportados** |
| banda entre semillas | conservador [6,35, 13,2]; medio 26,7 [14,56, 28,7]; agresivo 19,0 [17,98, 20,16] | `barrido_semillas` | **se sostiene con etiqueta** | es **percentil entre sorteos de señal**, no un IC de muestreo, y con K=20 los p2,5/p97,5 son prácticamente el mín-máx (6,26 / 13,23). Decirlo. La mediana 12,4 queda **en el borde superior de su propia banda** |
| «51 de 480 IC excluyen el cero» | 0,1062, **Wilson95 [0,082, 0,137]** | `barrido_semillas.ic_excluye_cero` | **SE RETIRA el Wilson** | intervalo **iid sobre unidades agrupadas**: 24 comparaciones por semilla comparten sorteo, calendario, instrumentos y la misma semilla de bootstrap. La unidad de replicación es la **semilla** (20), no la comparación (480). Mandato «clúster siempre». El conteo 51/480 se sostiene como descriptivo |
| σ de la diferencia semanal | 2,3362, IC [1,9952, 2,6686] | `sigma_dif_semanal` | **se sostiene con etiqueta** | punto de **UN sorteo** (semilla 20260906): no hay banda entre semillas para σ mientras la fricción varía 6,3–13,2 % entre semillas. Su IC **no es un 95 %** (cobertura 0,850). El artefacto lo dice; la API lo borra |
| IC de cada `contra.{SMH,XSD}` | `alpha: 0.05`, `ic_lo/ic_hi`, `cruza_cero` | `juegos[*]` | **se sostiene con etiqueta** | el `alpha: 0.05` del objeto es **nominal**; el α real medido a 156 semanas es **0,064 [0,054, 0,075]**. El `.md` lo aclara en prosa; el objeto que la API sirve, no |
| «ningún juego muestra ventaja positiva que excluya el cero contra SMH» | 5 ✓ de 24, todos negativos | `.md` §4b/4c | **se sostiene** | y la negativa a llamarlo tasa de falsos positivos es correcta: la nula no es cero |
| gate de invariancia | INVARIANTE, 25 cortes | `reconstruccion.gate_invariancia` | **se sostiene con etiqueta** | «INVARIANTE ≠ sin fuga»: contra una fuga de 1 día por `precios_ref` la veían **2 de 11** cortes; G3 pendiente. La etiqueta ya está en el `.json` y en el `.md` |
| cobertura causal | 28,0 % / 84,5 % (antes 0,0 % / 0,0 %) | `cobertura_causal.json` | **se sostiene sin intervalo** | es un **censo de líneas**, determinista: no lleva barra de error. Etiqueta: no mide ausencia de fuga |
| sesgo de la sonda | 57,8 % positivas, +2,20 pp de magnitud media, n=24.882 | `sesgo_de_la_sonda` | **se sostiene con etiqueta** | sin intervalo; con n=24.882 señales correlacionadas por instrumento y fecha, un Wilson iid sería falsamente angosto — mejor sin barra que con una mentirosa, pero hay que decir por qué no la tiene |

## D. Censo del universo operable (`dinero_universo.json`, y `rieles.json.mapa`)

| cifra | valor que sirve la máquina | dónde | verdicto | etiqueta exigida / razón |
|---|---|---|---|---|
| censo por presupuesto | 7 / 13 / 29 / 33 alcanzables de 36 (enteras, 100/250/500/1000 USD) | `censo_por_presupuesto_y_modo.celdas` | **se sostiene con etiqueta** | **censo de UN SOLO DÍA (2026-09-04)**. No lleva intervalo y no debe llevarlo: es un censo de la población de 36, no una muestra — un Wilson sobre 36 mediría la incertidumbre equivocada. La unidad de replicación es el **día**, y n_días = 1. El segundo congelado cayó en la misma sesión (feriado NYSE del 7-sep) y **no cuenta como segundo día**; `MSFT` al borde a 500 USD (499,70 más comisión) |
| `mapa` del riel | candidatos 36, **huecos 0**, representados 6, sustituidos 2, verificados 36 | `rieles.json.rieles[1].mapa`; `api/main.py:1100` | **se sostiene con etiqueta OBLIGATORIA** | es la celda **500 USD / enteras** y el objeto **no declara ni el presupuesto ni el modo**. Sin esa etiqueta «0 huecos» es falso: a 100 USD enteras son **4 huecos y 7 alcanzables**. Falta además `al_borde: [MSFT]`, que el `resumen` no propaga |

## E. Rama de coherencia (`intervalo_coherencia.md/.json`)

| cifra | valor que sirve la máquina | dónde | verdicto | etiqueta exigida / razón |
|---|---|---|---|---|
| +14,3 pp, n=223, 33 días | percentil [−1,4, +32,1]; **t de clúster [−3,5, +32,2]**; permutación 0,111; b/c 69/37; exacta 0,0024 | `.md` §3 | **se sostiene con etiqueta** | **es OTRO ESTIMANDO**, no «+9,7 medido mejor»; el movimiento entero sale de **2 días de 34**; el estimador calibrado es el t de clúster y acá k=33 con 3 clústeres de tamaño 1, **fuera** del estudio de cobertura |
| R2 sobre la rama | +7,8 pp, t [−10,8, +26,5], permutación 0,433, exacta 0,1354, n=179 | `.md` §3b | **se sostiene** | las dos fechas retiradas están FUERA del bloque: la rama hereda la ventana afortunada |
| 70,9 % y 56,5 % | modelo y base de la rama | `.md` §3 | **se sostiene con etiqueta** | **viajan sin Wilson**. Modelo 158/223 = 70,9 % [64,6, 76,4] (`evaluacion.wilson_ci`). Regla 1: ningún puntual sin intervalo |
| ¿está clara en todos lados que es otro estimando? | — | grep | **parcialmente** | **El README NO la cita** (`grep -n "14,3\|14.3\|coherencia" README.md` → 0 líneas): correcto, no está cableada. `ESTADO.md:14`, `estado_epistemico.md:222`, `DECISIONES.md:8973` y `dictamen_11/` la citan **con** la etiqueta. `cola_decisiones.md:278` y `bitacora_05.md:910` la traen **sin** la frase «otro estimando» |

## F. Señal larga (bloque `senal_larga` de `rieles.json`)

| cifra | valor | verdicto | etiqueta exigida |
|---|---|---|---|
| «ganan_a_la_climatologia_sin_corregir: 1» junto a «contrastes: 30» | 1 y 30 | **se sostiene con etiqueta** | el **1 es sobre 6 CELDAS**, no sobre 30 contrastes: dos denominadores en el mismo objeto se leen como «1 de 30». Y falta lo que el mandato exige para todo «k de m cruzan alfa»: **la distribución de k bajo la nula con el ICC medido** (`grep` en `senal_larga_v1.json`: no existe). Dato duro: de los 30 p crudos, **11 están bajo 0,05** |
| `pasan_holm: []`, `ganan_tras_ablacion_anual: 0`, `L1_refutada: true` | — | **se sostiene** | resultado negativo publicado como tal: la etapa funcionando |

---

## Criterios congelados, tras las cifras RE-CORRIDAS

- **V1 — NO PASA.** +9,7 pp con IC de día [−7,2, +26,6] que contiene el cero y permutación p = 0,294. Sigue bloqueante hasta que se firme V1-bis; rige `DISEÑO.md` §6. La rama de coherencia no lo cambia (su IC también contiene el cero en las tres rutas).
- **V2 — NO EVALUABLE.** No hay retador con CRPS medido contra el campeón.
- **V3 — NO PASA.** Cobertura 92,9 % contra [76, 84]; ratio de ancho 2,19× [1,71, 2,78].
- **V4 — NO EVALUABLE.** MAE del gap 2,52 pp sobre n=238; no hay retador.
- **V5 — NO EVALUABLE.** Sin retador no hay Sharpe que deflactar; y el conteo de intentos está en disputa (abajo).
- **V6 — NO EVALUABLE.** El riel de dinero tiene CERO filas selladas; nada compara contra comprar SMH fuera de la simulación.
- **V7 — NO EVALUABLE.** El holdout en cuarentena no se tocó.
- **R1 — en pie** el resultado negativo del WS2b; no se re-evaluó en la corrida 11.
- **R2 — SE DISPARA**, y ahora en las dos ramas y bajo la regla firmada: campeón +9,7 → **+2,6 pp** (p permutación 0,821, exacta 0,6752, n=194); coherencia +14,3 → **+7,8 pp** (p 0,433).
- **R3 — NO CERRABLE.** El `auditor-lookahead` no encontró fuga en 25 cortes; que no queden es indemostrable, y G3 (contraprueba de `precios_ref`) está pendiente.

## Conteo de intentos: NO estoy de acuerdo con el 0 del bloque 4

`GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO = 352` (35 filas), `dinero.registro_intentos.N_INTENTOS_RIEL_LARGO = 3`. Ambos sin cambio.

- **Bloque 1 (simulador con verdad conocida): 0 — de acuerdo.** No se evaluó ninguna hipótesis sobre datos reales; los precios entran sólo como parámetro de calibración.
- **Bloque 2 (cuenta con señal sin información): 0 — de acuerdo.** La nula es conocida por construcción.
- **Bloque 4: NO de acuerdo con el 0.** El propio registro tiene dos precedentes que lo contradicen: la fila `COLA` cuenta **2** por «reglas de deduplicación keep=first y keep=last» — reglas de filas alternativas **que tampoco se cablearon** —, y la fila `DEUDA-2f` cuenta **14** por «IC de ΔMAE recomputados por clúster de día» sobre cifras ya publicadas. `filtrar_sesion_coherente` es exactamente una regla de filas alternativa y **no tiene fila en el registro** pese a haberse evaluado desde `bitacora_05.md`. El DSR deflacta por la BÚSQUEDA, no por la publicación.
- **Piso honesto: 352 → 354 y 358 → 360** (una por la regla de filas de coherencia, nunca registrada; una por la recomputación por clúster y bajo R2 del bloque 4). El número exacto lo escribe el orquestador con la convención del §28; **lo que no puede quedar es el cero.**

---

## Exigencias nuevas, aplicables al ejecutable

**D1.** `_comisiones_juego_activo` (`api/main.py:969`) deja de devolver un escalar. Devuelve un objeto con `mediana`, `banda_p2_5_p97_5`, `K`, `deslizamiento_pb`, `semanas`, `denominador_usd` y `es_una_semilla: false`. Un escalar de fricción no sale más de esta API.
**D2.** `_potencia_desde_artefacto` (`api/main.py:1001`) deja de escribir «95 %» a mano: propaga `sigma_dif_semanal.advertencia` y `cobertura_medida_del_ic_a_156_semanas`, y el `tipo_intervalo` pasa a «bootstrap circular de bloques de semanas, **nominal 95 %, cobertura medida 0,850 [0,833, 0,865] a 156 semanas**».
**D3.** La misma función deja de atribuir el MDE80 de 1,05 a la σ que sirve. O cita el MDE80 con **su** σ (2,704, ancla del simulador) o computa el de la σ servida (**0,91** pp/semana a 52 semanas). Test que falle si las dos σ se mezclan en la misma frase.
**D4.** `mde80()` (`GEMELO/simulador/instrumento_dinero.py:250`) toma α como argumento y el reporte publica las dos columnas: a α nominal y **al α real medido**. Hoy usa `Z = 1,96` fijo en una tabla cuya columna vecina es «α real».
**D5.** El MDE80 viaja con intervalo, propagado de la **banda entre sorteos** de σ ([1,911, 4,016] → **[0,74, 1,56]** pp/semana a 52 semanas). Ningún MDE sin barra.
**D6.** Toda cifra en pp/año declara si es **suma aritmética** o **capitalizada** (55 contra 72 a 52 semanas). Campo `convencion_anualizacion` en el JSON.
**D7.** El Wilson de `ic_excluye_cero` se recomputa con la **semilla** como clúster (20 unidades, no 480) o se retira y queda el conteo desnudo con el clúster declarado.
**D8.** Cada objeto `juegos[*].contra.*` lleva `alpha_real` y `cobertura_medida` junto a `alpha`. La regla de la casa que `api/main.py:888-891` declara —«todo estimador puntual viaja con su intervalo en el mismo objeto»— se extiende: **el intervalo viaja con su cobertura medida en el mismo objeto**.
**D9.** `rieles.json.mapa` declara `presupuesto_usd`, `modo` y `al_borde`, o no se sirve. «0 huecos» sin presupuesto es falso a 100 USD.
**D10.** El bloque `mapa` y el `.md` del censo llevan `dias_de_censo: 1` y `fecha_censo`, y la frase «no lleva intervalo porque la unidad de replicación es el día y n = 1».
**D11.** `que_lo_mata` del riel de medición se reescribe con el R2 recomputado bajo la regla firmada (+2,6 pp, n=194, 28 días, t de clúster [−15,7, +20,9], permutación 0,821) y borra «NO está recomputada».
**D12.** `cobertura_80_pct` viaja con su Wilson (221/238), como toda proporción de esta casa.
**D13.** El bloque del riel de medición lleva la etiqueta de **un solo régimen** (39 snapshots): n = 238 en un régimen es más chico que n = 238.
**D14.** «validado» sale de `api/main.py:1007`, `dinero/cuenta_papel.py:670` y `dinero/preregistro_dinero.md:240`; y el patrón entra al guardia. La corrección del curador se aplicó a una línea y no al generador, así que vuelve en cada regeneración.
**D15.** `senal_larga` separa los dos denominadores (`ganan_a_la_climatologia_sin_corregir` es **de 6 celdas**) y no se publica ningún «k de m» sin la distribución de k bajo la nula con el ICC medido.
**D16.** El artefacto de coherencia publica Wilson para 70,9 % y 56,5 %.
**D17.** A7 deja de ser prosa: test que fije `BLOQUE_SEMANAS = 4` y falle si cambia sin una fila de intento.
**D18.** Se abre la fila de intentos de `filtrar_sesion_coherente` en `GEMELO.relevo_asiatico` (352 → 354 como piso, 358 → 360), con la convención del §28 y citando los precedentes `COLA` y `DEUDA-2f`.

## Cifras RETIRADAS — patrones para el guardia de `cifras_retiradas.md`

| `patrón` | contexto | reemplazo |
|---|---|---|
| `12[,.]5\s?%?[^\n]{0,40}(comisi\|fricci\|aportado)` y `(comisi\|fricci\|aportado)[^\n]{0,40}12[,.]5\s?%` | fricción del juego activo servida como escalar de UNA semilla, sin intervalo, sin período ni denominador | mediana **12,4 %** de K=20 semillas, banda [6,35, 13,2], 5 pb, **156 semanas sobre 500 USD aportados** |
| `bootstrap circular de bloques de semanas,?\s*95\s?%` | etiqueta del IC de la σ semanal que la API escribía a mano | nominal 95 %, **cobertura medida 0,850 [0,833, 0,865]** a 156 semanas |
| `simulador validado\|instrumento validado` | palabra retirada por el curador el 8-sep y sobreviviente en el ejecutable | «puesto a prueba contra una verdad conocida: **discrimina y NO está calibrado a α = 0,05**» |
| `deduplicaci[óo]n firmada[^\n]{0,60}NO est[áa] (recomputad\|computad)` | afirmación falsa desde el 8-sep en `que_lo_mata` | R2 bajo la regla firmada: **+2,6 pp**, n=194, 28 días, t de clúster [−15,7, +20,9], permutación 0,821 |
| `51\s*(de\|/)\s*480[^\n]{0,80}(0[,.]082\|Wilson)` | Wilson iid sobre 480 comparaciones agrupadas en 20 semillas | 51/480 como conteo descriptivo, o IC con la **semilla** como clúster |
| `0\s*huecos` sin `500` ni `enteras` a ±1 línea | resumen del mapa servido sin presupuesto ni modo | «0 huecos **a 500 USD, acciones enteras**; a 100 USD son 4 huecos y 7 alcanzables» |

---

**VEREDICTO GLOBAL:** las cifras re-corridas de los tres artefactos **se sostienen en los artefactos y NO se sostienen en la forma en que la API las sirve** — el hallazgo firme sigue siendo negativo (el instrumento discrimina pero no está calibrado, α real 0,086 a 52 semanas y 0,064 a 156; la rama de coherencia es otro estimando y bajo R2 se apaga igual que el titular; la cuenta mide fricción, no habilidad), y las cuatro cifras que la pantalla mostraría hoy —el 12,5 pelado, el «95 %» del IC de la σ, el «NO está recomputada» del R2 y el «0 huecos» sin presupuesto— **se retiran hasta que D1 a D18 estén en el ejecutable**.
