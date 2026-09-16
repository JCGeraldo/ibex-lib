#!/usr/bin/env bash
# F1: compila e instala el fork de ibex-lib en ~/ibex-local/prefix
# y corre el benchmark del tutorial (ex5_4_3.bch con --lr=xn por defecto).
set -euo pipefail

ROOT="$HOME/ibex-local"
SRC="$ROOT/ibex-lib"
BUILD="$SRC/build"
PREFIX="$ROOT/prefix"
LOGS="$ROOT/logs"
JOBS="${JOBS:-8}"   # 8 de 12 hilos: deja margen para que Windows siga usable
mkdir -p "$BUILD" "$PREFIX" "$LOGS"

trap 'echo; echo "*** FALLO. Ultimas lineas del log correspondiente:"; tail -40 "$CURRENT_LOG" 2>/dev/null' ERR

CURRENT_LOG="$LOGS/ibexlib-cmake.log"
echo "== configurando (log: $CURRENT_LOG)"
cmake -S "$SRC" -B "$BUILD" \
      -DCMAKE_BUILD_TYPE=Release \
      -DLP_LIB=soplex \
      -DCMAKE_INSTALL_PREFIX="$PREFIX" \
      > "$CURRENT_LOG" 2>&1
grep -iE "Configuring Ibex|interval library|Linear Programming|soplex|gaol|filib" "$CURRENT_LOG" | head -8 || true

CURRENT_LOG="$LOGS/ibexlib-make.log"
echo "== compilando con -j$JOBS (log: $CURRENT_LOG)"
start=$(date +%s)
make -C "$BUILD" -j"$JOBS" > "$CURRENT_LOG" 2>&1
echo "   compilado en $(( $(date +%s) - start )) s"

CURRENT_LOG="$LOGS/ibexlib-install.log"
echo "== instalando en $PREFIX (log: $CURRENT_LOG)"
make -C "$BUILD" install > "$CURRENT_LOG" 2>&1
echo "   cabeceras de Optimizer04Config instaladas: $(find "$PREFIX" -name 'ibex_Optimizer04Config.h' | wc -l)"

CURRENT_LOG="$LOGS/ibexlib-tutorial.log"
echo "== prueba del tutorial: ibexopt04 benchs/optim/easy/ex5_4_3.bch (log: $CURRENT_LOG)"
cd "$SRC"
timeout 600 "$BUILD/bin/ibexopt04" benchs/optim/easy/ex5_4_3.bch > "$CURRENT_LOG" 2>&1
tail -25 "$CURRENT_LOG"
