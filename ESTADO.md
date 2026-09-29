# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 28-sep-2026 (corrida 14).

## Primero: `espera_firma.md` §61
**El reporte de las 18:25 ya salió** compuesto desde el sello del 28-sep, o sea desde las filas que
`snapshot.py` construyó **a las 13:42 de Nueva York, con la bolsa abierta**, y publicó `roca_chip` **44**.
El recomputado tras el cierre es **17**, pero **PROVISIONAL**: el job de las 18:15 marcó `8035.T` con un
salto de **−80 %** (`data/snapshot.log:147`, «revisar split/dato corrupto») y ese solo ticker explica
~83 % del movimiento del crudo. **Contrastar 8035.T antes de citar el 17.**
Esas 24 filas son la **única fecha de toda la historia sellada** con `available_at > timestamp_utc`: el sello
declara su insumo conocible 2 h 17 min después de existir (la suspensión es **inferencia**: WSL2 no registra
suspend/resume). Veredicto del `auditor-lookahead`: `FILAS INVÁLIDAS ENTRARON COMO VÁLIDAS`; no hay
look-ahead, pero las 8 predicciones son
`beta × (−1,63)` sobre una lectura intradía etiquetada como cierre, **no reproducible por un tercero, y de
forma irreversible**: la sonda de las 20:05 NY midió que la barra del 28 que estaba a las 13:42 **ya no la sirve la fuente** para 35 de 36 tickers.
`senales.py` no compara `available_at` con `timestamp_utc`; `dinero/sello_dinero.py` sí, y descartó sus
33 filas del mismo evento. **Nada publicado está contaminado** (corte del README: 28-ago). **Daño medido a las 17:31:**
insumo −1,63 → −1,61 (0,02 pp, mismo signo), **0 de 8 direcciones invertidas**, régimen **idéntico**; peor
predicción entre los siete tickers sin dato marcado **0,03 pp** (el 0,11 es de 8035.T, de su beta
reestimada). El auditor **ratificó el veredicto con fuerza neta MAYOR**: la medición **confirma** la
no-reproducibilidad que antes sólo deducía. **No decide la regla** en ninguna dirección. **Sigue SIN
MEDIR** `puntaje_ia` y `divergencias` del 28: **24 filas** rumbo a `verificacion_puntaje` el ~5-oct, y esa
diferencia ya no se puede medir.
**Por eso los bloques 2 (erratas de los README) y 3 (`bifurcaciones`) NO se ejecutaron:** publican
cifras, y §88.5 sigue sin aplicar.

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers del riel + `mki-sonda-cierre` + `mki-sello-dinero`,
  emite; el modo se le pregunta a `modo.py`. Modelo 4.6.0; `PLATAFORMA_VERSION` 5.1.0.
- **La corrida 14 no tocó el camino de sellado** (`motor.py`, `senales.py`, `snapshot.py`, `universo.py`, `dinero/sello_dinero.py`). Todo cambio de base es de un timer: `noticias.db` 17:52:39, `senales.db` 18:15:12 (4 filas a `verificacion_puntaje`), `sello_dinero.db` intacta. **HEAD lo movió el backup de las 18:40 a `f7b65e0`**, con sólo `data/backups/`.
- **Sesión del 25-sep perdida en los TRES rieles**; §57 no la recupera, y la del 28 también se pierde en el riel de dinero (§62).
- **Medición** (`VISION.md` §80): cifras en el README; **el IC95 de día contiene el cero**, §46 NO cableada, ventaja **no capturable** (§10).
- **Dinero:** todo SIMULADO. **E0: 14 sesiones selladas, 9 cuentan de 40** (no cuentan 09, 18, 22, 23 por `insumo_incompleto` ni el 28 por `no_verificable_timing`; señal = sorteo sin información: maquinaria, no track record). **E1 NO EJECUTADO**, cuenta IBKR **en revisión al 19-sep**. E2: 500 USD, no iniciado.

## Corrida 14 (acta §89)
- **Sonda:** `sesion_atribuida()` — lo anterior a la apertura pertenece a la sesión hábil previa, y reproduce el `sesion_ny` de las **1.188 filas ya escritas** (0 diferencias): sin columna nueva ni reescrituras. Reloj de la noche monótono; el resumen **descarta y declara** lo previo al cierre. Franja `Tue..Sat 00..03:05,35` **propuesta**.
- **§58, DESCRIPTIVO, 4 noches:** coincide **ticker por ticker** con el meta del sello por dos vías independientes; el 22-sep **34 de 36 sin cierre a las 23:35 NY**, y eso no lo arregla ninguna noche más de la grilla actual. **No se recomendó nada.** El 28 no cuenta como quinta porque **no va a tener segunda vía**; cuesta **un día**, no una semana.
- **M2: §9 de `dinero/preregistro_dinero.md`**, PROPUESTA y **NO APLICABLE: le faltan seis definiciones**
  (la urgente, qué es «el primer aporte»). El umbral firmado es **3× más duro** a 52 semanas: `medio` dispara en **19/20** semillas simuladas, conservador (3,9 %/año) en 0/20.
- Intentos sin cambio: gap asiático **354**, veredicto 5.1 **360**, riel largo **4**.

## Deuda
- **Suite con 2 rojos permanentes** (`tests/test_readme.py`): contador vivo de E0 que nada regenera y badges vencidos (904 tests bajo `tests/`, 5.1.0); la sección de E0 **no existe en español**, de ahí el test (§65).
- `tests/test_motor.py` trunca con `<= fecha`, **inclusive**: ciego a una barra no liquidada EN `t`.
- «Lecturas de criterio» (§43) sin sitio. `bifurcaciones` sin tocar (§88.6). **Dos skills contradicen a la máquina** (bitácora 8.5-bis): el gate de `gate` importa `scipy`/`sklearn`, que el proyecto **no** tiene a propósito, y el recordatorio de `cierre-sesion` es pre-switch.

## Lo más urgente, que sigue siendo de Nicolás
**§61** (antes de las 18:15 del 29: a esa hora el verificador escribe las 8 filas); **§65** junto con él; **§58**; **§62** a **§64**; **§43**; y las dos firmas con fecha del pre-registro secuencial (§2a-ter y el MDE) **antes del 19-nov-2026**, que ninguna corrida puede hacer por él. **No hay push.**
