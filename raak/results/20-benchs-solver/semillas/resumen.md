## Resueltas por semilla
| semilla | art_raa_k0 | art_raa_k4 | art_raa_k6 |
|---|---|---|---|
| 1 | 14 | 15 | 15 |
| 2 | 14 | 15 | 15 |
| 3 | 14 | 15 | 15 |
| 42 | 14 | 15 | 15 |

## Cocientes por semilla (instancias resueltas por ambas)
| par | medida | semilla 1 | semilla 2 | semilla 3 | semilla 42 | min | max |
|---|---|---|---|---|---|---|---|
| raa_k4/raa_k0 | celdas | 0.460 (n=14) | 0.458 (n=14) | 0.463 (n=14) | 0.457 (n=14) | 0.457 | 0.463 |
| raa_k4/raa_k0 | cpu_s | 0.511 (n=14) | 0.506 (n=14) | 0.515 (n=14) | 0.508 (n=14) | 0.506 | 0.515 |
| raa_k6/raa_k0 | celdas | 0.378 (n=14) | 0.369 (n=14) | 0.381 (n=14) | 0.378 (n=14) | 0.369 | 0.381 |
| raa_k6/raa_k0 | cpu_s | 0.417 (n=14) | 0.407 (n=14) | 0.421 (n=14) | 0.421 (n=14) | 0.407 | 0.421 |
| raa_k6/raa_k4 | celdas | 0.815 (n=15) | 0.799 (n=15) | 0.815 (n=15) | 0.818 (n=15) | 0.799 | 0.818 |
| raa_k6/raa_k4 | cpu_s | 0.814 (n=15) | 0.802 (n=15) | 0.815 (n=15) | 0.824 (n=15) | 0.802 | 0.824 |

## Mismo conjunto en todas las semillas (resueltas por las dos variantes en las 4 semillas)
| par | n | celdas s1 | celdas s2 | celdas s3 | celdas s42 | cpu s1 | cpu s2 | cpu s3 | cpu s42 |
|---|---|---|---|---|---|---|---|---|---|
| raa_k4/raa_k0 | 14 | 0.460 | 0.458 | 0.463 | 0.457 | 0.511 | 0.506 | 0.515 | 0.508 |
| raa_k6/raa_k0 | 14 | 0.378 | 0.369 | 0.381 | 0.378 | 0.417 | 0.407 | 0.421 | 0.421 |
| raa_k6/raa_k4 | 15 | 0.815 | 0.799 | 0.815 | 0.818 | 0.814 | 0.802 | 0.815 | 0.824 |

## Dispersion entre semillas (celdas max/min por instancia, resueltas en las 4 semillas)
| variante | n | mediana max/min | peor max/min | instancias donde gana k6 a k0 en las 4 semillas |
|---|---|---|---|---|
| raa_k0 | 14 | 1.024 | 1.081 | 14 de 14 |
| raa_k4 | 15 | 1.032 | 1.201 | 14 de 14 |
| raa_k6 | 15 | 1.031 | 1.365 | 14 de 14 |
