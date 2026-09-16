#!/usr/bin/env bash
# F2: compila ibex-affine (rama local 'raak') contra el ibex-lib instalado en
# ~/ibex-local/prefix, corre su suite de tests y lo instala en el mismo prefijo.
set -euo pipefail

ROOT="$HOME/ibex-local"
SRC="$ROOT/ibex-affine"
BUILD="$SRC/build"
PREFIX="$ROOT/prefix"
LOGS="$ROOT/logs"
JOBS="${JOBS:-8}"
mkdir -p "$BUILD" "$LOGS"

trap 'echo; echo "*** FALLO. Ultimas lineas del log correspondiente:"; tail -40 "$CURRENT_LOG" 2>/dev/null' ERR

CURRENT_LOG="$LOGS/affine-cmake.log"
echo "== configurando ibex-affine contra $PREFIX (log: $CURRENT_LOG)"
cmake -S "$SRC" -B "$BUILD" \
      -DCMAKE_BUILD_TYPE=Release \
      -DIBEX_DIR="$PREFIX" \
      -DCMAKE_INSTALL_PREFIX="$PREFIX" \
      > "$CURRENT_LOG" 2>&1
grep -iE "Found Ibex version|interval library|Linear Programming" "$CURRENT_LOG" || true

CURRENT_LOG="$LOGS/affine-make.log"
echo "== compilando con -j$JOBS (log: $CURRENT_LOG)"
start=$(date +%s)
make -C "$BUILD" -j"$JOBS" > "$CURRENT_LOG" 2>&1
echo "   compilado en $(( $(date +%s) - start )) s"

CURRENT_LOG="$LOGS/affine-check.log"
echo "== tests (make check, igual que el CI) (log: $CURRENT_LOG)"
start=$(date +%s)
make -C "$BUILD" check ARGS="--no-tests=error" > "$CURRENT_LOG" 2>&1
echo "   tests en $(( $(date +%s) - start )) s"
grep -E "tests passed|tests failed|Failed|OK \(" "$CURRENT_LOG" | tail -10 || true

CURRENT_LOG="$LOGS/affine-install.log"
echo "== instalando en $PREFIX (log: $CURRENT_LOG)"
make -C "$BUILD" install > "$CURRENT_LOG" 2>&1
echo "   instalado: $(find "$PREFIX" -name 'ibex_LinearizerAffine2.h' | wc -l) cabecera(s) de LinearizerAffine2, $(find "$PREFIX" -name 'libibex-affine*' | wc -l) archivo(s) de biblioteca"
