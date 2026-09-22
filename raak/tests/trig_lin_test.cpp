// [raak local] Fase 2.2 (parche 0008): calidad de la linealizacion de sin y cos.
//
// Compara los tres modos de trig_lin_mode() -- legacy (codigo original del plugin: pendiente de
// Gauss de dos puntos), cheb (pendiente de cuerda, Ec. 12 de [A]) y minrange -- en las dos
// aritmeticas del plugin: Affine2 (AF_fAF2, la base de AF2 y RAA) y Affine3 (AF_fAFFullI, AA).
//
// Barrido: intervalos [c - w/2, c + w/2] con c en una malla de [-pi, pi] (paso pi/24, incluye los
// extremos y puntos de inflexion de sin y cos) y w en una lista de anchos de 0.01 a 2 pi. Para cada
// intervalo y funcion:
//   sin(x), cos(x)                  funciones basicas
//   sin(x)^2 + cos(x)^2  (== 1)     composicion: la anchura de la forma es puro error de linealizacion
//   sin(x) * cos(x)  (== sin(2x)/2)  producto de dos formas correlacionadas por el mismo simbolo
// Metricas por fila (CSV en stdout):
//   width_aff    anchura de la forma resultante (itv())
//   width_exact  anchura del rango exacto de la funcion sobre el intervalo (aritmetica de intervalos)
//   ratio        width_aff / width_exact (1 = optimo; si width_exact < 1e-15 se escribe -1)
//   excess       width_aff - width_exact
//   lin_err      radio de la parte no lineal: itv().rad() - |coeficiente de la variable|
//   slope        coeficiente del simbolo de ruido de la variable (pendiente en coordenadas eps)
//   viol         numero de puntos muestreados (401 por intervalo) en los que f(v) queda fuera de la
//                envolvente mid + slope*eps(v) +- lin_err (debe ser 0 en todos los modos)
//   ns           tiempo medio por evaluacion, en nanosegundos (media de 50 repeticiones)
// Columnas de contexto: func, arith, mode, center, width, has_ext (el intervalo contiene un extremo de
// la funcion basica), has_infl (contiene un punto de inflexion). Para las compuestas has_ext/has_infl
// se refieren a sin.
//
// Al final imprime en stderr un resumen por (func, arith, mode): media geometrica de ratio, media de
// lin_err, violaciones y el desglose por has_ext / has_infl.
//
// uso: trig_lin_test > trig_lin.csv
#include <bits/stdc++.h>
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_AffineTrig.h"
using namespace std;
using namespace ibex;

static const double PI = 3.14159265358979323846;

struct Res {
	bool active;
	double mid, slope, lin_err, width_aff;
};

// evalua la funcion func sobre la variable x en itv, con la aritmetica T
template<class T>
static Res eval_one(int func, const Interval& itv) {
	IntervalVector box(1);
	box[0] = itv;
	AffineVarMainVector<T> vars(box);
	AffineMain<T> x(vars[0]);
	AffineMain<T> z;
	switch (func) {
	case 0: z = sin(x); break;
	case 1: z = cos(x); break;
	case 2: z = sqr(sin(x)) + sqr(cos(x)); break;
	default: z = sin(x) * cos(x); break;
	}
	Res r;
	const Interval I = z.itv();
	r.active = z.is_active();
	r.width_aff = I.diam();
	r.mid = z.mid();
	r.slope = r.active ? z.noise(0) : 0.0;              // simbolo de la variable: indice / id 0
	r.lin_err = r.active ? (I.rad() - fabs(r.slope)) : I.rad();
	if (r.lin_err < 0.0) r.lin_err = 0.0;
	return r;
}

static double exact_f(int func, double v) {
	switch (func) {
	case 0: return sin(v);
	case 1: return cos(v);
	case 2: return 1.0;
	default: return sin(v) * cos(v);
	}
}

static Interval exact_range(int func, const Interval& itv) {
	switch (func) {
	case 0: return sin(itv);
	case 1: return cos(itv);
	case 2: return Interval(1.0, 1.0);
	default: return 0.5 * sin(2.0 * itv);
	}
}

// contiene un punto (k + off) * pi ?
static bool contains_grid(const Interval& itv, double off) {
	const double k1 = ceil(itv.lb() / PI - off - 1e-12);
	const double k2 = floor(itv.ub() / PI - off + 1e-12);
	return k1 <= k2;
}

struct Acc {
	long n, viol, n_ext, n_infl;
	double sum_log_ratio, n_ratio, sum_err, sum_err_ext, sum_err_infl, sum_log_ratio_ext, n_ratio_ext;
	Acc() : n(0), viol(0), n_ext(0), n_infl(0), sum_log_ratio(0), n_ratio(0), sum_err(0), sum_err_ext(0),
	        sum_err_infl(0), sum_log_ratio_ext(0), n_ratio_ext(0) {}
};

int main() {
	const char* FUNC[4] = {"sin", "cos", "sin2+cos2", "sin*cos"};
	const char* ARITH[2] = {"AF2", "AA"};
	const char* MODE[3] = {"legacy", "cheb", "minrange"};
	const TrigLinMode TM[3] = {TRIG_LEGACY, TRIG_CHEBYSHEV, TRIG_MINRANGE};
	const double widths[] = {0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 6.28};
	const int NW = sizeof(widths) / sizeof(widths[0]);
	const int NC = 49;                       // centros: -pi .. pi, paso pi/24
	const int S = 401;                       // puntos de muestreo por intervalo
	const int REP = 50;                      // repeticiones para el tiempo

	map<string, Acc> acc;
	printf("func,arith,mode,center,width,has_ext,has_infl,width_aff,width_exact,ratio,excess,lin_err,slope,viol,ns\n");

	for (int func = 0; func < 4; func++)
	for (int ci = 0; ci < NC; ci++)
	for (int wi = 0; wi < NW; wi++) {
		const double c = -PI + ci * (2.0 * PI / (NC - 1));
		const double w = widths[wi];
		const Interval itv(c - w / 2, c + w / 2);
		// extremos e inflexiones de la funcion basica (sin para las compuestas)
		const bool is_cos = (func == 1);
		const bool has_ext  = contains_grid(itv, is_cos ? 0.0 : 0.5);
		const bool has_infl = contains_grid(itv, is_cos ? 0.5 : 0.0);
		const Interval ex = exact_range(func, itv);

		for (int ar = 0; ar < 2; ar++)
		for (int mo = 0; mo < 3; mo++) {
			trig_lin_mode() = TM[mo];
			Res r;
			auto t0 = chrono::steady_clock::now();
			for (int rep = 0; rep < REP; rep++)
				r = (ar == 0) ? eval_one<AF_fAF2>(func, itv) : eval_one<AF_fAFFullI>(func, itv);
			const double ns = chrono::duration<double, nano>(chrono::steady_clock::now() - t0).count() / REP;
			trig_lin_mode() = TRIG_AUTO;

			// contencion por muestreo: f(v) in mid + slope*eps(v) +- lin_err
			long viol = 0;
			const double tol = 1e-9 * (1.0 + fabs(r.mid) + fabs(r.slope) + r.lin_err) + 1e-14;
			for (int s = 0; s < S; s++) {
				const double v = itv.lb() + (itv.ub() - itv.lb()) * s / (S - 1);
				const double eps = (v - itv.mid()) / itv.rad();
				const double model = r.mid + r.slope * eps;
				if (fabs(exact_f(func, v) - model) > r.lin_err + tol) viol++;
			}
			const double wex = ex.diam();
			const double ratio = (wex > 1e-15) ? r.width_aff / wex : -1.0;
			printf("%s,%s,%s,%.6f,%.4g,%d,%d,%.10g,%.10g,%.6g,%.6g,%.10g,%.10g,%ld,%.0f\n",
			       FUNC[func], ARITH[ar], MODE[mo], c, w, has_ext ? 1 : 0, has_infl ? 1 : 0,
			       r.width_aff, wex, ratio, r.width_aff - wex, r.lin_err, r.slope, viol, ns);

			Acc& a = acc[string(FUNC[func]) + "," + ARITH[ar] + "," + MODE[mo]];
			a.n++; a.viol += viol; a.sum_err += r.lin_err;
			if (ratio > 0) { a.sum_log_ratio += log(ratio); a.n_ratio++; }
			if (has_ext) { a.n_ext++; a.sum_err_ext += r.lin_err; if (ratio > 0) { a.sum_log_ratio_ext += log(ratio); a.n_ratio_ext++; } }
			if (has_infl) { a.n_infl++; a.sum_err_infl += r.lin_err; }
		}
	}

	fprintf(stderr, "%-10s %-4s %-9s %6s %6s %10s %10s %10s %10s\n", "func", "arith", "mode", "n", "viol",
	        "gm_ratio", "gm_ratio_ext", "lin_err", "lin_err_ext");
	long total_viol = 0;
	for (map<string, Acc>::const_iterator it = acc.begin(); it != acc.end(); ++it) {
		const Acc& a = it->second;
		total_viol += a.viol;
		string f, ar, mo;
		{ stringstream ss(it->first); getline(ss, f, ','); getline(ss, ar, ','); getline(ss, mo, ','); }
		fprintf(stderr, "%-10s %-4s %-9s %6ld %6ld %10.4f %10.4f %10.4g %10.4g\n", f.c_str(), ar.c_str(), mo.c_str(),
		        a.n, a.viol, a.n_ratio ? exp(a.sum_log_ratio / a.n_ratio) : -1.0,
		        a.n_ratio_ext ? exp(a.sum_log_ratio_ext / a.n_ratio_ext) : -1.0,
		        a.n ? a.sum_err / a.n : 0.0, a.n_ext ? a.sum_err_ext / a.n_ext : 0.0);
	}
	fprintf(stderr, "violaciones_totales=%ld\n", total_viol);
	fprintf(stderr, total_viol == 0 ? "TRIG OK: todas las envolventes contienen a la funcion\n" : "TRIG FALLA: hay violaciones de contencion\n");
	return total_viol == 0 ? 0 : 1;
}
