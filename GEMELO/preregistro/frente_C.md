# Pre-registro · Frente C — la paradoja de la no capturabilidad como hipótesis

**Escrito 2-sep-2026 12:16, antes de mirar ningún dato de estas
preguntas.** Octava corrida. PROPUESTA hasta el dictamen. Retornos
crudos, sin motor: la «predicción» es el signo del último cierre de NY
anterior a la apertura local (como en B y D), no el modelo 4.6.0.

## El hecho a explicar

Acierto direccional alto del gap y cartera que pierde sin costos no son una
contradicción: son un dato sobre la distribución condicional. Tres
explicaciones, no excluyentes, con lo que cada una predice:

| hipótesis | qué dice | predicción refutable |
|---|---|---|
| **H1 estructural** | el gap es intradeable: la información llega después del cierre asiático y lo único ejecutable es la sesión posterior (abrir → cerrar). Lo que el backtest operó fue la sesión, no el gap. | Verificar en `backtest/cartera.py` qué se opera. Si es la sesión: el retorno de sesión condicionado al signo predicho tiene media ≤ 0 aunque el gap la tenga > 0. |
| **H2 asimetría de magnitud** | los aciertos son chicos y los errores grandes | descomponer el retorno de la cartera direccional en contribución de aciertos y de errores: media condicionada a acierto vs a error, con IC de día. Si \|E[r \| error]\| > E[r \| acierto] con IC que lo separe, H2 se sostiene. |
| **H3 sobrerreacción / deriva post-gap** | la sesión posterior revierte el gap (sobrerreacción) o lo continúa (deriva) según la sorpresa | regresión de la sesión (close/open − 1) sobre la sorpresa s = gap realizado − gap «implícito» (β_i·SOX con β del ajuste). **Signo pre-registrado:** sobrerreacción ⇒ pendiente < 0; deriva ⇒ pendiente > 0. IC por bootstrap de fechas. |

## Estadísticos

- Por fila: gap g = open/close_prev − 1; sesión r = close/open − 1;
  «capturable» c = (1+g)(1+r)/(1+g) − 1 = r (lo que se obtiene entrando
  en la apertura); predicción p = signo(SOX_prev). Cartera direccional:
  q = signo(p)·r (largo si p > 0, corto si p < 0), sin costos.
- H1: E[q] con IC de día; acierto de signo de g vs de r, ambos contra
  «siempre al alza».
- H2: E[q | acierto de g] y E[q | error de g], y la fracción del total que
  aporta cada grupo; IC de día.
- H3: pendiente OLS de r sobre s (y sobre s₂ = g − 0, la sorpresa «sin
  modelo»), IC de día; también por terciles de s.
- Todo sobre la ventana larga reconstruida (gaps v2 + cierres testigo del
  26-ago para los 8 tickers), `excluir_cero`.

## Efecto relevante y refutaciones

- H1 se sostiene si E[q] tiene IC que contiene 0 o es negativo mientras
  el acierto de g supera al de «siempre al alza» con IC que excluye 0.
- H2 es relevante si |E[q | error]| ≥ 1,5 × E[q | acierto] con IC que
  excluya la igualdad.
- H3: pendiente con IC que excluya 0; relevante si |pendiente| ≥ 0,1
  (una sorpresa de 1 pp mueve la sesión 0,1 pp).

## Partición de años

Ajuste 2018-09-01 → 2023-12-31; prueba 2024-01-01 → 2026-08-31 (con
embargo de 5 sesiones y sin las 37 fechas selladas). La prueba se abre
tras el ajuste y la auditoría.

## Intentos del DSR

Tres hipótesis con un estadístico cada una = **3 intentos**, declarados.

## Enmienda 1 (2-sep-2026, 14:15, después de la auditoría de fuga y ANTES de abrir la prueba)

El `auditor-lookahead` dictaminó sobre `no_capturabilidad.py` con el ajuste
abierto y la prueba cerrada. Lo que cambia, todo al ejecutable primero:

1. **Fuga demostrada, inmaterial, en el ajuste:** β se estimaba por OLS sobre
   todo el ajuste, así que la sorpresa s(t) del ajuste usa datos posteriores a
   t (Δ de la pendiente H3 = 0,0005 contra umbral 0,10; no llega a la prueba:
   β es invariante a truncar en cualquier fecha ≥ 2023-12-29). La H3 del
   ajuste se rotula **descriptiva, in-sample**; se agrega la pendiente con β
   de la primera mitad del ajuste, y para la prueba β queda congelada del
   ajuste (ya lo estaba).
2. **Fuga demostrada, hoy inocua:** las 7 filas del 2026-08-26 se construían
   sobre una barra INTRADÍA (el testigo de cierres se capturó a las 04:23 UTC
   con Asia en sesión). `cargar()` trunca en la última barra COMPLETA
   (`< 2026-08-26`).
3. **`SELLADA` se deriva de `sesion_objetivo`** del backup versionado (hoy
   2026-07-06 → 2026-09-02, 40 sesiones; la constante a mano decía 05-jul →
   31-ago) y **se embargan sus dos bordes** con 5 sesiones: la prueba termina
   5 sesiones antes de la primera sesión sellada (la misma barra del `^SOX`
   alimentaba la última fila de prueba y la primera sellada).
4. **Cortes de tercil de H3 congelados en el ajuste** y sellados en
   `parametros`; en la prueba no se recalculan.
5. **Una sola apertura:** `--abrir-prueba` escribe `no_capturabilidad.lock`
   con el sha256 del módulo y de este pre-registro; si el hash cambió, se
   niega a reabrir.
6. **Bootstrap de bloques circulares de 10 fechas** (`backtest/DISEÑO.md`
   §8.5) en vez de iid de fechas: |q| tiene AC 0,18–0,21 en rezagos 1–3
   (agrupamiento de volatilidad) y H2/H3 son funcionales de segundos
   momentos. Se reporta el conteo de réplicas no finitas.
7. **H2, el signo:** el criterio «|E[q|error]| ≥ 1,5 × E[q|acierto]» suponía
   E[q|acierto] > 0. En el ajuste los DOS son negativos (los aciertos pierden
   más que los errores). Se reportan los dos signos junto a la razón; la
   lectura de la razón contra 1,5 se declara **no aplicable** cuando
   E[q|acierto] ≤ 0. El criterio original no se toca.
8. **Por exchange:** Fráncfort no es contemporáneo de Asia (su ventana de gap
   sólo contiene la cola de la sesión de NY); H1 y H3 se publican también
   partidos por exchange.
9. **Intentos del DSR:** el pre-registro declaró 3 (una hipótesis, un
   estadístico); el módulo publica 14 intervalos. Se cuenta **por
   estadístico publicado: 14**, errando hacia arriba, como manda la casa.
10. **Test de invariancia a truncar** para `cargar()` en `tests/`, con
    contraprueba (`shift(-1)` en `sox_prev`), antes de abrir la prueba.

Zonas ciegas que la auditoría dejó declaradas y no se resuelven aquí: no
hay `Open` independiente en los testigos (la identidad (1+g)(1+r) es
tautológica por construcción); ningún testigo es point-in-time; los horarios
se argumentan contra la tabla sellada de `GEMELO/datos.py`, no contra marcas
observadas; y el margen entre «antes de mirar» y «mirando» fue de minutos y
descansa en disciplina, no en mecanismo.

## Enmienda 2 (2-sep-2026, 14:35, después del dictamen del adversario sobre la prueba abierta)

Dictamen: `GEMELO/resultados/dictamen_08/C.md` — **H1 verificado y robusto;
H2 refutada en su premisa (no «inaplicable»); H3 no sostiene «no hay
sobrerreacción medible»; la afirmación de conjunto no sostiene la palabra
«estructural»; el conteo de 14 intentos era la mitad del conteo real**.
Lo que cambia, al ejecutable primero:

1. **El candado se enmienda con rastro, no se rompe:** la prueba ya se abrió
   (14:15) y se volvió a correr con `--enmienda "razón"`; el candado guarda
   hash anterior, hash nuevo, instante y razón, y ahora cubre también los
   tres testigos (sha256). **Ninguna hipótesis cambia**; todo lo agregado es
   reporte que el dictamen exigió, y **cada estadístico nuevo es un
   intento**.
2. `excluir_cero` en los DOS lados (retorno total exactamente cero = el
   mismo artefacto de ffill; en esa fila la sesión es −gap por identidad).
3. McNemar (b, c, p) para las cuatro comparaciones pareadas, con la
   advertencia de que p y Wilson de filas son optimistas por clustering.
4. Intervalo para la fracción de aciertos y las dos contribuciones.
5. Cada IC declara su nulo (1 para la razón de H2) y el umbral
   pre-registrado (±0,1 para las pendientes de H3, 1,5 para la razón).
6. **H2: REFUTADA en su premisa** —los aciertos pierden más que los
   errores— con el IC de la diferencia E[q|acierto] − E[q|error] (contiene
   el cero). Declarado: el criterio original aplicado literalmente habría
   dado un FALSO POSITIVO por aritmética de signos, y **el §7 de la
   Enmienda 1 se escribió después de ver el ajuste**: es una regla de
   lectura post-resultado (atenuante: impidió una confirmación espuria; el
   criterio original no se tocó).
7. **H3:** «no hay sobrerreacción medible» se retira. Queda: «no se detecta
   relación con la sorpresa respecto de β». La pendiente sesión~gap se
   publica con tres cosas: el IC del ajuste contiene −0,10; el signo
   depende del bloque; y es indistinguible de la atenuación por error de
   medición dada la identidad exacta (1+g)(1+r) sin Open independiente.
   Diferencia de terciles alto − bajo con IC.
8. **Costos**, que faltaban en todo el frente: barrido 0/5/10/25 pb por lado
   sobre la cartera direccional Y sobre la contraria que H1 implica, punto
   muerto y DSR de la contraria contando el registro de la máquina.
9. El gap «operable» va rotulado **NO EJECUTABLE**.
10. Colisión de procedencia declarada: el signo crudo del SOX da a Fráncfort
    una ventaja distinguible de cero sobre la ventana reconstruida; el README
    dice +2,5 pp, p 0,111 con el modelo 4.6.0 sobre n = 14.618. Otra
    población, otro predictor.
11. Barrido de bloque (1/5/10/20/40/60); la contradicción bloque 10
    (`backtest/DISEÑO.md` §8.5) vs 20 (`.claude/rules/backtest.md`) va a
    `cola_decisiones.md`. Robustez: dejar-un-año-fuera, dejar-un-ticker-
    fuera, winsorizado, por ticker.
12. **Intentos:** se cuentan por máquina (`contar_intervalos`) = intervalos
    publicados en el artefacto; el 14 se retira; la tupla va a
    `GEMELO/relevo_asiatico.REGISTRO_INTENTOS` con su procedencia.
13. Lo que sigue sin resolverse y se declara: «estructural» es una
    afirmación de horarios que este diseño no midió (la palabra correcta es
    *consistente con*); testigos de dos añadas; IFX.DE no contemporáneo;
    E[q] heterogéneo por ticker.
