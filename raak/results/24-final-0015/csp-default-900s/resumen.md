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
| default+affine_af2 | default | 16 | 0.884 | 1.140 | 1.115 (n=14) | 11 | 2 | 3 | 0 | 0 |
| default+affine_raa | default | 16 | 0.811 | 1.057 | 1.023 (n=14) | 12 | 2 | 2 | 0 | 0 |
| default+affine_raa_k6 | default | 16 | 0.730 | 0.936 | 0.904 (n=14) | 14 | 2 | 0 | 0 | 0 |
| default+affine_raa | default+affine_af2 | 16 | 0.917 | 0.927 | 0.918 (n=14) | 8 | 3 | 5 | 0 | 0 |
| default+affine_raa_k6 | default+affine_raa | 16 | 0.900 | 0.886 | 0.883 (n=14) | 8 | 6 | 2 | 0 | 0 |

## Coherencia de soluciones entre configuraciones con SUCCESS
instancias con discrepancia: 0

## Instancias con material k-nomial (bloques > 0 en alguna configuracion)
| instancia | config | estado | celdas | cpu_s | productos | con_bloques |
|---|---|---|---|---|---|---|
| Pramanik | default | SUCCESS | 21285 | 10.33 | 0 | 0 |
| Pramanik | default+affine_af2 | SUCCESS | 5321 | 4.46 | 0 | 0 |
| Pramanik | default+affine_raa | SUCCESS | 2745 | 2.38 | 44019 | 0 |
| Pramanik | default+affine_raa_k6 | SUCCESS | 2719 | 2.40 | 43722 | 22194 |
| Trigexp2-11 | default | INFEASIBLE | 3215 | 6.69 | 0 | 0 |
| Trigexp2-11 | default+affine_af2 | INFEASIBLE | 3175 | 7.98 | 0 | 0 |
| Trigexp2-11 | default+affine_raa | INFEASIBLE | 3173 | 8.23 | 17509 | 0 |
| Trigexp2-11 | default+affine_raa_k6 | INFEASIBLE | 3169 | 8.42 | 18040 | 18040 |
| Trigexp2-13 | default | INFEASIBLE | 7429 | 27.36 | 0 | 0 |
| Trigexp2-13 | default+affine_af2 | INFEASIBLE | 7257 | 31.94 | 0 | 0 |
| Trigexp2-13 | default+affine_raa | INFEASIBLE | 7241 | 33.25 | 48612 | 0 |
| Trigexp2-13 | default+affine_raa_k6 | INFEASIBLE | 7227 | 33.59 | 49972 | 49972 |
| Trigexp2-15 | default | INFEASIBLE | 10865 | 60.09 | 0 | 0 |
| Trigexp2-15 | default+affine_af2 | INFEASIBLE | 11657 | 78.13 | 0 | 0 |
| Trigexp2-15 | default+affine_raa | INFEASIBLE | 11793 | 78.89 | 99783 | 0 |
| Trigexp2-15 | default+affine_raa_k6 | INFEASIBLE | 10547 | 70.04 | 91636 | 91636 |
| Trigexp2-17 | default | INFEASIBLE | 18701 | 135.69 | 0 | 0 |
| Trigexp2-17 | default+affine_af2 | INFEASIBLE | 16379 | 141.30 | 0 | 0 |
| Trigexp2-17 | default+affine_raa | INFEASIBLE | 17489 | 154.85 | 189808 | 0 |
| Trigexp2-17 | default+affine_raa_k6 | INFEASIBLE | 9305 | 79.83 | 106948 | 106948 |
| Trigexp2-19 | default | INFEASIBLE | 15495 | 136.22 | 0 | 0 |
| Trigexp2-19 | default+affine_af2 | INFEASIBLE | 19111 | 214.53 | 0 | 0 |
| Trigexp2-19 | default+affine_raa | INFEASIBLE | 20419 | 224.43 | 285111 | 0 |
| Trigexp2-19 | default+affine_raa_k6 | INFEASIBLE | 9915 | 108.86 | 149054 | 149054 |
| Trigexp2-21 | default | INFEASIBLE | 34993 | 377.46 | 0 | 0 |
| Trigexp2-21 | default+affine_af2 | INFEASIBLE | 33503 | 477.91 | 0 | 0 |
| Trigexp2-21 | default+affine_raa | INFEASIBLE | 34731 | 507.39 | 656046 | 0 |
| Trigexp2-21 | default+affine_raa_k6 | INFEASIBLE | 28123 | 419.07 | 548223 | 548223 |
| Trigexp2-23 | default | TIME_OUT | 68417 | 900.01 | 0 | 0 |
| Trigexp2-23 | default+affine_af2 | TIME_OUT | 51613 | 900.03 | 0 | 0 |
| Trigexp2-23 | default+affine_raa | TIME_OUT | 53193 | 900.02 | 1141776 | 0 |
| Trigexp2-23 | default+affine_raa_k6 | TIME_OUT | 50397 | 900.00 | 1197078 | 1197078 |
| Trigexp2-3 | default | NOT_ALL_VALIDATED | 1161369 | 412.39 | 0 | 0 |
| Trigexp2-3 | default+affine_af2 | NOT_ALL_VALIDATED | 1161513 | 822.94 | 0 | 0 |
| Trigexp2-3 | default+affine_raa | NOT_ALL_VALIDATED | 1159985 | 762.70 | 6955501 | 0 |
| Trigexp2-3 | default+affine_raa_k6 | NOT_ALL_VALIDATED | 1160761 | 721.22 | 6960482 | 6960482 |
| Trigexp2-5 | default | INFEASIBLE | 855 | 0.67 | 0 | 0 |
| Trigexp2-5 | default+affine_af2 | INFEASIBLE | 855 | 0.80 | 0 | 0 |
| Trigexp2-5 | default+affine_raa | INFEASIBLE | 855 | 0.81 | 1658 | 0 |
| Trigexp2-5 | default+affine_raa_k6 | INFEASIBLE | 855 | 0.79 | 1658 | 1658 |
| Trigexp2-7 | default | INFEASIBLE | 1417 | 1.84 | 0 | 0 |
| Trigexp2-7 | default+affine_af2 | INFEASIBLE | 1391 | 2.19 | 0 | 0 |
| Trigexp2-7 | default+affine_raa | INFEASIBLE | 1395 | 2.26 | 4593 | 0 |
| Trigexp2-7 | default+affine_raa_k6 | INFEASIBLE | 1397 | 2.26 | 4575 | 4575 |
| Trigexp2-9 | default | INFEASIBLE | 2365 | 4.31 | 0 | 0 |
| Trigexp2-9 | default+affine_af2 | INFEASIBLE | 2327 | 5.21 | 0 | 0 |
| Trigexp2-9 | default+affine_raa | INFEASIBLE | 2325 | 5.12 | 10422 | 0 |
| Trigexp2-9 | default+affine_raa_k6 | INFEASIBLE | 2317 | 5.36 | 10540 | 10540 |
