instancias: 264  configuraciones: affine_af2, affine_raa, affine_raa_k6, default, xn

## Estados por configuracion
| config | INFEASIBLE | KILLED | MEM | NOT_ALL_VALIDATED | SUCCESS | TIME_OUT | terminadas |
|---|---|---|---|---|---|---|---|
| affine_af2 | 5 | 14 | 1 | 18 | 71 | 155 | 94 |
| affine_raa | 5 | 14 | 1 | 18 | 73 | 153 | 96 |
| affine_raa_k6 | 5 | 14 | 1 | 18 | 73 | 153 | 96 |
| default | 10 | 12 | 1 | 19 | 130 | 92 | 159 |
| xn | 5 | 12 | 1 | 16 | 65 | 165 | 86 |

terminadas por todas las configuraciones: 75

## Comparaciones por pares (a / b)
| a | b | ambas terminan | celdas a/b (mg) | cpu a/b (mg) | cpu a/b (mg, >=1 s) | a menos celdas | igual | b menos celdas | solo a termina | solo b termina |
|---|---|---|---|---|---|---|---|---|---|---|
| affine_af2 | xn | 75 | 0.618 | 0.526 | 0.526 (n=43) | 37 | 6 | 32 | 19 | 11 |
<!-- solo affine_af2: Brown-12 Brown-15 Brown-18 Brown-20 Brown-20-1 Brown-30sp BroydenTri-0060 Discrete-Integral-6 Discrete-Integralf2-10 Discrete-Integralf2-9 Eiger-0100 Katsura-17 Trigo1-0010 Trigo1-0010m1 Trigo1-0012 Trigo1-0013 Trigo1-0014 Trigo1-0015 Trigo1-0100sp -->
<!-- solo xn: Designsp ExtendedWood-08 Redeco8 Trigexp1-020 Trigexp1-022 Trigexp1-024 Trigexp1-030 Yamamua1-0012 Yamamua1-0022sp Yamamua1-0028sp transistor-icse -->
| affine_raa | affine_af2 | 94 | 0.982 | 0.994 | 0.979 (n=46) | 4 | 90 | 0 | 2 | 0 |
<!-- solo affine_raa: Neveu1 ponts-geo -->
| affine_raa_k6 | affine_raa | 96 | 1.000 | 1.002 | 1.008 (n=49) | 2 | 94 | 0 | 0 | 0 |
| affine_raa | default | 93 | 6.890 | 3.018 | 2.857 (n=50) | 10 | 7 | 76 | 3 | 66 |
<!-- solo affine_raa: Discrete-Integral-6 Trigo1-0014 Trigo1-0015 -->
<!-- solo default: Bratu-0050 Brent-10 Brown-19 BroydenBanded-100 BroydenBanded-120 BroydenBanded-140 BroydenTri-0090 BroydenTri-0100 CountercurrentReactors2-10 CountercurrentReactors2-12 CountercurrentReactors2-14 CountercurrentReactors2-16 CountercurrentReactors2-18 CountercurrentReactors2-6 CountercurrentReactors2-8 CountercurrentReactors2-9 Design Designbis Designsp Discrete-Integralf2-11 Discrete-Integralf2-12 Discrete-Integralf2-13 Discrete-Integralf2-14 Discrete-Integralf2-15 Discrete-Integralf2-16 Discrete-Integralf2-17 Discrete-Integralf2-18 Discrete-Integralf2-19 Discrete-Integralf2-20 Discrete-Integralf2-21 DiscreteBoundary-0100 Eco10 ExtendedFreud-0100 ExtendedWood-08 Geneig I5 I5bis Katsura-18 Redeco8 Redeco9 Trigexp1-020 Trigexp1-022 Trigexp1-024 Trigexp1-030 Trigexp1-100 Trigexp2-11 Trigexp2-13 Trigexp2-13sp Trigexp2-7 Trigexp2-9 Yamamua1-0012 Yamamua1-0012sp Yamamua1-0014sp Yamamua1-0016sp Yamamua1-0018sp Yamamua1-0022sp Yamamua1-0024sp Yamamua1-0026sp Yamamua1-0028sp Yamamua1-0030sp Yamamua1-0032sp Yamamura1-0020sp Yamamura1-0040sp cyclohexan3D transistor transistor-icse -->

## Coherencia de soluciones entre configuraciones con SUCCESS
- Brent-8: soluciones {'affine_af2': '186', 'affine_raa': '181', 'affine_raa_k6': '181'} infactible []
instancias con discrepancia: 1

## Instancias con material k-nomial (bloques > 0 en alguna configuracion)
| instancia | config | estado | celdas | cpu_s | productos | con_bloques |
|---|---|---|---|---|---|---|
| AOL-legentil | affine_af2 | TIME_OUT | 152155 | 60.00 | 0 | 0 |
| AOL-legentil | affine_raa | TIME_OUT | 152273 | 60.00 | 61016 | 0 |
| AOL-legentil | affine_raa_k6 | TIME_OUT | 152459 | 60.00 | 61052 | 1086 |
| AOL-legentil | default | TIME_OUT | 21519 | 60.00 | 0 | 0 |
| AOL-legentil | xn | TIME_OUT | 161811 | 60.00 | 0 | 0 |
| Pramanik | affine_af2 | SUCCESS | 5461 | 1.82 | 0 | 0 |
| Pramanik | affine_raa | SUCCESS | 2761 | 1.22 | 46395 | 0 |
| Pramanik | affine_raa_k6 | SUCCESS | 2737 | 1.22 | 46191 | 23379 |
| Pramanik | default | SUCCESS | 21285 | 10.07 | 0 | 0 |
| Pramanik | xn | SUCCESS | 27735 | 10.39 | 0 | 0 |
| Trigexp2-11 | affine_af2 | TIME_OUT | 24347 | 60.00 | 0 | 0 |
| Trigexp2-11 | affine_raa | TIME_OUT | 24139 | 60.00 | 295925 | 0 |
| Trigexp2-11 | affine_raa_k6 | TIME_OUT | 22901 | 60.00 | 271144 | 271144 |
| Trigexp2-11 | default | INFEASIBLE | 3215 | 7.87 | 0 | 0 |
| Trigexp2-11 | xn | TIME_OUT | 32389 | 60.00 | 0 | 0 |
| Trigexp2-13 | affine_af2 | TIME_OUT | 16221 | 60.01 | 0 | 0 |
| Trigexp2-13 | affine_raa | TIME_OUT | 16411 | 60.00 | 170043 | 0 |
| Trigexp2-13 | affine_raa_k6 | TIME_OUT | 16267 | 60.01 | 168209 | 168209 |
| Trigexp2-13 | default | INFEASIBLE | 7429 | 30.83 | 0 | 0 |
| Trigexp2-13 | xn | TIME_OUT | 24451 | 60.00 | 0 | 0 |
| Trigexp2-15 | affine_af2 | TIME_OUT | 11023 | 60.01 | 0 | 0 |
| Trigexp2-15 | affine_raa | TIME_OUT | 11033 | 60.00 | 158287 | 0 |
| Trigexp2-15 | affine_raa_k6 | TIME_OUT | 10863 | 60.01 | 156462 | 156462 |
| Trigexp2-15 | default | TIME_OUT | 10279 | 60.01 | 0 | 0 |
| Trigexp2-15 | xn | TIME_OUT | 13367 | 60.01 | 0 | 0 |
| Trigexp2-17 | affine_af2 | TIME_OUT | 9637 | 60.01 | 0 | 0 |
| Trigexp2-17 | affine_raa | TIME_OUT | 9843 | 60.00 | 160529 | 0 |
| Trigexp2-17 | affine_raa_k6 | TIME_OUT | 9477 | 60.00 | 160576 | 160576 |
| Trigexp2-17 | default | TIME_OUT | 8939 | 60.00 | 0 | 0 |
| Trigexp2-17 | xn | TIME_OUT | 13251 | 60.00 | 0 | 0 |
| Trigexp2-19 | affine_af2 | TIME_OUT | 11209 | 60.00 | 0 | 0 |
| Trigexp2-19 | affine_raa | TIME_OUT | 11199 | 60.01 | 125393 | 0 |
| Trigexp2-19 | affine_raa_k6 | TIME_OUT | 11131 | 60.01 | 124764 | 124764 |
| Trigexp2-19 | default | TIME_OUT | 7651 | 60.00 | 0 | 0 |
| Trigexp2-19 | xn | TIME_OUT | 20309 | 60.00 | 0 | 0 |
| Trigexp2-21 | affine_af2 | TIME_OUT | 9455 | 60.01 | 0 | 0 |
| Trigexp2-21 | affine_raa | TIME_OUT | 9409 | 60.00 | 112574 | 0 |
| Trigexp2-21 | affine_raa_k6 | TIME_OUT | 9387 | 60.00 | 112555 | 112555 |
| Trigexp2-21 | default | TIME_OUT | 6043 | 60.01 | 0 | 0 |
| Trigexp2-21 | xn | TIME_OUT | 9265 | 60.01 | 0 | 0 |
| Trigexp2-23 | affine_af2 | TIME_OUT | 7535 | 60.03 | 0 | 0 |
| Trigexp2-23 | affine_raa | TIME_OUT | 7539 | 60.02 | 103569 | 0 |
| Trigexp2-23 | affine_raa_k6 | TIME_OUT | 7543 | 60.01 | 104767 | 104767 |
| Trigexp2-23 | default | TIME_OUT | 4907 | 60.05 | 0 | 0 |
| Trigexp2-23 | xn | TIME_OUT | 8513 | 60.00 | 0 | 0 |
| Trigexp2-3 | affine_af2 | TIME_OUT | 105541 | 60.00 | 0 | 0 |
| Trigexp2-3 | affine_raa | TIME_OUT | 104253 | 60.00 | 932091 | 0 |
| Trigexp2-3 | affine_raa_k6 | TIME_OUT | 101447 | 60.00 | 906938 | 906938 |
| Trigexp2-3 | default | TIME_OUT | 174423 | 60.00 | 0 | 0 |
| Trigexp2-3 | xn | TIME_OUT | 84671 | 60.00 | 0 | 0 |
| Trigexp2-5 | affine_af2 | INFEASIBLE | 48597 | 31.40 | 0 | 0 |
| Trigexp2-5 | affine_raa | INFEASIBLE | 48029 | 31.75 | 289333 | 0 |
| Trigexp2-5 | affine_raa_k6 | INFEASIBLE | 47443 | 31.99 | 283499 | 283496 |
| Trigexp2-5 | default | INFEASIBLE | 855 | 0.68 | 0 | 0 |
| Trigexp2-5 | xn | INFEASIBLE | 36685 | 33.42 | 0 | 0 |
| Trigexp2-7 | affine_af2 | TIME_OUT | 53259 | 60.00 | 0 | 0 |
| Trigexp2-7 | affine_raa | TIME_OUT | 52795 | 60.00 | 514841 | 0 |
| Trigexp2-7 | affine_raa_k6 | TIME_OUT | 51251 | 60.00 | 498016 | 498014 |
| Trigexp2-7 | default | INFEASIBLE | 1417 | 1.86 | 0 | 0 |
| Trigexp2-7 | xn | TIME_OUT | 38335 | 60.00 | 0 | 0 |
| Trigexp2-9 | affine_af2 | TIME_OUT | 37399 | 60.00 | 0 | 0 |
| Trigexp2-9 | affine_raa | TIME_OUT | 35001 | 60.00 | 541055 | 0 |
| Trigexp2-9 | affine_raa_k6 | TIME_OUT | 34215 | 60.00 | 548380 | 548371 |
| Trigexp2-9 | default | INFEASIBLE | 2365 | 4.30 | 0 | 0 |
| Trigexp2-9 | xn | TIME_OUT | 25355 | 60.00 | 0 | 0 |
