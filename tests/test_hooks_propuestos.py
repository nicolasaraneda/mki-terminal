"""Los hooks del bundle de agentes v2 (2-sep-2026), YA INSTALADOS por Nicolás
con `bash GEMELO/propuestas/hooks/instalar.sh`. Hasta la instalación este
archivo comparaba propuesta contra vigente con `>`; instalada la propuesta los
dos archivos son idénticos y esa comparación no puede sostenerse. Lo que se
verifica ahora es el estado post-instalación:

1. La propuesta está APLICADA: ninguna línea de `GEMELO/propuestas/hooks/`
   falta en el hook vigente de `.claude/hooks/` (la propuesta se conserva como
   registro de qué se instaló, y sigue siendo lo que el instalador copia).
2. El hook VIGENTE contiene el bloque nuevo, por su marca: el bloque 8 en
   `guardia-reglas.py`, el bloque de arranque en `contexto-mki.sh`.
3. El comportamiento se prueba contra el hook VIGENTE, que es el que ahora
   guarda de verdad: el bloque 8 deniega una reintroducción de cifra retirada
   en un .py y en un .md, la deja pasar con marca de retiro, exime el registro
   y los casos de regresión de agentes, y las reglas viejas siguen en pie.

Los tests corren el hook como subproceso con su mismo contrato (JSON por
stdin, exit 2 = denegado, exit 0 = pasa)."""
import json
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROP = os.path.join(RAIZ, "GEMELO", "propuestas", "hooks")
VIG = os.path.join(RAIZ, ".claude", "hooks")

# Marca por la que se reconoce el bloque nuevo dentro del hook vigente.
MARCAS = {
    "guardia-reglas.py": ("BLOQUE 8 (bundle v2): cifras retiradas",
                          "fin del bloque 8"),
    "contexto-mki.sh": ("BLOQUE NUEVO (bundle v2, 2-sep-2026)",
                        "fin del bloque nuevo"),
}


def _correr(tool_name: str, tool_input: dict) -> int:
    """Corre el hook VIGENTE, que es el instalado y el que guarda."""
    p = subprocess.run([sys.executable, os.path.join(VIG, "guardia-reglas.py")],
                       input=json.dumps({"tool_name": tool_name, "tool_input": tool_input}),
                       capture_output=True, text=True, cwd=RAIZ,
                       env={**os.environ, "CLAUDE_PROJECT_DIR": RAIZ})
    return p.returncode


@pytest.mark.parametrize("archivo", ["guardia-reglas.py", "contexto-mki.sh"])
def test_la_propuesta_esta_aplicada(archivo):
    vigente = open(os.path.join(VIG, archivo), encoding="utf-8").read().splitlines()
    propuesta = open(os.path.join(PROP, archivo), encoding="utf-8").read().splitlines()
    faltan = [l for l in propuesta if l not in vigente]
    assert not faltan, f"líneas de la propuesta que el hook vigente no tiene: {faltan[:5]}"
    assert len(vigente) >= len(propuesta)


@pytest.mark.parametrize("archivo", ["guardia-reglas.py", "contexto-mki.sh"])
def test_el_hook_vigente_contiene_el_bloque_nuevo(archivo):
    vigente = open(os.path.join(VIG, archivo), encoding="utf-8").read()
    for marca in MARCAS[archivo]:
        assert marca in vigente, f"falta la marca del bloque nuevo en {archivo}: {marca}"


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


def test_las_reglas_vigentes_siguen_en_pie():
    assert _correr("Edit", {"file_path": "motor.py", "old_string": "a", "new_string": "b"}) == 2
    assert _correr("Bash", {"command": "git " + "push origin main"}) == 2
