# Fase 3, nivel 2 — barrido del solver

Fuente: `runs.csv`: 105 corridas, 15 instancias, limite 1800 s de CPU.

## Relajacion `compo`

### Estados

| variante | NO_FEASIBLE_FOUND | SUCCESS | TIME_OUT | UNBOUNDED_OBJ | CPU total (h) |
|---|---|---|---|---|---|
| compo_aa_k0 | 1 | 8 | 4 | 2 | 2.33 |
| compo_aa_k3 | 1 | 11 | 1 | 2 | 1.06 |
| compo_af2_k0 | 1 | 11 | 1 | 2 | 0.98 |
| compo_af2_k3 | 1 | 11 | 1 | 2 | 0.98 |
| compo_raa_k0 | 1 | 11 | 1 | 2 | 0.97 |
| compo_raa_k3 | 1 | 11 | 1 | 2 | 0.97 |
| xn | 1 | 7 | 5 | 2 | 2.99 |

### Frente a la base `compo_af2_k0` (instancias resueltas por ambas; gana = menos de 0.95x, pierde = mas de 1.05x)

| variante | n | celdas: gana/empata/pierde | celdas media geom. | CPU: gana/empata/pierde | CPU media geom. | resuelve solo esta | resuelve solo la base |
|---|---|---|---|---|---|---|---|
| compo_aa_k0 | 8 | 2/2/4 | 0.992 | 1/3/4 | 1.183 | 0 | 3 |
| compo_aa_k3 | 11 | 3/8/0 | 0.830 | 1/2/8 | 1.001 | 0 | 0 |
| compo_af2_k3 | 11 | 0/11/0 | 0.997 | 1/10/0 | 0.984 | 0 | 0 |
| compo_raa_k0 | 11 | 1/10/0 | 0.830 | 1/10/0 | 0.835 | 0 | 0 |
| compo_raa_k3 | 11 | 1/10/0 | 0.828 | 2/9/0 | 0.824 | 0 | 0 |
| xn | 7 | 0/0/7 | 2.766 | 2/0/5 | 2.089 | 0 | 4 |

### Separacion de efectos

| efecto | comparacion | n | celdas gana/empata/pierde | celdas media geom. | CPU media geom. |
|---|---|---|---|---|---|
| aritmetica | compo_raa_k0 / compo_af2_k0 | 11 | 1/10/0 | 0.830 | 0.835 |
| aritmetica | compo_aa_k0 / compo_af2_k0 | 8 | 2/2/4 | 0.992 | 1.183 |
| k-nomial | compo_af2_k3 / compo_af2_k0 | 11 | 0/11/0 | 0.997 | 0.984 |
| k-nomial | compo_raa_k3 / compo_raa_k0 | 11 | 0/11/0 | 0.997 | 0.986 |
| k-nomial | compo_aa_k3 / compo_aa_k0 | 8 | 4/3/1 | 0.779 | 0.807 |
| total | compo_raa_k3 / compo_af2_k0 | 11 | 1/10/0 | 0.828 | 0.824 |
| total | compo_aa_k3 / compo_af2_k0 | 11 | 3/8/0 | 0.830 | 1.001 |

## Tabla consolidada por instancia (celdas / CPU s; `—` = no resuelta)

| instancia | compo_aa_k0 | compo_aa_k3 | compo_af2_k0 | compo_af2_k3 | compo_raa_k0 | compo_raa_k3 | xn |
|---|---|---|---|---|---|---|---|
| hard/chem | TIME_OUT | 111720 / 485.7 | 111578 / 417.2 | 111578 / 424.8 | 111578 / 422.9 | 111578 / 419.0 | TIME_OUT |
| hard/chem-1 | TIME_OUT | 111720 / 478.0 | 111578 / 418.7 | 111578 / 416.9 | 111578 / 423.1 | 111578 / 421.5 | TIME_OUT |
| hard/chembis | TIME_OUT | 57974 / 223.8 | 57582 / 202.4 | 57582 / 202.2 | 57582 / 202.0 | 57582 / 204.3 | TIME_OUT |
| hard/ex6_1_3 | 9544 / 56.5 | 5982 / 36.7 | 5736 / 32.6 | 5736 / 33.1 | 5736 / 32.9 | 5736 / 32.9 | 23158 / 103.5 |
| hard/ex6_2_10 | 256732 / 781.5 | 139174 / 447.0 | 143026 / 280.9 | 139092 / 279.5 | 143026 / 281.0 | 139092 / 280.1 | 890118 / 1432.0 |
| hard/ex8_5_1bis | 1452 / 4.9 | 1000 / 3.4 | 1006 / 3.1 | 1006 / 3.0 | 1006 / 3.0 | 1006 / 2.9 | 3564 / 7.7 |
| hard/sambal | 49308 / 263.1 | 49308 / 260.7 | 54218 / 268.6 | 54218 / 269.2 | 54218 / 270.3 | 54218 / 274.2 | TIME_OUT |
| others/dualc1 | 1820 / 56.5 | 980 / 34.2 | 1040 / 23.8 | 1040 / 23.9 | 1040 / 24.2 | 1040 / 23.8 | 1816 / 21.6 |
| others/ex14_1_6 | 72 / 0.2 | 72 / 0.2 | 70 / 0.2 | 70 / 0.2 | 70 / 0.2 | 70 / 0.2 | 74 / 0.1 |
| others/ex8_4_5-1 | 2316 / 29.4 | 2486 / 31.9 | 2396 / 28.2 | 2396 / 27.7 | 2396 / 27.6 | 2396 / 28.2 | 13036 / 116.7 |
| others/ex8_4_5bis | 7088 / 9.4 | 7088 / 9.9 | 51412 / 45.7 | 51412 / 45.2 | 6602 / 6.3 | 6602 / 6.1 | 71190 / 66.0 |
| others/polygon25 | TIME_OUT | TIME_OUT | TIME_OUT | TIME_OUT | TIME_OUT | TIME_OUT | TIME_OUT |
| others/ship | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND |
| others/test_infinity3 | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ |
| others/test_infinity4 | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ |
