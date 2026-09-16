#!/usr/bin/env bash
# F5: sobrecosto de CPU de RAA-K medido en la misma sesion. Corridas secuenciales
# (sin paralelismo), REPS repeticiones con el orden de variantes rotado, sobre
# instancias donde RAA-K no se usa (celdas identicas en las tres variantes).
set -uo pipefail
ROOT="$HOME/ibex-local"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
OUT="$ROOT/results/timing-$(date +%Y%m%d-%H%M%S)"
REPS="${REPS:-3}"
INSTS="${INSTS:-medium/ex7_3_4 medium/ex5_3_2 medium/launch medium/alkyl medium/ex7_3_5bis medium/ex8_5_2_1 easy/ex7_2_3 medium/ex2_1_9fact medium/ex2_1_9 medium/alkylbis}"
mkdir -p "$OUT"
echo "instance,variant,rep,cpu_s,cells" > "$OUT/timing.csv"
for rep in $(seq 1 "$REPS"); do
  case $((rep % 3)) in
    1) order="art raak:0 raak:3" ;;
    2) order="raak:0 raak:3 art" ;;
    0) order="raak:3 art raak:0" ;;
  esac
  for inst in $INSTS; do
    for var in $order; do
      lr="${var%%:*}"
      k=""
      [ "$var" != "$lr" ] && k="--raak_k=${var#*:}"
      clean="$("$BIN" --lr="$lr" $k -t 120 "$ROOT/ibex-lib/benchs/optim/$inst.bch" 2>&1 | sed -r 's/\x1b\[[0-9;]*m//g')"
      cpu="$(awk -F'\t+' '/cpu time used/ {v = $2; sub(/s.*$/, "", v); print v; exit}' <<<"$clean")"
      cells="$(awk -F'\t+' '/number of cells/ {print $2; exit}' <<<"$clean")"
      echo "$inst,$var,$rep,$cpu,$cells" >> "$OUT/timing.csv"
    done
  done
  echo "repeticion $rep lista"
done
echo "CSV: $OUT/timing.csv"
