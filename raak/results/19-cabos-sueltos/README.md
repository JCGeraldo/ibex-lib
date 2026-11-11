# Cabos sueltos de implementación (10-11-2026)

Cierre de lo que faltaba para considerar la implementación lista para el paper. Informe: pestaña "Cabos sueltos" del
Informe RAA-K 5 (Claude Docs).

## 1. Rigor del corner test, el cuadrado de Chebyshev y sin/cos/exp/ln (`contencion/`)

`tests/affine_containment_check.cpp`: test estricto, sin tolerancia. Genera funciones aleatorias de 9 familias que ejercitan
cada pieza (productos de formas con error, cuadrados de formas compuestas, sin/cos de combinaciones y de productos, exp y
ln, mezclas), n = 2..6, coeficientes con magnitudes 2⁻⁶..2⁶ en el 40 %, cajas de radio 10⁻⁶ a 3. Para 32 puntos por caja
(16 vértices, 16 interiores) comprueba f(p) ∈ mid + Σ aᵢ εᵢ(p) + err·[−1,1] con todo evaluado en intervalos. Violación
segura = intervalos disjuntos. Variantes: af2_k0, raa_k0, raa_k4 con trig auto, cheb y minrange.

4 semillas × 20 000 casos por familia (`seed11..14.csv/.log`): 720 000 formas por variante, 3.6 millones en total.

| | casos | violaciones seguras | posibles |
|---|---|---|---|
| af2_k0 | 720 000 | 0 | 99 |
| raa_k0 | 720 000 | 0 | 106 |
| raa_k4 (auto / cheb / minrange) | 720 000 cada una | 0 | 108 / 108 / 117 |

Las piezas se ejercitan de verdad: por semilla, el corner test sustituye a la cota de fAF2 en 644 000 de 1 040 000 productos
con error, el cuadrado de Chebyshev en 553 000 de 560 000 y la cota k-nomial en 757 000 productos.
Control de sensibilidad (`control_encoger_1e-12.*`): multiplicando el término de error por 1 − 10⁻¹², el mismo test encuentra
3 536 violaciones seguras en 225 000 formas, así que detecta fallos del orden de un ulp.

Conclusión: no hay evidencia de fallo en ninguna pieza; el esquema de mayoración por factores (1 + 2ε) de fAF2, que usan el
corner test y Chebyshev, contiene. No es una demostración: para el paper el corner test y Chebyshev se remiten a [A].

## 2. Opciones del CLI

`cli/cli_ibexopt_raak.cpp`: `--knomial_budget=N` (0 = sin límite, por defecto) y `--knomial_bound=interval|directed`
(interval por defecto). Prevalecen sobre `RAAK_NODE_BUDGET` y `RAAK_BOUND_MODE`, que siguen valiendo como valor inicial.
La línea de eco del binario muestra los dos valores. Probado: defecto, opción, variable, opción sobre variable, valor inválido.

## 3. Cabecera de `ibex_KNomial.h` (parche 0014, solo comentarios)

Ya no dice "PROTOTIPO sin redondeo dirigido": describe el teorema, el residuo intervalar y las opciones por hilo. Hashes de
`knomial_diff_dump` idénticos (13f8bd6372dd083f interval, 87e9221dac5eceb6 directed); 11 tests de ibex-affine pasan.

## 4. Construcción y distribución

- `scripts/wsl_build_cli.sh` buscaba las fuentes del CLI en `raak/scripts`; ahora las toma de `raak/cli` y el script corre
  de principio a fin (compila y resuelve ex5_4_3 con xn, art y compo).
- `patches/raak-ibex-affine-consolidado.patch`: toda la cadena 0001, 0002, 0004..0014 en un archivo (10 archivos, 1267
  inserciones); verificado que aplica sobre c219009c y reproduce el árbol de trabajo byte a byte.
- `affine/ibex_KNomial.h` (copia legible) y `raak/README.md` puestos al día.

Queda por decidir cómo se publica el código con el paper (fork de ibex-affine, el parche consolidado o un repositorio
suplementario) y los valores por defecto definitivos de k, presupuesto y modo de cota.
