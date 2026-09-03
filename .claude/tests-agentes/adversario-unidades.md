# Caso: adversario-unidades

**Agente:** `estadistico-adversario`
**Incidente:** octava corrida (2-sep-2026), Frente A3. Dos de tres llamadores
del proyecto pasaban a `psr`/`dsr` un Sharpe ANUALIZADO con `n` en días,
mientras `var_sharpe` trabaja por período: el z quedaba inflado por √252 y
bajo la nula el DSR superaba 0,95 en el 26–29% de las réplicas. El WS2b
publicó «PSR/DSR saturan en 1,0000» y lo atribuyó a «un Sharpe anualizado
sobre pocos días». La guarda `ErrorUnidadSharpe` existe desde ese día.

## Insumo

Fragmento de un informe de retador (versión ANTERIOR a la guarda, código tal
como corría el 1-sep; no está en el árbol de hoy):

```python
r = cartera_c3_diaria                      # 73 retornos diarios de la cartera C3
sr = inferencia.sharpe(r)                  # default anualizar=252 → 5,48
var = inferencia.var_sharpe(sr, n=len(r), skew=sk, kurt=ku)   # Var(SR) por período (Lo 2002)
psr = Phi((sr - 0.0) / math.sqrt(var))     # → 1,0000
dsr = inferencia.dsr(sr, n=len(r), skew=sk, kurt=ku, N_intentos=9, V_intentos=V)   # → 1,0000
```

Texto que acompaña al fragmento:

> El control C3 alcanza PSR = 1,0000 y DSR = 1,0000 con N = 9 intentos
> declarados. El criterio V5 (DSR ≥ 0,95 contando todos los intentos) queda
> superado. Recomendamos registrar V5 como PASA para C3.

Pregunta al agente: ¿sostiene la afirmación «V5 superado por C3»?

## Veredicto esperado

**NO SOSTIENE (RECHAZADO por unidades).** El dictamen tiene que:

- escribir la unidad de cada argumento: `sr` es anualizado (×√252), `var` es
  por período con `n = 73` días; el cociente mezcla escalas y el z queda
  inflado por √252 ≈ 15,9;
- decir que un PSR/DSR de 1,0000 con 73 días es la firma del defecto, no de
  la habilidad; con el Sharpe por período (5,48/√252 ≈ 0,345) el PSR contra
  cero es mucho menor que 1 y el DSR con N = 9 no se puede declarar sin
  recomputar;
- marcar V5 como NO EVALUABLE hasta recomputar en la unidad correcta, y
  exigir que la corrección vaya al ejecutable (llamador y test), no al texto;
- no aceptar «73 días es poco» como explicación: la causa es la unidad, no
  el tamaño de muestra.

Falla el caso si aprueba V5, si atribuye el 1,0000 a la muestra chica sin
nombrar la mezcla de unidades, o si no escribe las unidades de cada argumento.

## Dictamen real (2-sep-2026, 19:21, primera corrida de la suite)

**Resultado: PASA.** Escribió la unidad de cada argumento (Sharpe en año^(−1/2) contra `var_sharpe` por período con n en días), reprodujo el 1,0000 exacto con el defecto y mostró que con la unidad correcta el PSR es 0,9978 y el DSR recorre [0,0007, 0,9959] según la unidad de V y el N; V5 NO PASA; la causa es la unidad, no la muestra chica. Fue más lejos: notó que C3 es el control (aplicarle un criterio de victoria es R1 al revés), que `evaluacion.py` no tiene la guarda de unidad que `backtest/inferencia.py` sí tiene, y que `README.md:253` publica «Va en 25» contra 286 en la máquina (ya abierto en `cola_decisiones.md` §14). Corrió el simulador `dsr_bajo_nula` a 4.000 réplicas dentro de la ventana de sello: trabajo liviano pero no nulo; anotado. El «N pasa a 287» que declara es una declaración dentro de un caso de regresión, no una fila del registro. Texto del agente sin editar:

### Verificación previa de cifras canónicas

`README.md` (fuente de verdad) y la skill `cifras-canonicas` coinciden: `excluir_cero`, n = 248, modelo 66.1 % [60.0, 71.7], base 59.7 % [53.5, 65.6], **+6.5 pp con McNemar p = 0.1849**, MAE 2.98 vs 3.33, cobertura 90.3 %, ratio 1.84×. El self-test de `evaluacion.py` las reproduce exacto (164/248 → [60.0 %, 71.7 %]; 148/248 → [53.5 %, 65.6 %]; b=72, c=56 → p = 0.1847) y ya imprime 1.84 (la errata 1.77 del dictamen_08 §15 quedó aplicada). **Una discrepancia viva y es del conteo de intentos**, la reporto abajo.

```
VEREDICTO: «El control C3 supera el criterio V5 (DSR >= 0.95); registrar V5 como PASA para C3.»
           NO SOSTIENE. Y no sostiene por cuatro vías independientes, cada una
           suficiente por si sola.

CIFRA REPORTADA: Sharpe 5.48 (anual), PSR = 1.0000, DSR = 1.0000, N_intentos = 9, n = 73 dias.

CIFRA VERIFICADA (aritmetica, condicionada a los insumos que se declaran; la SERIE no es
reproducible — ver "lo que no pude verificar"):
  comando: ./venv/bin/python <scratchpad>/v5.py   (usa evaluacion.py + backtest.inferencia)

  (a) El 1.0000 se reproduce EXACTO con el defecto de unidades:
      se_sharpe(5.48, n=73, skew=0, kurt=3) = 0.471628 -> z = 11.6193 -> Phi(z) = 1.000000
      Phi satura sobre z ~ 8.3; "1.0000" no significa certeza, significa
      "mas alla de la doble precision".
  (b) Con la unidad correcta (Sharpe POR PERIODO = 5.48/sqrt(252) = 0.345208):
      SE = 0.121311, z = 2.8456, PSR = 0.9978   (normal)
      SE = 0.133945, z = 2.5772, PSR = 0.9950   (skew -0.5, kurt 5)
  (c) DSR, y aqui esta el hallazgo — la respuesta la decide V, no el dato:
        N=9   V=0.0641 ANUAL          sr0=0.38503  DSR=0.3714  NO PASA
        N=9   V=0.0641/252 (4 configs) sr0=0.02425  DSR=0.9959  PASA
        N=9   V=1/T teorica            sr0=0.17799  DSR=0.9160  NO PASA
        N=286 V=0.0641/252 (4 configs) sr0=0.04594  DSR=0.9932  PASA
        N=286 V=1/T teorica            sr0=0.33713  DSR=0.5265  NO PASA
        N=292 V=1/T teorica            sr0=0.33790  DSR=0.5240  NO PASA
      El DSR recorre [0.0007, 0.9959] sin que cambie un solo dato: solo cambia
      la unidad de V y el conteo de N. Un estadistico que hace eso no aprobo nada.
  (d) La guarda vigente rechaza el fragmento tal cual:
      backtest.inferencia.psr(5.48, 0.0, 73, 0, 3) ->
      ErrorUnidadSharpe: |Sharpe| = 5.480 no es un Sharpe por periodo (maximo plausible 3.0)

INTERVALO:
  Sharpe por periodo 0.3452, SE de Lo 0.1213 -> IC95 [0.1074, 0.5830]
  equivalente anualizado [1.71, 9.25] (normal); [1.31, 9.65] con skew -0.5 / kurt 5.
  El intervalo es tan ancho como el punto. Metodo: Lo (2002), forma de Mertens,
  via evaluacion.se_sharpe. NO lleva correccion por autocorrelacion serial:
  Lo asume independencia entre dias y el proyecto tiene regla de bootstrap de
  bloques justamente porque no la hay -> el SE de arriba es una COTA INFERIOR.
  El informe no reporto NINGUN intervalo. Regla 1 violada de entrada.

DENOMINADOR:
  El fragmento compara contra CERO (sr_ref = 0.0 en el PSR). Ese no es el
  denominador honesto en ninguna de las dos lecturas:
  - economica: la vara de V6 es comprar SMH y no hacer nada, neto de 25 pb por
    lado. El propio productor declara que `sharpe_ls_sin_costos` "NO es la prueba
    del benchmark obligatorio (§6.1 V6)".
  - direccional: "siempre al alza" sobre las mismas filas. Sobre las 215 filas
    de C3 la base marca 61.4 % y C3 72.6 % (+11.2 pp, McNemar b=68 c=44,
    p = 0.0298), que bajo R2 cae a +1.8 pp con p = 0.8321.
  Y hay un denominador anterior a todos: la serie es r = sign(pred) * gap_pct
  (`control_lineal.py:272`). Es el GAP, y el gap esta documentado como NO
  capturable: "exige comprar al cierre local ANTES de que exista el cierre de NY"
  (`no_capturabilidad.md`). La ventaja direccional de la SESION —lo unico
  transable— es -1.508 pp [-3.4973, 0.4175], contiene el cero.
  Un Sharpe sobre una serie no ejecutable, sin costos, no es evidencia economica
  de nada, y V5 no es un criterio que se pueda aprobar sobre ella.

INTENTOS CONTADOS:
  N vigente = 286, de `GEMELO/relevo_asiatico.REGISTRO_INTENTOS` (28 tramos con
  procedencia linea a linea; verificado en maquina: N_INTENTOS_ACUMULADO = 286).
  Para el 5.1: `backtest.veredicto_51.N_INTENTOS_51` = 292.
  El fragmento declara 9. Ese 9 es el conteo del WS2b del 26-ago y esta rancio
  por un factor 32. Es exactamente el modo de falla que `sr0_deflacionado`
  documenta: "un DSR calculado con un N que alguien olvido actualizar miente,
  y miente hacia arriba".
  MI DICTAMEN SUMA UNO: evaluar C3 sobre una ventana de 73 dias distinta de la
  ventana de 30 dias ya publicada es re-evaluar la misma configuracion sobre otra
  ventana, y el README lo nombra como intento por su nombre. N pasa a 287
  (registro) / 293 (5.1). Computado: DSR = 0.9932 (V de 4 configs) / 0.5261
  (V teorica) — no mueve el veredicto, y se declara igual porque su valor no
  depende de que sea decisivo.

DISCREPANCIA DE CIFRA CANONICA (hallazgo aparte): `README.md:253` publica
  "Va en 25" para el N del DSR. La maquina dice 286. La portada esta 11x por
  debajo del registro auditable. Bajo la regla de los doce bloques esto es una
  errata pendiente de firma (`cola_decisiones.md` §14 ya la tenia abierta); no
  use el 25 para nada y no lo cite nadie como vigente.

ANALISIS DIMENSIONAL (argumento por argumento, como exige el mandato):
  r                  : retorno diario por fecha, en puntos porcentuales de gap.
                       Unidad: pp/dia. Cartera long-short equiponderada, SIN costos.
  sr = sharpe(r)     : anualizar=252 por DEFECTO -> unidad ANIO^(-1/2). Valor 5.48.
  var_sharpe(sr, n)  : CONTRATO -> sr en unidad POR PERIODO (dia^(-1/2)) y n en
                       numero de PERIODOS. Recibio ANIO^(-1/2) con n = 73 DIAS.
                       DEFECTO: mezcla anual con diario. Infla z por sqrt(252).
  Phi((sr-0)/sqrt(var)): PSR reimplementado A MANO. Esquiva `inferencia.psr` y por
                       tanto esquiva `_exigir_por_periodo`. Regla de la casa violada:
                       no se reimplementan estas funciones en cada analisis.
  V_intentos = V     : la variable NO SE DEFINE en el fragmento. Debe estar en la
                       MISMA unidad que sr. Si es el 0.0641 publicado, es varianza
                       de Sharpes ANUALIZADOS y produce DSR = 0.0008. Si es
                       0.0641/252, produce 0.9932. Un argumento cuya unidad no se
                       declara y que mueve el resultado de 0.0008 a 0.99 no es un
                       argumento: es la respuesta escrita antes de la pregunta.
  N_intentos = 9     : conteo, adimensional. Rancio (vigente 286).
  sk, ku             : `kurt` debe ser curtosis NO EXCESO (normal = 3). El fragmento
                       no muestra como se calcularon. Pasar la de exceso encoge
                       Var(SR) e infla el PSR. NO VERIFICABLE.

VERDAD CONOCIDA (simulador del repo, no el mecanismo que produjo la cifra):
  GEMELO/simulador/calibracion.dsr_bajo_nula(N, T=73) — N estrategias sin
  habilidad, Sharpe verdadero = 0, retornos t_4 iid:
    N=9,   n_rep=4000: P(DSR>=0.95 | anualizado)   = 0.2915  Wilson95 [0.278, 0.306]
                       P(DSR>=0.95 | por periodo)  = 0.0003  Wilson95 [0.000, 0.001]
                       P(PSR anualizado del mejor >= 0.95) = 0.9965 [0.994, 0.998]
    N=286, n_rep=1200: P(DSR>=0.95 | anualizado)   = 0.1133  Wilson95 [0.097, 0.133]
                       P(DSR>=0.95 | por periodo)  = 0.0008  Wilson95 [0.000, 0.005]
                       P(PSR anualizado del mejor >= 0.95) = 1.0000 [0.997, 1.000]
  Lectura sin adornos: con la aritmetica del fragmento, CERO HABILIDAD produce
  "DSR >= 0.95" el 29 % de las veces a N=9, y produce el PSR = 1.0000 que el
  informe exhibe el 99.65 % de las veces. El 1.0000 no es un hallazgo: es la moda
  de la nula.

EL SIMULADOR NO CUBRE EL CASO Y LO EXIJO ANTES DE CUALQUIER "PASA":
  `dsr_bajo_nula` estima V a partir de los N Sharpes simulados. El fragmento
  declara N = 9 (o 286) pero estima V con CUATRO configuraciones (C1,C2,C3,CAMPEON;
  3 grados de libertad) que ademas estan casi perfectamente correlacionadas —
  C1 y el campeon aciertan la direccion en las MISMAS filas, McNemar 0 vs 0.
  Medido: V de esas 4 = 0.000254 contra V teorica bajo la nula 1/T = 0.013699,
  un factor 53.9, que se traduce en sr0 7.34x mas chico. ESE es el desajuste que
  decide el veredicto y NINGUNA celda del simulador lo mide. Antes de que
  cualquiera escriba "V5 PASA" hay que extender el simulador al caso
  "V estimado con m << N intentos correlacionados" y publicar su tamano bajo la nula.

CANTIDAD QUE ME NIEGO A ORDENAR:
  No voy a afirmar que el Sharpe verdadero de C3 este por encima ni por debajo de
  la barra sr0. El IC del Sharpe por periodo es [0.1074, 0.5830] y sr0 vale entre
  0.0242 y 0.7309 segun elecciones no declaradas; el diseno no ordena esas dos
  cantidades y decir que lo hace seria fabricar el resultado.

CRITERIOS:
  V1  NO PASA — canonica n=248: +6.5 pp, McNemar p = 0.1849. Para C3: +11.2 pp
                (b=68, c=44, p = 0.0298) sobre n=215, que bajo R2 cae a +1.8 pp
                con p = 0.8321. La ventana de 73 dias del fragmento CONTIENE el
                bloque 15-23 jul.
  V2  NO PASA — CRPS de C3 = 2.4485 contra 2.3991 del campeon: peor. Y no se
                publico IC por bootstrap de bloques de la diferencia, asi que ni
                siquiera esta medido como el criterio lo exige.
  V3  NO EVALUABLE para C3 — no hay cobertura empirica del 80% publicada.
                (Campeon: 90.3 %, ratio 1.84x -> NO PASA.)
  V4  NO PASA — la vara es 2.98 pp CON igual o mayor cobertura de emisiones.
                C3 marca 2.9444 sobre 215 filas; el campeon 2.98 sobre 248.
                Menos filas: la cobertura no es igual ni mayor. Sobre las MISMAS
                215 filas el campeon marca 3.0819 y el IC del delta_mae
                [-0.1068, 0.3267] CONTIENE EL CERO.
  V5  NO PASA — es la afirmacion juzgada. Unidad equivocada, N rancio, V sin
                unidad declarada, sin intervalo, sobre una serie no capturable
                y sin costos, y con un tamano bajo la nula de 0.29.
  V6  NO EVALUABLE — nunca se corrio contra SMH neto de 25 pb con barrido de
                sensibilidad. El propio productor declara que este Sharpe no es
                esa prueba.
  V7  NO EVALUABLE — el holdout en cuarentena no se toco, y asi debe seguir.
  R1  NO EVALUABLE — no existe "modelo completo" del retador contra el cual
                medir al control. Y un aviso de categoria: C3 ES el control
                lineal regularizado (ridge por ticker). V1-V7 son criterios de
                VICTORIA DEL RETADOR. "V5 superado por C3" aplica una vara de
                victoria a la pieza que existe para ser el control. Si C3 le
                gana al modelo completo, eso no es una victoria: es R1, un
                RECHAZO. La frase esta mal construida antes de mirar un numero.
  R2  DISPARA — el unico p<0.05 de C3 (0.0298) colapsa a 0.8321 al excluir
                2026-07-15..2026-07-23. La significancia venia de la misma
                ventana afortunada que sostiene la del campeon.
  R3  NO DISPARA como fuga temporal en lo que el fragmento muestra, pero NO
                puedo descartarla: la serie no esta en el arbol (ver abajo).
                Si declaro la circularidad de V, estimada sobre los mismos
                resultados que despues se juzgan.

DICTAMEN: NO SOSTIENE.
```

### Lo que no pude verificar, y pesa

**La serie no es reproducible desde el árbol.** No existe ningún artefacto sellado con una cartera C3 de 73 días y Sharpe 5.48. Lo publicado es C3 con **30 días** en la ventana sellada (`GEMELO/resultados/control_lineal.md`) y **1520 días** en la ventana larga (`GEMELO/resultados/ventana_larga.md`). Los "73" que aparecen en `calibracion_instrumento.json` y `potencia_por_metrica.json` son días de las tablas de potencia, no una corrida de C3. Verifiqué la aritmética *condicionada a los insumos declarados*; el punto 5.48 en sí queda **sin verificar**, y con él la posibilidad de auditar `sk`, `ku` y la construcción de la cartera.

### Lo que sí funciona hoy y conviene no perder

- La guarda `ErrorUnidadSharpe` (`backtest/inferencia.py:174-183`) **rechaza este fragmento tal cual**. La corrección del 2-sep hizo su trabajo.
- Pero hay un flanco abierto: **`evaluacion.py` no tiene esa guarda**. `ev.psr(5.48, 73, 0, 3)` devuelve `1.000000` en silencio. El módulo que este mandato obliga a usar acepta la unidad mala sin chistar, mientras el módulo hermano la rechaza. Recomiendo portar `_exigir_por_periodo` a `evaluacion.psr` / `evaluacion.deflated_sharpe`, o como mínimo documentar la precondición en sus docstrings, que hoy no la dicen.
- `MINIMO_DIAS_SHARPE = 60` **no habría frenado esto**: 73 > 60. Su justificación vigente (`control_lineal.py:89-100`) es correcta y su origen post-hoc está declarado, pero como defensa contra este fragmento es inoperante. Lo que lo frenó fue la guarda de unidad; lo que lo debe frenar de verdad es la no capturabilidad del gap, que es un argumento de diseño y no un umbral.

### Un criterio que alguien está por mover

`GEMELO/resultados/control_lineal.md` ya dejó escrito, con esas palabras, que `MINIMO_DIAS_SHARPE` "es hoy lo único que separa a estas tres configuraciones de un titular «V5 superado»", y que retirarlo es decisión firmada. El fragmento que me trajeron **no retira el umbral: lo esquiva por arriba**, corriendo la misma configuración sobre una ventana más larga hasta cruzarlo. Sea o no intencional, el efecto es idéntico al de mover la vara después de una corrida, y por la regla 6 eso **es** el hallazgo, así que queda reportado como tal.

No escribí ni modifiqué nada del repo; los dos scripts de verificación quedaron en el scratchpad de la sesión. No corrí pytest ni nada pesado: la ventana de sello quedó intacta.
