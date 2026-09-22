// Prueba del corner test de la Ec. (16) de [A] en AffineMain<AF_fAF2> (Fase 1, parche 0005).
//
// 10 000 pares aleatorios de formas Affine2 con n in {1..6} simbolos, coeficientes N(0,1) con ceros
// aleatorios, errores ex, ey in {0} U |N(0,1)|. Para cada par:
//   (i)   radio del producto con RAA/k=0 <= radio con AF2/k=0 + 1e-12*escala
//   (ii)  contencion: 2000 muestras (eps, h, g) in [-1,1]^(n+2); el producto exacto esta dentro de la
//         forma resultante evaluada en eps (mid + sum noise_i eps_i +- err), en ambas variantes; eso
//         implica la contencion en itv(), que tambien se comprueba
//   (iii) si ex = ey = 0, el resultado con RAA/k=0 es bit a bit igual al guardado antes del parche
//         (modo --dump: vuelca mid, err y noise(i) en hexadecimal; modo --compare: compara)
// Ademas: E_RAA / E_fAF2 medio del termino de cruces (formula cerrada) y, si la biblioteca ya tiene
// los contadores (compilar con -DRAA_CORNER_STATS), corner_used / corner_products.
//
// uso: raa_corner_test --dump <archivo> | --compare <archivo>
#include <bits/stdc++.h>
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_KNomial.h"
using namespace std;
using namespace ibex;

struct Form {
	double center;
	vector<double> coef;
	double err;
};

static Affine2 build(const Affine2Variables& vars, const Form& f) {
	Affine2 x = Affine2(vars[0]) * 0.0;
	x = x + f.center;
	for (size_t i = 0; i < f.coef.size(); i++)
		if (f.coef[i] != 0.0) x = x + f.coef[i] * Affine2(vars[(int) i]);
	if (f.err > 0.0) x = x + Interval(-f.err, f.err);
	return x;
}

static void set_variant(AffineMode mode, int k) {
	affine_mode() = mode;
	knomial_max_k() = k;
}

// representacion exacta (hexadecimal) de la forma, para la comparacion bit a bit
static string dump_form(const Affine2& r, int n) {
	char buf[64];
	string s;
	snprintf(buf, sizeof buf, "%d %a %a", r.noise_count(), r.mid(), r.err());
	s += buf;
	for (int i = 0; i < n && i < r.noise_count(); i++) {
		snprintf(buf, sizeof buf, " %a", r.noise(i));
		s += buf;
	}
	return s;
}

// E_RAA y E_fAF2 del termino de cruces (formulas cerradas, sin redondeo)
static double cross_corner_exact(const Form& fx, const Form& fy) {
	double pp = 0.0, pm = 0.0;
	for (size_t i = 0; i < fx.coef.size(); i++) {
		pp += fabs(fy.err * fx.coef[i] + fx.err * fy.coef[i]);
		pm += fabs(fy.err * fx.coef[i] - fx.err * fy.coef[i]);
	}
	return max(pp, pm) + fx.err * fy.err;
}
static double cross_faf2_exact(const Form& fx, const Form& fy) {
	double sx = 0.0, sy = 0.0;
	for (size_t i = 0; i < fx.coef.size(); i++) { sx += fabs(fx.coef[i]); sy += fabs(fy.coef[i]); }
	return fx.err * sy + sx * fy.err + fx.err * fy.err;
}

int main(int argc, char** argv) {
	if (argc != 3 || (string(argv[1]) != "--dump" && string(argv[1]) != "--compare")) {
		printf("uso: %s --dump <archivo> | --compare <archivo>\n", argv[0]);
		return 2;
	}
	const bool dumping = (string(argv[1]) == "--dump");
	ofstream out;
	ifstream in;
	if (dumping) out.open(argv[2]);
	else in.open(argv[2]);
	if (!(dumping ? out.good() : in.good())) { printf("no se pudo abrir %s\n", argv[2]); return 2; }

	const int T = 10000, S = 2000;
	mt19937_64 rng(20260916);
	normal_distribution<double> N01(0.0, 1.0);
	uniform_real_distribution<double> U01(0.0, 1.0), U(-1.0, 1.0);

	long viol_radio = 0, viol_contencion = 0, viol_itv = 0, diff_bits = 0, sin_error = 0, comparados = 0;
	long con_error = 0, corner_mejora = 0, saltados = 0;
	double ratio_sum = 0.0, max_excess = 0.0;
	long tighter = 0;

	for (int t = 0; t < T; t++) {
		const int n = 1 + (int) (rng() % 6);
		const double pzero = (rng() % 3 == 0) ? 0.5 : 0.2;
		Form fx, fy;
		fx.center = 2.0 * N01(rng);
		fy.center = 2.0 * N01(rng);
		fx.coef.resize(n);
		fy.coef.resize(n);
		for (int i = 0; i < n; i++) {
			fx.coef[i] = (U01(rng) < pzero) ? 0.0 : N01(rng);
			fy.coef[i] = (U01(rng) < pzero) ? 0.0 : N01(rng);
		}
		fx.err = (rng() % 2) ? fabs(N01(rng)) : 0.0;
		fy.err = (rng() % 2) ? fabs(N01(rng)) : 0.0;

		Affine2Variables vars(n, Interval(-1, 1));
		const Affine2 x = build(vars, fx), y = build(vars, fy);

		set_variant(AFFINE_AF2, 0);
		const Affine2 r_af2 = x * y;
		set_variant(AFFINE_RAA, 0);
		const Affine2 r_raa = x * y;
		set_variant(AFFINE_AF2, 0);

		if (!r_af2.is_active() || !r_raa.is_active() || r_af2.noise_count() < n || r_raa.noise_count() < n) {
			saltados++;
			continue;
		}

		// (i) radio
		const double escala = 1.0 + fabs(r_af2.mid()) + r_af2.err();
		if (r_raa.err() > r_af2.err() + 1e-12 * escala) viol_radio++;
		if (r_raa.err() < r_af2.err() * (1.0 - 1e-9)) tighter++;

		// (ii) contencion por muestreo (mitad de las muestras en vertices)
		const Affine2* forms[2] = {&r_af2, &r_raa};
		const Interval itv_af2 = r_af2.itv(), itv_raa = r_raa.itv();
		for (int s = 0; s < S; s++) {
			const bool vertex = (s % 2 == 0);
			auto pick = [&]() { return vertex ? ((rng() % 2) ? 1.0 : -1.0) : U(rng); };
			const double h = pick(), g = pick();
			double vx = fx.center + fx.err * h, vy = fy.center + fy.err * g;
			double lin[2] = {r_af2.mid(), r_raa.mid()};
			for (int i = 0; i < n; i++) {
				const double e = pick();
				vx += fx.coef[i] * e;
				vy += fy.coef[i] * e;
				for (int m = 0; m < 2; m++) lin[m] += forms[m]->noise(i) * e;
			}
			const double exact = vx * vy, tol = 1e-9 * (1.0 + fabs(exact));
			for (int m = 0; m < 2; m++) {
				const double excess = fabs(exact - lin[m]) - forms[m]->err();
				if (excess > tol) { viol_contencion++; max_excess = max(max_excess, excess); }
			}
			if (!itv_af2.contains(exact) && (exact < itv_af2.lb() - tol || exact > itv_af2.ub() + tol)) viol_itv++;
			if (!itv_raa.contains(exact) && (exact < itv_raa.lb() - tol || exact > itv_raa.ub() + tol)) viol_itv++;
		}

		// (iii) sin error en los factores: bit a bit igual a la referencia anterior al parche
		if (fx.err == 0.0 && fy.err == 0.0) {
			sin_error++;
			const string line = dump_form(r_raa, n);
			if (dumping) out << t << ' ' << line << '\n';
			else {
				string expected;
				if (getline(in, expected)) {
					comparados++;
					if (expected != to_string(t) + " " + line) diff_bits++;
				}
			}
		} else {
			con_error++;
			const double e_raa = cross_corner_exact(fx, fy), e_faf2 = cross_faf2_exact(fx, fy);
			if (e_faf2 > 0.0) ratio_sum += e_raa / e_faf2;
			if (e_raa < e_faf2 * (1.0 - 1e-12)) corner_mejora++;
		}
	}

	printf("raa_corner_test: %d pares (n de 1 a 6), %d muestras por par; saltados (forma no activa): %ld\n", T, S, saltados);
	printf("violaciones_radio=%ld violaciones_contencion=%ld violaciones_itv=%ld diferencias_bit_a_bit_sin_error=%ld\n",
	       viol_radio, viol_contencion, viol_itv, diff_bits);
	printf("  (max exceso de contencion: %.3e; pares sin error: %ld, comparados con la referencia: %ld; RAA mas estrecho que AF2 en %ld pares)\n",
	       max_excess, sin_error, comparados, tighter);
	printf("termino de cruces (formula cerrada) sobre %ld pares con error: E_RAA/E_fAF2 medio = %.4f, E_RAA < E_fAF2 en %ld pares (reduccion media %.1f %%)\n",
	       con_error, con_error ? ratio_sum / con_error : 1.0, corner_mejora, con_error ? 100.0 * (1.0 - ratio_sum / con_error) : 0.0);
#ifdef RAA_CORNER_STATS
	const KNomialStats& st = knomial_stats();
	printf("biblioteca: corner_used/corner_products = %ld/%ld, cruces usados / fAF2 = %.4f\n",
	       st.corner_used, st.corner_products, st.cross_faf2 > 0 ? st.cross_corner / st.cross_faf2 : 1.0);
#endif
	const bool ok = (viol_radio == 0 && viol_contencion == 0 && viol_itv == 0 && diff_bits == 0 && (dumping || comparados == sin_error));
	printf("%s\n", ok ? "CORNER OK" : "CORNER CON PROBLEMAS");
	return ok ? 0 : 1;
}
