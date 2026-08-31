/* _GNU_SOURCE, no _POSIX_C_SOURCE: syscall() es una extensión de glibc y
 * su declaración en <unistd.h> no aparece bajo el perfil POSIX estricto. */
#define _GNU_SOURCE

/*
 * bench_syscall — overhead de una syscall trivial en bucle.
 *
 * Se usa syscall(SYS_getpid) en lugar de getpid() de libc a propósito:
 * getpid() puede quedar servida por una capa de la biblioteca en algunos
 * entornos, y lo que se quiere medir acá es el viaje real a modo kernel.
 * En WSL2 esto atraviesa además la capa de traducción de syscalls de Linux
 * sobre el hypervisor — es exactamente la capa que 1C tiene que cuantificar.
 */

#include "comun.h"

#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>

#define N_MUESTRAS 500000
#define N_WARMUP 5000

int main(void) {
    ColeccionMuestras c;
    cm_iniciar(&c, N_MUESTRAS);

    for (int i = 0; i < N_WARMUP + N_MUESTRAS; i++) {
        uint64_t t0 = ahora_ns();
        (void)syscall(SYS_getpid);
        uint64_t t1 = ahora_ns();
        cm_agregar(&c, t1 - t0);
    }

    Percentiles p = cm_percentiles(&c, N_WARMUP);
    imprimir_tabla("overhead de syscall(SYS_getpid) en bucle", "ns", p);

    JsonBuilder jb;
    jb_iniciar(&jb);
    jb_str(&jb, "benchmark", "syscall");
    jb_str(&jb, "unidad", "ns");
    jb_str(&jb, "syscall_usada", "SYS_getpid");
    jb_u64(&jb, "warmup_descartado_config", N_WARMUP);
    jb_percentiles(&jb, "overhead", p);
    jb_str(&jb, "notas",
           "incluye el costo de leer el reloj dos veces (ver reloj.json, "
           "costo_lectura_p50); no se resta porque restar percentiles no es "
           "matematicamente valido, se reporta el crudo y se compara a ojo "
           "con el piso del reloj");

    if (jb_escribir_archivo(&jb, "resultados/syscall.json") != 0) {
        fprintf(stderr, "no se pudo escribir micro/resultados/syscall.json\n");
        return 1;
    }

    cm_liberar(&c);
    return 0;
}
