# To-do de la reunion del 21-10: k=4, tiempos de linealizacion y familias con funciones (28 de octubre de 2026)

Informe: "Informe RAA-K 2: k=4, tiempos y familias con funciones" (Claude Docs, 28-10-2026).

| carpeta | que es |
|---|---|
| `nivel1-k4/` | `tests/range_eval.cpp` con 8 variantes (af2_k0, af2_k3, raa_k0, raa_k2, raa_k3, raa_k4, aa_k0, aa_k3) sobre reales + sinteticas `synq`: `range.csv`, `range_log.txt`, `resumen_nivel1_k4.csv` (ancho medio geom. frente a raa_k0), `sinteticas_por_n_nivel1.csv`. |
| `nivel1-fun/` | Lo mismo sobre `instancias/sinteticas-log/` (synl) y `instancias/sinteticas-fun/` (synt). |
| `nivel2-k4/` | Barrido `art_raa_k4` (1800 s, 10 procesos, 28-10) anadido a los `runs.csv` del 20-10 (k=0, 2, 3) de reales y sinteticas; `analysis/raa_baseline.py --cmp art_raa_k2,art_raa_k3,art_raa_k4` y `sinteticas_resumen.py` (tabla por instancia, `resumen.json`, `por_n.csv`, `timeouts.csv`, figuras). La CPU de k=4 NO es comparable con la de k=0, 2, 3 (dias distintos). |
| `nivel2-log/`, `nivel2-fun/` | Barridos de las familias synl y synt con las 4 configuraciones en la misma sesion (28-10, 1800 s, 10 procesos): `runs.csv`, `meta.txt` y el mismo analisis. Aqui la CPU si es comparable entre configuraciones. |
| `tiempos/` | `range_eval` sobre las 78 sinteticas `synq` con la maquina en reposo y un solo proceso (`range.csv`, `meta.txt`); `analysis/tiempos_linealizacion.py`: `tiempos_por_n.csv` (us por evaluacion afin), `tiempos_relativos.csv`, `costo_por_operacion.csv`, `tiempos_por_n.png`. `perf/`: perfiles de `ibexopt-raak` con perf (ver su README). |

Cifras principales: nivel 2 sinteticas `synq` (64 resueltas por las 4), celdas frente a RAA k=0: k=2 0.794, k=3 0.672, k=4 0.618; k=4 nunca pierde contra k=3.
Reales: k=4 identico a k=3. Familia log (24): k=3 0.861, k=4 0.842. Familia trig/exp (22): k=3 0.930, k=4 0.919.
Tiempo por evaluacion afin (n=10, reposo): raa_k0 44.6 us, k=2 79.4, k=3 80.2, k=4 124.2; perf: knomial_rewrite 17 % del tiempo del solver con k=3, 3/4 en reservas de memoria.
