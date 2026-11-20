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
| raa_k4/raa_k0 | celdas | 0.461 (n=14) | 0.457 (n=14) | 0.459 (n=14) | 0.461 (n=14) | 0.457 | 0.461 |
| raa_k4/raa_k0 | cpu_s | 0.520 (n=14) | 0.517 (n=14) | 0.520 (n=14) | 0.522 (n=14) | 0.517 | 0.522 |
| raa_k6/raa_k0 | celdas | 0.379 (n=14) | 0.368 (n=14) | 0.378 (n=14) | 0.378 (n=14) | 0.368 | 0.379 |
| raa_k6/raa_k0 | cpu_s | 0.423 (n=14) | 0.416 (n=14) | 0.425 (n=14) | 0.428 (n=14) | 0.416 | 0.428 |
| raa_k6/raa_k4 | celdas | 0.814 (n=15) | 0.799 (n=15) | 0.817 (n=15) | 0.812 (n=15) | 0.799 | 0.817 |
| raa_k6/raa_k4 | cpu_s | 0.812 (n=15) | 0.803 (n=15) | 0.815 (n=15) | 0.817 (n=15) | 0.803 | 0.817 |

## Mismo conjunto en todas las semillas (resueltas por las dos variantes en las 4 semillas)
| par | n | celdas s1 | celdas s2 | celdas s3 | celdas s42 | cpu s1 | cpu s2 | cpu s3 | cpu s42 |
|---|---|---|---|---|---|---|---|---|---|
| raa_k4/raa_k0 | 14 | 0.461 | 0.457 | 0.459 | 0.461 | 0.520 | 0.517 | 0.520 | 0.522 |
| raa_k6/raa_k0 | 14 | 0.379 | 0.368 | 0.378 | 0.378 | 0.423 | 0.416 | 0.425 | 0.428 |
| raa_k6/raa_k4 | 15 | 0.814 | 0.799 | 0.817 | 0.812 | 0.812 | 0.803 | 0.815 | 0.817 |

## Dispersion entre semillas (celdas max/min por instancia, resueltas en las 4 semillas)
| variante | n | mediana max/min | peor max/min | instancias donde gana k6 a k0 en las 4 semillas |
|---|---|---|---|---|
| raa_k0 | 14 | 1.024 | 1.081 | 14 de 14 |
| raa_k4 | 15 | 1.047 | 1.149 | 14 de 14 |
| raa_k6 | 15 | 1.028 | 1.282 | 14 de 14 |
