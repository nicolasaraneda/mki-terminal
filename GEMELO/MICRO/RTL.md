# El pipeline RTL — diseño, no implementación

**Estado:** diseño. No hay una línea de RTL escrita todavía — este documento
se revisa antes de escribirla, como pide `GEMELO/MICRO/DISEÑO.md` §9.
**Fecha:** 31-ago-2026. **Insumos:** `GEMELO/MICRO/piso_de_latencia.md`
(veredicto: la lectura "captura en vivo" muere por 3-4 órdenes de magnitud;
la lectura "pipeline RTL académico, validado por backtest" sobrevive) y
`GEMELO/MICRO/fpga.md` (presupuesto de recursos por placa).

> **Regla cero de este documento:** ninguna cifra de LUTs, anchos de bit o
> tolerancia se ajustó para que el pipeline "quepa" en una placa en
> particular. Se mide qué exige el pipeline y se compara contra lo que hay
> — si no entra, el resultado es que no entra, no una cifra retocada.

Este es el proyecto que sobrevivió a `piso_de_latencia.md`: un pipeline de
decisión de trading intradía en RTL, validado por backtest, como proyecto
final de Arquitectura de Computadores. No pretende capturar una ventaja de
mercado en vivo — eso ya se descartó con evidencia medida. Es un
instrumento de arquitectura: demuestra que el hardware decide con latencia
determinística, algo que ningún sistema operativo de uso general puede
prometer (`GEMELO/MICRO/WSL2.md`: el piso de software es ~72-85 µs y
variable; el hardware, una vez sintetizado, es N ciclos de reloj, siempre
los mismos).

## 1. El pipeline, en etapas

```
┌──────────┐   ┌────────────┐   ┌──────────────┐   ┌───────────┐   ┌────────┐
│ INGESTA  │──▶│  ESTADO /  │──▶│   PUNTAJE    │──▶│ DECISIÓN  │──▶│ SALIDA │
│ (parser) │   │ FEATURES   │   │ (MAC)        │   │ (umbral)  │   │ + sello│
└──────────┘   └────────────┘   └──────────────┘   └───────────┘   └────────┘
```

1. **INGESTA** — deserializa el mensaje binario de mercado de formato fijo
   (mismo formato que `micro/src/bench_mensaje.c` ya definió y midió en
   software: 28 bytes, timestamp/id/precio/cantidad/lado/flags). En RTL:
   una máquina de estados que corre un byte (o un word, si el bus lo
   permite) por ciclo, deserializando campo por campo hacia registros de
   ancho fijo — nunca "castea" el buffer entero a una struct como el
   software puede permitirse; en hardware cada campo se ensambla
   explícitamente con selects de bits, que es la forma nativa de hacerlo,
   no un rodeo.
2. **ESTADO/FEATURES** — mantiene acumuladores rodantes de ancho fijo (ej.
   una ventana de N mensajes para una media o una volatilidad simple):
   un registro de desplazamiento de N entradas más una suma corrida
   (sumar el nuevo, restar el que sale — dos sumadores, no N).
3. **PUNTAJE** — la etapa que decide cuánto pipeline cabe: una combinación
   lineal (multiplicar-y-acumular, MAC) de F features por sus pesos
   pre-cargados. F=1 (comparación contra umbral, sin multiplicar) es
   prácticamente gratis. Cada F adicional agrega un multiplicador.
4. **DECISIÓN** — compara el puntaje contra un umbral (o dos, para
   BUY/HOLD/SELL) y emite la señal.
5. **SALIDA + SELLO** — la señal se latchea junto con un timestamp de un
   contador libre de ciclos (igual al principio de `fpga.md` §2): la
   latencia de decisión es, por diseño, el mismo número de ciclos siempre.

## 2. Presupuesto de recursos, medido por etapa

Estimado con reglas de la casa para síntesis en fábrica de LUTs de 4
entradas (iCE40) sin multiplicador dedicado, y contrastado contra Artix-7
con DSP48E1. Cifras de orden de magnitud, no un reporte de síntesis real —
eso solo lo da el sintetizador de cada placa, y es lo primero que hay que
correr en cuanto exista RTL.

| Etapa | LUTs (iCE40, sin DSP) | Flip-flops | BRAM | DSP (Artix-7) |
|---|---|---|---|---|
| Ingesta (parser 28 bytes) | ~100-150 | ~224 (el mensaje completo) | 0 (o 1 si se buffera >1 mensaje) | 0 |
| Estado/features (1 acumulador rodante, N=10) | ~50-100 | ~160 (registro de desplazamiento) | 0 | 0 |
| Puntaje, **F=1** (solo umbral, sin multiplicar) | ~20-30 | ~16 | 0 | 0 |
| Puntaje, **cada F adicional** (1 multiplicador 16×16 con signo) | **+200 a +300** | +16-32 | 0 | **+1** |
| Decisión (comparador doble, BUY/HOLD/SELL) | ~15-25 | ~8 | 0 | 0 |
| Salida (contador de 48 bits + UART 115200 baudios) | ~100-150 | ~60-80 | 0 (o 1 chica para buffer TX) | 0 |
| **Total, F=1 (solo umbral)** | **~300-450** | ~475 | 0 | 0 |
| **Total, F=3** (1 acumulador + 3 features ponderadas) | **~750-1.150** | ~570 | 0 | 3 |
| **Total, F≥6** (algo parecido al modelo real, 15-16 features causales de WS2a) | **~1.500-2.100+** | ~700+ | 0-1 | 6+ |

**Lectura del presupuesto, sin adornarla:**
- **F=1 cabe cómodo en el iCE40HX1K** (1.280 LUTs): deja 60-75% de margen.
- **F=3 se aprieta contra el techo del iCE40** (750-1.150 de 1.280 — entre
  59% y 90% de ocupación, sin margen para nada más si el sintetizador real
  usa el extremo alto de la estimación). Es viable, pero al límite.
- **F≥6 NO cabe en el iCE40HX1K** — la sola cuenta de multiplicadores
  (6 × 200-300 LUTs = 1.200-1.800 LUTs) ya excede o iguala el total
  disponible antes de contar ingesta, estado, decisión y salida. **Esto
  hay que saberlo ahora, no después de tres semanas de RTL** (la
  instrucción original, y sigue siendo la razón de ser de esta tabla).
- **En una Arty A7-100T** (63.400 LUTs, 240 DSP48E1), cualquiera de las
  tres filas es trivial — el DSP48E1 hace la multiplicación sin gastar un
  LUT, y F=6 usa 6 de los 240 disponibles (2.5%). La placa grande no
  discute esta pregunta, la vuelve irrelevante.

## 3. Aritmética: punto fijo, justificado por datos reales del proyecto

**Nunca se eligió un ancho de bits de memoria.** Se midió el rango real de
los datos que el pipeline manejaría, con `senales.db` en modo lectura:

| Cantidad | n medido | Rango real | Formato propuesto | Rango del formato | Resolución |
|---|---|---|---|---|---|
| `apertura_estimada_pct` (la predicción) | 279 | −5.02 a +6.91 | **Q8.8** (16 bits con signo, 8 fraccionarios, escala 1/256) | ±128.0 | 0.0039 |
| `gap_pct` (el resultado real, para validar) | 253 | −9.99 a +28.37 | mismo Q8.8 | ±128.0 | 0.0039 |
| `beta` | 181 | 0.05 a 1.01 | **Q2.14** (16 bits, 14 fraccionarios) | −2.0 a +1.9999 | 0.000061 |

**Pérdida de precisión medida, no estimada:** se tomaron las 279
predicciones reales selladas, se cuantizaron a Q8.8 y se reconstruyeron.
**Error absoluto máximo: 0.00188 pp. Error medio: 0.001 pp.** Contra el MAE
publicado del gap (2.98 pp), el error de cuantización es el **0.063% del
MAE** — dos órdenes de magnitud por debajo de cualquier cifra que el
proyecto reporta o decide sobre ella. **Ninguna de las 279 predicciones
cambió de signo al cuantizar.** Mismo resultado para `beta`: error máximo
0.0000293, sin ningún caso al límite de un umbral de decisión conocido.
**Conclusión: Q8.8/Q2.14 no mueve ninguna decisión que el proyecto ya haya
tomado con los mismos datos en punto flotante.** Reproducible: script en
`GEMELO/MICRO/` no versionado aún (queda para cuando exista RTL de verdad
contra el cual validar; el número de arriba ya está medido y no cambia).

## 4. Protocolo de validación por backtest

Esto es lo que separa "medición" de "demo", y es la parte del proyecto que
lo hace un ejercicio de arquitectura de computadores, no una maqueta:

1. **Vector de referencia**: tomar N mensajes de mercado sintéticos (el
   mismo generador de `micro/src/bench_mensaje.c`, semilla fija) o, mejor,
   una serialización de datos reales ya sellados (`senales_ticker`,
   `verificacion_apertura`) al formato binario de 28 bytes.
2. **Referencia en software**: correr el mismo cómputo (parseo + feature +
   puntaje + decisión) en Python/C de punto flotante, tomándolo como la
   verdad de referencia — NO `motor.py` en producción (eso violaría la
   Regla Cero de intocabilidad), sino una reimplementación aislada, fuera
   del árbol de producción, del mismo álgebra que el RTL va a sintetizar.
3. **Simulación RTL** (testbench en el simulador de la toolchain elegida:
   Icarus Verilog / Yosys+nextpnr para iCE40, o el simulador de Xilinx
   para Artix-7): alimentar el MISMO vector de mensajes, capturar la señal
   de decisión y el puntaje intermedio ciclo a ciclo.
4. **Comparación**: decisión RTL == decisión de referencia, para el 100%
   de los mensajes del vector (la decisión es discreta —
   BUY/HOLD/SELL— así que "bit a bit" y "dentro de tolerancia" coinciden
   acá: o es la misma decisión o no lo es). El puntaje intermedio (antes
   del umbral) sí tolera una diferencia — la que ya se midió en la §3
   (0.00188 pp máximo) — y esa tolerancia se declara ANTES de comparar,
   nunca se ajusta después de ver que algo no calza.
5. **En hardware real** (si se llega a sintetizar sobre una placa física):
   repetir el mismo vector, y agregar la medición de latencia determinista
   —el hallazgo que esta pista busca demostrar— con el mismo instrumento
   de medición externo que ya construyó `micro/` (o un contador interno de
   la propia FPGA, más preciso que cualquier reloj de host).

**Esto es la medición central del proyecto de la materia**: no "¿la
placa parpadea bonito?" sino "¿el RTL decide lo mismo que el software de
referencia, y en cuántos ciclos, siempre los mismos?".

## 5. Qué queda fuera del alcance del ramo

- **Entrenar o re-estimar `beta`, o cualquier coeficiente, en la FPGA.**
  Los pesos se calculan off-chip (en software, con los datos históricos) y
  se cargan a la FPGA como constantes o vía un registro de configuración.
  Nada de regresión rodante de 120 sesiones corriendo en hardware — eso es
  trabajo de investigación de otro proyecto, no de esta materia.
- **Conexión a un feed de mercado real o a un bróker.** Ya excluido por la
  Constitución 5.0 del proyecto MKI (sin dinero real, sin órdenes) y,
  independientemente, por el veredicto de `piso_de_latencia.md` — no hay
  ninguna ventaja que capturar en vivo con esta plataforma.
- **Optimizar el pipeline para mínima latencia de producción** (pipelining
  profundo, especulación, múltiples relojes). El proyecto de la materia
  demuestra que el hardware decide en un número FIJO y conocido de
  ciclos — no que ese número sea el mínimo posible. Eso sería trabajo
  posterior, con otro alcance y otro tiempo.
- **Portar el modelo completo de 15-16 features de GEMELO/WS2a.** La §2 ya
  mostró que eso no cabe en la placa del ramo. Si el pipeline crece más
  allá de F=3, es explícitamente Arty A7 o una versión simplificada — ver
  §6.

## 6. Decisiones de Nicolás, marcadas explícitamente

- **Qué placa** (Go Board / iCE40HX1K vs. Arty A7-100T). Esta sección no
  la resuelve, igual que `fpga.md` §5 tampoco la resolvió. La tabla de la
  §2 es el insumo para decidir informado.
- **Si el pipeline replica al modelo 4.6.0 (simplificado, F≤3) o una
  versión deliberadamente distinta, declarada como tal desde el inicio.**
  Replicar el 4.6.0 tiene la ventaja de un vector de validación ya
  existente (las filas selladas reales); una versión propia (ej. un
  indicador de momentum simple, sin pretensión de imitar a MKI) es
  igualmente válida para el ramo y evita cualquier confusión entre "esto
  es el proyecto de la materia" y "esto es producción de MKI" — son cosas
  distintas y esta línea las separa a propósito.
- **Cuánto pipeline construir sobre el iCE40 actual antes de justificar el
  gasto de una Arty A7** — ya marcado en `fpga.md` §5, se repite acá
  porque es la misma pregunta vista desde el diseño del pipeline en vez de
  desde el catálogo de la placa.
- **La tolerancia de la §4 (0.00188 pp) como criterio de aceptación
  formal del proyecto** — el número está medido; que sea EL criterio que
  la materia evalúa es una decisión de alcance académico, no técnica.
