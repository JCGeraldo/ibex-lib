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
#include <list>
#include <map>
#include <queue>
#include <set>
#include <tuple>
#include <utility>
#include <vector>

namespace ibex {

/**
 * [raak local] Dos interruptores independientes, ambos por hilo (Fase 1, parche 0004):
 *
 *   affine_mode()   AFFINE_AF2 (por defecto) o AFFINE_RAA. Solo afecta a AffineMain<AF_fAF2>.
 *   knomial_max_k() 0 (por defecto) = sin reescritura k-nomial; k>=2 = reescritura SDSOS con
 *                   cliques de hasta k variables. El valor 1 ya no es un modo: su significado
 *                   anterior (parte cuadratica de la RAA de [A]) es ahora AFFINE_RAA con k=0.
 *
 *   Aritmetica  k-nomial  Productos (operator*=)              Asqr compuestas   Errores factores
 *   AF2  k=0    no        fAF2 original (bit a bit)           fAF2              fAF2
 *   AF2  k>=2   si        knomial_quad_bound con bloques;     fAF2              fAF2
 *                         residuo termino a termino (Lemma 3
 *                         de [A]); solo si mejora a fAF2
 *   RAA  k=0    no        forma simetrica termino a termino   Chebyshev         corner test (0005)
 *                         (= knomial_quad_bound con max_k<2)  [0,(Sx+e)^2]
 *   RAA  k>=2   si        knomial_quad_bound con bloques      Chebyshev         corner test (0005)
 *   AA   k=0    no        AF_fAFFullI original (bit a bit)    Chebyshev (ya)    rayo nuevo
 *   AA   k>=2   si        ruta simetrica sobre la union de    Chebyshev         rayo nuevo
 *                         rayos (parche 0006)
 *
 * Equivalencias con los modos del prototipo (bit a bit): raak_k=0 == AF2/k=0;
 * raak_k=1 == RAA/k=0 (antes del corner test); raak_k=3 == RAA/k=3 (antes del corner test).
 */
inline int& knomial_max_k() {
	static thread_local int k = 0;
	return k;
}

enum AffineMode { AFFINE_AF2 = 0, AFFINE_RAA = 1 };

inline AffineMode& affine_mode() {
	static thread_local AffineMode m = AFFINE_AF2;
	return m;
}

/**
 * [raak local] Corner test de la Ec. (16) de [A] en coordenadas de ruido (parche 0005).
 *
 * Para x = x0 + a^T eps + ex h, y = y0 + b^T eps + ey g (h, g en [-1,1]) los cruces de los errores
 * con las partes lineales son ey g (a^T eps) + ex h (b^T eps). Maximizando en eps queda
 * sum_i |ey g a_i + ex h b_i|, convexa en (h, g): el maximo esta en una esquina de [-1,1]^2.
 * Como |-z| = |z|, la esquina (-s1,-s2) vale lo mismo que (s1,s2): bastan (+,+) y (+,-).
 * fAF2 usa ex Sy + Sx ey, que siempre es >= por la desigualdad triangular.
 *
 * Devuelve max_{s} sum_i |ey a_i + s ex b_i| mayorado por el redondeo: cada termino tiene 2
 * productos y 1 suma, y la acumulacion n sumas; con un factor (1 + 2 em) por operacion (patron
 * de ibex_Affine2_fAF2.cpp, em = AF_EM) se usa (1+2em)^3 (1 + 4 em n) >= (1+2em)^(n+3), valido
 * mientras 2 em n <= 1. No incluye el termino ex*ey (lo suma el llamador). Mayorante razonado,
 * no riguroso en el sentido de F6.
 */
inline double raa_corner_cross(const std::vector<double>& a, const std::vector<double>& b,
                               double ex, double ey, double em) {
	const size_t n = std::min(a.size(), b.size());
	double corner_pp = 0.0, corner_pm = 0.0;
	for (size_t i = 0; i < n; i++) {
		const double p = ey * a[i], q = ex * b[i];
		corner_pp += std::fabs(p + q);
		corner_pm += std::fabs(p - q);
	}
	const double f = (1 + 2*em) * (1 + 2*em) * (1 + 2*em) * (1 + 4*em*(double) n);
	return f * std::max(corner_pp, corner_pm);
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

/** Contadores por hilo de la cota cuadratica alternativa (RAA o k>=2; diagnostico del prototipo). */
struct KNomialStats {
	long products;           // productos de formas activas no degeneradas con RAA o k>=2
	long calls;              // productos que pasaron el filtro y llegaron a knomial_quad_bound
	long calls_with_blocks;  // productos en los que la reescritura extrajo al menos un bloque
	long blocks;             // bloques extraidos en total
	long calls_used;         // productos en los que la cota k-nomial reemplazo a la de fAF2
	double rad_faf2;         // suma del radio cuadratico de fAF2 (Sx*Sy - Sxy/2) en los evaluados
	double rad_used;         // suma del radio cuadratico k-nomial en los evaluados
	long sqr_products;       // cuadrados de formas compuestas con AFFINE_RAA
	long sqr_used;           // cuadrados en los que la cota de un solo bloque reemplazo a la de fAF2
	long corner_products;    // productos con AFFINE_RAA y algun factor con error (candidatos al corner test)
	long corner_used;        // productos en los que el corner test reemplazo a ex*Sy + Sx*ey
	double cross_faf2;       // suma de ex*Sy + Sx*ey en los candidatos
	double cross_corner;     // suma del termino de cruces usado (corner o fAF2) en los candidatos
	long aa_products;        // productos AF_fAFFullI de formas compuestas con k>=2 (parche 0006)
	long aa_used;            // productos AF_fAFFullI en los que la cota k-nomial reemplazo a rad(x)*rad(y)
};

inline KNomialStats& knomial_stats() {
	static thread_local KNomialStats s = {0, 0, 0, 0, 0, 0.0, 0.0, 0, 0, 0, 0, 0.0, 0.0, 0, 0};
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

/**
 * [raak local] Version dispersa para AF_fAFFullI (parche 0006). rx, ry son listas de pares
 * (id de simbolo, coeficiente) ordenadas por id creciente, como _rays. Se construye la union
 * ordenada de ids, se forman qx, qy densos sobre ella y se llama a knomial_quad_bound: en
 * Affine3 cada rayo tambien es coeficiente * eps_id con eps_id en [-1,1], asi que la cota de la
 * parte cuadratica (a^T eps)(b^T eps) es la misma. Plantilla sobre el tipo del id (af3_int) para
 * que esta cabecera siga sin depender de ibex_Affine3_fAFFullI.h.
 */
template<class Id>
inline int knomial_quad_bound_sparse(const std::list<std::pair<Id, double> >& rx,
                                     const std::list<std::pair<Id, double> >& ry,
                                     int max_k, double& shift, double& rad) {
	std::vector<double> qx, qy;
	typename std::list<std::pair<Id, double> >::const_iterator ix = rx.begin(), iy = ry.begin();
	while (ix != rx.end() || iy != ry.end()) {
		if (iy == ry.end() || (ix != rx.end() && ix->first < iy->first)) {
			qx.push_back(ix->second); qy.push_back(0.0); ++ix;
		} else if (ix == rx.end() || iy->first < ix->first) {
			qx.push_back(0.0); qy.push_back(iy->second); ++iy;
		} else {
			qx.push_back(ix->second); qy.push_back(iy->second); ++ix; ++iy;
		}
	}
	return knomial_quad_bound(qx, qy, (int) qx.size(), max_k, shift, rad);
}

} // namespace ibex

#endif // __IBEX_KNOMIAL_H__
