collect-only (árbol real, con los tests nuevos):
Sun Oct 11 21:00:01 -03 2026
1216 tests collected in 1.28s
antes: {'tests_recolectados': 1025, 'plataforma_version': '5.1.0', 'leido_el': '2026-09-29'}
después: {'tests_recolectados': 1216, 'plataforma_version': '5.1.0', 'leido_el': '2026-10-11'}
README.es.md: escrito
README.md: escrito
README.es.md: coincide con el disco
README.md: coincide con el disco
 README.es.md                       |  4 ++--
 README.md                          | 31 ++++++++++++++++++-------------
 docs/readme/badges_congelados.json |  4 ++--
 3 files changed, 22 insertions(+), 17 deletions(-)
=== tsc ===
tsc exit 0
=== test_motor ===
  OK  prediccion_apertura_al(2026-04-14): idéntico con y sin datos futuros
  OK  divergencias_al(2026-04-14): idéntico con y sin datos futuros

RESULTADO: todas las funciones del motor pasan el test de no-contaminación (sin look-ahead bias).
Sun Oct 11 21:00:22 -03 2026
