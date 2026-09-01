`include "mki_definiciones.vh"

// VARIANTE 2 DEL ESPACIO DE DISEÑO — FUENTE INTERNA: reproductor de las filas
// selladas desde memoria en el chip.
//
// POR QUÉ ÉSTA. Es el último pendiente de `SINTESIS_A7.md` §8, textual: "La
// ingesta ancha desde BRAM: hoy la fuente del testbench es el propio banco de
// pruebas. Un reproductor desde BRAM es RTL nuevo y no está escrito." Y es la
// pieza que decide si el ancho de bus sirve de algo: §4.1 midió que B=28 baja
// la latencia a 5 ciclos, pero 28 bytes en paralelo son 224 pines y la Arty A7
// expone 32 señales por los cuatro Pmod. **Un bus ancho desde afuera es
// imposible en esta placa.** Adentro no: §3.2 midió que la historia sellada
// entera son 5.292 B = 0,85% de la BRAM. Sin este módulo, la mejora de la
// latencia es real pero irrealizable más allá de B=4; con él, B=28 pasa a ser
// una opción de verdad. Por eso se eligió, y no por lo que impresiona.
//
// QUÉ REPRODUCE. Los 181 casos completos: los 28 bytes de cada mensaje Y los
// seis pesos de cada caso. La beta rodante cambia fecha a fecha, así que un
// banco de pesos cargado una vez NO reproduce nada — los pesos tienen que
// venir del mismo reproductor. Con esto el diseño arranca con UN pulso y no
// necesita ni UART ni banco de pruebas: es la arquitectura de la demo del ramo.
//
// LECTURA SÍNCRONA A PROPÓSITO. La BRAM de un Artix-7 (y el SB_RAM40_4K del
// iCE40) sólo tiene lectura registrada. Una lectura combinacional obligaría al
// sintetizador a mapear la memoria a LUTs y el costo medido sería el de otro
// diseño. Por eso las salidas van un ciclo detrás de la dirección — y ese
// ciclo está ANTES del pipeline, no dentro, así que la latencia de decisión
// (primer byte → sello) no se mueve. Es la predicción que `tb/tb_demo.v`
// verifica.
//
// El contenido se carga con $readmemh, que yosys entiende como valor inicial
// de la memoria y traduce a INIT de la BRAM. Los archivos los produce
// `empaquetar_vectores.py` re-agrupando `vectores/mensajes.hex`; no se toca
// `senales.db` en ningún punto de esta cadena.

module fuente_bram #(
    parameter integer B      = 4,
    parameter integer N_MSG  = 181,
    parameter integer HUECO  = 8,      // ciclos de silencio entre mensajes
    parameter ARCHIVO_MSG   = "vectores/mensajes_b4.hex",
    parameter ARCHIVO_PESOS = "vectores/pesos.hex"
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        arrancar,

    output reg         peso_we,
    output reg  [2:0]  peso_idx,
    output reg  signed [`MKI_ANCHO_PESO-1:0] peso_dato,

    output reg         palabra_valida,
    output reg  [8*B-1:0] palabra_dato,

    output reg         fin
);
    localparam integer BYTES = `MKI_BYTES_MSG;                // 28
    localparam integer N_PAL = (BYTES + B - 1) / B;
    localparam integer TOT_PAL = N_MSG * N_PAL;
    localparam integer TOT_PES = N_MSG * 6;
    localparam integer AW_M = $clog2(TOT_PAL);
    localparam integer AW_P = $clog2(TOT_PES);
    localparam integer AW_K = $clog2(N_MSG + 1);
    localparam integer AW_C = $clog2((N_PAL > HUECO ? N_PAL : HUECO) + 7);

    localparam [2:0] S_OCIO = 3'd0, S_PESO = 3'd1, S_MSG = 3'd2,
                     S_HUECO = 3'd3, S_FIN = 3'd4;

    reg [8*B-1:0] rom_msg [0:TOT_PAL-1];
    reg [`MKI_ANCHO_PESO-1:0] rom_pes [0:TOT_PES-1];

    initial begin
        $readmemh(ARCHIVO_MSG, rom_msg);
        $readmemh(ARCHIVO_PESOS, rom_pes);
    end

    // -----------------------------------------------------------------------
    // HUECO MÍNIMO = 2 CICLOS. MEDIDO, NO SUPUESTO, Y NO ES UNA COMODIDAD DEL
    // BANCO DE PRUEBAS.
    //
    // `SINTESIS.md` §9 y `SINTESIS_A7.md` §3.5 describen los 8 ciclos de
    // silencio entre mensajes como algo que el banco inserta "para que la
    // latencia se mida limpia". Al barrer HUECO de 0 a 8 con las 181 filas
    // selladas resulta que el silencio hace algo más que eso: con HUECO = 0 ó
    // 1, **178 de los 181 sellos salen mal**, y salen corridos un mensaje —
    // el escritor de pesos del mensaje k+1 pisa el banco antes de que
    // `etapa_puntaje` haya muestreado el peso del mensaje k. Con HUECO >= 2,
    // 181/181 bit a bit, y el umbral es 2 en los dos anchos probados (B=4 y
    // B=28), o sea que no depende del ancho del bus sino de la profundidad del
    // pipeline entre `msg_valido` y el muestreo del peso.
    //
    // LO PEOR DEL HALLAZGO: la LATENCIA seguía dando 11 ciclos exactos y
    // determinista mientras los resultados estaban mal. Una prueba que sólo
    // mirara la latencia habría pasado en verde. Por eso el guardia va acá, en
    // elaboración, y no en un comentario.
    //
    // El bypass existe sólo para poder MEDIR la zona insegura (es como se
    // encontró el 2) y hay que pedirlo a propósito.
`ifndef CFG_PERMITIR_HUECO_INSEGURO
    initial begin
        if (HUECO < 2) begin
            $display("fuente_bram: HUECO=%0d < 2 produce sellos CORRIDOS UN MENSAJE.", HUECO);
            $display("             Medido: 178/181 mal con HUECO 0 y 1; 181/181 desde 2.");
            $display("             Si lo que se quiere es medir la zona insegura,");
            $display("             compilar con -DCFG_PERMITIR_HUECO_INSEGURO.");
            $fatal(1);
        end
    end
`endif

    reg [2:0]      estado;
    reg [AW_K-1:0] idx_msg;
    reg [AW_C-1:0] cnt;

    wire [AW_M-1:0] dir_msg = idx_msg * N_PAL + ((estado == S_MSG) ? cnt : {AW_C{1'b0}});
    wire [AW_P-1:0] dir_pes = idx_msg * 6     + ((estado == S_PESO) ? cnt : {AW_C{1'b0}});

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            estado  <= S_OCIO;
            idx_msg <= {AW_K{1'b0}};
            cnt     <= {AW_C{1'b0}};
        end else begin
            case (estado)
                S_OCIO: if (arrancar) begin
                    estado <= S_PESO; idx_msg <= {AW_K{1'b0}}; cnt <= {AW_C{1'b0}};
                end
                S_PESO: if (cnt == 3'd5) begin estado <= S_MSG; cnt <= {AW_C{1'b0}}; end
                        else cnt <= cnt + 1'b1;
                // HUECO=0 salta el estado de silencio: es la configuracion que
                // mide el caudal espalda-con-espalda que SINTESIS.md §9 dejo
                // pendiente. No es el default (el default sigue siendo 8) para
                // que ninguna cifra ya publicada se mueva.
                S_MSG:  if (cnt == (N_PAL - 1)) begin
                            cnt <= {AW_C{1'b0}};
                            if (HUECO == 0) begin
                                if (idx_msg == (N_MSG - 1)) estado <= S_FIN;
                                else begin idx_msg <= idx_msg + 1'b1; estado <= S_PESO; end
                            end else estado <= S_HUECO;
                        end else cnt <= cnt + 1'b1;
                S_HUECO: if (cnt == (HUECO - 1)) begin
                    cnt <= {AW_C{1'b0}};
                    if (idx_msg == (N_MSG - 1)) estado <= S_FIN;
                    else begin idx_msg <= idx_msg + 1'b1; estado <= S_PESO; end
                end else cnt <= cnt + 1'b1;
                default: estado <= S_FIN;
            endcase
        end
    end

    // Etapa de salida: un ciclo detrás del estado, que es exactamente el
    // ciclo de la lectura de la memoria. Los `we`/`valido` viajan por el mismo
    // registro que el dato, así que no pueden desalinearse.
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            peso_we        <= 1'b0;
            peso_idx       <= 3'd0;
            peso_dato      <= {`MKI_ANCHO_PESO{1'b0}};
            palabra_valida <= 1'b0;
            palabra_dato   <= {(8*B){1'b0}};
            fin            <= 1'b0;
        end else begin
            peso_we        <= (estado == S_PESO);
            peso_idx       <= cnt[2:0];
            peso_dato      <= rom_pes[dir_pes];
            palabra_valida <= (estado == S_MSG);
            palabra_dato   <= rom_msg[dir_msg];
            fin            <= (estado == S_FIN);
        end
    end

endmodule
