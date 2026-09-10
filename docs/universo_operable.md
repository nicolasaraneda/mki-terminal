# Universo operable — qué eslabón se puede comprar de verdad

> **SIMULADO / PROPUESTA.** No hay cuenta de corredora abierta y este
> documento no es una recomendación de compra. Es el mapa del **riel de
> dinero** (ver `VISION.md`): qué eslabón de la cadena se puede comprar
> desde Chile con el presupuesto declarado, y cuál no.
>
> **Generado por `python -m dinero.mapa`, no escrito a mano.** Los precios
> salen de `dinero/datos/cierres_congelados.csv` (congelado
> 2026-09-07T01:47:34+00:00 UTC, sha256 `69ca7283ae18fd37…`,
> 2011 filas, 2018-09-05 a 2026-09-04).
> Regenerado el 2026-09-09.

## Las dos clases de afirmación de este documento

1. **VERIFICADO POR LA MÁQUINA** — que el ticker existe y devuelve precio.
   Ningún ticker de las tablas se escribió de memoria: entró sólo si la
   descarga trajo al menos un cierre. Los que no, están en la lista de no
   verificados con su razón.
2. **CONTEXTO NO VERIFICADO** — quién domina cada eslabón. Es conocimiento
   de fondo, no una medición de esta corrida, y va rotulado así en cada
   sección. Un lector no tiene por qué distinguirlo solo.

Una tercera cosa que este documento **no** afirma: que una orden se llene.
Un cierre demuestra que el instrumento cotiza, no que sea líquido.

## El supuesto de costo, a la vista

- Comisión: 0.0035 USD por acción, mínimo
  0.35 USD por orden, tope 1.0 %
  del monto. Deslizamiento supuesto: 5.0 pb por lado.
- **Arancel PUBLICADO, no supuesto** (desde el 8-sep-2026): es la columna de
  acciones enteras del insumo del §40 (`GEMELO/propuestas/insumo_40_aranceles_*.md`,
  Pro Tiered, consultado el 7-sep-2026). El insumo es PROPUESTA y espera firma;
  hasta el 7-sep esto era un supuesto sin verificar (0,005 / 1,00 USD / 1 %).
- Consecuencia aritmética que ordena el mapa: **con mínimo de 0.35 USD y
  tope de 1.0 %, el cruce está en 35 USD por orden**: por debajo
  manda el tope proporcional, por encima el mínimo fijo.
- Las tablas por eslabón asumen **acciones enteras** con el techo de reglas.json;
  el censo por presupuesto y modo de compra (más abajo) computa también
  fraccionarias.

## Resumen

- Presupuesto declarado: 100 a 500 USD.
- Instrumentos candidatos: 36. **Verificados: 36.** No verificados: 0.
- Instrumentos de los que alcanza para **una acción con 500 USD**: 29 de 36.
- Con el **piso** de 100 USD: 7 de 36.

| Eslabón | Estado | Exigiendo liquidez verificada |
|---|---|---|
| Materias primas y nodos maduros | **REPRESENTADO** | REPRESENTADO |
| Materiales químicos y obleas | **REPRESENTADO** | SUSTITUIDO |
| Litografía y equipamiento | **SUSTITUIDO** | SUSTITUIDO |
| Fabricación de vanguardia | **REPRESENTADO** | REPRESENTADO |
| Memoria | **SUSTITUIDO** | SUSTITUIDO |
| Ensamblaje y prueba (OSAT) | **REPRESENTADO** | REPRESENTADO |
| Diseño de chips y software EDA | **REPRESENTADO** | REPRESENTADO |
| Demanda final de IA y datacenter | **REPRESENTADO** | REPRESENTADO |

**Frase con estatus evidencial (MEDIDO el 2026-09-04, sobre 36 instrumentos verificados):** de los 8 eslabones, **6 quedan representados, 2 sustituidos y 0 huecos a 500 USD en acciones enteras** (censo de un solo día: a otros presupuestos el conteo es otro, ver la tabla por presupuesto). Exigiendo además que el instrumento tenga liquidez verificada —que esta corrida NO verificó para los ADR de mostrador— pasan a ser **5 representados, 3 sustituidos y 0 huecos a 500 USD en acciones enteras**.

«Representado» significa aquí *un instrumento dominante comprable con el
techo del presupuesto*, no *un instrumento listado*: un dominante que
cotiza pero cuya acción cuesta más de lo que hay no representa nada. La
regla se escribió antes de mirar los precios y está fijada en un test
(`tests/test_dinero.py::test_el_estado_de_un_eslabon_sigue_la_regla_escrita`).

### Lo que el presupuesto deja afuera

Instrumentos verificados que **no entran en 500 USD**. El
criterio es **precio más comisión**, no el precio solo: por eso hay
instrumentos acá cuyo precio está por debajo del techo.

- `SNDK` — SanDisk: 1,740.00 USD. Rol declarado: complemento.
- `ASML` — ASML Holding: 1,714.88 USD. Rol declarado: dominante.
- `MU` — Micron Technology: 1,016.59 USD. Rol declarado: dominante.
- `META` — Meta Platforms: 616.77 USD. Rol declarado: dominante.
- `SMH` — VanEck Semiconductor ETF: 567.01 USD. Rol declarado: sustituto.
- `SOXX` — iShares Semiconductor ETF: 519.86 USD. Rol declarado: sustituto.
- `MSFT` — Microsoft: 499.70 USD. Rol declarado: dominante. **Caso al borde:** su precio (499.70) está por DEBAJO del techo; lo que no entra es precio más comisión.

**El censo es de un solo día** (los cierres del congelado) y por eso
los casos al borde van declarados: a centavos del techo, la respuesta
cambia con el cierre siguiente. Los que no están al borde sí son
afirmaciones estables.

## Eslabón por eslabón

### Materias primas y nodos maduros — **REPRESENTADO**

*Quién domina (CONTEXTO NO VERIFICADO):* Obleas de silicio y gases: Shin-Etsu y SUMCO (Tokio). Nodos maduros: UMC, GlobalFoundries, Tower.  
*Obstáculo:* Los proveedores de materia prima pura cotizan en Tokio o son privados; los nodos maduros sí tienen listado en EE.UU.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `UMC` | United Microelectronics (ADR) | ADR | dominante | 20.77 | sí | 24 | 1.00 % | 0.07 % |
| `GFS` | GlobalFoundries | accion | complemento | 45.21 | sí | 11 | 0.77 % | 0.07 % |
| `GSM` | Ferroglobe | accion | sustituto | 4.67 | sí | 106 | 1.00 % | 0.07 % |
| `TSEM` | Tower Semiconductor | accion | complemento | 222.34 | sí | 2 | 0.16 % | 0.08 % |

- `GFS`: Nodos maduros, listado en EE.UU.
- **`GSM` sustituye a los productores de silicio metálico y cuarzo de grado semiconductor, casi todos privados (Sibelco, Quartz Corp).** Ferroglobe vende silicio metálico y ferroaleaciones a muchos sectores; el semiconductor es una fracción menor de su demanda. Comprarlo no es comprar la materia prima del chip.
- `TSEM`: Nodos maduros y especialidad.
- **`UMC` sustituye a 2303.TW, el listado principal en Taipéi.** Un ADR no es la acción: cotiza en el horario de Nueva York, trae riesgo de tipo de cambio TWD/USD y su precio puede separarse del local por prima o descuento.
- `UMC`: Es el par de 2330.TW en PARES_COMPETIDORES del riel de medición, así que el proyecto ya lo observa.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *Sibelco, The Quartz Corp (cuarzo de alta pureza)* — PRIVADAS. No cotizan en ninguna bolsa. Se le compra, en su lugar, a productores diversificados de silicio metálico.

### Materiales químicos y obleas — **REPRESENTADO · SUSTITUIDO exigiendo liquidez**

*Quién domina (CONTEXTO NO VERIFICADO):* Shin-Etsu y SUMCO en obleas; JSR y Tokyo Ohka en fotorresinas; Entegris y MKS en materiales y subsistemas.  
*Obstáculo:* El grueso del eslabón cotiza en Tokio. Lo listado en EE.UU. es la capa de materiales de proceso, no la oblea.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `SHECY` | Shin-Etsu Chemical (ADR OTC) | ADR | dominante | 18.61 | sí | 26 | 1.00 % | 0.07 % |
| `ENTG` | Entegris | accion | sustituto | 138.74 | sí | 3 | 0.25 % | 0.08 % |
| `LIN` | Linde | accion | sustituto | 477.57 | sí | 1 | 0.07 % | 0.07 % |
| `MKSI` | MKS Instruments | accion | complemento | 260.31 | sí | 1 | 0.13 % | 0.13 % |

- **`ENTG` sustituye a Shin-Etsu (4063.T) y SUMCO (3436.T), los dos fabricantes de obleas de silicio.** Entegris vende materiales de proceso, filtración y manejo de obleas: es proveedor de la fábrica, no fabricante de la oblea. La correlación es de sector, no de producto.
- **`LIN` sustituye a los gases de proceso de grado electrónico.** Linde es un gigante de gases industriales diversificado; el electrónico es una línea, no la empresa.
- `MKSI`: Subsistemas de vacío, láser y control de proceso.
- **`SHECY` sustituye a 4063.T, el listado principal en Tokio.** ADR de mostrador (OTC), no listado en bolsa: liquidez baja y diferencial de compra-venta ancho. Verificar antes de creerle.
- **`SHECY`: liquidez NO verificada.** Esta corrida comprobó que devuelve precio, nada más. Que una orden se llene a un diferencial razonable no se puede afirmar desde un cierre.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *Shin-Etsu Chemical (4063.T), SUMCO (3436.T)* — COTIZAN FUERA DE EE.UU.. Listado principal en Tokio. Sólo hay ADR de mostrador.

### Litografía y equipamiento — **SUSTITUIDO**

*Quién domina (CONTEXTO NO VERIFICADO):* ASML en litografía EUV (monopolio de facto); Applied Materials, Lam Research, KLA y Tokyo Electron en el resto del equipo.  
*Obstáculo:* ASML y varios pares tienen listado o ADR en EE.UU.; Tokyo Electron no tiene listado principal en EE.UU.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `ASML` | ASML Holding | ADR | dominante | 1,714.88 | **no** | **0** | 0.02 % | — |
| `AMAT` | Applied Materials | accion | complemento | 454.71 | sí | 1 | 0.08 % | 0.08 % |
| `KLAC` | KLA Corporation | accion | complemento | 185.60 | sí | 2 | 0.19 % | 0.09 % |
| `LRCX` | Lam Research | accion | complemento | 307.65 | sí | 1 | 0.11 % | 0.11 % |
| `TER` | Teradyne | accion | complemento | 357.03 | sí | 1 | 0.10 % | 0.10 % |
| `TOELY` | Tokyo Electron (ADR OTC) | ADR | sustituto | 176.49 | sí | 2 | 0.20 % | 0.10 % |

- **`ASML` sustituye a ASML.AS, el listado principal en Ámsterdam.** El ADR de ASML es de nivel III y cotiza en Nasdaq con liquidez propia; la diferencia con el original es horario y moneda, no profundidad.
- `TER`: Equipo de prueba.
- **`TOELY` sustituye a 8035.T, el listado principal en Tokio.** ADR de mostrador: liquidez baja. Verificar.
- **`TOELY`: liquidez NO verificada.** Esta corrida comprobó que devuelve precio, nada más. Que una orden se llene a un diferencial razonable no se puede afirmar desde un cierre.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *Tokyo Electron (8035.T)* — COTIZA FUERA DE EE.UU.. Listado principal en Tokio.

### Fabricación de vanguardia — **REPRESENTADO**

*Quién domina (CONTEXTO NO VERIFICADO):* TSMC. Samsung Foundry e Intel Foundry como segundos.  
*Obstáculo:* TSMC cotiza en Taipéi; en EE.UU. sólo hay ADR. Samsung no tiene listado principal en EE.UU.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `TSM` | TSMC (ADR) | ADR | dominante | 428.91 | sí | 1 | 0.08 % | 0.08 % |
| `INTC` | Intel | accion | complemento | 95.80 | sí | 5 | 0.37 % | 0.07 % |

- `INTC`: Intel Foundry como segundo intento occidental.
- **`TSM` sustituye a 2330.TW, el listado principal en Taipéi.** El riel de medición usa 2330.TW y trata al ADR como DUPLICADO (universo.py, `duplicado_de`), justamente porque no son el mismo instrumento: distinto horario, distinta moneda, prima variable. Para comprar desde Chile con 500 dólares, el ADR es lo único disponible.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *TSMC (2330.TW)* — COTIZA FUERA DE EE.UU.. Listado principal en Taipéi; en EE.UU. sólo el ADR.

### Memoria — **SUSTITUIDO**

*Quién domina (CONTEXTO NO VERIFICADO):* Samsung, SK Hynix y Micron en DRAM; Samsung, SK Hynix, Kioxia y Micron en NAND.  
*Obstáculo:* De los cuatro, sólo Micron tiene listado principal en EE.UU. El eslabón queda representado por su tercer actor.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `MU` | Micron Technology | accion | dominante | 1,016.59 | **no** | **0** | 0.03 % | — |
| `SNDK` | SanDisk | accion | complemento | 1,740.00 | **no** | **0** | 0.02 % | — |
| `WDC` | Western Digital | accion | complemento | 467.46 | sí | 1 | 0.07 % | 0.07 % |

- `MU`: Tercero mundial en DRAM; el único de los grandes con listado principal en EE.UU.
- `SNDK`: NAND, escindida de Western Digital. Verificar: si el ticker no responde, no entra.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *Samsung Electronics (005930.KS), SK Hynix (000660.KS)* — COTIZAN FUERA DE EE.UU.. Listado principal en Seúl. Samsung tiene ADR de mostrador poco líquido; SK Hynix no tiene ADR utilizable.
- *Kioxia* — COTIZA FUERA DE EE.UU.. Listado en Tokio desde 2024.

### Ensamblaje y prueba (OSAT) — **REPRESENTADO**

*Quién domina (CONTEXTO NO VERIFICADO):* ASE Technology, Amkor, JCET y las casas de empaquetado avanzado; parte del empaquetado avanzado lo hace la propia fundición.  
*Obstáculo:* ASE tiene ADR y Amkor cotiza en EE.UU.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `ASX` | ASE Technology (ADR) | ADR | dominante | 37.51 | sí | 13 | 0.93 % | 0.07 % |
| `AMKR` | Amkor Technology | accion | complemento | 47.77 | sí | 10 | 0.73 % | 0.07 % |

- **`ASX` sustituye a 3711.TW, el listado principal en Taipéi.** Mismas diferencias que cualquier ADR: horario, moneda, prima.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *JCET (600584.SS)* — COTIZA FUERA DE EE.UU.. Listado en Shanghái.

### Diseño de chips y software EDA — **REPRESENTADO**

*Quién domina (CONTEXTO NO VERIFICADO):* Diseño: NVIDIA, Broadcom, AMD, Qualcomm, Arm. EDA: Synopsys y Cadence (duopolio, con Siemens EDA tercero).  
*Obstáculo:* Es el eslabón mejor representado en EE.UU. de toda la cadena.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `CDNS` | Cadence Design Systems | accion | dominante | 292.70 | sí | 1 | 0.12 % | 0.12 % |
| `NVDA` | NVIDIA | accion | dominante | 230.36 | sí | 2 | 0.15 % | 0.08 % |
| `SNPS` | Synopsys | accion | dominante | 393.84 | sí | 1 | 0.09 % | 0.09 % |
| `AMD` | AMD | accion | complemento | 477.57 | sí | 1 | 0.07 % | 0.07 % |
| `ARM` | Arm Holdings (ADR) | ADR | complemento | 252.09 | sí | 1 | 0.14 % | 0.14 % |
| `AVGO` | Broadcom | accion | complemento | 357.90 | sí | 1 | 0.10 % | 0.10 % |
| `QCOM` | Qualcomm | accion | complemento | 168.74 | sí | 2 | 0.21 % | 0.10 % |
| `SMH` | VanEck Semiconductor ETF | ETF | sustituto | 567.01 | **no** | **0** | 0.06 % | — |
| `SOXX` | iShares Semiconductor ETF | ETF | sustituto | 519.86 | **no** | **0** | 0.07 % | — |
| `XSD` | SPDR S&P Semiconductor ETF | ETF | sustituto | 491.45 | sí | 1 | 0.07 % | 0.07 % |

- **`ARM` sustituye a ARM.L / la matriz SoftBank.** El ADR de Arm es el vehículo listado tras la salida a bolsa de 2023; SoftBank retiene la mayoría.
- `CDNS`: La otra mitad.
- **`SMH` sustituye a la cadena entera.** Una cesta no es un eslabón: pondera por capitalización y queda dominada por diseño y fabricación. Comprarla es comprar el sector, que es justo lo contrario de apostar a un eslabón contra otro.
- `SMH`: Es el BENCHMARK del riel de medición (universo.py).
- `SNPS`: Mitad del duopolio de EDA.
- **`SOXX` sustituye a la cadena entera.** Mismo reparo que SMH.
- **`XSD` sustituye a la cadena entera.** Ponderación igualitaria en vez de por capitalización: menos dominado por los tres grandes, más expuesto a los chicos.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *Siemens EDA* — SEGMENTO DE UN CONGLOMERADO. No cotiza por separado: es una división de Siemens AG.

### Demanda final de IA y datacenter — **REPRESENTADO**

*Quién domina (CONTEXTO NO VERIFICADO):* Microsoft, Google, Meta y Amazon como compradores; Vertiv, Equinix y Digital Realty en la infraestructura física.  
*Obstáculo:* Todos listados en EE.UU.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `GOOGL` | Alphabet | accion | dominante | 338.46 | sí | 1 | 0.10 % | 0.10 % |
| `META` | Meta Platforms | accion | dominante | 616.77 | **no** | **0** | 0.06 % | — |
| `MSFT` | Microsoft | accion | dominante | 499.70 | **no** | **0** | 0.07 % | — |
| `AMZN` | Amazon | accion | complemento | 258.51 | sí | 1 | 0.14 % | 0.14 % |
| `VRT` | Vertiv Holdings | accion | complemento | 280.53 | sí | 1 | 0.12 % | 0.12 % |

- `GOOGL`: Nivel 4 del riel de medición.
- `META`: Nivel 4 del riel de medición.
- `MSFT`: Nivel 4 del riel de medición.
- `VRT`: Energía y refrigeración de datacenter.

## Dominantes que no se pueden comprar

La empresa privada no es comprable, y la que cotiza sólo fuera de Estados
Unidos tampoco lo es con este presupuesto y esta cuenta. Se declara a quién
se le compra en su lugar, y en qué se diferencia.

| Eslabón | Quién domina | Por qué no se compra | A quién se le compra en su lugar |
|---|---|---|---|
| Materias primas y nodos maduros | Sibelco, The Quartz Corp (cuarzo de alta pureza) | PRIVADAS: No cotizan en ninguna bolsa. Se le compra, en su lugar, a productores diversificados de silicio metálico. | `UMC`, `GFS`, `TSEM`, `GSM` |
| Materiales químicos y obleas | Shin-Etsu Chemical (4063.T), SUMCO (3436.T) | COTIZAN FUERA DE EE.UU.: Listado principal en Tokio. Sólo hay ADR de mostrador. | `ENTG`, `MKSI`, `LIN`, `SHECY` |
| Litografía y equipamiento | Tokyo Electron (8035.T) | COTIZA FUERA DE EE.UU.: Listado principal en Tokio. | `AMAT`, `LRCX`, `KLAC`, `TER`, `TOELY` |
| Fabricación de vanguardia | TSMC (2330.TW) | COTIZA FUERA DE EE.UU.: Listado principal en Taipéi; en EE.UU. sólo el ADR. | `TSM`, `INTC` |
| Memoria | Samsung Electronics (005930.KS), SK Hynix (000660.KS) | COTIZAN FUERA DE EE.UU.: Listado principal en Seúl. Samsung tiene ADR de mostrador poco líquido; SK Hynix no tiene ADR utilizable. | `WDC` |
| Memoria | Kioxia | COTIZA FUERA DE EE.UU.: Listado en Tokio desde 2024. | `WDC` |
| Ensamblaje y prueba (OSAT) | JCET (600584.SS) | COTIZA FUERA DE EE.UU.: Listado en Shanghái. | `ASX`, `AMKR` |
| Diseño de chips y software EDA | Siemens EDA | SEGMENTO DE UN CONGLOMERADO: No cotiza por separado: es una división de Siemens AG. | `NVDA`, `AVGO`, `AMD`, `QCOM`, `ARM`, `SNPS`, `CDNS`, `XSD` |

## No verificados

**Ninguno.** Los 36 candidatos devolvieron al menos un cierre.

## Censo por presupuesto y modo de compra (corrida 11, bloque 10)

El presupuesto del riel quedó sin decidir porque el censo original se computó
con piso de 100 USD y acciones enteras (§82.7). Acá el modo de compra y el
presupuesto son **parámetros explícitos** y el censo se produce para los
cuatro montos en discusión. Arancel del insumo §40: enteras 0.0035 USD/acción, mínimo 0.35 USD, tope 1.0 %; fraccionarias 1.0 % del monto, mínimo 0.01 USD.
«Alcanzable» = con ese presupuesto entra al menos una unidad, comisión incluida.
Con fraccionarias todo instrumento con precio es alcanzable por construcción:
lo que separa los modos no es el alcance sino la **fricción**.

| Presupuesto | Modo | Alcanzables | Representados / sustituidos / huecos | Exigiendo liquidez | Casos al borde (enteras) |
|---:|---|---:|---|---|---|
| 100 USD | enteras | **7 de 36** | 3 / 1 / 4 | 2 / 1 / 5 | — |
| 100 USD | fraccionarias | **36 de 36** | 8 / 0 / 0 | 7 / 1 / 0 | — |
| 250 USD | enteras | **13 de 36** | 4 / 2 / 2 | 3 / 3 / 2 | — |
| 250 USD | fraccionarias | **36 de 36** | 8 / 0 / 0 | 7 / 1 / 0 | — |
| 500 USD | enteras | **29 de 36** | 6 / 2 / 0 | 5 / 3 / 0 | `MSFT` |
| 500 USD | fraccionarias | **36 de 36** | 8 / 0 / 0 | 7 / 1 / 0 | — |
| 1000 USD | enteras | **33 de 36** | 6 / 2 / 0 | 5 / 3 / 0 | — |
| 1000 USD | fraccionarias | **36 de 36** | 8 / 0 / 0 | 7 / 1 / 0 | — |

### Fricción de ida y vuelta por instrumento

Comisión de compra más comisión de venta, sin deslizamiento, para una posición
que usa el presupuesto entero en ese instrumento. Enteras: «unidades (fricción %)».
Fraccionarias: la fricción es la misma a cualquier presupuesto y se muestra una vez.

| Ticker | Cierre USD | 100 USD enteras | 250 USD enteras | 500 USD enteras | 1000 USD enteras | fraccionarias |
|---|---:|---:|---:|---:|---:|---:|
| `AMAT` | 454.71 | **0** | **0** | 1 (0.15 %) | 2 (0.08 %) | 2.00 % |
| `AMD` | 477.57 | **0** | **0** | 1 (0.15 %) | 2 (0.07 %) | 2.00 % |
| `AMKR` | 47.77 | 2 (0.73 %) | 5 (0.29 %) | 10 (0.15 %) | 20 (0.07 %) | 2.00 % |
| `AMZN` | 258.51 | **0** | **0** | 1 (0.27 %) | 3 (0.09 %) | 2.00 % |
| `ARM` | 252.09 | **0** | **0** | 1 (0.28 %) | 3 (0.09 %) | 2.00 % |
| `ASML` | 1,714.88 | **0** | **0** | **0** | **0** | 2.00 % |
| `ASX` | 37.51 | 2 (0.93 %) | 6 (0.31 %) | 13 (0.14 %) | 26 (0.07 %) | 2.00 % |
| `AVGO` | 357.90 | **0** | **0** | 1 (0.20 %) | 2 (0.10 %) | 2.00 % |
| `CDNS` | 292.70 | **0** | **0** | 1 (0.24 %) | 3 (0.08 %) | 2.00 % |
| `ENTG` | 138.74 | **0** | 1 (0.50 %) | 3 (0.17 %) | 7 (0.07 %) | 2.00 % |
| `GFS` | 45.21 | 2 (0.77 %) | 5 (0.31 %) | 11 (0.14 %) | 22 (0.07 %) | 2.00 % |
| `GOOGL` | 338.46 | **0** | **0** | 1 (0.21 %) | 2 (0.10 %) | 2.00 % |
| `GSM` | 4.67 | 21 (0.71 %) | 53 (0.28 %) | 106 (0.15 %) | 213 (0.15 %) | 2.00 % |
| `INTC` | 95.80 | 1 (0.73 %) | 2 (0.37 %) | 5 (0.15 %) | 10 (0.07 %) | 2.00 % |
| `KLAC` | 185.60 | **0** | 1 (0.38 %) | 2 (0.19 %) | 5 (0.08 %) | 2.00 % |
| `LIN` | 477.57 | **0** | **0** | 1 (0.15 %) | 2 (0.07 %) | 2.00 % |
| `LRCX` | 307.65 | **0** | **0** | 1 (0.23 %) | 3 (0.08 %) | 2.00 % |
| `META` | 616.77 | **0** | **0** | **0** | 1 (0.11 %) | 2.00 % |
| `MKSI` | 260.31 | **0** | **0** | 1 (0.27 %) | 3 (0.09 %) | 2.00 % |
| `MSFT` | 499.70 | **0** | **0** | **0** | 2 (0.07 %) | 2.00 % |
| `MU` | 1,016.59 | **0** | **0** | **0** | **0** | 2.00 % |
| `NVDA` | 230.36 | **0** | 1 (0.30 %) | 2 (0.15 %) | 4 (0.08 %) | 2.00 % |
| `QCOM` | 168.74 | **0** | 1 (0.41 %) | 2 (0.21 %) | 5 (0.08 %) | 2.00 % |
| `SHECY` | 18.61 | 5 (0.75 %) | 13 (0.29 %) | 26 (0.14 %) | 53 (0.07 %) | 2.00 % |
| `SMH` | 567.01 | **0** | **0** | **0** | 1 (0.12 %) | 2.00 % |
| `SNDK` | 1,740.00 | **0** | **0** | **0** | **0** | 2.00 % |
| `SNPS` | 393.84 | **0** | **0** | 1 (0.18 %) | 2 (0.09 %) | 2.00 % |
| `SOXX` | 519.86 | **0** | **0** | **0** | 1 (0.13 %) | 2.00 % |
| `TER` | 357.03 | **0** | **0** | 1 (0.20 %) | 2 (0.10 %) | 2.00 % |
| `TOELY` | 176.49 | **0** | 1 (0.40 %) | 2 (0.20 %) | 5 (0.08 %) | 2.00 % |
| `TSEM` | 222.34 | **0** | 1 (0.31 %) | 2 (0.16 %) | 4 (0.08 %) | 2.00 % |
| `TSM` | 428.91 | **0** | **0** | 1 (0.16 %) | 2 (0.08 %) | 2.00 % |
| `UMC` | 20.77 | 4 (0.84 %) | 12 (0.28 %) | 24 (0.14 %) | 48 (0.07 %) | 2.00 % |
| `VRT` | 280.53 | **0** | **0** | 1 (0.25 %) | 3 (0.08 %) | 2.00 % |
| `WDC` | 467.46 | **0** | **0** | 1 (0.15 %) | 2 (0.07 %) | 2.00 % |
| `XSD` | 491.45 | **0** | **0** | 1 (0.14 %) | 2 (0.07 %) | 2.00 % |

**Lectura, y lo que no se puede leer.** La fricción de enteras es un peaje fijo
(0,70 USD de ida y vuelta mientras la orden tenga menos de 100 acciones) y se
diluye con el tamaño; la de fraccionarias es proporcional y no se diluye. El
cruce está en 35 USD por orden (§40 §6). Esto es aritmética del arancel, no una
medición: las tarifas de terceros y de bolsa por venue no están, y la liquidez de
los ADR de mostrador sigue sin verificar. **La decisión del presupuesto se toma
con esta tabla a la vista y es de Nicolás**; este documento no la recomienda.

## El segundo congelado no aportó sesión: el censo sigue siendo de un solo día

**Los dos congelados terminan en la MISMA sesión (2026-09-04): el segundo
congelado no aporta una sesión nueva y esto NO cuenta como segundo día de censo.**
Se deja registrado con su fecha y su sha256 para que la comparación se pueda
repetir cuando exista una sesión posterior; hasta entonces el censo sigue siendo
de un solo día.

Día 1: congelado 2026-09-07T01:47:34+00:00 UTC, hasta 2026-09-04, sha256 `69ca7283ae18fd37…`. Día 2: congelado 2026-09-08T04:21:27+00:00 UTC, hasta 2026-09-04, sha256 `4222c8ecd0607497…`. **La comparación entre los dos días es el dato, no el segundo día solo.**

La comparación entre los dos congelados es **trivialmente idéntica** (misma sesión final) y
no verifica estabilidad de nada; se deja el sha256 para repetirla cuando exista una sesión
posterior.

## Lo que este mapa NO resuelve

- **La liquidez de los ADR de mostrador** (`SHECY`, `TOELY`). Devuelven
  precio; el diferencial de compra-venta no se midió.
- **El arancel real, medido en una cuenta.** El costo de arriba es el arancel
  PUBLICADO del insumo §40, no el observado en una orden real: faltan tarifas de
  terceros y de bolsa por venue, y el insumo espera firma.
- **El tratamiento tributario** de dividendos de ADR para un residente
  chileno, que cambia el retorno neto y no es objeto de esta corrida.
- **Que comprar un eslabón sea buena idea.** Este documento dice qué se
  puede comprar, no qué conviene comprar. Lo segundo depende de una señal
  que el proyecto todavía no tiene.
