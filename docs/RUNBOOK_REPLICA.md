# Runbook de activación de la réplica

**Qué es este documento.** El procedimiento operativo, paso a paso, para
el día que Nicolás decida activar una réplica permanente. `docs/REPLICA.md`
es el diseño y la evaluación (qué significa divergir, quién gana, qué se
registra, qué requiere firma); este archivo es la ejecución de esa
decisión ya tomada — mismo criterio que separa `docs/SOMBRA.md`
(procedimiento del switch) de las secciones de diseño de `CLAUDE.md` y
`DECISIONES.md`.

**Nadie corre este runbook sin haber cerrado primero la sección 0.** Un
runbook que empieza a ejecutar pasos con decisiones de diseño todavía
abiertas es exactamente el tipo de cosa que `docs/REPLICA.md` §5 existe
para impedir.

---

## 0. Decisiones que tienen que estar tomadas ANTES de empezar

Sin estas cuatro decisiones, escritas y fechadas en `DECISIONES.md`, este
runbook no arranca — no hay paso 1:

1. **Que se activa una réplica permanente, en absoluto, y con qué
   máquina.** (`docs/REPLICA.md` §5, primer punto.) Hoy el candidato
   natural es el Mac (quedó fuera de servicio como emisor tras el switch,
   `Python 3.11.15`, `launchd`), pero es una decisión explícita, no una
   inferencia de este runbook.
2. **La regla de "quién gana" ante una discrepancia** (`docs/REPLICA.md`
   §2). La propuesta razonada del documento es "la titular gana siempre,
   sin excepción" — pero sigue siendo propuesta hasta que Nicolás la
   adopte o la reemplace. Este runbook asume que la regla adoptada,
   cualquiera sea, ya está escrita en `DECISIONES.md` antes del paso 1.
3. **Qué máquina queda designada titular de sellado** (ya resuelto hoy:
   este PC — pero repetirlo en el acta de activación de la réplica evita
   que quede implícito). `modo.py` sigue siendo la única fuente de verdad;
   este runbook no la reemplaza ni la deduce.
4. **La política de retención** de `data/sombra/` (o el directorio
   equivalente que use la réplica permanente) y de la tabla
   `divergencias_replica` (`docs/REPLICA.md` §4, último punto): cuánto se
   guarda, si se resume, con qué cadencia. Sin esto, el paso 6 de este
   runbook no tiene qué instalar.

Decisión aparte, **no bloqueante** para activar pero sí para el
comportamiento del día 1: si se retira `FECHA_CORTE` como comportamiento
por defecto de `comparar_sombra.comparar_fecha()` (`docs/REPLICA.md` §4).
Si no se decide, el runbook usa el comportamiento por defecto que ya
existe (`fecha_corte=FECHA_CORTE`), lo cual es seguro pero puede rechazar
como `DIA_NO_COMPUTABLE` fechas tempranas que en rigor ya no son copia de
nadie — un costo de oportunidad, no un error.

---

## 1. Verificar que las dos máquinas parten del mismo código

**Qué se hace:** confirmar que la máquina designada réplica va a correr
exactamente el mismo commit que la titular antes de instalar nada.

```bash
# en la máquina titular (este PC)
git rev-parse HEAD

# en la máquina candidata a réplica
git fetch origin --quiet
git rev-parse origin/main
git status --porcelain   # debe salir vacío
```

**Cómo se verifica que salió bien:** los dos `rev-parse` devuelven el
mismo SHA, y `git status` en la réplica no muestra cambios locales sin
commitear. Si la réplica tiene una rama distinta o commits propios sin
mergear, se resuelve ANTES de seguir — nunca con `git pull` sobre un árbol
con timers instalados (regla dura del proyecto).

**Vuelta atrás:** ningún cambio hecho todavía. Si los SHA no coinciden,
no se avanza al paso 2.

---

## 2. Poner la máquina réplica en modo sombra

**Qué se hace:** en la máquina designada réplica (nunca en la titular),
agregar la línea que ya usa el mecanismo existente:

```bash
# en el .env de la máquina RÉPLICA únicamente
echo "MKI_MODO=sombra" >> .env
```

**Cómo se verifica que salió bien:**

```bash
source venv/bin/activate && python -c "import modo; print(modo.modo_actual())"
# debe imprimir: sombra
```

y en la máquina TITULAR, el mismo comando debe seguir imprimiendo
`titular` — confirmar esto explícitamente, en la propia máquina titular,
antes de seguir. Un valor puesto pero ilegible cae a sombra, nunca a
titular (falla seguro asimétrica, ver skill `modo-emision`) — así que un
typo en esta línea no puede convertir por accidente a la réplica en una
segunda emisora.

**Vuelta atrás:** borrar la línea `MKI_MODO=sombra` del `.env` de la
réplica (o comentarla). Sin esa línea la máquina vuelve a comportarse como
titular — por eso el paso 3 (instalar timers) NUNCA se hace antes de
confirmar el modo, y por eso este paso es completamente reversible por sí
solo, sin dejar nada a medias: si se aborta acá, la réplica simplemente no
tiene timers todavía y no sella nada.

**Qué NO hace este paso:** no toca `.env` ni `MKI_MODO` en la máquina
titular, bajo ninguna circunstancia.

---

## 3. Instalar los seis timers en la máquina réplica

**Qué se hace:** el instalador que ya existe, sin modificarlo:

```bash
./mki instalar
```

(`launchd/instalar.sh` en macOS, `systemd/instalar.sh` en Linux — `./mki
instalar` elige por `uname -s`.)

**Cómo se verifica que salió bien:**

```bash
./mki estado
```

primera línea debe decir modo `sombra`; y los seis jobs deben aparecer
programados (`systemctl --user list-timers` en Linux, `launchctl list |
grep mki` en macOS) con los horarios de siempre (noticias 17:50, snapshot
18:15, reporte 18:25, backup 18:40, vigía 19:00, vigía-rechequeo 20:30,
hora de Chile).

**Vuelta atrás:** desinstalar los timers de la réplica (el proyecto ya
tiene el camino simétrico de desinstalación de la fase de migración;
`systemctl --user disable --now <unidad>` por cada una, o el equivalente
`launchctl unload`, si no hay script de desinstalación dedicado) y volver
al paso 2 para revertir el modo. Si se aborta a mitad de este paso (por
ejemplo con tres timers instalados y tres no), la réplica queda en un
estado inconsistente pero SEGURO: en modo sombra sigue sin poder emitir
nada real aunque algún timer dispare, así que el peor caso es "sella
parcialmente, no reporta" — nunca "emite por error".

---

## 4. Confirmar en frío que la réplica sella sin emitir

**Qué se hace:** repetir, en la máquina réplica, el mismo tipo de prueba
que ya aprobó el GATE A-bis en la migración anterior — reinicio en frío,
sin sesión abierta, y comprobar que el snapshot sella y que NINGÚN mensaje
sale por Telegram.

**Cómo se verifica que salió bien:**

```bash
# después de que corra el snapshot de esa noche
grep <fecha-de-hoy> data/sombra_telegram.log   # el mensaje quedó ACÁ
# y NO llegó al Telegram real (confirmar a ojo en la app, una vez)
python -c "import senales; print(senales.historial_snapshots().tail(1))"
```

el snapshot de esa fecha existe y está sellado, y `sombra_telegram.log`
tiene la entrada del reporte que en la titular sí habría salido a la red.

**Vuelta atrás:** si algo emitió de verdad (falla de la asimetría del
modo, lo más grave posible en este runbook), el primer paso es volver el
`.env` de la réplica al estado del paso 2 (revertir `MKI_MODO=sombra` NO
alcanza si ya emitió — hay que además dar de baja los timers, paso 3, de
inmediato) y documentar el incidente en `DECISIONES.md` antes de
reintentar nada. No se reintenta el mismo día.

---

## 5. Primer día de comparación real

**Qué se hace:** una vez que la réplica selló al menos un día completo,
correr el comparador tal como existe hoy (sin automatizar todavía):

```bash
python comparar_sombra.py --fecha <la-fecha-de-ayer>
```

Si la decisión de la sección 0 fue retirar `FECHA_CORTE` como
comportamiento permanente, este es el primer día en que ese cambio de
código (agregar `fecha_corte=None` en el llamador, o cambiar el default —
ver `docs/REPLICA.md` §4) ya tiene que estar hecho y su propio test verde;
si no se decidió, se usa el comportamiento actual sin tocar nada.

**Cómo se verifica que salió bien:** el veredicto impreso es uno de los
cuatro conocidos (`PARIDAD`, `DIVERGENCIA`, `DIA_NO_COMPUTABLE`,
`PENDIENTE_PUBLICACION`) y el reporte quedó en `data/sombra/` (o el
directorio que la política de retención de la sección 0 haya definido
para el uso permanente).

Después, registrar el resultado con la pieza de este mismo frente:

```python
import comparar_sombra as cs, replica
res = cs.comparar_fecha("<la-fecha>", snaps_titular, tickers_titular)
replica.registrar_comparacion(res)   # usa data/divergencias_replica.db real
```

(`snaps_titular`/`tickers_titular` salen de `cs.leer_csv_titular(...)`
tras `cs.fetch_titular()`, igual que en `cs.main()`.)

**Cómo se verifica que salió bien:** si el veredicto fue `DIVERGENCIA`,
`leer_divergencias()` muestra al menos una fila nueva con `resuelto_como
IS NULL`; si fue cualquier otro veredicto, cero filas nuevas — exactamente
lo que `scripts/ensayo_replica.py` ya demostró contra datos sintéticos
(`docs/REPLICA.md` §6).

**Vuelta atrás:** este paso es de solo lectura sobre el titular (`git
fetch`, nunca `pull`) y solo INSERT sobre `data/divergencias_replica.db`.
No hay nada que revertir: si el resultado no convence, se puede volver a
correr el mismo día las veces que haga falta sin efecto acumulativo
distinto (cada corrida es una comparación nueva; `registrar_comparacion`
sí acumula filas de auditoría en cada llamada — si eso no es deseable,
NO se llama a `registrar_comparacion` hasta estar conforme con el
veredicto de `comparar_fecha`, que no escribe nada por sí solo).

---

## 6. Automatizar la comparación diaria (pendiente de construir)

**Qué falta, con honestidad:** hoy no existe un timer ni un cron que
invoque el paso 5 automáticamente. `comparar_sombra.py` se pensó para la
ventana de switch (corrida manual o por script de auditoría), y
`replica.py` "no corre sola: nadie la invoca todavía" (comentario propio
del módulo). Activar una réplica PERMANENTE sin automatizar este paso
significa que alguien tiene que acordarse de correrlo todos los días — la
misma clase de punto débil que `docs/REPLICA.md` §4 ya señaló para
`FECHA_CORTE`.

**Qué se hace, si se decide construir el cableado:** un séptimo job
(nombre propuesto: `mki-comparar-replica`, mismo patrón que los seis
existentes — `OnCalendar=Mon..Fri`, después de que ambas máquinas hayan
sellado y de que el push manual de la titular sea razonablemente probable,
p. ej. 21:00 hora de Chile) que corra el paso 5 sin intervención. Esto es
código nuevo que no existe hoy — este runbook NO lo construye ni lo
instala; deja constancia de que hace falta y de dónde encajaría.

**Mientras tanto:** el paso 5 se corre a mano, con la cadencia que
Nicolás decida, y el vacío entre corridas queda documentado como deuda en
`DECISIONES.md` (mismo tratamiento que la deuda de `N_intentos`
desactualizado en `GEMELO/relevo_asiatico.py`, §45).

---

## 7. Instalar la política de retención

**Qué se hace:** una vez definida en la sección 0, implementarla — por
ejemplo, un job de limpieza/resumen sobre `data/sombra/*.md` y sobre
`divergencias_replica.db` con la cadencia decidida. **No implementado por
este runbook**: es código nuevo, condicionado a una decisión que hoy no
existe.

**Cómo se verificaría que salió bien:** el tamaño de `data/sombra/` (o su
sucesor) y el conteo de filas de `divergencias_replica` dejan de crecer
sin límite; auditable con `du -sh data/sombra` y
`len(replica.leer_divergencias())` antes/después de cada ciclo de
retención.

---

## 8. Cerrar el acta

**Qué se hace:** documentar la activación completa en `DECISIONES.md` —
qué máquina, con qué commit, qué regla de "quién gana" quedó adoptada
(sección 0), y el resultado del primer día real de comparación (paso 5).

**Cómo se verifica que salió bien:** `guardian-constitucion` sobre el
acta antes de cerrarla, igual que cualquier otra tanda.

---

## Qué NO hace este runbook, en ningún paso

- No toca `MKI_MODO` en la máquina titular — ni para ponerlo ni para
  quitarlo. La titular no tiene esa variable hoy y este runbook no se la
  agrega.
- No borra nada: ni `data/sombra/`, ni `divergencias_replica.db`, ni
  commits, ni timers de la titular.
- No decide "quién gana" en ningún caso concreto — `resuelto_como` queda
  en NULL siempre, en cualquier fila que este runbook produzca, sea cual
  sea la regla adoptada en la sección 0 (la regla se aplica en el reporte
  y en la operación, no reescribiendo la auditoría).
- No hace `git pull` en ningún paso, en ninguna máquina con timers
  instalados — solo `git fetch` y lectura vía `git show`.
- No hace commit ni push por sí solo en ningún paso — cada `git`
  mencionado acá es de lectura (`fetch`, `rev-parse`, `show`, `status`).
- No construye el séptimo timer de comparación automática (sección 6) ni
  la política de retención (sección 7) — dejar constancia de que faltan es
  parte del runbook; construirlos no lo es, salvo que se ejecuten esas
  secciones como su propia tanda de trabajo, con su propio
  `guardian-constitucion` al cerrar.
