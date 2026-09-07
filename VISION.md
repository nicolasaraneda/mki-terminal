# VISION — qué persigue MKI Terminal

> **Estatus de este documento.** Es una declaración de INTENCIÓN y de
> arquitectura, no un informe de resultados. Cada cifra que aparece abajo se
> lee del árbitro (`cifras.py`, sobre filas selladas) o del pre-registro que
> la fijó, y lleva su intervalo. Ninguna frase de aquí afirma más de lo que
> la cifra que la sostiene permite. Escrito en la corrida 10 (6-sep-2026).

## 1. La intención

Construir una herramienta que reciba un presupuesto y tome decisiones de
compra y venta cada vez más afinadas sobre la cadena de semiconductores.

Eso es **lo que Nicolás quiere que el proyecto llegue a ser**, no lo que hoy
hace. Hoy el proyecto emite predicciones y se mide; no decide compras, no
mueve plata y no tiene demostrada ninguna ventaja distinguible de cero. La
distancia entre esa frase y el estado actual es el contenido del resto de
este documento.

## 2. Los dos rieles

El proyecto construyó un instrumento que mide **una noche**: el cierre de
Nueva York contra la apertura asiática, unas horas después. La intención de
arriba opera en **semanas**. Las dos cosas son legítimas y **no son la
misma**, así que desde la corrida 10 son dos rieles declarados y separados.

### 2.1 Riel de medición — el gap asiático sellado

- **Qué mide.** Si la apertura de Tokio, Taipéi y Seúl se puede anticipar
  desde el cierre del SOX, con la predicción emitida y sellada ANTES de la
  apertura que intenta predecir.
- **Horizonte.** Una noche.
- **Vara.** "Siempre al alza", evaluada sobre las mismas filas.
- **No mueve plata.** Su función es demostrar que el proyecto puede emitir
  antes del hecho y medirse sin engañarse.
- **Estado (árbitro `cifras.sellada()`, ventana sellada hasta el 28-ago,
  convención `excluir_cero`, deduplicado):** n = 238 sobre 34 días. Modelo
  67.6 % [61.5, 73.3]; base 58.0 % [51.6, 64.1]; **ventaja +9.7 pp con IC95
  de clúster de día [−7.2, +26.6] — el intervalo contiene el cero**
  (permutación por día p = 0.29). El McNemar de filas da p = 0.0455, pero
  las filas no son independientes: ICC 0.392, DEFF 3.55, n efectivo 67.
  Magnitud: MAE 2.5204 pp contra 2.9751 pp de predecir cero, ganancia
  +0.4547 pp con IC [−0.087, +0.996], **también contiene el cero**.
- **Qué lo mata.** Está pre-registrado y no se inventa aquí: las barreras
  V1–V7 y los rechazos R1–R3 de `GEMELO/DISEÑO.md` §6, fijados antes de
  cualquier resultado. La más dura ya golpeó al titular: **R2** —excluir la
  ventana 15–23 jul, que sostiene casi toda la ventaja— deja al campeón en
  n = 184, modelo 62.0 %, base 65.2 %, **ventaja −3.3 pp (p = 0.60)**: no
  pierde la ventaja, la vuelve negativa. Ese resultado está publicado y la
  valla no se bajó.

### 2.2 Riel de dinero — instrumentos de EE.UU. a semanas

- **Qué mide.** Si un movimiento en un eslabón de la cadena anticipa el de
  otro eslabón aguas abajo con retardo medible, y si actuar sobre eso supera
  a comprar un ETF del sector todas las semanas sin decidir nada.
- **Horizonte.** Semanas (20 y 60 días hábiles).
- **Vara.** La línea base aburrida: aporte fijo semanal a un ETF del sector,
  con los mismos costos.
- **Presupuesto.** 100 a 500 dólares, y **no hay cuenta de corredora
  abierta**. Por eso opera sobre instrumentos listados en Estados Unidos: los
  papeles que el riel de medición predice están en Tokio, Taipéi y Seúl, con
  lotes mínimos que ese presupuesto no alcanza. No es una concesión: es la
  única forma en que presupuesto y horizonte encajan.
- **Estado.** **No existe todavía.** La corrida 10 construyó su maquinaria:
  el mapa de eslabones a instrumentos comprables (`docs/universo_operable.md`),
  la capa que convierte señales en órdenes propuestas (`dinero/`), la cuenta
  en papel y su pre-registro (`dinero/preregistro_dinero.md`). **Todo
  SIMULADO.** Ninguna cifra suya es un resultado del proyecto todavía.
- **Qué lo mata.** El criterio numérico está en `dinero/preregistro_dinero.md`,
  escrito antes de mirar ningún resultado, y es lo que decide si se pasa de
  papel a plata real o si el riel se cierra.

## 3. La pista de hardware, y qué NO es

`GEMELO/MICRO/` y `micro/` son **plataforma de verificación y proyecto de
Arquitectura de Computadores**. No son un motor de backtesting ni una ruta a
microtrading, y decirlo importa porque la tentación existe.

La ruta de latencia está **medida y muerta desde casa**: el piso medido a un
endpoint público es p50 = 8.79 ms (p99 = 36.76 ms), contra los cientos de
nanosegundos de un cross-connect colocado — unos **cuatro órdenes de
magnitud**. Lo que desbloquearía esa ruta es **colocación**, no hardware:
ningún RTL, ninguna FPGA y ninguna optimización de software mueven una
latencia de red de milisegundos.

## 4. Legalidad

**Todas las entradas del sistema son datos públicos**: precios de cierre,
calendarios de bolsa, titulares de RSS. Cualquier diseño que dependa de
información no pública se rechaza, y se escribe por qué.

## 5. Qué NO es el proyecto

- **No es un vendedor.** No hay producto, no hay suscripción, no hay clientes.
- **No promete retorno.** La única ventaja medida tiene un intervalo que
  contiene el cero, y bajo R2 se vuelve negativa.
- **El primer monto de plata real es costo de aprendizaje operativo**, no una
  apuesta con retorno esperado positivo demostrado. Lo que se compra con esos
  100 a 500 dólares es saber cómo se abre una cuenta, cómo se cursa una
  orden, qué comisión se paga de verdad y cuánto se desliza el precio: cosas
  que en papel no se aprenden. No es una inversión con tesis.
- **No se opera con dinero real sin firma humana.** Ninguna función del
  proyecto envía órdenes a una corredora ni guarda credenciales de una.
- **Nada se publica solo.** El push a GitHub es un acto manual de Nicolás.
