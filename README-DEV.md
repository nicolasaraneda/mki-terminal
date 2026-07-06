# MKI Terminal — guía de desarrollo (Etapa 4.7 "Fachada")

Tres procesos que conviven sin pisarse (puertos distintos):

| Proceso | Puerto | Comando |
|---|---|---|
| API (FastAPI, solo lectura) | 8000 | `source venv/bin/activate && uvicorn api.main:app --reload` |
| Frontend React (Vite) | 5173 | `cd frontend && npm run dev` |
| Streamlit (respaldo, intacto) | 8501 | `source venv/bin/activate && python -m streamlit run app.py` |

> Node vive en `~/.local/node` (sin brew/sudo). Si `npm` no aparece:
> `export PATH="$HOME/.local/node/bin:$PATH"`

Abrir el terminal: **http://localhost:5173** (necesita la API en :8000).

## Arquitectura

```
motor.py, senales.py, noticias.py, calendarios.py   ← REGLA CERO: intocables
        ▲ import (solo lectura)
api/                    FastAPI: 10 endpoints GET, contrato en api/CONTRATO.md
  main.py               envuelve motor.py y lee senales.db/noticias.db
  utilidades.py         cache TTL + earnings + OHLC (presentación pura)
        ▲ fetch /api (proxy de Vite)
frontend/               Vite + React + TS + Tailwind 4
  src/lib/              api.ts (TanStack Query) · tipos.ts (espejo del contrato)
                        tiempo.ts (todo en hora de Chile)
  src/componentes/      Card, StatTile, SignalBadge, RegimeChip, DataTable,
                        CandleChart, CorrHeatmap, NewsSentiment, EmptyState,
                        Sparkline, CintaHusos (elemento firma)
  src/vistas/           Hoy, Aperturas, Cadena, Mercados, Comparador,
                        Analisis, Historial, Detalle, Sistema (oculta)
```

Reglas que el código respeta y toda contribución debe respetar:

- **La API jamás escribe** en las bases ni llama a la API de Anthropic
  (noticias solo desde el cache de `noticias.db`).
- **El frontend jamás computa una señal** — presenta lo que la API sirve.
  Si un número del terminal difiere de Streamlit, el bug está en `api/` por
  definición (los dos beben del mismo motor).
- **Incertidumbre de primera clase:** todo número de señal va acompañado de
  n, R² e intervalo — al lado, no en un tooltip.
- **Anti look-ahead como UI:** una predicción sellada muestra "emitida
  {fecha hora}, antes de la apertura objetivo".
- Presupuesto de cian ≤ 4 por vista; jerarquía por fondos/bordes, sin glow;
  cifras en JetBrains Mono tabular; sin emojis en la UI.

## Tests

```bash
source venv/bin/activate
python -m pytest tests/test_api.py -q     # paridad API ↔ motor (17 tests)
python -m pytest tests/ -q                # todo
cd frontend && npm run build              # typecheck + build
```

## Vistas y datos

| Vista | Endpoint(s) |
|---|---|
| /hoy | /api/hoy (incluye la cinta de husos) |
| /aperturas | /api/aperturas |
| /cadena | /api/cadena |
| /mercados | /api/mercados |
| /comparador | /api/comparador + /api/universo |
| /analisis | /api/noticias + /api/universo |
| /historial | /api/historial |
| /detalle/:t | /api/detalle/{t} |
| /sistema | catálogo de componentes (oculta, sin enlace) |

Capturas de referencia en `docs/capturas/`.
