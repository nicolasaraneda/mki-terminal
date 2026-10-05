# Bitácora de la corrida 16b — TOELY fuera del universo del insumo de E0 (acta §95.4)

> Domingo 4-oct-2026. Encargo: `~/encargo.md` (escrito por el asistente del chat a las 15:05, sin leer el código de
> `dinero/`; guardado por Nicolás a las 16:19:50). Orquestador: Fable 5.1, esfuerzo alto, elegidos al arrancar.
> Acta que la autoriza: **§95.4 y §95.5** (firmas de Nicolás, 4-oct). Horas de Chile leídas de `date`. Nada se
> pusheó, nada se commiteó, nada se firmó, nada se operó; ninguna unidad de systemd se tocó; el sellador real no se
> corrió; `dinero/sello_dinero.db` se abrió sólo en `mode=ro`.

**PRIMERA LÍNEA (estado al cierre): el parche NO está aplicado al árbol real.** El reloj del encargo exigía la
aplicación a más tardar a las 16:45 con dictamen APLICABLE; la sesión del orquestador quedó **pausada 3 h entre su
segunda y su tercera llamada** (primer `date` 16:20:39; el proceso de la suite de apertura nació a las 19:18:16 según
`ps -o lstart`; el latido del journal del sistema es continuo en esa ventana exacta, 356 líneas cada 30 s sin hueco mayor de
60 s: la máquina no se suspendió, la sesión esperó). Por la letra del encargo («si a las 16:45 el parche no tiene dictamen APLICABLE, no se
aplica nada al árbol real»), el parche quedó en **`GEMELO/propuestas/parches/toely_fuera_insumo_e0_16b.diff`** (sha256
`e8989db56742c593aa75c3ac3e6f0f25ec4a9dceaefd60bb8524938d6127d9b6`, `git apply --check` limpio sobre HEAD `f5b659e`)
con sus tests dentro y el dictamen **APLICABLE CON EXIGENCIAS** del auditor (`dictamen_16b/auditor_toely.md`; la única
exigencia de código, B3, ya está dentro del parche). **Aplicarlo es acto de Nicolás** (receta en §5) antes del sello
del lunes (6-oct, 00:30 Chile) si quiere que la sesión del 5-oct cuente; si no, la sesión sale `insumo_incompleto`
por TOELY y se declara, como §95.5 previó. **Criterio §95.5 aplicado:** el permiso de copiar las bases al worktree se
pidió una vez y fue denegado; juzgan la suite del árbol real con todas las bases (apertura, HEAD sin parche: **1032
passed, 5 skipped, 1 xfailed, 0 failed**) y el control sobre HEAD puro en un segundo worktree: el conjunto de rojos
del worktree con parche y sin parche es **idéntico** (26, todos por bases y artefactos gitignorados ausentes);
ningún rojo aparece sólo con el parche (§4).

---

## 0. Reloj, orientación y lecturas de sólo lectura

### 0.1 Reloj y timers

- **Inicio: 16:20:39** (primer `date`, al leer el encargo). Pausa de la sesión hasta las **19:18:16**. Trabajo real
  19:18 a ~19:55. Fin: ver §7.
- `systemctl --user list-timers --no-pager` a las 16:20:39, copia textual de las unidades `mki-*`:

```
NEXT                                  LEFT LAST                                   PASSED UNIT                           ACTIVATES
Mon 2026-10-05 17:50:00 -03            22h Fri 2026-10-02 17:50:00 -03        2 days ago mki-noticias.timer             mki-noticias.service
Mon 2026-10-05 18:15:00 -03            22h Fri 2026-10-02 18:15:00 -03        2 days ago mki-snapshot.timer             mki-snapshot.service
Mon 2026-10-05 18:25:00 -03            23h Fri 2026-10-02 18:25:00 -03        2 days ago mki-reporte.timer              mki-reporte.service
Mon 2026-10-05 18:40:00 -03            23h Fri 2026-10-02 18:40:00 -03        2 days ago mki-backup.timer               mki-backup.service
Mon 2026-10-05 19:00:00 -03            23h Fri 2026-10-02 19:00:00 -03        2 days ago mki-vigia.timer                mki-vigia.service
Mon 2026-10-05 20:30:00 -03       1 day 1h Fri 2026-10-02 20:30:00 -03     1 day 22h ago mki-vigia-rechequeo.timer      mki-vigia-rechequeo.service
Mon 2026-10-05 21:05:00 -03       1 day 1h Sat 2026-10-03 04:35:00 -03     1 day 14h ago mki-sonda-cierre.timer         mki-sonda-cierre.service
Tue 2026-10-06 00:30:00 -03       1 day 5h Sat 2026-10-03 00:30:00 -03     1 day 18h ago mki-sello-dinero.timer         mki-sello-dinero.service
```

- **Próximo disparo de `mki-sello-dinero`: martes 6-oct 00:30 Chile** (lunes 5-oct 23:30 NY), confirmado de la máquina.
  Hoy domingo no dispara ningún job `mki-*`. Nada de esta corrida está a menos de 28 h de ese disparo.

### 0.2 Árbol de git (16:20:39)

HEAD `f5b659e` = commit de la corrida 16a («Corrida 16a y actas §93 y §94»), con los backups del 1 y 2-oct debajo.
Modificados: `DECISIONES.md` (sólo el acta §95, anexada por Nicolás a las 16:19:35), `data/backups/sello_dinero.csv`,
`data/sonda_cierre.csv`; sin seguimiento: `data/backups/sello_dinero_ext/ext_2026-10-02.{csv,meta.json}`. Exactamente
lo que el encargo esperaba: no se mezclan corridas.

### 0.3 Suite de apertura (árbol real, HEAD sin parche, todas las bases)

`venv/bin/python -m pytest tests/ -q`: **1032 passed, 5 skipped, 1 xfailed, 29 warnings in 419.95 s**, terminada
19:25:16 (`dictamen_16b/evidencia/suite_arbol_real_apertura.txt`). Igual que el cierre de la 16a (acta §94.1).

### 0.4 Lo leído del código antes de escribir una línea (punto 0.4 del encargo)

1. **Dónde está el universo del insumo de E0.** No es una lista: se **calcula**. `sello_dinero.decidir` llama
   `cuenta_papel.universo_operable(hasta, cfg, hasta=CP.DESDE)`, que cruza `universo_dinero.CANDIDATOS` (36, TOELY
   entre ellos: `universo_dinero.py:178`, rol «sustituto», `liquidez_no_verificada=True`) con `construir_mapa` sobre
   los cierres hasta `DESDE` (2023-09-05) y deja los `verificado and alcanza_con_techo and ticker in columns` →
   **33** con el techo de 500 USD. `reglas.json` no tenía ningún universo. La fila sella `reglas_sha256`
   (`_sha256(U.RUTA_REGLAS)`) y `sellador_sha256` (el propio módulo): el universo está «sellado» sólo
   indirectamente, por el hash del código y por el censo.
2. **`insumo_completo` y el motivo.** En `decidir`, por cada operable: si `precio_ref_usd is None` (sin cierre en
   `dia`), la fila lleva `decision="nada"` y el motivo «sin dato en el insumo para la sesión … (último cierre: …)»;
   `completo = all(ultimo_cierre_ticker == dia)`; `sin_dato` lista los que no. En `sellar`, `estado =
   insumo_incompleto` si no `completo`, y `cuenta_para_N` exige completo + fresco + timing + sesión.
3. **Quién más lee ese universo.** La sonda (`GEMELO/sonda_cierre.py:65`) lee su lista de
   `dinero/datos/cierres_congelados.meta.json` (36 tickers) y no importa nada de `dinero/`: **el cambio NO le llega**.
   `GEMELO/m2_periodo.py`, `GEMELO/universo_por_presupuesto.py` y el censo `universo_operable.json` usan
   `CP.universo_operable` directamente: no les llega si el filtro va después. La API (`/api/dinero/*`) lee el
   artefacto del censo y `S.estado()` en `mode=ro`. `exportar_csv` vuelca la tabla. `scripts/generar_readme.py` lee de
   `sello_dinero.py` sólo `N_OBJETIVO_E0` por regex. El vigía no menciona `dinero/`. Los tests fijan `33` en ocho
   aserciones de `tests/test_sello_dinero.py`.
4. **Identificador de versión.** `VERSION_SELLO = "E0.2"` en el sellador; `version_reglas = "0.2.0-PROPUESTA"` en
   `reglas.json`, sellado por fila como `reglas_version`. El parche T de §62 mueve `VERSION_SELLO` a `E0.3`. Decisión
   de diseño de la 16b: **no mover ninguno**; la distinción por fila es `reglas_sha256` (lo que §95.4 nombra), y
   `sellador_sha256` cambia también. Sin choque con T. Mover `version_reglas` queda como opción en la tarjeta §79.
5. **El sorteo.** `contabilidad.senales_sin_informacion` recorre `for t in tickers` con UN generador por sesión: una
   lista más corta corre la **realización** del sorteo de los tickers posteriores a TOELY la primera sesión y de todos
   desde la segunda; distribución por ticker (historia ≤ DESDE) y semilla, intactas. Declarado antes del dictamen;
   el auditor lo midió (99,81 % de las casillas cambian; medias y desvíos indistinguibles; E0 no puntúa nada).

### 0.5 Base real al abrir (`mode=ro`, 19:21)

18 sesiones selladas, 594 filas, 33 tickers por sesión, 9 cuentan de 40; TOELY con 18 filas (8-sep a 2-oct); un solo
`reglas_sha256` (`125a8602…`), dos `sellador_sha256` (`93db9b70…`, `480fbdc9…`); 2 divergencias. Sesiones del
29-sep al 2-oct: `insumo_incompleto`, único faltante TOELY (también el 18 y el 23-sep: hallazgo R5 del auditor; el
28-sep es `no_verificable_timing`).

---

## 1. Diseño del cambio (lo mínimo que cumple §95.4)

- **`dinero/reglas.json`**: clave nueva `exclusiones_insumo_e0 = {"_": nota con la firma, "tickers": ["TOELY"]}`.
  `version_reglas` no se mueve. El hash del archivo pasa de `125a8602a684…` a **`b6080eee4351ed433aeb5a124ec4603dcb3db3b3278b1791c40ee8a4ad0abc6c`**, y ése es el marcador por fila.
- **`dinero/sello_dinero.py::decidir`**: después de `universo_operable`, `excluidos = sorted(set(tickers declarados)
  & set(operables))` y `operables = [t for t in operables if t not in excluidos]`; devuelve `excluidos_universo`.
  **B3 del auditor:** `sellar()` propaga `excluidos_universo` a su retorno, así el log de cada noche dice por qué son
  32. `VERSION_SELLO` sigue `E0.2`. Nada más del módulo cambia; `descargar_extension` sigue bajando TOELY (la
  extensión y su sha no cambian de forma).
- **`tests/test_sello_dinero.py`**: los ocho pins `== 33` pasan a la constante `N_OPERABLES = 32` con su comentario.
- **`tests/test_toely_fuera_insumo_e0.py`** (nuevo, 10 tests): escrito ANTES de la corrección; **sobre HEAD: 8 rojos,
  1 verde (gate de invariancia), 1 saltado** (la base real no está en el worktree). Cubre: reproducción (falta sólo
  TOELY → completo, `pendiente`, `cuenta_para_N = 1`, `excluidos_universo == ["TOELY"]`); cero faltantes tolerados
  (`AMD`; `AMD`+TOELY; `KLAC`+`NVDA`+TOELY → `insumo_incompleto` con esos nombres y TOELY nunca aparece); TOELY
  presente no vuelve; la exclusión vive en reglas y el censo no la ve; sin la clave el comportamiento es el anterior;
  la ventana horaria sigue mandando (completo pero tardío → no cuenta); el gate de invariancia; la base real en
  `mode=ro` conserva TOELY y la huella vieja, con los triggers de inmutabilidad en pie.

Huellas tras aplicar (verificables con `sha256sum`): `dinero/reglas.json` = `b6080eee4351ed433aeb5a124ec4603dcb3db3b3278b1791c40ee8a4ad0abc6c`;
`dinero/sello_dinero.py` = `cd0e70c8005143b2f6b63c62fb9e3f75b5303e083a936c98c13b86df6a8b2c25`.

---

## 2. Lo que se descartó, y por qué

- Filtrar dentro de `universo_operable`: alcanzaría el censo, `m2_periodo` y `universo_por_presupuesto` (resultados ya
  sellados) sin necesidad.
- Sortear con TOELY y descartarlo (preserva la realización del sorteo de los otros 32): es la R1 del auditor, que la
  midió (40 sesiones: HEAD 30 compras, parche 25, preservar 30 = HEAD ticker por ticker). **No se eligió**: §95.4 dice
  «sale del universo», E0 no puntúa nada, y elegir entre dos realizaciones ya vistas es un grado de libertad que el
  auditor pide dejar escrito. Tarjeta §79.3.
- Mover `version_reglas` / `VERSION_SELLO`: tarjeta §79.2.
- Tolerar faltantes: prohibido por §95.4 (no se elige (d)).

---

## 3. Dictamen del auditor (19:32:27 a 19:39:59): APLICABLE CON EXIGENCIAS

`dictamen_16b/auditor_toely.md`. Sin fuga temporal ni de futuro, sin efecto retroactivo, regla maestra intacta.
Bloqueantes: **B1** el parche dispara V4 de la regla sellada de §58 (universo permanente 33 → 32: la regla se cierra
«NO DECIDIBLE» con 4 noches válidas juntadas, y reiniciar con el universo nuevo es acto de Nicolás con acta; la regla
no se edita); **B2** `A(D)` pasa a medirse sobre 32 y `C(D,g)` de la sonda sigue sobre 33 → toda noche con sólo TOELY
faltante es clase C por construcción, sin alarma de concordancia; **B3** propagar la exclusión al retorno de `sellar()`
(**aplicado en el parche a las 19:43**); **B4** la suite del árbol real como juez al aplicar (el worktree no cubre
`api/` ni `test_dinero.py`); **B5** una fila nueva en `divergencias_sello` sobre una fecha anterior al 5-oct daría
`decisiones_distintas` ≈ 33, incomparable con los dos valores registrados. B1, B2 y B5 están declaradas en el acta §96.
Recomendadas R1 a R5: tarjeta §79 y corrida 16. Zonas ciegas nombradas, incluida la fuga por el analista (el cambio
mejora mecánicamente la tasa de sesiones que cuentan y se firmó sabiéndolo).

---

## 4. Suites

| suite | resultado | archivo |
|---|---|---|
| árbol real, apertura, HEAD sin parche, todas las bases (19:25:16) | 1032 passed, 5 skipped, 1 xfailed, 0 failed | `evidencia/suite_arbol_real_apertura.txt` |
| worktree con parche (antes de B3), sin bases (19:38:34) | 938 passed, 83 skipped, 20 failed, 6 errors, 1 xpassed | `evidencia/suite_worktree_parche_sin_bases.txt` |
| worktree HEAD puro, sin bases (19:38:31) | 929 passed, 82 skipped, 20 failed, 6 errors, 1 xpassed | `evidencia/suite_worktree_HEAD_puro_sin_bases.txt` |
| worktree con parche + B3: sellador, dinero, instrumento, segundo sello (19:43) | 73 passed, 5 skipped | — |
| árbol real, cierre, HEAD sin parche, todas las bases (19:50:10 a 19:57:14) | 1032 passed, 5 skipped, 1 xfailed, 0 failed | `evidencia/suite_arbol_real_cierre.txt` |

`diff` de los conjuntos de rojos (nombres) entre los dos worktrees: **vacío**. Los 26 son `test_api` (6),
`test_backtest` (1), `test_cifras_arbitro` (6 errores), `test_dinero` (2), `test_frontend_estatus` (1),
`test_linea_base` (1), `test_readme` (9): bases y corridas selladas gitignoradas que el worktree no tiene (memoria de la
16a). Sobre HEAD puro, `tests/test_toely_fuera_insumo_e0.py` da 8 rojos, 1 verde, 1 saltado (19:24:16).

**Suite de cierre del árbol real:** el árbol real no recibió ningún cambio de código ni de tests en esta corrida (sólo
documentos, el `.diff`, el dictamen y la evidencia), así que la suite de cierre es la de apertura; se volvió a correr al
cierre para el registro: ver §7.

---

## 5. Receta de aplicación, para la mano de Nicolás (antes del lunes 5-oct 23:30 NY)

**Apartamiento declarado de la letra de §95.5** («si la 16b no queda commiteada antes de las 17:50 del 4-oct, la sesión
del 5-oct se pierde igual»): la sesión todavía se salva porque (a) **el sellador lee el árbol de trabajo, no git**: lo que
la salva es el `git apply`, el commit es registro; (b) el plazo operativo real es el disparo de `mki-sello-dinero`, martes
6-oct 00:30 Chile (`list-timers`); (c) el hook pre-commit no bloquea un commit de hoy domingo (`scripts/guarda_red.sh`
devuelve «fuera de la ventana»); **el lunes entre 17:50 y 20:30 sí lo rechaza**: commitear antes de las 17:50 o después de
las 20:30 del lunes. Exigencia E3 del guardián.

```bash
cd ~/dev/mki-terminal
git apply --check GEMELO/propuestas/parches/toely_fuera_insumo_e0_16b.diff && \
git apply GEMELO/propuestas/parches/toely_fuera_insumo_e0_16b.diff
sha256sum dinero/reglas.json dinero/sello_dinero.py          # b6080eee… y cd0e70c8…
venv/bin/python -m pytest tests/ -q                           # PREDICCIÓN (nunca corrida): 1042 passed, 5 skipped, 1 xfailed, 0 failed (1048 recolectados)
python tests/test_motor.py                                    # anti-look-ahead del motor, en verde
git status --short                                            # aparece tests/test_toely_fuera_insumo_e0.py sin seguimiento: va en el commit
```

Si la suite real da un rojo que no sea de entorno, `git apply -R` el mismo archivo lo revierte entero. El test
`test_las_filas_selladas_antes_del_cambio_siguen_con_toely_y_con_la_huella_vieja` sólo puede estar verde CON el parche
aplicado (compara la huella nueva de `reglas.json` contra las selladas). El commit incluye la lista de §8 más
`dinero/reglas.json`, `dinero/sello_dinero.py`, `tests/test_sello_dinero.py` y `tests/test_toely_fuera_insumo_e0.py`.
**Corte de método:** la hora del `git apply` es la que el acta de aplicación (de Nicolás o de la corrida 16) declara.

---

## 6. Predicción falsable para el sello del 6-oct a las 00:30 Chile (escrita antes de cerrar)

**Si el parche está aplicado antes del disparo:** la sesión del 5-oct queda sellada con `insumo_completo = 1`, `estado
= pendiente`, `cuenta_para_N = 1`, **32 filas** (ninguna de TOELY), `reglas_sha256 = b6080eee…`, `sellador_sha256 =
cd0e70c8…`, `reglas_version = 0.2.0-PROPUESTA`, `version_sello = E0.2`; el contador de sesiones que cuentan pasa de
**9 a 10**; la línea del sello en `data/sello_dinero.log` lleva `"excluidos_universo": ["TOELY"]` y
`"filas_insertadas": 32`. Salvo que falte OTRO ticker: entonces `insumo_incompleto` con ese ticker nombrado en el
motivo, 32 filas, contador en 9. **Si el parche NO está aplicado:** `insumo_incompleto`, 33 filas, TOELY el único sin
dato, `reglas_sha256 = 125a8602…`, contador en 9 (y la causa es el reloj de esta corrida, no el sellador).

Consulta exacta (`mode=ro`), martes 6-oct en la mañana:

```bash
cd ~/dev/mki-terminal && venv/bin/python - <<'EOF'
import sqlite3
con = sqlite3.connect("file:dinero/sello_dinero.db?mode=ro", uri=True)
for r in con.execute("""SELECT fecha_insumo, estado, insumo_completo, cuenta_para_N, COUNT(*) AS filas,
       SUM(ticker='TOELY') AS filas_toely, substr(reglas_sha256,1,12) AS reglas, substr(sellador_sha256,1,12) AS sellador,
       GROUP_CONCAT(CASE WHEN ultimo_cierre_ticker != fecha_insumo THEN ticker END) AS sin_dato, timestamp_utc
       FROM sellos_dinero WHERE fecha_insumo >= '2026-10-01' GROUP BY fecha_insumo ORDER BY fecha_insumo"""):
    print(r)
print("cuentan para N:", con.execute("SELECT COUNT(DISTINCT fecha_insumo) FROM sellos_dinero WHERE cuenta_para_N=1").fetchone()[0])
EOF
grep -c excluidos_universo data/sello_dinero.log
```

Hoy (4-oct, 19:32) la misma consulta devuelve 1-oct y 2-oct `insumo_incompleto`, 33 filas, 1 de TOELY, `125a8602a684`,
`480fbdc99167`, sin_dato `TOELY`; cuentan para N: 9.

---

## 7. Cierre

- Guardián (19:50:47 a 20:10): **CONFORME CON OBSERVACIONES**, `dictamen_16b/guardian_cierre.md`; sus cuatro exigencias de registro cumplidas a las 20:12 (§96.6-bis). Fin de la corrida: 20:16.
- Acta de cierre: **§96** en `DECISIONES.md`, sin firmas.
- Tarjeta nueva: **§79** en `espera_firma.md` (quién aplica, marcador de versión, realización del sorteo, la sonda).
- `ESTADO.md` regenerado (50 líneas).
- Suite de cierre del árbol real (código intacto): **1032 passed, 5 skipped, 1 xfailed, 0 failed**, 423,89 s, terminada 19:57:14.
- Lo que queda para la corrida 16: declaración del universo nuevo en el README y en el CSV (§95.4), R2 a R5 del
  auditor, la sonda (§79.4), el desglose por hash en `estado()`, el badge de tests, y la lectura de §58 con V4 a la vista.

## 8. Lista exacta de archivos para el commit (no incluye `data/backups/` ni `data/sonda_cierre.csv`)

```
DECISIONES.md
ESTADO.md
GEMELO/propuestas/parches/toely_fuera_insumo_e0_16b.diff
GEMELO/resultados/bitacora_16b.md
GEMELO/resultados/dictamen_16b/auditor_toely.md
GEMELO/resultados/dictamen_16b/guardian_cierre.md
GEMELO/resultados/dictamen_16b/evidencia/suite_arbol_real_apertura.txt
GEMELO/resultados/dictamen_16b/evidencia/suite_arbol_real_cierre.txt
GEMELO/resultados/dictamen_16b/evidencia/suite_worktree_parche_sin_bases.txt
GEMELO/resultados/dictamen_16b/evidencia/suite_worktree_HEAD_puro_sin_bases.txt
GEMELO/resultados/espera_firma.md
```

Si Nicolás aplica el parche antes de commitear, se suman: `dinero/reglas.json`, `dinero/sello_dinero.py`,
`tests/test_sello_dinero.py`, `tests/test_toely_fuera_insumo_e0.py`.
