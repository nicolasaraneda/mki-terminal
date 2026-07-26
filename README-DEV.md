# MKI Terminal — guía de desarrollo (Etapa 5.0 "Plataforma")

**Un comando para todo:** `./mki <subcomando>`

| Subcomando | Qué hace |
|---|---|
| `./mki arrancar` | API (:8000) + frontend Vite (:5173), un Ctrl+C corta ambos |
| `./mki estado` | jobs launchd, último sello con salud de descarga, presupuesto IA, estados de predicciones, cola del vigía |
| `./mki reporte` | envía el reporte de Telegram AHORA (compuesto 100% del sello) |
| `./mki tests` | pytest completo + test anti-look-ahead del motor |
| `./mki auditoria` | revisión de SOLO LECTURA: los 5 chequeos del vigía, sellos de la semana, gasto del mes, git |
| `./mki instalar` | los 5 jobs de launchd + el hook pre-commit |

Los tres procesos, a mano si se prefiere:

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
motor.py (v4.6.0 CONGELADO), senales.py, noticias.py, calendarios.py
        ▲ import (solo lectura)
api/                    FastAPI: endpoints GET, contrato en api/CONTRATO.md
  main.py               envuelve motor.py y lee senales.db/noticias.db;
                        errores homogéneos {"detail","codigo"} enmascarados
  utilidades.py         cache TTL + earnings + OHLC + Wilson (presentación)
        ▲ fetch /api (proxy de Vite)
frontend/               Vite + React + TS + Tailwind 4 (versiones exactas)
  src/vistas/           Hoy, Aperturas, Cadena, Mercados, Comparador,
                        Analisis, Historial, Laboratorio, Salud, Detalle,
                        Sistema (oculta)
backtest/               motor B0→B5 (DISEÑO.md congelado en el GATE B);
                        SOLO LECTURA, resultados/ propios, ejecución con
                        veredicto diferida a la Etapa 5.1
jobs (launchd, hábiles) noticias 17:50 · snapshot 18:15 · reporte 18:25 ·
                        backup 18:40 · vigía 19:00  (launchd/INSTALACION.md)
```

Reglas que el código respeta y toda contribución debe respetar:

- **La API jamás escribe** en las bases ni llama a la API de Anthropic
  (noticias solo desde el cache de `noticias.db`).
- **El frontend jamás computa una señal** — presenta lo que la API sirve.
  Si un número del terminal difiere de Streamlit, el bug está en `api/` por
  definición (los dos beben del mismo motor).
- **Incertidumbre de primera clase:** todo número de señal va acompañado de
  n, R² e intervalo — y desde 5.0, los aciertos con su Wilson 95%.
- **Anti look-ahead como UI:** una predicción sellada muestra "emitida
  {fecha hora}, antes de la apertura objetivo".
- **Un secreto jamás se imprime completo** (`seguridad.enmascarar_secretos`);
  el gasto de IA vive bajo tope diario (`costos.py`, .env).
- Presupuesto de cian ≤ 4 por vista; jerarquía por fondos/bordes, sin glow;
  cifras en JetBrains Mono tabular; sin emojis en la UI.

## Tests y hook pre-commit

```bash
./mki tests                               # todo (pytest + motor)
python -m pytest tests/test_api.py -q     # solo paridad API ↔ motor
python -m pytest tests/test_backtest.py -q  # solo el framework de backtest
cd frontend && npm run build              # typecheck + build
```

El hook pre-commit (se instala con `./mki instalar`) SIEMPRE escanea lo
stageado por patrones de secretos, y corre la suite salvo que el commit sea
solo de `data/backups/` (el job diario no se bloquea) o se fuerce con
`SKIP_TESTS=1 git commit ...` (emergencias conscientes).

## Logs y rotación

Cada job escribe a su `data/*.log` (gitignorados) y rota su propio log al
arrancar (`registro.rotar_log`, copy-truncate 2 MB × 2 copias — launchd
mantiene el descriptor y sigue escribiendo limpio).

## Vistas y datos

| Vista | Endpoint(s) |
|---|---|
| /hoy | /api/hoy (incluye la cinta de husos) |
| /aperturas | /api/aperturas |
| /cadena | /api/cadena |
| /mercados | /api/mercados |
| /comparador | /api/comparador + /api/universo |
| /analisis | /api/noticias + /api/universo |
| /historial | /api/historial (Wilson, calibración, desgloses 5.0) |
| /laboratorio | /api/historial (progreso del gatillo 5.1) |
| /salud | /api/salud (bloque operacion 5.0) |
| /detalle/:t | /api/detalle/{t} |
| /sistema | catálogo de componentes (oculta, sin enlace) |

Capturas de referencia en `docs/capturas/`.
