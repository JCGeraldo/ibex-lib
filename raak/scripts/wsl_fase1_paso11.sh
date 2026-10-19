#!/usr/bin/env bash
# Fase 1, paso 1.1 (parche 0004): recompila ibex-affine con los dos interruptores, reinstala,
# recompila el CLI y corre la ACEPTACION del paso: knomial_golden, raak_arith_test (salida identica
# a la del paso 1.0), --arith=aa rechazado, y 7 instancias x 6 variantes comparadas con la referencia
# fusionada (filas SUCCESS de ref.csv + ref_t300.csv), con -t 300.
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
S="$ROOT/scripts"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
BENCHS="$ROOT/ibex-lib/benchs/optim"
REF="$ROOT/results/fase1-ref"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUTDIR="$ROOT/results/fase1-$STAMP/paso11"
fail () { echo "*** $1"; exit 1; }

echo "== 0. fuentes editadas sin CR"
for f in ibex-affine/src/arithmetic/ibex_KNomial.h ibex-affine/src/arithmetic/ibex_Affine2_fAF2.cpp; do
  c=$(grep -c $'\r' "$ROOT/$f" || true); echo "   $f CR=$c"; [ "$c" = 0 ] || fail "CR en $f"
done

echo "== 1. copiar cli_*, tests y scripts del repo (sin CR)"
cp "$REPO"/raak/cli/cli_* "$S"/; cp "$REPO"/raak/tests/*.cpp "$ROOT/tests"/; cp "$REPO"/raak/scripts/*.sh "$S"/
sed -i 's/\r$//' "$S"/cli_* "$ROOT/tests"/*.cpp "$S"/*.sh; chmod +x "$S"/*.sh

echo "== 2. ibex-affine: make ($(date +%T))"
make -C "$ROOT/ibex-affine/build" -j12 > "$ROOT/logs/p11-make.log" 2>&1 || { tail -30 "$ROOT/logs/p11-make.log"; fail "make"; }
grep -E "warning" "$ROOT/logs/p11-make.log" | head -5 || true
echo "== 2. make check"
make -C "$ROOT/ibex-affine/build" check > "$ROOT/logs/p11-check.log" 2>&1; grep -E "tests passed|tests failed" "$ROOT/logs/p11-check.log"
echo "== 2. make install"
make -C "$ROOT/ibex-affine/build" install > "$ROOT/logs/p11-install.log" 2>&1 || fail "install"

echo "== 3. CLI ($(date +%T))"
bash "$S/wsl_build_cli.sh" > "$ROOT/logs/p11-cli.log" 2>&1 || { tail -30 "$ROOT/logs/p11-cli.log"; fail "cli"; }
grep -E "binario|number of cells|f\* in|arith=" "$ROOT/logs/p11-cli.log" | sed 's/^/   /'

echo "== 4. knomial_golden"
g++ -std=c++11 -O2 -I "$ROOT/ibex-affine/src/arithmetic" "$ROOT/tests/knomial_golden.cpp" -o "$ROOT/tests/knomial_golden" || fail "golden build"
"$ROOT/tests/knomial_golden" "$ROOT/tests/knomial_golden.txt"

echo "== 5. raak_arith_test (con set_mode)"
bash "$S/wsl_run_test.sh" raak_arith_test

echo "== 6. --arith=aa debe rechazarse"
"$BIN" --lr=art --arith=aa -t 5 "$BENCHS/easy/ex5_4_3.bch" 2>&1 | tail -1; echo "   exit=${PIPESTATUS[0]}"
echo "== 6. --knomial_k=1 debe rechazarse"
"$BIN" --lr=art --knomial_k=1 -t 5 "$BENCHS/easy/ex5_4_3.bch" 2>&1 | tail -1; echo "   exit=${PIPESTATUS[0]}"

echo "== 7. referencia fusionada"
awk -F, 'NR==FNR { if (FNR>1) t[$1","$2","$3]=$0; next }
         FNR==1 { print; next }
         { k=$1","$2","$3; if (k in t) { print t[k]; delete t[k] } else if ($4!="TIME_OUT") print }
         END { for (k in t) print t[k] }' "$REF/ref_t300.csv" "$REF/ref.csv" > "$REF/ref_merged.csv"
echo "   filas: $(( $(wc -l < "$REF/ref_merged.csv") - 1 )) (TIME_OUT restantes: $(grep -c TIME_OUT "$REF/ref_merged.csv" || true))"
cp "$REF/ref_merged.csv" "$REPO/raak/results/04-fase1-validacion/fase1-ref/"

echo "== 8. corridas ($(date +%T))"
OUT="$OUTDIR" TLIM=300 P=4 REF="$REF/ref_merged.csv" \
VARIANTS="art=--lr=art --arith=af2 --knomial_k=0;raak_1=--lr=art --arith=raa --knomial_k=0;raak_3=--lr=art --arith=raa --knomial_k=3;raakcompo_3=--lr=compo --arith=raa --knomial_k=3;alias_raak_1=--lr=raak --raak_k=1;art_af2_k3=--lr=art --arith=af2 --knomial_k=3" \
MAP="art=art,;raak_1=raak,1;raak_3=raak,3;raakcompo_3=raakcompo,3;alias_raak_1=raak,1" \
bash "$S/wsl_fase1_runs.sh"

echo "== 9. lineas [compat] y arith= del alias"
grep -hE "^\[compat\]|^arith=|^affine_mode=" "$OUTDIR/logs/easy__ex5_4_3__alias_raak_1.log"
echo "== 9. stats de art_af2_k3 (variante nueva)"
grep -h "RAA-K stats" "$OUTDIR"/logs/*__art_af2_k3.log | sed 's/^/   /'

mkdir -p "$REPO/raak/results/04-fase1-validacion/fase1-$STAMP/paso11"
cp "$OUTDIR"/runs.csv "$OUTDIR"/comparacion.txt "$OUTDIR"/meta.txt "$REPO/raak/results/04-fase1-validacion/fase1-$STAMP/paso11/"
echo "== listo ($(date +%T))"
