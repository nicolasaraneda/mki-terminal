# Parche de `snapshot.py:140` — expediente listo para aplicar

**Autor:** Frente C de la segunda tanda (agente de solo lectura sobre la
ruta de sellado). **No aplica nada.** `snapshot.py` no fue tocado ni
editado de prueba; `senales.db` se leyó siempre en `mode=ro`. No hay
commit ni push de este trabajo. Nicolás aplica el parche cuando lo decida
— este documento existe para que le tome un minuto y no una investigación.

**Contra qué se preparó:** `HEAD` en el momento de escribir esto es
`01a2e98e0f2233dc9c1a2fa02db2ab447b6ee6f5` (2026-09-01). Otros frentes de
esta misma tanda están commiteando en paralelo a rutas que no tocan
`snapshot.py`; el número de línea citado abajo (140) es estable contra
`snapshot.py` tal como está en ese `HEAD` — verificar con
`grep -n "proxima_sesion_despues_de(exchange, ahora_utc)" snapshot.py`
antes de aplicar el diff, por si alguien tocó el archivo entretanto (nadie
debería: está en la lista de intocables).

---

## 1. El parche exacto

**Precondición verificada:** `available_at` (variable local de
`ejecutar_snapshot`, tipo `str` en formato ISO-8601 con offset) ya existe
y ya tiene el valor correcto en el punto exacto donde se necesita. Se
calcula en las líneas 123-135, **antes** del bucle de la línea 136, como
el cierre UTC de la sesión del SOX efectivamente usada
(`calendarios.cierre_utc("XNYS", sox_fecha)`), con fallback a
`ts_emision` (el propio reloj de pared) si no hay `sox_fecha` o si
`cierre_utc` lanza una excepción — en ese caso de fallback el
comportamiento quedaría objetivamente IGUAL al actual (no hay regresión:
si no hay ancla mejor, se usa la misma que hoy). No hace falta agregar
ningún cálculo nuevo, ninguna importación nueva (`datetime` ya está
importado en la línea 27) ni ningún parámetro nuevo — es un cambio de una
sola expresión.

```diff
--- a/snapshot.py
+++ b/snapshot.py
@@ -136,9 +136,12 @@ def ejecutar_snapshot(origen: str, ventana_betas: int = motor.VENTANA_BETAS_DE
         for _, fila in pred.iterrows():
             t = fila["Ticker"]
             exchange = EXCHANGE_POR_TICKER.get(t, "XNYS")
             try:
-                sesion_obj, _, _ = calendarios.proxima_sesion_despues_de(exchange, ahora_utc)
+                # Corrección (Frente C, segunda tanda): la sesión objetivo se
+                # ancla en `available_at` (cuándo era conocible el insumo),
+                # NUNCA en el reloj de pared del proceso. Con `ahora_utc` un
+                # sello tardío que cruza medianoche/01h UTC salta a la sesión
+                # siguiente porque la asiática ya abrió — ver
+                # GEMELO/resultados/parche_snapshot140.md y dedup_opciones.md.
+                sesion_obj, _, _ = calendarios.proxima_sesion_despues_de(
+                    exchange, datetime.fromisoformat(available_at))
             except Exception:
                 continue
             predicciones.append({
```

Verificado con `patch --dry-run` (no se aplicó de verdad, solo se probó
que el hunk calza sin ambigüedad contra el `snapshot.py` actual):

```
$ patch -p1 --dry-run < parche_snapshot140.diff
patching file snapshot.py
```

**Nada más cambia.** `ahora_utc` (línea 111) sigue existiendo y se sigue
usando para `ts_emision`/`timestamp_utc` (eso SÍ debe seguir siendo el
reloj de pared: es el instante real de emisión, no el ancla conceptual de
la sesión objetivo). El único punto que cambia de ancla es el cálculo de
`sesion_objetivo` en la línea 140.

---

## 2 y 3. Los tests

Un solo archivo nuevo, listo para copiar a
`tests/test_sello_tardio_sesion_objetivo.py`. Contiene el test de fijación
(#2) y la contraprueba (#3), con una sola diferencia entre ambos: el
segundo verbaliza explícitamente la colisión de destino documentada en
`dedup_opciones.md` (el síntoma observable — el duplicado — no solo el
valor). Los dos usan el mismo mecanismo de control: una subclase de
`datetime` que reemplaza `snapshot.datetime` (así que `datetime.now(tz)`
dentro de `ejecutar_snapshot` devuelve un instante fijo) y un
`motor.prediccion_apertura_al` fijo (fecha de SOX controlada). Ningún
test toca `senales.db` real — cada uno usa su propia DB temporal
(`tmp_path`), igual que `tests/test_autonomia.py`.

```python
# tests/test_sello_tardio_sesion_objetivo.py
# ============================================================
# Frente C, segunda tanda — fija que sesion_objetivo se calcula desde
# available_at (cuándo era conocible el insumo), no desde el reloj de
# pared del proceso (ahora_utc en snapshot.py:111). Contraprueba: sin
# el parche de snapshot.py:140, este archivo FALLA (ver
# GEMELO/resultados/parche_snapshot140.md).
# ============================================================

import os
import sys
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import pytest

import calendarios
import motor
import noticias
import senales
import snapshot


class _RelojFalso(datetime):
    """Sustituye datetime.now() dentro de snapshot.py por un instante fijo,
    sin tocar date.today() (snapshot.py los usa por separado)."""
    _instante = None

    @classmethod
    def now(cls, tz=None):
        return cls._instante if tz else cls._instante.replace(tzinfo=None)


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    """DB temporal + motor completamente controlado: sin red, sin
    depender de datos de mercado reales."""
    monkeypatch.setattr(senales, "DB_PATH", str(tmp_path / "senales_test.db"))
    monkeypatch.setattr(noticias, "sentimiento_promedio_por_ticker", lambda: {})
    monkeypatch.setattr(snapshot, "salud_descarga",
                        lambda fecha: {"ok_n": 1, "total": 1, "caidos": [],
                                       "completa": True})
    monkeypatch.setattr(motor, "puntaje_v0_al",
                        lambda fecha: pd.DataFrame(
                            {"Ticker": ["005930.KS"], "Puntaje v0": [0.1]}))
    monkeypatch.setattr(motor, "regimen_al", lambda fecha: {"etiqueta": "test"})
    monkeypatch.setattr(motor, "roca_chip_al", lambda fecha: {"valor": 50.0})
    monkeypatch.setattr(motor, "divergencias_al", lambda fecha: [])

    def instalar_prediccion(sox_fecha: str):
        """La predicción del anticipador usa un movimiento del SOX cuyo
        cierre fue `sox_fecha` — eso fija available_at de forma controlada,
        exactamente como lo hace snapshot.py:129-135."""
        monkeypatch.setattr(
            motor, "prediccion_apertura_al",
            lambda fecha, ventana=motor.VENTANA_BETAS_DEFAULT, dias_earnings=None:
                pd.DataFrame([{
                    "Ticker": "005930.KS",
                    "Apertura estimada %": -1.0,
                    "R2": 0.3,
                    "Intervalo80 pp": 2.0,
                    "N muestra": 120,
                    "Beta de contagio": 0.5,
                    "SOX usado %": -0.8,
                    "SOX fecha": sox_fecha,
                }]))

    def fijar_reloj(instante_utc_iso: str):
        _RelojFalso._instante = datetime.fromisoformat(instante_utc_iso)
        monkeypatch.setattr(snapshot, "datetime", _RelojFalso)

    return {"prediccion": instalar_prediccion, "reloj": fijar_reloj}


def _sesion_objetivo_sellada(ticker: str = "005930.KS") -> str:
    conn = senales.get_connection()
    fila = conn.execute(
        "SELECT sesion_objetivo FROM senales_ticker WHERE ticker = ?",
        (ticker,)).fetchone()
    conn.close()
    return fila[0] if fila else None


# ------------------------------------------------------------
# Test 2 — fija el comportamiento correcto (pin de especificación)
# ------------------------------------------------------------
def test_sesion_objetivo_sigue_available_at_no_el_reloj_de_pared(entorno):
    """Sello que cruza medianoche/las 01h UTC (KRX ya abrió su sesión del
    día siguiente cuando el proceso por fin sella): la sesión objetivo debe
    seguir siendo la que corresponde al cierre del SOX usado
    (`available_at` = cierre XNYS 2026-07-29T20:00:00Z), NUNCA la que salta
    por el reloj de pared. La sesión correcta, verificada independientemente
    contra el calendario de XKRX: XKRX abre el 2026-07-29 y el 2026-07-30 a
    las 00:00 UTC cada una — `available_at` (20:00 UTC del 29-jul) cae
    DESPUÉS de que abrió la sesión del 29 y ANTES de que abra la del 30, así
    que la sesión objetivo correcta es 2026-07-30."""
    entorno["prediccion"]("2026-07-29")
    # Reloj de pared: sella recién a la 01:23:34 UTC del día siguiente —
    # tarde, ya con XKRX habiendo abierto su sesión del 30-jul (00:00 UTC).
    entorno["reloj"]("2026-07-30T01:23:34+00:00")

    resultado = snapshot.ejecutar_snapshot("test")
    assert resultado["snapshot"] is True

    assert _sesion_objetivo_sellada() == "2026-07-30"


# ------------------------------------------------------------
# Test 3 — contraprueba: reproduce el defecto documentado y FALLA HOY
# ------------------------------------------------------------
def test_reproduce_defecto_duplicado_31_jul_HOY_FALLA(entorno):
    """Reproduce, con los timestamps reales del par documentado en
    GEMELO/resultados/dedup_opciones.md (sesión objetivo 2026-07-31, primer
    par KRX/TWSE/TSE): la fila emitida el 2026-07-29 pero sellada tarde
    (2026-07-30T01:23:34 UTC, el timestamp real recuperado de `snapshots`)
    aterriza HOY en sesion_objetivo='2026-07-31' — la MISMA sesión que la
    emisión fresca y a tiempo del 2026-07-30. Esa colisión es el duplicado;
    el origen es que snapshot.py:140 usa `ahora_utc` (01:23:34 UTC, ya
    después de que XKRX abrió su sesión del 07-30) en lugar de
    `available_at` (cierre XNYS del 07-29, 20:00 UTC, ANTES de esa
    apertura).

    Este test FALLA hoy contra snapshot.py sin parchear, porque hoy sella
    '2026-07-31' en vez de '2026-07-30'. Pasa contra la versión parcheada
    de snapshot.py:140 (ver GEMELO/resultados/parche_snapshot140.md)."""
    entorno["prediccion"]("2026-07-29")
    entorno["reloj"]("2026-07-30T01:23:34+00:00")

    resultado = snapshot.ejecutar_snapshot("test")
    assert resultado["snapshot"] is True

    sesion_obj = _sesion_objetivo_sellada()
    assert sesion_obj != "2026-07-31", (
        f"defecto reproducido: selló '{sesion_obj}' — el reloj de pared "
        "cruzó la apertura de XKRX del 07-30 y saltó a la sesión "
        "siguiente, duplicando el destino de la emisión fresca del 07-30")
    assert sesion_obj == "2026-07-30"
```

### Evidencia de que falla hoy y pasa parcheado (regla de la casa #1 y #2)

No basta con decirlo en prosa: lo corrí. Contra el `snapshot.py` real
(sin tocar), los dos tests **fallan hoy**, ambos con el mismo síntoma
(`AssertionError: assert '2026-07-31' == '2026-07-30'` /
`assert '2026-07-31' != '2026-07-31'`). Después apliqué el diff de arriba
**sobre una copia en `/tmp`** (nunca sobre el `snapshot.py` del repo) y
corrí el mismo archivo de test con esa copia inyectada como módulo
`snapshot` vía `PYTHONPATH` (sin el `sys.path.insert` de la primera línea
del test, que de otro modo fuerza el `snapshot.py` real — se restaura tal
cual al pegar el archivo en `tests/`): **2 passed**. La corrección
propuesta arregla exactamente lo que dice arreglar, ni más ni menos, y
quedó demostrado contra el código, no solo argumentado.

---

## 4. Filas históricas afectadas — auditoría contra `senales.db` (mode=ro)

**Método:** sobre las 279 filas de `senales_ticker` que tienen una
predicción real sellada (`exchange` y `sesion_objetivo` no nulos — las
otras 640 de las 919 totales son filas de `puntaje_v0` sin beta, no
tienen `sesion_objetivo` que pueda estar mal), recalculé, para cada una,
`calendarios.proxima_sesion_despues_de(exchange, available_at)` — la
fórmula que el parche instala — y comparé contra el `sesion_objetivo`
ya sellado. Las 279 filas tienen `available_at` y `timestamp_utc` no
nulos, así que la auditoría es completa: no hay ninguna fila de las 279
que no se pudo evaluar por falta de dato. Esto usa `calendarios`, la
misma librería de producción, pero con el ancla correcta (`available_at`)
— no reproduce el mecanismo que produjo el número erróneo (que ancla en
`ahora_utc`), así que no cae bajo la regla de la casa #1.

**Resultado: 25 filas selladas tienen `sesion_objetivo` distinto del que
da `available_at`.** Se descomponen en dos grupos de origen distinto:

### 4.1 — Las 10 filas del lado "viejo" de los 10 pares ya documentados

`dedup_opciones.md` ya había encontrado 10 pares (20 filas) explicados por
este defecto, sobre las sesiones objetivo 2026-07-31 (7 pares) y
2026-08-05 (3 pares). Mi auditoría, corriendo independientemente sobre
`available_at`, confirma algo que ese documento no necesitó decir porque
no era su pregunta: **de las 20 filas de esos 10 pares, solo 10 —el lado
"viejo", el emitido antes— tienen `sesion_objetivo` objetivamente mal.**
Las otras 10 (el lado "fresco") ya apuntaban, por su cuenta, a la sesión
que `available_at` also les asigna — no son parte del recuento de "filas
mal", son la fila correcta con la que el lado viejo choca.

| Emisión (fecha_senal) | Sesión sellada | Sesión correcta (`available_at`) | Filas | `timestamp_utc` real |
|---|---|---|---|---|
| 2026-07-29 | 2026-07-31 | **2026-07-30** | 7 (000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T) | 2026-07-30T01:23:34 UTC |
| 2026-08-03 | 2026-08-05 | **2026-08-04** | 3 (2330.TW, 3436.T, 4063.T) | 2026-08-04T02:57:44 UTC |

### 4.2 — Retomando la pregunta abierta: 15 filas MÁS, sin pareja, que `dedup_opciones.md` no pudo ver

`dedup_opciones.md` buscaba duplicados con
`GROUP BY ticker, sesion_objetivo HAVING COUNT(*) > 1` — un método que por
construcción **solo ve el defecto cuando choca con otra fila**. Retomando
la pregunta abierta de anoche (filas del 5-ago sin pareja que no se pudo
reconstruir): sí reproduce, y es más grande de lo que se sospechaba —
**15 filas adicionales, en dos grupos, ninguno documentado hasta ahora**:

| Emisión (fecha_senal) | Sesión sellada (HOY, mal) | Sesión correcta (`available_at`) | Filas | `timestamp_utc` real | Por qué quedó sin pareja |
|---|---|---|---|---|---|
| **2026-08-05** | 2026-08-07 | **2026-08-06** | 7 (000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T) | 2026-08-06T01:38:52 UTC | El snapshot del 2026-08-06 (a tiempo, 22:24:52 UTC) tuvo una caída total de datos ese día: `motor.puntaje_v0_al` no devolvió fila para NINGUNO de estos tickers (verificado: la fila de `senales_ticker` fecha=2026-08-06 para estos 7 tickers tiene `exchange` y `sesion_objetivo` NULL). Sin "fila fresca" del 08-06 que también apunte a 08-07, no hay con qué chocar — la fila queda sola y mal, invisible al método de pares. |
| **2026-07-05** | 2026-07-06 | **2026-07-03** | 8 (000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T, IFX.DE) | 2026-07-05T10:06:05 UTC, `origen='manual'` | Este es un caso más severo del mismo mecanismo, no uno nuevo: el snapshot del 07-05 fue un sello **manual**, con `available_at` calculado sobre un SOX de 2026-07-02 (jueves) — es decir, sellado casi 3 días después de que la información fuera conocible, saltándose un feriado de XNYS (viernes 03-jul) y un fin de semana. Con el reloj de pared (domingo 05-jul, 10:06 UTC) ya pasadas las aperturas de KRX/TWSE/TSE del 03-jul y del propio domingo inexistente, el salto no es de una sesión sino de tres: cae en 07-06 en vez de 07-03. Nunca chocó con otra fila porque nadie más apuntó a 07-06 esos días. |

**Total confirmado por auditoría exhaustiva contra `senales.db`
(mode=ro), sobre las 279 filas con predicción sellada:**

- **25 filas con `sesion_objetivo` objetivamente mal calculado** (10 del
  lado viejo de pares ya documentados + 15 nuevas, sin pareja).
- Las 25 están `estado='verificada'`, `modelo_version='4.6.0'` — es decir,
  **las 25 ya contribuyen su `gap_pct`/`retorno_real_pct` a las métricas
  selladas de hoy**, evaluadas contra el cierre de la sesión que el
  código eligió, no la que `available_at` implica.
- No es una proporción ni un estimador muestral — es un censo exhaustivo
  sobre las 279 filas que tienen algo que auditar (las 640 filas restantes
  de `senales_ticker` no tienen `sesion_objetivo`, no aplican). No lleva
  intervalo porque no hay incertidumbre muestral: es la cuenta completa a
  esta fecha, y crecerá si hay más sellos tardíos antes de aplicar el
  parche.

**Un hallazgo aparte, sobre el caso del 07-05, que importa para el
diseño del parche mismo, no solo para el conteo:** si el parche hubiera
estado activo ese día, la fórmula correcta (`available_at` = cierre
XNYS del 02-jul) habría dado sesión objetivo 2026-07-03 — pero para
cuando el proceso manual corrió (2026-07-05T10:06 UTC), **la apertura de
esa sesión (2026-07-03T00:00 UTC) ya había pasado**. La regla maestra del
verificador (`CLAUDE.md`: solo se evalúan predicciones cuyo
`timestamp_utc` precede la apertura UTC de su sesión objetivo) las habría
tomado entonces como `no_verificable_timing`, no como `verificada`. Esto
no es un defecto del parche: es la regla maestra funcionando exactamente
como está diseñada una vez que el ancla es la correcta. Hoy, en cambio,
esas 8 filas están mal-verificadas como si hubieran predicho una sesión
tres días más adelante de la que en realidad describían — el parche no
solo corrige el destino, corrige también, como efecto correcto de
construcción, la elegibilidad de verificación en los casos extremos.

> **Corrección 1-sep-2026 — no son 8, son 15, y el párrafo de arriba se
> quedó corto.** El forense de las huérfanas
> (`GEMELO/resultados/huerfanas.md` §3.1) recalculó el grupo del **2026-08-05**
> y encontró el mismo desenlace: con `available_at` corregido la sesión
> correcta es **2026-08-06**, que **ya había abierto** cuando el proceso
> terminó de sellar (01:38 UTC del 06-ago, tras que el Mac se re-durmiera
> durante los reintentos). Esas **7 filas también caerían en
> `no_verificable_timing`**.
>
> La diferencia entre los dos grupos es de **severidad, no de resultado**:
> agosto queda a mitad de la sesión correcta, julio con la sesión ya cerrada
> por completo. **En el eje de elegibilidad los dos grupos dan lo mismo.**
> Vale decirlo con todas las letras porque cambia el costo del parche: no son
> 8 filas las que salen de las métricas selladas, son **15**.
>
> Y de ahí sale el **riesgo simétrico** que este documento tiene que llevar
> escrito: una corrección que toque `sesion_objetivo` **sin tocar `estado`**
> dejaría 15 filas "corregidas" pero **todavía contando como `verificada`**,
> cuando bajo la regla maestra las 15 dejan de serlo. Las dos cosas se mueven
> juntas o no se mueven.

**Lo que la auditoría NO pudo determinar:** por qué el snapshot del
2026-08-06 perdió el 100% de sus predicciones ese día (dropout total, no
parcial) es una anomalía de datos aparte, no investigada aquí porque cae
fuera del alcance de este parche — queda anotada para quien mire salud de
datos de esa fecha, igual que el dropout del 17-ago que `dedup_opciones.md`
ya había dejado anotado sin investigar.

> **Corrección 1-sep-2026 — el 06-ago no era una incógnita, y este párrafo
> es la cuarta vez que el proyecto lo trató como si lo fuera.** Estaba
> reconstruido y documentado en `DECISIONES.md` (acta de la Etapa 5.0.2)
> **desde el 8-ago**, 23 días antes: el proceso arrancó tarde (18:24:48
> Chile), descargó 28/28 en 4 s, estampó `ts_emision` — y el Mac se
> **re-durmió, dejando el proceso congelado ~44 minutos** con el timestamp ya
> escrito. Al despertar (~19:08) el TTL de 15 min de la caché había expirado
> y la re-descarga en red inestable falló para 12 tickers más `^KS11` y
> `^SOX`; sin `^SOX`, `prediccion_apertura_al` devuelve vacío → **0
> predicciones**. `regimen` y `roca_chip` sí quedaron bien porque se
> calcularon **antes** del congelamiento.
>
> Lo que sigue sin determinarse es sólo la **atribución fina Yahoo-real vs.
> red-dormida** para esos 12 tickers: los logs primarios ya rotaron y no
> están en git (verificadas las dos cosas).
>
> **Y el hallazgo de proceso vale por sí solo.** `cola_decisiones.md`,
> `bifurcaciones.md`, `espera_firma.md` y este documento —cuatro— marcaron el
> 06-ago como cabo suelto no investigado. La respuesta llevaba tres semanas
> escrita en `DECISIONES.md`. **La memoria institucional existía y la capa
> que la necesitaba no la leyó.**

---

## 5. Declaración del corte de método (a fijar ANTES de aplicar)

**Corregir `snapshot.py:140` cambia el significado de la columna
`sesion_objetivo` a partir de un instante preciso. Las filas ya selladas
no se reescriben nunca (Constitución 5.0, punto 3) — así que este corte
existe por construcción, se declara ahora, con fecha, y no se descubre
después leyendo un salto raro en los datos.**

- **Qué significaba `sesion_objetivo` ANTES de este parche (todo el
  historial hasta la fila sellada inmediatamente antes de aplicarlo):**
  "la primera sesión de ese exchange cuya apertura es posterior al
  instante de reloj de pared en que el proceso de sellado llegó a la
  línea 140" — que coincide con "la sesión que la información conocible
  anticipaba" únicamente cuando el sello no cruza la apertura de un
  mercado asiático/europeo entre el cierre del SOX usado y el momento
  real de sellado. Cuando cruza, el campo miente por construcción sobre
  cuál era la sesión objetivo real de la predicción — y **puede llegar a
  reflejar una sesión que ya cerró** en vez de una sesión futura (caso
  4.2, 07-05).

- **Qué significa `sesion_objetivo` DESPUÉS de este parche:** "la primera
  sesión de ese exchange cuya apertura es posterior a `available_at` —
  el cierre UTC de la sesión del SOX cuyo movimiento alimenta la
  predicción". Esto es invariante al reloj de pared: sella lo mismo sin
  importar si el proceso corre a tiempo o con horas de atraso. Es también
  la definición que la regla maestra de `CLAUDE.md` ya asume que
  `sesion_objetivo` tiene — el parche no introduce un concepto nuevo,
  alinea el código con la definición que el resto del sistema ya daba por
  cierta.

- **Desde cuándo:** desde la primera fila sellada con el `snapshot.py`
  parcheado en producción — es decir, el primer sello de la ventana
  17:50–20:30 Chile posterior al momento en que Nicolás aplique este
  diff. **Marcador estructural recomendado, ya presente en el esquema:**
  cada fila de `snapshots` sella `plataforma_version`
  (`version.PLATAFORMA_VERSION`, hoy congelada en `5.0.3`). Si al aplicar
  este parche Nicolás también decide bumpear `PLATAFORMA_VERSION` (una
  decisión suya, manual, fuera de mi alcance — no toqué `version.py`), el
  corte queda auto-documentado para siempre en cada fila:
  `plataforma_version < <nueva>` ⇒ semántica vieja de `sesion_objetivo`,
  `>= <nueva>` ⇒ semántica nueva. Si NO bumpea la versión, el corte igual
  existe pero hay que anclarlo a mano con el `timestamp_utc` exacto del
  primer sello posterior al deploy (anotarlo en el momento, no
  reconstruirlo después de memoria — la cita de un acta se desplaza, un
  timestamp sellado no).

- **Cómo debe tratar cualquier análisis futuro las filas de cada lado:**
  ningún análisis (backtest, `linea_base.py`, métricas de `/historial`,
  cola de decisiones) debe mezclar `sesion_objetivo` de antes y de
  después del corte como si fueran la misma medida sin más — exactamente
  la misma disciplina que el proyecto ya aplica entre
  `modelo_version`s distintos ("Metrics never mix modelo_versions").
  Concretamente: (a) cualquier reconteo de duplicados o de filas afectadas
  hecho DESPUÉS del corte que incluya filas de ANTES debe seguir aplicando
  esta misma auditoría (el `available_at` sigue estando sellado en las
  filas viejas, así que siempre se puede recalcular cuál "debería" haber
  sido la sesión — pero la columna sellada real seguirá siendo la vieja,
  errónea, y eso se declara, no se corrige en el dato); (b) un cambio de
  `sesion_objetivo` entre dos filas que rodean el corte por la razón
  correcta (la fórmula cambió) no debe leerse como una anomalía de datos
  nueva — es exactamente el corte declarado aquí operando.

Esta declaración va, en su forma final, a `DECISIONES.md` — no la escribí
ahí yo mismo porque sellar la decisión de aplicar el parche (y, con ella,
la fecha real del corte) es exactamente el acto que este documento evita
adelantar. El texto de arriba está listo para pegarse tal cual cuando
Nicolás aplique el parche y sepa la fecha/hora real y si bumpeó la
versión.

---

## 6. Qué NO arregla el parche

**Las 25 filas ya selladas con `sesion_objetivo` equivocado (10 del lado
viejo de los pares documentados + 15 sin pareja, §4) siguen ahí, sin
tocar, para siempre.** El parche solo cambia el código que sella FILAS
NUEVAS a partir de que se aplique. No hay backfill, no hay UPDATE, no hay
excepción — coincide con la Constitución 5.0 punto 3 (las filas selladas
nunca se reescriben; los errores históricos se documentan como erratas).

**Cómo quedan tratadas bajo la regla de deduplicación ya firmada** ("la
fila válida es la de sesión objetivo correcta según `available_at`, nunca
la más fresca por sí sola"):

- **Los 10 pares documentados en `dedup_opciones.md` (07-31 y 08-05):** la
  regla firmada ya los resuelve sin necesidad de nada adicional, porque
  coincide exactamente con lo que mi auditoría de §4.1 mide: en cada uno
  de los 10 pares, la fila "fresca" YA es la que tiene `sesion_objetivo`
  correcto según su propio `available_at` (no fue tocada por el defecto);
  la fila "vieja" es la que no. La regla firmada, aplicada literalmente,
  descarta la vieja y conserva la fresca en los 10 — que es la misma
  conclusión a la que `dedup_opciones.md` llegó por otro camino
  (comparación contra la baseline), ahora con una segunda vara
  independiente que coincide.
- **Los 5 pares de feriado real (12-ago, 18-ago) NO son este defecto** —
  ninguna de las dos filas de esos pares tiene `sesion_objetivo`
  incorrecto según `available_at` (verificado: no aparecen en absoluto en
  la lista de 25 de §4). La regla firmada, tal como está escrita, no
  tiene nada que arbitrar ahí — quedan fuera de este parche por completo,
  como ya había recomendado el forense de origen.
- **Las 15 filas sin pareja de §4.2 son el caso que la regla firmada, tal
  como está redactada, NO cubre todavía.** La regla se escribió para
  decidir entre DOS filas que compiten por el mismo `(ticker,
  sesión_objetivo)` — estas 15 no compiten con nada, están solas y
  mal. Aplicar el ESPÍRITU de la regla (preferir la sesión que
  `available_at` implica) a una fila sin pareja significaría marcarla
  como lo que en los hechos ya es: una predicción cuyo `sesion_objetivo`
  sellado no es el que su propio `available_at` sostiene. Pero eso es una
  extensión de la regla, no la regla misma — **queda explícitamente sin
  decidir aquí, para que Nicolás la resuelva con el mismo criterio que
  usó para las otras 10, no por omisión.** Mientras no se decida, esas 15
  filas siguen contando en las métricas selladas de hoy exactamente como
  si su `sesion_objetivo` fuera correcto. Dicho eso, no las 15 quedarían
  igual si se re-evaluaran con el `sesion_objetivo` correcto: las 8 del
  grupo 07-05 (no las 7 del grupo 08-05) dejarían de ser `verificada` y
  pasarían a `no_verificable_timing` bajo la regla maestra, porque su
  `available_at` es tan viejo que la sesión correcta (07-03) ya había
  cerrado antes de que el proceso sellara (07-05T10:06 UTC) — ver el
  hallazgo del caso 07-05 en §4.2. Hoy, sin embargo, las 25 están
  contadas como `verificada`, sin distinción.
