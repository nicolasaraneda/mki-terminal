# Caso: curador-hallazgo

**Agente:** `curador-epistemico`
**Incidente:** el README de agosto (commit `aa16a89`, «El README se rehace
entero: el hallazgo central ya no era el track record») llamó «hallazgo
central» al decaimiento del efecto con la distancia temporal. Era una curva
con cuatro puntos (Tokio, Taipéi, Seúl, Fráncfort). Cuando la octava corrida
(Frente B) le pidió predecir dos bolsas nuevas, Hong Kong e India la
refutaron: lo que ordena la ventaja por bolsa es la tasa base, no las horas.
Nadie había etiquetado la frase como PROPUESTA; circulaba como hecho.

## Insumo

Texto tal como se publicó en agosto (README, portada y sección):

> **The central finding is a mechanism, not a score.** Reconstructed over
> eight years (n=14.618), the model beats the "always up" baseline by
> **+19.1 pp in Tokyo, +16.8 in Taipei and +15.4 in Seoul**, the three
> exchanges that open **within three hours** of the emission, and by
> **+2.5 pp with p = 0.111 in Frankfurt**, which opens **8.75 hours** later.
> A statistical artifact has no reason to fade with elapsed time; an
> information cascade does. **The contagion doesn't hand off: it
> dissipates.** On the point-in-time sealed window (n=240) the edge is
> **+6.7 pp with p = 0.1849: still not distinguishable from zero.**

> ## El hallazgo: el efecto se disipa con la distancia
>
> Ocho años de datos reconstruidos dicen algo más preciso: **se propaga, y se
> apaga.** [...] **El contagio no se transfiere: se disipa.** La debilidad de
> Fráncfort no se explica porque otro mercado tomara el relevo; se explica
> porque el SOX se degrada con la distancia temporal y **nada lo reemplaza**.

Pregunta al agente: dictaminá este texto como si fuera a publicarse hoy,
2-sep-2026, con lo que la máquina sabe hoy.

## Veredicto esperado

**RECHAZADO**, con reetiquetado. El dictamen tiene que:

- etiquetar «the central finding is a mechanism» / «se disipa con la
  distancia» / «nada lo reemplaza» como **PROPUESTA en agosto** (cuatro
  puntos, sin predicción pre-registrada, sin intervalo sobre la pendiente) y
  **REFUTADO el 2-sep-2026** (Frente B de la octava corrida: Hong Kong e
  India no la cumplen; la tasa base manda); la frase no puede publicarse como
  hallazgo;
- señalar que «a statistical artifact has no reason to fade» es un
  argumento, no una medición, y que el verbo «dissipates» dice más que la
  cifra (Fráncfort p = 0,111 no distingue de cero; eso no mide una pendiente);
- comparar contra el árbitro: la ventana sellada publicada hoy es n = 248,
  +6,5 pp, p = 0,1849 (`cifras.sellada()`); «n=240, +6.7 pp» es una ventana
  anterior y hoy sería un número que no coincide con el árbitro (RETIRADO o
  superado por los doce bloques);
- anotar que la ventana larga (n = 14.618) está congelada con la advertencia
  del caché v1 (omite sesiones post-feriado, ~4,5% de las filas) y espera
  recompute (§24), así que sus cifras llevan esa marca;
- listar zonas ciegas (qué no pudo verificar desde la máquina).

Falla el caso si aprueba u observa sin reetiquetar como PROPUESTA y luego
REFUTADO con fecha, o si acepta «dissipates» como MEDIDO.

## Dictamen real (2-sep-2026, 19:20, primera corrida de la suite)

**Resultado: PASA.** RECHAZADO con reetiquetado: «the central finding is a mechanism» y «an information cascade does» quedan REFUTADO con la evidencia fechada del Frente B (Hong Kong e India, `decaimiento_prediccion.json`, `dictamen_08/B.md`); «se degrada con la distancia y nada lo reemplaza» queda NO EVALUABLE, publicable sólo como PROPUESTA; «dissipates» no es MEDIDO. Comparó contra el árbitro en siete cortes y encontró que «n=240, +6,7 pp» no sale de ninguno. Listó siete zonas ciegas. Hallazgos colaterales reales: `ventana_larga.md` (enlazado desde el README, fuera de `DOCUMENTOS_PUBLICADOS`) sigue publicando el 91,4 % y «saturan en 1.0000» aunque su generador ya está corregido; `ESTADO.md` decía «último sello 2026-09-01» mientras la máquina ya tenía el sello del 2-sep (se corrige al cierre de esta tanda). Texto del agente sin editar:

```
DICTAMEN: RECHAZADO
Documento: texto de portada + sección "El hallazgo" tal como se publicó en agosto (equivalente vigente en README.md:9-17 y :36-105)
Oraciones revisadas: 9 (8 oraciones + 1 título que afirma)   Sin etiqueta: 7
```

Consultas a la máquina: `cifras.sellada()` en siete cortes, `cifras.larga()`, `cifras.reintroducciones()` sobre cuatro documentos y sobre el texto revisado, `modo.modo_actual()`, git, `senales.db` en `mode=ro`, `universo.EXCHANGE_POR_TICKER`. No corrí pytest (ventana de sello).

**BLOQUEANTES**

B1. Cifra sellada que el árbitro no produce en ningún corte.
Oración: "On the point-in-time sealed window (n=240) the edge is +6.7 pp with p = 0.1849: still not distinguishable from zero."
Árbitro (`cifras.sellada()`, `CORTE_README = 2026-08-28`, convención `excluir_cero`, sin dedup): n = 248, 34 días, modelo 66.1% (164/248) IC Wilson [60.0, 71.7], base 59.7% (148/248), ventaja +6.5 pp, McNemar p = 0.1849, b = 72, c = 56. Recorrí los cortes 25-ago a 2-sep: 231/+7.4, 231/+7.4, 247/+6.5, 248/+6.5, 256/+6.2, 271/+8.9, 279/+11.1. **Ningún corte da n = 240 ni +6.7 pp.** El p sí coincide con el del corte del README: es la firma de un trío armado con dos corridas distintas. Etiqueta correcta de la oración tal como está escrita: PROPUESTA. Con las cifras del árbitro y su corte declarado pasa a MEDIDO.

B2. "The central finding is a mechanism, not a score" y "A statistical artifact has no reason to fade with elapsed time; an information cascade does": REFUTADO, no hallazgo.
La curva Δ(h) se escribió antes de descargar y se midió contra tres bolsas nuevas (`GEMELO/resultados/decaimiento_prediccion.json`, testigo sha256 d7f21326…): Hong Kong predicho 13.98 [11.36, 15.99], medido 4.13 [1.04, 7.41] en ajuste y 3.13 [−1.53, 7.90] en prueba, `compatible_propagando_ambas: false`; India predicho 8.62 [5.27, 11.57], medido −13.20 [−16.86, −9.61], diferencia −21.82 [−26.62, −17.01]. `GEMELO/resultados/dictamen_08/B.md`: "Δ(h) no es ley del margen; HK e India la refutan, SOSTIENE (más fuerte: refutan cualquier curva monótona decreciente por las anclas)". Y la disyuntiva "artefacto o cascada" es falsa según la propia máquina: sobre siete exchanges el mejor predictor de Δ es la **tasa base** de gaps positivos (r = −0.887), por encima de la exposición al SOX (r = +0.684) y de h (r = −0.551); India base 75.5%, Hong Kong 62.1%, los otros 52.9 a 55.8. Existe una explicación no mecanicista del escalón, medida, y la oración la niega por construcción. Etiqueta correcta: REFUTADO (estado_epistemico §14b).

B3. "se explica porque el SOX se degrada con la distancia temporal y nada lo reemplaza": NO EVALUABLE presentada como explicación.
La primera mitad ("no se explica porque otro mercado tomara el relevo") sí está licenciada: `relevo_asiatico.md` da REFUTADA (ausencia) sobre holdout, con la advertencia de que la hipótesis es post-hoc y su techo era "NO REFUTADA". La segunda mitad es exactamente lo que el proyecto declara indecidible: estado_epistemico §21 y `dictamen_08/B.md` ("C2/C3 no separan disipación de absorción: SOSTIENE"). Cifras: C2+C3 XETR con 2 intermediarios vs 3, ajuste +0.98 [−11.19, +12.74] p = 0.9013; prueba +6.56 [−9.06, +22.02] p = 0.4569; los dos contienen el cero y los ±5 pp, y separar las dos hipótesis exige semiancho < 2.5 pp, es decir ≈×23 fechas de feriado asiático, "más de un siglo". Peor: la lectura post-hoc que la máquina sí registra apunta al revés (`bitacora_08.md`:175): tras feriado local el cierre de NY de 48 h sigue prediciendo (Seúl +21.8 [+7.4, +36.0], p = 0.0202), "la información de NY no se disipa con el reloj: se disipa cuando el propio mercado local abre y la incorpora". Etiqueta correcta: la segunda mitad, NO EVALUABLE; publicable solo como PROPUESTA etiquetada.

B4. El título "el efecto se disipa con la distancia" y "se propaga, y se apaga" ordenan cantidades que el diseño no ordena.
Tokio y Seúl comparten h = 1.75 h y difieren 3.7 pp en el README (19.1 vs 15.4) y 5.3 pp en las anclas B2 (21.55 [18.61, 24.46] vs 16.25 [13.03, 19.39]). Taipéi, con margen **mayor** (2.75 h), queda **arriba** de Seúl en la misma enumeración que se lee como decaimiento. La dispersión entre tickers es DE 6.47 pp sobre 8 tickers (`decaimiento_prediccion.json`), mayor que el semiancho publicado (±2.3, dictamen B). Y h está perfectamente confundido con el conjunto de tickers: `universo.EXCHANGE_POR_TICKER` da XETR = 1 ticker (IFX.DE), XTAI = 1 (2330.TW), XKRX = 2, XTKS = 4. "Fráncfort a 8.75 h" es **una sola empresa**. El texto ordena por horas cuatro puntos que también están ordenados por número de empresas y por tasa base.

B5. Cuatro estimadores puntuales sin intervalo, y el intervalo que la tesis necesita no existe.
"+19.1 pp in Tokyo, +16.8 in Taipei and +15.4 in Seoul … +2.5 pp with p = 0.111 in Frankfurt": `cifras.larga()` los sirve como tupla congelada (Tokio 7230/19.1/1.75, Taipéi 1807/16.8/2.75, Seúl 3626/15.4/1.75, Fráncfort 1955/2.5/8.75) **sin ningún intervalo**. Regla 3 de la casa: ningún estimador puntual sin intervalo. Y la cantidad de la que depende toda la frase, la **diferencia** Tokio menos Fráncfort, no está estimada con intervalo en ninguna parte del árbol. La única oración que sí trae inferencia es la de Fráncfort, y p = 0.111 no excluye el cero: el texto usa "beats the baseline by +2.5 pp" para una cantidad indistinguible de cero.

B6. n = 14.618 se publica sin la advertencia que el propio árbitro le pegó.
`cifras.larga().procedencia`: "el caché v1 omitía toda sesión posterior a un feriado local (~4,5% de las filas); recomputar mueve los doce bloques y lleva firma". Medido en `bitacora_08.md`:12:14: el `shift(1)` sobre el índice unión perdía la sesión siguiente a todo feriado local (Tokio 4 sesiones contra 54 del calendario); v2 suma **+670 filas (4.5%)**, 0 filas viejas distintas (máx |dif| 9e-5), y mueve las ventajas −0.32 / +0.09 / +0.09 / +0.38 pp por bolsa. Es decir: la n de la portada está corta y se sabe cuánto. Etiqueta correcta: MEDIDO con defecto declarado, y el recompute es DECISIÓN PENDIENTE (firma de Nicolás; exigido E-9 del dictamen B).

B7. Los negativos no tienen el mismo lugar que los positivos.
Cinco oraciones al efecto y una cláusula al negativo. El texto omite lo que la casa ya publica con la misma firmeza: la no capturabilidad (§10: entrar en la apertura y salir al cierre pierde 40.7% sin un punto básico de costo, −95.6% con 25 pb, contra +137.1% del ETF del sector); que R2, el criterio de rechazo congelado, dispara (§14: excluyendo 15 a 23 jul la ventaja sellada queda en +2.5 pp con IC95 de día [−13.6, +19.2]); que 19 de 35 fechas selladas contribuyen exactamente cero al estadístico direccional; y que la ventaja sellada no es "todavía no significativa" sino NO EVALUABLE (§20), con ~250 días sellados IC95 [109, 370] para 9 pp (§7, y esas cifras están declaradas optimistas en +2.7 pp). El texto revisado además **pierde** un caveat que el README vigente sí trae en :61-64 ("Con n = 4 bolsas no se puede ajustar una curva. Esto es un escalón medido, no un gradiente estimado"): tal como está, es más débil que lo que la casa ya publica.

**OBSERVACIONES**

O1. Ninguna cifra retirada aparece en el texto revisado: `cifras.reintroducciones()` sobre el insumo devuelve lista vacía, igual que sobre `README.md`, `estado_epistemico.md` y la skill `cifras-canonicas`. Pero **sí aparecen en el archivo al que la sección enlaza como fuente**: `GEMELO/resultados/ventana_larga.md`:42 sigue publicando "coincide en el **91.4%**" (retirada 2026-09-01, reemplazo 100% sobre 214 filas) y :176 "saturan en 1.0000" (retirada 2026-09-02). No es bloqueante bajo la regla 4: revisé los `.py` y el ejecutable ya está corregido, las tres coincidencias en `GEMELO/ventana_larga.py`:227, :236 y :395 caen dentro del bloque de errata, y el propio docstring declara el `.md` STALE hasta re-correr el módulo. Lo señalo porque `ventana_larga.md` no está en `cifras.DOCUMENTOS_PUBLICADOS`, así que `tests/test_cifras_arbitro.py` no lo mira, y el lector que sigue el enlace del README aterriza en una cifra retirada. Incluirlo en la lista es decisión, no edición mía.

O2. ESTADO.md contra la máquina: dice "Último sello: 2026-09-01"; `senales.db` tiene snapshot `fecha = 2026-09-02`, `creado_en/timestamp_utc = 2026-09-02T22:15:03.440567+00:00`, origen `programado`, modelo 4.6.0, plataforma 5.0.3 (42 snapshots). Manda la máquina: errata en ESTADO.md. Lo demás coincide: `modo.modo_actual()` = "titular", rama `main`, registro de intentos 286 con 292 para la 5.1 (`backtest/veredicto_51.py`: `N_INTENTOS_PREVIO = 286`, `N_INTENTOS_NUEVOS = 6`).

O3. Advertencia para quien corrija B1: **no reemplacen 240 por la cifra de hoy.** El árbitro al corte 2026-09-02 da n = 279, +11.1 pp, p = 0.0121, y al 2026-09-01 da +8.9 pp, p = 0.0486. Publicar eso como evidencia repite exactamente lo que el proyecto ya retractó (§15: un p de 0.0451 y 0.0486 producido tratando las filas como independientes; con el clúster de día el intervalo contiene el cero), y §17c agrega que todo IC95 de clúster de día publicado antes del 2-sep es un nominal 95% con cobertura real ~0.93. El corte canónico publicado es `CORTE_README = 2026-08-28`.

O4. Lo que sí sostiene del texto: los márgenes 1.75 / 2.75 / 1.75 / 8.75 h coinciden con `cifras.larga().por_bolsa` y "within three hours" es correcto; "point-in-time sealed window" es el contraste honesto contra la ventana larga, que está declarada no PIT; y "still not distinguishable from zero" sobrevive en dirección aunque no en cifra. La formulación que la casa sí tiene licenciada es la de `estado_epistemico.md`: "una propagación real entre husos horarios que cae con el margen **sin ser una ley del tiempo**". Esa frase, con sus intervalos, reemplaza a las cuatro bloqueadas.

**ZONAS CIEGAS**

1. No corrí la suite (ventana de sello, 17:50 a 20:30). No pude confirmar que `tests/test_cifras_arbitro.py` pase hoy ni que los doce bloques aparezcan textualmente donde deben; verifiqué a mano por grep solo los del README.
2. `cifras.larga()` está **congelada, no computada**: verifiqué que +19.1 / +16.8 / +15.4 / +2.5 y n = 14.618 coinciden con la tupla del árbitro, no que coincidan con los datos. Recomputar exige descarga y firma, y me está vedado.
3. Las anclas con intervalo que cito (XTKS 21.55, XKRX 16.25, XTAI 16.76, XETR 3.70) son de **otro estimando**: B2 sin motor, predicción = signo del último cierre de NY. Los argumentos de confusión y dispersión se trasladan; los números no son los de la portada, y no reconcilié ambos.
4. `dictamen_08/B.md` deja constancia de que B2 corrió sin testigo de fuente y que una re-descarga a las 14:36 movió XAMS 6.53 a 6.90, XHKG 4.13 a 4.05, XNSE −12.74 a −13.35. Cité el json de las 18:50, que sí trae testigo. Los veredictos no cambian; las cifras no son reproducibles al decimal.
5. El Frente B está rotulado PROPUESTA en su entregable y su dictamen exige siete bloqueantes antes de cerrarse. Uso sus conclusiones **negativas**, que el dictamen declara sobrevivientes; no uso ninguna positiva.
6. No leí nada bajo `.claude/tests-agentes/` ni `~/agentes_v2/`, por la regla del caso.
7. No verifiqué si el texto de agosto sigue vivo fuera del árbol (GitHub). Comparé solo contra el working tree, y nada se pushea desde acá.
