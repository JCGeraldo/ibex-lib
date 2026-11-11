// [raak local] Test estricto de contencion de las piezas de RAA-K que no cubre knomial_lemma_check:
// corner test (parche 0005), cuadrado de Chebyshev, linealizacion de sin/cos (AffineTrig) y exp/log.
// Genera funciones aleatorias que ejercitan cada pieza, las evalua con Affine2Eval sobre cajas de
// radio 1e-6..3 y comprueba, para puntos muestreados p (vertices e interiores), que
//     f(p)  esta en  mid + sum_i a_i eps_i(p) + err [-1,1],   eps_i(p) = (p_i - c_i) / r_i,
// con TODO evaluado en aritmetica de intervalos (f(p), eps_i, la envolvente). Violacion SEGURA: el
// intervalo de f(p) es disjunto del de la envolvente (el valor real esta fuera, sin duda). Posible:
// solo sobresale (puede ser el redondeo de la propia evaluacion). A diferencia de range_eval no hay
// tolerancia: detecta fallos de un ulp.
// Uso: affine_containment_check [N=4000 por familia] [semilla=11] [encoger=1]
// 'encoger' < 1 multiplica el termino de error por ese factor: control de sensibilidad (el test debe
// detectar violaciones cuando la envolvente se estrecha artificialmente).
#include <bits/stdc++.h>
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_KNomial.h"
#include "ibex_AffineTrig.h"
using namespace std;
using namespace ibex;

static mt19937_64 rng;
static double U(double a, double b) { return uniform_real_distribution<double>(a, b)(rng); }
static int RI(int a, int b) { return uniform_int_distribution<int>(a, b)(rng); }

static string num(double v) { char b[64]; snprintf(b, sizeof b, "%.17g", v); return (v < 0) ? string("(") + b + ")" : string(b); }
// combinacion lineal aleatoria c0 + sum c_i x(i); mix = magnitudes 2^-6..2^6
static string L(int n, bool mix, double c0scale = 1.0) {
	string s = num(U(-1, 1) * c0scale);
	int used = 0;
	for (int i = 1; i <= n; i++) {
		if (U(0, 1) < 0.25 && used > 0) continue;
		double c = U(-1, 1) * (mix ? ldexp(1.0, RI(-6, 6)) : 1.0);
		if (fabs(c) < 0.05) c = 0.5;
		s += "+" + num(c) + "*x(" + to_string(i) + ")"; used++;
	}
	return "(" + s + ")";
}
struct Fam { const char* name; int id; };
static const Fam FAMS[] = {
	{"corner: (L*L)*(L*L)", 0}, {"corner: (L*L+L)*(sin(L)+L)", 1}, {"corner: (L*L)*(L^2+L)", 2},
	{"sqr: (L*L+L)^2", 3}, {"sqr: L^2 y (L^2+L)^2", 4},
	{"trig: sin(L), cos(L)", 5}, {"trig: sin(L*L)+cos(L)*L", 6},
	{"exp/log: exp(L)*L + ln(4+L^2)", 7}, {"mezcla: (sin(L)+L)^2*(L*L)", 8},
};
static string expr(int fam, int n, bool mix) {
	switch (fam) {
	case 0: return "(" + L(n, mix) + "*" + L(n, mix) + ")*(" + L(n, mix) + "*" + L(n, mix) + ")";
	case 1: return "(" + L(n, mix) + "*" + L(n, mix) + "+" + L(n, mix) + ")*(sin(" + L(n, false) + ")+" + L(n, mix) + ")";
	case 2: return "(" + L(n, mix) + "*" + L(n, mix) + ")*(" + L(n, mix) + "^2+" + L(n, mix) + ")";
	case 3: return "(" + L(n, mix) + "*" + L(n, mix) + "+" + L(n, mix) + ")^2";
	case 4: return L(n, mix) + "^2+(" + L(n, mix) + "^2+" + L(n, mix) + ")^2";
	case 5: return "sin(" + L(n, false, 3.0) + ")+cos(" + L(n, false, 3.0) + ")";
	case 6: return "sin(" + L(n, false) + "*" + L(n, false) + ")+cos(" + L(n, false, 3.0) + ")*" + L(n, mix);
	case 7: return "exp(" + L(n, false) + ")*" + L(n, mix) + "+ln(4+" + L(n, false) + "^2)";
	default: return "(sin(" + L(n, false) + ")+" + L(n, mix) + ")^2*(" + L(n, mix) + "*" + L(n, mix) + ")";
	}
}
struct Var { const char* name; AffineMode mode; int k; TrigLinMode trig; };
static const Var VARS[] = {
	{"af2_k0", AFFINE_AF2, 0, TRIG_AUTO}, {"raa_k0", AFFINE_RAA, 0, TRIG_AUTO}, {"raa_k4", AFFINE_RAA, 4, TRIG_AUTO},
	{"raa_k4_cheb", AFFINE_RAA, 4, TRIG_CHEBYSHEV}, {"raa_k4_minrange", AFFINE_RAA, 4, TRIG_MINRANGE},
};
static const int NV = 5, NF = 9;

int main(int argc, char** argv) {
	long N = argc > 1 ? atol(argv[1]) : 4000;
	rng.seed(argc > 2 ? (unsigned) atol(argv[2]) : 11u);
	const double shrink = argc > 3 ? atof(argv[3]) : 1.0;
	long seg[NF][NV] = {{0}}, pos[NF][NV] = {{0}}, casos[NF][NV] = {{0}}, inact[NF] = {0};
	double worst[NF][NV] = {{0}};
	const KNomialStats s0 = knomial_stats();
	for (int fam = 0; fam < NF; fam++) {
		for (long it = 0; it < N; it++) {
			const int n = RI(2, 6);
			const bool mix = U(0, 1) < 0.4;
			const string e = expr(FAMS[fam].id, n, mix);
			const string xs = "x[" + to_string(n) + "]";
			Function f(xs.c_str(), e.c_str());
			IntervalVector B(n);
			const double rscale = pow(10.0, U(-6, 0.5));
			for (int i = 0; i < n; i++) { const double c = U(-2, 2), r = rscale * U(0.2, 1.0); B[i] = Interval(c - r, c + r); }
			// puntos: 16 vertices + 16 interiores
			vector<Vector> pts;
			for (int s = 0; s < 32; s++) {
				Vector p(n);
				for (int i = 0; i < n; i++) p[i] = (s < 16) ? (U(0, 1) < 0.5 ? B[i].lb() : B[i].ub()) : B[i].lb() + U(0, 1) * B[i].diam();
				pts.push_back(p);
			}
			vector<Interval> F(pts.size());
			bool bad = false;
			for (size_t s = 0; s < pts.size(); s++) { F[s] = f.eval(IntervalVector(pts[s])); if (F[s].is_empty() || F[s].is_unbounded()) { bad = true; break; } }
			if (bad) continue;
			Affine2Eval ev(f);
			for (int v = 0; v < NV; v++) {
				affine_mode() = VARS[v].mode; knomial_max_k() = VARS[v].k; trig_lin_mode() = VARS[v].trig;
				pair<Domain*, TemplateDomain<AffineMain<AF_fAF2> >*> res = ev.eval(B, AffineVarMainVector<AF_fAF2>(B));
				const AffineMain<AF_fAF2>& af = res.second->i();
				affine_mode() = AFFINE_AF2; knomial_max_k() = 0; trig_lin_mode() = TRIG_AUTO;
				if (!af.is_active()) { if (v == 0) inact[fam]++; continue; }
				casos[fam][v]++;
				const int nc = af.noise_count();
				const double mid = af.mid(), err = af.err() * shrink;
				bool vs = false, vp = false;
				for (size_t s = 0; s < pts.size(); s++) {
					Interval E(mid);
					for (int i = 0; i < n && i < nc; i++) {
						const Interval eps = (Interval(pts[s][i]) - Interval(B[i].mid())) / Interval(B[i].rad());
						E += Interval(af.noise(i)) * eps;
					}
					// simbolos de ruido que no son variables (no deberia haber en fAF2): se acotan por [-1,1]
					for (int i = n; i < nc; i++) E += Interval(af.noise(i)) * Interval(-1.0, 1.0);
					E += Interval(-err, err);
					if (!E.is_superset(F[s])) vp = true;
					if (!E.intersects(F[s])) {
						vs = true;
						const double exc = F[s].lb() > E.ub() ? F[s].lb() - E.ub() : E.lb() - F[s].ub();
						const double rel = exc / (fabs(mid) + af.itv().rad() + 1e-300);
						if (rel > worst[fam][v]) worst[fam][v] = rel;
						if (seg[fam][v] < 2 && !vs) {}
					}
				}
				if (vs) { if (seg[fam][v] < 1) fprintf(stderr, "VIOLACION SEGURA fam=%d var=%s n=%d rscale=%.2e expr=%s\n", fam, VARS[v].name, n, rscale, e.c_str()); seg[fam][v]++; }
				if (vp) pos[fam][v]++;
			}
		}
	}
	const KNomialStats s1 = knomial_stats();
	printf("familia,variante,casos,violaciones_seguras,posibles,peor_exceso_relativo\n");
	long tot = 0;
	for (int fam = 0; fam < NF; fam++)
		for (int v = 0; v < NV; v++) {
			printf("\"%s\",%s,%ld,%ld,%ld,%.3e\n", FAMS[fam].name, VARS[v].name, casos[fam][v], seg[fam][v], pos[fam][v], worst[fam][v]);
			tot += seg[fam][v];
		}
	fprintf(stderr, "uso de las piezas: productos k-nomial usados=%ld, cuadrados Chebyshev usados=%ld de %ld, corner usados=%ld de %ld\n",
	        s1.calls_used - s0.calls_used, s1.sqr_used - s0.sqr_used, s1.sqr_products - s0.sqr_products,
	        s1.corner_used - s0.corner_used, s1.corner_products - s0.corner_products);
	fprintf(stderr, "TOTAL violaciones seguras = %ld\n", tot);
	return tot == 0 ? 0 : 1;
}
