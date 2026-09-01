// costo_a7.v — micro-mediciones aisladas para el estudio de la Arty A7-100T.
//
// POR QUÉ UN ARCHIVO APARTE Y NO AMPLIAR costo_multiplicador.v: ese archivo
// documenta en su cabecera los resultados MEDIDOS sobre iCE40 y publicados en
// GEMELO/MICRO/SINTESIS.md §3.1. Tocarlo obligaría a reverificar esas cifras.
// Acá van las piezas que la Arty A7 hace interesantes y que en un iCE40 no
// tenía sentido ni intentar (un divisor, una raíz, acumuladores de 48 bits).
//
// Todo se sintetiza SOLO, como su propio top, con
//   yosys -p "read_verilog costo_a7.v; synth_xilinx -family xc7 -top <mod>"
// para que ninguna entrada se vuelva constante y no haya nada que podar.
// Ver micro/rtl/medir_a7.py, que es quien las corre y tabula.
//
// REGLA DE LA CASA APLICADA ACÁ: el DSP48E1 tiene un multiplicador de 25x18
// (DS180, nota 2 de la Tabla 4). O sea que "cuántos DSP cuesta multiplicar"
// NO es una constante: depende del ancho, y salta de golpe cuando el operando
// pasa de 18 o de 25 bits. Las variantes de abajo existen para MEDIR ese salto
// en vez de razonarlo, porque es exactamente el número que decide el §4.4.3 de
// SINTESIS_A7.md.

// ---------------------------------------------------------------------------
// 1. Multiplicadores con signo de anchos crecientes.
//    a: W bits, b: W bits, producto 2W bits, registrado.
// ---------------------------------------------------------------------------
module mul_a7 #(parameter integer W = 16) (
    input  wire                 clk,
    input  wire signed [W-1:0]  a,
    input  wire signed [W-1:0]  b,
    output reg  signed [2*W-1:0] p
);
    always @(posedge clk) p <= a * b;
endmodule

module mul_a7_w8  (input wire clk, input wire signed [7:0]  a, input wire signed [7:0]  b, output reg signed [15:0] p);
    always @(posedge clk) p <= a * b;
endmodule
module mul_a7_w16 (input wire clk, input wire signed [15:0] a, input wire signed [15:0] b, output reg signed [31:0] p);
    always @(posedge clk) p <= a * b;
endmodule
module mul_a7_w18 (input wire clk, input wire signed [17:0] a, input wire signed [17:0] b, output reg signed [35:0] p);
    always @(posedge clk) p <= a * b;
endmodule
module mul_a7_w24 (input wire clk, input wire signed [23:0] a, input wire signed [23:0] b, output reg signed [47:0] p);
    always @(posedge clk) p <= a * b;
endmodule
module mul_a7_w25 (input wire clk, input wire signed [24:0] a, input wire signed [24:0] b, output reg signed [49:0] p);
    always @(posedge clk) p <= a * b;
endmodule
module mul_a7_w32 (input wire clk, input wire signed [31:0] a, input wire signed [31:0] b, output reg signed [63:0] p);
    always @(posedge clk) p <= a * b;
endmodule
// Asimétrico 25x18: el multiplicador NATIVO del DSP48E1. Es la cota inferior
// contra la que hay que leer todas las de arriba.
module mul_a7_25x18 (input wire clk, input wire signed [24:0] a, input wire signed [17:0] b, output reg signed [42:0] p);
    always @(posedge clk) p <= a * b;
endmodule

// ---------------------------------------------------------------------------
// 2. Lo que hoy NO está en el pipeline y haría falta para replicar al 4.6.0
//    COMPLETO en silicio (ver SINTESIS_A7.md §4.3).
//
//    motor.betas_al hace, sobre una ventana rodante de 120 sesiones:
//      beta = cov(x,y)/var(x)          -> UNA DIVISIÓN
//      alfa = mean(y) - beta*mean(x)   -> dos divisiones por N y un producto
//      r2   = corr(x,y)^2              -> otra división
//      resid_std = sqrt(sum(r^2)/(n-1))-> UNA RAÍZ CUADRADA y otra división
//    y motor.prediccion_apertura_al agrega
//      intervalo80 = 1.2816 * resid_std -> un producto por constante
//
//    Ninguna de esas tres piezas —divisor, raíz, acumuladores de momentos—
//    existe hoy en micro/rtl/. Acá se miden por separado para poder decir
//    cuánto cuesta cerrar la brecha, en vez de decir "cabe" a ojo.
// ---------------------------------------------------------------------------

// 2a. Divisor 32/32 con signo, COMBINACIONAL (registrado a la salida).
//     Es a propósito el caso caro: es la forma en que un programador lo
//     escribiría sin pensar, y sirve de cota superior.
module div32_comb (
    input  wire               clk,
    input  wire signed [31:0] num,
    input  wire signed [31:0] den,
    output reg  signed [31:0] q
);
    always @(posedge clk) q <= (den == 0) ? 32'sd0 : num / den;
endmodule

// 2b. Divisor 32/32 SIN signo, restaurador, un bit por ciclo (32 ciclos).
//     Es la forma sensata en hardware: área chica y latencia FIJA — que es la
//     propiedad que este proyecto entero afirma tener. Un divisor combinacional
//     tampoco tiene cola, pero se come la frecuencia; éste no.
module div32_serie (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        arranca,
    input  wire [31:0] num,
    input  wire [31:0] den,
    output reg  [31:0] cociente,
    output reg  [31:0] resto,
    output reg         listo
);
    reg [31:0] n_reg, d_reg, q_reg;
    reg [32:0] r_reg;
    reg [5:0]  i;
    reg        ocupado;
    wire [32:0] r_desp = {r_reg[31:0], n_reg[31]};
    wire [32:0] r_menos = r_desp - {1'b0, d_reg};

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ocupado <= 1'b0; listo <= 1'b0; i <= 6'd0;
            n_reg <= 32'd0; d_reg <= 32'd0; q_reg <= 32'd0; r_reg <= 33'd0;
            cociente <= 32'd0; resto <= 32'd0;
        end else begin
            listo <= 1'b0;
            if (!ocupado) begin
                if (arranca) begin
                    n_reg <= num; d_reg <= den; q_reg <= 32'd0; r_reg <= 33'd0;
                    i <= 6'd0; ocupado <= 1'b1;
                end
            end else begin
                if (r_menos[32] == 1'b0) begin
                    r_reg <= r_menos;
                    q_reg <= {q_reg[30:0], 1'b1};
                end else begin
                    r_reg <= r_desp;
                    q_reg <= {q_reg[30:0], 1'b0};
                end
                n_reg <= {n_reg[30:0], 1'b0};
                if (i == 6'd31) begin
                    ocupado  <= 1'b0;
                    listo    <= 1'b1;
                    cociente <= (r_menos[32] == 1'b0) ? {q_reg[30:0], 1'b1}
                                                      : {q_reg[30:0], 1'b0};
                    resto    <= (r_menos[32] == 1'b0) ? r_menos[31:0] : r_desp[31:0];
                end else begin
                    i <= i + 6'd1;
                end
            end
        end
    end
endmodule

// 2c. Raíz cuadrada entera de 48 bits -> 24 bits, no restauradora, dos bits
//     por iteración (24 ciclos). Es lo que exige `resid_std` y por lo tanto el
//     intervalo del 80%, que la Constitución 5.0 obliga a mostrar SIEMPRE al
//     lado de la señal. Sin esto el pipeline no puede emitir una fila sellada
//     completa: emite el punto pero no su incertidumbre.
module sqrt48 (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        arranca,
    input  wire [47:0] x,
    output reg  [23:0] raiz,
    output reg         listo
);
    reg [47:0] resto_r, x_reg;
    reg [23:0] q_reg;
    reg [4:0]  i;
    reg        ocupado;
    wire [49:0] r_desp = {resto_r[45:0], x_reg[47:46]};
    wire [49:0] r_menos = r_desp - {q_reg, 2'b01};

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ocupado <= 1'b0; listo <= 1'b0; i <= 5'd0;
            resto_r <= 48'd0; x_reg <= 48'd0; q_reg <= 24'd0; raiz <= 24'd0;
        end else begin
            listo <= 1'b0;
            if (!ocupado) begin
                if (arranca) begin
                    x_reg <= x; resto_r <= 48'd0; q_reg <= 24'd0;
                    i <= 5'd0; ocupado <= 1'b1;
                end
            end else begin
                if (!r_menos[49]) begin
                    resto_r <= r_menos[47:0];
                    q_reg   <= {q_reg[22:0], 1'b1};
                end else begin
                    resto_r <= r_desp[47:0];
                    q_reg   <= {q_reg[22:0], 1'b0};
                end
                x_reg <= {x_reg[45:0], 2'b00};
                if (i == 5'd23) begin
                    ocupado <= 1'b0;
                    listo   <= 1'b1;
                    raiz    <= (!r_menos[49]) ? {q_reg[22:0], 1'b1} : {q_reg[22:0], 1'b0};
                end else begin
                    i <= i + 5'd1;
                end
            end
        end
    end
endmodule

// 2d. Acumuladores de momentos para una regresión rodante de N sesiones.
//     Suma corrida de sum(x), sum(y), sum(xy), sum(x2) — la misma técnica de
//     etapa_features.v (entra uno, sale el más viejo), extendida a cuatro
//     acumuladores. Es lo que betas_al necesita ANTES de dividir.
//
//     La ventana vive en registros; a N=120 son 2 x 120 x 16 = 3.840 bits.
//     En un iCE40 eso son 240 LCs de puro almacenamiento; en la A7 es media
//     BRAM de 36 Kb. Ésa es una de las tres cosas que la placa nueva compra y
//     por eso el módulo se mide en las dos familias.
module momentos_rodantes #(
    parameter integer W = 16,
    parameter integer N = 120
) (
    input  wire                clk,
    input  wire                rst_n,
    input  wire                valido,
    input  wire signed [W-1:0] x,
    input  wire signed [W-1:0] y,
    output reg  signed [47:0]  sx,
    output reg  signed [47:0]  sy,
    output reg  signed [47:0]  sxy,
    output reg  signed [47:0]  sxx
);
    reg signed [W-1:0] vx [0:N-1];
    reg signed [W-1:0] vy [0:N-1];
    integer k;
    wire signed [W-1:0] x_sale = vx[N-1];
    wire signed [W-1:0] y_sale = vy[N-1];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sx <= 48'sd0; sy <= 48'sd0; sxy <= 48'sd0; sxx <= 48'sd0;
            for (k = 0; k < N; k = k + 1) begin
                vx[k] <= {W{1'b0}};
                vy[k] <= {W{1'b0}};
            end
        end else if (valido) begin
            sx  <= sx  + x - x_sale;
            sy  <= sy  + y - y_sale;
            sxy <= sxy + (x * y) - (x_sale * y_sale);
            sxx <= sxx + (x * x) - (x_sale * x_sale);
            vx[0] <= x; vy[0] <= y;
            for (k = 1; k < N; k = k + 1) begin
                vx[k] <= vx[k-1];
                vy[k] <= vy[k-1];
            end
        end
    end
endmodule
