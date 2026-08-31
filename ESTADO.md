# ESTADO

Resumen curado de dónde está el proyecto. Se regenera al cierre de cada sesión
con la skill `/cierre-sesion`. **Máximo 50 líneas.** No es historia: la historia
vive en `DECISIONES.md`. Las cifras publicadas viven en `README.md`.

**Actualizado:** 31-ago-2026 (tercera corrida) · verificar con `orientador`

## Producción

- **Titular: este PC (Windows/WSL), en `main`.** 6 timers activos, emite. Al
  modo se le **pregunta a `modo.py`**.
- Modelo 4.6.0 congelado, `PLATAFORMA_VERSION` 5.0.3. Último sello: 2026-08-31
  18:15 · N verificaciones: 253 (248 bajo `excluir_cero`).
- **Réplica: todas las piezas listas y probadas, nada activado.** Ensayo
  general con cero hallazgos + `docs/RUNBOOK_REPLICA.md`. Falta solo la firma.

## Errata pendiente de registrar

Actas 36/37 dicen `MKI_MODO=sombra` puesto — **ya no es cierto**. Manda la
máquina.

## Frente · GEMELO 6.0.0

- **`GEMELO/SECUENCIAL/` — pre-registro TERMINADO Y NO CONGELADO.** Rechazado
  tres veces por `estadistico-adversario` en un día; los tres rechazos
  correctos y corregidos. Lo que falta no es un defecto: el plan declara
  α=0.05 y entrega 0.046–0.079 según la autocorrelación entre fechas, y
  arreglarlo (declarar α=0.10) cambia el estándar del proyecto. **Decisión de
  Nicolás.** Primera mirada escrita para el 2026-11-19; si llega sin
  congelarse, mirar ese día es una mirada más sin declarar.
- **Pasivo medido:** mirar la misma cifra cada vez que crecía costó **α entre
  0.09 y 0.18** (1.8× a 3.6× el nominal). Nunca produjo un falso positivo en
  la cifra principal; **sí en tres subgrupos que hubo que retractar**.
- **`GEMELO/MICRO/SINTESIS.md` — el campeón NO cabe en la Go Board**: 1.545
  celdas contra 1.280. RTL valida 181/181 filas selladas bit a bit, latencia
  32 ciclos constante. Dos afirmaciones de `RTL.md` refutadas.
- **`expediente_pit.md` — no comprar datos PIT, cero dólares.** La
  contaminación por revisión de precios es CERO (lo sostiene un teorema, no la
  muestra). Lo que sigue abierto es la composición del universo, que esos datos
  no arreglan.
- `parche_honestidad.md` **reemplaza** a `parche_documental.md` (retirado).
  Preparado, NO aplicado.
- N del DSR: **≥43** (`relevo_asiatico.py` sigue en 25, sin actualizar).

## Deuda con modo de falla activo

`GEMELO/ventana_larga.py:314-345` emite la cifra de contaminación ya refutada
y `tests/test_ventana_larga.py:186` **la exige por test**. Re-correr el WS3
republicaría la falsedad, y el test verde es lo que lo hace peligroso.

## Esperando decisión de Nicolás

`GEMELO/resultados/cola_decisiones.md`, priorizada por costo de postergar.
Primero: **activar la réplica**. Segundo: **α y MDE del secuencial** (bloquean
el congelamiento). También: el McNemar p canónico es **0.1847** según el módulo
árbitro, no el **0.1849** publicado — regla de los doce bloques, sin aplicar.

## Operación pendiente, de Nicolás

`.env` tiene permisos **644** y la regla pide 600.

## Siguiente paso

`git push origin main` (lo hace Nicolás, tras revisar el diff).
