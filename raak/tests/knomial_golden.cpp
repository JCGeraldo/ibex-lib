// Prueba "dorada" del port C++ de knomial: para cada caso generado por
// raa_lib/knomial.py (Q, w, max_k -> bloques y Q_res), verifica que
// ibex::knomial_rewrite produzca los mismos bloques y la misma Q_res.
#include "ibex_KNomial.h"

#include <cmath>
#include <cstdio>
#include <fstream>
#include <vector>

int main(int argc, char** argv) {
	if (argc < 2) {
		std::printf("uso: %s knomial_golden.txt\n", argv[0]);
		return 2;
	}
	std::ifstream in(argv[1]);
	if (!in) {
		std::printf("no se pudo abrir %s\n", argv[1]);
		return 2;
	}
	int ncases;
	in >> ncases;
	int fails = 0, mismatch_nb = 0, infeasible_total = 0;
	long blocks_total = 0;
	double worst = 0.0;
	for (int t = 0; t < ncases; t++) {
		int n, k;
		in >> n >> k;
		std::vector<double> w(n), Q(n * n);
		for (int i = 0; i < n; i++) in >> w[i];
		for (int i = 0; i < n * n; i++) in >> Q[i];
		int nb;
		in >> nb;
		std::vector<ibex::KNomialBlock> expected(nb);
		for (int b = 0; b < nb; b++) {
			in >> expected[b].c;
			expected[b].u.resize(n);
			for (int i = 0; i < n; i++) in >> expected[b].u[i];
		}
		std::vector<double> Qres_expected(n * n);
		for (int i = 0; i < n * n; i++) in >> Qres_expected[i];
		if (!in) {
			std::printf("error de lectura en el caso %d\n", t);
			return 2;
		}

		std::vector<ibex::KNomialBlock> got;
		std::vector<double> Qgot(Q);
		infeasible_total += ibex::knomial_rewrite(Qgot, w, n, k, got);

		if ((int) got.size() != nb) {
			mismatch_nb++;
			fails++;
			std::printf("  caso %2d (n=%d, k=%d): %d bloques, esperados %d\n", t, n, k, (int) got.size(), nb);
			continue;
		}
		double diff = 0.0;
		for (int b = 0; b < nb; b++) {
			diff = std::max(diff, std::fabs(got[b].c - expected[b].c));
			for (int i = 0; i < n; i++) diff = std::max(diff, std::fabs(got[b].u[i] - expected[b].u[i]));
		}
		for (int i = 0; i < n * n; i++) diff = std::max(diff, std::fabs(Qgot[i] - Qres_expected[i]));
		blocks_total += nb;
		worst = std::max(worst, diff);
		if (diff > 1e-12) {
			fails++;
			std::printf("  caso %2d (n=%d, k=%d): diferencia maxima %.3e\n", t, n, k, diff);
		}
	}
	std::printf("casos: %d | bloques comparados: %ld | casos con distinto numero de bloques: %d\n",
	            ncases, blocks_total, mismatch_nb);
	std::printf("diferencia maxima (bloques y Q_res): %.3e | cliques degradados: %d\n", worst, infeasible_total);
	std::printf("%s\n", fails == 0 ? "PORT OK: reproduce knomial.py" : "PORT CON DIFERENCIAS");
	return fails == 0 ? 0 : 1;
}
