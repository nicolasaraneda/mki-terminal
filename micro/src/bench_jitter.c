#define _POSIX_C_SOURCE 200809L

/*
 * bench_jitter — jitter del planificador: se pide dormir N microsegundos
 * exactos con nanosleep() y se mide cuánto duerme DE VERDAD el proceso.
 *
 * jitter = duración_real - duración_pedida (siempre >= 0 salvo error de
 * medición: nanosleep no puede despertar antes de tiempo salvo por señal,
 * y este proceso no instala manejadores de señal).
 *
 * Esto es también el benchmark que usa tests/test_arnes.sh para verificar
 * que el arnés mide lo que dice medir: una espera conocida (1000 us) tiene
 * que reportarse dentro de una tolerancia razonable.
 */

#include "comun.h"

#include <stdio.h>
#include <time.h>

typedef struct {
    const char *nombre;
    uint64_t objetivo_us;
    int iteraciones;
    int warmup;
} ObjetivoSueno;

static const ObjetivoSueno OBJETIVOS[] = {
    {"10us", 10, 3000, 100},
    {"100us", 100, 3000, 100},
    {"1000us", 1000, 2000, 50},
    {"10000us", 10000, 300, 20},
};
#define N_OBJETIVOS (sizeof(OBJETIVOS) / sizeof(OBJETIVOS[0]))

int main(void) {
    JsonBuilder jb;
    jb_iniciar(&jb);
    jb_str(&jb, "benchmark", "jitter");
    jb_str(&jb, "unidad", "ns");
    jb_str(&jb, "metodo", "nanosleep(CLOCK_MONOTONIC_RAW implicito via timespec relativo)");

    for (size_t o = 0; o < N_OBJETIVOS; o++) {
        const ObjetivoSueno *obj = &OBJETIVOS[o];
        uint64_t objetivo_ns = obj->objetivo_us * 1000ULL;

        ColeccionMuestras actual, jitter;
        cm_iniciar(&actual, (size_t)obj->iteraciones);
        cm_iniciar(&jitter, (size_t)obj->iteraciones);

        for (int i = 0; i < obj->warmup + obj->iteraciones; i++) {
            struct timespec req;
            req.tv_sec = (time_t)(objetivo_ns / 1000000000ULL);
            req.tv_nsec = (long)(objetivo_ns % 1000000000ULL);

            uint64_t t0 = ahora_ns();
            /* Se ignora interrupción por señal: este proceso no las recibe
             * en uso normal; si nanosleep devuelve error, la muestra se
             * descarta explícitamente (no se finge un valor). */
            struct timespec restante;
            if (nanosleep(&req, &restante) != 0) {
                continue;
            }
            uint64_t t1 = ahora_ns();

            uint64_t dur = t1 - t0;
            cm_agregar(&actual, dur);
            uint64_t j = (dur >= objetivo_ns) ? (dur - objetivo_ns) : 0;
            cm_agregar(&jitter, j);
        }

        Percentiles p_actual = cm_percentiles(&actual, (size_t)obj->warmup);
        Percentiles p_jitter = cm_percentiles(&jitter, (size_t)obj->warmup);

        char titulo[128];
        snprintf(titulo, sizeof(titulo), "jitter — objetivo %s (duración real)", obj->nombre);
        imprimir_tabla(titulo, "ns", p_actual);
        snprintf(titulo, sizeof(titulo), "jitter — objetivo %s (exceso sobre lo pedido)", obj->nombre);
        imprimir_tabla(titulo, "ns", p_jitter);

        char clave[64];
        snprintf(clave, sizeof(clave), "objetivo_%s_ns", obj->nombre);
        jb_u64(&jb, clave, objetivo_ns);
        snprintf(clave, sizeof(clave), "real_%s", obj->nombre);
        jb_percentiles(&jb, clave, p_actual);
        snprintf(clave, sizeof(clave), "exceso_%s", obj->nombre);
        jb_percentiles(&jb, clave, p_jitter);

        cm_liberar(&actual);
        cm_liberar(&jitter);
    }

    jb_str(&jb, "notas",
           "exceso_* = duracion_real - duracion_pedida, nunca negativo por "
           "construccion; es la metrica que 1C usa como evidencia de jitter "
           "de WSL2 frente a una espera conocida");

    if (jb_escribir_archivo(&jb, "resultados/jitter.json") != 0) {
        fprintf(stderr, "no se pudo escribir micro/resultados/jitter.json\n");
        return 1;
    }

    return 0;
}
