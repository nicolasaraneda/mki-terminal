# Dictamen del `auditor-lookahead` sobre la reconstrucción de la cuenta en papel (corrida 11, bloque 2)

**8-sep-2026, 01:45 hora de Chile aprox. Texto del agente, archivado por el orquestador sin editar
el contenido (sólo formato).** Lo que se aplicó de esto en la misma corrida está en la bitácora
(G1, G2, G4, G5, G6, G7, G9); lo demás (G3, G8) queda para la corrida 12.

**NO ENCONTRÉ FUGA** en la cuenta reconstruida. Encontré una **debilidad demostrada del gate E6**, una
convención muerta y varias zonas ciegas. Partí del supuesto de que había fuga y ataqué con truncados
no declarados, perturbaciones de valor e inyecciones; ninguna la sacó.

## Fugas demostradas

Ninguna en el código actual.

## Debilidades demostradas (no son fuga hoy; son la puerta por donde entraría mañana)

- **D1.** `cuenta_papel.verificar_invariancia` era **ciego a una fuga de 1 día que entre por
  `precios_ref`**. Inyecté `fila_m = cierres.iloc[i+1]` en `correr_estrategia` (el precio con que se
  dimensiona la decisión pasa a ser el de mañana) y el gate con los dos cortes declarados devolvió
  `INVARIANTE`. Barrí 11 cortes: la detecta en 2 (2024-12-31, 2026-07-31) y en ninguno de los dos
  declarados. Materialidad: `medio` a 5 pb 415 → 436 órdenes, final 1220,42 → 969,43 USD. Mecanismo:
  una fuga de k días sólo deja huella en los k días anteriores al corte, así que el poder del gate
  contra fugas cortas es la probabilidad de que justo ese día haya una decisión distinta. Es el
  problema de purga/embargo trasladado al gate.
- **D2.** El descuento de **caja comprometida era código muerto**: 0 de 754 días con
  `comprometido != 0` (con retardo 1, `pendientes` queda vacío en el paso 1 antes del paso 3). Y las
  dos patas usaban convenciones distintas para esa cantidad siempre nula. Con retardo > 1 divergían.

## Respuestas ejecutadas

1. `correr()` sin dependencia del futuro que yo pueda encontrar. 58 cortes no declarados
   equiespaciados: INVARIANTE, 136.996 movimientos y 137.444 decisiones comparadas (102 s). Sobre el
   código de hoy, 24 cortes más: INVARIANTE. Perturbaciones, no sólo truncados, en 2024-03-15 y
   2025-06-30, seis por corte (×3, ruido, NaN total, barajar filas, invertir el orden temporal, columna
   nueva viva sólo después de t): 0 claves distintas en las 12.
2. E1 no introduce sesgo distinto del declarado, y el que introduce va en contra: 33 operables al
   DESDE contra 29 al HASTA. Los 3 excluidos lo son por causa legítima: ASML (647,27 > techo 500 al
   2023-09-05), SNDK y ARM (sin cierre anterior al DESDE). Mediana de retorno en ventana: excluidos
   +296,4 % contra incluidos +166,1 %. Distorsión nueva, no fuga: la membresía es un corte transversal
   fijo, ni futuro ni point-in-time (ARM listada el 14-sep-2023, SNDK el 13-feb-2025, vetadas tres
   años). Supervivencia residual: las 36 columnas son una lista escrita a mano en sep-2026.
3. Mismo mecanismo de retardo en las dos patas (1 sesión). La caja comprometida no estaba bien
   descontada: estaba sin descontar por vacuidad (D2). `medio` a 5 pb: 255 decisiones de compra → 254
   movimientos, 0 reducidas; la columna «reducidas» vale 0 en 11 de 12 celdas.
4. E3 sigue sin información sobre la dirección: n = 24.222 pares (señal, retorno real a 20 d), corr
   = −0,0055, acierto de signo 51,21 % contra 60,59 % de «siempre arriba». Pero la sonda no es neutral:
   57,9 % de los sorteos son positivos y la magnitud media es +2,21 pp (deriva 2018-2023). Conocible al
   DESDE, no es fuga: lo medido es la fricción de un comprador aleatorio sesgado a largo.
5. El gate sí ve una fuga por los aportes y sí ve una ejecución al cierre de d+3. No veía la de 1
   día por `precios_ref` (D1).
6. `sigma_diferencia_semanal` = 2,3362 pp/semana, IC95 [1,9952, 2,6686], 156 semanas: sin fuga
   temporal (descriptiva sobre series ya producidas). Reservas: σ de un solo sorteo, y alimenta la
   tabla de potencia calibrada sobre la misma ventana que después justifica.
7. E7 corresponde igual, como guarda de regresión: los cortes de `tests/test_senal_larga.py`
   estaban en o después del borde de ajuste. Corrí 2019-12-31, 2020-12-31, 2021-06-30, 2022-12-30,
   2023-03-31 × 2 horizontes × 3 especificaciones = 30 celdas: diferencia máxima 0,0.

## Verificado limpio

- `tests/test_motor.py` exit 0. Suite completa sobre árbol quieto: 778 passed, 1 xfailed (352,92 s);
  una corrida intermedia dio 1 failed por edición concurrente del árbol.
- E5: σ hasta el DESDE = 14,17 (archivo entero 15,6177); apagados 14,2 / 21,3 / 28,3 coinciden con
  k × σ. Materialidad nula: peor pérdida acumulada 43,29 / 43,59 / 36,96 USD contra umbrales 71,00 /
  106,50 / 141,50.
- Calendario: 2011 filas = 2011 sesiones XNYS, 0 faltantes, 0 extra.
- Segundo congelado (8-sep 04:21 UTC): 32.880 de 68.720 celdas difieren con diferencia relativa
  máxima 8,4e-7; la cuenta recorrida contra él es bit a bit idéntica.
- `cuenta_papel.json` reproduce exacto desde una corrida fresca.

## Zonas ciegas

Z1 fuga por el analista (sólo el sellado en vivo la desmiente); Z2 fugas de ≤ 2 días por precios;
Z3 el congelado no es point-in-time ni lleva `available_at` por ticker; Z4 auditoría sobre árbol en
movimiento (re-verificado lo que cambió); Z5 `barrido_semillas` no pasa por el gate (verificado a
mano en un corte); Z6 liquidez, impacto, tarifas de terceros, impuestos.

## Exigencias

- **G1** declarar el alcance real del gate (aplicada: `verificar_invariancia.alcance` y reporte).
- **G2** barrido denso de cortes por regla, ≥ 20 (aplicada: una sesión de cada 30, 25 cortes).
- **G3** contraprueba de la fuga de 1 día por `precios_ref` en `test_dinero.py` (PENDIENTE, corrida 12).
- **G4** unificar la convención de caja comprometida y corregir la frase del reporte (aplicada).
- **G5** declarar la sonda larga por construcción con la medición (aplicada: 57,8 %, +2,20 pp).
- **G6** declarar la membresía como corte transversal fijo con dirección (aplicada).
- **G7** ampliar los cortes de `test_senal_larga.py` (aplicada: 2020-12-31 y 2022-12-30 agregados).
- **G8** sellar `available_at` por ticker en el `.meta.json` del congelado (PENDIENTE, corrida 12).
- **G9** declarar el segundo congelado en el reporte (aplicada).
- **G10** re-correr la suite con el árbol quieto y citar esa corrida (aplicada: número en la bitácora).
