# Código agregado: qué es cada función y qué hace

Inventario de todo lo que este proyecto añade sobre `ibex-affine` (commit `c219009`) y sobre el fork
`rilianx/ibex-lib` (`5e51fffc`). Nada del código original se borra: los cambios se insertan con el
marcador `[raak local]` y los caminos originales siguen ejecutándose cuando el interruptor
correspondiente está apagado (y son entonces bit a bit idénticos). Los cambios C++ se aplican como
parches numerados (`raak/patches/`, cada uno con su cabecera "Qué cambia / Por qué / Verificado").

Convenciones: `AF_fAF2` = modelo denso del plugin (`Affine2`), base de las variantes **AF2** y **RAA**;
`AF_fAFFullI` = modelo disperso (`Affine3`), la **AA** tradicional. `[A]` y `[B]` son los papers
citados en `README.md`.

---

## 1. `ibex_KNomial.h` (nuevo, solo cabecera) — reducción k-nomial e interruptores

| Función / tipo | Qué hace |
|---|---|
| `knomial_max_k()` | Interruptor por hilo (`thread_local int&`). `0` = sin reescritura k-nomial; `k ≥ 2` = reescritura SDSOS con cliques de hasta `k` variables. Lo fija el CLI (`--knomial_k`). |
| `enum AffineMode { AFFINE_AF2, AFFINE_RAA }`, `affine_mode()` | Segundo interruptor por hilo: qué aritmética usa `AffineMain<AF_fAF2>` en productos y cuadrados (AF2 original o la RAA de [A]). No afecta a `AF_fAFFullI`. |
| `struct KNomialBlock { c; u }` | Un bloque `c·(uᵀx)²` extraído por la reescritura. |
| `knomial_detail::benefit(clique, Q, C, w, n)` | Para un clique de variables, la escala `λ` (mínimo de `|Q_uv| / sqrt(C_u C_v)` sobre las aristas) y la ganancia `ΔE = Σ λ sqrt(C_u C_v) w_u w_v / 2` (modo `sdsos` de `knomial.py`). |
| `knomial_detail::bfs_signs(S, Q, n, r, sign, tol)` | Asigna signos `s_v` a las variables del clique de modo que `s_u s_v = sign(r Q_uv)` en toda arista (BFS); devuelve si el clique es balanceado. |
| `knomial_detail::intersect(a, b)` | Intersección de dos `std::set<int>` (candidatos a extender un clique). |
| `knomial_rewrite(Q, w, n, max_k, blocks, tol)` | El método: simetriza `Q`, calcula el presupuesto diagonal `C_i = |Q_ii|`, construye el grafo de aristas con diagonal del mismo signo, y con un max-heap de ganancias extrae greedy bloques `r·(Σ s_v sqrt(λ C_v) x_v)²` de hasta `max_k` variables, descontando presupuesto y aristas. Deja en `Q` el residuo `Q_res` y devuelve el número de cliques degradados al par base. Port bit a bit de `raa_lib/knomial.py` (`mode='sdsos'`, `sign_mode='fixed'`). |
| `struct KNomialStats`, `knomial_stats()` | Contadores por hilo (productos evaluados, bloques, cotas usadas, radios acumulados, cuadrados, corner test, AA). Solo diagnóstico; los imprime el CLI. |
| `knomial_quad_bound(x, y, n, max_k, shift, rad)` | Cota de la parte cuadrática `εᵀQε` de un producto de formas afines en coordenadas de ruido (`Q = (xyᵀ + yxᵀ)/2`, `ε ∈ [−1,1]ⁿ`): comprime a los símbolos presentes, reescribe con `knomial_rewrite` si `max_k ≥ 2` y acota bloque a bloque (`c (uᵀε)² ∈ [0, (Σ|uᵢ|)²]`), diagonal residual (`Q_ii ε_i² ∈ [0, Q_ii]`) y cruces residuales (`2|Q_ij|`). Devuelve `shift` (lo que se suma al centro) y `rad` (radio), más un margen heurístico por el redondeo de la reescritura. Con `max_k < 2` es la forma simétrica término a término (la parte cuadrática de la RAA de [A]). |
| `knomial_quad_bound_sparse(rx, ry, max_k, shift, rad)` | Versión para `AF_fAFFullI`: alinea dos listas dispersas `(id, coef)` por unión ordenada de ids y llama a `knomial_quad_bound`. |
| `raa_corner_cross(a, b, ex, ey, em)` | Corner test de la Ec. (16) de [A] en coordenadas de ruido: `max_s Σᵢ |ey·aᵢ + s·ex·bᵢ|` (los cruces de los errores `ex`, `ey` de los factores con sus partes lineales; el máximo está en una esquina de `[−1,1]²`), mayorado por el redondeo. Sustituye a `ex·Sy + Sx·ey` de fAF2 cuando es menor. |

## 2. `ibex_Affine2_fAF2.cpp` — multiplicación y cuadrado de AF2 / RAA

| Dónde | Qué se agregó |
|---|---|
| `AffineMain<AF_fAF2>::operator*=(const AffineMain&)` | Bloque `[raak local]` que (i) copia los coeficientes de ruido de ambos factores antes de que se sobrescriban; (ii) filtro exacto: solo intenta la cota alternativa si `x` e `y` comparten ≥ 2 símbolos (`kcand`); (iii) con `AFFINE_RAA` o `k ≥ 2` calcula `knomial_quad_bound` y la usa (`use_raak`) solo si mejora a fAF2 más allá de su margen; (iv) con `AFFINE_RAA` y algún factor con error aplica `raa_corner_cross` (`use_corner`) si mejora; (v) recompone el error `_err` con `qerr` (cruces + cuadrático) o, si nada mejora, con la fórmula original de fAF2, bit a bit. |
| `AffineMain<AF_fAF2>::Asqr(const Interval&)` | Con `AFFINE_RAA`: la parte cuadrática `(aᵀε + e·h)²` se acota por su rango exacto `[0, (Sx+e)²]` (Chebyshev del cuadrado, RAA de [A]) en lugar de centro `Sx2/2` y radio `(Sx+e)² − Sx2/2`; solo si mejora (`use_raak_sq`). Con `AFFINE_AF2` el cuadrado es siempre el original. |

## 3. `ibex_Affine3_fAFFullI.cpp`, `ibex_AffineMain.h`, `ibex_AffineMain_impl.h` — AA tradicional

| Función | Qué hace |
|---|---|
| `AffineMain<AF_fAFFullI>::operator*=` (bloque `[raak local]`) | Con `knomial_max_k() ≥ 2`: la parte no lineal `(aᵀε + gx)(bᵀε + gy)` se acota con `knomial_quad_bound_sparse` sobre la unión de rayos más los cruces con los `_garbage` en aritmética de intervalos, en lugar de `rad(x)·rad(y)`; solo si estrecha el intervalo. El rayo nuevo lo crea, como siempre, `operator+(Interval)`. |
| `AffineMain<T>::nonvar_noise_sum(int nb_var)` (nuevo, genérico y especializado para `AF_fAFFullI`) | Suma de `|coef|` de los símbolos de ruido que no son variables (índice o id ≥ `nb_var`), con redondeo hacia arriba. Es la parte del error que `err()` no incluye en Affine3 (los rayos creados por operaciones no afines). |

## 4. `ibex_LinearizerAffine2.{h,cpp}` — relajación lineal con cualquier modelo afín

| Función / tipo | Qué hace |
|---|---|
| `template<class T> class LinearizerAffineT` | El antiguo `LinearizerAffine2` parametrizado por el modelo afín; `LinearizerAffine2` es ahora `LinearizerAffineT<AF_fAF2>` (mismo código). Instanciado también para `AF_fAFFullI`. |
| `affine_form_is_linearizable<T>(af, nb_var)` | Cuándo una forma se puede convertir en restricción lineal: `AF_fAF2` exige `is_active() && noise_count() == nb_var`; `AF_fAFFullI` solo `is_active()`. Incluye el arreglo del parche 0001 (una forma no activa no tiene coeficientes: antes producía segfault). |
| `affine_extra_error<T>(af, nb_var)` | Error adicional que se suma a `err()` en la relajación: `0` para `AF_fAF2`; `nonvar_noise_sum(nb_var)` para `AF_fAFFullI` (relajar cada símbolo no-variable como `|coef|·[−1,1]` es válido). |

## 5. `ibex_AffineTrig.h` y `ibex_AffineMain_trig_impl.h` (nuevos) — seno y coseno (Fase 2)

| Función / tipo | Qué hace |
|---|---|
| `enum TrigLinMode { TRIG_AUTO, TRIG_CHEBYSHEV, TRIG_MINRANGE, TRIG_LEGACY }`, `trig_lin_mode()` | Interruptor por hilo de la linealización de `sin`/`cos`. `AUTO` (por defecto) sigue el modo Chebyshev/MinRange del plugin; `LEGACY` = código original. Lo fija el CLI (`--trig`). |
| `trig_lin_resolve(bool mode_is_minrange)` | Traduce `TRIG_AUTO` al modo efectivo. |
| `struct TrigLinStats`, `trig_lin_stats()` | Contadores por hilo (cuántas linealizaciones por modo, cuántas degeneraron a intervalo). |
| `trig_residual_range(is_sin, alpha, itv, residual)` | **Mecanismo general** (Sec. 3.2 de [A], pasos 1–3): rango con redondeo exterior de `g(v) = f(v) − αv` sobre `itv`, evaluando `g` en los extremos y en todos los puntos críticos `f'(v) = α` (`±acos α + 2kπ` para `sin`; `asin(−α) + 2kπ` y `π − asin(−α) + 2kπ` para `cos`). Hace válida la forma aunque el intervalo contenga extremos o puntos de inflexión. Devuelve `false` si el número de períodos no cabe en un `int`. |
| `AffineMain<T>::Atrig_apply(alpha, residual)` | Paso final común: `*this ← α·(*this) + mid(residual) ± rad(residual)` (mismo patrón que `Aexp_CH` y las demás unarias del plugin). |
| `AffineMain<T>::Asin_CH`, `Acos_CH` | Pendiente de cuerda `α = (f(b) − f(a))/(b − a)` (Ec. 12 de [A]: el "Chebyshev" de la RAA) + `trig_residual_range`. Casos particulares idénticos al original (forma no activa, vacío, no acotado, `diam < AF_EC`, `diam ≥ 2π` → intervalo). |
| `AffineMain<T>::Asin_MR`, `Acos_MR` | Min-range: si `f'` se anula en `itv` (extremo dentro) → `α = 0`, la forma es el intervalo `f(itv)`; si no, `α = f'` en el extremo con menor `|f'|`, con lo que la anchura de la forma es exactamente la del rango de `f`. |
| Despacho en `AffineMain<T>::Asin` / `Acos` (`ibex_AffineMain_impl.h`) | Un `switch` al comienzo de cada una: `CHEBYSHEV → *_CH`, `MINRANGE → *_MR`, `LEGACY → cae al código original`, que no se toca. |

## 6. `ibex_Optimizer04Config.cpp` (fork de ibex-lib, parche 0003)

`get_ctc()` envuelve también las relajaciones `raak`/`raakcompo` en `CtcPolytopeHull` (2 líneas). Con el
CLI nuevo ya no hace falta (los alias se traducen a `art`/`compo`), pero se conserva por compatibilidad.

## 7. `ibexopt-raak` (`raak/cli/`)

| Archivo / función | Qué hace |
|---|---|
| `cli_ibexopt_raak.cpp`, `main()` | Copia adaptada de `ibexopt_config04.cpp` del fork. Parsea `--lr=xn\|art\|compo`, `--arith=af2\|raa\|aa`, `--knomial_k=K`, `--trig=auto\|cheb\|minrange\|legacy`, los alias de compatibilidad (`--lr=raak`, `--raak_k`), fija los tres interruptores por hilo (`affine_mode`, `knomial_max_k`, `trig_lin_mode`), construye `Optimizer04Config_Affine` y el `Optimizer`, y al final imprime `RAA-K stats:` y `TRIG stats:`. |
| `Optimizer04Config_Affine` (`cli_Optimizer04Config_Affine.{h,cpp}`) | Subclase de `Optimizer04Config` que sobreescribe `get_linear_relax()`: `xn` → `LinearizerXTaylor`; `art` → `LinearizerAffine2` (AF2/RAA) o `LinearizerAffineT<AF_fAFFullI>` (AA); `compo` → `LinearizerCompo(XTaylor, afín)`. |

## 8. Programas de prueba y evaluación (`raak/tests/`)

| Programa | Qué comprueba |
|---|---|
| `knomial_golden.cpp` | `knomial_rewrite` reproduce los bloques y `Q_res` de la referencia Python (`knomial_golden.txt`, 80 casos). |
| `raak_arith_test.cpp` | Productos y cuadrados aleatorios de `Affine2` en los cuatro modos históricos: contención, pendientes invariantes, radio nunca mayor que fAF2, filtro exacto. |
| `raa_corner_test.cpp` | Corner test: 10 000 pares, contención por muestreo, radio no mayor, bit a bit con la referencia cuando no hay error. |
| `aa_knomial_test.cpp` | k-nomial en `Affine3`: contención (rayos nuevos como símbolos libres), radio, k=0 bit a bit. |
| `aa_linearizer_test.cpp` | La relajación con `LinearizerAffineT` contiene a `f` en 200 polinomios × 1000 puntos (AA k=0/k=3, AF2). |
| `six_variants_test.cpp` | Las seis variantes sobre los mismos productos y cuadrados: contención, radio medio, identidad bit a bit por pares. |
| `trig_lin_test.cpp` (Fase 2.2) | `sin`, `cos`, `sin²+cos²`, `sin·cos` en 735 intervalos × {AF2, AA} × {legacy, cheb, minrange}: contención, sobreestimación, error de linealización, tiempo. |
| `range_eval.cpp` (Fase 3, nivel 1) | Sobreestimación de las seis variantes sobre objetivo y restricciones de cada instancia, en la caja inicial y sub-cajas, con contención por muestreo. |
| `qplib_affine_eval.cpp` | Evaluador de formas cuadráticas QPLIB (trabajo previo). |

## 9. Scripts (`raak/scripts/`) y análisis (`raak/analysis/`)

| Script | Qué hace |
|---|---|
| `wsl_setup_env.sh`, `wsl_clone.sh`, `wsl_build_*.sh`, `wsl_build_all.sh` | Reconstruyen el entorno WSL: dependencias, clonado y fijado de los repos, compilación e instalación de ibex-lib, ibex-affine y el CLI. |
| `wsl_save_patch.sh` | Guarda el cambio incremental del árbol de trabajo como parche numerado y verifica que la cadena completa aplica en limpio. |
| `wsl_run_test.sh` | Compila y ejecuta un test C++ contra el prefix instalado. |
| `wsl_fase1_runs.sh` | Corre `ibexopt-raak` sobre instancias × variantes, escribe `runs.csv` y compara con una referencia. |
| `wsl_fase1_ref*.sh`, `wsl_fase1_paso1*.sh` | Pasos de aceptación de la Fase 1 (referencia bit a bit, cada parche). |
| `wsl_fase2_paso21.sh` | Fase 2: recompila, corre `trig_lin_test`, los tests de la Fase 1, la regresión sin trigonométricas, las instancias con `sin`/`cos` por modo, y guarda el parche 0008. |
| `wsl_fase3_nivel1.sh` | Fase 3 nivel 1: compila y corre `range_eval` sobre todos los conjuntos de `benchs/optim`. |
| `wsl_fase3_sweep.sh`, `wsl_fase3_status.sh` | Fase 3 nivel 2: barrido reanudable en paralelo con las seis variantes (+ `xn`), y su monitor. |
| `analysis/analyze_trig.py` | Fase 2.2: tablas y gráficos de calidad de `sin`/`cos`. |
| `analysis/analyze_range.py` | Nivel 1: sobreestimación por variante, separación de efectos aritmética / k-nomial. |
| `analysis/analyze_sweep.py` | Nivel 2: victorias/derrotas/empates, medias geométricas, perfiles de desempeño, dispersión log-log, tabla consolidada y `README.md` de la carpeta de resultados. |
