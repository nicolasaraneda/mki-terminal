`include "mki_definiciones.vh"

// SINT_TOP — envoltorio de PLACA para llevar el pipeline a place & route real
// sobre el iCE40HX1K de la Nandland Go Board.
//
// POR QUÉ EXISTE (y por qué NO es hacer trampa):
// `pipeline_top` expone el sello completo —168 bits entre id, contador de
// ciclos, latencia y puntaje— porque el banco de pruebas los necesita. El
// encapsulado tq144 tiene ~96 pines: llevar ese top a nextpnr falla POR
// PINES, y ese fallo no informa nada sobre si la LÓGICA cabe.
//
// La tentación es podar salidas hasta que entren. Eso está MAL y hay que
// decir por qué: el sintetizador propaga constantes hacia atrás y borra toda
// la lógica que ya no alimenta un pin. El diseño "cabría" porque se habría
// evaporado. El área medida sería una ficción cómoda.
//
// Lo que se hace en cambio es poner el envoltorio que un proyecto real
// tendría: los bytes llegan por UART RX, la decisión sale por dos LEDs, y el
// sello se serializa por UART TX. Todos los registros del sello siguen
// alimentando algo, así que nada se poda. El costo del envoltorio (UART RX +
// serializador) se mide APARTE sintetizando `pipeline_top` solo, y se resta:
// el Makefile corre las dos y SINTESIS.md publica las dos columnas.
//
// Parámetros por -D en la línea de yosys (ver el Makefile) porque `chparam`
// renombra el módulo y `synth_ice40 -top` después no lo encuentra.

`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif

module sint_top (
    input  wire clk,        // 12 MHz en la Go Board
    input  wire rst_n,
    input  wire uart_rx_linea,
    output wire uart_tx_linea,
    output wire led_compra,
    output wire led_venta,
    output wire led_saturo,
    output wire led_actividad
);

    // --- Entrada: bytes por UART ---
    wire [7:0] byte_dato;
    wire       byte_valido;

    uart_rx #(.DIVISOR(104)) u_rx (
        .clk(clk), .rst_n(rst_n),
        .rx(uart_rx_linea),
        .dato(byte_dato), .dato_valido(byte_valido)
    );

    // --- Carga de pesos ---
    // ESTA PARTE NO ES OPCIONAL Y CASI CUESTA LA MEDICIÓN ENTERA.
    //
    // La primera versión de este envoltorio dejaba `peso_we` clavado en 0. El
    // resultado: yosys vio que el banco de pesos nunca se escribía, propagó la
    // constante cero hacia el MAC y BORRÓ EL MULTIPLICADOR. La síntesis
    // reportó 295 LUTs para F=1 — una cifra preciosa y completamente falsa,
    // porque medía un pipeline sin la etapa que el proyecto quiere medir.
    //
    // Es el modo de fallo más peligroso de una medición de área: no da error,
    // da un número mejor. Por eso los pesos se cargan DE VERDAD, desde el
    // mismo flujo de bytes: tras el reset, los primeros 12 bytes son los 6
    // pesos (16 bits little-endian cada uno) y todo lo que sigue son mensajes.
    // Y por eso `reportar_sintesis.py` verifica que el multiplicador SIGA
    // EXISTIENDO en el netlist en vez de confiar en que sí.
    localparam integer BYTES_PESOS = 12;

    reg [3:0]  cnt_pesos;      // 0..12; en 12 la carga terminó
    reg [7:0]  byte_bajo;
    reg        peso_we;
    reg [2:0]  peso_idx;
    reg signed [`MKI_ANCHO_PESO-1:0] peso_dato;

    wire cargando = (cnt_pesos < BYTES_PESOS[3:0]);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cnt_pesos <= 4'd0;
            byte_bajo <= 8'd0;
            peso_we   <= 1'b0;
            peso_idx  <= 3'd0;
            peso_dato <= {`MKI_ANCHO_PESO{1'b0}};
        end else begin
            peso_we <= 1'b0;
            if (byte_valido && cargando) begin
                if (cnt_pesos[0] == 1'b0) begin
                    byte_bajo <= byte_dato;          // byte bajo primero
                end else begin
                    peso_dato <= {byte_dato, byte_bajo};
                    peso_idx  <= cnt_pesos[3:1];
                    peso_we   <= 1'b1;
                end
                cnt_pesos <= cnt_pesos + 4'd1;
            end
        end
    end

    // Los bytes de la fase de carga NO deben entrar al parser de mensajes: si
    // entraran, los 12 primeros bytes del primer mensaje serían pesos y el
    // pipeline arrancaría desalineado para siempre.
    wire byte_a_pipeline = byte_valido && !cargando;

    wire [1:0]  decision_sellada;
    wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje_sellado;
    wire [31:0] id_sellado;
    wire [47:0] ciclo_sellado;
    wire [31:0] latencia_ciclos;
    wire        sello_valido;
    wire        saturo;

    pipeline_top #(
        .N_FEATURES(`CFG_NF),
        .USAR_PESOS(`CFG_PESOS)
    ) u_pipeline (
        .clk(clk), .rst_n(rst_n),
        .byte_valido(byte_a_pipeline), .byte_dato(byte_dato),
        .peso_we(peso_we), .peso_idx(peso_idx), .peso_dato(peso_dato),
        .enviar_uart(1'b0),
        .decision_sellada(decision_sellada),
        .puntaje_sellado(puntaje_sellado),
        .id_sellado(id_sellado),
        .ciclo_sellado(ciclo_sellado),
        .latencia_ciclos(latencia_ciclos),
        .sello_valido(sello_valido),
        .saturo(saturo),
        .uart_tx_linea()   // el UART interno de la etapa 5 no se usa acá
    );

    // --- Salida: serializador del sello completo por UART ---
    // Los 16 bytes cubren puntaje(2) + decision(1) + id(4) + ciclo(6) +
    // latencia(4) menos el relleno. Lo importante para la MEDICIÓN es que
    // TODOS los bits del sello alimentan este multiplexor: por eso ningún
    // registro del sello queda huérfano y el sintetizador no puede podarlo.
    reg [3:0]   idx_tx;
    reg         tx_enviar;
    reg [7:0]   tx_dato;
    reg         tx_activo;
    wire        tx_ocupado;

    reg [1:0]   d_lat;
    reg [15:0]  p_lat;
    reg [31:0]  i_lat;
    reg [47:0]  c_lat;
    reg [31:0]  l_lat;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            idx_tx    <= 4'd0;
            tx_enviar <= 1'b0;
            tx_dato   <= 8'd0;
            tx_activo <= 1'b0;
            d_lat <= 2'd0; p_lat <= 16'd0; i_lat <= 32'd0;
            c_lat <= 48'd0; l_lat <= 32'd0;
        end else begin
            tx_enviar <= 1'b0;

            if (sello_valido && !tx_activo) begin
                d_lat <= decision_sellada;
                p_lat <= puntaje_sellado;
                i_lat <= id_sellado;
                c_lat <= ciclo_sellado;
                l_lat <= latencia_ciclos;
                idx_tx    <= 4'd0;
                tx_activo <= 1'b1;
            end else if (tx_activo && !tx_ocupado && !tx_enviar) begin
                case (idx_tx)
                    4'd0:  tx_dato <= {6'd0, d_lat};
                    4'd1:  tx_dato <= p_lat[7:0];
                    4'd2:  tx_dato <= p_lat[15:8];
                    4'd3:  tx_dato <= i_lat[7:0];
                    4'd4:  tx_dato <= i_lat[15:8];
                    4'd5:  tx_dato <= i_lat[23:16];
                    4'd6:  tx_dato <= i_lat[31:24];
                    4'd7:  tx_dato <= c_lat[7:0];
                    4'd8:  tx_dato <= c_lat[15:8];
                    4'd9:  tx_dato <= c_lat[23:16];
                    4'd10: tx_dato <= c_lat[31:24];
                    4'd11: tx_dato <= c_lat[39:32];
                    4'd12: tx_dato <= c_lat[47:40];
                    4'd13: tx_dato <= l_lat[7:0];
                    4'd14: tx_dato <= l_lat[15:8];
                    default: tx_dato <= {l_lat[31:24] ^ l_lat[23:16]};
                endcase
                tx_enviar <= 1'b1;
                if (idx_tx == 4'd15)
                    tx_activo <= 1'b0;
                else
                    idx_tx <= idx_tx + 4'd1;
            end
        end
    end

    uart_tx #(.DIVISOR(104)) u_tx (
        .clk(clk), .rst_n(rst_n),
        .enviar(tx_enviar), .dato(tx_dato),
        .tx(uart_tx_linea), .ocupado(tx_ocupado)
    );

    assign led_compra    = (d_lat == `MKI_COMPRA);
    assign led_venta     = (d_lat == `MKI_VENTA);
    assign led_saturo    = saturo;
    assign led_actividad = tx_activo;

endmodule
