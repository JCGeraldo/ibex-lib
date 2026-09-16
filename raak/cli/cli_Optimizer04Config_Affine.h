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

namespace ibex {

class Optimizer04Config_Affine : public Optimizer04Config {
public:
	Optimizer04Config_Affine(int argc, char** argv);

protected:
	// load_sys NO se sobreescribe a proposito: el constructor de la clase base lo
	// invoca, y una llamada virtual dentro de un constructor despacha a la version
	// de la base, asi que una version propia nunca se ejecutaria al construir.
	//
	// get_linear_relax si se sobreescribe: la llama get_ctc(), que se invoca
	// cuando el Optimizer se construye con este objeto ya completo.
	virtual Linearizer* get_linear_relax() override;
};

} // namespace ibex

#endif // __IBEX_OPTIMIZER_04_CONFIG_AFFINE__
