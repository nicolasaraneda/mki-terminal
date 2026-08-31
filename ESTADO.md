# ESTADO

Resumen curado de dónde está el proyecto. Se regenera al cierre de cada sesión
con la skill `/cierre-sesion`. **Máximo 50 líneas.** No es historia: la historia
vive en `DECISIONES.md`. Las cifras publicadas viven en `README.md`.

**Actualizado:** 31-ago-2026 · verificar con el agente `orientador`

## Producción

- **Titular: este PC (Windows/WSL), en `main`.** Switch completo, 6 timers
  activos, emite. El Mac quedó fuera. Al modo se le **pregunta a `modo.py`**.
- **No hay réplica** (`docs/REPLICA.md`, nuevo, es diseño — nada implementado).
- Modelo 4.6.0 congelado, `PLATAFORMA_VERSION` 5.0.3 desde el 26-ago. Último
  sello: 2026-08-28 · N verificaciones: 253 (248 bajo `excluir_cero`).

## Errata pendiente de registrar

Actas 36/37 y docs del Proyecto dicen `MKI_MODO=sombra` puesto y segundo
movimiento pendiente. **Ya no es cierto** (30-ago, `modo.py` → `titular`).
Manda la máquina; se documenta como errata, no se corrige hacia atrás.

## Frente · GEMELO 6.0.0

- WS1-WS5 recorridos (WS2b negativo, WS5 REFUTADO). **31-ago:**
  `GEMELO/RELEVO.md` (protocolo de relevo, sin retador real hoy) y
  `GEMELO/MICRO/` (microtrading/latencia, comparte pregunta con el proyecto
  de Arquitectura de Computadores de Nicolás — la captura en vivo muere por
  3-4 órdenes de magnitud en la red, el pipeline RTL académico sobrevive).
- **Hallazgo (`dos_ventanas.md`):** toda la ventaja sellada (+6.5pp) vive en
  6 fechas de 15-23-jul; el resto (n=204) da -1.0pp.
- §34.9 (IC del ΔMAE): **resuelto, §38**, no cambia en los 12 pares WS2b+WS3.
- Ningún documento designa el siguiente paso EXPERIMENTAL. Decisión de Nicolás.

## Esperando decisión de Nicolás

1. Las cinco preguntas del WS4 (§33.8, 8 filas del 29-jul); si `.claude/`
   se versiona o queda local a esta máquina.
2. Placa FPGA (Go Board vs. Arty A7-100T) — `GEMELO/MICRO/fpga.md`.
3. Umbrales de `GEMELO/RELEVO.md` (margen 5pp, n≥150/60d) y si se activa una
   réplica permanente (`docs/REPLICA.md`, con qué máquina).
4. Expedientes 6B/6C (`GEMELO/resultados/expedientes.md`): visibilidad de
   `ts_emision`, estampida de `Persistent=true` (sin discusión previa),
   alcance del pin de pandas.

## Deudas y asimetrías declaradas

- `pd.concat`/`Pandas4Warning`: contenida por el pin (3 sitios, confirmado
  en vivo esta noche). Bloquea upgrade — expediente 6C con opciones.
- Intérprete: Mac 3.11.15, PC 3.14.4. Decisión: no igualar.
