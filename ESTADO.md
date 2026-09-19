# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 19-sep-2026 (corrida 13).

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers del riel de medición + `mki-sello-dinero.timer`
  (usuario, `Mon..Fri 23:30 America/New_York`), emite; el modo se le pregunta a `modo.py`. Modelo
  4.6.0 congelado; `PLATAFORMA_VERSION` 5.1.0 (§84). El sello vigente se lee de `./mki estado`.
  **La corrida 13 no tocó el camino de sellado**; `senales.db` y `dinero/sello_dinero.db` con el
  mismo sha256 antes y después.

## Los dos rieles (detalle en `VISION.md`, acta §80)
- **Medición:** gap asiático sellado, una noche. n 238 / 34 días, +9,7 pp, **IC95 de día
  [−7,2, +26,6] contiene el cero**; R2 bajo la regla firmada +2,6 pp (n 194, contiene el cero).
  La rama de coherencia (§46) sigue NO cableada. **La ventaja no es capturable** (CONTESTADA, §10).
- **Dinero** (`dinero/`): todo SIMULADO. **E0 EN CURSO: 9 sesiones selladas por el timer, 7 cuentan
  de 40** (leído de la base; no cuentan 09 y 18-sep por `insumo_incompleto`; señal = sorteo sin
  información: prueba de maquinaria, no track record, §86.2). **E1 NO EJECUTADO** (sin cuenta de
  práctica ni gateway). E2: monto 500 USD firmado (§86.3), no iniciado.

## Corrida 13 (19-sep): E4-bis, sonda, README en dos idiomas, universo por presupuesto (acta §87)
- **Fuga cerrada en producción (E4-bis):** el sellador pisaba `ext_<fecha>.csv` de una fecha ya
  sellada cuando el timer volvía a disparar (10-sep; nueve días con el disco citando otro sha). Con la
  fecha sellada ya no se escribe ningún archivo de esa fecha (opción A del auditor); test permanente
  de integridad disco = base en la suite. Aplicado a las 17:02 −03, fuera de la ventana 00:00–01:00.
- **Sonda del cierre** (`GEMELO/sonda_cierre.py` + resumen + unidad propuesta, sin instalar): el dato
  para decidir la hora del timer (§58). TOELY perdió el 18-sep; en dos descargas separadas 24 h sus
  cierres del 08 al 15 pasaron de estar a estar vacíos (MEDIDO, n = 1 par; atribuirlo a Yahoo es
  PROPUESTA).
- **README:** `README.md` inglés y `README.es.md` español, generados por `scripts/generar_readme.py`
  desde plantillas y el árbitro; guardias sobre los dos; cifras idénticas entre idiomas (adversario).
- **Bloque 6:** `universo_por_presupuesto.md` (PROPUESTA, descriptivo) como insumo del monto de E2.
- **Bookkeeping:** §51/§52/§53/§57 marcadas firmadas (§86); §58, §59, §60 nuevas; 4.3 NO ejecutado.
- Registro de intentos: gap asiático **354**, veredicto 5.1 **360** (sin cambio); riel largo **4**.

## Deuda
- **Erratas en los dos README, pendientes de Nicolás:** N de intentos 352/358 (registro 354/360);
  «59×» (n derogado; con 238 es 61,4×); badges `tests-650` y `plataforma-5.0.3`; `ventana_larga.md`
  fuera de `DOCUMENTOS_PUBLICADOS` con dos cifras retiradas vivas. `data/backups/sello_dinero.csv` sin
  commitear: el contador de E0 del README sólo es regenerable desde HEAD cuando se commitee.
- Contador de «lecturas de criterio» (§43): sin sitio. `bifurcaciones.md` sin regenerar: el nivel `vivo`
  creció (251 → 371 filas) y regenerar es medir de nuevo, no cambiar réplicas (§87.4; decisión de Nicolás).
- Reintroducciones en `DECISIONES.md` (53 líneas de actas históricas): no se tocan por diseño.

## Lo más urgente, que sigue siendo de Nicolás
Instalar (o no) la sonda y decidir **§58** con su dato; **§60** (gitignore de las extensiones);
**§59** (`visible_en`); **§43**, **§46**, **§48**, **§50**, **§54**, V1-bis (§30). Commit de la
corrida 13 con `data/backups/sello_dinero.csv` y los dictámenes a la vista. **No hay push.**
