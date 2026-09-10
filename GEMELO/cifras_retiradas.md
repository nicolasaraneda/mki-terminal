# Cifras retiradas — registro legible por máquina

Cada fila es un patrón (regex) que **no debe reaparecer sin marca de
retiro** en un documento publicado (`README.md`,
`GEMELO/resultados/estado_epistemico.md`, la skill `cifras-canonicas`).
Lo lee `cifras.cifras_retiradas()`; lo aplican `tests/test_cifras_arbitro.py`
y, desde el 2-sep-2026 de noche, el **bloque 8 del hook VIGENTE**
`.claude/hooks/guardia-reglas.py`, que deniega el `Edit`/`Write` que reintroduzca
uno de estos patrones en un `.md` o en un `.py` sin marca de retiro (exentos este
registro y `.claude/tests-agentes/`; un `.txt` o un heredoc por Bash no pasan por
él, y evalúa sólo el texto nuevo de la edición, no el archivo resultante). Lo
instaló Nicolás con `GEMELO/propuestas/hooks/instalar.sh`; reemplaza a la
propuesta anterior `GEMELO/propuestas/guardia-cifras-retiradas.py`, que cubría
sólo los tres documentos publicados y nunca se instaló (DECISIONES §77).
Una mención con «retirad», «errata», «decía», «era», «refutad», «corregid»,
«es falsa», «falso» o «desmont» a ±2 líneas no cuenta como reintroducción:
es la historia (el README dice del 91,4% «es falsa» en la línea siguiente).

> **Límite conocido del instrumento, medido el 7-sep-2026 (corrida 10).** La
> ventana de ±2 líneas supone que la marca habla de la cifra que está al lado, y
> eso no siempre es cierto: en `dinero/resultados/senal_larga_v1.md` la palabra
> «corregida» de una línea vecina —que hablaba de otro tema— hizo que
> `cifras.reintroducciones()` diera **falso verde** sobre una reintroducción real
> del 91,4 %. La cazó el `curador-epistemico` leyendo, no la máquina. Desde esa
> fecha la exención exige además que el contexto **nombre el patrón o traiga una
> marca fuerte** (ver `cifras.MARCAS_FUERTES`), y hay contraprueba en
> `tests/test_cifras_arbitro.py`.
>
> **Segundo límite, misma fecha:** los patrones se escriben en una sola
> conjugación. «satura en 1,0000» no caza «saturó» ni «saturado», y las dos
> formas circularon en la corrida 10. Un patrón nuevo se escribe pensando en
> cómo se va a conjugar, no en cómo se escribió la primera vez.

Formato: `| patrón | contexto | fecha de retiro | acta o expediente | reemplazo |`

| `patrón` | contexto | retirada | acta / expediente | reemplazo |
|---|---|---|---|---|
| `8[,.]6\s?%\s*(de\s+)?contaminaci` | contaminación PIT por revisión de precios | 2026-08-31 | `auditoria_ws3.md`:213-236; acta §68 | 0,00% sobre 223 filas |
| `91[,.]4\s?%` | coincidencia sello/reconstrucción con clave equivocada | 2026-09-01 | acta §68; `espera_firma.md` §11 | 100% sobre 214 filas |
| `3[,.]64\s?×` | «los datos refutan la simetría por 3,64×» | 2026-08-31 | acta §56; `SECUENCIAL/DISEÑO.md` §A3.1.b | razón 1,33× [0,89, 2,16] |
| `MDE[^\n]{0,40}\b7\s?pp` | MDE de 7 pp derivado en la escala del retorno | 2026-08-31 | acta §56 | 8,96 pp [6,67, 11,32] (a su vez objetado) |
| `−62[,.]5\s?pp|-62[,.]5\s?pp` | «−62,5 pp sobre 16 filas en dos fechas» | 2026-09-01 | `bitacora_06.md` 12:20 y 12:50 | −50,0 pp sobre 28 filas, 4 fechas |
| `α\s*(empírico|empirico)[^\n]{0,30}0[,.]083` | α empírico 0,083 de la permutación de signo por día | 2026-09-02 | `dictamen_07/DICTAMEN.md` B; acta §74 | 0,055 [0,048, 0,064] a 3.000 réplicas |
| `4×\s*menos\s*señal|cuatro veces menos señal` | «el mecanismo tiene 4× menos señal por día que el nivel» | 2026-09-02 | `dictamen_07/DICTAMEN.md` E; `tesis.md` §6 | no establecido (unidad de replicación = bolsa) |
| `−1[,.]6\s?pp\s*(de ventaja\s*)?por hora|-1[,.]6\s?pp\s*(de ventaja\s*)?por hora` | pendiente del decaimiento por hora con IC de fecha | 2026-09-02 | `dictamen_07/DICTAMEN.md` E-2 | escalón por bolsa, sin pendiente |
| `1\.962\s*(celdas|niveles)` | «1.962 celdas reescaladas por dividendos en varios tickers» | 2026-09-02 | `dictamen_07/DICTAMEN.md` A(ii) | 1.953 celdas de 000660.KS, factor 0,999783 |
| `~?15\s?MB/año` | costo estimado a ojo de la copia de insumos | 2026-09-02 | `bitacora_07.md` 02:37 | 9 MB/año (130 barras) / 53 MB/año (3 años), medidos |
| `0[,.]34\s*\[0[,.]31,\s*0[,.]37\]` | potencia del 25-oct a 1.000 simulaciones | 2026-09-02 | `bitacora_08.md` 11:36 | 0,36 [0,34, 0,37] de `horizonte.md`, a su vez retirado abajo |
| `0[,.]36\s*\[0[,.]34,\s*0[,.]37\]` | potencia del 25-oct según `horizonte.md`, instrumento medido optimista (+2,7 pp) | 2026-09-02 | `dictamen_08/A.md` A4; acta §75 | 0,31 [0,27, 0,35] (simulador calibrado, `calibracion_instrumento.md` A4) |
| `satura[n]?\s+en\s+1[,.]0000` | «el PSR y el DSR saturan en 1,0000 por anualizar un Sharpe sobre pocos días» | 2026-09-02 | `dictamen_08/A.md` A3; erratas en `control_lineal.md`, `ventana_larga.md` | defecto de unidades del PSR/DSR; con la unidad correcta 0,95–0,96 |
| `3[,.]47\s?pp[^\n]{0,60}revis` | «la fuente revisó su historia, 3,47 pp» | 2026-09-01 | acta §69 (`docs/SEGUNDO_SELLO.md` §0) | barra retirada; 5,80 pp bajo la lógica de producción |
| `\bn\s?=\s?248\b|n%3D248|\b(164|148)/248\b` | ventana sellada SIN deduplicar (n = 248), convención derogada por D1 | 2026-09-03 | acta §78; `cola_decisiones.md` §2a; encargo 09 D1 | n = 238 bajo la regla de deduplicación firmada (`cifras.sellada()`) |
| `\+6[,.]5\s?pp` | ventaja de la ventana sellada sin deduplicar | 2026-09-03 | acta §78 | +9,7 pp [−7,2, +26,6] de día (n = 238) |
| `0[,.]1849` | McNemar χ²cc de la rama sin deduplicar | 2026-09-03 | acta §78 | 0,0455 de filas, y decide el IC de día |
| `1[,.]84\s?[×x]` | ratio ancho/error de los intervalos del 80% sin n ni intervalo | 2026-09-03 | acta §78; encargo 09 §1d | 2,19× [1,71, 2,78] de día (n = 238) |
| `269\s?(días\s?)?\[229,\s?275\]` | días para 0,80 a 9 pp con el Wilson invertido por bisección y UNA sola semilla: el intervalo no medía la incertidumbre que decía medir | 2026-09-03 | `bitacora_09.md` 12:20; acta §78.3 | ≈263 días, rango Monte Carlo [229, 296] sobre tres semillas (`horizonte.json`) |
| `58\s?(días\s?)?\[54,\s?62\]` | días para 0,80 en magnitud «antes del 25-oct», condicional a un efecto que el observado no distingue de cero | 2026-09-03 | `bitacora_09.md` 12:20; acta §78.3 | 96 [20, ∞) días al efecto observado; ninguna fecha encabeza |
| `ganancia[^\n]{0,30}93\s?%` | «la constante μ recupera el 93 % de la ganancia de MAE» | 2026-09-03 | `dictamen_08/E.md`, errata al pie; `bitacora_08.md` 15:03 | 7,2 % sobre n = 238 (7,3 % en `potencia_por_metrica.json`) |
| `satur[oó]|saturad[oa]s?` | conjugaciones de «el PSR saturó / saturado en 1,0000»: el patrón original sólo cazaba el presente y las dos formas circularon igual en la corrida 10 | 2026-09-07 | `dictamen_10/curador_epistemico.md` O6; acta §80 errata | defecto de unidades del PSR/DSR; con la unidad correcta 0,95–0,96 |
| `21\s?%[^\n]{0,60}falso|falso[^\n]{0,40}21\s?%` | «este diseño produce un falso positivo el 21 % de las veces» (5 de 24 comparaciones de la cuenta en papel) | 2026-09-07 | `dictamen_10/estadistico_adversario.md` exigencias 1 a 4; acta §80.4 errata | 1 de 24 sin explicación de fricción (el α nominal); la tasa de tipo I de ese diseño NO está medida y la página está retirada por fuga |
| `14\s?%[^\n]{0,20}(a|–|-)[^\n]{0,5}43\s?%` | «las comisiones se comen 14 % a 43 % del capital», rango de un solo sorteo y medido con fuga F1/F2 adentro | 2026-09-07 | `dictamen_10/auditor_lookahead.md` E8 | sin cifra en la v1; la v2 reconstruida (8-sep-2026) mide 12,4 % para el juego por defecto, mediana de 20 semillas, 156 semanas |
| `−3[,.]3\s?pp|-3[,.]3\s?pp` | ventaja del campeón bajo la ablación R2, publicada como estado vigente | 2026-09-07 | `dictamen_10/curador_epistemico.md` B1 | bajo R2 la ventaja no se distingue de cero en las tres convenciones (+0,5 / −1,0 / −1,9 pp); sin recomputar bajo la regla firmada el 1-sep |
| `sobrevive[^\n]{0,40}una (sola )?celda|una celda de seis` | «sobrevive una celda de seis a la climatología causal» | 2026-09-07 | `dictamen_10/estadistico_adversario.md` exigencias 9 y 14; acta §80.8 errata | ninguna celda sobrevive: no pasa Holm sobre 30 contrastes (p 0,1740) ni la ablación anual (sin 2024 el IC contiene el cero) |
| `27\s?%\s*(→|->|a|pasa\s+a)\s*(\*\*)?57\s?%` | «el juego medio pasa de 27 % a 57 % del capital en comisiones»: cuenta v1 con fuga F1 a F4, medida por el auditor sobre la v1 | 2026-09-08 | acta §82.4 y §83.3; `dictamen_11/auditor_lookahead.md` | v2: 26,7 % mediana de 20 semillas para el juego medio (un diseño distinto: arancel del §40) |
| `σ\s?=\s?2[,.]54|2[,.]54\s?pp\s?(por|/)\s?semana` | σ de la diferencia semanal de la cuenta v1, tabla §2.1 del pre-registro del riel | 2026-09-08 | `preregistro_dinero.md` §7 C; acta §83.1 | 2,336 pp/semana en la v2 (punto utilizable; su IC no es un 95 %) y ancla 2,704 en el simulador |
| `12[,.]5\s?%?[^\n]{0,40}(comisi\|fricci\|aportado)` | fricción del juego activo servida por la API como escalar de UNA semilla, sin intervalo, sin período ni denominador | 2026-09-09 | `dictamen_12/re_dictamen_corrida_11.md` §C, D1 | mediana 12,4 % de K=20 semillas, banda [6,35, 13,2], 5 pb, 156 semanas sobre 500 USD aportados |
| `(comisi\|fricci\|aportado)[^\n]{0,40}12[,.]5\s?%` | ídem, con el número después de la palabra | 2026-09-09 | `dictamen_12/re_dictamen_corrida_11.md` §C, D1 | el objeto completo (mediana, banda, K, pb, semanas, denominador) |
| `bootstrap circular de bloques de semanas,?\s*95\s?%` | etiqueta del IC de la σ semanal escrita a mano por la API: cobertura medida 0,850 a 156 semanas | 2026-09-09 | re-dictamen §B, D2; `instrumento_dinero.md` columna «cobertura IC sd» | «nominal 95 %, cobertura medida 0,850 [0,833, 0,865] a 156 semanas» |
| `(simulador\|instrumento) validad[oa]` | palabra retirada por el curador el 8-sep, sobreviviente en los generadores | 2026-09-09 | re-dictamen §B, D14 | «puesto a prueba contra una verdad conocida: discrimina y NO está calibrado a α = 0,05» |
| `deduplicaci[óo]n firmada[^\n]{0,60}NO est[áa] (recomputad\|computad)` | afirmación falsa desde el 8-sep en `que_lo_mata` del riel de medición | 2026-09-09 | re-dictamen §A, D11; `intervalo_coherencia.md` §3b | R2 bajo la regla firmada: +2,6 pp, n=194, 28 días, t de clúster [−15,7, +20,9], permutación 0,821 |
| `51\s*(de\|/)\s*480[^\n]{0,80}(0[,.]082\|Wilson)` | Wilson iid sobre 480 comparaciones agrupadas en 20 semillas | 2026-09-09 | re-dictamen §C, D7 | 51/480 como conteo descriptivo, con la semilla como clúster |
| `\b0\s*huecos\b(?![^\n]{0,80}(500\|enteras))` | resumen del mapa servido sin presupuesto ni modo: a 100 USD enteras son 4 huecos | 2026-09-09 | re-dictamen §D, D9 | «0 huecos a 500 USD, acciones enteras; a 100 USD son 4 huecos y 7 alcanzables» |
