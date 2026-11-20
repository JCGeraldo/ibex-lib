instancias: 17  configuraciones: affine_af2, affine_raa, affine_raa_k4, affine_raa_k6, default, default+affine_raa_k6, xn

## Estados por configuracion
| config | INFEASIBLE | NOT_ALL_VALIDATED | SUCCESS | TIME_OUT | terminadas |
|---|---|---|---|---|---|
| affine_af2 | 3 | 1 | 4 | 9 | 8 |
| affine_raa | 3 | 1 | 5 | 8 | 9 |
| affine_raa_k4 | 3 | 1 | 5 | 8 | 9 |
| affine_raa_k6 | 3 | 1 | 5 | 8 | 9 |
| default | 10 | 2 | 4 | 1 | 16 |
| default+affine_raa_k6 | 10 | 1 | 5 | 1 | 16 |
| xn | 1 | 1 | 3 | 12 | 5 |

terminadas por todas las configuraciones: 5

## Comparaciones por pares (a / b)
| a | b | ambas terminan | celdas a/b (mg) | cpu a/b (mg) | cpu a/b (mg, >=1 s) | a menos celdas | igual | b menos celdas | solo a termina | solo b termina |
|---|---|---|---|---|---|---|---|---|---|---|
| affine_raa | affine_af2 | 8 | 0.535 | 0.572 | 0.572 (n=8) | 7 | 1 | 0 | 1 | 0 |
<!-- solo affine_raa: Dietmaier -->
| affine_raa_k4 | affine_raa | 9 | 1.000 | 1.002 | 1.002 (n=9) | 2 | 5 | 2 | 0 | 0 |
| affine_raa_k6 | affine_raa | 9 | 1.000 | 0.990 | 0.990 (n=9) | 2 | 5 | 2 | 0 | 0 |
| affine_raa_k6 | affine_raa_k4 | 9 | 1.000 | 0.988 | 0.988 (n=9) | 0 | 9 | 0 | 0 | 0 |
| affine_raa_k6 | xn | 5 | 0.343 | 0.306 | 0.306 (n=5) | 3 | 0 | 2 | 4 | 0 |
<!-- solo affine_raa_k6: Dietmaier Neveu1 Trigexp2-13sp Trigexp2-7 -->
| default+affine_raa_k6 | default | 16 | 0.730 | 0.935 | 0.910 (n=14) | 14 | 2 | 0 | 0 | 0 |

## Coherencia de soluciones entre configuraciones con SUCCESS
instancias con discrepancia: 0

## Instancias con material k-nomial (bloques > 0 en alguna configuracion)
| instancia | config | estado | celdas | cpu_s | productos | con_bloques |
|---|---|---|---|---|---|---|
| Pramanik | affine_af2 | SUCCESS | 5461 | 1.94 | 0 | 0 |
| Pramanik | affine_raa | SUCCESS | 2761 | 1.27 | 46395 | 0 |
| Pramanik | affine_raa_k4 | SUCCESS | 2737 | 1.27 | 46191 | 23379 |
| Pramanik | affine_raa_k6 | SUCCESS | 2737 | 1.24 | 46191 | 23379 |
| Pramanik | default | SUCCESS | 21285 | 10.33 | 0 | 0 |
| Pramanik | default+affine_raa_k6 | SUCCESS | 2719 | 2.37 | 43722 | 22194 |
| Pramanik | xn | SUCCESS | 27735 | 10.52 | 0 | 0 |
| Trigexp2-11 | affine_af2 | TIME_OUT | 343825 | 900.01 | 0 | 0 |
| Trigexp2-11 | affine_raa | TIME_OUT | 340175 | 900.01 | 6378192 | 0 |
| Trigexp2-11 | affine_raa_k4 | TIME_OUT | 308961 | 900.00 | 6129876 | 6128961 |
| Trigexp2-11 | affine_raa_k6 | TIME_OUT | 308411 | 900.01 | 6118438 | 6117523 |
| Trigexp2-11 | default | INFEASIBLE | 3215 | 6.61 | 0 | 0 |
| Trigexp2-11 | default+affine_raa_k6 | INFEASIBLE | 3169 | 7.97 | 18040 | 18040 |
| Trigexp2-11 | xn | TIME_OUT | 242307 | 900.01 | 0 | 0 |
| Trigexp2-13 | affine_af2 | TIME_OUT | 249467 | 900.01 | 0 | 0 |
| Trigexp2-13 | affine_raa | TIME_OUT | 246057 | 900.00 | 4820639 | 0 |
| Trigexp2-13 | affine_raa_k4 | TIME_OUT | 230173 | 900.01 | 4788069 | 4787851 |
| Trigexp2-13 | affine_raa_k6 | TIME_OUT | 228451 | 900.01 | 4733891 | 4733683 |
| Trigexp2-13 | default | INFEASIBLE | 7429 | 28.23 | 0 | 0 |
| Trigexp2-13 | default+affine_raa_k6 | INFEASIBLE | 7227 | 35.24 | 49972 | 49972 |
| Trigexp2-13 | xn | TIME_OUT | 303757 | 900.03 | 0 | 0 |
| Trigexp2-15 | affine_af2 | TIME_OUT | 161469 | 900.02 | 0 | 0 |
| Trigexp2-15 | affine_raa | TIME_OUT | 157621 | 900.00 | 3604539 | 0 |
| Trigexp2-15 | affine_raa_k4 | TIME_OUT | 158489 | 900.00 | 3680797 | 3680748 |
| Trigexp2-15 | affine_raa_k6 | TIME_OUT | 156485 | 900.00 | 3646641 | 3646592 |
| Trigexp2-15 | default | INFEASIBLE | 10865 | 60.48 | 0 | 0 |
| Trigexp2-15 | default+affine_raa_k6 | INFEASIBLE | 10547 | 70.70 | 91636 | 91636 |
| Trigexp2-15 | xn | TIME_OUT | 184855 | 900.00 | 0 | 0 |
| Trigexp2-17 | affine_af2 | TIME_OUT | 151811 | 900.00 | 0 | 0 |
| Trigexp2-17 | affine_raa | TIME_OUT | 151599 | 900.00 | 3955109 | 0 |
| Trigexp2-17 | affine_raa_k4 | TIME_OUT | 151271 | 900.00 | 3982468 | 3982437 |
| Trigexp2-17 | affine_raa_k6 | TIME_OUT | 151825 | 900.00 | 3999718 | 3999687 |
| Trigexp2-17 | default | INFEASIBLE | 18701 | 135.82 | 0 | 0 |
| Trigexp2-17 | default+affine_raa_k6 | INFEASIBLE | 9305 | 78.04 | 106948 | 106948 |
| Trigexp2-17 | xn | TIME_OUT | 227793 | 900.00 | 0 | 0 |
| Trigexp2-19 | affine_af2 | TIME_OUT | 106663 | 900.00 | 0 | 0 |
| Trigexp2-19 | affine_raa | TIME_OUT | 99961 | 900.00 | 2953870 | 0 |
| Trigexp2-19 | affine_raa_k4 | TIME_OUT | 99471 | 900.01 | 2843989 | 2843769 |
| Trigexp2-19 | affine_raa_k6 | TIME_OUT | 99209 | 900.01 | 2837510 | 2837290 |
| Trigexp2-19 | default | INFEASIBLE | 15495 | 132.50 | 0 | 0 |
| Trigexp2-19 | default+affine_raa_k6 | INFEASIBLE | 9915 | 107.18 | 149054 | 149054 |
| Trigexp2-19 | xn | TIME_OUT | 268391 | 900.00 | 0 | 0 |
| Trigexp2-21 | affine_af2 | TIME_OUT | 90007 | 900.01 | 0 | 0 |
| Trigexp2-21 | affine_raa | TIME_OUT | 92425 | 900.02 | 2408160 | 0 |
| Trigexp2-21 | affine_raa_k4 | TIME_OUT | 87809 | 900.01 | 2226134 | 2225992 |
| Trigexp2-21 | affine_raa_k6 | TIME_OUT | 87473 | 900.01 | 2207204 | 2207062 |
| Trigexp2-21 | default | INFEASIBLE | 34993 | 371.23 | 0 | 0 |
| Trigexp2-21 | default+affine_raa_k6 | INFEASIBLE | 28123 | 417.37 | 548223 | 548223 |
| Trigexp2-21 | xn | TIME_OUT | 149017 | 900.00 | 0 | 0 |
| Trigexp2-23 | affine_af2 | TIME_OUT | 71711 | 900.01 | 0 | 0 |
| Trigexp2-23 | affine_raa | TIME_OUT | 70495 | 900.03 | 2166094 | 0 |
| Trigexp2-23 | affine_raa_k4 | TIME_OUT | 72015 | 900.01 | 2176592 | 2176569 |
| Trigexp2-23 | affine_raa_k6 | TIME_OUT | 71603 | 900.02 | 2156145 | 2156122 |
| Trigexp2-23 | default | TIME_OUT | 69039 | 900.00 | 0 | 0 |
| Trigexp2-23 | default+affine_raa_k6 | TIME_OUT | 50235 | 900.01 | 1192621 | 1192621 |
| Trigexp2-23 | xn | TIME_OUT | 124085 | 900.00 | 0 | 0 |
| Trigexp2-3 | affine_af2 | NOT_ALL_VALIDATED | 1172051 | 697.51 | 0 | 0 |
| Trigexp2-3 | affine_raa | NOT_ALL_VALIDATED | 1171509 | 703.61 | 10476753 | 0 |
| Trigexp2-3 | affine_raa_k4 | NOT_ALL_VALIDATED | 1172101 | 712.14 | 10483349 | 10483349 |
| Trigexp2-3 | affine_raa_k6 | NOT_ALL_VALIDATED | 1172101 | 717.92 | 10483349 | 10483349 |
| Trigexp2-3 | default | NOT_ALL_VALIDATED | 1161369 | 411.78 | 0 | 0 |
| Trigexp2-3 | default+affine_raa_k6 | NOT_ALL_VALIDATED | 1160761 | 858.11 | 6960482 | 6960482 |
| Trigexp2-3 | xn | NOT_ALL_VALIDATED | 993891 | 725.59 | 0 | 0 |
| Trigexp2-5 | affine_af2 | INFEASIBLE | 48597 | 31.96 | 0 | 0 |
| Trigexp2-5 | affine_raa | INFEASIBLE | 48029 | 31.41 | 289333 | 0 |
| Trigexp2-5 | affine_raa_k4 | INFEASIBLE | 47443 | 31.67 | 283499 | 283496 |
| Trigexp2-5 | affine_raa_k6 | INFEASIBLE | 47443 | 31.49 | 283499 | 283496 |
| Trigexp2-5 | default | INFEASIBLE | 855 | 0.64 | 0 | 0 |
| Trigexp2-5 | default+affine_raa_k6 | INFEASIBLE | 855 | 0.80 | 1658 | 1658 |
| Trigexp2-5 | xn | INFEASIBLE | 36685 | 33.51 | 0 | 0 |
| Trigexp2-7 | affine_af2 | INFEASIBLE | 423193 | 476.94 | 0 | 0 |
| Trigexp2-7 | affine_raa | INFEASIBLE | 414047 | 468.61 | 4098091 | 0 |
| Trigexp2-7 | affine_raa_k4 | INFEASIBLE | 421505 | 484.28 | 4265876 | 4265861 |
| Trigexp2-7 | affine_raa_k6 | INFEASIBLE | 421505 | 487.33 | 4265876 | 4265861 |
| Trigexp2-7 | default | INFEASIBLE | 1417 | 1.83 | 0 | 0 |
| Trigexp2-7 | default+affine_raa_k6 | INFEASIBLE | 1397 | 2.22 | 4575 | 4575 |
| Trigexp2-7 | xn | TIME_OUT | 560403 | 900.00 | 0 | 0 |
| Trigexp2-9 | affine_af2 | TIME_OUT | 530345 | 900.00 | 0 | 0 |
| Trigexp2-9 | affine_raa | TIME_OUT | 518273 | 900.00 | 7985571 | 0 |
| Trigexp2-9 | affine_raa_k4 | TIME_OUT | 500829 | 900.00 | 8248975 | 8248492 |
| Trigexp2-9 | affine_raa_k6 | TIME_OUT | 500911 | 900.00 | 8250485 | 8250000 |
| Trigexp2-9 | default | INFEASIBLE | 2365 | 4.24 | 0 | 0 |
| Trigexp2-9 | default+affine_raa_k6 | INFEASIBLE | 2317 | 5.10 | 10540 | 10540 |
| Trigexp2-9 | xn | TIME_OUT | 332739 | 900.01 | 0 | 0 |
