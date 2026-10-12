# Dictamen del `curador-epistemico` sobre los textos de la corrida 16-3 (README, contrato, tesis, tarjetas, ESTADO.md, bitácora)

> Archivado por el orquestador tal como lo devolvió el agente (el agente no escribe archivos). Lanzado a las 21:01 de
> Chile del 11-oct-2026 sobre el árbol real con los cambios aplicados (sin commitear). Apertura **21:01:24**, cierre
> **21:12:57** (−03:00, `date` del agente). Nada escrito; las tres bases con las huellas de apertura. **Cómo se atendieron
> las tres bloqueantes y las observaciones: bitácora 16-3 §5.3.** El veredicto es sobre el estado de las 21:01; los
> arreglos son posteriores (21:14 a 21:20) y el acta §104 se escribió después del dictamen, que es lo que la bloqueante
> 1 exigía.

```
VEREDICTO: RECHAZA
Documentos: README.md · README.es.md · docs/readme/README.en.tmpl.md · api/CONTRATO.md ·
            GEMELO/resultados/tesis.md · GEMELO/resultados/espera_firma.md ·
            ESTADO.md · GEMELO/resultados/bitacora_16_3.md
Oraciones revisadas: 14 en «Execution rail» del README (8 nuevas o reescritas) + 50 líneas de
            ESTADO.md + 44 líneas de la enmienda 16-3 del contrato + 8 tarjetas nuevas (§82 a §89)
            + 4 marcas FUNDIDA + 2 FIRMADA + bitácora §0 a §5 y §7.
Sin etiqueta posible: 0 en el README (toda afirmación nueva es trazable a acta o a la máquina);
            3 afirmaciones con etiqueta equivocada o ausente, abajo.
```

## BLOQUEANTES

**1. `ESTADO.md` línea 4 y `GEMELO/resultados/bitacora_16_3.md` §5.1 citan un acta que no existe.** `grep -n "^## Acta
§10[0-9]" DECISIONES.md` devuelve §100, §101, §102, §103; el archivo tiene 10108 líneas; §104 no existe. La máquina manda:
el estado del proyecto cita como fuente un acta no escrita, y es el documento que se commitea. Arreglo: escribir §104
antes del commit, o decir «acta §104, en redacción». La bitácora ya lo tiene previsto en su fila `[cierre]`, así que esto
es secuencia, no error de hecho; pero no puede entrar al commit colgando.

**2. `bitacora_16_3.md` §2 afirma un estado mental que ningún instrumento sostiene, y contradice la zona ciega que el
propio auditor de la corrida declaró.** Texto: «La regla se firmó por su mérito el 29-sep (§90.1 d), antes de mirar esto
(el auditor de la 15 ya lo había medido para el árbitro)». Cifra del árbitro (dictamen del auditor, Z2): §90.1 d se firmó
el 29-sep a las 18:29, 14 minutos después de que el verificador escribiera las 8 filas, con la magnitud en la bitácora 14
§9; la dirección del efecto era computable al redactar; no es demostrable en ninguna dirección. «Antes de mirar esto» es
una afirmación sobre lo que una persona miró, no medible. Etiqueta correcta: el acta registra el orden de método
(DECLARADO); la dirección del efecto era computable al redactar (Z2, DECLARADA). Regla 2 de la casa: la prosa no supera
a la cifra.

**3. `GEMELO/resultados/tesis.md` ofrece una cifra retirada como exigencia vigente, sin marca de retiro a ±2 líneas.**
Línea 172: «la copia cruda congelada al sellar (**C3**: ~60 líneas, ~15 MB/año, …». `cifras.reintroducciones` la marca
(`~?15\s?MB/año`); `GEMELO/cifras_retiradas.md` la retiró el 2026-09-02 (`bitacora_07.md` 02:37) con reemplazo medido «9
MB/año (130 barras) / 53 MB/año (3 años), medidos». No es autoría de la 16-3 (en HEAD está igual) y la suite no la caza
porque `tests/test_cifras_arbitro.py` cubre sólo los tres documentos publicados; pero la 16-3 edita y commitea este
archivo, y la cifra está ofrecida como el costo del camino C3. Etiqueta correcta: el valor medido, o la cita con su marca.

## OBSERVACIONES

**O1.** El estatus evidencial de «a power cut» no está a la vista (README): la única noche atribuida a un corte es el
6-oct y el acta §99.1 la etiqueta DEDUCIDA (no medida con `journalctl --list-boots`); la lista plana le da el mismo peso
que a «an incomplete input», MEDIDO sobre 10 sesiones. **O2.** La razón que el README da para sacar TOELY es más angosta
que la máquina: TOELY también rompió el insumo el 18-sep y el 23-sep con un día de atraso, cuando la fuente sí lo servía
(medido sobre el CSV: único ticker con `ultimo_cierre_ticker < fecha_insumo` en esas fechas); §96.3 ya lo anotó como
«rezagado crónico». **O3.** La página declina el conteo por firma (§93.11.1 b) y el conteo es el negativo: 22 fechas
selladas, 12 cuentan para N = 40, 10 no, y dos noches de bolsa sin ninguna fila (25-sep y 6-oct); «nights get missed» sin
proporción permite leer el riel como mayormente funcionando. **O4.** `ESTADO.md` nombra tres sesiones perdidas donde la
máquina cuenta 10 de 22 sin contar más dos sin filas; la lista de tres se lee como exhaustiva. **O5.** Un cuantil sin su
método (§82: «p25 38 %»): recomputado, la mediana da 75,0 exacta y el p25 depende del método (34,4 `linear`, 37,5
`higher`/`nearest`, 31,25 `midpoint`, 25,0 `lower`); `P(≤3|8, 0,624) = 0,1388`, exacta. **O6.** «Mismo denominador» a dos
cláusulas de «n 149 → 141» (contrato): lo invariante es la definición, no el conteo. **O7.** «La cifra del campeón» es
ambigua (§82.1): el +0,75 pp es la tasa de gap de toda la historia viva (316/482 → 313/472), no la ventana sellada del
README. **O8.** Dos huecos que son condición de cierre: la PRIMERA LÍNEA de la bitácora y la línea de la suite real en §6
(B2 del auditor). **O9.** Rayas largas: 8 en líneas nuevas, las ocho separadores de encabezado o viñeta (convención
preexistente del archivo; 31 de 37 encabezados de `espera_firma.md` en HEAD la usan); ninguna en prosa nueva. **O10.**
Barrido de cifras retiradas en `.py`: 17 de 197 marcados, ninguno en el diff de la 16-3, todos historia, pedagogía o
falsos positivos de conjugación (`"scan_saturado"`); la suite no cubre `.py`, el único guardia es el hook sobre el texto
nuevo. **O11.** Preexistente y fuera del alcance: la columna sellada `senales_ticker.confianza_r2` lleva la palabra
prohibida; en los dos README el barrido da limpio (`README.es.md:304` es el enunciado de la prohibición).

## Lo verificado, con comando y cifra (resumen)

- `pytest tests/ --collect-only -q` → 1216; `version.py` 5.1.0; `badges_congelados.json` mueve los tres valores juntos;
  `generar_readme.py --verificar` coincide con el disco; `test_cifras_arbitro.py` + `test_readme.py` → 29 passed.
- Las dos frases firmadas, al carácter: §93.11.3 → `README.md:391` idéntica; §102.5 → `README.md:407` idéntica, errata de
  hecho correcta sobre §93.11.2 por §95.3. §93.11.1 cumplido (`grep salud README.md`: ninguno del riel).
- Riel E0 contra `data/backups/sello_dinero.csv` (722 filas): primera fila 2026-09-08; 18 fechas con 33 filas y
  `125a8602…` hasta el 2-oct, 4 con 32 y `b6080eee…` desde el 5-oct; `ultimo_cierre_ticker` de TOELY tope en 2026-09-24;
  `cuenta_para_N = 1` en 12 fechas; `e0_N_objetivo = 40`; las cuatro condiciones del README mapean 1 a 1 con
  `sello_dinero.py:736`; `corredor/ibkr.py` levanta `ErrorCuentaNoPractica` y `NotImplementedError("E1 no ejecutado …")`.
- Enmienda 16-3 del contrato, cifra por cifra contra `dictamen_16_3/evidencia/`: todas coinciden (n 149 → 141, gap 62,4 →
  63,8, MAE 3,95 → 4,07, sesión 65,1 → 67,4, calibración 490 → 482 y 93,5 → 93,6, evolución 64 → 63 con la del 28-sep
  fuera, detalle 490 → 482 y 319 → 316, exchanges, puntaje 1308 sin cambio, últimas 21-sep → 18-sep, orden verificado).
  Las 8 filas: un solo par de instantes; aciertos 3 y 2; MAE 1,8072; dedup 10 filas, 482 → 472, +0,753 pp.
- `tesis.md` 61× contra `larga_veces = 61` (14618/238 = 61,42); §82 (17 de 56 días; 0,1388); §80 contra el punto 102.1 del acta §102;
  §81 contra §103.1; las cuatro FUNDIDA conservan el texto; las ocho tarjetas con etiqueta y «No se eligió nada».
- `ESTADO.md` 50 líneas; `modo.py` titular; `senales.py` fuera de `git status`; 7 huellas de la tabla de §6 idénticas; las
  tres bases idénticas; las predicciones de §7 coinciden con `medicion_despues.txt`.

## Zonas ciegas

Z1: sin suite completa del árbol real registrada al momento del dictamen (la línea de §6 estaba vacía). Z2: no reprodujo
las mediciones de los dos auditores. Z3: las cifras del CSV y de `senales.db` son del estado de hoy; Yahoo revisa. Z4: no
juzgó `frontend/src/vistas/SellosDinero.tsx`. Z5: el p25 lo recomputó con su propio SQL, no con `lb.sin_conocibilidad`.
Z6: no leyó `.env` ni tocó systemd.

Lo que hay que cambiar es poco y es barato: escribir §104 antes del commit, una oración en la bitácora §2 que diga lo que
el Z2 del auditor midió, y la línea de `tesis.md:172` con su cifra medida. Ninguno de los tres toca una cifra publicada.
