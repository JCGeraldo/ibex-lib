# Fase 3, nivel 1 — sobreestimacion de rangos sin resolver

Fuente: `range.csv`: 124674 filas, 20608 (instancia, funcion, caja), 380 instancias. Violaciones de contencion: puntual 0, de intervalo 0.

*ratio* = anchura de la forma afin / anchura del rango muestreado (media geometrica sobre las cajas donde la forma es activa).
Escala 1 = caja inicial; 0.5, 0.25, ... = sub-cajas aleatorias de esa anchura relativa.

## Sobreestimacion por variante y escala

| variante | escala 1 | escala 0.5 | escala 0.25 | escala 0.125 | escala 0.0625 | todas | formas inactivas | no linearizables | k-nomial/RAA actuo (filas) | us/eval |
|---|---|---|---|---|---|---|---|---|---|---|
| AF2 | 2.051 | 1.806 | 1.620 | 1.505 | 1.445 | 1.633 | 97 | 19 | 0 | 71.8 |
| AF2 + k-nomial | 2.050 | 1.805 | 1.619 | 1.505 | 1.444 | 1.632 | 97 | 19 | 522 | 72.0 |
| RAA | 2.021 | 1.782 | 1.603 | 1.492 | 1.434 | 1.616 | 97 | 19 | 1237 | 69.8 |
| RAA + k-nomial | 2.020 | 1.782 | 1.603 | 1.492 | 1.434 | 1.615 | 97 | 19 | 1366 | 70.6 |
| AA | 2.026 | 1.790 | 1.606 | 1.496 | 1.436 | 1.620 | 97 | 0 | 0 | 1189.8 |
| AA + k-nomial | 2.021 | 1.785 | 1.601 | 1.492 | 1.432 | 1.615 | 97 | 0 | 2039 | 1098.5 |
| *extension natural de intervalos* | 1.828 | 1.646 | 1.535 | 1.476 | 1.459 | 1.557 | — | — | — | — |

## Separacion de efectos (anchura de la forma; gana = mas estrecha en mas de 5 %)

| efecto | comparacion | n | gana | empata | pierde | identicas | media geom. |
|---|---|---|---|---|---|---|---|
| aritmetica | RAA / AF2 | 20511 | 577 | 19934 | 0 | 19371 | 0.9899 |
| aritmetica | AA / AF2 | 20511 | 515 | 19767 | 229 | 17640 | 0.9916 |
| k-nomial | AF2 + k-nomial / AF2 | 20511 | 46 | 20465 | 0 | 20015 | 0.9997 |
| k-nomial | RAA + k-nomial / RAA | 20511 | 42 | 20469 | 0 | 20086 | 0.9998 |
| k-nomial | AA + k-nomial / AA | 20511 | 224 | 20287 | 0 | 18642 | 0.9971 |
| total | RAA + k-nomial / AF2 | 20511 | 609 | 19902 | 0 | 19228 | 0.9896 |
| total | AA + k-nomial / AF2 | 20511 | 570 | 19933 | 8 | 18960 | 0.9887 |

## Por conjunto de instancias (media geometrica del ratio, todas las escalas)

| conjunto | AF2 | AF2 + k-nomial | RAA | RAA + k-nomial | AA | AA + k-nomial |
|---|---|---|---|---|---|---|
| benchs-unconstrainedoptim | 9.683 | 9.679 | 8.716 | 8.715 | 8.694 | 8.660 |
| blowup | 1.342 | 1.342 | 1.341 | 1.341 | 1.344 | 1.342 |
| easy | 1.279 | 1.279 | 1.277 | 1.277 | 1.279 | 1.277 |
| hard | 1.615 | 1.613 | 1.615 | 1.613 | 1.623 | 1.613 |
| medium | 1.476 | 1.475 | 1.467 | 1.466 | 1.477 | 1.466 |
| others | 1.715 | 1.715 | 1.715 | 1.715 | 1.715 | 1.715 |
| unsolved | 1.446 | 1.446 | 1.443 | 1.442 | 1.448 | 1.444 |
