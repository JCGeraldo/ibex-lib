#!/usr/bin/env bash
# Fase 1, paso 1.3, segunda parte: diagnostico del fallo de (c) y aceptacion con el test corregido.
#   1. diagnostico: el binario viejo del test (productos k=0 y k=3 intercalados) vuelca con la
#      biblioteca actual; se compara con aa_ref_v1 ignorando noise_count e ids de rayos
#   2. test reestructurado (todos los k=0 antes de cualquier k=3): referencia con prefix-pre13
#      (c219009 + 0001 + 0002 + 0004 + 0005, ver wsl_build_prefix_pre.sh) y comparacion con prefix
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
TESTS="$ROOT/tests"; PREFIX="$ROOT/prefix"; PRE="$ROOT/prefix-pre13"; REF="$ROOT/results/fase1-ref"
TMP="$ROOT/tmp"; mkdir -p "$TMP"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUTDIR="$ROOT/results/fase1-$STAMP/paso13"; mkdir -p "$OUTDIR"
fail () { echo "*** $1"; exit 1; }

echo "== 1. diagnostico con el test viejo (intercalado) y la biblioteca actual"
[ -f "$REF/aa_ref_v1.txt" ] || mv "$REF/aa_ref.txt" "$REF/aa_ref_v1.txt"
"$TESTS/aa_knomial_test" --dump "$TMP/aa_post_v1.txt" | tail -1
strip () { awk '{ $2 = ""; for (i = 6; i <= NF; i++) sub(/^[0-9]+:/, "", $i); print }' "$1"; }
strip "$REF/aa_ref_v1.txt" > "$TMP/a.txt"; strip "$TMP/aa_post_v1.txt" > "$TMP/b.txt"
echo "   lineas: $(wc -l < "$TMP/a.txt") / $(wc -l < "$TMP/b.txt")"
echo "   lineas distintas CON ids y noise_count: $(diff "$REF/aa_ref_v1.txt" "$TMP/aa_post_v1.txt" | grep -c '^<')"
echo "   lineas distintas SIN ids ni noise_count: $(diff "$TMP/a.txt" "$TMP/b.txt" | grep -c '^<')"
echo "   par 14 pre : $(sed -n '15p' "$REF/aa_ref_v1.txt" | cut -c1-150)"
echo "   par 14 post: $(sed -n '15p' "$TMP/aa_post_v1.txt" | cut -c1-150)"

echo "== 2. test reestructurado: copiar y compilar contra prefix-pre13"
cp "$REPO/raak/tests/aa_knomial_test.cpp" "$TESTS/"; sed -i 's/\r$//' "$TESTS/aa_knomial_test.cpp"
grep -q "for (int t = 0; t < T; t++) z0s.push_back" "$TESTS/aa_knomial_test.cpp" || fail "el test copiado no es el reestructurado"
export PKG_CONFIG_PATH="$PRE/share/pkgconfig:$PRE/lib/pkgconfig:$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig"
echo "   biblioteca pre: $(find "$PRE" -name 'libibex-affine*' -printf '%f ')"
grep -q aa_products "$PRE/include/ibex-affine/ibex_KNomial.h" && fail "prefix-pre13 tiene el 0006"
g++ -std=c++11 -O2 -msse3 -frounding-math "$TESTS/aa_knomial_test.cpp" $(pkg-config --cflags ibex-affine ibex) \
    -o "$TESTS/aa_knomial_test_pre" $(pkg-config --libs ibex-affine ibex) || fail "build pre"
LD_LIBRARY_PATH="$PRE/lib:${LD_LIBRARY_PATH:-}" "$TESTS/aa_knomial_test_pre" --dump "$REF/aa_ref.txt" || fail "dump pre"
echo "   lineas en aa_ref.txt: $(wc -l < "$REF/aa_ref.txt")  md5: $(md5sum "$REF/aa_ref.txt" | cut -c1-12)"
cp "$REF/aa_ref.txt" "$REF/aa_ref_v1.txt" "$REPO/raak/results/04-fase1-validacion/fase1-ref/"

echo "== 3. compilar contra prefix (0006) y comparar"
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig"
grep -q aa_products "$PREFIX/include/ibex-affine/ibex_KNomial.h" || fail "prefix no tiene el 0006"
g++ -std=c++11 -O2 -msse3 -frounding-math -DRAA_AA_STATS "$TESTS/aa_knomial_test.cpp" $(pkg-config --cflags ibex-affine ibex) \
    -o "$TESTS/aa_knomial_test" $(pkg-config --libs ibex-affine ibex) || fail "build post"
"$TESTS/aa_knomial_test" --compare "$REF/aa_ref.txt" | tee "$OUTDIR/aa_knomial_test.txt"
mkdir -p "$REPO/raak/results/04-fase1-validacion/fase1-$STAMP/paso13"; cp "$OUTDIR/aa_knomial_test.txt" "$REPO/raak/results/04-fase1-validacion/fase1-$STAMP/paso13/"
echo "== listo"
