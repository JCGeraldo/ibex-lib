# Nivel 1 sobre los conjuntos de `benchs/optim` que faltaban (29-10-2026)

Pregunta que lo motiva: para los productos de funciones (sin, cos, exp), ¿solo tenemos las instancias sintéticas `synt`?
El filtro del nivel 1 (`11-filtro-instancias`) había corrido solo sobre easy, medium, hard, others y coconut. Aquí se corre
`tests/range_eval` (sub-cajas 2, muestras 200, trig auto) sobre los otros cuatro conjuntos de `benchs/optim`
(270 instancias, 3.5 min, 0 errores) y se clasifica con `analysis/filtro_instancias.py` (misma regla: `knomial` si kn_raa < 0.99
o estrecha > 1 % en al menos 10 % de las (función, caja)). `analysis/productos_funciones.py` marca por texto qué instancias
tienen un producto con sin/cos/exp o con ln/log en algún factor.

| conjunto | instancias | con k-nomial | solo RAA | nada | con producto trig/exp | de ellas con k-nomial | con producto log | de ellas con k-nomial |
|---|---|---|---|---|---|---|---|---|
| benchs-unconstrainedoptim | 179 | 3 | 63 | 113 | 64 | 0 | 0 | 0 |
| unsolved | 38 | 3 | 2 | 33 | 11 | 0 | 11 | 2 (`ex6_2_5`, `ex6_2_7`) |
| blowup | 25 | 1 | 2 | 22 | 5 | 0 | 10 | 1 (`ex6_2_13`) |
| benchs-minlp | 27 | 1 | 4 | 22 | 2 | 0 | 1 | 0 |

(`f1` no se pudo cargar (error de parseo del .bch): 179 de 180 en unconstrained.)

## Las 8 con material para el k-nomial

| conjunto | instancia | kn_raa | frac_kn | k_used raa k=3 | raa_vs_af2 | sobre_raa | qué estructura tiene |
|---|---|---|---|---|---|---|---|
| unsolved | ex6_2_7 | 0.984 | 0.25 | 54 | 1.000 | 4.63 | familia Gibbs, productos x·ln(.) (misma que `instancias/reales`) |
| unsolved | ex6_2_5 | 0.987 | 0.25 | 36 | 1.000 | 3.06 | idem |
| unsolved | ex8_1_3 | 0.987 | 0.22 | 53 | 0.955 | 2.17 | Goldstein-Price: producto de polinomios en (x1, x2) |
| benchs-minlp | st_e36 | 0.989 | 0.17 | 128 | 0.950 | 1.88 | restricción = producto de 5 cuadráticas en (x2, i1); i1 entera |
| blowup | ex6_2_13 | 0.994 | 0.25 | 18 | 1.000 | 2.33 | familia Gibbs |
| benchs-unconstrainedoptim | mishra01-10 | 0.995 | 0.11 | 9 | 1.000 | 14.68 | (1+s)^s con s afín: potencia de forma afín por sí misma |
| benchs-unconstrainedoptim | xinshe-yang2 | 0.995 | 0.11 | 2 | 0.998 | 3.19 | (abs x1 + abs x2) / exp(sin x1² + sin x2²): cociente, ambos factores en x1, x2 |
| benchs-unconstrainedoptim | mishra02-10 | 0.995 | 0.11 | 9 | 1.000 | 13.00 | como mishra01 |

## Respuesta

- Productos con sin, cos o exp: 82 instancias reales los tienen en el texto; **ninguna** tiene material para el k-nomial.
  Las que más se acercan (`keane-2/3/4`, k_used 21-47, kn_raa 0.9995) usan bloques pero no estrechan nada: los factores
  comparten como mucho un símbolo (`cos(x_i)^2 * cos(x_j)^2`), que es justo donde el k-nomial no tiene nada que reescribir.
  La única real con una función trascendente donde actúa es `xinshe-yang2`, y es marginal (kn_raa 0.995, 2 bloques).
  Para el solver, los productos de funciones trascendentes de formas afines con símbolos compartidos solo están en `synt`
  (y en los CSP `Trigexp2-*` de `benchs/solver`, que no son de optimización).
- Productos con logaritmo: aparecen 3 instancias más de la familia `ex6_2_*` (5, 7, 13) con material, iguales a las 7 ya usadas.
  Son `unsolved`/`blowup`, es decir instancias que ibexopt no resuelve en el tiempo límite, por eso no estaban en el subconjunto real.
- RAA sola (sin k-nomial) estrecha en 63 de las 179 unconstrained (raa_vs_af2 medio 0.897): son casos para el artículo de la RAA, no del k-nomial.

| archivo | qué es |
|---|---|
| `range.csv.gz`, `meta.txt`, `range_log.txt` | La corrida del nivel 1 (270 instancias, 8 variantes). |
| `tabla_instancias.csv` | Indicadores del nivel 1 por instancia + clase + columnas `prod_trig_exp`, `prod_log`. |
| `productos_funciones_optim.csv` | Marca textual de productos con funciones para los 8 conjuntos de `benchs/optim` (417 instancias). |
