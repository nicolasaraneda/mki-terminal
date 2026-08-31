// mki_definiciones.vh — anchos y constantes compartidas del pipeline.
//
// Por qué un header y no parámetros sueltos en cada módulo: los formatos de
// punto fijo (Q8.8 / Q2.14) están JUSTIFICADOS CON DATOS en
// GEMELO/MICRO/RTL.md §3 — se midió el rango real de 279 predicciones
// selladas antes de elegir el ancho. Si el ancho vive replicado en cinco
// archivos, tarde o temprano uno se cambia solo y la justificación deja de
// aplicar en silencio. Acá vive una vez.

`ifndef MKI_DEFINICIONES_VH
`define MKI_DEFINICIONES_VH

// Unidad de tiempo para simulación. Yosys la ignora; Icarus avisa si falta.
`timescale 1ns / 1ps

// --- Formato del mensaje de mercado (congelado por micro/src/bench_mensaje.c) ---
// 28 bytes, little-endian, campo a campo:
//   [ 0.. 7] ts_ns          u64
//   [ 8..11] id_instrumento u32
//   [12..19] precio_fp      i64
//   [20..23] cantidad       i32
//   [24]     lado           u8
//   [25]     flags          u8
//   [26..27] reservado      u16
`define MKI_BYTES_MSG 28

// --- Punto fijo ---
// Q8.8: 16 bits con signo, 8 fraccionarios. Rango ±128.0, resolución 0.0039.
// Elegido porque apertura_estimada_pct real vive en [-5.02, +6.91] y gap_pct
// en [-9.99, +28.37] — sobra un factor 4 de cabecera y el error de
// cuantización medido (0.00188 pp máx) es el 0.063% del MAE publicado.
`define MKI_ANCHO_FEATURE 16
`define MKI_FRAC_FEATURE  8

// Q2.14: 16 bits con signo, 14 fraccionarios. Rango [-2.0, +1.9999],
// resolución 0.000061. Los pesos del modelo (beta real en [0.05, 1.01])
// entran con margen; se privilegia resolución sobre rango porque un peso
// nunca llega a 2 en este modelo.
`define MKI_ANCHO_PESO 16
`define MKI_FRAC_PESO  14

// --- Códigos de decisión ---
// Se codifican en 2 bits en vez de one-hot: son mutuamente excluyentes por
// construcción (un puntaje no puede estar arriba y abajo del par de umbrales
// a la vez, y el testbench lo verifica), así que one-hot solo gastaría un
// flip-flop más sin comprar nada.
`define MKI_MANTENER 2'b00
`define MKI_VENTA    2'b01
`define MKI_COMPRA   2'b10

`endif
