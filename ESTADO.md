# ESTADO

Resumen curado de dónde está el proyecto. Se regenera al cierre de cada sesión
con la skill `/cierre-sesion`. **Máximo 50 líneas.** No es historia: la historia
vive en `DECISIONES.md`. Las cifras publicadas viven en `README.md`.

**Actualizado:** 1-sep-2026 (cuarta corrida) · verificar con `orientador`

## Producción

- **Titular: este PC (Windows/WSL), en `main`.** 6 timers activos, emite. Al
  modo se le **pregunta a `modo.py`**.
- Modelo 4.6.0 congelado, `PLATAFORMA_VERSION` 5.0.3. Último sello: 2026-08-31
  18:15 · 261 verificaciones (256 bajo `excluir_cero`).
- **Réplica: piezas listas y probadas, nada activado.** `replica_una_pagina.md`
  es la página para decidir en cinco minutos.

## Errata registrada, y una que queda

Actas 36/37 decían `MKI_MODO=sombra` — **ya no es cierto** (`modo.py` →
`titular`). Registrada como errata en **§57**. Sigue viva en `CLAUDE.md`,
que dice que el Mac es titular: **eso lo tiene que ver Nicolás**, no se
corrige de paso porque cambia cómo trabajan todas las sesiones futuras.

## Regla nueva de la casa (§52)

**Una verificación que usa el mismo mecanismo que produjo la cifra NO es una
verificación.** Vara independiente de otra familia de método; si no existe, se
dice. Se cobró una pieza el día que se escribió, y era mía.

## Frente · GEMELO 6.0.0

- **`GEMELO/SECUENCIAL/` — NO CONGELADO, rechazado 4 veces.** α = 0.05 ya está
  firmado con la banda [0.046, 0.079]. Lo que bloquea ahora es **la regla de
  deduplicación** y el **MDE**. Ver abajo.
- **Verificado en verde y no hay que volver a tocar:** las fronteras contra dos
  varas externas, la tabla de exposición residual (8/8 celdas), el candado del
  MDE, y el pasivo de miradas [0.09, 0.18].
- **Retractado en esta corrida, y era mío:** la "razón 2" del MDE (la razón de
  magnitudes tiene IC95 [0.89, 2.16], **incluye 1.0**) y la "vara independiente"
  que era una reproducción del mismo campo.
- **`GEMELO/MICRO/` — la A7-100T medida.** El cuello no es la lógica ni la BRAM
  (sale 0) ni la DDR3L: es el **DSP48E1 a 240 tickers**. La mejor mejora es
  gratis: ingesta ancha, **32 → 11 ciclos**, con el área *bajando*. El 4.6.0
  completo **cabe** (1,4% de LUT6) y es 309% de la Go Board entera.
- N del DSR: **25** (`RELEVO.md`:147, con test).

## Hallazgo urgente, sin decidir

**30 de 256 filas (11,7%) apuntan a la misma sesión objetivo que otra.** La
regla que se elija mueve el veredicto de un lado al otro del umbral:
`keep="first"` → p = 0,1847; `keep="last"` → **p = 0,0323**. Mientras no se
firme, todo análisis de la ventana sellada tiene un grado de libertad sin
declarar.

## Deuda con modo de falla activo

`GEMELO/ventana_larga.py:314-345` emite la cifra de contaminación ya refutada y
`tests/test_ventana_larga.py:186` **la exige por test**.

## Esperando decisión de Nicolás

`GEMELO/resultados/cola_decisiones.md`, por costo de postergar. Primero:
**la regla de deduplicación** (§2a) y **activar la réplica** (§1). Después: el
**MDE** (§2b, el 7 pp quedó retirado por escala equivocada), la **cuenta AMD**
que bloquea todos los hitos del ramo (§4), y el **método del McNemar** (§3-bis).

## Operación pendiente, de Nicolás

`.env` tiene permisos **644** y la regla pide 600.

## Siguiente paso

`git push origin main` (lo hace Nicolás, tras revisar el diff).
