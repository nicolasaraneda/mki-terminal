# Dictamen del `curador-epistemico` — los textos de la corrida 14

Transcripción por el orquestador. Solo lectura, `mode=ro`, sin descargas (ventana 17:50–20:30).
Dictaminado sobre el árbol congelado a las **18:04** (verificó mtimes), después de que se le avisara que el
árbol se había movido tres veces mientras leía. 9 documentos pedidos más el cuarto dictamen que apareció
después. Volumen: 1.094 líneas cambiadas en rastreados y 2.153 nuevas sin versionar.

```
DICTAMEN: PUBLICABLE CON CORRECCIONES
```

**Los cinco bloqueantes están aplicados**; las diez observaciones, las que se podían aplicar sin mover
cifras heredadas. Lo que queda va al encargo 15 y está en `cola_decisiones.md`.

## Lo que reprodujo contra la máquina, por su cuenta

Las 24 filas y que `available_at > timestamp_utc` da una sola fecha en toda la tabla; `CORTE_README` =
2026-08-28; `verificacion_apertura` con 0 filas del 28-sep y máximo 2026-09-24; las 8 predicciones contra
`beta × (−1,63)`; 462 filas de `sellos_dinero`, 14 fechas, 9 con `cuenta_para_N = 1`; 1.188 filas de la
sonda y sus 21 tests en verde; 34 de 36 sin cierre el 22-sep a las 23:35; 35 de 36 con
`ultima_fecha_close = 2026-09-28` a las 13:42, con TOELY como excepción; la tabla de M2 completa (0/20
contra 19/20 a h=52, Wilson [76,4 · 99,1], medianas 3,87 / 6,44 / 9,38); 25/3 = 8,3333; los contadores
354 / 360 / 4; `modo.py` = titular en `main`; la fórmula de `roca_chip` y que se sella el percentil y no el
crudo; y el canal de publicación de `roca_chip`.

**Palabra «confianza»: 0** en todo el texto nuevo (el único rastro es la columna legacy `confianza_r2` del
esquema). **Cifras retiradas: `cifras.reintroducciones()` da 0** en los nueve documentos nuevos y en los
cuatro ejecutables tocados; la banda «14 % a 43 %» lleva su marca RETIRADA en la misma línea, y las 53
coincidencias de `DECISIONES.md` están todas en actas anteriores, **ninguna en el §89**.

## BLOQUEANTES

**B1 — `roca_chip` 44 → 17 se publicaba como daño medido, y la máquina marca su insumo dominante como
sospechoso.** Del log del job de las 18:15, o sea **44 minutos después de la medición**:
`data/snapshot.log:147` → `- Tokyo Electron (8035.T): salto de -80% el 2026-09-28 — revisar split/dato
corrupto`. Única aparición en todo el log; `salud_datos_al` lo emite con umbral 0,40 llamándolo «posible
split mal ajustado o dato corrupto». **Por qué toca a `roca_chip`:** 8035.T es eslabón del nivel 2, que
tiene tres tickers, sobre cinco niveles de peso igual, y la serie es `mom20`, así que −80 pp en su `mom20`
mueve el crudo de la cadena **(80/3)/5 = 5,33 pp** contra los 6,44 pp observados (+3,64 → −2,8): **explica
del orden del 83 %**, y «el cambio de signo, ~5,8 pp, INFERIDO de la misma línea es casi exactamente el
tamaño del artefacto». Declaró que el 5,33 es **aritmética de orden de magnitud, no una remedición**, y que
no pudo recomputar sin descargar. *Aplicado: el 17, los 27 puntos y la lectura de los dos canales quedan
**PROVISIONALES** con la cita al log en la misma línea, en los cinco documentos.* (El orquestador agregó
después: 8035.T cotiza ~55.000 yenes y **−80 % es exactamente un split 5:1**.)

**B2 — «peor predicción (8035.T) 0,11 pp» se atribuía a la contaminación, y es el mismo ticker y la misma
fecha de B1.** Con 0,02 pp de desvío en el escalar, **el máximo propagable con las betas selladas es
0,81 × 0,02 = 0,016 pp**. El 0,11 sólo existe porque **la beta de 8035.T se reestimó**. La bitácora lo
decía; los cuatro documentos derivados no, «así que un lector que verifique la tabla de §61 no la puede
reproducir». *Aplicado en los cuatro, más el número que sí mide la barra parcial: **entre los siete tickers
sin dato marcado, la peor diferencia es 0,03 pp**.*

**B3 — una afirmación de verificación falsa por los números impresos en la misma línea.** «recuperó las
betas … todas dentro de 0,005 de las selladas»: **0,497 contra 0,56 son 0,063, doce veces la tolerancia
declarada**; 0,801 contra 0,81 son 0,009; 0,304 contra 0,31 son 0,006. **Tres de ocho la incumplen.**
*Aplicado: «las siete dentro de 0,009 —el redondeo a dos decimales ya da ±0,003— y 8035.T a 0,063 porque su
beta se reestimó». El hallazgo que sostiene sobrevive con la tolerancia corregida.*

**B4 — la tarjeta que Nicolás firma decía cuatro definiciones donde toda la corrida dice seis.** La nota
nueva del §43 enumeraba cuatro y **omitía la urgente** —«qué es el primer aporte», la que puede disparar M2
con dos órdenes sobre los 5,00 USD ya fondeados— y el veredicto NO APLICABLE. «Es la única incoherencia de
las que revisé **que cambia lo que Nicolás ve al firmar**.» *Aplicado: §43 lleva las seis enumeradas, con la
urgente y su aritmética, más los cuatro huecos menores y la exigencia del adversario sobre el simulador.*

**B5 — «el PC volvió de suspensión a las 14:40» iba como hecho medido en tres documentos, y la hora no sale
de ninguna medición citada.** Lo medido es el hueco del journal entre `2026-09-25T02:16:24` y
`2026-09-28T14:42:52`, el `systemd[317]` sobreviviente y el uptime; **las 14:40 vienen del encargo**. Y el
propio auditor exige que «suspendido y no apagado» sea inferencia, nunca hecho registrado. *Aplicado en las
tres —`espera_firma.md` §61, el acta §89.1 y `cola_decisiones.md`—: se usa **14:42:52**, que es lo que da la
máquina, y la suspensión va marcada como inferencia con su ventana [vie 02:16, vie 17:50].*

## OBSERVACIONES, y qué se hizo con cada una

| # | Observación | Estado |
|---|---|---|
| O1 | La no-reproducibilidad de la columna «recomputado» estaba en dos documentos y **no en el acta ni en las salvedades del §61**, «que cita cuatro cifras nuevas cuya única fuente es la palabra de la corrida». | **Aplicada** en los dos. |
| O2 | «904 tests (`pytest --collect-only -q`)» **no reproduce con ese comando**: da **907**; 904 es con el alcance `tests/`. Los 3 son casos parametrizados de `GEMELO/propuestas/`. Y es la cifra que §88.5 manda publicar en un badge. | **Aplicada** en los cuatro sitios. |
| O3 | El encabezado de §8.2 («idénticas al abrir y al cerrar, las tres») quedaba contradicho por el párrafo que se le apendó abajo. | **Aplicada**: encabezado reescrito. |
| O4 | «(tres dictámenes)» cuando en `dictamen_14/` hay cuatro. | **Aplicada** (y con este archivo son cinco). |
| O5 | El encabezado de `estado_epistemico.md` nombraba tres agentes y omitía el dictamen de cierre; y la numeración romana salta (iv)→(vii)→(ix) sin decir que se retiraron tres ítems. | **Aplicada**. |
| O6 | «0 pares de transición 1 → 0» iba **sin denominador y sin Wilson**, cuando el hallazgo análogo de la corrida 13 sí llevaba su intervalo. «El cero es censurado, no vacío.» | **Aplicada**: 0 de **1.008** oportunidades (4 noches × 36 tickers × 7 intervalos), Wilson 95 % [0,00 · 0,38] %. |
| O7 | El canal de look-ahead del ancla (`snapshot.py:163` ancla `sesion_objetivo` en `available_at`, que el 28 estaba 2 h 17 min en el futuro; medido nulo en efecto, «coincidencia de esta fecha, no garantía») **vivía sólo en el dictamen**, y el §61 pide firmar una regla justo sobre ese camino. | **Aplicada**: está en §61. |
| O8 | La tabla «Firmado en §82, pendiente de ejecución» sigue pidiendo aplicar `snapshot140.diff`, **que ya está aplicado** en producción por el acta §84.1. Texto preexistente, pero el archivo se republica hoy. | **Anotada en su sitio**, no corregida de paso. |
| O9 | `sonda_cierre_resumen.md` publica «mediana 22:35» sobre 2 noches, **y las dos noches censuradas (22 y 23-sep) son justamente las tardías**, así que el estadístico está condicionado a las noches en que el evento se observó. | Inventariada (bitácora §8.6), diferida al encargo 15. |
| O10 | `data/sombra_telegram.log` con mtime 18:25:01 en una máquina **titular**, y contenido que termina en agosto. No lo pudo explicar en solo lectura. | **Abierta**: ítem de diagnóstico, no afecta ninguna afirmación revisada. |

## Lo que confirmó del aviso que se le mandó

Verificó en el árbol de las 18:04 que «no se materializaron en esta fecha» está en los cuatro documentos y
que «quedan refutadas» **no aparece en ninguno**; que «una de las dos sospechas» y su ubicación fuera de los
cuatro fundamentos está dicha; que (v), (vi) y (viii) salieron **con el hueco declarado**; que las tres
condiciones del dictamen complementario están aplicadas en (iii-bis); que `noticias.db` está declarado con
su hora; y que la bitácora §4.4 ya dice seis con la enumeración completa.

Sobre la corrección de la §9 del pre-registro: «tiene su nota de redacción, es honesta ("la midió y es
falsa"), y **la frase falsa no queda en ningún lugar presentada como verdadera**: sus seis apariciones en el
repo son todas bajo marca de falsedad o de corrección».

Y lo que más importa del veredicto general: «**Ninguna afirmación escala a "hay fuga temporal" ni a "el
track record está contaminado"**: los cinco documentos dicen "no hay look-ahead" y "nada publicado está
contaminado" con el corte a la vista, y la inversión de las 8 direcciones va siempre en condicional o como
no materializada.»

## Sus zonas ciegas

1. **No pudo recomputar nada** —descargar está prohibido en la ventana y su mandato es solo lectura—, así
   que **todo B1 y B2 depende de un aviso del log y de aritmética de orden de magnitud**. La prueba que lo
   cierra, después de las 20:30: mirar el `Close` de 8035.T del 25 y del 28-sep, decidir si es split no
   ajustado o dato corrupto, y **recién entonces** releer `roca_chip_al(date(2026,9,28))`.
2. La columna «recomputado» no la pudo verificar por ninguna vía; reprodujo su coherencia interna y **ahí
   encontró B3**.
3. **Leyó el árbol en tres estados distintos** (empezó 17:24, el árbol se movió hasta 18:04). Releyó al
   congelado cada sección que cita, «pero no puedo descartar que algo que leí temprano y no releí haya
   cambiado».
4. No verificó los dos README ni `cifras.py`: los bloques que los tocaban no se ejecutaron y el diff
   confirma que están intactos.
5. No juzgó el 897 heredado de la corrida 13: está declarado como inventario y viene de HEAD.
6. No pudo explicar O10 sin ejecutar algo que escribiera.
