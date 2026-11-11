// [raak local] Comprobacion numerica del lema de conservatividad de la cota k-nomial.
// Para productos aleatorios de formas afines (coeficientes x, y de magnitudes mezcladas):
//   (a) corre knomial_rewrite (dobles) y obtiene bloques (c_b, u_b);
//   (b) calcula el residuo con intervalos [R] = [Q] - sum c [u][u]^T y la cota del lema 3,
//       [L,U] = sum c [0, s^2] + sum [R_ii][0,1] + sum 2[R_ij][-1,1], con s redondeado arriba;
//   (c) calcula la cota actual (knomial_quad_bound: shift, rad con disc) y el margen qmargin de fAF2;
//   (d) muestrea eps en [-1,1]^n (vertices y puntos interiores) y evalua f(eps) = eps^T Q eps con
//       intervalos (Q a partir de los dobles x, y, exacta en los reales), comprobando la contencion
//       en la cota del lema 3 y en la cota actual con y sin qmargin;
//   (e) compara anchuras y la discrepancia |R_tilde - (Q - sum c u u^T)| del lema 2.
// Uso: knomial_lemma_check [N=20000] [semilla=7]
#include "ibex.h"
#include "ibex_KNomial.h"
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <random>

using namespace ibex;
using std::vector;

int main(int argc, char** argv) {
	long N = argc > 1 ? atol(argv[1]) : 20000;
	unsigned seed = argc > 2 ? (unsigned) atol(argv[2]) : 7u;
	std::mt19937_64 rng(seed);
	std::uniform_real_distribution<double> U(-1.0, 1.0);
	std::uniform_int_distribution<int> Rn(2, 12), Rk(2, 6), Rmag(-8, 8), Rmode(0, 3);

	long viol_lema3 = 0, viol_actual = 0, viol_actual_margen = 0, pos_lema3 = 0, pos_actual = 0, pos_actual_margen = 0, productos_con_bloques = 0, bloques = 0;
	double max_disc_rel = 0.0, min_disc_rel = 1e300, sum_disc_rel = 0.0, max_lema2_rel = 0.0;
	double sum_ratio_w = 0.0; long n_ratio = 0;
	double min_ratio_w = 1e300, max_ratio_w = 0.0;
	const double EM = std::ldexp(1.0, -53);

	for (long it = 0; it < N; it++) {
		int n = Rn(rng), k = Rk(rng), mode = Rmode(rng);
		vector<double> x(n), y(n);
		for (int i = 0; i < n; i++) {
			double mx = (mode >= 2) ? std::ldexp(1.0, Rmag(rng)) : 1.0;   // magnitudes mezcladas 2^-8..2^8
			double my = (mode >= 2) ? std::ldexp(1.0, Rmag(rng)) : 1.0;
			x[i] = U(rng) * mx;
			y[i] = (mode % 2 == 1) ? std::copysign(std::fabs(U(rng)) * my, x[i]) : U(rng) * my;   // mismo signo: cliques grandes
			if (std::fabs(x[i]) < 0.05) x[i] = 0.0;
			if (std::fabs(y[i]) < 0.05) y[i] = 0.0;
		}
		// --- cota actual (dobles, con disc)
		double shift = 0.0, rad = 0.0;
		knomial_max_k() = k;
		int nb = knomial_quad_bound(x, y, n, k, shift, rad);
		double Sx = 0, Sy = 0;
		for (int i = 0; i < n; i++) { Sx += std::fabs(x[i]); Sy += std::fabs(y[i]); }
		double qmargin = EM * ((double) n * n + 4.0) * (std::fabs(shift) + rad + Sx * Sy);
		if (nb > 0) productos_con_bloques++;
		bloques += nb;

		// --- reescritura en dobles para obtener los bloques (misma secuencia que knomial_quad_bound)
		vector<double> Qd((size_t) n * n), w(n, 2.0);
		for (int i = 0; i < n; i++)
			for (int j = 0; j < n; j++) Qd[i * n + j] = 0.5 * (x[i] * y[j] + x[j] * y[i]);
		vector<double> Q0 = Qd;
		vector<KNomialBlock> blk;
		if (k >= 2) knomial_rewrite(Qd, w, n, k, blk);

		// --- lema 2: discrepancia entre el residuo incremental y Q - sum c u u^T (en dobles, relativa)
		double num = 0, den = 0;
		for (int i = 0; i < n; i++)
			for (int j = 0; j < n; j++) {
				double r = Q0[i * n + j];
				for (size_t b = 0; b < blk.size(); b++) r -= blk[b].c * blk[b].u[i] * blk[b].u[j];
				num = std::max(num, std::fabs(r - Qd[i * n + j]));
				den = std::max(den, std::fabs(Q0[i * n + j]));
			}
		if (den > 0) max_lema2_rel = std::max(max_lema2_rel, num / den);

		// --- lema 3: residuo con intervalos y cota [L,U]
		vector<Interval> R((size_t) n * n);
		for (int i = 0; i < n; i++)
			for (int j = 0; j < n; j++) {
				Interval q = 0.5 * (Interval(x[i]) * Interval(y[j]) + Interval(x[j]) * Interval(y[i]));
				for (size_t b = 0; b < blk.size(); b++)
					q -= Interval(blk[b].c) * Interval(blk[b].u[i]) * Interval(blk[b].u[j]);
				R[i * n + j] = q;
			}
		Interval LU(0.0);
		for (size_t b = 0; b < blk.size(); b++) {
			Interval s(0.0);
			for (int i = 0; i < n; i++) s += Interval(std::fabs(blk[b].u[i]));
			Interval s2 = Interval(0.0, s.ub()) * Interval(0.0, s.ub());   // [0, s_bar^2]
			LU += Interval(blk[b].c) * Interval(0.0, s2.ub());
		}
		for (int i = 0; i < n; i++) {
			LU += R[i * n + i] * Interval(0.0, 1.0);
			for (int j = i + 1; j < n; j++) LU += 2.0 * R[i * n + j] * Interval(-1.0, 1.0);
		}
		double mid3 = LU.mid(), rad3 = LU.rad();
		Interval cota3(mid3 - rad3, mid3 + rad3);   // en reales; aqui redondeado hacia fuera por Interval
		cota3 = Interval(mid3) - Interval(rad3) | Interval(mid3) + Interval(rad3);
		Interval cota_actual(shift - rad, shift + rad);
		cota_actual = (Interval(shift) - Interval(rad)) | (Interval(shift) + Interval(rad));
		Interval cota_actual_m = (Interval(shift) - Interval(rad) - Interval(qmargin)) | (Interval(shift) + Interval(rad) + Interval(qmargin));

		// --- muestreo de eps
		bool v3 = false, va = false, vam = false;          // violacion segura: f disjunto de la cota
		bool p3 = false, pa = false, pam = false;          // posible: f (intervalo de evaluacion) sobresale
		for (int sm = 0; sm < 64; sm++) {
			vector<double> e(n);
			for (int i = 0; i < n; i++) e[i] = (sm < 32) ? (U(rng) < 0 ? -1.0 : 1.0) : U(rng);
			Interval a(0.0), bb(0.0);
			for (int i = 0; i < n; i++) { a += Interval(x[i]) * Interval(e[i]); bb += Interval(y[i]) * Interval(e[i]); }
			Interval f = a * bb;   // contiene el valor real de f(eps)
			if (!cota3.is_superset(f)) p3 = true;
			if (!cota_actual.is_superset(f)) pa = true;
			if (!cota_actual_m.is_superset(f)) pam = true;
			if (!cota3.intersects(f)) v3 = true;
			if (!cota_actual.intersects(f)) {
				if (!va) {
					double exc = f.lb() > cota_actual.ub() ? f.lb() - cota_actual.ub() : cota_actual.lb() - f.ub();
					printf("VIOLACION SEGURA cota actual sin qmargin: producto %ld n=%d k=%d modo=%d bloques=%d f=[%.17g,%.17g] cota=[%.17g,%.17g] exceso=%.3e exceso/rad=%.3e qmargin=%.3e lema3=[%.17g,%.17g]\n",
					       it, n, k, mode, nb, f.lb(), f.ub(), cota_actual.lb(), cota_actual.ub(), exc, exc / rad, qmargin, cota3.lb(), cota3.ub());
					printf("  x="); for (int i = 0; i < n; i++) printf(" %.17g", x[i]);
					printf("\n  y="); for (int i = 0; i < n; i++) printf(" %.17g", y[i]);
					printf("\n  eps="); for (int i = 0; i < n; i++) printf(" %g", e[i]); printf("\n");
				}
				va = true;
			}
			if (!cota_actual_m.intersects(f)) vam = true;
		}
		if (v3) viol_lema3++;
		if (va) viol_actual++;
		if (vam) viol_actual_margen++;
		if (p3) pos_lema3++;
		if (pa) pos_actual++;
		if (pam) pos_actual_margen++;
		if (rad > 0) {
			double ratio = cota3.diam() / cota_actual_m.diam();
			sum_ratio_w += ratio; n_ratio++;
			min_ratio_w = std::min(min_ratio_w, ratio); max_ratio_w = std::max(max_ratio_w, ratio);
		}
		// disc relativo: rad actual menos la parte sin disc no es accesible; medimos (rad - rad3) / rad3
		if (rad3 > 0) { double q = (rad - rad3) / rad3; max_disc_rel = std::max(max_disc_rel, q); min_disc_rel = std::min(min_disc_rel, q); sum_disc_rel += q; }
	}
	printf("productos=%ld con_bloques=%ld bloques=%ld\n", N, productos_con_bloques, bloques);
	printf("violaciones SEGURAS (f(eps) evaluado con intervalos, disjunto de la cota): lema3=%ld actual_sin_qmargin=%ld actual_con_qmargin=%ld\n",
	       viol_lema3, viol_actual, viol_actual_margen);
	printf("posibles (el intervalo de evaluacion de f sobresale, puede ser su propio redondeo): lema3=%ld actual_sin_qmargin=%ld actual_con_qmargin=%ld\n",
	       pos_lema3, pos_actual, pos_actual_margen);
	printf("lema 2: max |R_tilde - (Q - sum c u u^T)| / max|Q| = %.3e\n", max_lema2_rel);
	printf("anchura lema3 / anchura actual con qmargin: media=%.6f min=%.6f max=%.6f (n=%ld)\n",
	       sum_ratio_w / n_ratio, min_ratio_w, max_ratio_w, n_ratio);
	printf("(rad_actual - rad_lema3)/rad_lema3: min=%.3e media=%.3e max=%.3e\n", min_disc_rel, sum_disc_rel / n_ratio, max_disc_rel);
	return 0;
}
