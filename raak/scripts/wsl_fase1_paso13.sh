#!/usr/bin/env bash
# Fase 1, paso 1.3 (parche 0006, k-nomial en AF_fAFFullI). Orden obligatorio:
#   A. con la biblioteca INSTALADA del paso 1.2, volcar aa_ref.txt (aa_knomial_test --dump, k=0)
#   B. compilar/instalar el 0006, CLI, knomial_golden, raak_arith_test, raa_corner_test --compare
#   C. aa_knomial_test --compare (con -DRAA_AA_STATS)
#   D. regresion: 7 instancias x {art, compo} con --arith=af2 --knomial_k=0 identicas a la referencia
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
S="$ROOT/scripts"; TESTS="$ROOT/tests"; PREFIX="$ROOT/prefix"
REF="$ROOT/results/fase1-ref"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUTDIR="$ROOT/results/fase1-$STAMP/paso13"
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fail () { echo "*** $1"; exit 1; }
mkdir -p "$OUTDIR"
CFL="$(pkg-config --cflags ibex-affine ibex)"; LFL="$(pkg-config --libs ibex-affine ibex)"

echo "== 0. copiar cli_*, tests y scripts del repo (sin CR)"
cp "$REPO"/raak/cli/cli_* "$S"/; cp "$REPO"/raak/tests/*.cpp "$TESTS"/; cp "$REPO"/raak/scripts/*.sh "$S"/
sed -i 's/\r$//' "$S"/cli_* "$TESTS"/*.cpp "$S"/*.sh; chmod +x "$S"/*.sh
for f in ibex-affine/src/arithmetic/ibex_KNomial.h ibex-affine/src/arithmetic/ibex_Affine3_fAFFullI.cpp; do
  c=$(grep -c $'\r' "$ROOT/$f" || true); echo "   $f CR=$c"; [ "$c" = 0 ] || fail "CR en $f"
done

echo "== A. aa_ref.txt con la biblioteca instalada del paso 1.2 ($(date +%T))"
HDR_INST="$(find "$PREFIX/include" -name ibex_KNomial.h | head -1)"; [ -n "$HDR_INST" ] || fail "sin cabecera instalada"
grep -q aa_products "$HDR_INST" && fail "la cabecera instalada ya tiene el 0006: la referencia debe volcarse antes"
g++ -std=c++11 -O2 -msse3 -frounding-math "$TESTS/aa_knomial_test.cpp" $CFL -o "$TESTS/aa_knomial_test_pre" $LFL || fail "build aa_knomial_test (pre)"
"$TESTS/aa_knomial_test_pre" --dump "$REF/aa_ref.txt" || fail "dump"
echo "   lineas en aa_ref.txt: $(wc -l < "$REF/aa_ref.txt")  md5: $(md5sum "$REF/aa_ref.txt" | cut -c1-12)"
cp "$REF/aa_ref.txt" "$REPO/raak/results/fase1-ref/aa_ref.txt"

echo "== B. ibex-affine: make ($(date +%T))"
make -C "$ROOT/ibex-affine/build" -j12 > "$ROOT/logs/p13-make.log" 2>&1 || { tail -40 "$ROOT/logs/p13-make.log"; fail "make"; }
grep -E "warning" "$ROOT/logs/p13-make.log" | head -5 || true
echo "== B. make check"
make -C "$ROOT/ibex-affine/build" check > "$ROOT/logs/p13-check.log" 2>&1; grep -E "tests passed|tests failed" "$ROOT/logs/p13-check.log"
echo "== B. make install"
make -C "$ROOT/ibex-affine/build" install > "$ROOT/logs/p13-install.log" 2>&1 || fail "install"
grep -q aa_products "$HDR_INST" || fail "la cabecera instalada no tiene el 0006"
echo "== B. CLI"
bash "$S/wsl_build_cli.sh" > "$ROOT/logs/p13-cli.log" 2>&1 || { tail -30 "$ROOT/logs/p13-cli.log"; fail "cli"; }
grep -E "binario|number of cells" "$ROOT/logs/p13-cli.log" | sed 's/^/   /'
echo "== B. knomial_golden"
g++ -std=c++11 -O2 -I "$ROOT/ibex-affine/src/arithmetic" "$TESTS/knomial_golden.cpp" -o "$TESTS/knomial_golden" || fail "golden build"
"$TESTS/knomial_golden" "$TESTS/knomial_golden.txt"
echo "== B. raak_arith_test"
bash "$S/wsl_run_test.sh" raak_arith_test | tail -4
echo "== B. raa_corner_test --compare"
g++ -std=c++11 -O2 -msse3 -frounding-math -DRAA_CORNER_STATS "$TESTS/raa_corner_test.cpp" $CFL -o "$TESTS/raa_corner_test" $LFL || fail "build raa_corner_test"
"$TESTS/raa_corner_test" --compare "$REF/corner_ref.txt" | grep -E "violaciones|biblioteca|CORNER"

echo "== C. aa_knomial_test --compare ($(date +%T))"
g++ -std=c++11 -O2 -msse3 -frounding-math -DRAA_AA_STATS "$TESTS/aa_knomial_test.cpp" $CFL -o "$TESTS/aa_knomial_test" $LFL || fail "build aa_knomial_test"
"$TESTS/aa_knomial_test" --compare "$REF/aa_ref.txt" | tee "$OUTDIR/aa_knomial_test.txt"

echo "== D. regresion AF2/k=0 (7 instancias x {art, compo}, -t 300) ($(date +%T))"
OUT="$OUTDIR/regresion_af2" TLIM=300 P=4 REF="$REF/ref_merged.csv" \
VARIANTS="art=--lr=art --arith=af2 --knomial_k=0;compo=--lr=compo --arith=af2 --knomial_k=0" \
MAP="art=art,;compo=compo," bash "$S/wsl_fase1_runs.sh" | tail -17

mkdir -p "$REPO/raak/results/fase1-$STAMP/paso13/regresion_af2"
cp "$OUTDIR/aa_knomial_test.txt" "$REPO/raak/results/fase1-$STAMP/paso13/"
cp "$OUTDIR/regresion_af2"/{runs.csv,comparacion.txt,meta.txt} "$REPO/raak/results/fase1-$STAMP/paso13/regresion_af2/"
echo "== listo ($(date +%T))"
