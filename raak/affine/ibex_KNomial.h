//============================================================================
//                    ibex-affine -- rama local "raak"
//
// Reduccion k-nomial SDSOS de formas cuadraticas para el prototipo de RAA-K.
// Port directo de raa_lib/knomial.py con mode='sdsos' y sign_mode='fixed'.
//
// PROTOTIPO (fase F5): aritmetica en punto flotante sin redondeo dirigido.
// La fase de rigor (F6) debe acotar formalmente el redondeo de la reescritura.
//
// C++11, solo cabecera.
//============================================================================

#ifndef __IBEX_KNOMIAL_H__
#define __IBEX_KNOMIAL_H__

#include <algorithm>
#include <cmath>
#include <deque>
#include <iterator>
#include <map>
#include <queue>
#include <set>
#include <tuple>
#include <utility>
#include <vector>

namespace ibex {

/**
 * Modo de la multiplicacion de formas afines AF_fAF2 (valor por hilo):
 *   0     multiplicacion original de fAF2 (valor por defecto)
 *   1     parte cuadratica de la RAA de [A]: productos simetrizados y linealizados termino a
 *         termino (Chebyshev en x_i^2, envolvente plana en x_i x_j) y cuadrados de formas
 *         compuestas por Chebyshev. Los errores de los factores se propagan como en fAF2
 *         (no se usa el corner test de [A]).
 *   k>=2  lo anterior + reescritura k-nomial SDSOS con cliques de hasta k variables (RAA-K)
 */
inline int& knomial_max_k() {
	static thread_local int k = 0;
	return k;
}

/** Bloque c * (u^T x)^2 de la reescritura. */
struct KNomialBlock {
	double c;
	std::vector<double> u;
};

namespace knomial_detail {

inline double sign1(double v) { return std::copysign(1.0, v); }

typedef std::pair<double, double> ParamBenefit;   // (lambda, delta_E)

// benefit(clique) de knomial.py en modo sdsos
inline ParamBenefit benefit(const std::vector<int>& clique, const std::vector<double>& Q,
                            const std::vector<double>& C, const std::vector<double>& w, int n) {
	double lam = 1.0;
	for (size_t x = 0; x < clique.size(); x++)
		for (size_t y = x + 1; y < clique.size(); y++) {
			int u = clique[x], v = clique[y];
			double cp = C[u] * C[v];
			if (cp <= 1e-12) return ParamBenefit(0.0, 0.0);
			lam = std::min(lam, std::fabs(Q[u * n + v]) / std::sqrt(cp));
		}
	double de = 0.0;
	for (size_t x = 0; x < clique.size(); x++)
		for (size_t y = x + 1; y < clique.size(); y++) {
			int u = clique[x], v = clique[y];
			de += lam * std::sqrt(C[u] * C[v]) * w[u] * w[v] / 2.0;
		}
	return ParamBenefit(lam, de);
}

// _bfs_signs de knomial.py: signos de un bloque r*(sum s_v x_v)^2 con
// s_u*s_v = sign(r*Q_uv) en toda arista. Devuelve si el clique es balanceado.
inline bool bfs_signs(const std::vector<int>& S, const std::vector<double>& Q, int n, double r,
                      std::map<int, double>& sign, double tol) {
	sign.clear();
	for (size_t a = 0; a < S.size(); a++) {
		int root = S[a];
		if (sign.count(root)) continue;
		sign[root] = 1.0;
		std::deque<int> dq(1, root);
		while (!dq.empty()) {
			int u = dq.front();
			dq.pop_front();
			for (size_t b = 0; b < S.size(); b++) {
				int v = S[b];
				if (sign.count(v) || std::fabs(Q[u * n + v]) <= tol) continue;
				sign[v] = sign[u] * sign1(r * Q[u * n + v]);
				dq.push_back(v);
			}
		}
	}
	bool ok = true;
	for (size_t a = 0; a < S.size(); a++)
		for (size_t b = a + 1; b < S.size(); b++) {
			int u = S[a], v = S[b];
			if (std::fabs(Q[u * n + v]) > tol && sign[u] * sign[v] != sign1(r * Q[u * n + v]))
				ok = false;
		}
	return ok;
}

inline std::set<int> intersect(const std::set<int>& a, const std::set<int>& b) {
	std::set<int> out;
	std::set_intersection(a.begin(), a.end(), b.begin(), b.end(), std::inserter(out, out.begin()));
	return out;
}

} // namespace knomial_detail

/**
 * Reescribe x^T Q x como x^T Q_res x + sum_k c_k (u_k^T x)^2.
 *
 * Q (n*n, por filas) entra como la matriz original y sale como Q_res.
 * w: anchos de las variables (en coordenadas de ruido de AF2 todos valen 2).
 * Devuelve el numero de cliques no balanceados que se degradaron al par base
 * (con sign_mode='fixed' debe ser siempre 0).
 */
inline int knomial_rewrite(std::vector<double>& Q, const std::vector<double>& w, int n, int max_k,
                           std::vector<KNomialBlock>& blocks, double tol = 1e-12) {
	using namespace knomial_detail;
	blocks.clear();
	if (n <= 0) return 0;
	{
		std::vector<double> S(Q);
		for (int i = 0; i < n; i++)
			for (int j = 0; j < n; j++)
				Q[i * n + j] = 0.5 * (S[i * n + j] + S[j * n + i]);
	}
	if (max_k < 2) return 0;

	std::vector<double> C(n), rvec(n);
	std::vector<char> P(n), N(n);
	for (int i = 0; i < n; i++) {
		double d = Q[i * n + i];
		C[i] = std::fabs(d);
		P[i] = d > 0;
		N[i] = d < 0;
		rvec[i] = P[i] ? 1.0 : (N[i] ? -1.0 : 0.0);
	}

	std::vector<std::set<int> > adj(n);
	for (int i = 0; i < n; i++)
		for (int j = i + 1; j < n; j++)
			if (Q[i * n + j] != 0 && ((P[i] && P[j]) || (N[i] && N[j]))) {
				adj[i].insert(j);
				adj[j].insert(i);
			}

	// (delta_E, -i, -j) en un max-heap reproduce el orden de heapq con (-delta_E, i, j)
	typedef std::tuple<double, int, int> HeapItem;
	std::priority_queue<HeapItem> heap;
	for (int i = 0; i < n; i++)
		for (std::set<int>::const_iterator it = adj[i].begin(); it != adj[i].end(); ++it) {
			int j = *it;
			if (j > i) {
				std::vector<int> pr(2);
				pr[0] = i;
				pr[1] = j;
				double de = benefit(pr, Q, C, w, n).second;
				if (de > 1e-12) heap.push(HeapItem(de, -i, -j));
			}
		}

	struct Item {
		std::vector<int> clique;
		std::set<int> cands;
		std::map<int, double> sg;
	};

	int n_infeasible = 0;
	int guard = 0;
	const int max_iter = 200 * std::max(1, n * n);
	while (!heap.empty() && guard < max_iter) {
		guard++;
		HeapItem top = heap.top();
		heap.pop();
		double prev = std::get<0>(top);
		int bi = -std::get<1>(top), bj = -std::get<2>(top);
		if (!adj[bi].count(bj)) continue;

		std::vector<int> base(2);
		base[0] = bi;
		base[1] = bj;
		ParamBenefit pb = benefit(base, Q, C, w, n);
		double p_ij = pb.first, de_ij = pb.second;
		if (de_ij < prev - 1e-9) {
			if (de_ij > 1e-12) heap.push(HeapItem(de_ij, -bi, -bj));
			continue;
		}
		if (de_ij <= 1e-12) continue;

		double r = rvec[bi];
		std::vector<int> best_clique = base;
		double best_de = de_ij, best_p = p_ij;

		// busqueda en profundidad de cliques balanceados de hasta max_k variables
		std::vector<Item> stack;
		Item root;
		root.clique = base;
		root.cands = intersect(adj[bi], adj[bj]);
		root.sg[bi] = 1.0;
		root.sg[bj] = sign1(r * Q[bi * n + bj]);
		stack.push_back(root);
		while (!stack.empty()) {
			Item cur = stack.back();
			stack.pop_back();
			ParamBenefit pc = benefit(cur.clique, Q, C, w, n);
			if (pc.second > best_de && pc.first > 1e-12) {
				best_de = pc.second;
				best_clique = cur.clique;
				best_p = pc.first;
			}
			if ((int) cur.clique.size() < max_k) {
				for (std::set<int>::const_iterator it = cur.cands.begin(); it != cur.cands.end(); ++it) {
					int v = *it;
					double s_v = cur.sg[bi] * sign1(r * Q[bi * n + v]);
					bool ok = true;
					for (size_t t = 0; t < cur.clique.size(); t++) {
						int u = cur.clique[t];
						if (u != bi && sign1(r * Q[u * n + v]) != cur.sg[u] * s_v) {
							ok = false;
							break;
						}
					}
					if (ok) {
						Item nx;
						nx.clique = cur.clique;
						nx.clique.push_back(v);
						nx.cands = intersect(cur.cands, adj[v]);
						nx.sg = cur.sg;
						nx.sg[v] = s_v;
						stack.push_back(nx);
					}
				}
			}
		}

		std::vector<int> clique = best_clique;
		double p = best_p;
		std::map<int, double> C_loc;
		for (size_t t = 0; t < clique.size(); t++) C_loc[clique[t]] = C[clique[t]];

		std::map<int, double> signs;
		if (!bfs_signs(clique, Q, n, r, signs, tol)) {
			// clique no balanceado: degradar al par base, que siempre lo es
			n_infeasible++;
			clique = base;
			p = p_ij;
			C_loc.clear();
			for (size_t t = 0; t < clique.size(); t++) C_loc[clique[t]] = C[clique[t]];
			bfs_signs(clique, Q, n, r, signs, tol);
		}

		double lam = p;
		if (lam <= 1e-12) continue;

		KNomialBlock blk;
		blk.c = r;
		blk.u.assign(n, 0.0);
		for (size_t t = 0; t < clique.size(); t++) {
			int v = clique[t];
			blk.u[v] = signs[v] * std::sqrt(lam * C_loc[v]);
		}
		for (size_t t = 0; t < clique.size(); t++) {
			int v = clique[t];
			C[v] = std::max(0.0, C[v] * (1.0 - lam));
		}
		blocks.push_back(blk);

		for (size_t x = 0; x < clique.size(); x++)
			for (size_t y = x + 1; y < clique.size(); y++) {
				int uu = clique[x], vv = clique[y];
				double s = sign1(Q[uu * n + vv]);
				double ext = p * std::sqrt(C_loc[uu] * C_loc[vv]);
				double nv = std::max(0.0, std::fabs(Q[uu * n + vv]) - ext);
				Q[uu * n + vv] = s * nv;
				Q[vv * n + uu] = Q[uu * n + vv];
				if (nv < 1e-12) {
					adj[uu].erase(vv);
					adj[vv].erase(uu);
				}
			}

		if (std::fabs(Q[bi * n + bj]) > 1e-12) heap.push(HeapItem(de_ij, -bi, -bj));
	}

	for (int k = 0; k < n; k++)
		Q[k * n + k] = P[k] ? C[k] : (N[k] ? -C[k] : 0.0);
	return n_infeasible;
}

/** Contadores por hilo de la multiplicacion con modo >= 1 (diagnostico del prototipo). */
struct KNomialStats {
	long products;           // productos de formas activas no degeneradas con modo >= 1
	long calls;              // productos que pasaron el filtro y llegaron a knomial_quad_bound
	long calls_with_blocks;  // productos en los que la reescritura extrajo al menos un bloque
	long blocks;             // bloques extraidos en total
	long calls_used;         // productos en los que la cota k-nomial reemplazo a la de fAF2
	double rad_faf2;         // suma del radio cuadratico de fAF2 (Sx*Sy - Sxy/2) en los evaluados
	double rad_used;         // suma del radio cuadratico k-nomial en los evaluados
	long sqr_products;       // cuadrados con modo >= 1
	long sqr_used;           // cuadrados en los que la cota de un solo bloque reemplazo a la de fAF2
};

inline KNomialStats& knomial_stats() {
	static thread_local KNomialStats s = {0, 0, 0, 0, 0, 0.0, 0.0, 0, 0};
	return s;
}

/**
 * Cota de la parte cuadratica eps^T Q eps, con Q = (x y^T + y x^T)/2 y eps en
 * [-1,1]^n (coordenadas de ruido de AF2). En 'shift' devuelve lo que se suma al
 * centro y en 'rad' el radio de error:
 *   - bloque c (u^T eps)^2, con s = sum|u_i|: rango [0, s^2]  -> centro c s^2/2,  radio |c| s^2/2
 *   - diagonal residual Q_ii eps_i^2 en Q_ii [0,1]           -> centro Q_ii/2,   radio |Q_ii|/2
 *   - cruce residual 2 Q_ij eps_i eps_j (i < j)               -> radio 2|Q_ij|
 * Mas un margen por la discrepancia en punto flotante de Q = Q_res + sum c u u^T
 * (prototipo: no es una cota rigurosa del redondeo).
 * Con max_k < 2 no hay reescritura: es la forma simetrica termino a termino.
 * Devuelve el numero de bloques extraidos.
 */
inline int knomial_quad_bound(const std::vector<double>& x_all, const std::vector<double>& y_all, int n_all,
                              int max_k, double& shift, double& rad) {
	// Solo entran los simbolos de ruido presentes en x o en y: las filas nulas de Q no
	// generan aristas ni bloques, y comprimir conserva el orden de desempate de knomial.
	std::vector<double> xc, yc;
	double Sx = 0.0, Sy = 0.0, Sxy = 0.0;
	for (int i = 0; i < n_all; i++) {
		Sx += std::fabs(x_all[i]);
		Sy += std::fabs(y_all[i]);
		Sxy += std::fabs(x_all[i] * y_all[i]);
		if (x_all[i] != 0.0 || y_all[i] != 0.0) {
			xc.push_back(x_all[i]);
			yc.push_back(y_all[i]);
		}
	}
	int n = (int) xc.size();
	std::vector<double> Q(n * n);
	for (int i = 0; i < n; i++)
		for (int j = 0; j < n; j++)
			Q[i * n + j] = 0.5 * (xc[i] * yc[j] + xc[j] * yc[i]);
	std::vector<double> Q0(Q);

	std::vector<KNomialBlock> blocks;
	std::vector<double> w(n, 2.0);
	if (max_k >= 2) knomial_rewrite(Q, w, n, max_k, blocks);

	shift = 0.0;
	rad = 0.0;
	for (size_t b = 0; b < blocks.size(); b++) {
		double s = 0.0;
		for (int i = 0; i < n; i++) s += std::fabs(blocks[b].u[i]);
		double sq = s * s;
		shift += blocks[b].c * sq / 2.0;
		rad += std::fabs(blocks[b].c) * sq / 2.0;
	}
	for (int i = 0; i < n; i++) {
		shift += Q[i * n + i] / 2.0;
		rad += std::fabs(Q[i * n + i]) / 2.0;
		for (int j = i + 1; j < n; j++) rad += 2.0 * std::fabs(Q[i * n + j]);
	}

	double disc = 0.0;
	for (int i = 0; i < n; i++)
		for (int j = i; j < n; j++) {
			double d = Q0[i * n + j] - Q[i * n + j];
			for (size_t b = 0; b < blocks.size(); b++) d -= blocks[b].c * blocks[b].u[i] * blocks[b].u[j];
			disc += (i == j ? 1.0 : 2.0) * std::fabs(d);
		}
	rad += disc;

	KNomialStats& st = knomial_stats();
	st.calls++;
	if (!blocks.empty()) st.calls_with_blocks++;
	st.blocks += (long) blocks.size();
	st.rad_faf2 += Sx * Sy - 0.5 * Sxy;
	st.rad_used += rad;
	return (int) blocks.size();
}

} // namespace ibex

#endif // __IBEX_KNOMIAL_H__
