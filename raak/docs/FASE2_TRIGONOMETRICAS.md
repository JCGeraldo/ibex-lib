# Fase 2 — Seno y coseno en la aritmética afín

Fecha: 2026-09-21. Parche `0008-ibex-affine-trig-sin-cos-CH-MR.patch`. Resultados en
`results/fase2-20260921/` (`trig_lin.csv`, `analisis/`).

## 2.1 Qué había y qué se implementó

**Punto de partida.** Las tres aritméticas (AF2, RAA, AA) comparten la plantilla
`AffineMain<T>`, así que `sin` y `cos` ya existían en las tres. Pero, a diferencia de `exp`, `log`,
`sqrt`, `inv`, `pow`, etc., que tienen variantes `*_CH` (Chebyshev) y `*_MR` (min-range) elegidas
por el modo del hilo, `sin`/`cos` tenían **una sola** implementación que ignora el modo: la pendiente
se toma de la cuadratura de Gauss de dos puntos (`α = 2·c₁/(b−a)` con `c₁ = x₀·(f(xb₀) − f(xb₁))`,
`x₀ = 1/√2`), es decir, una aproximación de la recta de mínimos cuadrados, y el residuo se evalúa
en los extremos y en los puntos donde `f' = α`. No es ni la fórmula de Chebyshev ni la de min-range,
y no coincide con la Sec. 3.2 de [A] (RAA), que fija la pendiente de cuerda (Ec. 12).

**Decisión: fórmulas específicas + mecanismo general.**

- *Mecanismo general* (`trig_residual_range`, en `ibex_AffineTrig.h`): dada cualquier pendiente
  `α`, el rango exacto del residuo `g(v) = f(v) − αv` sobre `[a,b]` es el hull de `g` en `a`, `b` y
  en todos los puntos críticos `f'(v) = α` que caen en `[a,b]` (`±acos α + 2kπ` para `sin`;
  `asin(−α) + 2kπ` y `π − asin(−α) + 2kπ` para `cos`), calculado con aritmética de intervalos. Es
  exactamente el procedimiento en tres pasos de la Sec. 3.2 de [A] y la razón por la que la forma
  resultante es válida **aunque el intervalo contenga extremos o puntos de inflexión**: no hace
  falta suponer convexidad ni monotonía, solo diferenciabilidad. Se escribió una sola vez para `sin`
  y `cos` y lo usan las dos fórmulas.
- *Chebyshev* (`Asin_CH`, `Acos_CH`): pendiente de cuerda `α = (f(b) − f(a))/(b − a)`. Es la
  aproximación minimax cuando `f` es convexa o cóncava en `[a,b]` (teorema de Chebyshev) y es la
  elección por defecto de la RAA de [A]. Cuando el intervalo contiene un punto de inflexión la cuerda
  deja de ser minimax (la pendiente óptima habría que buscarla numéricamente), pero el residuo sigue
  siendo exacto y, como muestra la tabla, sigue siendo mejor que la pendiente original.
- *Min-range* (`Asin_MR`, `Acos_MR`): si `f'` no se anula en `[a,b]` (la función es monótona),
  `α = f'` en el extremo con menor `|f'|`; entonces `g' = f' − α` no cambia de signo, `g` es monótona
  y la anchura de la forma es **exactamente** la del rango de `f`. Si `[a,b]` contiene un extremo
  (`f'` se anula), la forma de rango mínimo es el propio intervalo `f([a,b])`, así que `α = 0`. Se
  detecta con `cos(itv) ∋ 0` (o `sin(itv) ∋ 0` para `cos`): es conservador solo por redondeo en el
  borde.
- El código original queda intacto como modo `legacy` (control), seleccionable con `--trig=legacy`.

Interruptor: `trig_lin_mode()` ∈ {`auto` (sigue el modo del plugin; Chebyshev por defecto),
`cheb`, `minrange`, `legacy`}, flag `--trig` de `ibexopt-raak`. El valor de la Fase 3 es `auto`
(= cuerda), por las razones de 2.2.

## 2.2 Calidad de la aproximación

Barrido (`tests/trig_lin_test.cpp`): 49 centros en `[−π, π]` (incluyen los extremos y los puntos de
inflexión) × 15 anchos de 0.01 a 6.28 = 735 intervalos, para `sin`, `cos`, `sin²+cos²` (≡ 1) y
`sin·cos` (= ½ sin 2x), en `Affine2` (base de AF2/RAA) y `Affine3` (AA), en los tres modos.
**Contención: 0 violaciones en 17 640 evaluaciones** (401 puntos por intervalo).

| función | modo | sobreestimación (media geom.) | … con extremo dentro | … con inflexión dentro | error de linealización medio |
|---|---|---|---|---|---|
| sin | legacy | 1.279 | 1.545 | 1.506 | 0.314 |
| sin | **cuerda** | **1.095** | **1.150** | **1.121** | **0.275** |
| sin | min-range | 1.000 | 1.000 | 1.000 | 0.422 |
| cos | legacy | 1.272 | 1.513 | 1.508 | 0.315 |
| cos | **cuerda** | **1.094** | **1.144** | **1.122** | **0.277** |
| cos | min-range | 1.000 | 1.000 | 1.000 | 0.421 |
| sin·cos (AF2) | legacy / cuerda / min-range | 2.126 / 1.598 / 1.584 | 3.819 / 2.192 / 1.878 | | 1.012 / 0.487 / 0.490 |
| sin·cos (AA) | legacy / cuerda / min-range | 2.307 / 1.709 / 1.598 | 4.207 / 2.344 / 1.878 | | 1.125 / 0.534 / 0.490 |
| sin²+cos² (AF2) | legacy / cuerda / min-range | — | — | — | 2.118 / 1.014 / 0.979 |
| sin²+cos² (AA) | legacy / cuerda / min-range | — | — | — | 1.392 / 0.671 / 0.606 |

(`sin` y `cos` dan los mismos números en AF2 y AA porque la operación unaria es la misma plantilla;
difieren en las compuestas, donde interviene la multiplicación de cada aritmética.)

Lecturas:

1. **La cuerda domina al código original en todos los intervalos**: error de linealización menor
   en 705/735 (`sin`) y 690/735 (`cos`) y nunca mayor (los empates son intervalos que ambos
   resuelven como intervalo: ancho ≥ 2π o `α` fuera de `[−1,1]`). La sobreestimación del rango cae de
   1.27× a 1.09× en promedio, y de 1.5× a 1.15× en los intervalos que contienen un extremo.
2. **Min-range da el rango exacto pero pierde correlación**: su error de linealización es un 35 %
   mayor que el de la cuerda (0.42 frente a 0.27), porque en cuanto el intervalo contiene un extremo
   degenera a intervalo (pendiente 0). En las compuestas, sin embargo, gana ligeramente a la cuerda
   (la forma más estrecha de cada factor compensa la peor pendiente). La comparación por intervalo
   muestra el patrón: min-range es mejor que legacy solo en 102/735 intervalos de `sin`.
3. **AA frente a AF2**: en las compuestas la AA tradicional tiene *menor* error de linealización
   (0.67 frente a 1.01 en `sin²+cos²` con la cuerda) porque cada residuo es un símbolo propio y la
   suma de cuadrados no lo duplica, pero *mayor* sobreestimación en `sin·cos` (1.71 frente a 1.60),
   porque su multiplicación pierde la correlación entre los rayos nuevos. Es la disyuntiva que
   el nivel 1 de la Fase 3 mide sobre las instancias reales.
4. Coste: la cuerda es un 10–15 % más rápida que el código original (una evaluación menos de la
   función); min-range es la más barata (a menudo termina en el intervalo).

**Elección para la Fase 3:** `auto` = cuerda. Es la definición de la RAA de [A] para las unarias,
es la mejor de las tres en las funciones básicas por un margen amplio, es válida sin hipótesis de
forma gracias al mecanismo general, y su coste no es mayor. Min-range queda disponible (`--trig=minrange`)
para experimentos donde importe más el rango que la correlación.

## 2.3 Efecto en el solver (instancias con sin/cos de `easy`, `-t 120`)

| instancia | xn | art legacy / cuerda / min-range | compo legacy / cuerda / min-range |
|---|---|---|---|
| ex14_1_4 (celdas) | 14 | 18 / **14** / 14 | 16 / **14** / 18 |
| ex8_1_1 | 44 | 30 / 30 / 30 | 30 / 30 / 30 |
| ex8_1_2 | 22 | 22 / 22 / 32 | 12 / 12 / 12 |

Las tres instancias son muy fáciles (≤ 0.02 s) y solo `ex14_1_4` cambia con el modo; el barrido
`benchs-unconstrainedoptim` (58 instancias con `sin`/`cos`) queda para el nivel 1 de la Fase 3.
La regresión sin trigonométricas (7 instancias × {xn, art, compo}, `-t 300`) es **idéntica** a la
referencia: 21/21.

Gráficos: `analisis/trig_ratio_vs_width.png` (sobreestimación frente al ancho),
`analisis/trig_linerr_vs_width.png` (error frente al ancho, las 4 funciones),
`analisis/trig_aa_vs_af2.png` (AA frente a AF2 en las compuestas). Tabla completa en
`analisis/trig_tabla.md`.
