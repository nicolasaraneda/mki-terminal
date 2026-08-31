# Bitácora nocturna — corrida autónoma 31-ago-2026

Corrida sin supervisión. Nicolás no contesta durante esta sesión. Una línea
por hito, hora UTC. Los entregables completos viven en sus propios archivos;
acá solo el rastro de qué se hizo y cuándo.

- 14:52 UTC — Arranque. Creados `GEMELO/MICRO/` y confirmado `GEMELO/resultados/`.
  Toolchain: gcc 15.2.0 y make presentes en el sistema. `DECISIONES.md` tiene
  3632 líneas (no se lee entera en esta sesión; se delega).
- 14:53 UTC — Cifras canónicas cargadas via skill `cifras-canonicas`: ventana
  sellada `excluir_cero` n=248, modelo 66.1%, base 59.7%, +6.5pp, McNemar
  p=0.1849. Ventana larga n=14618, +19.1pp Tokio / +16.8 Taipéi / +15.4 Seúl /
  +2.5pp Fráncfort (p=0.111 — nota: el prompt de la corrida decía +19,1pp a
  1,75h y +2,5pp a 8,75h; la skill no repite las horas pero confirma las pp y
  el patrón de decaimiento con la distancia).
- 14:54 UTC — Despachados en paralelo `orientador` (estructura de
  GEMELO/DISEÑO.md, mecanismo del decaimiento, WS4/WS5, §34.9, "efecto
  estampida", pin de pandas, docs/SOMBRA.md) e `integridad-datos` (esquemas
  de senales.db/noticias.db, n verificable hoy, ritmo de sellado, estructura
  de los CSV de backup, PRAGMAs sqlite). Ambos completados ~15:26 UTC —
  hallazgos incorporados directamente a los documentos de este frente sin
  volver a leer los archivos fuente completos.
- 15:00–15:20 UTC — Frente 1B construido: `micro/` con arnés en C puro
  (comun.h/c + 6 binarios: reloj, syscall, jitter, memoria, mensaje, red),
  Makefile con `-O2 -Wall -Wextra -Werror`, sin dependencias fuera de libc
  (syscall() vía `_GNU_SOURCE`, sockets POSIX). Dos bugs de implementación
  encontrados y corregidos por la propia compilación/ejecución: ruta relativa
  mal armada (`micro/resultados/…` en vez de `resultados/…`, el binario corre
  con cwd=micro/) y `JB_MAX_CAMPOS` insuficiente (64→128, bench_jitter con 4
  objetivos genera ~80 campos y abortaba). `make test` (tests/test_arnes.sh)
  pasa: verifica que una espera pedida de 1000us se reporta dentro de 3x de
  tolerancia y que el costo del reloj está bajo el umbral de sanidad de 10us.
- 15:22 UTC — Suite completa corrida (`make ejecutar`, ~8s) y repetida 5 veces
  para chequear estabilidad del piso de jitter. Hallazgo central de 1C: el
  exceso de `nanosleep()` sobre lo pedido es **prácticamente constante,
  ~72–85 µs, independiente de si se piden 10µs o 10.000µs** (10us→72.3µs
  exceso p50, 100us→73.1µs, 1000us→78.6µs, 10000us→85.2µs; reproducido en 5
  corridas con desviación &lt;1µs). Esto es la firma de un piso de granularidad
  del planificador/temporizador de la capa de virtualización, no ruido de
  aplicación. `syscall(SYS_getpid)`: p50=290ns pero max=57.459ns (198× el
  p50) — cola larga típica de interrupción de VM. JSONs en
  `micro/resultados/*.json`. Detalle completo en `GEMELO/MICRO/WSL2.md`.
- 15:35 UTC — Despachado `escriba-decisiones` #1 para `GEMELO/MICRO/DISEÑO.md`
  (pre-registro de la pista de microtrading, 9 secciones, V1-V5/R1-R4). Escrito
  y verificado (290 líneas, estructura correcta). Yo mismo escribí
  `GEMELO/MICRO/WSL2.md` (evidencia del piso de jitter), `piso_de_latencia.md`
  (veredicto: la lectura "captura en vivo" muere por 3-4 órdenes de magnitud
  en la red — connect() a 1.1.1.1:443 dio p50=8.79ms/p99=36.76ms vs. los
  cientos de ns que exige HFT colocado; la lectura "pipeline RTL académico,
  validado por backtest" sobrevive intacta) y `fpga.md` (iCE40HX1K ~1280 LUTs
  sin multiplicador dedicado vs Artix-7 ~63.400 LUTs + 240 DSP; el mínimo que
  la pregunta exige — parser+comparador — cabe en el iCE40, una combinación
  ponderada de features ya lo aprieta; elección de placa marcada como decisión
  de Nicolás). Frente 1 (1A-1E) completo salvo el dictamen final del guardián.
- 15:40 UTC — Despachado `escriba-decisiones` #2 para `GEMELO/RELEVO.md`
  (protocolo de relevo de MODELO_VERSION, Frente 2) — en curso en paralelo.
- 15:45 UTC — Frente 3: recalculado desde `senales.db` en modo lectura
  (b=72, c=56 sobre las 248 filas `excluir_cero`, reproduce 66.1%/59.7%/
  p=0.1849 exacto). Con `evaluacion.py` (Connor 1987 para McNemar): n
  necesario para potencia .80/α.05 = **163** para detectar +15.66pp (YA
  SUPERADO, n=248 > 163 — evidencia EN CONTRA de que el régimen en vivo
  tenga un efecto de esa magnitud, no solo "faltan datos") y **957** para
  detectar +6.5pp (faltan 709 filas, ~101-118 días hábiles al ritmo medido
  de 6-7/día hábil, ~mediados ene-feb 2027). CI 95% de la ventaja sellada:
  [-2.45pp, +15.36pp] — roza pero NO excluye limpiamente el +15.66pp
  (margen de 0.3pp, menor que el propio redondeo) ni excluye el cero:
  **el CI no discrimina hoy entre las dos explicaciones.** Diseñado (no
  ejecutado) el experimento discriminador: reconstrucción de
  `backtest/linea_base.py` restringida a las fechas exactas de la ventana
  sellada, comparada contra sellado-en-vivo y contra el agregado de ocho
  años, para separar "brecha backtest-vs-producción" de "cambio de época
  real". Entregable: `GEMELO/resultados/dos_ventanas.md`.
- 16:10 UTC — `estadistico-adversario` dictaminó **RECHAZADO** sobre
  `dos_ventanas.md` v1: las 248 filas no son independientes (34 fechas de
  emisión, 7.3 tickers/fecha, mismo signo dentro de una fecha porque el
  modelo sigue el signo del SOX), DEFF~2.5-3.6 medido por bootstrap de
  bloques/cluster, n_efectivo real 69-99, no 248 — la potencia real para
  +15.66pp es 44-59% (moneda al aire), no 93%, así que "no lo vimos =
  evidencia en contra" NO sostenía. También: cita de fuente equivocada del
  +15.66pp (es `auditoria_ws3.md`, no `DISEÑO.md` §2.8), módulo equivocado
  en el experimento del §4 (`linea_base.py` reproduce filas ya selladas,
  tautológico), y un carve-out no autorizado al conteo de intentos del DSR.
  Encontró además, sin que se lo pidiera, que **toda la ventaja sellada vive
  en 6 fechas de 15-23 jul (n=44, +40.9pp, p=0.0014); el resto (n=204) da
  -1.0pp, p=0.92**. Reproduje YO MISMO, independientemente y en modo
  lectura, cada cifra citada del dictamen (DEFF=3.60 vía bootstrap por
  fecha, potencias 43.9%/58.5%/93.4%, CI cluster [-10.04,+23.67]pp, n
  ajustados por DEFF 407-587/2427-3495, el desglose 15-23jul y el desglose
  por bolsa) antes de aceptar ninguna. Reescribí `dos_ventanas.md` v2 con
  todo corregido: retracté la conclusión de potencia, corregí la proyección
  de fecha (~dic-2027 a jul-2028, no ene-2027), reemplacé el CI de Wald por
  el bootstrap por cluster, rediseñé el experimento del §4 (complemento de
  la ventana larga, no el agregado; módulo `ventana_larga.py`, no
  `linea_base.py`; intento declarado N=26, sin carve-out), y agregué la
  concentración de 15-23jul como hallazgo principal nuevo. No se re-despachó
  una segunda revisión adversaria completa por presupuesto de la corrida;
  cada corrección específica del dictamen quedó atendida y verificada a mano.
- 16:45 UTC — Frente 5 (importador CSV) implementado y probado:
  `scripts/restaurar_backup.py` (nunca escribe en senales.db/noticias.db,
  siempre a ruta temporal nueva), `tests/test_restaurar_backup.py` (17 tests,
  todos verdes). Bug real encontrado y corregido en la primera corrida:
  `titulares.tickers`/`divergencias.explicacion`/`analisis.tickers_afectados`
  son `TEXT NOT NULL DEFAULT ''` — un vacío del CSV ahí es `''`, no `NULL`
  (el importador insertaba NULL y violaba la constraint). Hallazgo real al
  correr `--verificar` contra las bases reales: el backup del 30-ago tiene
  una fila `snapshots` fecha=2026-08-29 (plataforma 5.0.2) que la base viva
  ya no tiene, y la base viva tiene fecha=2026-08-28 (plataforma 5.0.3) que
  el backup no tiene — más 7 filas de `verificacion_apertura` del 27-ago en
  el backup ausentes en la base viva. **Confirmado más tarde por
  `guardian-constitucion` (18:0x UTC), citando DECISIONES.md §36.1/§36.7:
  no es pérdida de datos** — 2026-08-29 es la fila espuria de sábado que la
  §36.1 descarta, y las 7 filas del 27-ago las reemplazó la composición
  canónica del modo sombra (región `>=26-ago` = PC). `docs/RESTAURAR.md`
  actualizado para cerrar la alarma en vez de dejarla abierta.
- 17:50 UTC — Primer dictamen de `guardian-constitucion` sobre la tanda
  completa (los 6 frentes): **RECHAZADO**, tres motivos bloqueantes. R2:
  `docs/REPLICA.md` afirmaba que el push de la titular "ya es automático,
  vía los timers systemd" — falso, `mki_backup.py` dice "Jamás push"
  explícitamente. R4: 5 de 6 frentes sin acta en DECISIONES.md (solo el
  6A/§38 la tenía). R7: los 6 binarios ELF + `comun.o` de `micro/bin/` y
  los JSON de `micro/resultados/` no estaban en `.gitignore` — un binario
  en git es irreversible en la historia. Observaciones no bloqueantes:
  atribución incorrecta en §38.1 (el crecimiento de n 223→248 no es solo
  tiempo, la composición canónica del §36.7 también movió el n), encabezado
  de §38 partido en dos líneas, test placebo en
  `test_restaura_sin_tocar_las_bases_reales` (no verificaba nada de verdad),
  la alarma de `docs/RESTAURAR.md` sobre las filas del backup ausentes en
  la base viva SÍ tenía explicación en §36.1/§36.7 y se podía cerrar,
  `bench_red.c` abre una salida de red nueva no declarada, `.env` en 644 en
  vez de 600 (preexistente). **Todo corregido**: reescrito el párrafo de
  `REPLICA.md`, agregadas las secciones 39-43 en DECISIONES.md (una por
  frente, con las decisiones de diseño que el guardián señaló sin acta:
  esquema duplicado del importador, `TEXTO_DEFECTO_VACIO`, hash de
  contenido, la salida de red de `bench_red.c`), `micro/bin/` a
  `.gitignore`, corregidos §38.1 y el encabezado partido, reescrito el
  test placebo con monkeypatch de `sqlite3.connect` (falla si alguna
  conexión apunta a la ruta real), cerrada la alarma de `RESTAURAR.md`.
  `.env` a 600 quedó bloqueado por el propio harness (comando denegado) —
  no se pudo hacer, queda para Nicolás. Segundo dictamen despachado.
- 17:05 UTC — Frente 6A ejecutado: recomputados los 12 pares WS2b+WS3
  (`GEMELO/experimento.py` + `GEMELO/ventana_larga.py`, `usar_cache=True`,
  sin red salvo el `yf.download` interno de `_descargar_para_el_campeon`
  de WS3, ~176s) con `inf.bootstrap_media` en vez de `inf.bootstrap_bloques`,
  cruzado con `evaluacion.block_bootstrap` (método independiente, no
  circular). **En los 12 pares, sin excepción, `ic_excluye_cero` es
  idéntico entre escala vieja/nueva/cruzada — ninguna conclusión cambia**,
  igual que ya se había confirmado para los 12 del WS5. Despachado
  `escriba-decisiones` para la errata en DECISIONES.md.
- 18:00 UTC — Segundo dictamen de `guardian-constitucion`: **OBSERVADO**,
  un solo señalamiento — el acta §42 decía "Commit hecho" cuando
  `scripts/restaurar_backup.py`/`tests/test_restaurar_backup.py` todavía
  eran `??` en git. El resto (R0,R1,R3,R6,R8,R9, las tres correcciones
  bloqueantes de la ronda anterior, portabilidad bash-3.2) verificado en
  verde de forma independiente por el propio guardián, no de segunda mano.
- 18:05 UTC — Commiteado el Frente 5 (`0dce853`: `scripts/restaurar_backup.py`,
  `tests/test_restaurar_backup.py`, `docs/RESTAURAR.md`), con lo cual la
  frase del acta §42 pasó a ser cierta. Commiteado el resto de la corrida
  (`d1d0092`: `GEMELO/MICRO/`, `GEMELO/RELEVO.md`, `docs/REPLICA.md`,
  `GEMELO/resultados/{bitacora,dos_ventanas,expedientes}.md`, `micro/` con
  `micro/bin/` en `.gitignore`, y las actas §39-43 + la corrección de §38
  en `DECISIONES.md`). Ambos commits corrieron la suite completa vía el
  hook de pre-commit (316 passed las dos veces). **No se pusheó nada** —
  el push queda para Nicolás, ver el cierre más abajo.
- 18:15 UTC — `ESTADO.md` regenerado (skill `cierre-sesion`): último sello
  2026-08-28/253 verificaciones, los dos pre-registros nuevos de GEMELO
  6.0.0, el hallazgo de la concentración en 15-23-jul, §34.9 resuelto, y
  la lista de decisiones que esperan a Nicolás actualizada con los cinco
  frentes de esta noche. 50 líneas exactas.

## Cierre — handoff para Nicolás

**Hecho y commiteado (2 commits, sin pushear):** el importador de CSV
(Frente 5, único frente que se ejecutaba de verdad) con 17 tests y su
runbook; el pre-registro de microtrading/latencia con arnés en C medido de
verdad (WSL2 tiene un piso de ~75µs, la lectura de captura en vivo muere
por la red, la lectura de pipeline RTL académico sobrevive); el protocolo
de relevo de MODELO_VERSION (revisado y corregido tras un RECHAZO
adversario); el diseño de réplica permanente; el análisis de potencia de
la ventana sellada (con el hallazgo no pedido de que toda la ventaja vive
en 6 fechas de julio); los expedientes 6B/6C; y la corrección ejecutada
del §34.9 en los 12 pares de WS2b/WS3. Dos tandas de `guardian-constitucion`
(RECHAZADO → corregido → OBSERVADO → corregido), dos de
`estadistico-adversario` (RECHAZADO cada vez en su primera versión,
corregidas ambas). Todo verificado en modo lectura contra `senales.db`
donde hizo falta; ninguna base real se escribió.

**A medias, y por qué:** el protocolo de relevo y el análisis de potencia
llevan solo UNA corrección adversaria aplicada, no una segunda ronda de
verificación completa — presupuesto de la corrida, no negligencia; ambos
quedan sólidos pero sin el segundo par de ojos que sí tuvo el importador.
El expediente del "efecto estampida" de `Persistent=true` (6B) se abrió de
cero: no hay ninguna discusión previa en el proyecto, así que es una
pregunta nueva, no una respuesta.

**Espera decisión de Nicolás, en el orden que más importa primero:** (1)
qué hacer con el hallazgo de que la ventaja sellada vive en 6 fechas de
julio — cambia cómo leer el track record hoy mismo; (2) el segundo
movimiento del switch (`MKI_MODO=sombra` sigue puesto, ya sabido de antes,
no de esta noche); (3) los umbrales propuestos de `RELEVO.md`; (4) placa
FPGA y alcance de `MICRO/`, si sigue esa pista; (5) si se activa una
réplica permanente y con qué máquina; (6) los expedientes 6B/6C (campo de
visibilidad, auditoría de idempotencia de los timers, alcance del pin de
pandas) — todos de bajo riesgo para investigar, ninguno urgente.

**Comandos que le tocan a Nicolás**, en orden:

```
git log --oneline -5              # revisar los dos commits de esta noche
git diff e815249..HEAD --stat     # el diff completo de la corrida
git push origin main              # SOLO si el diff se ve bien
```

No se pusheó nada. No se tocó `motor.py`, `senales.py`, `snapshot.py`,
`universo.py`, `.env`, ningún timer, ni `MKI_MODO`. `.env` sigue en 644
(el harness no me dejó cambiarlo) — `chmod 600 .env` a mano cuando puedas.
