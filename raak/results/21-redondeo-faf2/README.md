# 21 · Pendientes de la demostración: redondeo de fAF2 y literatura (11-11-2026)

Revisión de los cuatro pendientes que quedaban alrededor del lema de conservatividad, con los papers de
`k-nomial/referencias` (OneDrive, fuera del repositorio). Sin cambios en el código de la biblioteca.

## 1. `twoSum` de fAF2 bajo redondeo hacia arriba: hay un hueco, diminuto

**Hecho.** fAF2 calcula el error de redondeo de cada suma con `twoSum` (2Sum de Knuth) y suma `2(1+2εₘ)|t|` al
término de error. Eso es exacto con redondeo al más cercano. Pero Gaol deja el procesador en redondeo hacia +∞
en todo programa de IBEX, y en ese modo el error de una suma no siempre es representable.

**Literatura.** Boldo, Graillat y Muller (2017), Teorema 4.1: con cualquier función de redondeo y sin desbordamiento,
2Sum devuelve `t = (a+b) − s + α` con `|α| < 2^(−p+1)·ulp(a+b)`; `t` es un redondeo fiel del error solo si los
exponentes de `s` y `b` difieren en a lo más `p−1`. Es decir, el error real puede exceder a `|t|` en hasta
`2^-52·ulp(s)`, que es menos de `2^-104·|s|`.

**Comprobación** (`tests/faf2_twosum_probe.cpp`, `tests/faf2_suma_constante_probe.cpp`, salida en `salida_sondas.txt`):
- `a = 1`, `b = −1e-40`: `s = 1`, `t = 0`. El error real es `b`, no cero.
- Con `b` negativo y `|b| < 2^-106·|a|`, `twoSum` devuelve 0 en el 54 % de un millón de casos.
- Cómo leer `salida_sondas.txt`: la etiqueta "t exacto" de las tres primeras líneas no es fiable (compara contra un
  encierro del error de un ulp de ancho); el dato es el valor de `t`. Las filas "al más cercano" tampoco prueban ese
  modo: la biblioteca vuelve a fijar el redondeo hacia arriba en cada operación de intervalos, por eso salen iguales.
- En la forma afín: `x + (−1e-40)` con `x ∈ [1, 2]` da centro 1,5, coeficiente 0,5 y **error 0**; la forma
  encierra `[1, 2]`, que no contiene `1 − 1e-40`. Con `b = −1e-17` o `−1e-10` el error sí queda cubierto.

**Alcance.** La violación es de a lo más `2^-104` relativo al centro, y solo cuando se suma un término más de
`2^105` veces menor y de signo negativo. No afecta a ningún resultado medido (los tests de contención con 3,6
millones de formas no la detectan). Pero formalmente fAF2, tal como corre en IBEX, no es riguroso en ese caso,
y nuestra proposición hereda su tratamiento del centro y de los coeficientes lineales.

**No es de nuestros parches.** Está en `operator+=(double)` y en las demás sumas del fAF2 original (17 usos de
`twoSum` y 10 de `twoProd` en `ibex_Affine2_fAF2.cpp`). La cota k-nomial (parches 0012 y 0013) no usa `twoSum`.

**Arreglo propuesto (no aplicado).** Sumar la cota de α al error: en cada uso,
`ttt = (1+2εₘ)·(ttt + |eee| + εₘ²·|s|)`, ya que `2^-52·ulp(s) ≤ 2^-104·|s| < εₘ²·|s|` con `εₘ = 2^-51`.
Costo: un producto y una suma por operación. Sería el parche 0015; conviene decidirlo con el profesor y, si
procede, avisar al equipo de IBEX.

**`twoProd`.** En esta máquina usa FMA (`ibex_fma_runtime() = 1`): `fma(x, y, −r)` devuelve el error exacto del
producto con cualquier modo de redondeo, salvo subdesbordamiento. La variante sin FMA (Dekker) no se revisó.

## 2. Origen de fAF2 y su redondeo

Vu, Sam-Haroud y Faltings (2009), apéndice A: la forma afín revisada acumula el redondeo en el término de error
con las ecuaciones (55a)–(55c): cada coeficiente se calcula redondeado con una cota `eᵢ` de su error, y
`e_z = ⌈|α|eₓ + |β|e_y + Σ eᵢ⌉` redondeado hacia arriba. El Teorema 10 lo declara "obvio" y omite la demostración.
El esquema publicado supone que cada `eᵢ` **encierra** el error; la implementación de IBEX obtiene `eᵢ` con
`twoSum`, y ahí está la diferencia del punto 1.

## 3. Composición

Para la frase de que la forma afín de una expresión completa encierra a la función: Messine (2002), Teorema 4
(p. 1006 de la revista), y para la versión fiable Ninin, Messine y Hansen (2015), Proposición 5 (AF2) y sección 4
(rAF1 y rAF2).

## 4. Relación con la forma cuadrática general

Messine y Touhami (2006) conservan `εᵀAε` de forma explícita en cada operación (ecuación 3.1), pero al convertir
a intervalo la acotan **monomio a monomio**: `Σ_{i≠j} [−|aᵢⱼ|, |aᵢⱼ|] + Σ aᵢᵢ[0,1]` (su Proposición 4.2:
`GQF(X) = QNE_g([−1,1]ⁿ)`). Es exactamente la cota de nuestro lema con cero bloques.
Consecuencia para el paper: el k-nomial no compite con la forma cuadrática general, la complementa. Ataca el paso
de acotar `εᵀQε`, que ellos hacen término a término; se puede aplicar a un producto de formas afines (lo que
hacemos) o a la conversión final de una forma cuadrática general. Costo: ellos guardan n² coeficientes por forma;
nosotros mantenemos formas lineales y pagamos la búsqueda solo en los productos.
