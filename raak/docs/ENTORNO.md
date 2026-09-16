# Entorno local de IBEX para experimentos con RAA-K

Actualizado: 2026-09-13. Vive en `~/ibex-local` dentro de WSL (Ubuntu 24.04).
Copia de referencia en la carpeta del proyecto (`AA/k-nomial/ENTORNO.md`).

## Sistema

| Componente | Versión |
|---|---|
| Windows | 11 Home Single Language, build 26200 |
| WSL | 2.7.8.0, kernel 6.18.33.1 |
| Distribución | Ubuntu 24.04.5 LTS (`Ubuntu-24.04`, distro predeterminada) |
| Compilador | GCC 13.3.0 |
| CMake | 3.28.3 |
| Recursos de la VM | 11 GiB RAM, 3 GiB swap, 12 hilos (sin `.wslconfig`: valores por defecto) |

## Código fijado

| Repositorio | Commit fijado | Rama local | Ruta |
|---|---|---|---|
| `rilianx/ibex-lib` (rama `pucv_practica`) | `5e51fffc` (2025-01-15) | `local` | `~/ibex-local/ibex-lib` |
| `ibex-team/ibex-affine` (rama `update_affine`) | `c219009c` (2026-09-04) | `raak` | `~/ibex-local/ibex-affine` |
| `ibexopt-raak` (proyecto propio) | — | — | `~/ibex-local/ibexopt-raak` |

Los commits están fijados a propósito: `update_affine` está en plena reescritura upstream
y así los experimentos no cambian bajo nuestros pies.

## Compilación

Todo se instala en `~/ibex-local/prefix`. Registros completos en `~/ibex-local/logs`.

| Paso | Configuración | Resultado |
|---|---|---|
| `ibex-lib` | `Release`, `-DLP_LIB=soplex`; intervalos **gaol 4.2.0** (valor por defecto, desde `3rd/`); LP **SoPlex 4.0.2** | 56 s con `-j8`; instalado, incluidas las cabeceras de `Optimizer04Config` |
| `ibex-affine` | `Release`, `-DIBEX_DIR=~/ibex-local/prefix` | 17 s; `make check`: **11 de 11 tests OK** (94 s); instalado |
| `ibexopt-raak` | `Release`, `-DCMAKE_PREFIX_PATH=~/ibex-local/prefix` | compila; opciones `--lr=xn|art|compo|raak|raakcompo` y `--raak_k=K` (por defecto 3) |

## Verificación

Instancia `benchs/optim/easy/ex5_4_3.bch` con los valores por defecto de `ibexopt04`
(filtrado `acidhc4`, bisección `lsmearmg`, estrategia `bs`, semilla 42). Una sola corrida por fila.

| `--lr` | Estado | f\* (intervalo final) | Celdas del B&B | CPU (s) |
|---|---|---|---|---|
| `xn` | optimization successful | [4845.45714313, 4845.46198858] | 60 | 0.17 |
| `art` | optimization successful | [4845.45714313, 4845.46198859] | 44 | 0.13 |
| `compo` | optimization successful | [4845.45715125, 4845.46199671] | 44 | 0.17 |

*Celdas* = `number of cells` del reporte de IBEX (nodos explorados). *CPU* = `cpu time used`.

## Scripts (`~/ibex-local/scripts`)

| Script | Fase | Qué hace |
|---|---|---|
| `wsl_clone.sh` | — | Clona (o repara) los repos y los fija en sus commits, en ramas locales |
| `wsl_build_ibexlib.sh` | F1 | Compila e instala el fork y corre el benchmark del tutorial |
| `wsl_build_affine.sh` | F2 | Compila `ibex-affine`, corre `make check` e instala |
| `wsl_build_cli.sh` | F3 | Arma y compila `ibexopt-raak` (con los `cli_*`) y prueba `xn`, `art`, `compo` |
| `wsl_baseline.sh` | F4 | Barrido `xn`/`art`/`compo` sobre `benchs/optim` → `~/ibex-local/results/baseline-<fecha>/results.csv` |
| `wsl_analyze.sh` | F4 | Tabla de estados y cocientes de celdas frente a `xn` de un barrido |
| `wsl_build_raak.sh` | F5 | De punta a punta: prueba dorada de knomial, ibex-lib, ibex-affine, prueba aritmética, CLI y corridas cortas |
| `wsl_raak_quick.sh` | F5 | Tras cambiar el prototipo: recompila ibex-affine y CLI, prueba aritmética y ablación de `raak_k` (`INSTS`, `VARIANTS`, `TLIM`) |
| `wsl_sweep_raak.sh` | F5 | Barrido `raak`/`raakcompo` con los parámetros de la línea base |
| `wsl_raak_v2.sh` | F5 | Recompila, prueba y, solo si las pruebas pasan, lanza `wsl_sweep_raak.sh` |
| `wsl_timing_raak.sh` | F5 | Sobrecosto de CPU en la misma sesión: corridas secuenciales `art`/`raak:0`/`raak:3` con orden rotado → `results/timing-<fecha>/timing.csv` |
| `wsl_qplib_eval.sh` | F5 | Compila `tests/qplib_affine_eval` y evalúa con fAF2 y RAA-K las formulaciones de QPLIB generadas por `qplib/qplib_ibex_forms.py` (variable `SP`) → `results/qplib-eval-<fecha>/eval.csv` |
| `wsl_save_raak_patches.sh` | F5 | Guarda los cambios de RAA-K como parches 0002/0003 y comprueba que se aplican sobre los commits fijados |

Pruebas del prototipo en `~/ibex-local/tests`: `knomial_golden` (C++ contra `knomial.py`, datos en
`knomial_golden.txt`) y `raak_arith_test` (contención, pendientes y radio frente a fAF2).

Reconstruir todo desde cero, dentro de Ubuntu:

```bash
cd ~/ibex-local/scripts
./wsl_clone.sh && ./wsl_build_ibexlib.sh && ./wsl_build_affine.sh && ./wsl_build_cli.sh
```

Barrido base (parámetros por variable de entorno; `ONLY` acepta nombres separados por coma):

```bash
SETS="easy medium" LRS="xn art compo" TLIM=60 P=4 ./wsl_baseline.sh
ONLY=ex5_4_3,wall TLIM=10 ./wsl_baseline.sh      # prueba corta
```

Desde PowerShell: `wsl -d Ubuntu-24.04 -- bash ~/ibex-local/scripts/<script>.sh`.
Evitar pasar comandos con comillas o `|` por PowerShell: `wsl` los reinterpreta.

## Parches locales (sin commit)

| # | Repo | Archivo | Qué corrige |
|---|---|---|---|
| 0001 | `ibex-affine` (rama `raak`) | `src/numeric/ibex_LinearizerAffine2.cpp` | Segfault de `--lr=art`/`compo` cuando una restricción queda con forma afín no activa (vacía o no acotada, p. ej. al dividir por un intervalo que contiene 0). La validación sólo miraba `noise_count()`, y `noise(i)` leía un vector nulo. Se agrega `af2.is_active() &&` en `goal_linearization`, `inlinearization` y `linearize`. Omitir una restricción mantiene válida la relajación. |

Guardado en `~/ibex-local/patches/0001-LinearizerAffine2-omitir-formas-no-activas.patch`.
Revertir: `git -C ~/ibex-local/ibex-affine checkout -- src/numeric/ibex_LinearizerAffine2.cpp`.

Verificación del parche (2026-09-13): 11/11 tests OK; `wall.bch` pasa de segfault a resuelta
(`art` 24 celdas, `compo` 12 celdas, mismo f\* que `xn`); en la prueba corta de 7 instancias × 3
relajaciones, las **19 corridas que ya funcionaban dan exactamente el mismo estado y número de
celdas** que antes del parche, y las 2 que fallaban ahora terminan. El bug ya existía en el
`master` de 2021 del plugin; no lo introdujo el refactor de `update_affine`.

### Prototipo RAA-K (F5, 2026-09-13)

| # | Repo | Archivos | Qué hace |
|---|---|---|---|
| 0002 | `ibex-affine` (rama `raak`) | `src/arithmetic/ibex_KNomial.h` (nuevo), `src/arithmetic/ibex_Affine2_fAF2.cpp`, `src/CMakeLists.txt` | Port C++11 de `knomial.py` y modo RAA-K en `AF_fAF2`, controlado por `ibex::knomial_max_k()` (por hilo; 0 = fAF2 original). **Productos** (`operator*=`): cota k-nomial, calculada solo si x e y comparten ≥ 2 símbolos de ruido (filtro exacto). **Cuadrados** (`Asqr`, con k ≥ 1): cota de Chebyshev de la RAA de [A], `[0, (Σ|aᵢ|+e)²]`. Con k = 1 la parte cuadrática es la de la RAA de [A]; con k ≥ 2 se agrega la reescritura k-nomial. En ambos casos la cota RAA-K solo reemplaza a la de fAF2 cuando es más ajustada que ella más su margen de redondeo; si no, el cálculo es bit a bit el de fAF2. Contadores en `ibex::knomial_stats()`. |
| 0003 | `ibex-lib` (rama `local`) | `src/optim/ibex_Optimizer04Config.cpp` | `get_ctc()` también envuelve `raak` y `raakcompo` en `CtcPolytopeHull`. |

Parches en `~/ibex-local/patches/` (0002 va sobre 0001). Revertir:
`git -C ~/ibex-local/ibex-affine checkout -- src/arithmetic/ibex_Affine2_fAF2.cpp src/CMakeLists.txt`
(y borrar `ibex_KNomial.h`); `git -C ~/ibex-local/ibex-lib checkout -- src/optim/ibex_Optimizer04Config.cpp`.

Verificación: prueba dorada 80 casos / 327 bloques idénticos a Python; prueba aritmética 3000
productos sin violaciones de contención ni radios mayores que fAF2; 11/11 tests; con `--raak_k=0`, o
cuando la cota no mejora, las corridas son idénticas a `art`/`compo`. v2 (filtro + cuadrados): 3000
productos y 3000 cuadrados sin violaciones ni radios mayores; filtro bit a bit exacto; en el barrido,
111 de 111 corridas sin uso en cuadrados idénticas a v1. Resultados en `REPORTE_IBEX_BASELINE.md` §10–§12.

## Pendientes conocidos

- Rigor de RAA-K: el margen de redondeo de la reescritura es heurístico; acotarlo formalmente.
- Fase de rigor (F6): compilar un segundo `ibex-lib` con `-DINTERVAL_LIB=filib`, porque el CI de
  `ibex-affine` prueba ambos backends de intervalos.
