# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 7-sep-2026 (corrida 10).

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers, emite; el modo se le pregunta a
  `modo.py`. Modelo 4.6.0 congelado. El sello vigente se lee de `./mki estado`, no de
  aquí. `.env` en 600. **La corrida 10 no tocó nada del camino de sellado.**
- `noticias.py` corregido (O(n²) → lineal) desde el 3-sep; el bump de `FEATURE_VERSION`
  es de Nicolás (`espera` §38).

## Los dos rieles (detalle en `VISION.md`, acta §80)
- **Medición** (el de siempre): gap asiático sellado, una noche, no mueve plata. n 238 /
  34 días, ventaja +9,7 pp, **IC95 de día [−7,2, +26,6] contiene el cero**. Lo que lo
  mata: V1–V7 / R1–R3 de `GEMELO/DISEÑO.md` §6.
- **Dinero** (`dinero/`): instrumentos de EE.UU., semanas, 100–500 USD, **todo SIMULADO,
  cero filas selladas**. Aislado del sellado en las dos direcciones, con test.

## Corrida 10, DESPUÉS de los cuatro dictámenes (`GEMELO/resultados/dictamen_10/`)
**Los cuatro rechazaron.** Lo de abajo ya tiene aplicadas sus exigencias. Nada al README.
- **Mapa operable (en pie):** 36/36 verificados; 6 representados / 2 sustituidos / 0
  huecos (5/3/0 con liquidez). `SMH` no cabe en 500 USD; con 100 USD alcanzan 7 de 36.
  Censo de **un solo día**, casos al borde declarados (`MSFT`, por 30 centavos).
- **Cuenta en papel: RETIRADA.** Cuatro fugas temporales demostradas ejecutando código; la
  cifra titular se mueve (el juego medio pasa de 27 % a **57 %** a 5 pb). **Ninguna de sus
  cifras se puede citar.** El signo aguanta, el número no. Clavadas con **xfail estricto**
  en `tests/test_dinero.py`: el día que se arreglen, el test obliga a volver acá.
- **Señal larga: no queda ninguna afirmación positiva en pie.** L1 **REFUTADA** por su
  regla pre-registrada, y eso se sostiene solo. Lo demás se cayó: la familia son **30
  contrastes, no 24**, y con Holm **ninguno cruza α = 0,05**; la celda que ganaba sin
  corregir no pasa la ablación anual (sin 2024 el IC contiene el cero); el −2,339 pp de
  dirección, bajo Holm, tampoco. **La segunda vara pre-registrada no se evaluó**, así que
  ni la regla §6 ni M4 se pueden dar por leídos.
- **Potencia del riel: RETIRADA.** σ salía de la cuenta con fuga y viajaba sin intervalo.
  Sobrevive lo cualitativo: 52 semanas sólo alcanzan para una ventaja grande, y una así no
  es plausible; si el criterio se cumple, sospechar un error (`preregistro_dinero.md`
  §2.1 — el «§2.5» que se citaba **no existe**, errata §6 D).

## Deuda
- **Pagada:** la suite ya no corre en la ventana de sellado (`red`, `guarda_red.sh`,
  hook, `./mki tests`). **6 tests marcados en 2 archivos.**
- **La grande, nueva: reconstruir la cuenta en papel sin fuga.** Orden del auditor: el
  test de truncación va **antes** que la corrección; los tres xfail ya están escritos.
- Registro de intentos del riel largo: **3**, propio. Asiático intacto (352 / 358).

## Lo más urgente, que sigue siendo de Nicolás
Firmar **V1-bis** (cero vs climatología — la corrida 10 tropezó con eso en el bloque 6) y
el parche `snapshot.py:140`. De la 10: **§39** qué juego rige, **§40** el arancel real del
corredor, **§41** si los registros de intentos se fusionan. Del cierre: **§42** si la
cuenta en papel se reconstruye o se descarta, **§43** el período de M2, **§44** M4
reescrita bajo multiplicidad.
