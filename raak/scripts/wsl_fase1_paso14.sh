#!/usr/bin/env bash
# Fase 1, paso 1.4 (parche 0007, LinearizerAffineT). Tramo 1: compilar/instalar, CLI y tests.
# Los tramos de corridas van aparte (wsl_fase1_paso14_runs.sh) para no superar 10 min por llamada.
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
S="$ROOT/scripts"; TESTS="$ROOT/tests"; PREFIX="$ROOT/prefix"; REF="$ROOT/results/fase1-ref"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"; BENCHS="$ROOT/ibex-lib/benchs/optim"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUTDIR="$ROOT/results/fase1-$STAMP/paso14"; mkdir -p "$OUTDIR"
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig"
fail () { echo "*** $1"; exit 1; }

echo "== 0. copiar cli_*, tests y scripts del repo (sin CR)"
cp "$REPO"/raak/cli/cli_* "$S"/; cp "$REPO"/raak/tests/*.cpp "$TESTS"/; cp "$REPO"/raak/scripts/*.sh "$S"/
sed -i 's/\r$//' "$S"/cli_* "$TESTS"/*.cpp "$S"/*.sh; chmod +x "$S"/*.sh
for f in src/arithmetic/ibex_KNomial.h src/arithmetic/ibex_AffineMain.h src/arithmetic/ibex_AffineMain_impl.h \
         src/arithmetic/ibex_Affine3_fAFFullI.cpp src/numeric/ibex_LinearizerAffine2.h src/numeric/ibex_LinearizerAffine2.cpp; do
  c=$(grep -c $'\r' "$ROOT/ibex-affine/$f" || true); echo "   $f CR=$c"; [ "$c" = 0 ] || fail "CR en $f"
done

echo "== 1. ibex-affine: make ($(date +%T))"
make -C "$ROOT/ibex-affine/build" -j12 > "$ROOT/logs/p14-make.log" 2>&1 || { grep -E "error|Error" -A3 "$ROOT/logs/p14-make.log" | head -60; fail "make"; }
grep -E "warning" "$ROOT/logs/p14-make.log" | head -5 || true
echo "== 1. make check"
make -C "$ROOT/ibex-affine/build" check > "$ROOT/logs/p14-check.log" 2>&1; grep -E "tests passed|tests failed" "$ROOT/logs/p14-check.log"
echo "== 1. make install"
make -C "$ROOT/ibex-affine/build" install > "$ROOT/logs/p14-install.log" 2>&1 || fail "install"
grep -q "LinearizerAffineT" "$PREFIX/include/ibex-affine/ibex_LinearizerAffine2.h" || fail "cabecera del linearizador no instalada"

echo "== 2. CLI ($(date +%T))"
bash "$S/wsl_build_cli.sh" > "$ROOT/logs/p14-cli.log" 2>&1 || { grep -E "error" -A3 "$ROOT/logs/p14-cli.log" | head -40; fail "cli"; }
grep -E "binario|number of cells" "$ROOT/logs/p14-cli.log" | sed 's/^/   /'
echo "== 2. --arith=aa en ex5_4_3 (art y compo, -t 120)"
for lr in art compo; do
  "$BIN" --lr=$lr --arith=aa --knomial_k=0 -t 120 "$BENCHS/easy/ex5_4_3.bch" 2>&1 | sed -r 's/\x1b\[[0-9;]*m//g' \
    | grep -E "^arith=|linearizador=|optimization successful|f\* in|cpu time|number of cells|RAA-K stats" | sed "s/^/   [$lr aa k0] /"
done

echo "== 3. tests ($(date +%T))"
g++ -std=c++11 -O2 -I "$ROOT/ibex-affine/src/arithmetic" "$TESTS/knomial_golden.cpp" -o "$TESTS/knomial_golden" || fail "golden build"
"$TESTS/knomial_golden" "$TESTS/knomial_golden.txt" | tail -1
bash "$S/wsl_run_test.sh" raak_arith_test | tail -1
CFL="$(pkg-config --cflags ibex-affine ibex)"; LFL="$(pkg-config --libs ibex-affine ibex)"
g++ -std=c++11 -O2 -msse3 -frounding-math -DRAA_CORNER_STATS "$TESTS/raa_corner_test.cpp" $CFL -o "$TESTS/raa_corner_test" $LFL || fail "build corner"
"$TESTS/raa_corner_test" --compare "$REF/corner_ref.txt" | grep -E "violaciones|CORNER"
g++ -std=c++11 -O2 -msse3 -frounding-math -DRAA_AA_STATS "$TESTS/aa_knomial_test.cpp" $CFL -o "$TESTS/aa_knomial_test" $LFL || fail "build aa_knomial"
"$TESTS/aa_knomial_test" --compare "$REF/aa_ref.txt" | grep -E "violaciones|AA KNOMIAL"
echo "== 3. aa_linearizer_test"
g++ -std=c++11 -O2 -msse3 -frounding-math "$TESTS/aa_linearizer_test.cpp" $CFL -o "$TESTS/aa_linearizer_test" $LFL 2> "$ROOT/logs/p14-lintest-build.log" \
  || { grep -E "error" -A3 "$ROOT/logs/p14-lintest-build.log" | head -40; fail "build aa_linearizer_test"; }
"$TESTS/aa_linearizer_test" | tee "$OUTDIR/aa_linearizer_test.txt"
mkdir -p "$REPO/raak/results/04-fase1-validacion/fase1-$STAMP/paso14"; cp "$OUTDIR/aa_linearizer_test.txt" "$REPO/raak/results/04-fase1-validacion/fase1-$STAMP/paso14/"
echo "== listo ($(date +%T))"
