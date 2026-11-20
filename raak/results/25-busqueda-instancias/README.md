# 25 · Búsqueda de instancias reales con material para el k-nomial

16 y 20 de noviembre de 2026. Pregunta: ¿hay, en las bibliotecas públicas, modelos con productos de dos
formas afines que compartan varias variables de la misma clase de signo, fuera de los que ya conocíamos?

## Método

`analysis/escaneo_gams.py` recorre los árboles de expresión de modelos GAMS escalares. Para cada producto de
dos formas afines `a(x)·b(x)` cuenta las variables compartidas por clase de signo (`a_v b_v > 0` y
`a_v b_v < 0`); hay material cuando una clase tiene al menos dos variables. Distingue:

- **genuino**: los dos factores son formas distintas;
- **cuadrado**: los dos factores son la misma forma (`(a)*(a)`), es decir, un cuadrado escrito como producto;
- **fun**: forma afín por `f(forma afín)` (por ejemplo `log`), con las mismas clases respecto del argumento;
- **levantado**: `z1*z2` con `z1`, `z2` definidas cada una por una igualdad lineal; el material solo aparece
  si se eliminan esas variables;
- **cadenas**: productos de tres o más formas afines con al menos dos variables comunes.

Es un escaneo sintáctico: no ve los productos en que un factor no lineal se vuelve forma afín durante la
evaluación. Para eso sirve el filtro dinámico de `11-filtro-instancias` y `14-filtro-resto`.

Fuentes: `minlplib_gms.zip` de minlplib.org (versión del 2025-08-07) y las versiones GAMS de las tres
bibliotecas COCONUT (arnold-neumaier.at/glopt/coconut/Benchmark). Los modelos no están en el repositorio.

## Resultado

| Biblioteca | Modelos escaneados | Con material | Genuino | Solo cuadrados | fun | Levantado |
|---|---|---|---|---|---|---|
| MINLPLib | 1569 de 1633 | 32 | 3 | 29 | 10 | 3 |
| COCONUT 1 (GLOBALLib) | 241 | 0 | 0 | 0 | 10 | 4 |
| COCONUT 2 (CUTE) | 545 | 12 | 0 | 12 | 0 | 0 |
| COCONUT 3 (CSP) | 332 | 0 | 0 | 0 | 0 | 2 |

Quedaron fuera 64 modelos de MINLPLib de más de 3 MB. En COCONUT 1 hay 11 modelos con ecuaciones que el
escáner no pudo leer (no están en formato escalar); esa biblioteca está contenida en MINLPLib. Tablas por
instancia en `escaneo/`.

- **Genuino (3):** `st_e25` (programa multiplicativo lineal de Thoai 1991, 4 variables, una clase de 4);
  `johnall` (gestión de activos: 380 cadenas de 12 factores sobre las mismas 3 variables; 4 continuas y 190
  binarias) y `saa_2` (misma aplicación: 2000 cadenas de 12 factores sobre 5 variables; 4407 variables, 400
  binarias).
- **Solo cuadrados (41):** entre ellos `3pk` y `mistake`, que están en nuestro conjunto de benchmarks
  (`instancias/reales/3pk-borne.bch` y `benchs/UBinvar/mistake.bch` tienen los cuadrados escritos como
  `(a)*(a)`), además de `grouping`, `tointqor`, `spectra2` y las familias `kall_*` y `obstcl*`.
- **fun (10):** las `ex6_2_*`, ya conocidas.
- **Levantado:** `ex9_2_*` (binivel), `combustion`, `comb3000`, con clases de 2 variables.

## Instancias convertidas

`analysis/gams2minibex.py` convierte un modelo GAMS escalar a Minibex. En `instancias/`:

| Archivo | Qué es | Corrida con `ibexopt-raak` (k=0 y k=6) |
|---|---|---|
| `st_e25.bch` | `st_e25`; las cotas superiores se agregaron a partir de la primera restricción y `x >= 0` | 2 celdas en ambos casos; óptimo 0.890193 (MINLPLib: 0.89019359). Bloques en 6 de 6 productos; radio cuadrático frente a fAF2 1.000 → 0.759 |
| `johnall_obj.bch` | objetivo de `johnall` con la restricción de presupuesto; sin las 190 restricciones por escenario ni sus binarias (es otro problema) | 2 celdas en ambos casos; óptimo −224.7302, igual al mejor valor conocido del modelo original. Bloques en 12 540 de 12 540 productos; radio 0.892 → 0.715 |

La relajación continua de `johnall` (binarias en [0, 1], 194 variables) no devolvió nada en 200 s con un
límite de 60 s; no se investigó. `saa_2` no se convirtió.

## Lectura

La estructura que aprovecha el k-nomial casi no aparece en estas bibliotecas, y donde aparece con datos
reales los problemas se resuelven en el nodo raíz: la reescritura actúa, pero no hay árbol que reducir. La
clase de `synq` (suma de productos de formas afines con restricciones lineales) corresponde a los programas
multiplicativos lineales generalizados (Konno y Kuno 1992; Ryoo y Sahinidis 2003), cuyos bancos de prueba
son ejemplos pequeños e instancias aleatorias.
