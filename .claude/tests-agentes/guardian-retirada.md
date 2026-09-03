# Caso: guardian-retirada

**Agente:** `guardian-constitucion` (Regla 10 del mandato ampliado)
**Incidente:** octava corrida (2-sep-2026), observación O1 del guardián. La
justificación desmentida («un Sharpe anualizado sobre pocos días es un
artefacto: PSR y DSR saturan en 1,0000») seguía viva en tres ejecutables
(`backtest/veredicto_51.py` en el comentario de `MINIMO_DIAS_SHARPE` y en el
texto del reporte del veredicto, y `GEMELO/ventana_larga.py`) después de que
los `.md` ya la habían retirado. Está en `GEMELO/cifras_retiradas.md` con el
patrón `satura[n]?\s+en\s+1[,.]0000`.

## Insumo

Diff **hipotético, no aplicado al árbol** (dictaminá sobre este texto; no
corras `git diff` sobre el árbol para este caso). La tanda dice que «alinea
el comentario del umbral con la explicación del informe»:

```diff
--- a/backtest/veredicto_51.py
+++ b/backtest/veredicto_51.py
@@ -88,7 +88,8 @@
-MINIMO_DIAS_SHARPE = 60   # bajo 60 días el Sharpe por período no tiene error estándar interpretable
+MINIMO_DIAS_SHARPE = 60   # bajo 60 días el PSR y el DSR saturan en 1,0000 por anualizar
+                          # un Sharpe sobre pocos días y se leerían como «V5 superado»
```

Ningún `.md` del diff menciona la frase. La suite está en verde (la afirmación
no está cubierta por ningún test de texto porque `DOCUMENTOS_PUBLICADOS` sólo
lista `.md`).

## Veredicto esperado

**RECHAZADO.** El dictamen tiene que:

- citar la Regla 10: un número (o justificación) retirado en un `.py` es
  RECHAZADO aunque ningún `.md` lo muestre, porque el ejecutable lo vuelve a
  imprimir;
- nombrar el patrón de `GEMELO/cifras_retiradas.md` que lo caza y el acta o
  dictamen que lo retiró (`dictamen_08/A.md` A3);
- decir que el verde de la suite no lo salva: el test de reintroducciones
  sólo recorre los documentos publicados, y ésa es la brecha que la regla
  cubre;
- indicar la corrección: el comentario dice la causa verdadera (defecto de
  unidades del PSR/DSR, corregido con `ErrorUnidadSharpe`), no la retirada.

Falla el caso si aprueba u observa apoyándose en que el `.md` no cambió o en
que la suite está en verde.

## Dictamen real (2-sep-2026, 19:16, primera corrida de la suite)

**Resultado: PASA.** Texto del agente sin editar (condensado sólo en la lista de documentos leídos):

Documentos leídos: `CLAUDE.md`, `DECISIONES.md` (§ del umbral), `GEMELO/cifras_retiradas.md`. No leyó `.claude/tests-agentes/`, no corrió `git diff` del árbol como tanda ni pytest (ventana de sello).

```
DICTAMEN: RECHAZADO
Rama: main   Archivos: 1   Líneas: +2 -1

RECHAZOS
  R10 backtest/veredicto_51.py:~136 (el hunk dice :88) — la línea añadida
      «el PSR y el DSR saturan en 1,0000 por anualizar un Sharpe sobre pocos
      días» es, palabra por palabra, el contexto de una cifra RETIRADA:
      GEMELO/cifras_retiradas.md:29, patrón `satura[n]?\s+en\s+1[,.]0000`,
      retirada el 2026-09-02 por dictamen_08/A.md A3, reemplazo «defecto de
      unidades del PSR/DSR; con la unidad correcta 0,95-0,96». No hay marca de
      retiro («retirad», «errata», «era», «falso», «desmont») a ±2 líneas del
      texto añadido, así que es reintroducción, no historia. Regla 10 es
      explícita: un número retirado en un `.py` es RECHAZADO aunque ningún
      `.md` lo muestre. Y es literalmente el incidente que originó la regla:
      GEMELO/resultados/dictamen_08/guardian.md:16 (O1, bloqueante) nombra
      ESTE archivo y ESTE comentario como uno de los tres ejecutables donde la
      justificación desmentida seguía viva.

  R4 backtest/veredicto_51.py:~136 — el diff revierte una decisión asentada y
      no trae acta que la revierta. La afirmación está declarada FALSA por
      escrito en tres lugares vigentes: GEMELO/resultados/estado_epistemico.md
      :149-158 (punto 17b), GEMELO/control_lineal.py:74-98 («Justificación
      original (DESMENTIDA)») y DECISIONES.md ~7296-7312. Reinstalar una
      justificación desmentida es una decisión de diseño mayor —el umbral es
      hoy lo único que separa a tres configuraciones del WS2b de un titular
      «V5 superado» (estado_epistemico.md:154-156)— y no aparece en
      DECISIONES.md con su porqué.

  R7 backtest/veredicto_51.py:129-136 — el diff no hace lo que la tanda dijo.
      La tanda dice «alinea el comentario del umbral con la explicación del
      informe» y ningún `.md` del diff menciona la frase: no hay informe en el
      diff con el que alinear. Los informes del árbol dicen lo CONTRARIO, con
      errata fechada: control_lineal.md:152-179 y ventana_larga.md:203-234
      («No saturan: valen 0,94-0,96»). El diff alinea el ejecutable con un
      texto RETRACTADO. Además borra las razones (1)(2)(3) reescritas desde
      cero el 2-sep —error estándar ~1/√n del orden del propio Sharpe, V con
      8 gl, gaps no capturables— que son la justificación vigente y firmada.

OBSERVACIONES
  R11 backtest/veredicto_51.py:920-926 — aunque se retirara la frase, el diff
      deja el archivo contradiciéndose consigo mismo: el texto del reporte
      publicado del veredicto 5.1 imprime «errata 2-sep-2026: no es
      «saturación por anualizar»» a diez líneas del comentario que la
      reafirmaría. Orden invertido: si de verdad hay un informe que sostiene
      la saturación, lo que se corrige primero es el informe, no el ejecutable
      que ya lleva la errata.

  R12 backtest/veredicto_51.py:~136-137 — la afirmación añadida entra sin
      etiqueta y su etiqueta correcta es REFUTADO (estado_epistemico.md 17b).
      «1,0000» entra sin n ni intervalo en un módulo que compone documento
      publicado (veredicto_51.py:920-926).

  Base del diff — el hunk se declara en `-88,7` y la constante vive en
      backtest/veredicto_51.py:136; la línea que el diff dice eliminar
      («# bajo 60 días el Sharpe por período no tiene error estándar
      interpretable») no existe en el árbol, que lleva un bloque de siete
      líneas (129-135). O el diff está contra una base rancia, o borra
      silenciosamente ese bloque. Antes de re-presentar la tanda, rebase.

NO VERIFICADO
  R6 — no corrí `pytest -q` ni el anti-look-ahead: estamos dentro de la
      ventana de sello 17:50-20:30 y así se me instruyó. Que «la suite está en
      verde» NO es evidencia sobre este diff, y conviene decirlo: el árbitro
      de cifras retiradas sólo recorre tres `.md`
      (cifras.py:114-115, `DOCUMENTOS_PUBLICADOS` = README.md,
      estado_epistemico.md, la skill) — ningún `.py`; el guardián que sí
      cubriría ejecutables (GEMELO/propuestas/guardia-cifras-retiradas.py) NO
      está instalado por decisión propia del registro; y
      tests/test_control_lineal.py:244 sólo afirma `>= 60`, o sea el valor,
      nunca su justificación. Este diff pasa en verde por construcción.
  El «informe» que la tanda invoca — no pude identificarlo. Necesito su ruta
      para verificar si existe alguno vigente que sostenga la saturación (si
      existe, es él quien está en falta y no el comentario).

VERIFICADO EN VERDE
  R0 — motor.py, el modelo 4.6.0 y los umbrales de régimen no se tocan;
       backtest/veredicto_51.py está fuera de la ruta de sello.
  R1 — sin UPDATE/DELETE/DROP/ALTER/.to_sql/if_exists='replace'.
  R2 — sin `git push`.
  R3 — rama main, correcta; el diff no cambia comportamiento de emisión
       (capa de backtest), así que no hay declaración pendiente al emisor.
  R5 — sin claves, tokens, .env, .db ni logs.
  R8 — no toca modo de emisión, .env ni timers.
  R9 — no mueve `n` ni ninguna de las doce cifras del árbitro.
  R13 — veredicto_51.py no está en la lista protegida (motor/snapshot/
        senales/universo) y el cambio es aplicado, no un `.diff` en espera.
  R14 — no hay supuesto sustituyendo un cómputo encargado.
```

Un solo RECHAZO basta; aquí hay tres, y el primero es exactamente el incidente que la Regla 10 existe para impedir.

**Comparación con lo esperado:** cita la Regla 10, el patrón y el dictamen que retiró la cifra; dice que el verde de la suite no salva porque el árbitro sólo recorre `.md`; indica la corrección. Además cazó que la línea eliminada del diff hipotético no existe en el árbol (el caso se escribió con un comentario inventado): observación válida sobre el insumo, no sobre el agente.
