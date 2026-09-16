// Evalua con la aritmetica afin de ibex-affine las formulaciones de x^T Q x que
// genera qplib/qplib_ibex_forms.py, en modo fAF2 (raak_k = 0) y RAA-K (raak_k = 3).
// Salida CSV por stdout: archivo, modo, radio (err de la forma afin), intervalo, ms,
// cuadrados y productos donde la cota RAA-K reemplazo a la de fAF2.
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_KNomial.h"

#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

using namespace ibex;

struct Term {
	char kind;
	double c;
	std::vector<int> idx;
	std::vector<double> coef;
};

int main(int argc, char** argv) {
	std::printf("file,mode,radius,lb,ub,ms,sqr_used,prod_used\n");
	for (int a = 1; a < argc; a++) {
		std::ifstream in(argv[a]);
		int n = 0;
		in >> n;
		IntervalVector box(n);
		for (int i = 0; i < n; i++) {
			double l, u;
			in >> l >> u;
			box[i] = Interval(l, u);
		}
		int T = 0;
		in >> T;
		std::vector<Term> terms(T);
		for (int t = 0; t < T; t++) {
			Term& tm = terms[t];
			in >> tm.kind >> tm.c;
			int m = (tm.kind == 'P') ? 2 : 1;
			if (tm.kind == 'S') in >> m;
			tm.idx.resize(m);
			tm.coef.assign(m, 1.0);
			for (int k = 0; k < m; k++) {
				in >> tm.idx[k];
				if (tm.kind == 'S') in >> tm.coef[k];
			}
		}
		if (!in) {
			std::fprintf(stderr, "error de lectura en %s\n", argv[a]);
			return 2;
		}
		const char* base = std::strrchr(argv[a], '/');
		base = base ? base + 1 : argv[a];

		Affine2Variables v(box);
		std::vector<Affine2> x;
		x.reserve(n);
		for (int i = 0; i < n; i++) x.push_back(Affine2(v[i]));

		const int modes[2] = {0, 3};
		for (int mi = 0; mi < 2; mi++) {
			knomial_max_k() = modes[mi];
			knomial_stats() = KNomialStats();
			std::chrono::steady_clock::time_point t0 = std::chrono::steady_clock::now();

			Affine2 f = x[0] * 0.0;
			for (size_t t = 0; t < terms.size(); t++) {
				const Term& tm = terms[t];
				if (tm.kind == 'P') {
					f = f + tm.c * (x[tm.idx[0]] * x[tm.idx[1]]);
				} else if (tm.kind == 'Q') {
					f = f + tm.c * sqr(x[tm.idx[0]]);
				} else {
					Affine2 lin = x[0] * 0.0;
					for (size_t k = 0; k < tm.idx.size(); k++) lin = lin + tm.coef[k] * x[tm.idx[k]];
					f = f + tm.c * sqr(lin);
				}
			}
			double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
			knomial_max_k() = 0;

			Interval I = f.itv();
			double rad = f.is_active() ? f.err() : NAN;
			std::printf("%s,%d,%.17g,%.17g,%.17g,%.3f,%ld,%ld\n", base, modes[mi], rad, I.lb(), I.ub(), ms,
			            knomial_stats().sqr_used, knomial_stats().calls_used);
		}
		std::fflush(stdout);
	}
	return 0;
}
