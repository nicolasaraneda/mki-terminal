# Dictamen del `estadistico-adversario` sobre los bloques 1, 2 y 4 (corrida 11)

**8-sep-2026, 01:30 hora de Chile aprox. Texto del agente, archivado por el orquestador sin editar el
contenido (sólo formato).** Las exigencias se aplicaron al ejecutable en la misma corrida y los
artefactos se re-corrieron a las 01:31 (bloques 1 y 4) y 01:35 y 01:50 (bloque 2). **Las cifras
re-corridas no volvieron a pasar por el adversario**: lo que sigue juzga la primera versión.

Análisis dimensional: bloque 1, δ y σ en pp por semana, T en semanas, proporciones sobre 2.000
réplicas con Wilson; bloque 2, USD acumulados sobre 156 semanas sobre USD totales; bloque 4, pp de
acierto con clúster de día.

## (A) `instrumento_dinero.md`: SOSTIENE CON EXIGENCIAS

Cifra reportada: σ 2,704; tamaño bilateral 0,086 [0,074, 0,099]; cobertura 0,914 [0,901, 0,926];
detección 0,136 / 0,344 / 0,790. Verificada con semilla independiente: σ 2,7042 exacto; tamaño 0,0765
[0,0656, 0,0890]; cobertura 0,9235; detección a 0,25 → 0,148. Intentos: 0, correcto.

- El criterio de fallo es honesto y se aplicó tal cual, pero es unilateral: sólo puede fallar por
  falta de potencia, nunca por descalibración. Y la descalibración está (tamaño excluye 0,05,
  cobertura excluye 0,95). «Discrimina» se lee como validación y no lo es.
- La σ = 2,704 es un ancla legítima y va contra el proyecto (mayor σ, menor potencia); queda por
  encima del techo del IC de la σ realizada (2,336 [1,995, 2,669]). Tres reservas: proxy estructural
  distinto; el titular publica el IC de la mediana entre sorteos cuando la dispersión que importa es
  la banda entre sorteos [1,91, 4,02]; un solo régimen (SMH +253 %).
- La segunda ruta no es tautológica pero está a α nominal: reevaluada a α = 0,086 da 0,147 / 0,351 /
  0,829 contra 0,136 / 0,344 / 0,790 simulados. La brecha es el tamaño.
- Faltaba: MDE80 en número (1,05 pp/semana a 52 semanas); la celda T = 156 (tamaño 0,0615, cobertura
  0,9385: el α real de los ✓ de la cuenta es ~0,06); el ρ medido (mediana 0,000, banda [−0,190,
  +0,164]); la fuente de la descalibración (con ε normal 0,0745 / 0,9255: es el percentil de bloques a
  n = 52, no las colas); ε con agrupamiento de volatilidad (0,0770 / 0,9230, benigno).

Exigencias: A1 brazo de calibración pre-declarado y decir que la corrida 11 lo habría cruzado; A2
MDE80 en pp/semana y pp/año; A3 celda T = 156; A4 publicar ρ medido; A5 potencia ajustada por tamaño;
A6 contrastar σ 2,704 con 2,336; A7 no barrer el bloque después de ver la cobertura sin declararlo.

## (B) `intervalo_coherencia.md`: SOSTIENE CON EXIGENCIAS

Cifras verificadas idénticas a la última decimal (n 223, +14,3 pp, percentil [−1,4, 32,1], t [−3,5,
32,2], permutación 0,111, 69/37, exacta 0,0024). Identidad de conjuntos confirmada. Estimadores bien
aplicados (razón de sumas, permutación de signo sobre sumas de día, ICC de Fisher-Donner con m de Kish).

- La asimetría del retiro, en números: Σ por día en la regla firmada `−8, −4, −4, −4, −4, −2, 0×18,
  +1, +2, +2, +4, +6, +6, +6, +6, +8, +8`; el retiro se llevó 2 de 6 negativos y 0 de 10 positivos. No
  es acomodo: es el mecanismo del §82.3 escrito antes. Pero +14,3 pp no es «+9,7 medido mejor»: es
  otro estimando, y el movimiento entero sale de 2 días de 34.
- Bloqueante: R2 no se corrió sobre la rama nueva. Corrida: sin 15–23 jul cae a +7,8 pp, exacta
  0,0024 → 0,1354, permutación 0,111 → 0,433, percentil [−9,1, 25,6], t [−10,8, 26,5] (n 179, 27 días).
  Las fechas retiradas están fuera del bloque: la rama hereda la ventana afortunada.
- El estimador calibrado (t de clúster, cobertura 0,949–0,951 a k = 35) no es el que encabeza; acá
  k = 33 con un clúster de tamaño 1.
- No se puede decir que la rama «casi alcanza» significancia ni ordenar +14,3 contra un MDE.

Exigencias: B1 correr y publicar R2 sobre la rama; B2 declarar cuál IC está calibrado y con qué k;
B3 publicar la distribución de Σ por día y el conteo 2/0; B4 escribir que es un estimando distinto;
B5 si algún día se cablea, es un intento (352 → 353, 358 → 359).

## (C) `cuenta_papel.md` v2: SOSTIENE CON EXIGENCIAS

Sobrevive: el gate de invariancia (sujeto al auditor; 2 cortes es delgado); la identidad contable de
que la fricción la fija el número de órdenes; los signos negativos contra SMH; la negativa a llamar
tasa de falsos positivos al 5/24; que nada es habilidad.

No sobrevive: (1) los rangos de fricción leídos como cifras con incertidumbre (un sorteo, sin
intervalo); (2) cualquier comparación entre juegos; (3) la aritmética de primer orden como estaba
(205 × 0,35 / 500 = 14,4 % contra 12,4 % real: el tope del 1 % muerde bajo 35 USD); (4) la nota del
IC citaba la cobertura a 52 semanas cuando las 24 filas son de 156.

La σ con intervalo: el punto 2,336 es utilizable como insumo; el intervalo no, porque es un
percentil de bootstrap de una desviación y el bloque 1 validó sólo el IC de la media. Para leer M2
faltan: la base temporal (156 contra 52 declaradas), si el deslizamiento cuenta como comisión, un
intervalo por K semillas, y una errata fechada en el §3 del pre-registro (con la v2 el juego por
defecto queda en 12,4–12,6 %, la mitad de la vara: M2 no se dispara; `medio` sí cruza pero no rige).

Exigencias: C1 K ≥ 20 semillas con intervalo; C2 corregir la aritmética nombrando el tope del 1 %;
C3 nota del IC a 156 semanas; C4 medir la cobertura del IC de la sd antes de usarlo; C5 errata
fechada al §3 M2; C6 cruzar 2,336 contra 2,704.

## Criterios congelados tras los tres artefactos

V1 NO PASA (rige V1-bis pendiente; la rama de coherencia no lo cambia); V2, V4, V5, V6, V7 NO
EVALUABLES; V3 NO PASA (92,9 %, ratio 2,19×); R1 en pie el WS2b; **R2 SE DISPARA sobre la rama de
coherencia** (+14,3 → +7,8, p 0,433) y sobre la regla firmada (+9,7 → +2,6, p 0,675); R3 es del
auditor (dos cortes no cierran R3).

**DICTAMEN GLOBAL: NO CONCLUYENTE, con un hallazgo firme.** Los tres artefactos son trabajo honesto y
ninguno autoriza una afirmación positiva. El instrumento discrimina pero no está calibrado (α real
≈ 0,08 a 52 semanas, ≈ 0,06 a 156) y su MDE80 es una ventaja implausible; la rama de coherencia no
cambia la conclusión de día y bajo R2 se apaga; la cuenta en papel medía fricción de un solo sorteo.
Una vara de rechazo congelada no se omite porque la rama sea PROPUESTA.
