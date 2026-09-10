# Dictamen del `estadistico-adversario` — §43, el período de M2

**Corrida 12, bloque 8.1.** Escrito 2026-09-09 00:18 −03 (03:18 UTC), leído de `date`, no estimado.
Artefactos verificados por `mtime`: `m2_periodo.json`/`.md` 00:11:24, `m2_periodo.py` 00:10:20, `cuenta_papel.json` 23:54:18 del 8-sep. Coinciden con lo declarado.
Cifras canónicas leídas de `.claude/skills/cifras-canonicas/SKILL.md` (n=238, +9,7 pp, IC de día [−7,2, +26,6]); ninguna de este dictamen las toca.
(Archivado tal cual por el orquestador; la aplicación de las exigencias está en `bitacora_12.md`, bloque 8.)

## 1. Verificación de cifras

Recomputé a mano una celda con `venv/bin/python`, por camino independiente de `lecturas_m2` (sumando `m.comision_usd` sobre `libro.movimientos` y los aportes del calendario):

```
semilla 0, conservador: corte52 2024-09-03  comisión 17.4843 / aportado 500.0 = 3.50 %
                        corte104 2025-09-02  41.015 / 500.0 = 8.20 %
                        corte156 2026-09-01  62.496 / 500.0 = 12.50 %
```

El JSON trae `{'conservador': [3.5, 8.2, 12.5]}` para la semilla 0. **Reproduce exacto.** `m2_periodo.py` computa lo que dice.

Wilson sobre las proporciones entre semillas (`evaluacion.py`, self-test TODO EN VERDE):

```
conservador dispara@52 : 0/20 = 0.0 %  Wilson95 [0.0, 16.1]
conservador dispara@156: 0/20 = 0.0 %  Wilson95 [0.0, 16.1]
medio dispara@156      : 17/20 = 85.0 %  Wilson95 [64.0, 94.8]
```

## 2. Análisis dimensional (la parte que decide)

- **Numerador:** comisión acumulada, USD, es un **flujo** sobre [0, h]. Crece monótono con h.
- **Denominador:** capital aportado, USD, es un **stock**. Verificado en `contabilidad.calendario_aportes` y en la corrida: **5 aportes de 100 USD y después nada; el denominador vale 500 desde la semana 5 y NO crece**.
- **Cociente:** adimensional en USD, pero **proporcional a h**. Sus unidades reales son «% del capital *por período*», y el período es el argumento.
- **Umbral 25 %:** un número desnudo, **sin período declarado**. Dimensionalmente incompleto. Y peor: se escribió mirando la banda de la cuenta v1 (la del «14 % a 43 %», cifra RETIRADA por fuga y citada acá sólo como historia), que es de **156 semanas** (§6 E lo dice). El período implícito en la autoría del umbral es 156 semanas ≈ **8,3 %/año**.

**Consecuencia:** elegir 52 semanas no es elegir una lectura entre lecturas equivalentes; es dividir el numerador por ~3 dejando el umbral quieto. Es un aflojamiento de 3× de un criterio de **cierre**, hecho con las tres respuestas sobre la mesa.

**La tasa anualizada es la única lectura invariante al período** (computada desde el JSON):

| juego | anualizada desde 52 s | desde 104 s | desde 156 s |
|---|---|---|---|
| conservador | 3,87 %/año [3,56 · 4,58] | 4,28 [3,18 · 4,69] | 4,12 [2,12 · 4,37] |
| medio | 9,38 [8,23 · 10,82] | 9,41 [7,28 · 10,20] | 8,86 [4,85 · 9,51] |
| agresivo | 6,44 [5,77 · 7,78] | 6,20 [5,81 · 6,94] | 6,25 [5,91 · 6,63] |

Estable a través de los tres horizontes. Eso es la prueba aritmética de que la recomendación (c) del §43 era la correcta: **elimina el grado de libertad en vez de firmarlo.**

## 3. Tres hallazgos que el módulo no publica

**(a) La elección es materialmente INERTE para M2 como está escrita.** M2 gobierna «el juego **por defecto**» (`reglas.json: juego_activo = "conservador"`, versión `0.2.0-PROPUESTA`, sin firma). Conservador: 3,9 · 8,6 · 12,4 · 5,0 % — **techo de banda 13,1 %, no cruza el 25 % en ningún horizonte**. `medio` cruza a 156, pero M2 no lo nombra. La elección de Nicolás no cambia el veredicto de M2 sobre el juego que M2 rige.

**(b) El ratio está acotado por construcción, y en la dirección equivocada.** En 5 de 20 semillas la cuenta conservadora **se congela**: semilla 2, último movimiento 2025-03-31, efectivo final 3,30 USD con 7 posiciones; semilla 12, 2025-04-03, efectivo 7,51. La comisión deja de acumularse porque la cuenta deja de operar, no porque sea barata. Por eso las bandas a 104 y 156 son **bimodales** (conservador@156: 15 semillas en 12–13 %, 5 en 6,3–7,5 %) y publicar p2,5/p97,5 de una mezcla bimodal como «banda» es engañoso. M2 puntúa **bajo** a la cuenta que la fricción mató. Un criterio de cierre que premia la quiebra no mide lo que dice medir.

**(c) M2 como se computa excluye el deslizamiento**, decisión no firmada (§7 B (ii) sigue abierto). `deslizamiento_usd` vive aparte de `comision_usd`. Medido: conservador vida 12,50 % → **13,87 %** con 5 pb; medio 25,90 % → **29,31 %**. No cambia ningún veredicto, pero la elección está tomada por el módulo, no por el pre-registro.

**(d) Dos documentos publican la misma banda con dos definiciones.** `cuenta_papel.md` da conservador [6,35 · **13,2**] (vida entera, 156,4 semanas); `m2_periodo` da [6,35 · **13,1**] (156 semanas exactas, corte 2026-09-01, 3 días antes del fin). Diferencia real de definición, no de redondeo.

## 4. ¿Es la banda la incertidumbre correcta? ¿Tiene potencia el «0 de 20»?

**No y sí, respectivamente.** La banda entre semillas captura **una sola** fuente de variación: el sorteo de la señal sin información (que fija cuántas órdenes hay). No captura la fuente que domina la pregunta prospectiva: **hay UNA sola trayectoria de mercado**, 2023-09-05 a 2026-09-04. Es la misma forma que «n = 228 en un solo régimen es más chico que n = 228». La banda no es un intervalo sobre «cuánto costará rotar las próximas 52 semanas».

El «0 de 20 a 52 semanas» **no es una afirmación de potencia baja**: conservador@52 tiene media 3,97, sd entre semillas 0,333, máximo 4,69; el umbral está a **61 desviaciones** del máximo observado. No es un casi-cruce. Pero el Wilson honesto sobre las semillas es **[0 %, 16,1 %]**, y eso es todo lo que 20 sorteos sobre una historia pueden decir. Y no ordeno «el efecto observado está por debajo del umbral con margen»: la cantidad de la izquierda es un sorteo sobre una trayectoria fija y la de la derecha un umbral sin período; **el diseño no las ordena**.

## 5. La lectura de los textos que gobiernan

El §2 punto 1 dice **«Período mínimo: 52 semanas de cuenta en papel corriendo hacia adelante»**. Eso es (i) un **piso** sobre la duración de la cuenta, no un horizonte de acumulación para M2; y (ii) **prospectivo**. Ninguna de las dos cosas es lo que `pct_a_52_semanas` mide: mide el primer año de una simulación retrospectiva sobre precios congelados. El §7 B (iv) ya lo había dicho: «la cifra sobre 52 semanas **hacia adelante**, que es la única que el criterio nombra».

Por lo tanto **el «horizonte pre-registrado de la vara» que el §84.4.5 invoca no existe escrito**, y se dispara la cláusula de escape del propio §84.4.5: *«Si la vara no tiene horizonte escrito, la decisión no es aplicable todavía y vuelve a la cola con la pregunta exacta.»*

## VEREDICTO

**OTRA COSA: NO APLICABLE.** La elección no invalida el pre-registro ni basta con declararla; **no puede tomarse como está formulada**, porque el «horizonte pre-registrado de la vara» que invoca no existe en el §2 (52 semanas es un piso prospectivo sobre la duración de la cuenta, no una ventana de acumulación de M2), y la cláusula de escape que el propio §84.4.5 escribió se dispara sola.

Y por si se reformulara: la elección **sí es del tipo que el §5 declara ilegítimo** —afloja 3× un criterio de cierre, con las tres respuestas a la vista— aunque en este caso sea **inerte**, porque el juego que M2 nombra no cruza en ningún horizonte. Que no cambie el resultado no la vuelve legítima; la vuelve barata de deshacer.

**La vara honesta que queda: las cuatro lecturas se publican todas sin elegir una, y la lectura que se compara contra un umbral es la TASA ANUALIZADA** (opción (c) del §43, ahora con la aritmética que la respalda), con el umbral **re-declarado en %/año antes** de que corra la cuenta prospectiva. M2 no se mata: se re-registra hacia adelante.

## Exigencias

Al ejecutable (`GEMELO/m2_periodo.py`):

1. **E1.** Publicar `pct_anualizado_desde_{52,104,156}` con mediana y banda, y declararlo lectura primaria. Campo `convencion_anualizacion: "suma aritmética"` (regla D6 del re-dictamen).
2. **E2.** `denominador_usd: 500.0`, `n_aportes: 5`, `aportes_terminan_en: <fecha>` y la frase **«el denominador NO crece; el numerador es un flujo»** en el JSON y en la tabla.
3. **E3.** Marcar cada celda que cruza el 25 % y publicar `semillas_que_disparan` **para los cuatro horizontes**, no sólo para 52.
4. **E4.** Campo `semillas_congeladas` por juego y horizonte (último movimiento < corte y efectivo < precio mínimo operable), con la advertencia de que su lectura baja **por quiebra operativa, no por baratura**. Y sustituir la «banda» por mín–máx + el conteo de los dos modos cuando la distribución sea bimodal.
5. **E5.** `deslizamiento_incluido: false` explícito, con la lectura alternativa incluyéndolo (conservador vida 13,87 %; medio 29,31 %) y la cita de que §7 B (ii) sigue **sin firma**.
6. **E6.** `pct_a_156_semanas` declara que corta 3 días antes del fin de la cuenta y **no** es la cifra de vida entera de `cuenta_papel.md` (13,1 contra 13,2).
7. **E7.** Bloque `una_sola_trayectoria: true`, `n_historias_de_mercado: 1`, `la_banda_no_cubre: "variación de trayectoria de mercado"`.
8. **E8.** `periodo_firmado` se reemplaza por `periodo: NO APLICABLE — vuelve a la cola (§84.4.5, cláusula de escape)`, citando este dictamen.
9. **E9.** `juego_por_defecto: "conservador" (reglas.json 0.2.0-PROPUESTA, SIN FIRMA)` junto a toda lectura de M2.

Al texto (`preregistro_dinero.md`, `espera_firma.md`, acta):

10. **E10.** Enmienda fechada al pre-registro, **sin borrar**, que reescriba M2 en **%/año** con umbral re-declarado y con el período de la cuenta prospectiva escrito **antes** de la primera fila. Debe decir explícitamente que el 25 % original se escribió contra una cifra de 156 semanas ≈ 8,3 %/año.
11. **E11.** El §84.4.5 se corrige con nota fechada: la decisión se tomó, este dictamen la declara **no aplicable** por falta de horizonte escrito, y vuelve a `espera_firma.md` §43 con la pregunta exacta: *«¿en qué unidad y contra qué umbral se lee M2, y sobre qué ventana de la cuenta prospectiva?»*
12. **E12.** El §43 registra que **se computaron 12 lecturas (3 juegos × 4 períodos) y se eligió 1 con los resultados a la vista**. Eso se declara en el artefacto, no sólo en el acta.
13. **E13.** M2 no puede seguir siendo un criterio de cierre que puntúa bajo a la cuenta congelada. La enmienda de E10 agrega la condición de supervivencia operativa (la cuenta que no puede tomar una posición entera está **muerta**, y eso dispara M2 aunque su ratio sea 6 %).

## Conteo de intentos

**Esto NO es un intento del DSR, y `intentos_dsr: 0` es correcto.** No hay selección sobre Sharpes, no hay hipótesis sobre una señal: la señal es sin información por construcción y la nula es conocida. No suma a `GEMELO.relevo_asiatico.N_INTENTOS_ACUMULADO` ni a `dinero/registro_intentos.N_INTENTOS_RIEL_LARGO`.

**Pero sí es un grado de libertad del investigador y se registra como tal:** fila «§43 — lectura del período de M2: 12 lecturas computadas, 1 elegida con los resultados a la vista, elección declarada NO APLICABLE» en un tercer contador —**lecturas de criterio**, no intentos de DSR—. Dónde vive ese contador es decisión de Nicolás y va a la cola.

## Qué se publica y con qué estatus

- `GEMELO/resultados/m2_periodo.md` / `.json`: **se publican, con las cuatro lecturas y sin período elegido**, estatus **PROPUESTA** hasta E1–E9. Las cifras aritméticas **SOSTIENEN** (reproduje una celda exacta); lo que no sostiene es la etiqueta `periodo_firmado`.
- La lectura primaria publicable hoy: **conservador gasta 3,9 %/año [3,56 · 4,58] del capital aportado en comisiones**, sobre una sola trayectoria de mercado y 20 sorteos de señal, deslizamiento excluido. Con deslizamiento, ~4,4 %/año.
- **M2 sigue sin poder leerse como disparada ni como no disparada**, exactamente como decía el §6 E — pero ahora por una razón distinta y mejor documentada: no es que falte elegir el período, es que **el umbral no tiene unidad**.
- Ninguna cifra de acá entra al README. Ninguna toca las canónicas (n = 238).

**Un resultado negativo es un resultado:** la decisión firmada del §84.4.5 punto 5 no se puede ejecutar, y eso es el hallazgo, no un trámite pendiente.
