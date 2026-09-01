# ESTADO

Resumen curado de dónde está el proyecto. Se regenera al cierre de cada sesión
con la skill `/cierre-sesion`. **Máximo 50 líneas.** No es historia: la historia
vive en `DECISIONES.md`. Las cifras publicadas viven en `README.md`.

**Actualizado:** 1-sep-2026 (quinta corrida, dos tandas) · verificar con `orientador`

## Producción

- **Titular: este PC (Windows/WSL), en `main`.** 6 timers activos, emite. Al
  modo se le **pregunta a `modo.py`**.
- Modelo 4.6.0 congelado. Último sello: 2026-08-31.
- **Réplica: piezas listas, nada activado.** Falta una firma: quién gana ante
  divergencia. Ver `GEMELO/resultados/espera_firma.md`.

## Las cuatro reglas de la casa

1. Una verificación con el mismo mecanismo que produjo la cifra **no es una
   verificación**.
2. Una retractación en prosa no es una retractación: **la corrección va al
   ejecutable antes que al texto**.
3. **Ningún estimador puntual sin intervalo**, y el intervalo se computa.
4. **Un número retirado que sigue ofrecido en el código vuelve a circular** —
   se retira también de defaults, constantes y firmas de función.

## Lo que la quinta corrida estableció

- **La ventana sellada no alcanza para juzgar nada.** n efectivo **67**, no
  238 (ICC ~0,39, DEFF ~3,6). Toda su información discriminante es un
  **10-6 en 17 días**. **0 de 192 celdas** de la matriz de bifurcaciones dan
  p < 0,05 con inferencia de clúster.
- **Cruzar α no es tener evidencia.** Con la regla de deduplicación firmada la
  ventaja es +9,7 pp con p=0,0451 — **pero su IC95 de clúster es
  [−7,2, +26,5]**. McNemar cruza porque supone independencia que no hay.
- **La ventaja NO está concentrada: está más dispersa que el azar.** Sobre
  2.030 fechas, el 100% del neto vive en el 16,5% de ellas contra 0,64% bajo
  la nula. **Julio no es de otra especie**: 157 bloques históricos iguales o
  mejores.
- **El gap existe (69% direccional) y no es capturable**: la cartera pierde
  40,7% sin un solo punto básico de costo.
- **R3 quedó LIMPIO.** Las dos fugas del arnés, corregidas con contraprueba
  que dispara 10/10. **El holdout sigue intacto y sin gastar.**

## Gatillo de la Etapa 5.1

**NO se releva.** Se espera al **25-oct-2026** (condición b, se cumple sola).
Relevar la (a) habiendo visto que N se cumple y el régimen no sería mover un
criterio congelado después de mirar.

## Deuda con modo de falla activo

`snapshot.py:140` calcula `sesion_objetivo` con el reloj de pared: **25 filas
históricas afectadas** y **sigue ocurriendo**. Parche listo con test y
declaración del corte de método en `GEMELO/resultados/parche_snapshot140.md`.

## Esperando decisión

**`GEMELO/resultados/espera_firma.md`** — un solo documento, resoluble en una
sentada. Detrás está `cola_decisiones.md` con los 16 ítems y su costo de
postergar.

## Siguiente paso

`git push origin main` (lo hace Nicolás, tras revisar el diff).
