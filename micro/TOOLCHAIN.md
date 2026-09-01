# Toolchain de síntesis y simulación RTL — qué se instaló y cómo reproducirlo

**Fecha:** 31-ago-2026. **Máquina:** el PC (WSL2, Linux 6.18.33.2-microsoft-standard-WSL2, x86-64).
**Restricción de partida:** sin `sudo`. No hay autenticación interactiva
disponible, así que `apt-get install` está descartado de entrada. Todo lo que
está acá se instaló bajo `~/.local`, sin tocar nada del sistema.

## 1. Qué se instaló

**OSS CAD Suite** (YosysHQ), release `2026-08-31`, tarball portable
`oss-cad-suite-linux-x64-20260831.tgz`. Es la vía diseñada exactamente para
este caso: un árbol relocalizable con todo el flujo adentro, sin paquetes de
sistema y sin root. 465 MB comprimido, **2,5 GB descomprimido**, 153 binarios.

Versiones exactas, leídas de las herramientas instaladas:

| Herramienta | Versión reportada |
|---|---|
| `yosys` | Yosys 0.68+136 (git sha1 c30457480-dirty, Release, Clang 21.1.8) |
| `nextpnr-ice40` | nextpnr-0.11.1-18-gdec04b3b |
| `icepack` / `icetime` | icestorm, incluidos en el mismo release |
| `iverilog` | Icarus Verilog 14.0 (devel) (s20260301-391-g64f13540a-dirty) |
| `verilator` | 5.051 devel rev v5.050-294-gc81be029a (mod) |

Se usa **Icarus Verilog** para simular, no Verilator: el banco de pruebas es
Verilog puro con lógica de comparación en un `initial`, y Icarus lo corre sin
necesidad de un envoltorio en C++. Verilator quedó instalado y disponible por
si alguna vez hace falta velocidad, pero para 181 vectores no hace falta.

## 2. Cómo reproducirlo desde cero

```bash
mkdir -p ~/.local/opt && cd ~/.local/opt
curl -sL -o oss-cad-suite.tgz \
  https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2026-08-31/oss-cad-suite-linux-x64-20260831.tgz
tar xzf oss-cad-suite.tgz
export PATH="$HOME/.local/opt/oss-cad-suite/bin:$PATH"
yosys -V && nextpnr-ice40 --version && iverilog -V
```

No hace falta ejecutar el `environment` del suite: los binarios de `bin/` son
lanzadores que ya resuelven sus propias bibliotecas. **`micro/rtl/Makefile`
antepone esa ruta al `PATH` por su cuenta**, así que `make` funciona sin
exportar nada. Si `yosys` ya está en el `PATH` por otra vía, se usa ése.

Para fijar la versión en el release exacto (y no en "el último"), el URL de
arriba ya lleva el tag `2026-08-31` en vez de `latest`. Es a propósito: un
número de síntesis que no dice con qué versión de yosys salió no es
reproducible.

## 3. Qué NO se pudo instalar, y por qué

- **`nextpnr-xilinx`.** No viene en el OSS CAD Suite estándar. Verificado
  listando los `nextpnr-*` incluidos: `ice40`, `ecp5`, `machxo2`, `nexus`,
  `gowin`, `generic`, `himbaechel`. **Consecuencia concreta: para el
  Artix-7 no hay place & route, y por lo tanto no hay reporte de utilización
  real ni frecuencia máxima.** No se forzó (el encargo lo prohibía
  explícitamente y con razón: compilar `nextpnr-xilinx` exige además la base
  de datos de `prjxray`, que es una descarga y una compilación aparte).
  Lo que sí se hizo es correr `yosys synth_xilinx -family xc7`, que mapea a
  celdas Artix-7 REALES (`DSP48E1`, `LUT6`, `CARRY4`) y permite contarlas.
  Es más duro que una cuenta a mano y más blando que Vivado, y en
  `GEMELO/MICRO/SINTESIS.md` y `SINTESIS_A7.md` se publica marcado como tal.

### 3.1 Vivado — averiguado, no recordado (31-ago-2026)

La placa comprada es una **Digilent Arty A7-100T con XC7A100TCSG324-1**, así
que la pregunta dejó de ser hipotética. Se verificó contra fuentes de AMD
consultadas hoy, no de memoria — **los nombres de las ediciones cambiaron y lo
que "se sabía" ya no vale**:

- **"WebPACK" y "Standard Edition" están retirados.** Desde la release
  **2026.1**, Vivado pasó a un **modelo de tiers**: BASIC, CORE, PRO (anuales)
  y ENTERPRISE, GOLD (perpetuas).
- **El tier que cubre la XC7A100T es BASIC, y cuesta $0.** La tabla "Device
  Support by Tiers" de amd.com marca la fila **"7 Series"** con ✔ en BASIC
  (con la nota *"Includes Virtex 7 and Zynq 7000 devices"*), y la ficha del
  tier dice **"All 7 Series & low-end UltraScale / UltraScale+ devices —
  Cost: $0 — Annual License (requires free renewal)"**.
  **La XC7A100T está cubierta con holgura**: el tier gratis de hoy cubre MÁS
  que la vieja WebPACK, que dejaba afuera Virtex-7.
- **Diferencia con el modelo viejo que hay que tener presente:** BASIC **no es
  "sin licencia"**, es una licencia gratuita **con renovación anual**. Si
  caduca, *"active tool use will be suspended until renewal"*.
- **La última versión es 2026.1** (23-jun-2026). El instalador unificado web
  pesa poco; el SFD completo son **98,28 GB**, aunque una instalación limitada
  a 7-series es una fracción de eso.
- **Sistemas operativos:** UG973 "Supported Operating Systems" de 2026.1 lista
  Windows 10/11 y, en Linux, RHEL, SUSE, AlmaLinux, Rocky y **Ubuntu 22.04.x /
  24.04.x**; y declara explícitamente que *"All the AMD Vivado subscription
  tiers including the Basic tier support these operating systems"*. La tabla de
  tiers de amd.com concuerda: la fila **OS SUPPORT** marca **Windows ✔ y
  Linux ✔ en los cinco tiers**, BASIC incluido.
  **Discrepancia declarada:** en mayo-2026 circuló ampliamente —blogs y
  agregadores— que 2026.1 sacaba Linux del tier gratis. **Las dos fuentes
  primarias de AMD consultadas hoy dicen lo contrario.** No se pudo determinar
  si la noticia era errónea o si AMD revirtió; **queda como no resuelto**, y en
  cualquier caso el PC es Windows con WSL2 encima, así que hay salida por los
  dos lados.

**Por qué NO se instaló acá, y qué NO fue el bloqueo.** Se verificó antes de
declarar nada:

| Candidato a bloqueo | Estado real |
|---|---|
| Disco | **NO es el bloqueo** — `df -h /` da **946 GB libres** de 1007 GB |
| Memoria | **NO** — 31 GB de RAM, 24 hilos |
| `sudo` | **NO** — Vivado instala en `$HOME` sin root |
| Licencia | **NO** — BASIC cubre la XC7A100T y cuesta $0 |
| **Descarga** | **SÍ, ES EL BLOQUEO** |

Todos los enlaces de instalador de `xilinx.com/support/download.html`
apuntan a `https://account.amd.com/en/forms/downloads/xef.html?filename=...`
— **cuenta AMD con sesión iniciada más el formulario de control de
exportación** (XEF). Verificado siguiendo el enlace: `account.amd.com` no
responde a una descarga no autenticada.

**Crear esa cuenta y firmar una declaración de control de exportación es un
acto de identidad de Nicolás**, de la misma clase que pushear a GitHub, que la
Constitución 5.0 (5) ya reserva para él. No se hizo y no se debe hacer en su
nombre.

**Consecuencia, escrita sin suavizar:** todo lo que dependa de place & route
—**Fmax, utilización real de slices, cierre de temporización y bitstream**—
sigue **sin medir** y está marcado como tal en `GEMELO/MICRO/SINTESIS_A7.md` §5.

**Dos avisos para cuando se instale**, verificados hoy y anotados para que no
cuesten una tarde:

1. **Este WSL2 corre Ubuntu 26.04**, que **no** está en la lista de UG973
   (22.04.x / 24.04.x). Suele funcionar igual, pero es un riesgo declarado. La
   alternativa sin riesgo es instalar Vivado **del lado Windows**.
2. **Programar la placa desde WSL2 exige pasar el USB al kernel de Linux**
   (`usbipd-win`): el JTAG de la Arty entra por el FT2232HQ del micro-USB y
   WSL2 no ve dispositivos USB por sí solo. **Instalar Vivado del lado Windows
   evita este problema entero**, que es la razón principal para preferirlo.

### 3.2 Lo demás

- **Programar una placa física.** La placa **ya existe** (Arty A7-100T
  comprada) pero no hay bitstream, porque no hay Vivado. El paso 5 del
  protocolo de validación de `RTL.md` §4 sigue pendiente — ahora por falta de
  herramienta y de JTAG, ya no por falta de placa.

## 4. Nota sobre el formato del mensaje de 28 bytes

El formato de wire NO se tocó: sigue siendo exactamente el que definió y midió
`micro/src/bench_mensaje.c` — `ts_ns` u64, `id_instrumento` u32, `precio_fp`
i64, `cantidad` i32, `lado` u8, `flags` u8, `reservado` u16, little-endian, 28
bytes. El parser en RTL deserializa esas mismas posiciones.

Lo que sí cambia, y se declara acá para que no se descubra leyendo el código:
**en el vector de validación, `precio_fp` transporta cuatro features Q8.8
empaquetadas (16 bits cada una) y `cantidad` otras dos.** `cantidad[31:16]`
queda reservado para una séptima feature. Es una reinterpretación del payload,
no un formato nuevo: la etapa de ingesta hace los mismos selects de bits sobre
las mismas posiciones, así que su medición de área es fiel.

## 5. Cómo correr todo

```bash
cd micro/rtl
make            # vectores + simulación + costo del multiplicador + etapas + síntesis + placas
make simular    # solo el banco de pruebas contra las 181 filas selladas reales
make sintetizar # solo yosys + nextpnr-ice40 + icetime
make etapas     # área de cada etapa por separado, vs. la estimación de RTL.md §2
make placas     # LCs colocadas en iCE40 + celdas Artix-7
make multiplicador  # costo aislado de un multiplicador 16x16 en LUT4

# Estudio de la Arty A7-100T (GEMELO/MICRO/SINTESIS_A7.md):
make a7          # los cinco bloques: presupuesto, multiplicador por ancho,
                 # barrido de punto fijo, K tickers en paralelo, piezas del 4.6.0
make ancho       # ingesta de B bytes/ciclo: latencia MEDIDA y 181/181 bit a bit
make error-ancho # qué error de cuantización compra cada bit (solo Python, ro)

# Un bloque suelto de `make a7`:
python3 medir_a7.py presupuesto   # tambien: multiplicador anchos tickers faltante ingesta
```

Archivos nuevos de ese estudio, todos en `micro/rtl/`: `medir_a7.py`,
`medir_ancho_error.py`, `costo_a7.v` (divisor, raíz, momentos rodantes),
`multi_top.v` (K pipelines), `etapa_ingesta_ancha.v` + `pipeline_top_ancho.v`
+ `tb/tb_pipeline_ancho.v` (la variante de bus ancho).

**Los anchos de punto fijo de `mki_definiciones.vh` pasaron a estar guardados
con `ifndef`** para poder barrerlos con `-D`. **Los valores por defecto no
cambiaron** (Q8.8 / Q2.14), y se verificó que las cifras publicadas siguen
idénticas: F1 sigue dando **1.545 ICESTORM_LC** en iCE40, **222 LUT6 + 569 FF +
1 DSP48E1** en Artix-7 y **181/181** en simulación.

Los vectores se generan desde `senales.db` **abierta en modo `ro`**
(`referencia.py`). Nada de este árbol escribe una fila en ninguna base del
proyecto, y `referencia.py` **no importa `motor.py`** — reimplementa el álgebra
en float64 aislado, como exige `RTL.md` §4.2 y la Regla Cero del proyecto.
