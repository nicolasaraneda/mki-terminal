`include "mki_definiciones.vh"

// demo_top.v — el sistema completo AUTÓNOMO: fuente interna + pipeline.
//
// Un solo pulso de `arrancar` y el chip reproduce las 181 filas selladas desde
// su propia memoria, las hace pasar por el pipeline y emite 181 sellos. No hay
// UART de entrada, no hay banco de pruebas alimentando bytes, no hay DDR3L y
// no hace falta ni un pin de datos: es la arquitectura que `SINTESIS_A7.md`
// §3.2 y §4.1 describen como la de la demo del ramo, y que §8 anotaba como no
// escrita.
//
// El bus ancho vive ENTERO adentro del chip, que es la única forma de que B=28
// (5 ciclos de latencia) sea realizable: 28 bytes en paralelo son 224 pines y
// la placa expone 32 señales por los Pmod.

`ifndef CFG_B
  `define CFG_B 4
`endif
`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif
`ifndef CFG_NMSG
  `define CFG_NMSG 181
`endif
`ifndef CFG_ARCHIVO_MSG
  `define CFG_ARCHIVO_MSG "vectores/mensajes_b4.hex"
`endif
`ifndef CFG_HUECO
  `define CFG_HUECO 8
`endif

module demo_top #(
    parameter integer B     = `CFG_B,
    parameter integer N_MSG = `CFG_NMSG,
    parameter integer HUECO = `CFG_HUECO,
    parameter integer N_FEATURES = `CFG_NF,
    parameter integer USAR_PESOS = `CFG_PESOS
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        arrancar,
    output wire [1:0]  decision_sellada,
    output wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje_sellado,
    output wire [31:0] id_sellado,
    output wire [47:0] ciclo_sellado,
    output wire [31:0] latencia_ciclos,
    output wire        sello_valido,
    output wire        saturo,
    output wire        uart_tx_linea,
    output wire        fin
);
    wire        peso_we;
    wire [2:0]  peso_idx;
    wire signed [`MKI_ANCHO_PESO-1:0] peso_dato;
    wire        palabra_valida;
    wire [8*B-1:0] palabra_dato;

    // LA RUTA DEL ARCHIVO VA LITERAL EN CADA RAMA, y no por parámetro ni por
    // macro. Se probaron las dos alternativas y las dos fallan en yosys aunque
    // Icarus las acepte: reenviar un parámetro de tipo string a través de la
    // jerarquía da "Parameter with non-constant value", y pasarlo por -D desde
    // el guion de yosys pierde las comillas en el tokenizador y da error de
    // sintaxis. Queda escrito para no volver a perder el rato averiguándolo —
    // es el mismo género de tropiezo que el `chparam` que ya documenta el
    // Makefile. Dos ramas explícitas cuestan una línea y funcionan en las dos
    // herramientas.
    generate
    if (B == 28) begin : fuente28
        fuente_bram #(
            .B(B), .N_MSG(N_MSG), .HUECO(HUECO),
            .ARCHIVO_MSG("vectores/mensajes_b28.hex"),
            .ARCHIVO_PESOS("vectores/pesos.hex")
        ) u_fuente (
            .clk(clk), .rst_n(rst_n), .arrancar(arrancar),
            .peso_we(peso_we), .peso_idx(peso_idx), .peso_dato(peso_dato),
            .palabra_valida(palabra_valida), .palabra_dato(palabra_dato),
            .fin(fin)
        );
    end else begin : fuente4
        fuente_bram #(
            .B(B), .N_MSG(N_MSG), .HUECO(HUECO),
            .ARCHIVO_MSG("vectores/mensajes_b4.hex"),
            .ARCHIVO_PESOS("vectores/pesos.hex")
        ) u_fuente (
            .clk(clk), .rst_n(rst_n), .arrancar(arrancar),
            .peso_we(peso_we), .peso_idx(peso_idx), .peso_dato(peso_dato),
            .palabra_valida(palabra_valida), .palabra_dato(palabra_dato),
            .fin(fin)
        );
    end
    endgenerate

    pipeline_top_ancho #(
        .B(B), .N_FEATURES(N_FEATURES), .USAR_PESOS(USAR_PESOS)
    ) u_pipe (
        .clk(clk), .rst_n(rst_n),
        .palabra_valida(palabra_valida), .palabra_dato(palabra_dato),
        .peso_we(peso_we), .peso_idx(peso_idx), .peso_dato(peso_dato),
        .enviar_uart(1'b0),
        .decision_sellada(decision_sellada),
        .puntaje_sellado(puntaje_sellado),
        .id_sellado(id_sellado), .ciclo_sellado(ciclo_sellado),
        .latencia_ciclos(latencia_ciclos), .sello_valido(sello_valido),
        .saturo(saturo), .uart_tx_linea(uart_tx_linea)
    );

endmodule
