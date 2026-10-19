# Experimentos y resultados

Todo lo que se corrió, en una sola carpeta, separado del código. Cada subcarpeta es un tipo de
experimento; dentro, cada barrido conserva su carpeta con fecha y su `meta.txt` (binario, commit,
parches, parámetros, hora de inicio y fin). Los logs por corrida no se incluyen por tamaño; quedan
en WSL (`~/ibex-local/results/`).

| carpeta | qué contiene | de dónde sale |
|---|---|---|
| `01-linea-base/` | El solver sin modificaciones: 133 instancias de `easy`+`medium` × `xn`, `art`, `compo`, 60 s. Es la referencia para ordenar instancias por dificultad. | `scripts/wsl_baseline.sh` |
| `02-prototipo-raak/` | Las primeras pruebas del k-nomial en el B&B (13 a 15 de septiembre): prototipo v1 (solo productos), v2 (+ cuadrados de Chebyshev), ablación k=1 frente a k=3, y la medición de sobrecosto de CPU con repeticiones. | `scripts/wsl_sweep_raak.sh`, `wsl_timing_raak.sh` |
| `03-qplib/` | El k-nomial sobre formas cuadráticas completas: 58 instancias QPLIB × 4 formulaciones, evaluadas con fAF2 y con RAA-K k=3. | `tests/qplib_affine_eval.cpp`, `scripts/wsl_qplib_eval.sh` |
| `04-fase1-validacion/` | Referencias bit a bit (`fase1-ref/`) y los pasos de aceptación de la Fase 1 (`fase1-20260916/paso11..15`): regresión del refactor, corner test, k-nomial en AA, linearizador, reproducción de QPLIB. | `scripts/wsl_fase1_*.sh`, `tests/*_test.cpp` |
| `05-fase2-trigonometria/` | Seno y coseno: 17 640 evaluaciones (4 funciones × 735 intervalos × 2 aritméticas × 3 modos), regresión sin trigonométricas e instancias con `sin`/`cos` en el solver. | `tests/trig_lin_test.cpp`, `scripts/wsl_fase2_paso21.sh`, `analysis/analyze_trig.py` |
| `06-fase3-nivel1-rangos/` | Nivel 1 de la Fase 3: sobreestimación de las seis variantes sobre 380 instancias sin resolver (`range.csv.gz`, 124 674 evaluaciones) y su análisis. | `tests/range_eval.cpp`, `scripts/wsl_fase3_nivel1.sh`, `analysis/analyze_range.py` |
| `07-fase3-nivel2-solver/` | Nivel 2 de la Fase 3: el solver con las seis variantes (+ `xn`), 1800 s por corrida. `fase3-20260921/` tiene las etapas A–D (easy+medium y hard+others × compo y art), `RESUMEN.md` y `README.md`; `fase3-k2-20261005/` es la corrida adicional de RAA k=2 con `art` (5 de octubre). | `scripts/wsl_fase3_sweep.sh`, `wsl_fase3_launch.sh`, `wsl_fase3_k2_launch.sh`, `analysis/analyze_sweep.py`, `consolidate.py` |
| `08-graficos/` | Un gráfico por experimento (18 PNG) con su `README.md`, generados a partir de los CSV de esta carpeta. | `analysis/graficos_resultados.py` |
| `09-informes/` | Los dos informes para el profesor guía (Word y PDF): el completo del 30 de septiembre y el corto del 5 de octubre (`art` frente a RAA k=0..3, nodos y CPU por instancia), con su tabla por instancia en CSV, `resumen.json` y figuras. | `analysis/art_vs_raa.py`, `analysis/informes/*.js` |

Orden de lectura sugerido: `09-informes/` para el resumen, `07-fase3-nivel2-solver/fase3-20260921/RESUMEN.md`
para la tabla consolidada, y `docs/FASE3_EXPERIMENTOS.md` para el diseño y las lecturas.

Regenerar: `python analysis/graficos_resultados.py` (gráficos), `python analysis/art_vs_raa.py` seguido de
`node analysis/informes/informe_corto.js` (informe corto), `node analysis/informes/informe.js` (informe completo).
Los `.js` necesitan el paquete `docx` de npm (ver `analysis/informes/README.md`).
