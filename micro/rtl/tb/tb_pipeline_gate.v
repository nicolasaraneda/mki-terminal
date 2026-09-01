`timescale 1ns / 1ps
`include "parametros.vh"

// BANCO DE PRUEBAS INDEPENDIENTE DEL MECANISMO — el mismo estímulo de
// `tb_pipeline_ancho.v` sobre un DUT que se instancia SIN sobrescribir
// parámetros, para que el mismo archivo sirva contra el RTL y contra la
// NETLIST MAPEADA que sale del sintetizador.
//
// POR QUÉ EXISTE. La casa manda que una verificación que usa el mismo
// mecanismo que produjo la cifra no es una verificación. Las dos cifras que
// esta corrida tiene que confirmar —11 ciclos a B=4 y 181/181 bit a bit— las
// produjo `tb_pipeline_ancho.v` simulando el RTL y leyendo el registro
// `latencia_ciclos` del propio DUT. Acá se cambian LAS DOS COSAS:
//
//   1. EL INSTRUMENTO. La latencia se mide además contando flancos de reloj
//      del lado del banco, sin mirar el contador de 48 bits que vive dentro
//      de `etapa_salida`. Si ese contador arranca o para donde no debe, o si
//      el truncado a 32 bits miente, el banco lo ve y el DUT no.
//      Relación PREDICHA ANTES DE CORRER: el DUT mide de `inicio_mensaje` a
//      `decision_valida`, y `sello_valido` va un ciclo después, así que
//          ciclos_tb == latencia_ciclos + 1
//      exactamente, para todo B y todo caso. El banco falla si no se cumple.
//      Alcance honesto: esto es independiente del CONTADOR del diseño, no de
//      la noción de "ciclo" — las dos cuentas comparten el mismo reloj.
//
//   2. EL DISEÑO BAJO PRUEBA. Sin `#()` se puede compilar contra la netlist
//      de celdas (SB_LUT4/SB_DFF, o LUT6/FDRE) que produce `yosys`, donde ya
//      no hay parámetros ni for-loops ni aritmética de Verilog: sólo celdas.
//      Que los 181 vectores y la latencia sobrevivan al MAPEO TECNOLÓGICO es
//      una familia de evidencia distinta de simular el RTL.
//
// Los valores por defecto de `pipeline_top_ancho` (N_VENTANA=10,
// RECIPROCO_Q16=6554) coinciden con `vectores/parametros.vh`; se comprueba
// abajo con un $fatal en vez de suponerlo.

`ifndef CFG_B
  `define CFG_B 1
`endif
`ifndef CFG_ARCHIVO_ESPERADO
  `define CFG_ARCHIVO_ESPERADO "vectores/esperado_F1.hex"
`endif
`ifndef CFG_ETIQUETA
  `define CFG_ETIQUETA "rtl"
`endif

module tb_pipeline_gate;

    localparam integer N_CASOS    = `N_CASOS;
    localparam integer BYTES_MSG  = 28;
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
    reg signed [15:0] peso_dato = 16'sd0;

    wire [1:0]  decision_sellada;
    wire signed [15:0] puntaje_sellado;
    wire [31:0] id_sellado;
    wire [47:0] ciclo_sellado;
    wire [31:0] latencia_ciclos;
    wire        sello_valido, saturo, uart_tx_linea;

    // SIN #(): así el mismo archivo compila contra el RTL y contra la netlist.
    pipeline_top_ancho dut (
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

    // ---------------------------------------------------------------------
    // Instrumento independiente: cuenta de flancos del lado del banco.
    // ---------------------------------------------------------------------
    integer ciclos_tb;          // flancos desde el primer palabra_valida
    integer ciclos_tb_ultimo;   // congelado cuando sube sello_valido
    reg     armado;
    integer desajustes;         // veces que ciclos_tb != latencia_ciclos + 1

    initial begin
        ciclos_tb = 0; ciclos_tb_ultimo = -1; armado = 1'b0; desajustes = 0;
    end

    always @(posedge clk) begin
        if (!rst_n) begin
            armado <= 1'b0;
            ciclos_tb <= 0;
        end else begin
            if (armado) ciclos_tb <= ciclos_tb + 1;
            if (palabra_valida && !armado) begin
                armado    <= 1'b1;
                ciclos_tb <= 0;
            end
            if (sello_valido && armado) begin
                armado <= 1'b0;
                // ciclos_tb aún no incorporó este flanco: +1 lo hace.
                ciclos_tb_ultimo <= ciclos_tb + 1;
                if ((ciclos_tb + 1) !== (latencia_ciclos + 1))
                    desajustes <= desajustes + 1;
            end
        end
    end

    reg [7:0]  mensajes [0:N_CASOS*BYTES_MSG-1];
    reg [15:0] pesos    [0:N_CASOS*6-1];
    reg [31:0] esperado [0:N_CASOS-1];

    integer k, b, wi, bl, idx, fallos;
    integer latencia_min, latencia_max, tb_min, tb_max;
    reg [1:0] dec_esp;
    reg signed [15:0] pun_esp;

    initial begin
        if (`N_VENTANA !== 10 || `RECIPROCO_Q16 !== 6554) begin
            $display("  parametros.vh no coincide con los defaults del DUT. Aborta.");
            $fatal(1);
        end

        $readmemh("vectores/mensajes.hex", mensajes);
        $readmemh("vectores/pesos.hex", pesos);
        $readmemh(`CFG_ARCHIVO_ESPERADO, esperado);

        fallos = 0;
        latencia_min = 32'h7FFFFFFF; latencia_max = 0;
        tb_min = 32'h7FFFFFFF; tb_max = 0;

        $display("=== tb_pipeline_gate [%0s]: B=%0d  palabras=%0d  casos=%0d ===",
                 `CFG_ETIQUETA, B, N_PALABRAS, N_CASOS);
        $display("    latencia PREDICHA antes de medir: %0d ciclos (DUT) / %0d (banco)",
                 LAT_ESPERADA, LAT_ESPERADA + 1);

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
            @(negedge clk);   // deja que el monitor congele ciclos_tb_ultimo

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
            $display("  LATENCIA NO DETERMINISTA (DUT): min != max.");
            fallos = fallos + 1;
        end
        if (tb_min !== tb_max) begin
            $display("  LATENCIA NO DETERMINISTA (BANCO): min != max.");
            fallos = fallos + 1;
        end
        if (latencia_max !== LAT_ESPERADA) begin
            $display("  LA PREDICCION FALLA (DUT): predicho %0d, medido %0d.",
                     LAT_ESPERADA, latencia_max);
            fallos = fallos + 1;
        end
        if (tb_max !== LAT_ESPERADA + 1) begin
            $display("  LA PREDICCION FALLA (BANCO): predicho %0d, medido %0d.",
                     LAT_ESPERADA + 1, tb_max);
            fallos = fallos + 1;
        end
        if (desajustes !== 0) begin
            $display("  LOS DOS INSTRUMENTOS NO COINCIDEN: %0d desajustes.", desajustes);
            fallos = fallos + 1;
        end

        if (fallos == 0)
            $display("  VEREDICTO [%0s]: OK — %0d/%0d bit a bit, %0d ciclos (DUT) = %0d (banco) - 1",
                     `CFG_ETIQUETA, N_CASOS, N_CASOS, latencia_max, tb_max);
        else
            $display("  VEREDICTO [%0s]: FALLA — %0d discrepancias", `CFG_ETIQUETA, fallos);

        $display("");
        if (fallos != 0) $fatal(1);
        $finish;
    end

    initial begin
        #200000000;
        $display("  TIMEOUT: la simulacion no termino. Falla.");
        $fatal(1);
    end

endmodule
