# ESTADO

Resumen curado de dónde está el proyecto. Se regenera al cierre de cada sesión
con la skill `/cierre-sesion`. **Máximo 50 líneas.** No es historia: la historia
vive en `DECISIONES.md`. Las cifras publicadas viven en `README.md`.

**Actualizado:** 30-ago-2026 · verificar con el agente `orientador`

## Producción

- **Titular: este PC (Windows/WSL), en `main`.** El switch está completo: tiene
  la base canónica, los 6 timers activos y emite. El Mac quedó fuera.
- Al modo se le **pregunta a `modo.py`**, no se deduce. Ver `/modo-emision`.
- **No hay réplica.** Es la única máquina emitiendo.
- Modelo 4.6.0 congelado. `PLATAFORMA_VERSION` 5.0.3 congelada desde el 26-ago.
- Último sello: <rellenar>   N verificaciones: <rellenar>

## Errata pendiente de registrar

Las actas 36 y 37 y los docs del Proyecto afirman que `MKI_MODO=sombra` sigue
puesto y que el segundo movimiento está pendiente. **Ya no es cierto.** El
30-ago se comprobó que `modo.py` responde `titular`. Manda la máquina; la
discrepancia se documenta como errata, no se corrige hacia atrás.

## Frente · GEMELO 6.0.0

- Recorrido: pre-registro congelado, §9 (§2 reproducida 21/21), WS1 maquinaria
  de inferencia, WS2a capa de datos, WS2b control lineal NEGATIVO publicado,
  WS3 ventana larga, WS4 auditoría adversarial, WS5 hipótesis del relevo
  asiático REFUTADA.
- **Ningún documento designa el siguiente paso de esta etapa.** Decidirlo es de
  Nicolás.

## Esperando decisión de Nicolás

1. Las cinco preguntas abiertas del WS4 (§33.8), entre ellas si las 8 filas del
   29-jul siguen en las métricas, que es la abstención pendiente desde 5.0.2.
2. Si `.claude/` se versiona o queda local a esta máquina.
3. Los intervalos del ΔMAE de WS2b y WS3 están en otra escala (§34.9): no
   cambia conclusiones, pero los publicados no son los correctos.

## Sin commitear

`data/sombra/comparacion_2026-08-26/27/28.md` y `data/sombra/veredictos.jsonl`.

## Deudas y asimetrías declaradas

- `pd.concat` y `Pandas4Warning`: contenida por el pin de pandas. Bloquea todo
  upgrade.
- Intérprete: Mac 3.11.15, PC 3.14.4. Decisión: no igualar.
