# RAA-K en IBEX: prototipo y experimentos

Integración de **RAA-K** (reducción k-nomial por presupuesto diagonal, generalización del método
binomial de [B] a bloques de hasta k variables) en la aritmética afín de IBEX, más los experimentos
que la evalúan.

Trabajo local sobre dos repos fijados a un commit:

| Repo | Commit | Para qué |
|---|---|---|
| `rilianx/ibex-lib`, rama `pucv_practica` | `5e51fffc` | Optimizador `ibexopt04` y su opción `--lr` |
| `ibex-team/ibex-affine`, rama `update_affine` | `c219009c` | Aritmética afín (`AF_fAF2`) y relajaciones `art` / `compo` |

**Estado:** prototipo de investigación. La aritmética no es rigurosa: el margen de redondeo de la
reescritura es heurístico (falta la fase F6).

## Resultados en una línea

- **Implementación validada:** el port en C++ reproduce bit a bit la implementación de referencia en
  Python (`knomial.py`), y en 58 instancias QPLIB coincide con su métrica `af2_error` con diferencia
  relativa ≤ 1e-11.
- **Aislamiento:** donde RAA-K no mejora la cota, los resultados son **bit a bit** los de fAF2.
- **En el B&B** (133 instancias `easy` + `medium`, límite 60 s): la reescritura k-nomial reduce las
  celdas en las 11 instancias donde extrae bloques sin perder en ninguna, combinada con `compo`
  (media geométrica 0.88). Con `art` sola, empeora (1.09).
- **Ojo con la atribución:** las dos mejoras más grandes (`ex8_4_4bis`, ~10× menos nodos; `bearing`,
  −41%) vienen de la parte cuadrática de la **RAA de [A]** (cuadrados de Chebyshev), no del k-nomial.

Todo el detalle, con tablas y controles, está en [`docs/REPORTE_IBEX_BASELINE.md`](docs/REPORTE_IBEX_BASELINE.md)
(§1–§14). Un resumen corto en [`docs/RESUMEN_IBEX.md`](docs/RESUMEN_IBEX.md).

## Qué hay aquí

| Carpeta | Contenido |
|---|---|
| `docs/` | Reporte completo, resumen y `ENTORNO.md` (versiones, comandos y cómo reconstruir todo) |
| `patches/` | `0001` corrige un segfault de `LinearizerAffine2`; `0002` es el prototipo RAA-K en ibex-affine; `0003` es el cambio de 2 líneas en este repo |
| `affine/ibex_KNomial.h` | El método: reescritura k-nomial y cota de la parte cuadrática (copia legible; se instala vía el parche `0002`) |
| `cli/` | `ibexopt-raak`: subclase de `Optimizer04Config` que habilita `--lr=art\|compo\|raak\|raakcompo` y el flag `--raak_k` |
| `scripts/` | Clonado, compilación, barridos, medición de tiempos y guardado de parches (pensados para WSL/Ubuntu) |
| `tests/` | Prueba dorada contra Python, prueba aritmética (contención, pendientes, radio) y el evaluador de QPLIB |
| `results/` | CSV de cada barrido, con su `meta.txt`. Los logs por corrida no se incluyen por tamaño |

## El cambio en este repo

Una sola modificación, de 2 líneas, en `src/optim/ibex_Optimizer04Config.cpp`: `get_ctc()` ahora
envuelve también `raak` y `raakcompo` en `CtcPolytopeHull`, igual que hace con `xn`, `art` y `compo`.
Sin eso, las relajaciones nuevas se construyen pero no se usan.

## Cómo reproducir

Requiere Ubuntu (probado en WSL, Ubuntu 24.04, GCC 13.3, CMake 3.28).

```bash
mkdir -p ~/ibex-local && cp -r raak/scripts ~/ibex-local/scripts
cd ~/ibex-local/scripts
./wsl_clone.sh              # clona y fija ibex-lib e ibex-affine
# aplicar los parches 0001 y 0002 sobre ibex-affine, y 0003 sobre ibex-lib
./wsl_build_ibexlib.sh && ./wsl_build_affine.sh && ./wsl_build_cli.sh
```

Uso del binario:

```bash
ibexopt-raak --lr=raakcompo --raak_k=3 -t 60 benchs/optim/medium/ex8_4_4bis.bch
```

`--raak_k`: `0` = fAF2 original · `1` = parte cuadrática de la RAA de [A] · `≥2` = RAA-K.

Barridos y análisis: ver `docs/ENTORNO.md`, sección *Scripts*.

## Modos de la aritmética

| `--raak_k` | Productos | Cuadrados de formas compuestas |
|---|---|---|
| 0 | fAF2 (Vu, Sam-Haroud y Faltings 2004) | fAF2 |
| 1 | RAA de [A]: `Q` simetrizada, término a término | RAA de [A]: Chebyshev, rango exacto |
| ≥2 | Lo anterior + reescritura k-nomial (RAA-K) | Igual que k=1 |

En todos los modos, los errores de los factores se propagan como en fAF2: **falta portar el corner
test de [A]** (Ec. 16).

## Pendientes

- Rigor: acotar formalmente el redondeo de la reescritura (fase F6).
- Portar el corner test de [A] para tener su aritmética completa.
- Reescribir los objetivos QP de `benchs/optim` (familia `ex2_1_*`) como residuo + `Σ c·sqr(uᵀx)`:
  RAA-K solo actúa si el modelo llega ya reescrito (ver §13 del reporte).

## Licencia y créditos

El código de este directorio se deriva de IBEX (`ibex-lib`, LGPL) y del plugin `ibex-affine`
(GPL-3.0, Jordan Ninin), y se distribuye bajo las mismas licencias que el código del que deriva.
`cli/cli_ibexopt_raak.cpp` es una copia adaptada de `src/bin/ibexopt_config04.cpp` de este fork
(Ignacio Araya, Gilles Chabert).

**Papers:** [A] *Extending Affine Arithmetic with Bilinear Operators and non-parallel Envelopes*;
[B] *Greedy Bilinear Reduction via Diagonal Budgeting for Improved Affine Arithmetic Bounds*
(Araya, Madariaga, Geraldo-Ulloa, Ponce-Fernández). RAA-K generaliza [B] a bloques k-nomiales y es
trabajo nuevo, sin resultados publicados con los que compararse.
