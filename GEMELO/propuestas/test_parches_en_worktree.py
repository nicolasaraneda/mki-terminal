"""PROPUESTA (corrida 12, 9-sep-2026), NO instalada en la suite — instalarla
es decisión de Nicolás (espera_firma.md).

Lección del `snapshot140.diff` (acta §84.1): un parche a un archivo protegido
aplicaba limpio y sus tests sobre copias pasaban, pero al aplicarse al archivo
real rompió `test_el_camino_de_sellado_no_importa_GEMELO` por dos líneas de
comentario. Este test aplica cada `.diff` de `GEMELO/propuestas/parches/` sobre
un `git worktree` temporal del HEAD y corre ahí los tests de aislamiento (los
que leen el texto de los archivos protegidos), no sólo los del parche.

Por qué no está en la suite: crea un worktree por parche (segundos cada uno,
toca `.git/worktrees`), y un parche YA aplicado (como el §26/§49) falla al
aplicarse sobre HEAD por diseño — hay que saltarlo detectándolo, como hacen
`tests/test_parche_snapshot140.py` y `tests/test_parche_guardia_ancla_temporal.py`.

Uso manual:  venv/bin/python -m pytest GEMELO/propuestas/test_parches_en_worktree.py -q
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARCHES = sorted(glob.glob(os.path.join(RAIZ, "GEMELO", "propuestas", "parches", "*.diff")))
TESTS_AISLAMIENTO = (
    "tests/test_control_lineal.py::test_el_camino_de_sellado_no_importa_GEMELO",
    "tests/test_dinero.py::test_el_camino_de_sellado_no_importa_dinero",
    "tests/test_gemelo_datos.py::test_gemelo_no_importa_el_camino_de_sellado",
)


def _aplica_limpio(worktree: str, diff: str) -> bool:
    r = subprocess.run(["git", "apply", "--check", diff], cwd=worktree, capture_output=True, text=True)
    return r.returncode == 0


@pytest.mark.parametrize("diff", PARCHES, ids=[os.path.basename(p) for p in PARCHES])
def test_el_parche_aplicado_sobre_el_arbol_entero_no_rompe_el_aislamiento(diff):
    tmp = tempfile.mkdtemp(prefix="mki-worktree-")
    wt = os.path.join(tmp, "wt")
    try:
        subprocess.run(["git", "worktree", "add", "--detach", wt, "HEAD"], cwd=RAIZ, check=True,
                       capture_output=True)
        if not _aplica_limpio(wt, diff):
            pytest.skip(f"{os.path.basename(diff)} no aplica sobre HEAD (¿ya aplicado?): se salta, no se fuerza")
        subprocess.run(["git", "apply", diff], cwd=wt, check=True, capture_output=True)
        # los tests de aislamiento leen el TEXTO de los protegidos: corren sobre la copia parcheada
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *TESTS_AISLAMIENTO],
                           cwd=wt, capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, f"{os.path.basename(diff)} rompe el aislamiento al aplicarse al árbol:\n{r.stdout[-2000:]}"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", wt], cwd=RAIZ, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)
