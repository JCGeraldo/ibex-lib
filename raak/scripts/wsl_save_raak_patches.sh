#!/usr/bin/env bash
# Guarda como parches (sin commit) los cambios locales del prototipo RAA-K.
set -euo pipefail

ROOT="$HOME/ibex-local"
P="$ROOT/patches"
A="$ROOT/ibex-affine"
L="$ROOT/ibex-lib"
mkdir -p "$P"

out="$P/0002-ibex-affine-RAA-K-multiplicacion-knomial.patch"
{
  git -C "$A" diff -- src/arithmetic/ibex_Affine2_fAF2.cpp src/CMakeLists.txt
  git -C "$A" diff --no-index -- /dev/null src/arithmetic/ibex_KNomial.h || true
} > "$out"

out2="$P/0003-ibex-lib-get_ctc-acepta-raak.patch"
git -C "$L" diff -- src/optim/ibex_Optimizer04Config.cpp > "$out2"

echo "== parches guardados"
wc -l "$P"/*.patch
echo
echo "== ibex-affine (rama $(git -C "$A" branch --show-current), HEAD $(git -C "$A" rev-parse --short HEAD))"
git -C "$A" status --short
echo
echo "== ibex-lib (rama $(git -C "$L" branch --show-current), HEAD $(git -C "$L" rev-parse --short HEAD))"
git -C "$L" status --short | head -20
echo
echo "== comprobacion: el parche 0002 se aplica en limpio sobre HEAD de ibex-affine"
tmp=$(mktemp -d)
git -C "$A" worktree add --detach "$tmp/wt" HEAD > /dev/null 2>&1
git -C "$tmp/wt" apply --check "$P/0001-LinearizerAffine2-omitir-formas-no-activas.patch" && echo "   0001 ok"
git -C "$tmp/wt" apply "$P/0001-LinearizerAffine2-omitir-formas-no-activas.patch"
git -C "$tmp/wt" apply --check "$out" && echo "   0002 ok (sobre 0001)"
git -C "$A" worktree remove --force "$tmp/wt"
rm -rf "$tmp"
