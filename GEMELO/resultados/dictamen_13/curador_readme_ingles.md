# Dictamen del `curador-epistemico` — README.md en inglés (corrida 13, 19-sep-2026)

**DICTAMEN INICIAL: RECHAZADO** (no publicable hasta corregir B1 a B4). 100 frases de prosa y 44 filas de tabla revisadas contra README.es.md. Qué se hizo con cada punto:

## Bloqueantes

1. Frase de apertura sólo-inglés «built to be unable to lie to its own author»: absoluto que el expediente desmiente (el WS3 publicó una ventaja inflada en 0,24 pp, cifra retirada y con errata, y una «contaminación por revisión» del 91,4 %, cifra retirada por errata del WS4; la curva de decaimiento circuló como hecho en agosto). Lo que el proyecto sostiene es lo contrario: miente y queda cazado. → **Aplicado:** «A measurement instrument for a market hypothesis. Its own errors get caught, dated and published.»
2. Faltaba el negativo más duro del proyecto, el que la página inglesa más necesita porque abre un riel de dinero: `estado_epistemico.md` §10 (CONTESTADA), entrar en la apertura y salir al cierre pierde 40,7 % sin costo y 95,6 % a 25 pb por lado, contra +137,1 % del ETF del sector. El hueco era idéntico en español. → **Aplicado en las dos plantillas**, tras el párrafo «NO distinguible de cero»: «TESTED AND FAILED: the advantage is not capturable…» / «CONTESTADA: la ventaja no es capturable…». Es la única adición de contenido a README.es.md (cifras ya publicadas en `estado_epistemico.md`, no movidas).
3. «Sealed prospective sessions so far: 9, of which 7 count… (last sealed input session: 2026-09-18)» exhibía como más fresca una sesión que NO cuenta sin decirlo. → **Aplicado:** marcador nuevo `{{e0_no_cuentan}}` (leído del CSV): «the ones that do not (2026-09-09, 2026-09-18) had incomplete or late input».
4. «Read from the versioned copy» falsa para un tercero mientras `data/backups/sello_dinero.csv` esté sin commitear (sobre HEAD el generador da 8 / 7 / 2026-09-17). → **Aplicado** en la redacción (misma exigencia #3 del adversario); commitear el CSV en el mismo acto que el README es acto de Nicolás.

## Observaciones

5. «edge» dos veces en el TL;DR compartido; el cuerpo dice «advantage». → **Aplicado en las dos plantillas:** «advantage» (el curador tiene la última palabra sobre el vocabulario).
6. La viñeta que esquivaba la palabra prohibida no se entendía. → **Aplicado:** «Subjective certainty labels are banned system-wide, this page included (a test verifies it, which is why the word itself is not printed here)…».
7. Las marcas «(now in the errata)» junto a las cifras retiradas de la rama derogada y del WS3 son honestas (retiradas el 3-sep, acta §78, y el 1-sep, acta §68); `cifras.reintroducciones()` da vacío sobre los cuatro archivos. Dos avisos **no aplicados, a la cola:** `GEMELO/resultados/ventana_larga.md` (líneas 42 y 176) sigue publicando vivas dos cifras retiradas (la «contaminación por revisión» del WS3 y la saturación del PSR) porque no está en `DOCUMENTOS_PUBLICADOS`; y de las cinco `MARCAS_FUERTES` sólo «errata» sobrevive a la traducción: la página inglesa está guardada por una marca de cinco.
8. «The step stands as MEASURED» y «TESTED AND FAILED» se sostienen. Sin hallazgo.
9. Badge `tests-650 passing` sin fecha (hoy pytest colecta 897) y prosa «652 tests … as of 6-Sep-2026». Mismo defecto en español. → **No aplicado** (ninguna cifra publicada se mueve sola): a la cola, con el `plataforma-5.0.3`.
10. «the rail exists to prove» → «to test» (E0 va 7 de 40); «every night» → «every trading night». → **Aplicado.**
11. Referencia colgante a `docs/readme/procedencia.json` en el generador. → **Aplicado:** el docstring remite al censo de procedencia del adversario (`adversario_readme.md` §7).

## Zonas ciegas declaradas por el curador

No corrió la suite (sólo colectó 897); no abrió `sello_dinero.db` (contó sobre la copia versionada, como el generador); no recomputó las ventanas; no auditó ESTADO.md; no verificó Hong Kong/India ni las capturas; el README no dice que los puertos 4001/4002 y el prefijo DU del corredor quedaron NO VERIFICADOS DIRECTAMENTE (`corredor/ibkr.py`).
