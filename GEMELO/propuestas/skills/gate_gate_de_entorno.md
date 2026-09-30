# Skill `gate`: la línea del gate de entorno — PROPUESTA, NO APLICADA (corrida 15)

> **Por qué es una propuesta y no un cambio hecho.** El acta §91.4 firmó la deuda (5): «la skill
> `gate` deja de importar `scipy` y `sklearn`». El 29-sep-2026 a las 22:26 de Chile el orquestador
> intentó la edición con la herramienta `Edit` y **el clasificador de permisos de la sesión la
> denegó** (motivo: «Self-Modification»). Una barrera puesta a propósito no se rodea con otra
> herramienta: queda el texto exacto para que lo aplique Nicolás a mano. La deuda (6), la skill
> `cierre-sesion`, sí se aplicó en la misma tanda (la misma herramienta la aceptó).

## El cambio, una línea

Archivo: `.claude/skills/gate/SKILL.md`, bloque «Gate de entorno», línea 41.

Dice:

```bash
python -c "import pandas,numpy,scipy,sklearn; print(pandas.__version__, numpy.__version__)"
```

Debe decir:

```bash
python -c "import pandas,numpy,yfinance,exchange_calendars,fastapi; print(pandas.__version__, numpy.__version__)"
```

## Por qué

`scipy` y `sklearn` no están instalados ni figuran en `requirements.txt`, a propósito: la
inferencia del proyecto va con `math.erfc` y bisección. Medido en esta máquina el 29-sep-2026 a
las 22:26: `import scipy` y `import sklearn` dan `ModuleNotFoundError`. O sea que el gate de
entorno **falla por diseño en una máquina bien provista**, y un gate que falla siempre es un gate
que se aprende a saltar (bitácora 14, 8.5-bis).

La línea propuesta importa lo que el proyecto usa de verdad. Corrida en esta máquina a la misma
hora, sale sin error e imprime `3.0.3 2.4.6` (pandas, numpy); las otras tres versiones instaladas
son `yfinance` 1.5.1, `exchange_calendars` 4.13.2 y `fastapi` 0.139.0.

## Lo que esta propuesta no toca

El resto de la skill tiene otros textos que ya no describen la máquina (el «299 al 30-ago» del
GATE 1, la referencia al badge del README como «cifra vigente»). No los firmó ningún acta y no
se proponen acá.
