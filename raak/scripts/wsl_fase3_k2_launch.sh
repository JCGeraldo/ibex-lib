#!/usr/bin/env bash
# Lanza la variante que falta para el profesor: --lr=art --arith=raa --knomial_k=2 sobre easy+medium+hard+others,
# -t 1800, 12 procesos. Reutiliza wsl_fase3_sweep.sh del repo (solo lectura) con el bucle de variantes cambiado,
# en una copia dentro de ~/ibex-local/tmp. Escribe solo en ~/ibex-local/results/fase3-k2-20261005.
set -euo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
mkdir -p "$ROOT/tmp" "$ROOT/results/fase3-k2-20261005"
tr -d '\r' < "$REPO/raak/scripts/wsl_fase3_sweep.sh" > "$ROOT/tmp/sweep_k2.sh"
sed -i 's/for a in af2 raa aa; do for k in 0 3; do/for a in raa; do for k in 2; do/' "$ROOT/tmp/sweep_k2.sh"
grep -n "for a in raa; do for k in 2" "$ROOT/tmp/sweep_k2.sh" >/dev/null || { echo "sed no aplico"; exit 1; }
OUT="$ROOT/results/fase3-k2-20261005/art_raa_k2"
export OUT SETS="easy medium hard others" LRS=art TLIM=1800 P=12 WITH_XN=0
setsid nohup bash "$ROOT/tmp/sweep_k2.sh" > "$ROOT/results/fase3-k2-20261005/sweep_k2.log" 2>&1 < /dev/null &
sleep 5
echo "lanzado; log: $ROOT/results/fase3-k2-20261005/sweep_k2.log"
head -3 "$ROOT/results/fase3-k2-20261005/sweep_k2.log"
cat "$OUT/meta.txt" 2>/dev/null | tail -4
pgrep -c ibexopt-raak || true
