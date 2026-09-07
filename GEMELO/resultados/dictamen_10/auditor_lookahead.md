# AUDITORÍA DE FUGA, corrida 10

Alcance revisado: todo lo nuevo en `git diff origin/main..main` (commits `e368dad`,
`062287f`, `8dd0e0d`), con foco en el riel de dinero: `dinero/senal_larga.py`,
`dinero/senal_larga_reporte.py`, `dinero/cuenta_papel.py`, `dinero/contabilidad.py`,
`dinero/precios.py`, `dinero/derivacion.py`, `dinero/decision.py`, `dinero/mapa.py`,
`dinero/universo_dinero.py`, `dinero/reglas.json`,
`dinero/datos/cierres_congelados.csv` + `.meta.json`, y los tres endpoints nuevos de
`api/main.py`.

Fecha de la auditoría: 7-sep-2026. Auditor: `auditor-lookahead`.

## Veredicto

**Hay fuga.** No es una sospecha: son cuatro mecanismos demostrados ejecutando
código, más un quinto latente. Los cuatro viven en la **cuenta en papel**
(`cuenta_papel.py`, `contabilidad.py`, `derivacion.py`), no en la señal larga.

La separación importa y va dicha antes que nada:

* **`dinero/senal_larga.py` pasa la prueba maestra**, incluso en cortes que la
  suite no prueba. Diferencia máxima 0.000e+00. La climatología es causal, el
  horizonte cierra dentro del archivo, la purga y el embargo están donde el
  reporte dice, y el artefacto publicado reproduce exacto. Lo que ese archivo
  afirma sobre fuga temporal, lo pude verificar.
* **`dinero/cuenta_papel.py` + `dinero/contabilidad.py` NO pasan.** El universo
  operable de una ventana de tres años se elige con el cierre del último día de
  esa misma ventana, y la señal "sin información" se sortea de la distribución
  de retornos futuros de esa misma ventana. La cifra titular de esa página (la
  comisión como fracción del capital) **se mueve al quitar la fuga**: el juego
  `medio` pasa de 27 % a 57 % a 5 pb.

Bajo la regla R3 de `GEMELO/DISEÑO.md`, cualquier fuga descalifica sin excepción.
R3 está escrita para el retador del riel de medición, no para este riel, así que
no la invoco como descalificación formal. Sí digo lo que corresponde: **ninguna
cifra de `dinero/resultados/cuenta_papel.md` ni de `cuenta_papel.json` puede
citarse mientras F1 a F4 sigan en pie**, y eso incluye lo que hoy sirve
`GET /api/dinero/cuenta` y `GET /api/rieles`.

Exigencias: **10**, numeradas al final.

## Qué probé ejecutando y qué sólo leí

**Ejecutado** (comandos y salidas literales más abajo): `python tests/test_motor.py`;
`python -m pytest tests/ -q`; nueve sondas propias escritas para esta auditoría
(truncar y comparar sobre `dinero/`, verificación del congelado contra el
calendario XNYS real, reproducción del artefacto publicado, cuantificación de
materialidad de cada fuga).

**Sólo leído, no ejecutado**: `frontend/` (Vite/React), `scripts/guarda_red.sh`,
`GEMELO/preregistro/senal_larga_v1.md`, `dinero/preregistro_dinero.md`,
`GEMELO/resultados/bitacora_10.md`, `VISION.md`, `DECISIONES.md`. La capa visual
no computa cifras y por eso no entra por la vía de la prueba de propiedad; su
riesgo es de rotulado, no de fuga.

Punto de partida obligado, cumplido: `grep -rn "ErrorLookAhead" .` devuelve
`backtest/causalidad.py`, `backtest/datos.py` y `tests/test_backtest.py`.
**Ninguna aparición en `dinero/`.** `validar_sin_futuro` tampoco. La guarda dura
del proyecto no está cableada al riel nuevo, y eso es la exigencia E6.

# FUGAS DEMOSTRADAS

## F1. El universo operable de tres años se elige con el cierre del último día

**Dónde:** `dinero/cuenta_papel.py:55-58`.

```python
mapa = U.construir_mapa(precios.cargar_congelado(), cfg)
operables = [f.candidato.ticker for f in mapa
             if f.verificado and f.alcanza_con_techo]
```

**Mecanismo exacto:** `construir_mapa` llama a `precios.ultimo_cierre`
(`dinero/precios.py:110-117`), que devuelve el último cierre no nulo del
DataFrame **entero**, o sea el 2026-09-04. Con ese precio decide
`alcanza_con_techo` (¿entra una acción en 500 USD?), y esa bandera define el
universo con el que se simula desde el **2023-09-05**. La membresía de tres
años la fija el último renglón del archivo.

Es exactamente el defecto F1 que la auditoría anterior encontró en
`senal_larga.py` y que allí se corrigió (errata E1 del pre-registro, documentada
en `dinero/senal_larga.py:23-33`). **Quedó sin corregir en la cuenta en papel.**
El mismo repositorio tiene el test que lo caza
(`tests/test_senal_larga.py::test_el_filtro_de_precio_excluye_por_haber_subido`)
y no se aplicó a este camino.

**Cómo reproducirlo:**

```python
from dinero import precios, universo_dinero as U
cfg = U.reglas(); c = precios.cargar_congelado()
op = lambda x: [f.candidato.ticker for f in U.construir_mapa(x, cfg)
                if f.verificado and f.alcanza_con_techo]
print(len(op(c)), len(op(c.loc[:"2023-09-05"])))
```

**Medido:**

| corte del archivo | operables | entran y luego salen | faltan y al final están |
|---|---:|---|---|
| completo (2026-09-04) | 29 | | |
| 2023-09-05 (inicio de la simulación) | 33 | META, MSFT, MU, SMH, SOXX | ARM |
| 2024-09-04 | 33 | MSFT, MU, SMH, SOXX | |
| 2025-09-04 | 32 | MU, SMH, SNDK, SOXX | SNPS |

**Dirección del sesgo, medida sobre la ventana simulada 2023-09-05 a 2026-09-04:**
retorno total mediano de los excluidos +210,8 % contra +166,1 % de los incluidos.
El filtro es sobre el NIVEL de precio del final, así que expulsa mecánicamente a
los que subieron: MU (+1362 %) y SNDK (+4733 %) quedan fuera de un universo que
se usa para simular su propio período. Nótese que **SMH queda excluido del
universo operable de la estrategia mientras la línea base sí lo compra**: la
estrategia no puede comprar su propia vara.

**Materialidad, medida:** re-corrí la cuenta con el universo elegido al inicio de
la ventana (más F2 corregida, ver abajo), a 5 pb:

| escenario | juego | órdenes | comisiones USD | % del capital | final USD | resultado |
|---|---|---:|---:|---:|---:|---:|
| publicado | conservador | 227 | 125,87 | 25 % | 1291,78 | +158,4 % |
| publicado | medio | 220 | 133,78 | 27 % | 1769,07 | +253,8 % |
| publicado | agresivo | 357 | 214,87 | 43 % | 669,45 | +33,9 % |
| sin fuga | conservador | 222 | 127,10 | 25 % | 985,13 | +97,0 % |
| sin fuga | medio | **422** | **284,54** | **57 %** | 956,75 | +91,3 % |
| sin fuga | agresivo | 380 | 218,35 | 44 % | 652,07 | +30,4 % |

El rango publicado como "**14 % a 43 %**" del capital en comisiones no sobrevive.
El signo de la conclusión sí sobrevive (la comisión se come el capital, y de
hecho se lo come más), pero **el número publicado no es el número**.

## F2. La señal "sin información" se sortea de la distribución de retornos futuros de la propia ventana simulada

**Dónde:** `dinero/contabilidad.py:181-206`, llamada desde
`dinero/cuenta_papel.py:59-61` con `cierres` ya recortado a la ventana simulada.

```python
s = cierres[t].dropna()
r = ((s.shift(-horizonte) / s - 1.0).dropna() * 100.0).to_numpy()
dist[t] = r ...
sigma[t] = float(np.std(dist[t], ddof=1)) ...
ancho = 1.2816 * sigma[t]
```

**Mecanismo exacto:** `shift(-20)` es explícitamente el retorno a 20 días
**hacia adelante**, calculado sobre `v = cierres.loc["2023-09-05":"2026-09-04"]`,
que es la ventana entera de la simulación. La señal del día `d` se sortea de esa
distribución, y su banda es `±1.2816·σ` con la σ de esa misma distribución. La
señal no correlaciona con el futuro fila a fila (el sorteo es independiente, y
por eso el reporte tiene razón cuando dice que no hay habilidad), pero **su
escala y su forma vienen del futuro de cada día**, y de la escala dependen las
dos compuertas que gobiernan cuántas órdenes se emiten:

* `magnitud_pp >= umbral_senal_pp` (3,49 pp en el conservador), y
* `exigir_intervalo_que_no_cruce_cero`, que es `|m| >= 1.2816·σ`.

**Cómo reproducirlo:**

```python
from dinero import precios, contabilidad as C, cuenta_papel as CP
v = CP._ventana(precios.cargar_congelado())
tk = ["NVDA","AMD","INTC"]
a = C.senales_sin_informacion(v, tk, 20, C.SEMILLA_SENAL_SIN_INFORMACION)
b = C.senales_sin_informacion(v.loc[:"2024-09-04"], tk, 20, C.SEMILLA_SENAL_SIN_INFORMACION)
```

**Medido:** sobre 252 días comunes y 3 tickers, **755 de 756 señales cambian de
valor** al borrar los datos posteriores al corte. Diferencia máxima 121,10 pp.

| ticker | σ con la ventana entera | σ truncada | P(sorteo > 3,49 pp) entera | truncada |
|---|---:|---:|---:|---:|
| NVDA | 12,028 pp | 14,807 pp | 0,477 | 0,586 |
| AMD | 18,705 pp | 12,889 pp | 0,481 | 0,547 |
| INTC | 21,588 pp | 15,167 pp | 0,447 | 0,310 |

Para INTC la probabilidad de que un sorteo dispare una orden cambia de 0,310 a
0,447 según cuánto futuro se le dé al generador. La frase del reporte "sorteada
de la distribución histórica de retornos a 20 días hábiles" es literalmente
cierta y a la vez engañosa: esa "historia" incluye los tres años que se están
midiendo.

El reporte se defiende diciendo que la respuesta verdadera es cero en las 24
comparaciones. Para el **signo** eso sigue siendo válido. Para el **conteo de
órdenes**, que es el hallazgo que la propia página declara como "lo único que se
sostiene solo", no lo es: ese conteo está calibrado con el futuro.

## F3. El interruptor de pérdida sale de una sigma calculada con futuro y sobre la propia ventana simulada

**Dónde:** `dinero/derivacion.py:70-79` (`sigma_60d_pct`), consumido por
`dinero/reglas.json` como `apagado_por_perdida_pct` (15,6 / 23,4 / 31,2 %) y
aplicado en `dinero/decision.py:170-177`.

```python
serie = cierres[ticker].dropna()
ret = (serie.shift(-horizonte) / serie - 1.0).dropna()
```

**Mecanismo exacto:** dos cosas a la vez. Primero, `shift(-60)` es futuro por
construcción. Segundo, y es lo que lo vuelve fuga y no sólo una convención:
la sigma se mide sobre `dinero/datos/cierres_congelados.csv` **entero**
(2018-09-05 a 2026-09-04), que **contiene la ventana simulada** (2023-09-05 a
2026-09-04). El parámetro que decide cuándo se apaga el riel durante 2023 a 2026
se calibró con lo que pasó en 2023 a 2026.

**Cómo reproducirlo:**

```python
from dinero import derivacion, precios, cuenta_papel as CP
c = precios.cargar_congelado()
derivacion.sigma_60d_pct(c)                    # 15,6177 %  <- el que está en reglas.json
derivacion.sigma_60d_pct(c.loc[:"2023-09-05"]) # 14,1700 %  <- el conocible al empezar
derivacion.sigma_60d_pct(CP._ventana(c))       # 17,1926 %  <- sólo la ventana medida
```

**Materialidad, medida: nula en esta corrida, y lo digo con la misma firmeza con
que digo lo anterior.** Reproduje el bucle de `correr_estrategia` contando la
pérdida contra lo aportado **hasta cada día**: la peor pérdida acumulada es
**0,00 USD**, y el tope más bajo es 78,00 USD. **El interruptor nunca dispara.**
Barrí el parámetro entre 14,2 %, 15,6 % y 17,2 % y las tres corridas dan
idénticas: 227 órdenes, 125,87 USD de comisión, 1291,78 USD final. El defecto
está en el código, no en el resultado de hoy. Se corrige igual, porque el día
que la cuenta pierda plata el interruptor va a decidir con futuro.

## F4. Se decide y se ejecuta en el mismo cierre: retardo de implementación cero

**Dónde:** `dinero/contabilidad.py:221-257` (`correr_estrategia`) y
`dinero/contabilidad.py:162-175` (`linea_base`).

```python
for dia, fila in cierres.iterrows():
    ...
    precios_ref = {t: float(fila[t]) for t in cierres.columns ...}
    dec = D.proponer_ordenes(..., precios_ref, ...)
    for o in dec.ordenes:
        libro.comprar(d, o.ticker, o.acciones, o.precio_ref_usd, ...)
```

**Mecanismo exacto:** `fila` es el cierre del día `d`. Con ese cierre se decide
(`precios_ref`) y contra ese mismo cierre se ejecuta (`o.precio_ref_usd`). Nadie
opera al cierre que acaba de observar. Es el defecto S7 que la auditoría anterior
encontró en `senal_larga.py` y que allí se corrigió subiendo
`RETARDO_IMPLEMENTACION = 1` (`dinero/senal_larga.py:86`). **La cuenta en papel
no tiene esa constante.** Los dos módulos del mismo riel usan convenciones de
ejecución distintas, y la que gobierna la cifra publicada es la laxa.

**Cómo reproducirlo:**

```python
libro = C.correr_estrategia(v, sen, cfg, "conservador", aportes, 5.0, 500.0)
m0 = libro.movimientos[0]           # 2023-09-05 AVGO compra 1 @ 84,1691
v2 = v.copy(); v2.loc["2023-09-05", "AVGO"] *= 1.5
C.correr_estrategia(v2, sen, cfg, "conservador", aportes, 5.0, 500.0).movimientos[0]
```

**Medido:** el primer movimiento publicado es 2023-09-05, compra de 1 AVGO a
84,1691, contra un cierre de ese mismo día de 84,127 (el del día siguiente es
84,1367). Perturbar en +50 % el cierre del 2023-09-05 cambia la primera orden
**de ese mismo día**: pasa de 1 acción de AVGO a 2 de VRT. La orden del día `d`
depende del precio del día `d`.

Atenuante honesto: la línea base hace lo mismo, así que la **comparación** entre
estrategia y vara es simétrica y las cifras relativas no se inflan por esto. La
fuga es sobre la ejecutabilidad absoluta, y sobre la coherencia interna del riel.

## F5. La membresía de los eslabones se decide con datos posteriores a las filas de ajuste (mecanismo demostrado, efecto nulo en este archivo)

**Dónde:** `dinero/senal_larga.py:113-140`, línea 127: `ajuste = cierres.loc[:hasta]`
con `hasta = AJUSTE_HASTA = "2023-09-04"`.

**Mecanismo exacto:** la cobertura se mide sobre **todo** el período de ajuste.
Para una fila de emisión de 2019, la composición de su eslabón se decidió con
datos de hasta 2023-09-04, que es su futuro. Para el período de PRUEBA la
membresía es estrictamente causal (se fija antes de que la prueba empiece) y por
eso la contaminación queda confinada al ajuste; pero un ajuste contaminado
produce coeficientes que después se aplican fuera de muestra.

La suite no lo ve porque `tests/test_senal_larga.py:43` fija
`CORTES = ("2023-09-04", "2024-12-31", "2025-12-31")`: **los tres cortes están en
o después de `AJUSTE_HASTA`**, y para esos cortes `cierres.loc[:"2023-09-04"]` es
el mismo objeto con y sin truncar. El test no puede fallar por esta vía.

**Cómo reproducirlo:** inyectar ausencia de cotización **posterior** a la fila
que se mira, hasta bajar del 98 % de cobertura:

```python
c2 = c.copy()
c2.loc[(c2.index >= "2022-01-01") & (c2.index <= "2023-09-04"), "TSEM"] = np.nan
SL.miembros_por_eslabon(c2)["materias_primas"]     # ['UMC','GSM'], sin TSEM
p1 = SL.construir_paneles(c, 20)["L1"]; p2 = SL.construir_paneles(c2, 20)["L1"]
```

**Medido:** 313 filas de 2019 cambian de valor, diferencia máxima 0,141758 en `x`.
Ejemplo: `(2019-05-20, materias_primas>materiales_obleas)` pasa de
`x = -0,09209253` a `x = -0,09929258`. Un dato de 2022 mueve una feature de 2019.

**Efecto sobre el archivo real: exactamente cero.** Corrí la prueba maestra con
cortes **dentro** del período de ajuste (2019-12-31, 2020-12-31, 2021-12-31,
2022-12-30), los seis paneles y los dos horizontes: censo idéntico y
`maxdif = 0.000e+00` en las 24 combinaciones. La membresía tampoco cambia
truncando en 2019-06-28, 2020-12-31, 2021-12-31, 2022-12-30, 2023-06-30 ni
2023-09-04. La razón es que los tickers que entran no tienen huecos y los que
faltan (GFS 793 NaN, ARM 1264, SNDK 1619) faltan por no existir todavía, no por
cobertura marginal. Es suerte del dato, no propiedad del código.

# SOSPECHAS NO DEMOSTRADAS

## S1. La vara que decide el único resultado positivo se eligió después de ver el resultado, y no entra al registro de intentos

`dinero/senal_larga_reporte.py:210-236` rotula la climatología causal como
"**AGREGADA DESPUÉS DE VER EL RESULTADO**", y eso está bien hecho: se declara, y
se declara que endurece la prueba en vez de ablandarla. Pero el único positivo
que la página deja en pie (L2 a 60 días, ganancia de MAE +0,2293 pp, IC
[+0,0543, +0,4238]) **se define contra esa vara post hoc**, y
`dinero/registro_intentos.py:44` fija `N_INTENTOS_RIEL_LARGO = 3`, que cuenta las
tres especificaciones y **no cuenta la vara**. La propia página declara 24
contrastes y mide, en el bloque 4, que un diseño así produce un IC que excluye el
cero el 21 % de las veces sin información.

Por qué es sospecha y no fuga: no es fuga temporal, es fuga de selección del
analista. Ninguna prueba de este repositorio la detecta.

Qué la resolvería: (a) subir el registro de intentos para incluir cada vara, no
sólo cada especificación, y recomputar cualquier DSR que dependa de él;
(b) aplicar a L2 h=60 la ablación tipo R2 que `dinero/preregistro_dinero.md` §2.5
ya exige y que esta corrida declara no haber hecho.

## S2. El congelado no tiene semántica de disponibilidad, y la guarda dura del proyecto no está cableada al riel

`dinero/datos/cierres_congelados.csv` es una matriz fecha x ticker y nada más.
No hay hora de cierre, no hay `available_at`, no hay huso. `GEMELO/datos.py` sí
sella esas dos cosas como dato y tiene `verificar_conocibles()` como guarda dura;
`backtest/datos.py` tiene `ErrorLookAhead` y `validar_sin_futuro`. **`dinero/` no
importa ninguna de las tres.** El supuesto implícito es que el cierre del día D
es conocible el día D, y para 36 instrumentos todos listados en EE.UU. ese
supuesto es defendible (mismo cierre, 20:00 UTC), pero **nadie lo escribió y nada
lo comprueba**.

Dos casos donde el supuesto se pone fino y no está auditado: `SHECY` y `TOELY`
son ADR de mostrador de nombres de Tokio. Su cierre de EE.UU. del día D refleja
una sesión de Tokio que cerró a las 06:00 UTC del día D (hacia atrás, correcto),
pero si el ADR no negoció ese día el cierre publicado es de arrastre.

Qué la resolvería: sellar en el `.meta.json` la hora de cierre en UTC por ticker
y un `available_at` computado, como hace `GEMELO/datos.py`, y llamar a
`validar_sin_futuro` en `construir_paneles` y en `correr_estrategia`.

## S3. La fuente no es point in time, y el sesgo va en dirección optimista

`dinero/precios.py:78-82` lo declara en el propio metadato: los cierres de
yfinance vienen ajustados retroactivamente por splits y dividendos, así que la
serie no es la que se veía ese día. `GEMELO/resultados/ventana_larga.md` ya midió
la contaminación en el riel de medición (198 filas comunes, 91,4 % de
coincidencia, máximo 31,2 pp). Está declarado y no corregido, que es lo correcto
cuando no se puede corregir, pero **cualquier conclusión de este riel lleva ese
caveat escrito**, incluida L2 h=60.

Qué la resolvería: nada disponible hoy. Sólo un archivo point in time, o el
sellado prospectivo.

## S4. Supervivencia: los 36 tickers son los que existen el 6-sep-2026

`dinero/universo_dinero.py:120-249` lista candidatos escritos hoy. Ninguna
deslistada, ninguna adquirida, ninguna quebrada. El reporte lo declara. Es sesgo
de selección con signo optimista y del mismo orden que la mejora medida.

Qué la resolvería: una lista de constituyentes históricos con fecha de alta y
baja, que este repositorio no tiene.

## S5. `VRT` no es `VRT` durante el 17,8 % de la muestra

Declarado en `dinero/senal_larga_reporte.py:379-382`: fue el SPAC GS Acquisition
hasta feb-2020, con sigma diaria 0,59 % contra 3,86 % después. Es un tercio de
`demanda_final`, que es el eslabón objetivo del último par de la cadena. No es
fuga temporal: es fuga de identidad del instrumento, y afecta al ajuste.

Qué la resolvería: recortar `VRT` al período post-fusión y volver a medir, o
sacarlo del eslabón y declararlo.

## S6. Los endpoints nuevos estampan hora fresca sobre artefactos viejos

`api/main.py`, `_meta_simple()` y `_artefacto()`: los tres endpoints leen el JSON
que haya en `dinero/resultados/` y le ponen `meta.generado_en =
datetime.now(timezone.utc)`. Un artefacto de hace un mes sale con hora de hoy.
No hay campo que diga cuándo se generó el artefacto, ni el sha256 del congelado
del que salió. Es la misma zona ciega de sellado que el proyecto ya conoce
(`ts_emision` se estampa antes del cómputo), reaparecida en la capa de lectura.

Qué la resolvería: que `_artefacto` devuelva también el `mtime` y que el envelope
lleve `artefacto_generado_en` y la huella de la fuente. `universo_operable.json`
ya trae `fuente.sha256`; `cuenta_papel.json` y `senal_larga_v1.json` no.

## S7. Fuga por el analista, declarada y no resoluble

Los ocho eslabones, su orden, los siete pares, las tres especificaciones, los dos
horizontes, el umbral, los tres juegos y las dos varas los diseñó alguien que ya
vio 2018 a 2026. **Ninguna prueba de este repositorio lo detecta.** La única
defensa es el sellado en vivo, y este riel tiene **cero filas selladas**. El
reporte lo dice; lo repito acá porque es zona ciega declarada y va en cada
dictamen sobre GEMELO.

# VERIFICADO LIMPIO

Cada punto va con el comando y la salida. Lo que no aparece acá, no lo probé.

## V1. Guarda anti look ahead del motor de producción

```
$ python tests/test_motor.py
  OK  regimen_al(2026-08-08): idéntico con y sin datos futuros
  OK  puntaje_v0_al(2026-08-08): idéntico con y sin datos futuros
  OK  roca_chip_al(2026-08-08): idéntico con y sin datos futuros
  OK  betas_al(2026-08-08): idéntico con y sin datos futuros
  OK  prediccion_apertura_al(2026-08-08): idéntico con y sin datos futuros
  OK  divergencias_al(2026-08-08): idéntico con y sin datos futuros
  [idem para 2026-06-09 y 2026-03-11]
RESULTADO: todas las funciones del motor pasan el test de no-contaminación (sin look-ahead bias).
```

Alcance de esta prueba: sólo `motor.py`. No dice nada de `dinero/`.

## V2. Suite completa

```
$ python -m pytest tests/ -q
748 passed, 2 xfailed, 36 warnings in 327.09s (0:05:27)
```

Verde, sin fallas ni errores. Los 36 warnings son `Pandas4Warning` de
`pd.concat` sobre `DatetimeIndex` y un `RuntimeWarning` de división en
`GEMELO/transversal.py:260`, ninguno relacionado con causalidad.

Alcance: la suite verde **no contradice** F1 a F5, porque ninguna de las cinco
tiene test. `tests/test_dinero.py` tiene 26 tests y **ninguno es de truncación**:
prueba aislamiento, propiedades de la capa de decisión, derivación de parámetros,
integridad del congelado y rotulado. La causalidad de `cuenta_papel.py` y
`contabilidad.py` **no está probada por nadie**.

## V3. Prueba maestra sobre `construir_paneles`, con cortes que la suite no prueba

Corrí la prueba de invariancia con cortes **dentro del período de ajuste**, que es
donde `CORTES` no llega:

```
T=2019-12-31 h=20 L1: completo=2044 trunc=2044 comun=2044 maxdif=0.000e+00
T=2019-12-31 h=60 L3: completo=1484 trunc=1484 comun=1484 maxdif=0.000e+00
T=2020-12-31 h=20 L2: completo=3815 trunc=3815 comun=3815 maxdif=0.000e+00
T=2021-12-31 h=60 L2: completo=5019 trunc=5019 comun=5019 maxdif=0.000e+00
T=2022-12-30 h=20 L3: completo=7336 trunc=7336 comun=7336 maxdif=0.000e+00
[24 combinaciones, todas maxdif=0.000e+00 y censo idéntico]
```

Borrar el futuro no altera ninguna fila anterior al límite exacto, ni el censo.
Alcance: prueba el archivo `sha256 69ca7283…`, no el código en abstracto (ver F5).

## V4. La climatología es causal

La pregunta del encargo, contestada ejecutando: `clima_media` sale de
`np.mean(ya)` con `ya` = etiquetas del **ajuste** (`dinero/senal_larga.py:298`).
Truncando el archivo en 2024-12-31, o sea borrando 20 meses del período de
prueba:

```
L1 h=20: clima_media completo=0.02219949 truncado=0.02219949 | a,b,n_ajuste idénticos -> IGUAL
L2 h=20: clima_media completo=-0.00053671 truncado=-0.00053671 -> IGUAL
L3 h=20: clima_media completo=0.02219949 truncado=0.02219949 -> IGUAL
L1 h=60: clima_media completo=0.07043786 truncado=0.07043786 -> IGUAL
L2 h=60: clima_media completo=-0.00326828 truncado=-0.00326828 -> IGUAL
L3 h=60: clima_media completo=0.07043786 truncado=0.07043786 -> IGUAL
```

Además de `clima_media`, comprobé que el intercepto `a`, la pendiente `b` y
`n_ajuste` son bit a bit idénticos. **No es una climatología de toda la muestra.**
Las betas de L2 también se estiman sólo en ajuste
(`dinero/senal_larga.py:271-276`) y se aplican a la prueba, que es el orden
correcto.

## V5. El horizonte cierra dentro del archivo: no hay observación con horizonte abierto

```
h=20: última emisión en panel 2026-08-06 ; etiqueta cierra 2026-09-04 ; archivo termina 2026-09-04 -> OK
h=60: última emisión en panel 2026-06-09 ; etiqueta cierra 2026-09-04 ; archivo termina 2026-09-04 -> OK
```

`_acumulado_hacia_adelante` deja NaN los últimos `h + retardo` días y
`panel.dropna()` los elimina (`dinero/senal_larga.py:216`). Ninguna fila del
corte final tiene etiqueta truncada ni rellenada. La segunda pregunta del encargo
queda contestada: la etiqueta de `t` usa cierres que en `t` no existían, que es lo
que debe hacer una etiqueta, y el corte no deja horizontes abiertos.

## V6. Purga y embargo presentes, dimensionados y verificados

```
h=20: corte_de_ajuste=2023-07-28  PRUEBA_DESDE=2023-09-05  n_ajuste=8477  prueba 2023-09-05..2026-08-06 (5131 filas)
h=60: corte_de_ajuste=2023-05-31  PRUEBA_DESDE=2023-09-05  n_ajuste=7917  prueba 2023-09-05..2026-06-09 (4851 filas)
```

`corte_de_ajuste` retrocede `h + retardo + embargo` posiciones **del panel**
desde la primera fecha de prueba (`dinero/senal_larga.py:236-248`), y
`tests/test_senal_larga.py:386-389` verifica antes que el panel no se saltee días
de negociación, que es lo que hace equivalente contar en posiciones y contar en
sesiones. Embargo declarado: `EMBARGO_DIAS = 5`, el mismo de `backtest`, más el
horizonte, más el retardo. **Un solo ajuste y una sola evaluación**
(`res["corte_ajuste"].nunique() == 1`, verificado). **Ninguna fila de test es
anterior a una de train**: el ajuste termina 2023-07-28 y la prueba empieza
2023-09-05, con la ventana de etiqueta del ajuste cerrando antes.

## V7. El calendario del congelado es el calendario real de Nueva York

Contra `exchange_calendars.get_calendar("XNYS")`:

```
sesiones XNYS en el rango: 2011 | filas del congelado: 2011
sesiones de NY que FALTAN en el congelado: 0
filas del congelado que NO son sesión de NY: 0
2026-08-28 (la sesión que Yahoo retiró en el incidente) presente: True
saltos > 4 días: 0 | duplicados en índice: 0
2024-07-04, 2024-11-28, 2024-12-25, 2025-01-01, 2025-07-04 en el índice: False (correcto, son feriados)
```

Coincidencia exacta, 2011 de 2011. **El "cierre anterior" es el cierre anterior
real y no uno de dos días atrás rellenado.** El último día del archivo es
2026-09-04 (viernes) y 2026-09-07 es el Labor Day, que XNYS confirma como no
sesión: no falta ninguna sesión al borde.

Los únicos NaN son GFS (793), SNDK (1619) y ARM (1264), y son ausencia real por
no cotizar todavía, no relleno. `correr_estrategia` los excluye correctamente
(`precios_ref` filtra NaN), así que ARM no se opera antes de su salida a bolsa.

## V8. La congelación es real

```
$ sha256sum dinero/datos/cierres_congelados.csv
69ca7283ae18fd37736827e1b19a79d3557e2e8177dbfd05c9685be22502402b
meta sha256: 69ca7283ae18fd37736827e1b19a79d3557e2e8177dbfd05c9685be22502402b
$ git diff --stat HEAD -- dinero/datos/     (vacío: idéntico al commit e368dad)
```

Huella coincide, archivo versionado, árbol de trabajo idéntico al commit.
`cargar_congelado` revienta con `FileNotFoundError` si falta, no descarga
(`dinero/precios.py:91-100`), y hay test que lo fija
(`test_cargar_congelado_no_sale_a_la_red_si_falta_el_archivo`). **La única
función que toca la red es `descargar_cierres`**, y la cuenta en papel no la
llama. Este punto está bien resuelto y es la parte más sólida del riel.

Lo que sí hay que decir: el congelado se hizo el **2026-09-07 01:47 UTC** sobre
datos hasta el 2026-09-04. Es un congelado **retrospectivo**. Protege contra la
fuga de disponibilidad hacia adelante (nadie puede volver a bajar otra cosa y
llamarla igual), no contra el hecho de que los ocho años se miraron de una vez.

## V9. El artefacto publicado reproduce exacto

Recomputé `senal_larga_reporte.correr()` con el código de hoy y comparé celda por
celda contra `dinero/resultados/senal_larga_v1.json`:

```
celdas nuevas y publicadas: L1/20, L1/60, L2/20, L2/60, L3/20, L3/60
resumen publicado: ganan_a_la_climatologia=1 | recomputado: 1
DIFERENCIAS: 0 -> REPRODUCE EXACTO
```

Comparados `mae_modelo_pp`, `filas`, `n_ajuste`, `corte_ajuste` y los tres
bloques (`vara_cero`, `vara_climatologia`, `direccion`) con sus intervalos, a
1e-9. La distinción del mandato entre "emitido antes" y "reproducible después"
queda del lado bueno: es reproducible.

## V10. No hay artefacto de precio rancio empujando el lead lag

La autocorrelación de orden 1 del retorno diario de los ocho eslabones es
**negativa en los ocho**:

```
materias_primas -0.0177 | materiales_obleas -0.0874 | litografia_equipos -0.0963
fabricacion_vanguardia -0.1108 | memoria -0.0235 | ensamblaje_prueba -0.0510
diseno_eda -0.1067 | demanda_final -0.0600
```

Un rho1 positivo habría sido firma de no negociación, y habría abierto la
posibilidad de que un L1 positivo fuera artefacto mecánico. No es el caso. Los
días con cierre idéntico al previo son pocos y en los sospechosos previsibles
(GSM 4,5 %, UMC 4,5 %, VRT 4,4 % que es el período SPAC; SHECY 0,9 % y TOELY
0,3 %, menos de lo que temía para dos ADR de mostrador).

## V11. Aislamiento respecto del camino de sellado

`tests/test_dinero.py::test_dinero_no_importa_el_camino_de_sellado` y
`::test_el_camino_de_sellado_no_importa_dinero` pasan en la corrida de V2. La
descarga está duplicada a propósito (`dinero/precios.py:18-21`), el mismo criterio
de `GEMELO/datos.py`. Nada de `dinero/` puede tumbar el sello de las 18:15.

## V12. La capa de decisión es pura y no lee el reloj

`dinero/decision.py`: el día entra como argumento, no hay red, no hay escritura,
los tipos son `frozen`, el orden de evaluación de candidatos es explícito
(`-magnitud, ticker`), y hay test de determinismo
(`test_propiedad_es_determinista`). La tenencia mínima se cuenta en días hábiles
con `np.busday_count`, no en días corridos. Sobre este archivo no encontré nada.
Nota menor: `np.busday_count` usa lunes a viernes sin feriados de NY, así que
sobreestima levemente los días hábiles transcurridos; con tenencias mínimas de 5,
20 y 60 el efecto es de uno a dos días y sólo puede **adelantar** una venta
permitida. No lo cuento como fuga; lo dejo escrito.

# ZONAS CIEGAS

Lo que **no** es auditable con lo que hay hoy:

1. **Nada de este riel es prospectivo.** Cero filas selladas. Todas las cifras de
   `dinero/` salen de mirar ocho años de una vez, el 6-sep-2026. La fuga por el
   analista (S7) no tiene prueba posible: sólo la desmiente el sellado en vivo.
2. **No hay hora de disponibilidad en ningún dato del riel.** No puedo verificar
   que el cierre del día D fuera conocible el día D; puedo argumentar que sí
   porque los 36 son de EE.UU., y eso es un argumento, no una prueba.
3. **La fuente no es point in time y no hay copia de lo que la fuente decía
   antes.** No puedo distinguir un retorno cambiado por revisión silenciosa de
   uno real, ni reproducir la serie tal como se veía en 2019.
4. **No puedo auditar la liquidez de SHECY y TOELY.** Un cierre demuestra que
   cotiza, no que se pueda ejecutar. Los dos son miembros de eslabones que entran
   a los paneles L1, L2 y L3.
5. **El supuesto de costo no está verificado contra ningún tarifario.** Todo el
   bloque de comisiones descansa en un supuesto declarado. No es fuga temporal,
   pero es la mitad de la cifra titular.
6. **El impacto de mercado no está modelado.** El deslizamiento es lineal por
   lado. A 500 dólares probablemente sobra; no se verificó.
7. **La suite verde no cubre `cuenta_papel.py` ni `contabilidad.py` por
   causalidad.** Un verde de `pytest tests/ -q` hoy no es evidencia de ausencia
   de fuga en el riel de dinero, y no debe leerse así.
8. **No audité la capa visual ejecutándola.** `frontend/src/vistas/RielDinero.tsx`,
   `Operable.tsx` y `Rieles.tsx` sólo los leí.

# EXIGENCIAS

Diez, numeradas. Las cuatro primeras cierran fugas demostradas y son bloqueantes
para citar cualquier cifra de la cuenta en papel.

**E1. Mover la selección del universo operable al inicio de la ventana, o
volverla point in time día a día.** `cuenta_papel.py:55-58` debe recibir la
membresía como argumento explícito, igual que hizo `senal_larga.construir_paneles`
tras la errata E1. Si se elige el criterio "point in time día a día", la
restricción de presupuesto la aplica `decision.py` con el precio del día, que es
donde ya vive. Cierra F1.

**E2. Escribir el test de truncación de la cuenta en papel ANTES de volver a
correrla.** Es el primer entregable, antes que cualquier corrección: `operables`,
`senales_sin_informacion`, `calendario_aportes` y `correr_estrategia` invariantes
a borrar todo dato posterior a `t`, con contraprueba que inyecte una fuga y
demuestre que el test sabe ponerse rojo. Hoy `tests/test_dinero.py` tiene 26 tests
y cero de esta familia.

**E3. Sortear la señal sin información de una distribución construida sólo con
datos anteriores a `DESDE`**, o de una paramétrica declarada por adelantado. Si
se prefiere lo segundo, el parámetro va a `reglas.json` con su regla de
derivación, como todo lo demás. Cierra F2.

**E4. Introducir `RETARDO_IMPLEMENTACION` en `contabilidad.correr_estrategia` y
en `linea_base`, con el mismo valor que `senal_larga.RETARDO_IMPLEMENTACION`.**
Se decide con el cierre de `t`, se ejecuta al cierre de `t+1`, en las dos patas
de la comparación. Cierra F4. Que dos módulos del mismo riel usen convenciones
de ejecución distintas es, en sí, un hallazgo.

**E5. Recalcular `apagado_por_perdida_pct` con datos anteriores al inicio de la
ventana simulada** (14,17 % en vez de 15,62 % con k=1), o declarar explícitamente
en `reglas.json` que el parámetro se calibró sobre la ventana que después se mide.
Cierra F3. Con la salvedad medida de que hoy el interruptor no dispara y el
resultado no cambia: se corrige por el código, no por la cifra.

**E6. Cablear la guarda dura al riel.** `dinero/` no importa `ErrorLookAhead` ni
`validar_sin_futuro`. Debe hacerlo: una llamada en `construir_paneles` y otra en
`correr_estrategia` que revienten si entra una fila posterior a la fecha de
decisión. Y sellar en `cierres_congelados.meta.json` la hora de cierre en UTC por
ticker más un `available_at` computado, como ya hace `GEMELO/datos.py`. Cierra S2.

**E7. Ampliar `CORTES` en `tests/test_senal_larga.py:43` con al menos dos cortes
dentro del período de ajuste** (por ejemplo 2020-12-31 y 2022-12-30), y hacer que
`miembros_por_eslabon` reciba la ventana de cobertura como argumento acotado por
`t` en vez de leerla de la constante `AJUSTE_HASTA`. Cierra F5. Adjunto la
evidencia de que hoy los tres cortes están en o después de `AJUSTE_HASTA` y por
eso el test no puede fallar por esa vía.

**E8. Republicar `dinero/resultados/cuenta_papel.md` y `.json` con las cifras
recomputadas sin F1 y F2, y corregir el rango de comisiones.** El "14 % a 43 %"
que hoy sostiene el hallazgo 1 de esa página no sobrevive: en la re-corrida sin
fuga el juego `medio` gasta el 57 % del capital a 5 pb. El signo de la conclusión
aguanta; el número no. Mientras no se republique, `GET /api/dinero/cuenta` y el
bloque `cuenta_en_papel` de `GET /api/rieles` sirven cifras contaminadas, y
`que_lo_mata` cita el "entre 14 % y 43 %" como si fuera medido limpio.

**E9. Contar la vara climatológica en el registro de intentos.**
`registro_intentos.N_INTENTOS_RIEL_LARGO = 3` cuenta especificaciones y no cuenta
varas, y el único positivo de la corrida está definido contra una vara elegida
después de ver el resultado. Sumarla, y aplicar a L2 h=60 la ablación tipo R2 que
`dinero/preregistro_dinero.md` §2.5 ya exige. Cierra S1.

**E10. Que los endpoints declaren la fecha del artefacto y la huella de su
fuente.** `api/main.py:_meta_simple()` estampa `generado_en = now` sobre un JSON
que puede tener semanas. Agregar `artefacto_generado_en` (del propio JSON o del
mtime) y `fuente_sha256` en los tres. Cierra S6. Es la misma zona ciega de
sellado que el proyecto ya tiene identificada en el camino de producción,
reaparecida en la capa de lectura.

# Lo que este dictamen NO dice

No dice que la señal larga sea buena: dice que su medición no tiene fuga temporal
detectable con las pruebas que corrí, que es otra cosa. El juicio sobre si
+0,2293 pp de MAE con IC [+0,0543, +0,4238] en una de seis celdas, contra una vara
post hoc y con 24 contrastes, significa algo, es del `estadistico-adversario`.

No dice que la cuenta en papel esté mal concebida: el orden (línea base primero,
señal sin información, barrido de costo, publicar los tres juegos sin ranking) es
correcto y poco común. Dice que su implementación mira el futuro en cuatro
lugares y que sus números publicados hay que rehacerlos.

Y no dice que la suite verde sea evidencia: 748 tests pasando no cubren ni una
sola de las cinco fugas de este documento, porque para ninguna existe el test.
Escribir esos tests es E2, y va antes que las correcciones.
