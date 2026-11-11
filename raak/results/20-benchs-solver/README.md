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
- default+RAA k=6 contra default (15 comunes): celdas 0,720, CPU 0,885. Dietmaier: default 71 889 celdas / 479 s con 23 cajas sin validar; con RAA 33 127 / 240 s y las 54 soluciones validadas. Trigexp2-17 y -19: 40–50 % menos celdas y 25–40 % menos tiempo. Contra: Trigexp2-3 no termina con la relajación añadida (default sí, en 458 s) y Trigexp2-21 tarda 30 % más.

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

## Pendiente de verificar

- Brent-8: las configuraciones que terminan con SUCCESS dan distinto número de cajas solución (AF2 186, RAA 181;
  default 146 + 18 sin validar; X-Newton 169 + 2). La instancia tiene soluciones mal condicionadas y el conteo
  varía en todas las configuraciones, pero no se comprobó que las cajas de una cubran las de otra. Haría falta
  que el CLI escriba las cajas.

## Regenerar

```
python analysis/csp_analisis.py results/20-benchs-solver/csp-60s/runs.csv --pares affine_raa:affine_af2,affine_raa_k6:affine_raa
python analysis/semillas_analisis.py results/20-benchs-solver/semillas
```
