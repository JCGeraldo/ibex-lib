#!/usr/bin/env bash
# Barrido de ibexopt-raak sobre una carpeta cualquiera de .bch (no solo benchs/optim), con las variantes que se
# indiquen. Mismo formato de salida que wsl_fase3_sweep.sh (rows/, logs/, runs.csv, meta.txt), reanudable.
#
# Variables:
#   DIR=<carpeta>         carpeta con .bch                                     [obligatoria]
#   OUT=<dir>             carpeta de salida                                    [obligatoria]
#   SET=<nombre>          prefijo del nombre de instancia en runs.csv (por defecto, basename de DIR)
#   VARIANTS="raa_k0 raa_k2 raa_k3"   etiquetas <arith>_k<K>; LR=art; opcional xn
#   TLIM=1800  P=10       limite de CPU por corrida (s) y procesos en paralelo
#   TRIG=auto             --trig para las variantes afines
#   BIN=<binario>         ibexopt-raak a usar (por defecto el de ~/ibex-local/ibexopt-raak/build)
# Uso tipico (en segundo plano):
#   DIR=~/ibex-local/ibex-lib/raak/instancias/sinteticas OUT=~/ibex-local/results/sint-$(date +%Y%m%d) \
#     setsid nohup bash wsl_sweep_dir.sh > log 2>&1 &
set -uo pipefail
ROOT="$HOME/ibex-local"
BIN="${BIN:-$ROOT/ibexopt-raak/build/ibexopt-raak}"
: "${DIR:?falta DIR}"; : "${OUT:?falta OUT}"
SET="${SET:-$(basename "$DIR")}"; LR="${LR:-art}"; VARIANTS="${VARIANTS:-raa_k0 raa_k2 raa_k3}"
TLIM="${TLIM:-1800}"; P="${P:-10}"; TRIG="${TRIG:-auto}"
mkdir -p "$OUT/logs" "$OUT/rows"
export BIN DIR SET TLIM OUT

VLIST=()
for v in $VARIANTS; do
  if [ "$v" = xn ]; then VLIST+=("xn"$'\t'"--lr=xn"); continue; fi
  a="${v%_k*}"; k="${v##*_k}"
  VLIST+=("${LR}_${a}_k${k}"$'\t'"--lr=$LR --arith=$a --knomial_k=$k --trig=$TRIG")
done

run_one () {
  local inst="$1" label="$2" argstr="$3"
  local row="$OUT/rows/${inst}__${label}.csv"
  [ -s "$row" ] && return 0
  local log="$OUT/logs/${inst}__${label}.log"
  local t0; t0=$(date +%s.%N)
  # shellcheck disable=SC2086
  timeout "$(( TLIM * 2 + 120 ))" "$BIN" $argstr -t "$TLIM" "$DIR/$inst.bch" > "$log" 2>&1
  local code=$?
  if [ "$code" -eq 143 ] || [ "$code" -eq 137 ]; then echo "[INTERRUMPIDA] $inst $label (exit $code)"; return 0; fi
  local wall; wall=$(awk -v a="$t0" -v b="$(date +%s.%N)" 'BEGIN{printf "%.2f", b-a}')
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
  local flb fub cells cpu kst tst
  flb="$(awk -F'[][,]' '/f\* in/ {print $2; exit}' <<<"$clean")"
  fub="$(awk -F'[][,]' '/f\* in/ {print $3; exit}' <<<"$clean")"
  cells="$(awk -F'\t+' '/number of cells/ {print $2; exit}' <<<"$clean")"
  cpu="$(awk -F'\t+' '/cpu time used/ {v = $2; sub(/s.*$/, "", v); print v; exit}' <<<"$clean")"
  kst="$(grep -oE "RAA-K stats:.*" <<<"$clean" | head -1 | cut -c13-)"
  tst="$(grep -oE "TRIG stats:.*" <<<"$clean" | head -1 | cut -c12-)"
  echo "$SET/$inst,$label,$status,$cells,$flb,$fub,$cpu,$wall,$code,\"$kst\",\"$tst\"" > "$row"
  echo "[$status] $SET/$inst $label celdas=$cells f=[$flb,$fub] cpu=${cpu}s wall=${wall}s"
}
run_task () { local inst label argstr; IFS=$'\t' read -r inst label argstr <<<"$1"; run_one "$inst" "$label" "$argstr"; }
export -f run_one run_task

TASKS="$OUT/tasks.txt"; : > "$TASKS"
# instancias en orden alfabetico (en las sinteticas, eso es n creciente)
for f in "$DIR"/*.bch; do inst="$(basename "$f" .bch)"; for v in "${VLIST[@]}"; do printf '%s\t%s\n' "$inst" "$v" >> "$TASKS"; done; done
{ echo "binario: $BIN"; echo "ibex-affine: $(git -C "$ROOT/ibex-affine" log -1 --format='%h') + parches: $(git -C "$ROOT/ibex-affine" status --short -- src | tr '\n' ' ')"
  echo "ibex-lib: $(git -C "$ROOT/ibex-lib" log -1 --format='%h') ($(git -C "$ROOT/ibex-lib" branch --show-current))"
  echo "DIR=$DIR SET=$SET LR=$LR VARIANTS=$VARIANTS TLIM=$TLIM P=$P TRIG=$TRIG"; echo "instancias: $(ls "$DIR"/*.bch | wc -l)  variantes: ${#VLIST[@]}  tareas: $(wc -l < "$TASKS")"
  echo "inicio: $(date -Is)"; } >> "$OUT/meta.txt"
echo "== $(date -Is) tareas: $(wc -l < "$TASKS") (P=$P, TLIM=$TLIM)"
xargs -P "$P" -d '\n' -n 1 bash -c 'run_task "$0"' < "$TASKS"
echo "fin: $(date -Is)" >> "$OUT/meta.txt"

echo "instancia,variante,estado,celdas,f_lb,f_ub,cpu_s,wall_s,exit,raak_stats,trig_stats" > "$OUT/runs.csv"
cat "$OUT/rows"/*.csv | sort >> "$OUT/runs.csv"
echo "== $(date -Is) listo: $(( $(wc -l < "$OUT/runs.csv") - 1 )) filas en $OUT/runs.csv"
