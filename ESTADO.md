# ESTADO

Resumen curado de dónde está el proyecto. Se regenera al cierre de cada sesión
con la skill `/cierre-sesion`. **Máximo 50 líneas.** No es historia: la historia
vive en `DECISIONES.md`. Las cifras publicadas viven en `README.md`.

**Actualizado:** 31-ago-2026 (segunda corrida) · verificar con `orientador`

## Producción

- **Titular: este PC (Windows/WSL), en `main`.** Switch completo, 6 timers
  activos, emite. Al modo se le **pregunta a `modo.py`**.
- **No hay réplica activa.** `replica.py` (registro de divergencias) y
  `fecha_corte` en `comparar_sombra.py` ya existen y están probados (329
  tests) — nada activado, nada decidido sobre "quién gana".
- Modelo 4.6.0 congelado, `PLATAFORMA_VERSION` 5.0.3 desde el 26-ago. Último
  sello: 2026-08-28 · N verificaciones: 253 (248 bajo `excluir_cero`).

## Errata pendiente de registrar

Actas 36/37 dicen `MKI_MODO=sombra` puesto — **ya no es cierto** (30-ago,
`modo.py` → `titular`). Manda la máquina.

## Frente · GEMELO 6.0.0

- **La concentración de julio, corregida dos veces (§45):** la v1 de
  `concentracion.md` concluía "es azar" apoyada en un criterio movido sin
  declararlo (invertía el veredicto). **Retractado.** Hoy: la evidencia
  NO alcanza para decidir "hay condición" vs. "es azar" — sí es sólido
  que el campeón no pasa su propio R2 y que la ventana completa sigue sin
  ser distinguible de cero (p=0.185).
- `GEMELO/MICRO/RTL.md` (pipeline RTL) y `GEMELO/RELEVO.md` (relevo)
  siguen vigentes. `parche_documental.md` quedó **desactualizado** por la
  corrección de arriba — no aplicar sin revisarlo primero.
- N del DSR: **≥43** (`relevo_asiatico.py` sigue en 25, sin actualizar).

## Esperando decisión de Nicolás

Lista consolidada y priorizada por costo de postergar (no tamaño) en
`GEMELO/resultados/cola_decisiones.md`. Primero: activar la réplica y con
qué máquina — único ítem cuyo costo de espera ya se materializó una vez
(el disco que falló). Después: la lectura del track record, y los
umbrales de `RELEVO.md`.

## Deudas y asimetrías declaradas

- `pd.concat`/`Pandas4Warning`: contenida por el pin (3 sitios) — expediente 6C.
- Intérprete: Mac 3.11.15, PC 3.14.4. Decisión: no igualar.
- Lección de §45: todo análisis estadístico va a un script versionado
  desde el primer cómputo, nunca a comandos sueltos.
