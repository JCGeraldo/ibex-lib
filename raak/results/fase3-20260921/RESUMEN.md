# Fase 4 — tabla consolidada del nivel 2

Etapas: A_easy_medium_compo, B_easy_medium_art, C_hard_others_compo. Base de cada comparacion: AF2 sin k-nomial de la misma etapa; 
*gana* = cociente < 0.95, *pierde* = > 1.05; medias geometricas sobre las instancias resueltas por ambas.

## A_easy_medium_compo

132 instancias.

| variante | resueltas | celdas gana / empata / pierde | celdas media geom. | CPU gana / empata / pierde | CPU media geom. |
|---|---|---|---|---|---|
| AF2 (base) | 126 | — | 1 | — | 1 |
| AF2 + k-nomial | 126 | 7 / 113 / 2 | 0.994 | 17 / 91 / 18 | 0.990 |
| RAA | 126 | 5 / 111 / 6 | 0.984 | 22 / 81 / 23 | 0.990 |
| RAA + k-nomial | 126 | 8 / 109 / 5 | 0.982 | 18 / 73 / 35 | 1.000 |
| AA | 126 | 27 / 63 / 32 | 0.946 | 23 / 30 / 73 | 1.039 |
| AA + k-nomial | 126 | 27 / 74 / 21 | 0.905 | 25 / 27 / 74 | 1.009 |
| X-Taylor (control) | 126 | 19 / 42 / 61 | 1.443 | 56 / 14 / 56 | 1.272 |

| efecto | comparacion | celdas gana / empata / pierde | celdas media geom. | CPU media geom. |
|---|---|---|---|---|
| aritmetica | RAA / AF2 | 5 / 111 / 6 | 0.984 | 0.990 |
| aritmetica | AA / AF2 | 27 / 63 / 32 | 0.946 | 1.039 |
| k-nomial | AF2 + k-nomial / AF2 | 7 / 113 / 2 | 0.994 | 0.990 |
| k-nomial | RAA + k-nomial / RAA | 4 / 116 / 2 | 0.998 | 1.011 |
| k-nomial | AA + k-nomial / AA | 24 / 83 / 15 | 0.957 | 0.971 |
| total | RAA + k-nomial / AF2 | 8 / 109 / 5 | 0.982 | 1.000 |
| total | AA + k-nomial / AF2 | 27 / 74 / 21 | 0.905 | 1.009 |

## B_easy_medium_art

132 instancias.

| variante | resueltas | celdas gana / empata / pierde | celdas media geom. | CPU gana / empata / pierde | CPU media geom. |
|---|---|---|---|---|---|
| AF2 (base) | 126 | — | 1 | — | 1 |
| AF2 + k-nomial | 126 | 2 / 115 / 5 | 1.002 | 27 / 79 / 20 | 0.996 |
| RAA | 126 | 5 / 113 / 4 | 0.979 | 27 / 79 / 20 | 0.969 |
| RAA + k-nomial | 126 | 4 / 113 / 5 | 0.984 | 30 / 67 / 29 | 0.986 |
| AA | 126 | 18 / 64 / 40 | 1.029 | 18 / 32 / 76 | 1.159 |
| AA + k-nomial | 126 | 19 / 79 / 24 | 0.975 | 19 / 25 / 82 | 1.132 |

| efecto | comparacion | celdas gana / empata / pierde | celdas media geom. | CPU media geom. |
|---|---|---|---|---|
| aritmetica | RAA / AF2 | 5 / 113 / 4 | 0.979 | 0.969 |
| aritmetica | AA / AF2 | 18 / 64 / 40 | 1.029 | 1.159 |
| k-nomial | AF2 + k-nomial / AF2 | 2 / 115 / 5 | 1.002 | 0.996 |
| k-nomial | RAA + k-nomial / RAA | 3 / 116 / 3 | 1.005 | 1.017 |
| k-nomial | AA + k-nomial / AA | 29 / 86 / 7 | 0.948 | 0.977 |
| total | RAA + k-nomial / AF2 | 4 / 113 / 5 | 0.984 | 0.986 |
| total | AA + k-nomial / AF2 | 19 / 79 / 24 | 0.975 | 1.132 |

## C_hard_others_compo

15 instancias.

| variante | resueltas | celdas gana / empata / pierde | celdas media geom. | CPU gana / empata / pierde | CPU media geom. |
|---|---|---|---|---|---|
| AF2 (base) | 11 | — | 1 | — | 1 |
| AF2 + k-nomial | 11 | 0 / 11 / 0 | 0.997 | 1 / 10 / 0 | 0.984 |
| RAA | 11 | 1 / 10 / 0 | 0.830 | 1 / 10 / 0 | 0.835 |
| RAA + k-nomial | 11 | 1 / 10 / 0 | 0.828 | 2 / 9 / 0 | 0.824 |
| AA | 8 | 2 / 2 / 4 | 0.992 | 1 / 3 / 4 | 1.183 |
| AA + k-nomial | 11 | 3 / 8 / 0 | 0.830 | 1 / 2 / 8 | 1.001 |
| X-Taylor (control) | 7 | 0 / 0 / 7 | 2.766 | 2 / 0 / 5 | 2.089 |

| efecto | comparacion | celdas gana / empata / pierde | celdas media geom. | CPU media geom. |
|---|---|---|---|---|
| aritmetica | RAA / AF2 | 1 / 10 / 0 | 0.830 | 0.835 |
| aritmetica | AA / AF2 | 2 / 2 / 4 | 0.992 | 1.183 |
| k-nomial | AF2 + k-nomial / AF2 | 0 / 11 / 0 | 0.997 | 0.984 |
| k-nomial | RAA + k-nomial / RAA | 0 / 11 / 0 | 0.997 | 0.986 |
| k-nomial | AA + k-nomial / AA | 4 / 3 / 1 | 0.779 | 0.807 |
| total | RAA + k-nomial / AF2 | 1 / 10 / 0 | 0.828 | 0.824 |
| total | AA + k-nomial / AF2 | 3 / 8 / 0 | 0.830 | 1.001 |

