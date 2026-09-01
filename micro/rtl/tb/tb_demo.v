`timescale 1ns / 1ps
`include "parametros.vh"

// BANCO DE PRUEBAS de la VARIANTE 2: el sistema autónomo desde memoria interna.
//
// El banco aquí NO alimenta datos: sólo suelta reset, da UN pulso de
// `arrancar` y recoge los sellos que salen. Todo el estímulo vive dentro del
// chip. Si los 181 sellos coinciden bit a bit con `esperado_F1.hex`, entonces
// el reproductor entrega exactamente los mismos mensajes y los mismos pesos
// que el banco de pruebas entregaba a mano — que es la única forma de saber
// que el re-empaquetado a palabras de B bytes no invirtió nada.
//
// PREDICCIONES escritas antes de correr:
//   1. 181/181 bit a bit contra el mismo `esperado_F1.hex` del campeón.
//   2. Latencia = ceil(28/B) + 4, IDÉNTICA a la de la fuente externa: el ciclo
//      de la lectura de memoria está antes del pipeline, no dentro, y el
//      contador de `etapa_salida` empieza en el primer byte que ENTRA al
//      pipeline. Si la latencia sube, la fuente está metida en el camino de
//      medición y eso sería un hallazgo, no un detalle.
//   3. La cuenta de flancos del banco sigue dando latencia + 1.

`ifndef CFG_B
  `define CFG_B 4
`endif
`ifndef CFG_ARCHIVO_ESPERADO
  `define CFG_ARCHIVO_ESPERADO "vectores/esperado_F1.hex"
`endif

module tb_demo;

    localparam integer N_CASOS  = `N_CASOS;
    localparam integer B        = `CFG_B;
    localparam integer N_PAL    = (28 + B - 1) / B;
    localparam integer LAT_ESPERADA = N_PAL + 4;

    reg clk = 1'b0;
    reg rst_n = 1'b0;
    reg arrancar = 1'b0;
    always #5 clk = ~clk;

    wire [1:0]  decision_sellada;
    wire signed [15:0] puntaje_sellado;
    wire [31:0] id_sellado;
    wire [47:0] ciclo_sellado;
    wire [31:0] latencia_ciclos;
    wire        sello_valido, saturo, uart_tx_linea, fin;

    demo_top #(.B(B), .N_MSG(N_CASOS)) dut (
        .clk(clk), .rst_n(rst_n), .arrancar(arrancar),
        .decision_sellada(decision_sellada),
        .puntaje_sellado(puntaje_sellado),
        .id_sellado(id_sellado), .ciclo_sellado(ciclo_sellado),
        .latencia_ciclos(latencia_ciclos), .sello_valido(sello_valido),
        .saturo(saturo), .uart_tx_linea(uart_tx_linea), .fin(fin)
    );

    reg [31:0] esperado [0:N_CASOS-1];

    // Instrumento independiente del contador del DUT.
    integer ciclos_tb, desajustes;
    reg     armado;

    integer vistos, fallos;
    integer lat_min, lat_max, tb_min, tb_max;
    reg [1:0] dec_esp;
    reg signed [15:0] pun_esp;

    initial begin
        ciclos_tb = 0; armado = 1'b0; desajustes = 0;
        vistos = 0; fallos = 0;
        lat_min = 32'h7FFFFFFF; lat_max = 0;
        tb_min = 32'h7FFFFFFF; tb_max = 0;
    end

    // Recolector: corre solo, sin coordinarse con ningún estímulo, porque no
    // hay estímulo que coordinar.
    always @(posedge clk) begin
        if (!rst_n) begin
            armado <= 1'b0; ciclos_tb <= 0;
        end else begin
            if (armado) ciclos_tb <= ciclos_tb + 1;
            if (dut.palabra_valida && !armado) begin armado <= 1'b1; ciclos_tb <= 0; end

            if (sello_valido) begin
                dec_esp = esperado[vistos][17:16];
                pun_esp = esperado[vistos][15:0];
                if (decision_sellada !== dec_esp || puntaje_sellado !== pun_esp) begin
                    fallos = fallos + 1;
                    if (fallos <= 10)
                        $display("  FALLO sello %0d: puntaje=%0d esperado=%0d decision=%0d esperada=%0d",
                                 vistos, puntaje_sellado, pun_esp,
                                 decision_sellada, dec_esp);
                end
                if (latencia_ciclos < lat_min) lat_min = latencia_ciclos;
                if (latencia_ciclos > lat_max) lat_max = latencia_ciclos;
                if ((ciclos_tb + 1) < tb_min) tb_min = ciclos_tb + 1;
                if ((ciclos_tb + 1) > tb_max) tb_max = ciclos_tb + 1;
                if ((ciclos_tb + 1) !== (latencia_ciclos + 1)) desajustes = desajustes + 1;
                vistos = vistos + 1;
                armado <= 1'b0;
            end
        end
    end

    initial begin
        $readmemh(`CFG_ARCHIVO_ESPERADO, esperado);

        $display("=== tb_demo: sistema AUTONOMO desde memoria interna, B=%0d ===", B);
        $display("    el banco no alimenta datos: solo un pulso de arrancar");
        $display("    latencia PREDICHA antes de medir: %0d ciclos (DUT) / %0d (banco)",
                 LAT_ESPERADA, LAT_ESPERADA + 1);

        repeat (4) @(posedge clk);
        rst_n = 1'b1;
        repeat (4) @(posedge clk);
        @(negedge clk); arrancar = 1'b1;
        @(negedge clk); arrancar = 1'b0;

        wait (fin === 1'b1);
        repeat (20) @(posedge clk);

        $display("");
        $display("  sellos recogidos        : %0d (esperados %0d)", vistos, N_CASOS);
        $display("  fallos bit a bit        : %0d", fallos);
        $display("  latencia DUT min/max    : %0d / %0d ciclos", lat_min, lat_max);
        $display("  latencia BANCO min/max  : %0d / %0d ciclos", tb_min, tb_max);
        $display("  desajustes DUT vs banco : %0d", desajustes);

        if (vistos !== N_CASOS) begin
            $display("  LA FUENTE NO ENTREGO LOS %0d MENSAJES.", N_CASOS);
            fallos = fallos + 1;
        end
        if (lat_min !== lat_max) begin
            $display("  LATENCIA NO DETERMINISTA (DUT)."); fallos = fallos + 1; end
        if (lat_max !== LAT_ESPERADA) begin
            $display("  LA PREDICCION FALLA (DUT): predicho %0d, medido %0d.",
                     LAT_ESPERADA, lat_max); fallos = fallos + 1; end
        if (tb_max !== LAT_ESPERADA + 1) begin
            $display("  LA PREDICCION FALLA (BANCO): predicho %0d, medido %0d.",
                     LAT_ESPERADA + 1, tb_max); fallos = fallos + 1; end
        if (desajustes !== 0) begin
            $display("  LOS DOS INSTRUMENTOS NO COINCIDEN."); fallos = fallos + 1; end

        if (fallos == 0)
            $display("  VEREDICTO: OK — %0d/%0d bit a bit desde memoria interna, %0d ciclos",
                     vistos, N_CASOS, lat_max);
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
