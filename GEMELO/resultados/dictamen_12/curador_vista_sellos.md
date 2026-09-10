# Dictamen del `curador-epistemico` — vista `/sellos` y frases fijas nuevas de la API (corrida 12, bloque 5.3)

**9-sep-2026, ~00:17 hora de Chile.** DICTAMEN: **RECHAZADO** (4 bloqueantes, 12 correcciones, 4 observaciones). Archivado tal cual por el orquestador; la aplicación está en `bitacora_12.md`, bloque 5.

Documentos: `frontend/src/vistas/SellosDinero.tsx`, `api/main.py` (dinero_sellos, _e1_estado, _potencia_desde_artefacto, _que_mata_medicion, _mapa_con_etiqueta, _comisiones_juego_activo), `frontend/src/vistas/RielDinero.tsx`, `frontend/src/vistas/Rieles.tsx`, `dinero/sello_dinero.py`.
Frases fijas revisadas: 44. Sin estatus utilizable: 4. Reintroducción de cifras retiradas: 0 (verificado con `cifras.reintroducciones()` sobre los 5 archivos).

## SellosDinero.tsx

| # | cita literal (recortada) | estatus que lleva / falta | verdicto |
|---|---|---|---|
| 1 | "Riel de dinero, lo sellado para la próxima apertura" | chips SIMULADO + TAMAÑO CERO + PROPUESTA | PASA (lo salva la frase 3 pegada abajo) |
| 2 | "Nada de esta pantalla mueve plata ni afirma una ventaja" | PROPUESTA | PASA |
| 3 | "Qué señal se sella: sorteo sin información (...): prueba de maquinaria, no track record" | declarado | PASA |
| 4 | "{d.smh}" | falta n/fuente en pantalla | CORREGIR: "(censo de 1 día, `universo_operable.json`)" |
| 5 | "Sesiones que cuentan para N: 0 de 40" + "fuente: dinero/sello_dinero.db" | fuente FALSA para el 40 | **BLOQUEANTE 1** |
| 6 | nota E0 | PROPUESTA | PASA |
| 7 | "No hay cuenta de práctica conectada (...)" | NO EJECUTADO + PRÁCTICA | PASA |
| 8 | `<Estatus valor="PRÁCTICA">` y `"TAMAÑO CERO"` | no son estatus evidenciales | CORREGIR: fuera de la ranura de estatus |
| 9 | "fuera de la ventana de sellado" | contradictorio | CORREGIR: "fuera de la ventana 17:50 a 20:30 de producción" |
| 10 | cuenta regresiva hh:mm:ss | sin fuente ni estatus | CORREGIR: leyenda de procedencia y «a esa hora no ocurre nada: el tamaño es cero» |
| 11 | título "Decisiones selladas para la apertura del …" | | CORREGIR: agregar "señal sin información" al título |
| 12 | "acciones por la regla … lo sellado es tamaño cero" | condicional explícito | PASA |
| 13 | "La señal es un sorteo sin información …" | | PASA (frase modelo) |
| 14 | "Precio ref. USD", "Señal pp [banda]" | sin fecha ni naturaleza | CORREGIR: "(cierre del insumo sellado)", "[banda del sorteo]" |
| 15 | "Gate de invariancia de la última corrida" + INVARIANTE a 18px | atribuye a E0 un gate de la cuenta v2 | **BLOQUEANTE 2** |
| 16 | "{alcance}" | | PASA en contenido; a 11px bajo un 18px |
| 17 | comentario "lo que la máquina decidió" | no se renderiza | OBSERVACIÓN |
| 18 | "{compras} de {N} instrumentos …" | | PASA |

## api/main.py

| # | cita | verdicto |
|---|---|---|
| 19–23 | estatus PROPUESTA; que_es; _e1_estado (fecha, hora, método); "NO es evidencia de C1/C2"; fuente del gate | PASA |
| 24 | "con intervalo cuya cobertura está MEDIDA, no supuesta" | CORREGIR: "con cobertura medida 0,850, por debajo del 95 % nominal: el punto es utilizable, el intervalo no" |
| 25 | "discrimina y NO está calibrado a α = 0,05" | PASA por registro; OBSERVACIÓN: calificar «discrimina» (0,83 a 1 σ; 0,15 a 0,25 σ) |
| 26 | MDE80 con su σ ancla | PASA |
| 27 | "a 156 semanas" fijo mientras la celda se busca por `sig["semanas"]` | CORREGIR: interpolar |
| 28 | "R2 … la ventana 15 a 23 jul, que sostiene casi toda la ventaja" | **BLOQUEANTE 3**: ordena cantidades que el diseño no ordena (la ventaja completa ya incluye el cero) |
| 29–31 | R2 recomputado con n e intervalo; rama sin artefacto; mapa etiquetado | PASA |
| 32 | `"dias_de_censo": 1` fijo | CORREGIR: derivarlo de las metas |
| 33 | fricción como objeto | PASA |
| 34 | `estatus: PROPUESTA` en fricción y potencia | OBSERVACIÓN: SIMULADO describe mejor |

## dinero/sello_dinero.py

| 35 | `SENAL_FUENTE` | PASA | · | 36 | `estado()` PROPUESTA | PASA | · | 37 | `N_objetivo 40` sin fuente | CORREGIR: `N_objetivo_fuente` (raíz del bloqueante 1) |

## RielDinero.tsx y Rieles.tsx

| 38 | chip en cabecera de cada Card | PASA |
| 39 | "el hallazgo robusto" junto a PROPUESTA | CORREGIR: "estable entre los 20 sorteos" |
| 40 | chip MEDIDO presidiendo toda la columna (que_lo_mata, potencia, falta_para_veredicto tienen estatus propio) | CORREGIR: acotar el alcance |
| 41 | `estatus="MEDIDO / SIMULADO"` a mano en la tarjeta introductoria sin cifras | **BLOQUEANTE 4** |

## BLOQUEANTES

1. El `N_objetivo` (40) no sale de `sello_dinero.db`: es una DECISIÓN firmada (acta §84.4.7). Fuente por celda; con base ausente «aún sin base: 0 filas».
2. El gate que la vista muestra es el de la cuenta en papel v2 (corrida 11), no de E0. Título honesto, resultado al mismo tamaño que su alcance, y decir que E0 no tiene gate propio todavía.
3. "sostiene casi toda la ventaja" presupone una ventaja que sostener; la ventana completa (+9,7 pp, IC de día [−7,2, +26,6], n=238) ya incluye el cero.
4. `estatus="MEDIDO / SIMULADO"` inventado para una tarjeta de prosa, efecto colateral del test que exige la prop en toda Card. Permitir `SIN CIFRAS` explícito.

## OBSERVACIONES

- Los negativos están publicados con la misma firmeza que lo demás. El balance de la vista PASA la regla 3.
- «confianza» no aparece en ninguno de los cinco archivos. «Oportunidad» tampoco aparece en el repo.
- El censo de palabras prohibidas sólo mira el TSX; la mayoría de las frases fijas viven en `api/main.py`: agregar el mismo censo sobre el JSON servido.
- No hay prueba que garantice que `E1` nunca traiga datos de ejemplo (pre-mortem 20).

## ZONAS CIEGAS

- No levanté la API ni el frontend: dictamino sobre el código fuente, no sobre el pixel.
- No corrí `pytest` ni `cifras.sellada()`; el +9,7 pp lo tomé del README.
- `dinero/sello_dinero.db` no existía: las frases del bloque «Decisiones selladas» se juzgaron sobre la rama de código.
