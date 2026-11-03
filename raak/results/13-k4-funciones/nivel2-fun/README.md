# RAA k=0 como linea base (relajacion `art`, escalas lineales)

Generado por `analysis/raa_baseline.py` a partir de: results/13-k4-funciones/nivel2-fun/runs.csv.
`art` (AF2) queda archivado: la referencia es **RAA k=0** y contra ella se miden las tecnicas k-nomiales k=2, 3, 4 (k=2 es el binomial del paper [B]).
Celdas = nodos del B&B, metrica principal; CPU secundaria (una sola corrida por configuracion, sin repeticiones).

| comparacion | instancias comparables | celdas identicas | media geom. celdas | gana / empata / pierde (celdas, +-5 %) | media geom. CPU | gana / empata / pierde (CPU) |
|---|---|---|---|---|---|---|
| RAA k=2 (binomial) vs base | 22 | 9 | 0.994 | 4 / 14 / 4 | 1.126 | 4 / 9 / 9 |
| RAA k=3 (k-nomial) vs base | 22 | 9 | 0.930 | 8 / 11 / 3 | 1.060 | 5 / 8 / 9 |
| RAA k=4 (k-nomial) vs base | 22 | 9 | 0.919 | 8 / 12 / 2 | 1.036 | 3 / 9 / 10 |

Instancias en las que alguna configuracion k-nomial (k=2, 3, 4) cambia las celdas: 13 de 22. Instancias en las que la reescritura k=3 llega a extraer bloques: 21.

| archivo | que muestra |
|---|---|
| `dispersion_raa_baseline.png` | Por instancia, x = RAA k=0, y = k=2 (+) y k=3 (x); celdas y CPU; fila superior todas, fila inferior recorte al percentil 90 de la base. Ejes lineales. |
| `perfiles_raa_baseline.png` | Perfiles de desempeno (fraccion de instancias dentro de un factor X de la mejor), eje x lineal. |
| `cociente_por_instancia.png` | Solo las instancias cuyas celdas cambian: cociente k / base, con las celdas de la base bajo cada nombre. |
| `tabla_raa_baseline.csv` | Estado, celdas y CPU de todas las configuraciones por instancia, cocientes, y los contadores RAA-K de la corrida k=3 (productos, con_bloques, bloques, usados, cuadrados, corner). |
| `resumen.json` | Las cifras de arriba por grupo (easy+medium, hard+others, todas), la lista de instancias que cambian y la de instancias con bloques. |
