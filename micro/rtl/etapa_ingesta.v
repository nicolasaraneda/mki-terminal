`include "mki_definiciones.vh"

// ETAPA 1 — INGESTA (parser del mensaje de 28 bytes).
//
// Por qué una máquina de estados byte a byte y no un casteo del buffer:
// en software `bench_mensaje.c` puede darse el lujo de un memcpy campo a
// campo sobre un buffer ya residente en memoria. En hardware el mensaje
// LLEGA — un byte por ciclo desde un PHY, un UART o una FIFO — y no existe
// un "buffer entero" hasta que terminó de llegar. Ensamblar cada campo con
// selects de bits sobre un contador de byte es la forma nativa, no un rodeo:
// el registro de destino ya es el almacenamiento, no hay copia.
//
// Determinismo: exactamente `MKI_BYTES_MSG` ciclos desde el primer byte hasta
// que se afirma msg_valido. Siempre los mismos. No hay camino que dependa del
// contenido del mensaje — esa es la propiedad que este proyecto quiere
// demostrar y por eso el parser NO tiene ni un early-exit ni un salto.

module etapa_ingesta (
    input  wire        clk,
    input  wire        rst_n,

    // Flujo de entrada: un byte por ciclo cuando byte_valido está alto.
    input  wire        byte_valido,
    input  wire [7:0]  byte_dato,

    // Campos deserializados, estables mientras msg_valido está alto.
    output reg  [63:0] ts_ns,
    output reg  [31:0] id_instrumento,
    output reg  [63:0] precio_fp,
    output reg  [31:0] cantidad,
    output reg  [7:0]  lado,
    output reg  [7:0]  flags,
    output reg  [15:0] reservado,

    output reg         msg_valido,   // pulso de un ciclo
    output wire [4:0]  indice_byte   // observable para el testbench y el sello
);

    // 28 bytes entran en 5 bits (0..27). El contador se compara contra la
    // constante en vez de usar un wrap por potencia de dos porque 28 no lo es
    // — y forzarlo a 32 con bytes de relleno sería inventar formato.
    reg [4:0] contador;
    assign indice_byte = contador;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            contador       <= 5'd0;
            msg_valido     <= 1'b0;
            ts_ns          <= 64'd0;
            id_instrumento <= 32'd0;
            precio_fp      <= 64'd0;
            cantidad       <= 32'd0;
            lado           <= 8'd0;
            flags          <= 8'd0;
            reservado      <= 16'd0;
        end else begin
            // msg_valido es un pulso: se limpia siempre y solo se vuelve a
            // afirmar en el ciclo del byte 27. Que sea pulso y no nivel evita
            // que la etapa de features reprocese el mismo mensaje si el flujo
            // de bytes se pausa.
            msg_valido <= 1'b0;

            if (byte_valido) begin
                // Little-endian: el byte i-ésimo de un campo va a los bits
                // [8i+7 : 8i]. Se escribe con un case explícito y no con un
                // desplazamiento variable porque un shifter de 64 bits con
                // cantidad variable cuesta cientos de LUTs en un iCE40 y acá
                // el índice es una constante por rama — el sintetizador lo
                // resuelve como cableado puro.
                case (contador)
                    5'd0:  ts_ns[7:0]            <= byte_dato;
                    5'd1:  ts_ns[15:8]           <= byte_dato;
                    5'd2:  ts_ns[23:16]          <= byte_dato;
                    5'd3:  ts_ns[31:24]          <= byte_dato;
                    5'd4:  ts_ns[39:32]          <= byte_dato;
                    5'd5:  ts_ns[47:40]          <= byte_dato;
                    5'd6:  ts_ns[55:48]          <= byte_dato;
                    5'd7:  ts_ns[63:56]          <= byte_dato;
                    5'd8:  id_instrumento[7:0]   <= byte_dato;
                    5'd9:  id_instrumento[15:8]  <= byte_dato;
                    5'd10: id_instrumento[23:16] <= byte_dato;
                    5'd11: id_instrumento[31:24] <= byte_dato;
                    5'd12: precio_fp[7:0]        <= byte_dato;
                    5'd13: precio_fp[15:8]       <= byte_dato;
                    5'd14: precio_fp[23:16]      <= byte_dato;
                    5'd15: precio_fp[31:24]      <= byte_dato;
                    5'd16: precio_fp[39:32]      <= byte_dato;
                    5'd17: precio_fp[47:40]      <= byte_dato;
                    5'd18: precio_fp[55:48]      <= byte_dato;
                    5'd19: precio_fp[63:56]      <= byte_dato;
                    5'd20: cantidad[7:0]         <= byte_dato;
                    5'd21: cantidad[15:8]        <= byte_dato;
                    5'd22: cantidad[23:16]       <= byte_dato;
                    5'd23: cantidad[31:24]       <= byte_dato;
                    5'd24: lado                  <= byte_dato;
                    5'd25: flags                 <= byte_dato;
                    5'd26: reservado[7:0]        <= byte_dato;
                    5'd27: reservado[15:8]       <= byte_dato;
                    default: ; // inalcanzable: el contador nunca pasa de 27
                endcase

                if (contador == (`MKI_BYTES_MSG - 1)) begin
                    contador   <= 5'd0;
                    msg_valido <= 1'b1;
                end else begin
                    contador <= contador + 5'd1;
                end
            end
        end
    end

endmodule
