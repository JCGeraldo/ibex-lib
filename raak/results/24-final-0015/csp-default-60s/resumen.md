instancias: 264  configuraciones: default, default+affine_af2, default+affine_raa, default+affine_raa_k6

## Estados por configuracion
| config | INFEASIBLE | KILLED | MEM | NOT_ALL_VALIDATED | SUCCESS | TIME_OUT | terminadas |
|---|---|---|---|---|---|---|---|
| default | 11 | 13 | 1 | 20 | 130 | 89 | 161 |
| default+affine_af2 | 10 | 14 | 1 | 20 | 138 | 81 | 168 |
| default+affine_raa | 10 | 14 | 1 | 20 | 138 | 81 | 168 |
| default+affine_raa_k6 | 10 | 14 | 1 | 20 | 138 | 81 | 168 |

terminadas por todas las configuraciones: 159

## Comparaciones por pares (a / b)
| a | b | ambas terminan | celdas a/b (mg) | cpu a/b (mg) | cpu a/b (mg, >=1 s) | a menos celdas | igual | b menos celdas | solo a termina | solo b termina |
|---|---|---|---|---|---|---|---|---|---|---|
| default+affine_af2 | default | 159 | 0.672 | 0.901 | 0.795 (n=87) | 103 | 39 | 17 | 9 | 2 |
<!-- solo default+affine_af2: Bratu-0060 Bratu-0065 Bratu-0070 Discrete-Integral-6 Trigo1-0014 Trigo1-0015 Trigo1-0016 Trigo1-0017 Yamamua1-0014 -->
<!-- solo default: Trigexp2-15 Yamamura1-0040sp -->
| default+affine_raa | default | 159 | 0.667 | 0.896 | 0.789 (n=87) | 103 | 39 | 17 | 9 | 2 |
<!-- solo default+affine_raa: Bratu-0060 Bratu-0065 Bratu-0070 Discrete-Integral-6 Trigo1-0014 Trigo1-0015 Trigo1-0016 Trigo1-0017 Yamamua1-0014 -->
<!-- solo default: Trigexp2-15 Yamamura1-0040sp -->
| default+affine_raa_k6 | default | 159 | 0.667 | 0.898 | 0.790 (n=87) | 103 | 39 | 17 | 9 | 2 |
<!-- solo default+affine_raa_k6: Bratu-0060 Bratu-0065 Bratu-0070 Discrete-Integral-6 Trigo1-0014 Trigo1-0015 Trigo1-0016 Trigo1-0017 Yamamua1-0014 -->
<!-- solo default: Trigexp2-15 Yamamura1-0040sp -->
| default+affine_raa | default+affine_af2 | 168 | 0.993 | 0.995 | 0.992 (n=91) | 7 | 159 | 2 | 0 | 0 |
| default+affine_raa_k6 | default+affine_raa | 168 | 1.000 | 1.002 | 1.002 (n=91) | 4 | 163 | 1 | 0 | 0 |

## Coherencia de soluciones entre configuraciones con SUCCESS
instancias con discrepancia: 0

## Instancias con material k-nomial (bloques > 0 en alguna configuracion)
| instancia | config | estado | celdas | cpu_s | productos | con_bloques |
|---|---|---|---|---|---|---|
| Pramanik | default | SUCCESS | 21285 | 9.40 | 0 | 0 |
| Pramanik | default+affine_af2 | SUCCESS | 5321 | 3.81 | 0 | 0 |
| Pramanik | default+affine_raa | SUCCESS | 2745 | 2.04 | 44019 | 0 |
| Pramanik | default+affine_raa_k6 | SUCCESS | 2719 | 2.28 | 43722 | 22194 |
| Trigexp2-11 | default | INFEASIBLE | 3215 | 7.58 | 0 | 0 |
| Trigexp2-11 | default+affine_af2 | INFEASIBLE | 3175 | 9.06 | 0 | 0 |
| Trigexp2-11 | default+affine_raa | INFEASIBLE | 3173 | 9.01 | 17509 | 0 |
| Trigexp2-11 | default+affine_raa_k6 | INFEASIBLE | 3169 | 8.90 | 18040 | 18040 |
| Trigexp2-13 | default | INFEASIBLE | 7429 | 28.37 | 0 | 0 |
| Trigexp2-13 | default+affine_af2 | INFEASIBLE | 7257 | 32.43 | 0 | 0 |
| Trigexp2-13 | default+affine_raa | INFEASIBLE | 7241 | 31.82 | 48612 | 0 |
| Trigexp2-13 | default+affine_raa_k6 | INFEASIBLE | 7227 | 32.39 | 49972 | 49972 |
| Trigexp2-15 | default | INFEASIBLE | 10865 | 57.13 | 0 | 0 |
| Trigexp2-15 | default+affine_af2 | TIME_OUT | 9717 | 60.01 | 0 | 0 |
| Trigexp2-15 | default+affine_raa | TIME_OUT | 9643 | 60.00 | 82758 | 0 |
| Trigexp2-15 | default+affine_raa_k6 | TIME_OUT | 9743 | 60.01 | 84639 | 84639 |
| Trigexp2-17 | default | TIME_OUT | 9517 | 60.00 | 0 | 0 |
| Trigexp2-17 | default+affine_af2 | TIME_OUT | 8009 | 60.00 | 0 | 0 |
| Trigexp2-17 | default+affine_raa | TIME_OUT | 7803 | 60.01 | 88340 | 0 |
| Trigexp2-17 | default+affine_raa_k6 | TIME_OUT | 7737 | 60.01 | 89944 | 89944 |
| Trigexp2-19 | default | TIME_OUT | 8049 | 60.00 | 0 | 0 |
| Trigexp2-19 | default+affine_af2 | TIME_OUT | 6331 | 60.00 | 0 | 0 |
| Trigexp2-19 | default+affine_raa | TIME_OUT | 6369 | 60.01 | 92342 | 0 |
| Trigexp2-19 | default+affine_raa_k6 | TIME_OUT | 6275 | 60.01 | 96697 | 96697 |
| Trigexp2-21 | default | TIME_OUT | 6479 | 60.01 | 0 | 0 |
| Trigexp2-21 | default+affine_af2 | TIME_OUT | 4883 | 60.01 | 0 | 0 |
| Trigexp2-21 | default+affine_raa | TIME_OUT | 4723 | 60.04 | 89560 | 0 |
| Trigexp2-21 | default+affine_raa_k6 | TIME_OUT | 4805 | 60.01 | 100096 | 100096 |
| Trigexp2-23 | default | TIME_OUT | 5127 | 60.07 | 0 | 0 |
| Trigexp2-23 | default+affine_af2 | TIME_OUT | 3517 | 60.00 | 0 | 0 |
| Trigexp2-23 | default+affine_raa | TIME_OUT | 4185 | 60.01 | 92728 | 0 |
| Trigexp2-23 | default+affine_raa_k6 | TIME_OUT | 3425 | 60.00 | 93212 | 93212 |
| Trigexp2-3 | default | TIME_OUT | 188673 | 60.00 | 0 | 0 |
| Trigexp2-3 | default+affine_af2 | TIME_OUT | 93781 | 60.00 | 0 | 0 |
| Trigexp2-3 | default+affine_raa | TIME_OUT | 92713 | 60.00 | 555874 | 0 |
| Trigexp2-3 | default+affine_raa_k6 | TIME_OUT | 91299 | 60.00 | 547433 | 547433 |
| Trigexp2-5 | default | INFEASIBLE | 855 | 0.64 | 0 | 0 |
| Trigexp2-5 | default+affine_af2 | INFEASIBLE | 855 | 0.70 | 0 | 0 |
| Trigexp2-5 | default+affine_raa | INFEASIBLE | 855 | 0.75 | 1658 | 0 |
| Trigexp2-5 | default+affine_raa_k6 | INFEASIBLE | 855 | 0.75 | 1658 | 1658 |
| Trigexp2-7 | default | INFEASIBLE | 1417 | 1.71 | 0 | 0 |
| Trigexp2-7 | default+affine_af2 | INFEASIBLE | 1391 | 2.05 | 0 | 0 |
| Trigexp2-7 | default+affine_raa | INFEASIBLE | 1395 | 1.95 | 4593 | 0 |
| Trigexp2-7 | default+affine_raa_k6 | INFEASIBLE | 1397 | 1.98 | 4575 | 4575 |
| Trigexp2-9 | default | INFEASIBLE | 2365 | 4.08 | 0 | 0 |
| Trigexp2-9 | default+affine_af2 | INFEASIBLE | 2327 | 4.87 | 0 | 0 |
| Trigexp2-9 | default+affine_raa | INFEASIBLE | 2325 | 4.80 | 10422 | 0 |
| Trigexp2-9 | default+affine_raa_k6 | INFEASIBLE | 2317 | 4.85 | 10540 | 10540 |
