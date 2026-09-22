#!/usr/bin/env bash
# Fase 2, paso 2.1 (parche 0008, seno/coseno): recompila ibex-affine con los headers nuevos, corre
# make check, reinstala, recompila el CLI (con --trig) y corre la ACEPTACION del paso:
#   1. trig_lin_test (Fase 2.2): CSV + resumen; debe terminar con "TRIG OK"
#   2. los tests de la Fase 1 siguen igual: knomial_golden, raa_corner_test --compare,
#      aa_knomial_test --compare, aa_linearizer_test
#   3. regresion: 7 instancias de referencia (sin sin/cos) x {xn, art, compo} af2/k=0 con -t 300,
#      identicas a ref_merged.csv (el parche no debe cambiar nada donde no hay trigonometricas)
#   4. efecto en las instancias con sin/cos de easy (ex14_1_4, ex8_1_1, ex8_1_2) y others:
#      {art, compo} x trig {legacy, cheb, minrange} con af2/k=0, -t 120 (variantes nuevas, se registran)
#   5. guarda el parche 0008 con wsl_save_patch.sh y copia los resultados al repo
# Variables: STAMP (fecha), SKIP_BUILD=1 para saltar la compilacion.
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
S="$ROOT/scripts"; T="$ROOT/tests"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
BENCHS="$ROOT/ibex-lib/benchs/optim"
REF="$ROOT/results/fase1-ref"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUTDIR="$ROOT/results/fase2-$STAMP"
mkdir -p "$OUTDIR" "$ROOT/logs"
fail () { echo "*** $1"; exit 1; }
export PKG_CONFIG_PATH="$ROOT/prefix/share/pkgconfig:$ROOT/prefix/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
CFL="$(pkg-config --cflags ibex-affine ibex)"; LFL="$(pkg-config --libs ibex-affine ibex)"

echo "== 0. fuentes nuevas sin CR"
for f in ibex-affine/src/arithmetic/ibex_AffineTrig.h ibex-affine/src/arithmetic/ibex_AffineMain_trig_impl.h \
         ibex-affine/src/arithmetic/ibex_AffineMain.h ibex-affine/src/arithmetic/ibex_AffineMain_impl.h ibex-affine/src/CMakeLists.txt; do
  c=$(grep -c $'\r' "$ROOT/$f" || true); echo "   $f CR=$c"; [ "$c" = 0 ] || fail "CR en $f"
done

echo "== 1. copiar cli_*, tests y scripts del repo (sin CR)"
cp "$REPO"/raak/cli/cli_* "$S"/; cp "$REPO"/raak/tests/*.cpp "$T"/; cp "$REPO"/raak/scripts/*.sh "$S"/
sed -i 's/\r$//' "$S"/cli_* "$T"/*.cpp "$S"/*.sh; chmod +x "$S"/*.sh

if [ "${SKIP_BUILD:-0}" != 1 ]; then
  echo "== 2. ibex-affine: cmake + make ($(date +%T))"
  cmake -S "$ROOT/ibex-affine" -B "$ROOT/ibex-affine/build" > "$ROOT/logs/p21-cmake.log" 2>&1 || fail "cmake"
  make -C "$ROOT/ibex-affine/build" -j12 > "$ROOT/logs/p21-make.log" 2>&1 || { tail -30 "$ROOT/logs/p21-make.log"; fail "make"; }
  grep -E "warning" "$ROOT/logs/p21-make.log" | head -5 || true
  echo "== 2. make check"
  make -C "$ROOT/ibex-affine/build" check > "$ROOT/logs/p21-check.log" 2>&1; grep -E "tests passed|tests failed" "$ROOT/logs/p21-check.log"
  echo "== 2. make install"
  make -C "$ROOT/ibex-affine/build" install > "$ROOT/logs/p21-install.log" 2>&1 || fail "install"
  ls "$ROOT/prefix/include/ibex-affine/ibex_AffineTrig.h" > /dev/null || fail "header no instalado"
  echo "== 3. CLI ($(date +%T))"
  bash "$S/wsl_build_cli.sh" > "$ROOT/logs/p21-cli.log" 2>&1 || { tail -30 "$ROOT/logs/p21-cli.log"; fail "cli"; }
  grep -E "binario|number of cells|f\* in|arith=" "$ROOT/logs/p21-cli.log" | sed 's/^/   /'
fi

echo "== 4. trig_lin_test ($(date +%T))"
g++ -std=c++11 -O2 -msse3 -frounding-math "$T/trig_lin_test.cpp" $CFL -o "$T/trig_lin_test" $LFL 2> "$ROOT/logs/p21-trig-build.log" || { tail -20 "$ROOT/logs/p21-trig-build.log"; fail "build trig_lin_test"; }
"$T/trig_lin_test" > "$OUTDIR/trig_lin.csv" 2> "$OUTDIR/trig_lin_resumen.txt"; rc=$?
cat "$OUTDIR/trig_lin_resumen.txt"; echo "   filas: $(( $(wc -l < "$OUTDIR/trig_lin.csv") - 1 ))  exit=$rc"

echo "== 5. tests de la Fase 1 sin cambios"
g++ -std=c++11 -O2 -I "$ROOT/ibex-affine/src/arithmetic" "$T/knomial_golden.cpp" -o "$T/knomial_golden" && "$T/knomial_golden" "$T/knomial_golden.txt" | tail -1
g++ -std=c++11 -O2 -msse3 -frounding-math -DRAA_CORNER_STATS "$T/raa_corner_test.cpp" $CFL -o "$T/raa_corner_test" $LFL && "$T/raa_corner_test" --compare "$REF/corner_ref.txt" | tail -1
g++ -std=c++11 -O2 -msse3 -frounding-math -DRAA_AA_STATS "$T/aa_knomial_test.cpp" $CFL -o "$T/aa_knomial_test" $LFL && "$T/aa_knomial_test" --compare "$REF/aa_ref.txt" | tail -1
g++ -std=c++11 -O2 -msse3 -frounding-math "$T/aa_linearizer_test.cpp" $CFL -o "$T/aa_linearizer_test" $LFL && "$T/aa_linearizer_test" | tail -1

echo "== 6. regresion sin trigonometricas ($(date +%T))"
OUT="$OUTDIR/regresion" TLIM=300 P=6 REF="$REF/ref_merged.csv" \
VARIANTS="xn=--lr=xn;art=--lr=art --arith=af2 --knomial_k=0;compo=--lr=compo --arith=af2 --knomial_k=0" \
MAP="xn=xn,;art=art,;compo=compo," bash "$S/wsl_fase1_runs.sh" | tail -3

echo "== 7. instancias con sin/cos: efecto del modo ($(date +%T))"
OUT="$OUTDIR/trig_instancias" TLIM=120 P=6 \
INSTS="easy/ex14_1_4 easy/ex8_1_1 easy/ex8_1_2 others/ex4_1_7" \
VARIANTS="art_legacy=--lr=art --trig=legacy;art_cheb=--lr=art --trig=cheb;art_minrange=--lr=art --trig=minrange;compo_legacy=--lr=compo --trig=legacy;compo_cheb=--lr=compo --trig=cheb;compo_minrange=--lr=compo --trig=minrange;xn=--lr=xn" \
bash "$S/wsl_fase1_runs.sh" | grep -v "^\[" ; column -s, -t "$OUTDIR/trig_instancias/runs.csv" | cut -c1-150
echo "   TRIG stats:"; for f in "$OUTDIR"/trig_instancias/logs/*.log; do printf "   %-36s %s\n" "$(basename "$f" .log)" "$(grep -oE 'TRIG stats:.*' "$f" | cut -c13-)"; done

echo "== 8. parche 0008"
bash "$S/wsl_save_patch.sh" ibex-affine 0008-ibex-affine-trig-sin-cos-CH-MR.patch \
  0001-LinearizerAffine2-omitir-formas-no-activas.patch 0002-ibex-affine-RAA-K-multiplicacion-knomial.patch \
  0004-ibex-affine-separar-affine_mode-y-knomial_k.patch 0005-ibex-affine-RAA-corner-test-ec16.patch \
  0006-ibex-affine-knomial-en-fAFFullI.patch 0007-ibex-affine-LinearizerAffineT-Affine3.patch | tail -6

mkdir -p "$REPO/raak/results/fase2-$STAMP"
cp "$OUTDIR"/trig_lin.csv "$OUTDIR"/trig_lin_resumen.txt "$REPO/raak/results/fase2-$STAMP/"
for d in regresion trig_instancias; do mkdir -p "$REPO/raak/results/fase2-$STAMP/$d"; cp "$OUTDIR/$d"/{runs.csv,meta.txt} "$REPO/raak/results/fase2-$STAMP/$d/"; cp "$OUTDIR/$d"/comparacion.txt "$REPO/raak/results/fase2-$STAMP/$d/" 2>/dev/null; done
echo "== listo ($(date +%T))"
