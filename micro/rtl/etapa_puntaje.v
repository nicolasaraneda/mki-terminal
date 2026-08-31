`include "mki_definiciones.vh"

// ETAPA 3 — PUNTAJE (MAC: combinación lineal de N_FEATURES features).
//
// Ésta es LA etapa del proyecto. RTL.md §2 predijo que cada feature adicional
// cuesta +200 a +300 LUTs en un iCE40 (que no tiene multiplicador dedicado) y
// que a partir de F=6 el pipeline no cabe en la placa. Todo el módulo está
// parametrizado en N_FEATURES precisamente para poder sintetizar F=1, F=3 y
// F=6 y contrastar esa predicción contra el reporte real del sintetizador.
//
// F=1 NO es un juguete: el modelo campeón 4.6.0 de MKI es literalmente
//   apertura_estimada_pct = beta × ultimo_movimiento_no_cero_del_SOX
// una sola multiplicación, sin intercepto. F=3 y F=6 son la generalización
// que mide cómo escala el área, no un modelo que el proyecto afirme tener.
//
// Aritmética, sin margen para interpretaciones (el modelo de referencia en
// referencia.py replica esto bit a bit):
//   feature  Q8.8   → 8 bits fraccionarios
//   peso     Q2.14  → 14 bits fraccionarios
//   producto Q10.22 → 22 bits fraccionarios, 32 bits con signo
//   acumulado: 32 + ceil(log2(F)) bits, dimensionado por fórmula
//   puntaje  Q8.8   ← acumulado >>> 14, con SATURACIÓN (no wrap)
//
// Por qué saturación y no envolvimiento: un puntaje que desborda y cambia de
// signo produce la decisión OPUESTA a la correcta. Saturar produce la
// decisión correcta llevada al extremo. Entre dos formas de estar mal, la que
// no invierte el signo es estrictamente mejor. El testbench verifica que
// sobre los vectores reales la saturación nunca se activa — o sea que el
// rango elegido en RTL.md §3 aguanta —, pero el circuito la tiene igual.
//
// Por qué desplazamiento aritmético (truncado hacia -infinito) y no redondeo:
// el redondeo al más cercano cuesta un sumador de 32 bits más un comparador
// por cada acumulación. El truncado es cableado puro. El sesgo que introduce
// es de medio LSB de Q8.8 (0.00195 pp) SIEMPRE hacia abajo, y ese sesgo se
// mide en el arnés en vez de suponerse despreciable.

// Valores por defecto desde macros para que esta etapa se pueda sintetizar
// SOLA con `yosys -DCFG_NF=3` (ver medir_etapas.py). Instanciada desde
// pipeline_top los parámetros llegan explícitos y estos no se usan.
`ifndef CFG_NF
  `define CFG_NF 1
`endif
`ifndef CFG_PESOS
  `define CFG_PESOS 1
`endif

module etapa_puntaje #(
    parameter integer N_FEATURES = `CFG_NF,
    // USAR_PESOS=0 sintetiza la variante "solo umbral, sin multiplicar" que
    // RTL.md §2 estima aparte (~20-30 LUTs). Existe para AISLAR el costo del
    // multiplicador: (área con pesos) - (área sin pesos) es el costo del MAC
    // y de nada más. Sin este punto de medición habría que creerle a una
    // resta entre dos diseños que difieren en más de una cosa.
    parameter integer USAR_PESOS = `CFG_PESOS
) (
    input  wire clk,
    input  wire rst_n,

    input  wire features_validas,
    input  wire signed [`MKI_ANCHO_FEATURE-1:0] g0,
    input  wire signed [`MKI_ANCHO_FEATURE-1:0] g1,
    input  wire signed [`MKI_ANCHO_FEATURE-1:0] g2,
    input  wire signed [`MKI_ANCHO_FEATURE-1:0] g3,
    input  wire signed [`MKI_ANCHO_FEATURE-1:0] g4,
    input  wire signed [`MKI_ANCHO_FEATURE-1:0] g5,

    // Pesos precargados. RTL.md §5 lo deja explícito: NADA se entrena en la
    // FPGA; los pesos se calculan fuera y entran por un registro de
    // configuración. Acá entran como puerto y el banco de registros vive en
    // el top — así esta etapa queda como función pura y es testeable sola.
    input  wire signed [`MKI_ANCHO_PESO-1:0] w0,
    input  wire signed [`MKI_ANCHO_PESO-1:0] w1,
    input  wire signed [`MKI_ANCHO_PESO-1:0] w2,
    input  wire signed [`MKI_ANCHO_PESO-1:0] w3,
    input  wire signed [`MKI_ANCHO_PESO-1:0] w4,
    input  wire signed [`MKI_ANCHO_PESO-1:0] w5,

    output reg signed [`MKI_ANCHO_FEATURE-1:0] puntaje,   // Q8.8
    output reg                                 puntaje_valido,
    output reg                                 saturo       // testigo de saturación
);

    localparam integer WF = `MKI_ANCHO_FEATURE;
    localparam integer WP = `MKI_ANCHO_PESO;
    localparam integer W_PROD = WF + WP;                  // 32
    // Ancho del acumulador por fórmula: F sumandos de W_PROD bits necesitan
    // W_PROD + ceil(log2(F)). Se usa +3 (alcanza hasta F=8) en vez de un
    // $clog2 para que el ancho no cambie entre configuraciones y las
    // comparaciones de área midan el MAC, no un acumulador que se encogió.
    localparam integer W_ACC = W_PROD + 3;                // 35

    wire signed [WF-1:0] g [0:5];
    wire signed [WP-1:0] w [0:5];
    assign g[0]=g0; assign g[1]=g1; assign g[2]=g2;
    assign g[3]=g3; assign g[4]=g4; assign g[5]=g5;
    assign w[0]=w0; assign w[1]=w1; assign w[2]=w2;
    assign w[3]=w3; assign w[4]=w4; assign w[5]=w5;

    // --- Sub-etapa A: los productos, registrados ---
    // Registrar acá y no dejar todo combinacional es lo que evita que la ruta
    // crítica sea (multiplicador + árbol de sumas + saturación) de una sola
    // vez. Cuesta un ciclo de latencia FIJO y compra frecuencia. El ciclo se
    // paga siempre, en todos los mensajes: la latencia sigue siendo constante,
    // que es la propiedad que este pipeline afirma tener.
    reg signed [W_PROD-1:0] prod [0:5];
    reg                     etapa_a_valida;

    genvar k;
    integer j;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            etapa_a_valida <= 1'b0;
            for (j = 0; j < 6; j = j + 1)
                prod[j] <= {W_PROD{1'b0}};
        end else begin
            etapa_a_valida <= features_validas;
            for (j = 0; j < 6; j = j + 1) begin
                if (j < N_FEATURES) begin
                    if (USAR_PESOS != 0)
                        prod[j] <= g[j] * w[j];
                    else
                        // Sin pesos: la feature se lleva al mismo formato
                        // Q10.22 desplazando 14 bits. Es cableado, no un
                        // multiplicador — que es exactamente el punto de
                        // esta variante.
                        prod[j] <= $signed({{(W_PROD-WF){g[j][WF-1]}}, g[j]}) <<< `MKI_FRAC_PESO;
                end else begin
                    // Las features por encima de N_FEATURES se fuerzan a cero
                    // para que el sintetizador PODE de verdad el multiplicador
                    // y el área medida corresponda a la F declarada.
                    prod[j] <= {W_PROD{1'b0}};
                end
            end
        end
    end

    // --- Sub-etapa B: suma, desplazamiento y saturación ---
    reg signed [W_ACC-1:0] acumulado;
    always @(*) begin
        acumulado = {W_ACC{1'b0}};
        for (j = 0; j < 6; j = j + 1)
            if (j < N_FEATURES)
                acumulado = acumulado + {{(W_ACC-W_PROD){prod[j][W_PROD-1]}}, prod[j]};
    end

    // Q10.22 → Q8.8 es un desplazamiento de 14 a la derecha.
    wire signed [W_ACC-1:0] desplazado = acumulado >>> `MKI_FRAC_PESO;
    // Desborda si los bits altos no son todos iguales al bit de signo del
    // resultado de 16 bits — la comprobación canónica de saturación.
    wire desborda_pos = (!desplazado[W_ACC-1]) && (|desplazado[W_ACC-2:WF-1]);
    wire desborda_neg = ( desplazado[W_ACC-1]) && (!(&desplazado[W_ACC-2:WF-1]));

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            puntaje        <= {WF{1'b0}};
            puntaje_valido <= 1'b0;
            saturo         <= 1'b0;
        end else begin
            puntaje_valido <= etapa_a_valida;
            if (desborda_pos) begin
                puntaje <= {1'b0, {(WF-1){1'b1}}};   // +32767 = +127.996 en Q8.8
                saturo  <= etapa_a_valida;
            end else if (desborda_neg) begin
                puntaje <= {1'b1, {(WF-1){1'b0}}};   // -32768 = -128.0 en Q8.8
                saturo  <= etapa_a_valida;
            end else begin
                puntaje <= desplazado[WF-1:0];
                saturo  <= 1'b0;
            end
        end
    end

endmodule
