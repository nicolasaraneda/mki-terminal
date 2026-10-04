# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 4-oct-2026 (corrida 16a, diurna).

## Primero: el lunes 5-oct a las 18:15 es la primera prueba viva de la guarda de `verificacion_puntaje`
0. **Commit de la 16a antes de las 17:50 del 4-oct** (lista de archivos al final de `GEMELO/resultados/bitacora_16a.md`);
   si no entra, las 24 filas del 28-sep entran el lunes y se declara (§93.4-bis i). **Martes 6-oct en la mañana:**
   correr la consulta de la bitácora §6 (PREDICCIÓN falsable: 0 filas del 28-sep en `verificacion_puntaje`, una línea
   `AVISO verificador puntaje: 24 fila(s) …` en `snapshot.log`, las 3 del 24-sep entran como siempre).
1. **Lunes ~17:52: primera lectura del crédito repuesto** (§93.2, 10 USD el 4-oct): `data/costos_ia.log` con
   `analizados > 0`. Pendientes acumulados al 2-oct: 4289 (20 corridas con «credit balance is too low» desde el 7-sep).
2. **E0 no suma ninguna sesión desde la del 24-sep**: TOELY sin cierre en el insumo desde esa fecha, 5 noches seguidas
   `insumo_incompleto` (**§77**, hallazgo de la 16a). La lectura de la regla de §58 (K = 10 desde el 29-sep) llega
   confundida por él si sigue así. Verificar la fuente es un acto de cinco minutos (opción b).

## Lo que la corrida 16a dejó aplicado en el árbol real (acta §94, 4-oct 13:51:31, corte de método)
- **Guarda de conocibilidad en `verificar_puntaje_pendientes`** (§93.4-bis i): ninguna fila con `available_at >
  timestamp_utc` entra a `verificacion_puntaje`; no se escribe ni se cambia `estado`; una línea de aviso por corrida en
  `snapshot.log`. Hoy no-operativa (3 candidatas limpias); el lunes excluye exactamente las 24 del 28-sep. Auditor:
  APLICABLE CON EXIGENCIAS; elección del trato a ratificar (**§78**). La regla maestra sigue ausente ahí (§93.4).
  `analisis_puntaje_ia` **no entra** a la fuente única de §93.4 (`linea_base.py` sin «puntaje»): hueco para la 16.
- Badge congelado `tests_recolectados = 1025` desfasado en +13 (1038); lo actualiza la 16 (§90.4). La suite del worktree
  no pudo correr con las bases (permiso denegado); el control sobre HEAD puro atribuye sus rojos al entorno (bitácora §4.1).

## Lo que la corrida 15 dejó aplicado (acta §92) y lo firmado en §93
- Guardas de conocibilidad de §90.1 (corte 29-sep 23:22:17): verificador de apertura, `snapshot.py` (margen cero) y la
  capa de medición. 30-sep, 1 y 2-oct sellaron a las 18:15:01 con 8 predicciones, 28/28; la guarda (b) no se negó; vigía
  en silencio. README sin contador; `mki_backup.py` detrás del sello; §90.2 DETENIDA (§71).
- **Firmado en §93 (4-oct), por ejecutar en la corrida 16:** fuente única `linea_base.cargar()` para API, Telegram y
  dashboard (§93.4); ledger/vigía distinguen «0 con error» (§93.3 ii); guarda de frescura + vigía con epílogo (§93.8);
  vigía prueba orden (§93.9); camino T de §62 firmado, aplicación con acta propia (§93.7, §75); README (§93.11); fusión
  de tarjetas (§93.12); regla de §58 firmada tal cual (§93.5; script de evaluación con datos sintéticos). E1 máxima
  prioridad (§93.15): usuario de práctica y gateway, actos de Nicolás.

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers del riel + `mki-sonda-cierre` + `mki-sello-dinero`; el modo se le
  pregunta a `modo.py`. Modelo 4.6.0; `PLATAFORMA_VERSION` 5.1.0. Del 2-nov-2026 al 12-mar-2027 la holgura entre las
  18:15 de Chile y el cierre de XNYS es de 15 min (MEDIDO, §66 C.2). Sin suspensión del 30-sep al 4-oct (latido del journal).
- **Dinero:** todo SIMULADO. E0: 18 sesiones selladas, **9 cuentan de 40**; las del 28-sep al 2-oct no cuentan (TOELY,
  **§77**). `dinero/sello_dinero.py` intacto. **8035.T:** split 5:1 con fecha 29-sep; el «17» del 28 era artefacto (**§68**).

## Deuda
`tests/test_motor.py` trunca inclusive; la skill `gate` importa `scipy`/`sklearn` (**§69**); `tesis.md:161` dice «59×»
(**§76**); del auditor 16a (§78): comparación de instantes duplicada, PIN a `xfail` estricto, cuenta de excluidas sólo en el log.

## Lo más urgente, que sigue siendo de Nicolás
**Commit de la 16a** (hoy, antes de las 17:50); **§77** (TOELY, verificar la fuente) y **§78** (ratificar); la corrida 16
(se diseña con §93 y la bitácora 16a a la vista); las dos firmas del pre-registro secuencial (§2a-ter y el MDE) **antes
del 19-nov-2026**. **No hay push.**
