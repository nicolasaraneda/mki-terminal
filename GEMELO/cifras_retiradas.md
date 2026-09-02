# Cifras retiradas — registro legible por máquina

Cada fila es un patrón (regex) que **no debe reaparecer sin marca de
retiro** en un documento publicado (`README.md`,
`GEMELO/resultados/estado_epistemico.md`, la skill `cifras-canonicas`).
Lo lee `cifras.cifras_retiradas()`; lo aplican `tests/test_cifras_arbitro.py`
y el hook propuesto `GEMELO/propuestas/guardia-cifras-retiradas.py` (NO
instalado: el hook vigente se protege a sí mismo y sólo Nicolás lo edita).
Una mención con «retirad», «errata», «decía», «era», «refutad», «corregid»,
«es falsa», «falso» o «desmont» a ±2 líneas no cuenta como reintroducción:
es la historia (el README dice del 91,4% «es falsa» en la línea siguiente).

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
