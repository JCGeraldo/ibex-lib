#!/usr/bin/env bash
# Reconstruye ibex-affine en un worktree limpio (commit fijado + una cadena de parches) y lo instala
# en un prefix aparte, para volcar referencias bit a bit "anteriores a un parche" cuando la biblioteca
# instalada ya lo incluye. No toca ~/ibex-local/prefix ni el arbol de trabajo de ibex-affine.
#
# uso: wsl_build_prefix_pre.sh <nombre_prefix> <parche_1> [<parche_2> ...]
#   -> ~/ibex-local/<nombre_prefix>  (p. ej. prefix-pre13 con 0001 0002 0004 0005)
set -euo pipefail
ROOT="$HOME/ibex-local"
A="$ROOT/ibex-affine"
P="$ROOT/patches"
name="$1"; shift
PRE="$ROOT/$name"
WT="$ROOT/worktrees/$name"
mkdir -p "$ROOT/worktrees" "$ROOT/logs"

if [ -d "$WT" ]; then git -C "$A" worktree remove --force "$WT"; fi
git -C "$A" worktree add --detach "$WT" HEAD > /dev/null 2>&1
echo "== worktree en $(git -C "$WT" rev-parse --short HEAD) + parches: $*"
for pt in "$@"; do git -C "$WT" apply "$P/$pt" && echo "   $pt ok"; done

echo "== cmake + make -j12 (log: $ROOT/logs/$name-build.log)"
cmake -S "$WT" -B "$WT/build" -DCMAKE_BUILD_TYPE=Release -DIBEX_DIR="$ROOT/prefix" -DCMAKE_INSTALL_PREFIX="$PRE" > "$ROOT/logs/$name-build.log" 2>&1
make -C "$WT/build" -j12 >> "$ROOT/logs/$name-build.log" 2>&1
make -C "$WT/build" install >> "$ROOT/logs/$name-build.log" 2>&1
echo "   instalado en $PRE: $(find "$PRE" -name 'libibex-affine*' | wc -l) biblioteca(s), cabecera KNomial: $(find "$PRE/include" -name ibex_KNomial.h | head -1)"
git -C "$A" worktree remove --force "$WT"
echo "== worktree eliminado; prefix $PRE listo"
