`timescale 1ns / 1ps
`include "parametros.vh"

// BANCO DE PRUEBAS de la VARIANTE 1: tabla de pesos por instrumento.
//
// Los 181 vectores sellados ya traen `id_instrumento` = 0..7 (los ocho
// tickers de `MERCADOS_POR_ABRIR`, `referencia.py` los numera denso). O sea
// que el campo que `SINTESIS_A7.md` §4.2 describe como "hoy sólo se usa para
// sellar" ya está poblado con la información correcta: no hubo que inventar
// nada para probar esto.
//
// EL TEST NO ES "PROGRAMAR Y LEER". Programar sólo el slot correcto y ver que
// sale bien no distingue una tabla de un registro único: con una sola entrada
// escrita, cualquier decodificador roto que devuelva siempre esa entrada
// pasaría. Así que antes de cada caso se escriben LOS T SLOTS: el del
// instrumento del mensaje con su peso real, y todos los demás con un SEÑUELO
// (peso ^ 0x5A5A, que nunca coincide con el real). Si el mensaje toma la fila
// equivocada, el puntaje cambia y el banco lo grita. Es la diferencia entre
// verificar la tabla y verificar que la tabla existe.
//
// PREDICCIONES, escritas antes de correr (el banco falla si no se cumplen):
//   1. 181/181 bit a bit contra el MISMO `esperado_F1.hex` del campeón.
//   2. Latencia = ceil(28/B) + 4, la misma que sin tabla: la lectura es
//      síncrona y cabe en el ciclo que ya existía.
//   3. Los dos instrumentos (contador del DUT y cuenta de flancos del banco)
//      siguen coincidiendo: ciclos_tb == latencia_ciclos + 1.

`ifndef CFG_B
  `define CFG_B 4
`endif
`ifndef CFG_T
  `define CFG_T 8
`endif
`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif
`ifndef CFG_ARCHIVO_ESPERADO
  `define CFG_ARCHIVO_ESPERADO "vectores/esperado_F1.hex"
`endif

module tb_pipeline_multi;

    localparam integer N_CASOS    = `N_CASOS;
    localparam integer BYTES_MSG  = 28;
    localparam integer B          = `CFG_B;
    localparam integer T          = `CFG_T;
    localparam integer LOG_T      = (T <= 1) ? 1 : $clog2(T);
    localparam integer N_PALABRAS = (BYTES_MSG + B - 1) / B;
    localparam integer LAT_ESPERADA = N_PALABRAS + 4;
    localparam integer HUECO = 8;

    reg clk = 1'b0;
    reg rst_n = 1'b0;
    always #5 clk = ~clk;

    reg               palabra_valida = 1'b0;
    reg [8*B-1:0]     palabra_dato = {(8*B){1'b0}};
    reg               peso_we = 1'b0;
    reg [LOG_T-1:0]   peso_slot = {LOG_T{1'b0}};
    reg [2:0]         peso_idx = 3'd0;
    reg signed [15:0] peso_dato = 16'sd0;

    wire [1:0]  decision_sellada;
    wire signed [15:0] puntaje_sellado;
    wire [31:0] id_sellado;
    wire [47:0] ciclo_sellado;
    wire [31:0] latencia_ciclos;
    wire        sello_valido, saturo, uart_tx_linea;

    pipeline_top_multi #(
        .B(B), .T(T), .N_FEATURES(`CFG_NF), .USAR_PESOS(`CFG_PESOS),
        .N_VENTANA(`N_VENTANA), .RECIPROCO_Q16(`RECIPROCO_Q16)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .palabra_valida(palabra_valida), .palabra_dato(palabra_dato),
        .peso_we(peso_we), .peso_slot(peso_slot), .peso_idx(peso_idx),
        .peso_dato(peso_dato),
        .enviar_uart(1'b0),
        .decision_sellada(decision_sellada),
        .puntaje_sellado(puntaje_sellado),
        .id_sellado(id_sellado), .ciclo_sellado(ciclo_sellado),
        .latencia_ciclos(latencia_ciclos), .sello_valido(sello_valido),
        .saturo(saturo), .uart_tx_linea(uart_tx_linea)
    );

    // Instrumento independiente del contador del DUT (ver tb_pipeline_gate.v).
    integer ciclos_tb, ciclos_tb_ultimo, desajustes;
    reg     armado;
    initial begin ciclos_tb = 0; ciclos_tb_ultimo = -1; armado = 0; desajustes = 0; end
    always @(posedge clk) begin
        if (!rst_n) begin armado <= 1'b0; ciclos_tb <= 0; end
        else begin
            if (armado) ciclos_tb <= ciclos_tb + 1;
            if (palabra_valida && !armado) begin armado <= 1'b1; ciclos_tb <= 0; end
            if (sello_valido && armado) begin
                armado <= 1'b0;
                ciclos_tb_ultimo <= ciclos_tb + 1;
                if ((ciclos_tb + 1) !== (latencia_ciclos + 1))
                    desajustes <= desajustes + 1;
            end
        end
    end

    reg [7:0]  mensajes [0:N_CASOS*BYTES_MSG-1];
    reg [15:0] pesos    [0:N_CASOS*6-1];
    reg [31:0] esperado [0:N_CASOS-1];

    integer k, b, s, wi, bl, idx, fallos;
    integer latencia_min, latencia_max, tb_min, tb_max;
    integer id_caso;
    reg [1:0] dec_esp;
    reg signed [15:0] pun_esp;

    initial begin
        $readmemh("vectores/mensajes.hex", mensajes);
        $readmemh("vectores/pesos.hex", pesos);
        $readmemh(`CFG_ARCHIVO_ESPERADO, esperado);

        fallos = 0;
        latencia_min = 32'h7FFFFFFF; latencia_max = 0;
        tb_min = 32'h7FFFFFFF; tb_max = 0;

        $display("=== tb_pipeline_multi: B=%0d  T=%0d instrumentos  casos=%0d ===",
                 B, T, N_CASOS);
        $display("    latencia PREDICHA antes de medir: %0d ciclos (DUT) / %0d (banco)",
                 LAT_ESPERADA, LAT_ESPERADA + 1);
        $display("    los T-1 slots que NO corresponden se cargan con senuelos");

        repeat (4) @(posedge clk);
        rst_n = 1'b1;
        repeat (4) @(posedge clk);

        for (k = 0; k < N_CASOS; k = k + 1) begin
            // id del mensaje: bytes 8..11, little-endian.
            id_caso = {mensajes[k*BYTES_MSG+11], mensajes[k*BYTES_MSG+10],
                       mensajes[k*BYTES_MSG+9],  mensajes[k*BYTES_MSG+8]};

            for (s = 0; s < T; s = s + 1) begin
                for (b = 0; b < 6; b = b + 1) begin
                    @(negedge clk);
                    peso_we   = 1'b1;
                    peso_slot = s[LOG_T-1:0];
                    peso_idx  = b[2:0];
                    peso_dato = (s == (id_caso % T)) ? pesos[k*6 + b]
                                                     : (pesos[k*6 + b] ^ 16'h5A5A);
                end
            end
            @(negedge clk);
            peso_we = 1'b0;

            for (wi = 0; wi < N_PALABRAS; wi = wi + 1) begin
                @(negedge clk);
                palabra_valida = 1'b1;
                for (bl = 0; bl < B; bl = bl + 1) begin
                    idx = wi * B + bl;
                    palabra_dato[bl*8 +: 8] =
                        (idx < BYTES_MSG) ? mensajes[k*BYTES_MSG + idx] : 8'h00;
                end
            end
            @(negedge clk);
            palabra_valida = 1'b0;

            while (!sello_valido) @(posedge clk);
            @(negedge clk);

            dec_esp = esperado[k][17:16];
            pun_esp = esperado[k][15:0];
            if (decision_sellada !== dec_esp || puntaje_sellado !== pun_esp) begin
                fallos = fallos + 1;
                if (fallos <= 10)
                    $display("  FALLO caso %0d (id=%0d): puntaje=%0d esperado=%0d decision=%0d esperada=%0d",
                             k, id_caso, puntaje_sellado, pun_esp,
                             decision_sellada, dec_esp);
            end
            if (id_sellado !== id_caso) begin
                fallos = fallos + 1;
                if (fallos <= 10)
                    $display("  FALLO caso %0d: id sellado %0d != %0d", k, id_sellado, id_caso);
            end
            if (latencia_ciclos < latencia_min) latencia_min = latencia_ciclos;
            if (latencia_ciclos > latencia_max) latencia_max = latencia_ciclos;
            if (ciclos_tb_ultimo < tb_min) tb_min = ciclos_tb_ultimo;
            if (ciclos_tb_ultimo > tb_max) tb_max = ciclos_tb_ultimo;

            repeat (HUECO) @(negedge clk);
        end

        $display("");
        $display("  casos comparados        : %0d", N_CASOS);
        $display("  fallos bit a bit        : %0d", fallos);
        $display("  latencia DUT min/max    : %0d / %0d ciclos", latencia_min, latencia_max);
        $display("  latencia BANCO min/max  : %0d / %0d ciclos", tb_min, tb_max);
        $display("  desajustes DUT vs banco : %0d", desajustes);

        if (latencia_min !== latencia_max) begin
            $display("  LATENCIA NO DETERMINISTA (DUT)."); fallos = fallos + 1; end
        if (latencia_max !== LAT_ESPERADA) begin
            $display("  LA PREDICCION FALLA (DUT): predicho %0d, medido %0d.",
                     LAT_ESPERADA, latencia_max); fallos = fallos + 1; end
        if (tb_max !== LAT_ESPERADA + 1) begin
            $display("  LA PREDICCION FALLA (BANCO): predicho %0d, medido %0d.",
                     LAT_ESPERADA + 1, tb_max); fallos = fallos + 1; end
        if (desajustes !== 0) begin
            $display("  LOS DOS INSTRUMENTOS NO COINCIDEN."); fallos = fallos + 1; end

        if (fallos == 0)
            $display("  VEREDICTO: OK — %0d/%0d bit a bit con tabla de %0d instrumentos, %0d ciclos",
                     N_CASOS, N_CASOS, T, latencia_max);
        else
            $display("  VEREDICTO: FALLA — %0d discrepancias", fallos);

        $display("");
        if (fallos != 0) $fatal(1);
        $finish;
    end

    initial begin
        #500000000;
        $display("  TIMEOUT: la simulacion no termino. Falla.");
        $fatal(1);
    end

endmodule
