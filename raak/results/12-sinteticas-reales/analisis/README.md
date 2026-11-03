# RAA k=0 como linea base (relajacion `art`, escalas lineales)

Generado por `analysis/raa_baseline.py` a partir de: results/12-sinteticas-reales/nivel2-reales/runs.csv, results/12-sinteticas-reales/nivel2-sinteticas/runs.csv.
`art` (AF2) queda archivado: la referencia es **RAA k=0** y contra ella se miden las tecnicas k-nomiales k=2 (binomial, paper [B]) y k=3.
Celdas = nodos del B&B, metrica principal; CPU secundaria (una sola corrida por configuracion, sin repeticiones).

| comparacion | instancias comparables | celdas identicas | media geom. celdas | gana / empata / pierde (celdas, +-5 %) | media geom. CPU | gana / empata / pierde (CPU) |
|---|---|---|---|---|---|---|
| RAA k=2 (binomial) vs base | 64 | 6 | 0.794 | 50 / 12 / 2 | 0.909 | 43 / 10 / 11 |
| RAA k=3 (k-nomial) vs base | 64 | 5 | 0.672 | 53 / 10 / 1 | 0.796 | 50 / 4 / 10 |

Instancias en las que k=2 o k=3 cambian las celdas: 59 de 64. Instancias en las que la reescritura k=3 llega a extraer bloques: 88.

| archivo | que muestra |
|---|---|
| `dispersion_raa_baseline.png` | Por instancia, x = RAA k=0, y = k=2 (+) y k=3 (x); celdas y CPU; fila superior todas, fila inferior recorte al percentil 90 de la base. Ejes lineales. |
| `perfiles_raa_baseline.png` | Perfiles de desempeno (fraccion de instancias dentro de un factor X de la mejor), eje x lineal. |
| `cociente_por_instancia.png` | Solo las instancias cuyas celdas cambian: cociente k / base, con las celdas de la base bajo cada nombre. |
| `tabla_raa_baseline.csv` | Estado, celdas y CPU de las tres configuraciones por instancia, cocientes, y los contadores RAA-K de la corrida k=3 (productos, con_bloques, bloques, usados, cuadrados, corner). |
| `resumen.json` | Las cifras de arriba por grupo (easy+medium, hard+others, todas), la lista de instancias que cambian y la de instancias con bloques. |
