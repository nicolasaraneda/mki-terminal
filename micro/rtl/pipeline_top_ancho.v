`include "mki_definiciones.vh"

// TOP (VARIANTE) — el mismo pipeline de `pipeline_top.v` con la ingesta de B
// bytes por ciclo. Las etapas 2 a 5 son LAS MISMAS instancias, sin un solo
// cambio: si el resultado difiere del original, la culpa es de la ingesta y
// de nada más. Ésa es toda la razón por la que esta variante existe como top
// aparte en vez de como una bandera dentro del original.
//
// Latencia esperada, por construcción:
//     ceil(28/B) - 1   ciclos de ingesta  (de la palabra 0 a la última)
//   + 1                registro de features
//   + 2                MAC
//   + 1                decisión
//   + 1                sello
//   = ceil(28/B) + 4   ciclos
// Con B=1 da 32, que es exactamente lo que el banco de pruebas ya midió sobre
// `pipeline_top`. Esa coincidencia es la prueba de que la variante no cambió
// nada más — se verifica corriendo el banco con B=1 ANTES de leer cualquier
// otro B.

`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif
`ifndef CFG_B
  `define CFG_B 1
`endif

module pipeline_top_ancho #(
    parameter integer B            = `CFG_B,
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
    input  wire        palabra_valida,
    input  wire [8*B-1:0] palabra_dato,
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

    wire [63:0] ts_ns;
    wire [31:0] id_instrumento;
    wire [63:0] precio_fp;
    wire [31:0] cantidad;
    wire [7:0]  lado, flags;
    wire [15:0] reservado;
    wire        msg_valido;
    wire        inicio_mensaje;

    etapa_ingesta_ancha #(.B(B)) u_ingesta (
        .clk(clk), .rst_n(rst_n),
        .palabra_valida(palabra_valida), .palabra_dato(palabra_dato),
        .ts_ns(ts_ns), .id_instrumento(id_instrumento),
        .precio_fp(precio_fp), .cantidad(cantidad),
        .lado(lado), .flags(flags), .reservado(reservado),
        .msg_valido(msg_valido), .inicio_mensaje(inicio_mensaje)
    );

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

    wire [1:0] decision;
    wire decision_valida;

    etapa_decision #(
        .UMBRAL_ALZA(UMBRAL_ALZA), .UMBRAL_BAJA(UMBRAL_BAJA)
    ) u_decision (
        .clk(clk), .rst_n(rst_n),
        .puntaje_valido(puntaje_valido), .puntaje(puntaje),
        .decision(decision), .decision_valida(decision_valida)
    );

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
