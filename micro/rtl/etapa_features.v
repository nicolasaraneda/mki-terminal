`include "mki_definiciones.vh"

// ETAPA 2 — ESTADO / FEATURES.
//
// Mantiene el ÚNICO estado con memoria del pipeline: una ventana rodante de
// N_VENTANA mensajes sobre la observable primaria. Todo lo demás del pipeline
// es una función pura del mensaje actual.
//
// Por qué suma corrida y no volver a sumar N cada vez: sumar la ventana
// entera en un ciclo son N-1 sumadores encadenados; la suma corrida son DOS
// (sumar el que entra, restar el que sale) sin importar cuánto valga N. Es la
// diferencia entre que N sea un parámetro libre y que N sea el techo del
// diseño. Esto ya estaba escrito en RTL.md §1.2 y acá se cumple literal.
//
// Por qué el recíproco constante y no un divisor: N=10 no es potencia de dos,
// así que la media no sale de un desplazamiento. Un divisor general en un
// iCE40 (sin DSP) es carísimo. Multiplicar por una constante precalculada
// (65536/N) NO es un multiplicador general: el sintetizador lo colapsa a un
// puñado de sumas y desplazamientos porque uno de los operandos es fijo en
// tiempo de síntesis. La aproximación que introduce se mide en el testbench,
// no se supone.
//
// Calentamiento: tras el reset la ventana está en cero, así que los primeros
// N_VENTANA-1 mensajes tienen una media sesgada hacia abajo. NO se corrige.
// Corregirlo exigiría un contador de ocupación y una división por un valor
// variable — precisamente el divisor que se acaba de evitar. El modelo de
// referencia replica el mismo sesgo, así que la comparación sigue siendo
// válida; el testbench lo declara en vez de esconderlo.

module etapa_features #(
    parameter integer N_VENTANA = 10,
    // 65536/N_VENTANA redondeado. Para N=10 da 6554 (el valor exacto es
    // 6553.6). El error relativo resultante es ~6e-6 y se mide en el arnés.
    parameter integer RECIPROCO_Q16 = 6554
) (
    input  wire        clk,
    input  wire        rst_n,

    input  wire        msg_valido,
    input  wire [63:0] precio_fp,   // empaqueta f0..f3 en Q8.8
    input  wire [31:0] cantidad,    // empaqueta f4..f5 en Q8.8

    // Vector de features hacia la etapa de puntaje. Índice fijo:
    //   g0 = f0                      (observable primaria, pasa directo)
    //   g1 = f0 - media_rodante(f0)  (la ÚNICA feature derivada del estado)
    //   g2..g5 = f1..f4              (features ya calculadas fuera del chip)
    output reg  signed [`MKI_ANCHO_FEATURE-1:0] g0,
    output reg  signed [`MKI_ANCHO_FEATURE-1:0] g1,
    output reg  signed [`MKI_ANCHO_FEATURE-1:0] g2,
    output reg  signed [`MKI_ANCHO_FEATURE-1:0] g3,
    output reg  signed [`MKI_ANCHO_FEATURE-1:0] g4,
    output reg  signed [`MKI_ANCHO_FEATURE-1:0] g5,
    output reg                                  features_validas
);

    localparam integer W    = `MKI_ANCHO_FEATURE;
    // La suma nunca puede desbordar: N_VENTANA valores de W bits necesitan
    // W + ceil(log2(N)) bits. Se dimensiona por fórmula y no con un "20 que
    // seguro alcanza", porque un N mayor lo rompería en silencio.
    localparam integer W_SUMA = W + 5;   // alcanza hasta N_VENTANA = 32

    // Desempaquetado del payload. Los campos precio_fp y cantidad conservan
    // su ancho y posición EXACTOS del formato de 28 bytes de bench_mensaje.c
    // — el formato no se tocó; lo que cambia es qué significa el payload en
    // el vector de validación, y eso está declarado en TOOLCHAIN.md.
    wire signed [W-1:0] f0 = precio_fp[15:0];
    wire signed [W-1:0] f1 = precio_fp[31:16];
    wire signed [W-1:0] f2 = precio_fp[47:32];
    wire signed [W-1:0] f3 = precio_fp[63:48];
    wire signed [W-1:0] f4 = cantidad[15:0];
    // cantidad[31:16] queda reservado: hay lugar para una séptima feature sin
    // volver a tocar el formato de wire. Se deja explícito para que nadie
    // "descubra" espacio libre y lo use sin declararlo.

    reg signed [W-1:0]      ventana [0:N_VENTANA-1];
    reg signed [W_SUMA-1:0] suma;

    // media = (suma * RECIPROCO_Q16) >>> 16. El producto necesita
    // W_SUMA + 17 bits con signo antes de desplazar.
    wire signed [W_SUMA+17:0] producto_media = $signed(suma) * $signed({1'b0, RECIPROCO_Q16[16:0]});
    wire signed [W-1:0]       media          = producto_media[W+15:16];

    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            suma             <= {W_SUMA{1'b0}};
            features_validas <= 1'b0;
            g0 <= {W{1'b0}}; g1 <= {W{1'b0}}; g2 <= {W{1'b0}};
            g3 <= {W{1'b0}}; g4 <= {W{1'b0}}; g5 <= {W{1'b0}};
            for (i = 0; i < N_VENTANA; i = i + 1)
                ventana[i] <= {W{1'b0}};
        end else begin
            features_validas <= 1'b0;

            if (msg_valido) begin
                // Suma corrida: entra f0, sale el más viejo. Dos sumadores.
                suma <= suma + {{(W_SUMA-W){f0[W-1]}}, f0}
                             - {{(W_SUMA-W){ventana[N_VENTANA-1][W-1]}}, ventana[N_VENTANA-1]};

                ventana[0] <= f0;
                for (i = 1; i < N_VENTANA; i = i + 1)
                    ventana[i] <= ventana[i-1];

                // La media que se usa es la de la ventana ANTERIOR a este
                // mensaje. Es deliberado y es la única versión causal: la
                // desviación de un valor contra una media que ya lo incluye
                // se contamina a sí misma. En el vocabulario de este
                // proyecto: la feature sería no causal.
                g0 <= f0;
                g1 <= f0 - media;
                g2 <= f1;
                g3 <= f2;
                g4 <= f3;
                g5 <= f4;

                features_validas <= 1'b1;
            end
        end
    end

endmodule
