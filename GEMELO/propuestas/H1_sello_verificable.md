# H1 · Un sello verificable por un tercero — PROPUESTA (octava corrida, 2-sep-2026)

> **Nada de esto está construido ni activado.** Es una propuesta para
> `cola_decisiones.md` / `espera_firma.md`. No toca `snapshot.py`,
> `senales.py` ni el camino del sello. Intentos del DSR que consume: **0**
> (no prueba ninguna hipótesis sobre retornos).

## 0. Qué prueba hoy el sello, y a quién

La regla maestra dice: una predicción es verificable si fue emitida ANTES
del evento, **probablemente vía timestamps**. Hoy la prueba de «antes» es:

1. `timestamp_utc` en la fila, puesto por el reloj de esta máquina;
2. el commit «Backup diario {fecha}» de `data/backups/`, cuya fecha también
   la pone esta máquina;
3. el **push manual** de Nicolás, después de las 20:30: el servidor de
   GitHub registra cuándo recibió el commit. **Ése es hoy el único
   instante que no depende del reloj ni de la buena fe de esta máquina.**

Un tercero que no confía en la máquina sólo puede afirmar «la predicción
existía cuando GitHub recibió el push», es decir, **después de las 20:30 de
Chile, cuando Seúl ya abrió** (~21:00 Chile). Para las bolsas asiáticas el
sello es verificable ante uno mismo, no ante un tercero. La séptima corrida
agregó la otra mitad del problema: la fuente sirve el mismo query en
estados distintos (hipótesis M6), así que «emitido antes» hoy no implica
«reproducible después».

**Dos propiedades, dos mecanismos.** Ninguno modifica el sello; los dos
leen `senales.db` en `mode=ro` y corren en un proceso aparte, DESPUÉS del
sello, de modo que su fallo jamás pueda impedirlo (misma regla que
`_epilogo_vigia()`).

## 1. Mecanismo A · Anclaje externo del resumen (emitido antes, ante un tercero)

**Qué:** un job `mki_sello_externo.py` (séptimo timer, 18:20, lunes a
viernes) que:

1. lee las filas selladas de hoy (`senales.db`, `mode=ro`), las serializa
   de forma canónica (columnas fijas, orden por ticker, sin `creado_en`) y
   computa un SHA-256; **o, más simple y ya existente:** el SHA-256 del CSV
   de respaldo del día tal como lo exporta `snapshot.py` — el mismo archivo
   que se commitea;
2. ancla ese resumen fuera de la máquina por una de dos vías (a elegir):
   - **A-1 · OpenTimestamps** (`ots stamp`, gratuito, prueba anclada a la
     cadena de Bitcoin; la prueba completa tarda horas en confirmarse, pero
     el resumen queda enviado a los calendarios en segundos). Verificación
     por cualquiera con `ots verify` y un nodo o un explorador público.
   - **A-2 · Sello RFC 3161** contra una TSA pública (token instantáneo,
     firmado por la autoridad; verificación con `openssl ts -verify`).
     Depende de confiar en la TSA; más de una TSA reduce esa dependencia.
3. guarda `data/sellos_externos/{fecha}.sha256` + `.ots`/`.tsr`,
   **versionados como los backups** (el job de backup ya commitea
   `data/backups/` por pathspec; se agrega la carpeta al mismo pathspec).

**Qué afirma entonces un tercero:** «el resumen R existía en el instante
T_ancla, y T_ancla es anterior a la apertura de la sesión objetivo». Como
T_ancla ≥ emisión real, acota la emisión **por arriba**, que es exactamente
lo que la regla maestra necesita. Hoy la apertura más cercana es Seúl
(~00:00 UTC); un anclaje a las 18:20 Chile (22:20 UTC) deja ~1 h 40 de
margen, contra las ~2 h de margen de publicación que el proyecto ya exige.

**Costo medido o medible:** un archivo de ~1 KB por día; segundos de
ejecución; **0 USD**. **Costo no monetario, y es el que pesa:** una
**segunda salida de red** del sistema (hoy la única es
`alertas.enviar_mensaje()`, y `modo.py` la conmuta en sombra). El job debe
(i) preguntar el modo y no anclar en sombra; (ii) usar
`socket.setdefaulttimeout` como el entrypoint de noticias (un TSA colgado
no puede dejar un proceso vivo 4 días); (iii) pasar todo error por
`seguridad.enmascarar_secretos()`; (iv) ser vigilado por el vigía por su
artefacto (existe `{fecha}.ots`), no por su log.

## 2. Mecanismo B · Reproducible después (insumos congelados)

**Qué:** activar la **copia de insumos** ya diseñada y con arnés probado
(`GEMELO/INSUMOS/insumos.py`, séptima corrida), y extender el resumen del
mecanismo A para que cubra **insumos y salidas** del día: el SHA-256 de la
copia de precios usada por el motor, junto al de las predicciones. Un
tercero puede entonces (1) verificar que los insumos existían en T_ancla,
(2) recomputar la predicción con `motor.py` en el commit etiquetado sobre
esos insumos, (3) comparar con la fila sellada. Eso cierra la brecha M6:
la fuente puede servir hoy otro estado, pero el estado que se usó está
guardado y anclado.

**Costo medido (séptima corrida, `bitacora_07.md` 02:37, no estimado):**
**9 MB/año** con 130 barras por ticker; **53 MB/año** con 3 años. Cabe en
el repo o en un almacenamiento aparte; la decisión de dónde es de Nicolás.

## 3. Qué NO arregla ninguno de los dos

- No prueba que la predicción se computó CON esos insumos (B lo prueba
  sólo si el tercero recomputa; A solo no).
- No corrige el reloj: si la máquina emite tarde, T_ancla lo muestra,
  y la fila cae en `no_verificable_timing` como hoy. Es el resultado
  correcto.
- No mueve ninguna cifra publicada, ni el criterio de verificación, ni el
  modelo. Vale para el 4.6.0 y para cualquier retador por igual.
- No reemplaza el `segundo sello` (`docs/SEGUNDO_SELLO.md`): aquél observa
  a la fuente después; éste prueba el instante y guarda los insumos.

## 4. Lo que espera la firma

1. **Si se agrega una segunda salida de red** al sistema (es la
   constitución 5.0 §6 en espíritu: una salida más es una superficie más).
2. **A-1 o A-2** (o ambos). Recomendación: **A-1** (sin autoridad en la
   que confiar), con A-2 como segunda firma si se quiere verificación
   instantánea.
3. **Si el mecanismo B se activa** con la copia de insumos y dónde vive el
   almacenamiento (9 o 53 MB/año, medidos).
4. Todo esto es un séptimo timer: **timers = Nicolás**.

Orden si se firma: primero A (un día de sombra, comparar el resumen con el
CSV commiteado), después B. Ninguno antes del 25-oct: no cambia el gatillo
y no hay que introducir un proceso nuevo en la ventana que se está midiendo.
