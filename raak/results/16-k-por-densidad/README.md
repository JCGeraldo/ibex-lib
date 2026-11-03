# Mejor k según densidad (punto 2 del to-do de fin de octubre, 02-11-2026)

Pregunta del profesor: ¿cómo elegir k según la densidad? Respuesta corta: **k debe seguir al tamaño de clique disponible en cada
producto, y ese tamaño lo fija el número de símbolos compartidos con diagonal del mismo signo, no la densidad de Q.** En synq
los factores (A_k·x) y (M_k·x) son densos (ρ es la densidad de Q = AᵀM), así que el clique disponible crece con n (medio 2.4, 2.9,
4.0, 4.9 para n = 3, 5, 8, 10) y ρ solo entra por las restricciones, cuyos factores sí se generan con densidad max(ρ, 0.5).
Con el parche 0009 el costo de k es despreciable, así que la regla práctica es "k tan grande como el material": k=3 basta para
n=3, k=4 es el mejor en todo lo demás, y para n ≥ 8 el nivel 2 del 02-11 confirma que k=5 y k=6 siguen ganando (celdas 0.86 y 0.81 de k=4, CPU 0.87 y 0.86; ver `nivel2-k56/`).

Tres fuentes cruzadas:
1. `analysis/cliques_sinteticas.py` (`cliques_synq.csv`): clique máximo por producto leído del .bch (mayor clase de signo de a_i·m_i).
2. Nivel 1 con el parche 0010 (`range.csv.gz`, `tests/range_eval` con k = 2..6 y columnas `b2..b7p` = bloques por tamaño), sobre synq,
   reales, synl y synt.
3. Nivel 2 de la sesión 0009 por (n, ρ) (`15-barrido-0009/nivel2-synq/por_configuracion.csv`, `tabla_raa_baseline.csv`).

`analysis/k_por_densidad.py` produce `anchura_por_k.csv`, `bloques_por_tamano.csv`, `nivel2_por_config.csv`,
`mejor_k_por_instancia.csv`, `k_nivel1.png`, `k_nivel2.png`; la salida completa está en `analisis_stdout.txt`.

## Lo que sale

| n | clique disponible (medio / máx) | anchura k3 → k4 → k6 (ρ=0.9) | bloques de ≥5 símbolos con k=6 | mejor k en CPU (nivel 2) |
|---|---|---|---|---|
| 3 | 2.4 / 2.7 | 0.921 → 0.921 → 0.921 | 0 % | k=3 (k=2 si ρ=0.2: celdas iguales) |
| 5 | 2.9 / 4.3 | 0.944 → 0.937 → 0.933 | 2 a 9 % | k=4 |
| 8 | 4.0 / 6.4 | 0.949 → 0.931 → 0.921 | 32 a 33 % | k=6 (nivel2-k56: CPU 0.86 de k=4) |
| 10 | 4.9 / 8.2 | 0.950 → 0.930 → 0.911 | 45 a 51 % | k=6 (nivel2-k56: celdas 0.81 de k=4, brecha menor en los TO) |

- La ganancia k3 → k4 en celdas sigue a la fracción de productos con clique ≥ 4: 1.000 cuando es 0 (21 instancias), 0.925 entre 0 y
  0.3, 0.843 entre 0.3 y 0.6, 0.826 por encima de 0.6 (Spearman −0.885). Es decir, k=4 no cuesta nada donde no hay cliques de 4 y
  gana donde los hay.
- La densidad ρ actúa a través de las restricciones: con ρ=0.9 los productos de las restricciones también son densos y el k-nomial
  estrecha más (n=8: 0.931 con ρ=0.9 frente a 0.961 y 0.970 con ρ=0.2 y 0.5); con ρ ≤ 0.5 las restricciones usan densidad 0.5.
- En las familias reales y con funciones el clique disponible es pequeño: ex6_2_* satura en k=3 (0.9759 → 0.9757 → 0.9755), synl y synt
  ganan poco más allá de k=4 (0.978 → 0.975).
- Con k=6 la búsqueda extrae bloques de 5 y 6 símbolos en synq n ≥ 8 (hasta la mitad de los bloques) y la anchura sigue bajando;
  el barrido de nivel 2 del 02-11 (abajo) confirma que se traduce en celdas y CPU.

## Regla propuesta para el paper

k no se elige por la densidad de la forma cuadrática sino por el material de cada producto: el k efectivo es min(k, c) donde c es el
tamaño de la mayor clase de signo entre los símbolos compartidos. Como la búsqueda ya se detiene sola cuando no hay cliques
mayores, fijar k alto (4, o más para productos con muchos símbolos compartidos) no penaliza: con el parche 0009 el costo por
evaluación de k=4 es 1.04 a 1.06 veces el de k=0, y en el solver k=6 cuesta por evaluación 1.06 veces k=4 (misma sesión).

## Nivel 2 con k = 4, 5, 6 (`nivel2-k56/`, 02-11-2026, 20:25 a 23:32)

Misma sesión y mismo binario (lib 0009 + 0010) para las tres variantes: synq n = 8 y 10, ρ = 0.2, 0.5, 0.9, pos y posneg, 3 semillas
(36 instancias × 3 = 108 corridas, `--lr=art --arith=raa --trig=auto -t 1800`, P=10). Archivos: `runs_k456.csv` (filas crudas),
`por_configuracion_k456.csv`, `resumen_k456.txt` (salida de `analysis/k56_analisis.py`), `meta.txt`, `run.sh`.

| respecto a k=4 | celdas (36, media geom.) | CPU (36) | celdas (20 resueltas por ambas) | CPU (20) | CPU por evaluación (20) |
|---|---|---|---|---|---|
| k=5 | 0.911 | 0.925 | 0.859 | 0.874 | 1.015 |
| k=6 | 0.853 | 0.915 | 0.805 | 0.857 | 1.062 |

- Timeouts: 16 con k=4, 15 con k=5 y con k=6 (synq_n08_d20_pos_s3 se resuelve con k=5 en 1623 s y con k=6 en 1589 s). En los 15
  que agotan las tres variantes la brecha ub−lb a los 1800 s baja con k en 14 de 15 (p. ej. n10_d20_pos_s1: 5.48 → 4.77 → 4.41).
- Por configuración, k=6 gana más donde el clique disponible es mayor: n=8 pos ρ=0.9 celdas 0.714 y CPU 0.737; n=8 d20 pos 0.753 /
  0.779. Las posneg de n=8 quedan en 0.84 a 0.95 de celdas con CPU 0.86 a 1.00. Ninguna configuración empeora en celdas; en CPU
  solo n=10 d20 posneg (1.007) y dos instancias sueltas de n=8 posneg (1.05, 1.10) cuestan algo más con k=6.
- Bloques por producto bajan con k (n=10 ρ=0.9: 2.54 → 2.13 → 2.00): la búsqueda junta en un bloque grande lo que con k=4 eran
  dos o tres bloques, que es exactamente lo que estrecha la cota.
- El costo por evaluación afín (CPU/evaluados) de k=6 es 1.06 veces el de k=4 (1.015 para k=5); el ahorro en CPU viene del árbol
  más pequeño, no de evaluar más rápido.

Conclusión para el punto 2: en synq n ≥ 8 el mejor k en celdas y en CPU es el mayor probado, k=6, y k=5 queda en medio. Junto con
el nivel 1 (n=3 satura en 3, n=5 en 5) la regla queda confirmada: k alto, el material de cada producto decide.
