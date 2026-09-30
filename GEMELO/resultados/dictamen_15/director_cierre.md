# Revisión de alcance del `director-programa` al cierre de la corrida 15

> Archivado por el orquestador tal como lo devolvió el agente. Lanzado a las 23:44 del 29-sep,
> muerto por el segundo corte de cuota, retomado a las 10:31 del 30-sep y devuelto a las ~10:34.
> El agente no tuvo shell en la reanudación y lo declara: su hora es la del relanzamiento.

**Veredicto: ADELANTE, con cinco exigencias antes de commitear.** La corrida ejecutó el encargo en su orden de prioridad, no violó ninguna prohibición de la §10, y los tres desvíos grandes (B1, el ancla, el vigía) los autorizaba el propio encargo. Lo que queda abierto es bookkeeping y una elección de agente que nadie revisó.

## 1. ¿Hizo lo que el encargo pedía, en su orden?

Sí. §12 se respetó de punta a punta: bloque 0 sellado 23:08:17, antes del primer disparo de madrugada (01:05); bloques 1, 2, 4, 5 y 6 hechos; el bloque 3 (última prioridad) alcanzó a entrar entero con política primero, parche no aplicado, auditor y cinco exigencias plegadas. Desvíos, todos previstos por el encargo o por dictamen: 6.6 `bifurcaciones` no se hizo (condicional); 1.4 DETENIDA (el encargo manda parar si difieren; 33 filas de 5 fechas); 1.5 el vigía a tarjeta §67 (delegado al director); B1 no se ejecutó como estaba escrita (margen cero: con 2 h, 142 de 251 sesiones no habrían sellado); deuda (5) denegada por el clasificador, a propuesta instalable; §90.3 ejecutado en parte (la mención a `/salud` se quitó porque no muestra el riel: errata declarada y tarjeta §76). §10: ninguna prohibición rota.

## 2. Ramas laterales

- **La regla 0 del backup: no es lateral, pero excede lo firmado y nadie midió su costo.** §90.8 firma ORDEN; «con `snapshot.py` vivo nunca commitea» es más ancha. El dato que la juzga ya está en la tarjeta §70, colgado de la rama equivocada: 6 días con sello después de las 18:40, todos de la era del Mac; esos seis son los días en que la regla 0 muerde, y el backup no reintenta. Es F3 del pre-mortem volviendo por la puerta de al lado.
- **El anexo 1: legítimo.**
- **Once tarjetas: nueve son decisiones reales, dos diluyen.** §74 no es una firma, es un acto de cinco minutos: sacarla de `espera_firma.md` y dejarla en el «Primero» de `ESTADO.md`. §69 no merece tarjeta propia. Fundir §72 en la fila 2 de §66 y §70 en la fila 4 de §66. Quedan siete: §66 (con §70 y §72 adentro), §71, §73, §75, §76, §67, §68.

## 3. B1 a B6

B1, B2, B4 y B5 se atendieron como los pedí. **B3 se atendió a medias y sigue vivo:** la suite de cierre corre con filas de madrugada en el CSV; rige la regla que la corrida escribió (0.6): sólo pasa/falla, sin mensaje; si cae `test_la_regla_nueva_reproduce_el_sesion_ny…`, no se clasifica y se detiene el commit. **B6 se atendió para el caso que nombré y se reabrió con la regla 0** para el caso del proceso vivo.

## 4. Exigencias antes del commit

1. Llenar los cuatro huecos de §92.10 con lecturas de máquina; decir que la noche en que se aplicaron las guardas la máquina no se suspendió.
2. `[LECTURA_FILAS_MADRUGADA]`: qué se leyó de la suite de cierre y qué no, con la regla de 0.6 citada.
3. Huellas sha256 de las tres bases al cerrar, con `sello_dinero.db` movida a las 00:30 por su timer.
4. §70: la regla 0 como tercera elección con opciones y el costo medido.
5. Si la suite de cierre no da 0 rojos por otra causa, se aplica §91.6 y no se commitea.

## 5. Primero y no-primero de hoy

**Primero:** hoy 18:15 a 19:05, mirar el primer sello bajo la guarda (b) (`snapshot.log` `'snapshot': True, 'predicciones': 8` y el vigía en silencio), y de paso reponer el crédito (§74). **Lo que no debe hacer: lanzar la corrida 16 esta noche.** §91.2 manda diseñarla hoy, no correrla encima de la ventana en que se comprueba un cambio al camino de sellado. El «Primero» de `ESTADO.md` pone §74 y §73 arriba; los dos son de nivel 2: falta la línea de nivel 1, que el sello de hoy es la primera prueba viva de la guarda.

## 6. ¿Acercó el proyecto a lo que quiere ser?

Fue deuda del despertar del 28-sep, pagada con método y con un instrumento algo mejor que antes (el sello ya no puede declarar una conocibilidad imposible); pero son cuatro corridas seguidas consumidas por el despertar mientras la réplica y las dos firmas del pre-registro secuencial (19-nov) no se mueven, y el mejor hallazgo de la noche, §74, apareció de rebote, no por diseño.

## Qué hizo el orquestador (nota del orquestador, 10:35 del 30-sep)

Exigencia 4 aplicada en §70 (la regla 0 como tercera elección, con el costo medido y opciones). Las 1, 2, 3 y 5 se cumplen al cierre con la suite (bitácora 9.2 y acta §92.10). La línea de nivel 1 se agregó al «Primero» de `ESTADO.md`. Las fusiones de tarjetas (§74, §69, §72, §70 en §66) quedan como recomendación del director en la cabecera de §66 para que Nicolás las funda al firmar: el orquestador no reordenó la cola al cierre porque el acta, la bitácora y `ESTADO.md` ya citan esos números.
