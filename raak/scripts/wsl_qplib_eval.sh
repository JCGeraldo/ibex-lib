#!/usr/bin/env bash
# F5: evalua con ibex-affine (fAF2 y RAA-K) las formulaciones de la parte cuadratica de
# QPLIB generadas por qplib/qplib_ibex_forms.py. Requiere SP = carpeta que contiene
# qplib_affine_eval.cpp y el subdirectorio qplib_forms/.
set -euo pipefail

ROOT="$HOME/ibex-local"
TESTS="$ROOT/tests"
PREFIX="$ROOT/prefix"
: "${SP:?falta SP}"
OUT="$ROOT/results/qplib-eval-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" "$TESTS"

echo "== compilando el evaluador"
cp "$SP/qplib_affine_eval.cpp" "$TESTS/"
export PKG_CONFIG_PATH="$PREFIX/share/pkgconfig:$PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
g++ -std=c++11 -O2 -msse3 -frounding-math "$TESTS/qplib_affine_eval.cpp" \
    $(pkg-config --cflags ibex-affine ibex) -o "$TESTS/qplib_affine_eval" \
    $(pkg-config --libs ibex-affine ibex)

echo "== copiando formulaciones"
cp -r "$SP/qplib_forms" "$OUT/forms"
cp "$OUT/forms/predicciones.json" "$OUT/"

echo "== evaluando $(ls "$OUT/forms"/*.txt | wc -l) formulaciones"
start=$(date +%s)
"$TESTS/qplib_affine_eval" "$OUT/forms"/*.txt > "$OUT/eval.csv"
echo "   listo en $(( $(date +%s) - start )) s: $(( $(wc -l < "$OUT/eval.csv") - 1 )) filas"
rm -rf "$OUT/forms"
echo "CSV: $OUT/eval.csv"
