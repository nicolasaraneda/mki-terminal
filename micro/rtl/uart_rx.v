// UART receptor 8N1. Existe por una razón de HONESTIDAD DE LA MEDICIÓN.
//
// `pipeline_top` expone 165 señales de depuración (el sello completo, el
// contador de 48 bits, la latencia, el id). Eso está bien para simular, pero
// el encapsulado tq144 del iCE40HX1K tiene ~96 pines de E/S: llevar
// `pipeline_top` a place & route tal cual FALLA POR PINES, no por lógica — y
// ese fallo no dice nada sobre si el pipeline cabe.
//
// La solución no es podar salidas hasta que entren (eso deja que el
// sintetizador borre lógica y regale área que el diseño sí usa). Es poner el
// envoltorio de placa que un proyecto real tendría: los bytes ENTRAN por
// UART, la decisión sale por dos LEDs y el sello se va por UART. Así el
// número de nextpnr corresponde a un diseño que se podría programar, y el
// costo del envoltorio se mide y se resta por separado.
//
// Sobremuestreo 16x y decisión en el centro del bit: un receptor que muestrea
// en el flanco confunde ruido con datos en cuanto los relojes derivan un
// poco, y los relojes SIEMPRE derivan un poco entre dos placas distintas.

module uart_rx #(
    parameter integer DIVISOR = 104   // ciclos por bit: 12 MHz / 115200
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       rx,
    output reg [7:0]  dato,
    output reg        dato_valido   // pulso de un ciclo
);

    localparam integer W_CNT = (DIVISOR <= 2) ? 2 : $clog2(DIVISOR);
    localparam integer MEDIO = DIVISOR / 2;

    localparam [1:0] REPOSO = 2'd0, ARRANQUE = 2'd1, DATOS = 2'd2, PARADA = 2'd3;

    reg [1:0]       estado;
    reg [W_CNT-1:0] contador;
    reg [2:0]       bit_idx;
    reg [7:0]       desplaza;
    // Sincronizador de dos etapas: `rx` viene de un pin, o sea de OTRO dominio
    // de reloj (ninguno, en realidad). Muestrearlo directo es la receta
    // clásica de metaestabilidad, y fpga.md §2 avisa que una ruta mal
    // sincronizada aparecería como COLA en la distribución de latencia — es
    // decir, arruinaría justo la medición que este proyecto busca.
    reg [1:0]       sinc;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            estado      <= REPOSO;
            contador    <= {W_CNT{1'b0}};
            bit_idx     <= 3'd0;
            desplaza    <= 8'd0;
            dato        <= 8'd0;
            dato_valido <= 1'b0;
            sinc        <= 2'b11;
        end else begin
            sinc        <= {sinc[0], rx};
            dato_valido <= 1'b0;

            case (estado)
                REPOSO: begin
                    if (sinc[1] == 1'b0) begin   // flanco de bajada = arranque
                        estado   <= ARRANQUE;
                        contador <= {W_CNT{1'b0}};
                    end
                end
                ARRANQUE: begin
                    // Se espera medio bit y se re-verifica: un glitch de un
                    // ciclo en la línea no debe disparar una trama entera.
                    if (contador == MEDIO[W_CNT-1:0]) begin
                        if (sinc[1] == 1'b0) begin
                            estado   <= DATOS;
                            contador <= {W_CNT{1'b0}};
                            bit_idx  <= 3'd0;
                        end else begin
                            estado <= REPOSO;
                        end
                    end else begin
                        contador <= contador + {{(W_CNT-1){1'b0}}, 1'b1};
                    end
                end
                DATOS: begin
                    if (contador == (DIVISOR - 1)) begin
                        contador <= {W_CNT{1'b0}};
                        desplaza <= {sinc[1], desplaza[7:1]};   // LSB primero
                        if (bit_idx == 3'd7)
                            estado <= PARADA;
                        else
                            bit_idx <= bit_idx + 3'd1;
                    end else begin
                        contador <= contador + {{(W_CNT-1){1'b0}}, 1'b1};
                    end
                end
                PARADA: begin
                    if (contador == (DIVISOR - 1)) begin
                        contador <= {W_CNT{1'b0}};
                        estado   <= REPOSO;
                        // El byte se entrega aunque el bit de parada venga mal
                        // formado: descartarlo silenciosamente convertiría un
                        // problema de cableado en "el pipeline no responde",
                        // que es el síntoma más difícil de diagnosticar.
                        dato        <= desplaza;
                        dato_valido <= 1'b1;
                    end else begin
                        contador <= contador + {{(W_CNT-1){1'b0}}, 1'b1};
                    end
                end
                default: estado <= REPOSO;
            endcase
        end
    end

endmodule
