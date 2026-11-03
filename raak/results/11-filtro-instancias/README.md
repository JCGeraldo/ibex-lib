# Filtro de instancias: donde tienen material RAA y el k-nomial (nivel 1)

Generado por `analysis/filtro_instancias.py` desde `range.csv.gz` (tests/range_eval.cpp, sub-cajas 2, muestras 200) sobre los conjuntos
actuales y las 89 instancias `coconutbenchmark-library2` de la carpeta `All` (no estan en `benchs/optim`; copia local en `~/ibex-local/instancias/coconut`).
Por instancia se promedia (media geometrica) sobre todas las (funcion, caja) donde las seis formas son activas.

| conjunto | instancias | con k-nomial | solo RAA | nada | con k_used>0 (raa k=3) | kn_raa media | raa_vs_af2 media |
|---|---|---|---|---|---|---|---|
| easy | 101 | 0 | 3 | 98 | 13 | 1.000 | 0.996 |
| medium | 31 | 6 | 4 | 21 | 13 | 0.997 | 0.996 |
| hard | 7 | 1 | 0 | 6 | 1 | 0.999 | 1.000 |
| others | 8 | 0 | 1 | 7 | 2 | 1.000 | 0.997 |
| coconut | 89 | 4 | 19 | 66 | 27 | 0.999 | 0.972 |

`kn_raa` = anchura afin con k=3 / con k=0 dentro de RAA (menor es mejor); `raa_vs_af2` = RAA k=0 / AF2 k=0. Clase `knomial`: kn_raa < 0.99 o k-nomial estrecha >1 % en al menos 10 % de las (funcion, caja).

## coconut: instancias con material para el k-nomial (4)

| instancia | kn_raa | frac_kn | k_used raa k=3 | raa_vs_af2 | sobre_raa | vars no acotadas | nivel 2: celdas k3/k0 |
|---|---|---|---|---|---|---|---|
| mistake | 0.957 | 0.36 | 81 | 1.000 | 1.51 | 0 | — |
| 3pk | 0.978 | 0.56 | 243 | 1.000 | 2.15 | 30 | — |
| 3pk-borne | 0.978 | 0.56 | 243 | 1.000 | 2.17 | 0 | — |
| s365mod | 0.998 | 0.11 | 59 | 0.959 | 48.01 | 0 | — |

## medium: instancias con material para el k-nomial (6)

| instancia | kn_raa | frac_kn | k_used raa k=3 | raa_vs_af2 | sobre_raa | vars no acotadas | nivel 2: celdas k3/k0 |
|---|---|---|---|---|---|---|---|
| ex6_2_6 | 0.970 | 0.50 | 18 | 1.000 | 10.80 | 0 | TIME_OUT |
| ex6_2_8 | 0.972 | 0.50 | 18 | 1.000 | 20.91 | 0 | 0.9082 |
| ex6_2_11 | 0.978 | 0.50 | 18 | 1.000 | 9.58 | 0 | 0.9504 |
| ex6_2_9 | 0.992 | 0.30 | 36 | 1.000 | 6.55 | 0 | 0.9776 |
| ex6_2_12 | 0.993 | 0.30 | 18 | 1.000 | 3.15 | 0 | 0.9879 |
| ex6_2_14 | 0.994 | 0.30 | 36 | 1.000 | 2.21 | 0 | 1.0 |

## hard: instancias con material para el k-nomial (1)

| instancia | kn_raa | frac_kn | k_used raa k=3 | raa_vs_af2 | sobre_raa | vars no acotadas | nivel 2: celdas k3/k0 |
|---|---|---|---|---|---|---|---|
| ex6_2_10 | 0.992 | 0.25 | 36 | 1.000 | 2.47 | 0 | 0.9728 |

| archivo | que es |
|---|---|
| `tabla_instancias.csv` | Todas las instancias con los indicadores del nivel 1, el conteo estatico y, para las 147 actuales, el cociente de celdas del nivel 2. |
| `material_por_instancia.png` | Las 40 instancias con mas reduccion de anchura por el k-nomial (barra naranja) y por la RAA (verde), eje lineal. |
| `nivel1_vs_nivel2.png` | Indicador del nivel 1 contra el efecto real en celdas del nivel 2, en las instancias ya corridas en el solver. |
| `range.csv.gz`, `meta.txt`, `range_log.txt` | La corrida del nivel 1 (236 instancias, 6 variantes). |

## Anexo (21-10): `benchs/solver` y clasificacion de objetivos

- `benchs-solver/`: nivel 1 sobre las 231 instancias de satisfaccion de `benchs/solver` (polynom 153, non-polynom 70, others 8), 0 violaciones.
  Con material para el k-nomial: la familia `Trigexp2-*` (11, productos sin(.)*sin(.) de formas afines, kn_raa 0.984-0.990, sobreestimacion enorme por exp
  sobre cajas [-200,200]) y `Pramanik` (polynom, kn_raa 0.991, RAA 0.71 frente a AF2). Solo RAA: `Neveu1`, `ponts-geo`, `Dietmaier`, `Directkin`.
  Son CSP: se resuelven con `ibexsolve`, que no usa la relajacion afin por defecto.
- `clasificacion_objetivos.csv` (`analysis/clasificar_objetivos.py`): clase del objetivo de optim, coconut y sinteticas. En optim, 29 instancias tienen
  objetivo = una variable (forma epigrafo: ex14_1_*, ex14_2_*, ex7_3_*, wall) y 23 lineal; las 11 con material k-nomial tienen todas objetivo no lineal.
