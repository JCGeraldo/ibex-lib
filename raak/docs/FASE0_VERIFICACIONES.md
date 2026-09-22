# Fase 0 — Verificaciones previas

Fecha: 2026-09-21. Entorno: WSL Ubuntu 24.04 (`~/ibex-local`, ver `ENTORNO.md`).

## 0.1 La "línea 778 de ibex affine 2"

El único archivo del plugin cuyo nombre contiene "Affine2" y tiene más de 778 líneas es
`src/arithmetic/ibex_Affine2_fAF2.cpp` (la aritmética fAF2). El número de línea depende de qué
versión se mira, porque los parches locales insertan código antes:

| Versión del archivo | Función que contiene la línea 778 | Línea 778 |
|---|---|---|
| Upstream `c219009` (sin parches) | `AffineMain<AF_fAF2>::compact(double tol)` (empieza en 760) | `double eee = _elt.twoSum(_elt._err, std::fabs(_elt._val[i]), &temp);` |
| Rama `raak-experimentos` (c219009 + 0001 + 0002) | `AffineMain<AF_fAF2>::Asqr(const Interval&)` (empieza en 719) | `bool use_raak_sq = false;` (inicio del bloque `[raak local]` del cuadrado de Chebyshev) |
| Árbol de trabajo actual (0001..0007) | `AffineMain<AF_fAF2>::Asqr(const Interval&)` (empieza en 756) | línea en blanco dentro del bucle que acumula `Sx2 = Σ aᵢ²` y `Sx = Σ|aᵢ|` con `twoProd`/`twoSum` |

**Qué hace `compact(tol)` (versión upstream).** Recorre los coeficientes de ruido `_val[i]` y
los que son menores que `tol` en valor absoluto los pasa al término de error `_err` (con la
contabilidad de redondeo del plugin: `twoSum`, factor `(1+2·AF_EM)`, umbral `AF_EC`) y los pone a
cero. Es decir, "compacta" la forma afín sacrificando correlación por compacidad.

**¿Afecta a la implementación actual?** No. `compact()` solo se define; no se llama en ningún
punto del plugin (`grep -rn "compact(" src` solo muestra las definiciones y los envoltorios de
`AffineMainVector`/`AffineMainMatrix`) ni en el fork de ibex-lib, ni en `ibexopt-raak`. Si en el
futuro se llamara, sí importaría para RAA-K: al borrar coeficientes pequeños reduciría los
símbolos compartidos entre factores (el filtro de la multiplicación exige ≥ 2 compartidos) y
cambiaría las pendientes que usa el linearizador.

**Si la referencia era al archivo de la rama (línea 778 = `use_raak_sq`).** Ese bloque es el
cuadrado de Chebyshev de la RAA de [A]: para `sqr(x)` con `x = x₀ + Σaᵢεᵢ + e·h` reemplaza la cota
fAF2 de la parte cuadrática (centro `Sx2/2`, radio `(Sx+e)² − Sx2/2`) por su rango exacto
`[0, (Sx+e)²]`, solo si mejora. Tras el parche 0004 se activa solo con `--arith=raa` (antes con
`raak_k ≥ 1`). Está validado (3000 cuadrados sin violaciones ni radios mayores, ver Fase 1) y es
la fuente de las dos mayores mejoras observadas (`ex8_4_4bis`, `bearing`).

**Si la referencia era al archivo actual (bucle de `Asqr`).** Es código original del plugin (la
acumulación con transformaciones libres de error); no fue modificado por ningún parche.

## 0.2 Plugin de aritmética afín de Jordan Ninin

| Dato | Valor |
|---|---|
| Repositorio | `https://github.com/ibex-team/ibex-affine`, rama `update_affine` |
| Commit fijado | `c219009c` (2026-09-04, "update workflow"), rama local `raak` |
| Versión declarada | 1.0 (`project (IBEX_AFFINE VERSION 1.0)`, `ibex-affine.pc`) |
| Requiere | ibex ≥ 2.8.9.1 (instalado: fork `rilianx/ibex-lib` `5e51fffc`, versión 2.8.9.1) |
| Instalado en | `~/ibex-local/prefix` (`lib/libibex-affine.a`, `include/ibex-affine/*.h`) |
| Tests upstream | 11 suites CppUnit, **11/11 OK** (`make check`, 2026-09-21) |

Funcionalidades que ya provee (sin nuestros parches):

- Dos modelos intercambiables por plantilla `AffineMain<T>`:
  `Affine2` = `AF_fAF2` (vector denso de coeficientes + un término de error, todo el redondeo
  contabilizado con `twoSum`/`twoProd`) y `Affine3` = `AF_fAFFullI` (lista dispersa de símbolos
  con id global + intervalo `_garbage`; cada operación no afín crea un símbolo nuevo: es la AA
  tradicional de Stolfi). Los modelos extendidos (`AF_fAF1`, `AF_iAF`, `AF_sAF`, `AF_No`) están
  detrás de `_IBEX_WITH_AFFINE_EXTENDED_` y **sus cabeceras no están en el repositorio**.
- `Affine2Variables`/`Affine3Variables`: caja de variables afines; la componente `i` posee el
  símbolo `i`.
- Operaciones: `+ - * /`, `sqr`, `sqrt`, `inv`, `exp`, `log`, `pow`, `root`, `cos`, `sin`, `tan`,
  `acos`, `asin`, `atan`, `atan2`, hiperbólicas e inversas, `abs`, `sign`, `chi`, `integer`,
  `floor`, `ceil`, `saw`.
- Dos modos de linealización por hilo (`AffineMain<T>::change_mode`): Chebyshev (por defecto) y
  MinRange, con variantes `*_CH` y `*_MR` para `inv, sqrt, exp, log, cosh, tanh, atan, asin, acos,
  sinh, asinh, acosh, atanh, pow`. **`sin`, `cos` y `tan` tienen una sola implementación** (pendiente
  de la cuadratura de Gauss de dos puntos + residuo exacto en extremos y puntos críticos) que
  ignora el modo: no hay `Asin_CH/Asin_MR` ni `Acos_CH/Acos_MR`. Esto motiva la Fase 2.
- `AffineEval<T>` (evaluador de `Function` en aritmética afín), `LinearizerAffine2`
  (relajación lineal para `CtcPolytopeHull`), `CtcAffineFwdBwd`.

Estado de nuestros parches sobre él (verificado el 2026-09-21: la cadena 0001, 0002, 0004, 0005,
0006, 0007 aplica en limpio sobre `c219009` y reproduce el árbol de trabajo archivo a archivo):

| Parche | Contenido |
|---|---|
| 0001 | Segfault del linearizador con formas no activas |
| 0002 | Prototipo RAA-K: `ibex_KNomial.h` y k-nomial en la multiplicación/cuadrado de fAF2 |
| 0003 | (ibex-lib) `get_ctc()` acepta `raak`/`raakcompo` |
| 0004 | Separación de los interruptores `affine_mode()` (AF2/RAA) y `knomial_max_k()` |
| 0005 | Corner test de la Ec. (16) de [A] (propagación de errores de la RAA) |
| 0006 | k-nomial en la multiplicación de `AF_fAFFullI` (AA) |
| 0007 | `LinearizerAffineT<T>` para poder relajar con Affine3 |
| 0008 | (Fase 2) seno/coseno con cuerda (Chebyshev) y min-range |
