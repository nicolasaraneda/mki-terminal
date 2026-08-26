# Modo sombra — operación y checklist de switch

**Etapa 5.0.3 · Fase 3 de la reactivación.** Este documento es el
procedimiento de la ventana de sombra y la lista de lo que tiene que estar
resuelto antes de que el PC pase a titular. Manda `CLAUDE.md`; la memoria
de por qué cada cosa es así está en `DECISIONES.md`.

---

## Qué es

Durante la ventana hay **dos máquinas corriendo el mismo código sobre la
misma historia**. El Mac es **titular**: sella, manda el reporte de
Telegram y commitea los respaldos. El PC corre en **sombra**: sella igual
—ese sello es el objeto mismo de la comparación— pero no emite nada.

```
MKI_MODO=sombra   → máquina sombra
MKI_MODO ausente  → titular
```

| | Titular (Mac) | Sombra (PC) |
|---|---|---|
| Sella en `senales.db` | sí | **sí** — si no, no hay nada que comparar |
| Telegram | sale a la red | interceptado a `data/sombra_telegram.log` |
| `mki_backup.py` | commitea | no commitea, ni toca el índice de git |
| Vigía: "backup sin commit" | falla real | correcto, no alerta |

Un `MKI_MODO` puesto pero ilegible (`sombrra`) **cae a sombra**, nunca a
titular: el error caro es el otro. `./mki estado` muestra el modo activo
como primera línea — durante la ventana, leer el estado sin saber en qué
modo está la máquina es leerlo mal.

---

## Las dos trampas epistemológicas

Están en el acta de migración y siguen vigentes. El comparador las hace
cumplir por código, pero conviene tenerlas presentes al leer un resultado.

**1. La paridad en fechas anteriores al corte no prueba nada.** Las bases
del PC son copia por pendrive de las del Mac hasta el **2026-08-24
inclusive**. Para esas fechas las dos máquinas no tienen datos parecidos:
tienen **literalmente el mismo archivo**. Compararlas es comparar un
archivo consigo mismo. `comparar_sombra.py` se **niega** a evaluarlas y lo
dice — nunca las ignora en silencio.

**2. Un día sin sello del titular no cuenta.** Si el Mac no selló esa
noche, "nada = nada" daría paridad trivial. Ese día es **perdido**, no
bueno. Por eso hay tres veredictos y no dos:

| Veredicto | Cuándo | Cuenta | ¿Final? |
|---|---|---|---|
| `PARIDAD` | ambos sellaron y coinciden niveles 1 y 2 | **+1** | sí |
| `DIVERGENCIA` | ambos sellaron y difieren — **o** el titular selló y la sombra no | **racha a cero** | sí |
| `DIA_NO_COMPUTABLE` | fecha ≤ corte · huella de base copiada · el titular no selló (ausencia **definitiva**) | no suma ni rompe | sí |
| `PENDIENTE_PUBLICACION` | no hay fila del titular y tampoco sellos suyos posteriores: no se sabe si no selló o si aún no pusheó | no suma ni rompe | **NO** |

Que la sombra no selle habiendo sellado el titular es **DIVERGENCIA**, no
día perdido: es la sombra fallando, que es justo lo que la ventana existe
para detectar.

**`PENDIENTE_PUBLICACION` es el que hay que entender bien.** El comparador
lee del titular por `origin/main`, y el push del Mac es manual y va después
de las 20:30: la ausencia de fila ahí es **ambigua**. Marcar ese día como
perdido lo quemaría en silencio por un push que todavía no llegó — un
tercio de la ventana perdido por sincronización. Así que queda **sin
cerrar** y se resuelve **volviendo a correr esa fecha** cuando llegue el
push. El contador los lista aparte con el comando exacto.

Se desambigua sin mirar el reloj: **si el titular ya publicó sellos de una
fecha posterior**, su historia está publicada más allá de este día y la
ausencia pasa a ser definitiva → `DIA_NO_COMPUTABLE`. Por eso un feriado no
queda "pendiente" para siempre.

---

## Rutina de las tres noches

Código **congelado en ambas máquinas** durante toda la ventana. Un cambio
a mitad de camino invalida los días ya acumulados.

**Cada noche:**

1. **Mac enchufado con `caffeinate -dimsu` entre 17:45 y 20:30.** Las
   **tres** noches, no solo la primera — el sueño del Mac ya congeló el
   bucle de reintentos antes (sellos de 21:23 y 19:40 en la auditoría de
   julio).
2. Dejar que corran los 6 jobs en las dos máquinas.
3. **Push manual del Mac después de las 20:30.** El comparador lee de
   `origin/main`: sin push no hay nada que leer, y el día sale
   `DIA_NO_COMPUTABLE` por "el titular no selló" aunque haya sellado.
4. En el PC, al día siguiente:

```bash
source venv/bin/activate
python comparar_sombra.py                 # compara HOY
python comparar_sombra.py --fecha 2026-08-27
python comparar_sombra.py --contador      # progreso de la ventana
```

El reporte queda en `data/sombra/comparacion_<fecha>.md` y el veredicto se
acumula en `data/sombra/veredictos.jsonl`. El reporte declara el criterio
completo, la revisión de `origin/main` usada y la procedencia de los dos
lados: se puede releer en tres semanas y entender qué se comparó.

**Antes de arrancar la ventana:** volver a copiar `senales.db` y
`noticias.db` del Mac — la copia actual llega al 24-ago y el Mac sigue
sellando. **Si se recopian, sube la `FECHA_CORTE` de `comparar_sombra.py`
al nuevo día de copia.** Es una constante declarada arriba del archivo con
su justificación.

Y si se te olvida, el comparador lo atrapa igual: además de la constante
hay un **chequeo estructural** que no depende de la memoria de nadie. Dos
filas selladas independientemente **jamás comparten `creado_en` ni
`timestamp_utc`** — son marcas de microsegundos tomadas por procesos
distintos. Si la fila local y la de `origin/main` coinciden en `creado_en`,
`timestamp_utc` **y** `plataforma_version`, eso no es paridad: es la misma
fila copiada, y el comparador se niega **aunque la fecha sea posterior al
corte**, diciéndote que subas la constante.

Cinturón y tirantes: los dos mecanismos son independientes y basta que se
dispare **uno**.

---

## Cómo lee el comparador (pendiente #3 del acta)

`git fetch` y después `git show origin/main:data/backups/<archivo>.csv`.
**Nunca `git pull`:** el árbol de trabajo es el código que los timers
ejecutan esa misma noche, y un merge lo alteraría bajo los pies. El lado
local sale de `senales.db` abierta en `mode=ro`. Nada de lo que hace el
comparador escribe en el árbol ni en el índice. Hay un test que falla si
la cadena `pull` reaparece en el archivo.

### Los tres niveles de tolerancia

Declarados **antes** de correr, en `comparar_sombra.py`. La intuición
ingenua —"son floats, pon tolerancia amplia"— es exactamente el error: las
dos máquinas corren pandas 3.0.3 y numpy 2.4.6 idénticos sobre la misma
ventana de 120 sesiones. Con los mismos insumos, los números deben salir
iguales. Una tolerancia amplia escondería justo lo que buscamos.

- **Nivel 1 — identidad numérica** (tolerancia relativa `1e-9`):
  `apertura_estimada_pct`, `confianza_r2` (el R²), `beta`,
  `intervalo80_pp`, `puntaje_v0`, `sox_usado_pct`. Una diferencia mayor
  **no es ruido**: es evidencia de que los insumos difieren, y se reporta
  como **hallazgo**.
- **Nivel 2 — igualdad exacta**: `fecha`, `sesion_objetivo`,
  `available_at`, `modelo_version`, `feature_version`, `universo_version`,
  `regimen`, `roca_chip`, `exchange`, `n_muestra`, `ventana_betas`,
  `sox_fecha`, `descarga_ok`/`descarga_total`/`descarga_caidos`, el
  conjunto de tickers sellados, el número de predicciones y las filas
  selladas.
- **Nivel 3 — diferencia legítima esperada**, fuera del veredicto:
  `plataforma_version` (el Mac sella 5.0.2 y el PC 5.0.3 — registrado en
  `DECISIONES.md` Etapa 5.0.3 §8), `timestamp_utc`, `creado_en`, `origen`,
  `estado` y todo lo dependiente de noticias (`sentimiento_ia`,
  `puntaje_ia`).

Los extremos del intervalo del 80% son `apertura_estimada_pct ±
intervalo80_pp`; ambos están en el nivel 1, así que compararlos es
comparar los extremos.

---

## ⚠ PREGUNTA ABIERTA — decisión de Nicolás, ANTES del switch

**No la responde Claude. Tiene que quedar resuelta y escrita aquí antes de
que el PC pase a titular. Si no, el track record se corrompe en silencio.**

Durante la ventana **las dos máquinas sellan las MISMAS fechas**. Cuando
el PC pase a titular, su base va a tener la historia copiada del Mac **más
sus propios sellos de sombra** para los días de solapamiento; y el Mac va
a tener los suyos para esas mismas fechas.

**¿Cuáles son canónicos?**

La regla dice que **las filas selladas jamás se reescriben**, así que no se
puede sobreescribir una con la otra. Y de ahí sale la pregunta incómoda:

**¿Borrar cuenta como reescribir?**

Notas para la decisión, sin tomarla:

- Si los días de solapamiento dieron `PARIDAD`, las dos filas dicen lo
  mismo en todo lo que el veredicto cubre — pero **no son idénticas**:
  difieren en `plataforma_version`, `timestamp_utc` y `creado_en`, que es
  precisamente lo que el nivel 3 declara legítimo.
- Cualquier salida elegida (quedarse con las del Mac, quedarse con las del
  PC, conservar ambas con una marca de procedencia, o declarar el
  solapamiento fuera de métricas como ya se hace con
  `no_verificable_timing` y `legacy_pre_4.6`) tiene que quedar **escrita
  con su porqué en `DECISIONES.md`** antes de ejecutarse.
- El proyecto ya tiene precedente para la cuarta salida: estados
  terminales que se conservan, son visibles en auditoría y quedan **fuera
  de TODAS las métricas**. No es una recomendación — es el precedente que
  existe.

**Estado: SIN RESOLVER.**

---

## Checklist de switch

Todo esto en verde antes de que el PC pase a titular:

- [ ] Tres días hábiles con `PARIDAD` (`--contador` lo dice), con el
      titular sellando de verdad esas tres noches.
- [ ] Código congelado durante toda la ventana en ambas máquinas.
- [ ] La pregunta abierta de arriba, **resuelta y escrita** en
      `DECISIONES.md`.
- [ ] `data/sombra_telegram.log` revisado: lo que el PC habría mandado es
      lo que el Mac efectivamente mandó.
- [ ] GATE 1 en verde en el PC.
- [ ] Timers instalados y probados en el PC (Fase 4, GATE A-bis: reiniciar,
      **no** iniciar sesión, esperar 3 min en la pantalla de bloqueo).
- [ ] Al hacer el switch: **apagar los timers del Mac primero**, y recién
      entonces quitar `MKI_MODO=sombra` del PC. Nunca al revés — el hueco
      es preferible al día con dos titulares.
- [ ] Retirar la guarda de confirmación de `./mki instalar` según la
      condición escrita en `DECISIONES.md` Etapa 5.0.3 §6.
