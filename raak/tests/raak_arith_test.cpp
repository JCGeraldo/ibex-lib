// Prueba de la aritmetica RAA-K en AF_fAF2 (prototipo).
//
// Productos x*y de formas afines aleatorias, en cada modo
// (0 = fAF2 original, 1 = simetrica termino a termino, 2 y 3 = RAA-K):
//   (a) contencion: el valor exacto del producto cae dentro de la forma resultante
//   (b) invariancia de pendientes: los coeficientes de ruido no dependen del modo
//   (c) el radio de error con modo >= 1 no supera al de fAF2 original
//   (d) filtro: si x e y comparten menos de dos simbolos de ruido, el resultado es
//       bit a bit identico al de fAF2
// Cuadrados sqr(x), modo 0 frente a modo 3: (a), (b) y (c).
// Devuelve 0 solo si todo se cumple.
#include "ibex.h"
#include "ibex_Affine.h"
#include "ibex_KNomial.h"

#include <cmath>
#include <cstdio>
#include <random>
#include <vector>

using namespace ibex;

struct Form {
	double c0;
	std::vector<double> a;
	double e;
};

static Affine2 build(const Affine2Variables& v, const Form& f) {
	int n = (int) f.a.size();
	Affine2 x = Affine2(v[0]) * 0.0;
	x = x + f.c0;
	for (int i = 0; i < n; i++)
		if (f.a[i] != 0.0) x = x + f.a[i] * Affine2(v[i]);
	if (f.e > 0.0) x = x + Interval(-f.e, f.e);
	return x;
}

static bool identical(const Affine2& p, const Affine2& q, int n) {
	if (p.is_active() != q.is_active()) return false;
	if (!p.is_active()) return true;
	if (p.noise_count() != q.noise_count() || p.mid() != q.mid() || p.err() != q.err()) return false;
	for (int i = 0; i < n && i < p.noise_count(); i++)
		if (p.noise(i) != q.noise(i)) return false;
	return true;
}

// muestra puntos (mitad vertices) y cuenta violaciones de contencion de exact(eps, hx, hy)
struct Sampler {
	std::mt19937_64& rng;
	std::uniform_real_distribution<double> U;
	explicit Sampler(std::mt19937_64& r) : rng(r), U(-1.0, 1.0) {}
	double pick(bool vertex) { return vertex ? ((rng() % 2) ? 1.0 : -1.0) : U(rng); }
};

int main() {
	const int NM = 4;
	const int modes[NM] = {0, 1, 2, 3};
	const int T = 3000;     // productos (y cuadrados)
	const int S = 200;      // puntos muestreados por forma

	std::mt19937_64 rng(2026);
	std::uniform_real_distribution<double> U(-1.0, 1.0), U01(0.0, 1.0);
	Sampler smp(rng);

	std::vector<long> violations(NM, 0), wider(NM, 0), tighter(NM, 0), ratio_count(NM, 0);
	std::vector<double> max_violation(NM, 0.0), ratio_sum(NM, 0.0), max_slope_diff(NM, 0.0);
	long filtered = 0, filter_mismatch = 0;

	long sq_tested = 0, sq_viol0 = 0, sq_viol3 = 0, sq_wider = 0, sq_tighter = 0, sq_k1_mismatch = 0;
	double sq_ratio_sum = 0.0, sq_max_viol = 0.0, sq_slope = 0.0;

	for (int t = 0; t < T; t++) {
		int n = 1 + (int) (rng() % 12);
		double pz = (rng() % 3 == 0) ? 0.7 : 0.2;   // un tercio con soportes dispersos
		Form fx, fy;
		fx.c0 = 5.0 * U(rng);
		fy.c0 = 5.0 * U(rng);
		fx.a.resize(n);
		fy.a.resize(n);
		int shared = 0;
		for (int i = 0; i < n; i++) {
			fx.a[i] = (U01(rng) < pz) ? 0.0 : 3.0 * U(rng);
			fy.a[i] = (U01(rng) < pz) ? 0.0 : 3.0 * U(rng);
			if (fx.a[i] != 0.0 && fy.a[i] != 0.0) shared++;
		}
		fx.e = (rng() % 2) ? std::fabs(U(rng)) : 0.0;
		fy.e = (rng() % 2) ? std::fabs(U(rng)) : 0.0;

		Affine2Variables v(n, Interval(-1, 1));
		Affine2 x = build(v, fx);
		Affine2 y = build(v, fy);

		// ---------------------------------------------------------------- productos
		std::vector<Affine2> res;
		for (int m = 0; m < NM; m++) {
			knomial_max_k() = modes[m];
			res.push_back(x * y);
		}
		knomial_max_k() = 0;

		if (shared < 2) {
			filtered++;
			for (int m = 1; m < NM; m++)
				if (!identical(res[m], res[0], n)) filter_mismatch++;
		}

		for (int m = 0; m < NM; m++) {
			const Affine2& r = res[m];
			if (!r.is_active() || r.noise_count() < n) continue;
			for (int s = 0; s < S; s++) {
				bool vertex = (s % 2 == 0);
				double hx = smp.pick(vertex), hy = smp.pick(vertex);
				double vx = fx.c0 + fx.e * hx, vy = fy.c0 + fy.e * hy, lin = r.mid();
				for (int i = 0; i < n; i++) {
					double ei = smp.pick(vertex);
					vx += fx.a[i] * ei;
					vy += fy.a[i] * ei;
					lin += r.noise(i) * ei;
				}
				double exact = vx * vy;
				double excess = std::fabs(exact - lin) - r.err();
				if (excess > 1e-9 * (1.0 + std::fabs(exact))) {
					violations[m]++;
					if (excess > max_violation[m]) max_violation[m] = excess;
				}
			}
			if (m == 0 || !res[0].is_active()) continue;
			for (int i = 0; i < n; i++)
				max_slope_diff[m] = std::max(max_slope_diff[m], std::fabs(r.noise(i) - res[0].noise(i)));
			double e0 = res[0].err(), em = r.err();
			if (em > e0 * (1.0 + 1e-12) + 1e-14) wider[m]++;
			if (em < e0 * (1.0 - 1e-9)) tighter[m]++;
			if (e0 > 0.0) {
				ratio_sum[m] += em / e0;
				ratio_count[m]++;
			}
		}

		// ---------------------------------------------------------------- cuadrados
		knomial_max_k() = 0;
		Affine2 s0 = sqr(x);
		knomial_max_k() = 3;
		Affine2 s3 = sqr(x);
		knomial_max_k() = 1;
		Affine2 s1 = sqr(x);
		knomial_max_k() = 0;
		if (!identical(s1, s3, n)) sq_k1_mismatch++;
		if (s0.is_active() && s3.is_active() && s0.noise_count() >= n && s3.noise_count() >= n) {
			sq_tested++;
			for (int s = 0; s < S; s++) {
				bool vertex = (s % 2 == 0);
				double hx = smp.pick(vertex);
				double vx = fx.c0 + fx.e * hx, l0 = s0.mid(), l3 = s3.mid();
				for (int i = 0; i < n; i++) {
					double ei = smp.pick(vertex);
					vx += fx.a[i] * ei;
					l0 += s0.noise(i) * ei;
					l3 += s3.noise(i) * ei;
				}
				double exact = vx * vx, tol = 1e-9 * (1.0 + exact);
				double x0 = std::fabs(exact - l0) - s0.err(), x3 = std::fabs(exact - l3) - s3.err();
				if (x0 > tol) sq_viol0++;
				if (x3 > tol) {
					sq_viol3++;
					sq_max_viol = std::max(sq_max_viol, x3);
				}
			}
			for (int i = 0; i < n; i++) sq_slope = std::max(sq_slope, std::fabs(s3.noise(i) - s0.noise(i)));
			if (s3.err() > s0.err() * (1.0 + 1e-12) + 1e-14) sq_wider++;
			if (s3.err() < s0.err() * (1.0 - 1e-9)) sq_tighter++;
			if (s0.err() > 0.0) sq_ratio_sum += s3.err() / s0.err();
		}
	}

	std::printf("PRODUCTOS: %d (n de 1 a 12, %d puntos por producto y modo)\n", T, S);
	std::printf("%-6s %-12s %-16s %-14s %-14s %-18s %s\n", "modo", "violaciones", "max violacion",
	            "radio > fAF2", "radio < fAF2", "radio/fAF2 medio", "max |dif pendiente|");
	long bad = 0;
	for (int m = 0; m < NM; m++) {
		bad += violations[m];
		if (m == 0) {
			std::printf("%-6d %-12ld %-16.3e %-14s %-14s %-18s %s\n", modes[m], violations[m], max_violation[m],
			            "-", "-", "1 (referencia)", "-");
			continue;
		}
		bad += wider[m];
		std::printf("%-6d %-12ld %-16.3e %-14ld %-14ld %-18.4f %.3e\n", modes[m], violations[m], max_violation[m],
		            wider[m], tighter[m], ratio_count[m] ? ratio_sum[m] / ratio_count[m] : 1.0, max_slope_diff[m]);
	}
	std::printf("filtro: %ld productos con menos de 2 simbolos compartidos; resultados distintos de fAF2: %ld\n",
	            filtered, filter_mismatch);
	bad += filter_mismatch;

	std::printf("\nCUADRADOS: %ld probados (modo 3 frente a modo 0)\n", sq_tested);
	std::printf("violaciones modo 0: %ld | violaciones modo 3: %ld (max %.3e) | radio > fAF2: %ld | radio < fAF2: %ld"
	            " | radio/fAF2 medio: %.4f | max |dif pendiente|: %.3e\n",
	            sq_viol0, sq_viol3, sq_max_viol, sq_wider, sq_tighter,
	            sq_tested ? sq_ratio_sum / sq_tested : 1.0, sq_slope);
	std::printf("cuadrados con modo 1 distintos de modo 3 (deben ser identicos): %ld\n", sq_k1_mismatch);
	bad += sq_viol0 + sq_viol3 + sq_wider + sq_k1_mismatch;

	std::printf("\n%s\n", bad == 0
	                          ? "ARITMETICA OK: contiene, conserva pendientes, nunca ensancha y el filtro es exacto"
	                          : "ARITMETICA CON PROBLEMAS");
	return bad == 0 ? 0 : 1;
}
