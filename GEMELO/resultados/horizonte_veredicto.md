# ¿Es el instrumento medible en principio? — veredicto del Frente B (séptima corrida, 2-sep-2026)

**Toda cifra sale de `GEMELO/SECUENCIAL/horizonte.py`** (`horizonte.json`,
tablas en `horizonte.md`). Ancla pinchada: `hasta_sello = 2026-08-31`,
regla firmada, `excluir_cero` → n = 246 filas en 35 días sellados, ventaja
+9,3 pp, IC95 de clúster de día [−7,5, +26,2], n efectivo 69, ICC 0,39.
Dos rutas independientes (analítica 1/√D y simulación con días reales
remuestreados, 3.000 réplicas por celda con Wilson) que coinciden dentro
del ruido de Monte Carlo (p. ej. potencia a 250 días frente a 9 pp: 0,82
[0,81, 0,83] simulada contra 0,80 analítica por construcción).

> **EN DIEZ SEGUNDOS**
>
> 1. **No es estructuralmente subpotente.** El clúster de día no acota el
>    n efectivo: lo divide por ~3,6 y **crece lineal, ~2 observaciones
>    efectivas por día sellado**. Cualquier efecto fijo es detectable con
>    tiempo suficiente.
> 2. **Pero el tiempo suficiente es de años, no de meses.** Al 80% de
>    potencia y α = 0,05: **9 pp → ~250 días sellados, IC95 [109, 370]
>    (jul-2027, entre dic-2026 y feb-2028)**; **6,5 pp → ~475 [209, 709]
>    (jul-2028)**; **5 pp → ~800 [354, 1.199] (dic-2029)**. Los intervalos
>    heredan el del propio SE de día (bootstrap anidado: 8,0 pp [5,7,
>    10,5]) y son anchos porque 35 días estiman mal su propia varianza.
>    Coincide con la tabla de `GEMELO/SECUENCIAL/DISEÑO.md` obtenida por
>    otra vía (McNemar × DEFF).
> 3. **El veredicto 5.1 del 25-oct llegará con ~73 días: MDE al 80% de
>    16,6 pp, IC95 [11,0, 20,3]; potencia 0,36 [0,34, 0,37] frente a 9 pp
>    (3.000 simulaciones).** Es decir, el 25-oct el instrumento sólo puede ver un efecto
>    casi el doble del que importa. La «franja invisible» entre 8–9 pp de
>    relevancia y 24 pp de detectabilidad de hoy **se cierra recién a
>    mediados de 2027.**
> 4. **Lo que sí es estructural es otra cosa: el instrumento no puede
>    distinguir «efecto constante» de «efecto que se fue».** Primera mitad
>    de la ventana +19,2 pp [−3,5, +44,1] (contiene el cero); segunda mitad
>    **0,0 pp** [−21,6, +20,5] (contiene el cero). Los dos se solapan —no es evidencia de cambio—, pero
>    todo el cálculo del punto 2 supone que el efecto de 2027 es el de
>    2026, con un solo régimen sellado, un modelo congelado y una fuente
>    que sirve estados distintos (Frente A). **Eso no lo arregla acumular
>    días: lo arregla tener más de un régimen, y eso no depende del
>    proyecto.**
> 5. **Hallazgo colateral RETIRADO y reemplazado:** la primera versión
>    decía «α empírico 0,083 a 35 días: anticonservador con pocos días». El
>    adversario lo replicó subiendo las simulaciones y era ruido de Monte
>    Carlo (n_sim = 300; y la permutación re-sembraba igual en cada réplica,
>    una sola matriz de signos para todas). Corregido en el ejecutable
>    (semilla por réplica, n_sim = 3.000 como exigió el dictamen): **α
>    empírico 0,055 [0,048, 0,064] a 35 días, 0,045–0,053 en los demás
>    horizontes, todos con IC que contiene 0,05.** El test de permutación de signo por día está bien
>    calibrado en todo el rango. Nada que agregar al Frente C.
> 6. **R2 dispara sobre este mismo ancla, y la primera versión lo llamó
>    «mitades».** Excluyendo el bloque 15–23 jul (criterio de rechazo
>    congelado, `GEMELO/DISEÑO.md` §6.2): n = 202, **+2,5 pp**, IC95 de día
>    [−13,6, +19,2] (contiene el cero), McNemar de filas p = 0,675 (b = 48,
>    c = 43), permutación de día p = 0,82. Los seis días del bloque 1 están
>    enteros en la «primera mitad» del punto 4: no era estacionariedad, era
>    R2. Lo cazó el adversario.

## La tabla que fija el calendario

| efecto de interés | días sellados para potencia 0,80 (IC95) | años de sellado | fecha estimada (IC95) | potencia HOY (35 días) |
|---|---|---|---|---|
| 12 pp | 139 [61, 208] | 0,6 | feb-2027 [oct-2026, may-2027] | 0,29 |
| **9 pp** (relevancia, 25 pb) | **248 [109, 370]** | **1,1** | **jul-2027 [dic-2026, feb-2028]** | 0,18 |
| 6,5 pp (lo publicado en el README) | 475 [209, 709] | 2,1 | jul-2028 [may-2027, jul-2029] | 0,12 |
| 5 pp (umbral de `RELEVO.md`) | 803 [354, 1.199] | 3,6 | dic-2029 [ene-2028, ago-2031] | 0,09 |

Simulación con días reales (potencia a 250 días: 0,81 para 9 pp; a 500:
0,85 para 6,5 pp; a 750: 0,81 para 5 pp): las dos rutas dicen lo mismo.

| horizonte | fecha | MDE 80% (IC95) | MDE 50% |
|---|---|---|---|
| hoy (35 días) | — | **24,0 pp** [15,9, 29,3] | 16,8 pp |
| veredicto 5.1 (73 días) | 26-oct-2026 | **16,6 pp** [11,0, 20,3] | 11,6 pp |
| 125 días | ene-2027 | 12,7 pp [8,4, 15,5] | 8,9 pp |
| 250 días | jul-2027 | **9,0 pp** [5,9, 10,9] | 6,3 pp |
| 500 días | ago-2028 | 6,3 pp [4,2, 7,7] | 4,4 pp |

## La respuesta a la pregunta dura, escrita con la misma firmeza en las dos direcciones

**¿Es el instrumento estructuralmente subpotente para su propia pregunta?**

- **Como aparato estadístico: no.** Con la estructura real (8 tickers, 4
  bolsas, ICC 0,39, ~0,9 sellos por día hábil) el n efectivo crece a ~2 por
  día y el MDE cae como 1/√D. Un efecto de 9 pp es detectable en poco más
  de un año. Nada en la aritmética lo impide.
- **Como instrumento para responder ANTES de que la respuesta deje de
  importar: sí, hoy.** El diseño del proyecto fija un veredicto el 25-oct
  con MDE de 16,6 pp [11,0, 20,3]. Un efecto de 9 pp —el que el propio
  proyecto declaró relevante— tiene **36% [34, 37] de probabilidad** de ser
  detectado ese día (3.000 simulaciones a 73 días; la ruta analítica da
  0,33; arrastrando el IC del SE, entre 0,25 y 0,57). Un veredicto negativo
  del 25-oct **no será evidencia de ausencia**, y hay que escribirlo antes
  de correrlo, con ese intervalo.
- **Como instrumento para la pregunta que de verdad importa —«¿el efecto
  persiste?»— es ciego por construcción hasta que el mercado cambie de
  régimen.** Un solo régimen (`Alcista · vol alta`) en 35 días; el modelo
  congelado; la ventaja de la segunda mitad en cero. Acumular 250 días bajo
  un régimen responde «¿hubo efecto en ese régimen?», no «¿hay efecto?».

**Lo que cambia río abajo si esto se acepta:**

1. El MDE del diseño secuencial (`espera_firma.md` §5) no es sólo una
   elección de valores: es una elección de **cuánto tiempo el proyecto
   está dispuesto a esperar por una respuesta que, en el camino, puede
   volverse sobre otro régimen.** +10 pp (jul-2027) es la única opción que
   responde dentro de un horizonte en el que el régimen tiene chances de
   ser el mismo.
2. El veredicto 5.1 del 25-oct necesita, **escrito antes**, una frase que
   diga que su potencia frente al efecto relevante es 0,36 [0,34, 0,37] (y
   [0,25, 0,57] con la incertidumbre del SE). Sin eso, un NO PASA se leerá
   como refutación.
3. El Frente E (estimandos alternativos) tiene sentido justamente acá: si
   el endpoint binario necesita 250 días, un endpoint continuo con la misma
   información podría necesitar menos. Es propuesta y va con la regla
   quinta.

## Lo que este veredicto NO dice

- No dice que la ventaja sea cero. Dice que a 35 días el instrumento no
  puede verla si mide 9 pp, y que a 73 tampoco con potencia razonable.
- No dice que el efecto cambió entre mitades: los intervalos se solapan.
- El gasto de α del diseño secuencial (O'Brien-Fleming) es un factor
  **1,0241** sobre los días (`DISEÑO.md` §A3.3, líneas 774-775: 2,4%, no
  «3–5%» como decía la primera versión): 248 → 254 días. Irrelevante frente
  al IC [109, 370].
- La cadencia de sellado (0,897 sellos por día hábil, Wilson [0,76, 0,96])
  mueve la fecha de los 9 pp entre jul-2027 y sep-2027 por sí sola, y el
  calendario usa días hábiles genéricos, no feriados de bolsa: ±2 meses más.
- Supone días intercambiables (AC1 ≈ 0). El Frente D mide ese supuesto.
