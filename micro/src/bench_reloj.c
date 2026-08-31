#define _POSIX_C_SOURCE 200809L

/*
 * bench_reloj — resolución nominal y costo real de leer el reloj.
 *
 * Dos cosas distintas y ambas importan:
 *   1. clock_getres(): lo que el kernel DICE que puede resolver.
 *   2. Costo de la propia llamada clock_gettime(): el "impuesto" que paga
 *      cada medición de este arnés, medido llamando al reloj dos veces
 *      seguidas y restando. Todo lo que midan los demás benchmarks tiene
 *      este piso incorporado y no se puede medir nada por debajo de él.
 */

#include "comun.h"

#include <stdio.h>
#include <time.h>

#define N_MUESTRAS 200000
#define N_WARMUP 2000

int main(void) {
    struct timespec res;
    if (clock_getres(CLOCK_MONOTONIC_RAW, &res) != 0) {
        fprintf(stderr, "clock_getres falló\n");
        return 1;
    }
    uint64_t resolucion_ns = (uint64_t)res.tv_sec * 1000000000ULL + (uint64_t)res.tv_nsec;

    ColeccionMuestras c;
    cm_iniciar(&c, N_MUESTRAS);

    for (int i = 0; i < N_WARMUP + N_MUESTRAS; i++) {
        uint64_t t0 = ahora_ns();
        uint64_t t1 = ahora_ns();
        cm_agregar(&c, t1 - t0);
    }

    Percentiles p = cm_percentiles(&c, N_WARMUP);

    printf("resolución nominal reportada por clock_getres(CLOCK_MONOTONIC_RAW): %llu ns\n",
           (unsigned long long)resolucion_ns);
    imprimir_tabla("costo de clock_gettime (dos llamadas back-to-back, delta)", "ns", p);

    JsonBuilder jb;
    jb_iniciar(&jb);
    jb_str(&jb, "benchmark", "reloj");
    jb_str(&jb, "unidad", "ns");
    jb_u64(&jb, "resolucion_nominal_ns", resolucion_ns);
    jb_u64(&jb, "warmup_descartado_config", N_WARMUP);
    jb_percentiles(&jb, "costo_lectura", p);
    jb_str(&jb, "notas",
           "costo_lectura mide el delta entre dos llamadas consecutivas a "
           "clock_gettime(CLOCK_MONOTONIC_RAW); es el piso de medición de "
           "todo el resto del arnés, no una latencia de aplicación");

    if (jb_escribir_archivo(&jb, "resultados/reloj.json") != 0) {
        fprintf(stderr, "no se pudo escribir micro/resultados/reloj.json\n");
        return 1;
    }

    cm_liberar(&c);
    return 0;
}
