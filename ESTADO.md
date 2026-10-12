# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 11-oct-2026 (corrida 16-3, nocturna con Nicolás; acta §104).

## Primero: lo que la 16-3 aplicó al árbol real y Nicolás commitea antes de las 17:50 del lunes 12-oct
0. **La 16-3 está aplicada al árbol real y SIN commitear** (corte de método en `bitacora_16_3.md` §6; lista de rutas en §9).
   Desde el reporte de Telegram del lunes 18:25, la API y el dashboard, **las cifras de acierto salen de
   `backtest/linea_base.py` (fuente única, §93.4) y excluyen las filas con `available_at > timestamp_utc`**: track record
   30 d n 149 → 141 al 11-oct (gap 62,4 % → 63,8 %); `analisis_puntaje_ia` igual. Tabla completa en la bitácora §2.
1. **El parche de `dinero/` NO está aplicado:** `GEMELO/propuestas/parches/version_reglas_16_3.{diff,md}` (`version_reglas`
   0.3.0-PROPUESTA, R2, R4, §81.3 b). Va en una noche sin otro cambio al sellador, después del primer sello E0.3 del
   martes 13-oct a las 00:30; quién y cuándo, tarjeta §89. Dictamen del auditor en `dictamen_16_3/`.
2. **Tarjetas nuevas §82 a §89** en `espera_firma.md` (dedup de las cifras vivas y las seis funciones de `senales.py`;
   R6+§80.5; R3; R7; S2; F4; candado §81.5 b; el parche de `dinero/`). §80 y §81 firmadas (§102); §69, §70, §72 y §74
   FUNDIDAS (§93.12). Crédito de noticias (ex §74) repuesto el 4-oct. Predicciones del lunes 12-oct: bitácora §7.

## Lo que cambia en operación desde el lunes
- Telegram 18:25: «Track record (modelo 4.6.0, 30d): N=…» ya sin las 8 filas del 28-sep; cobertura del 80 % sobre 482+.
- `/api/hoy`, `/api/aperturas`, `/api/historial`: mismas claves, valores sin las invertidas (`api/CONTRATO.md`,
  enmienda 16-3). La API deja de correr `init_db()` sobre `senales.db` en esas rutas (`mode=ro`).
- Si el fallback del dashboard (Streamlit) se niega a sellar por regla, la negativa queda en `data/snapshot.log` y el
  vigía la lee como negativa, no como falla (R9). `/sellos` muestra «intentos no verificables: N; último: …».
- La suite ya no crea `senales.db`/`noticias.db` en un árbol sin bases (guarda en `tests/conftest.py`); ocho archivos de
  tests saltan por «tabla con filas» y no por «archivo presente» (R5).
- Lo que NO cambia: `motor.py`, `snapshot.py`, `senales.py` (byte a byte), el vigía, la sonda, el backup, `dinero/`, los
  timers; ninguna fila sellada; ningún esquema. E0: 10 de las 22 fechas selladas no cuentan y dos noches (25-sep, 6-oct) no
  tienen filas; ninguna se recupera (§57).

## Lo firmado que sigue por ejecutar
- Aplicar `version_reglas_16_3.diff` (§99.5, §102.4, §102.6 (3); tarjeta §89). Las firmas de §82 a §89.
- Cola (§102.2): R3 (§84), R6+§80.5 (§83), R7 en noviembre (§85), S2 (§86), F4 al adversario (§87), candado (§88).
## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers del riel + `mki-sonda-cierre` + `mki-sello-dinero`; el modo se le
  pregunta a `modo.py`. Modelo 4.6.0; `PLATAFORMA_VERSION` 5.1.0. Ningún job disparó durante la corrida (domingo).
- Riel de medición: lunes 12-oct, primera sesión con la guarda de frescura y el vigía de la 16-1 (predicciones en
  `bitacora_16_1.md` §7) y con la fuente única (`bitacora_16_3.md` §7). Residuo: 24 filas del 28-sep invertidas, fuera de
  `verificacion_puntaje` y, desde hoy, fuera de toda cifra publicada.
- **Dinero:** todo SIMULADO. E0: **12 cuentan de 40**, 22 fechas selladas, todas `E0.2` (18 con 33 operables, 4 con 32);
  el primer sello `E0.3` es el del martes 13-oct 00:30 (predicción §103.6). `version_reglas` sigue 0.2.0-PROPUESTA
  hasta que entre el parche.
## Deuda
`test_motor.py` trunca inclusive; skill `gate` importa `scipy`/`sklearn` (§69, fundida); PIN de la regla maestra a `xfail`
estricto (R4 del 16a); el rechequeo sin negativa dice «20:30» (§80.5, va con §83);
`available_at` computado y no observado decide tabla desde E0.3 (§72); `respaldar_extension` con `DIR_BACKUP_EXT` por
defecto (la guarda del conftest lo caza); las seis de `senales.py` sin consumidor (§82.2); el riel de dinero sin vigía (§89).
## Lo más urgente, que sigue siendo de Nicolás
**Commitear la 16-3** (lista en `bitacora_16_3.md` §9; el hook corre la suite ~8 min; antes de las 17:50 del lunes);
leer el lunes las predicciones de las bitácoras 16-1 y 16-3 y el martes la de §103.6; aplicar el parche de `dinero/` con
su acta (§89); las firmas de §82 a §89; E1 (§93.15); las dos firmas del pre-registro secuencial **antes del 19-nov-2026**.
