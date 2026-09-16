#!/usr/bin/env bash
# F5: separar el efecto de la RAA de [A] (raak_k=1) del de la reescritura k-nomial (raak_k=3).
# Recompila con la cota de Chebyshev del cuadrado activa desde k=1, corre las pruebas,
# verifica que k=3 reproduce las celdas del barrido v2 y, si todo pasa, barre con K=1.
set -uo pipefail
HERE="$HOME/ibex-local/scripts"
TESTS="$HOME/ibex-local/tests"

INSTS="easy/ex14_2_4 medium/ex8_4_4bis easy/ex5_4_3" \
VARIANTS="art raak:1 raak:3 compo raakcompo:1 raakcompo:3" \
TLIM=60 bash "$HERE/wsl_raak_quick.sh" || { echo "*** compilacion fallida: no se lanza el barrido"; exit 1; }

"$TESTS/raak_arith_test" > /dev/null || { echo "*** prueba aritmetica fallida: no se lanza el barrido"; exit 1; }

# con k=3 nada cambia: deben salir las celdas del barrido v2 (baseline-20260914-131620)
LOGS="$HOME/ibex-local/logs"
cells () { sed 's/\x1b\[[0-9;]*m//g' "$1" | grep -oE "number of cells:[^0-9]*[0-9]+" | grep -oE "[0-9]+$" | head -1; }
c1=$(cells "$LOGS/raak-quick-easy__ex14_2_4-raak_k3.log")
c2=$(cells "$LOGS/raak-quick-medium__ex8_4_4bis-raak_k3.log")
c3=$(cells "$LOGS/raak-quick-easy__ex14_2_4-raakcompo_k3.log")
c4=$(cells "$LOGS/raak-quick-medium__ex8_4_4bis-raakcompo_k3.log")
echo
echo "== control k=3 frente al barrido v2: ex14_2_4 raak $c1 (v2 3692), ex8_4_4bis raak $c2 (v2 10294), ex14_2_4 raakcompo $c3 (v2 92), ex8_4_4bis raakcompo $c4 (v2 8618)"
if [ "$c1" != 3692 ] || [ "$c2" != 10294 ] || [ "$c3" != 92 ] || [ "$c4" != 8618 ]; then
  echo "*** k=3 cambio respecto de v2: no se lanza el barrido"; exit 1
fi

echo
echo "== pruebas y control OK: barrido completo con raak_k=1"
K=1 bash "$HERE/wsl_sweep_raak.sh"
