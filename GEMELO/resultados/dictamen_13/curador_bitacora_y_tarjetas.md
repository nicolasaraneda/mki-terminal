# Dictamen del `curador-epistemico` — bitácora 13 (bloques 0–3), tarjetas §58–§60 y cabeceras §51–§53/§57 (corrida 13, 19-sep-2026)

**DICTAMEN INICIAL: RECHAZADO** (8 afirmaciones nuevas sin etiqueta de estatus). Qué se hizo con cada hallazgo:

## Bloqueantes (todos aplicados)

1. §58 decía «sello manual a las 21:00 Chile» del 9-sep; el acta §86.4 y la base (`:04` de systemd) dicen timer en 21:00 Santiago. → «(la del 9-sep, con el timer todavía en 21:00 Santiago)».
2. «Contador 7 de 40» circulaba sin la etiqueta obligatoria del §86.2. → «(E0 sella el sorteo sin información: prueba de maquinaria, no track record — §86.2)» en §58 y en la bitácora.
3. Cabecera §53 decía «La hora siguiente se decide con el dato de la sonda»: §86.4 no firmó eso (la regla viene del encargo 13). → «El encargo 13 manda producir el dato de la sonda; elegir la hora siguiente sigue en espera de firma (§58)».
4. Cabecera §52 omitía el grado de libertad declarado (monto fijado después de lo que la regla 5.4 exigía) y «durante la ventana de E2 el monto no se mueve». → añadidos.
5. «Si TOELY se atrasa una de cada nueve, N = 40 tarda ~45 noches»: estimador puntual de 1/9 sin intervalo. → Wilson 95 % [0,02, 0,44] → entre ~41 y ~71 noches (MEDIDO el 1/9, PROPUESTA la proyección).
6. «Yahoo retira retroactivamente sesiones ya publicadas»: (i) no se retiran sesiones, se vacían los cierres (las fechas siguen en el índice); (ii) atribuir a Yahoo desde dos descargas por la MISMA ruta no es verificación. → «MEDIDO: en dos descargas por la misma ruta separadas 24 h, los cierres de TOELY del 08 al 15 pasaron de estar a estar vacíos (n = 1 par, 1 ticker); PROPUESTA: que el borrado ocurra en Yahoo y no en la ruta de descarga no se probó con una segunda vía». Refuerzo independiente desde la base: las filas del 10, 11, 14 y 15 con `cuenta_para_N = 1` exigen 33 de 33 con cierre, así que esos cierres existían al sellar.
7. «El test de integridad habría estado rojo del 10 al 19-sep»: contrafáctico presentado como hecho. → «habría fallado entre el 10-sep 00:30 y el 19-sep 16:12 — inferencia, no ejecución».
8. Bloques 2 y 3 con horas sin `date` y solapadas con el bloque 1. → declarados en paralelo con el bloque 1, sin horas propias.

## Observaciones (aplicadas)

9. «Huellas antes de tocar nada (19:36:56 UTC)» era 16:36:56 −03, después del bloque 0. → «antes de la primera escritura del bloque 1».
10. Dos horas sin procedencia (16:33–16:39 del auditor; 17:02 del test_backtest). → procedencia declarada (duración del agente; misma marca `date` que la aplicación).
11. La cita «§86 líneas 9176–9186» dejaba fuera §86.5. → 9176–9190.
12. Denominadores 36 (extensión) vs 33 (operables sellados) sin declarar en §58. → declarados.
13. TOELY con el mismo cierre `164.55…` el 16 y el 17: candidato a cotización rezagada; presencia no es frescura. → anotado en §58 y en la bitácora.
14. F2 del dictamen del auditor: lo demostrado es el mtime; que el meta cambie de sha en producción es inferencia. → nota fechada anexada al dictamen (no se edita el dictamen).
15. Vocabulario: limpio. 16. Ninguna frase afirma ventaja.

## Zonas ciegas declaradas por el curador

No corrió la suite ni los tests nuevos; no pudo verificar el disco entre el 10 y el 19-sep; las dos descargas del hallazgo TOELY salen de la misma ruta; no revisó el borrador, las ediciones del bloque 2, la sonda ni las unidades; no reverificó el escáner de reintroducciones (es el mismo instrumento que produjo el hallazgo).
