#define _POSIX_C_SOURCE 200809L

/*
 * bench_mensaje — throughput y latencia de parseo de un mensaje binario de
 * mercado sintético, formato fijo, un millón de mensajes.
 *
 * El formato es un invento propio (no FIX/ITCH real) pero con la forma
 * típica de un feed de mercado: timestamp, id de instrumento, precio en
 * punto fijo, cantidad, lado, flags. 28 bytes por mensaje, campo por campo
 * con memcpy — nunca se castea un puntero del buffer a una struct (eso
 * evitaría el warning de "address of packed member" y, más importante,
 * evita acceso desalineado indefinido: memcpy es la forma correcta y
 * portable de leer un formato de wire empaquetado).
 */

#include "comun.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAM_MSG 28u
#define N_MENSAJES 1000000u
#define TAM_LOTE 200u
#define N_LOTES (N_MENSAJES / TAM_LOTE)
#define N_LOTES_WARMUP 50u

typedef struct {
    uint64_t ts_ns;
    uint32_t id_instrumento;
    int64_t precio_fp; /* precio * 10000, punto fijo */
    int32_t cantidad;
    uint8_t lado;  /* 0 = compra, 1 = venta */
    uint8_t flags;
} MensajeParseado;

static void escribir_mensaje(uint8_t *buf, uint64_t ts_ns, uint32_t id,
                              int64_t precio_fp, int32_t cantidad,
                              uint8_t lado, uint8_t flags) {
    uint16_t reservado = 0;
    memcpy(buf + 0, &ts_ns, 8);
    memcpy(buf + 8, &id, 4);
    memcpy(buf + 12, &precio_fp, 8);
    memcpy(buf + 20, &cantidad, 4);
    buf[24] = lado;
    buf[25] = flags;
    memcpy(buf + 26, &reservado, 2);
}

static void leer_mensaje(const uint8_t *buf, MensajeParseado *m) {
    memcpy(&m->ts_ns, buf + 0, 8);
    memcpy(&m->id_instrumento, buf + 8, 4);
    memcpy(&m->precio_fp, buf + 12, 8);
    memcpy(&m->cantidad, buf + 20, 4);
    m->lado = buf[24];
    m->flags = buf[25];
}

int main(void) {
    size_t tam_buffer = (size_t)N_MENSAJES * TAM_MSG;
    uint8_t *buffer = malloc(tam_buffer);
    if (!buffer) {
        fprintf(stderr, "sin memoria para %zu bytes\n", tam_buffer);
        return 1;
    }

    Prng rng;
    prng_iniciar(&rng, 0x5EED5EEDULL);
    for (uint32_t i = 0; i < N_MENSAJES; i++) {
        uint64_t ts = (uint64_t)i * 1000ULL;
        uint32_t id = (uint32_t)prng_rango(&rng, 500);
        int64_t precio = (int64_t)(1000000 + prng_rango(&rng, 2000000));
        int32_t cantidad = (int32_t)(1 + prng_rango(&rng, 10000));
        uint8_t lado = (uint8_t)prng_rango(&rng, 2);
        uint8_t flags = (uint8_t)prng_rango(&rng, 256);
        escribir_mensaje(buffer + (size_t)i * TAM_MSG, ts, id, precio, cantidad, lado, flags);
    }

    /* --- 1: throughput de una pasada completa --- */
    uint64_t checksum = 0;
    MensajeParseado m;
    uint64_t t0 = ahora_ns();
    for (uint32_t i = 0; i < N_MENSAJES; i++) {
        leer_mensaje(buffer + (size_t)i * TAM_MSG, &m);
        checksum += (uint64_t)m.cantidad + m.lado;
    }
    uint64_t t1 = ahora_ns();
    uint64_t total_ns = t1 - t0;
    double msgs_por_seg = (double)N_MENSAJES * 1e9 / (double)total_ns;
    double mb_por_seg = ((double)N_MENSAJES * TAM_MSG / 1e6) / ((double)total_ns / 1e9);

    printf("\n=== mensaje — pasada completa (%u mensajes, %u bytes c/u) ===\n",
           N_MENSAJES, TAM_MSG);
    printf("  tiempo total       : %llu ns\n", (unsigned long long)total_ns);
    printf("  throughput         : %.0f mensajes/s (%.1f MB/s)\n", msgs_por_seg, mb_por_seg);
    printf("  checksum (control) : %llu\n", (unsigned long long)checksum);

    /* --- 2: distribución de latencia por lote --- */
    ColeccionMuestras c;
    cm_iniciar(&c, N_LOTES);
    uint64_t checksum2 = 0;
    for (uint32_t lote = 0; lote < N_LOTES; lote++) {
        uint32_t base = lote * TAM_LOTE;
        uint64_t tl0 = ahora_ns();
        for (uint32_t j = 0; j < TAM_LOTE; j++) {
            leer_mensaje(buffer + (size_t)(base + j) * TAM_MSG, &m);
            checksum2 += m.lado;
        }
        uint64_t tl1 = ahora_ns();
        cm_agregar(&c, (tl1 - tl0) / TAM_LOTE);
    }
    Percentiles p = cm_percentiles(&c, N_LOTES_WARMUP);
    imprimir_tabla("mensaje — latencia de parseo por mensaje (promedio de lotes de 200)", "ns", p);

    JsonBuilder jb;
    jb_iniciar(&jb);
    jb_str(&jb, "benchmark", "mensaje");
    jb_str(&jb, "unidad_latencia", "ns_por_mensaje_promedio_de_lote");
    jb_u64(&jb, "n_mensajes", N_MENSAJES);
    jb_u64(&jb, "bytes_por_mensaje", TAM_MSG);
    jb_u64(&jb, "tam_lote", TAM_LOTE);
    jb_u64(&jb, "pasada_completa_ns", total_ns);
    jb_double(&jb, "pasada_completa_msgs_por_seg", msgs_por_seg, 0);
    jb_double(&jb, "pasada_completa_mb_por_seg", mb_por_seg, 1);
    jb_percentiles(&jb, "parseo", p);
    jb_u64(&jb, "checksum_pasada_completa", checksum);
    jb_u64(&jb, "checksum_lotes", checksum2);
    jb_str(&jb, "notas",
           "formato inventado, no FIX/ITCH real; el parseo es campo a campo "
           "con memcpy, nunca casteo de puntero a struct, para no incurrir "
           "en acceso desalineado indefinido sobre un buffer empaquetado");

    if (jb_escribir_archivo(&jb, "resultados/mensaje.json") != 0) {
        fprintf(stderr, "no se pudo escribir micro/resultados/mensaje.json\n");
        return 1;
    }

    cm_liberar(&c);
    free(buffer);
    return 0;
}
