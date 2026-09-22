// Prueba de validez de la relajacion lineal de formas Affine3 (Fase 1, parche 0007).
//
// 200 polinomios aleatorios de grado 2-3 en 2-4 variables (API simbolica de Function), cada uno sobre
// una caja aleatoria. Se evalua con Affine3Eval (AA, k=0 y k=3) y con Affine2Eval (AF2, control) y se
// comprueba, en 1000 puntos muestreados de la caja, que la relajacion que usa LinearizerAffineT
//     mid(af) + sum_{i<n} noise(i) (x_i - mid_i)/rad_i  +-  (err(af) + extra)
// contiene f(x), con extra = affine_extra_error (Affine3: suma de |coef| de los rayos con id >= n;
// AF2: 0). Con el evaluador AF2 la forma debe ser linearizable (noise_count == n); con Affine3 basta
// is_active(). Tambien se registra cuantas formas Affine3 tienen rayos no-variable (extra > 0).
#include <bits/stdc++.h>
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_AffineEval.h"
#include "ibex_LinearizerAffine2.h"
#include "ibex_KNomial.h"
using namespace std;
using namespace ibex;

int main() {
	const int F = 200, S = 1000;
	mt19937_64 rng(20260917);
	normal_distribution<double> N01(0.0, 1.0);
	uniform_real_distribution<double> U01(0.0, 1.0);

	struct Variant { const char* name; bool aa; int k; };
	const Variant variants[3] = {{"AA k=0", true, 0}, {"AA k=3", true, 3}, {"AF2 k=0", false, 0}};
	long viol[3] = {0, 0, 0}, no_lin[3] = {0, 0, 0}, con_extra = 0, formas = 0;
	double max_exc[3] = {0.0, 0.0, 0.0}, extra_rel_sum = 0.0;

	for (int t = 0; t < F; t++) {
		const int n = 2 + (int) (rng() % 3);
		const int deg = 2 + (int) (rng() % 2);
		const int nterms = 2 + (int) (rng() % 5);
		Variable x(n);
		const ExprNode* e = &ExprConstant::new_scalar(N01(rng));
		for (int q = 0; q < nterms; q++) {
			const int d = 1 + (int) (rng() % deg);
			const ExprNode* term = &(N01(rng) * x[(int) (rng() % n)]);
			for (int r = 1; r < d; r++) term = &((*term) * x[(int) (rng() % n)]);
			e = &((*e) + (*term));
		}
		Function f(x, *e);

		IntervalVector box(n);
		for (int i = 0; i < n; i++) {
			const double c = 2.0 * N01(rng), r = 0.1 + 1.9 * U01(rng);
			box[i] = Interval(c - r, c + r);
		}

		// formas: AA k=0, AA k=3, AF2 k=0
		knomial_max_k() = 0;
		Affine3Eval ev3(f);
		Affine2Eval ev2(f);
		Affine3 af_aa0 = ev3.eval(box, Affine3Variables(box)).second->i();
		knomial_max_k() = 3;
		Affine3 af_aa3 = ev3.eval(box, Affine3Variables(box)).second->i();
		knomial_max_k() = 0;
		Affine2 af_af2 = ev2.eval(box, Affine2Variables(box)).second->i();

		const bool lin[3] = {affine_form_is_linearizable(af_aa0, n), affine_form_is_linearizable(af_aa3, n),
		                     affine_form_is_linearizable(af_af2, n)};
		const double extra[3] = {affine_extra_error(af_aa0, n), affine_extra_error(af_aa3, n), affine_extra_error(af_af2, n)};
		const double mid[3] = {af_aa0.mid(), af_aa3.mid(), af_af2.mid()};
		const double err[3] = {af_aa0.err(), af_aa3.err(), af_af2.err()};
		vector<double> slope[3];
		for (int v = 0; v < 3; v++) {
			if (!lin[v]) { no_lin[v]++; continue; }
			slope[v].resize(n);
			for (int i = 0; i < n; i++)
				slope[v][i] = (v == 0 ? af_aa0.noise(i) : (v == 1 ? af_aa3.noise(i) : af_af2.noise(i))) / box[i].rad();
		}
		formas++;
		if (extra[0] > 0.0) { con_extra++; extra_rel_sum += extra[0] / (err[0] + extra[0]); }

		for (int s = 0; s < S; s++) {
			IntervalVector pt(n);
			Vector xv(n);
			for (int i = 0; i < n; i++) {
				xv[i] = (s % 2 == 0) ? ((rng() % 2) ? box[i].ub() : box[i].lb()) : box[i].lb() + U01(rng) * box[i].diam();
				pt[i] = Interval(xv[i]);
			}
			const Interval fx = f.eval(pt);
			const double tol = 1e-9 * (1.0 + fx.mag());
			for (int v = 0; v < 3; v++) {
				if (!lin[v]) continue;
				double l = mid[v];
				for (int i = 0; i < n; i++) l += slope[v][i] * (xv[i] - box[i].mid());
				const double rad = err[v] + extra[v];
				const double exc = max(fx.ub() - (l + rad), (l - rad) - fx.lb());
				if (exc > tol) { viol[v]++; max_exc[v] = max(max_exc[v], exc); }
			}
		}
	}

	printf("aa_linearizer_test: %d polinomios (2-4 variables, grado 2-3), %d puntos por funcion; formas evaluadas: %ld\n", F, S, formas);
	long total = 0;
	for (int v = 0; v < 3; v++) {
		printf("  %-8s violaciones=%ld (max exceso %.3e) formas_no_linearizables=%ld\n", variants[v].name, viol[v], max_exc[v], no_lin[v]);
		total += viol[v];
	}
	printf("  Affine3 con rayos no-variable (extra > 0): %ld de %ld; extra/(err+extra) medio = %.3f\n",
	       con_extra, formas, con_extra ? extra_rel_sum / con_extra : 0.0);
	printf("violaciones=%ld\n", total);
	printf("%s\n", total == 0 ? "LINEARIZADOR AA OK" : "LINEARIZADOR AA CON PROBLEMAS");
	return total == 0 ? 0 : 1;
}
