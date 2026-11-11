instancias: 17  configuraciones: affine_af2, affine_raa, affine_raa_k4, affine_raa_k6, default, default+affine_raa_k6, xn

## Estados por configuracion
| config | INFEASIBLE | NOT_ALL_VALIDATED | SUCCESS | TIME_OUT | terminadas |
|---|---|---|---|---|---|
| affine_af2 | 3 | 1 | 4 | 9 | 8 |
| affine_raa | 3 | 1 | 5 | 8 | 9 |
| affine_raa_k4 | 3 | 1 | 5 | 8 | 9 |
| affine_raa_k6 | 3 | 1 | 5 | 8 | 9 |
| default | 10 | 2 | 4 | 1 | 16 |
| default+affine_raa_k6 | 10 | 0 | 5 | 2 | 15 |
| xn | 1 | 1 | 3 | 12 | 5 |

terminadas por todas las configuraciones: 4

## Comparaciones por pares (a / b)
| a | b | ambas terminan | celdas a/b (mg) | cpu a/b (mg) | cpu a/b (mg, >=1 s) | a menos celdas | igual | b menos celdas | solo a termina | solo b termina |
|---|---|---|---|---|---|---|---|---|---|---|
| affine_raa | affine_af2 | 8 | 0.535 | 0.581 | 0.581 (n=8) | 7 | 1 | 0 | 1 | 0 |
<!-- solo affine_raa: Dietmaier -->
| affine_raa_k4 | affine_raa | 9 | 1.000 | 1.003 | 1.003 (n=9) | 2 | 5 | 2 | 0 | 0 |
| affine_raa_k6 | affine_raa | 9 | 1.000 | 0.971 | 0.971 (n=9) | 2 | 5 | 2 | 0 | 0 |
| default+affine_raa_k6 | default | 15 | 0.720 | 0.885 | 0.858 (n=13) | 13 | 2 | 0 | 0 | 1 |
<!-- solo default: Trigexp2-3 -->
| affine_raa | xn | 5 | 0.345 | 0.321 | 0.321 (n=5) | 3 | 0 | 2 | 4 | 0 |
<!-- solo affine_raa: Dietmaier Neveu1 Trigexp2-13sp Trigexp2-7 -->

## Coherencia de soluciones entre configuraciones con SUCCESS
instancias con discrepancia: 0

## Instancias con material k-nomial (bloques > 0 en alguna configuracion)
| instancia | config | estado | celdas | cpu_s | productos | con_bloques |
|---|---|---|---|---|---|---|
| Pramanik | affine_af2 | SUCCESS | 5461 | 2.13 | 0 | 0 |
| Pramanik | affine_raa | SUCCESS | 2761 | 1.38 | 46395 | 0 |
| Pramanik | affine_raa_k4 | SUCCESS | 2737 | 1.41 | 46191 | 22758 |
| Pramanik | affine_raa_k6 | SUCCESS | 2737 | 1.35 | 46191 | 22758 |
| Pramanik | default | SUCCESS | 21285 | 11.57 | 0 | 0 |
| Pramanik | default+affine_raa_k6 | SUCCESS | 2719 | 2.57 | 43713 | 21730 |
| Pramanik | xn | SUCCESS | 27735 | 11.87 | 0 | 0 |
| Trigexp2-11 | affine_af2 | TIME_OUT | 300417 | 900.00 | 0 | 0 |
| Trigexp2-11 | affine_raa | TIME_OUT | 301427 | 900.00 | 5627608 | 0 |
| Trigexp2-11 | affine_raa_k4 | TIME_OUT | 278411 | 900.01 | 5457379 | 2763721 |
| Trigexp2-11 | affine_raa_k6 | TIME_OUT | 278865 | 900.00 | 5465122 | 2767258 |
| Trigexp2-11 | default | INFEASIBLE | 3215 | 9.23 | 0 | 0 |
| Trigexp2-11 | default+affine_raa_k6 | INFEASIBLE | 3169 | 11.15 | 18040 | 18007 |
| Trigexp2-11 | xn | TIME_OUT | 224409 | 900.00 | 0 | 0 |
| Trigexp2-13 | affine_af2 | TIME_OUT | 217763 | 900.00 | 0 | 0 |
| Trigexp2-13 | affine_raa | TIME_OUT | 217165 | 900.01 | 4044812 | 0 |
| Trigexp2-13 | affine_raa_k4 | TIME_OUT | 207829 | 900.00 | 4107480 | 2716246 |
| Trigexp2-13 | affine_raa_k6 | TIME_OUT | 207413 | 900.01 | 4099668 | 2713069 |
| Trigexp2-13 | default | INFEASIBLE | 7429 | 33.95 | 0 | 0 |
| Trigexp2-13 | default+affine_raa_k6 | INFEASIBLE | 7227 | 39.14 | 49972 | 49903 |
| Trigexp2-13 | xn | TIME_OUT | 285535 | 900.00 | 0 | 0 |
| Trigexp2-15 | affine_af2 | TIME_OUT | 144463 | 900.00 | 0 | 0 |
| Trigexp2-15 | affine_raa | TIME_OUT | 140995 | 900.01 | 3263488 | 0 |
| Trigexp2-15 | affine_raa_k4 | TIME_OUT | 138503 | 900.00 | 3360818 | 2093122 |
| Trigexp2-15 | affine_raa_k6 | TIME_OUT | 137455 | 900.01 | 3341278 | 2073717 |
| Trigexp2-15 | default | INFEASIBLE | 10865 | 67.68 | 0 | 0 |
| Trigexp2-15 | default+affine_raa_k6 | INFEASIBLE | 10547 | 79.33 | 91636 | 91560 |
| Trigexp2-15 | xn | TIME_OUT | 165413 | 900.01 | 0 | 0 |
| Trigexp2-17 | affine_af2 | TIME_OUT | 136875 | 900.00 | 0 | 0 |
| Trigexp2-17 | affine_raa | TIME_OUT | 137973 | 900.01 | 3614862 | 0 |
| Trigexp2-17 | affine_raa_k4 | TIME_OUT | 136327 | 900.01 | 3633581 | 2244702 |
| Trigexp2-17 | affine_raa_k6 | TIME_OUT | 136405 | 900.00 | 3634532 | 2245637 |
| Trigexp2-17 | default | INFEASIBLE | 18701 | 150.65 | 0 | 0 |
| Trigexp2-17 | default+affine_raa_k6 | INFEASIBLE | 9305 | 88.11 | 106948 | 106853 |
| Trigexp2-17 | xn | TIME_OUT | 200971 | 900.01 | 0 | 0 |
| Trigexp2-19 | affine_af2 | TIME_OUT | 90269 | 900.01 | 0 | 0 |
| Trigexp2-19 | affine_raa | TIME_OUT | 85641 | 900.02 | 2731912 | 0 |
| Trigexp2-19 | affine_raa_k4 | TIME_OUT | 82591 | 900.00 | 2685200 | 1563255 |
| Trigexp2-19 | affine_raa_k6 | TIME_OUT | 82689 | 900.01 | 2686276 | 1564317 |
| Trigexp2-19 | default | INFEASIBLE | 15495 | 148.72 | 0 | 0 |
| Trigexp2-19 | default+affine_raa_k6 | INFEASIBLE | 9261 | 112.21 | 134909 | 134648 |
| Trigexp2-19 | xn | TIME_OUT | 244805 | 900.00 | 0 | 0 |
| Trigexp2-21 | affine_af2 | TIME_OUT | 83537 | 900.04 | 0 | 0 |
| Trigexp2-21 | affine_raa | TIME_OUT | 86491 | 900.01 | 2126420 | 0 |
| Trigexp2-21 | affine_raa_k4 | TIME_OUT | 82033 | 900.02 | 1964986 | 1555524 |
| Trigexp2-21 | affine_raa_k6 | TIME_OUT | 82179 | 900.00 | 1968440 | 1558978 |
| Trigexp2-21 | default | INFEASIBLE | 34993 | 412.12 | 0 | 0 |
| Trigexp2-21 | default+affine_raa_k6 | INFEASIBLE | 33829 | 537.94 | 661769 | 633485 |
| Trigexp2-21 | xn | TIME_OUT | 135155 | 900.01 | 0 | 0 |
| Trigexp2-23 | affine_af2 | TIME_OUT | 66223 | 900.00 | 0 | 0 |
| Trigexp2-23 | affine_raa | TIME_OUT | 66109 | 900.00 | 1960384 | 0 |
| Trigexp2-23 | affine_raa_k4 | TIME_OUT | 67593 | 900.02 | 1925282 | 1523007 |
| Trigexp2-23 | affine_raa_k6 | TIME_OUT | 67559 | 900.01 | 1923484 | 1522362 |
| Trigexp2-23 | default | TIME_OUT | 62853 | 900.11 | 0 | 0 |
| Trigexp2-23 | default+affine_raa_k6 | TIME_OUT | 43201 | 900.00 | 1012349 | 921470 |
| Trigexp2-23 | xn | TIME_OUT | 110381 | 900.02 | 0 | 0 |
| Trigexp2-3 | affine_af2 | NOT_ALL_VALIDATED | 1172051 | 772.78 | 0 | 0 |
| Trigexp2-3 | affine_raa | NOT_ALL_VALIDATED | 1171509 | 790.91 | 10476753 | 0 |
| Trigexp2-3 | affine_raa_k4 | NOT_ALL_VALIDATED | 1171837 | 790.70 | 10480970 | 2303958 |
| Trigexp2-3 | affine_raa_k6 | NOT_ALL_VALIDATED | 1171837 | 794.06 | 10480970 | 2303958 |
| Trigexp2-3 | default | NOT_ALL_VALIDATED | 1161369 | 458.08 | 0 | 0 |
| Trigexp2-3 | default+affine_raa_k6 | TIME_OUT | 1098799 | 900.00 | 6588906 | 1255894 |
| Trigexp2-3 | xn | NOT_ALL_VALIDATED | 993891 | 799.53 | 0 | 0 |
| Trigexp2-5 | affine_af2 | INFEASIBLE | 48597 | 36.00 | 0 | 0 |
| Trigexp2-5 | affine_raa | INFEASIBLE | 48029 | 35.91 | 289333 | 0 |
| Trigexp2-5 | affine_raa_k4 | INFEASIBLE | 47459 | 35.95 | 283516 | 281288 |
| Trigexp2-5 | affine_raa_k6 | INFEASIBLE | 47459 | 35.54 | 283516 | 281288 |
| Trigexp2-5 | default | INFEASIBLE | 855 | 0.76 | 0 | 0 |
| Trigexp2-5 | default+affine_raa_k6 | INFEASIBLE | 855 | 0.89 | 1658 | 1652 |
| Trigexp2-5 | xn | INFEASIBLE | 36685 | 37.90 | 0 | 0 |
| Trigexp2-7 | affine_af2 | INFEASIBLE | 423193 | 536.40 | 0 | 0 |
| Trigexp2-7 | affine_raa | INFEASIBLE | 414047 | 524.70 | 4098091 | 0 |
| Trigexp2-7 | affine_raa_k4 | INFEASIBLE | 420907 | 545.83 | 4258048 | 3077810 |
| Trigexp2-7 | affine_raa_k6 | INFEASIBLE | 420907 | 543.74 | 4258048 | 3077810 |
| Trigexp2-7 | default | INFEASIBLE | 1417 | 1.94 | 0 | 0 |
| Trigexp2-7 | default+affine_raa_k6 | INFEASIBLE | 1397 | 2.45 | 4575 | 4560 |
| Trigexp2-7 | xn | TIME_OUT | 496859 | 900.00 | 0 | 0 |
| Trigexp2-9 | affine_af2 | TIME_OUT | 474277 | 900.00 | 0 | 0 |
| Trigexp2-9 | affine_raa | TIME_OUT | 467263 | 900.00 | 7282547 | 0 |
| Trigexp2-9 | affine_raa_k4 | TIME_OUT | 439319 | 900.00 | 7337820 | 3668307 |
| Trigexp2-9 | affine_raa_k6 | TIME_OUT | 436663 | 900.00 | 7304353 | 3653310 |
| Trigexp2-9 | default | INFEASIBLE | 2365 | 4.71 | 0 | 0 |
| Trigexp2-9 | default+affine_raa_k6 | INFEASIBLE | 2317 | 5.76 | 10540 | 10520 |
| Trigexp2-9 | xn | TIME_OUT | 297177 | 900.03 | 0 | 0 |
