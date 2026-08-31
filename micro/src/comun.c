#define _POSIX_C_SOURCE 200809L

#include "comun.h"

#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

uint64_t ahora_ns(void) {
    struct timespec ts;
    /* CLOCK_MONOTONIC_RAW: no está sujeto a ajustes NTP ni a slewing.
     * En kernels muy viejos podría no existir; si clock_gettime falla acá,
     * es preferible abortar que reportar cero en silencio. */
    if (clock_gettime(CLOCK_MONOTONIC_RAW, &ts) != 0) {
        abort();
    }
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* ---------- PRNG splitmix64 (dominio público, Vigna) ---------- */

void prng_iniciar(Prng *p, uint64_t semilla) {
    p->estado = semilla;
}

uint64_t prng_siguiente(Prng *p) {
    uint64_t z = (p->estado += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

uint64_t prng_rango(Prng *p, uint64_t limite) {
    if (limite == 0) return 0;
    /* Sesgo de módulo despreciable para los tamaños de este arnés
     * (limite del orden de 10^6-10^7, dominio de 2^64). */
    return prng_siguiente(p) % limite;
}

/* ---------- colección de muestras ---------- */

void cm_iniciar(ColeccionMuestras *c, size_t capacidad_inicial) {
    c->n = 0;
    c->capacidad = capacidad_inicial > 0 ? capacidad_inicial : 1024;
    c->datos = malloc(c->capacidad * sizeof(uint64_t));
    if (!c->datos) abort();
}

void cm_agregar(ColeccionMuestras *c, uint64_t valor) {
    if (c->n == c->capacidad) {
        size_t nueva_cap = c->capacidad * 2;
        uint64_t *nuevo = realloc(c->datos, nueva_cap * sizeof(uint64_t));
        if (!nuevo) abort();
        c->datos = nuevo;
        c->capacidad = nueva_cap;
    }
    c->datos[c->n++] = valor;
}

void cm_liberar(ColeccionMuestras *c) {
    free(c->datos);
    c->datos = NULL;
    c->n = 0;
    c->capacidad = 0;
}

static int comparar_u64(const void *a, const void *b) {
    uint64_t va = *(const uint64_t *)a;
    uint64_t vb = *(const uint64_t *)b;
    if (va < vb) return -1;
    if (va > vb) return 1;
    return 0;
}

/* Método "nearest-rank": índice = ceil(p * n) - 1, con p en (0,1]. */
static uint64_t percentil_en(const uint64_t *ordenado, size_t n, double p) {
    if (n == 0) return 0;
    size_t idx = (size_t)(p * (double)n);
    if (idx == 0) idx = 1;
    if (idx > n) idx = n;
    return ordenado[idx - 1];
}

Percentiles cm_percentiles(const ColeccionMuestras *c, size_t descartar_warmup) {
    Percentiles r;
    memset(&r, 0, sizeof(r));
    r.n_total = c->n;
    r.n_descartado = descartar_warmup < c->n ? descartar_warmup : c->n;
    size_t n_ef = c->n - r.n_descartado;
    r.n_efectivo = n_ef;

    if (n_ef == 0) {
        return r;
    }

    uint64_t *copia = malloc(n_ef * sizeof(uint64_t));
    if (!copia) abort();
    memcpy(copia, c->datos + r.n_descartado, n_ef * sizeof(uint64_t));
    qsort(copia, n_ef, sizeof(uint64_t), comparar_u64);

    r.minimo = copia[0];
    r.maximo = copia[n_ef - 1];
    r.p50 = percentil_en(copia, n_ef, 0.50);
    r.p99 = percentil_en(copia, n_ef, 0.99);
    r.p999 = percentil_en(copia, n_ef, 0.999);

    long double suma = 0.0L;
    for (size_t i = 0; i < n_ef; i++) suma += (long double)copia[i];
    r.media = (double)(suma / (long double)n_ef);

    free(copia);
    return r;
}

void imprimir_tabla(const char *nombre_benchmark, const char *unidad, Percentiles p) {
    printf("\n=== %s ===\n", nombre_benchmark);
    printf("  muestras totales   : %zu\n", p.n_total);
    printf("  warm-up descartado : %zu\n", p.n_descartado);
    printf("  muestras efectivas : %zu\n", p.n_efectivo);
    if (p.n_efectivo == 0) {
        printf("  (sin muestras efectivas)\n");
        return;
    }
    printf("  %-8s %10s\n", "métrica", unidad);
    printf("  %-8s %10llu\n", "mínimo", (unsigned long long)p.minimo);
    printf("  %-8s %10llu\n", "p50", (unsigned long long)p.p50);
    printf("  %-8s %10llu\n", "p99", (unsigned long long)p.p99);
    printf("  %-8s %10llu\n", "p99.9", (unsigned long long)p.p999);
    printf("  %-8s %10llu\n", "máximo", (unsigned long long)p.maximo);
    printf("  %-8s %10.1f  (referencia, NUNCA el número que decide nada)\n", "media", p.media);
}

/* ---------- JSON ---------- */

void jb_iniciar(JsonBuilder *jb) {
    jb->n = 0;
}

static void jb_agregar_crudo(JsonBuilder *jb, const char *clave, const char *valor_json) {
    if (jb->n >= JB_MAX_CAMPOS) abort();
    int escritos = snprintf(jb->campos[jb->n], JB_LEN_CAMPO, "\"%s\": %s", clave, valor_json);
    if (escritos < 0 || (size_t)escritos >= JB_LEN_CAMPO) abort();
    jb->n++;
}

void jb_u64(JsonBuilder *jb, const char *clave, uint64_t valor) {
    char buf[64];
    snprintf(buf, sizeof(buf), "%llu", (unsigned long long)valor);
    jb_agregar_crudo(jb, clave, buf);
}

void jb_double(JsonBuilder *jb, const char *clave, double valor, int decimales) {
    char buf[64];
    snprintf(buf, sizeof(buf), "%.*f", decimales, valor);
    jb_agregar_crudo(jb, clave, buf);
}

void jb_str(JsonBuilder *jb, const char *clave, const char *valor) {
    if (jb->n >= JB_MAX_CAMPOS) abort();
    /* Escape mínimo: este arnés solo emite strings propias (nombres de
     * benchmark, notas fijas), nunca texto arbitrario de afuera, así que
     * escapar solo comillas y backslash alcanza. */
    char escapado[JB_LEN_CAMPO];
    size_t j = 0;
    for (size_t i = 0; valor[i] != '\0' && j < sizeof(escapado) - 2; i++) {
        if (valor[i] == '"' || valor[i] == '\\') {
            escapado[j++] = '\\';
        }
        escapado[j++] = valor[i];
    }
    escapado[j] = '\0';
    int escritos = snprintf(jb->campos[jb->n], JB_LEN_CAMPO, "\"%s\": \"%s\"", clave, escapado);
    if (escritos < 0 || (size_t)escritos >= JB_LEN_CAMPO) abort();
    jb->n++;
}

void jb_bool(JsonBuilder *jb, const char *clave, int valor) {
    jb_agregar_crudo(jb, clave, valor ? "true" : "false");
}

void jb_percentiles(JsonBuilder *jb, const char *prefijo, Percentiles p) {
    char clave[128];
    snprintf(clave, sizeof(clave), "%s_n_total", prefijo);
    jb_u64(jb, clave, p.n_total);
    snprintf(clave, sizeof(clave), "%s_n_descartado", prefijo);
    jb_u64(jb, clave, p.n_descartado);
    snprintf(clave, sizeof(clave), "%s_n_efectivo", prefijo);
    jb_u64(jb, clave, p.n_efectivo);
    snprintf(clave, sizeof(clave), "%s_min", prefijo);
    jb_u64(jb, clave, p.minimo);
    snprintf(clave, sizeof(clave), "%s_p50", prefijo);
    jb_u64(jb, clave, p.p50);
    snprintf(clave, sizeof(clave), "%s_p99", prefijo);
    jb_u64(jb, clave, p.p99);
    snprintf(clave, sizeof(clave), "%s_p999", prefijo);
    jb_u64(jb, clave, p.p999);
    snprintf(clave, sizeof(clave), "%s_max", prefijo);
    jb_u64(jb, clave, p.maximo);
    snprintf(clave, sizeof(clave), "%s_media", prefijo);
    jb_double(jb, clave, p.media, 2);
}

int jb_escribir_archivo(const JsonBuilder *jb, const char *ruta) {
    FILE *f = fopen(ruta, "w");
    if (!f) return -1;
    fprintf(f, "{\n");
    for (size_t i = 0; i < jb->n; i++) {
        fprintf(f, "  %s%s\n", jb->campos[i], (i + 1 < jb->n) ? "," : "");
    }
    fprintf(f, "}\n");
    if (fclose(f) != 0) return -1;
    return 0;
}
