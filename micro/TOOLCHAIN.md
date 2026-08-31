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
  `GEMELO/MICRO/SINTESIS.md` se publica marcado como tal.
- **Vivado.** Ni se intentó: requiere licencia, registro y decenas de GB.
  Fuera de alcance para una corrida sin root.
- **Programar una placa física.** No hay hardware conectado. Todo lo de este
  frente es simulación y síntesis; el paso 5 del protocolo de validación de
  `RTL.md` §4 (medición sobre placa real) sigue pendiente por falta de placa,
  no por falta de herramientas.

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
```

Los vectores se generan desde `senales.db` **abierta en modo `ro`**
(`referencia.py`). Nada de este árbol escribe una fila en ninguna base del
proyecto, y `referencia.py` **no importa `motor.py`** — reimplementa el álgebra
en float64 aislado, como exige `RTL.md` §4.2 y la Regla Cero del proyecto.
