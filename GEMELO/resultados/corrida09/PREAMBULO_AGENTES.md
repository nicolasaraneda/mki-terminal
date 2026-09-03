# Reglas para todo agente de la corrida 09 (noche 2→3-sep-2026)

- Repo: /home/nicolasaraneda/dev/mki-terminal, rama `main`, venv en `venv/` (`source venv/bin/activate`).
- Esta máquina (PC/WSL) es el TITULAR: emite y sella. No tocar modo de emisión, `.env`, timers, ni correr `systemctl` con nada que no sea lectura.
- INTOCABLES: `motor.py`, `senales.py`, `snapshot.py`, `universo.py`. Donde haga falta cambiarlos, se produce un `.diff` NO aplicado + test que corre contra una copia parcheada en un directorio temporal (nunca contra el archivo real).
- `senales.db` y `noticias.db` SOLO se leen en `mode=ro` (`sqlite3.connect("file:...?mode=ro", uri=True)`). Ninguna fila sellada se reescribe. Si hay que experimentar sobre una base, se copia a un directorio temporal primero.
- NINGUNA operación de git que escriba (ni commit, ni add, ni publicar, ni traer cambios sobre el árbol). La integración y los commits los hace el orquestador; publicar es de Nicolás.
- NO editar: `README.md`, `DECISIONES.md`, `ESTADO.md`, `CLAUDE.md`, `GEMELO/resultados/{espera_firma,cola_decisiones,estado_epistemico,bitacora_09}.md`, `GEMELO/cifras_retiradas.md`, `cifras.py`, nada bajo `.claude/`. Escribí tus entregables en los archivos que te indica tu encargo; el orquestador los integra.
- Un hook deniega ediciones que reintroduzcan cifras retiradas (`GEMELO/cifras_retiradas.md`) en `.md`/`.py` sin una marca («retirada», «errata», «era», «refutada», «corregida») a ±2 líneas. Si te bloquea, agregá la marca; no lo rodees.
- Ninguna cifra se cita de memoria: se lee del README o se computa. Ningún estimador puntual sin intervalo computado. Si hay más de un ticker por fecha, el intervalo es de clúster de día (`GEMELO/bifurcaciones._bootstrap_dia`, `_p_permutacion_dia`, `_ic_t_cluster`).
- Todo lo nuevo se etiqueta PROPUESTA en el texto. Marcá cada afirmación con su estatus (MEDIDO / PROPUESTA / NO EVALUABLE).
- No descargues nada de la red en ningún caso: no se agrega ninguna fuente de datos.
- Al final de tu informe: (a) lista de archivos creados/modificados, (b) cuántos intentos del DSR consumió tu frente (una hipótesis probada sobre retornos reales = un intento por intervalo publicado; instrumento/simulación = configuraciones nuevas; 0 si nada), (c) qué quedó abierto, (d) errores propios que cometiste y corregiste.
- Horas: si citás una hora, leela de `TZ=America/Santiago date`.
