`include "mki_definiciones.vh"

// multi_top_ancho.v — K instancias del pipeline DE INGESTA ANCHA en paralelo.
//
// POR QUÉ EXISTE. `multi_top.v` midió el techo de replicación con la ingesta
// byte a byte: 240 tickers, con el DSP48E1 topando primero. La ingesta ancha
// baja el área por instancia (108 → 102 → 93 LUT6 según B), así que la
// pregunta obvia es si el techo se movió. La respuesta se MIDE, no se deduce:
// bajar LUT y FF sube esos dos topes, pero el DSP no lo toca nadie, y si el
// que topa primero sigue siendo el DSP entonces el techo es INDEPENDIENTE de
// la latencia. Eso es un resultado, no un supuesto — y sólo se puede afirmar
// después de sintetizar el barrido completo con B distinto de 1.
//
// Es copia deliberada de `multi_top.v` con el top cambiado, por la misma razón
// por la que `etapa_ingesta_ancha.v` es un archivo aparte: `multi_top.v`
// produjo la tabla de SINTESIS_A7.md §3.4 y tocarlo obligaría a reverificar
// esa tabla entera.
//
// Los sellos van a puertos de verdad (no a cables sueltos) por el mismo motivo
// documentado en `multi_top.v`: sin eso el sintetizador poda el contador de 48
// bits y el área por ticker sale artificialmente barata.

`ifndef CFG_K
  `define CFG_K 8
`endif
`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif
`ifndef CFG_B
  `define CFG_B 4
`endif

module multi_top_ancho #(
    parameter integer K          = `CFG_K,
    parameter integer B          = `CFG_B,
    parameter integer N_FEATURES = `CFG_NF,
    parameter integer USAR_PESOS = `CFG_PESOS
) (
    input  wire              clk,
    input  wire              rst_n,
    input  wire [K-1:0]      palabra_valida,
    input  wire [8*B*K-1:0]  palabra_dato,
    input  wire [K-1:0]      peso_we,
    input  wire [3*K-1:0]    peso_idx,
    input  wire [`MKI_ANCHO_PESO*K-1:0] peso_dato,
    output wire [2*K-1:0]    decision_sellada,
    output wire [`MKI_ANCHO_FEATURE*K-1:0] puntaje_sellado,
    output wire [32*K-1:0]   id_sellado,
    output wire [48*K-1:0]   ciclo_sellado,
    output wire [32*K-1:0]   latencia_ciclos,
    output wire [K-1:0]      sello_valido,
    output wire [K-1:0]      saturo,
    output wire [K-1:0]      uart_tx_linea
);
    genvar k;
    generate
        for (k = 0; k < K; k = k + 1) begin : ticker
            pipeline_top_ancho #(
                .B(B),
                .N_FEATURES(N_FEATURES),
                .USAR_PESOS(USAR_PESOS)
            ) u_pipe (
                .clk(clk), .rst_n(rst_n),
                .palabra_valida(palabra_valida[k]),
                .palabra_dato(palabra_dato[8*B*k +: 8*B]),
                .peso_we(peso_we[k]),
                .peso_idx(peso_idx[3*k +: 3]),
                .peso_dato(peso_dato[`MKI_ANCHO_PESO*k +: `MKI_ANCHO_PESO]),
                .enviar_uart(1'b0),
                .decision_sellada(decision_sellada[2*k +: 2]),
                .puntaje_sellado(puntaje_sellado[`MKI_ANCHO_FEATURE*k +: `MKI_ANCHO_FEATURE]),
                .id_sellado(id_sellado[32*k +: 32]),
                .ciclo_sellado(ciclo_sellado[48*k +: 48]),
                .latencia_ciclos(latencia_ciclos[32*k +: 32]),
                .sello_valido(sello_valido[k]),
                .saturo(saturo[k]),
                .uart_tx_linea(uart_tx_linea[k])
            );
        end
    endgenerate
endmodule
