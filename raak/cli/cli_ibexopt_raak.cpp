//============================================================================
// ibexopt-raak (version local de experimentos)
//
// Copia de src/bin/ibexopt_config04.cpp del fork rilianx/ibex-lib
// (Ignacio Araya, Gilles Chabert), usando Optimizer04Config_Affine para
// habilitar las relajaciones del plugin ibex-affine y el prototipo de RAA-K.
//============================================================================

#include "ibex.h"
#include "ibex_Optimizer04Config_Affine.h"
#include "ibex_KNomial.h"
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
    args::ArgumentParser parser("ibexopt-raak", "Optimizer04 con relajaciones de ibex-affine y RAA-K");
    args::HelpFlag help(parser, "help", "Display this help menu", {'h', "help"});

    args::Group filteringGroup(parser, "Filtering Options", args::Group::Validators::DontCare);
    args::ValueFlag<std::string> _filtering(filteringGroup, "filtering", "Filtering option (hc4|acidhc4*|3bcidhc4)", {"filtering"});

    args::Group hc4Group(filteringGroup, "HC4 Options", args::Group::Validators::DontCare);
    args::ValueFlag<double> _precHc4(hc4Group, "prec_hc4", "Precision for hc4 (default=1e-7)", {"hc4_p"});

    args::Group bcidhc4Group(filteringGroup, "3BCIDHC4 Options", args::Group::Validators::DontCare);
    args::ValueFlag<double> _prec3Bcidhc4(bcidhc4Group, "prec_3bcidhc4", "Precision for 3bcidhc4 (default=1e-7)", {"prec_3bcidhc4"});
    args::ValueFlag<int> _slices3Bcidhc4(bcidhc4Group, "slices_3bcidhc4", "Number of slices for 3bcidhc4", {"slices"});

    args::ValueFlag<std::string> _linearRelaxation(parser, "linear relaxation", "Linear relaxation option (xn*|art|compo|raak|raakcompo)", {"lr"});
    args::ValueFlag<int> _raakK(parser, "raak_k", "RAA-K: max_k of the affine multiplication for raak|raakcompo (0 = fAF2, 1 = quadratic part of RAA [A]: symmetric products + Chebyshev squares, >=2 = RAA-K k-nomial; default 3)", {"raak_k"});
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

    std::string defaultFiltering = "acidhc4";
    std::string defaultLinearRelaxation = "xn";
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
        _linearRelaxation ? _linearRelaxation.Get() : defaultLinearRelaxation,
        _bisection ? _bisection.Get() : defaultBisection,
        _strategy ? _strategy.Get() : defaultStrategy,
        _beamsize ? std::to_string(_beamsize.Get()) : std::to_string(defaultBeamsize),
        _prec ? std::to_string(_prec.Get()) : std::to_string(defaultPrec),
        _goalPrec ? std::to_string(_goalPrec.Get()) : std::to_string(defaultGoalPrec),
        _timeLimit ? std::to_string(_timeLimit.Get()) : std::to_string(defaultTimeLimit),
        _randomSeed ? std::to_string(_randomSeed.Get()) : std::to_string(defaultRandomSeed)
    };

    printArgsSummary(args);

    // Modo de la multiplicacion de formas afines: solo cambia con raak/raakcompo.
    const std::string& lr = args[3];
    int raak_k = _raakK ? _raakK.Get() : 3;
    ibex::knomial_max_k() = (lr == "raak" || lr == "raakcompo") ? raak_k : 0;
    std::cout << "RAA-K max_k (multiplicacion afin): " << ibex::knomial_max_k() << std::endl;

    std::vector<char*> argv_new;
    for (auto& arg : args) {
        argv_new.push_back(&arg[0]);
    }

    Optimizer04Config_Affine config(argv_new.size(), argv_new.data());

    Optimizer o(config);

    cout.precision(12);

    if (!quiet)
        cout << "\n\nrunning............" << endl << endl;

    o.optimize(config.sys->box);

    if (!quiet)
        o.report();

    if (ibex::knomial_max_k() >= 1) {
        const ibex::KNomialStats& s = ibex::knomial_stats();
        double ratio = s.rad_faf2 > 0 ? s.rad_used / s.rad_faf2 : 1.0;
        std::printf("RAA-K stats: productos=%ld con_bloques=%ld bloques=%ld usados=%ld radio_cuadratico_vs_fAF2=%.4f"
                    " evaluados=%ld cuadrados=%ld cuadrados_usados=%ld\n",
                    s.products, s.calls_with_blocks, s.blocks, s.calls_used, ratio,
                    s.calls, s.sqr_products, s.sqr_used);
    }

    return 0;
}
