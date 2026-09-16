#!/usr/bin/env bash
# F5: recompila ibex-affine y el CLI tras un cambio del prototipo RAA-K, repite la
# prueba aritmetica y corre una verificacion corta con ablacion de raak_k.
# Variable opcional SP: carpeta desde donde copiar las fuentes del CLI y las pruebas.
set -euo pipefail

ROOT="$HOME/ibex-local"
HERE="$ROOT/scripts"
PREFIX="$ROOT/prefix"
LOGS="$ROOT/logs"
TESTS="$ROOT/tests"
JOBS="${JOBS:-8}"
TLIM="${TLIM:-60}"
INSTS="${INSTS:-easy/ex5_4_3 easy/wall easy/ex14_2_4 medium/alkyl easy/ex2_1_1}"
VARIANTS="${VARIANTS:-art raak:0 raak:1 raak:2 raak:3 compo raakcompo:0 raakcompo:3}"

if [ -n "${SP:-}" ]; then
  cp "$SP/cli_Optimizer04Config_Affine.cpp" "$SP/cli_ibexopt_raak.cpp" "$HERE/"
  cp "$SP/raak_arith_test.cpp" "$TESTS/"
fi

echo "== ibex-affine: compilar, tests, instalar"
make -C "$ROOT/ibex-affine/build" -j"$JOBS" > "$LOGS/raak-affine-make.log" 2>&1 \
  || { tail -30 "$LOGS/raak-affine-make.log"; exit 1; }
make -C "$ROOT/ibex-affine/build" check ARGS="--no-tests=error" > "$LOGS/raak-affine-check.log" 2>&1 || true
grep -E "tests passed|tests failed" "$LOGS/raak-affine-check.log" | sed 's/^/   /' || true
make -C "$ROOT/ibex-affine/build" install > "$LOGS/raak-affine-install.log" 2>&1

echo
echo "== prueba aritmetica"
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
g++ -std=c++11 -O2 -msse3 -frounding-math "$TESTS/raak_arith_test.cpp" \
    $(pkg-config --cflags ibex-affine ibex) -o "$TESTS/raak_arith_test" \
    $(pkg-config --libs ibex-affine ibex) > "$LOGS/raak-arith-build.log" 2>&1 \
  || { tail -30 "$LOGS/raak-arith-build.log"; exit 1; }
"$TESTS/raak_arith_test" || echo "*** PRUEBA ARITMETICA FALLIDA"

echo
echo "== CLI"
bash "$HERE/wsl_build_cli.sh" > "$LOGS/raak-cli-build.log" 2>&1 \
  || { tail -30 "$LOGS/raak-cli-build.log"; exit 1; }
echo "   compilado"

echo
echo "== corridas cortas (limite $TLIM s)"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
printf "   %-16s %-12s %-12s %-8s %-8s %-40s %s\n" "instancia" "variante" "estado" "celdas" "cpu" "f* final" "estadisticas RAA-K"
for inst in $INSTS; do
  for var in $VARIANTS; do
    lr="${var%%:*}"
    k=""
    [ "$var" != "$lr" ] && k="${var#*:}"
    log="$LOGS/raak-quick-${inst//\//__}-${var/:/_k}.log"
    if [ -n "$k" ]; then
      timeout $((TLIM + 60)) "$BIN" --lr="$lr" --raak_k="$k" -t "$TLIM" "$ROOT/ibex-lib/benchs/optim/$inst.bch" > "$log" 2>&1 || true
    else
      timeout $((TLIM + 60)) "$BIN" --lr="$lr" -t "$TLIM" "$ROOT/ibex-lib/benchs/optim/$inst.bch" > "$log" 2>&1 || true
    fi
    clean=$(sed 's/\x1b\[[0-9;]*m//g' "$log")
    # ojo: el resumen de argumentos imprime "Time Limit: N", no confundirlo con el estado
    status="?"
    echo "$clean" | grep -qiE "time limit [0-9.e+]+ ?s reached" && status="tiempo"
    echo "$clean" | grep -qi "infeasible problem" && status="infactible"
    echo "$clean" | grep -qi "optimization successful" && status="resuelta"
    cells=$(echo "$clean" | grep -oE "number of cells:[^0-9]*[0-9]+" | grep -oE "[0-9]+$" | head -1)
    cpu=$(echo "$clean" | grep -oE "cpu time used:[^0-9]*[0-9.]+" | grep -oE "[0-9.]+$" | head -1)
    fstar=$(echo "$clean" | grep -oE "f\* in[[:space:]]*\[[^]]*\]" | sed 's/f\* in[[:space:]]*//' | head -1)
    stats=$(echo "$clean" | grep -oE "productos=.*" || true)
    printf "   %-16s %-12s %-12s %-8s %-8.3f %-40s %s\n" "$inst" "$var" "$status" "${cells:-?}" "${cpu:-0}" "${fstar:-?}" "$stats"
  done
done
