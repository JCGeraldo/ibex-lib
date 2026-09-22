#!/usr/bin/env bash
# Compilacion completa del entorno RAA-K (se ejecuta como evapo, tras wsl_setup_env.sh):
#   - copia cli_* a ~/ibex-local/scripts (wsl_build_cli.sh los toma de ahi) y tests/ a ~/ibex-local/tests
#   - F1 ibex-lib -> F2 ibex-affine (make check) -> F3 ibexopt-raak, con los scripts del repo
set -euo pipefail
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
export JOBS="${JOBS:-12}"

echo "== copiar cli_* y tests ($(date +%T))"
mkdir -p ~/ibex-local/tests
cp "$REPO"/raak/cli/cli_* ~/ibex-local/scripts/
cp "$REPO"/raak/tests/* ~/ibex-local/tests/
sed -i 's/\r$//' ~/ibex-local/scripts/cli_* ~/ibex-local/tests/*
ls ~/ibex-local/scripts/cli_* ~/ibex-local/tests/ | sed 's/^/   /'

cd ~/ibex-local/scripts
echo; echo "== F1 ibex-lib ($(date +%T))";     bash wsl_build_ibexlib.sh
echo; echo "== F2 ibex-affine ($(date +%T))";  bash wsl_build_affine.sh
echo; echo "== F3 ibexopt-raak ($(date +%T))"; bash wsl_build_cli.sh
echo; echo "== listo ($(date +%T))"
