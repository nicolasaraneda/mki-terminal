---
paths:
  - "data/**"
  - "*.db"
  - "**/*.sql"
  - "universo.py"
---

# Reglas al tocar datos

- **Las filas selladas jamás se reescriben.** Un error histórico se documenta
  como errata en `DECISIONES.md`. La fila no se toca.
- Ningún `UPDATE`, `DELETE`, `ALTER` ni `to_sql(if_exists='replace')` contra
  snapshots, señales o verificaciones. Está bloqueado por hook, a propósito.
- La base actual es la **cadena canónica**, compuesta de dos fuentes bajo la
  regla de `docs/SOMBRA.md`. Toda cifra que salga de ella **declara su
  procedencia**. Un número sin procedencia, en una base compuesta, es un número
  sin denominador.
- La convención canónica de conteo es **`excluir_cero`**. Las otras dos
  (`estricta`, `verificador`) se reportan como sensibilidad, nunca como la
  cifra principal.
- **Mover una cifra que depende de `n` obliga a mover todas.** Son doce bloques
  y varios dependen de `n`; moverlas a medias es peor que no moverlas. Hay un
  script de barrido para verificar que ninguna cifra invalidada sobrevive.
- Cambiar `universo.py` es **cambio de universo** y mueve `UNIVERSO_VERSION`.
- Yahoo revisa la historia en silencio. Ninguna conclusión fuerte sobre datos
  que no son point-in-time va sin ese caveat.
- Antes y después de tocar bases: `integridad-datos`.
