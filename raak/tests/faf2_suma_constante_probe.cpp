#include <bits/stdc++.h>
#include <cfenv>
#include "ibex.h"
#include "ibex_Affine.h"
using namespace std; using namespace ibex;
static void direct(const char* tag) {
	IntervalVector B(1, Interval(1.0, 2.0));
	AffineVarMainVector<AF_fAF2> v(B);
	AffineMain<AF_fAF2> a(v[0]);
	a += -1e-40;
	printf("%-30s directo  a += -1e-40 : centro=%.17g err=%.6g cota inferior=%.17g\n", tag, a.mid(), a.err(), a.mid() - fabs(a.noise(0)) - a.err());
	AffineMain<AF_fAF2> b(v[0]);
	b += Interval(-1e-40);
	printf("%-30s directo  b += Interval(-1e-40): centro=%.17g err=%.6g\n", tag, b.mid(), b.err());
	AffineMain<AF_fAF2> c(v[0]);
	c += -1e-10;
	printf("%-30s directo  c += -1e-10 : centro=%.17g err=%.6g cota inferior=%.17g\n", tag, c.mid(), c.err(), c.mid() - fabs(c.noise(0)) - c.err());
	AffineMain<AF_fAF2> d(v[0]);
	d += -1e-17;
	printf("%-30s directo  d += -1e-17 : centro=%.17g err=%.6g cota inferior=%.17g\n", tag, d.mid(), d.err(), d.mid() - fabs(d.noise(0)) - d.err());
}
int main() {
	Interval dummy(1.0); dummy += 1.0;
	direct("hacia arriba (Gaol)");
	fesetround(FE_TONEAREST); direct("al mas cercano"); fesetround(FE_UPWARD);
	return 0;
}
