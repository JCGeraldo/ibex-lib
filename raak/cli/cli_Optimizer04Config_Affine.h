//============================================================================
// ibexopt-raak (version local de experimentos)
//
// Subclase de Optimizer04Config (fork rilianx/ibex-lib, rama pucv_practica)
// que agrega las relajaciones lineales del plugin ibex-affine.
// Adaptada de ibex-team/ibex-optim-extra (Bertrand Neveu, Gilles Chabert).
//============================================================================

#ifndef __IBEX_OPTIMIZER_04_CONFIG_AFFINE__
#define __IBEX_OPTIMIZER_04_CONFIG_AFFINE__

#include "ibex_Optimizer04Config.h"

#include <string>

namespace ibex {

class Optimizer04Config_Affine : public Optimizer04Config {
public:
	/**
	 * \param arith aritmetica afin del linearizador de art/compo: "af2" (LinearizerAffine2, modelo
	 *              AF_fAF2, tambien para "raa": la diferencia RAA/AF2 la fija ibex::affine_mode())
	 *              o "aa" (LinearizerAffineT<AF_fAFFullI>, Affine3; parche 0007).
	 */
	Optimizer04Config_Affine(int argc, char** argv, const std::string& arith = "af2");

protected:
	// load_sys NO se sobreescribe a proposito: el constructor de la clase base lo
	// invoca, y una llamada virtual dentro de un constructor despacha a la version
	// de la base, asi que una version propia nunca se ejecutaria al construir.
	//
	// get_linear_relax si se sobreescribe: la llama get_ctc(), que se invoca
	// cuando el Optimizer se construye con este objeto ya completo.
	virtual Linearizer* get_linear_relax() override;

	std::string arith;
};

} // namespace ibex

#endif // __IBEX_OPTIMIZER_04_CONFIG_AFFINE__
