// Formato de cifras de señal. El intervalo SIEMPRE se nombra con su nivel:
// el "80%" es información de calibración, no decoración (regla 4.7.1).

const signo = (v: number, dec: number) => `${v >= 0 ? '+' : '−'}${Math.abs(v).toFixed(dec)}`

/** "intervalo 80%: −5.1 a +4.3 pp" desde el estimado y el semiancho. */
export function rangoIntervalo80(estimadoPct: number, semianchoPp: number): string {
  return `intervalo 80%: ${signo(estimadoPct - semianchoPp, 1)} a ${signo(
    estimadoPct + semianchoPp,
    1,
  )} pp`
}
