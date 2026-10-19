# Comparación de aritméticas afines con y sin reducción k-nomial — plan y bitácora

**Objetivo general:** determinar qué aritmética afín (AA tradicional, AF2 o RAA) produce las cotas
más ajustadas, cuantificar el aporte de la reducción k-nomial sobre cada una y evaluar si ese
aporte se traduce en mejor desempeño del solver.

| Aritmética | Sin k-nomial | Con k-nomial | En `ibexopt-raak` |
|---|---|---|---|
| AA tradicional (`Affine3` = `AF_fAFFullI`) | ✓ | ✓ | `--arith=aa --knomial_k=0 \| 3` |
| AF2 (`Affine2` = `AF_fAF2`, fAF2) | ✓ | ✓ | `--arith=af2 --knomial_k=0 \| 3` |
| RAA (paper [A], sobre `AF_fAF2`) | ✓ | ✓ | `--arith=raa --knomial_k=0 \| 3` |

Las seis variantes actúan solo cuando la relajación lineal usa formas afines (`--lr=art` o
`--lr=compo`); `--lr=xn` (X-Taylor) es el control sin aritmética afín.

Convenciones de todo el trabajo: los cambios C++ viven en el clon WSL de `ibex-affine` y se guardan
como parches numerados en `raak/patches/` (cada uno con su cabecera "Qué cambia / Por qué /
Verificado"); todo código agregado lleva el marcador `[raak local]` y no se borra código existente;
el archivo `CAMBIOS_CODIGO.md` lista cada función agregada. Un commit local por fase, sin push.

---

## Fase 0 — Verificaciones previas  ✅ (2026-09-21)

1. Línea 778 de `ibex_Affine2_fAF2.cpp`: analizada en las tres versiones del archivo
   (upstream = `compact()`, no se llama desde ningún sitio; rama = cuadrado de Chebyshev de la RAA;
   actual = bucle original de `Asqr`). No afecta a la implementación. → `FASE0_VERIFICACIONES.md` §0.1.
2. Plugin de Jordan Ninin: `ibex-team/ibex-affine` `c219009c` (2026-09-04), versión 1.0, instalado,
   11/11 tests. Inventario de funcionalidades y del estado de los parches. → `FASE0_VERIFICACIONES.md` §0.2.

## Fase 1 — Separación e implementación de aritméticas  ✅ (código 2026-09-16/17, consolidado 2026-09-21)

1. Las tres aritméticas activables por separado: `affine_mode()` ∈ {AF2, RAA} (parche 0004) sobre
   `AF_fAF2`; AA = `AF_fAFFullI` con su propio linearizador (0007). La RAA incluye la parte cuadrática
   (0002/0004: Q simetrizada, Chebyshev en `xᵢ²`, envolvente plana en `xᵢxⱼ`, cuadrados de
   Chebyshev) y la propagación de errores por esquinas de la Ec. (16) de [A] (0005).
2. k-nomial como opción independiente `knomial_max_k()` (0 ó ≥ 2) sobre las tres (0004, 0006).
   CLI: `--arith`, `--knomial_k` (más alias de compatibilidad `--lr=raak`, `--raak_k`).
3. Validación (re-ejecutada el 2026-09-21, `~/ibex-local/logs/fase1-validacion-*.log`):
   `knomial_golden` 80 casos / 327 bloques idénticos a la referencia Python; `raak_arith_test`
   3000 productos y 3000 cuadrados sin violaciones; `raa_corner_test` 10 000 pares, 2000 muestras,
   0 violaciones, bit a bit con la referencia sin error; `aa_knomial_test` 3000 productos Affine3,
   0 violaciones, k=0 bit a bit; `aa_linearizer_test` 200 polinomios × 1000 puntos, 0 violaciones;
   `make check` 11/11. Regresiones del B&B: 7 instancias × {xn, art, compo} idénticas a la
   referencia (`results/04-fase1-validacion/fase1-20260916/paso14/regresion/comparacion.txt`).

Pendiente conocido (heredado): el margen de redondeo de la reescritura k-nomial es heurístico
(fase de rigor F6, fuera de este plan).

## Fase 2 — Funciones trigonométricas  ✅ (2026-09-21)

1. Implementación (parche 0008): `Asin_CH/Acos_CH` (pendiente de cuerda = Chebyshev de la RAA,
   Ec. 12 de [A]) y `Asin_MR/Acos_MR` (min-range), con el mecanismo general de residuo exacto
   (`trig_residual_range`: extremos + todos los puntos críticos `f'(v)=α`, que cubre intervalos con
   extremos y puntos de inflexión). Interruptor `trig_lin_mode()` y flag `--trig`. El código
   original se conserva como `legacy`. Justificación en `FASE2_TRIGONOMETRICAS.md`.
2. Evaluación (`tests/trig_lin_test.cpp`): 4 funciones × 735 intervalos (centros en [−π, π],
   anchos de 0.01 a 2π) × 2 aritméticas × 3 modos: contención por muestreo, sobreestimación
   respecto del rango exacto, error de linealización, tiempo. Resultados en `results/05-fase2-trigonometria/fase2-*/`.

## Fase 3 — Evaluación experimental  ✅ (nivel 1 2026-09-21; nivel 2 etapas A–D 2026-09-22)

1. Nivel 1 (rangos): `tests/range_eval.cpp` evalúa objetivo y restricciones de cada instancia de
   `benchs/optim` con las seis variantes sobre la caja inicial y sub-cajas, sin resolver:
   anchura afín vs. rango muestreado (sobreestimación) y contención.
2. Nivel 2 (solver): barrido `ibexopt-raak` con las seis variantes (+ `xn`), `-t 1800`, sobre
   `easy`+`medium` primero y `hard`+`others` después, con `compo` y luego `art`. Estrategia de
   cómputo: 12 procesos en paralelo (16 hilos disponibles), instancias ordenadas por dificultad
   creciente para que los resultados parciales sean útiles, reanudable. Ver `FASE3_EXPERIMENTOS.md`.
3. Análisis: victorias/derrotas/empates y medias geométricas de celdas y tiempo, separando el
   efecto de la aritmética (`arith` con `k=0` frente a `af2 k=0`) del efecto del k-nomial
   (`k=3` frente a `k=0` dentro de cada aritmética).

## Fase 4 — Resultados  ✅ (nivel 1 y etapas A–D)

Gráficos (perfiles de desempeño, dispersión log-log de tiempos y celdas, calidad de sin/cos) y
tabla consolidada (`results/07-fase3-nivel2-solver/fase3-20260921/RESUMEN.md`, `resumen_medias_geom.png`), con
`README.md` en la carpeta de resultados que explica cada gráfico. Conclusiones en
`FASE3_EXPERIMENTOS.md`.

---

## Bitácora

- 2026-09-21: Fase 0 documentada; Fase 1 consolidada en el repo (parches 0004–0007, CLI, tests,
  scripts, resultados) y revalidada; Fase 2 implementada (parche 0008), validada (17 640
  evaluaciones sin violaciones; regresión 21/21 idéntica) y documentada; nivel 1 de la Fase 3
  ejecutado (380 instancias, 0 violaciones) y analizado; nivel 2 lanzado en WSL (cadena A→D,
  `-t 1800`, 12 procesos) con análisis probado sobre el parcial de la etapa A.
- 2026-09-22: etapas A, B y C del nivel 2 terminadas, analizadas y commiteadas; Fase 4
  (tabla consolidada, gráficos, README de resultados) hecha para ellas. Etapa D detenida a
  petición del usuario (reanudable) a la espera de su confirmación; reanudada con su confirmación
  y terminada el mismo día (12 corridas interrumpidas rehechas). **Plan completo**: las cuatro
  etapas analizadas, consolidación y conclusiones finales en `FASE3_EXPERIMENTOS.md`.
