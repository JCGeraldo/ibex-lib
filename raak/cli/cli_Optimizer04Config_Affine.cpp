//============================================================================
// ibexopt-raak (version local de experimentos)
//============================================================================

#include "ibex_Optimizer04Config_Affine.h"
#include "ibex_LinearizerXTaylor.h"
#include "ibex_LinearizerCompo.h"
#include "ibex_LinearizerAffine2.h"
#include "ibex_Exception.h"

#include <sstream>

namespace ibex {

Optimizer04Config_Affine::Optimizer04Config_Affine(int argc, char** argv) :
		Optimizer04Config(argc, argv) {
}

// "raak" y "raakcompo" usan los mismos linearizadores que "art" y "compo": la
// diferencia esta en la multiplicacion de formas afines, que el main configura
// con ibex::knomial_max_k() antes de construir el optimizador.
//
// Nota: Optimizer04Config::get_ctc() solo envuelve la relajacion en
// CtcPolytopeHull si el nombre esta en su lista; el fork local la amplia
// con "raak" y "raakcompo".
Linearizer* Optimizer04Config_Affine::get_linear_relax() {
	if (linearrelaxation == "xn")
		return &rec(new LinearizerXTaylor(*ext_sys));

	if (linearrelaxation == "art" || linearrelaxation == "raak")
		return &rec(new LinearizerAffine2(*ext_sys));

	if (linearrelaxation == "compo" || linearrelaxation == "raakcompo")
		return &rec(new LinearizerCompo(
				rec(new LinearizerXTaylor(*ext_sys)),
				rec(new LinearizerAffine2(*ext_sys))));

	std::stringstream ss;
	ss << "[ibexopt-raak] relajacion lineal desconocida: '" << linearrelaxation
	   << "' (opciones: xn | art | compo | raak | raakcompo)";
	ibex_error(ss.str().c_str());
	return NULL;
}

} // namespace ibex
