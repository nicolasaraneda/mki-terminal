"""Los hooks PROPUESTOS del bundle de agentes v2 (2-sep-2026), que viven en
`GEMELO/propuestas/hooks/` hasta que Nicolás los instale a mano:

1. `guardia-reglas.py` propuesto = vigente + bloque 8 (cifras retiradas en
   .md Y en .py): nada del vigente se quita (toda línea del vigente está en
   la propuesta), y el bloque 8 deniega una reintroducción en un .py, la
   deja pasar con marca de retiro, y exime el registro y los casos de
   regresión de agentes.
2. `contexto-mki.sh` propuesto = vigente + un bloque: nada se quita.

Los tests corren la propuesta como subproceso con el mismo contrato del hook
(JSON por stdin, exit 2 = denegado, exit 0 = pasa)."""
import json
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROP = os.path.join(RAIZ, "GEMELO", "propuestas", "hooks")
VIG = os.path.join(RAIZ, ".claude", "hooks")


def _correr(tool_name: str, tool_input: dict) -> int:
    p = subprocess.run([sys.executable, os.path.join(PROP, "guardia-reglas.py")],
                       input=json.dumps({"tool_name": tool_name, "tool_input": tool_input}),
                       capture_output=True, text=True, cwd=RAIZ,
                       env={**os.environ, "CLAUDE_PROJECT_DIR": RAIZ})
    return p.returncode


@pytest.mark.parametrize("archivo", ["guardia-reglas.py", "contexto-mki.sh"])
def test_la_propuesta_solo_agrega(archivo):
    vigente = open(os.path.join(VIG, archivo), encoding="utf-8").read().splitlines()
    propuesta = open(os.path.join(PROP, archivo), encoding="utf-8").read().splitlines()
    faltan = [l for l in vigente if l not in propuesta]
    assert not faltan, f"líneas del hook vigente que la propuesta quita: {faltan[:5]}"
    assert len(propuesta) > len(vigente)


def test_bloque_8_deniega_cifra_retirada_en_py():
    assert _correr("Edit", {"file_path": "backtest/veredicto_51.py", "old_string": "x",
                            "new_string": "# el PSR y el DSR saturan en 1,0000"}) == 2


def test_bloque_8_deniega_cifra_retirada_en_md():
    assert _correr("Write", {"file_path": "README.md",
                             "content": "La ventana larga tiene 8,6% de contaminación."}) == 2


def test_bloque_8_deja_pasar_con_marca_de_retiro():
    assert _correr("Write", {"file_path": "README.md",
                             "content": "Errata: el 8,6% de contaminación era un artefacto del join."}) == 0


def test_bloque_8_exime_registro_y_casos_de_regresion():
    assert _correr("Write", {"file_path": ".claude/tests-agentes/guardian-retirada.md",
                             "content": "saturan en 1,0000"}) == 0
    assert _correr("Write", {"file_path": "GEMELO/cifras_retiradas.md",
                             "content": "| `satura[n]?\\s+en\\s+1[,.]0000` | x | 2026-09-02 | y | z |"}) == 0


def test_bloque_8_no_cubre_otros_sufijos_y_lo_declara():
    """Zona ciega declarada: sólo .md y .py; un .txt o un heredoc por Bash no
    pasan por el bloque 8. El literal de abajo es una cifra retirada puesta a
    propósito (contraprueba), no una reintroducción."""
    assert _correr("Write", {"file_path": "notas.txt", "content": "saturan en 1,0000"}) == 0


def test_las_reglas_vigentes_siguen_en_la_propuesta():
    assert _correr("Edit", {"file_path": "motor.py", "old_string": "a", "new_string": "b"}) == 2
    assert _correr("Bash", {"command": "git " + "push origin main"}) == 2
