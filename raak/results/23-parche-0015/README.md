# 23 · Parche 0015: umbrales de la búsqueda relativos al tamaño de la forma

15-11-2026. Parche `patches/0015-ibex-affine-umbrales-relativos.patch`, sobre la cadena 0001–0014.

## El problema

`knomial_rewrite` (en `ibex_KNomial.h`) comparaba coeficientes y ganancias contra un umbral fijo de
`1e-12` en nueve puntos de la búsqueda de bloques. La forma que recibe está en coordenadas escaladas:
cada coeficiente es el coeficiente original por el radio de la caja. En una caja de radio `r` los
coeficientes de la parte cuadrática son del orden de `r²`, de modo que con `r` cerca de `1e-3` o menor
la búsqueda descartaba todo y no formaba bloques. La cota seguía siendo válida (se cae a RAA k=0),
pero la reescritura dejaba de actuar sin aviso, justo en las cajas pequeñas del final del árbol.

## El cambio

`knomial_rewrite` ahora divide `Q` por una potencia de 4 que deja su mayor coeficiente en `[1/4, 1)`,
llama a la búsqueda anterior (renombrada `knomial_rewrite_abs`) y deshace la escala en el residuo y en
los vectores `u` de los bloques. Multiplicar por potencias de 2 es exacto en punto flotante, así que
no se agrega redondeo y los umbrales pasan a ser relativos. `knomial_relative_tol()` (por hilo, activo
por omisión) permite volver al comportamiento anterior.

## Verificación

| Comprobación | Resultado |
|---|---|
| `knomial_golden` (80 casos contra `knomial.py`) | diferencia 0 |
| `knomial_diff_dump` (20 000 productos de escala 1) | mismo hash que con 0014: cotas idénticas bit a bit |
| `knomial_lemma_check` (8 semillas × 20 000 productos) | 0 violaciones |
| `affine_containment_check` (4 semillas, cajas de radio 1e-6 a 3) | 0 violaciones |
| Tests de ibex-affine | 11 de 11 |

**Producto de prueba.** `(x1 + x2 − x3)(x1 + x2 + x3)` con `x1, x2 ∈ [1−r, 1+r]`, `x3 ∈ [−r, r]`
(`radio/r1e-3.bch` es el caso `r = 1e-3`; tabla completa en `radio/radio.csv`). Error no lineal de
RAA k=3 sobre el de RAA k=0:

| radio r | 1 | 1e-2 | 1e-3 | 5e-4 | 1e-4 | 1e-6 |
|---|---|---|---|---|---|---|
| binario 0014 | 0.714 | 0.714 | 0.714 | 1.000 | 1.000 | 1.000 |
| binario 0015 | 0.714 | 0.714 | 0.714 | 0.714 | 0.714 | 0.715 |

## Efecto en el optimizador

Binario 0014 contra 0015 en una misma sesión (`run.sh`, 18:03 a 19:18): las 7 `ex6_2` y las 18 `synq`
con n = 8, RAA k=4 y k=6 con cada binario más RAA k=0 con el nuevo, 900 s, semilla 42, cota por
intervalos, sin presupuesto. Análisis con `analysis/parche0015_comparacion.py` (salida en `resumen.md`).

| familia | variante | resueltas (0014 / 0015) | celdas 0015 / 0014 | menos / igual / más | celdas frente a k=0: 0014 | 0015 |
|---|---|---|---|---|---|---|
| `ex6_2` | k=4 | 6 / 6 | 0.991 | 5 / 1 / 0 | 0.966 | 0.957 |
| `ex6_2` | k=6 | 6 / 6 | 0.991 | 5 / 1 / 0 | 0.966 | 0.957 |
| synq n=8 | k=4 | 15 / 15 | 1.007 | 7 / 3 / 5 | 0.451 | 0.454 |
| synq n=8 | k=6 | 15 / 15 | 1.000 | 7 / 4 / 4 | 0.369 | 0.369 |

Productos candidatos (los que tienen estructura para formar bloques) que efectivamente reciben bloques:

| familia | binario 0014 | binario 0015 |
|---|---|---|
| `ex6_2` | 8.5 % (1.0 % en `ex6_2_6`) | 100 % |
| synq n=8 | 87 % | 87 % |

- En `ex6_2` el umbral fijo apagaba la reescritura en más del 90 % de los productos donde era
  aplicable. Al corregirlo, las celdas bajan 0,9 % (entre 0 y 2,9 % por instancia, ninguna empeora).
  El efecto es pequeño porque solo el 8,7 % de los productos de esa familia son candidatos.
  `ex6_2_6` sigue sin cerrar en 900 s, con la misma cota inferior.
- En `synq` con n = 8 el umbral casi no actuaba y el resultado no cambia: las diferencias por
  instancia van de −3 % a +6 % sin dirección.
- Cero inconsistencias de óptimos entre binarios y variantes (21 instancias revisadas).

**Tiempos de CPU.** No sirven para comparar los binarios en esta prueba: el lado 0014 corría dos
variantes y terminó a las 18:52; el resto del lado 0015 corrió con la máquina menos cargada. Por lo
mismo, tampoco son comparables las celdas ni las cotas de las instancias que no cierran.

## Alcance

Las tablas del barrido `22-barrido-final` (binario 0014) no cambian de forma apreciable: la fila de
benchmarks pasaría de 0.966 a 0.957 para k ≥ 4 y `synq` queda igual. No se probaron `synl`, `synt`,
`synq` con n distinto de 8 ni los otros benchmarks (`3pk-borne`, `mistake`, `s365mod`).

Importa más fuera de estas familias: en problemas con coeficientes pequeños desde el planteamiento
(por ejemplo flujo de potencia en por unidad, con coeficientes de 1e-5 a 1e-7) el binario 0014 no
formaba bloques en ninguna caja.
