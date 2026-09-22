# Fase 3 — Evaluación experimental

Fecha de las corridas: 2026-09-21/22. Binario `ibexopt-raak` con ibex-affine `c219009` + parches
0001, 0002, 0004–0008; ibex-lib `5e51fffc` + 0003. Máquina: WSL Ubuntu 24.04, 16 hilos, 11 GiB.
Linealización de `sin`/`cos`: `--trig=auto` (cuerda; ver Fase 2).

## Las seis variantes

| etiqueta | `ibexopt-raak` | aritmética | k-nomial |
|---|---|---|---|
| `af2_k0` | `--arith=af2 --knomial_k=0` | fAF2 original del plugin (bit a bit) | no |
| `af2_k3` | `--arith=af2 --knomial_k=3` | fAF2 | sí (bloques ≤ 3) |
| `raa_k0` | `--arith=raa --knomial_k=0` | RAA de [A]: Q simetrizada, cuadrados de Chebyshev, corner test | no |
| `raa_k3` | `--arith=raa --knomial_k=3` | RAA | sí |
| `aa_k0`  | `--arith=aa --knomial_k=0`  | AA tradicional (`Affine3`, un símbolo nuevo por operación no afín) | no |
| `aa_k3`  | `--arith=aa --knomial_k=3`  | AA | sí |
| `xn`     | `--lr=xn`                   | control sin aritmética afín (X-Taylor) | — |

Separación de efectos: *aritmética* = `X_k0` frente a `af2_k0`; *k-nomial* = `X_k3` frente a `X_k0`
dentro de cada aritmética; *total* = `X_k3` frente a `af2_k0`.

## Nivel 1 — rangos, sin resolver (`tests/range_eval.cpp`)

Para cada instancia de `benchs/optim` (todos los conjuntos: `easy`, `medium`, `hard`, `others`,
`blowup`, `unsolved`, `benchs-unconstrainedoptim`) se evalúan el objetivo y hasta 50 restricciones
escalares sobre 9 cajas: la caja inicial (componentes no acotadas recortadas a ±10⁴ y contadas en
`clipped`) y 2 sub-cajas aleatorias por cada anchura relativa 1/2, 1/4, 1/8, 1/16, que imitan las
cajas que ve el B&B. Métricas por (instancia, función, caja, variante): anchura de la forma afín,
anchura del rango muestreado (200 puntos + centro: aproximación *interior* del rango real),
sobreestimación = cociente de ambas, parte no lineal `rad(itv) − Σ|aᵢ|` (comparable entre AF2 y AA),
violaciones de contención puntual, si la variante llegó a reemplazar alguna cota (`k_used`) y el
tiempo. Resultados: `results/fase3-<fecha>/nivel1/` (`range.csv.gz`, `analisis/nivel1_tabla.md`,
gráficos). Ver la sección de resultados más abajo.

## Nivel 2 — solver (`scripts/wsl_fase3_sweep.sh`)

**Estrategia de cómputo (definida antes de lanzar).** El plan pide ≥ 30 min por instancia. Con la
línea base de 60 s (133 instancias de `easy`+`medium`, `compo`) solo 2 instancias agotaban el tiempo
y el percentil 90 de CPU era 3.8 s, así que el coste lo dominan las pocas instancias difíciles:
≈ 13 configuraciones × ~4 instancias × 1800 s ≈ 26 h de CPU, que con 12 procesos en paralelo son
≈ 2–3 h de pared por etapa. Por eso:

- `-t 1800` (CPU, medido por el propio optimizador), 12 procesos en paralelo (16 hilos: quedan 4
  para el sistema y el nivel 1), sin límite adicional de memoria (11 GiB para 12 procesos).
- Cuatro etapas encadenadas, cada una reanudable (una fila por corrida; se saltan las hechas):
  **A** `easy`+`medium` × `compo` (6 variantes + `xn`) → **B** `easy`+`medium` × `art` (6) →
  **C** `hard`+`others` × `compo` (6 + `xn`) → **D** `hard`+`others` × `art` (6).
  `compo` (X-Taylor ∘ afín) va primero porque es la relajación en la que el trabajo previo vio el
  efecto positivo del k-nomial; `art` aísla la relajación afín sola. `blowup` y `unsolved` (63
  instancias, casi todas sin resolver a 60 s) quedan fuera del barrido principal: costarían ≈ 40 h
  de pared y aportarían casi solo `TIME_OUT`.
- Instancias ordenadas por dificultad creciente (CPU de la línea base), para que la consolidación
  parcial (`wsl_fase3_status.sh`) sea útil desde el principio.
- Registro por corrida: estado, celdas, `[f_lb, f_ub]`, CPU, pared, código de salida, y las líneas
  `RAA-K stats` / `TRIG stats` (cuántas veces actuó cada mecanismo).

**Análisis (`analysis/analyze_sweep.py`).** Estados por variante; frente a la base `af2_k0`:
victorias/empates/derrotas en celdas y en CPU (umbral ±5 %) y medias geométricas sobre las
instancias resueltas por ambas; separación de efectos; perfiles de desempeño (Dolan–Moré) en CPU y
celdas; dispersión log-log por instancia; tabla consolidada. Cada carpeta de resultados lleva un
`README.md` que explica sus archivos.

## Resultados del nivel 1 (`results/fase3-20260921/nivel1/`)

380 instancias cargadas (de 390; 10 no se pudieron parsear), 20 608 ternas (instancia, función,
caja), 124 674 evaluaciones afines. **Contención: 0 violaciones** puntuales y 0 de intervalo, en las
seis variantes. 97 formas inactivas por variante (funciones con singularidad dentro de la caja).

| variante | caja inicial | 1/2 | 1/4 | 1/8 | 1/16 | todas | no linearizables | filas donde actuó | µs/eval |
|---|---|---|---|---|---|---|---|---|---|
| AF2 | 2.051 | 1.806 | 1.620 | 1.505 | 1.445 | 1.633 | 19 | — | 72 |
| AF2 + k-nomial | 2.050 | 1.805 | 1.619 | 1.505 | 1.444 | 1.632 | 19 | 522 | 72 |
| RAA | 2.021 | 1.782 | 1.603 | 1.492 | 1.434 | 1.616 | 19 | 1237 | 70 |
| RAA + k-nomial | 2.020 | 1.782 | 1.603 | 1.492 | 1.434 | 1.615 | 19 | 1366 | 71 |
| AA | 2.026 | 1.790 | 1.606 | 1.496 | 1.436 | 1.620 | 0 | — | 1190 |
| AA + k-nomial | 2.021 | 1.785 | 1.601 | 1.492 | 1.432 | 1.615 | 0 | 2039 | 1099 |
| *extensión natural de intervalos* | 1.828 | 1.646 | 1.535 | 1.476 | 1.459 | 1.557 | | | |

(sobreestimación = anchura de la forma / anchura del rango muestreado, media geométrica)

| efecto | comparación | más estrecha (>5 %) | igual | más ancha (>5 %) | idénticas bit a bit | media geom. |
|---|---|---|---|---|---|---|
| aritmética | RAA / AF2 | 577 | 19 934 | **0** | 19 371 | 0.990 |
| aritmética | AA / AF2 | 515 | 19 767 | 229 | 17 640 | 0.992 |
| k-nomial | AF2+k / AF2 | 46 | 20 465 | 0 | 20 015 | 0.9997 |
| k-nomial | RAA+k / RAA | 42 | 20 469 | 0 | 20 086 | 0.9998 |
| k-nomial | AA+k / AA | 224 | 20 287 | 0 | 18 642 | 0.997 |
| total | RAA+k / AF2 | 609 | 19 902 | 0 | 19 228 | 0.990 |

Lecturas:

1. **RAA nunca es más ancha que AF2 y la mejora en 577 de 20 511 casos** (por construcción: cada
   cota alternativa se usa solo si estrecha). El efecto agregado es pequeño (−1 %) porque la mayoría
   de las funciones de los benchmarks son productos de variables sueltas, donde RAA = AF2 (Prop. 1
   de [A]). Donde actúa, actúa mucho: en `benchs-unconstrainedoptim` (funciones densas en `sqr`,
   `sin`, `cos`) pasa de 9.68× a 8.72×, y en `medium` de 1.476 a 1.467.
2. **AA (tradicional) es un arma de doble filo**: gana en 515 casos (los productos de formas con
   residuo, donde el símbolo nuevo conserva correlación) pero pierde en 229 (`blowup`, `unsolved`,
   `medium`, `others`: cadenas largas de operaciones no afines, donde acumula símbolos). Es además
   **15 veces más lenta** por evaluación (listas dispersas). Nunca deja formas no linearizables.
3. **El k-nomial casi no actúa sobre AF2/RAA en el nivel 1** (46 y 42 casos): necesita que dos
   factores compartan ≥ 2 símbolos con diagonal del mismo signo, algo raro en modelos escritos
   monomio a monomio (misma conclusión que el trabajo previo, §13). Sobre AA actúa 5 veces más
   (224 casos) y sin perder nunca, porque en AA los factores de un producto arrastran más símbolos
   comunes (los rayos nuevos de operaciones previas).
4. **Sobreestimación frente a la extensión de intervalos**: en las cajas grandes (inicial y 1/2)
   las formas afines son *peores* que los intervalos (2.05 frente a 1.83): la linealización de
   operaciones no lineales sobre dominios anchos acumula error; a partir de 1/8 de la caja las
   afines ganan (1.49 frente a 1.48 y 1.43 frente a 1.46). Es lo esperado y justifica que el B&B use
   `compo` (intersección con X-Taylor) y no `art` sola.
5. **19 formas AF2 no linearizables** (todas en `schafferf7-*`, `stretchedv*`, `f2`: `sin` de un
   argumento de ancho ≥ 2π colapsa a intervalo y la forma pierde sus símbolos): el linearizador las
   descarta, mientras que AA las conserva. En el barrido del nivel 2 estas instancias no están
   (`benchs-unconstrainedoptim` no forma parte de las etapas A–D).

Gráficos: `analisis/nivel1_gm_por_escala.png` (sobreestimación por variante y tamaño de caja,
con la extensión de intervalos como referencia), `analisis/nivel1_efectos.png` (casos más
estrechos / más anchos por par). Tabla completa en `analisis/nivel1_tabla.md`.

## Resultados del nivel 2

### Etapa A — `easy` + `medium`, relajación `compo` (132 instancias × 7 configuraciones, `-t 1800`)

`results/fase3-20260921/A_easy_medium_compo/`. Todas las configuraciones terminan con el mismo
estado en las 132 instancias: 125 `SUCCESS`, 1 `INFEASIBLE`, 1 `NO_FEASIBLE_FOUND`, 4 `UNBOUNDED_OBJ`
y 1 `UNREACHED_PREC` (`medium/ex6_2_6`: el B&B agota las cajas sin alcanzar la precisión; de 508 s
con RAA+k a 1249 s con AA). Nadie resuelve algo que otro no resuelva. Óptimos compatibles en todas.

| variante | celdas gana / empata / pierde | celdas media geom. | CPU gana / empata / pierde | CPU media geom. | CPU total (h) |
|---|---|---|---|---|---|
| AF2 (base) | — | 1 | — | 1 | 0.35 |
| AF2 + k-nomial | 7 / 113 / 2 | 0.994 | 17 / 91 / 18 | 0.990 | 0.34 |
| RAA | 5 / 111 / 6 | 0.984 | 22 / 81 / 23 | 0.990 | 0.31 |
| RAA + k-nomial | 8 / 109 / 5 | 0.982 | 18 / 73 / 35 | 1.000 | 0.30 |
| AA | 27 / 63 / 32 | 0.946 | 23 / 30 / 73 | 1.039 | 0.50 |
| **AA + k-nomial** | **27 / 74 / 21** | **0.905** | 25 / 27 / 74 | 1.009 | 0.37 |
| X-Taylor (control) | 19 / 42 / 61 | 1.443 | 56 / 14 / 56 | 1.272 | 0.55 |

(122 instancias resueltas por ambas; gana = cociente < 0.95, pierde = > 1.05; media geométrica del
cociente variante / base)

| efecto | comparación | celdas gana / empata / pierde | celdas media geom. | CPU media geom. |
|---|---|---|---|---|
| aritmética | RAA / AF2 | 5 / 111 / 6 | 0.984 | 0.990 |
| aritmética | AA / AF2 | 27 / 63 / 32 | 0.946 | 1.039 |
| k-nomial | AF2+k / AF2 | 7 / 113 / 2 | 0.994 | 0.990 |
| k-nomial | RAA+k / RAA | 4 / 116 / 2 | 0.998 | 1.011 |
| k-nomial | **AA+k / AA** | **24 / 83 / 15** | **0.957** | **0.971** |
| total | RAA+k / AF2 | 8 / 109 / 5 | 0.982 | 1.000 |
| total | AA+k / AF2 | 27 / 74 / 21 | 0.905 | 1.009 |

Lecturas:

1. **Las tres aritméticas afines dominan al control X-Taylor** (celdas ×0.69, CPU ×0.79 frente a
   `xn`): la relajación afín aporta, como ya se sabía.
2. **RAA frente a AF2 es casi neutra en `easy`+`medium`** (celdas 0.984, 5 gana / 6 pierde). Sus
   dos mejoras grandes históricas se mantienen (`ex8_4_4bis`: 83 220 → 8 618 celdas y 127 → 15 s;
   `bearing`: 25 704 → 15 210 celdas), ambas por los cuadrados de Chebyshev; AA, que ya tenía ese
   cuadrado, también resuelve `ex8_4_4bis` en 8 560 celdas. En el resto RAA = AF2 (Prop. 1 de [A]:
   los benchmarks son mayormente productos de variables sueltas) y las diferencias restantes son
   ruido del recorrido del B&B.
3. **AA tradicional es la más distinta**: gana en 27 instancias y pierde en 32 (media 0.946 en
   celdas), pero cuesta más CPU (1.039; sus listas dispersas son ~15 veces más lentas por
   evaluación, aunque el LP y la propagación diluyen ese coste en el B&B).
4. **El k-nomial actúa poco sobre AF2/RAA y mucho sobre AA.** Sobre AF2/RAA solo entra en la
   familia `ex14_2_*` (5 instancias con bloques; efecto 0.994 / 0.998, pero sin perder: 7–4 gana,
   2 pierde). Sobre AA actúa en 63 instancias (los rayos que AA crea en cada operación dan a los
   factores símbolos comunes) y **mejora las celdas en 24, empeora en 15, media geométrica 0.957,
   y baja la CPU (0.971)**: es la única combinación en la que el k-nomial reduce a la vez celdas y
   tiempo. La mejor variante en celdas de la etapa es **AA + k-nomial (0.905 frente a AF2)**, con
   CPU equivalente a AF2 (1.009).
5. `ex6_2_6` (la única no resuelta): AF2 894 164 celdas → AF2+k 822 338 → AA+k 857 482, frente a
   AA 1 596 408 y `xn` 1 834 760: el k-nomial reduce el trabajo en la instancia más dura en las tres
   aritméticas.

Gráficos: `analisis/nivel2_perfil_compo.png` (perfiles de desempeño en CPU y celdas),
`analisis/nivel2_dispersion_compo.png` (celdas y CPU de cada variante frente a AF2, log-log).
Tablas completas y consolidada por instancia: `analisis/nivel2_tabla.md`.

### Etapa B — `easy` + `medium`, relajación `art` (132 instancias × 6 variantes, `-t 1800`)

`results/fase3-20260921/B_easy_medium_art/`. Mismos estados en las seis variantes (125 `SUCCESS`,
1 `INFEASIBLE`, 1 `NO_FEASIBLE_FOUND`, 4 `UNBOUNDED_OBJ`); `ex6_2_6` agota los 1800 s en todas
(con `art` sola es más dura que con `compo`: 3.8 M de celdas frente a 0.9 M en la etapa A).

| variante | celdas gana / empata / pierde | celdas media geom. | CPU gana / empata / pierde | CPU media geom. |
|---|---|---|---|---|
| AF2 (base) | — | 1 | — | 1 |
| AF2 + k-nomial | 2 / 115 / 5 | 1.002 | 27 / 79 / 20 | 0.996 |
| RAA | 5 / 113 / 4 | 0.979 | 27 / 79 / 20 | **0.969** |
| RAA + k-nomial | 4 / 113 / 5 | 0.984 | 30 / 67 / 29 | 0.986 |
| AA | 18 / 64 / 40 | 1.029 | 18 / 32 / 76 | 1.159 |
| AA + k-nomial | 19 / 79 / 24 | 0.975 | 19 / 25 / 82 | 1.132 |

| efecto | comparación | celdas gana / empata / pierde | celdas media geom. | CPU media geom. |
|---|---|---|---|---|
| aritmética | RAA / AF2 | 5 / 113 / 4 | 0.979 | 0.969 |
| aritmética | AA / AF2 | 18 / 64 / 40 | 1.029 | 1.159 |
| k-nomial | AF2+k / AF2 | 2 / 115 / 5 | 1.002 | 0.996 |
| k-nomial | RAA+k / RAA | 3 / 116 / 3 | 1.005 | 1.017 |
| k-nomial | **AA+k / AA** | **29 / 86 / 7** | **0.948** | **0.977** |

Lecturas:

1. Con la relajación afín sola, **RAA es la mejor variante**: celdas 0.979 y CPU 0.969 frente a
   AF2, sin perder en casi ninguna instancia (5 gana / 4 pierde; las dos grandes son otra vez
   `ex8_4_4bis` y `bearing`).
2. **AA sola empeora** frente a AF2 (celdas 1.029, CPU 1.159): sin la intersección con X-Taylor, la
   pérdida de correlación de sus rayos nuevos en cadenas largas pesa más que su ganancia en
   productos con residuo. El k-nomial la rescata en parte (0.975 en celdas, y es la comparación con
   más victorias: 29 gana / 7 pierde dentro de AA), pero sigue costando un 13 % más de CPU.
3. **El k-nomial sobre AF2 y RAA es neutro con `art`** (1.002 y 1.005), coherente con el trabajo
   previo (§14: "con `art` sola, empeora" se reduce aquí a ruido: 2–5 instancias en cada sentido).
4. Coincidencia con la etapa A: en las dos relajaciones, el k-nomial solo produce un efecto
   consistente sobre AA (0.957 con `compo`, 0.948 con `art`), y RAA es al menos tan buena como AF2.

Gráficos y tablas: `analisis/nivel2_perfil_art.png`, `analisis/nivel2_dispersion_art.png`,
`analisis/nivel2_tabla.md`.

### Etapas C y D — `hard` + `others`

*(en curso)*
