#!/usr/bin/env bash
# Clona (o repara) los repositorios fijados en ~/ibex-local. Es idempotente:
# si un directorio existe pero no es un repo git valido (clon interrumpido),
# lo elimina y vuelve a clonar.
set -euo pipefail

ROOT="$HOME/ibex-local"
mkdir -p "$ROOT"
cd "$ROOT"

clone_pinned () {
  local dir="$1" url="$2" sha="$3" branch="$4"
  if [ -d "$dir" ] && ! git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
    echo "[$dir] clon incompleto: se elimina y se vuelve a clonar"
    rm -rf "$dir"
  fi
  if [ ! -d "$dir" ]; then
    echo "[$dir] clonando $url ..."
    git clone -q "$url" "$dir"
  fi
  git -C "$dir" checkout -q -B "$branch" "$sha"
  echo "[$dir] rama local '$(git -C "$dir" branch --show-current)' en $(git -C "$dir" log -1 --format='%h %ad %s' --date=short) | $(du -sh "$dir" | cut -f1)"
}

clone_pinned ibex-lib    https://github.com/rilianx/ibex-lib.git     5e51fffc886bf4bf60415e865b5eadff3ff1a7d2 local
clone_pinned ibex-affine https://github.com/ibex-team/ibex-affine.git c219009cc6425826b760939b9486776f744ded96 raak
