`include "mki_definiciones.vh"

// TOP — las cinco etapas de RTL.md §1 cableadas en orden, más el banco de
// pesos precargables.
//
//   INGESTA ──▶ ESTADO/FEATURES ──▶ PUNTAJE (MAC) ──▶ DECISIÓN ──▶ SALIDA+SELLO
//
// Latencia MEDIDA por el banco de pruebas: 32 ciclos, idéntica en los 181
// vectores reales, en las cuatro configuraciones (F=1, 3, 6 y sin pesos).
//
//   27 ciclos   ingesta (el byte 0 se consume en el mismo ciclo en que
//               `inicio_mensaje` marca el arranque, así que del primer byte
//               al byte 27 hay 27 flancos, no 28)
//  + 1 ciclo    registro de features
//  + 2 ciclos   MAC (productos, luego suma+saturación)
//  + 1 ciclo    decisión
//  + 1 ciclo    sello
//  = 32 ciclos  desde el primer byte hasta sello_valido.
//
// La cuenta a mano decía 33 hasta que el banco de pruebas midió 32: el error
// era contar el ciclo del byte 0 dos veces. Se corrige la cuenta, no la
// medición — que es la regla de la casa cuando el arnés contradice al papel.
//
// A 12 MHz (reloj de la Go Board) son 2,67 µs. Comparar con el piso de
// software medido en WSL2.md: ~72-85 µs de despertar del planificador, con
// cola. El punto no es el promedio — es que 32 no tiene distribución.
//
// El banco de pesos es un registro de configuración, no memoria: RTL.md §5
// prohíbe explícitamente entrenar o re-estimar nada en la FPGA. Los pesos
// (beta, en el modelo real) se calculan fuera con los datos históricos y se
// cargan. Que sean registros y no una BRAM indexada por instrumento es una
// decisión de alcance: el pipeline procesa un instrumento configurado a la
// vez. Una tabla por instrumento es trabajo posterior y agregaría una BRAM.

// Los valores por defecto salen de macros para que `yosys -DCFG_NF=3` alcance
// a parametrizar el módulo cuando se sintetiza SOLO (sin `sint_top` encima).
// La alternativa —`chparam` de yosys— deriva un módulo con nombre nuevo y el
// `hierarchy -top` que corre `synth_ice40` después ya no lo encuentra.
// Instanciado desde sint_top los parámetros llegan explícitos y estos valores
// por defecto no se usan.
`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif

module pipeline_top #(
    parameter integer N_FEATURES   = `CFG_NF,
    parameter integer USAR_PESOS   = `CFG_PESOS,
    parameter integer N_VENTANA    = 10,
    parameter integer RECIPROCO_Q16 = 6554,
    parameter integer DIVISOR_UART = 104,
    parameter signed [`MKI_ANCHO_FEATURE-1:0] UMBRAL_ALZA =  16'sd128,
    parameter signed [`MKI_ANCHO_FEATURE-1:0] UMBRAL_BAJA = -16'sd128
) (
    input  wire        clk,
    input  wire        rst_n,

    // Flujo de bytes del mensaje de 28 bytes.
    input  wire        byte_valido,
    input  wire [7:0]  byte_dato,

    // Carga de pesos (Q2.14). Un peso por ciclo, indexado.
    input  wire        peso_we,
    input  wire [2:0]  peso_idx,
    input  wire signed [`MKI_ANCHO_PESO-1:0] peso_dato,

    input  wire        enviar_uart,

    output wire [1:0]  decision_sellada,
    output wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje_sellado,
    output wire [31:0] id_sellado,
    output wire [47:0] ciclo_sellado,
    output wire [31:0] latencia_ciclos,
    output wire        sello_valido,
    output wire        saturo,
    output wire        uart_tx_linea
);

    // --- Banco de pesos ---
    reg signed [`MKI_ANCHO_PESO-1:0] peso [0:5];
    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 6; i = i + 1)
                peso[i] <= {`MKI_ANCHO_PESO{1'b0}};
        end else if (peso_we && peso_idx < 3'd6) begin
            peso[peso_idx] <= peso_dato;
        end
    end

    // --- Etapa 1: ingesta ---
    wire [63:0] ts_ns;
    wire [31:0] id_instrumento;
    wire [63:0] precio_fp;
    wire [31:0] cantidad;
    wire [7:0]  lado, flags;
    wire [15:0] reservado;
    wire        msg_valido;
    wire [4:0]  indice_byte;

    etapa_ingesta u_ingesta (
        .clk(clk), .rst_n(rst_n),
        .byte_valido(byte_valido), .byte_dato(byte_dato),
        .ts_ns(ts_ns), .id_instrumento(id_instrumento),
        .precio_fp(precio_fp), .cantidad(cantidad),
        .lado(lado), .flags(flags), .reservado(reservado),
        .msg_valido(msg_valido), .indice_byte(indice_byte)
    );

    // El pulso de inicio es el ciclo del byte 0: es el instante desde el que
    // se mide la latencia. Se deriva del contador del parser en vez de
    // llevar una señal aparte para que no puedan desincronizarse.
    wire inicio_mensaje = byte_valido && (indice_byte == 5'd0);

    // --- Etapa 2: estado / features ---
    wire signed [`MKI_ANCHO_FEATURE-1:0] g0, g1, g2, g3, g4, g5;
    wire features_validas;

    etapa_features #(
        .N_VENTANA(N_VENTANA), .RECIPROCO_Q16(RECIPROCO_Q16)
    ) u_features (
        .clk(clk), .rst_n(rst_n),
        .msg_valido(msg_valido),
        .precio_fp(precio_fp), .cantidad(cantidad),
        .g0(g0), .g1(g1), .g2(g2), .g3(g3), .g4(g4), .g5(g5),
        .features_validas(features_validas)
    );

    // --- Etapa 3: puntaje (MAC) ---
    wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje;
    wire puntaje_valido;

    etapa_puntaje #(
        .N_FEATURES(N_FEATURES), .USAR_PESOS(USAR_PESOS)
    ) u_puntaje (
        .clk(clk), .rst_n(rst_n),
        .features_validas(features_validas),
        .g0(g0), .g1(g1), .g2(g2), .g3(g3), .g4(g4), .g5(g5),
        .w0(peso[0]), .w1(peso[1]), .w2(peso[2]),
        .w3(peso[3]), .w4(peso[4]), .w5(peso[5]),
        .puntaje(puntaje), .puntaje_valido(puntaje_valido), .saturo(saturo)
    );

    // --- Etapa 4: decisión ---
    wire [1:0] decision;
    wire decision_valida;

    etapa_decision #(
        .UMBRAL_ALZA(UMBRAL_ALZA), .UMBRAL_BAJA(UMBRAL_BAJA)
    ) u_decision (
        .clk(clk), .rst_n(rst_n),
        .puntaje_valido(puntaje_valido), .puntaje(puntaje),
        .decision(decision), .decision_valida(decision_valida)
    );

    // --- Etapa 5: salida + sello ---
    etapa_salida #(
        .DIVISOR_UART(DIVISOR_UART)
    ) u_salida (
        .clk(clk), .rst_n(rst_n),
        .inicio_mensaje(inicio_mensaje),
        .decision_valida(decision_valida), .decision(decision),
        .puntaje(puntaje), .id_instrumento(id_instrumento),
        .decision_sellada(decision_sellada),
        .puntaje_sellado(puntaje_sellado),
        .id_sellado(id_sellado),
        .ciclo_sellado(ciclo_sellado),
        .latencia_ciclos(latencia_ciclos),
        .sello_valido(sello_valido),
        .uart_tx_linea(uart_tx_linea),
        .enviar_uart(enviar_uart)
    );

endmodule
