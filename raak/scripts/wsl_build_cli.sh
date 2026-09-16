#!/usr/bin/env bash
# F3: arma ~/ibex-local/ibexopt-raak con los archivos cli_* que estan junto a este
# script, lo compila contra ~/ibex-local/prefix y corre ex5_4_3.bch con las tres
# relajaciones lineales disponibles (xn, art, compo).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HOME/ibex-local"
PREFIX="$ROOT/prefix"
LOGS="$ROOT/logs"
CLI="$ROOT/ibexopt-raak"
JOBS="${JOBS:-8}"
BENCH="$ROOT/ibex-lib/benchs/optim/easy/ex5_4_3.bch"
mkdir -p "$CLI/src/bin" "$LOGS"

trap 'echo; echo "*** FALLO. Ultimas lineas del log correspondiente:"; tail -40 "$CURRENT_LOG" 2>/dev/null' ERR

echo "== copiando fuentes a $CLI"
cp "$HERE/cli_CMakeLists.txt"               "$CLI/CMakeLists.txt"
cp "$HERE/cli_Optimizer04Config_Affine.h"   "$CLI/src/ibex_Optimizer04Config_Affine.h"
cp "$HERE/cli_Optimizer04Config_Affine.cpp" "$CLI/src/ibex_Optimizer04Config_Affine.cpp"
cp "$HERE/cli_ibexopt_raak.cpp"             "$CLI/src/bin/ibexopt_raak.cpp"
cp "$ROOT/ibex-lib/src/bin/parse_args.h"    "$CLI/src/bin/parse_args.h"

CURRENT_LOG="$LOGS/cli-cmake.log"
echo "== configurando (log: $CURRENT_LOG)"
cmake -S "$CLI" -B "$CLI/build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$PREFIX" \
      > "$CURRENT_LOG" 2>&1

CURRENT_LOG="$LOGS/cli-make.log"
echo "== compilando (log: $CURRENT_LOG)"
make -C "$CLI/build" -j"$JOBS" > "$CURRENT_LOG" 2>&1
echo "   binario: $CLI/build/ibexopt-raak"

for lr in xn art compo; do
  CURRENT_LOG="$LOGS/cli-ex5_4_3-$lr.log"
  echo
  echo "== ex5_4_3.bch con --lr=$lr (log: $CURRENT_LOG)"
  start=$(date +%s.%N)
  timeout 600 "$CLI/build/ibexopt-raak" --lr="$lr" -t 300 "$BENCH" > "$CURRENT_LOG" 2>&1
  end=$(date +%s.%N)
  awk -v a="$start" -v b="$end" 'BEGIN { printf "   tiempo de pared: %.2f s\n", b - a }'
  grep -iE "successful|infeasible|time limit|f\* in|best bound|cpu time|number of cells" "$CURRENT_LOG" | sed 's/^/   /' || true
done
