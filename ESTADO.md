# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 30-sep-2026 (corrida 15, nocturna).

## Primero: hoy 30-sep a las 18:15 es la primera prueba viva de la guarda (b), y dos actos con fecha
0. **Mirar el sello de hoy entre las 18:15 y las 19:05** (PREDICCIÓN falsable: `snapshot.log` con `'snapshot': True, 'predicciones': 8`;
   vigía en silencio). **No lanzar la corrida 16 esta noche** (dictamen del director): se diseña hoy, se corre después.
1. **`mki-noticias` no analiza nada desde el 7-sep**: 17 corridas con «credit balance is too low», `analizados 0`,
   `resultado 'ok'` en el ledger; el vigía dice OK. Reponer crédito es un acto de cinco minutos (**§74**). Los
   sentimientos sellados desde el 7-sep se apoyan en análisis de hasta el 4-sep (deducido).
2. **`verificacion_puntaje` absorbe las 24 filas del 28-sep alrededor del 5-oct**: su verificador no aplica ni la regla
   maestra ni la de conocibilidad (**§73**); una de dos frases de Nicolás lo cierra antes de esa fecha.

## Lo que la corrida 15 dejó aplicado en el árbol real (acta §92)
- **Guardas de conocibilidad de §90.1, corte de método 29-sep 23:22:17:** el verificador marca `no_verificable_timing`
  toda fila `pendiente` con `available_at > timestamp_utc`; `snapshot.py` se niega a sellar si la sesión del SOX no
  cerró (`available_at > emisión`, margen cero); la capa de medición excluye por regla. Si hoy el sello se niega, el
  vigía alerta dos fallas a las 19:00 y **no se retracta** (§72).
  Alcance hoy: 24 filas del 28-sep, 8 con verificación; **ninguna cifra publicada cambió**. Lo que NO cubre: las
  métricas vivas de 30 días de `senales.py` (Telegram, dashboard, API) cuentan hoy 8 de 160 filas invertidas.
- **README sin contador** (§90.3), badges congelados «1025 recolectados al 2026-09-29» (§90.4), 354/360 y 61× como
  marcadores (§88.5). Suite del árbol real, 23:29:33 del 29-sep: **1019 en verde, 5 saltados, 1 xfail, 0 rojos**.
- **`mki_backup.py` no se adelanta al sello** (§90.8): con `snapshot.py` vivo nunca commitea; en día de semana sin
  sello antes de las 18:15 se niega; elecciones de agente en **§70**.
- **§90.2 (el ancla) DETENIDA:** las dos anclas difieren en 33 filas de 5 fechas; la premisa del encargo tiene contraejemplo (**§71**).

## Regla de §58, sellada antes del primer dato de madrugada
`GEMELO/propuestas/regla_58.md`, 23:08:17 del 29-sep, sha256 `ca2ccd53…` (anexo 1 `2c9eec1d…`); dictamen y re-dictamen
incorporados. K = 10 noches válidas, primera candidata la sesión del 29-sep, plazo la del 26-oct. **Hallazgo:** toda hora
candidata de (b) es posterior a la medianoche NY y con el código vigente pierde los viernes (`dia_sin_sesion`); la rama
(b) lleva umbral 5 de 10 y con la tasa del antecedente (3/11) se indica con probabilidad 0,11. **Firmarla es de Nicolás.**

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers del riel + `mki-sonda-cierre` + `mki-sello-dinero`; el modo se le
  pregunta a `modo.py`. Modelo 4.6.0; `PLATAFORMA_VERSION` 5.1.0. Del 2-nov-2026 al 12-mar-2027 la holgura entre las
  18:15 de Chile y el cierre de XNYS es de 15 min (MEDIDO, `exchange_calendars`, §66 C.2). La máquina no corrió del
  **25-sep 03:37:10 al 28-sep 14:42:52** (latido del journal del sistema, ±30 s); que fuera suspensión es INFERENCIA.
- **Dinero:** todo SIMULADO. E0: 15 sesiones selladas, **9 cuentan de 40**; las del 28 y del 29 perdidas. `dinero/sello_dinero.py`
  intacto; el parche de §62 (camino T) espera acta (**§75**): la (a) firmada choca con la `UNIQUE` de la tabla. **8035.T:**
  split 5:1 con fecha 29-sep; el «17» de `roca_chip` del 28 era artefacto; releído 39 (DESCRIPTIVO, **§68**).

## Deuda
- `tests/test_motor.py` trunca inclusive (ciego a una barra no liquidada EN `t`); el vigía prueba `av == ts` y no orden
  (**§67**); la skill `gate` importa `scipy`/`sklearn` (**§69**); `tesis.md:161` dice «59×» (**§76**). Corrida 16 (se
  diseña el 30-sep, §91.2): deudas (3) y (4) de la sonda; el lector no filtra «fuera de grilla».

## Lo más urgente, que sigue siendo de Nicolás
**§74** (crédito) y **§73** (antes del 5-oct); **§58** (firmar la regla); **§71**, **§75**, **§70**, **§72**, **§76**;
las dos firmas del pre-registro secuencial (§2a-ter y el MDE) **antes del 19-nov-2026**. **No hay push.**
