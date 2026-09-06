# Dictamen del curador epistémico sobre los textos públicos de la corrida 09

Fecha y hora (reloj, `TZ=America/Santiago date`): 2026-09-06 19:05 -03.
Estado revisado: commit 4feb32e (3-sep-2026 18:08); los cuatro archivos no cambiaron
desde entonces (`git diff --stat 4feb32e HEAD` vacío para los cuatro).

Documentos revisados:
  /home/nicolasaraneda/dev/mki-terminal/README.md
  /home/nicolasaraneda/dev/mki-terminal/ESTADO.md
  /home/nicolasaraneda/dev/mki-terminal/GEMELO/resultados/estado_epistemico.md
  /home/nicolasaraneda/dev/mki-terminal/GEMELO/resultados/bitacora_09.md

**VEREDICTO: RECHAZADO** (siete bloqueantes; ninguno mueve una cifra del árbitro:
todos son prosa que dice más que la cifra, una decisión pendiente dada por aplicada,
una omisión de lo que no se obtuvo, y cifras retiradas que siguen en ejecutables).

DICTAMEN: RECHAZADO
Documento: los cuatro de arriba   Oraciones revisadas: ~251 (66 + 18 + 83 + 84;
conteo automático, tablas y bloques de código excluidos)   Sin etiqueta o con
etiqueta que la cifra no sostiene: 17

## Lo que la máquina dice (contra lo que se contrastó todo)

- `cifras.sellada()` al corte 28-ago, dedup=True: n 238, 34 días, 161/238 = 67,6 %
  [61,5, 73,3] vs 138/238 = 58,0 % [51,6, 64,1], +9,7 pp (9,66), IC de día percentil
  [−7,2, +26,6], t de clúster [−8,1, +27,4], p de permutación de día 0,294, ICC 0,392,
  DEFF 3,55, n efectivo 67, McNemar χ²cc 0,0455 (exacta 0,0451; b 72, c 49), retorno de
  sesión 151/243 = 62,1 % [55,9, 68,0], MAE 2,5204 vs 2,9751 (−15,3 %, SIN intervalo en
  el árbitro), cobertura 92,9 %, ratio 2,19× [1,71, 2,78].
- `cifras.sellada(dedup=False)` (rama derogada): n 248, 164/148, +6,5, p 0,1849, b 72,
  c 56. Diferencia con la publicada: c baja 7, aciertos del modelo bajan 3: las 10 filas
  retiradas son 7 discordantes a favor de la base y 3 concordantes. La frase del README
  :147-150 es MEDIDA y correcta.
- Ganancia de MAE del campeón contra predecir cero, computada con las funciones del
  árbitro (`backtest.linea_base` + `GEMELO.bifurcaciones`) sobre la misma ventana:
  +0,4547 pp por fila; bootstrap de día [−0,05, +1,00]; t de clúster [−0,087, +0,996];
  p de permutación de día 0,101. Bajo R2 (194 filas, 28 días): +0,362 [−0,283, +1,007].
  Coincide con lo que el adversario midió el 3-sep 00:48 (`enmienda_v1bis.md` §6).
- `cifras.larga()`: 14.618, +15,66; por bolsa 19,1 / 16,8 / 15,4 / 2,5 (p 0,111). Sin
  intervalo. Su `procedencia` ADVIERTE: el caché v1 omitía toda sesión posterior a un
  feriado local (~4,5 % de las filas); recomputar lleva firma.
- `modo.py`: TITULAR; `MKI_MODO` ausente del entorno y de `.env`. Rama `main`, 6 commits
  por delante de `origin/main` (nada pusheado). `systemctl --user`: 6 timers mki.
  `.env`: permisos 600 (ctime 2-sep 15:26). `senales.db`: 44 snapshots, último sello
  2026-09-04; hasta el 28-ago 39 snapshots, 37 con 'Alcista · vol alta' y 2 sin etiqueta;
  verificaciones 4.6.0 con `acierto_gap`: 284 al 2-sep, 292 al 3-sep, 300 hoy.
- `backtest/veredicto_51.py:98` N_INTENTOS_PREVIO = 352; N_INTENTOS_51 = 358.
- `pytest --collect-only`: 651 tests. `tests/test_cifras_arbitro.py`: verde.
- `data/noticias.log` 3-sep 22:00 UTC: dedup retroactivo 615,9 s, 20 borrados,
  primera_corrida True (la predicción de ESTADO:10 se cumplió tal cual la medición en copia).
- `GEMELO/resultados/dictamen_09/` no existía en 4feb32e; hoy contiene sólo lo que otro
  proceso escribió el 6-sep. En la corrida 09 no hubo dictamen del guardián ni del curador.
- `cifras.reintroducciones()` sobre los cuatro documentos: limpio. Sobre los `.py`:
  cifras retiradas en cadenas de salida de `GEMELO/bifurcaciones.py` y
  `GEMELO/simulador/potencia_por_metrica.py` (detalle en B7).

## Un punto por documento

**README.md.** Las cifras de la ventana sellada coinciden una a una con el árbitro y
la errata de D1 está bien marcada (:20-21, :143-150). Falla en tres lugares de prosa:
(a) la fila del MAE dice «la magnitud sí aporta» cuando el intervalo de día de esa
ganancia contiene el cero y el árbitro ni siquiera le computa intervalo; (b) la sección
«Lo que la información expandida aporta» concluye «SÍ aporta» apoyada en una columna
de IC que la propia corrida 09 declaró en escala equivocada (errata al pie de
`ventana_larga.md`) y no recomputada; (c) el titular entero sigue siendo «el efecto se
disipa con la distancia» y «la firma de un mecanismo», cuando la predicción fuera de
muestra de esa curva FALLÓ (dictamen B, octava corrida; `estado_epistemico.md` 14b lo
lista como CONTESTADA) y el README no lo menciona en ninguna parte. Es exactamente el
caso que motivó este rol. Además: «Va en 25» intentos (máquina: 352), «299 tests»
(máquina: 651), la ventana larga sin intervalo y sin la advertencia del caché v1.

**ESTADO.md.** Coincide con la máquina en modo, rama, timers, registro de intentos y
cifra D1. Falla en: «D3 aplicada: magnitud primaria» (V1-bis espera firma; V1 sigue
bloqueante, como el propio director corrigió en el mandato del adversario a las 12:44);
no declara que la corrida cerró sin guardián ni curador (el documento de estado vivo
omite que su propia compuerta de cierre no se pasó); «`.env` sigue en 644» (máquina:
600 desde el 2-sep 15:26, antes de la corrida); la frase de potencia sin declarar que
su ancla es el 31-ago (n 246, 35 días, cadena local) y no la ventana publicada.

**estado_epistemico.md.** Es el mejor de los cuatro: casi toda afirmación lleva estatus
y los negativos tienen sección propia. Falla en el punto 8 («La magnitud predicha
aporta», bajo ACOTADA), que contradice a su propia PROPUESTA (iii) tres pantallas más
abajo («nadie mejora a predecir cero de forma distinguible»); en el encabezado de la
novena corrida («con dictamen del adversario») que calla los dos dictámenes que no
hubo; en «cae con el margen» de la frase final (14b lo contestó); y en cuatro cifras
citadas sin su ancla o su fecha (0,30 de potencia y MDE 16,6 sobre n 246 / ruta 1;
«−1,0 pp sobre la publicada» que es la rama derogada, n 204; «276 verificaciones»
que es el censo del 1-sep, no hoy).

**bitacora_09.md.** Declara con claridad, al final (:342-358), que faltan los dos
dictámenes: cumple. Las horas contrastadas con mtimes de `corrida09/` calzan
(tarjetas 00:49, ic_dmae 10:05, ws4 10:08, frase 12:35, juez 12:50) y las dos erratas
de horas están anotadas. Falla en: el hito 01:06 y el 11:22 ofrecen «269 [229, 275] →
27-ago-2027» sin marca inline (la retirada llega 80 líneas después); «El guardián se
sustituye por verificación mecánica propia» asciende un autochequeo a sustituto de un
dictamen (la casa dice en ESTADO:14 que verificar con el mismo mecanismo no es
verificar); y las cifras retiradas en esta corrida (269 [229, 275], 58 [54, 62], el 93 %
de `dictamen_08/E.md`) no entraron en `cifras_retiradas.md`: sólo las cuatro de D1.

## BLOQUEANTES

B1. README.md:155. Oración: «**la magnitud sí aporta: −15.3%**». Cifra del árbitro:
`mae_modelo_pp` 2,5204, `mae_cero_pp` 2,9751, `mae_mejora_pct` −15,3 sin intervalo;
con las funciones del árbitro sobre la misma ventana la ganancia es +0,4547 pp por fila,
t de clúster de día [−0,087, +0,996], p de día 0,101: contiene el cero. Etiqueta
correcta: MEDIDO, no distinguible de cero al nivel de día. El verbo «aporta» está mal.

B2. GEMELO/resultados/estado_epistemico.md:84. Oración: «**La magnitud predicha
aporta:**» bajo «Lo que está ACOTADO». Misma cifra que B1; el mismo documento dice en
:211-213 «nadie mejora a predecir cero de forma distinguible: campeón +0,375 pp
[−0,201, +0,955]». Etiqueta correcta: ACOTADA con el intervalo a la vista y el verbo
invertido («no se distingue de cero al nivel de día»).

B3. README.md:206 y :213-214. Oraciones: «**+1.3 pp, p = 0.0003** · IC del ΔMAE
**excluye cero**» y «**La conclusión correcta es: la información expandida SÍ aporta,
y aporta poco.**». Cifra: la corrida 09 dejó errata al pie de `ventana_larga.md`
(:237-243): la columna «IC 95 %» de esa tabla está en escala de Sharpe, no en pp, y
recomputarla es NO EVALUABLE sin red; el p 0,0003 es de filas, sin clúster de día. En
la ventana sellada, `corrida09/ic_dmae_recomputados.md`:50 da C2 vs C1 +0,2002
[−0,061, +0,432] (79 filas parciales) y el juez D3 da +0,200 [−0,088, +0,488], p 0,17.
Etiqueta correcta: PROPUESTA; el veredicto «excluye cero» es RETIRADO por errata.

B4. README.md:9-10, :14-16, :40, :58-62. Oraciones: «**The central finding is a
mechanism, not a score.**»; «A statistical artifact has no reason to fade with elapsed
time; an information cascade does. **The contagion doesn't hand off — it
dissipates.**»; «## El hallazgo: el efecto se disipa con la distancia»; «**Eso no es
una debilidad del resultado: es la firma de un mecanismo.**». Cifra: `cifras.larga()`
da el escalón por bolsa sin intervalo y advierte la omisión del caché v1; la
predicción fuera de muestra de la curva falló (Hong Kong predicho 14,0 medido 4,1;
India predicho 8,6 medido −12,7; mejor predictor la tasa base, r = −0,89:
`decaimiento_prediccion.json`, `estado_epistemico.md`:130-137, CONTESTADA). El README
no menciona esa refutación en ningún lugar y la mantiene como titular. Etiqueta
correcta: el escalón es MEDIDO (reconstruido, sin IC de día, caché v1 con omisión
conocida); «mecanismo que se disipa con la distancia» es PROPUESTA cuya predicción
fue REFUTADA. Viola además la regla 3: el negativo no tiene el lugar del positivo.

B5. ESTADO.md:22-23. Oración: «**D3 aplicada:** magnitud primaria; enmienda V1-bis v2
escrita». Máquina y actas: `enmienda_v1bis.md` §5 «Lo que espera firma»; `espera_firma`
§30 conflicto sin resolver; bitácora :297-299: el director corrigió ese mismo error en
el mandato del adversario («V1 sigue bloqueante hasta la firma»). Etiqueta correcta:
DECISIÓN PENDIENTE. «Aplicada» y «magnitud primaria» dan por firmado lo que espera firma.

B6. ESTADO.md (ausencia; :49-50) y GEMELO/resultados/estado_epistemico.md:201. Falta la
oración que diga que la corrida cerró sin dictamen del guardián ni del curador y que
estos textos se publicaron sin curaduría. Máquina: `dictamen_09/` vacío en 4feb32e.
La bitácora lo declara (:342-358); el documento de estado vivo y el estado epistémico
público no. ESTADO:49-50 enuncia la regla («Antes de cerrar: guardian-constitucion y
curador-epistemico») sin decir que no se cumplió.

B7. Cifras retiradas en ejecutables que generan documentos citados.
(a) GEMELO/bifurcaciones.py:1339-1345 emite a `bifurcaciones.md` «(1) *Publicada*: sin
la regla de deduplicación, la celda … reproduce la ventana sellada del README (n=248,
66.1% contra 59.7%, +6.5 pp, b=72, c=56, p = 0.1849)» —cifra RETIRADA por D1— y
:2116-2117 imprime «[ancla]
reproduce la ventana sellada del README (n=248, +6.5 pp, p=0.1849)». El comentario del
ANCLA (:105-108) lleva la marca de retiro; las cadenas de salida no, y siguen llamando
«Publicada» y «del README» a la rama derogada. `bifurcaciones.md` es la fuente del
«0 de 192» de `estado_epistemico.md`:58.
(b) GEMELO/simulador/potencia_por_metrica.py:235 emite «(lo que el modelo tendría si su
intervalo no fuera 1,84× ancho)» (ya emitido en `potencia_por_metrica.md`:25) y :14-15
lo declara en el docstring como «README». 1,84× está en `cifras_retiradas.md`:40. Su
JSON alimenta `frase_potencia.py`:67, de donde salen las bandas 0,90 / 0,86 / 0,70 de
ESTADO:27 y `estado_epistemico.md`:209. La σ numérica se computa desde datos (:149); lo
retirado es la prosa hardcodeada, y vuelve a circular en cada corrida.

## OBSERVACIONES

O1. README.md:31 y :401: «tests-299 passing» / «pytest (299 tests)». Máquina: 651
recolectados (649 passed + 2 xfailed al 12:58 del 3-sep). Errata.
O2. README.md:271: «Va en 25». Máquina: `veredicto_51.py:98` 352 (358 con el 5.1). Errata
en una frase cuyo punto es que contar de menos inutiliza el DSR.
O3. ESTADO.md:11: «`.env` sigue en 644». Máquina: 600, ctime 2-sep 15:26 (anterior al
arranque de la corrida). Errata.
O4. ESTADO.md:8: «Último sello: 2026-09-02 (42 snapshots)». Cierto al escribirse; hoy la
máquina dice 2026-09-04 (44). «Se regenera al cierre» y no se regeneró en los cierres
del 3 y 4-sep. Fechar la línea o regenerar.
O5. ESTADO.md:26-29 y estado_epistemico.md:67-75: la potencia 0,30 [0,27, 0,33] y el
≈263 están calibrados sobre el ancla 31-ago (cadena local, n 246, 35 días:
`frase_potencia.md`:7), no sobre la ventana publicada (n 238, 34 días); el MDE 16,6 pp
[11,0, 20,3] es de la ruta 1 (analítica, `horizonte.md`:19-24), no de la ruta 3 que
manda; «~475–510 [209, 709]» mezcla punto de ruta 1 y 3 con intervalo de ruta 1.
Ninguno de los dos documentos declara el ancla ni la ruta.
O6. estado_epistemico.md:128: «y en −1,0 pp sobre la publicada». Es la rama sin
deduplicar (n 204 = 248 − 44; DECISIONES.md:4725-4728). Tras D1 «la publicada» apunta a
otra cifra; no está recomputado bajo la regla firmada.
O7. estado_epistemico.md:30 y :37: «276 verificaciones desde julio» / «276/276». Es el
censo del 1-sep 18:15 (`fuente_canonica.md`:38); `senales.db` da 292 al 3-sep. Fechar.
O8. README.md:157 y :279-280: «1 sola etiqueta en 39 snapshots». Máquina: 37 con
etiqueta, 2 sin etiqueta (NULL).
O9. README.md:164 y estado_epistemico.md:45-49: la ventana larga (+15,66) no lleva
intervalo (regla de la casa: ningún estimador sin intervalo) ni la advertencia del
caché v1 que el propio árbitro adjunta en `larga().procedencia`.
O10. README.md:17 y :134: el «day-cluster 95% CI» es el percentil de día, cuya cobertura
medida es ~0,93 (`estado_epistemico.md`:169-173, 17c); la t de clúster [−8,1, +27,4]
es la PROPUESTA que cubre 0,95. La conclusión no cambia; la etiqueta «95 %» sí.
O11. bitacora_09.md:158-159 y :227: «269 [229, 275] → 27-ago-2027» sin marca inline;
retirado a las 12:20 (:238). Y `cifras_retiradas.md` no recibió las cifras retiradas en
esta corrida: 269 [229, 275], 58 [54, 62], el «93 %» de `dictamen_08/E.md`.
O12. bitacora_09.md:344-345: «El guardián se sustituye por verificación mecánica propia».
Está declarada como propia (bien) pero «se sustituye» le da valor de dictamen.
O13. estado_epistemico.md:250-252: «una propagación real entre husos horarios que cae
con el margen». 14b contestó precisamente «cae con el margen».
O14. README.md:100-102: la tabla del holdout no lleva n (393 filas XETR, 2.548 Asia:
`relevo_asiatico.md`:42-43).
O15. estado_epistemico.md:55 y ESTADO.md:19: n 238 sin «34 días» al lado (la unidad de
replicación que el propio párrafo defiende).
O16. cifras.py:141: `mae_mejora_pct` es el único estimador del árbitro sin intervalo;
`test_todo_estimador_del_arbitro_lleva_intervalo` no lo caza. La corrección va al
ejecutable antes que a la prosa (B1/B2 dependen de esto).
O17. GEMELO/SECUENCIAL/mde_vs_observado.py:57-58: comentario «sobre el que el README
publica +6.5 pp» en presente; falso desde el 3-sep. Comentario, no salida: observación.
O18. ESTADO.md:21: «"+ coherencia" (+14,3) sigue en cola» sin decir «sin intervalo»
(estado_epistemico:82 sí lo dice).
O19. README.md:384-385: «la auditoría adversarial ya hizo dos pasadas»; van nueve corridas.

## EXIGENCIAS (aplicables sin interpretar; los fragmentos de los doce bloques se conservan)

1. cifras.py:141. Falta el intervalo de la ganancia de MAE. Insertar tras la línea de
   `"mae_mejora_pct"` los campos `mae_ganancia_pp`, `mae_ganancia_ic_t_dia` y
   `mae_ganancia_p_dia` computados con `bf._ic_t_cluster` y `bf._p_permutacion_dia`
   sobre los grupos de día de la serie `|gap| − |pred − gap|`
   (con la ventana actual da +0,4547, [−0,087, +0,996], 0,101) y extender el bloque 8 de
   `doce_bloques` para que publique la ganancia con su IC de clúster de día.

2. README.md:155. Sobra «**la magnitud sí aporta: −15.3%**». Fila completa nueva:
   `| **MAE del gap** | **2.52 pp** vs **2.98** de predecir cero | ganancia +0.45 pp por fila, IC95 t de clúster de día [-0.09, +1.00], p de día 0.10: **contiene el cero, no distinguible al nivel de día**; parte de la mejora respecto de la rama retirada es que la regla saca filas con gaps enormes del 29-jul |`

3. GEMELO/resultados/estado_epistemico.md:84-88. Sobra «**La magnitud predicha
   aporta:**». Punto 8 completo nuevo:
   «8. **La magnitud predicha no se distingue de cero al nivel de día:** MAE del gap
   2,52 pp contra 2,98 de predecir cero (n = 238, 34 días; ganancia +0,45 pp por fila,
   IC95 t de clúster de día [−0,09, +1,00], p de día 0,10: contiene el cero). Parte de
   la mejora relativa respecto de la rama retirada (era 2,98 contra 3,33) es que la
   regla saca filas con gaps enormes del 29-jul. Los intervalos del 80% cubren el
   92,9%: son 2,19× [1,71, 2,78] más anchos de lo necesario. *(`cifras.sellada()`;
   verificado por el adversario el 3-sep, `enmienda_v1bis.md` §6.)*»

4. README.md:205-206. Reemplazar las dos filas por:
   `| **WS2b** | 223 filas selladas | +2.8 pp, **p = 0.3613** · ΔMAE C2 vs C1 recomputado por clúster de día: +0.20 pp [-0.06, +0.43] sobre 79 filas parciales (corrida09/ic_dmae_recomputados.md), **incluye cero** |`
   `| **WS3** | 12.628 filas | +1.3 pp, p = 0.0003 **de filas, sin IC de clúster de día**; la columna «IC del ΔMAE» estaba en escala de Sharpe, no en pp (errata 3-sep al pie de ventana_larga.md); recomputarla es NO EVALUABLE sin red |`

5. README.md:208-215. Sobra «**La conclusión correcta es: la información expandida SÍ
   aporta, y aporta poco.**» y el párrafo que lo precede. Texto nuevo para :208-215:
   «El efecto encogió de +2.8 a +1.3 pp al pasar de 223 a 12.628 filas y el p de filas
   bajó a 0.0003. Ese p trata las filas como independientes; con la unidad de día
   (acta §61) el WS3 no está recomputado. **Estatus: PROPUESTA. En la ventana sellada,
   el juez lineal bajo D3 (EXPLORATORIO, 3-sep) da C2 − C1 +0.20 pp [-0.09, +0.49], p de
   día 0.17: los 16 features no traen magnitud detectable distinta de SOX(t, t−1).**
   *"No significativo"* no es *"no hay nada"*; tampoco es *"sí aporta"*.»

6. README.md:9-10. Sobra «**The central finding is a mechanism, not a score.**».
   Poner: «**The central measurement is a step across exchanges, not a score, and not
   (yet) a mechanism.**»

7. README.md:14-16. Sobra «A statistical artifact has no reason to fade with elapsed
   time; an information cascade does. **The contagion doesn't hand off — it
   dissipates.**». Poner: «The obvious reading, an information cascade fading with
   elapsed time, was **pre-registered as a prediction for three new exchanges and
   failed** in two (Hong Kong: predicted +14.0 pp, measured +4.1; India: predicted
   +8.6, measured -12.7); the best predictor of the per-exchange edge is the base rate
   of positive gaps (r = -0.89), not hours elapsed. **The hand-off to Asia was refuted
   too.** The step is measured; the mechanism is a PROPOSAL.»

8. README.md:40. Sobra «## El hallazgo: el efecto se disipa con la distancia». Poner:
   «## Lo medido: un escalón entre bolsas, no una ley de la distancia».

9. README.md:58-62. Sobra el párrafo «**Eso no es una debilidad del resultado: es la
   firma de un mecanismo.** …». Poner:
   «**Lo que ese escalón no es: una ley de la distancia.** La lectura de mecanismo (una
   propagación de información que se apaga con las horas) se pre-registró como
   predicción para tres bolsas nuevas antes de descargarlas y falló en dos: Hong Kong
   (predicho +14,0 pp, medido +4,1) e India (predicho +8,6, medido −12,7). Lo que mejor
   predice la ventaja por bolsa no es el margen horario sino la tasa base de gaps
   positivos (r = −0,89). Estatus: **CONTESTADA** (`decaimiento_prediccion.json`,
   dictamen B de la octava corrida; `estado_epistemico.md` 14b). El escalón queda
   MEDIDO; el mecanismo queda PROPUESTA.»

10. README.md:164 y GEMELO/resultados/estado_epistemico.md:49 (tras «*(`README.md`.)*»).
    Falta: « Sin IC de clúster de día computado; reconstrucción sobre el caché v1, que
    omite toda sesión posterior a un feriado local (~4,5 % de las filas): recomputar
    mueve los doce bloques y lleva firma (`cifras.larga().procedencia`).»

11. ESTADO.md:22-23. Sobra «**D3 aplicada:** magnitud primaria; enmienda V1-bis v2
    escrita — el adversario dictaminó». Poner: «**D3 en curso, DECISIÓN PENDIENTE:** la
    enmienda V1-bis v2 que la instrumenta está escrita y espera firma; hasta la firma V1
    (dirección) sigue bloqueante y la magnitud no es primaria. El adversario dictaminó».

12. ESTADO.md:46-47. Sobra «**Lo más urgente: firmar V1-bis (y resolver cero vs
    climatología) y el parche `:140`.**». Poner (mantiene las 50 líneas): «**La 09 cerró
    sin dictamen del guardián ni del curador (`dictamen_09/` vacío; textos públicos sin
    curaduría). Lo más urgente: esos dos dictámenes, firmar V1-bis (cero vs
    climatología) y el parche `:140`.**»

13. GEMELO/resultados/estado_epistemico.md:201. Sobra «**Novena corrida (3-sep), con
    dictamen del adversario:**». Poner: «**Novena corrida (3-sep), con dictamen del
    adversario y SIN dictamen del guardián ni del curador (agentes caídos por límite de
    API; este documento se publicó sin curaduría):**»

14. GEMELO/bifurcaciones.py. :1340 sobra «(1) *Publicada*: sin la regla de
    deduplicación, la »; poner «(1) *Histórica (publicada hasta el 2-sep-2026; retirada
    por D1, acta §78)*: sin la regla de deduplicación, la ». :1342 sobra «reproduce la
    ventana sellada del README »; poner «reproduce la ventana que el README publicó
    hasta el 2-sep ». :2116 sobra «[ancla]   reproduce la ventana sellada del README »;
    poner «[ancla]   reproduce la ventana RETIRADA (publicada hasta el 2-sep) ». :54
    sobra «reproduce EXACTAMENTE la cifra del README (n=248, +6.5 pp, p=0.1849).»; poner
    «reproducía EXACTAMENTE la cifra que el README publicó hasta el 2-sep (n=248, +6.5
    pp, p=0.1849; retirada por D1).»

15. GEMELO/simulador/potencia_por_metrica.py. :235 sobra el literal «(lo que el modelo
    tendría si su intervalo no fuera 1,84× ancho)»; poner una f-string con el ratio
    computado desde el mismo `sell` o leído de `cifras.sellada()["ratio_ancho"]`; nunca
    un literal. :14-15 sobra «(1,84× más ancho de lo necesario, README)»; poner «(más
    ancho de lo necesario por el ratio que publica el árbitro con su IC,
    `cifras.sellada()['ratio_ancho']`: 2,19× [1,71, 2,78] al 3-sep-2026)».

16. README.md:271. Sobra «Va en 25:». Poner «Va en 352 (`backtest/veredicto_51.py:
    N_INTENTOS_PREVIO`; 358 con los seis del 5.1):».

17. README.md:31 y :401. Sobra «tests-299%20passing» y «pytest (299 tests)». Poner la
    cifra vigente de la suite el día del commit.

18. ESTADO.md:11. Sobra «`.env` sigue en 644.». Poner «`.env` en 600 (máquina; ctime
    2-sep 15:26).»  ESTADO.md:8. Sobra «**Último sello: 2026-09-02** (42 snapshots).».
    Poner «**Último sello al 3-sep mediodía: 2026-09-02** (42 snapshots; el vigente se
    lee de `./mki estado`, no de aquí).»

19. ESTADO.md:26. Falta, tras «Frase de potencia en dos versiones (`espera` §29):», «
    ancla 31-ago, cadena local, n 246, 35 días (no la ventana publicada);». GEMELO/
    resultados/estado_epistemico.md:67. Falta, tras «**El instrumento acumula ~2
    observaciones efectivas por día sellado.**», « Todo lo que sigue está calibrado
    sobre el ancla del 31-ago (cadena local, n = 246, 35 días), no sobre la ventana
    publicada (n = 238, 34 días); el MDE a 73 días es de la ruta 1 (analítica).» Y en
    :71 sobra «~475–510 [209, 709]»; poner «≈510 (MC [467, 580]; ruta 1: 475 [209, 709])».

20. GEMELO/resultados/estado_epistemico.md:128. Sobra «y en −1,0 pp sobre la
    publicada». Poner «y en −1,0 pp sobre la rama sin deduplicar que entonces se
    publicaba (n = 204 tras excluir el bloque; rama retirada por D1; no recomputado bajo
    la regla firmada)».

21. GEMELO/resultados/estado_epistemico.md:30. Sobra «276 verificaciones desde
    julio.». Poner «276 verificaciones desde julio al censo del 1-sep
    (`fuente_canonica.md`); 292 al 3-sep en `senales.db`.»

22. README.md:157 y :279-280. Sobra «1 sola etiqueta en 39 snapshots» y «una sola
    etiqueta en 39 snapshots». Poner «1 sola etiqueta en 37 de 39 snapshots (2 sin
    etiqueta)» en ambos.

23. README.md:134. Falta, tras «binomial exacta 0.0451)», «; percentil de día con
    cobertura medida ~0.93 (`calibracion_instrumento.md` A1), t de clúster
    [-8.1, +27.4]». README.md:17: dejar el fragmento del bloque 2 intacto y añadir la
    cobertura entre paréntesis después del intervalo.

24. GEMELO/resultados/bitacora_09.md:158-159 y :227. Falta, inmediatamente después de
    «→ 27-ago-2027» en ambos hitos, la marca inline de retiro. GEMELO/cifras_retiradas.md:
    añadir las tres filas de las cifras retiradas en esta corrida (el horizonte de 269
    días con su intervalo inválido, los 58 días de magnitud, y el «93 %» de
    `dictamen_08/E.md`).

25. GEMELO/resultados/bitacora_09.md:344-345. Sobra «El guardián se sustituye por
    **verificación mecánica propia, con evidencia**:». Poner «El dictamen del guardián
    NO se obtuvo y nada lo sustituye; queda, sin valor de dictamen y hecha por el mismo
    orquestador que produjo los cambios, esta verificación mecánica:».

26. GEMELO/resultados/estado_epistemico.md:250-252. Sobra «una propagación real entre
    husos horarios que cae con el margen sin ser una ley del tiempo». Poner «un escalón
    real entre bolsas (tres cercanas arriba, la lejana no distinguible de cero) cuya
    lectura como decaimiento con el margen falló fuera de muestra (14b)».

27. README.md:93. Falta, tras «Medido sobre el holdout en cuarentena», « (n = 393 filas
    en Fráncfort, 2.548 en Asia)».

28. GEMELO/resultados/estado_epistemico.md:55 y ESTADO.md:19. Sobra «**+9,7 pp, n =
    238**» y «n 238, +9,7 pp»; poner «**+9,7 pp, n = 238, 34 días**» y «n 238 (34 días),
    +9,7 pp» (el bloque 12 «+9,7 pp, n = 238» se conserva textual).

29. ESTADO.md:21. Sobra «"+ coherencia" (+14,3) sigue en cola.»; poner «"+ coherencia"
    (+14,3, sin intervalo: no publicable) sigue en cola.»

30. GEMELO/SECUENCIAL/mde_vs_observado.py:57-58. Sobra «exacto de 248 filas sobre el
    que el README publica +6.5 pp.»; poner «exacto de 248 filas sobre el que el README
    publicó +6.5 pp hasta el 2-sep-2026 (rama sin deduplicar, retirada por D1).»

## ZONAS CIEGAS

- Cifras de WS3/WS4/WS5 (14.618, +15,66, por bolsa, 0 violaciones en 15.033 pares, 105
  filas, holdout del relevo, +2,8 pp p 0,3613): aceptadas de sus archivos y del `Larga`
  congelado del árbitro; recomputarlas exige descarga y lleva firma. No las verifiqué.
- Ruta 3 de `horizonte.py` (0,30 [0,27, 0,33]; ≈263) y el tipo I de la conjunción
  V1-bis: no relancé el simulador (55 min); contrasté sólo con `frase_potencia.md` y
  `horizonte.md`.
- El «36 celdas reproducidas al 4.º decimal» del juez: el dictamen dice recomputadas por
  fila desde caché + `senales.db`; no corrí el juez ni puedo afirmar que la ruta del
  adversario fuera independiente del código de hipótesis.
- Suite completa: no la corrí entera. `test_cifras_arbitro.py` verde;
  `test_epistemico.py` falla hoy por una cita por número de línea en
  `dictamen_09/guardian_constitucion.md:157`, archivo escrito el 6-sep por otro proceso,
  ajeno al estado de 4feb32e.
- Registro de intentos: 352 verificado contra `veredicto_51.py` y la cadena de
  bitácoras (286 + 66); no existe un libro mayor por máquina de los 66 incrementos.
- Horas de la bitácora: contrasté las de `corrida09/` con mtimes; las de 23:37, 23:47 y
  00:05 no tienen artefacto contra el cual leerse.
- La cifra «0 de 192» de `bifurcaciones.md` corresponde al ancla de regla firmada
  (`bifurcaciones.md`:7 dice 238 filas) pero el informe data del 1-sep y no se regeneró
  tras D1; no lo relancé.
- No escribí este archivo: el mandato del curador prohíbe escribir en el árbol. Lo
  vuelca quien lo pidió.

---

> **Nota de quien lo volcó (6-sep-2026).** El texto es del `curador-epistemico`,
> reproducido sin editar salvo dos podas declaradas: en las exigencias 1, 15, 17 y 24 se
> resumió el fragmento de código o la cifra literal que el dictamen proponía pegar, para
> que este archivo no reintroduzca por sí mismo lo que exige retirar. La versión
> ejecutada de cada una está en el acta y en el diff. El estado de aplicación, en
> `aplicacion_dictamenes.md`.
