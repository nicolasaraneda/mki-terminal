# `version_reglas_16_3.diff`: la versión de las reglas, R2 y R4 del dictamen 16b y §81.3 (b), en un solo parche del riel de dinero (corrida 16-3, 11-oct-2026). **NO APLICADO.**

> Encargo 16-3, Bloque C (acta §102.4 y §102.6 (3)). Un solo cambio al sellador por noche: la noche del lunes 12 al
> martes 13-oct lleva el camino T (E0.3, aplicado por Nicolás a las 17:49:31 del 11-oct, acta §103), así que esto va
> en **otra noche**, sin otro cambio al sellador, fuera de las 23:30 de Nueva York y fuera de 17:50 a 20:30 de Chile
> para el commit. Quién y cuándo es decisión de Nicolás (tarjeta §89 de `espera_firma.md`).

## Qué contiene (tres archivos, +362/−5: `2 1 dinero/reglas.json`, `56 4 dinero/sello_dinero.py`, `304 0 tests/test_version_reglas_16_3.py`; `git apply --check` limpio sobre HEAD `ad4b829` y sobre el árbol real)

| archivo | qué cambia | por qué |
|---|---|---|
| `dinero/reglas.json` | `version_reglas` 0.2.0-PROPUESTA → **0.3.0-PROPUESTA**, más `version_reglas_nota` (fechada) | **§99.5, firma de Nicolás del 10-oct-2026.** Marca legible en el CSV versionado de la tercera población de filas de E0 (universo de 32 sin TOELY, §95.4). Ninguna regla numérica se mueve (`tests/test_dinero.py` las recomputa). |
| `dinero/sello_dinero.py::decidir` | un ticker declarado en `exclusiones_insumo_e0.tickers` que no está en el censo de operables levanta `ValueError` nombrándolo | **R4 del dictamen 16b.** Hoy un nombre mal escrito se ignora en silencio y deja de excluir. El censo es fijo (membresía al DESDE), así que sólo salta si alguien edita `reglas.json`. |
| `dinero/sello_dinero.py::sellar` | las filas de un intento no verificable llevan en `motivo`, detrás del motivo de E3 y separado por «; », con qué se decidió el timing: (i) con el bloque `timing` del meta (la evidencia nació `.no_verificable`): «timing roto decidido al congelar la evidencia, a las <emision_utc>: la regla available_at … < emisión < apertura objetivo … no se cumplía a ese instante»; (ii) sin bloque `timing` (camino de reserva, hoy no alcanzable por `main()`): «timing roto decidido por la clase de la evidencia (<archivo>, congelada a las <congelado_en_utc>); el reloj del sello (<ts>) no fijó el veredicto» (B1 del auditor: la versión anterior citaba el reloj del sello y podía sellar una frase falsa en un campo inmutable); (iii) evidencia canónica con timing roto en la tabla de intentos (código muerto en producción: esas ramas retornan antes con cero filas): el reloj del sello | **§81.3 (b), firmada en §102.6 (3).** F2 del dictamen 16-2. Sin cambio de esquema; las filas de `sellos_dinero` no cambian. **R3 del auditor, declarado:** `motivo` de un intento pasa a ser un campo COMPUESTO, no parseable por máquina (por qué «nada» y por qué el timing está roto), y viaja al CSV versionado `data/backups/sello_dinero_no_verificables.csv`, que nace con el primer intento (unos 300 caracteres por fila). |
| `dinero/sello_dinero.py::estado` | clave aditiva `por_reglas_sha256`: por población (hash, versión) sesiones selladas, las que cuentan para N, filas, desde y hasta, en orden de primera fecha | **R2 del dictamen 16b.** `sesiones_selladas` y `filas` se agregaban sobre las dos poblaciones sin separarlas. **Alcance declarado (R1 del auditor 16-3):** agrupa SÓLO `sellos_dinero` (no la tabla de intentos) y SÓLO por reglas; la población de MÉTODO es `sellador_sha256` (hoy 3 contra 2 de reglas; tras aplicar, 4 contra 3) y no se agrupa acá. La API **no** lo sirve: servirlo exige enmendar `api/CONTRATO.md` antes (un test lo fija). |
| `tests/test_version_reglas_16_3.py` | 15 tests (14 corren sin la base real; 1 sobre la base real en `mode=ro`) | Escritos antes del código; **sobre HEAD, con el archivo FINAL (B3 del auditor): 10 rojos por su propia aserción, 4 verdes de control** (`test_R4_toely_sigue_saliendo…`, `test_las_filas_de_un_sello_no_llevan_la_nota…`, `test_sin_cambio_de_esquema…`, `test_la_api_no_sirve_el_desglose…`), 1 saltado (`GEMELO/resultados/dictamen_16_3/evidencia/pytest_version_reglas_sobre_HEAD.txt`). Con el parche: 14 passed, 1 skipped; los seis archivos del riel más `test_senal_larga.py`: 199 passed, 12 skipped, 2 failed del control (artefactos ausentes en el worktree; verdes en el árbol real). |

**Huellas.** Del parche: **`5acdb3e2967e794cf21c981cb83544a5958222fba053fa1635f0e48b584667cd`** (versión final, tras B1 del
auditor; la que el auditor dictaminó era `f164b232…`, y lo que cambió entre las dos está en la bitácora §5.2). Pre
imágenes que el diff exige (B2/R6 del auditor): `git rev-parse HEAD:dinero/sello_dinero.py` =
`d1cdef8a860e90b0bb949b8e9f0944851d824862` y `HEAD:dinero/reglas.json` = `279d088491b933176927b8876e599657070f1d16`. Tras
aplicar: `dinero/reglas.json` `6f3715275dadc5279e3661a9fcc1dc64af799e0a140de3a7f3eff17765ab444a` (es el `reglas_sha256` que
llevarán las filas nuevas) y `dinero/sello_dinero.py` **`2a9c2d57f9c4cbf5eb925526549e565a481c5d6678aadeb2a9227034812280f6`**
(el `sellador_sha256` de las filas nuevas, leído con el método del propio sellador; `VERSION_SELLO` sigue `E0.3`, que
fijó el corte de método del camino T). Aplicar crea una CUARTA población de `sellador_sha256` (`480fbdc9…`,
`93db9b70…`, `cd0e70c8…`, `299a7627…` desde el 13-oct, y ésta) mientras `por_reglas_sha256` muestra TRES.

**Lo que NO cambia.** Las filas selladas (ninguna se reescribe); la tabla de intentos y la principal conservan las 36
columnas de HEAD (test); el sorteo, el censo, el gate de invariancia, `evaluar_timing`, la regla maestra, el timer. La
sesión del 12-oct (primer sello E0.3) se sella con 0.2.0-PROPUESTA y `b6080eee…`: este parche es posterior.

## Dictamen del `auditor-lookahead` (20:19:03 → 20:35:24): APLICABLE CON EXIGENCIAS

`GEMELO/resultados/dictamen_16_3/auditor_version_reglas.md`. Sin fuga demostrada (gate `INVARIANTE` con 2 y 6 cortes sobre
el insumo real; 40 huellas de decisión idénticas a HEAD; `estado()` sobre la base real con las 13 claves anteriores byte a
byte iguales, sha `eaf5ad7a…`); ninguna fila ni cifra publicada se mueve. Tres BLOQUEANTES, atendidas antes de cerrar la
corrida: **B1** (el camino de reserva citaba el reloj del sello y podía sellar una frase falsa: corregido, cita la clase
de la evidencia y `congelado_en_utc`, con el caso falso fijado por test), **B2** (preflight y postflight de R4: en la
receta, abajo; preflight sobre HEAD ya corrido el 11-oct 20:48 en `mode=ro`: censo 33, TOELY dentro, `decidir` 32
operables con `excluidos_universo = ['TOELY']`, gate `INVARIANTE`), **B3** (rojos sobre HEAD retomados con el archivo
final: 10/4/1). Recomendadas: R1 y R3 declaradas arriba; R2 (test de la base real sin posiciones) aplicada; R4 (separar
«fuera del universo» de «fuera del censo» en el raise: hoy `techo_usd` bajo ~72 USD sacaría a TOELY del censo y mataría la
noche) y R5 (el riel de dinero no tiene vigía: ningún chequeo mira `sello_dinero.db`) van a la tarjeta §89 como opciones.

## Receta de aplicación (una noche sin otro cambio al sellador; acto de Nicolás)

Fuera de 17:50 a 20:30 de Chile, fuera de las 23:30 de Nueva York, en una noche sin otro cambio al sellador, y DESPUÉS del
primer sello E0.3 (martes 13-oct 00:30) si se quiere que las cuatro poblaciones queden ordenadas. Un verde antes del sello
no es un verde: la suite se corre después de la ventana.

```bash
cd ~/dev/mki-terminal
systemctl --user is-active mki-sello-dinero.service      # 0. tiene que decir: inactive (regla operativa §81.5 a)
pgrep -fa "dinero.sello_dinero" || echo "sin sellador vivo" # 0b. una corrida manual no aparece en is-active (R6.5)
git status --porcelain dinero/                           # 1. vacío: nadie tocó dinero/ después del dictamen
git rev-parse HEAD:dinero/sello_dinero.py HEAD:dinero/reglas.json   # d1cdef8a… y 279d0884…: las pre imágenes del diff
sha256sum GEMELO/propuestas/parches/version_reglas_16_3.diff   # 2. 5acdb3e2…
git apply --numstat GEMELO/propuestas/parches/version_reglas_16_3.diff   # 2 1 / 56 4 / 304 0
venv/bin/python -m dinero.sello_dinero --estado | head -5 # 6. el contador ANTES (sesiones_que_cuentan_para_N): se declara
venv/bin/python - <<'PY'                                  # 3. PREFLIGHT de R4 con el módulo de HEAD, mode=ro (B2)
import sys; sys.path.insert(0, ".")
from dinero import sello_dinero as S, precios, cuenta_papel as CP, universo_dinero as U
base = precios.cargar_congelado(); cfg = U.reglas(); ops = CP.universo_operable(base, cfg, hasta=CP.DESDE)
assert "TOELY" in ops and len(ops) == 33, (len(ops), "TOELY" in ops)
ruta, _ = S.ultima_extension(); c = S.insumo(ruta); d = S.decidir(c, c.index.max(), cfg)
assert d["excluidos_universo"] == ["TOELY"] and len(d["operables"]) == 32, d["excluidos_universo"]
print("preflight R4 ok:", len(ops), d["excluidos_universo"])
PY
date                                                      # 11. corte de método: se declara en el acta siguiente
git apply --check GEMELO/propuestas/parches/version_reglas_16_3.diff
git apply GEMELO/propuestas/parches/version_reglas_16_3.diff
date
sha256sum dinero/reglas.json dinero/sello_dinero.py       # 6f371527…  y  2a9c2d57…
venv/bin/python - <<'PY'                                  # 3b. POSTFLIGHT: el gate con el módulo parchado (B2)
import sys; sys.path.insert(0, ".")
from dinero import sello_dinero as S
ruta, _ = S.ultima_extension(); print(S.gate_previo_al_sello(S.insumo(ruta)))   # INVARIANTE, sin ValueError
PY
venv/bin/python -m pytest tests/ -q                       # 8. suite completa del árbol real, ~8 min, fuera de la ventana
venv/bin/python tests/test_motor.py                       # anti look-ahead del motor
./mki auditoria
git add dinero/reglas.json dinero/sello_dinero.py tests/test_version_reglas_16_3.py
git commit -m "Parche version_reglas 0.3.0-PROPUESTA, R2 y R4 del 16b, §81.3 b (acta §104, tarjeta §89): aplicado a mano por Nicolas"
# sin SKIP_TESTS=1: el hook corre la suite con el test nuevo adentro
```

Reversión (4): `git apply -R GEMELO/propuestas/parches/version_reglas_16_3.diff` del MISMO archivo y borrar
`tests/test_version_reglas_16_3.py`. Si la suite da un rojo que no sea de entorno, se revierte y se declara; lo que se
pierde es que la noche siguiente sella con 0.2.0-PROPUESTA (ninguna sesión se pierde). **Lo que el parche agrega como modo
de falla (B2 y R5 del auditor):** si el raise de R4 saltara (nombre mal escrito, `techo_usd` bajo ~72 USD, un recongelado
sin TOELY), la noche muere en el gate con cero filas, cero intentos y cero divergencias, y el único rastro es el traceback
en `data/sello_dinero.log`: el vigía no mira el riel de dinero. La mañana siguiente se revisa `--estado` y `journalctl
--user -u mki-sello-dinero` (10).

## Predicción falsable para el primer sello DESPUÉS de aplicar (`mode=ro`)

```sql
SELECT fecha_insumo, reglas_version, substr(reglas_sha256, 1, 8), substr(sellador_sha256, 1, 8), version_sello, COUNT(*)
FROM sellos_dinero GROUP BY 1,2,3,4,5 ORDER BY 1 DESC LIMIT 3;
-- esperado en la primera fila: <fecha>, 0.3.0-PROPUESTA, 6f371527, 2a9c2d57, E0.3, 32
```
`venv/bin/python -m dinero.sello_dinero --estado` → `por_reglas_sha256` con TRES entradas (125a8602… / b6080eee… /
6f371527…), cuya suma de `sesiones_selladas` y `filas` iguala `sesiones_selladas` y `filas` del estado; el contador
`sesiones_que_cuentan_para_N` sube en 1 respecto del declarado antes de aplicar (hoy 12; 13 si la del 12-oct cuenta; 14
tras el primer sello con el parche si cuenta), y `data/sello_dinero.log` dice `"excluidos_universo": ["TOELY"]`. Un
intento no verificable posterior lleva en cada `motivo` «timing roto decidido al congelar la evidencia, a las …». Si
`reglas_version` sigue en 0.2.0-PROPUESTA, el parche no se aplicó o se aplicó después del sello.
