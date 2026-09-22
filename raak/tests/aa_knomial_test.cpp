// Prueba del k-nomial en AffineMain<AF_fAFFullI> (AA tradicional, Fase 1, parche 0006).
//
// 3000 productos z = x*y de formas Affine3 construidas con Affine3Variables y operaciones previas
// (cuadrados y productos de formas compuestas), de modo que existan rayos con id >= 50.
//   (a) contencion por muestreo: para (eps, h, g) aleatorios, el producto exacto
//       (mid_x + sum a_id eps_id + err_x h)(mid_y + sum b_id eps_id + err_y g) esta en
//       mid_z + sum_{id en x o y} c_id eps_id +- (sum_{id nuevo} |c_id| + err_z), en k=0 y k=3.
//       Los rayos "nuevos" (id que no esta ni en x ni en y) son simbolos libres del resultado.
//   (b) radio (sum |c_id| + err) con k=3 <= radio con k=0
//   (c) con k=0 el resultado es bit a bit igual (noise_count, mid, err, cada rayo con su id) al de la
//       biblioteca anterior al parche: --dump vuelca en hexadecimal, --compare compara.
//
// Orden de calculo: primero se generan todos los pares (x, y), luego TODOS los productos con k=0 y
// despues todos los con k=3. AF_fAFFullI::_counter es un contador global compartido: si se intercalaran,
// un producto k=3 que consumiera un numero distinto de ids desplazaria los ids de todos los z0
// siguientes y (c) fallaria sin que la aritmetica de k=0 hubiera cambiado (eso ocurrio en la primera
// version de este test: 2985 "diferencias" que eran solo de numeracion).
//
// Razonado: _garbage no es publico; err() = _garbage.rad() y mid() = _center, asi que el test trata
// _garbage como simetrico. Es diminuto por diseno (se convierte en rayo al superar maTol = 2.5e-15),
// muy por debajo de la tolerancia relativa 1e-9 de la contencion.
//
// uso: aa_knomial_test --dump <archivo> | --compare <archivo>
#include <bits/stdc++.h>
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_KNomial.h"
using namespace std;
using namespace ibex;

struct Sparse {
	double mid, err;
	int nc;
	vector<pair<int, double>> coef;   // (id, coeficiente) de los rayos no nulos
	double radius() const { double r = err; for (auto& p : coef) r += fabs(p.second); return r; }
};

static Sparse sparse_of(const Affine3& f) {
	Sparse s;
	s.mid = f.mid(); s.err = f.err(); s.nc = f.noise_count();
	for (int i = 0; i < s.nc; i++) {
		const double c = f.noise(i);
		if (c != 0.0) s.coef.push_back({i, c});
	}
	return s;
}

static string dump_form(const Sparse& s) {
	char buf[96];
	snprintf(buf, sizeof buf, "%d %a %a %zu", s.nc, s.mid, s.err, s.coef.size());
	string out = buf;
	for (auto& p : s.coef) { snprintf(buf, sizeof buf, " %d:%a", p.first, p.second); out += buf; }
	return out;
}

int main(int argc, char** argv) {
	if (argc != 3 || (string(argv[1]) != "--dump" && string(argv[1]) != "--compare")) {
		printf("uso: %s --dump <archivo> | --compare <archivo>\n", argv[0]);
		return 2;
	}
	const bool dumping = (string(argv[1]) == "--dump");
	ofstream out; ifstream in;
	if (dumping) out.open(argv[2]); else in.open(argv[2]);
	if (!(dumping ? out.good() : in.good())) { printf("no se pudo abrir %s\n", argv[2]); return 2; }

	const int T = 3000, S = 300;
	mt19937_64 rng(20260913);
	normal_distribution<double> N01(0.0, 1.0);
	uniform_real_distribution<double> U01(0.0, 1.0), U(-1.0, 1.0);

	auto build = [&](const Affine3Variables& vars, int nv) {
		Affine3 f = Affine3(vars[0]) * 0.0 + 2.0 * N01(rng);
		for (int i = 0; i < nv; i++)
			if (U01(rng) < 0.8) f = f + N01(rng) * Affine3(vars[i]);
		// operaciones previas que crean rayos con id >= 50
		if (U01(rng) < 0.7) {
			const int j = (int) (rng() % nv);
			f = f + N01(rng) * sqr(Affine3(vars[j]) + N01(rng) * Affine3(vars[(j + 1) % nv]) + N01(rng));
		}
		if (U01(rng) < 0.5) {
			const int j = (int) (rng() % nv);
			f = f * (Affine3(vars[j]) + 0.5 * N01(rng) * Affine3(vars[(j + 1) % nv]) + 2.0 + fabs(N01(rng)));
		}
		return f;
	};

	// 1. todos los pares, con k=0
	knomial_max_k() = 0;
	vector<Affine3> xs, ys;
	xs.reserve(T); ys.reserve(T);
	for (int t = 0; t < T; t++) {
		const int nv = 2 + (int) (rng() % 4);
		Affine3Variables vars(nv, Interval(-1, 1));
		xs.push_back(build(vars, nv));
		ys.push_back(build(vars, nv));
	}
	// 2. todos los productos con k=0, luego todos con k=3
	vector<Affine3> z0s, z3s;
	z0s.reserve(T); z3s.reserve(T);
	knomial_max_k() = 0;
	for (int t = 0; t < T; t++) z0s.push_back(xs[t] * ys[t]);
	knomial_max_k() = 3;
	for (int t = 0; t < T; t++) z3s.push_back(xs[t] * ys[t]);
	knomial_max_k() = 0;

	long viol_cont = 0, viol_radio = 0, diff_k0 = 0, comparados = 0, saltados = 0, tighter = 0, con_rayos_nuevos = 0;
	double max_excess = 0.0, ratio_sum = 0.0;
	long ratio_n = 0;

	// 3. comprobaciones
	for (int t = 0; t < T; t++) {
		const Affine3& x = xs[t]; const Affine3& y = ys[t]; const Affine3& z0 = z0s[t]; const Affine3& z3 = z3s[t];
		if (!x.is_active() || !y.is_active() || !z0.is_active() || !z3.is_active()) { saltados++; continue; }
		const Sparse sx = sparse_of(x), sy = sparse_of(y), sz0 = sparse_of(z0), sz3 = sparse_of(z3);

		// (c) bit a bit con k=0
		const string line = to_string(t) + " " + dump_form(sz0);
		if (dumping) out << line << '\n';
		else { string expected; if (getline(in, expected)) { comparados++; if (expected != line) diff_k0++; } }

		// (b) radio
		const double r0 = sz0.radius(), r3 = sz3.radius();
		if (r3 > r0 * (1.0 + 1e-12) + 1e-14) viol_radio++;
		if (r3 < r0 * (1.0 - 1e-9)) tighter++;
		if (r0 > 0.0) { ratio_sum += r3 / r0; ratio_n++; }

		// (a) contencion
		set<int> ids_xy;
		for (auto& p : sx.coef) ids_xy.insert(p.first);
		for (auto& p : sy.coef) ids_xy.insert(p.first);
		const int nmax = max(max(sx.nc, sy.nc), max(sz0.nc, sz3.nc));
		vector<double> eps(nmax, 0.0);
		const Sparse* zs[2] = {&sz0, &sz3};
		double budget[2] = {sz0.err, sz3.err};
		bool nuevos = false;
		for (int m = 0; m < 2; m++)
			for (auto& p : zs[m]->coef)
				if (!ids_xy.count(p.first)) { budget[m] += fabs(p.second); nuevos = true; }
		if (nuevos) con_rayos_nuevos++;
		for (int s = 0; s < S; s++) {
			const bool vertex = (s % 2 == 0);
			auto pick = [&]() { return vertex ? ((rng() % 2) ? 1.0 : -1.0) : U(rng); };
			for (int id : ids_xy) eps[id] = pick();
			const double h = pick(), g = pick();
			double vx = sx.mid + sx.err * h, vy = sy.mid + sy.err * g;
			for (auto& p : sx.coef) vx += p.second * eps[p.first];
			for (auto& p : sy.coef) vy += p.second * eps[p.first];
			const double exact = vx * vy, tol = 1e-9 * (1.0 + fabs(exact));
			for (int m = 0; m < 2; m++) {
				double lin = zs[m]->mid;
				for (auto& p : zs[m]->coef) if (ids_xy.count(p.first)) lin += p.second * eps[p.first];
				const double excess = fabs(exact - lin) - budget[m];
				if (excess > tol) { viol_cont++; max_excess = max(max_excess, excess); }
			}
		}
	}

	printf("aa_knomial_test: %d productos Affine3 (2 a 5 variables, rayos id>=50 por sqr/productos previos), %d muestras por producto; saltados: %ld\n", T, S, saltados);
	printf("violaciones_contencion=%ld violaciones_radio=%ld diferencias_k0=%ld\n", viol_cont, viol_radio, diff_k0);
	printf("  (max exceso: %.3e; comparados con la referencia: %ld; productos con rayos nuevos en el resultado: %ld; k=3 mas estrecho que k=0 en %ld; radio k3/k0 medio = %.4f)\n",
	       max_excess, comparados, con_rayos_nuevos, tighter, ratio_n ? ratio_sum / ratio_n : 1.0);
#ifdef RAA_AA_STATS
	const KNomialStats& st = knomial_stats();
	printf("biblioteca: aa_used/aa_products = %ld/%ld (bloques extraidos: %ld en %ld llamadas)\n", st.aa_used, st.aa_products, st.blocks, st.calls);
#endif
	const bool ok = (viol_cont == 0 && viol_radio == 0 && diff_k0 == 0 && (dumping || comparados == T - saltados));
	printf("%s\n", ok ? "AA KNOMIAL OK" : "AA KNOMIAL CON PROBLEMAS");
	return ok ? 0 : 1;
}
