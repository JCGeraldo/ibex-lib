#!/usr/bin/env bash
# Paso 1.0 de la Fase 1: estado inicial reproducible y tabla de referencia bit a bit.
#   A. comandos de ACEPTACION del paso (salida literal para la bitacora)
#   B. ref.csv: 7 instancias x {xn, art, compo, raak:0/1/3, raakcompo:0/1/3}, -t 60
#      columnas: instancia,lr,raak_k,estado,celdas,f_lb,f_ub
set -uo pipefail
ROOT="$HOME/ibex-local"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
BENCHS="$ROOT/ibex-lib/benchs/optim"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
OUT="$ROOT/results/fase1-ref"
TLIM="${TLIM:-60}"
P="${P:-4}"
INSTS="easy/ex5_4_3 easy/ex2_1_1 easy/ex2_1_2 medium/ex8_4_4bis medium/bearing medium/ex7_3_4 medium/ex5_3_2"
VARIANTS="xn art compo raak:0 raak:1 raak:3 raakcompo:0 raakcompo:1 raakcompo:3"
mkdir -p "$OUT/logs" "$OUT/rows"

echo "### A. versiones"
gcc --version | head -1
cmake --version | head -1
echo "fecha: $(date -Is)"
echo
echo '### A. cd ~/ibex-local/ibex-affine && git log --oneline -1 && git status --short && git diff --stat'
cd "$ROOT/ibex-affine" && git log --oneline -1 && git status --short && git diff --stat
echo
echo '### A. cd ~/ibex-local/ibex-lib && git log --oneline -1 && git status --short && git diff --stat'
cd "$ROOT/ibex-lib" && git log --oneline -1 && git status --short && git diff --stat
echo
echo '### A. cd ~/ibex-local/ibex-affine/build && make check 2>&1 | tail -5'
cd "$ROOT/ibex-affine/build" && make check 2>&1 | tail -5
echo
echo '### A. ibexopt-raak --lr=raak --raak_k=1 -t 60 easy/ex5_4_3.bch | grep -E "number of cells|f\*|cpu time"'
"$BIN" --lr=raak --raak_k=1 -t 60 "$BENCHS/easy/ex5_4_3.bch" 2>&1 | sed -r 's/\x1b\[[0-9;]*m//g' | grep -E "number of cells|f\*|cpu time|optimization successful"
echo

echo "### B. ref.csv (TLIM=$TLIM, P=$P)"
export BIN BENCHS TLIM OUT
run_one () {
  local inst="$1" spec="$2"
  local lr="${spec%%:*}" k="" extra=""
  if [ "$spec" != "$lr" ]; then k="${spec#*:}"; extra="--raak_k=$k"; fi
  local log="$OUT/logs/${inst//\//__}__${lr}${k:+_k$k}.log"
  timeout "$(( TLIM * 2 + 30 ))" "$BIN" --lr="$lr" $extra -t "$TLIM" "$BENCHS/$inst.bch" > "$log" 2>&1
  local code=$?
  local clean; clean="$(sed -r 's/\x1b\[[0-9;]*m//g' "$log")"
  local status
  if   grep -q "optimization successful"  <<<"$clean"; then status=SUCCESS
  elif grep -q "time limit"               <<<"$clean"; then status=TIME_OUT
  elif grep -q "no feasible point found"  <<<"$clean"; then status=NO_FEASIBLE_FOUND
  elif grep -q "infeasible problem"       <<<"$clean"; then status=INFEASIBLE
  elif grep -q "possibly unbounded"       <<<"$clean"; then status=UNBOUNDED_OBJ
  elif grep -q "unreached precision"      <<<"$clean"; then status=UNREACHED_PREC
  elif [ "$code" -eq 124 ];                            then status=KILLED
  else status=ERROR; fi
  local flb fub cells
  flb="$(awk -F'[][,]' '/f\* in/ {print $2; exit}' <<<"$clean")"
  fub="$(awk -F'[][,]' '/f\* in/ {print $3; exit}' <<<"$clean")"
  cells="$(awk -F'\t+' '/number of cells/ {print $2; exit}' <<<"$clean")"
  echo "$inst,$lr,$k,$status,$cells,$flb,$fub" > "$OUT/rows/${inst//\//__}__${lr}${k:+_k$k}.csv"
  echo "[$status] $inst --lr=$lr $extra celdas=$cells f=[$flb,$fub]"
}
export -f run_one
TASKS="$OUT/tasks.txt"; : > "$TASKS"
for inst in $INSTS; do for v in $VARIANTS; do echo "$inst $v" >> "$TASKS"; done; done
xargs -P "$P" -L 1 bash -c 'run_one "$0" "$1"' < "$TASKS"

echo "instancia,lr,raak_k,estado,celdas,f_lb,f_ub" > "$OUT/ref.csv"
cat "$OUT/rows"/*.csv | sort >> "$OUT/ref.csv"
mkdir -p "$REPO/raak/results/04-fase1-validacion/fase1-ref"
cp "$OUT/ref.csv" "$REPO/raak/results/04-fase1-validacion/fase1-ref/ref.csv"
echo
echo "### ref.csv ($(( $(wc -l < "$OUT/ref.csv") - 1 )) filas)"
cat "$OUT/ref.csv"
