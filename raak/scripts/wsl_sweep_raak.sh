#!/usr/bin/env bash
# F5: barrido de RAA-K (raak y raakcompo) con los mismos parametros que la linea base F4.
# Sin K usa el raak_k por defecto del CLI (3); con K=1 corre raak:1 y raakcompo:1.
# Resultado en results/baseline-<fecha>/.
set -uo pipefail
cd "$HOME/ibex-local/scripts"
if [ -n "${K:-}" ]; then DEF="raak:$K raakcompo:$K"; else DEF="raak raakcompo"; fi
SETS="${SETS:-easy medium}" LRS="${LRS:-$DEF}" TLIM="${TLIM:-60}" P="${P:-4}" \
  bash ./wsl_baseline.sh
