//============================================================================
//                    ibex-affine -- rama local "raak"
//
// Reduccion k-nomial SDSOS de formas cuadraticas para RAA-K.
// La busqueda de bloques (knomial_rewrite) es un port de raa_lib/knomial.py con mode='sdsos' y
// sign_mode='fixed', en dobles: es una heuristica y solo decide la anchura de la cota.
//
// RIGOR (parches 0012 y 0013, noviembre de 2026): la cota de knomial_quad_bound es conservativa en
// punto flotante. Teorema: para bloques (c_b, u_b) cualesquiera,
//     eps^T Q eps = sum_b c_b (u_b^T eps)^2 + eps^T R eps,  R = Q - sum_b c_b u_b u_b^T,
// y el residuo se calcula con coeficientes intervalares (redondeo hacia fuera), de modo que todo el
// error de redondeo queda dentro de [R]. No hay margenes heuristicos (los antiguos 'disc' y 'qmargin').
// Comprobado sin tolerancia con tests/knomial_lemma_check.cpp y tests/affine_containment_check.cpp (raak).
//
// Opciones por hilo: knomial_max_k() (tope k del bloque), knomial_node_budget() (presupuesto de la
// busqueda, 0 = sin limite), knomial_bound_mode() (0 = ibex::Interval, 1 = dobles con redondeo dirigido).
//
// C++11, solo cabecera. Parche 0009: sin reservas de memoria por llamada (buffers por hilo).
// Parche 0011: cada clique se enumera una sola vez y la busqueda admite presupuesto de nodos.
//============================================================================

#ifndef __IBEX_KNOMIAL_H__
#define __IBEX_KNOMIAL_H__

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <list>
#include <tuple>
#include <utility>
#include <vector>
#include "ibex_Interval.h"
#include <cfenv>

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
 * Parche 0011: presupuesto de nodos de la busqueda de cliques por producto (0 = sin limite).
 * Se lee una vez por hilo de la variable de entorno RAAK_NODE_BUDGET. Cuando se agota, los
 * nodos pendientes se evaluan pero no se extienden, asi que el resultado sigue siendo un clique
 * balanceado valido (solo deja de ser el optimo entre los de hasta k simbolos).
 */
/**
 * Parche 0013: modo de calculo de la cota rigurosa de knomial_quad_bound, por hilo, leido una vez de la
 * variable de entorno RAAK_BOUND_MODE: "interval" (0, por defecto) usa ibex::Interval (parche 0012);
 * "directed" (1) usa dobles con redondeo dirigido hacia +inf (fesetround(FE_UPWARD)) y el truco de
 * signo para los extremos inferiores, -up((-a)*b). Misma matematica, sin objetos ni comprobaciones
 * de Gaol. Nota: con Gaol el procesador ya esta en FE_UPWARD de forma permanente; se fija y se restaura
 * igualmente para no depender de ello.
 */
inline int& knomial_bound_mode() {
	static thread_local int m = -1;
	if (m < 0) {
		const char* e = std::getenv("RAAK_BOUND_MODE");
		m = (e && (e[0] == 'd' || e[0] == 'D' || e[0] == '1')) ? 1 : 0;
	}
	return m;
}

inline long& knomial_node_budget() {
	static thread_local long b = -1;
	if (b < 0) {
		const char* e = std::getenv("RAAK_NODE_BUDGET");
		b = e ? std::atol(e) : 0;
		if (b < 0) b = 0;
	}
	return b;
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
 * mientras 2 em n <= 1. No incluye el termino ex*ey (lo suma el llamador). Es el mismo esquema de
 * mayoracion por factores (1 + 2 em) que usa fAF2 en todo el producto. Comprobado sin tolerancia con
 * tests/affine_containment_check.cpp (raak, 10-11-2026): 0 violaciones seguras en 3.6 millones de
 * evaluaciones de funciones que ejercitan el corner test, el cuadrado de Chebyshev y sin/cos/exp/ln.
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

// benefit(clique) de knomial.py en modo sdsos. Parche 0009: recibe puntero y tamano para no
// construir vectores temporales (la aritmetica es la misma, en el mismo orden).
inline ParamBenefit benefit(const int* clique, size_t m, const std::vector<double>& Q,
                            const std::vector<double>& C, const std::vector<double>& w, int n) {
	double lam = 1.0;
	for (size_t x = 0; x < m; x++)
		for (size_t y = x + 1; y < m; y++) {
			int u = clique[x], v = clique[y];
			double cp = C[u] * C[v];
			if (cp <= 1e-12) return ParamBenefit(0.0, 0.0);
			lam = std::min(lam, std::fabs(Q[u * n + v]) / std::sqrt(cp));
		}
	double de = 0.0;
	for (size_t x = 0; x < m; x++)
		for (size_t y = x + 1; y < m; y++) {
			int u = clique[x], v = clique[y];
			de += lam * std::sqrt(C[u] * C[v]) * w[u] * w[v] / 2.0;
		}
	return ParamBenefit(lam, de);
}

inline ParamBenefit benefit(const std::vector<int>& clique, const std::vector<double>& Q,
                            const std::vector<double>& C, const std::vector<double>& w, int n) {
	return benefit(clique.empty() ? nullptr : &clique[0], clique.size(), Q, C, w, n);
}

// _bfs_signs de knomial.py: signos de un bloque r*(sum s_v x_v)^2 con
// s_u*s_v = sign(r*Q_uv) en toda arista. Devuelve si el clique es balanceado.
// Parche 0009: 'sign' y 'seen' son vectores indexados por simbolo (tamano >= n) y 'dq' la cola,
// todos reutilizados por el llamador; sustituyen al std::map y al std::deque, con el mismo orden
// de visita (los miembros de S en orden, cola FIFO).
inline bool bfs_signs(const int* S, size_t m, const std::vector<double>& Q, int n, double r,
                      std::vector<double>& sign, std::vector<char>& seen, std::vector<int>& dq, double tol) {
	for (size_t a = 0; a < m; a++) seen[S[a]] = 0;
	for (size_t a = 0; a < m; a++) {
		int root = S[a];
		if (seen[root]) continue;
		seen[root] = 1;
		sign[root] = 1.0;
		dq.clear();
		dq.push_back(root);
		for (size_t h = 0; h < dq.size(); h++) {
			int u = dq[h];
			for (size_t b = 0; b < m; b++) {
				int v = S[b];
				if (seen[v] || std::fabs(Q[u * n + v]) <= tol) continue;
				seen[v] = 1;
				sign[v] = sign[u] * sign1(r * Q[u * n + v]);
				dq.push_back(v);
			}
		}
	}
	bool ok = true;
	for (size_t a = 0; a < m; a++)
		for (size_t b = a + 1; b < m; b++) {
			int u = S[a], v = S[b];
			if (std::fabs(Q[u * n + v]) > tol && sign[u] * sign[v] != sign1(r * Q[u * n + v]))
				ok = false;
		}
	return ok;
}

// Nodo de la busqueda en profundidad de cliques. 'sg' va alineado con 'clique' (signo de la
// posicion t), 'cands' es una lista ordenada creciente (lo que antes era un std::set).
struct DfsItem {
	std::vector<int> clique;
	std::vector<int> cands;
	std::vector<double> sg;
};

// (delta_E, -i, -j) en un max-heap reproduce el orden de heapq con (-delta_E, i, j)
typedef std::tuple<double, int, int> HeapItem;

// Buffers por hilo de knomial_rewrite (parche 0009): evitan las reservas de memoria por llamada.
// La reescritura se invoca en cada producto de formas afines; con std::set/std::map por nodo de la
// busqueda, las reservas eran ~3/4 del tiempo de la funcion (perf, 28-10-2026).
struct RewriteBuf {
	std::vector<double> C, rvec, sign, Cloc;
	std::vector<char> P, N, A, seen;
	std::vector<int> dq, best, cl;
	std::vector<HeapItem> heap;
	std::vector<DfsItem> stack;
	DfsItem cur;
};

inline RewriteBuf& rewrite_buf() {
	static thread_local RewriteBuf b;
	return b;
}

} // namespace knomial_detail

/**
 * Reescribe x^T Q x como x^T Q_res x + sum_k c_k (u_k^T x)^2.
 *
 * Q (n*n, por filas) entra como la matriz original y sale como Q_res.
 * w: anchos de las variables (en coordenadas de ruido de AF2 todos valen 2).
 * Devuelve el numero de cliques no balanceados que se degradaron al par base
 * (con sign_mode='fixed' debe ser siempre 0).
 *
 * Parche 0009: misma busqueda y misma aritmetica que la version con std::set/std::map/std::deque
 * (bit a bit: knomial_golden y el nivel 1 dan los mismos bloques y anchuras), pero con adyacencia
 * densa (A, n*n), candidatos en vectores ordenados, signos por posicion del clique, monticulo sobre
 * un vector con std::push_heap/pop_heap (lo que hace std::priority_queue por dentro) y todos los
 * buffers reutilizados por hilo. El benefit del nodo raiz de la busqueda no se recalcula: es
 * exactamente benefit(base), ya calculado, y no puede superar best_de.
 */
inline int knomial_rewrite(std::vector<double>& Q, const std::vector<double>& w, int n, int max_k,
                           std::vector<KNomialBlock>& blocks, double tol = 1e-12) {
	using namespace knomial_detail;
	blocks.clear();
	if (n <= 0) return 0;
	// simetrizacion en sitio: 0.5*(S_ij + S_ji) en ambas posiciones (la suma es conmutativa)
	for (int i = 0; i < n; i++) {
		Q[i * n + i] = 0.5 * (Q[i * n + i] + Q[i * n + i]);
		for (int j = i + 1; j < n; j++) {
			double v = 0.5 * (Q[i * n + j] + Q[j * n + i]);
			Q[i * n + j] = v;
			Q[j * n + i] = v;
		}
	}
	if (max_k < 2) return 0;

	RewriteBuf& B = rewrite_buf();
	std::vector<double>& C = B.C;
	std::vector<double>& rvec = B.rvec;
	std::vector<char>& P = B.P;
	std::vector<char>& N = B.N;
	std::vector<char>& A = B.A;
	C.resize(n); rvec.resize(n); P.resize(n); N.resize(n);
	B.sign.resize(n); B.seen.resize(n);
	for (int i = 0; i < n; i++) {
		double d = Q[i * n + i];
		C[i] = std::fabs(d);
		P[i] = d > 0;
		N[i] = d < 0;
		rvec[i] = P[i] ? 1.0 : (N[i] ? -1.0 : 0.0);
	}

	A.assign((size_t) n * n, 0);
	for (int i = 0; i < n; i++)
		for (int j = i + 1; j < n; j++)
			if (Q[i * n + j] != 0 && ((P[i] && P[j]) || (N[i] && N[j]))) {
				A[i * n + j] = 1;
				A[j * n + i] = 1;
			}

	std::vector<HeapItem>& heap = B.heap;
	heap.clear();
	for (int i = 0; i < n; i++)
		for (int j = i + 1; j < n; j++)
			if (A[i * n + j]) {
				int pr[2] = {i, j};
				double de = benefit(pr, 2, Q, C, w, n).second;
				if (de > 1e-12) {
					heap.push_back(HeapItem(de, -i, -j));
					std::push_heap(heap.begin(), heap.end());
				}
			}

	std::vector<DfsItem>& stack = B.stack;
	DfsItem& cur = B.cur;
	std::vector<int>& best_clique = B.best;
	std::vector<int>& clique = B.cl;
	std::vector<double>& C_loc = B.Cloc;
	std::vector<double>& signs = B.sign;

	int n_infeasible = 0;
	int guard = 0;
	const int max_iter = 200 * std::max(1, n * n);
	long dfs_nodes = 0;
	const long budget = knomial_node_budget();
	while (!heap.empty() && guard < max_iter) {
		guard++;
		HeapItem top = heap.front();
		std::pop_heap(heap.begin(), heap.end());
		heap.pop_back();
		double prev = std::get<0>(top);
		int bi = -std::get<1>(top), bj = -std::get<2>(top);
		if (!A[bi * n + bj]) continue;

		int base[2] = {bi, bj};
		ParamBenefit pb = benefit(base, 2, Q, C, w, n);
		double p_ij = pb.first, de_ij = pb.second;
		if (de_ij < prev - 1e-9) {
			if (de_ij > 1e-12) {
				heap.push_back(HeapItem(de_ij, -bi, -bj));
				std::push_heap(heap.begin(), heap.end());
			}
			continue;
		}
		if (de_ij <= 1e-12) continue;

		double r = rvec[bi];
		best_clique.assign(base, base + 2);
		double best_de = de_ij, best_p = p_ij;

		// busqueda en profundidad de cliques balanceados de hasta max_k variables
		size_t sp = 0;
		if (stack.empty()) stack.resize(1);
		{
			DfsItem& root = stack[sp++];
			root.clique.assign(base, base + 2);
			root.cands.clear();
			for (int v = 0; v < n; v++)
				if (A[bi * n + v] && A[bj * n + v]) root.cands.push_back(v);
			root.sg.resize(2);
			root.sg[0] = 1.0;
			root.sg[1] = sign1(r * Q[bi * n + bj]);
		}
		bool is_root = true;
		while (sp > 0) {
			std::swap(cur, stack[--sp]);
			dfs_nodes++;
			if (!is_root) {
				ParamBenefit pc = benefit(&cur.clique[0], cur.clique.size(), Q, C, w, n);
				if (pc.second > best_de && pc.first > 1e-12) {
					best_de = pc.second;
					best_clique = cur.clique;
					best_p = pc.first;
				}
			}
			is_root = false;
			// Parche 0011: cada clique se enumera una sola vez. La DFS saca primero el candidato
			// mayor, asi que la primera secuencia con la que se alcanzaba cada conjunto era la
			// descendente; se conserva esa (v < ultimo agregado) y se descartan las permutaciones,
			// con lo que los valores de benefit y el orden de descubrimiento son los de antes.
			// Con presupuesto agotado no se extiende ningun nodo mas.
			bool extend = (int) cur.clique.size() < max_k
			              && (budget == 0 || dfs_nodes < budget);
			if (extend) {
				int last = cur.clique.size() > 2 ? cur.clique.back() : n;
				for (size_t ci = 0; ci < cur.cands.size(); ci++) {
					int v = cur.cands[ci];
					if (v >= last) continue;
					double s_v = cur.sg[0] * sign1(r * Q[bi * n + v]);
					bool ok = true;
					for (size_t t = 1; t < cur.clique.size(); t++) {   // t = 0 es bi
						int u = cur.clique[t];
						if (sign1(r * Q[u * n + v]) != cur.sg[t] * s_v) {
							ok = false;
							break;
						}
					}
					if (ok) {
						if (sp == stack.size()) stack.resize(sp + 1);
						DfsItem& nx = stack[sp++];
						nx.clique.assign(cur.clique.begin(), cur.clique.end());
						nx.clique.push_back(v);
						nx.cands.clear();
						for (size_t cj = 0; cj < cur.cands.size(); cj++)
							if (A[v * n + cur.cands[cj]]) nx.cands.push_back(cur.cands[cj]);
						nx.sg.assign(cur.sg.begin(), cur.sg.end());
						nx.sg.push_back(s_v);
					}
				}
			}
		}

		clique = best_clique;
		double p = best_p;
		C_loc.resize(clique.size());
		for (size_t t = 0; t < clique.size(); t++) C_loc[t] = C[clique[t]];

		if (!bfs_signs(&clique[0], clique.size(), Q, n, r, signs, B.seen, B.dq, tol)) {
			// clique no balanceado: degradar al par base, que siempre lo es
			n_infeasible++;
			clique.assign(base, base + 2);
			p = p_ij;
			C_loc.resize(clique.size());
			for (size_t t = 0; t < clique.size(); t++) C_loc[t] = C[clique[t]];
			bfs_signs(&clique[0], clique.size(), Q, n, r, signs, B.seen, B.dq, tol);
		}

		double lam = p;
		if (lam <= 1e-12) continue;

		blocks.push_back(KNomialBlock());
		KNomialBlock& blk = blocks.back();
		blk.c = r;
		blk.u.assign(n, 0.0);
		for (size_t t = 0; t < clique.size(); t++) {
			int v = clique[t];
			blk.u[v] = signs[v] * std::sqrt(lam * C_loc[t]);
		}
		for (size_t t = 0; t < clique.size(); t++) {
			int v = clique[t];
			C[v] = std::max(0.0, C[v] * (1.0 - lam));
		}

		for (size_t x = 0; x < clique.size(); x++)
			for (size_t y = x + 1; y < clique.size(); y++) {
				int uu = clique[x], vv = clique[y];
				double s = sign1(Q[uu * n + vv]);
				double ext = p * std::sqrt(C_loc[x] * C_loc[y]);
				double nv = std::max(0.0, std::fabs(Q[uu * n + vv]) - ext);
				Q[uu * n + vv] = s * nv;
				Q[vv * n + uu] = Q[uu * n + vv];
				if (nv < 1e-12) {
					A[uu * n + vv] = 0;
					A[vv * n + uu] = 0;
				}
			}

		if (std::fabs(Q[bi * n + bj]) > 1e-12) {
			heap.push_back(HeapItem(de_ij, -bi, -bj));
			std::push_heap(heap.begin(), heap.end());
		}
	}

	for (int k = 0; k < n; k++)
		Q[k * n + k] = P[k] ? C[k] : (N[k] ? -C[k] : 0.0);
	return n_infeasible;
}

/** Contadores por hilo de la cota cuadratica alternativa (RAA o k>=2; diagnostico). */
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
	long blocks_by_size[6];  // [raak local, 0010] bloques extraidos por tamano de clique: indice 0 = 2 simbolos, ..., 5 = 7 o mas
};

inline KNomialStats& knomial_stats() {
	static thread_local KNomialStats s = {0, 0, 0, 0, 0, 0.0, 0.0, 0, 0, 0, 0, 0.0, 0.0, 0, 0};
	return s;
}

/**
 * Cota de la parte cuadratica eps^T Q eps, con Q = (x y^T + y x^T)/2 y eps en
 * [-1,1]^n (coordenadas de ruido de AF2). En 'shift' devuelve lo que se suma al
 * centro y en 'rad' el radio de error, con [shift - rad, shift + rad] (como reales)
 * conteniendo el rango de eps^T Q eps para todo eps.
 *
 * Parche 0012 (lema de conservatividad, 08-11-2026): la cota es rigurosa en punto flotante.
 * La reescritura (knomial_rewrite, en dobles) solo aporta los bloques (c_b, u_b); el lema vale
 * para bloques cualesquiera, asi que su redondeo no necesita analisis. El residuo se forma al
 * final con aritmetica de intervalos redondeada hacia fuera,
 *     [R_ij] = 1/2 ([x_i][y_j] + [x_j][y_i]) - sum_b c_b [u_bi][u_bj]   (contiene Q - sum c u u^T),
 * y la cota es la suma de intervalos
 *     [L,U] = sum_b c_b [0, s_b^2] + sum_i [R_ii] [0,1] + sum_{i<j} 2 [R_ij] [-1,1],
 * con s_b = sum|u_bi| redondeada hacia arriba; shift = mid([L,U]) y rad = rad([L,U]) de IBEX,
 * que garantizan [shift - rad, shift + rad] >= [L,U]. Desaparece el margen 'disc' (y el 'qmargin'
 * del producto de fAF2): el error de redondeo queda dentro de los coeficientes del residuo, como en
 * las formas afines fiables rAF2 de Ninin, Messine y Hansen (2015).
 * Con max_k < 2 no hay reescritura: [R] = [Q] y es la forma simetrica termino a termino (RAA de [A]).
 * Devuelve el numero de bloques extraidos.
 * Parche 0009: los vectores de trabajo (xc, yc, Q, w, blocks, R) se reutilizan por hilo.
 */
namespace knomial_detail {
struct QuadBuf {
	std::vector<double> xc, yc, Q, w;
	std::vector<KNomialBlock> blocks;
	std::vector<Interval> R;
};
inline QuadBuf& quad_buf() {
	static thread_local QuadBuf b;
	return b;
}
} // namespace knomial_detail

inline int knomial_quad_bound(const std::vector<double>& x_all, const std::vector<double>& y_all, int n_all,
                              int max_k, double& shift, double& rad) {
	knomial_detail::QuadBuf& B = knomial_detail::quad_buf();
	// Solo entran los simbolos de ruido presentes en x o en y: las filas nulas de Q no
	// generan aristas ni bloques, y comprimir conserva el orden de desempate de knomial.
	std::vector<double>& xc = B.xc;
	std::vector<double>& yc = B.yc;
	xc.clear();
	yc.clear();
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
	std::vector<double>& Q = B.Q;
	Q.resize((size_t) n * n);
	for (int i = 0; i < n; i++)
		for (int j = 0; j < n; j++)
			Q[i * n + j] = 0.5 * (xc[i] * yc[j] + xc[j] * yc[i]);
	std::vector<KNomialBlock>& blocks = B.blocks;
	blocks.clear();
	std::vector<double>& w = B.w;
	w.assign(n, 2.0);
	if (max_k >= 2) knomial_rewrite(Q, w, n, max_k, blocks);

	if (knomial_bound_mode() == 1) {
		// Parche 0013: misma cota que abajo con dobles y redondeo hacia +inf. Para cada entrada (i, j)
		// se necesitan solo los dos extremos de [R_ij]; un extremo inferior se obtiene como -up(-expr).
		// Las sumas de la cota se acumulan por separado: U (hacia arriba) y negL = -L (hacia arriba).
		const int old_rm = std::fegetround();
		if (old_rm != FE_UPWARD) std::fesetround(FE_UPWARD);
		double U = 0.0, negL = 0.0;
		for (size_t b = 0; b < blocks.size(); b++) {
			double sb = 0.0;
			for (int i = 0; i < n; i++) if (blocks[b].u[i] != 0.0) sb += std::fabs(blocks[b].u[i]);
			const double s2 = sb * sb;                       // hacia arriba
			if (blocks[b].c > 0.0) U += s2; else negL += s2;  // c [0, s2]: [0, s2] o [-s2, 0]
		}
		for (int i = 0; i < n; i++)
			for (int j = i; j < n; j++) {
				// [Q_ij] = 1/2 ([x_i][y_j] + [x_j][y_i])
				const double q_up = 0.5 * ((xc[i] * yc[j]) + (xc[j] * yc[i]));
				const double q_lo = -(0.5 * (((-xc[i]) * yc[j]) + ((-xc[j]) * yc[i])));
				// t = sum_b c_b u_bi u_bj
				double t_up = 0.0, negt = 0.0;
				for (size_t b = 0; b < blocks.size(); b++) {
					const double ui = blocks[b].u[i], uj = blocks[b].u[j];
					if (ui != 0.0 && uj != 0.0) {
						const double si = blocks[b].c * ui;   // exacto (c = +-1)
						t_up += si * uj;
						negt += (-si) * uj;
					}
				}
				const double t_lo = -negt;
				const double r_up = q_up - t_lo;             // hacia arriba
				const double r_lo = -(t_up - q_lo);          // hacia abajo
				if (i == j) {
					// [R_ii] [0,1] = [min(r_lo,0), max(r_up,0)]
					if (r_up > 0.0) U += r_up;
					if (r_lo < 0.0) negL += (-r_lo);
				} else {
					// 2 [R_ij] [-1,1] = [-2M, 2M], M = max(|r_lo|, |r_up|)
					const double M2 = 2.0 * std::max(std::fabs(r_lo), std::fabs(r_up));
					U += M2;
					negL += M2;
				}
			}
		const double L = -negL;
		const double m = 0.5 * (L + U);                  // cualquier doble sirve como centro
		const double r1 = m - L, r2 = U - m;             // ambas hacia arriba
		if (old_rm != FE_UPWARD) std::fesetround(old_rm);
		shift = m;
		rad = (r1 > r2) ? r1 : r2;
	} else {
	// Parche 0012: residuo con coeficientes intervalares (solo el triangulo superior) y cota [L,U].
	std::vector<Interval>& R = B.R;
	R.resize((size_t) n * n);
	for (int i = 0; i < n; i++)
		for (int j = i; j < n; j++) {
			Interval q = 0.5 * (Interval(xc[i]) * Interval(yc[j]) + Interval(xc[j]) * Interval(yc[i]));
			for (size_t b = 0; b < blocks.size(); b++) {
				const double ui = blocks[b].u[i], uj = blocks[b].u[j];
				if (ui != 0.0 && uj != 0.0) q -= blocks[b].c * (Interval(ui) * Interval(uj));
			}
			R[i * n + j] = q;
		}
	Interval LU(0.0);
	for (size_t b = 0; b < blocks.size(); b++) {
		Interval s(0.0);
		for (int i = 0; i < n; i++) if (blocks[b].u[i] != 0.0) s += Interval(std::fabs(blocks[b].u[i]));
		const double sb = s.ub();
		LU += blocks[b].c * Interval(0.0, (Interval(sb) * Interval(sb)).ub());
	}
	for (int i = 0; i < n; i++) {
		LU += R[i * n + i] * Interval(0.0, 1.0);
		for (int j = i + 1; j < n; j++) LU += 2.0 * (R[i * n + j] * Interval(-1.0, 1.0));
	}
	shift = LU.mid();
	rad = LU.rad();
	}

	KNomialStats& st = knomial_stats();
	st.calls++;
	if (!blocks.empty()) st.calls_with_blocks++;
	st.blocks += (long) blocks.size();
	for (size_t b = 0; b < blocks.size(); b++) {
		int sz = 0;
		for (int i = 0; i < n; i++) if (blocks[b].u[i] != 0.0) sz++;
		st.blocks_by_size[std::min(5, std::max(0, sz - 2))]++;
	}
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
