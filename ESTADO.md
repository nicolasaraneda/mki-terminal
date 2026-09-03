# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 3-sep-2026, mediodía (corrida 09).

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers, emite; el modo se le pregunta
  a `modo.py`. Modelo 4.6.0 congelado. **Último sello: 2026-09-02** (42 snapshots).
- **`noticias.py` corregido (O(n²) → lineal, marca en tabla `meta`)**: la primera
  corrida con el código es HOY 17:50 (~13–15 min; una transacción). El parche del
  timer a 2.700 s queda innecesario (firma). `.env` sigue en 644.

## Las cuatro reglas de la casa, ejecutables (`cifras.py` árbitro; `test_cifras_arbitro.py`)
Verificar con el mismo mecanismo no es verificar · la corrección va al ejecutable, no a
la prosa · ningún estimador sin intervalo computado (ahora de clúster de día) · un número
retirado en el código circula. Registro de intentos: **352** (5.1: 358), +66 esta corrida.

## Lo que la corrida 09 aplicó (acta §78)
- **D1 aplicada:** la cifra publicada es la de la regla firmada: **n 238, +9,7 pp, IC95
  de día [−7,2, +26,6] (contiene el cero), p de día 0,29; McNemar de filas 0,0455 al
  lado**. La rama sin deduplicar está RETIRADA; «+ coherencia» (+14,3) sigue en cola.
- **D2 confirmada** (cola §28). **D3 aplicada:** magnitud primaria; enmienda V1-bis v2
  escrita — el adversario dictaminó **cambio de PREGUNTA, no de vara**; firmable así, y con
  un **conflicto**: D3 dice «contra predecir cero», el adversario exige climatología causal
  («cero» es positivo bajo ventaja nula el 54 %). Nicolás decide (`espera` §30).
- Frase de potencia en dos versiones (`espera` §29): dirección 0,30 [0,27, 0,33] el 25-oct;
  magnitud 0,90 / 0,86 / 0,70 (generador / observado / R2); 96 [20, ∞) días al efecto
  observado; **ninguna fecha encabeza**. Horizonte con simulador calibrado: 9 pp ≈263
  días (MC [229, 296]; paramétrico 248 [109, 370]) → ago-2027.

## Deuda pagada (todo PROPUESTA hasta firma; nada aplicado a intocables)
- Importador verificado fila a fila (0 discrepancias, `plataforma_version` 42/42).
- Parche `snapshot.py:140` como `.diff` + test + tabla: **25 filas malas, las 25 serían
  `no_verificable_timing` bajo el parche** (la cola decía 15: errata). Firma §26.
- Cuatro tarjetas firmables (abstención, `ts_emision`, `Persistent`, campeón vs fuente);
  diseño de la réplica (8 decisiones, cola §29); IC de ΔMAE por día (nadie mejora a cero
  de forma distinguible); `motor_concat.diff` byte-idéntico; **`^VIX3M` sin datos en la
  caché desde el 17-jul** (firma: verificar con red).

## Lo que sigue en pie
- **Juez lineal bajo D3 corrido, EXPLORATORIO** (`corrida09/juez_lineal_d3.md`): C1 supera a
  cero pero no al campeón sobre las mismas filas, y no sobrevive a R2; los features no traen
  magnitud distinta de SOX(t, t−1). NO CONCLUYENTE (dictamen); corrió por orden del encargo.
- Gatillo 5.1: **25-oct**. La ventana sellada no distingue la dirección de cero con la
  unidad correcta; la magnitud sí tiene potencia a ese horizonte, pero su efecto
  observado tiene intervalo que contiene el cero. **Lo más urgente: firmar V1-bis (y
  resolver cero vs climatología) y el parche `:140`.**

Modo y timers: Nicolás. Hook: motor intocable, sellos jamás reescritos, sin push ni
pull. Antes de cerrar: `guardian-constitucion` y `curador-epistemico`. Ver `orientador`.
