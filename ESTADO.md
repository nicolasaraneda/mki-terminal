# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 11-oct-2026 (corrida 16-2, diurna con Nicolás; acta §101).

## Primero: dos cosas sin commitear, y tres parches listos que Nicolás aplica a mano
0. **La 16-1 sigue aplicada al árbol real y SIN commitear** (corte de método 10-oct 23:12:48; lista de 27 rutas en
   `bitacora_16_1.md` §8). La 16-2 agrega documentos y parches, nunca código (lista en `bitacora_16_2.md` §9).
1. **Camino T de §62 (§93.7, §99.2), listo para aplicar:** `GEMELO/propuestas/parches/camino_T_16_2.diff`,
   `b2_contrato_16_2.diff`, `b2_api_16_2.diff`, **en ese orden y en el mismo acto** (B2 del auditor). Receta exacta
   en `bitacora_16_2.md` §5 a §6; párrafo para el acta de aplicación en §6.2 (las cuatro decisiones del implementador,
   el texto B3 de §93.7, el corte `VERSION_SELLO = E0.3`, lo que cambió del dictamen 15 al 16-2). Dictamen APLICABLE
   CON EXIGENCIAS: R1 y R2 plegadas; B1 exige declarar que T cubre el disparo de recuperación con timing roto (28-sep,
   7-oct) y NO el de timing ok en día sin sesión, que sigue ocupando la fecha como `dia_sin_sesion` (§57).
2. **Plazo operativo:** antes del sello del martes 13-oct a las 00:30 Chile si se quiere que la sesión del 12-oct sea la
   primera con E0.3. Commit fuera de 17:50 a 20:30 del lunes. Predicción falsable del 13-oct en la bitácora §7.
3. **Tarjeta §81** (aplicación, la otra forma del disparo de recuperación, R3/R4/R5 del auditor, la pantalla `/sellos`);
   **§80** sigue sin firmas. La copia de `dinero/sello_dinero.db` al worktree fue denegada otra vez (§95.5 rigió).

## Lo que cambia en operación cuando los tres parches entren
- Un disparo del sellador con timing roto deja sus filas en `intentos_no_verificables` y su evidencia en
  `ext_<fecha>.no_verificable.csv`; `ext_<fecha>.csv` y la fecha quedan libres para el disparo bueno. Nace
  `data/backups/sello_dinero_no_verificables.csv`. `estado()` y `/api/dinero/sellos` sirven `intentos_no_verificables`,
  `ultimo_intento` y `nota_intentos` dentro de `E0`. Un insumo no persistido (cambio de juego) ya no inserta (R1).
- Lo que NO cambia: las sesiones del 28-sep, 6-oct y 7-oct siguen perdidas; N sigue en 12 hasta el primer sello E0.3;
  `version_reglas` se mueve en la 16-3 (§99.5); el timer no se toca.

## Lo firmado que sigue por ejecutar (actas §93, §95, §99)
- **16-3:** fuente única `linea_base.cargar()` para API, Telegram y dashboard (§93.4, 93.4-bis ii), `analisis_puntaje_ia`
  adentro (§99.6), README (§93.11, universo de §95.4, `version_reglas` 0.3.0-PROPUESTA §99.5), fusión de tarjetas
  (§93.12), badge `tests_recolectados` (§90.4, hoy desfasado), lo demás de §93.14; y de la 16-2: §81.3 (R3), §81.4 (R4),
  §81.6 (la pantalla) si se firman.
- Sin dueño: R3, R5, R6, R7, R9 del dictamen 16-1; F4 (clon del sábado, D.2) al `estadistico-adversario`; regla de §58
  cerrada por V4 y no reiniciada (§99.3); sonda sin tocar (§99.4).
## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers del riel + `mki-sonda-cierre` + `mki-sello-dinero`; el modo se le
  pregunta a `modo.py`. Modelo 4.6.0; `PLATAFORMA_VERSION` 5.1.0. Ningún job disparó durante la corrida (domingo).
- Riel de medición: lunes 12-oct es la primera sesión con la guarda de frescura y el vigía de la 16-1 (predicciones en
  `bitacora_16_1.md` §7). Residuo conocido: 24 filas del 28-sep invertidas, fuera de `verificacion_puntaje`.
- **Dinero:** todo SIMULADO. E0: **12 cuentan de 40**, 22 fechas selladas, todas `E0.2`; dos quemadas por disparo fuera de
  hora (28-sep, 7-oct) y una sin filas (6-oct). Universo de 32 desde el 5-oct (§95.4, §98).
## Deuda
`test_motor.py` trunca inclusive; skill `gate` importa `scipy`/`sklearn` (§69); `tesis.md:161` «59×» (§76); PIN de la
regla maestra a `xfail` estricto (R4 del 16a); el rechequeo sin negativa aún dice el literal «20:30» (§80.5);
`available_at` computado por calendario y no observado decide tabla desde E0.3 (§72, no firmado).
## Lo más urgente, que sigue siendo de Nicolás
**Commitear la 16-1 y la 16-2** (una lista en cada bitácora; el hook corre la suite ~8 min); **aplicar los tres parches
con su acta** antes del martes 00:30 (§81.1); cinco commits sin pushear; las firmas de §80 y §81; E1 (§93.15); las dos
firmas del pre-registro secuencial (§2a-ter y el MDE) **antes del 19-nov-2026**.
