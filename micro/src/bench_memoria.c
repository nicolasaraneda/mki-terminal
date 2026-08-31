#define _POSIX_C_SOURCE 200809L

/*
 * bench_memoria — latencia de acceso a memoria por nivel de caché, vía
 * pointer chasing (persiguiendo un puntero al azar, así el prefetcher de
 * hardware no puede adivinar la próxima dirección).
 *
 * La permutación se construye con el algoritmo de Sattolo: garantiza un
 * único ciclo que recorre TODOS los nodos sin repetir ninguno antes de
 * volver al principio, así que no hay atajos de ciclos cortos que el
 * hardware pueda aprender.
 *
 * Límite honesto del instrumento: el costo de una sola llamada a
 * clock_gettime (ver reloj.json) es del orden de una latencia L1 individual.
 * Medir salto por salto mediría el reloj, no la memoria. Por eso cada
 * MUESTRA acá es el tiempo de un lote de HOPS_POR_LOTE saltos consecutivos,
 * dividido por el tamaño del lote — es una latencia promedio por salto
 * DENTRO de un lote, con percentiles calculados sobre la distribución de
 * lotes. Es la misma razón por la que bench_syscall no resta el costo del
 * reloj: no hay forma honesta de aislar un solo salto con este reloj.
 */

#include "comun.h"

#include <stdio.h>
#include <stdlib.h>

typedef struct {
    uint64_t siguiente;
    char relleno[56]; /* nodo de 64 bytes: una línea de caché típica */
} Nodo;

#define HOPS_POR_LOTE 64
#define N_LOTES 20000
#define N_LOTES_WARMUP 200

typedef struct {
    const char *nombre;
    size_t n_nodos; /* n_nodos * 64 bytes = tamaño del buffer */
} NivelCache;

static const NivelCache NIVELES[] = {
    {"L1_16KB", 16384 / 64},
    {"L2_256KB", 262144 / 64},
    {"L3_16MB", 16777216 / 64},
    {"RAM_128MB", 134217728 / 64},
};
#define N_NIVELES (sizeof(NIVELES) / sizeof(NIVELES[0]))

/* Permutación de un solo ciclo (Sattolo) sobre n elementos, semilla fija. */
static void construir_ciclo(uint64_t *perm, size_t n, uint64_t semilla) {
    for (size_t i = 0; i < n; i++) perm[i] = i;
    Prng rng;
    prng_iniciar(&rng, semilla);
    for (size_t i = n - 1; i >= 1; i--) {
        uint64_t j = prng_rango(&rng, (uint64_t)i); /* j en [0, i-1], nunca i: sin puntos fijos */
        uint64_t tmp = perm[i];
        perm[i] = perm[j];
        perm[j] = tmp;
    }
}

int main(void) {
    JsonBuilder jb;
    jb_iniciar(&jb);
    jb_str(&jb, "benchmark", "memoria");
    jb_str(&jb, "unidad", "ns_por_salto_promedio_de_lote");
    jb_u64(&jb, "hops_por_lote", HOPS_POR_LOTE);
    jb_str(&jb, "metodo", "pointer chasing, ciclo unico de Sattolo, semilla fija 0xC0FFEE");

    uint64_t suma_checksum = 0; /* evita que el compilador elimine el recorrido */

    for (size_t niv = 0; niv < N_NIVELES; niv++) {
        size_t n = NIVELES[niv].n_nodos;
        Nodo *nodos = malloc(n * sizeof(Nodo));
        uint64_t *perm = malloc(n * sizeof(uint64_t));
        if (!nodos || !perm) {
            fprintf(stderr, "sin memoria para nivel %s\n", NIVELES[niv].nombre);
            return 1;
        }

        construir_ciclo(perm, n, 0xC0FFEEULL + niv);
        for (size_t i = 0; i < n; i++) nodos[i].siguiente = perm[i];
        free(perm);

        ColeccionMuestras c;
        cm_iniciar(&c, N_LOTES);

        uint64_t idx = 0;
        for (int lote = 0; lote < N_LOTES_WARMUP + N_LOTES; lote++) {
            uint64_t t0 = ahora_ns();
            for (int h = 0; h < HOPS_POR_LOTE; h++) {
                idx = nodos[idx].siguiente;
            }
            uint64_t t1 = ahora_ns();
            uint64_t ns_por_salto = (t1 - t0) / HOPS_POR_LOTE;
            cm_agregar(&c, ns_por_salto);
        }
        suma_checksum += idx;

        Percentiles p = cm_percentiles(&c, (size_t)N_LOTES_WARMUP);

        char titulo[128];
        snprintf(titulo, sizeof(titulo), "memoria — %s (%zu nodos, %.1f KB)",
                 NIVELES[niv].nombre, n, (double)(n * sizeof(Nodo)) / 1024.0);
        imprimir_tabla(titulo, "ns/salto", p);

        jb_percentiles(&jb, NIVELES[niv].nombre, p);

        cm_liberar(&c);
        free(nodos);
    }

    jb_u64(&jb, "checksum_no_optimizado", suma_checksum);
    jb_str(&jb, "notas",
           "checksum_no_optimizado no tiene significado propio: solo prueba "
           "que el compilador no elimino el recorrido");

    if (jb_escribir_archivo(&jb, "resultados/memoria.json") != 0) {
        fprintf(stderr, "no se pudo escribir micro/resultados/memoria.json\n");
        return 1;
    }

    return 0;
}
