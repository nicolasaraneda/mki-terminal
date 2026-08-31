/*
 * comun.h — utilidades compartidas del arnés de medición de latencia (micro/).
 *
 * Esto es un INSTRUMENTO DE MEDICIÓN, no un sistema de trading. Todo tiempo
 * se mide con clock_gettime(CLOCK_MONOTONIC_RAW): no se ve afectado por NTP
 * ni por ajustes del reloj de pared, que es justo lo que se necesita para
 * medir latencias de microsegundos sin que un salto de reloj contamine una
 * muestra.
 *
 * Convención dura del proyecto para este arnés: SIEMPRE se reportan
 * percentiles (p50, p99, p99.9, máximo), NUNCA una media sola. La media
 * esconde la cola, y la cola es lo único que importa en latencia.
 */
#ifndef MKI_MICRO_COMUN_H
#define MKI_MICRO_COMUN_H

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

/* ---------- reloj ---------- */

/* Tiempo monótono crudo en nanosegundos. No usar para tiempo de pared. */
uint64_t ahora_ns(void);

/* ---------- PRNG determinístico (splitmix64) ----------
 * NUNCA se usa rand()/random(): la semilla siempre es explícita para que
 * cualquier corrida sea reproducible bit a bit dado el mismo argumento.
 */
typedef struct {
    uint64_t estado;
} Prng;

void prng_iniciar(Prng *p, uint64_t semilla);
uint64_t prng_siguiente(Prng *p);
/* Entero uniforme en [0, limite) sin sesgo de módulo perceptible para los
 * tamaños que usa este arnés (limite << 2^64). */
uint64_t prng_rango(Prng *p, uint64_t limite);

/* ---------- colección de muestras ---------- */

typedef struct {
    uint64_t *datos;
    size_t n;
    size_t capacidad;
} ColeccionMuestras;

void cm_iniciar(ColeccionMuestras *c, size_t capacidad_inicial);
void cm_agregar(ColeccionMuestras *c, uint64_t valor);
void cm_liberar(ColeccionMuestras *c);

typedef struct {
    uint64_t minimo;
    uint64_t p50;
    uint64_t p99;
    uint64_t p999;
    uint64_t maximo;
    double media;
    size_t n_total;       /* incluye warm-up */
    size_t n_descartado;  /* warm-up descartado */
    size_t n_efectivo;    /* n_total - n_descartado, sobre el que se calculan los percentiles */
} Percentiles;

/*
 * Calcula percentiles descartando las primeras `descartar_warmup` muestras
 * (en el orden en que se agregaron, NO tras ordenar — el warm-up es "las
 * primeras N mediciones de este proceso", no "las N más rápidas").
 * Ordena internamente una copia; no modifica `c`.
 */
Percentiles cm_percentiles(const ColeccionMuestras *c, size_t descartar_warmup);

void imprimir_tabla(const char *nombre_benchmark, const char *unidad, Percentiles p);

/* ---------- salida JSON ---------- */

#define JB_MAX_CAMPOS 128
#define JB_LEN_CAMPO 256

typedef struct {
    char campos[JB_MAX_CAMPOS][JB_LEN_CAMPO];
    size_t n;
} JsonBuilder;

void jb_iniciar(JsonBuilder *jb);
void jb_u64(JsonBuilder *jb, const char *clave, uint64_t valor);
void jb_double(JsonBuilder *jb, const char *clave, double valor, int decimales);
void jb_str(JsonBuilder *jb, const char *clave, const char *valor);
void jb_bool(JsonBuilder *jb, const char *clave, int valor);
/* Agrega minimo/p50/p99/p999/maximo/media/n_total/n_descartado/n_efectivo
 * bajo claves "<prefijo>_<campo>". */
void jb_percentiles(JsonBuilder *jb, const char *prefijo, Percentiles p);
/* Escribe el objeto JSON completo (envuelto en { }) al archivo `ruta`.
 * Devuelve 0 en éxito, -1 en error (revisar errno). */
int jb_escribir_archivo(const JsonBuilder *jb, const char *ruta);

#endif /* MKI_MICRO_COMUN_H */
