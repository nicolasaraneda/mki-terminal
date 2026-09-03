# Las cinco preguntas del WS4 (DECISIONES.md §33.8; cola §7) — corrida 09, Frente 2f (Parte 3)

**Fecha:** 3-sep-2026, 10:03 (America/Santiago) · Todo lo nuevo es PROPUESTA;
cada afirmación lleva su estatus. Sin red, sin escribir en bases, sin tocar
`DECISIONES.md`/`README.md` (el orquestador integra).

## Resumen en una tabla

| # | Pregunta | Estado hoy | Qué queda por decidir |
|---|---|---|---|
| 1 | Corregir la ventana larga a la convención congelada | MEDIDO ya en `auditoria_ws3.md` (+15,66 pp, n=14.618); README lo publica; **código y `ventana_larga.md` siguen en la convención vieja** | Parchar `cl._acierto`/`ventana_larga.py:306` y re-correr (exige red) — tarjeta abajo |
| 2 | Corregir la sección de contaminación del WS3 | Código corregido (no por el acta §68, que no la menciona); **reporte estaba stale → errata al pie agregada hoy** | Nada, salvo que se quiera re-correr el módulo para regenerar la tabla |
| 3 | Reconciliar el §32.5 refutado | Sin marca de errata en el §32.5 | Tres líneas en DECISIONES.md — tarjeta |
| 4 | Cómo reportar Fráncfort | README ya lo reporta desglosado y con la explicación refutada | Si se añade el IC del desglose por bolsa — tarjeta |
| 5 | Las 8 filas del 29-jul | **MEDIDO: la regla de dedup firmada el 1-sep ya sacó las 7 saltadas del track record vivo**; la 8.ª (IFX.DE) no saltó sesión | Nada operativo; queda declarar el efecto sobre la ventana congelada |

---

## 5. Las 8 filas del 29-jul — MEDIDO (sin descargar; `senales.db` en `mode=ro`)

**Qué son.** El 29-jul se emitieron 8 predicciones: 7 asiáticas
(000660.KS, 005930.KS, 2330.TW, 3436.T, 4063.T, 6857.T, 8035.T) con
`sesion_objetivo = 2026-07-31` —la sesión del 30 quedó **saltada** por el
sello tardío— y 1 (IFX.DE) con objetivo 2026-07-30, que **no** saltó nada.
El 30-jul se volvieron a emitir las 7 asiáticas para la misma sesión objetivo
(07-31) con el mismo `gap_pct` sellado.

**Qué hizo la regla firmada.** `backtest.linea_base.cargar(dedup=True)`
(default desde la firma del 1-sep; causalidad `max()` del acta §62) conserva
por (ticker, sesión objetivo) la emisión del 30-jul y **descarta las 7 del
29-jul**. En la ventana viva quedan del 29-jul solo IFX.DE. Las 7 descartadas
acertaron 0/7; las 7 conservadas del 30-jul, 7/7 (mismo gap, distinta
predicción: el SOX del 30 apuntaba al alza).

**Efecto medido (ventaja = acierto − «siempre al alza», convención
`excluir_cero`; IC 95 % por clúster de día, 4.000 réplicas, semilla sellada;
p por permutación de signo por día):**

| Conjunto | n | días | acierto | base | ventaja | IC clúster de día | IC t-clúster | p perm. |
|---|---|---|---|---|---|---|---|---|
| Track record vivo hoy (dedup, hasta 1-sep) | 269 | 38 | 66,9 % | 52,8 % | **+14,1 pp** | **[−2,3, +30,9]** | [−3,1, +31,4] | 0,117 |
| Vivo sin las 7 saltadas | 269 | 38 | idem | idem | idem | idem | idem | idem (ya no están) |
| Vivo sin las 8 del 29-jul (también IFX.DE) | 268 | 37 | 66,8 % | 53,0 % | +13,8 pp | [−2,9, +30,7] | [−3,5, +31,1] | 0,134 |
| Ventana congelada del WS2b (223, rama histórica `dedup=False`, `hasta_sello=2026-08-24`) | 223 | 31 | 65,9 % | 61,9 % | +4,0 pp | [−14,3, +21,9] | [−15,1, +23,2] | 0,699 |
| Congelada sin las 7 saltadas | 216 | 31 | 68,1 % | 60,6 % | +7,4 pp | [−10,6, +24,6] | [−11,5, +26,3] | 0,470 |
| Congelada sin las 8 del 29-jul | 215 | 30 | 67,9 % | 60,9 % | +7,0 pp | [−10,8, +25,4] | [−12,0, +25,9] | 0,495 |

Nota de conteo: la fila «vivo» de esta tabla es lo que `lb.cargar()` devuelve
esta mañana (n=269, 5-jul → 1-sep) y **no** es la cifra canónica del README
(n=238, +9,7 pp), que sale de otra fecha de corte/convención de bloques; se
publica aquí solo para responder la pregunta, con sus parámetros, no como
cifra del proyecto.

**Respuesta.** (a) En las métricas vivas la pregunta **ya no existe**: las 7
filas saltadas salieron por una regla firmada por Nicolás, no por una
decisión ad hoc sobre este caso. (b) En la ventana congelada de 223, quitarlas
mueve la ventaja de +4,0 a +7,4 pp, **con IC de día que incluye cero en los dos
casos** (p 0,70 → 0,47): no cambia ninguna conclusión. (c) La regla de
abstención por sello tardío (propuesta 5.0.2) sigue **sin implementar y sin
firmar**; la dedup la hace innecesaria para el conteo, no para la emisión —
el sistema sigue emitiendo tarde una predicción que después descarta. Eso es
una decisión de Nicolás, con un caso concreto: **PROPUESTA** mantenerla como
está (modelo 4.6.0 congelado) y registrar esta medición como cierre de la
pregunta 5.

---

## 2. La sección de contaminación del WS3 — RESUELTA en código, errata añadida al reporte

- **Verificado:** el acta §68 **no** la menciona (grep en sus 72 líneas:
  nada de `ventana_larga`/contaminación). Lo que sí ocurrió: la función de
  contaminación de `GEMELO/ventana_larga.py` (docstring, líneas 211-236)
  alinea ahora por `sesion_objetivo`, declara el 91,4 % anterior como
  artefacto refutado y da 100 %; `tests/test_ventana_larga.py` ya no exige la
  cifra vieja (grep de `91`/`8.6`/`contamin`: vacío). Últimos commits del
  módulo: 6bb1f46, e900236 (1-sep), 0fbfbe9 (2-sep).
- **Lo que faltaba:** `GEMELO/resultados/ventana_larga.md` seguía mostrando
  «coincide en el 91,4 %», «17 filas», sin errata. **Hecho hoy:** errata
  fechada al pie (punto 2 de la nota) que remite a `auditoria_ws3.md`
  Amenaza 7 y a §33.4, sin editar las cifras originales.
- **Cola §5 («la mina»):** con el código y el test ya corregidos, la mina
  está desactivada; re-correr el módulo regeneraría la tabla correcta. Queda
  solo el reporte stale, ahora marcado. PROPUESTA: cerrar §5 y §7.2 de la
  cola con esta nota.

---

## 1. La ventana larga a la convención congelada — TARJETA

**Qué decidir:** si se parchea el código del WS3 para que aplique
`excluir_cero` y se re-corre (con red) para regenerar `ventana_larga.md`, o
si basta la corrección ya medida en la auditoría.

**Estado (MEDIDO):** `auditoria_ws3.md` tabla de convenciones: `estricta`
(la del WS3) +15,90 pp / 14.711 filas; **`excluir_cero` +15,66 pp / 14.618
filas**. El README publica lo segundo. El código sigue en la convención
vieja: `GEMELO/control_lineal._acierto` (`(pred>=0)==(gap>=0)`) con
`base = gap > 0` en `control_lineal.evaluar`:283, `evaluar_r2`:373 y
`ventana_larga.py`:306 — el sesgo que la §33.1 nombró (105 filas con
gap==0,00 regaladas al modelo y negadas a la baseline).

**¿Recomputable esta noche?** NO EVALUABLE sin red: `ventana_larga.py:94`
baja el OHLC del campeón con `yf.download` y no lo cachea; además la caché
de cierres del 1-sep tiene `^VIX3M` sin datos desde el 17-jul (ver
`ic_dmae_recomputados.md`), así que aun con red C2/C3 podrían salir con
menos cobertura que en agosto.

**Opciones:** (A) dejarlo: README correcto, reporte con errata al pie
(añadida hoy, punto 3). (B) parche de código: `_acierto` y las tres `base`
pasan a excluir gap==0 en el **medidor** (no en `senales.py`), con test que
falle si vuelve la convención vieja; re-corrida del WS3 cuando Nicolás
autorice red. (C) B sin re-corrida: el código queda correcto y el reporte
stale marcado.

**Costo:** A = 0. B = ~1 h de código y test + una corrida (~minutos) + acta;
re-correr **consume intentos del DSR** (regla §4.2 bis: cada par
configuración × ventana con resultado reportable). C = la mitad de B.

**Recomendación PROPUESTA:** **C ahora, B cuando se abra una ventana con
red.** El riesgo que importa es el de la cola §5: código que republica una
cifra vieja con test verde. Con C ese riesgo desaparece sin gastar intentos.

---

## 3. Reconciliar el §32.5 refutado — TARJETA

**Qué decidir:** cómo queda escrito en `DECISIONES.md` que el §32.5
(«el 29-jul huele a sello corrupto») fue refutado por el §33.3 (0 de 223
filas superan el 5 %; desviación máxima 0,00 %).

**Estado (MEDIDO):** el §32.5 no lleva marca de errata ni remisión; quien lo
lea sin llegar al §33.3 se queda con la hipótesis. La casa ya resolvió esto
antes: la errata fechada bajo el encabezado, sin tocar el texto original
(estilo de las actas §62/§66).

**Opciones:** (A) tres líneas bajo el título del §32.5: «Errata 3-sep-2026:
REFUTADA en §33.3 — los gaps sellados reproducen exactos; lo que hubo fue
una sesión saltada por sello tardío. Las 7 filas salieron después del track
record vivo por la regla de dedup firmada el 1-sep (§60-§62); efecto sobre la
ventana congelada medido en `corrida09/ws4_cinco_preguntas.md`». (B) no
tocar y confiar en el orden de lectura.

**Costo:** A = 3 líneas del orquestador (DECISIONES.md no es editable por
este frente). **Recomendación PROPUESTA: A.**

---

## 4. Cómo reportar Fráncfort — TARJETA

**Qué decidir:** si la forma actual del README (tabla por bolsa: Tokio
+19,1, Taipéi +16,8, Seúl +15,4 con p≈0; **Fráncfort +2,5 pp, p=0,111**,
8,75 h; más la sección «la explicación que probamos, y falló», WS5) es la
forma definitiva, o si falta algo.

**Estado (MEDIDO):** ya está reportado como desglose, no como promedio, y con
la hipótesis del relevo asiático marcada REFUTADA (§34: E2 «solo Asia» queda
**por debajo** de la base, 53,4 % vs 55,2 % en Fráncfort). Lo que la fila de
Fráncfort **no** lleva es intervalo: solo p. Para XETR hay un ticker por
fecha (IFX.DE), así que fila = día y el IC de clúster coincide con el
pareado por fila; **no se pudo computar esta noche** (exige el panel de la
ventana larga, NO EVALUABLE sin red).

**Opciones:** (A) dejar como está. (B) añadir a la fila de Fráncfort el IC 95 %
de la diferencia pareada cuando se re-corra el WS3 (misma corrida que la
tarjeta 1-B) y una frase: «con 1.955 filas, un efecto de +2,5 pp no es
distinguible de cero; tampoco está descartado». (C) retirar la fila de
Fráncfort del titular y dejarla solo en el desglose.

**Costo:** A = 0; B = una corrida con red + una línea; C = una edición.
**Recomendación PROPUESTA: B**, acoplado a la re-corrida de la tarjeta 1. No
C: quitar la bolsa que no funciona es la selección que el DSR penaliza.

---

## Intentos del DSR de esta parte

4 intervalos publicados sobre retornos reales (vivo 269, vivo 268,
congelada 223, congelada 216/215 —contadas como una hipótesis, «quitar el
29-jul», medida en dos ventanas—). Son re-mediciones del campeón, no
configuraciones nuevas; se declaran y el registro decide.

---
Herramienta de análisis — no constituye asesoría financiera. **No es el
veredicto de la 5.1.**
