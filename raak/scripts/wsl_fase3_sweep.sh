#!/usr/bin/env bash
# Fase 3, nivel 2: barrido de ibexopt-raak con las seis variantes (+ control xn) y limite de tiempo largo.
#
# Reanudable: cada corrida escribe rows/<inst>__<variante>.csv y se salta si ya existe. Las instancias
# se ordenan por dificultad creciente (CPU de la linea base de 60 s con compo, desconocidas al final)
# para que los resultados parciales sean utiles desde el principio.
#
# Variables:
#   OUT=<dir>            carpeta de salida                                  [obligatoria]
#   SETS="easy medium"   conjuntos de benchs/optim
#   LRS="compo"          relajaciones con formas afines a probar (compo | art | "compo art")
#   TLIM=1800  P=12      limite de CPU por corrida (s) y procesos en paralelo
#   TRIG=auto            --trig para todas las variantes afines
#   WITH_XN=1            agrega el control --lr=xn
#   ONLY="a,b"           solo esas instancias (nombres sin .bch)
#   ORDER=<results.csv>  CSV de la linea base para ordenar (por defecto el baseline de 60 s del repo)
# Uso tipico (en segundo plano):
#   OUT=~/ibex-local/results/fase3-$(date +%Y%m%d)/compo_easy_medium setsid nohup bash wsl_fase3_sweep.sh > log 2>&1 &
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
BENCHS="$ROOT/ibex-lib/benchs/optim"
: "${OUT:?falta OUT}"
SETS="${SETS:-easy medium}"; LRS="${LRS:-compo}"; TLIM="${TLIM:-1800}"; P="${P:-12}"; TRIG="${TRIG:-auto}"
WITH_XN="${WITH_XN:-1}"; ONLY="${ONLY:-}"
ORDER="${ORDER:-$REPO/raak/results/01-linea-base/baseline-20260913-193306/results.csv}"
mkdir -p "$OUT/logs" "$OUT/rows"
export BIN BENCHS TLIM OUT

# variantes: <etiqueta>\t<argumentos>
VARIANTS=()
for lr in $LRS; do
  for a in af2 raa aa; do for k in 0 3; do
    VARIANTS+=("${lr}_${a}_k${k}"$'\t'"--lr=$lr --arith=$a --knomial_k=$k --trig=$TRIG")
  done; done
done
[ "$WITH_XN" = 1 ] && VARIANTS+=("xn"$'\t'"--lr=xn")

# instancias ordenadas por CPU de la linea base (compo, 60 s); las que no estan, al final
declare -A CPU
if [ -f "$ORDER" ]; then
  while IFS=, read -r set inst lr status flb fub rp ap cpu rest; do
    [ "$lr" = compo ] || continue
    [ "$status" = SUCCESS ] && CPU["$set/$inst"]="$cpu" || CPU["$set/$inst"]="999999"
  done < <(tr -d '\r' < "$ORDER")
fi
INSTS=()
for set in $SETS; do
  for f in "$BENCHS/$set"/*.bch; do
    inst="$set/$(basename "$f" .bch)"
    if [ -n "$ONLY" ]; then case ",$ONLY," in *",$(basename "$f" .bch),"*) ;; *) continue;; esac; fi
    INSTS+=("${CPU[$inst]:-9999999} $inst")
  done
done
mapfile -t INSTS < <(printf '%s\n' "${INSTS[@]}" | sort -g | awk '{print $2}')

run_one () {
  local inst="$1" label="$2" argstr="$3"
  local row="$OUT/rows/${inst//\//__}__${label}.csv"
  [ -s "$row" ] && return 0
  local log="$OUT/logs/${inst//\//__}__${label}.log"
  local t0; t0=$(date +%s.%N)
  # shellcheck disable=SC2086
  timeout "$(( TLIM * 2 + 120 ))" "$BIN" $argstr -t "$TLIM" "$BENCHS/$inst.bch" > "$log" 2>&1
  local code=$?
  # corrida interrumpida desde fuera (SIGTERM 143 / SIGKILL 137, p. ej. al detener la cadena): no se
  # escribe fila, para que al reanudar se rehaga en vez de quedar registrada como ERROR
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
  echo "$inst,$label,$status,$cells,$flb,$fub,$cpu,$wall,$code,\"$kst\",\"$tst\"" > "$row"
  echo "[$status] $inst $label celdas=$cells f=[$flb,$fub] cpu=${cpu}s wall=${wall}s"
}
run_task () { local inst label argstr; IFS=$'\t' read -r inst label argstr <<<"$1"; run_one "$inst" "$label" "$argstr"; }
export -f run_one run_task

TASKS="$OUT/tasks.txt"; : > "$TASKS"
for inst in "${INSTS[@]}"; do for v in "${VARIANTS[@]}"; do printf '%s\t%s\n' "$inst" "$v" >> "$TASKS"; done; done
{ echo "binario: $BIN"; echo "ibex-affine: $(git -C "$ROOT/ibex-affine" log -1 --format='%h') + parches: $(git -C "$ROOT/ibex-affine" status --short -- src | tr '\n' ' ')"
  echo "SETS=$SETS LRS=$LRS TLIM=$TLIM P=$P TRIG=$TRIG WITH_XN=$WITH_XN ONLY=$ONLY"; echo "instancias: ${#INSTS[@]}  variantes: ${#VARIANTS[@]}  tareas: $(wc -l < "$TASKS")"
  echo "inicio: $(date -Is)"; } >> "$OUT/meta.txt"
echo "== $(date -Is) tareas: $(wc -l < "$TASKS") (P=$P, TLIM=$TLIM)"
xargs -P "$P" -d '\n' -n 1 bash -c 'run_task "$0"' < "$TASKS"
echo "fin: $(date -Is)" >> "$OUT/meta.txt"

echo "instancia,variante,estado,celdas,f_lb,f_ub,cpu_s,wall_s,exit,raak_stats,trig_stats" > "$OUT/runs.csv"
cat "$OUT/rows"/*.csv | sort >> "$OUT/runs.csv"
echo "== $(date -Is) listo: $(( $(wc -l < "$OUT/runs.csv") - 1 )) filas en $OUT/runs.csv"
