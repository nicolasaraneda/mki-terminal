# ESTADO

Dónde está el proyecto. Se regenera al cierre. **Máximo 50 líneas.** No es historia
(`DECISIONES.md`) ni cifras (`README.md`). **Actualizado:** 7-sep-2026 (corrida 10).

## Producción
- **Titular: este PC (WSL), en `main`**, 6 timers, emite; el modo se le pregunta a
  `modo.py`. Modelo 4.6.0 congelado. El sello vigente se lee de `./mki estado`, no de
  aquí. `.env` en 600. **La corrida 10 no tocó nada del camino de sellado.**
- `noticias.py` corregido (O(n²) → lineal) en producción desde el 3-sep. El bump de
  `FEATURE_VERSION` es de Nicolás (`espera` §38).

## Los dos rieles — decisión de arquitectura de la corrida 10 (`VISION.md`, acta §80)
El proyecto **mide una noche** y **quiere operar en semanas**. Son dos cosas legítimas y
no son la misma, así que desde ahora son dos rieles declarados y separados.
- **Riel de medición** (el de siempre): gap asiático sellado, una noche, no mueve plata.
  n 238 / 34 días, ventaja +9,7 pp, **IC95 de día [−7,2, +26,6] contiene el cero**.
  Lo que lo mata: V1–V7 / R1–R3 de `GEMELO/DISEÑO.md` §6.
- **Riel de dinero** (`dinero/`, nuevo): instrumentos de EE.UU., semanas, 100–500 USD,
  **todo SIMULADO, cero filas selladas**. Aislado del sellado en las dos direcciones, con
  test; y un test prohíbe toda mención de API de corredora o credencial.

## Lo que la corrida 10 midió (bitácora 10; nada entra al README)
- **Mapa operable:** 36/36 tickers verificados; 6 eslabones representados, 2 sustituidos,
  0 huecos (5/3/0 exigiendo liquidez). **`SMH` no cabe en 500 USD.** Con el piso de 100
  USD alcanzan 7 de 36 instrumentos.
- **Cuenta en papel (señal SIN información, mide fricción):** las comisiones se comen
  **14–43 % del capital** contra 0,4–0,6 % de no decidir nada; el barrido de costo cambia
  el camino y no el costo; **5 de 24 comparaciones dan IC que excluye el cero cuando la
  respuesta verdadera es cero en las 24**.
- **Señal larga v1:** **L1 (contagio directo) REFUTADA por su regla pre-registrada**, y a
  20 días acierta menos que la climatología (−2,339 pp [−4,522, −0,429]). Sobrevive una
  celda de seis contra la climatología causal: L2 a 60 días, +0,229 pp [+0,054, +0,424].
  **No autoriza nada.**
- **Potencia del riel:** σ = 2,54 pp/semana ⇒ las 52 semanas del criterio sólo alcanzan
  para ≈ +1,00 pp/semana. Si el criterio se cumple, la primera reacción es sospechar un
  error (`dinero/preregistro_dinero.md` §2.5).

## Deuda pagada y deuda nueva
- **La suite ya no puede correr en la ventana de sellado**: marcador `red`,
  `scripts/guarda_red.sh`, hook y `./mki tests`. Hallazgo: la primera guarda era ciega
  porque yfinance habla por libcurl. **6 tests marcados en 2 archivos** (4 los halló el
  censo, 2 más los halló la guarda después, corriendo en otro orden).
- **Registro de intentos del riel largo: 3, propio.** NO se tocó el asiático (352 / 358).
- **Sin hacer:** la ablación tipo R2 de la señal larga, que el pre-registro exige antes de
  cualquier monto real.

## Lo más urgente, que sigue siendo de Nicolás
Firmar **V1-bis** (cero vs climatología — la corrida 10 tropezó con exactamente ese
problema en el bloque 6) y el parche `snapshot.py:140`. Nuevos a firma: **§39** qué juego
de parámetros rige, **§40** el arancel real del corredor (M2 depende de él), **§41** si
los dos registros de intentos se fusionan. Los dictámenes de la 10 corren aparte.
