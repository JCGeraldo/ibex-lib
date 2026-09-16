#!/usr/bin/env bash
# Compila crashtest.cpp contra ~/ibex-local/prefix (via pkg-config, como el CI de
# ibex-affine) y lo ejecuta sobre wall_sym.bch. Con -g por si luego hay gdb.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PREFIX="$HOME/ibex-local/prefix"
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:${PKG_CONFIG_PATH:-}"
export LD_LIBRARY_PATH="$PREFIX/lib:${LD_LIBRARY_PATH:-}"
BIN=/tmp/crashtest

if ! FLAGS="$(pkg-config --cflags --libs ibex-affine 2>&1)"; then
  echo "*** pkg-config no encontro ibex-affine: $FLAGS"
  exit 1
fi

echo "== compilando crashtest.cpp"
if ! g++ -std=c++17 -g -O0 "$HERE/crashtest.cpp" -o "$BIN" $FLAGS 2>/tmp/crashtest-build.log; then
  echo "*** no compilo. Primeras lineas del error:"
  head -30 /tmp/crashtest-build.log
  exit 1
fi

echo "== ejecutando"
cd "$HERE"
"$BIN" "$HERE/wall_sym.bch"
code=$?
echo "== exit $code   (0 = sin fallas, 139 = segfault, 134 = abort)"
