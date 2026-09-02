# Qué puede afirmar MKI Terminal hoy — estado epistémico (2-sep-2026)

**Para quien pregunta «¿y esto qué demuestra?».** MKI es un experimento de
pronóstico: cada tarde, al cierre de Nueva York, un modelo congelado emite
ocho predicciones sobre cómo abrirán ocho acciones de semiconductores en
Seúl, Tokio, Taipéi y Fráncfort, las sella con marca de tiempo antes de que
esos mercados abran, y después las verifica contra lo que pasó. No mueve
dinero. Lo que sigue es cada afirmación del proyecto con su **estatus**:

| estatus | significa |
|---|---|
| **DEMOSTRADA** | verificada por un mecanismo distinto del que la produjo, o por censo (no muestra) |
| **ACOTADA** | medida con intervalo; el intervalo dice lo que se puede y lo que no |
| **CONTESTADA** | el propio proyecto la puso a prueba y la refutó |
| **RETRACTADA** | se publicó, estaba mal, y la corrección está en el ejecutable |
| **NO EVALUABLE** | los datos actuales no permiten decidirla en ninguna dirección |
| **PROPUESTA** | medida esta semana, pendiente de dictamen adversario; no es una afirmación del proyecto |

Ninguna cifra se cita de memoria: cada una tiene su archivo. Las canónicas
viven en `README.md`; las de esta semana, en `GEMELO/resultados/`.

---

## Lo que está DEMOSTRADO

1. **Las predicciones se emiten antes del evento, y eso es verificable.** Cada
   fila lleva `timestamp_utc`, la sesión objetivo y el instante en que su
   insumo era conocible; el verificador descarta toda predicción emitida
   después de la apertura objetivo (`no_verificable_timing`), y ese descarte
   no lo hace el modelo ni el tablero. 276 verificaciones desde julio.
   *(Regla maestra de la Etapa 4.6; `senales.py`.)*
2. **La fuente de precios no reescribió un solo retorno diario en 8 años ×
   27 tickers entre el 26-ago y el 2-sep** (52.507 celdas; 1.953 niveles de
   un solo ticker reescalados por un factor constante, retorno invariante).
   *(Censo, `fuente_canonica.md` §2; verificado por otra ruta en el
   dictamen.)* Vale para ese intervalo, no para siempre.
3. **La magnitud verificada de gap y retorno es estable:** 276/276 filas
   reproducen hoy desde la fuente (5 con ruido en el 4º decimal). *(Censo, id.)*
4. **Lo que el sello guardó del 28-ago es coherente y la fuente ya no lo
   sirve:** dos sellos con 72 h de diferencia implican el mismo cierre que
   hoy no existe. *(Aritmética, acta §69.)*

## Lo que está ACOTADO

5. **Sobre ocho años reconstruidos (n = 14.618), el modelo acierta la
   dirección del gap de apertura +15,66 pp más que "siempre al alza", y la
   ventaja cae con las horas de margen: +19,1 / +16,8 / +15,4 pp en las tres
   bolsas que abren dentro de 3 h, +2,5 pp (p = 0,111) en la que abre a
   8,75 h.** *(`README.md`.)* Es una **reconstrucción** desde la fuente de
   hoy —no un sello— y depende de que esa fuente no mute (punto 2) y de
   una composición de universo que no se pudo verificar (punto 17).
6. **Sobre la ventana sellada —la única evidencia prospectiva— la ventaja
   no se distingue de cero.** Publicado: +6,5 pp, n = 248. Bajo la regla de
   deduplicación firmada: +9,7 pp con **IC95 de clúster de día [−7,2,
   +26,5]**, n efectivo 67 (las ocho filas de un día comparten el mismo
   movimiento del SOX). 0 de 192 formas legítimas de medirla dan p < 0,05
   respetando el clúster. *(Acta §61, `bifurcaciones.md`.)*
7. **El instrumento acumula ~2 observaciones efectivas por día sellado.**
   Detectar 9 pp con potencia 0,80 exige ~250 días sellados, IC95 [109,
   370] (≈ jul-2027); 6,5 pp, ~475 [209, 709]; 5 pp, ~800 [354, 1.199]. El
   veredicto programado del 25-oct llegará con ~73 días y un efecto mínimo
   detectable de 16,6 pp [11,0, 20,3]: **un resultado negativo ese día no será evidencia de
   ausencia.** *(`horizonte_veredicto.md`.)*
8. **La magnitud predicha aporta:** MAE del gap 2,98 pp contra 3,33 de
   predecir cero (n = 248). Los intervalos del 80% cubren el 90,3%: son
   1,84× más anchos de lo necesario. *(`README.md`.)*
9. **Un solo régimen de mercado en toda la ventana sellada.** Todo lo
   anterior sobre esa ventana vale para ese régimen.

## Lo que el proyecto CONTESTÓ (puso a prueba y refutó)

10. **«La ventaja es capturable.»** No. Entrar en la apertura y salir al
    cierre **pierde 40,7% sin un solo punto básico de costo**; con 25 pb por
    lado, −95,6%, contra +137,1% de comprar el ETF del sector. El gap existe;
    el retorno de sesión no lo sigue. *(Acta §59.)*
11. **«Asia toma el relevo de Nueva York hacia Europa.»** No: el SOX pierde
    ~14 pp de ventaja al alejarse y ningún mercado intermedio lo reemplaza.
    *(`relevo_asiatico.md`, pre-registrado y refutado.)*
12. **«Se puede predecir cuándo el modelo funciona.»** Las condiciones que
    parecían predecirlo son la aritmética del propio modelo (β × movimiento
    del SOX). *(`condicional_ventana_larga.md`.)*
13. **«Un modelo con 14 features más lo mejora.»** No detectable: +2,8 pp,
    p = 0,36 sobre lo sellado; el control con la misma información acierta
    en las mismas filas. *(WS2b, `README.md`.)*
14. **«La ventaja sellada está concentrada en julio.»** Está más dispersa
    que el azar; hay 157 bloques históricos iguales o mejores que julio.
    *(Acta §64.)* Pero **R2 —el criterio de rechazo congelado— dispara**: al
    excluir el bloque 15–23 jul la ventaja sellada queda en +2,5 pp con IC95
    de día [−13,6, +19,2] (contiene el cero) sobre el ancla del 31-ago, y en
    −1,0 pp sobre la publicada. *(`horizonte.md`, acta §64.)* **La ventana no
    admite partirse**, en ninguna dirección.

## Lo que se RETRACTÓ

15. **«Cruzar α = 0,05 es tener evidencia.»** Un p de 0,0451 (y 0,0486 al día
    siguiente) se produjo tratando las filas como independientes; con el
    clúster de día el intervalo contiene el cero. El McNemar de filas dejó
    de ser el estadístico principal. *(Actas §61 y §70.)*
16. **«Una predicción sellada es reproducible desde la fuente.»** Nunca se
    afirmó en la portada, pero el backtest lo suponía. Es falso para 16 filas
    (la fuente retiró la sesión del 28-ago) y, en magnitud, para 32 más. El
    sello tiene **«emitido antes»** y no tiene **«reproducible después»**:
    guarda derivados, no insumos. *(`fuente_canonica.md`.)*
17. Dos cifras de auditoría —8,6% de contaminación y 91,4% de coincidencia—
    eran artefactos de una clave de join equivocada; corregidas a 0,00% y
    100% sobre 214 filas, con errata. *(`auditoria_ws3.md`, acta §68.)*

## Lo que NO ES EVALUABLE con los datos actuales

18. **Si el efecto persiste cuando cambie el régimen.** Un régimen, un
    modelo congelado: acumular días responde «¿hubo efecto en este
    régimen?», no «¿hay efecto?».
19. **Si la ventana larga sufre sesgo de supervivencia.** Ningún proveedor
    tasado vende constituyentes históricos del índice.
20. **Si la ventaja sellada existe.** Ver punto 6: no es «no», es «todavía no
    se puede saber», y el punto 7 dice cuándo.

## PROPUESTAS de esta semana (no son afirmaciones del proyecto)

- La ausencia intermitente de una barra del `^SOX` en cuatro noches de
  agosto explica las betas selladas que hoy no reproducen (hipótesis por
  fuerza bruta, única barra de 130, residuo 4–8× el piso; sin testigo
  directo). Dictamen: sigue siendo hipótesis.
- La pendiente de calibración magnitud predicha → realizada sobre lo
  sellado: 1,42 [0,65, 2,19] (contiene 1; excluye 0). Dictamen: entra sólo
  como endpoint secundario pre-registrado contra el control lineal, no
  contra cero.
- **Retirada por el dictamen:** «el decaimiento es −1,6 pp de ventaja por
  hora de margen, IC95 [−2,45, −0,77]». La unidad de replicación del
  mecanismo es la bolsa —cuatro, con dos valores de margen— y con cuatro
  bolsas no se ajusta una curva (`README.md` ya lo decía): p mínimo
  alcanzable 1/13. Queda el escalón por bolsa, no la pendiente.

---

**En una frase, para el que pregunta:** MKI demuestra que un experimento de
pronóstico puede sellarse y auditarse con rigor a costo cero; mide, sobre
ocho años reconstruidos, una propagación real entre husos horarios que se
disipa con el tiempo; demuestra que **no** se puede capturar entrando en la
apertura; y todavía **no** puede confirmar prospectivamente el fenómeno,
porque su ventana sellada es unas siete veces más corta que lo que hace
falta para ver un efecto del tamaño que importa.

*Herramienta de análisis y aprendizaje — no constituye asesoría financiera.*
