// [raak local] Fase 3, nivel 1: sobreestimacion de las seis variantes (AF2 | RAA | AA) x (k=0 | k=3)
// sobre las instancias de benchs/optim, SIN resolver.
//
// Para cada instancia Minibex: se carga el System, se toma la caja inicial (las componentes no
// acotadas se recortan a [-BIG, BIG] y se cuenta en 'clipped') y se generan sub-cajas aleatorias de
// anchura relativa 1/2, 1/4, 1/8 y 1/16 (SUBBOXES por escala), que imitan las cajas que ve el B&B.
// Sobre cada caja y cada funcion escalar del sistema (objetivo y restricciones) se calcula:
//   w_itv     anchura de la extension natural de intervalos f(B)
//   w_sample  anchura del hull de f en SAMPLES puntos aleatorios de B mas el centro
//             (aproximacion INTERIOR del rango real; por tanto ratio >= 1 salvo redondeo)
//   por variante: w_aff (anchura de la forma afin), nl_err (parte no lineal: rad(itv) - sum |a_i|,
//             i < n, comparable entre AF2 y AA), ratio_aff = w_aff / w_sample, viol (puntos muestreados
//             fuera de la envolvente mid + sum a_i eps_i +- nl_err), k_used (operaciones en las que la
//             variante reemplazo la cota base: productos/cuadrados/corner/aa) y us (microsegundos).
// Salida CSV por stdout, una fila por (instancia, funcion, caja, variante). Resumen en stderr.
//
// uso: range_eval [--subboxes N=2] [--samples S=200] [--seed X=20260921] [--trig auto|cheb|minrange|legacy]
//                 [--max-ctrs M=50] archivo.bch ...
#include <bits/stdc++.h>
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_KNomial.h"
#include "ibex_AffineTrig.h"
using namespace std;
using namespace ibex;

static const double BIG = 1e4;

struct Variant { const char* name; const char* arith; int k; bool aa; AffineMode mode; };
static const Variant VARS[6] = {
	{"af2_k0", "af2", 0, false, AFFINE_AF2}, {"af2_k3", "af2", 3, false, AFFINE_AF2},
	{"raa_k0", "raa", 0, false, AFFINE_RAA}, {"raa_k3", "raa", 3, false, AFFINE_RAA},
	{"aa_k0",  "aa",  0, true,  AFFINE_AF2}, {"aa_k3",  "aa",  3, true,  AFFINE_AF2},
};

struct AffRes { bool active; double mid, rad; vector<double> a; };

template<class T>
static AffRes eval_aff(AffineEval<T>& ev, const IntervalVector& box) {
	AffRes r;
	pair<Domain*, TemplateDomain<AffineMain<T> >*> res = ev.eval(box, AffineVarMainVector<T>(box));
	const AffineMain<T>& af = res.second->i();
	r.active = af.is_active();
	const Interval I = af.itv();
	r.mid = I.mid(); r.rad = I.rad();
	r.a.assign(box.size(), 0.0);
	if (r.active) for (int i = 0; i < box.size(); i++) r.a[i] = af.noise(i);
	return r;
}

static long k_used_total() {
	const KNomialStats& s = knomial_stats();
	return s.calls_used + s.sqr_used + s.corner_used + s.aa_used;
}

int main(int argc, char** argv) {
	int subboxes = 2, samples = 200, max_ctrs = 50;
	unsigned long seed = 20260921UL;
	string trig = "auto";
	vector<string> files;
	for (int i = 1; i < argc; i++) {
		string a = argv[i];
		if (a == "--subboxes" && i + 1 < argc) subboxes = atoi(argv[++i]);
		else if (a == "--samples" && i + 1 < argc) samples = atoi(argv[++i]);
		else if (a == "--seed" && i + 1 < argc) seed = strtoul(argv[++i], NULL, 10);
		else if (a == "--trig" && i + 1 < argc) trig = argv[++i];
		else if (a == "--max-ctrs" && i + 1 < argc) max_ctrs = atoi(argv[++i]);
		else files.push_back(a);
	}
	if (trig == "cheb") trig_lin_mode() = TRIG_CHEBYSHEV;
	else if (trig == "minrange") trig_lin_mode() = TRIG_MINRANGE;
	else if (trig == "legacy") trig_lin_mode() = TRIG_LEGACY;
	else trig_lin_mode() = TRIG_AUTO;

	const double scales[4] = {0.5, 0.25, 0.125, 0.0625};
	mt19937_64 rng(seed);
	uniform_real_distribution<double> U(0.0, 1.0);

	printf("instance,set,func,box_id,scale,variant,arith,k,n,clipped,active,w_itv,w_sample,w_aff,nl_err,ratio_aff,ratio_itv,viol,k_used,us\n");
	long rows = 0, skipped_vec = 0, total_viol = 0, inactive = 0;

	for (size_t fi = 0; fi < files.size(); fi++) {
		const string& path = files[fi];
		// nombre: <set>/<instance>.bch
		string inst = path, set = "";
		{
			size_t p = inst.rfind('/'); if (p != string::npos) { string dir = inst.substr(0, p); inst = inst.substr(p + 1); size_t q = dir.rfind('/'); set = (q == string::npos) ? dir : dir.substr(q + 1); }
			size_t d = inst.rfind(".bch"); if (d != string::npos) inst = inst.substr(0, d);
		}
		System* sys = NULL;
		try { sys = new System(path.c_str()); } catch (...) { fprintf(stderr, "  [skip] %s: no se pudo cargar\n", path.c_str()); continue; }
		const int n = sys->nb_var;
		IntervalVector box0 = sys->box;
		int clipped = 0;
		for (int i = 0; i < n; i++) {
			if (box0[i].is_unbounded() || box0[i].is_empty()) {
				double lo = std::max(box0[i].lb(), -BIG), hi = std::min(box0[i].ub(), BIG);
				if (!(lo < hi)) { lo = -BIG; hi = BIG; }
				box0[i] = Interval(lo, hi); clipped++;
			} else if (box0[i].is_degenerated()) {
				// una variable fija no aporta simbolo: se ensancha un poco para que la forma sea activa
				box0[i] = box0[i].inflate(1e-9);
			}
		}
		// funciones escalares: objetivo + restricciones
		vector<pair<string, const Function*> > funcs;
		if (sys->goal) funcs.push_back(make_pair(string("goal"), (const Function*) sys->goal));
		for (int c = 0; c < sys->nb_ctr && (int) funcs.size() <= max_ctrs; c++) {
			const Function& f = sys->ctrs[c].f;
			if (f.image_dim() != 1) { skipped_vec++; continue; }
			char nm[32]; snprintf(nm, sizeof nm, "c%d", c);
			funcs.push_back(make_pair(string(nm), &f));
		}
		// cajas: inicial + sub-cajas
		vector<pair<IntervalVector, double> > boxes;
		boxes.push_back(make_pair(box0, 1.0));
		for (int si = 0; si < 4; si++)
			for (int j = 0; j < subboxes; j++) {
				IntervalVector b(n);
				for (int i = 0; i < n; i++) {
					const double w = scales[si] * box0[i].diam();
					const double lo = box0[i].lb() + U(rng) * (box0[i].diam() - w);
					b[i] = Interval(lo, lo + w);
				}
				boxes.push_back(make_pair(b, scales[si]));
			}

		for (size_t k = 0; k < funcs.size(); k++) {
			const Function& f = *funcs[k].second;
			Affine2Eval ev2(f);
			Affine3Eval ev3(f);
			for (size_t bi = 0; bi < boxes.size(); bi++) {
				const IntervalVector& B = boxes[bi].first;
				// muestreo del rango
				vector<Vector> pts;
				pts.push_back(B.mid());
				for (int s = 0; s < samples; s++) { Vector p(n); for (int i = 0; i < n; i++) p[i] = B[i].lb() + U(rng) * B[i].diam(); pts.push_back(p); }
				Interval hull = Interval::empty_set();
				vector<double> fv(pts.size());
				bool bad = false;
				for (size_t s = 0; s < pts.size(); s++) {
					Interval v = f.eval(IntervalVector(pts[s]));
					if (v.is_empty() || v.is_unbounded()) { bad = true; break; }
					fv[s] = v.mid(); hull |= v;
				}
				if (bad) continue;                       // f no definida en algun punto (p. ej. log de negativo)
				Interval iv = f.eval(B);
				const double w_sample = hull.diam();
				const double w_itv = iv.diam();

				for (int vi = 0; vi < 6; vi++) {
					const Variant& V = VARS[vi];
					affine_mode() = V.mode; knomial_max_k() = V.k;
					const long ku0 = k_used_total();
					auto t0 = chrono::steady_clock::now();
					AffRes r = V.aa ? eval_aff<AF_fAFFullI>(ev3, B) : eval_aff<AF_fAF2>(ev2, B);
					const double us = chrono::duration<double, micro>(chrono::steady_clock::now() - t0).count();
					const long ku = k_used_total() - ku0;
					affine_mode() = AFFINE_AF2; knomial_max_k() = 0;

					double w_aff = 2.0 * r.rad, nl = 0.0; long viol = 0;
					if (r.active) {
						double sa = 0.0; for (int i = 0; i < n; i++) sa += fabs(r.a[i]);
						nl = std::max(0.0, r.rad - sa);
						const double tol = 1e-9 * (1.0 + fabs(r.mid) + r.rad) + 1e-12;
						for (size_t s = 0; s < pts.size(); s++) {
							double model = r.mid;
							for (int i = 0; i < n; i++) model += r.a[i] * ((pts[s][i] - B[i].mid()) / B[i].rad());
							if (fabs(fv[s] - model) > nl + tol) viol++;
						}
					} else { inactive++; w_aff = INFINITY; nl = INFINITY; }
					total_viol += viol; rows++;
					printf("%s,%s,%s,%zu,%g,%s,%s,%d,%d,%d,%d,%.10g,%.10g,%.10g,%.10g,%.6g,%.6g,%ld,%ld,%.1f\n",
					       inst.c_str(), set.c_str(), funcs[k].first.c_str(), bi, boxes[bi].second, V.name, V.arith, V.k, n, clipped,
					       r.active ? 1 : 0, w_itv, w_sample, w_aff, nl,
					       (w_sample > 1e-15 && r.active) ? w_aff / w_sample : -1.0,
					       (w_sample > 1e-15) ? w_itv / w_sample : -1.0, viol, ku, us);
				}
			}
		}
		delete sys;
		fprintf(stderr, "  %s/%s: n=%d funcs=%zu cajas=%zu\n", set.c_str(), inst.c_str(), n, funcs.size(), boxes.size());
	}
	fprintf(stderr, "filas=%ld restricciones_vectoriales_omitidas=%ld formas_inactivas=%ld violaciones=%ld\n", rows, skipped_vec, inactive, total_viol);
	fprintf(stderr, total_viol == 0 ? "RANGE OK: ninguna envolvente afin viola la contencion\n" : "RANGE FALLA: hay violaciones de contencion\n");
	return total_viol == 0 ? 0 : 1;
}
