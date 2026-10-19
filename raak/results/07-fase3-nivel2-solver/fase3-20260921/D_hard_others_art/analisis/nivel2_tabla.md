# Fase 3, nivel 2 — barrido del solver

Fuente: `runs.csv`: 90 corridas, 15 instancias, limite 1800 s de CPU.

## Relajacion `art`

### Estados

| variante | NO_FEASIBLE_FOUND | SUCCESS | TIME_OUT | UNBOUNDED_OBJ | CPU total (h) |
|---|---|---|---|---|---|
| art_aa_k0 | 1 | 9 | 3 | 2 | 2.19 |
| art_aa_k3 | 1 | 11 | 1 | 2 | 0.95 |
| art_af2_k0 | 1 | 11 | 1 | 2 | 0.88 |
| art_af2_k3 | 1 | 11 | 1 | 2 | 0.88 |
| art_raa_k0 | 1 | 11 | 1 | 2 | 0.87 |
| art_raa_k3 | 1 | 11 | 1 | 2 | 0.87 |

### Frente a la base `art_af2_k0` (instancias resueltas por ambas; gana = menos de 0.95x, pierde = mas de 1.05x)

| variante | n | celdas: gana/empata/pierde | celdas media geom. | CPU: gana/empata/pierde | CPU media geom. | resuelve solo esta | resuelve solo la base |
|---|---|---|---|---|---|---|---|
| art_aa_k0 | 9 | 2/1/6 | 1.346 | 2/1/6 | 1.628 | 0 | 2 |
| art_aa_k3 | 11 | 2/8/1 | 0.797 | 2/0/9 | 1.014 | 0 | 0 |
| art_af2_k3 | 11 | 0/11/0 | 0.998 | 0/11/0 | 0.998 | 0 | 0 |
| art_raa_k0 | 11 | 1/10/0 | 0.802 | 1/10/0 | 0.824 | 0 | 0 |
| art_raa_k3 | 11 | 1/10/0 | 0.800 | 3/8/0 | 0.807 | 0 | 0 |

### Separacion de efectos

| efecto | comparacion | n | celdas gana/empata/pierde | celdas media geom. | CPU media geom. |
|---|---|---|---|---|---|
| aritmetica | art_raa_k0 / art_af2_k0 | 11 | 1/10/0 | 0.802 | 0.824 |
| aritmetica | art_aa_k0 / art_af2_k0 | 9 | 2/1/6 | 1.346 | 1.628 |
| k-nomial | art_af2_k3 / art_af2_k0 | 11 | 0/11/0 | 0.998 | 0.998 |
| k-nomial | art_raa_k3 / art_raa_k0 | 11 | 0/11/0 | 0.998 | 0.980 |
| k-nomial | art_aa_k3 / art_aa_k0 | 9 | 5/4/0 | 0.563 | 0.606 |
| total | art_raa_k3 / art_af2_k0 | 11 | 1/10/0 | 0.800 | 0.807 |
| total | art_aa_k3 / art_af2_k0 | 11 | 2/8/1 | 0.797 | 1.014 |

## Tabla consolidada por instancia (celdas / CPU s; `—` = no resuelta)

| instancia | art_aa_k0 | art_aa_k3 | art_af2_k0 | art_af2_k3 | art_raa_k0 | art_raa_k3 |
|---|---|---|---|---|---|---|
| hard/chem | TIME_OUT | 112984 / 378.4 | 112836 / 330.4 | 112836 / 328.5 | 112836 / 331.5 | 112836 / 331.2 |
| hard/chem-1 | TIME_OUT | 112984 / 380.7 | 112836 / 332.0 | 112836 / 327.1 | 112836 / 330.1 | 112836 / 332.2 |
| hard/chembis | 548050 / 1433.1 | 58318 / 180.1 | 58306 / 163.1 | 58306 / 162.2 | 58306 / 161.9 | 58306 / 163.5 |
| hard/ex6_1_3 | 11892 / 55.9 | 7320 / 35.3 | 7304 / 32.2 | 7304 / 32.5 | 7304 / 32.4 | 7304 / 32.3 |
| hard/ex6_2_10 | 261322 / 596.0 | 140514 / 354.1 | 144436 / 192.5 | 140514 / 189.7 | 144436 / 194.9 | 140514 / 190.4 |
| hard/ex8_5_1bis | 2094 / 5.2 | 1386 / 3.5 | 1376 / 2.9 | 1376 / 2.9 | 1376 / 3.0 | 1376 / 2.9 |
| hard/sambal | 45640 / 199.3 | 45640 / 198.7 | 53162 / 212.1 | 53162 / 212.3 | 53162 / 212.5 | 53162 / 210.5 |
| others/dualc1 | 6384 / 144.5 | 1546 / 43.9 | 1546 / 31.0 | 1546 / 31.1 | 1546 / 31.0 | 1546 / 29.2 |
| others/ex14_1_6 | 80 / 0.2 | 80 / 0.2 | 80 / 0.2 | 80 / 0.2 | 80 / 0.2 | 80 / 0.1 |
| others/ex8_4_5-1 | 3886 / 29.0 | 3888 / 29.6 | 3658 / 24.3 | 3658 / 23.9 | 3658 / 24.2 | 3658 / 24.1 |
| others/ex8_4_5bis | 7836 / 9.8 | 7836 / 10.2 | 85942 / 54.8 | 85942 / 54.1 | 7600 / 6.2 | 7600 / 6.1 |
| others/polygon25 | TIME_OUT | TIME_OUT | TIME_OUT | TIME_OUT | TIME_OUT | TIME_OUT |
| others/ship | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND | NO_FEASIBLE_FOUND |
| others/test_infinity3 | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ |
| others/test_infinity4 | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ | UNBOUNDED_OBJ |
