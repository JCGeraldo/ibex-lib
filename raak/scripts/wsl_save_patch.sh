#!/usr/bin/env bash
# Guarda el cambio incremental del arbol de trabajo de un repo fijado como parche numerado, restando
# los parches anteriores, y comprueba que la cadena completa aplica en limpio sobre el commit fijado.
#
# uso: wsl_save_patch.sh <repo> <NNNN-nombre.patch> <parche_previo_1> [<parche_previo_2> ...]
#   repo            ibex-affine | ibex-lib   (en ~/ibex-local)
#   NNNN-nombre     nombre del parche nuevo (se escribe en ~/ibex-local/patches y en raak/patches)
#   parches previos nombres de archivo en ~/ibex-local/patches, en orden de aplicacion
#
# Procedimiento: worktree temporal en HEAD -> aplica los previos -> commit temporal -> copia encima
# los archivos del arbol de trabajo real (rastreados modificados y no rastreados de src/) -> git diff.
# Despues, en un segundo worktree limpio, aplica previos + nuevo con --check y de verdad.
set -euo pipefail
ROOT="$HOME/ibex-local"
REPO_VS=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
P="$ROOT/patches"
repo="$1"; new="$2"; shift 2
A="$ROOT/$repo"
[ -d "$A/.git" ] || { echo "no existe $A"; exit 1; }

# cabecera (primer archivo con ese nombre en raak/patches/headers, opcional)
HDR="$REPO_VS/raak/patches/headers/${new%.patch}.txt"

tmp=$(mktemp -d)
cleanup () { git -C "$A" worktree remove --force "$tmp/base" 2>/dev/null || true; git -C "$A" worktree remove --force "$tmp/chk" 2>/dev/null || true; rm -rf "$tmp"; }
trap cleanup EXIT

echo "== 1. base = HEAD $(git -C "$A" rev-parse --short HEAD) + previos: $*"
git -C "$A" worktree add --detach "$tmp/base" HEAD > /dev/null 2>&1
for prev in "$@"; do git -C "$tmp/base" apply "$P/$prev"; echo "   aplicado $prev"; done
git -C "$tmp/base" add -A src
git -C "$tmp/base" -c user.name=tmp -c user.email=tmp@local commit -q -m "base con previos" --allow-empty

echo "== 2. copiar el arbol de trabajo actual sobre la base"
( cd "$A" && git status --short --untracked-files=all -- src | awk '{print $2}' ) | while read -r f; do
  mkdir -p "$tmp/base/$(dirname "$f")"; cp "$A/$f" "$tmp/base/$f"
done
git -C "$tmp/base" add -A src
{
  if [ -f "$HDR" ]; then tr -d '\r' < "$HDR"; echo; fi
  git -C "$tmp/base" diff --cached
} > "$P/$new"
echo "   $(wc -l < "$P/$new") lineas -> $P/$new"
git -C "$tmp/base" diff --cached --stat | sed 's/^/   /'

echo "== 3. verificacion en worktree limpio: $* $new"
git -C "$A" worktree add --detach "$tmp/chk" HEAD > /dev/null 2>&1
for pt in "$@" "$new"; do
  git -C "$tmp/chk" apply --check "$P/$pt" && git -C "$tmp/chk" apply "$P/$pt" && echo "   $pt ok"
done
echo "== 4. el arbol verificado coincide con el arbol de trabajo real?"
diffs=0
( cd "$A" && git status --short --untracked-files=all -- src | awk '{print $2}' ) | while read -r f; do
  if ! cmp -s "$A/$f" "$tmp/chk/$f"; then echo "   DIFIERE: $f"; exit 1; fi
done && echo "   identicos (todos los archivos modificados/nuevos de src/)"

mkdir -p "$REPO_VS/raak/patches"
cp "$P/$new" "$REPO_VS/raak/patches/$new"
echo "== copiado a raak/patches/$new"
