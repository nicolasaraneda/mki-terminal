`timescale 1ns / 1ps
`include "mki_definiciones.vh"
`include "parametros.vh"

// BANCO DE PRUEBAS de la variante de ingesta ancha.
//
// Compara contra EL MISMO `vectores/esperado_F1.hex` que usa `tb_pipeline.v`.
// Ésa es toda la gracia: ensanchar el bus de entrada no puede cambiar ni un
// bit del resultado, porque no toca la aritmética. Si cambia, la variante está
// mal y el banco lo dice.
//
// Lo que sí tiene que cambiar es la LATENCIA, y la predicción está escrita
// ANTES de correr en `pipeline_top_ancho.v`: ceil(28/B) + 4 ciclos. El banco
// la verifica contra el valor medido y falla si no coinciden — es una
// predicción falsable, no una observación a posteriori.

`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif
`ifndef CFG_B
  `define CFG_B 1
`endif
`ifndef CFG_ARCHIVO_ESPERADO
  `define CFG_ARCHIVO_ESPERADO "vectores/esperado_F1.hex"
`endif

module tb_pipeline_ancho;

    localparam integer N_CASOS    = `N_CASOS;
    localparam integer BYTES_MSG  = `MKI_BYTES_MSG;
    localparam integer B          = `CFG_B;
    localparam integer N_PALABRAS = (BYTES_MSG + B - 1) / B;
    localparam integer LAT_ESPERADA = N_PALABRAS + 4;
    localparam integer HUECO = 8;

    reg clk = 1'b0;
    reg rst_n = 1'b0;
    always #5 clk = ~clk;

    reg           palabra_valida = 1'b0;
    reg [8*B-1:0] palabra_dato = {(8*B){1'b0}};
    reg           peso_we = 1'b0;
    reg [2:0]     peso_idx = 3'd0;
    reg signed [`MKI_ANCHO_PESO-1:0] peso_dato = 16'sd0;

    wire [1:0]  decision_sellada;
    wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje_sellado;
    wire [31:0] id_sellado;
    wire [47:0] ciclo_sellado;
    wire [31:0] latencia_ciclos;
    wire        sello_valido, saturo, uart_tx_linea;

    pipeline_top_ancho #(
        .B(B), .N_FEATURES(`CFG_NF), .USAR_PESOS(`CFG_PESOS),
        .N_VENTANA(`N_VENTANA), .RECIPROCO_Q16(`RECIPROCO_Q16)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .palabra_valida(palabra_valida), .palabra_dato(palabra_dato),
        .peso_we(peso_we), .peso_idx(peso_idx), .peso_dato(peso_dato),
        .enviar_uart(1'b0),
        .decision_sellada(decision_sellada),
        .puntaje_sellado(puntaje_sellado),
        .id_sellado(id_sellado), .ciclo_sellado(ciclo_sellado),
        .latencia_ciclos(latencia_ciclos), .sello_valido(sello_valido),
        .saturo(saturo), .uart_tx_linea(uart_tx_linea)
    );

    reg [7:0]  mensajes [0:N_CASOS*BYTES_MSG-1];
    reg [15:0] pesos    [0:N_CASOS*6-1];
    reg [31:0] esperado [0:N_CASOS-1];

    integer k, b, wi, bl, idx, fallos;
    integer latencia_min, latencia_max;
    reg [1:0] dec_esp;
    reg signed [`MKI_ANCHO_FEATURE-1:0] pun_esp;

    initial begin
        $readmemh("vectores/mensajes.hex", mensajes);
        $readmemh("vectores/pesos.hex", pesos);
        $readmemh(`CFG_ARCHIVO_ESPERADO, esperado);

        fallos = 0;
        latencia_min = 32'h7FFFFFFF;
        latencia_max = 0;

        $display("=== tb_pipeline_ancho: B=%0d bytes/ciclo  palabras=%0d  casos=%0d ===",
                 B, N_PALABRAS, N_CASOS);
        $display("    latencia PREDICHA antes de medir: %0d ciclos", LAT_ESPERADA);

        repeat (4) @(posedge clk);
        rst_n = 1'b1;
        repeat (4) @(posedge clk);

        for (k = 0; k < N_CASOS; k = k + 1) begin
            for (b = 0; b < 6; b = b + 1) begin
                @(negedge clk);
                peso_we = 1'b1; peso_idx = b[2:0]; peso_dato = pesos[k*6 + b];
            end
            @(negedge clk);
            peso_we = 1'b0;

            // Los 28 bytes en N_PALABRAS palabras de B bytes. La última va con
            // relleno si B no divide a 28: el formato de wire no se toca, el
            // relleno lo descarta la ingesta.
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

            dec_esp = esperado[k][17:16];
            pun_esp = esperado[k][15:0];
            if (decision_sellada !== dec_esp || puntaje_sellado !== pun_esp) begin
                fallos = fallos + 1;
                if (fallos <= 10)
                    $display("  FALLO caso %0d: puntaje=%0d esperado=%0d decision=%0d esperada=%0d",
                             k, puntaje_sellado, pun_esp, decision_sellada, dec_esp);
            end
            if (latencia_ciclos < latencia_min) latencia_min = latencia_ciclos;
            if (latencia_ciclos > latencia_max) latencia_max = latencia_ciclos;

            repeat (HUECO) @(negedge clk);
        end

        $display("");
        $display("  casos comparados : %0d", N_CASOS);
        $display("  fallos           : %0d", fallos);
        $display("  latencia min/max : %0d / %0d ciclos", latencia_min, latencia_max);

        if (latencia_min !== latencia_max) begin
            $display("  LATENCIA NO DETERMINISTA: min != max. Hallazgo, no detalle.");
            fallos = fallos + 1;
        end
        if (latencia_max !== LAT_ESPERADA) begin
            $display("  LA PREDICCION FALLA: predicho %0d, medido %0d.",
                     LAT_ESPERADA, latencia_max);
            fallos = fallos + 1;
        end

        if (fallos == 0)
            $display("  VEREDICTO: OK — %0d/%0d bit a bit, latencia %0d ciclos constante",
                     N_CASOS, N_CASOS, latencia_max);
        else
            $display("  VEREDICTO: FALLA — %0d discrepancias", fallos);

        $display("");
        if (fallos != 0) $fatal(1);
        $finish;
    end

    initial begin
        #20000000;
        $display("  TIMEOUT: la simulacion no termino. Falla.");
        $fatal(1);
    end

endmodule
