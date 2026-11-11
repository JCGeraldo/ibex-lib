# 20 · benchs/solver con ibexsolve-raak, repeticiones con semilla y ex6_2 a una hora

Corrida única de la noche del 2026-11-11 (02:25–08:46, P=10, máquina sin otro uso). Binario con los
parches 0001–0014 (cota por intervalos, k-nomial sin presupuesto). Cola: `run.sh`, bitácora `cola.log`.
Los tiempos solo se comparan dentro de esta sesión.

| Carpeta | Qué contiene |
|---|---|
| `csp-60s/` | 264 instancias de `benchs/solver` × 5 configuraciones, 60 s |
| `csp-900s/` | 17 instancias con material (`instancias.txt`) × 7 configuraciones, 900 s |
| `ex6_2-3600s/` | `ex6_2_5`, `ex6_2_7`, `ex6_2_13` con `ibexopt-raak`, RAA k=0, 4, 6, 3600 s |
| `semillas/` | 18 sintéticas `synq` n=8 × RAA k=0, 4, 6 × semillas 42, 1, 2, 3, 600 s |
| `csp-default-900s/` | Sesión del día 11-11 (09:53–10:15, `run-dia.sh`): las 17 instancias × default, default+AF2, default+RAA, default+RAA k=6, 900 s |
| `semillas-n03-n05/` | Misma sesión del día: 42 sintéticas `synq` n=3 y n=5 × RAA k=0, 4, 6 × 4 semillas |
| `csp-semillas/` | Tarde del 11-11: las 17 instancias × 4 configuraciones con default × semillas 1, 2, 3, 7 del solver, 900 s |
| `csp-default-60s/` | Tarde del 11-11: 264 instancias × default, default+AF2, default+RAA, default+RAA k=6, 60 s |
| `brent-8/` | Cajas solución de Brent-8 con cinco contractores y comprobación de cobertura |

Cada carpeta trae `runs.csv`, `meta.txt` y `resumen.md` (salida de `analysis/csp_analisis.py` o
`analysis/semillas_analisis.py`). Los logs crudos quedan fuera del repositorio
(`~/ibex-local/results/noche-20261111/`).

Configuraciones del solver (`--ctc`): `default` = contractor de DefaultSolver (HC4, ACID, Newton, X-Newton);
`xn` = solo X-Newton; `affine_<arit>[_k<K>]` = solo la relajación afín (AF2 o RAA, con k-nomial K);
`default+affine_raa_k6` = el contractor por omisión más la relajación RAA k=6.
"Terminada" = SUCCESS, INFEASIBLE o NOT_ALL_VALIDATED.

## Resultados

**1. Solo la relajación, 60 s (264 instancias).** Terminan: default 158, RAA 93, RAA k=6 93, AF2 92, X-Newton 85.
- AF2 contra X-Newton (73 terminadas por ambas): celdas 0,594, CPU 0,515; AF2 termina 19 que X-Newton no y X-Newton 12 que AF2 no.
- RAA contra AF2 (92): mismas celdas en 88; menos en Directkin (4745 → 1763), Pramanik (5461 → 2761), Trigexp2-5 y Brent-8; además RAA cierra Neveu1 y AF2 no.
- k-nomial (RAA k=6 contra RAA): cambia solo Pramanik (2761 → 2737) y Trigexp2-5 (48029 → 47459). En el resto no hay material.
- La relajación sola no reemplaza al contractor por omisión: 6,5 veces más celdas en las 90 comunes; default termina 68 que RAA no, RAA 3 que default no (Discrete-Integral-6, Trigo1-0014, Trigo1-0015).
- 14–15 instancias de n ≥ 400 quedan KILLED en todas las configuraciones (un solo nodo excede el límite).

**2. Instancias con material, 900 s (17).**
- RAA contra AF2: celdas 0,535 y CPU 0,581 en las 8 comunes; RAA además resuelve Dietmaier (165 501 celdas, 710 s) y AF2 no.
- Neveu1: AF2 164 081 celdas / 749 s; RAA 7 033 / 47 s.
- k=4 y k=6 contra RAA k=0: cociente de celdas 1,000 (2 mejoran, 2 empeoran, 5 iguales). En Trigexp2 el k-nomial actúa (hasta 7 millones de productos) pero no cambia el resultado.
- default+RAA k=6 contra default (15 comunes): celdas 0,720, CPU 0,885. Dietmaier: default 71 889 celdas / 479 s con 23 cajas sin validar; con RAA 33 127 / 240 s y las 54 soluciones validadas. Trigexp2-17 y -19: 40–50 % menos celdas y 25–40 % menos tiempo. Contra: Trigexp2-3 no termina con la relajación añadida en esta sesión (default sí, en 458 s; ver la corrección en el resultado 5) y Trigexp2-21 tarda 30 % más.

**3. ex6_2_5, ex6_2_7, ex6_2_13 a 3600 s.** Ninguna cierra con ninguna variante. La cota inferior mejora poco con k:
ex6_2_5 −1218,2 (k=0) → −1195,0 (k=4) → −1189,1 (k=6); ex6_2_7 −22,21 → −21,52 → −21,49; ex6_2_13 sin cambio.

**4. Semillas (synq n=8).** Los cocientes casi no dependen de la semilla:

| par | celdas (mín–máx entre 4 semillas) | CPU (mín–máx) | instancias |
|---|---|---|---|
| k=4 / k=0 | 0,457–0,463 | 0,506–0,515 | 14 |
| k=6 / k=0 | 0,369–0,381 | 0,407–0,421 | 14 |
| k=6 / k=4 | 0,799–0,818 | 0,802–0,824 | 15 |

k=6 gana a k=0 en las 14 instancias con las 4 semillas. Para una misma instancia y variante, las celdas cambian
entre semillas un 2–3 % en mediana (peor caso 37 %).

**5. default con y sin relajación afín, misma sesión (17 instancias, 900 s; 16 terminadas por las cuatro).**

| añadido a default | celdas / default | CPU / default | menos celdas | más celdas |
|---|---|---|---|---|
| AF2 | 0,884 | 1,133 | 11 | 3 |
| RAA | 0,811 | 1,053 | 12 | 2 |
| RAA k=6 | 0,735 | 0,947 | 14 | 0 |

- Esta tabla es de una sola semilla (la 1, por omisión del solver). **La ventaja de RAA k=6 sobre RAA no se sostiene con otras semillas** (resultado 7): venía de Trigexp2-17 y -19, cuyo árbol cambia hasta 2,7 veces según la semilla.
- Dietmaier: default 71 889 celdas con cajas sin validar; +AF2 49 455, también sin validar; +RAA 33 127 y todo validado. Estable entre semillas.
- Corrección al resultado 2: Trigexp2-3 con default+RAA k=6 sí termina (710 s; anoche agotó los 900 s con la máquina más cargada). Tarda 1,65 veces default con las mismas celdas.

**6. Semillas en synq n=3 y n=5 (42 instancias, todas resueltas).** k=4/k=0: celdas 0,638–0,654, CPU 0,688–0,714.
k=6/k=0: celdas 0,628–0,645, CPU 0,674–0,709. k=6/k=4: celdas 0,982–0,986 (el material se agota en k=4).
Por corrida (168): k=6 usa menos celdas que k=0 en 149, las mismas en 14 y más en 5.

**7. default con y sin relajación afín, cuatro semillas del solver (`csp-semillas/`, 17 instancias, 900 s; 16 terminan con todo).**
Media geométrica por instancia sobre las semillas 1, 2, 3 y 7, y luego sobre instancias:

| añadido a default | celdas / default | CPU / default | rango de celdas entre semillas |
|---|---|---|---|
| AF2 | 0,878 | 1,103 | 0,856–0,897 |
| RAA | 0,804 | 1,028 | 0,770–0,822 |
| RAA k=6 | 0,782 | 0,984 | 0,735–0,811 |

RAA contra AF2: celdas 0,917 (0,881–0,960 según la semilla), CPU 0,932. RAA k=6 contra RAA: celdas 0,972 (0,906–1,042), CPU 0,958:
dentro del ruido de la semilla. En Trigexp2-17, RAA k=0 da 17 489, 13 115, 17 925 y 8 805 celdas con las cuatro semillas, y RAA k=6
da 9 305, 12 703, 18 157 y 18 527. La mejora de RAA sobre AF2 sí es estable (Dietmaier, Pramanik y Directkin no cambian con la semilla).
Sonda de anchuras (`tests/csp_width_probe.cpp`): en Trigexp2-17 solo hay bloques de 2 símbolos y la forma afín se estrecha 1 a 4 % en cajas de ancho 1 y menos de 1 % en cajas más chicas.

**8. Conjunto completo con default (`csp-default-60s/`, 264 instancias, 60 s, una semilla).** Terminan: default 159; con AF2, RAA o RAA k=6, 167.
Sobre las 158 comunes: +AF2 celdas 0,672 y CPU 0,902 (0,807 en corridas de 1 s o más); +RAA 0,667 y 0,894; +RAA k=6 0,667 y 0,904.
La relajación usa menos celdas en 102, igual en 39 y más en 17; cierra 9 que default no (Bratu-0060/65/70, Discrete-Integral-6, Katsura-20,
Trigo1-0014 a -0017) contra 1 (Yamamura1-0040sp). RAA contra AF2: 0,993 (distintas en 9 instancias). RAA k=6 contra RAA: 1,000.

## Brent-8: verificado (`brent-8/`)

Con el `eps_min` por omisión (1e-3) las configuraciones dan distinto número de cajas solución (AF2 186, RAA 181,
default 146 + 18 sin validar, X-Newton 169 + 2) y hay soluciones certificadas de una que ninguna caja de otra
contiene, también entre `default` y `xn`, que no usan la relajación afín. No es una pérdida de soluciones de la
relajación: el `Solver` de IBEX, cuando una celda baja de `eps_min`, la reemplaza por la solución que Newton
certifica desde su centro, así que la salida solo es completa con resolución `eps_min`, y Brent-8 tiene
soluciones a menos de 1e-3 entre sí (componentes del orden de 1e-5). Comprobación (`analysis/cajas_cubren.py`,
opción nueva `--boxes` de `ibexsolve-raak`):

- con tolerancia `eps_min`, cada caja solución de cada configuración tiene una caja de todas las demás a esa distancia (0 sin cubrir);
- con `-e 1e-9`, AF2, RAA y default dan las mismas 256 = 2^8 soluciones y se cubren mutuamente sin tolerancia apreciable.

## Regenerar

```
python analysis/csp_analisis.py results/20-benchs-solver/csp-60s/runs.csv --pares affine_raa:affine_af2,affine_raa_k6:affine_raa
python analysis/semillas_analisis.py results/20-benchs-solver/semillas
```
