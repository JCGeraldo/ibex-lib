# 24 · Repetición de todos los experimentos con el binario del parche 0015

Del 15 al 20 de noviembre de 2026. Mismos experimentos de `22-barrido-final` y `20-benchs-solver`, ahora con
los parches 0001–0015 (`ibexopt-raak` `48e036b07056`, `ibexsolve-raak` `ede806a8940c`, `range_eval`
`6063e44af9ba`; ibex-lib `24480efb`). Cota k-nomial por intervalos, sin presupuesto de búsqueda, relajación
`art`. Lanzado con `cola.sh` (etapas 1 a 7) y `cola2.sh` (etapas 8 y 9); el avance quedó en `cola.log`.

## Sesiones

Los tiempos de CPU solo son comparables dentro de una misma sesión.

| Sesión | Etapas | Notas |
|---|---|---|
| 15-11 22:41 a 16-11 15:25 | 1 a 6 completas y 1305 de las 1320 corridas de la 7 | Una sola sesión, P=10. La máquina virtual de WSL se detuvo a las 15:25 (Windows no se reinició ni se suspendió; causa no determinada). |
| 16-11 19:12 a 19:22 | Las 15 corridas restantes de la etapa 7 | `Yamamura1-0400`, `Yamamura1-1000sp` y `yamamura8a`, con P=3. |
| 20-11 17:15 a 19:30 | 8 y 9 | Etapa 8 con P=9 sobre 262 sistemas y después los dos `Yamamura` grandes con P=2. |

El primer lanzamiento del 15-11 se saltó la etapa 1 por la guarda de `wsl_barrido_final.sh` (su `pgrep`
coincidió con el propio comando de lanzamiento); se detuvo a los 30 segundos, se borró lo parcial y se relanzó.

`Yamamura1-0400` llega al tope de 4 GB por proceso (estado `MEM`) y `Yamamura1-1000sp` se corta por tiempo
(`KILLED`) en todas las configuraciones. Con diez de esas corridas a la vez sobre los 11 GB de WSL es posible
que la caída del 16-11 haya sido por memoria; no quedó comprobado.

## Etapas

| Carpeta | Etapa | Qué es |
|---|---|---|
| `nivel2/` | 1 | Barrido final de optimización: 136 instancias × 6 variantes (AF2, RAA k=0, 2, 3, 4, 6), 1800 s, semilla 42. 816 corridas. |
| `semillas/`, `semillas-n03-n05/` | 2 | `synq` con n=8 y con n=3, 5; semillas 42, 1, 2, 3; RAA k=0, 4, 6; 600 s. |
| `csp-900s/` | 3 | 17 sistemas × 7 configuraciones de `ibexsolve-raak`, 900 s. |
| `csp-default-900s/` | 4 | Los mismos 17 sistemas, contractor por omisión con una relajación afín agregada, 900 s. |
| `csp-semillas/` | 5 | Lo anterior con las semillas 1, 2, 3, 7 (`bin-seed.sh`). |
| `tiempos/` | 6 | Costo por evaluación afín: `range_eval` de los binarios 0014 y 0015 alternados, 3 repeticiones, un proceso. |
| `csp-60s/` | 7 | 264 sistemas × 5 configuraciones (relajación como único contractor), 60 s. |
| `csp-default-60s/` | 8 | 264 sistemas, contractor por omisión con una relajación afín agregada, 60 s. |
| `ex6_2-3600s/` | 9 | `ex6_2_5`, `ex6_2_7`, `ex6_2_13` con RAA k=0, 4, 6, una hora. |

Cada carpeta tiene su `runs.csv`, su `meta.txt` y, donde corresponde, un `resumen.md` con la salida del
script de análisis (`analysis/barrido_final_analisis.py`, `semillas_analisis.py`, `csp_analisis.py`,
`csp_semillas.py`, `tiempos_binarios.py`). `nivel2/perfiles.txt` es la salida de `analysis/perfil_stats.py`.

## Resultados

**Optimización (etapa 1).** Celdas / CPU frente a RAA k=0, media geométrica sobre las instancias resueltas
por las cinco variantes RAA:

| familia | n | k=2 | k=3 | k=4 | k=6 |
|---|---|---|---|---|---|
| benchmarks | 6 | 0.972 / 0.971 | 0.957 / 0.968 | 0.957 / 0.996 | 0.957 / 0.997 |
| synq | 61 | 0.764 / 0.809 | 0.640 / 0.680 | 0.575 / 0.608 | 0.532 / 0.566 |
| synl | 24 | 0.897 / 0.974 | 0.871 / 0.954 | 0.840 / 0.958 | 0.811 / 0.844 |
| synt | 23 | 0.956 / 0.881 | 0.922 / 0.820 | 0.891 / 0.816 | 0.887 / 0.788 |

- Resueltas en `synq`: AF2 56, RAA k=0, 2, 3, 4: 61, k=6: 62. Frente a `22-barrido-final` (binario 0014) los
  cocientes cambian en el segundo o tercer decimal (benchmarks 0.966 → 0.957; `synq` 0.540 → 0.532).
- Las instancias que cierran en milisegundos meten ruido en los cocientes de CPU (en `synt` el de tiempo sale
  menor que el de celdas). Con las instancias de al menos 1 s, k=6 da 0.415 / 0.461 en `synq` (23),
  0.668 / 0.729 en `synl` (10), 0.831 / 0.895 en `synt` (9).
- 115 instancias resueltas por alguna variante; k=6 tiene el árbol más chico en 100 y queda a menos de 5 % en
  105. k=6 explora más celdas que k=0 en 5 de 114, todas con árboles de menos de 3000 celdas.
- RAA k=0 frente a AF2 en `synq`: 0.638 de las celdas y 0.701 del tiempo (56 instancias).
- Consistencia de óptimos: 114 instancias revisadas, 0 inconsistencias.

**Semillas (etapa 2).** `synq` n=8: k=6 / k=0 entre 0.368 y 0.379 en celdas según la semilla; k=4 / k=0 entre
0.457 y 0.461. k=6 gana a k=0 en las 14 instancias comparables con las cuatro semillas. `synq` n=3, 5 (168
corridas): k=6 explora menos celdas que k=0 en 151, igual en 12 y más en 5.

**CSP (etapas 3, 4, 5, 7, 8).** La reescritura no tiene efecto medible:

- Relajación como único contractor, 264 sistemas a 60 s: terminan 159 (por omisión), 86 (X-Newton), 94 (AF2),
  96 (RAA) y 96 (RAA k=6). k=6 / k=0: 1.000 en celdas.
- 17 sistemas a 900 s: RAA usa 0.535 de las celdas y 0.572 del tiempo de AF2 en los 8 que terminan ambas, y es
  la única que cierra `Dietmaier`.
- Contractor por omisión con relajación agregada, 264 sistemas a 60 s (159 terminados por las cuatro
  configuraciones): celdas / CPU frente al contractor solo 0.672 / 0.901 (AF2), 0.667 / 0.896 (RAA),
  0.667 / 0.898 (RAA k=6).
- Lo mismo con cuatro semillas, 16 sistemas a 900 s: 0.878 (AF2), 0.804 (RAA), 0.786 (RAA k=6) en celdas;
  k=6 / k=0 0.977 con un rango entre semillas de 0.900 a 1.038.
- La única diferencia en número de soluciones es `Brent-8` (186 con AF2, 181 con RAA), ya revisada en
  `20-benchs-solver/brent-8/`.

**Costo por evaluación (etapa 6).** Frente a RAA k=0, una evaluación con reescritura cuesta 1.084 (k=3),
1.103 (k=4) y 1.065 (k=6) con el binario 0015, y 1.051, 1.069 y 1.038 con el 0014: la normalización del
parche 0015 agrega unos 3 puntos. Las variantes sin reescritura, que no ejecutan ese código, salen 2 a 3 %
más lentas con 0015 (deriva entre binarios).

**`ex6_2` a una hora (etapa 9).** Ninguna cierra. Cota inferior con k=0 / k=4 / k=6: `ex6_2_5` −1197.92 /
−1164.50 / −1167.51; `ex6_2_7` −21.880 / −21.258 / −21.240; `ex6_2_13` −0.2162448 / −0.2162432 / −0.2162432.

## Alcance

No se repitieron con este binario el costo del rigor (`18-parche-0012`), el costo de k=n con la búsqueda
truncada (`16-k-por-densidad`) ni las pruebas de contención (`17-lema-conservatividad`, `19-cabos-sueltos`).
