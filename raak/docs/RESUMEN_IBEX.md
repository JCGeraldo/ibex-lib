# Resumen del trabajo con IBEX

**Periodo:** 2026-09-13 a 2026-09-15 · **Detalle:** [`REPORTE_IBEX_BASELINE.md`](REPORTE_IBEX_BASELINE.md) (§1–§14) · **Entorno:** [`ENTORNO.md`](ENTORNO.md)

> **Terminología.** RAA-K es un método nuevo: generaliza la reducción binomial por presupuesto
> diagonal del paper [B] a bloques k-nomiales y la integra en la multiplicación de la aritmética afín.
> Las validaciones de abajo comparan contra la **implementación de referencia en Python** del notebook
> (`knomial.py`, `af2_error`), no contra resultados publicados.
>
> **Aritméticas en IBEX.** `art` y `compo` usan **fAF2** (multiplicación de Vu, Sam-Haroud y Faltings
> 2004), que no es la RAA de [A]. `raak_k = 1` implementa la parte cuadrática de la RAA de [A] y
> `raak_k = 3` le agrega la reescritura k-nomial (RAA-K). En todos los modos, los errores de los factores
> se propagan como en fAF2.

---

## 1. Entorno local

- WSL Ubuntu 24.04 con:
  - **ibex-lib**: el fork `rilianx`, única versión que conserva el optimizador `ibexopt04`;
  - **ibex-affine**: el plugin de aritmética afín;
  - **`ibexopt-raak`**: ejecutable propio con las relajaciones `xn`, `art`, `compo`, `raak` y `raakcompo`.
- Todo fijado a commits concretos y sin commits nuestros. Los cambios quedan como parches en
  `~/ibex-local/patches/`.

## 2. Bug en ibex-affine

- `art` y `compo` fallaban con segfault en `wall.bch`: el linearizador leía coeficientes de formas
  afines no acotadas.
- **Parche 0001**, de tres líneas. Verificado con los tests y sin cambios en las corridas que ya funcionaban.

## 3. Línea base (133 instancias × `xn`/`art`/`compo`, 60 s)

- Las tres relajaciones son válidas: óptimos compatibles, nada podado.
- `compo` explora 31% menos nodos que `xn` (media geométrica de celdas 0.69).
- `art` es la más rápida.
- En la familia `ex2_1_*`, las relajaciones afines exploran ~10 veces menos nodos que `xn`.

## 4. Prototipo de RAA-K en ibex-affine

- Port a C++ de `knomial.py`, idéntico bit a bit a Python.
- Integrado en la multiplicación afín. Solo reemplaza la cota original cuando la mejora; si no, el
  cálculo es bit a bit el de antes.
- **v2** agregó dos cosas:
  - un filtro exacto que descarta los productos donde RAA-K no puede mejorar;
  - la cota de Chebyshev de la RAA de [A] en los cuadrados de formas compuestas.
- Pruebas: contención, pendientes y radio en miles de productos y cuadrados, más los 11 tests del plugin.

## 5. Barridos con RAA-K

- **Alcance:** alguna mejora se usa en 29–30 de 133 instancias; la reescritura k-nomial extrae bloques
  en 12. En las demás, los resultados son idénticos a la base.
- **Total** (`raakcompo` frente a `compo`): gana en 9 instancias y pierde en 4, con media geométrica de
  celdas 0.89 (0.97 sin su mejor caso).
- **Separación de efectos** (barrido extra con `raak_k = 1`):
  - **RAA de [A] frente a fAF2:** da las dos grandes mejoras, `ex8_4_4bis` (~10 veces menos nodos, 7 s en
    lugar de 50 s) y `bearing` (−41% con `compo`), por los cuadrados de Chebyshev. Fuera de ellas es neutra.
  - **Reescritura k-nomial sobre la RAA de [A]:** con `compo` reduce las celdas en las 11 instancias con
    bloques sin perder en ninguna (media geométrica 0.88, hasta −45%); con `art` solo empeora (1.09).
- **Costo:** medido en la misma sesión, el sobrecosto de CPU no se distingue del ruido. El ×1.5
  reportado antes comparaba sesiones distintas y quedó corregido.

## 6. QPLIB evaluado dentro de IBEX (58 instancias)

- IBEX coincide con la referencia en Python (`af2_error`) con diferencia relativa ≤ 1e-11.
- Con k=3, el radio de la parte cuadrática baja 4.4% en promedio (hasta ~10%) en las instancias con
  diagonal no nula.
- La ganancia solo aparece si el modelo se escribe ya reescrito. Desde monomios, RAA-K no la recupera.
- La descomposición espectral da una cota ~3 veces más holgada.

---

## Conclusión

El prototipo es correcto y coincide con la implementación de referencia en Python. En los benchmarks de
IBEX actúa poco, porque los términos suelen ser de variables sueltas. Las mayores ganancias en nodos
vienen de la RAA de [A] (cuadrados); el aporte propio del k-nomial es más modesto, pero consistente
cuando se combina con `compo`. Para aprovechar la reducción
k-nomial, la reescritura tiene que aplicarse al escribir el modelo (o como un nodo de forma
cuadrática en IBEX).

## Siguiente paso propuesto

Reescribir el objetivo de los QP de `ex2_1_*` como residuo + `Σ c·sqr(uᵀx)` y correr el B&B con
`raak` frente a `art`, para ver si ese 4–10% menos de radio se traduce en menos nodos.
