`include "mki_definiciones.vh"

// multi_top.v — K instancias del pipeline en paralelo, una por ticker.
//
// POR QUÉ EXISTE: la pregunta "¿cuántos tickers entran en la Arty A7-100T?"
// tiene dos respuestas y sólo una es honesta.
//
//   (a) La respuesta de servilleta: 240 DSP / 1 DSP por ticker = 240.
//   (b) La respuesta medida: sintetizar K instancias de verdad y ver dónde
//       topa el recurso que topa PRIMERO.
//
// No son la misma respuesta porque el área por instancia no es aditiva: el
// mapeo tecnológico global duplica lógica para cerrar tiempos, y
// GEMELO/MICRO/SINTESIS.md §3.4 ya midió ese efecto en un 45% sobre el iCE40.
// Suponer aditividad acá sería repetir exactamente el error estructural que
// ese hallazgo documentó. Por eso este módulo se sintetiza para varios K y el
// margen por instancia se lee de la PENDIENTE medida, no de una división.
//
// Cada instancia tiene su propio flujo de bytes y su propio banco de pesos: es
// la topología correcta para "ocho tickers, cada uno con su beta". Nada se
// comparte salvo el reloj y el reset, así que el sintetizador no puede fusionar
// dos instancias y regalar un número bajo que no significaría nada.
//
// ALTERNATIVA NO IMPLEMENTADA, Y ES LA QUE PROBABLEMENTE CORRESPONDE: un solo
// pipeline multiplexado en el tiempo sobre K tickers. A 100 MHz una decisión
// sale cada 32 ciclos de latencia y el sistema real emite OCHO predicciones POR
// DÍA. (El throughput SOSTENIDO no se midió — SINTESIS.md §9 —, pero para ocho
// mensajes diarios no hace falta medirlo para saber que sobra.)
// La replicación espacial es la que responde "cuánto cabe"; la multiplexación
// temporal es la que responde "cuánto hace falta". Ver SINTESIS_A7.md §4.2.

`ifndef CFG_K
  `define CFG_K 8
`endif
`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif

module multi_top #(
    parameter integer K          = `CFG_K,
    parameter integer N_FEATURES = `CFG_NF,
    parameter integer USAR_PESOS = `CFG_PESOS
) (
    input  wire            clk,
    input  wire            rst_n,
    input  wire [K-1:0]    byte_valido,
    input  wire [8*K-1:0]  byte_dato,
    input  wire [K-1:0]    peso_we,
    input  wire [3*K-1:0]  peso_idx,
    input  wire [`MKI_ANCHO_PESO*K-1:0] peso_dato,
    output wire [2*K-1:0]  decision_sellada,
    output wire [`MKI_ANCHO_FEATURE*K-1:0] puntaje_sellado,
    // Los tres sellos van a puertos de verdad y no a cables sueltos: si se
    // dejan sin conectar, el sintetizador PODA el contador de ciclos de 48
    // bits y la latencia de cada instancia, y el área por ticker sale
    // artificialmente barata. Se descubrió midiendo (K=8 daba 305 LUTs en vez
    // de ~1.700) y queda escrito para que nadie lo "simplifique" de vuelta.
    output wire [32*K-1:0] id_sellado,
    output wire [48*K-1:0] ciclo_sellado,
    output wire [32*K-1:0] latencia_ciclos,
    output wire [K-1:0]    sello_valido,
    output wire [K-1:0]    saturo,
    output wire [K-1:0]    uart_tx_linea
);
    genvar k;
    generate
        for (k = 0; k < K; k = k + 1) begin : ticker
            pipeline_top #(
                .N_FEATURES(N_FEATURES),
                .USAR_PESOS(USAR_PESOS)
            ) u_pipe (
                .clk(clk), .rst_n(rst_n),
                .byte_valido(byte_valido[k]),
                .byte_dato(byte_dato[8*k +: 8]),
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
