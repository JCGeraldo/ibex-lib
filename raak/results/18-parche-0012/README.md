# Parche 0012: cota k-nomial rigurosa, residuo con coeficientes intervalares (08-11-2026)

Implementación de la capa 2 del lema de conservatividad (carpeta `17-lema-conservatividad/`, Claude Docs "Lema: la cota
k-nomial es conservativa"). Informe: "Informe RAA-K 5: parche 0012, cota k-nomial rigurosa" (Claude Docs, 08-11-2026).

Parche `patches/0012-ibex-affine-cota-rigurosa-intervalos.patch`: `knomial_quad_bound` forma el residuo al final con
`ibex::Interval`, [R_ij] = ½([x_i][y_j] + [x_j][y_i]) − Σ c_b [u_bi][u_bj], y la cota [L,U] = Σ c_b [0, s̄_b²] + Σ [R_ii][0,1] +
Σ 2[R_ij][−1,1]; shift = mid, rad = rad. Desaparecen `disc` (header) y `qmargin` (productos de fAF2 y AF_fAFFullI).
Los bloques no cambian. Hash de `knomial_diff_dump`: 13f8bd6372dd083f (era 4e35cac9e4b800a4).

Verificación (binarios 0011 y 0012 en la misma sesión; los 0011 se conservan como `*-0011`):
- `lemma_check_0012_stdout.txt`: 160 000 productos, 0 violaciones seguras sin ningún margen (con 0011 sin qmargin había 3);
  la cota de la biblioteca coincide exactamente con la referencia del lema calculada por el test.
- `nivel1/`: `range_eval` sobre synq, reales, synl y synt (48 420 filas): anchura afín idéntica a 10 dígitos en todas, 0
  violaciones en ambos; µs por evaluación 0012/0011 = 1.10 en las variantes que pasan por `knomial_quad_bound`
  (RAA con todo k, AF2/AA con k ≥ 2) y 1.01 en af2_k0 y aa_k0. Guion `analysis/parche0012_nivel1.py`.
- `nivel2/`: seis instancias (4 synq, ex6_2_10, synl_n08_d90_s1) con k = 0, 4, 6 (`resumen_nivel2.md`, logs recortados):
  f* idéntico en 9 corridas (ex6_2_10, synq n=5, synl) y en las 9 de synq n=8 los intervalos f* difieren a partir del
  sexto dígito y se solapan (misma precisión pedida, árbol distinto); celdas iguales en ex6_2_10 y synq n=5, distintas en
  n=8 y synl porque la cota cambia en el último dígito y el árbol se bifurca distinto (de 610 frente a 926 a 12294 frente a
  11188); CPU 0012/0011 media geom. 1.03 (k=0), 1.01 (k=4), 0.98 (k=6).

Conclusión: la cota es rigurosa sin margen heurístico, igual de ancha, 10 % más cara por evaluación y sin efecto
sistemático en el solver. Los 11 tests de ibex-affine pasan; la cadena 0001..0012 aplica limpia sobre c219009c.

## Dos implementaciones: intervalos frente a redondeo dirigido (`modos/`, parche 0013)

`patches/0013-ibex-affine-cota-redondeo-dirigido.patch` añade `RAAK_BOUND_MODE=interval|directed` (por defecto interval).
El modo directed calcula la misma cota con dobles en FE_UPWARD y el truco −up(−expr) para los extremos inferiores. Con Gaol
el procesador ya está permanentemente en FE_UPWARD (1/3 → 0.33333333333333337), así que fijarlo es un no-op.

- `lemma_check_directed_stdout.txt`: 160 000 productos, 0 violaciones; radio igual o mayor que el modo interval en ≤ 2.2e-16
  relativo (media 5e-18); hash de `knomial_diff_dump` 87e9221dac5eceb6 (interval 13f8bd6372dd083f).
- `nivel1_*`: tres binarios a la vez (0011, interval, directed) sobre 48 420 filas: anchuras idénticas a 10 dígitos; µs por
  evaluación directed/interval 0.91–0.94 en las variantes con k-nomial, directed/0011 1.00–1.03, interval/0011 1.07–1.13.
- `resumen_nivel2_modos.md`: 4 instancias × k = 4, 6, ambos modos a la vez: CPU directed/interval media geom. 0.967; celdas
  iguales o movidas por bifurcación; f* iguales salvo donde cambia el árbol (intervalos solapados).

Recomendación: interval por defecto (se lee del lema 3 sin supuestos sobre el modo de redondeo); directed disponible si el
8–10 % importa.
