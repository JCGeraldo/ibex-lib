#!/usr/bin/env bash
# F5: compila el prototipo RAA-K de punta a punta y corre sus pruebas.
#   1. prueba dorada del port C++ de knomial contra raa_lib/knomial.py (solo cabecera)
#   2. ibex-lib (fork): recompila e instala (get_ctc acepta raak y raakcompo)
#   3. ibex-affine: compila, tests, instala (wsl_build_affine.sh)
#   4. prueba aritmetica de la multiplicacion k-nomial (contencion, pendientes, radio)
#   5. CLI ibexopt-raak (wsl_build_cli.sh)
#   6. corridas cortas: art frente a raak en algunas instancias
# Variable opcional SP: carpeta desde donde copiar fuentes nuevas antes de compilar.
set -euo pipefail

ROOT="$HOME/ibex-local"
HERE="$ROOT/scripts"
PREFIX="$ROOT/prefix"
LOGS="$ROOT/logs"
TESTS="$ROOT/tests"
JOBS="${JOBS:-8}"
mkdir -p "$LOGS" "$TESTS"

if [ -n "${SP:-}" ]; then
  echo "== copiando fuentes desde $SP"
  cp "$SP/cli_Optimizer04Config_Affine.cpp" "$SP/cli_ibexopt_raak.cpp" "$HERE/"
  cp "$SP/knomial_golden.cpp" "$SP/knomial_golden.txt" "$SP/raak_arith_test.cpp" "$TESTS/"
fi

echo
echo "== [1] prueba dorada de knomial (C++ contra Python)"
g++ -std=c++11 -O2 -Wall -I "$ROOT/ibex-affine/src/arithmetic" \
    "$TESTS/knomial_golden.cpp" -o "$TESTS/knomial_golden"
"$TESTS/knomial_golden" "$TESTS/knomial_golden.txt" || echo "*** PRUEBA DORADA FALLIDA"

echo
echo "== [2] ibex-lib: recompilar e instalar"
start=$(date +%s)
make -C "$ROOT/ibex-lib/build" -j"$JOBS" > "$LOGS/raak-ibexlib-make.log" 2>&1 \
  || { tail -30 "$LOGS/raak-ibexlib-make.log"; exit 1; }
make -C "$ROOT/ibex-lib/build" install > "$LOGS/raak-ibexlib-install.log" 2>&1
echo "   listo en $(( $(date +%s) - start )) s"

echo
echo "== [3] ibex-affine"
bash "$HERE/wsl_build_affine.sh"

echo
echo "== [4] prueba aritmetica de la multiplicacion k-nomial"
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
g++ -std=c++11 -O2 -msse3 -frounding-math "$TESTS/raak_arith_test.cpp" \
    $(pkg-config --cflags ibex-affine ibex) -o "$TESTS/raak_arith_test" \
    $(pkg-config --libs ibex-affine ibex) > "$LOGS/raak-arith-build.log" 2>&1 \
  || { tail -30 "$LOGS/raak-arith-build.log"; exit 1; }
"$TESTS/raak_arith_test" || echo "*** PRUEBA ARITMETICA FALLIDA"

echo
echo "== [5] CLI"
bash "$HERE/wsl_build_cli.sh"

echo
echo "== [6] corridas cortas (limite 60 s)"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
for inst in easy/ex5_4_3 easy/wall easy/ex2_1_1 medium/ex2_1_8 easy/ex14_2_4 medium/alkyl; do
  for lr in art raak compo raakcompo; do
    log="$LOGS/raak-quick-${inst//\//__}-$lr.log"
    timeout 120 "$BIN" --lr="$lr" -t 60 "$ROOT/ibex-lib/benchs/optim/$inst.bch" > "$log" 2>&1 || true
    status=$(grep -oiE "optimization successful|time limit [0-9.]+s reached|infeasible problem|no feasible point found" "$log" | head -1 | sed 's/\x1b\[[0-9;]*m//g')
    cells=$(grep -oE "number of cells:[^0-9]*[0-9]+" "$log" | grep -oE "[0-9]+$" | head -1)
    cpu=$(grep -oE "cpu time used:[^0-9]*[0-9.e+-]+" "$log" | grep -oE "[0-9.e+-]+$" | head -1)
    stats=$(grep -oE "productos=.*" "$log" || true)
    printf "   %-16s %-10s %-26s celdas=%-8s cpu=%-9s %s\n" "$inst" "$lr" "${status:-?}" "${cells:-?}" "${cpu:-?}" "$stats"
  done
done
