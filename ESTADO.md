# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 8-sep-2026 (corrida 11).

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers, emite; el modo se le pregunta a
  `modo.py`. Modelo 4.6.0 congelado. El sello vigente se lee de `./mki estado`. `.env` en 600.
  **La corrida 11 no tocó nada del camino de sellado.** `noticias.py` corregido desde el 3-sep;
  el bump de `FEATURE_VERSION` es de Nicolás (§38).

## Los dos rieles (detalle en `VISION.md`, acta §80)
- **Medición:** gap asiático sellado, una noche. n 238 / 34 días, +9,7 pp, **IC95 de día
  [−7,2, +26,6] contiene el cero**. La rama de coherencia (n 223, +14,3 pp, firmada en §82.3,
  NO cableada) tiene ya su intervalo: **también contiene el cero en las tres rutas**, y bajo R2
  cae a +7,8 pp (p 0,43). Cablearla y mover el README es decisión aparte (`espera` §46).
- **Dinero** (`dinero/`): todo SIMULADO, cero filas selladas. Aislado del sellado con test.

## Corrida 11 (8-sep): las seis firmas del §82, ejecutadas (acta §83)
- **El instrumento del riel de dinero, validado con verdad conocida:** DISCRIMINA (criterio
  pre-declarado), pero **no está calibrado a α = 0,05** (tamaño 0,086 y cobertura 0,914 a 52
  semanas; α real 0,064 a 156) y el IC de la sd cubre 0,78 a 0,85. MDE80 a 52 semanas: 1,05
  pp/semana. PROPUESTA con dictamen «sostiene con exigencias» (aplicadas).
- **Cuenta en papel RECONSTRUIDA (v2), PROPUESTA:** E1 a E6, gate de invariancia INVARIANTE en
  25 cortes por regla con contraprueba; el auditor no encontró fuga (`dictamen_11/`), y que no
  queden es indemostrable. Fricción del juego por defecto 12,4 % de los 500 USD aportados **sobre
  156 semanas** (mediana de 20 semillas, banda [6,4, 13,2]); la manda el número de órdenes
  (~210), no el arancel. Cobertura causal (MEDIDA) 0 % → 28 % / 84,5 %. Arancel del §40 (sin
  firma) en `reglas.json`; umbrales recomputados por su regla (`espera` §48).
- **§82.1, §82.5 ejecutadas:** el generador de la señal larga emite «3 especificaciones, 30
  contrastes»; el README declara el método de cada p; un xfail menos.
- **Guardia del `except` (§82.2 c): parche NO aplicado** `guardia_ancla_temporal.diff` (alerta
  del vigía + log + conteo en el verificador), con 6 tests; aplica junto al del §26. Conteo (d),
  MEDIDO en `senales.db` (`mode=ro`): **0 de 319 filas 4.6.0** con `available_at` de reloj de
  pared (8 legacy con NULL, no evaluables): agujero teórico hoy.
- **Censo por presupuesto y modo (MEDIDO sobre el congelado del 4-sep):** enteras 7 / 13 / 29 /
  33 de 36 a 100 / 250 / 500 / 1000 USD; fraccionarias 36 de 36 con 2 % de ida y vuelta. El
  «segundo día» no aportó sesión (7-sep feriado NYSE): sigue siendo censo de un solo día.
- Guardia nuevo: `tests/test_razones_xfail.py` (cada xfail con predicado ejecutable).

## Deuda
- Registro de intentos del riel largo: **3** (30 contrastes en la familia). Asiático intacto
  (352 / 358). La corrida 11 no sumó intentos.
- `inventario_abierto_2026-09-07.md`, citado por §82 y el encargo, **no existe en el repo**. El
  IC de σ de la cuenta no es un 95 % y el estimador del riel sub-cubre: decisión (`espera` §50).

## Lo más urgente, que sigue siendo de Nicolás
Aplicar **§26 + guardia §49** en el mismo acto (con bump). Decidir **§46** (cablear la
coherencia y el README), **§47** presupuesto con la tabla a la vista, **§48** arancel §40 y
umbrales, **§43** período de M2, **§44** M4, **V1-bis** (§30).
