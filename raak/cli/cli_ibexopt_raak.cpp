//============================================================================
// ibexopt-raak (version local de experimentos)
//
// Copia de src/bin/ibexopt_config04.cpp del fork rilianx/ibex-lib
// (Ignacio Araya, Gilles Chabert), usando Optimizer04Config_Affine para
// habilitar las relajaciones del plugin ibex-affine y las aritmeticas afines
// del proyecto RAA-K.
//
// Interruptores (Fase 1, parche 0004):
//   --lr=xn|art|compo        relajacion lineal (sin cambio de significado)
//   --arith=af2|raa|aa       aritmetica afin; solo tiene efecto con art/compo
//   --knomial_k=K            0 = sin reescritura k-nomial; K>=2 = reescritura con bloques de hasta K
// Alias de compatibilidad con el prototipo (imprimen una linea "[compat]"):
//   --lr=raak       == --lr=art   --arith=raa --knomial_k=3
//   --lr=raakcompo  == --lr=compo --arith=raa --knomial_k=3
//   --raak_k=0      == --arith=af2 --knomial_k=0
//   --raak_k=1      == --arith=raa --knomial_k=0
//   --raak_k=K>=2   == --arith=raa --knomial_k=K
// Un --arith o --knomial_k explicito prevalece sobre lo que fije un alias.
//
// Fase 2 (parche 0008):
//   --knomial_budget=N       presupuesto de nodos de la busqueda de cliques por producto (0 = sin limite)
//   --knomial_bound=interval|directed   como se calcula la cota rigurosa (parches 0012 / 0013)
//   --trig=auto|cheb|minrange|legacy   linealizacion de sin/cos en la aritmetica afin
//                                      (auto* = sigue el modo del plugin, que por defecto es
//                                      Chebyshev -> pendiente de cuerda; legacy = codigo original)
//============================================================================

#include "ibex.h"
#include "ibex_Optimizer04Config_Affine.h"
#include "ibex_KNomial.h"
#include "ibex_AffineTrig.h"
#include "parse_args.h"

#include <sstream>

using namespace std;
using namespace ibex;

void printArgsSummary(const std::vector<std::string>& args) {
    if (args.size() < 11) {
        std::cerr << "Numero insuficiente de argumentos." << std::endl;
        return;
    }
    std::cout << "Resumen de Argumentos:" << std::endl;
    std::cout << "Filename: " << args[1] << std::endl;
    std::cout << "Filtering: " << args[2] << std::endl;
    std::cout << "Linear Relaxation: " << args[3] << std::endl;
    std::cout << "Bisection: " << args[4] << std::endl;
    std::cout << "Strategy: " << args[5] << std::endl;
    std::cout << "Beamsize: " << args[6] << std::endl;
    std::cout << "Precision (eps_x): " << args[7] << std::endl;
    std::cout << "Goal Precision (eps): " << args[8] << std::endl;
    std::cout << "Time Limit: " << args[9] << std::endl;
    std::cout << "Random Seed: " << args[10] << std::endl;
}

int main(int argc, char** argv) {
    args::ArgumentParser parser("ibexopt-raak", "Optimizer04 con relajaciones de ibex-affine y aritmeticas AF2 / RAA / AA (con o sin k-nomial)");
    args::HelpFlag help(parser, "help", "Display this help menu", {'h', "help"});

    args::Group filteringGroup(parser, "Filtering Options", args::Group::Validators::DontCare);
    args::ValueFlag<std::string> _filtering(filteringGroup, "filtering", "Filtering option (hc4|acidhc4*|3bcidhc4)", {"filtering"});

    args::Group hc4Group(filteringGroup, "HC4 Options", args::Group::Validators::DontCare);
    args::ValueFlag<double> _precHc4(hc4Group, "prec_hc4", "Precision for hc4 (default=1e-7)", {"hc4_p"});

    args::Group bcidhc4Group(filteringGroup, "3BCIDHC4 Options", args::Group::Validators::DontCare);
    args::ValueFlag<double> _prec3Bcidhc4(bcidhc4Group, "prec_3bcidhc4", "Precision for 3bcidhc4 (default=1e-7)", {"prec_3bcidhc4"});
    args::ValueFlag<int> _slices3Bcidhc4(bcidhc4Group, "slices_3bcidhc4", "Number of slices for 3bcidhc4", {"slices"});

    args::ValueFlag<std::string> _linearRelaxation(parser, "linear relaxation", "Linear relaxation (xn*|art|compo). Alias: raak = art+raa+k3, raakcompo = compo+raa+k3", {"lr"});
    args::ValueFlag<std::string> _arith(parser, "arith", "Affine arithmetic for art/compo: af2* (fAF2), raa (RAA of [A]), aa (traditional AA, patch 0007)", {"arith"});
    args::ValueFlag<int> _knomialK(parser, "knomial_k", "k-nomial rewriting: 0* = none, K>=2 = blocks of up to K variables", {"knomial_k"});
    args::ValueFlag<int> _raakK(parser, "raak_k", "[compat] 0 -> af2,k=0 | 1 -> raa,k=0 | K>=2 -> raa,k=K", {"raak_k"});
    args::ValueFlag<long> _knomialBudget(parser, "knomial_budget", "Node budget of the clique search per product: 0* = unlimited (patch 0011). Overrides RAAK_NODE_BUDGET", {"knomial_budget"});
    args::ValueFlag<std::string> _knomialBound(parser, "knomial_bound", "Rigorous k-nomial bound computed with: interval* (ibex::Interval, patch 0012) | directed (doubles rounded upward, patch 0013). Overrides RAAK_BOUND_MODE", {"knomial_bound"});
    args::ValueFlag<std::string> _trig(parser, "trig", "sin/cos linearization in the affine arithmetic: auto* (plugin mode: Chebyshev = chord slope), cheb, minrange, legacy (original plugin code)", {"trig"});
    args::ValueFlag<std::string> _bisection(parser, "bisection", "Bisection option (roundrobin|largestfirst|largestfirstnoobj|smearsum|smearmax|smearsumrel|smearmaxrel|lsmear|lsmearmg*)", {'b'});
    args::ValueFlag<std::string> _strategy(parser, "strategy", "Search Strategy (bfs|dh|bs*)", {'s'});
    args::ValueFlag<int> _beamsize(parser, "beamsize", "Beamsize (default=1)", {'B'});
    args::ValueFlag<double> _prec(parser, "prec", "Precision (default=1e-7)", {"eps_x"});
    args::ValueFlag<double> _goalPrec(parser, "goal precision (default=1e-6)", "Goal precision", {"eps"});
    args::ValueFlag<double> _timeLimit(parser, "time limit", "Time limit (default=1000)", {'t'});
    args::ValueFlag<int> _randomSeed(parser, "random seed", "Random seed (default=42)", {"seed"});
    args::Flag quiet(parser, "quiet", "Print no report on the standard output.", {'q', "quiet"});

    args::Positional<std::string> filename(parser, "filename", "The name of the MINIBEX file.");

    try {
        parser.ParseCLI(argc, argv);
    } catch (const args::Help&) {
        std::cout << parser;
        return 0;
    } catch (const args::ParseError& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    } catch (const args::ValidationError& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }

    if (!filename) {
        std::cerr << "Filename is required." << std::endl;
        return 1;
    }

    // ---- relajacion, aritmetica y k-nomial: alias de compatibilidad primero, explicitos despues
    std::string lr = _linearRelaxation ? _linearRelaxation.Get() : "xn";
    std::string arith = "af2";
    int knomial_k = 0;

    if (lr == "raak" || lr == "raakcompo") {
        std::string lr_new = (lr == "raak") ? "art" : "compo";
        std::cout << "[compat] --lr=" << lr << " \xe2\x86\x92 --lr=" << lr_new << " --arith=raa --knomial_k=3" << std::endl;
        lr = lr_new;
        arith = "raa";
        knomial_k = 3;
    }
    if (_raakK) {
        int K = _raakK.Get();
        if (K < 0) { std::cerr << "--raak_k debe ser >= 0" << std::endl; return 1; }
        arith = (K == 0) ? "af2" : "raa";
        knomial_k = (K >= 2) ? K : 0;
        std::cout << "[compat] --raak_k=" << K << " \xe2\x86\x92 --arith=" << arith << " --knomial_k=" << knomial_k << std::endl;
    }
    if (_arith) arith = _arith.Get();
    if (_knomialK) knomial_k = _knomialK.Get();

    if (lr != "xn" && lr != "art" && lr != "compo") {
        std::cerr << "--lr=" << lr << ": relajacion desconocida (xn | art | compo; alias raak | raakcompo)" << std::endl;
        return 1;
    }
    if (arith != "af2" && arith != "raa" && arith != "aa") {
        std::cerr << "--arith=" << arith << ": aritmetica desconocida (af2 | raa | aa)" << std::endl;
        return 1;
    }
    if (knomial_k < 0 || knomial_k == 1) {
        std::cerr << "--knomial_k=" << knomial_k << ": debe ser 0 (sin reescritura) o >= 2" << std::endl;
        return 1;
    }
    // [raak local] 10-11-2026: presupuesto de la busqueda de cliques y modo de la cota rigurosa como opciones
    // (antes solo por las variables de entorno RAAK_NODE_BUDGET y RAAK_BOUND_MODE, que siguen valiendo como
    // valor inicial si la opcion no se da). Por hilo, igual que affine_mode() y knomial_max_k().
    if (_knomialBudget) {
        if (_knomialBudget.Get() < 0) { std::cerr << "--knomial_budget debe ser >= 0" << std::endl; return 1; }
        ibex::knomial_node_budget() = _knomialBudget.Get();
    }
    if (_knomialBound) {
        const std::string b = _knomialBound.Get();
        if (b == "interval")      ibex::knomial_bound_mode() = 0;
        else if (b == "directed") ibex::knomial_bound_mode() = 1;
        else { std::cerr << "--knomial_bound=" << b << ": modo desconocido (interval | directed)" << std::endl; return 1; }
    }
    // [raak local] Fase 2: linealizacion de sin/cos (por hilo; solo actua si art/compo evaluan formas afines)
    std::string trig = _trig ? _trig.Get() : "auto";
    if (trig == "auto")          ibex::trig_lin_mode() = ibex::TRIG_AUTO;
    else if (trig == "cheb")     ibex::trig_lin_mode() = ibex::TRIG_CHEBYSHEV;
    else if (trig == "minrange") ibex::trig_lin_mode() = ibex::TRIG_MINRANGE;
    else if (trig == "legacy")   ibex::trig_lin_mode() = ibex::TRIG_LEGACY;
    else {
        std::cerr << "--trig=" << trig << ": modo desconocido (auto | cheb | minrange | legacy)" << std::endl;
        return 1;
    }
    std::cout << "arith=" << arith << " knomial_k=" << knomial_k << " lr=" << lr << " trig=" << trig
              << " knomial_budget=" << ibex::knomial_node_budget()
              << " knomial_bound=" << (ibex::knomial_bound_mode() == 1 ? "directed" : "interval") << std::endl;

    std::string defaultFiltering = "acidhc4";
    std::string defaultBisection = "lsmearmg";
    std::string defaultStrategy = "bs";
    int defaultBeamsize = 1;
    double defaultPrec = 1.e-7;
    double defaultGoalPrec = 1.e-6;
    double defaultTimeLimit = 1000;
    int defaultRandomSeed = 42;

    std::vector<std::string> args = {
        "optimizer04", filename.Get(),
        _filtering ? _filtering.Get() : defaultFiltering,
        lr,
        _bisection ? _bisection.Get() : defaultBisection,
        _strategy ? _strategy.Get() : defaultStrategy,
        _beamsize ? std::to_string(_beamsize.Get()) : std::to_string(defaultBeamsize),
        _prec ? std::to_string(_prec.Get()) : std::to_string(defaultPrec),
        _goalPrec ? std::to_string(_goalPrec.Get()) : std::to_string(defaultGoalPrec),
        _timeLimit ? std::to_string(_timeLimit.Get()) : std::to_string(defaultTimeLimit),
        _randomSeed ? std::to_string(_randomSeed.Get()) : std::to_string(defaultRandomSeed)
    };

    printArgsSummary(args);

    // Interruptores de la aritmetica afin (por hilo). Solo art/compo evaluan formas afines.
    // affine_mode() solo tiene sentido en AF_fAF2 (af2|raa); con aa se ignora (queda AF2).
    // knomial_max_k() actua en AF_fAF2 (af2, raa) y en AF_fAFFullI (aa).
    const bool uses_affine = (lr == "art" || lr == "compo");
    ibex::affine_mode() = (uses_affine && arith == "raa") ? ibex::AFFINE_RAA : ibex::AFFINE_AF2;
    ibex::knomial_max_k() = uses_affine ? knomial_k : 0;
    std::cout << "affine_mode=" << (ibex::affine_mode() == ibex::AFFINE_RAA ? "RAA" : "AF2")
              << " knomial_max_k=" << ibex::knomial_max_k()
              << " linearizador=" << (!uses_affine ? "xn" : (arith == "aa" ? "LinearizerAffineT<AF_fAFFullI>" : "LinearizerAffine2")) << std::endl;

    std::vector<char*> argv_new;
    for (auto& arg : args) {
        argv_new.push_back(&arg[0]);
    }

    Optimizer04Config_Affine config(argv_new.size(), argv_new.data(), arith);

    Optimizer o(config);

    cout.precision(12);

    if (!quiet)
        cout << "\n\nrunning............" << endl << endl;

    o.optimize(config.sys->box);

    if (!quiet)
        o.report();

    if (ibex::knomial_max_k() >= 2 || ibex::affine_mode() == ibex::AFFINE_RAA || arith == "aa") {
        const ibex::KNomialStats& s = ibex::knomial_stats();
        double ratio = s.rad_faf2 > 0 ? s.rad_used / s.rad_faf2 : 1.0;
        double cross_ratio = s.cross_faf2 > 0 ? s.cross_corner / s.cross_faf2 : 1.0;
        std::printf("RAA-K stats: productos=%ld con_bloques=%ld bloques=%ld usados=%ld radio_cuadratico_vs_fAF2=%.4f"
                    " evaluados=%ld cuadrados=%ld cuadrados_usados=%ld"
                    " corner_products=%ld corner_used=%ld cruces_vs_fAF2=%.4f"
                    " aa_products=%ld aa_used=%ld\n",
                    s.products, s.calls_with_blocks, s.blocks, s.calls_used, ratio,
                    s.calls, s.sqr_products, s.sqr_used,
                    s.corner_products, s.corner_used, cross_ratio,
                    s.aa_products, s.aa_used);
    }

    // [raak local] Fase 2: contadores de la linealizacion de sin/cos (solo si hubo alguna)
    {
        const ibex::TrigLinStats& t = ibex::trig_lin_stats();
        const long total = t.sin_ch + t.cos_ch + t.sin_mr + t.cos_mr + t.sin_mr_itv + t.cos_mr_itv
                         + t.sin_legacy + t.cos_legacy + t.fallback_itv;
        if (total > 0)
            std::printf("TRIG stats: modo=%s sin_ch=%ld cos_ch=%ld sin_mr=%ld cos_mr=%ld sin_mr_itv=%ld cos_mr_itv=%ld"
                        " sin_legacy=%ld cos_legacy=%ld fallback_itv=%ld\n",
                        trig.c_str(), t.sin_ch, t.cos_ch, t.sin_mr, t.cos_mr, t.sin_mr_itv, t.cos_mr_itv,
                        t.sin_legacy, t.cos_legacy, t.fallback_itv);
    }

    return 0;
}
