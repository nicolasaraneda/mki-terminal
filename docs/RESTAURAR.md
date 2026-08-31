# Restaurar desde el backup — el camino de vuelta

Escrito para alguien que acaba de perder el disco y está apurado. Si esa
persona sos vos ahora mismo: andá directo a la sección "Procedimiento", el
resto es contexto que podés leer después.

## Lo primero que hay que saber

`data/backups/*.csv` se commitea todos los días desde julio de 2026 (job
`mki_backup.py`, 18:40 hora Chile) y hasta el 31-ago-2026 **nunca había
existido un importador que lo usara**. Este documento y
`scripts/restaurar_backup.py` son ese importador, escritos y probados esa
noche. Antes de esto, el respaldo diario era una promesa no verificada.

**Reglas duras del importador, sin excepción:**
- Nunca escribe en `senales.db` ni en `noticias.db` — ni para leer en modo
  escritura. Reconstruye SIEMPRE en una base nueva, en una ruta temporal.
- No corrige nada del contenido del CSV. Si algo no vuelve idéntico, eso se
  reporta como hallazgo, nunca se disimula.

## Qué se pierde y qué no en el viaje de ida y vuelta

Esto se midió, no se supuso, corriendo el importador contra los CSV reales
del 30-ago-2026 y comparando contra `senales.db`/`noticias.db` en modo
lectura. Tres clases de hallazgo, de menor a mayor importancia:

### 1. Artefacto cosmético, recuperado sin pérdida

Cualquier columna `INTEGER` que tenga al menos una fila `NULL` (ej.
`n_muestra`, `ventana_betas`, `descarga_ok`, `descarga_total`) sale del
`pd.read_sql_query` + `to_csv` de `snapshot.py` como float: el CSV dice
"120.0", no "120". Esto YA está en los CSV versionados, no lo introduce el
importador. Se recupera exacto (120.0 → 120) porque son enteros sin parte
fraccionaria real; si alguna vez apareciera una fracción de verdad en una
columna declarada `INTEGER`, el importador NO la trunca en silencio: la
conserva y lo reporta como hallazgo.

### 2. Ambigüedad NULL / cadena vacía — real, y ya causó un fallo

Un campo vacío en un CSV no distingue entre "esto es `NULL`" y "esto es la
cadena vacía `''`". Para la mayoría de las columnas de texto (nullable, sin
`DEFAULT`), tratar un vacío como `NULL` es la lectura correcta — así es como
`snapshot.py`/`noticias.py` representan "todavía no calculado". Pero tres
columnas están declaradas `TEXT NOT NULL DEFAULT ''`:
`titulares.tickers`, `divergencias.explicacion`, `analisis.tickers_afectados`.
Ahí un vacío del CSV es la cadena vacía real — nunca puede haber sido
`NULL`, porque la base nunca lo permitió. La primera corrida del importador
intentó insertar `NULL` en `titulares.tickers` y **falló con
`IntegrityError: NOT NULL constraint failed`** — el hallazgo se corrigió en
el propio importador (`TEXTO_DEFECTO_VACIO` en `restaurar_backup.py`), pero
queda documentado acá porque es la prueba de que la ambigüedad es real, no
teórica.

### 3. El backup es una foto fija — compararlo contra la base viva de HOY no es la prueba correcta

Al correr `--verificar` el 31-ago-2026 contra el backup del 30-ago-2026
(19:25), tres tablas de noticias mostraron MENOS filas en el backup que en
la base viva (`titulares` 4.733 vs 4.873, `analisis` igual, `resumen_dia`
17 vs 19) — **esto es normal**: la base viva siguió creciendo después de
que se tomó la foto, y noticias solo se agregan, nunca se borran. El
importador verifica esta dirección como invariante (`n_restaurado <=
n_original` — si algún día apareciera al revés, ESO sí sería una alarma).

Pero dos tablas mostraron una discrepancia que NO es explicable por simple
crecimiento — la foto tiene filas que la base viva ya no tiene:

- **`snapshots`**: el backup tiene una fila con `fecha='2026-08-29'`
  (`plataforma_version=5.0.2`) que la base viva no tiene; la base viva
  tiene una fila con `fecha='2026-08-28'` (`plataforma_version=5.0.3`) que
  el backup no tiene. Es una sustitución, no un crecimiento.
- **`verificacion_apertura`**: el backup tiene 7 filas para
  `fecha_senal='2026-08-27'` (los 7 tickers de esa fecha) que la base viva
  no tiene, y la base viva no tiene ninguna fila de reemplazo para esas
  claves.

**Confirmado, leyendo `DECISIONES.md` §36.1 y §36.7 (verificado por
`guardian-constitucion` al cerrar esta tanda, 31-ago-2026): esto NO es una
violación de la Constitución 5.0.** Ambas discrepancias las explica
íntegramente la composición canónica del modo sombra resuelta el 30-ago:

- La fila `fecha='2026-08-29'` del backup es la fila espuria de sábado que
  la §36.1 identifica y descarta explícitamente (2026-08-29 es sábado; no
  hay sesión que sellar ese día). No es una fila sellada legítima perdida.
- Las 7 filas de `verificacion_apertura` del 27-ago que el backup tiene y
  la base viva no: el 27-ago es una fecha cuya región canónica pasó a ser
  la del PC (regla `>= 2026-08-26` ⇒ serie PC, §36.7), y la composición
  sustituyó esas filas por su equivalente de la región canónica sin
  reescribir ninguna fila individual — es una recomposición de qué SERIE
  cuenta como oficial para ese rango de fechas, el mecanismo que el propio
  §36 diseñó y documentó, no una pérdida.
- La cifra viva de `verificacion_apertura` (253) es exactamente la que la
  §36.7 predice tras la composición, y la invariante 4a (`fecha >=
  2026-08-26` ⇒ `plataforma_version = 5.0.3`) da cero violaciones sobre la
  base real.

**Conclusión: el importador funciona bien** — reproduce fielmente lo que el
CSV tenía en el momento del backup (30-ago, 19:25), y la base viva cambió
después por una razón deliberada y ya documentada en `DECISIONES.md`. No
hace falta escalar nada. Esto queda como el ejemplo de referencia de cómo
leer una discrepancia backup-vs-viva: antes de tratarla como pérdida,
revisar si el rango de fechas cae dentro de una cirugía de datos ya
documentada.

## Procedimiento de restauración completa

Escenario: el disco murió, `senales.db` y `noticias.db` no existen, y lo
único que sobrevive es el repo de git (con `data/backups/*.csv` versionado).

```bash
# 1. Cloná el repo si hace falta.
git clone <url-del-repo> mki-terminal
cd mki-terminal

# 2. Restaurá a una base NUEVA en una ruta temporal (nunca pisa nada real).
python3 scripts/restaurar_backup.py --destino /tmp/mki_restaurado

# 3. Revisá la salida: cada tabla dice cuántas filas del CSV se importaron.
#    Cualquier línea que diga "hallazgo:" hay que leerla antes de seguir.

# 4. El último sello restaurado se imprime al final. Compará esa fecha
#    contra la fecha del último commit "Backup diario {fecha}" en el log:
git log --oneline -1 -- data/backups/senales_snapshots.csv

# 5. Si las dos bases (senales_restaurado.db, noticias_restaurado.db) se
#    ven bien, RECIÉN AHÍ copialas al lugar que corresponde:
cp /tmp/mki_restaurado/senales_restaurado.db ./senales.db
cp /tmp/mki_restaurado/noticias_restaurado.db ./noticias.db

# 6. Confirmá que el sistema arranca contra la base restaurada:
./mki estado
```

**Lo que este procedimiento NO recupera, y hay que saberlo antes de
confiar en él:**

- **Cualquier cosa sellada después del último backup commiteado.** El job
  de backup corre a las 18:40 hora Chile; una restauración siempre pierde,
  como mínimo, el snapshot y las verificaciones del día en que el disco
  murió (si murió antes de las 18:40) y potencialmente el día anterior si
  el backup de esa noche nunca llegó a commitearse. **No hay forma de
  recuperar eso desde el CSV — no existe.**
- **`AUTOINCREMENT` de SQLite.** El importador inserta los `id` explícitos
  que trae el CSV (no deja que SQLite reasigne), así que los IDs existentes
  se preservan, pero la tabla interna `sqlite_sequence` (el próximo ID a
  usar) arranca de cero en la base nueva. Si el sistema vuelve a escribir
  sobre la base restaurada, SQLite recalculará el próximo ID a partir del
  máximo existente la primera vez que inserte — no debería colisionar, pero
  no se verificó explícitamente en esta sesión.
- **`PRAGMA`s no funcionales** (`user_version`, etc.) — no se preservan
  porque no forman parte de ninguna tabla; hoy están todos en su valor por
  defecto en la base real, así que no hay nada que perder, pero un
  importador futuro que dependa de un `user_version` != 0 tendría que
  agregarlo.

## Verificar la fidelidad de una restauración vieja

```bash
# Compara la restauración contra las bases reales del repo, SI existen
# (si no existen — el escenario real de "perdí el disco" — esto se salta).
python3 scripts/restaurar_backup.py --destino /tmp/mki_restaurado --verificar
```

Esto compara, tabla por tabla, por HASH DE CONTENIDO (no por hash del
archivo — el formato de página de SQLite no es determinístico entre bases
construidas de formas distintas) — ordenado por clave primaria, así que
detecta cualquier fila que cambió de valor, no solo las que cambiaron de
cantidad.

## Pruebas

`tests/test_restaurar_backup.py`, en la suite normal
(`python -m pytest tests/ -q`): verifica que ninguna fila del CSV se pierde
ni se duplica al importar, que el hash de contenido es reproducible entre
dos restauraciones independientes desde el mismo CSV, que la coacción de
tipos recupera el artefacto de pandas sin pérdida, que el caso
`NOT NULL DEFAULT ''` no rompe, y (si `senales.db`/`noticias.db` existen en
el checkout) que `verificacion_puntaje` — la única tabla que hoy coincide
exacta con la base real — se mantiene así, y que ninguna tabla de noticias
tiene menos filas en la base real que en un backup viejo (la única
dirección de discrepancia que sería una alarma real).
