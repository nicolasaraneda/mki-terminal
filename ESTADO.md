# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 4-oct-2026 (corrida 16b, nocturna; acta §96).

## Primero: el parche de TOELY (§95.4) NO está aplicado; aplicarlo es acto de Nicolás antes del lunes 23:30 NY
0. **La 16b venció su reloj** (sesión pausada 3 h entre dos llamadas: aplicación exigida a las 16:45, trabajo real desde
   las 19:18). Por la letra del encargo el parche quedó en `GEMELO/propuestas/parches/toely_fuera_insumo_e0_16b.diff` con
   tests y dictamen, **sin aplicar**. La salva el `git apply` (el sellador lee el árbol), antes del sello del 6-oct 00:30 Chile; el
   commit es registro y el hook lo rechaza el lunes entre 17:50 y 20:30 (receta: `bitacora_16b.md` §5). **Martes 6-oct:** consultas §6 de las dos bitácoras.
1. **Lunes ~17:52: primera lectura del crédito repuesto** (§93.2, 10 USD el 4-oct): `data/costos_ia.log` con
   `analizados > 0`. Pendientes acumulados al 2-oct: 4289 (20 corridas con «credit balance is too low» desde el 7-sep).
2. **E0 no suma desde la sesión del 24-sep** (9 de 40): TOELY sin cierre en la fuente desde el 25-sep (§95.4). La sonda sigue
   con 36 tickers, TOELY incluido: su «noche completa» (§58) y el `insumo_completo` del sellador divergen cuando el parche entre (**§79**).

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
- **Dinero:** todo SIMULADO. E0: 18 sesiones selladas, **9 cuentan de 40**; 29-sep a 2-oct no cuentan por TOELY (§95.4), el
  28-sep por timing. `dinero/sello_dinero.py` y `reglas.json` intactos en el árbol real: el parche 16b (clave `exclusiones_insumo_e0`
  en `reglas.json`, filtro en `decidir`, 33 → 32 operables, `reglas_sha256` distingue las filas) espera la mano de Nicolás.

## Deuda
`tests/test_motor.py` trunca inclusive; la skill `gate` importa `scipy`/`sklearn` (**§69**); `tesis.md:161` dice «59×»
(**§76**); del auditor 16a (§78): comparación de instantes duplicada, PIN a `xfail` estricto, cuenta de excluidas sólo en el log.

## Lo más urgente, que sigue siendo de Nicolás
**Aplicar a mano el parche 16b y commitear** (actas §95 y §96; lista al final de `bitacora_16b.md`) antes del lunes
23:30 NY; **§79** (versión de reglas, sorteo y sonda tras TOELY); la corrida 16 (se diseña con §93, §95 y las bitácoras
16a/16b a la vista); las dos firmas del pre-registro secuencial (§2a-ter y el MDE) **antes del 19-nov-2026**. **No hay push.**
