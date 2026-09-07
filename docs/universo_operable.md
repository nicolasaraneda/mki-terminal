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
> Regenerado el 2026-09-07.

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

- Comisión: 0.005 USD por acción, mínimo
  1.00 USD por orden, tope 1.0 %
  del monto. Deslizamiento supuesto: 5.0 pb por lado.
- **SUPUESTO NO VERIFICADO.** No hay cuenta abierta, así que no hay
  tarifario que leer. Confirmarlo contra el arancel público del corredor
  que se abra es un ítem de firma (`GEMELO/resultados/espera_firma.md`).
- Consecuencia aritmética que ordena todo el mapa: **con mínimo de 1 USD y
  tope de 1 %, una orden de UNA acción de menos de 100 USD paga
  exactamente el 1 %.** La comisión no es un detalle a este tamaño de
  cuenta: es el primer obstáculo.
- Se asumen **acciones enteras**. Las fraccionarias dependen del corredor y
  no hay corredor.

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

**Frase con estatus evidencial (MEDIDO el 2026-09-04, sobre 36 instrumentos verificados):** de los 8 eslabones, **6 quedan representados, 2 sustituidos y 0 huecos**. Exigiendo además que el instrumento tenga liquidez verificada —que esta corrida NO verificó para los ADR de mostrador— pasan a ser **5 representados, 3 sustituidos y 0 huecos**.

«Representado» significa aquí *un instrumento dominante comprable con el
techo del presupuesto*, no *un instrumento listado*: un dominante que
cotiza pero cuya acción cuesta más de lo que hay no representa nada. La
regla se escribió antes de mirar los precios y está fijada en un test
(`tests/test_dinero.py::test_el_estado_de_un_eslabon_sigue_la_regla_escrita`).

### Lo que el presupuesto deja afuera

Instrumentos verificados cuya **acción sola cuesta más de 500 USD**:

- `SNDK` — SanDisk: 1,740.00 USD. Rol declarado: complemento.
- `ASML` — ASML Holding: 1,714.88 USD. Rol declarado: dominante.
- `MU` — Micron Technology: 1,016.59 USD. Rol declarado: dominante.
- `META` — Meta Platforms: 616.77 USD. Rol declarado: dominante.
- `SMH` — VanEck Semiconductor ETF: 567.01 USD. Rol declarado: sustituto.
- `SOXX` — iShares Semiconductor ETF: 519.86 USD. Rol declarado: sustituto.
- `MSFT` — Microsoft: 499.70 USD. Rol declarado: dominante.

## Eslabón por eslabón

### Materias primas y nodos maduros — **REPRESENTADO**

*Quién domina (CONTEXTO NO VERIFICADO):* Obleas de silicio y gases: Shin-Etsu y SUMCO (Tokio). Nodos maduros: UMC, GlobalFoundries, Tower.  
*Obstáculo:* Los proveedores de materia prima pura cotizan en Tokio o son privados; los nodos maduros sí tienen listado en EE.UU.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `UMC` | United Microelectronics (ADR) | ADR | dominante | 20.77 | sí | 24 | 1.00 % | 0.20 % |
| `GFS` | GlobalFoundries | accion | complemento | 45.21 | sí | 11 | 1.00 % | 0.20 % |
| `GSM` | Ferroglobe | accion | sustituto | 4.67 | sí | 106 | 1.00 % | 0.20 % |
| `TSEM` | Tower Semiconductor | accion | complemento | 222.34 | sí | 2 | 0.45 % | 0.22 % |

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
| `SHECY` | Shin-Etsu Chemical (ADR OTC) | ADR | dominante | 18.61 | sí | 26 | 1.00 % | 0.21 % |
| `ENTG` | Entegris | accion | sustituto | 138.74 | sí | 3 | 0.72 % | 0.24 % |
| `LIN` | Linde | accion | sustituto | 477.57 | sí | 1 | 0.21 % | 0.21 % |
| `MKSI` | MKS Instruments | accion | complemento | 260.31 | sí | 1 | 0.38 % | 0.38 % |

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
| `ASML` | ASML Holding | ADR | dominante | 1,714.88 | **no** | **0** | 0.06 % | — |
| `AMAT` | Applied Materials | accion | complemento | 454.71 | sí | 1 | 0.22 % | 0.22 % |
| `KLAC` | KLA Corporation | accion | complemento | 185.60 | sí | 2 | 0.54 % | 0.27 % |
| `LRCX` | Lam Research | accion | complemento | 307.65 | sí | 1 | 0.33 % | 0.33 % |
| `TER` | Teradyne | accion | complemento | 357.03 | sí | 1 | 0.28 % | 0.28 % |
| `TOELY` | Tokyo Electron (ADR OTC) | ADR | sustituto | 176.49 | sí | 2 | 0.57 % | 0.28 % |

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
| `TSM` | TSMC (ADR) | ADR | dominante | 428.91 | sí | 1 | 0.23 % | 0.23 % |
| `INTC` | Intel | accion | complemento | 95.80 | sí | 5 | 1.00 % | 0.21 % |

- `INTC`: Intel Foundry como segundo intento occidental.
- **`TSM` sustituye a 2330.TW, el listado principal en Taipéi.** El riel de medición usa 2330.TW y trata al ADR como DUPLICADO (universo.py, `duplicado_de`), justamente porque no son el mismo instrumento: distinto horario, distinta moneda, prima variable. Para comprar desde Chile con 500 dólares, el ADR es lo único disponible.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *TSMC (2330.TW)* — COTIZA FUERA DE EE.UU.. Listado principal en Taipéi; en EE.UU. sólo el ADR.

### Memoria — **SUSTITUIDO**

*Quién domina (CONTEXTO NO VERIFICADO):* Samsung, SK Hynix y Micron en DRAM; Samsung, SK Hynix, Kioxia y Micron en NAND.  
*Obstáculo:* De los cuatro, sólo Micron tiene listado principal en EE.UU. El eslabón queda representado por su tercer actor.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `MU` | Micron Technology | accion | dominante | 1,016.59 | **no** | **0** | 0.10 % | — |
| `SNDK` | SanDisk | accion | complemento | 1,740.00 | **no** | **0** | 0.06 % | — |
| `WDC` | Western Digital | accion | complemento | 467.46 | sí | 1 | 0.21 % | 0.21 % |

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
| `ASX` | ASE Technology (ADR) | ADR | dominante | 37.51 | sí | 13 | 1.00 % | 0.21 % |
| `AMKR` | Amkor Technology | accion | complemento | 47.77 | sí | 10 | 1.00 % | 0.21 % |

- **`ASX` sustituye a 3711.TW, el listado principal en Taipéi.** Mismas diferencias que cualquier ADR: horario, moneda, prima.

**Huecos declarados de este eslabón** (no se tapan con un sustituto):
- *JCET (600584.SS)* — COTIZA FUERA DE EE.UU.. Listado en Shanghái.

### Diseño de chips y software EDA — **REPRESENTADO**

*Quién domina (CONTEXTO NO VERIFICADO):* Diseño: NVIDIA, Broadcom, AMD, Qualcomm, Arm. EDA: Synopsys y Cadence (duopolio, con Siemens EDA tercero).  
*Obstáculo:* Es el eslabón mejor representado en EE.UU. de toda la cadena.

| Ticker | Instrumento | Forma | Rol | Cierre USD | 1 acción | 500 USD | Comisión 1 acción | Comisión al techo |
|---|---|---|---|---:|:---:|:---:|---:|---:|
| `CDNS` | Cadence Design Systems | accion | dominante | 292.70 | sí | 1 | 0.34 % | 0.34 % |
| `NVDA` | NVIDIA | accion | dominante | 230.36 | sí | 2 | 0.43 % | 0.22 % |
| `SNPS` | Synopsys | accion | dominante | 393.84 | sí | 1 | 0.25 % | 0.25 % |
| `AMD` | AMD | accion | complemento | 477.57 | sí | 1 | 0.21 % | 0.21 % |
| `ARM` | Arm Holdings (ADR) | ADR | complemento | 252.09 | sí | 1 | 0.40 % | 0.40 % |
| `AVGO` | Broadcom | accion | complemento | 357.90 | sí | 1 | 0.28 % | 0.28 % |
| `QCOM` | Qualcomm | accion | complemento | 168.74 | sí | 2 | 0.59 % | 0.30 % |
| `SMH` | VanEck Semiconductor ETF | ETF | sustituto | 567.01 | **no** | **0** | 0.18 % | — |
| `SOXX` | iShares Semiconductor ETF | ETF | sustituto | 519.86 | **no** | **0** | 0.19 % | — |
| `XSD` | SPDR S&P Semiconductor ETF | ETF | sustituto | 491.45 | sí | 1 | 0.20 % | 0.20 % |

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
| `GOOGL` | Alphabet | accion | dominante | 338.46 | sí | 1 | 0.30 % | 0.30 % |
| `META` | Meta Platforms | accion | dominante | 616.77 | **no** | **0** | 0.16 % | — |
| `MSFT` | Microsoft | accion | dominante | 499.70 | **no** | **0** | 0.20 % | — |
| `AMZN` | Amazon | accion | complemento | 258.51 | sí | 1 | 0.39 % | 0.39 % |
| `VRT` | Vertiv Holdings | accion | complemento | 280.53 | sí | 1 | 0.36 % | 0.36 % |

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

## Lo que este mapa NO resuelve

- **La liquidez de los ADR de mostrador** (`SHECY`, `TOELY`). Devuelven
  precio; el diferencial de compra-venta no se midió.
- **El arancel real.** Todo el costo de arriba es un supuesto declarado.
- **El tratamiento tributario** de dividendos de ADR para un residente
  chileno, que cambia el retorno neto y no es objeto de esta corrida.
- **Que comprar un eslabón sea buena idea.** Este documento dice qué se
  puede comprar, no qué conviene comprar. Lo segundo depende de una señal
  que el proyecto todavía no tiene.
