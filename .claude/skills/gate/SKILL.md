---
name: gate
description: Corre el gate de verificación antes de dar por buena cualquier tanda de cambios. Úsala antes de proponer un commit, después de portar scripts, después de tocar dependencias y antes de abrir una ventana de paridad. Ejecuta la suite completa, el anti-look-ahead del motor y las comprobaciones de entorno.
argument-hint: "[1 | A-bis | entorno]"
---

# Gate de verificación

Un gate no se pasa "en general". Se corre, se mira la salida literal y se
reporta. Si no se corrió, no está aprobado.

## GATE 1, el de código

```bash
cd ~/dev/mki-terminal
source venv/bin/activate
python -m pytest tests/ -q          # 299 al 31-ago; la cifra vigente esta
                                    # en la badge del README. Lo que importa
                                    # es que no baje.
python tests/test_motor.py          # anti-look-ahead, en las tres fechas
```

Reporta la salida tal cual, incluidos los warnings. `Pandas4Warning` en
`motor.py:215` y en `api/main.py:666-668` es **deuda declarada y esperada**:
está contenida por el pin `pandas==3.0.3` en las dos máquinas. No la arregles.
Es bloqueador explícito de cualquier upgrade de pandas, no un pendiente de hoy.

## Gate de entorno

```bash
python --version                                    # 3.14.4 en el PC
python -c "import pandas,numpy,scipy,sklearn; print(pandas.__version__, numpy.__version__)"
ls -la .env && stat -c '%a' .env                    # debe decir 600
cat .python-version
git status --porcelain                              # limpio; ni .db ni logs
git branch --show-current                           # main
echo "MKI_MODO=${MKI_MODO:-<no definido>}"          # decide si esta maquina emite
```

Referencia del Mac: Python 3.11.15. La asimetría de intérprete está declarada
y decidida: no se iguala. Las librerías del álgebra sí son idénticas.

## GATE A-bis, arranque en frío

Este no se simula. Es manual y estricto:

1. Reiniciar el PC.
2. **No** iniciar sesión.
3. Esperar 3 minutos en la pantalla de bloqueo.
4. Recién ahí entrar, y mirar el `Last Run Time` de la tarea
   `MKI-WSL-KeepAlive` y `systemctl --user list-timers 'mki-*'`.

Si el `Last Run Time` no muestra una ejecución durante esos 3 minutos, el
keep-alive no está funcionando en frío y los timers no cuentan como instalados.

## Formato del reporte

```
GATE <cuál>   FECHA <fecha>   MÁQUINA <Mac|PC>   RAMA <rama>
COMANDO      : <el comando exacto>
SALIDA       : <literal, sin resumir>
RESULTADO    : APROBADO | REPROBADO
SI REPROBADO : <qué falló y qué bloquea>
```
