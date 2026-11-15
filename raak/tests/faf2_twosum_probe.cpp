// Sonda: twoSum de fAF2 (2Sum de Knuth, copiado tal cual) bajo el modo de redondeo que deja Gaol,
// y efecto en una forma afin real: x + beta con beta diminuto.
#include <bits/stdc++.h>
#include <cfenv>
#include "ibex.h"
#include "ibex_Affine.h"
using namespace std; using namespace ibex;
static double twoSum(volatile double a, volatile double b, double* res) {
	volatile double s = a + b; *res = s;
	volatile double a2 = s - b; volatile double b2 = s - a2;
	volatile double da = a - a2; volatile double db = b - b2;
	volatile double t = da + db; return t;
}
int main() {
	Interval dummy(1.0); dummy += 1.0;   // asegura que Gaol esta inicializado
	printf("modo de redondeo: %d (FE_UPWARD=%d, FE_TONEAREST=%d)\n", fegetround(), FE_UPWARD, FE_TONEAREST);
	const double as[3] = {1.0, 1.0, 3.0}; const double bs[3] = {-1e-40, 1e-40, -1e-20};
	for (int i = 0; i < 3; i++) {
		double s; double t = twoSum(as[i], bs[i], &s);
		Interval e = (Interval(as[i]) + Interval(bs[i])) - Interval(s);   // error real, encerrado
		printf("a=%g b=%g: s=%.17g  t=%.17g  error real en [%.6g, %.6g]  %s\n", as[i], bs[i], s, t, e.lb(), e.ub(),
		       (t >= e.lb() && t <= e.ub()) ? "t exacto" : "t NO es el error");
	}
	// barrido aleatorio: cuantas veces |error real| > 2(1+2EM)|t| (lo que fAF2 suma al termino de error)
	mt19937_64 rng(1); uniform_real_distribution<double> U(-1, 1); long bad = 0, inexact = 0, N = 2000000; double worst = 0;
	for (long k = 0; k < N; k++) {
		double a = U(rng) * pow(2.0, (int)(U(rng) * 30)), b = U(rng) * pow(2.0, (int)(U(rng) * 30) - (k % 3 == 0 ? 60 : 0) - (k % 7 == 0 ? 110 : 0));
		double s; double t = twoSum(a, b, &s);
		Interval e = (Interval(a) + Interval(b)) - Interval(s);
		if (!(t >= e.lb() && t <= e.ub())) inexact++;
		double emag = e.mag(), cover = 2.0 * (1 + 2 * 4.44089209850062616e-16) * fabs(t);
		if (emag > cover) { bad++; worst = max(worst, (e.mig() - cover) / max(fabs(s), 1e-300)); }
	}
	printf("aleatorio: %ld sumas; t inexacto en %ld; error real > 2(1+2EM)|t| en %ld; peor defecto relativo a |s|: %.3g\n", N, inexact, bad, worst);
	// forma afin real: x en [1,1+1e-3]... x + beta
	Function f("x", "x+(-1e-40)"); IntervalVector B(1, Interval(1.0, 2.0));
	Affine2Eval ev(f); pair<Domain*, TemplateDomain<AffineMain<AF_fAF2> >*> r = ev.eval(B, AffineVarMainVector<AF_fAF2>(B));
	const AffineMain<AF_fAF2>& af = r.second->i();
	printf("forma afin de x+(-1e-40) en [1,2]: centro=%.17g coef=%.17g err=%.6g  itv=[%.17g, %.17g]\n", af.mid(), af.noise(0), af.err(), af.itv().lb(), af.itv().ub());
	// contencion en x=1: valor real 1-1e-40 < 1
	Interval real = Interval(1.0) + Interval(-1e-40);
	printf("valor real en x=1: [%.17g, %.17g]; la forma en eps=-1 da %.17g - err %.6g\n", real.lb(), real.ub(), af.mid() - af.noise(0), af.err());
	return 0;
}
