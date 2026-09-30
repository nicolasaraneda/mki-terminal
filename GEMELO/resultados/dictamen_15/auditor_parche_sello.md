# Auditoría de fuga del `auditor-lookahead` sobre el parche NO APLICADO `sello_no_verificable.diff` (bloque 3, corrida 15)

> Archivado por el orquestador tal como lo devolvió el agente (resumen fiel). Lanzado a las 23:25 de
> Chile del 29-sep-2026 sobre el worktree `wt15_b3`; devuelto a las **23:35** (hora de `date` del
> agente); ningún test corrido después de las 23:33. Sus dos sondas adversarias viven en el
> scratchpad de la sesión (`probe/p.py`, `probe/cal.py`). Nada escrito en el proyecto.

## Veredicto

**APLICABLE CON EXIGENCIAS.** El mecanismo hace lo que dice: ninguna ruta escribe en `sellos_dinero`
con `timing_ok` falso, ninguna escribe o reescribe un `ext_<fecha>.csv` canónico con timing roto, y
`--sin-red` no levanta un `.no_verificable.csv`. La tabla nueva tiene los dos disparadores y aborta.
Los tests escribieron sólo en `tmp_path` (medido por mtime). Lo bloqueante es otra cosa: **la rama
`rechazado_evidencia_canonica` no deja rastro en ninguna tabla**, y esa rama es alcanzable en
producción por la decisión de los dos relojes; y **un intento no verificable es invisible para todo
lo que monitorea el sistema** (`sesiones_selladas` no se mueve, `ultimo` es el de anoche, la API no
sirve la clave nueva, el vigía no mira el sellador): después de E0.3 una noche quemada se ve
idéntica a un sábado.

Prohibiciones respetadas: `sha256(dinero/sello_dinero.py)` del árbol real =
`480fbdc991679f2b06340bd4609dc08b3fd8c920cc4bc5eae1d03b93a39fbeab` = `git show HEAD:…`, al abrir y
al cerrar; `git status --porcelain dinero/` vacío; nada más nuevo que las 23:20 en `dinero/` ni en
`data/backups/`; nunca `--sellar`; la base real no se abrió; `data/sonda_cierre.csv` no se leyó.

## 1. Lo verificado

- `tests/test_sello_dinero.py tests/test_dinero.py -q -m "not red"` en el worktree: **91 passed** en
  100,4 s, cero saltados (los cuatro tests de integridad corrieron contra la copia de la base real).
- El test de reproducción falla en HEAD por su propia aserción (`divergencia_registrada`, 0 filas),
  no por la firma de la función (el shim `_congelar` existe para eso).
- Aislamiento medido: `find` de archivos más nuevos que el inicio de la corrida en
  `dinero/datos/sello`, la copia de la base y `data/backups`: vacío.
- Arnés `GEMELO/propuestas/test_parches_en_worktree.py -k sello_no_verificable`: **1 passed**; el
  worktree temporal se limpió; `git apply --check` contra HEAD limpio: OK.
- Sonda adversaria propia (P1): intradía → noche → tercer disparo tardío: d1 `intento_no_verificable`
  (33 filas en la tabla nueva), d2 `sellada` (33, `cuenta_para_N = 1`), d3 `divergencia_registrada` con
  0 filas y los cuatro archivos byte a byte y mtime a mtime iguales. (P3) los disparadores de la tabla
  nueva abortan UPDATE y DELETE. (P4) cero filas con timing roto en la principal en las dos bases.
- Exclusividad de la tabla principal, leída del fuente: `tabla = TABLA_INTENTOS` si y sólo si
  `not timing_ok`, y `timing_ok = timing["timing_ok"] and not evidencia_no_verificable` (la clase de la
  evidencia sólo endurece); `cuenta_para_N` es 0 para todo intento. `init_db` es todo `CREATE … IF NOT
  EXISTS`; los helpers de integridad abren en `mode=ro` y no llaman `init_db`.
- Calendario y husos: `cierre_utc` sale de `session_close` (media sesión del 27-nov y del 24-dic:
  18:00Z; EST 21:00Z; EDT 20:00Z); las dos desigualdades son estrictas en los dos extremos. El
  mecanismo que atrapó el 28-sep es causal: a las 13:42 NY el `available_at` computado (20:00Z) es
  futuro respecto del reloj.
- `estado()`, API, export, respaldo: la API (`api/main.py:1352`) lee las mismas claves y ninguna
  cambia (`test_los_tres_endpoints_del_riel_sirven_lo_que_el_contrato_dice` en verde); `exportar_csv`
  agrega `<ruta>_no_verificables.csv` sin tocar los otros dos; `respaldar_extension` no cambió y copia
  el par por construcción (`splitext`); `GEMELO/sonda_cierre.py` no abre bases; `mki_vigia.py` no
  nombra `sello_dinero` ni `dinero`; `scripts/generar_readme.py` lee el sellador sólo por regex de
  `N_OBJETIVO_E0`.
- Integridad permanente: los cuatro tests corrieron contra la copia real (sin la tabla nueva; 33 filas
  rotas, todas `E0.2`); la tolerancia es por versión (`_version(version_sello) >= E0.3`), sin nombrar
  fecha, con contraprueba.

## 2. Fugas demostradas (de auditabilidad, no temporales)

**F1 (BLOQUEANTE).** `rechazado_evidencia_canonica` no deja fila en ninguna tabla (sonda P2: cero
filas en las tres; sólo una línea en `data/sello_dinero.log`, que rota). Peor que E0.2 para esa rama,
y contra la doctrina de E4 («no se ignora en silencio»). Agravante: el canónico huérfano queda en
`DIR_EXT` y `es_extension_sellable()` da `True`, así que `--sin-red` lo vuelve a levantar y a
rechazar en silencio. La rama es alcanzable por la decisión de los dos relojes; en esta plataforma
ya se midió una brecha de 44 min entre estampar y commitear (6-ago).

**F2 (RECOMENDADA).** Congelar con timing roto y no sellar (proceso muerto, red caída, gate que
aborta) deja `ext_F.no_verificable.csv` citado por nadie, indistinguible en la carpeta del caso bueno.

## 3. Exigencias

**B1.** El rechazo deja una fila en `divergencias_sello` (sha del propio insumo rechazado en las dos
columnas, `decisiones_distintas` 0, detalle con los tres instantes) y `main()` exporta en esa rama;
test nuevo. **B2.** Un intento no verificable tiene que ser visible fuera del log: `estado()` agrega
`ultimo_intento`, `api/main.py` sirve `intentos_no_verificables` y `ultimo_intento` dentro de `E0`,
y `api/CONTRATO.md` se enmienda antes (no consume el presupuesto de «un cambio por noche al
sellador»: `estado()` es de sólo lectura y la API no es el sellador). **B3.** El acta que aplique
escribe que sustituye el mecanismo de §90.6 (a), no que lo implementa (texto en el dictamen).

**R1.** Integridad en la dirección archivos → filas para la clase nueva, o declarar el huérfano en
`main()`. **R2.** Con la tabla ausente en la base real, `pytest.skip` declarado en vez de pasar en
falso con `[]`. **R3.** `entorno_temporal` parchea también `S.RUTA_BACKUP_CSV`. **R4.** Mismo sha en un
segundo intento → `ya_intentada`, cero filas, simétrico con `ya_sellada`; enmendar la política §2.4.
**R5.** `main()` imprime los dos instantes (congelar y sellar) y su delta en toda rama.

## 4. Las cuatro discrepancias del implementador

(i) Rechazo: dirección correcta, implementación incompleta (B1); las alternativas descartadas lo
estaban por las razones buenas. (ii) La (a) literal no se implementa: correcto, es el hallazgo más
valioso de la corrida; M exigiría recrear la tabla con los disparadores caídos, la única regla sin
excepciones. (iii) Segundo intento con el mismo sha: la asimetría está al revés (R4). (iv) Dos
relojes: decisión correcta por una razón de fuga (unificarlos sellaría una emisión con hora
anterior a la real), y es la que hace urgente B1.

## 5. Aplicabilidad

No está listo tal cual: faltan B1, B2 y el texto de B3. Un cambio por noche al sellador alcanza si
B1 (y R4, R5) se pliegan al mismo diff antes de aplicar; aplicar el diff una noche y B1 la siguiente
es la peor combinación. B2 va aparte y puede ir antes. **La primera noche después de aplicarlo:**
la tabla nueva aparece con 0 filas y `sellos_dinero` crece +33; nace
`data/backups/sello_dinero_no_verificables.csv` vacío con cabecera y el backup lo commitea;
`SELECT version_sello, estado_timing, COUNT(*) …` sólo con `roto` en `E0.2`; `version_sello = 'E0.3'`
y `sellador_sha256` nuevo (la huella definitiva es la del archivo aplicado, no la del worktree);
`/api/dinero/sellos` responde igual; `dinero/datos/sello/` con el par canónico nuevo y ningún
`.no_verificable.*` si la noche fue normal; la suite del sellador fuera de la ventana.

## 6. Zonas ciegas

`main()` no es testeable y no se ejecutó (juicio por lectura); `--sin-red` no se corrió contra la
carpeta real; **dos instancias concurrentes no probadas** (entre `intento_previo` en `congelar` y la
cita en `sellar` no hay atomicidad: sospecha sin demostrar); Yahoo de verdad no; `available_at`
sigue siendo computado por calendario, no observado, y ahora decide a qué tabla va una fila (la
zona ciega subió de categoría); nada es point-in-time; fuga por el analista (F1 y F2 son huecos que
ningún test del parche cubre); el 28-sep no es reproducible desde la fuente; la base real no se
abrió; intentos del DSR: 0.

**Hora de `date` al cerrar: 23:35 de Chile.**

## Qué hizo el orquestador después (nota del orquestador, 23:38)

B1, R2, R3, R4 y R5 se le pidieron al implementador del bloque 3 para plegarlas al mismo diff antes
de las 00:03 (los tests del parche corren en su worktree, con bases temporales); la política se
enmendó en §2.4 (R4 y el caso de B1). B2 y B3 quedan en la tarjeta §75 para el acta que aplique.
