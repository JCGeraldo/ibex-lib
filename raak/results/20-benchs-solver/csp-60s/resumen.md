instancias: 264  configuraciones: affine_af2, affine_raa, affine_raa_k6, default, xn

## Estados por configuracion
| config | INFEASIBLE | KILLED | NOT_ALL_VALIDATED | SUCCESS | TIME_OUT | terminadas |
|---|---|---|---|---|---|---|
| affine_af2 | 5 | 15 | 18 | 69 | 157 | 92 |
| affine_raa | 5 | 15 | 18 | 70 | 156 | 93 |
| affine_raa_k6 | 5 | 15 | 18 | 70 | 156 | 93 |
| default | 10 | 14 | 19 | 129 | 92 | 158 |
| xn | 5 | 14 | 16 | 64 | 165 | 85 |

terminadas por todas las configuraciones: 73

## Comparaciones por pares (a / b)
| a | b | ambas terminan | celdas a/b (mg) | cpu a/b (mg) | cpu a/b (mg, >=1 s) | a menos celdas | igual | b menos celdas | solo a termina | solo b termina |
|---|---|---|---|---|---|---|---|---|---|---|
| affine_raa | affine_af2 | 92 | 0.982 | 0.979 | 0.980 (n=50) | 4 | 88 | 0 | 1 | 0 |
<!-- solo affine_raa: Neveu1 -->
| affine_raa_k6 | affine_raa | 93 | 1.000 | 0.999 | 1.001 (n=51) | 2 | 91 | 0 | 0 | 0 |
| affine_af2 | xn | 73 | 0.594 | 0.515 | 0.458 (n=43) | 37 | 6 | 30 | 19 | 12 |
<!-- solo affine_af2: Brown-12 Brown-15 Brown-18 Brown-20 Brown-20-1 Brown-30sp BroydenTri-0060 Discrete-Integral-6 Discrete-Integralf2-10 Discrete-Integralf2-9 Eiger-0100 Katsura-17 Trigo1-0010 Trigo1-0010m1 Trigo1-0012 Trigo1-0013 Trigo1-0014 Trigo1-0015 Trigo1-0100sp -->
<!-- solo xn: Designsp Eco9 ExtendedWood-08 Redeco8 Trigexp1-020 Trigexp1-022 Trigexp1-024 Trigexp1-030 Yamamua1-0012 Yamamua1-0022sp Yamamua1-0028sp transistor-icse -->
| affine_raa | xn | 73 | 0.581 | 0.501 | 0.449 (n=43) | 38 | 6 | 29 | 20 | 12 |
<!-- solo affine_raa: Brown-12 Brown-15 Brown-18 Brown-20 Brown-20-1 Brown-30sp BroydenTri-0060 Discrete-Integral-6 Discrete-Integralf2-10 Discrete-Integralf2-9 Eiger-0100 Katsura-17 Neveu1 Trigo1-0010 Trigo1-0010m1 Trigo1-0012 Trigo1-0013 Trigo1-0014 Trigo1-0015 Trigo1-0100sp -->
<!-- solo xn: Designsp Eco9 ExtendedWood-08 Redeco8 Trigexp1-020 Trigexp1-022 Trigexp1-024 Trigexp1-030 Yamamua1-0012 Yamamua1-0022sp Yamamua1-0028sp transistor-icse -->
| affine_raa | default | 90 | 6.548 | 2.876 | 2.752 (n=50) | 10 | 7 | 73 | 3 | 68 |
<!-- solo affine_raa: Discrete-Integral-6 Trigo1-0014 Trigo1-0015 -->
<!-- solo default: Bratu-0050 Brent-10 Brown-19 BroydenBanded-100 BroydenBanded-120 BroydenBanded-140 BroydenTri-0090 BroydenTri-0100 CountercurrentReactors2-10 CountercurrentReactors2-12 CountercurrentReactors2-14 CountercurrentReactors2-16 CountercurrentReactors2-18 CountercurrentReactors2-6 CountercurrentReactors2-8 CountercurrentReactors2-9 Design Designbis Designsp Discrete-Integralf2-11 Discrete-Integralf2-12 Discrete-Integralf2-13 Discrete-Integralf2-14 Discrete-Integralf2-15 Discrete-Integralf2-16 Discrete-Integralf2-17 Discrete-Integralf2-18 Discrete-Integralf2-19 Discrete-Integralf2-20 Discrete-Integralf2-21 DiscreteBoundary-0100 Eco10 Eco9 ExtendedFreud-0100 ExtendedWood-08 Geneig Geneigbis I5 I5bis Katsura-18 Redeco8 Redeco9 Trigexp1-020 Trigexp1-022 Trigexp1-024 Trigexp1-030 Trigexp1-100 Trigexp2-11 Trigexp2-13 Trigexp2-13sp Trigexp2-7 Trigexp2-9 Yamamua1-0012 Yamamua1-0012sp Yamamua1-0014sp Yamamua1-0016sp Yamamua1-0018sp Yamamua1-0022sp Yamamua1-0024sp Yamamua1-0026sp Yamamua1-0028sp Yamamua1-0030sp Yamamua1-0032sp Yamamura1-0020sp cyclohexan3D ponts-geo transistor transistor-icse -->
| default | xn | 85 | 0.092 | 0.151 | 0.120 (n=54) | 74 | 6 | 5 | 73 | 0 |
<!-- solo default: Bratu-0050 Brent-10 Brown-12 Brown-15 Brown-18 Brown-19 Brown-20 Brown-20-1 Brown-30sp BroydenBanded-100 BroydenBanded-120 BroydenBanded-140 BroydenTri-0060 BroydenTri-0090 BroydenTri-0100 CountercurrentReactors2-10 CountercurrentReactors2-12 CountercurrentReactors2-14 CountercurrentReactors2-16 CountercurrentReactors2-18 CountercurrentReactors2-6 CountercurrentReactors2-8 CountercurrentReactors2-9 Design Designbis Discrete-Integralf2-10 Discrete-Integralf2-11 Discrete-Integralf2-12 Discrete-Integralf2-13 Discrete-Integralf2-14 Discrete-Integralf2-15 Discrete-Integralf2-16 Discrete-Integralf2-17 Discrete-Integralf2-18 Discrete-Integralf2-19 Discrete-Integralf2-20 Discrete-Integralf2-21 Discrete-Integralf2-9 DiscreteBoundary-0100 Eco10 Eiger-0100 ExtendedFreud-0100 Geneig Geneigbis I5 I5bis Katsura-17 Katsura-18 Neveu1 Redeco9 Trigexp1-100 Trigexp2-11 Trigexp2-13 Trigexp2-13sp Trigexp2-7 Trigexp2-9 Trigo1-0010 Trigo1-0010m1 Trigo1-0012 Trigo1-0013 Trigo1-0100sp Yamamua1-0012sp Yamamua1-0014sp Yamamua1-0016sp Yamamua1-0018sp Yamamua1-0024sp Yamamua1-0026sp Yamamua1-0030sp Yamamua1-0032sp Yamamura1-0020sp cyclohexan3D ponts-geo transistor -->

## Coherencia de soluciones entre configuraciones con SUCCESS
- Brent-8: soluciones {'affine_af2': '186', 'affine_raa': '181', 'affine_raa_k6': '181'} infactible []
instancias con discrepancia: 1

## Instancias con material k-nomial (bloques > 0 en alguna configuracion)
| instancia | config | estado | celdas | cpu_s | productos | con_bloques |
|---|---|---|---|---|---|---|
| AOL-legentil | affine_af2 | TIME_OUT | 129497 | 60.00 | 0 | 0 |
| AOL-legentil | affine_raa | TIME_OUT | 125375 | 60.00 | 54166 | 0 |
| AOL-legentil | affine_raa_k6 | TIME_OUT | 126837 | 60.00 | 54440 | 842 |
| AOL-legentil | default | TIME_OUT | 18245 | 60.01 | 0 | 0 |
| AOL-legentil | xn | TIME_OUT | 135373 | 60.00 | 0 | 0 |
| Pramanik | affine_af2 | SUCCESS | 5461 | 2.07 | 0 | 0 |
| Pramanik | affine_raa | SUCCESS | 2761 | 1.44 | 46395 | 0 |
| Pramanik | affine_raa_k6 | SUCCESS | 2737 | 1.42 | 46191 | 22758 |
| Pramanik | default | SUCCESS | 21285 | 11.21 | 0 | 0 |
| Pramanik | xn | SUCCESS | 27735 | 11.65 | 0 | 0 |
| Trigexp2-11 | affine_af2 | TIME_OUT | 21949 | 60.00 | 0 | 0 |
| Trigexp2-11 | affine_raa | TIME_OUT | 21883 | 60.00 | 252916 | 0 |
| Trigexp2-11 | affine_raa_k6 | TIME_OUT | 20875 | 60.01 | 236585 | 215977 |
| Trigexp2-11 | default | INFEASIBLE | 3215 | 9.42 | 0 | 0 |
| Trigexp2-11 | xn | TIME_OUT | 29929 | 60.00 | 0 | 0 |
| Trigexp2-13 | affine_af2 | TIME_OUT | 15485 | 60.01 | 0 | 0 |
| Trigexp2-13 | affine_raa | TIME_OUT | 15621 | 60.00 | 155780 | 0 |
| Trigexp2-13 | affine_raa_k6 | TIME_OUT | 15541 | 60.00 | 155133 | 153864 |
| Trigexp2-13 | default | INFEASIBLE | 7429 | 33.34 | 0 | 0 |
| Trigexp2-13 | xn | TIME_OUT | 23179 | 60.00 | 0 | 0 |
| Trigexp2-15 | affine_af2 | TIME_OUT | 9657 | 60.02 | 0 | 0 |
| Trigexp2-15 | affine_raa | TIME_OUT | 9563 | 60.00 | 123489 | 0 |
| Trigexp2-15 | affine_raa_k6 | TIME_OUT | 9433 | 60.02 | 122531 | 116668 |
| Trigexp2-15 | default | TIME_OUT | 9617 | 60.01 | 0 | 0 |
| Trigexp2-15 | xn | TIME_OUT | 11015 | 60.00 | 0 | 0 |
| Trigexp2-17 | affine_af2 | TIME_OUT | 8207 | 60.01 | 0 | 0 |
| Trigexp2-17 | affine_raa | TIME_OUT | 8211 | 60.02 | 121419 | 0 |
| Trigexp2-17 | affine_raa_k6 | TIME_OUT | 8065 | 60.01 | 118158 | 117506 |
| Trigexp2-17 | default | TIME_OUT | 7397 | 60.01 | 0 | 0 |
| Trigexp2-17 | xn | TIME_OUT | 9691 | 60.00 | 0 | 0 |
| Trigexp2-19 | affine_af2 | TIME_OUT | 8763 | 60.01 | 0 | 0 |
| Trigexp2-19 | affine_raa | TIME_OUT | 8871 | 60.01 | 96219 | 0 |
| Trigexp2-19 | affine_raa_k6 | TIME_OUT | 8807 | 60.01 | 95579 | 94813 |
| Trigexp2-19 | default | TIME_OUT | 6051 | 60.00 | 0 | 0 |
| Trigexp2-19 | xn | TIME_OUT | 16035 | 60.00 | 0 | 0 |
| Trigexp2-21 | affine_af2 | TIME_OUT | 7257 | 60.00 | 0 | 0 |
| Trigexp2-21 | affine_raa | TIME_OUT | 7263 | 60.00 | 86253 | 0 |
| Trigexp2-21 | affine_raa_k6 | TIME_OUT | 7243 | 60.02 | 85639 | 84952 |
| Trigexp2-21 | default | TIME_OUT | 4925 | 60.01 | 0 | 0 |
| Trigexp2-21 | xn | TIME_OUT | 7599 | 60.01 | 0 | 0 |
| Trigexp2-23 | affine_af2 | TIME_OUT | 5499 | 60.01 | 0 | 0 |
| Trigexp2-23 | affine_raa | TIME_OUT | 5359 | 60.01 | 72270 | 0 |
| Trigexp2-23 | affine_raa_k6 | TIME_OUT | 5345 | 60.00 | 72474 | 71954 |
| Trigexp2-23 | default | TIME_OUT | 3955 | 60.01 | 0 | 0 |
| Trigexp2-23 | xn | TIME_OUT | 6379 | 60.01 | 0 | 0 |
| Trigexp2-3 | affine_af2 | TIME_OUT | 74681 | 60.00 | 0 | 0 |
| Trigexp2-3 | affine_raa | TIME_OUT | 72765 | 60.00 | 650226 | 0 |
| Trigexp2-3 | affine_raa_k6 | TIME_OUT | 72191 | 60.00 | 645182 | 141441 |
| Trigexp2-3 | default | TIME_OUT | 128847 | 60.00 | 0 | 0 |
| Trigexp2-3 | xn | TIME_OUT | 59809 | 60.00 | 0 | 0 |
| Trigexp2-5 | affine_af2 | INFEASIBLE | 48597 | 43.90 | 0 | 0 |
| Trigexp2-5 | affine_raa | INFEASIBLE | 48029 | 43.13 | 289333 | 0 |
| Trigexp2-5 | affine_raa_k6 | INFEASIBLE | 47459 | 43.56 | 283516 | 281288 |
| Trigexp2-5 | default | INFEASIBLE | 855 | 0.99 | 0 | 0 |
| Trigexp2-5 | xn | INFEASIBLE | 36685 | 48.64 | 0 | 0 |
| Trigexp2-7 | affine_af2 | TIME_OUT | 40093 | 60.00 | 0 | 0 |
| Trigexp2-7 | affine_raa | TIME_OUT | 39779 | 60.00 | 384921 | 0 |
| Trigexp2-7 | affine_raa_k6 | TIME_OUT | 38191 | 60.00 | 365640 | 290807 |
| Trigexp2-7 | default | INFEASIBLE | 1417 | 2.51 | 0 | 0 |
| Trigexp2-7 | xn | TIME_OUT | 27603 | 60.02 | 0 | 0 |
| Trigexp2-9 | affine_af2 | TIME_OUT | 28873 | 60.00 | 0 | 0 |
| Trigexp2-9 | affine_raa | TIME_OUT | 28127 | 60.00 | 433501 | 0 |
| Trigexp2-9 | affine_raa_k6 | TIME_OUT | 24741 | 60.00 | 414058 | 249873 |
| Trigexp2-9 | default | INFEASIBLE | 2365 | 5.74 | 0 | 0 |
| Trigexp2-9 | xn | TIME_OUT | 19123 | 60.00 | 0 | 0 |
