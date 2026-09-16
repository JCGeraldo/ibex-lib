# Línea base de relajaciones lineales en IBEX: `xn`, `art` y `compo`

**Fecha:** 2026-09-13 · **Entorno:** ver [`ENTORNO.md`](ENTORNO.md) · **Datos:** `~/ibex-local/results/baseline-20260913-193306/`

---

## Resumen

- Se armó una **versión local de IBEX con el plugin `ibex-affine`** y se corrió un barrido completo:
  **133 instancias × 3 relajaciones lineales = 399 corridas**, en 4 min 49 s de reloj.
- Durante la preparación apareció un **segfault en `LinearizerAffine2`** (el linearizador afín de
  `ibex-affine`) al procesar restricciones con formas afines no acotadas. Se corrigió con un parche
  local de tres líneas, verificado sin cambios en las corridas que ya funcionaban (§2).
- **Validez:** las tres relajaciones llegan siempre a óptimos compatibles; ninguna poda el óptimo.
- **`compo` es la más robusta:** explora en promedio **31% menos nodos** que `xn` (media geométrica
  0.69), gana en 60 de 120 instancias y pierde en 20.
- **`art` es la más rápida:** usa **47% menos CPU** total que `xn`, pero pierde en 36 instancias y
  tiene los peores retrocesos.
- En la **familia `ex2_1_*` (QP no convexos)** las relajaciones afines exploran unas **10 veces menos
  nodos** que `xn` (media geométrica 0.09–0.11).
- **RAA-K (§10–§14):** el prototipo es correcto y aislado: donde no se usa, los resultados son bit a
  bit los de fAF2. `art`/`compo` usan fAF2, no la RAA de [A]; §14 separa los dos efectos:
  - **RAA de [A]** (parte cuadrática, `raak_k = 1`) frente a fAF2: da las dos grandes mejoras
    (`ex8_4_4bis`, ~10 veces menos nodos; `bearing`, −41% con `compo`) gracias a los cuadrados de
    Chebyshev. Fuera de `ex8_4_4bis` es neutra (media geométrica de celdas 1.00–1.03).
  - **Reescritura k-nomial** (`raak_k = 3` frente a 1): con `compo` reduce las celdas en las 11
    instancias con bloques sin perder en ninguna (media geométrica 0.88); con `art` solo empeora (1.09).
  - Medido en una misma sesión, el sobrecosto de CPU no se distingue del ruido.
- **QPLIB (§13):** evaluado dentro de IBEX sobre 58 instancias reales, el prototipo reproduce la cota
  de la implementación de referencia en Python (`knomial.py`) con diferencia ≤ 1e-11: 4.4% menos radio con k = 3 (hasta ~10%). Esa ganancia solo
  aparece si el modelo se escribe con la reescritura k-nomial; desde monomios, RAA-K no la recupera.

---

## 1. Qué se comparó

| Relajación | Implementación | Descripción |
|---|---|---|
| `xn` | `LinearizerXTaylor` (ibex-lib) | Relajación X-Taylor; es la opción por defecto de `ibexopt` |
| `art` | `LinearizerAffine2` (ibex-affine) | Relajación afín: evalúa cada restricción en aritmética afín AF2 y la convierte en desigualdades lineales |
| `compo` | `LinearizerCompo(xn, art)` | Agrega las desigualdades de ambas al mismo LP |

**Configuración común.** Ejecutable propio `ibexopt-raak` (derivado de `ibexopt04` del fork), con los
valores por defecto de `ibexopt04`: filtrado `acidhc4`, bisección `lsmearmg`, estrategia `bs` (beam 1),
semilla 42. Límite de tiempo **60 s** por corrida; **4 corridas en paralelo**.

**Instancias.** `benchs/optim/easy` (102) y `benchs/optim/medium` (31) del fork de IBEX: problemas de
optimización global de la biblioteca COCONUT con menos de 50 variables. No se corrió `hard`.

**Métrica principal: celdas del B&B** (`number of cells` del reporte de IBEX), es decir, nodos
explorados. Es independiente de la carga de la máquina, y el tiempo de CPU no lo es.

---

## 2. Bug encontrado y parche aplicado

| | |
|---|---|
| **Síntoma** | `--lr=art` y `--lr=compo` terminaban con segfault (código 139) en `easy/wall.bch`; `--lr=xn` lo resolvía. |
| **Causa** | Al asignar un intervalo no acotado a una forma afín, ésta queda con estado `AllReals` **sin vector de coeficientes**. `LinearizerAffine2` validaba la forma sólo con `noise_count() == nb_var` (que no mira el estado) y luego leía los coeficientes con `noise(i)`, cuyo `assert(is_active())` se elimina al compilar en Release. |
| **Disparador** | Dividir por un intervalo que contiene 0. Con dominios `[0.01, 100]` no falla; con `[-100, 100]` sí. |
| **Parche** | `af2.is_active() && af2.noise_count() == nb_var` en `goal_linearization`, `inlinearization` y `linearize`. Omitir una restricción mantiene válida la relajación. Guardado en `~/ibex-local/patches/0001-…patch`, sin commit. |
| **Verificación** | 11/11 tests de `ibex-affine`; `wall` pasa a resolverse con el mismo óptimo que `xn`; las **19 corridas** de una prueba corta que ya funcionaban dan **exactamente el mismo estado y número de celdas** que antes. |
| **Riesgo de resultados silenciosamente erróneos** | Descartado: la asignación de copia de una forma no activa libera el vector, así que el linearizador no puede leer coeficientes de otra restricción. |
| **Origen** | El mismo patrón está en el `master` de 2021 del plugin; no lo introdujo la reescritura en curso (`update_affine`). |

---

## 3. Validez de los resultados

| Verificación | Resultado |
|---|---|
| Corridas con crash | **0** de 399 |
| Instancias resueltas por las 3 cuyos intervalos finales de f\* **no** se solapan | **0** de 122 |
| Corridas sin terminar cuyo intervalo final **excluye** el óptimo hallado por otra relajación | **0** |

Si alguna relajación podara regiones con el óptimo, se vería aquí; no ocurre.

---

## 4. Estado de las corridas

Número de instancias (de 133) en cada estado:

| Estado | `xn` | `art` | `compo` |
|---|---|---|---|
| Resuelta (`optimization successful`) | 124 | 123 | **125** |
| Tiempo agotado (60 s) | 3 | 4 | **2** |
| Objetivo posiblemente no acotado | 4 | 4 | 4 |
| Infactible | 1 | 1 | 1 |
| Sin punto factible encontrado | 1 | 1 | 1 |

Instancias donde las relajaciones **no coinciden** en el estado:

| Instancia | `xn` | `art` | `compo` |
|---|---|---|---|
| `easy/hockschittkowski` | resuelta (182 celdas, 0.1 s) | **tiempo agotado** (227 350 celdas) | resuelta (164 celdas, 0.1 s) |
| `medium/bearing` | resuelta (27 866 celdas, 56 s) | **tiempo agotado** (28 846 celdas) | resuelta (25 704 celdas, 54 s) |
| `medium/ex8_4_4bis` | **tiempo agotado** (122 696 celdas) | resuelta (120 168 celdas, 50 s) | resuelta (83 220 celdas, 52 s) |

---

## 5. Nodos explorados frente a `xn`

> **Cómo leer esta tabla.** Sobre las instancias **resueltas por las tres relajaciones** y con al
> menos una celda en `xn` (120 instancias; se excluyen `ex2_1_4` y `exp40`, resueltas con 0 celdas).
> *Cociente* = celdas de la relajación ÷ celdas de `xn`; **menor que 1 = explora menos nodos**.
> *Gana* = cociente < 0.95; *pierde* = cociente > 1.05; *empata* = el resto.
> *Media geom.* = media geométrica de los cocientes. *p25 / mediana / p75* = cuartiles del cociente.
> *≤ 0.5* y *≥ 2* = número de instancias con al menos la mitad o el doble de celdas.

| Grupo | Relajación | n | Gana | Empata | Pierde | Media geom. | p25 | Mediana | p75 | ≤ 0.5 | ≥ 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Todas** | `art` | 120 | 56 | 28 | 36 | 0.762 | 0.530 | 1.000 | 1.113 | 28 | 12 |
| **Todas** | `compo` | 120 | **60** | 40 | **20** | **0.691** | 0.619 | 0.952 | 1.000 | 22 | 3 |
| `easy` | `art` | 94 | 40 | 26 | 28 | 0.843 | 0.664 | 1.000 | 1.180 | 17 | 10 |
| `easy` | `compo` | 94 | 42 | 37 | 15 | 0.768 | 0.733 | 1.000 | 1.000 | 9 | 2 |
| `medium` | `art` | 26 | 16 | 2 | 8 | 0.527 | 0.299 | 0.545 | 1.096 | 11 | 2 |
| `medium` | `compo` | 26 | 18 | 3 | 5 | **0.471** | 0.329 | 0.543 | 0.986 | 13 | 1 |
| **Familia `ex2_1_*`** (QP no convexos) | `art` | 11 | 7 | 2 | 2 | **0.107** | 0.022 | 0.118 | 1.000 | 7 | 0 |
| **Familia `ex2_1_*`** | `compo` | 11 | 7 | 4 | 0 | **0.092** | 0.022 | 0.078 | 0.994 | 7 | 0 |
| Resto (sin `ex2_1_*`) | `art` | 109 | 49 | 26 | 34 | 0.928 | 0.556 | 1.000 | 1.156 | 21 | 12 |
| Resto (sin `ex2_1_*`) | `compo` | 109 | 53 | 36 | 20 | 0.847 | 0.674 | 0.977 | 1.000 | 15 | 3 |

**Lecturas:**

- El beneficio **crece con la dificultad**: en `medium` las dos relajaciones afines reducen los nodos
  a la mitad (media geométrica 0.47–0.53); en `easy`, muchas instancias se resuelven en pocas celdas
  con cualquier método y hay poco margen.
- **`compo` casi nunca empeora mucho** (sólo 3 instancias con el doble de celdas o más, contra 12 de
  `art`). Agregar las desigualdades afines a las de X-Taylor protege contra los casos malos de `art`.
- Sin la familia `ex2_1_*`, la ventaja se reduce pero se mantiene (`compo` 0.85).
- En **17 instancias** las tres relajaciones exploran exactamente el mismo número de celdas.

---

## 6. Tiempo de CPU

Suma de `cpu time used` sobre las instancias resueltas por las tres, en segundos:

| Conjunto | `xn` | `art` | `compo` |
|---|---|---|---|
| `easy` | 17.1 | 14.4 | 18.8 |
| `medium` | 144.0 | **71.4** | 102.1 |
| **Total** | 161.1 | **85.8** | 121.0 |

`art` es la más rápida pese a perder en más instancias: donde gana, gana mucho, y el LP que resuelve
es más chico que el de `compo`. Con 4 corridas en paralelo, estos tiempos son orientativos.

---

## 7. Casos notables

### Familia `ex2_1_*`: mejoras de uno a tres órdenes de magnitud

| Instancia | `xn` celdas | `art` celdas | `compo` celdas |
|---|---|---|---|
| `medium/ex2_1_8` | 1 712 | **4** | **4** |
| `medium/ex2_1_7` | 2 478 | **12** | **12** |
| `easy/ex2_1_6` | 688 | **4** | **4** |
| `easy/ex2_1_1` | 152 | **6** | **6** |
| `easy/ex2_1_3` | 102 | 12 | **8** |
| `easy/ex2_1_10` | 52 | **2** | **2** |
| `medium/ex2_1_9` | 5 752 | 10 876 | 5 688 |
| `medium/ex2_1_9fact` | 5 752 | 10 884 | 5 742 |

La excepción es `ex2_1_9` (y su variante factorizada): `art` casi duplica las celdas y `compo` iguala a `xn`.

### Retrocesos más grandes

| Instancia | `xn` | `art` | `compo` | Nota |
|---|---|---|---|---|
| `medium/alkylbis` | 36 | 9 708 | 3 084 | `xn` terminó con un intervalo final de f\* **unas 24 veces más ancho** que `art` (todos cumplen la precisión pedida). La comparación de celdas no es del todo pareja. |
| `easy/ex14_2_4` | 110 | 2 620 | 98 | Retroceso exclusivo de `art`; `compo` no lo sufre. |
| `medium/alkyl` | 14 340 | **1 578** | 24 156 | Caso inverso: `art` mejora 9 veces y `compo` empeora. |

---

## 8. Limitaciones

- **Una corrida por instancia.** Las celdas son deterministas con la semilla fija; el tiempo de CPU
  no, y además se midió con 4 corridas en paralelo.
- **Precisión efectiva ε = 1e-6** en `eps_x` (el valor por defecto que se buscaba era 1e-7). El
  ejecutable pasa la precisión a `Optimizer04Config` como texto y la conversión la redondea. Afecta
  por igual a las tres relajaciones.
- **`art` y `compo` incluyen el parche 0001.** No cambia ningún resultado que antes terminara.
- **Diferencias de precisión final** entre relajaciones (caso `alkylbis`) pueden favorecer en celdas
  a la que termina con un intervalo más ancho.
- No se corrió `benchs/optim/hard`. Seis instancias no son comparables porque son no acotadas,
  infactibles o no tienen punto factible con ningún método.

---

## 9. Implicaciones y siguiente paso

Las mayores ganancias de la relajación afín aparecen en QP no convexos, donde el cuello de botella
es la **cota del producto de formas afines**. Eso es precisamente lo que mejora RAA-K: reemplaza la
cota del término cuadrático de la multiplicación AF2 por la reescritura k-nomial.

**Siguiente paso (F5):** prototipo de RAA-K como modo de multiplicación de `AF_fAF2` en `ibex-affine`,
expuesto como `--lr=raak` y `--lr=raakcompo`, y comparado contra esta línea base con el mismo barrido.

---

## 10. Prototipo de RAA-K en IBEX: verificación inicial

### Qué se implementó

- **`ibex_KNomial.h`** (nuevo, ibex-affine): port a C++11 de `raa_lib/knomial.py`
  (`mode='sdsos'`, `sign_mode='fixed'`) y la cota de la parte cuadrática de un producto de formas afines.
- **`AF_fAF2::operator*=`**: con `raak_k ≥ 1`, la parte cuadrática de fAF2
  (centro `½Sz`, radio `Sx·Sy − ½Sxy`) se reemplaza por la cota k-nomial en coordenadas de ruido.
  Las pendientes y los términos con los errores no cambian. La cota k-nomial **solo se usa si
  mejora la de fAF2** más allá de su margen de redondeo; si no, el cálculo es bit a bit el de fAF2.
- **Modos (`--raak_k`)**: `0` = fAF2 original · `1` = parte cuadrática simétrica término a término,
  sin reescritura (la de la RAA de [A]; ver §14) · `k ≥ 2` = reescritura k-nomial con cliques de
  hasta k símbolos.
- **CLI**: `--lr=raak` (linearizador de `art`) y `--lr=raakcompo` (de `compo`) con la multiplicación
  RAA-K; `get_ctc` del fork acepta esos nombres.
- **Rigor**: prototipo en punto flotante. El margen por el redondeo de la reescritura es heurístico
  (≈ `n²·ε_máquina` relativo); acotarlo formalmente queda para la fase F6.

### Pruebas

**Prueba dorada del port.** 80 casos generados con `knomial.py` (n de 2 a 12, k ∈ {2, 3, 4},
matrices aleatorias y de producto de rango 2, anchos iguales y distintos):

| Casos | Bloques comparados | Casos con distinto nº de bloques | Diferencia máxima en bloques y `Q_res` |
|---|---|---|---|
| 80 | 327 | 0 | **0** (idéntico bit a bit) |

**Prueba aritmética.** 3000 productos `x·y` de formas afines aleatorias (1 a 12 símbolos de ruido,
con y sin término de error), 200 puntos muestreados por producto (mitad vértices):

> *Violaciones* = puntos donde el valor exacto del producto cae fuera de la forma resultante.
> *Radio / fAF2* = radio de error del modo ÷ radio de fAF2, promedio sobre los productos
> (menor que 1 = más ajustado). *Dif. pendiente* = mayor diferencia en coeficientes de ruido frente a fAF2.

| Modo | Violaciones | Productos con radio mayor que fAF2 | Productos con radio menor | Radio / fAF2 medio | Dif. pendiente máx. |
|---|---|---|---|---|---|
| 0 (fAF2) | 0 | — | — | 1 | — |
| 1 (simétrica) | 0 | 0 | 2066 | 0.898 | 0 |
| 2 | 0 | 0 | 2466 | 0.854 | 0 |
| 3 | 0 | 0 | 2466 | 0.833 | 0 |

Además, los 11 tests de ibex-affine pasan.

### Corridas cortas

Límite de 60 s, una corrida por variante, todas resueltas.

En **`ex5_4_3`, `wall`, `alkyl` y `ex2_1_1`** la cota k-nomial **nunca se usó** (0 productos
mejorados), y `raak`/`raakcompo` dan exactamente las mismas celdas y el mismo f\* que `art`/`compo`
con cualquier k. En `ex2_1_1` ni siquiera hay productos: sus términos cuadráticos son `xᵢ²` (operación
`sqr`, no `*`).

Solo **`ex14_2_4`** activa RAA-K:

> *Productos mejorados* = productos donde la cota k-nomial reemplazó a la de fAF2.
> *Radio cuadrático / fAF2* = suma de radios cuadráticos calculados ÷ suma de los de fAF2,
> sobre todos los productos de la corrida. *Cota sup. f\** = extremo superior del intervalo final
> (el óptimo es 0).

| Variante | Celdas | Frente a la base | Productos | Productos mejorados | Radio cuadrático / fAF2 | Cota sup. f\* |
|---|---|---|---|---|---|---|
| `art` (base) | 2620 | — | — | — | — | 3.6e-7 |
| `raak`, k=0 | 2620 | idéntico | — | — | — | 3.6e-7 |
| `raak`, k=1 | 2154 | −18% | 137 808 | 20 411 | 0.951 | 6.6e-7 |
| `raak`, k=2 | 5522 | **+111%** | 361 485 | 89 447 | 0.786 | 6.1e-7 |
| `raak`, k=3 | 2158 | −18% | 137 484 | 34 886 | 0.662 | 4.0e-7 |
| `compo` (base) | 98 | — | — | — | — | 1.5e-8 |
| `raakcompo`, k=3 | 112 | +14% | 11 610 | 4 548 | 0.662 | 2.5e-7 |

### Lecturas

1. **La implementación es correcta y aislada.** Reproduce el Python exactamente, contiene el producto
   exacto y con k=0 (o sin mejoras) no altera nada.
2. **RAA-K solo actúa en productos de formas afines compuestas** (con varios símbolos de ruido en
   ambos factores). IBEX evalúa la expresión nodo a nodo: un QP escrito como suma de monomios
   `xᵢ·xⱼ` o `xᵢ²` no le da nada que reescribir. Por eso la familia `ex2_1_*`, la de mayor ganancia
   de `art`, no cambia.
3. **Encierros más ajustados no garantizan menos celdas.** En `ex14_2_4` el radio baja
   monótonamente con k (0.95 → 0.79 → 0.66), pero las celdas oscilan (−18%, +111%, −18%). Como las
   variantes terminan con intervalos finales distintos dentro de la precisión pedida (caso `alkylbis`
   del §7), una sola instancia no permite concluir.
4. **Por qué el uso condicional.** Una primera versión usaba siempre la cota k-nomial; aunque
   no extraía bloques, el margen de redondeo (~1e-13 relativo) bastó para cambiar `alkyl` de 1 578 a
   19 822 celdas. El B&B es muy sensible a perturbaciones mínimas, así que cualquier comparación
   debe mirar muchas instancias.

### Próximos pasos propuestos

- **Barrido completo** de `raak` y `raakcompo` (k=3) sobre las 133 instancias (≈ 5 min), contando
  en cuántas se usa RAA-K y comparando celdas solo en esas.
- **Extender RAA-K a `sqr`**: el cuadrado de una forma compuesta `(aᵀε)²` tiene rango exacto
  `[0, (Σ|aᵢ|)²]`, que la reescritura k-nomial alcanza (un solo bloque), mientras que fAF2 usa
  radio `(Σ|aᵢ|)² − ½Σaᵢ²`.
- **Instancias con estructura cuadrática compuesta** (p. ej. QPLIB reescritas como `(Ax)ᵀQ(Ax)` o
  formas `xᵀQx` evaluadas en bloque), donde la reescritura k-nomial debería aportar.

---

## 11. Barrido completo de RAA-K (k = 3)

**Diseño.** Mismo barrido que la línea base (133 instancias `easy` + `medium`, límite 60 s,
4 corridas en paralelo, semilla 42), con `--lr=raak` y `--lr=raakcompo` y `raak_k = 3`.
Cada variante se compara con su par de la línea base, que usa **el mismo linearizador**:
`raak` ↔ `art` y `raakcompo` ↔ `compo`. Lo único que cambia es la multiplicación de formas afines.
Datos: `~/ibex-local/results/baseline-20260914-120246/` (`results.csv`, logs y `raak_vs_base.csv`).

### Estado de las corridas

Número de instancias (de 133) en cada estado:

| Estado | `art` | `raak` | `compo` | `raakcompo` |
|---|---|---|---|---|
| Resuelta | 123 | 122 | 125 | 123 |
| Tiempo agotado | 4 | 5 | 2 | 4 |
| Objetivo posiblemente no acotado | 4 | 4 | 4 | 4 |
| Infactible | 1 | 1 | 1 | 1 |
| Sin punto factible | 1 | 1 | 1 | 1 |

Las tres corridas nuevas con tiempo agotado se explican en *Costo*: en ellas RAA-K no se usó nunca.

### ¿En cuántas instancias se usa RAA-K?

> *Usada* = al menos un producto de la corrida en que la cota k-nomial reemplazó a la de fAF2.
> *Con bloques* = además, la reescritura extrajo al menos un bloque; sin bloques, la mejora viene
> solo de la forma simétrica término a término (modo 1). Las cifras coinciden para `raak` y `raakcompo`.

| | Instancias |
|---|---|
| RAA-K usada | **16 de 133** (`easy` 8 de 102, `medium` 8 de 31) |
| … con bloques extraídos | 12 |
| Con productos, pero RAA-K nunca mejora | 91 |
| Sin ningún producto de formas afines | 26 |

Las 16 pertenecen a tres familias: `ex14_2_*` (6), `ex6_1_3bis` + `ex6_2_*` (7) y `ex8_5_*` (3).

**Control de aislamiento.** En las instancias sin uso y resueltas en ambas corridas, las celdas son
**idénticas** a la línea base en 108 de 108 (`raak`) y 109 de 109 (`raakcompo`).

### Celdas en las instancias con uso

> *Cociente* = celdas de la variante RAA-K ÷ celdas de su par base; **menor que 1 = explora menos nodos**.
> *% productos mejorados* = productos donde se usó la cota k-nomial ÷ productos de la corrida
> (columna de `raak`; la de `raakcompo` es similar). *Radio* = suma de radios cuadráticos k-nomiales ÷
> suma de los de fAF2 sobre **todos** los productos de la corrida; un valor de 1.000 significa que la
> mejora existe pero es mínima frente al total. *Bloques* = bloques extraídos en la corrida de `raak`.
> "—" = sin cociente, porque alguna de las dos corridas no terminó.

| Instancia | `art` | `raak` | Cociente | `compo` | `raakcompo` | Cociente | % productos mejorados | Bloques | Radio |
|---|---|---|---|---|---|---|---|---|---|
| `easy/ex14_2_4` | 2 620 | 2 158 | 0.824 | 98 | 112 | 1.143 | 25.4% | 19 634 | 0.662 |
| `easy/ex14_2_5` | 14 | 16 | 1.143 | 38 | 34 | 0.895 | 27.5% | 132 | 0.671 |
| `easy/ex14_2_6` | 210 | 206 | 0.981 | 242 | 170 | **0.702** | 25.0% | 2 010 | 0.821 |
| `easy/ex14_2_8` | 22 | 28 | 1.273 | 32 | 40 | 1.250 | 25.0% | 0 | 0.904 |
| `easy/ex14_2_9` | 50 | 56 | 1.120 | 44 | 40 | 0.909 | 35.5% | 268 | 0.785 |
| `easy/ex8_5_5` | 226 | 228 | 1.009 | 212 | 182 | 0.858 | 5.3% | 0 | 0.998 |
| `easy/ex8_5_5-1` | 76 | 84 | 1.105 | 60 | 62 | 1.033 | 5.3% | 0 | 0.999 |
| `easy/ex8_5_6-1` (no acotado) | 174 | 174 | — | 196 | 196 | — | 3.7% | 0 | 0.965 |
| `medium/ex14_2_7` | 4 774 | 5 200 | 1.089 | 4 140 | 3 200 | **0.773** | 20.0% | 144 893 | 0.832 |
| `medium/ex6_1_3bis` | 3 146 | 3 136 | 0.997 | 3 012 | 2 994 | 0.994 | 4.1% | 4 342 | 0.691 |
| `medium/ex6_2_11` | 12 182 | 11 578 | 0.950 | 10 782 | 10 152 | 0.942 | 5.6% | 23 751 | 1.000 |
| `medium/ex6_2_12` | 3 962 | 3 914 | 0.988 | 3 854 | 3 796 | 0.985 | 4.6% | 7 803 | 1.000 |
| `medium/ex6_2_14` | 554 | 554 | 1.000 | 528 | 532 | 1.008 | 8.4% | 1 890 | 1.000 |
| `medium/ex6_2_6` (tiempo agotado en todas) | 234 600 | 151 890 | — | 177 000 | 117 488 | — | 1.5% | 56 314 | 0.742 |
| `medium/ex6_2_8` | 18 014 | 16 360 | 0.908 | 16 800 | 15 402 | 0.917 | 6.7% | 39 619 | 0.761 |
| `medium/ex6_2_9` | 10 010 | 9 786 | 0.978 | 9 818 | 9 632 | 0.981 | 5.2% | 29 368 | 1.000 |

**Resumen** sobre las 14 instancias resueltas por las cuatro variantes. *Gana* < 0.95,
*pierde* > 1.05; *media geom.* = media geométrica del cociente; *suma* = celdas totales RAA-K ÷ base.

| Comparación | n | Gana | Empata | Pierde | Media geom. | Mediana | Suma de celdas | Solo con bloques (n=11): gana / pierde / media geom. |
|---|---|---|---|---|---|---|---|---|
| `raak` / `art` | 14 | 2 | 7 | 5 | 1.020 | 0.998 | 0.954 | 2 / 3 / 0.994 |
| `raakcompo` / `compo` | 14 | **7** | 5 | 2 | **0.947** | 0.961 | 0.933 | **6 / 1 / 0.925** |

Ninguna instancia con uso de RAA-K cambió de estado.

### Costo

> **Corrección (ver §12, *Costo*):** una medición controlada en una misma sesión mostró que los
> tiempos varían 20–30% entre sesiones. Los cocientes de CPU de esta sección comparan sesiones
> distintas y **no miden el sobrecosto de RAA-K**; las conclusiones de costo de abajo quedan sin efecto.

El prototipo **calcula la cota k-nomial en todos los productos** y la descarta cuando no mejora.

> *CPU total* = suma de `cpu time used` en las instancias resueltas por la variante y su base.
> *×* = CPU RAA-K ÷ CPU base. Con 4 corridas en paralelo, los tiempos son orientativos.

| Grupo de instancias | n (`raak` / `raakcompo`) | `raak` / `art` | `raakcompo` / `compo` |
|---|---|---|---|
| Con productos, sin uso de RAA-K | 85 / 86 | ×1.47 | ×1.47 |
| Con uso de RAA-K | 14 / 14 | ×1.60 | ×1.43 |

Este sobrecosto causó las tres corridas nuevas con tiempo agotado. En la línea base terminaban cerca del
límite, y **no usaron RAA-K ni una vez**:

| Instancia | Base: estado, celdas, CPU | RAA-K: estado, celdas en 60 s | Celdas por segundo (base → RAA-K) |
|---|---|---|---|
| `medium/ex8_4_4bis`, `art` → `raak` | resuelta, 120 168, 49.5 s | tiempo agotado, 104 204 | 2 426 → 1 737 |
| `medium/ex8_4_4bis`, `compo` → `raakcompo` | resuelta, 83 220, 52.2 s | tiempo agotado, 71 668 | 1 593 → 1 194 |
| `medium/bearing`, `compo` → `raakcompo` | resuelta, 25 704, 53.6 s | tiempo agotado, 15 306 | 480 → 255 |

### Lecturas

1. **Alcance acotado.** RAA-K actúa en el 12% de las instancias; en el resto, los productos no tienen
   la estructura que la reescritura aprovecha.
2. **Donde actúa, la ganancia es modesta y depende del linearizador.** Con `compo`, reduce las celdas
   un 5% en media geométrica (7.5% en las instancias con bloques) y gana 6 de 11 de ellas; los mejores
   casos son `ex14_2_6` (−30%) y `ex14_2_7` (−23%). Con `art` el efecto es neutro (media geom. 1.02).
3. **La correlación con el ajuste del radio es débil.** `ex14_2_4` tiene el mayor ajuste (radio 0.66)
   y mejora con `art` pero empeora con `compo`. `ex14_2_8` empeora en ambas con la sola forma simétrica.
   Con n = 14 y una corrida, las diferencias por instancia son sensibles al recorrido del B&B.
4. **El costo parecía pesar más que la ganancia en este conjunto** (conclusión corregida en §12: el
   sobrecosto medido no era atribuible a RAA-K). ×1.5 de CPU general para una reducción de
   celdas del 5–7% en 16 instancias. Esto se puede recortar sin cambiar resultados: ambas mejoras
   (forma simétrica y bloques) requieren que **x e y compartan al menos dos símbolos de ruido**. Ese
   filtro cuesta O(n) y evitaría calcular la cota en la mayoría de los productos.

### Próximos pasos

1. **Filtro de símbolos compartidos** antes de llamar a `knomial_quad_bound`. Resultados idénticos,
   menor CPU; recupera las tres instancias perdidas por tiempo.
2. **RAA-K en `sqr`** (§10), que amplía el alcance.
3. **Instancias con estructura cuadrática compuesta** (QPLIB en forma `(Ax)ᵀQ(Ax)`), para medir
   RAA-K donde la reescritura k-nomial debería aportar.
4. Repetir el barrido tras (1) y (2); con más instancias con uso, conviene reportar también por familia.

---

## 12. RAA-K v2: filtro previo y cuadrados

> **Corrección (ver §14).** La cota de los cuadrados es la linealización de Chebyshev de la **RAA de
> [A]**, no una contribución de la reescritura k-nomial. Las mejoras que aquí se atribuyen a RAA-K por
> los cuadrados (`ex8_4_4bis`, `bearing`) son efecto de la RAA de [A] frente a fAF2. Desde §14, esa cota
> se activa con `raak_k ≥ 1`; los resultados de esta sección (k = 3) no cambian.

### Qué cambió respecto de §11

1. **Filtro de símbolos compartidos (productos).** Antes de calcular la cota k-nomial de `x·y` se
   verifica que x e y compartan al menos dos símbolos de ruido. Si no, la cota no puede mejorar a
   fAF2 y no se calcula. En aritmética exacta no cambia ningún resultado.
2. **RAA-K en `sqr`.** La parte cuadrática de `(aᵀε + e·h)²` tiene matriz `a aᵀ`, que es un único clique
   balanceado. La reescritura sin límite de clique lo extrae en **un solo bloque**, cuya cota es el rango
   exacto `[0, (Σ|aᵢ| + e)²]`. fAF2 usa radio `(Σ|aᵢ| + e)² − ½Σaᵢ²`. Se activa con `raak_k ≥ 2`
   (con k = 1, fAF2 ya coincide con la forma simétrica término a término) y, como en los productos,
   solo si mejora a fAF2 más allá del margen de redondeo.

### Pruebas

Prueba aritmética ampliada: 3000 productos y 3000 cuadrados; un tercio de las formas con soportes
dispersos, para ejercitar el filtro.

| Prueba | Resultado |
|---|---|
| Productos, modos 1 / 2 / 3: violaciones de contención · radios mayores que fAF2 | 0 · 0 en los tres modos |
| Productos: radio / fAF2 medio (modos 1 / 2 / 3) | 0.929 / 0.899 / 0.884 |
| Filtro: productos con menos de 2 símbolos compartidos · resultados distintos de fAF2 | 1 238 · **0** (bit a bit) |
| Cuadrados, modo 3: violaciones · radios mayores que fAF2 · radios menores | 0 · 0 · 2 666 de 3 000 |
| Cuadrados: radio / fAF2 medio | **0.684** |
| Tests de ibex-affine | 11/11 |

### Barrido completo

Mismo diseño que §11. Datos: `~/ibex-local/results/baseline-20260914-131620/` (incluye `raak_v2_vs_base.csv`).

**Verificaciones de exactitud**

| Verificación | `raak` | `raakcompo` |
|---|---|---|
| Instancias sin uso de RAA-K y resueltas: celdas idénticas a la base (`art` / `compo`) | 99 de 99 | 99 de 99 |
| Instancias sin uso en cuadrados y resueltas: celdas idénticas a v1 (§11) | 111 de 111 | 111 de 111 |
| … y mismo número de productos mejorados que v1 | 111 de 111 | 111 de 111 |
| Productos evaluados tras el filtro | 6.1% | 5.1% |
| Instancias resueltas (base) | **123** (123) | **125** (125) |
| Cambios de estado frente a la base | 0 | 0 |

El filtro no cambia ningún resultado y v2 recupera las tres instancias que v1 perdía por tiempo.

**Uso de RAA-K** (instancias con al menos una operación donde la cota RAA-K reemplazó a la de fAF2):

| | `raak` | `raakcompo` |
|---|---|---|
| Con uso en productos (con bloques) | 16 (12) | 16 (12) |
| Con uso en cuadrados | 15 | 16 |
| **Con algún uso** | **29 de 133** (easy 15, medium 14) | **30 de 133** (easy 16, medium 14) |

**Celdas por instancia con uso**

> *Tipo*: P = uso en productos, S = uso en cuadrados. *Cociente* = celdas v2 ÷ celdas base; **menor que
> 1 = menos nodos**. "—" = sin cociente (alguna corrida no terminó, o el problema es no acotado o sin
> punto factible). "sin uso" = esa variante no usó RAA-K en la instancia (celdas idénticas a la base).

| Instancia | Tipo | `art` → `raak` | Cociente | `compo` → `raakcompo` | Cociente |
|---|---|---|---|---|---|
| `easy/ex14_2_4` | PS | 2 620 → 3 692 | 1.409 | 98 → 92 | 0.939 |
| `easy/ex14_2_5` | PS | 14 → 22 | 1.571 | 38 → 38 | 1.000 |
| `easy/ex14_2_6` | P | 210 → 206 | 0.981 | 242 → 170 | **0.702** |
| `easy/ex14_2_8` | P | 22 → 28 | 1.273 | 32 → 40 | 1.250 |
| `easy/ex14_2_9` | P | 50 → 56 | 1.120 | 44 → 40 | 0.909 |
| `easy/ex2_1_10` | S | 2 → 2 | 1.000 | 2 → 2 | 1.000 |
| `easy/ex8_1_6` | S | sin uso | — | 30 → 30 | 1.000 |
| `easy/ex8_1_6bis` | S | 190 → 190 | 1.000 | 192 → 192 | 1.000 |
| `easy/ex8_1_7` | S | 292 → 298 | 1.021 | 264 → 394 | 1.492 |
| `easy/ex8_5_5` | P | 226 → 228 | 1.009 | 212 → 182 | 0.858 |
| `easy/ex8_5_5-1` | P | 76 → 84 | 1.105 | 60 → 62 | 1.033 |
| `easy/ex8_5_6-1` (no acotado) | P | 174 → 174 | — | 196 → 196 | — |
| `easy/m4wd` | S | 354 → 314 | 0.887 | 290 → 312 | 1.076 |
| `easy/rosenbrock` | S | 28 → 28 | 1.000 | 26 → 26 | 1.000 |
| `easy/rosenbrock10` | S | 252 → 252 | 1.000 | 352 → 344 | 0.977 |
| `easy/schaffer` | S | 4 → 4 | 1.000 | 6 → 6 | 1.000 |
| `medium/bearing` | S | tiempo agotado → tiempo agotado | — | 25 704 (53.6 s) → 15 210 (49.2 s) | **0.592** |
| `medium/ex14_2_7` | P | 4 774 → 5 200 | 1.089 | 4 140 → 3 200 | **0.773** |
| `medium/ex2_1_7` | S | 12 → 12 | 1.000 | 12 → 12 | 1.000 |
| `medium/ex6_1_3bis` | P | 3 146 → 3 136 | 0.997 | 3 012 → 2 994 | 0.994 |
| `medium/ex6_2_11` | P | 12 182 → 11 578 | 0.950 | 10 782 → 10 152 | 0.942 |
| `medium/ex6_2_12` | P | 3 962 → 3 914 | 0.988 | 3 854 → 3 796 | 0.985 |
| `medium/ex6_2_14` | P | 554 → 554 | 1.000 | 528 → 532 | 1.008 |
| `medium/ex6_2_6` (tiempo agotado en todas) | P | 234 600 → 157 446 | — | 177 000 → 119 136 | — |
| `medium/ex6_2_8` | P | 18 014 → 16 360 | 0.908 | 16 800 → 15 402 | 0.917 |
| `medium/ex6_2_9` | P | 10 010 → 9 786 | 0.978 | 9 818 → 9 632 | 0.981 |
| `medium/ex8_4_4bis` | S | 120 168 (49.5 s) → **10 294 (6.9 s)** | **0.086** | 83 220 (52.2 s) → **8 618 (8.5 s)** | **0.104** |
| `medium/himmel16` | S | 4 186 → 4 058 | 0.969 | 1 430 → 1 760 | 1.231 |
| `medium/like` (sin punto factible) | S | 418 → 418 | — | 418 → 418 | — |
| `medium/like-1` (no acotado) | S | 320 → 320 | — | 320 → 320 | — |

**Resumen del cociente de celdas.** Instancias con uso resueltas en ambas corridas; *gana* < 0.95,
*pierde* > 1.05; *media geom.* = media geométrica.

| Comparación | Grupo | n | Gana | Empata | Pierde | Media geom. | Media geom. sin `ex8_4_4bis` |
|---|---|---|---|---|---|---|---|
| `raak` / `art` | todas con uso | 24 | 3 | 15 | 6 | 0.941 | 1.044 |
| | solo productos (P) | 12 | 1 | 7 | 4 | 1.029 | — |
| | con cuadrados (S, PS) | 12 | 2 | 8 | 2 | 0.861 | 1.062 |
| `raakcompo` / `compo` | todas con uso | 26 | **9** | 13 | 4 | **0.892** | 0.972 |
| | solo productos (P) | 12 | 6 | 5 | 1 | 0.937 | — |
| | con cuadrados (S, PS) | 14 | 3 | 8 | 3 | 0.855 | 1.005 |

### Costo

Los barridos comparan tiempos medidos **en sesiones distintas**, así que sus cocientes de CPU no sirven
para medir el sobrecosto. Medición controlada: 10 instancias donde RAA-K no se usa (CPU de `art` entre 0.9
y 10.5 s en la línea base), corridas **secuenciales** en una misma sesión, 3 repeticiones con el orden
de las variantes rotado. `raak:0` ejecuta exactamente la misma aritmética que `art`, así que su
desviación mide el **ruido**. `raak:3` agrega el filtro, la verificación de los cuadrados y los contadores.

> *CPU* = mediana de las 3 repeticiones, en segundos. *Cociente* = CPU de la variante ÷ CPU de `art`.
> *Dispersión* = (máx − mín) ÷ mediana de las repeticiones de `art`. En las 10 instancias las tres
> variantes exploran exactamente las mismas celdas.

| Instancia | `art` | `raak:0` | `raak:3` | `raak:0` / `art` | `raak:3` / `art` | Dispersión de `art` |
|---|---|---|---|---|---|---|
| `easy/ex7_2_3` | 9.43 | 10.28 | 8.26 | 1.090 | 0.876 | 11.6% |
| `medium/alkyl` | 2.12 | 2.39 | 2.24 | 1.130 | 1.055 | 15.3% |
| `medium/alkylbis` | 12.61 | 13.35 | 13.59 | 1.059 | 1.078 | 14.0% |
| `medium/ex2_1_9` | 9.36 | 8.76 | 9.61 | 0.936 | 1.027 | 6.0% |
| `medium/ex2_1_9fact` | 9.51 | 9.15 | 9.22 | 0.963 | 0.970 | 23.1% |
| `medium/ex5_3_2` | 1.40 | 1.39 | 1.29 | 0.996 | 0.923 | 19.1% |
| `medium/ex7_3_4` | 1.06 | 1.15 | 1.26 | 1.091 | 1.189 | 20.4% |
| `medium/ex7_3_5bis` | 2.58 | 3.05 | 2.55 | 1.180 | 0.987 | 5.2% |
| `medium/ex8_5_2_1` | 3.88 | 4.13 | 3.83 | 1.067 | 0.989 | 8.3% |
| `medium/launch` | 2.00 | 2.08 | 1.92 | 1.039 | 0.962 | 15.8% |
| **Media geométrica** | | | | **1.053** | **1.002** | |
| **Suma** | 53.93 | 55.73 | 53.77 | 1.033 | **0.997** | |

**El sobrecosto de RAA-K v2 no se distingue del ruido de medición** (cociente 1.00, frente a un
ruido de ±5% en media y hasta 18% por instancia). Además, estas mismas instancias corrieron un **20–30%
más lento** que en la sesión de la línea base (p. ej. `ex2_1_9` con `art`: 7.6 s → 9.4 s), una variación
entre sesiones del tamaño del ×1.4–1.5 que mostraban los barridos.

> **Corrección a §11.** El ×1.5 de CPU atribuido a RAA-K v1 venía de comparar sesiones distintas y
> no puede atribuirse al prototipo. v1 calculaba la cota en todos los productos, así que tenía algún
> sobrecosto real, pero no se midió de forma controlada. Las tres corridas que v1 perdió por tiempo
> estaban a 49–54 s del límite de 60 s, lo que es compatible con esa variación entre sesiones.

### Lecturas

1. **El filtro es exacto** (111 de 111 corridas idénticas a v1) y evita calcular la cota en ~95% de los
   productos.
2. **Los cuadrados duplican el alcance** (de 16 a 29–30 instancias) y dan **el mayor efecto observado
   hasta ahora**: `ex8_4_4bis` explora ~10 veces menos nodos y resuelve en 7–8 s en lugar de 50 s, y
   `bearing` con `raakcompo` baja un 41% sus celdas.
3. **La ganancia está concentrada.** Sin `ex8_4_4bis`, el grupo con cuadrados queda neutro (medias
   geométricas 1.06 y 1.005) y hay retrocesos nuevos: `ex14_2_4` y `ex14_2_5` con `raak` (que en v1,
   sin cuadrados, estaban en 0.82 y 1.14) y `ex8_1_7` y `himmel16` con `raakcompo`.
4. **`raakcompo` sigue siendo la mejor combinación**: gana 9 y pierde 4 (media geom. 0.89; 0.97 sin
   `ex8_4_4bis`). Con `art` solo, el efecto es neutro salvo por `ex8_4_4bis`.

---

## 13. QPLIB: la cota k-nomial evaluada dentro de IBEX

> **Terminología.** RAA-K es un método nuevo: generaliza la reducción binomial por presupuesto
> diagonal de [B] a bloques k-nomiales y la integra en la multiplicación de la aritmética afín.
> "Referencia" aquí significa la implementación en Python del notebook (`knomial.py` y `af2_error`),
> no resultados publicados. `kn2` corresponde a la variante binomial (k = 2), pero con las desviaciones
> de [B] que documenta `RESUMEN_RAA_modular.md` (`mode='sdsos'`, `sign_mode='fixed'`); `kn3` es RAA-K.

### Por qué no un B&B

Las instancias QPLIB del notebook tienen entre 30 y 175 variables, con objetivo cuadrático no convexo
y restricciones. A esos tamaños la optimización global certificada no termina (ya advertido en
`qplib/README.md`). En su lugar se mide **el radio de la forma afín de `xᵀQx` sobre la caja**, que es
exactamente lo que cuantifica la métrica en forma cerrada del notebook (`af2_error`, construida con las
Prop. 1 y 2 de [B]; equivale a 2 × radio) y lo que linealiza `art`.

### Diseño

- **Instancias:** las 58 de `qplib/inst/` con caja finita (todas con cajas `[0, 1]`); parte cuadrática
  del objetivo, `xᵀQx` con `Q = ½·Q⁰` (la parte lineal es exacta en aritmética afín y no cambia el radio).
- **Formulaciones** (todas son la misma función), generadas por `qplib/qplib_ibex_forms.py`:

| Formulación | Cómo se escribe `xᵀQx` |
|---|---|
| `mono` | Monomios `Q_ii·x_i²` y `2Q_ij·x_i·x_j`, como en un `.bch` |
| `kn2`, `kn3` | Reescritura de `knomial.py` con k = 2 y 3: residuo en monomios + `Σ c·(uᵀx)²` |
| `eig` | Descomposición espectral `Σ λ·(vᵀx)²` |

- **Evaluación:** `qplib_affine_eval.cpp` suma los términos con la aritmética afín de ibex-affine (la
  misma que usa `AffineEval`), con `raak_k = 0` (fAF2) y `raak_k = 3` (RAA-K).
- Datos: `~/ibex-local/results/qplib-eval-20260914-212602/` (`eval.csv`, `predicciones.json`).

### Controles

| Control | Resultado |
|---|---|
| `mono`: mismo radio con `raak_k = 0` y `raak_k = 3` (variables sueltas) | 58 de 58 |
| 2 × radio de IBEX frente a `af2_error` de Python (desviación relativa máxima) | `mono` 8.9e-12 · `kn2` 6.8e-12 · `kn3` 6.5e-12 · `eig` 1.6e-13 |
| Identidad de las reescrituras, máx. \|Q reconstruida − Q\| | `kn2`/`kn3` 8.9e-16 · `eig` 7.6e-11 |

**La implementación en C++ coincide con la de referencia en Python** en instancias reales.

### Resultados

> *Reducción* = promedio sobre las instancias de (1 − radio de la formulación ÷ radio de `mono` con
> fAF2), en %. **Positivo = cota más ajustada**; negativo = más holgada. *Predicción de Python* = la
> misma reducción calculada con `af2_error` en forma cerrada.

| Grupo | Instancias | `kn2` RAA-K | `kn3` RAA-K | `kn3` fAF2 | `eig` RAA-K | `eig` fAF2 |
|---|---|---|---|---|---|---|
| Diagonal no nula | 37 | **2.65%** | **4.39%** | 0.00% | −186% | −464% |
| Diagonal cero | 21 | 0.00% | 0.00% | 0.00% | −193% | −480% |
| Todas | 58 | 1.69% | 2.80% | 0.00% | −189% | −469% |
| *Predicción de Python (diagonal no nula)* | 37 | *2.65%* | *4.39%* | — | — | — |

- **Mayores reducciones con `kn3`:** la familia QBL `10040`–`10054`, con diagonal completa, llega a
  9–10% (p. ej. `10040`: 9.9%, `10054`: 9.8%, `10043`: 9.0%), y `10072`/`10073` a 8%. En QCQ el
  máximo es `1507` (6.2%).
- **`eig`** es peor que `mono` en 56 de 58 instancias (radio entre 1.1 y 6.3 veces). Solo mejora en
  `3751` y `3714` (7.6% y 7.5%), que tienen apenas 3 autovalores positivos: son casi cóncavas.
- **Costo:** evaluar una formulación toma a lo sumo 80 ms (n = 175).

### Lecturas

1. **Validación de punta a punta.** El prototipo en IBEX calcula la misma cota que la implementación en Python, con
   diferencia relativa ≤ 1e-11, en 58 instancias reales.
2. **Toda la ganancia viene de RAA-K en los cuadrados, y exige escribir el modelo reescrito.** La
   reescritura evaluada con fAF2 da exactamente el mismo radio que los monomios (0.00%). A la vez,
   RAA-K en la aritmética no puede recuperar la ganancia desde un modelo en monomios, porque cada
   producto involucra variables sueltas. En IBEX, la reescritura k-nomial tiene que aplicarse **al
   modelar** (o como un nodo de forma cuadrática), no solo producto a producto.
3. **La magnitud es modesta:** 4.4% en promedio con k = 3 en instancias con diagonal (hasta ~10%), y
   0% en el 36% de las instancias (diagonal cero). Coincide con el hallazgo del notebook.
4. **La descomposición espectral no es alternativa:** aun con cuadrados exactos, cada autovector
   reparte el cuadrado sobre todas las variables con signos mezclados y la cota queda ~3 veces más
   holgada.

**Limitaciones.** Solo la caja raíz y la parte cuadrática del objetivo; se ignoran las restricciones.
Con anchos uniformes, los cocientes de radio no cambian al achicar la caja uniformemente, pero en un
B&B las cajas se vuelven no uniformes tras bisecar, y la reescritura calculada en la raíz ya no es la
que elegiría `knomial` en cada nodo.

### Próximo paso propuesto

Aplicar la reescritura **a los `.bch`** de los QP de `benchs/optim` (familia `ex2_1_*`, donde `art` ya
reducía mucho los nodos): extraer `Q` del objetivo, escribirlo como residuo + `Σ c·sqr(uᵀx)` y correr el
B&B con `raak` frente a `art`. Es la prueba directa de si una reducción del radio de ~4–10% se traduce
en menos nodos.

---

## 14. Separación de efectos: RAA de [A] frente a reescritura k-nomial

### Motivo

`art` y `compo` usan **fAF2**, la aritmética afín de ibex-affine, cuya multiplicación es la de Vu,
Sam-Haroud y Faltings (2004, Ec. 17). **No es la RAA de [A]** que usa el notebook. Por eso `raak`
frente a `art` mezclaba dos efectos: pasar de fAF2 a la RAA de [A] y agregar la reescritura k-nomial.
Para separarlos, el modo `raak_k = 1` implementa la parte cuadrática de la RAA de [A]:

| `raak_k` | Productos | Cuadrados de formas compuestas | Errores de los factores |
|---|---|---|---|
| 0 (`art`, `compo`) | fAF2: radio `Sx·Sy − ½Sxy` | fAF2 | fAF2 |
| **1** | **RAA de [A]:** `Q` simetrizada, Chebyshev en `xᵢ²` y envolvente plana en `xᵢxⱼ` | **RAA de [A]:** Chebyshev, rango exacto `[0, (Σ\|aᵢ\|+e)²]` | fAF2 |
| **3** (RAA-K) | Lo anterior + **reescritura k-nomial** | Igual que k = 1 | fAF2 |

La propagación de los errores de los factores sigue siendo la de fAF2 en todos los modos (no se portó
el corner test de [A]), así que `raak_k = 1` es **la parte cuadrática** de la RAA de [A], no la RAA completa.

**Cambio respecto de §12:** la cota de Chebyshev de los cuadrados se activaba con k ≥ 2; ahora se
activa con k ≥ 1. Con k = 3 no cambia nada: se verificó que 4 corridas reproducen exactamente las
celdas del barrido v2, y lo confirman los controles de abajo.

**Datos:** barrido `raak_k = 1` en `~/ibex-local/results/baseline-20260915-025226/` (incluye
`descomposicion_k1_k3.csv`), con los mismos parámetros que §3. Se compara con la línea base (§3) y con el
barrido `raak_k = 3` de §12. Solo se comparan **celdas**: los barridos son de sesiones distintas y la CPU no
es comparable (§12, *Costo*).

### Controles

| Control | Con `art` | Con `compo` |
|---|---|---|
| Instancias sin uso con k = 1 y resueltas: celdas idénticas a la base | 101 de 101 | 101 de 101 |
| Instancias sin bloques con k = 3 y resueltas: celdas idénticas a k = 1 | 109 de 109 | 111 de 111 |
| Estados de las corridas (base, k = 1, k = 3) | idénticos (123 resueltas) | idénticos (125 resueltas) |
| Prueba aritmética: cuadrados con k = 1 idénticos a k = 3 | 3 000 de 3 000 | — |

### Alcance

| | Con `art` | Con `compo` |
|---|---|---|
| Instancias donde la RAA de [A] mejora alguna operación (k = 1) | 23 (productos 9, cuadrados 15) | 24 (productos 9, cuadrados 16) |
| Instancias con bloques k-nomiales (k = 3) | 12 | 12 |

### Efectos sobre las celdas

> *Cociente* = celdas de la variante ÷ celdas de la referencia, en instancias resueltas por ambas;
> **menor que 1 = menos nodos**. *Gana* < 0.95, *pierde* > 1.05. *Media geom.* = media geométrica.
> Cada efecto se mide en las instancias donde actúa: la RAA de [A] donde k = 1 mejora alguna operación;
> el k-nomial donde k = 3 extrae bloques; el total donde hay algún uso.

| Linearizador | Efecto | Cociente | n | Gana | Empata | Pierde | Media geom. | Media geom. sin `ex8_4_4bis` |
|---|---|---|---|---|---|---|---|---|
| `art` | RAA de [A] | k=1 / `art` | 19 | 3 | 13 | 3 | 0.880 | 1.001 |
| `art` | k-nomial | k=3 / k=1 | 11 | 2 | 5 | 4 | 1.093 | — |
| `art` | total | k=3 / `art` | 24 | 3 | 15 | 6 | 0.941 | 1.044 |
| `compo` | RAA de [A] | k=1 / `compo` | 21 | 4 | 11 | 6 | 0.927 | 1.034 |
| `compo` | **k-nomial** | k=3 / k=1 | 11 | **6** | 5 | **0** | **0.881** | — |
| `compo` | total | k=3 / `compo` | 26 | 9 | 13 | 4 | 0.892 | 0.972 |

**Efecto k-nomial por instancia** (celdas con k = 1 → k = 3; instancias con bloques):

| Instancia | Bloques (`art`) | `art`: k=1 → k=3 | Cociente | `compo`: k=1 → k=3 | Cociente |
|---|---|---|---|---|---|
| `easy/ex14_2_4` | 30 519 | 2 564 → 3 692 | 1.440 | 166 → 92 | **0.554** |
| `easy/ex14_2_5` | 180 | 14 → 22 | 1.571 | 48 → 38 | 0.792 |
| `easy/ex14_2_6` | 2 010 | 242 → 206 | 0.851 | 174 → 170 | 0.977 |
| `easy/ex14_2_9` | 268 | 38 → 56 | 1.474 | 44 → 40 | 0.909 |
| `medium/ex14_2_7` | 144 893 | 4 606 → 5 200 | 1.129 | 4 196 → 3 200 | **0.763** |
| `medium/ex6_1_3bis` | 4 342 | 3 136 → 3 136 | 1.000 | 3 004 → 2 994 | 0.997 |
| `medium/ex6_2_11` | 23 751 | 12 182 → 11 578 | 0.950 | 10 782 → 10 152 | 0.942 |
| `medium/ex6_2_12` | 7 803 | 3 962 → 3 914 | 0.988 | 3 854 → 3 796 | 0.985 |
| `medium/ex6_2_14` | 1 890 | 554 → 554 | 1.000 | 528 → 532 | 1.008 |
| `medium/ex6_2_8` | 39 619 | 18 014 → 16 360 | 0.908 | 16 800 → 15 402 | 0.917 |
| `medium/ex6_2_9` | 29 368 | 10 010 → 9 786 | 0.978 | 9 818 → 9 632 | 0.981 |
| `medium/ex6_2_6` (tiempo agotado) | 56 314 | 230 148 → 157 446 | — | 181 866 → 119 136 | — |

**Efecto de la RAA de [A]: casos notables** (celdas base → k = 1):

| Instancia | Uso | `art` → k=1 | Cociente | `compo` → k=1 | Cociente |
|---|---|---|---|---|---|
| `medium/ex8_4_4bis` | cuadrados | 120 168 → 10 294 | **0.086** | 83 220 → 8 618 | **0.104** |
| `medium/bearing` | cuadrados | tiempo agotado → tiempo agotado | — | 25 704 → 15 210 | **0.592** |
| `easy/ex14_2_6` | productos | 210 → 242 | 1.152 | 242 → 174 | 0.719 |
| `easy/ex14_2_9` | productos | 50 → 38 | 0.760 | 44 → 44 | 1.000 |
| `easy/ex14_2_4` | ambos | 2 620 → 2 564 | 0.979 | 98 → 166 | 1.694 |
| `easy/ex8_1_7` | cuadrados | 292 → 298 | 1.021 | 264 → 394 | 1.492 |
| `easy/ex14_2_8` | productos | 22 → 28 | 1.273 | 32 → 40 | 1.250 |
| `medium/himmel16` | cuadrados | 4 186 → 4 058 | 0.969 | 1 430 → 1 760 | 1.231 |

### Lecturas

1. **Las dos grandes mejoras de §12 son de la RAA de [A], no de RAA-K.** `ex8_4_4bis` (~10 veces
   menos nodos) y `bearing` (−41% con `compo`) mejoran por la cota de Chebyshev de los cuadrados, que
   ya está en k = 1. §12 las había atribuido a RAA-K.
2. **Fuera de `ex8_4_4bis`, pasar de fAF2 a la RAA de [A] es neutro o levemente negativo** en celdas
   (media geométrica 1.00 con `art` y 1.03 con `compo`), con mucha variación por instancia.
3. **El efecto propio del k-nomial depende del linearizador.** Sobre la RAA de [A] y con `compo`, reduce
   las celdas en las 11 instancias con bloques sin perder en ninguna (media geométrica 0.88; hasta
   −45% en `ex14_2_4`). Con `art` solo, el efecto es negativo (1.09), concentrado en la familia
   `ex14_2_*`, que tiene pocas celdas y es sensible al recorrido del B&B.
4. **Por qué `art` empeora pese a encierros más ajustados no está establecido.** Una hipótesis es que
   el LP y la bisección siguen otro recorrido. Con 11 instancias y una corrida, no se puede distinguir de
   la variabilidad.

**Limitaciones:** 11 instancias con bloques; una corrida por variante; la "RAA de [A]" implementada es
solo su parte cuadrática (errores propagados como en fAF2).

---

## Reproducir

Dentro de Ubuntu (WSL):

```bash
cd ~/ibex-local/scripts
TLIM=60 P=4 ./wsl_baseline.sh           # barrido completo (~5 min)
./wsl_analyze.sh                        # análisis del barrido más reciente
```
