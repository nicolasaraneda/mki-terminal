`timescale 1ns / 1ps
`include "mki_definiciones.vh"
`include "parametros.vh"

// BANCO DE PRUEBAS — lo que convierte al RTL en una MEDICIÓN.
//
// Protocolo de RTL.md §4, paso por paso:
//   1. vector real: 181 filas selladas de senales.db serializadas a 28 bytes
//   2. referencia:  referencia.py, float64 y entero, AISLADA de motor.py
//   3. simulación:  este archivo
//   4. comparación: decisión idéntica al 100%; puntaje dentro de tolerancia
//
// La tolerancia se declara ANTES de comparar y NO se toca después de ver el
// resultado (RTL.md §4.4 lo dice con todas las letras). Acá la comparación
// contra `esperado_*.hex` es EXACTA —bit a bit— porque el archivo lo produjo
// el modelo ENTERO, que replica la semántica del RTL. Comparar bit a bit
// contra el modelo entero y por tolerancia contra el flotante son dos
// preguntas distintas; la segunda la responde referencia.py y su reporte, no
// este archivo. Confundirlas es cómo un banco de pruebas "pasa" sin probar
// nada.
//
// Configuración por -D en tiempo de compilación (ver el Makefile):
//   CFG_NF     número de features
//   CFG_PESOS  1 = MAC con pesos, 0 = variante "solo umbral"
//   CFG_ARCHIVO_ESPERADO  nombre del .hex de referencia

`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif
`ifndef CFG_ARCHIVO_ESPERADO
  `define CFG_ARCHIVO_ESPERADO "vectores/esperado_F1.hex"
`endif

module tb_pipeline;

    localparam integer N_CASOS   = `N_CASOS;
    localparam integer BYTES_MSG = `MKI_BYTES_MSG;
    // Ciclos de silencio entre mensajes. Existen para que la medición de
    // latencia sea limpia: `inicio_mensaje` del mensaje k+1 pisaría el
    // registro `ciclo_inicio` del mensaje k si se solaparan. El throughput
    // espalda-con-espalda es otra pregunta y NO se responde acá — decir que
    // se midió sería mentir sobre el experimento que se corrió.
    localparam integer HUECO = 8;

    reg clk = 1'b0;
    reg rst_n = 1'b0;
    always #5 clk = ~clk;   // 100 MHz en simulación; la placa real va a 12 MHz

    reg        byte_valido = 1'b0;
    reg [7:0]  byte_dato = 8'd0;
    reg        peso_we = 1'b0;
    reg [2:0]  peso_idx = 3'd0;
    reg signed [`MKI_ANCHO_PESO-1:0] peso_dato = 16'sd0;

    wire [1:0]  decision_sellada;
    wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje_sellado;
    wire [31:0] id_sellado;
    wire [47:0] ciclo_sellado;
    wire [31:0] latencia_ciclos;
    wire        sello_valido;
    wire        saturo;
    wire        uart_tx_linea;

    pipeline_top #(
        .N_FEATURES(`CFG_NF),
        .USAR_PESOS(`CFG_PESOS),
        .N_VENTANA(`N_VENTANA),
        .RECIPROCO_Q16(`RECIPROCO_Q16)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .byte_valido(byte_valido), .byte_dato(byte_dato),
        .peso_we(peso_we), .peso_idx(peso_idx), .peso_dato(peso_dato),
        .enviar_uart(1'b0),
        .decision_sellada(decision_sellada),
        .puntaje_sellado(puntaje_sellado),
        .id_sellado(id_sellado),
        .ciclo_sellado(ciclo_sellado),
        .latencia_ciclos(latencia_ciclos),
        .sello_valido(sello_valido),
        .saturo(saturo),
        .uart_tx_linea(uart_tx_linea)
    );

    // --- Vectores ---
    reg [7:0]  mensajes [0:N_CASOS*BYTES_MSG-1];
    reg [15:0] pesos    [0:N_CASOS*6-1];
    reg [31:0] esperado [0:N_CASOS-1];

    integer k, b, fallos, saturaciones;
    integer latencia_min, latencia_max;
    reg [31:0] obtenido;
    reg [1:0]  dec_esp;
    reg signed [`MKI_ANCHO_FEATURE-1:0] pun_esp;

    initial begin
        $readmemh("vectores/mensajes.hex", mensajes);
        $readmemh("vectores/pesos.hex", pesos);
        $readmemh(`CFG_ARCHIVO_ESPERADO, esperado);

        fallos = 0;
        saturaciones = 0;
        latencia_min = 32'h7FFFFFFF;
        latencia_max = 0;

        $display("=== tb_pipeline: N_FEATURES=%0d USAR_PESOS=%0d casos=%0d ===",
                 `CFG_NF, `CFG_PESOS, N_CASOS);
        $display("    referencia: %s", `CFG_ARCHIVO_ESPERADO);

        // Reset síncrono al flanco, largo a propósito: la ventana rodante son
        // N_VENTANA registros y todos tienen que quedar en cero antes del
        // primer mensaje, o el modelo de referencia y el DUT arrancarían con
        // estados distintos y toda la comparación posterior sería ruido.
        repeat (4) @(posedge clk);
        rst_n = 1'b1;
        repeat (4) @(posedge clk);

        for (k = 0; k < N_CASOS; k = k + 1) begin
            // --- Carga de pesos (registro de configuración, RTL.md §5) ---
            for (b = 0; b < 6; b = b + 1) begin
                @(negedge clk);
                peso_we   = 1'b1;
                peso_idx  = b[2:0];
                peso_dato = pesos[k*6 + b];
            end
            @(negedge clk);
            peso_we = 1'b0;

            // --- 28 bytes, uno por ciclo, sin huecos: así llega un mensaje ---
            for (b = 0; b < BYTES_MSG; b = b + 1) begin
                @(negedge clk);
                byte_valido = 1'b1;
                byte_dato   = mensajes[k*BYTES_MSG + b];
            end
            @(negedge clk);
            byte_valido = 1'b0;

            // --- Esperar el sello ---
            while (!sello_valido) @(posedge clk);

            obtenido = {14'd0, decision_sellada, puntaje_sellado};
            dec_esp  = esperado[k][17:16];
            pun_esp  = esperado[k][15:0];

            if (decision_sellada !== dec_esp || puntaje_sellado !== pun_esp) begin
                fallos = fallos + 1;
                if (fallos <= 10)
                    $display("  FALLO caso %0d: puntaje obtenido=%0d esperado=%0d | decision obtenida=%0d esperada=%0d",
                             k, puntaje_sellado, pun_esp, decision_sellada, dec_esp);
            end
            if (saturo) saturaciones = saturaciones + 1;

            if (latencia_ciclos < latencia_min) latencia_min = latencia_ciclos;
            if (latencia_ciclos > latencia_max) latencia_max = latencia_ciclos;

            repeat (HUECO) @(negedge clk);
        end

        $display("");
        $display("--- resultado ---");
        $display("  casos comparados     : %0d", N_CASOS);
        $display("  fallos               : %0d", fallos);
        $display("  saturaciones          : %0d", saturaciones);
        $display("  latencia min          : %0d ciclos", latencia_min);
        $display("  latencia max          : %0d ciclos", latencia_max);

        // ÉSTA es la afirmación falsable de fpga.md §2: en hardware
        // p50 = p99 = maximo = minimo. Si el mínimo y el máximo difieren,
        // hay una ruta que depende de los datos y ESO es el hallazgo, no un
        // detalle de implementación.
        if (latencia_min !== latencia_max) begin
            $display("  LATENCIA NO DETERMINISTA: min != max. Hallazgo, no detalle.");
            fallos = fallos + 1;
        end else begin
            $display("  latencia DETERMINISTA : %0d ciclos, identica en los %0d casos",
                     latencia_max, N_CASOS);
        end

        if (fallos == 0)
            $display("  VEREDICTO: OK — el RTL reproduce la referencia en los %0d casos", N_CASOS);
        else
            $display("  VEREDICTO: FALLA — %0d discrepancias", fallos);

        $display("");
        if (fallos != 0) $fatal(1);
        $finish;
    end

    // Red de seguridad: una simulación que se cuelga esperando `sello_valido`
    // que nunca llega se vería igual que una que "todavía corre". El corte
    // explícito la convierte en un fallo visible.
    initial begin
        #20000000;
        $display("  TIMEOUT: la simulacion no termino. Falla.");
        $fatal(1);
    end

endmodule
