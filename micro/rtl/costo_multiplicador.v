// costo_multiplicador.v — micro-medición aislada: ¿cuánto cuesta UN
// multiplicador con signo en la fábrica de LUT4 del iCE40, que no tiene
// multiplicador dedicado?
//
// POR QUÉ EXISTE: `GEMELO/MICRO/RTL.md` §2 estimó "+200 a +300 LUTs" por cada
// feature adicional, y `fpga.md` §3 habló de "un número de LUTs del orden de
// cientos". Toda la conclusión sobre si el pipeline cabe en la Go Board
// descansa en ese número. Medirlo dentro del pipeline completo lo mezcla con
// el ruteo y el resto de la lógica; medirlo solo lo aísla.
//
// Las cuatro variantes existen para descartar la explicación alternativa antes
// de acusar a la estimación. La sospecha razonable era que Verilog estuviera
// generando un multiplicador de 32x32 en vez de 16x16: en Verilog el ancho de
// los operandos lo determina el CONTEXTO de la asignación, así que
// `p[31:0] <= a[15:0] * b[15:0]` extiende ambos operandos a 32 bits antes de
// multiplicar, al menos en la letra del estándar. Las variantes de 8 bits y de
// resultado truncado permiten ver si el costo escala como W^2 (multiplicador
// honesto de 16x16) o como (2W)^2 (el desastre de 32x32).
//
// Resultado medido con yosys 0.68 + synth_ice40 (ver micro/TOOLCHAIN.md):
//   mul16x16_con_signo  -> 774 LUT4 + 28 CARRY
//   mul16x16_sin_signo  -> 679 LUT4 + 28 CARRY
//   mul16x16_truncado   -> 326 LUT4 + 12 CARRY
//   mul8x8_con_signo    -> 177 LUT4 + 11 CARRY
//
// Lectura: 177 x (16/8)^2 = 708, del mismo orden que 774. El costo escala como
// W^2, o sea que yosys SÍ construye un 16x16 y no un 32x32 — la estimación de
// la §2 no tiene esa excusa. El número real es 774, entre 2,6 y 3,9 veces la
// estimación de 200-300.

module mul16x16_con_signo (
    input  wire               clk,
    input  wire signed [15:0] a,
    input  wire signed [15:0] b,
    output reg  signed [31:0] p
);
    always @(posedge clk) p <= a * b;
endmodule

module mul16x16_sin_signo (
    input  wire        clk,
    input  wire [15:0] a,
    input  wire [15:0] b,
    output reg  [31:0] p
);
    always @(posedge clk) p <= a * b;
endmodule

// Resultado truncado a 16 bits: cota inferior de referencia. El sintetizador
// puede descartar la mitad alta de los productos parciales.
module mul16x16_truncado (
    input  wire               clk,
    input  wire signed [15:0] a,
    input  wire signed [15:0] b,
    output reg  signed [15:0] p
);
    always @(posedge clk) p <= a * b;
endmodule

module mul8x8_con_signo (
    input  wire              clk,
    input  wire signed [7:0] a,
    input  wire signed [7:0] b,
    output reg  signed [15:0] p
);
    always @(posedge clk) p <= a * b;
endmodule
