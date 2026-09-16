#!/usr/bin/env bash
# F5 v2 (filtro de simbolos compartidos + RAA-K en sqr): recompila, corre las pruebas y,
# solo si pasan, lanza el barrido completo de raak y raakcompo.
set -uo pipefail
HERE="$HOME/ibex-local/scripts"
TESTS="$HOME/ibex-local/tests"

INSTS="easy/ex14_2_4 easy/ex2_1_1 medium/ex2_1_8 easy/ex5_4_3" \
VARIANTS="art raak:0 raak:1 raak:3 compo raakcompo:3" \
TLIM=60 bash "$HERE/wsl_raak_quick.sh" || { echo "*** compilacion fallida: no se lanza el barrido"; exit 1; }

"$TESTS/raak_arith_test" > /dev/null || { echo "*** prueba aritmetica fallida: no se lanza el barrido"; exit 1; }
echo
echo "== pruebas OK: barrido completo"
bash "$HERE/wsl_sweep_raak.sh"
