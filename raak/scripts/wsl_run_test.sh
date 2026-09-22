#!/usr/bin/env bash
# Compila y corre un test C++ de raak contra el prefix instalado (mismo patron que wsl_raak_quick.sh).
# uso: wsl_arith_test.sh <nombre_sin_extension> [args...]
set -euo pipefail
ROOT="$HOME/ibex-local"
PREFIX="$ROOT/prefix"
TESTS="$ROOT/tests"
name="$1"; shift
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
g++ -std=c++11 -O2 -msse3 -frounding-math "$TESTS/$name.cpp" \
    $(pkg-config --cflags ibex-affine ibex) -o "$TESTS/$name" \
    $(pkg-config --libs ibex-affine ibex)
echo "== $name compilado; ejecutando"
"$TESTS/$name" "$@"
