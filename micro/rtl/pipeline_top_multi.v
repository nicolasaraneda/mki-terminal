`include "mki_definiciones.vh"

// VARIANTE 1 DEL ESPACIO DE DISEÑO — UN pipeline, TABLA de pesos por
// instrumento, multiplexado en el tiempo.
//
// POR QUÉ ÉSTA Y NO OTRA. No se eligió por impresionar: la eligieron los
// propios documentos del proyecto, dos veces y sin que nadie la construyera.
//   · `SINTESIS_A7.md` §3.5: "la forma correcta de servir 8 tickers no es 8
//     pipelines: es uno multiplexado en el tiempo, y sobra tanto que ni
//     siquiera hace falta multiplexar bien".
//   · `SINTESIS_A7.md` §4.2: lo único que el margen habilita en esa línea y
//     "hoy no existe" es "un banco de pesos por instrumento en vez del
//     registro único de configuración", indexado por `id_instrumento` — "el
//     campo ya viaja en el mensaje de 28 bytes y hoy sólo se usa para sellar".
//   · `multi_top.v`, en su propio encabezado: "ALTERNATIVA NO IMPLEMENTADA, Y
//     ES LA QUE PROBABLEMENTE CORRESPONDE".
// Tres documentos nombran la misma pieza faltante. Esto la construye y la mide.
//
// QUÉ CAMBIA Y QUÉ NO. Cambia UNA cosa: de dónde salen los pesos. Antes, un
// banco de 6 registros escrito por puerto, el mismo para todo mensaje — o sea
// UN instrumento por bitstream. Ahora, una tabla de T instrumentos y el
// mensaje elige su fila con los bits bajos de `id_instrumento`. Las etapas 2 a
// 5 son LAS MISMAS instancias, sin un cambio, igual que en
// `pipeline_top_ancho.v`.
//
// PREDICCIÓN ESCRITA ANTES DE MEDIR (el banco falla si no se cumple):
//   1. La latencia NO cambia: sigue siendo ceil(28/B) + 4. La lectura de la
//      tabla es SÍNCRONA y ocurre en el mismo flanco en que `etapa_features`
//      registra las features, así que el peso llega el ciclo en que
//      `etapa_puntaje` lo muestrea. No se agrega ninguna etapa.
//   2. Los 181 vectores sellados reproducen BIT A BIT, porque la aritmética no
//      se toca: sólo cambia el origen del operando.
//
// ALCANCE HONESTO — lo que esta variante NO resuelve. `etapa_features`
// mantiene UNA ventana rodante de N_VENTANA valores, y esa ventana es estado
// POR INSTRUMENTO. En la configuración campeona (N_FEATURES=1) eso no importa:
// la única feature usada es g0 = f0, función pura del mensaje, y el
// sintetizador ni siquiera conserva la ventana. Pero para N_FEATURES >= 2 la
// feature g1 usa la media rodante, y multiplexar en el tiempo sin replicar la
// ventana MEZCLARÍA la historia de dos tickers — un error de corrección, no de
// área. Se declara acá porque el campeón no lo expone y sería exactamente el
// tipo de cosa que se descubre tarde.

`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif
`ifndef CFG_B
  `define CFG_B 4
`endif
`ifndef CFG_T
  `define CFG_T 8
`endif

module pipeline_top_multi #(
    parameter integer B            = `CFG_B,
    parameter integer T            = `CFG_T,   // instrumentos en la tabla
    // LOG_T va como parameter y no como localparam porque se usa en la lista
    // de puertos, y un localparam del cuerpo todavia no existe ahi. No se
    // sobrescribe nunca: se deriva de T.
    parameter integer LOG_T        = (T <= 1) ? 1 : $clog2(T),
    parameter integer N_FEATURES   = `CFG_NF,
    parameter integer USAR_PESOS   = `CFG_PESOS,
    parameter integer N_VENTANA    = 10,
    parameter integer RECIPROCO_Q16 = 6554,
    parameter integer DIVISOR_UART = 104,
    parameter signed [`MKI_ANCHO_FEATURE-1:0] UMBRAL_ALZA =  16'sd128,
    parameter signed [`MKI_ANCHO_FEATURE-1:0] UMBRAL_BAJA = -16'sd128
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        palabra_valida,
    input  wire [8*B-1:0] palabra_dato,
    // Escritura de la tabla: ahora lleva SLOT además de índice de peso.
    input  wire        peso_we,
    input  wire [LOG_T-1:0] peso_slot,
    input  wire [2:0]  peso_idx,
    input  wire signed [`MKI_ANCHO_PESO-1:0] peso_dato,
    input  wire        enviar_uart,
    output wire [1:0]  decision_sellada,
    output wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje_sellado,
    output wire [31:0] id_sellado,
    output wire [47:0] ciclo_sellado,
    output wire [31:0] latencia_ciclos,
    output wire        sello_valido,
    output wire        saturo,
    output wire        uart_tx_linea
);
    wire [63:0] ts_ns;
    wire [31:0] id_instrumento;
    wire [63:0] precio_fp;
    wire [31:0] cantidad;
    wire [7:0]  lado, flags;
    wire [15:0] reservado;
    wire        msg_valido;
    wire        inicio_mensaje;

    etapa_ingesta_ancha #(.B(B)) u_ingesta (
        .clk(clk), .rst_n(rst_n),
        .palabra_valida(palabra_valida), .palabra_dato(palabra_dato),
        .ts_ns(ts_ns), .id_instrumento(id_instrumento),
        .precio_fp(precio_fp), .cantidad(cantidad),
        .lado(lado), .flags(flags), .reservado(reservado),
        .msg_valido(msg_valido), .inicio_mensaje(inicio_mensaje)
    );

    // -----------------------------------------------------------------------
    // LA TABLA. T instrumentos x 6 pesos. Se leen sólo N_FEATURES entradas:
    // pedir seis lecturas cuando el modelo usa una obligaría al sintetizador a
    // replicar la memoria seis veces y el costo medido sería el de un diseño
    // que nadie quiere. Las entradas no leídas quedan en cero, que es lo mismo
    // que hacía el banco único cuando N_FEATURES < 6.
    // -----------------------------------------------------------------------
    reg signed [`MKI_ANCHO_PESO-1:0] tabla [0:T*6-1];
    integer j;
    always @(posedge clk) begin
        if (peso_we)
            tabla[peso_slot*6 + peso_idx] <= peso_dato;
    end

    // El slot lo elige el MENSAJE, con los bits bajos de id_instrumento. Se
    // usan los bits bajos y no un mapeo: el id sellado es un entero denso y
    // cualquier tabla de traducción sería una decisión de alcance que nadie
    // tomó. Con T potencia de dos esto es cableado puro.
    // Con T=1 la tabla tiene una sola fila y el id no elige nada: forzar el
    // cero evita un indice fuera de rango que en simulacion daria X y en
    // sintesis daria logica muerta. T=1 existe para que el barrido tenga un
    // punto de comparacion con el banco unico de hoy.
    //
    // CONTRAPRUEBA. Un banco de pruebas que nunca falla no prueba nada. Con
    // `-DCFG_SABOTAJE_SLOT` el slot se fuerza a 0 — o sea, el decodificador se
    // rompe a propósito — y `tb/tb_pipeline_multi.v` TIENE que fallar. Si con
    // el sabotaje puesto sigue dando 181/181, entonces los señuelos no
    // discriminan y el test verde no significaba nada. Es la misma técnica que
    // GEMELO usa para demostrar que su prueba de causalidad puede fallar
    // (inyectar un `shift(-1)`). El define NO está activo por defecto.
`ifdef CFG_SABOTAJE_SLOT
    wire [LOG_T-1:0] slot = {LOG_T{1'b0}};
`else
    wire [LOG_T-1:0] slot = (T <= 1) ? {LOG_T{1'b0}} : id_instrumento[LOG_T-1:0];
`endif

    // Lectura SÍNCRONA en el mismo flanco en que etapa_features registra las
    // features: el peso queda disponible el ciclo en que etapa_puntaje lo
    // muestrea. Por eso la latencia no cambia (predicción 1 de arriba).
    reg signed [`MKI_ANCHO_PESO-1:0] w [0:5];
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (j = 0; j < 6; j = j + 1) w[j] <= {`MKI_ANCHO_PESO{1'b0}};
        end else if (msg_valido) begin
            for (j = 0; j < 6; j = j + 1)
                w[j] <= (j < N_FEATURES) ? tabla[slot*6 + j]
                                         : {`MKI_ANCHO_PESO{1'b0}};
        end
    end

    wire signed [`MKI_ANCHO_FEATURE-1:0] g0, g1, g2, g3, g4, g5;
    wire features_validas;

    etapa_features #(
        .N_VENTANA(N_VENTANA), .RECIPROCO_Q16(RECIPROCO_Q16)
    ) u_features (
        .clk(clk), .rst_n(rst_n),
        .msg_valido(msg_valido),
        .precio_fp(precio_fp), .cantidad(cantidad),
        .g0(g0), .g1(g1), .g2(g2), .g3(g3), .g4(g4), .g5(g5),
        .features_validas(features_validas)
    );

    wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje;
    wire puntaje_valido;

    etapa_puntaje #(
        .N_FEATURES(N_FEATURES), .USAR_PESOS(USAR_PESOS)
    ) u_puntaje (
        .clk(clk), .rst_n(rst_n),
        .features_validas(features_validas),
        .g0(g0), .g1(g1), .g2(g2), .g3(g3), .g4(g4), .g5(g5),
        .w0(w[0]), .w1(w[1]), .w2(w[2]), .w3(w[3]), .w4(w[4]), .w5(w[5]),
        .puntaje(puntaje), .puntaje_valido(puntaje_valido), .saturo(saturo)
    );

    wire [1:0] decision;
    wire decision_valida;

    etapa_decision #(
        .UMBRAL_ALZA(UMBRAL_ALZA), .UMBRAL_BAJA(UMBRAL_BAJA)
    ) u_decision (
        .clk(clk), .rst_n(rst_n),
        .puntaje_valido(puntaje_valido), .puntaje(puntaje),
        .decision(decision), .decision_valida(decision_valida)
    );

    etapa_salida #(
        .DIVISOR_UART(DIVISOR_UART)
    ) u_salida (
        .clk(clk), .rst_n(rst_n),
        .inicio_mensaje(inicio_mensaje),
        .decision_valida(decision_valida), .decision(decision),
        .puntaje(puntaje), .id_instrumento(id_instrumento),
        .decision_sellada(decision_sellada),
        .puntaje_sellado(puntaje_sellado),
        .id_sellado(id_sellado),
        .ciclo_sellado(ciclo_sellado),
        .latencia_ciclos(latencia_ciclos),
        .sello_valido(sello_valido),
        .uart_tx_linea(uart_tx_linea),
        .enviar_uart(enviar_uart)
    );

endmodule
