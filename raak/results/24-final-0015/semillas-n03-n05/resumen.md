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
| raa_k4/raa_k0 | celdas | 0.622 (n=42) | 0.622 (n=42) | 0.640 (n=42) | 0.629 (n=42) | 0.622 | 0.640 |
| raa_k4/raa_k0 | cpu_s | 0.675 (n=42) | 0.704 (n=42) | 0.700 (n=42) | 0.693 (n=42) | 0.675 | 0.704 |
| raa_k6/raa_k0 | celdas | 0.612 (n=42) | 0.611 (n=42) | 0.631 (n=42) | 0.618 (n=42) | 0.611 | 0.631 |
| raa_k6/raa_k0 | cpu_s | 0.651 (n=42) | 0.679 (n=42) | 0.680 (n=42) | 0.657 (n=42) | 0.651 | 0.680 |
| raa_k6/raa_k4 | celdas | 0.983 (n=42) | 0.983 (n=42) | 0.985 (n=42) | 0.983 (n=42) | 0.983 | 0.985 |
| raa_k6/raa_k4 | cpu_s | 0.964 (n=42) | 0.964 (n=42) | 0.972 (n=42) | 0.949 (n=42) | 0.949 | 0.972 |

## Mismo conjunto en todas las semillas (resueltas por las dos variantes en las 4 semillas)
| par | n | celdas s1 | celdas s2 | celdas s3 | celdas s42 | cpu s1 | cpu s2 | cpu s3 | cpu s42 |
|---|---|---|---|---|---|---|---|---|---|
| raa_k4/raa_k0 | 42 | 0.622 | 0.622 | 0.640 | 0.629 | 0.675 | 0.704 | 0.700 | 0.693 |
| raa_k6/raa_k0 | 42 | 0.612 | 0.611 | 0.631 | 0.618 | 0.651 | 0.679 | 0.680 | 0.657 |
| raa_k6/raa_k4 | 42 | 0.983 | 0.983 | 0.985 | 0.983 | 0.964 | 0.964 | 0.972 | 0.949 |

## Dispersion entre semillas (celdas max/min por instancia, resueltas en las 4 semillas)
| variante | n | mediana max/min | peor max/min | instancias donde gana k6 a k0 en las 4 semillas |
|---|---|---|---|---|
| raa_k0 | 42 | 1.001 | 1.667 | 36 de 42 |
| raa_k4 | 42 | 1.014 | 1.500 | 36 de 42 |
| raa_k6 | 42 | 1.009 | 1.500 | 36 de 42 |
