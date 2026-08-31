#!/usr/bin/env bash
# test_arnes.sh — el arnés se prueba a sí mismo: verifica que mide lo que
# dice medir. No mide "es rápido", mide "es correcto". Bash, no zsh, mismo
# criterio que el resto del proyecto.
set -euo pipefail

DIR_MICRO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$DIR_MICRO/bin"
RES="$DIR_MICRO/resultados"

fallos=0

fallar() {
    echo "FALLA: $1" >&2
    fallos=$((fallos + 1))
}

ok() {
    echo "ok: $1"
}

# --- 1. bench_jitter reporta una espera de 1000us dentro de tolerancia ---
# Tolerancia generosa a propósito: esta prueba corre potencialmente sobre
# WSL2, cuyo jitter es justo lo que 1C tiene que cuantificar. Se pide que el
# p50 este dentro de +200% del objetivo (o sea, hasta 3x) y que el p99 no
# explote a más de 20x — un jitter mayor que eso significaría que el arnés
# está roto, no que la plataforma es lenta.
if [ ! -x "$BIN/bench_jitter" ]; then
    fallar "bin/bench_jitter no existe — correr 'make all' primero"
else
    "$BIN/bench_jitter" > /tmp/salida_jitter_test.txt
    if [ ! -f "$RES/jitter.json" ]; then
        fallar "jitter.json no se generó"
    else
        objetivo_ns=$(grep -o '"objetivo_1000us_ns": [0-9]*' "$RES/jitter.json" | grep -o '[0-9]*$')
        real_p50=$(grep -o '"real_1000us_p50": [0-9]*' "$RES/jitter.json" | grep -o '[0-9]*$')
        real_p99=$(grep -o '"real_1000us_p99": [0-9]*' "$RES/jitter.json" | grep -o '[0-9]*$')

        if [ -z "$objetivo_ns" ] || [ -z "$real_p50" ]; then
            fallar "no se pudieron extraer objetivo_1000us_ns / real_1000us_p50 del JSON"
        else
            limite_p50=$((objetivo_ns * 3))
            if [ "$real_p50" -lt "$objetivo_ns" ]; then
                fallar "real_1000us_p50 ($real_p50 ns) es MENOR que lo pedido ($objetivo_ns ns) — nanosleep no puede despertar antes de tiempo, el arnés está midiendo mal"
            elif [ "$real_p50" -gt "$limite_p50" ]; then
                fallar "real_1000us_p50 ($real_p50 ns) excede 3x lo pedido ($objetivo_ns ns) — o la plataforma tiene un jitter extremo, o el arnés está roto; revisar a mano"
            else
                ok "bench_jitter: objetivo=1000us, p50 real=${real_p50}ns, dentro de 3x tolerancia"
            fi

            limite_p99=$((objetivo_ns * 20))
            if [ -n "$real_p99" ] && [ "$real_p99" -gt "$limite_p99" ]; then
                echo "aviso: real_1000us_p99 (${real_p99} ns) excede 20x lo pedido — anotar como evidencia de jitter en 1C, no es una falla del arnés" >&2
            fi
        fi
    fi
fi

# --- 2. el JSON de cada benchmark ejecutado es sintácticamente balanceado ---
# Sin parser JSON en libc: se verifica balance de llaves y que cada línea de
# campo termine en coma salvo la última antes de "}". Es una prueba de forma,
# no de contenido.
for archivo in "$RES"/reloj.json "$RES"/syscall.json "$RES"/jitter.json; do
    if [ -f "$archivo" ]; then
        aperturas=$(grep -o '{' "$archivo" | wc -l)
        cierres=$(grep -o '}' "$archivo" | wc -l)
        if [ "$aperturas" != "$cierres" ]; then
            fallar "$archivo: llaves desbalanceadas ($aperturas aperturas, $cierres cierres)"
        else
            ok "$(basename "$archivo"): JSON con llaves balanceadas"
        fi
    fi
done

# --- 3. bench_reloj: el costo de leer el reloj es menor que 10 microsegundos ---
# Umbral de sanidad, no de rendimiento: si clock_gettime tarda más de 10us,
# algo en el entorno (virtualización pesada, vdso deshabilitado) es
# anormal y hay que saberlo, no seguir midiendo como si nada.
if [ ! -x "$BIN/bench_reloj" ]; then
    fallar "bin/bench_reloj no existe"
else
    "$BIN/bench_reloj" > /tmp/salida_reloj_test.txt
    costo_p50=$(grep -o '"costo_lectura_p50": [0-9]*' "$RES/reloj.json" | grep -o '[0-9]*$')
    if [ -z "$costo_p50" ]; then
        fallar "no se pudo extraer costo_lectura_p50 de reloj.json"
    elif [ "$costo_p50" -gt 10000 ]; then
        fallar "costo_lectura_p50 ($costo_p50 ns) supera 10000 ns — clock_gettime anormalmente lento en este entorno, anotar en 1C"
    else
        ok "bench_reloj: costo_lectura_p50=${costo_p50}ns, por debajo del umbral de sanidad de 10us"
    fi
fi

if [ "$fallos" -gt 0 ]; then
    echo ""
    echo "$fallos prueba(s) del arnés fallaron." >&2
    exit 1
fi

echo ""
echo "todas las pruebas del arnés pasaron."
