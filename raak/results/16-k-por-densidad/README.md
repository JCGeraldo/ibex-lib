# Mejor k según densidad (punto 2 del to-do de fin de octubre, 02-11-2026)

Pregunta del profesor: ¿cómo elegir k según la densidad? Respuesta corta: **k debe seguir al tamaño de clique disponible en cada
producto, y ese tamaño lo fija el número de símbolos compartidos con diagonal del mismo signo, no la densidad de Q.** En synq
los factores (A_k·x) y (M_k·x) son densos (ρ es la densidad de Q = AᵀM), así que el clique disponible crece con n (medio 2.4, 2.9,
4.0, 4.9 para n = 3, 5, 8, 10) y ρ solo entra por las restricciones, cuyos factores sí se generan con densidad max(ρ, 0.5).
Con el parche 0009 el costo de k es despreciable hasta k=6, así que la regla práctica es "k tan grande como el material": en toda
familia con material el mejor k fue el mayor probado, y la ganancia se detiene donde se acaba el material (n=3 satura en k=3, n=5 en
k=5, reales y familias con funciones en k=3 o 4; synq n ≥ 8 sigue ganando hasta k=6: celdas 0.86 y 0.81 de k=4 con k=5 y k=6,
CPU 0.87 y 0.86; ver `nivel2-k56/`). k=n (sin tope) no se recomienda sin cambiar la búsqueda: ver la sección de estrés al final.

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
mayores, fijar k alto no penaliza mientras el material sea moderado (k=6 cubre todo lo observado): con el parche 0009 el costo por
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

## ¿k=n? Estrés con material grande y parche 0011 (`estres-k-grande/`, 03-11-2026)

Pregunta: si el mejor k es siempre el mayor probado, ¿se recomienda k=n (sin tope)? Como Q solo tiene los n símbolos de las
variables, k=n equivale a no limitar el clique. El problema no es la cota sino la búsqueda: la DFS de `knomial_rewrite` era
exhaustiva y visitaba cada clique en todas sus permutaciones, (c−2)!/(c−k)! secuencias por arista base para un producto con c
símbolos compartidos del mismo signo. Para medirlo se generaron synq `pos` con ρ=0.9 y n = 12, 15, 20, 30 (una semilla, mismo
generador con `n in (12, 15, 20, 30)`), cuyo material por producto (clique disponible medio / máximo, `cliques.csv`) va de 7 / 9 a
16 / 22, y se corrió el solver 60 s de CPU por configuración con corte duro a 300 s de reloj (`run_0010.sh`, `run_0011.sh`,
`corridas.csv`, tabla de `analysis/estres_k_grande.py`). La medida es el costo por evaluación afín (CPU / evaluados); las celdas
son las alcanzadas a los 60 s y solo indican cuánto avanzó cada corrida, no la calidad de la cota.

| n | material (medio / máx) | binario | k=0 | k=6 | k=8 | k=n |
|---|---|---|---|---|---|---|
| 12 | 7.1 / 9 | 0010 (exhaustiva) | 96 µs (19158 celdas) | 193 µs (8644 celdas) | 645 µs (2842 celdas) | 1004 µs (1806 celdas) |
| 12 | 7.1 / 9 | 0011 sin presupuesto | 107 µs (17362 celdas) | 125 µs (13954 celdas) | 133 µs (13186 celdas) | 131 µs (13168 celdas) |
| 12 | 7.1 / 9 | 0011, presupuesto 2000 | 107 µs (17362 celdas) | 126 µs (13790 celdas) | 132 µs (13254 celdas) | 132 µs (13074 celdas) |
| 15 | 8.8 / 12 | 0010 (exhaustiva) | 137 µs (10262 celdas) | 548 µs (2704 celdas) | 9977 µs (138 celdas) | 218029 µs (6 celdas) |
| 15 | 8.8 / 12 | 0011 sin presupuesto | 153 µs (9310 celdas) | 191 µs (7550 celdas) | 214 µs (6698 celdas) | 210 µs (7060 celdas) |
| 15 | 8.8 / 12 | 0011, presupuesto 2000 | 153 µs (9310 celdas) | 190 µs (7570 celdas) | 216 µs (6636 celdas) | 210 µs (7062 celdas) |
| 20 | 10.9 / 16 | 0010 (exhaustiva) | 181 µs (6316 celdas) | 1846 µs (514 celdas) | 67821 µs (18 celdas) | matada a 300 s |
| 20 | 10.9 / 16 | 0011 sin presupuesto | 192 µs (5946 celdas) | 325 µs (3612 celdas) | 534 µs (1834 celdas) | 718 µs (1300 celdas) |
| 20 | 10.9 / 16 | 0011, presupuesto 2000 | 192 µs (5946 celdas) | 319 µs (3786 celdas) | 427 µs (2372 celdas) | 464 µs (2000 celdas) |
| 30 | 15.8 / 22 | 0010 (exhaustiva) | 322 µs (2050 celdas) | 13985 µs (46 celdas) | 174 eval. en 265 s | matada a 300 s |
| 30 | 15.8 / 22 | 0011 sin presupuesto | 343 µs (1930 celdas) | 1284 µs (590 celdas) | 3881 µs (180 celdas) | 22910 µs (28 celdas) |
| 30 | 15.8 / 22 | 0011, presupuesto 2000 | 343 µs (1930 celdas) | 762 µs (952 celdas) | 721 µs (1004 celdas) | 1077 µs (732 celdas) |

- Con la búsqueda exhaustiva (binario 0010) el costo explota con el material incluso con k=6: n=15 k=8 cuesta 74 veces k=0 y
  k=15, 1600 veces (una evaluación cada 0.2 s); n=20 k=20 y n=30 k=30 no completan ni una iteración del solver en 300 s.
- **Parche 0011** (`patches/0011-ibex-affine-cliques-sin-repetir-presupuesto.patch`): (a) cada clique se enumera una sola vez,
  conservando la secuencia descendente que era la primera en alcanzarlo, con lo que benefit y orden de descubrimiento son los de
  antes (hash de `knomial_diff_dump` 4e35cac9e4b800a4 y celdas iguales en synq n=8 con k=4 y k=6: 2404, 2140, 11188, 10330); (b)
  presupuesto de nodos por producto, `RAAK_NODE_BUDGET` (0 = sin límite), que al agotarse deja de extender la búsqueda pero devuelve un
  clique balanceado válido.
- Solo con (a), k=n cuesta 1.2 veces k=0 en n=12, 1.4 en n=15, 3.7 en n=20 y 67 en n=30: el número de cliques distintos sigue siendo
  exponencial en el material. Con presupuesto 2000, k=n queda en 1.2, 1.4, 2.4 y 3.1 veces k=0, y k=6 entre 1.2 y 2.2.
- El presupuesto no interviene en n ≤ 15 (mismas cifras con y sin él) y por tanto no toca ninguno de los experimentos de los
  informes 1 a 3, cuyo material máximo es 8.

Respuesta: k=n es defendible solo con el parche 0011 y un presupuesto de nodos; sin él, un producto de dos sumas largas (12 o más
variables compartidas del mismo signo) deja una evaluación en segundos o minutos. La recomendación práctica sigue siendo k alto
(6) por defecto, y k=n con presupuesto cuando se quiera presentar "sin tope"; en ambos casos el k efectivo lo fija el material.
Queda por medir en el nivel 2 si k=n con presupuesto gana celdas frente a k=6 en instancias con material 10 a 20.
