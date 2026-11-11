// Sonda: ancho de la forma afin de cada restriccion de un CSP sobre cajas pequenas al azar,
// para AF2, RAA k=0 y RAA con k-nomial. Sirve para explicar en que restricciones actua el k-nomial.
// Uso: csp_width_probe <instancia.bch> [cajas por ancho=300] [semilla]
// Salida CSV: restriccion,ancho_caja,variante,mg_ancho_vs_af2,mg_ancho_vs_intervalo,productos_con_bloques,b2,b3,b4plus
#include <bits/stdc++.h>
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_KNomial.h"
#include "ibex_AffineTrig.h"
using namespace std; using namespace ibex;
struct V { const char* name; AffineMode m; int k; };
static const V VS[5] = {{"af2", AFFINE_AF2, 0}, {"raa_k0", AFFINE_RAA, 0}, {"raa_k2", AFFINE_RAA, 2}, {"raa_k4", AFFINE_RAA, 4}, {"raa_k6", AFFINE_RAA, 6}};
int main(int argc, char** argv) {
	System sys(argv[1]); const int n = sys.nb_var;
	const int NB = argc > 2 ? atoi(argv[2]) : 300; mt19937_64 rng(argc > 3 ? atol(argv[3]) : 7);
	uniform_real_distribution<double> U(0.0, 1.0);
	trig_lin_mode() = TRIG_AUTO;
	const double W[4] = {1.0, 0.1, 0.01, 0.001};
	printf("restriccion,ancho_caja,variante,mg_ancho_vs_af2,mg_ancho_vs_intervalo,con_bloques_por_eval,b2,b3,b4plus\n");
	for (int c = 0; c < sys.nb_ctr; c++) {
		const Function& f = sys.ctrs[c].f; if (f.image_dim() != 1) continue;
		Affine2Eval ev(f);
		for (int wi = 0; wi < 4; wi++) {
			double slog[5] = {0}, slogi[5] = {0}; long cb[5] = {0}, b2[5] = {0}, b3[5] = {0}, b4[5] = {0}; int cnt = 0;
			for (int t = 0; t < NB; t++) {
				IntervalVector B(n);
				for (int i = 0; i < n; i++) { const double lo = -3.0 + U(rng) * (6.0 - W[wi]); B[i] = Interval(lo, lo + W[wi]); }
				const double wit = f.eval(B).diam(); double w[5]; bool ok = wit > 0 && wit < 1e300;
				for (int v = 0; v < 5 && ok; v++) {
					affine_mode() = VS[v].m; knomial_max_k() = VS[v].k;
					const KNomialStats s0 = knomial_stats();
					pair<Domain*, TemplateDomain<AffineMain<AF_fAF2> >*> r = ev.eval(B, AffineVarMainVector<AF_fAF2>(B));
					const AffineMain<AF_fAF2>& af = r.second->i();
					if (!af.is_active()) { ok = false; break; }
					w[v] = af.itv().diam(); if (!(w[v] > 0)) { ok = false; break; }
					const KNomialStats& s1 = knomial_stats();
					cb[v] += s1.calls_with_blocks - s0.calls_with_blocks; b2[v] += s1.blocks_by_size[0] - s0.blocks_by_size[0]; b3[v] += s1.blocks_by_size[1] - s0.blocks_by_size[1];
					for (int q = 2; q < 6; q++) b4[v] += s1.blocks_by_size[q] - s0.blocks_by_size[q];
				}
				affine_mode() = AFFINE_AF2; knomial_max_k() = 0;
				if (!ok) continue;
				cnt++; for (int v = 0; v < 5; v++) { slog[v] += log(w[v] / w[0]); slogi[v] += log(w[v] / wit); }
			}
			if (cnt) for (int v = 0; v < 5; v++)
				printf("c%d,%g,%s,%.4f,%.4f,%.2f,%.2f,%.2f,%.2f\n", c, W[wi], VS[v].name, exp(slog[v] / cnt), exp(slogi[v] / cnt), (double) cb[v] / cnt, (double) b2[v] / cnt, (double) b3[v] / cnt, (double) b4[v] / cnt);
		}
	}
	return 0;
}
