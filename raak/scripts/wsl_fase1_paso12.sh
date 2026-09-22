#!/usr/bin/env bash
# Fase 1, paso 1.2 (parche 0005, corner test). Orden obligatorio:
#   A. con la biblioteca INSTALADA del paso 1.1, volcar la referencia bit a bit corner_ref.txt
#      (raa_corner_test --dump, compilado sin -DRAA_CORNER_STATS porque esa cabecera no tiene los contadores)
#   B. compilar/instalar el 0005, recompilar el CLI, knomial_golden, raak_arith_test
#   C. raa_corner_test --compare (con -DRAA_CORNER_STATS)
#   D. regresion: 7 instancias con --arith=af2 --knomial_k=0 identicas a la referencia
#   E. tabla ex8_4_4bis / bearing x {art, compo} x {raa k=0, raa k=3}: celdas antes (referencia) y con corner
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
S="$ROOT/scripts"; TESTS="$ROOT/tests"; PREFIX="$ROOT/prefix"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
BENCHS="$ROOT/ibex-lib/benchs/optim"
REF="$ROOT/results/fase1-ref"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUTDIR="$ROOT/results/fase1-$STAMP/paso12"
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fail () { echo "*** $1"; exit 1; }
mkdir -p "$OUTDIR"

echo "== 0. copiar cli_*, tests y scripts del repo (sin CR)"
cp "$REPO"/raak/cli/cli_* "$S"/; cp "$REPO"/raak/tests/*.cpp "$TESTS"/; cp "$REPO"/raak/scripts/*.sh "$S"/
sed -i 's/\r$//' "$S"/cli_* "$TESTS"/*.cpp "$S"/*.sh; chmod +x "$S"/*.sh
for f in ibex-affine/src/arithmetic/ibex_KNomial.h ibex-affine/src/arithmetic/ibex_Affine2_fAF2.cpp; do
  c=$(grep -c $'\r' "$ROOT/$f" || true); echo "   $f CR=$c"; [ "$c" = 0 ] || fail "CR en $f"
done

echo "== A. corner_ref.txt con la biblioteca instalada del paso 1.1 ($(date +%T))"
HDR_INST="$(find "$PREFIX/include" -name ibex_KNomial.h | head -1)"; [ -n "$HDR_INST" ] || fail "no hay ibex_KNomial.h instalada"
grep -q corner_products "$HDR_INST" && fail "la cabecera instalada ya tiene el 0005: la referencia debe volcarse antes"
g++ -std=c++11 -O2 -msse3 -frounding-math "$TESTS/raa_corner_test.cpp" $(pkg-config --cflags ibex-affine ibex) \
    -o "$TESTS/raa_corner_test_pre" $(pkg-config --libs ibex-affine ibex) || fail "build raa_corner_test (pre)"
"$TESTS/raa_corner_test_pre" --dump "$REF/corner_ref.txt" || fail "dump"
echo "   lineas en corner_ref.txt: $(wc -l < "$REF/corner_ref.txt")  md5: $(md5sum "$REF/corner_ref.txt" | cut -c1-12)"
cp "$REF/corner_ref.txt" "$REPO/raak/results/fase1-ref/corner_ref.txt"

echo "== B. ibex-affine: make ($(date +%T))"
make -C "$ROOT/ibex-affine/build" -j12 > "$ROOT/logs/p12-make.log" 2>&1 || { tail -30 "$ROOT/logs/p12-make.log"; fail "make"; }
grep -E "warning" "$ROOT/logs/p12-make.log" | head -5 || true
echo "== B. make check"
make -C "$ROOT/ibex-affine/build" check > "$ROOT/logs/p12-check.log" 2>&1; grep -E "tests passed|tests failed" "$ROOT/logs/p12-check.log"
echo "== B. make install"
make -C "$ROOT/ibex-affine/build" install > "$ROOT/logs/p12-install.log" 2>&1 || fail "install"
grep -q corner_products "$HDR_INST" || fail "la cabecera instalada no tiene el 0005"
echo "== B. CLI"
bash "$S/wsl_build_cli.sh" > "$ROOT/logs/p12-cli.log" 2>&1 || { tail -30 "$ROOT/logs/p12-cli.log"; fail "cli"; }
grep -E "binario|number of cells" "$ROOT/logs/p12-cli.log" | sed 's/^/   /'
echo "== B. knomial_golden"
g++ -std=c++11 -O2 -I "$ROOT/ibex-affine/src/arithmetic" "$TESTS/knomial_golden.cpp" -o "$TESTS/knomial_golden" || fail "golden build"
"$TESTS/knomial_golden" "$TESTS/knomial_golden.txt"
echo "== B. raak_arith_test"
bash "$S/wsl_run_test.sh" raak_arith_test

echo "== C. raa_corner_test --compare ($(date +%T))"
g++ -std=c++11 -O2 -msse3 -frounding-math -DRAA_CORNER_STATS "$TESTS/raa_corner_test.cpp" $(pkg-config --cflags ibex-affine ibex) \
    -o "$TESTS/raa_corner_test" $(pkg-config --libs ibex-affine ibex) || fail "build raa_corner_test"
"$TESTS/raa_corner_test" --compare "$REF/corner_ref.txt" | tee "$OUTDIR/raa_corner_test.txt"

echo "== D. regresion AF2/k=0 (7 instancias, -t 300) ($(date +%T))"
OUT="$OUTDIR/regresion_af2" TLIM=300 P=4 REF="$REF/ref_merged.csv" \
VARIANTS="art=--lr=art --arith=af2 --knomial_k=0;compo=--lr=compo --arith=af2 --knomial_k=0" \
MAP="art=art,;compo=compo," bash "$S/wsl_fase1_runs.sh" | tail -20

echo "== E. corner en ex8_4_4bis y bearing ($(date +%T))"
OUT="$OUTDIR/corner" TLIM=300 P=4 REF="$REF/ref_merged.csv" INSTS="medium/ex8_4_4bis medium/bearing" \
VARIANTS="raak_1=--lr=art --arith=raa --knomial_k=0;raak_3=--lr=art --arith=raa --knomial_k=3;raakcompo_1=--lr=compo --arith=raa --knomial_k=0;raakcompo_3=--lr=compo --arith=raa --knomial_k=3" \
MAP="raak_1=raak,1;raak_3=raak,3;raakcompo_1=raakcompo,1;raakcompo_3=raakcompo,3" bash "$S/wsl_fase1_runs.sh" | tail -14
echo "   stats:"; grep -h "RAA-K stats" "$OUTDIR"/corner/logs/*.log | sed 's/^/   /'
for f in "$OUTDIR"/corner/logs/*.log; do printf "   %-45s %s\n" "$(basename "$f" .log)" "$(grep -oE 'corner_products=[0-9]+ corner_used=[0-9]+ cruces_vs_fAF2=[0-9.]+' "$f")"; done

mkdir -p "$REPO/raak/results/fase1-$STAMP/paso12"
cp "$OUTDIR/raa_corner_test.txt" "$REPO/raak/results/fase1-$STAMP/paso12/"
for d in regresion_af2 corner; do mkdir -p "$REPO/raak/results/fase1-$STAMP/paso12/$d"; cp "$OUTDIR/$d"/{runs.csv,comparacion.txt,meta.txt} "$REPO/raak/results/fase1-$STAMP/paso12/$d/"; done
echo "== listo ($(date +%T))"
