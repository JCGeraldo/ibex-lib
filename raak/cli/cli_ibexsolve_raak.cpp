//============================================================================
// ibexsolve-raak (version local de experimentos, 10-11-2026)
//
// IbexSolve con el contractor elegible, para medir la relajacion afin (AF2 / RAA / AA, con o sin
// k-nomial) en problemas de satisfaccion de restricciones (benchs/solver). Punto 1 del to-do de fin
// de octubre: "usar en benchs/solver solo afin".
//
//   --ctc=affine           SOLO el politopo de la relajacion afin: CtcFixPoint(CtcPolytopeHull(LinearizerAffine))
//   --ctc=xn               solo el politopo de XTaylor (referencia de "solo relajacion lineal")
//   --ctc=hc4              solo HC4 (referencia de propagacion pura)
//   --ctc=hc4+affine       HC4 y despues el politopo afin, en punto fijo
//   --ctc=hc4+xn           HC4 y despues el politopo de XTaylor, en punto fijo
//   --ctc=default          el contractor de DefaultSolver (HC4, ACID, Newton si es cuadrado, politopo XTaylor)
//   --ctc=default+affine   el de DefaultSolver seguido del politopo afin
//   --arith=af2|raa|aa  --knomial_k=K  --knomial_budget=N  --knomial_bound=interval|directed  --trig=...
//                          igual que en ibexopt-raak
// Biseccion y pila: las de DefaultSolver (SmearSumRelative si el sistema es cuadrado de igualdades,
// RoundRobin si no; busqueda en profundidad).
//============================================================================
#include <fstream>
#include "ibex.h"
#include "ibex_LinearizerAffine2.h"
#include "ibex_KNomial.h"
#include "ibex_AffineTrig.h"
#include "parse_args.h"
#include <sstream>
#include <iostream>

using namespace std;
using namespace ibex;

int main(int argc, char** argv) {
	args::ArgumentParser parser("ibexsolve-raak", "IbexSolve con contractor elegible y relajaciones de ibex-affine (AF2 / RAA / AA, k-nomial)");
	args::HelpFlag help(parser, "help", "Display this help menu", {'h', "help"});
	args::ValueFlag<string> _ctc(parser, "ctc", "Contractor: affine* | xn | hc4 | hc4+affine | hc4+xn | default | default+affine", {"ctc"});
	args::ValueFlag<string> _arith(parser, "arith", "Affine arithmetic: af2* | raa | aa", {"arith"});
	args::ValueFlag<int> _knomialK(parser, "knomial_k", "k-nomial rewriting: 0* = none, K>=2 = blocks of up to K variables", {"knomial_k"});
	args::ValueFlag<long> _knomialBudget(parser, "knomial_budget", "Node budget of the clique search per product (0* = unlimited)", {"knomial_budget"});
	args::ValueFlag<string> _knomialBound(parser, "knomial_bound", "interval* | directed", {"knomial_bound"});
	args::ValueFlag<string> _trig(parser, "trig", "auto* | cheb | minrange | legacy", {"trig"});
	args::ValueFlag<double> _epsMin(parser, "eps-min", "Minimal width of output boxes (default 1e-3)", {'e', "eps-min"});
	args::ValueFlag<double> _epsMax(parser, "eps-max", "Maximal width of output boxes (default +oo)", {'E', "eps-max"});
	args::ValueFlag<double> _timeout(parser, "timeout", "Time limit in seconds (default: none)", {'t', "timeout"});
	args::ValueFlag<double> _seed(parser, "seed", "Random seed", {"random-seed"});
	args::ValueFlag<string> _boxes(parser, "boxes", "Write every output box to this text file: one line per box, 'S|B|U|P lb ub lb ub ...' (solution, boundary, unknown, pending)", {"boxes"});
	args::Flag _bfs(parser, "bfs", "Breadth-first search", {"bfs"});
	args::Flag quiet(parser, "quiet", "Print no report", {'q', "quiet"});
	args::Positional<string> filename(parser, "filename", "The name of the MINIBEX file.");
	try { parser.ParseCLI(argc, argv); }
	catch (const args::Help&) { cout << parser; return 0; }
	catch (const args::ParseError& e) { cerr << e.what() << endl << parser; return 1; }
	catch (const args::ValidationError& e) { cerr << e.what() << endl << parser; return 1; }
	if (!filename) { cerr << "Filename is required." << endl; return 1; }

	const string ctcname = _ctc ? _ctc.Get() : "affine";
	const string arith = _arith ? _arith.Get() : "af2";
	const int knomial_k = _knomialK ? _knomialK.Get() : 0;
	if (arith != "af2" && arith != "raa" && arith != "aa") { cerr << "--arith=" << arith << ": af2 | raa | aa" << endl; return 1; }
	if (knomial_k < 0 || knomial_k == 1) { cerr << "--knomial_k debe ser 0 o >= 2" << endl; return 1; }
	affine_mode() = (arith == "raa") ? AFFINE_RAA : AFFINE_AF2;
	knomial_max_k() = knomial_k;
	if (_knomialBudget) { if (_knomialBudget.Get() < 0) { cerr << "--knomial_budget debe ser >= 0" << endl; return 1; } knomial_node_budget() = _knomialBudget.Get(); }
	if (_knomialBound) {
		const string b = _knomialBound.Get();
		if (b == "interval") knomial_bound_mode() = 0; else if (b == "directed") knomial_bound_mode() = 1;
		else { cerr << "--knomial_bound=" << b << ": interval | directed" << endl; return 1; }
	}
	const string trig = _trig ? _trig.Get() : "auto";
	if (trig == "auto") trig_lin_mode() = TRIG_AUTO; else if (trig == "cheb") trig_lin_mode() = TRIG_CHEBYSHEV;
	else if (trig == "minrange") trig_lin_mode() = TRIG_MINRANGE; else if (trig == "legacy") trig_lin_mode() = TRIG_LEGACY;
	else { cerr << "--trig=" << trig << ": auto | cheb | minrange | legacy" << endl; return 1; }

	try {
		System sys(filename.Get().c_str());
		const double eps_min = _epsMin ? _epsMin.Get() : DefaultSolver::default_eps_x_min;
		const double eps_max = _epsMax ? _epsMax.Get() : POS_INFINITY;

		// sistema cuadrado de igualdades (para Newton y para el bisector), como en DefaultSolver
		int nb_eq = 0;
		for (int i = 0; i < sys.nb_ctr; i++) if (sys.ctrs[i].op == EQ) nb_eq += sys.ctrs[i].f.image_dim();
		System* eqs = (sys.nb_var == nb_eq) ? new System(sys, System::EQ_ONLY) : NULL;

		// piezas (viven hasta el final del programa)
		Linearizer* aff = NULL;
		const bool need_aff = ctcname.find("affine") != string::npos;
		if (need_aff) aff = (arith == "aa") ? (Linearizer*) new LinearizerAffineT<AF_fAFFullI>(sys) : (Linearizer*) new LinearizerAffine2(sys);
		Ctc* c = NULL;
		if (sys.nb_ctr == 0) c = new CtcIdentity(sys.nb_var);
		else if (ctcname == "affine") c = new CtcFixPoint(*new CtcPolytopeHull(*aff));
		else if (ctcname == "xn") c = new CtcFixPoint(*new CtcPolytopeHull(*new LinearizerXTaylor(sys)));
		else if (ctcname == "hc4") c = new CtcHC4(sys.ctrs, 0.01);
		else if (ctcname == "hc4+affine") c = new CtcFixPoint(*new CtcCompo(*new CtcHC4(sys.ctrs, 0.01), *new CtcPolytopeHull(*aff)));
		else if (ctcname == "hc4+xn") c = new CtcFixPoint(*new CtcCompo(*new CtcHC4(sys.ctrs, 0.01), *new CtcPolytopeHull(*new LinearizerXTaylor(sys))));
		else if (ctcname == "default" || ctcname == "default+affine") {
			Array<Ctc> l(5); int idx = 0;
			l.set_ref(idx++, *new CtcHC4(sys.ctrs, 0.01));
			l.set_ref(idx++, *new CtcAcid(sys, *new CtcHC4(sys.ctrs, 0.1, true)));
			if (eqs) l.set_ref(idx++, *new CtcNewton(eqs->f_ctrs, 5e8, eps_min, 1.e-4));
			l.set_ref(idx++, *new CtcFixPoint(*new CtcCompo(*new CtcPolytopeHull(*new LinearizerXTaylor(sys)), *new CtcHC4(sys.ctrs, 0.01))));
			if (ctcname == "default+affine")
				l.set_ref(idx++, *new CtcFixPoint(*new CtcCompo(*new CtcPolytopeHull(*aff), *new CtcHC4(sys.ctrs, 0.01))));
			l.resize(idx);
			c = new CtcCompo(l);
		} else { cerr << "--ctc=" << ctcname << ": affine | xn | hc4 | hc4+affine | hc4+xn | default | default+affine" << endl; return 1; }

		Bsc* bsc = eqs ? (Bsc*) new SmearSumRelative(*eqs, eps_min) : (Bsc*) new RoundRobin(eps_min);
		CellBuffer* buf = _bfs ? (CellBuffer*) new CellList() : (CellBuffer*) new CellStack();
		Solver s(sys, *c, *bsc, *buf, Vector(sys.nb_var, eps_min), Vector(sys.nb_var, eps_max));
		RNG::srand(_seed ? _seed.Get() : DefaultSolver::default_random_seed);
		if (_timeout) s.time_limit = _timeout.Get();

		if (!quiet)
			cout << "ctc=" << ctcname << " arith=" << arith << " knomial_k=" << knomial_k << " trig=" << trig
			     << " knomial_budget=" << knomial_node_budget() << " knomial_bound=" << (knomial_bound_mode() == 1 ? "directed" : "interval")
			     << " eps_min=" << eps_min << " cuadrado=" << (eqs ? 1 : 0) << " n=" << sys.nb_var << " m=" << sys.nb_ctr << endl;

		Solver::Status st = s.solve(sys.box);
		if (!quiet) s.report();
		const char* stn = st == Solver::SUCCESS ? "SUCCESS" : st == Solver::INFEASIBLE ? "INFEASIBLE" : st == Solver::NOT_ALL_VALIDATED ? "NOT_ALL_VALIDATED"
		                : st == Solver::TIME_OUT ? "TIME_OUT" : st == Solver::CELL_OVERFLOW ? "CELL_OVERFLOW" : "USER_BREAK";
		const CovSolverData& d = s.get_data();
		if (_boxes) {
			ofstream fo(_boxes.Get().c_str()); fo.precision(17);
			for (int t = 0; t < 4; t++) {
				const size_t nb = t == 0 ? d.nb_solution() : t == 1 ? d.nb_boundary() : t == 2 ? d.nb_unknown() : d.nb_pending();
				for (size_t i = 0; i < nb; i++) {
					const IntervalVector& b = t == 0 ? d.solution(i) : t == 1 ? d.boundary(i) : t == 2 ? d.unknown(i) : d.pending(i);
					fo << "SBUP"[t];
					for (int j = 0; j < b.size(); j++) fo << ' ' << b[j].lb() << ' ' << b[j].ub();
					fo << '\n';
				}
			}
		}
		const KNomialStats& ks = knomial_stats();
		cout << "RAAK-SOLVE status=" << stn << " cells=" << (long) s.get_nb_cells() << " time=" << s.get_time()
		     << " solution=" << d.nb_solution() << " boundary=" << d.nb_boundary() << " unknown=" << d.nb_unknown() << " pending=" << d.nb_pending()
		     << " productos=" << ks.calls << " con_bloques=" << ks.calls_with_blocks << " bloques=" << ks.blocks << " usados=" << ks.calls_used
		     << " corner_used=" << ks.corner_used << " sqr_used=" << ks.sqr_used << endl;
		return 0;
	} catch (SyntaxError& e) {
		cout << "RAAK-SOLVE status=SYNTAX_ERROR" << endl; return 2;
	} catch (Exception& e) {
		cout << "RAAK-SOLVE status=EXCEPTION" << endl; return 3;
	}
}
