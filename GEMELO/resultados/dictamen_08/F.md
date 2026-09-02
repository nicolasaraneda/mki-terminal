# Dictamen del `estadistico-adversario` · Frente F (plan secuencial v5) · 2-sep-2026

> Texto del agente, guardado por el orquestador. Leyó las cuatro objeciones anteriores antes de juzgar. La v2 de `secuencial_v5.py` aplica los bloqueantes; el plan vuelve a `cola_decisiones.md` §27.

**VEREDICTO juzgado:** «el v5 responde a los cuatro rechazos; tipo I 0,050 / 0,060 / 0,060 / 0,056 con φ 0–0,3; absorbe la autocorrelación mucho mejor que el plan anterior; potencia 0,79 a 9 pp, n esperado 197» — **NO SOSTIENE.**

**Cifra verificada:** fronteras [∞, 3,147, 2,572, 2,273, 2,06] y el tipo I en muestra reproducen exactos. **Defecto descalificante: la fila «tipo I a φ = 0» está medida sobre las MISMAS 20.000 trayectorias con las que se ajustaron las fronteras.** No es una medición, es la definición del ajuste (hasta el redondeo de `m = round(objetivo·n)`); su Wilson es un error de categoría. Fuera de muestra (7 semillas, 84.000 réplicas): **α = 0,0514 [0,0500, 0,0530]**; dispersión entre semillas 0,0483–0,0580, mayor que la binomial (el error de Monte Carlo de la frontera —38 cruces en la 2ª mirada— no está propagado).

**Contraste externo abandonado** (O'Brien-Fleming K = 5, recursión de Armitage, `GEMELO/SECUENCIAL/fronteras.py`): 4,562 / 3,226 / 2,634 / 2,281 / 2,040 contra ∞ / 3,147 / 2,572 / 2,273 / 2,060. Tres de cuatro fronteras finitas quedan **por debajo** de la referencia gaussiana en las miradas tempranas, con un estadístico de colas más pesadas. La mirada 1 muere por resolución (α₁ = 1,2e−5 → 0,2 cruces esperados → c = ∞): **el plan anuncia cinco miradas y tiene cuatro.**

**Denominador:** el nulo (generador calibrado a δ = 0) es el correcto. El de la VERIFICACIÓN no: las fronteras se validan contra el mismo generador, la misma parametrización y la misma muestra — el defecto que hundió a la v1, textual en `SECUENCIAL/DISEÑO.md`; la v5 ni siquiera cambia la semilla.

**Intentos:** «1» defendible como incremento, pero el z gaussiano es un estadístico principal candidato NUEVO (precedente TRAY: cuatro contados): incremento honesto **2**. Registro en 100, sin absorber.

**Por punto.** (1) Rechazos: #1 **REINTRODUCIDO y agravado**; #2 reformulado, no resuelto; #3 y #4 respondidos. (2) **El eje φ es inerte:** el AC1 del factor de día sigue a φ (0,19 / 0,29 / 0,58) pero el AC1 REALIZADO de las contribuciones es ≈ 0 para todo φ hasta 0,6 — cuando el SOX sube el modelo y la baseline coinciden y el día contribuye exactamente cero: **53,6 % de las fechas simuladas y 19 de 35 selladas (54 %)**. El control φ = 0 al mismo protocolo (6.000, misma semilla) da 0,0580 [0,0524, 0,0642] y **contiene las tres filas φ > 0**: la tabla es cuatro corridas de la misma nula. La frase «absorbe la autocorrelación mucho mejor que el plan anterior (banda [0,046, 0,079])» es falsa por partida doble; **la banda firmada queda intacta.** (3) El estadístico (z gaussiano sobre sumas diarias) NO es la permutación de signo por día del proyecto que el Frente A calibró: es nuevo, sin calibrar, y su validez descansa en un generador sin vara externa. (4) Intentos 2. (5) **No entra a `espera_firma`: vuelve a la cola.** «Un pre-registro que no reproduce el día que se firma no está congelado, está fechado»: éste reproduce, pero no se verifica contra nada que no sea él mismo. Quinto rechazo.

**Criterios:** V1–V7, R1 NO EVALUABLE (el plan propone cómo medir); el dimensionamiento a 9 pp descansa en un efecto que **muere bajo R2** (+2,5 pp, p 0,82); R3 sin fuga (población futura al ancla).

**DICTAMEN: NO SOSTIENE.**

**Bloqueantes:** (1) retirar el 0,050 como tipo I o rotularlo «ajuste»; α fuera de muestra 0,0514 [0,0500, 0,0530]; (2) retirar o reetiquetar la tabla φ («cuatro corridas de la misma nula»); (3) retractar la frase de la bitácora; la banda [0,046, 0,079] intacta; (4) reponer la validación externa (Jennison-Turnbull / Armitage); (5) declarar que la mirada 1 no puede rechazar; (6) propagar o declarar el error de Monte Carlo de la frontera; (7) declarar el estadístico como nuevo y contarlo (incremento 2).
**Exigidos:** (8) inyectar dependencia que llegue al estimador (autocorrelacionar U, o generar S_j con AC1 objetivo) y verificar el AC1 realizado antes de reportar α; (9) reportar el AC1 realizado junto a cada φ (el sellado es −0,17 sobre 35 fechas: ningún φ ∈ [0, 0,6] lo produce); (10) una frase de conclusión en el `.md`; (11) declarar que el dimensionamiento a 9 pp descansa en un efecto que no sobrevive a R2.

**Lo publicable hoy, sin firma:** más de la mitad de las fechas selladas no aportan información al estadístico direccional porque el campeón y la baseline coinciden por construcción cuando el SOX sube. Eso explica de un plumazo por qué la dirección necesita ~250 días y la magnitud ~100.
