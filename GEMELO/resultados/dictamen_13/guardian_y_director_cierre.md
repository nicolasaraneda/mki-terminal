# Dictámenes de cierre — `guardian-constitucion` y `director-programa` (corrida 13, 19-sep-2026)

## Guardián (árbol de las 17:41): APTO PARA QUE NICOLÁS LO MIRE

Regla por regla: protegidos intactos (`motor.py`, `senales.py`, `snapshot.py`, `universo.py`, `version.py`, `alertas.py`, `app.py`, `.env`, `systemd/`, `requirements.txt`); filas selladas intactas (`dinero/sello_dinero.db` `30d4b988…`, `senales.db` `d476b457…`, `ext_2026-09-09.csv` `126e4f2c…`, verificados antes y después de correr tests; cero UPDATE/DELETE/DROP/ALTER en el diff; `sello_dinero.csv` estrictamente aditivo); sin push; rama `main`; el cambio al emisor declarado en §87.1 con método worktree; actas §87 completas; sin secretos; 112 tests puntuales en verde; alcance dentro de los seis bloques, 4.3 no ejecutado correctamente; 7 timers `mki-*` sin `mki-sonda-cierre`; `.env` intacto; `data/sello_dinero.log` sin entradas después del 19-sep 00:30: el sellador real no se corrió; cifras del árbitro no movidas, `README.es.md` contra el README de HEAD tiene exactamente los tres hunks declarados en §87.5.

Hallazgos (ninguno bloqueante):
1. `README.md` (contenido nuevo) y `README.es.md` (archivo nuevo) propagan las cuatro cifras vencidas que §87.7 declara (badges, «59×», N 352/358). Bajo una lectura estricta de la regla 10 («introduce o toca»), un archivo publicado nuevo que estrena una cifra derivada de una retirada sería rechazo; bajo «ninguna cifra publicada se mueve sola», moverlas habría sido peor. Queda declarado: **Nicolás confirma o corrige esa lectura antes de publicar la página en inglés.**
2. `ventana_larga.md:42` y `:176` publican vivas dos cifras retiradas; preexistente, el diff no lo toca, R7 prohíbe arreglarlo de paso.
3. El árbol se editaba durante el dictamen: primera corrida 1 rojo en `test_epistemico::…contiene_el_nulo…` (bitácora 346/348, «los dos contienen el cero» no es la marca que el escáner reconoce), corregido a las 17:40:09 y 17 passed. **Condición: número final de la suite completa y los tres sha256 reverificados al momento del commit.**
4. La unidad propuesta usa `17..23:05,35` y no `17..23:00,30`: desviación declarada en §87.3. Correcto.
5. `_camino_main` (tests/test_sello_dinero.py) llama a `congelar_extension` sin `ruta_db`, seguro sólo porque el fixture parchea el global; vale un `assert` de guarda. **Pendiente, no se arregla en esta tanda.**

Nota del orquestador: el guardián leyó §87.8 antes de que el director marcara la norma de paso; §87.9 la declara ahora.

## Director (cierre): ADELANTE, nada de código a revertir

(1) Lo que se salió del encargo: poco y declarado (la sección de E0 y la frase de apertura sólo en inglés son instruidas; el párrafo de no capturabilidad en `README.es.md` es la única adición a un documento que el 7.3 congeló, por dictamen del curador, se queda; `{{e0_no_cuentan}}` obligatorio; la reversión del 4.5 «la mejor decisión de la noche»; la memoria sobre worktrees no instala norma). Agujero visto: el test de paridad excluye la sección de E0, la única sobre dinero de la portada. (2) Norma instalada de paso: sí, una: el registro de intentos del riel largo ampliado a un barrido descriptivo (§87.9), con la asimetría de que la re-medición de `bifurcaciones` no se contó. (3) Pre-mortem: once de doce cumplidas como se escribieron; la 12 se cumplió en paralelo, no antes (§87.10). (4) Nada que revertir; tres correcciones de etiqueta, aplicadas. Postergado por el bloque 5: la sonda todavía no corrió ninguna noche real.
