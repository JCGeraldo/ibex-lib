#!/usr/bin/env bash
# Complemento de ref.csv: las corridas que en esta maquina agotan los 60 s se repiten con -t 300
# para tener referencias SUCCESS (deterministas) donde sea posible. Mismas columnas que ref.csv.
set -uo pipefail
ROOT="$HOME/ibex-local"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
BENCHS="$ROOT/ibex-lib/benchs/optim"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
OUT="$ROOT/results/fase1-ref"
TLIM=300
P="${P:-4}"
mkdir -p "$OUT/logs300" "$OUT/rows300"
export BIN BENCHS TLIM OUT
run_one () {
  local inst="$1" spec="$2"
  local lr="${spec%%:*}" k="" extra=""
  if [ "$spec" != "$lr" ]; then k="${spec#*:}"; extra="--raak_k=$k"; fi
  local log="$OUT/logs300/${inst//\//__}__${lr}${k:+_k$k}.log"
  timeout "$(( TLIM * 2 + 30 ))" "$BIN" --lr="$lr" $extra -t "$TLIM" "$BENCHS/$inst.bch" > "$log" 2>&1
  local code=$?
  local clean; clean="$(sed -r 's/\x1b\[[0-9;]*m//g' "$log")"
  local status
  if   grep -q "optimization successful"  <<<"$clean"; then status=SUCCESS
  elif grep -q "time limit"               <<<"$clean"; then status=TIME_OUT
  elif [ "$code" -eq 124 ];                            then status=KILLED
  else status=ERROR; fi
  local flb fub cells cpu
  flb="$(awk -F'[][,]' '/f\* in/ {print $2; exit}' <<<"$clean")"
  fub="$(awk -F'[][,]' '/f\* in/ {print $3; exit}' <<<"$clean")"
  cells="$(awk -F'\t+' '/number of cells/ {print $2; exit}' <<<"$clean")"
  cpu="$(awk -F'\t+' '/cpu time used/ {v = $2; sub(/s.*$/, "", v); print v; exit}' <<<"$clean")"
  echo "$inst,$lr,$k,$status,$cells,$flb,$fub" > "$OUT/rows300/${inst//\//__}__${lr}${k:+_k$k}.csv"
  echo "[$status] $inst --lr=$lr $extra celdas=$cells f=[$flb,$fub] cpu=${cpu}s"
}
export -f run_one
TASKS="$OUT/tasks300.txt"; : > "$TASKS"
for v in xn art compo raak:0 raakcompo:0; do echo "medium/ex8_4_4bis $v" >> "$TASKS"; done
for v in xn art compo raak:0 raak:1 raak:3 raakcompo:0; do echo "medium/bearing $v" >> "$TASKS"; done
xargs -P "$P" -L 1 bash -c 'run_one "$0" "$1"' < "$TASKS"
echo "instancia,lr,raak_k,estado,celdas,f_lb,f_ub" > "$OUT/ref_t300.csv"
cat "$OUT/rows300"/*.csv | sort >> "$OUT/ref_t300.csv"
cp "$OUT/ref_t300.csv" "$REPO/raak/results/fase1-ref/ref_t300.csv"
echo; echo "### ref_t300.csv"; cat "$OUT/ref_t300.csv"
