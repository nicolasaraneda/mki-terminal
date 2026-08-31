# La limitación de WSL2, medida

**No es una nota al pie.** Esta máquina —la única que existe para este
frente— corre bajo WSL2, que es una máquina virtual liviana sobre Hyper-V.
Antes de decir una sola cifra de latencia hay que saber cuánto de esa cifra
es la capa y cuánto es lo que se está midiendo de verdad. Este documento es
esa medición, hecha con el arnés de `micro/` (ver `GEMELO/MICRO/DISEÑO.md`
para la pregunta de investigación que la motiva).

Todas las cifras de abajo salen de `micro/resultados/*.json`, generados con
`make ejecutar` el 31-ago-2026 en esta máquina (kernel
`6.18.33.2-microsoft-standard-WSL2`, AMD Ryzen 9 5900X, 24 hilos visibles).
Reproducible con `cd micro && make ejecutar`.

## El hallazgo: un piso de ~75 µs que no se mueve

`bench_jitter` pide dormir una duración exacta con `nanosleep()` y mide
cuánto duerme de verdad el proceso. El exceso sobre lo pedido (`exceso_*` en
`jitter.json`) es la cifra que importa:

| objetivo pedido | exceso p50 | exceso p99 | exceso p99.9 | exceso máximo |
|---|---|---|---|---|
| 10 µs | 72.3 µs | 125.6 µs | 183.4 µs | 255.2 µs |
| 100 µs | 73.1 µs | 127.5 µs | 183.7 µs | 192.2 µs |
| 1.000 µs | 78.6 µs | 117.8 µs | 185.2 µs | 212.4 µs |
| 10.000 µs | 85.2 µs | 110.2 µs | 126.3 µs | 126.3 µs |

Repetido 5 veces de forma independiente, el p50 del exceso a 10 µs varió
entre 72.3 y 72.8 µs, y a 1.000 µs entre 77.8 y 79.3 µs — una desviación
menor a 1 µs entre corridas. **No es ruido: es un piso reproducible.**

Lo que hace que esto sea un hallazgo de plataforma y no de la aplicación: el
exceso es prácticamente **constante en términos absolutos**, no proporcional
a lo pedido. Pedir dormir 10 µs cuesta ~82 µs reales (8.2× lo pedido); pedir
dormir 10.000 µs cuesta ~10.085 µs reales (1.0085×). El sistema no está
siendo 8 veces más lento al servir sueños cortos — está sumando un costo
fijo de entre 70 y 85 µs a cualquier despertar, sin importar cuánto se pidió.
Esa es la firma de una granularidad de temporizador o de planificación —
"el próximo tick disponible para despertar este proceso está a ~75 µs de
donde lo dejaste dormir", típico de una capa de virtualización que no expone
al huésped el temporizador de más alta resolución del host.

No se puede separar aquí, con este instrumento, cuánto de ese piso es
Hyper-V/vmbus y cuánto es la configuración del guest kernel de WSL2 (tick
dinámico, gobernador de CPU, C-states) — hacerlo requeriría instrumentación
del lado del host o del hipervisor, fuera del alcance de un arnés en
espacio de usuario. Lo que sí se puede afirmar con esta evidencia: **el piso
existe, es de esta magnitud, y es indiferente a qué tan corta sea la espera
pedida por debajo de él.**

## Segunda evidencia: la cola de una syscall trivial

`bench_syscall` mide `syscall(SYS_getpid)` en bucle — el viaje más barato
posible a modo kernel, sin trabajo real de por medio. El cuerpo de la
distribución es sano: p50 = 290 ns, p99 = 300 ns, p99.9 = 430 ns. Pero el
máximo sobre 500.000 muestras fue **57.459 ns — 198 veces el p50**. Esa cola
no viene del código (una syscall trivial no tiene variabilidad propia de esa
magnitud): viene de que, ocasionalmente, el planificador del host le quita
la CPU al hilo huésped para atender otra cosa (otra vCPU, una interrupción
del hipervisor), y cuando eso ocurre en medio de una medición de
nanosegundos, el resultado es un outlier de decenas de microsegundos.
`bench_reloj` muestra el mismo patrón en miniatura: p50 = 20 ns, p99 = 30 ns,
máximo = 20.340 ns (1.017×).

## Lo que esto significa para el piso de latencia atribuible a WSL2

No hay una única "cifra de overhead de WSL2" que restar — el efecto no es un
offset constante sobre un valor limpio, es un **piso de despertar** (~75 µs)
más una **probabilidad de interrupción por outlier** (cola de cientos de
veces el valor típico). Ambos son atribuibles a la capa de virtualización,
no al código del arnés: el mismo código, corriendo en Linux nativo sobre
hardware sin hipervisor, no tendría un motivo estructural para mostrar un
piso de decenas de microsegundos en un `nanosleep()` de 10 µs — los sistemas
Linux nativos con temporizadores de alta resolución (`hrtimer`) típicamente
sirven sueños cortos con error de bajo microsegundo o menos. No se hizo esa
medición comparativa en esta corrida (no hay una segunda máquina sin WSL2
disponible esta noche) — es una limitación declarada, no una comparación
inventada.

## La respuesta a la pregunta de 1C

**Si el régimen que importa para microtrading opera por debajo de ~75-100
µs, medir en esta plataforma no distingue señal de piso de la máquina.**
Cualquier decisión, cómputo o control de bucle que dependa de despertar un
proceso con precisión mejor que esa cifra está midiendo la capa de
virtualización, no el fenómeno de mercado. Por encima de ese piso —al nivel
de milisegundo, que es donde vive el resto de este documento en
`piso_de_latencia.md`— el ruido relativo cae por debajo del 1% y la
medición vuelve a ser informativa.

Esto no dice "WSL2 hace inviable microtrading" en abstracto: dice que
**hace inviable medir con esta plataforma cualquier afirmación de latencia
por debajo de la decena de microsegundos**, que es exactamente el régimen
que un pipeline de decisión intradía de segundos-a-minutos SÍ puede tolerar
perfectamente, pero que un pipeline de microtrading de microsegundos no
puede. Cuál de los dos es el régimen que le importa a la pregunta de
investigación se decide en `DISEÑO.md` y se concluye en
`piso_de_latencia.md`.
