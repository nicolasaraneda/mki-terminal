`include "mki_definiciones.vh"

// ETAPA 4 — DECISIÓN (comparador doble contra dos umbrales).
//
// Advertencia de alcance, porque el nombre de las señales invita al malentendido:
// COMPRA/VENTA acá son ETIQUETAS DE UNA SALIDA DIGITAL, no órdenes. La
// Constitución 5.0 de MKI prohíbe dinero real y órdenes a bróker, y
// piso_de_latencia.md ya demostró que no hay ventaja capturable en vivo con
// esta plataforma. Esto es un comparador de tres estados en RTL para un
// proyecto de Arquitectura de Computadores.
//
// Los umbrales son parámetros y no puertos: en la placa serían constantes
// cableadas (RTL.md §5 lo permite explícitamente) y como parámetros el
// sintetizador puede podar la mitad del comparador si el umbral es una
// potencia de dos — que es información real sobre el costo, no una trampa.
//
// Por qué dos comparadores y no uno con signo: un solo umbral daría
// COMPRA/VENTA sin zona muerta, y todo puntaje distinto de cero sería una
// decisión. La banda MANTENER es lo que hace que la decisión signifique algo.

module etapa_decision #(
    // Q8.8. 128 = 0.50 pp de gap esperado. Es un umbral ACADÉMICO elegido
    // para que las tres decisiones aparezcan en el vector real de validación,
    // no una regla de trading que el proyecto sostenga.
    parameter signed [`MKI_ANCHO_FEATURE-1:0] UMBRAL_ALZA = 16'sd128,
    parameter signed [`MKI_ANCHO_FEATURE-1:0] UMBRAL_BAJA = -16'sd128
) (
    input  wire clk,
    input  wire rst_n,

    input  wire                                puntaje_valido,
    input  wire signed [`MKI_ANCHO_FEATURE-1:0] puntaje,

    output reg  [1:0] decision,
    output reg        decision_valida
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            decision        <= `MKI_MANTENER;
            decision_valida <= 1'b0;
        end else begin
            decision_valida <= puntaje_valido;
            // Comparación ESTRICTA en ambos lados: un puntaje exactamente
            // igual al umbral cae en MANTENER. La regla se fija acá y el
            // modelo de referencia la copia; si quedara ambigua, un empate
            // exacto (que en punto fijo pasa: la rejilla es discreta y los
            // empates son frecuentes) haría diferir RTL y referencia sin que
            // ninguno de los dos esté "mal".
            if (puntaje > UMBRAL_ALZA)
                decision <= `MKI_COMPRA;
            else if (puntaje < UMBRAL_BAJA)
                decision <= `MKI_VENTA;
            else
                decision <= `MKI_MANTENER;
        end
    end

endmodule
