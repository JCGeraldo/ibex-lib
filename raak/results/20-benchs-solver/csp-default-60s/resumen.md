instancias: 264  configuraciones: default, default+affine_af2, default+affine_raa, default+affine_raa_k6

## Estados por configuracion
| config | INFEASIBLE | KILLED | MEM | NOT_ALL_VALIDATED | SUCCESS | TIME_OUT | terminadas |
|---|---|---|---|---|---|---|---|
| default | 10 | 13 | 1 | 19 | 130 | 91 | 159 |
| default+affine_af2 | 10 | 14 | 1 | 20 | 137 | 82 | 167 |
| default+affine_raa | 10 | 14 | 1 | 20 | 137 | 82 | 167 |
| default+affine_raa_k6 | 10 | 14 | 1 | 20 | 137 | 82 | 167 |

terminadas por todas las configuraciones: 158

## Comparaciones por pares (a / b)
| a | b | ambas terminan | celdas a/b (mg) | cpu a/b (mg) | cpu a/b (mg, >=1 s) | a menos celdas | igual | b menos celdas | solo a termina | solo b termina |
|---|---|---|---|---|---|---|---|---|---|---|
| default+affine_af2 | default | 158 | 0.672 | 0.902 | 0.807 (n=87) | 102 | 39 | 17 | 9 | 1 |
<!-- solo default+affine_af2: Bratu-0060 Bratu-0065 Bratu-0070 Discrete-Integral-6 Katsura-20 Trigo1-0014 Trigo1-0015 Trigo1-0016 Trigo1-0017 -->
<!-- solo default: Yamamura1-0040sp -->
| default+affine_raa | default | 158 | 0.667 | 0.894 | 0.795 (n=87) | 102 | 39 | 17 | 9 | 1 |
<!-- solo default+affine_raa: Bratu-0060 Bratu-0065 Bratu-0070 Discrete-Integral-6 Katsura-20 Trigo1-0014 Trigo1-0015 Trigo1-0016 Trigo1-0017 -->
<!-- solo default: Yamamura1-0040sp -->
| default+affine_raa_k6 | default | 158 | 0.667 | 0.904 | 0.799 (n=87) | 102 | 39 | 17 | 9 | 1 |
<!-- solo default+affine_raa_k6: Bratu-0060 Bratu-0065 Bratu-0070 Discrete-Integral-6 Katsura-20 Trigo1-0014 Trigo1-0015 Trigo1-0016 Trigo1-0017 -->
<!-- solo default: Yamamura1-0040sp -->
| default+affine_raa | default+affine_af2 | 167 | 0.993 | 0.992 | 0.987 (n=93) | 7 | 158 | 2 | 0 | 0 |
| default+affine_raa_k6 | default+affine_raa | 167 | 1.000 | 1.010 | 1.003 (n=93) | 4 | 162 | 1 | 0 | 0 |

## Coherencia de soluciones entre configuraciones con SUCCESS
instancias con discrepancia: 0

## Instancias con material k-nomial (bloques > 0 en alguna configuracion)
| instancia | config | estado | celdas | cpu_s | productos | con_bloques |
|---|---|---|---|---|---|---|
| Pramanik | default | SUCCESS | 21285 | 10.38 | 0 | 0 |
| Pramanik | default+affine_af2 | SUCCESS | 5321 | 4.09 | 0 | 0 |
| Pramanik | default+affine_raa | SUCCESS | 2745 | 2.37 | 44019 | 0 |
| Pramanik | default+affine_raa_k6 | SUCCESS | 2719 | 2.42 | 43713 | 21730 |
| Trigexp2-11 | default | INFEASIBLE | 3215 | 8.74 | 0 | 0 |
| Trigexp2-11 | default+affine_af2 | INFEASIBLE | 3175 | 10.57 | 0 | 0 |
| Trigexp2-11 | default+affine_raa | INFEASIBLE | 3173 | 10.66 | 17509 | 0 |
| Trigexp2-11 | default+affine_raa_k6 | INFEASIBLE | 3169 | 10.60 | 18040 | 18007 |
| Trigexp2-13 | default | INFEASIBLE | 7429 | 33.33 | 0 | 0 |
| Trigexp2-13 | default+affine_af2 | INFEASIBLE | 7257 | 38.24 | 0 | 0 |
| Trigexp2-13 | default+affine_raa | INFEASIBLE | 7241 | 38.45 | 48612 | 0 |
| Trigexp2-13 | default+affine_raa_k6 | INFEASIBLE | 7227 | 38.68 | 49972 | 49903 |
| Trigexp2-15 | default | TIME_OUT | 9977 | 60.01 | 0 | 0 |
| Trigexp2-15 | default+affine_af2 | TIME_OUT | 8505 | 60.00 | 0 | 0 |
| Trigexp2-15 | default+affine_raa | TIME_OUT | 8443 | 60.00 | 73131 | 0 |
| Trigexp2-15 | default+affine_raa_k6 | TIME_OUT | 8259 | 60.01 | 73242 | 73166 |
| Trigexp2-17 | default | TIME_OUT | 8201 | 60.01 | 0 | 0 |
| Trigexp2-17 | default+affine_af2 | TIME_OUT | 6941 | 60.01 | 0 | 0 |
| Trigexp2-17 | default+affine_raa | TIME_OUT | 6887 | 60.00 | 78658 | 0 |
| Trigexp2-17 | default+affine_raa_k6 | TIME_OUT | 6785 | 60.01 | 79392 | 79307 |
| Trigexp2-19 | default | TIME_OUT | 7097 | 60.01 | 0 | 0 |
| Trigexp2-19 | default+affine_af2 | TIME_OUT | 5381 | 60.01 | 0 | 0 |
| Trigexp2-19 | default+affine_raa | TIME_OUT | 5527 | 60.01 | 82087 | 0 |
| Trigexp2-19 | default+affine_raa_k6 | TIME_OUT | 5303 | 60.02 | 82654 | 82470 |
| Trigexp2-21 | default | TIME_OUT | 5637 | 60.02 | 0 | 0 |
| Trigexp2-21 | default+affine_af2 | TIME_OUT | 4255 | 60.00 | 0 | 0 |
| Trigexp2-21 | default+affine_raa | TIME_OUT | 4127 | 60.04 | 78652 | 0 |
| Trigexp2-21 | default+affine_raa_k6 | TIME_OUT | 4179 | 60.01 | 87732 | 87528 |
| Trigexp2-23 | default | TIME_OUT | 4525 | 60.01 | 0 | 0 |
| Trigexp2-23 | default+affine_af2 | TIME_OUT | 2865 | 60.02 | 0 | 0 |
| Trigexp2-23 | default+affine_raa | TIME_OUT | 3451 | 60.03 | 79774 | 0 |
| Trigexp2-23 | default+affine_raa_k6 | TIME_OUT | 2665 | 60.02 | 76542 | 76342 |
| Trigexp2-3 | default | TIME_OUT | 158167 | 60.00 | 0 | 0 |
| Trigexp2-3 | default+affine_af2 | TIME_OUT | 78759 | 60.00 | 0 | 0 |
| Trigexp2-3 | default+affine_raa | TIME_OUT | 78031 | 60.00 | 467821 | 0 |
| Trigexp2-3 | default+affine_raa_k6 | TIME_OUT | 77527 | 60.00 | 464852 | 89758 |
| Trigexp2-5 | default | INFEASIBLE | 855 | 0.76 | 0 | 0 |
| Trigexp2-5 | default+affine_af2 | INFEASIBLE | 855 | 0.86 | 0 | 0 |
| Trigexp2-5 | default+affine_raa | INFEASIBLE | 855 | 0.83 | 1658 | 0 |
| Trigexp2-5 | default+affine_raa_k6 | INFEASIBLE | 855 | 0.87 | 1658 | 1652 |
| Trigexp2-7 | default | INFEASIBLE | 1417 | 2.01 | 0 | 0 |
| Trigexp2-7 | default+affine_af2 | INFEASIBLE | 1391 | 2.39 | 0 | 0 |
| Trigexp2-7 | default+affine_raa | INFEASIBLE | 1395 | 2.46 | 4593 | 0 |
| Trigexp2-7 | default+affine_raa_k6 | INFEASIBLE | 1397 | 2.43 | 4575 | 4560 |
| Trigexp2-9 | default | INFEASIBLE | 2365 | 4.65 | 0 | 0 |
| Trigexp2-9 | default+affine_af2 | INFEASIBLE | 2327 | 5.66 | 0 | 0 |
| Trigexp2-9 | default+affine_raa | INFEASIBLE | 2325 | 5.66 | 10422 | 0 |
| Trigexp2-9 | default+affine_raa_k6 | INFEASIBLE | 2317 | 5.68 | 10540 | 10520 |
