# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es
historia (`DECISIONES.md`) ni cifras publicadas (`README.md`).
**Actualizado:** 2-sep-2026 (séptima corrida) · verificar con `orientador`

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers, emite; el modo se le pregunta
  a `modo.py`. Modelo 4.6.0 congelado. **Último sello: 2026-09-01.**
- `mki-noticias` murió el 1-sep por `TimeoutStartSec=1800`: **es O(n²) sobre
  toda `noticias.db` y crece cada día** (`parche_timeout_noticias.md`); parche a
  2700 s preparado, **no aplicado** (timers = Nicolás); la solución real toca
  `noticias.py`. El vigía ya distingue «no corrió» de «corrió y no completó».

## Las cuatro reglas de la casa
1. Una verificación con el mismo mecanismo que produjo la cifra no es verificación.
2. Una retractación en prosa no es retractación: la corrección va al ejecutable.
3. Ningún estimador puntual sin intervalo, y el intervalo se computa.
4. Un número retirado que sigue ofrecido en el código vuelve a circular.

## Lo que sigue en pie
- **La ventana sellada no alcanza para juzgar nada:** +9,7 pp, IC95 de día
  [−7,2, +26,5], n efectivo ~67–69, un solo régimen. Cruzar α no es evidencia.
- El gap existe (8 años reconstruidos) y **no es capturable** (−40,7% sin costos).
- Gatillo 5.1: se espera al **25-oct**. Ese día habrá ~73 días sellados:
  **MDE al 80% de 16,6 pp [11,0, 20,3], potencia 0,36 frente a 9 pp** (`horizonte_veredicto.md`).

## Lo nuevo de la séptima corrida (`GEMELO/resultados/bitacora_07.md`)
- **Fuente:** Yahoo no cambió un retorno en 8 años × 27 tickers (censo), pero sirve
  el mismo query en estados distintos: retiró el 28-ago y **cuatro noches de agosto
  sirvió el `^SOX` sin la barra del 31-jul** (hipótesis M6). El sello tiene «emitido
  antes» y no «reproducible después». Las 16 filas de signo contrario **ya están
  verificadas (15) dentro del track record vivo**; el README no se mueve (ancla).
- **Copia de insumos** diseñada y con arnés probado, no activada (`GEMELO/INSUMOS/`).
- **Medible en principio, no en meses:** ~2 obs. efectivas/día; 9 pp → jul-2027 [dic-2026,
  feb-2028], 6,5 pp → jul-2028, 5 pp → dic-2029 (IC en `horizonte.md`). Ciego a «¿persiste?» con un régimen.
- Propuestas C/D/E juzgadas (`propuestas_cde.md`, dictamen en `dictamen_07/`):
  entran C-1/C-2/C-3, D-1 como referencia, E-1 condicionada; **rechazadas E-2 y
  el α 0,083**. **R2 dispara sobre el ancla del 31-ago.** Nada entró a cifra
  publicada ni a criterio congelado. Registro de intentos 91 → 100.

## Deuda con modo de falla activo
`snapshot.py:140` sella `sesion_objetivo` con el reloj de pared: 25 filas, sigue.

## Esperando decisión
`GEMELO/resultados/espera_firma.md` (primero: el parche `:140` + la copia de
insumos en un solo bump; cuál es el campeón cuando sello y fuente discrepan).

## Siguiente paso
`git push origin main` (lo hace Nicolás, tras revisar el diff).
