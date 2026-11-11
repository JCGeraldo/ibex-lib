#!/usr/bin/env bash
# Barrido de ibexsolve-raak sobre una lista de instancias CSP (.bch), reanudable.
# Todas las configuraciones de una instancia quedan contiguas en la cola (misma sesion, misma carga).
#
# Variables:
#   LIST=<archivo>   una ruta .bch por linea                                   [obligatoria]
#   OUT=<dir>        carpeta de salida (logs/, rows/, runs.csv, meta.txt)      [obligatoria]
#   CONFIGS="default xn affine_af2 affine_raa affine_raa_k6"
#                    <ctc>[_<arith>[_k<K>]]; ctc = default|xn|hc4|affine|hc4+affine|hc4+xn|default+affine
#   TLIM=60 P=10     limite de CPU por corrida (s) y procesos en paralelo
#   MEMKB=4000000    tope de memoria virtual por corrida (kB)
#   BIN=<binario>    ibexsolve-raak
set -uo pipefail
ROOT="$HOME/ibex-local"
BIN="${BIN:-$ROOT/ibexopt-raak/build/ibexsolve-raak}"
: "${LIST:?falta LIST}"; : "${OUT:?falta OUT}"
CONFIGS="${CONFIGS:-default xn affine_af2 affine_raa affine_raa_k6}"
TLIM="${TLIM:-60}"; P="${P:-10}"; MEMKB="${MEMKB:-4000000}"
mkdir -p "$OUT/logs" "$OUT/rows"
export BIN TLIM OUT MEMKB

run_one () {
  local path="$1" label="$2" argstr="$3"
  local inst; inst="$(basename "$path" .bch)"
  local grupo; grupo="$(basename "$(dirname "$path")")"
  local row="$OUT/rows/${inst}__${label}.csv"
  [ -s "$row" ] && return 0
  local log="$OUT/logs/${inst}__${label}.log"
  local t0; t0=$(date +%s.%N)
  # shellcheck disable=SC2086
  ( ulimit -v "$MEMKB"; exec timeout "$(( TLIM * 2 + 60 ))" "$BIN" $argstr -t "$TLIM" "$path" ) > "$log" 2>&1
  local code=$?
  if [ "$code" -eq 143 ] || [ "$code" -eq 137 ]; then echo "[INTERRUMPIDA] $inst $label (exit $code)"; return 0; fi
  local wall; wall=$(awk -v a="$t0" -v b="$(date +%s.%N)" 'BEGIN{printf "%.2f", b-a}')
  local line; line="$(grep -a -oE 'RAAK-SOLVE .*' "$log" | tail -1)"
  get () { sed -nE "s/.*[ ]$1=([^ ]*).*/\1/p" <<<" $line"; }
  local status
  if [ -n "$line" ]; then status="$(get status)"
  elif [ "$code" -eq 124 ]; then status=KILLED
  elif grep -a -qiE 'bad_alloc|cannot allocate' "$log"; then status=MEM
  else status=ERROR; fi
  echo "$inst,$grupo,$label,$status,$(get cells),$(get time),$(get solution),$(get boundary),$(get unknown),$(get pending),$(get productos),$(get con_bloques),$(get bloques),$(get usados),$(get corner_used),$(get sqr_used),$wall,$code" > "$row"
  echo "[$status] $grupo/$inst $label celdas=$(get cells) cpu=$(get time)s wall=${wall}s"
}
run_task () { local path label argstr; IFS=$'\t' read -r path label argstr <<<"$1"; run_one "$path" "$label" "$argstr"; }
export -f run_one run_task

TASKS="$OUT/tasks.txt"; : > "$TASKS"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  for c in $CONFIGS; do
    ctc="${c%%_*}"; rest=""; [ "$c" != "$ctc" ] && rest="${c#*_}"
    arith=af2; k=0
    case "$rest" in *_k*) arith="${rest%_k*}"; k="${rest##*_k}";; "") ;; *) arith="$rest";; esac
    printf '%s\t%s\t%s\n' "$path" "$c" "--ctc=$ctc --arith=$arith --knomial_k=$k" >> "$TASKS"
  done
done < "$LIST"
{ echo "binario: $BIN ($(md5sum < "$BIN" | cut -c1-12))"
  echo "ibex-affine: $(git -C "$ROOT/ibex-affine" log -1 --format='%h') + parches locales"
  echo "ibex-lib: $(git -C "$ROOT/ibex-lib" log -1 --format='%h') ($(git -C "$ROOT/ibex-lib" branch --show-current))"
  echo "LIST=$LIST CONFIGS=$CONFIGS TLIM=$TLIM P=$P MEMKB=$MEMKB"
  echo "instancias: $(grep -c . "$LIST")  tareas: $(wc -l < "$TASKS")"; echo "carga al inicio: $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "inicio: $(date -Is)"; } >> "$OUT/meta.txt"
echo "== $(date -Is) tareas: $(wc -l < "$TASKS") (P=$P, TLIM=$TLIM)"
xargs -P "$P" -d '\n' -n 1 bash -c 'run_task "$0"' < "$TASKS"
echo "fin: $(date -Is)" >> "$OUT/meta.txt"
echo "instancia,grupo,config,estado,celdas,cpu_s,soluciones,frontera,desconocidas,pendientes,productos,con_bloques,bloques,usados,corner_used,sqr_used,wall_s,exit" > "$OUT/runs.csv"
cat "$OUT/rows"/*.csv | sort >> "$OUT/runs.csv"
echo "== $(date -Is) listo: $(( $(wc -l < "$OUT/runs.csv") - 1 )) filas en $OUT/runs.csv"
