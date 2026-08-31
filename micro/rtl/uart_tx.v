// UART transmisor 8N1. Existe por una razón de MEDICIÓN, no de adorno:
// RTL.md §2 presupuestó la etapa de salida como "contador de 48 bits + UART
// 115200 baudios" (~100-150 LUTs). Si el diseño sintetizado no incluyera el
// UART, el número medido no sería comparable con la estimación y la
// comparación de la §2 quedaría coja justo en la fila más fácil de inflar.
//
// El divisor entra por parámetro y no se calcula con división en RTL: una
// división por una constante en tiempo de elaboración la hace el
// elaborador, no el silicio.

module uart_tx #(
    parameter integer DIVISOR = 104   // 12 MHz / 115200 baudios ≈ 104
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       enviar,
    input  wire [7:0] dato,
    output reg        tx,
    output reg        ocupado
);

    // El contador se dimensiona al DIVISOR real; con un $clog2 el ancho
    // acompaña si alguien cambia la frecuencia de reloj de la placa.
    localparam integer W_CNT = (DIVISOR <= 2) ? 2 : $clog2(DIVISOR);

    reg [W_CNT-1:0] contador;
    reg [3:0]       bit_idx;
    reg [9:0]       trama;    // {stop, dato[7:0], start} — se desplaza a la derecha

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx       <= 1'b1;   // línea en reposo alta: es lo que un receptor
            ocupado  <= 1'b0;   // interpreta como "sin datos", no como un cero
            contador <= {W_CNT{1'b0}};
            bit_idx  <= 4'd0;
            trama    <= 10'h3FF;
        end else if (!ocupado) begin
            tx <= 1'b1;
            if (enviar) begin
                trama    <= {1'b1, dato, 1'b0};
                bit_idx  <= 4'd0;
                contador <= {W_CNT{1'b0}};
                ocupado  <= 1'b1;
            end
        end else begin
            if (contador == (DIVISOR - 1)) begin
                contador <= {W_CNT{1'b0}};
                tx       <= trama[0];
                trama    <= {1'b1, trama[9:1]};
                if (bit_idx == 4'd9)
                    ocupado <= 1'b0;
                else
                    bit_idx <= bit_idx + 4'd1;
            end else begin
                contador <= contador + {{(W_CNT-1){1'b0}}, 1'b1};
            end
        end
    end

endmodule
