# M2, recomputado sobre la cuenta v2 — las cuatro lecturas, sin elegir una

**PROPUESTA — hasta el dictamen del estadistico-adversario sobre el §43 (corrida 12).** Generado 2026-09-09T03:33:15.067482+00:00. M2 recomputado sobre la cuenta en papel v2 (sin fuga demostrada, gate INVARIANTE), señal sin información, arancel del §40 (PROPUESTA), K semillas del sorteo. Ninguna cifra de la v1 RETIRADA se usa.

Umbral M2: 25 % del capital aportado, **sin unidad de período declarada** (dictamen §43). Deslizamiento 5 pb, **NO incluido** en las lecturas `pct_a_*` (sí en `pct_con_deslizamiento_*`; si cuenta para M2 sigue sin firma). K = 20 semillas. **Una sola trayectoria de mercado**: la banda entre semillas no cubre la variación de mercado. Denominador: 500 USD en 5 aportes que terminan el 2023-10-02; **el denominador NO crece y el numerador es un flujo**, así que `pct_a_h` es proporcional a h. Juego por defecto: conservador (reglas.json 0.2.0-PROPUESTA, SIN FIRMA).

## Lectura primaria: tasa anualizada (suma aritmética v × 52/h), la única invariante al período

| juego | anualizada desde 52 | desde 104 | desde 156 |
|---|---|---|---|
| conservador | 3.9 % [3.56, 4.58] (mín–máx [3.5, 4.69]) | 4.3 % [3.17, 4.69] (mín–máx [3.13, 4.75]) | 4.1 % [2.12, 4.37] (mín–máx [2.09, 4.37]) |
| medio | 9.4 % [8.23, 10.82] (mín–máx [8.14, 11.18]) | 9.4 % [7.28, 10.2] (mín–máx [7.03, 10.28]) | 8.9 % [4.86, 9.51] (mín–máx [4.69, 9.73]) |
| agresivo | 6.4 % [5.77, 7.78] (mín–máx [5.66, 7.83]) | 6.2 % [5.81, 6.94] (mín–máx [5.76, 7.01]) | 6.2 % [5.91, 6.63] (mín–máx [5.81, 6.64]) |

## Las lecturas acumuladas, con cuántas semillas cruzan el 25 % en CADA horizonte

| juego | a 52 semanas | cruzan | a 104 | cruzan | a 156 (corte exacto, no vida entera) | cruzan | congeladas antes de 156 | peor ventana móvil de 52 | con deslizamiento a 156 |
|---|---|---|---|---|---|---|---|---|---|
| conservador | 3.9 % [3.56, 4.58] (mín–máx [3.5, 4.69]) | 0 de 20 | 8.6 % [6.35, 9.38] (mín–máx [6.26, 9.5]) | 0 de 20 | 12.4 % [6.35, 13.1] (mín–máx [6.26, 13.1]) | 0 de 20 | 5 | 5.0 % [4.63, 5.58] (mín–máx [4.6, 5.76]) | 13.7 % [7.04, 14.51] (mín–máx [6.95, 14.51]) |
| medio | 9.4 % [8.23, 10.82] (mín–máx [8.14, 11.18]) | 0 de 20 | 18.8 % [14.56, 20.4] (mín–máx [14.06, 20.57]) | 0 de 20 | 26.6 % [14.56, 28.54] (mín–máx [14.06, 29.2]) | 17 de 20 | 3 | 10.1 % [9.64, 11.24] (mín–máx [9.47, 11.48]) | 30.0 % [16.29, 31.95] (mín–máx [15.74, 32.61]) |
| agresivo | 6.4 % [5.77, 7.78] (mín–máx [5.66, 7.83]) | 0 de 20 | 12.4 % [11.62, 13.89] (mín–máx [11.52, 14.02]) | 0 de 20 | 18.7 % [17.73, 19.89] (mín–máx [17.43, 19.93]) | 0 de 20 | 0 | 6.9 % [6.38, 8.0] (mín–máx [6.34, 8.14]) | 22.4 % [21.36, 23.54] (mín–máx [21.08, 23.58]) |

**Período:** NO APLICABLE — la firma §84.4.5 («el horizonte pre-registrado de la vara») invoca un horizonte que el pre-registro no escribe (52 semanas es un piso prospectivo de duración, no una ventana de acumulación de M2); se dispara su propia cláusula de escape y vuelve a espera_firma §43 (dictamen_12/adversario_43_periodo_m2.md)

**Grado de libertad declarado (E12):** se computaron 12 lecturas (3 juegos × 4 períodos) y la firma eligió 1 con los resultados a la vista (E12 del dictamen).

**Semillas congeladas:** una cuenta que dejó de operar (sin caja para una acción entera) acumula poca comisión por quiebra operativa, no por baratura; su lectura de M2 baja por la razón equivocada (E4). La banda p2,5–p97,5 de una mezcla bimodal se lee con el mín–máx al lado.

Intentos del DSR: 0 (la nula es conocida por construcción). Grado de libertad de criterio: registrado en `espera_firma.md` §43 (contador de «lecturas de criterio», ubicación a decidir).
