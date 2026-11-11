## Resueltas por semilla
| semilla | art_raa_k0 | art_raa_k4 | art_raa_k6 |
|---|---|---|---|
| 1 | 42 | 42 | 42 |
| 2 | 42 | 42 | 42 |
| 3 | 42 | 42 | 42 |
| 42 | 42 | 42 | 42 |

## Cocientes por semilla (instancias resueltas por ambas)
| par | medida | semilla 1 | semilla 2 | semilla 3 | semilla 42 | min | max |
|---|---|---|---|---|---|---|---|
| raa_k4/raa_k0 | celdas | 0.638 (n=42) | 0.639 (n=42) | 0.654 (n=42) | 0.645 (n=42) | 0.638 | 0.654 |
| raa_k4/raa_k0 | cpu_s | 0.688 (n=42) | 0.714 (n=42) | 0.711 (n=42) | 0.709 (n=42) | 0.688 | 0.714 |
| raa_k6/raa_k0 | celdas | 0.629 (n=42) | 0.628 (n=42) | 0.645 (n=42) | 0.634 (n=42) | 0.628 | 0.645 |
| raa_k6/raa_k0 | cpu_s | 0.677 (n=42) | 0.696 (n=42) | 0.709 (n=42) | 0.674 (n=42) | 0.674 | 0.709 |
| raa_k6/raa_k4 | celdas | 0.985 (n=42) | 0.982 (n=42) | 0.986 (n=42) | 0.983 (n=42) | 0.982 | 0.986 |
| raa_k6/raa_k4 | cpu_s | 0.985 (n=42) | 0.975 (n=42) | 0.998 (n=42) | 0.951 (n=42) | 0.951 | 0.998 |

## Mismo conjunto en todas las semillas (resueltas por las dos variantes en las 4 semillas)
| par | n | celdas s1 | celdas s2 | celdas s3 | celdas s42 | cpu s1 | cpu s2 | cpu s3 | cpu s42 |
|---|---|---|---|---|---|---|---|---|---|
| raa_k4/raa_k0 | 42 | 0.638 | 0.639 | 0.654 | 0.645 | 0.688 | 0.714 | 0.711 | 0.709 |
| raa_k6/raa_k0 | 42 | 0.629 | 0.628 | 0.645 | 0.634 | 0.677 | 0.696 | 0.709 | 0.674 |
| raa_k6/raa_k4 | 42 | 0.985 | 0.982 | 0.986 | 0.983 | 0.985 | 0.975 | 0.998 | 0.951 |

## Dispersion entre semillas (celdas max/min por instancia, resueltas en las 4 semillas)
| variante | n | mediana max/min | peor max/min | instancias donde gana k6 a k0 en las 4 semillas |
|---|---|---|---|---|
| raa_k0 | 42 | 1.001 | 1.667 | 35 de 42 |
| raa_k4 | 42 | 1.015 | 1.500 | 35 de 42 |
| raa_k6 | 42 | 1.013 | 1.500 | 35 de 42 |
