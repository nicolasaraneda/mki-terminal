#define _POSIX_C_SOURCE 200809L

/*
 * bench_red — round trip de red: tiempo del handshake TCP (connect()) contra
 * un endpoint público estable y fijo (1.1.1.1:443, Cloudflare — se usa la IP
 * literal a propósito para no mezclar latencia de DNS con latencia de red).
 *
 * Esto mide la RED — WAN + pila TCP del kernel — no el mercado. Sirve como
 * referencia de piso: si el round trip de red ya son varios milisegundos,
 * ninguna optimización de software del lado local mueve la aguja de un
 * pipeline que depende de esa red.
 *
 * Si no hay salida de red (sandbox, entorno aislado), el benchmark lo
 * reporta como hallazgo — "sin salida de red" — en vez de fallar en
 * silencio o inventar un número.
 */

#include "comun.h"

#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define ENDPOINT_IP "1.1.1.1"
#define ENDPOINT_PUERTO 443
#define N_INTENTOS 50
#define TIMEOUT_MS 2000
#define ESPERA_ENTRE_INTENTOS_MS 20

/* Intenta un connect() no bloqueante con timeout acotado por poll().
 * Devuelve 0 y llena *latencia_ns en éxito; -1 en fallo/timeout. */
static int intentar_connect(uint64_t *latencia_ns) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    int flags = fcntl(fd, F_GETFL, 0);
    if (flags < 0 || fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        close(fd);
        return -1;
    }

    struct sockaddr_in destino;
    memset(&destino, 0, sizeof(destino));
    destino.sin_family = AF_INET;
    destino.sin_port = htons(ENDPOINT_PUERTO);
    if (inet_pton(AF_INET, ENDPOINT_IP, &destino.sin_addr) != 1) {
        close(fd);
        return -1;
    }

    uint64_t t0 = ahora_ns();
    int r = connect(fd, (struct sockaddr *)&destino, sizeof(destino));
    if (r == 0) {
        uint64_t t1 = ahora_ns();
        *latencia_ns = t1 - t0;
        close(fd);
        return 0;
    }
    if (errno != EINPROGRESS) {
        close(fd);
        return -1;
    }

    struct pollfd pfd = {.fd = fd, .events = POLLOUT, .revents = 0};
    int pr = poll(&pfd, 1, TIMEOUT_MS);
    if (pr <= 0) {
        close(fd); /* timeout o error de poll */
        return -1;
    }

    int err = 0;
    socklen_t len = sizeof(err);
    if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &len) != 0 || err != 0) {
        close(fd);
        return -1;
    }
    uint64_t t1 = ahora_ns();
    *latencia_ns = t1 - t0;
    close(fd);
    return 0;
}

int main(void) {
    ColeccionMuestras c;
    cm_iniciar(&c, N_INTENTOS);
    int exitos = 0, fallos = 0;

    for (int i = 0; i < N_INTENTOS; i++) {
        uint64_t lat;
        if (intentar_connect(&lat) == 0) {
            cm_agregar(&c, lat);
            exitos++;
        } else {
            fallos++;
        }
        struct timespec espera = {0, ESPERA_ENTRE_INTENTOS_MS * 1000000L};
        nanosleep(&espera, NULL);
    }

    JsonBuilder jb;
    jb_iniciar(&jb);
    jb_str(&jb, "benchmark", "red");
    jb_str(&jb, "unidad", "ns");
    jb_str(&jb, "endpoint", ENDPOINT_IP ":" "443 (Cloudflare, IP literal, sin DNS)");
    jb_u64(&jb, "intentos", N_INTENTOS);
    jb_u64(&jb, "exitos", (uint64_t)exitos);
    jb_u64(&jb, "fallos", (uint64_t)fallos);

    if (exitos == 0) {
        printf("\n=== red ===\n");
        printf("  sin salida de red: %d/%d intentos fallaron (o el entorno la bloquea)\n",
               fallos, N_INTENTOS);
        jb_bool(&jb, "sin_salida_de_red", 1);
        jb_str(&jb, "notas", "no se pudo completar ningun handshake TCP; se reporta como hallazgo, no como error silencioso");
        if (jb_escribir_archivo(&jb, "resultados/red.json") != 0) {
            fprintf(stderr, "no se pudo escribir micro/resultados/red.json\n");
            cm_liberar(&c);
            return 1;
        }
        cm_liberar(&c);
        return 0;
    }

    /* Sin warm-up: cada conexión TCP es nueva por construcción, no hay
     * calentamiento posible de un handshake. Se reportan las N muestras. */
    Percentiles p = cm_percentiles(&c, 0);
    imprimir_tabla("red — round trip de handshake TCP (connect) a 1.1.1.1:443", "ns", p);

    jb_bool(&jb, "sin_salida_de_red", 0);
    jb_percentiles(&jb, "connect", p);
    jb_str(&jb, "notas",
           "mide WAN + pila TCP del kernel, no el mercado; sirve de piso de "
           "referencia frente a la latencia local medida en los demas benchmarks");

    if (jb_escribir_archivo(&jb, "resultados/red.json") != 0) {
        fprintf(stderr, "no se pudo escribir micro/resultados/red.json\n");
        cm_liberar(&c);
        return 1;
    }

    cm_liberar(&c);
    return 0;
}
