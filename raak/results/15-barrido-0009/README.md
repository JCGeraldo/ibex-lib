# Barrido completo del nivel 2 con el parche 0009 (29-10-2026)

Una sola sesión (03:35 a 09:39, 6 h 4 min, 10 procesos, límite 1800 s de CPU) con `ibexopt-raak` recompilado con el parche 0009
(`knomial_rewrite` sin reservas de memoria por llamada, resultados idénticos bit a bit): k=0, 2, 3 y 4 de `--lr=art --arith=raa`
sobre reales (10), `synq` (78), `synl` (24) y `synt` (24). 544 corridas: 458 resueltas, 86 timeouts, 0 interrumpidas.
Como todo corrió en la misma sesión y con el mismo binario, aquí la CPU sí es comparable entre variantes y entre familias.

| archivo | qué es |
|---|---|
| `runs_reales.csv`, `runs_sinteticas.csv`, `runs_log.csv`, `runs_fun.csv` | Las corridas (una fila por instancia y variante). `meta.txt`, `run_all.sh`: la sesión. |
| `nivel2-synq/` | `raa_baseline.py --cmp art_raa_k2,art_raa_k3,art_raa_k4` y `sinteticas_resumen.py` sobre reales + synq (tabla por instancia, `resumen.json`, `por_n.csv`, `timeouts.csv`, figuras). |
| `nivel2-log/`, `nivel2-fun/` | Lo mismo sobre reales + synl y reales + synt. |
| `tiempos/` | `range_eval` sobre las 78 synq en reposo con el binario nuevo (`range.csv.gz`) y `tiempos_linealizacion.py` (us por evaluación afín, relativos, costo por bloque). |
| `comparacion_sesiones.txt`, `cpu_vs_sesiones_anteriores.csv` | Celdas y CPU de esta sesión frente a las del 20-10 y 28-10, timeouts que ahora se resuelven, nivel 1 antes/después. |
| `figuras/` | `sobrecosto_por_evaluacion.png` (nivel 1, antes y después del parche), `cpu_vs_celdas.png` (nivel 2, CPU frente a celdas). `analysis/parche0009_figuras.py`. |

## Resultados

Celdas idénticas a las sesiones anteriores en las 449 corridas resueltas en ambas (el parche no cambia nada). Timeouts: 86 frente a 95
antes; 9 corridas que antes agotaban los 1800 s ahora terminan (7 en synq, 2 en synt), por la velocidad.

| familia | resueltas por las 4 | k=2 celdas / CPU | k=3 celdas / CPU | k=4 celdas / CPU | k4 vs k3 celdas |
|---|---|---|---|---|---|
| reales | 6 | 0.977 / 0.976 | 0.966 / 0.962 | 0.966 / 0.959 | 1.000 |
| synq | 61 | 0.778 / 0.810 | 0.646 / 0.682 | 0.588 / 0.620 | 0.910 (34 gana, 22 idénticas, 0 pierde) |
| synl | 24 | 0.919 / 0.884 | 0.861 / 0.927 | 0.842 / 0.847 | 0.978 |
| synt | 23 | 0.990 / 0.991 | 0.922 / 0.878 | 0.904 / 0.873 | 0.981 |

(medias geométricas de los cocientes variante / RAA k=0). En synq la CPU queda a 3-4 puntos de las celdas: el k-nomial ya no cuesta
tiempo apreciable por nodo. Antes del parche (sesión del 20-10) k=3 daba celdas 0.672 y CPU 0.796.

Nivel 1 en reposo, us por evaluación afín relativo a RAA k=0 (mediana, n=3/5/8/10): k=2 1.11/1.14/1.17/1.18 (antes 1.46-1.49),
k=3 1.04/1.02/1.03/1.04 (antes 1.23-1.31), k=4 1.06/1.04/1.05/1.06 (antes 1.23-1.49). Los tiempos absolutos de esta sesión son
también más bajos para AF2 k=0, que no usa el k-nomial (0.6-0.8 de los del 28-10), así que la máquina del 28-10 no estaba tan en reposo
como se creía: la comparación válida es la relativa dentro de cada sesión.

Timeouts de synq con las 4 variantes agotadas (15): brecha media k0 16.9, k2 16.1, k3 14.8, k4 13.7; k4 con mejor cota inferior que k3
en 14 de 15. `synq_n10_d20_posneg_normal_s2` ahora la resuelven k0, k2 y k3 (antes solo k4); `synq_n08_d20_pos_normal_s3` y
`synq_n10_d90_posneg_normal_s2` solo k4.

## Los dos binarios en la misma sesión (`2binarios/`, 29-10, 11:52 a 13:50)

Para separar el efecto del parche del de la máquina se compiló también el binario sin el 0009 (parches 0001 a 0008) y se corrieron
los dos a la vez, cada uno con 5 procesos, sobre las 67 instancias (reales + synq) que las cuatro configuraciones resuelven, con
k=0, 2, 3, 4 (268 corridas por binario). Antes, `range_eval` de los dos binarios alternados 3 veces sobre las 78 synq en reposo.

- Celdas idénticas en las 268 corridas; todas resueltas con los dos binarios.
- Nivel 1, µs por evaluación afín 0009 / pre0009 (n = 3, 5, 8, 10): AF2 k=0 y AA k=0, que no usan el k-nomial, 0.98 a 1.07;
  RAA k=0 0.91 a 0.99; k=2 0.80, 0.85, 0.74, 0.76; k=3 0.74, 0.76, 0.63, 0.61; k=4 0.77, 0.72, 0.54, 0.42.
- Solver, CPU 0009 / pre0009 (media geométrica, misma instancia): k=0 0.993, k=2 0.954, k=3 0.916, k=4 0.896; sobre las corridas de
  10 s o más: k=3 0.870, k=4 0.791. En synq con n=8: k=3 0.82, k=4 0.75.
- Dentro de cada binario, CPU k / k=0 sobre las 67: pre0009 k2 0.879, k3 0.765, k4 0.725; con 0009 k2 0.844, k3 0.706, k4 0.655
  (celdas 0.794, 0.670, 0.614 en ambos).

El efecto en el solver (8 a 20 %) es menor que el efecto por evaluación (25 a 60 %) porque la reescritura era el 17 % del tiempo del
solver con k=3; el resto (producto de AF2, linealizador, politopo) no cambia. Es coherente con el perfil del 28-10.
Los tiempos absolutos de la sesión completa del 29-10 frente al 20-10 incluyen además un factor de máquina (RAA k=0: 0.66 en synq), que
no es del parche.

| archivo | qué es |
|---|---|
| `2binarios/runs_pre0009.csv`, `runs_0009.csv`, `instancias.txt`, `meta.txt`, `run_both.sh` | Las dos corridas del solver y la lista de instancias (enlaces en `~/ibex-local/instancias/comparacion-2binarios`). |
| `2binarios/resumen_nivel2.txt` | Cocientes de CPU por variante, por n y por instancia real; k/k0 dentro de cada binario. |
| `2binarios/nivel1/` | `range_eval` alternado (3 repeticiones por binario, `range_<bin>_r<i>.csv.gz`) y `resumen_nivel1.txt`. |
