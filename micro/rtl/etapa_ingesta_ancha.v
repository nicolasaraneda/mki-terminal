`include "mki_definiciones.vh"

// ETAPA 1 (VARIANTE) — ingesta de B bytes por ciclo.
//
// POR QUÉ EXISTE. La latencia medida del pipeline es de 32 ciclos y
// `pipeline_top.v` la desglosa: 27 son la ingesta byte a byte y 5 son las
// cuatro etapas siguientes. O sea que el 84% de la latencia determinista que
// este proyecto exhibe NO es cómputo — es el ancho del bus de entrada.
//
// El encargo de esta corrida preguntaba qué etapas están "serializadas por
// falta de espacio" y podrían paralelizarse ahora. La respuesta honesta es
// NINGUNA: las etapas 2 a 5 ya corren encadenadas, una por ciclo, y ninguna se
// partió por presupuesto. Lo único serializado es el PARSER, y no por falta de
// LUTs sino porque el diseño supuso un flujo de un byte por ciclo (un UART).
// Este módulo mide qué se gana ensanchando ese flujo — que es la palanca real,
// no la imaginada.
//
// Se deja como ARCHIVO APARTE en vez de parametrizar `etapa_ingesta.v` a
// propósito: ese módulo produjo los 44 LUT4 / 230 FF publicados en
// SINTESIS.md §3, y tocarle los puertos obligaría a reverificar esa fila.
// Acá el default es B=1 justamente para poder demostrar que la variante
// reproduce el comportamiento original antes de creerle cualquier otro B.
//
// Determinismo: N_PALABRAS = ceil(28/B) ciclos desde la primera palabra hasta
// msg_valido, SIEMPRE los mismos. No hay camino que dependa del contenido.
// Si B no divide a 28, la última palabra lleva relleno y los bytes sobrantes
// se descartan — el formato de wire de 28 bytes NO se toca.

module etapa_ingesta_ancha #(
    parameter integer B = 1   // bytes por ciclo
) (
    input  wire            clk,
    input  wire            rst_n,

    input  wire            palabra_valida,
    input  wire [8*B-1:0]  palabra_dato,

    output reg  [63:0]     ts_ns,
    output reg  [31:0]     id_instrumento,
    output reg  [63:0]     precio_fp,
    output reg  [31:0]     cantidad,
    output reg  [7:0]      lado,
    output reg  [7:0]      flags,
    output reg  [15:0]     reservado,

    output reg             msg_valido,
    output wire            inicio_mensaje
);
    localparam integer BYTES = `MKI_BYTES_MSG;                 // 28
    localparam integer N_PALABRAS = (BYTES + B - 1) / B;       // ceil(28/B)
    localparam integer W_CNT = (N_PALABRAS <= 1) ? 1 : $clog2(N_PALABRAS);

    reg [W_CNT-1:0] contador;
    // El buffer NO es una copia extra: es el mismo almacenamiento que en la
    // versión byte a byte estaban los registros de campo, agrupado para que el
    // índice de escritura sea constante por rama. Los campos salen de recortes
    // de bits, que es cableado y no lógica.
    reg [8*BYTES-1:0] bufer;

    assign inicio_mensaje = palabra_valida && (contador == {W_CNT{1'b0}});

    integer wi, bl;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            contador   <= {W_CNT{1'b0}};
            bufer      <= {(8*BYTES){1'b0}};
            msg_valido <= 1'b0;
            // Los campos NO se resetean acá: son una vista combinacional del
            // búfer (ver el always @(*) de abajo) y el búfer sí se resetea.
            // Dos bloques manejando el mismo reg sería un cortocircuito.
        end else begin
            msg_valido <= 1'b0;

            if (palabra_valida) begin
                // Escritura con índice CONSTANTE por rama: el bucle se
                // desenrolla en tiempo de elaboración y el `contador == wi`
                // queda como un decodificador, no como un shifter variable.
                // Es la misma razón por la que `etapa_ingesta.v` usa un `case`
                // y no un desplazamiento — está explicado ahí y vale igual acá.
                for (wi = 0; wi < N_PALABRAS; wi = wi + 1)
                    if (contador == wi[W_CNT-1:0])
                        for (bl = 0; bl < B; bl = bl + 1)
                            if (wi * B + bl < BYTES)
                                bufer[(wi*B + bl)*8 +: 8] <= palabra_dato[bl*8 +: 8];

                if (contador == (N_PALABRAS - 1)) begin
                    contador   <= {W_CNT{1'b0}};
                    msg_valido <= 1'b1;
                end else begin
                    contador <= contador + {{(W_CNT-1){1'b0}}, 1'b1};
                end
            end
        end
    end

    // Los campos se publican combinacionalmente desde el búfer. Se muestrean
    // el mismo ciclo en que msg_valido está alto, igual que en la versión byte
    // a byte, salvo por la última palabra: por eso los recortes miran el búfer
    // y la última palabra escrita a la vez no hace falta — msg_valido es un
    // pulso RETRASADO un ciclo respecto de la última escritura, así que el
    // búfer ya está completo cuando la etapa 2 lo lee.
    always @(*) begin
        ts_ns          = bufer[63:0];
        id_instrumento = bufer[95:64];
        precio_fp      = bufer[159:96];
        cantidad       = bufer[191:160];
        lado           = bufer[199:192];
        flags          = bufer[207:200];
        reservado      = bufer[223:208];
    end

endmodule
