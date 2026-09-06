# Dictamen del guardián de la constitución — corrida 09 (diff completo, revisión independiente)

**Fecha y hora (leídas de `TZ=America/Santiago date` al escribir):** Sun Sep  6 18:30:40 -03 2026

**Rango dictaminado:** `git diff e0179b7~1 4feb32e` — cuatro commits `e0179b7` (D1), `7d13f5e` (bloque 2), `1b638cf` (bloque 3 y 1b/1c), `4feb32e` (acta 78). 65 archivos, +9.958 −218 (`git diff --stat`). HEAD al dictaminar: `ebebe0f` (dos «Backup diario» del 3 y 4-sep por encima del rango, sólo `data/backups/`). Rama `main`, 6 commits por delante de `origin/main`, nada publicado.

**Regla de independencia.** Ninguna afirmación de `bitacora_09.md` §13:05, del acta §78, de `ESTADO.md` ni de `estado_epistemico.md` se usó como evidencia: cada una se trató como hipótesis y se contrastó con la máquina. Cada punto cita el comando que corrí y la salida relevante. Lo que no pude verificar está en NO VERIFICADO.

---

## VEREDICTO: APROBADO CON EXIGENCIAS

```
DICTAMEN: OBSERVADO
Rama: main   Archivos: 65   Líneas: +9958 -218

RECHAZOS
  ninguno

OBSERVACIONES
  R6      tests/test_linea_base.py:333 (HEAD) — la suite completa sobre HEAD da 1 failed / 648 passed / 2 xfailed
          (test_senales_db_conserva_su_scoring_original, assert 6 == 5: censo de gap==0 clavado contra la base viva;
          el sello del 2-sep verificado el 3-sep 18:15 lo cruzó). El test no está en el diff; la corrección existe
          hoy SIN commitear en el árbol (git status: " M tests/test_linea_base.py", docstring «corregido el 6-sep-2026»)
          y ese test solo pasa. Sin suite en verde no hay APROBADO.
  Regla10 cifras.py:176 — el diff INTRODUCE «1,84×» en un .py sin marca de retiro que el detector de la casa reconozca
          (cifras.reintroducciones(cifras.py) → [(176, '1[,.]84\s?[×x]')]). Es una mención de retiro por su sentido
          («no circula suelto; entra con n e intervalo o se retira») y el ejecutable no EMITE la cifra (doce_bloques
          imprime c['ratio_ancho']=2.19): por eso OBSERVADO y no RECHAZADO; la lectura literal de la regla 10 diría
          RECHAZADO y la nota de instalación reserva a Nicolás confirmar la lectura.
  Regla10 GEMELO/resultados/encargo_corrida_09.md:45 — copia del encargo (texto de Nicolás) que el diff agrega al repo;
          contiene «1,84×» sin marca reconocible (mismo detector). Es la orden de retirarlo; exige nota fechada, no edición.
  Regla11 GEMELO/control_lineal.py:344-356 — el diff corrige en PROSA (erratas al pie de control_lineal.md:183 y
          ventana_larga.md:237) el IC del ΔMAE publicado en escala Sharpe, pero el ejecutable que lo produce sigue igual:
          `delta_mae_ic` sale de `inf.bootstrap_bloques(..., anualizar=1)`. La corrección va al ejecutable antes que al texto.
  R4      DECISIONES.md:7913 (§78.4, 2c) — el acta declara «una republicación a más de 10 días ya no se detecta» pero NO
          declara que el sentimiento de noticias entra en un campo SELLADO: senales.py:256
          `puntaje_ia = round(puntaje_v0*0.7 + ((sentimiento+1)/2)*0.3, 4)` con `sentimientos =
          noticias.sentimiento_promedio_por_ticker()` (snapshot.py:157). Desde el 3-sep 18:15 `sentimiento_ia`/`puntaje_ia`
          se sellan con un insumo cuya deduplicación cambió (11 titulares sobreviven que la versión vieja borraba,
          noticias_on2.md:118). Es un corte de método en un insumo sellado, no en motor.py; hay que declararlo y que
          Nicolás decida si toca FEATURE_VERSION / plataforma.
  R4      DECISIONES.md:7843 — «agente estadistico-adversario (V1 secundaria)» contradice el texto final del agente
          (.claude/agents/estadistico-adversario.md:52-53: «V1 sigue bloqueante hasta que V1-bis se firme», corrección
          del director a las 12:44 según la bitácora). Errata de una línea.
  R4/§0.4 GEMELO/resultados/bitacora_09.md:342-361 — el último hito es 13:05, pero bitacora_09.md tiene mtime
          2026-09-03 18:02:46 y los cuatro commits son de las 18:03:05 y 18:08:52 (×3, mismo segundo), DENTRO de la ventana
          de sellado 17:50–20:30 de un jueves; el primero corrió el hook con la suite (~5 min de CPU, terminando 18:03, en
          paralelo al job de noticias) y los otros tres llevan «SKIP_TESTS=1» en el cuerpo. Además el job de las 17:50 corrió
          noticias.py SIN commitear (commit a las 18:08; el archivo es byte-idéntico a 7d13f5e, mtime 10:15). Nada de esto
          está en la bitácora ni en el acta. Se registra; no se rehace.

NO VERIFICADO
  - Las 36 celdas del juez lineal (corrida09/juez_lineal_d3.{md,json}), la ruta 3 de horizonte.py (55 min de cómputo),
    la frase de potencia, los IC recomputados de ic_dmae_recomputados.md y las particiones de tarjetas_09.md (15/269, etc.):
    no las recomputé; verifiqué sólo que sus artefactos existen, son JSON válido, llevan etiqueta PROPUESTA/EXPLORATORIO,
    `es_veredicto_5_1: false`, huella sha256+mtime de la caché (bajada 2026-09-01T13:16 UTC) y fecha del 1-sep excluida.
  - Si la suite del hook pre-commit (~17:57–18:03 del 3-sep, en ventana) tocó la red: pytest NO colecta tests/test_motor.py
    («no tests collected»), pero no audité qué otros tests abren red.
  - El IC t de clúster [−8,1, +27,4] del árbitro (mi entorno no tiene scipy); sí reproduje el bootstrap y la permutación.
  - Las afirmaciones MEDIDO de replica.md sobre timers/`systemctl` (no ejecuté systemctl: no era necesario para el dictamen).

VERIFICADO EN VERDE
  R0 intocables · R1 filas selladas · R2 sin push/pull nuevos · R3 rama main, sin publicar · R5 secretos/.env 600/ignores ·
  R8 emisión y timers intactos · R9 doce bloques + aritmética independiente · Regla 13 parches no aplicados con test ·
  Regla 14 sin supuestos donde se pidió cómputo · encargo §7 (sin 5.1, sin retador, sin fuente nueva, sin parche aplicado) ·
  hooks y settings intactos · tests/test_motor.py OK · 48/48 tests nuevos + árbitro.
```

---

## 1. Intocables (R0, Regla 13)

- `git diff --name-only e0179b7~1 4feb32e | grep -E '^(motor|senales|snapshot|universo|version|modo|alertas|calendarios|app)\.py$|^systemd/|^launchd/|^data/|\.db$|^\.claude/hooks/|^\.claude/settings\.json$|^\.env|^mki$|^scripts/|^GEMELO/DISE|^backtest/resultados/'` → **vacío**.
- Último commit que tocó cada intocable (`git log -1 -- <archivo>`): motor.py `2bd3192` 2026-07-05; snapshot.py `c7a5e44` 2026-08-03; senales.py `7182a5f` 2026-07-25; universo.py `2bd3192` 2026-07-05; version.py `1f4ec75` 2026-08-25. Todos anteriores al rango.
- Parches NO aplicados: `git apply --check GEMELO/propuestas/parches/snapshot140.diff` → rc 0 (aplica limpio = no está aplicado); `git apply --check -R` → «patch failed: snapshot.py:137» (no se puede revertir = no está aplicado). Ídem `motor_concat.diff` (rc 0 hacia adelante; «patch failed: motor.py:182» en reversa). Contenido leído: snapshot140 cambia UNA expresión (`ahora_utc` → `datetime.fromisoformat(available_at)`); motor_concat agrega `sort=True` en tres `pd.concat`.
- Tests que los cubren, leídos enteros: `tests/test_parche_snapshot140.py` (copia a tmp, `patch -p1`, `senales.DB_PATH` a tmp con guardia `assert os.path.abspath(senales.DB_PATH) != .../senales.db`, calendario real, contraprueba sobre el original) y `tests/test_parche_motor_concat.py` (copia a tmp, sha256 de motor.py antes/después, igualdad exacta en 5 funciones, `git diff --quiet -- motor.py`). Listados en `espera_firma.md` §26 (línea 1092) y §36 (línea 1265). La suite confirma el aviso `Pandas4Warning` en motor.py:215 que el parche silencia.

## 2. Filas selladas (R1)

- `git diff e0179b7~1 4feb32e | grep -nE "^\+.*(UPDATE |DELETE FROM|DROP |ALTER TABLE|\.to_sql\(|if_exists=.replace.)"`: las únicas sentencias ejecutables agregadas son noticias.py:392-393 (`DELETE` sobre `analisis` y `titulares` por id) y las de `tests/test_importador_roundtrip.py` (`_corromper` sobre la copia temporal, línea 394: «copia temporal de pytest, nunca la real»). El resto son prosa (tarjetas, réplica, importador).
- Los dos `DELETE` **ya existían** en la base del rango: `git show e0179b7~1:noticias.py | grep -n "DELETE FROM\|UPDATE "` → 289 (UPDATE tickers, retag), 310-311 y 340-341 (los DELETE del dedup viejo). Ninguna tabla de `senales.db` aparece.
- `data/backups/` no está en el rango (filtro del punto 1). Los dos commits posteriores (`cef52c0`, `ebebe0f`) sólo tocan `data/backups/*.csv` (`git show --stat`). Las 20 y 13 líneas borradas en `noticias_titulares.csv` de esos backups son los duplicados que el dedup borró; ese comportamiento es previo al diff: `git log --shortstat -- data/backups/noticias_titulares.csv` muestra 33 borrados el 2-sep, 426 el 31-ago, 28 el 30-ago, 25 el 29-ago… con el código viejo.
- Bases: `git check-ignore -v` → `.gitignore:15 senales.db`, `:14 noticias.db`, `:16 alertas.db`, `:20 data/*.log`; `git ls-files | grep -E "\.db$|\.log$"` → nada.
- `noticias.db` (leída en `mode=ro`): tabla `meta` creada con `CREATE TABLE IF NOT EXISTS`, filas `dedup_retro_ultimo_id=6667`, `dedup_retro_corrido_en=2026-09-04T21:50:55Z`; esquema de `titulares`/`analisis`/`resumen_dia` sin ALTER nuevos (el único `ALTER TABLE` de noticias.py:208 es el previo de `relevancia`).

## 3. Emisión (R8)

- Ningún archivo bajo `systemd/`, `launchd/`, ni `modo.py`, ni `.env` en el rango (punto 1). `stat -c '%a' .en[v]` → **600**; `.gitignore:2 .env*`. Nota: `ESTADO.md:11` (dentro del diff) afirma «`.env` sigue en 644»; hoy la máquina dice 600. Manda la máquina.
- El diff no cambia el modo: `noticias.py`/`mki_noticias.py` no consultan `modo` ni lo alteran.

## 4. Producción tocada a propósito: `noticias.py` y `mki_noticias.py` (frente 2c)

Diff leído entero (`git diff e0179b7~1 4feb32e -- noticias.py mki_noticias.py`):
- **Aditivo:** `_asegurar_tabla_meta` (`CREATE TABLE IF NOT EXISTS meta`), `_leer_meta`/`_escribir_meta` (`INSERT OR REPLACE` sobre `meta`), `VENTANA_DEDUP_RETRO_DIAS = 10`, `_desplazar_fecha_iso`, `_deduplicar_retro_incremental`; `migrar_noticias_v2` conserva firma y sigue idempotente. Sin `DROP`, sin `ALTER`. Los dos `DELETE` son los preexistentes (punto 2).
- **Ruta de sellado:** `snapshot.py` no cambia; pero el sello SÍ consume noticias: snapshot.py:157 pasa `noticias.sentimiento_promedio_por_ticker()` y senales.py:256 sella `puntaje_ia` con peso 0,3 del sentimiento. El cambio de ventana de dedup altera qué titulares alimentan ese promedio (11 republicaciones de 11,9–138 días sobreviven; noticias_on2.md §4). No es lógica del modelo (motor.py) pero es un insumo sellado: **debe declararse en acta** (exigencia 4).
- **Test:** `tests/test_noticias_dedup_lineal.py` leído entero: 7 tests sobre bases sintéticas en tmp (`monkeypatch.setattr(noticias, "DB_PATH", …)`); prueba lineal vs cuadrático con un `SequenceMatcher` contador (N=400 vs 2N=800: mismas comparaciones diarias; vieja > 3,5×), equivalencia dentro de la ventana y el caso declarado fuera de ella, «el más antiguo sobrevive» en las dos direcciones, borrado del análisis de la réplica, idempotencia y marca, esquema aditivo sobre una base «4.6» sin `meta`. `pytest tests/test_noticias_dedup_lineal.py …` → dentro de **48 passed in 6.00s** (junto a los otros cinco archivos nuevos).
- **¿Puede romper el job de las 17:50?** Evidencia de dos corridas reales en `data/noticias.log`: `[2026-09-03T22:00:16Z] dedup retroactivo: {'candidatos': 5286, 'comparaciones': 4921843, 'duplicados_borrados': 20, 'primera_corrida': True} en 615.9s` y `[2026-09-04T21:50:54Z] … {'candidatos': 328, 'comparaciones': 445139, 'duplicados_borrados': 13, 'primera_corrida': False} en 54.0s`. Ambas bajo los 1.800 s del timer; `primera_corrida: True` el 3-sep prueba que la corrida NO ejecutó la migración sobre la base real antes del job. `mki_noticias.py` envuelve la llamada en `try/except` con `enmascarar_secretos`. Riesgo residual que anoto (no bloqueante): `bisect` sobre `fechas` asume orden lexicográfico ISO homogéneo; noticias_on2.md §2 declara medido que las 5.286 filas comparten formato.
- **Identidad del código que corrió:** `git show 7d13f5e:noticias.py | diff -q - noticias.py` → idéntico; mtime de noticias.py 2026-09-03 10:15:31 < 17:50 < commit 18:08:52. El job corrió código sin commitear pero byte-idéntico al commiteado.

## 5. Decisiones registradas (R4)

- `git diff e0179b7~1 4feb32e -- DECISIONES.md | grep "^@@"` → una sola hunk `@@ -7793,3 +7793,208 @@`: el acta §78 se apendizó; nada anterior se reescribió. §78 cubre D1/D2/D3, 2a–2f, 3a–3c, 1d, «cómo se revierte» y lo que decide Nicolás (§78.7 ↔ espera_firma §26–§37, cola §29–§34, leídos en su diff).
- Registro de intentos verificado en la máquina: `GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO = 352`; `backtest.veredicto_51.N_INTENTOS_PREVIO/N_INTENTOS_51 = 352/358`; suma de los tramos nuevos 14+7+1+1+1+36+6 = 66; 286+66 = 352.
- Faltan dos declaraciones (exigencias 4 y 5) y los hitos de cierre (exigencia 6). Asimetría Mac/PC nueva: ninguna en código; `replica.md` propone al Mac como réplica sólo como DECISIÓN PENDIENTE (cola §29).

## 6. Rama y push (R2, R3)

- `git branch --show-current` → `main`. `git log --oneline origin/main..HEAD` → 6 commits (los 4 del rango + `cef52c0`, `ebebe0f`). `git status --porcelain` al abrir: vacío; a las 18:20 aparece ` M tests/test_linea_base.py` (edición concurrente de hoy, fuera del rango).
- `git diff … | grep -nE "^\+.*git (pus|pul|fet)"` → sólo prosa de `replica.md` (`git fetch` + `git show`; «nunca pull, nunca checkout, nunca merge»); ningún script, hook, unit ni workflow nuevo empuja o trae. `replica.md` §7.3 lista un push automático a rama propia como alternativa (i) y la deja como DECISIÓN PENDIENTE de Nicolás: no es código.
- El único cambio que corre en el emisor es el del punto 4; el emisor es este PC (Mac fuera), así que ya corrió (log del 3 y 4-sep). Declarado en §78.4 («Corre por primera vez hoy 17:50»).

## 7. Cifras retiradas (Regla 10)

- Escáner propio (python, patrones leídos de `GEMELO/cifras_retiradas.md`, 19 patrones, marcas ±2 líneas) sobre las líneas del diff y sobre TODOS los `.py` del árbol en `4feb32e`, más el detector de la casa `cifras.reintroducciones()`:
  - En el diff, sin marca reconocible: **`cifras.py:176`** («1,84×») y **`GEMELO/resultados/encargo_corrida_09.md:45`** («1,84×»). Todas las demás menciones (README:20,145; skill:49; evaluacion.py:357,419; RELEVO.md:16,118,133; estado_epistemico:54-55; bifurcaciones.py:104-109; DECISIONES 7821-7822, 7984; bitácora 85-86; adversario:51,59) llevan «era»/«errata»/«retirad»/«derogad» a ±2 líneas.
  - Preexistentes en HEAD y NO tocados por el diff (se inventarían, no rechazan; el diff los vuelve «retirados» al agregar las cuatro filas al registro): GEMELO/bifurcaciones.py:36,54,333; GEMELO/SECUENCIAL/diseno_secuencial.py:53; GEMELO/SECUENCIAL/mde_vs_observado.py:58; GEMELO/SECUENCIAL/trayectoria.py:8; backtest/linea_base.py:152; GEMELO/simulador/calibracion.py:368,536; GEMELO/simulador/potencia_por_metrica.py:14; GEMELO/CONDICIONAL/condicional.py:1063,1708,2084,2141; GEMELO/ventana_larga.py:236; tests/test_control_lineal.py:234; tests/test_epistemico.py:286,403,436,455,744,747,787,789,797,800,836,838; tests/test_bifurcaciones.py:241,246 (ancla de aritmética). Ya lo decía `ESTADO.md` antes del diff («Seis .py citan cifras retiradas sin marca»).
- `pytest tests/test_cifras_arbitro.py` (en los 48 passed): los tres documentos publicados (`cifras.DOCUMENTOS_PUBLICADOS`) sin reintroducciones; el detector caza la rama derogada.

## 8. Lo que el encargo prohibía (§1 y §7)

- Sin 5.1: `backtest/resultados/` no aparece en el rango; `backtest/veredicto_51.py` sólo cambia las constantes N (diff leído). Sin retador: `juez_lineal_d3.py` corre `CONFIGS = ("C1", "C2")` y el campeón (JSON `parametros.configs`); C3 no se corre (pre-registro §2). Sin parche aplicado: punto 1. Sin fuente nueva: `GEMELO/datos.py`, `features.py`, `control_lineal.py`, `experimento.py` no están en el rango; el juez inutiliza `yf.download` (`_prohibir_descarga`, con test) y `ic_dmae_recomputar.py` bloquea `socket`.
- Descargas en la ventana de sellado: los artefactos de la corrida tienen mtime 00:26–12:52 del 3-sep (`ls --time-style=full-iso`), fuera de la ventana. Lo que SÍ cayó en la ventana: la edición de la bitácora (18:02:46) y los commits (18:03:05, 18:08:52), y con el primero la suite del hook. Si esa suite descargó: NO VERIFICADO.

## 9. Hooks, agentes y skills

- `.claude/hooks/` y `.claude/settings.json` no están en el rango (punto 1). `.claude/hooks/guardia-reglas.py` no menciona `migracion-wsl` (grep vacío); el propio hook me bloqueó dos comandos por contener cadenas prohibidas y respondió «La rama de trabajo es main».
- Cambios en `.claude/agents/` y `.claude/skills/` leídos enteros: (a) `cifras-canonicas/SKILL.md` y `estadistica-evaluacion/{SKILL.md,scripts/evaluacion.py}` son dos de los doce bloques y sitios de la cifra vieja: legítimo bajo 1a; el self-test de `evaluacion.py` pasa a 161/238, 138/238 y `mcnemar_exact(72,49)`; (b) `guardian-constitucion.md:3` corrige «rama migracion-wsl en el PC»: legítimo bajo 1d; (c) `integridad-datos.md:71` nota fechada sobre el importador: hallazgo declarado en §78.4; (d) `estadistico-adversario.md:46-63` actualiza V1/V3/V4 a la cifra vigente y declara que V1 sigue bloqueante hasta la firma de V1-bis: legítimo, pero el acta lo describe al revés (exigencia 5). Ninguno toca `GEMELO/DISEÑO.md` (frozen; no está en el rango).

## 10. Verdes (R6)

- `venv/bin/python -m pytest tests/ -q` sobre HEAD `ebebe0f` (18:13–18:19 Chile): **1 failed, 648 passed, 2 xfailed in 332.62s**. Fallo: `tests/test_linea_base.py::test_senales_db_conserva_su_scoring_original — assert 6 == 5` (la sexta fila de gap cero es `2026-09-02 2330.TW`, verificada por producción el 3-sep 18:15, después del verde de las 12:58 y de los commits). El test no está en el diff; el diff no lo causa; pero HEAD está en rojo y «un verde antes del sello no es un verde».
- `venv/bin/python tests/test_motor.py` → «RESULTADO: todas las funciones del motor pasan el test de no-contaminación», exit 0.
- Con la corrección uncommitted del árbol (`git diff -- tests/test_linea_base.py`: censo fijado a `CORTE_SECCION_2`, invariante `>= 5` sobre la base viva): ese test solo → `1 passed in 3.13s`. Suite completa sobre el árbol: relanzada a las 18:22, resultado anexado al pie.
- Los seis archivos de test nuevos/modificados del diff + el árbitro: `48 passed in 6.00s`.

## 11. Cifras publicadas (R9, Regla 12, Regla 14)

- Aritmética independiente (python puro, sin módulos de la casa): 161/238 = 67,6 % Wilson [61,5, 73,3]; 138/238 = 58,0 % [51,6, 64,1]; ventaja 9,66 pp; McNemar b=72, c=49: exacta 0,0451, χ²cc = 4,0 → p 0,0455; retorno 151/243 → [55,9, 68,0]. Coinciden con README/skill/estado.
- Regla firmada, por mi cuenta con `backtest.linea_base` (dedup=False vs True, corte 28-ago): 248 → 238 filas, 34 días en ambas; **10 filas retiradas**, 7 discordantes y las 7 a favor de la base (000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T del 29-jul → sesión 31-jul; las 3 del 3-ago concordantes). Reproduce la frase nueva del README:140-146.
- Clúster de día con código propio (semilla distinta, 20.000 réplicas): IC95 [−6,8, +26,8]; permutación de signo por día p = 0,300. Árbitro: [−7,2, +26,6] y 0,294. Consistente dentro del error de Monte Carlo.
- Doce bloques: `test_cifras_arbitro.py` en verde (los doce fragmentos textuales; cambiar n o la convención mueve los doce; la rama derogada no sobrevive sin marca). Toda cifra nueva en README/estado_epistemico/skill lleva n e intervalo y procedencia (`cifras.sellada()`, cadena canónica compuesta el 30-ago, corte pinchado 28-ago). Etiquetas: horizonte.md «PROPUESTA», juez «PROPUESTA/EXPLORATORIO», enmienda «PROPUESTA para firma», tarjetas y réplica con MEDIDO/PROPUESTA/DECISIÓN PENDIENTE por afirmación; estado_epistemico agrega lo nuevo bajo «PROPUESTAS». No hubo curador: hice yo la lectura de los tres documentos publicados.
- Regla 14: no encontré valores asumidos donde el encargo pidió cómputo; lo no medido está declarado como tal (noticias_on2.md §6 «fase RSS NO MEDIDA»; tarjetas «NO EVALUABLE» con razón).

## 12. Alcance (R7)

El diff hace lo que el encargo ordena (bloques 1–3) y lo cierra en acta. Fuera de lo pedido, sólo notas fechadas de errata sobre texto stale (`docs/RESTAURAR.md:171`, `.claude/agents/integridad-datos.md:71`, `dictamen_08/E.md` pie, `parche_dedup.md` cabecera), declaradas en §78.4/§78.6: son hallazgos convertidos en errata, no arreglos de código. No se sacó nada del diff.

---

## EXIGENCIAS

1. **`cifras.py:176`** — en la docstring de `doce_bloques`, reemplazar «(D1: el 1,84× no circula suelto; entra con n e intervalo o se retira)» por una redacción con marca reconocible, p. ej. «(D1: el ratio 1,84× está **retirado** (3-sep-2026, cifras_retiradas.md); el bloque 9 lo publica recomputado con n e intervalo)». Verificar con `python -c "import cifras; print(cifras.reintroducciones(open('cifras.py').read()))"` → `[]`.
2. **`tests/test_linea_base.py:333` (HEAD)** — commitear la corrección que hoy está sin commitear en el árbol, en su propio commit, con línea de errata en `DECISIONES.md` (test escrito el 25-ago contra la base viva; producción lo cruzó el 3-sep 18:15); correr `./mki tests` en verde ANTES de publicar y fuera de la ventana 17:50–20:30. Ese commit tendrá su propio dictamen.
3. **`GEMELO/control_lineal.py:344-356`** — `delta_mae_ic` se calcula con `inf.bootstrap_bloques(..., anualizar=1)` (escala Sharpe) y se publica al lado de `delta_mae` en pp: corregir el ejecutable (IC de la media —`inf.bootstrap_media` o clúster de día— bajo `delta_mae_ic`, y el de Sharpe bajo su propio nombre) con un test que fije la escala; las erratas en prosa (`control_lineal.md:183`, `ventana_larga.md:237`) se conservan. Regla 11: la corrección va al ejecutable antes que al texto.
4. **`DECISIONES.md` §78.4, viñeta 2c** — errata fechada: el cambio de ventana del dedup altera el insumo de `noticias.sentimiento_promedio_por_ticker()` y con él `senales_ticker.sentimiento_ia` y `puntaje_ia` sellados desde el 3-sep 18:15 (`senales.py:256`, peso 0,3); declarar el corte de método en el insumo (primer sello afectado: 2026-09-03) y dejar a Nicolás la decisión sobre `FEATURE_VERSION`/bump de plataforma. Las filas ya selladas no se tocan.
5. **`DECISIONES.md` §78.1, línea final de D3** — donde dice «`estadistico-adversario` (V1 secundaria)» corregir a «(V1 sigue bloqueante hasta la firma de V1-bis; corrección del director, 12:44)» para que coincida con `.claude/agents/estadistico-adversario.md:52-53`.
6. **`GEMELO/resultados/bitacora_09.md`** (después de la línea 361) — hito fechado de cierre: edición de la bitácora a las 18:02:46; commit `e0179b7` a las 18:03:05 con el hook corriendo la suite dentro de la ventana de sellado; commits `7d13f5e`/`1b638cf`/`4feb32e` a las 18:08:52 con `SKIP_TESTS=1`; el job de las 17:50 corrió `noticias.py` sin commitear y byte-idéntico a `7d13f5e`; y que `ESTADO.md:11` decía «.env en 644» cuando la máquina hoy da 600.
7. **`GEMELO/resultados/encargo_corrida_09.md:45-46`** — sin editar el texto de Nicolás, insertar debajo de la línea 45 una anotación fechada: «[Nota 3-sep-2026: el 1,84× quedó retirado por esta misma instrucción; ver `cifras_retiradas.md` y acta §78]», para que el detector de la casa encuentre la marca a ±2 líneas.


> **Nota de quien aplicó (6-sep-2026).** Dos exigencias citaban `DECISIONES.md`
> por número de línea y **su propia aplicación las desplazó**: es el error
> crónico que vigila
> `test_ninguna_cita_por_numero_de_linea_a_decisiones_quedo_desplazada`, y la
> suite lo detectó. Las dos citas se reescribieron por sección, que es estable.
> Nada más del dictamen se tocó: el juicio, la evidencia y el veredicto son del
> guardián. Qué se aplicó y qué no está en `aplicacion_dictamenes.md`.


## PENDIENTES INVENTARIADOS (fuera del diff; R7 prohíbe arreglarlos de paso)

- `README.md:31` badge «tests-299 passing»: la suite hoy es 649/650 tests; cifra publicada stale, no tocada por el diff.
- Los `.py` preexistentes con cifras retiradas sin marca (lista del punto 7): barrido en tanda propia, con errata o marca, no en este diff.
- `api/main.py:666-668` y `backtest/baselines.py:154` emiten el mismo `Pandas4Warning` que `motor_concat.diff` silencia en motor.py: mismo tratamiento cuando se firme.
- `ESTADO.md:11` («.env sigue en 644») se regenera al cierre; hoy la máquina dice 600.

---
*Este dictamen no aprueba parcialmente ni «con salvedad»: es OBSERVADO hasta que las siete exigencias estén hechas y la suite completa esté en verde después del sello.*

---
**Anexo (Sun Sep  6 18:30:51 -03 2026) — suite completa sobre el árbol de trabajo** (HEAD `ebebe0f` + la corrección uncommitted de `tests/test_linea_base.py` del 6-sep): 649 passed, 2 xfailed, 36 warnings in 316.60s (0:05:16). Confirma que el único rojo de HEAD era ese test y que la corrección lo resuelve; la exigencia 2 sigue en pie porque la corrección no está commiteada ni dictaminada.
