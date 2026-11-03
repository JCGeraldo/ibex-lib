// Volcado determinista de knomial_quad_bound sobre 20000 productos aleatorios (n 1-14, k 2-4). Se compila
// contra dos versiones de ibex_KNomial.h y se comparan las salidas (parche 0009: hash 4e35cac9e4b800a4).
// volcado determinista de knomial_rewrite y knomial_quad_bound sobre casos aleatorios (para diff entre versiones)
#include "ibex_KNomial.h"
#include <cstdio>
#include <cstdlib>
#include <random>
#include <cstring>
int main() {
	std::mt19937_64 g(20261029);
	std::uniform_real_distribution<double> U(-1.0, 1.0);
	std::uniform_int_distribution<int> Dn(1, 14);
	unsigned long long h = 1469598103934665603ULL; long nb = 0, calls = 0;
	for (int t = 0; t < 20000; t++) {
		int n = Dn(g), k = 2 + (t % 3);
		std::vector<double> x(n), y(n);
		double dens = (t % 5) / 4.0;
		for (int i = 0; i < n; i++) { x[i] = (U(g) + 1 > 2 * dens) ? U(g) : 0.0; y[i] = (U(g) + 1 > 2 * dens) ? U(g) : 0.0; }
		if (t % 7 == 0) for (int i = 0; i < n; i++) y[i] = x[i] * (t % 2 ? 1 : -1);  // cuadrados
		double sh, rd; int b = ibex::knomial_quad_bound(x, y, n, k, sh, rd);
		nb += b; calls++;
		unsigned long long a, c; memcpy(&a, &sh, 8); memcpy(&c, &rd, 8);
		h = (h ^ a) * 1099511628211ULL; h = (h ^ c) * 1099511628211ULL; h = (h ^ (unsigned) b) * 1099511628211ULL;
		if (t % 997 == 0) std::printf("%d n=%d k=%d b=%d shift=%.17g rad=%.17g\n", t, n, k, b, sh, rd);
	}
	std::printf("hash=%llx bloques=%ld llamadas=%ld\n", h, nb, calls);
	return 0;
}
