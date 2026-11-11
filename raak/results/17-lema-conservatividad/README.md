# Lema de conservatividad de la cota k-nomial: comprobación numérica (08-11-2026)

Documento: "Lema: la cota k-nomial es conservativa" (Claude Docs, 05-11 y 08-11-2026), con la versión para el paper y una
guía de estudio aparte. Punto 3 del to-do de fin de octubre ("lo que sobra con coeficientes en intervalos; el error se lleva
al residuo").

Qué se comprueba (`tests/knomial_lemma_check.cpp`, compilado contra la biblioteca con el parche 0011):
- Lema 3: con los bloques (c_b, u_b) que devuelve `knomial_rewrite` en dobles, el residuo con intervalos
  [R] = [Q] − Σ c_b [u_b][u_b]ᵀ y la cota [L,U] = Σ c_b [0, s̄_b²] + Σ [R_ii][0,1] + Σ 2[R_ij][−1,1] contienen la parte
  cuadrática del producto para todo ε.
- La cota actual de `knomial_quad_bound` (dobles, con `disc`) con y sin el margen `qmargin` del producto de fAF2.
- Lema 2: discrepancia entre el residuo incremental y Q − Σ c u uᵀ.

Protocolo: 8 semillas × 20 000 productos, n = 2..12, k = 2..6, cuatro regímenes (uniforme; mismo signo en los dos factores;
magnitudes 2⁻⁸..2⁸; ambos); 64 puntos ε por producto (32 vértices, 32 interiores), f(ε) evaluado con intervalos. Violación
segura = el intervalo de f es disjunto de la cota; posible = solo sobresale (redondeo del propio f en los vértices).

Resultado (`lemma_check_stdout.txt`):

| cota | violaciones seguras (160 000) | posibles por semilla | anchura / actual con qmargin |
|---|---|---|---|
| lema 3 (intervalos) | 0 | 154–178 | 1.000000 (desvíos ≤ 1.1e-15) |
| actual sin qmargin | 3 (n=2, 0 bloques, exceso de 1 ulp) | 548–568 | |
| actual con qmargin | 0 | 0 | 1 |

Discrepancia del lema 2: ≤ 6.3e-16 relativa a max|Q|.

Conclusión: la cota con coeficientes intervalares en el residuo es rigurosa, no cuesta anchura y permite quitar `disc` y
`qmargin` (parche 0012, pendiente). La cota actual depende de `qmargin` para la contención en punto flotante.
