`include "mki_definiciones.vh"

// ETAPA 5 — SALIDA + SELLO.
//
// El sello es el entregable científico de esta pista, no la decisión. La
// decisión ya la sabe calcular el software (y lo hace 488 millones de veces
// por segundo, ver WSL2.md). Lo que el software NO puede prometer es el
// número de la derecha: la MISMA latencia, siempre. fpga.md §2 formuló la
// predicción falsable —"p50 = p99 = p99.9 = máximo"— y este contador es el
// instrumento que la puede refutar.
//
// El contador es de 48 bits y libre: nunca se resetea durante la operación,
// porque un contador que se reinicia por mensaje mediría el intervalo que uno
// cree que está midiendo en vez del que realmente ocurre. A 12 MHz, 48 bits
// dan ~271 días antes de dar la vuelta; la resta funciona igual si vuelve
// (aritmética modular sin signo), así que la vuelta no es un caso especial.
//
// Ojo con lo que este contador mide y lo que no: mide de PRIMER BYTE a
// DECISIÓN, dentro del dominio de reloj de la FPGA. No incluye el tiempo del
// medio físico que trajo el mensaje ni el del UART que se lleva la respuesta
// — el UART sale del camino de medición a propósito, porque 115200 baudios
// son ~87 µs por byte y taparían por completo la latencia de decisión que se
// quiere demostrar.

module etapa_salida #(
    parameter integer DIVISOR_UART = 104
) (
    input  wire        clk,
    input  wire        rst_n,

    input  wire        inicio_mensaje,   // pulso en el PRIMER byte del mensaje
    input  wire        decision_valida,
    input  wire [1:0]  decision,
    input  wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje,
    input  wire [31:0] id_instrumento,

    output reg  [1:0]  decision_sellada,
    output reg  signed [`MKI_ANCHO_FEATURE-1:0] puntaje_sellado,
    output reg  [31:0] id_sellado,
    output reg  [47:0] ciclo_sellado,     // valor del contador al decidir
    output reg  [31:0] latencia_ciclos,   // primer byte → decisión
    output reg         sello_valido,

    output wire        uart_tx_linea,
    input  wire        enviar_uart
);

    reg [47:0] contador_ciclos;
    reg [47:0] ciclo_inicio;

    // La resta va en un wire y no dentro del always porque Verilog no permite
    // indexar el resultado de una expresión (`(a-b)[31:0]` es sintaxis
    // inválida). Es aritmética modular sin signo de 48 bits: si el contador
    // dio la vuelta, la resta SIGUE dando el intervalo correcto — por eso la
    // vuelta no necesita un caso especial.
    wire [47:0] delta_ciclos = contador_ciclos - ciclo_inicio;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            contador_ciclos <= 48'd0;
            ciclo_inicio    <= 48'd0;
        end else begin
            contador_ciclos <= contador_ciclos + 48'd1;
            if (inicio_mensaje)
                ciclo_inicio <= contador_ciclos;
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            decision_sellada <= `MKI_MANTENER;
            puntaje_sellado  <= {`MKI_ANCHO_FEATURE{1'b0}};
            id_sellado       <= 32'd0;
            ciclo_sellado    <= 48'd0;
            latencia_ciclos  <= 32'd0;
            sello_valido     <= 1'b0;
        end else begin
            sello_valido <= decision_valida;
            if (decision_valida) begin
                decision_sellada <= decision;
                puntaje_sellado  <= puntaje;
                id_sellado       <= id_instrumento;
                ciclo_sellado    <= contador_ciclos;
                // Truncada a 32 bits: la latencia real son unas decenas de
                // ciclos, y truncar acá ahorra 16 bits de registro. Si alguna
                // vez superara 2^32 ciclos, el diseño tendría un problema
                // mucho peor que el truncamiento.
                latencia_ciclos  <= delta_ciclos[31:0];
            end
        end
    end

    // El UART transmite el byte bajo del puntaje bajo demanda del banco de
    // pruebas o de un host. Se deja como demostración de camino completo de
    // punta a punta, fuera del camino de medición de latencia.
    uart_tx #(.DIVISOR(DIVISOR_UART)) u_uart (
        .clk     (clk),
        .rst_n   (rst_n),
        .enviar  (enviar_uart),
        .dato    (puntaje_sellado[7:0]),
        .tx      (uart_tx_linea),
        .ocupado ()
    );

endmodule
