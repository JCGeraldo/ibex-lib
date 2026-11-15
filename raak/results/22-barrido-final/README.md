# 22 · Barrido final de optimización con el binario riguroso

Una sola sesión, noche del 2026-11-11 (19:30) al 2026-11-12 (05:00), P=10, máquina sin otro uso.
Binario con los parches 0001–0014: cota k-nomial por intervalos (`--knomial_bound=interval`), sin
presupuesto de búsqueda (`--knomial_budget=0`), semilla 42, relajación `art`, 1800 s por corrida.
Lanzado con `scripts/wsl_barrido_final.sh`; análisis con `analysis/barrido_final_analisis.py`
(salida completa en `resumen.md`). Los tiempos de CPU son comparables entre sí dentro de esta sesión.

816 corridas: 136 instancias × 6 variantes (AF2, RAA k=0, 2, 3, 4, 6). Ninguna terminó con un estado
distinto de SUCCESS o TIME_OUT.

| Carpeta | Familia | Instancias |
|---|---|---|
| `reales/` | benchmarks con material (`instancias/reales/`) | 10 |
| `sinteticas/` | `synq`, cuadráticas (n = 3, 5, 8, 10) | 78 |
| `sinteticas-log/` | `synl`, un factor con logaritmo | 24 |
| `sinteticas-fun/` | `synt`, factores con sin, cos, exp | 24 |

## Resultados

**1. Resueltas en 1800 s.**

| familia | instancias | AF2 | RAA k=0 | k=2 | k=3 | k=4 | k=6 |
|---|---|---|---|---|---|---|---|
| benchmarks | 10 | 6 | 6 | 6 | 6 | 6 | 6 |
| synq | 78 | 56 | 60 | 61 | 61 | 61 | 63 |
| synl | 24 | 24 | 24 | 24 | 24 | 24 | 24 |
| synt | 24 | 21 | 23 | 23 | 23 | 23 | 23 |

k=6 resuelve dos `synq` que ninguna otra variante resuelve (`n08_d20_pos_s3` en 1597 s y
`n10_d90_posneg_s2` en 1722 s). No hay ninguna instancia que una variante con k menor resuelva y una
con k mayor no.

**2. Efecto de k frente a RAA k=0** (media geométrica de celdas / CPU, instancias resueltas por las
cinco variantes RAA).

| familia | n | k=2 | k=3 | k=4 | k=6 |
|---|---|---|---|---|---|
| benchmarks | 6 | 0.977 / 0.996 | 0.966 / 0.986 | 0.966 / 0.965 | 0.966 / 0.985 |
| synq | 60 | 0.770 / 0.804 | 0.646 / 0.690 | 0.583 / 0.623 | 0.540 / 0.577 |
| synl | 24 | 0.896 / 0.944 | 0.865 / 0.888 | 0.837 / 0.861 | 0.809 / 0.847 |
| synt | 23 | 0.970 / 0.946 | 0.937 / 0.977 | 0.932 / 0.930 | 0.898 / 0.874 |

Las celdas de las tres primeras columnas reproducen las del barrido del 29-10 (`15-barrido-0009`,
cota sin residuo intervalar): `synq` 0.778, 0.646, 0.588 entonces. La cota rigurosa no cambió el
efecto.

**3. Por número de variables en `synq`** (resueltas por las seis variantes).

| n | resueltas / total | k=2 | k=3 | k=4 | k=6 | k=6 / k=4 |
|---|---|---|---|---|---|---|
| 3 | 18 / 18 | 0.851 / 0.866 | 0.811 / 0.833 | 0.811 / 0.832 | 0.811 / 0.855 | 1.000 / 1.028 |
| 5 | 24 / 24 | 0.737 / 0.765 | 0.594 / 0.647 | 0.543 / 0.590 | 0.527 / 0.563 | 0.971 / 0.953 |
| 8 | 13 / 18 | 0.739 / 0.797 | 0.575 / 0.620 | 0.463 / 0.507 | 0.381 / 0.417 | 0.823 / 0.823 |
| 10 | 1 / 18 | 0.766 / 0.880 | 0.602 / 0.642 | 0.491 / 0.524 | 0.339 / 0.365 | 0.692 / 0.697 |

La ganancia crece con n y con k. Con n = 3 se satura en k = 3; con n = 8, k = 6 explora el 38 % de
las celdas de k = 0. En `synl` y `synt` el patrón es el mismo con menor magnitud (tabla en `resumen.md`).

**4. RAA frente a AF2** (resueltas por ambas): `synq` celdas 0.638, CPU 0.688 (menos celdas en 50 de
56, igual en 6); `synl` 0.860 / 0.867; `synt` 0.878 / 0.935; benchmarks 1.000 / 1.021 (árboles
idénticos). RAA k=6 frente a AF2 en `synq`: celdas 0.355, CPU 0.410.

**5. Monotonía en k.** En `synq`, k=6 nunca explora más celdas que k=4 (menos en 26, igual en 35).
k=4 explora más que k=3 en 2 de 61 (24 contra 22 celdas y 810 contra 806). En `synt` hay dos casos
con diferencia apreciable de k=4 frente a k=3 (`n08_d90_s3` y `n10_d90_s3`, +24 %); en ambas k=6
vuelve a quedar por debajo de k=0. Lista completa en `resumen.md`, sección «Casos con más celdas».

**6. Instancias sin resolver.** En las 15 `synq` que ninguna variante cierra, la cota inferior a los
1800 s es mejor con k=6 que con k=0 en 14 (por ejemplo `n10_d50_pos_s2`: −63.5 con AF2, −50.8 con k=0, −41.6 con
k=6). De los benchmarks, `3pk-borne`, `ex6_2_6`, `mistake` y `s365mod` no cierran con ninguna
variante.

**7. Consistencia.** En las 114 instancias resueltas por al menos dos variantes, los intervalos
[f_lb, f_ub] de todas las variantes se solapan, y ninguna variante sin resolver tiene una cota
inferior por encima del óptimo encontrado por otra. Cero inconsistencias.
