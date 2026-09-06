# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 6-sep-2026 (dictámenes de la 09).

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers, emite; el modo se le pregunta a
  `modo.py`. Modelo 4.6.0 congelado. Último sello al escribir esto: 2026-09-04 (44
  snapshots); el vigente se lee de `./mki estado`, no de aquí. `.env` en 600.
- **`noticias.py` corregido (O(n²) → lineal)**: en producción desde el 3-sep (615,9 s la
  primera pasada, 54,0 s la diaria). Toca un insumo SELLADO: `puntaje_ia` lleva el
  sentimiento con peso 0,3, y el bump de `FEATURE_VERSION` es de Nicolás (`espera` §38).

## Las cuatro reglas de la casa, ejecutables (`cifras.py` árbitro; `test_cifras_arbitro.py`)
Verificar con el mismo mecanismo no es verificar · la corrección va al ejecutable, no a
la prosa · ningún estimador sin intervalo computado (ahora de clúster de día) · un número
retirado en el código circula. Registro de intentos: **352** (5.1: 358), +66 en la 09.

## Los dos dictámenes que faltaban, obtenidos el 6-sep (`GEMELO/resultados/dictamen_09/`)
- **La 09 cerró SIN ellos** (agentes caídos por límite de API): el diff se commiteó sin
  guardián y los textos públicos salieron sin curaduría. `guardian-constitucion`: APROBADO
  CON EXIGENCIAS (7). `curador-epistemico`: **RECHAZADO** (7 bloqueantes, 30 exigencias).
  Todas aplicadas; ninguna movió una cifra del árbitro.
- Destaparon: el IC del ΔMAE salía en escala de Sharpe en el ejecutable con la errata
  sólo en la prosa; la ganancia de MAE se publicaba sin intervalo; y el titular del
  README sostenía un mecanismo cuya predicción fuera de muestra había fallado.

## Lo que la corrida 09 aplicó (acta §78; los dictámenes, §79)
- **D1 aplicada:** **n 238 (34 días), +9,7 pp, IC95 de día [−7,2, +26,6] (contiene el
  cero), p de día 0,29; McNemar de filas 0,0455 al lado**. La rama sin deduplicar está
  RETIRADA; «+ coherencia» (+14,3, sin intervalo: no publicable) sigue en cola.
- **D2 confirmada** (cola §28). **D3 en curso, DECISIÓN PENDIENTE:** la enmienda V1-bis
  v2 está escrita y espera firma; hasta la firma, V1 (dirección) sigue bloqueante y la
  magnitud no es primaria. El adversario dictaminó **cambio de PREGUNTA, no de vara**,
  con un **conflicto**: D3 dice «contra predecir cero», él exige climatología causal
  («cero» es positivo bajo ventaja nula el 54 %). Nicolás decide (`espera` §30).
- Frase de potencia (`espera` §29): ancla 31-ago, cadena local, n 246, 35 días (no la
  ventana publicada); dirección 0,30 [0,27, 0,33]; magnitud 0,90 / 0,86 / 0,70; 96 [20, ∞)
  días al efecto observado; **ninguna fecha encabeza**. Horizonte: ≈263 días, MC [229, 296].

## Deuda pagada (todo PROPUESTA hasta firma; nada aplicado a intocables)
Importador verificado fila a fila (0 discrepancias); parche `snapshot.py:140` con `.diff`,
test y tabla (**25 filas malas, las 25 serían `no_verificable_timing`**; la cola decía 15:
errata; firma §26); cuatro tarjetas; réplica (cola §29); `motor_concat.diff`; **`^VIX3M`
sin datos en la caché desde el 17-jul**. Juez lineal bajo D3 EXPLORATORIO: los features
no traen magnitud distinta de SOX(t, t−1). NO CONCLUYENTE.

Gatillo 5.1: **25-oct**. **Lo más urgente: firmar V1-bis (cero vs climatología) y el
parche `:140` con su bump.** Modo y timers: Nicolás. Hook: motor intocable, sellos jamás
reescritos, sin push ni pull. Antes de cerrar: los dos dictámenes. Ver `orientador`.
