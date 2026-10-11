# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 10-oct-2026 (corrida 16-1, nocturna con Nicolás; acta §100).

## Primero: la corrida 16-1 está aplicada al árbol real y SIN commitear; el commit es de Nicolás
0. **Corte de método 10-oct 23:12:48.** Cuatro bloques en el árbol real: guarda de frescura en `snapshot.py` (§93.8 b),
   el vigía con negativa declarada + epílogo, igualdad Y orden del ancla, y el predicado de `verificacion_puntaje` en
   `mode=ro` (§93.8 d, §93.9, §95.2 R3), la cuenta de excluidas en el retorno del verificador (§95.2 R2), y el ledger de
   noticias con `error_analisis` (§93.3 ii). Dictamen APLICABLE CON EXIGENCIAS, las tres bloqueantes de código
   atendidas antes de aplicar. Lista de archivos para el commit al final de `GEMELO/resultados/bitacora_16_1.md`.
1. **Lunes 12-oct, predicciones falsables** (bitácora 16-1 §7): snapshot 18:15 sin `NEGATIVA DECLARADA` y con
   «verificador puntaje: N verificadas, 24 excluidas por conocibilidad (fechas: 2026-09-28)»; vigía 19:00 con el séptimo
   chequeo «OK guarda puntaje: 24 fila(s) invertida(s) fuera … (2026-09-28: 24); 0 dentro»; 20:30 en silencio.
2. **Tarjeta §80** (6 elecciones de agente, 2 hechos de entorno, 5 recomendadas sin dueño); la lista de permisos
   **deniega** `cp senales.db *` y las otras dos copias aunque estén en ella.

## Lo que cambia en operación desde el lunes
- Un día con la fuente atrasada (H0 de §72) **no sella**: `snapshot.log` lleva `NEGATIVA DECLARADA [insumo_no_fresco]
  fecha=… sox_fecha=…`; el vigía manda un mensaje 🟡 («NO sellado por negativa declarada… no es falla»), y a las 20:30
  cierra el caso (retractación si sello; «caso cerrado por hoy» si no, marcador en pie). La guarda (b) de §90.1 también
  declara su negativa (`sesion_sox_abierta`). Sin `sox_fecha`, se sella como antes (reloj de pared, alerta del vigía).
- El vigía alerta la INVERSIÓN (`available_at > timestamp_utc`), no sólo la igualdad; y declara ilegibles sin morir.
- El ledger de noticias ya no dice «ok» cuando la API rechaza el lote: `error_analisis` + `error_tipo` + `error_lote`,
  sin texto de la API; el vigía lo trata como falla. «freno_presupuesto» y «0 sin pendientes» siguen OK.
- Desde el **2-nov-2026** la holgura 18:15 Chile → cierre XNYS es de 15 min (125 de 308 sesiones hasta fin de 2027,
  MEDIDO por el auditor); la guarda no agrega margen. Cuántos días negará no tiene historia (S1/S2 del dictamen).

## Lo firmado que sigue por ejecutar (actas §93, §95, §99)
- **16-2:** camino T de §62 (§93.7, §99.2) sobre el sellador que cambió la 16b, con acta de aplicación propia.
- **16-3:** fuente única `linea_base.cargar()` para API, Telegram y dashboard (§93.4, 93.4-bis ii), `analisis_puntaje_ia`
  adentro (§99.6), README (§93.11, universo de §95.4, `version_reglas` 0.3.0-PROPUESTA §99.5), fusión de tarjetas
  (§93.12), badge `tests_recolectados` (§90.4, hoy desfasado), lo demás de §93.14.
- Sin dueño: R3 (registro durable de negativas), R5, R6, R7, R9 del dictamen 16-1; F4 (clon del sábado, D.2) al
  `estadistico-adversario`; regla de §58 cerrada por V4 y no reiniciada (§99.3); sonda sin tocar (§99.4).
## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers del riel + `mki-sonda-cierre` + `mki-sello-dinero`; el modo se le
  pregunta a `modo.py`. Modelo 4.6.0; `PLATAFORMA_VERSION` 5.1.0. Ningún job disparó durante la corrida (sábado).
- Riel de medición: 5 al 9-oct sellados, 8 predicciones, 28/28 (6-oct tarde, 19:37, retractado). Residuo conocido: 24
  filas del 28-sep invertidas, fuera de `verificacion_puntaje`. Noticias: ~1000 analizados/día; pendientes 4289 → 340.
- **Dinero:** todo SIMULADO. E0: **12 cuentan de 40** (5, 8 y 9-oct cuentan; 6-oct sin filas por corte de luz; 7-oct
  `no_verificable_timing` por disparo de recuperación a las 10:30, §99.1). Universo de 32 desde el 5-oct (§95.4, §98).
## Deuda
`test_motor.py` trunca inclusive; skill `gate` importa `scipy`/`sklearn` (§69); `tesis.md:161` «59×» (§76); PIN de la
regla maestra a `xfail` estricto (R4 del 16a); el rechequeo sin negativa aún dice el literal «20:30» (§80.5).
## Lo más urgente, que sigue siendo de Nicolás
**Commitear la 16-1** (lista en la bitácora; el hook corre la suite ~8 min; fuera de 17:50–20:30 de un día hábil o el
sábado/domingo); **cinco commits sin pushear** (cuatro backups + éste; no hay push); las firmas de **§80**; E1 (§93.15):
licencia del `ibapi` e IB Gateway en WSL; las dos firmas del pre-registro secuencial (§2a-ter y el MDE) **antes del
19-nov-2026**.
