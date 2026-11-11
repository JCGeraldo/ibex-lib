instancias: 17  configuraciones: default, default+affine_af2, default+affine_raa, default+affine_raa_k6

## Estados por configuracion
| config | INFEASIBLE | NOT_ALL_VALIDATED | SUCCESS | TIME_OUT | terminadas |
|---|---|---|---|---|---|
| default | 10 | 2 | 4 | 1 | 16 |
| default+affine_af2 | 10 | 2 | 4 | 1 | 16 |
| default+affine_raa | 10 | 1 | 5 | 1 | 16 |
| default+affine_raa_k6 | 10 | 1 | 5 | 1 | 16 |

terminadas por todas las configuraciones: 16

## Comparaciones por pares (a / b)
| a | b | ambas terminan | celdas a/b (mg) | cpu a/b (mg) | cpu a/b (mg, >=1 s) | a menos celdas | igual | b menos celdas | solo a termina | solo b termina |
|---|---|---|---|---|---|---|---|---|---|---|
| default+affine_af2 | default | 16 | 0.884 | 1.133 | 1.114 (n=14) | 11 | 2 | 3 | 0 | 0 |
| default+affine_raa | default | 16 | 0.811 | 1.053 | 1.030 (n=14) | 12 | 2 | 2 | 0 | 0 |
| default+affine_raa_k6 | default | 16 | 0.735 | 0.947 | 0.906 (n=14) | 14 | 2 | 0 | 0 | 0 |
| default+affine_raa | default+affine_af2 | 16 | 0.917 | 0.929 | 0.925 (n=14) | 8 | 3 | 5 | 0 | 0 |
| default+affine_raa_k6 | default+affine_raa | 16 | 0.906 | 0.900 | 0.880 (n=14) | 8 | 6 | 2 | 0 | 0 |

## Coherencia de soluciones entre configuraciones con SUCCESS
instancias con discrepancia: 0

## Instancias con material k-nomial (bloques > 0 en alguna configuracion)
| instancia | config | estado | celdas | cpu_s | productos | con_bloques |
|---|---|---|---|---|---|---|
| Pramanik | default | SUCCESS | 21285 | 10.06 | 0 | 0 |
| Pramanik | default+affine_af2 | SUCCESS | 5321 | 4.03 | 0 | 0 |
| Pramanik | default+affine_raa | SUCCESS | 2745 | 2.24 | 44019 | 0 |
| Pramanik | default+affine_raa_k6 | SUCCESS | 2719 | 2.28 | 43713 | 21730 |
| Trigexp2-11 | default | INFEASIBLE | 3215 | 6.95 | 0 | 0 |
| Trigexp2-11 | default+affine_af2 | INFEASIBLE | 3175 | 8.30 | 0 | 0 |
| Trigexp2-11 | default+affine_raa | INFEASIBLE | 3173 | 8.39 | 17509 | 0 |
| Trigexp2-11 | default+affine_raa_k6 | INFEASIBLE | 3169 | 8.41 | 18040 | 18007 |
| Trigexp2-13 | default | INFEASIBLE | 7429 | 27.26 | 0 | 0 |
| Trigexp2-13 | default+affine_af2 | INFEASIBLE | 7257 | 33.74 | 0 | 0 |
| Trigexp2-13 | default+affine_raa | INFEASIBLE | 7241 | 36.19 | 48612 | 0 |
| Trigexp2-13 | default+affine_raa_k6 | INFEASIBLE | 7227 | 36.61 | 49972 | 49903 |
| Trigexp2-15 | default | INFEASIBLE | 10865 | 65.10 | 0 | 0 |
| Trigexp2-15 | default+affine_af2 | INFEASIBLE | 11657 | 87.07 | 0 | 0 |
| Trigexp2-15 | default+affine_raa | INFEASIBLE | 11793 | 87.89 | 99783 | 0 |
| Trigexp2-15 | default+affine_raa_k6 | INFEASIBLE | 10547 | 76.86 | 91636 | 91560 |
| Trigexp2-17 | default | INFEASIBLE | 18701 | 149.26 | 0 | 0 |
| Trigexp2-17 | default+affine_af2 | INFEASIBLE | 16379 | 152.35 | 0 | 0 |
| Trigexp2-17 | default+affine_raa | INFEASIBLE | 17489 | 170.15 | 189808 | 0 |
| Trigexp2-17 | default+affine_raa_k6 | INFEASIBLE | 9305 | 93.40 | 106948 | 106853 |
| Trigexp2-19 | default | INFEASIBLE | 15495 | 146.38 | 0 | 0 |
| Trigexp2-19 | default+affine_af2 | INFEASIBLE | 19111 | 227.27 | 0 | 0 |
| Trigexp2-19 | default+affine_raa | INFEASIBLE | 20419 | 239.79 | 285111 | 0 |
| Trigexp2-19 | default+affine_raa_k6 | INFEASIBLE | 9261 | 106.93 | 134909 | 134648 |
| Trigexp2-21 | default | INFEASIBLE | 34993 | 382.00 | 0 | 0 |
| Trigexp2-21 | default+affine_af2 | INFEASIBLE | 33503 | 492.66 | 0 | 0 |
| Trigexp2-21 | default+affine_raa | INFEASIBLE | 34731 | 518.97 | 656046 | 0 |
| Trigexp2-21 | default+affine_raa_k6 | INFEASIBLE | 33829 | 503.20 | 661769 | 633485 |
| Trigexp2-23 | default | TIME_OUT | 68001 | 900.00 | 0 | 0 |
| Trigexp2-23 | default+affine_af2 | TIME_OUT | 50573 | 900.00 | 0 | 0 |
| Trigexp2-23 | default+affine_raa | TIME_OUT | 52745 | 900.02 | 1128768 | 0 |
| Trigexp2-23 | default+affine_raa_k6 | TIME_OUT | 48437 | 900.02 | 1114749 | 975906 |
| Trigexp2-3 | default | NOT_ALL_VALIDATED | 1161369 | 428.64 | 0 | 0 |
| Trigexp2-3 | default+affine_af2 | NOT_ALL_VALIDATED | 1161513 | 830.79 | 0 | 0 |
| Trigexp2-3 | default+affine_raa | NOT_ALL_VALIDATED | 1159985 | 764.66 | 6955501 | 0 |
| Trigexp2-3 | default+affine_raa_k6 | NOT_ALL_VALIDATED | 1160847 | 709.66 | 6961026 | 1326527 |
| Trigexp2-5 | default | INFEASIBLE | 855 | 0.65 | 0 | 0 |
| Trigexp2-5 | default+affine_af2 | INFEASIBLE | 855 | 0.76 | 0 | 0 |
| Trigexp2-5 | default+affine_raa | INFEASIBLE | 855 | 0.74 | 1658 | 0 |
| Trigexp2-5 | default+affine_raa_k6 | INFEASIBLE | 855 | 0.82 | 1658 | 1652 |
| Trigexp2-7 | default | INFEASIBLE | 1417 | 1.91 | 0 | 0 |
| Trigexp2-7 | default+affine_af2 | INFEASIBLE | 1391 | 2.24 | 0 | 0 |
| Trigexp2-7 | default+affine_raa | INFEASIBLE | 1395 | 2.44 | 4593 | 0 |
| Trigexp2-7 | default+affine_raa_k6 | INFEASIBLE | 1397 | 2.64 | 4575 | 4560 |
| Trigexp2-9 | default | INFEASIBLE | 2365 | 5.24 | 0 | 0 |
| Trigexp2-9 | default+affine_af2 | INFEASIBLE | 2327 | 6.13 | 0 | 0 |
| Trigexp2-9 | default+affine_raa | INFEASIBLE | 2325 | 6.07 | 10422 | 0 |
| Trigexp2-9 | default+affine_raa_k6 | INFEASIBLE | 2317 | 5.65 | 10540 | 10520 |
