#!/usr/bin/env bash
# F4: experimentos base, todavia sin RAA-K. Corre ibexopt-raak con cada relajacion
# lineal (xn, art, compo) sobre los benchmarks de optimizacion del fork y guarda
# un CSV con una fila por (instancia, relajacion).
#
# Parametros por variable de entorno:
#   SETS="easy medium"   conjuntos de benchs/optim a correr
#   LRS="xn art compo"   relajaciones lineales; "raak:1" fija --raak_k=1 (etiqueta raak_k1)
#   TLIM=60              limite de tiempo de ibexopt por corrida, en segundos
#   P=4                  corridas en paralelo. El numero de celdas NO depende de
#                        esto; el tiempo de CPU medido SI se ve afectado por la carga.
#   ONLY="ex5_4_3 wall"  (opcional) restringe a estas instancias, sin extension
set -uo pipefail   # sin -e: una instancia que falla no debe detener el barrido

ROOT="$HOME/ibex-local"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
BENCHS="$ROOT/ibex-lib/benchs/optim"
SETS="${SETS:-easy medium}"
LRS="${LRS:-xn art compo}"
TLIM="${TLIM:-60}"
P="${P:-4}"
ONLY="${ONLY:-}"

[ -x "$BIN" ] || { echo "No existe $BIN: compila primero ibexopt-raak (wsl_build_cli.sh)"; exit 1; }

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$ROOT/results/baseline-$STAMP"
mkdir -p "$OUT/logs" "$OUT/rows"
export BIN BENCHS TLIM OUT

run_one () {
  local set="$1" inst="$2" spec="$3"
  # spec = relajacion, o relajacion:K para fijar --raak_k=K (etiqueta relajacion_kK)
  local lr="${spec%%:*}" lab="${spec%%:*}" extra=""
  if [ "$spec" != "$lr" ]; then extra="--raak_k=${spec#*:}"; lab="${lr}_k${spec#*:}"; fi
  local name; name="$(basename "$inst")"; name="${name%.*}"
  local log="$OUT/logs/${set}__${name}__${lab}.log"
  local start end code
  start="$(date +%s.%N)"
  timeout "$(( TLIM * 2 + 30 ))" "$BIN" --lr="$lr" $extra -t "$TLIM" "$inst" > "$log" 2>&1
  code=$?
  end="$(date +%s.%N)"

  # el reporte trae codigos de color ANSI: se quitan antes de leerlo
  local clean; clean="$(sed -r 's/\x1b\[[0-9;]*m//g' "$log")"

  local status
  if   grep -q "optimization successful"  <<<"$clean"; then status=SUCCESS
  elif grep -q "time limit"               <<<"$clean"; then status=TIME_OUT
  elif grep -q "no feasible point found"  <<<"$clean"; then status=NO_FEASIBLE_FOUND
  elif grep -q "infeasible problem"       <<<"$clean"; then status=INFEASIBLE
  elif grep -q "possibly unbounded"       <<<"$clean"; then status=UNBOUNDED_OBJ
  elif grep -q "unreached precision"      <<<"$clean"; then status=UNREACHED_PREC
  elif grep -q "not started"              <<<"$clean"; then status=NOT_STARTED
  elif [ "$code" -eq 124 ];                            then status=KILLED
  else status=ERROR; fi

  # campos ausentes quedan vacios (p. ej. INFEASIBLE no imprime f*)
  local flb fub rel abs cpu cells wall
  flb="$(awk -F'[][,]' '/f\* in/ {print $2; exit}' <<<"$clean")"
  fub="$(awk -F'[][,]' '/f\* in/ {print $3; exit}' <<<"$clean")"
  rel="$(awk -F'\t' '/relative precision on f\*/ {split($2, a, " "); print a[1]; exit}' <<<"$clean")"
  abs="$(awk -F'\t' '/absolute precision on f\*/ {split($2, a, " "); print a[1]; exit}' <<<"$clean")"
  cpu="$(awk -F'\t+' '/cpu time used/ {v = $2; sub(/s.*$/, "", v); print v; exit}' <<<"$clean")"
  cells="$(awk -F'\t+' '/number of cells/ {print $2; exit}' <<<"$clean")"
  wall="$(awk -v a="$start" -v b="$end" 'BEGIN { printf "%.3f", b - a }')"

  echo "$set,$name,$lab,$status,$flb,$fub,$rel,$abs,$cpu,$cells,$wall,$code" \
       > "$OUT/rows/${set}__${name}__${lab}.csv"
  echo "[$status] $set/$name --lr=$lr $extra  celdas=$cells  cpu=${cpu}s"
}
export -f run_one

TASKS="$OUT/tasks.txt"
: > "$TASKS"
for set in $SETS; do
  for inst in "$BENCHS/$set"/*.bch "$BENCHS/$set"/*.mbx; do
    [ -e "$inst" ] || continue
    name="$(basename "$inst")"; name="${name%.*}"
    # ONLY acepta nombres separados por espacio o por coma
    if [ -n "$ONLY" ] && [[ " ${ONLY//,/ } " != *" $name "* ]]; then continue; fi
    for lr in $LRS; do echo "$set $inst $lr" >> "$TASKS"; done
  done
done

{
  echo "binario: $BIN"
  echo "ibex-lib: $(git -C "$ROOT/ibex-lib" log -1 --format='%h %ad' --date=short) rama $(git -C "$ROOT/ibex-lib" branch --show-current)"
  echo "ibex-affine: $(git -C "$ROOT/ibex-affine" log -1 --format='%h %ad' --date=short) rama $(git -C "$ROOT/ibex-affine" branch --show-current)"
  echo "SETS=$SETS  LRS=$LRS  TLIM=$TLIM  P=$P  ONLY=$ONLY"
  echo "corridas: $(wc -l < "$TASKS")"
  echo "inicio: $(date -Is)"
} > "$OUT/meta.txt"
cat "$OUT/meta.txt"
echo

xargs -P "$P" -L 1 bash -c 'run_one "$0" "$1" "$2"' < "$TASKS"

echo "set,instance,lr,status,f_lb,f_ub,rel_prec,abs_prec,cpu_s,cells,wall_s,exit" > "$OUT/results.csv"
cat "$OUT/rows"/*.csv | sort >> "$OUT/results.csv"
echo "fin: $(date -Is)" >> "$OUT/meta.txt"

echo
echo "== Resumen"
echo "   'resueltas' = corridas con estado SUCCESS sobre el total de esa relajacion."
echo "   'celdas' y 'CPU' = SUMA sobre las instancias que resolvieron TODAS las relajaciones,"
echo "   para que la comparacion sea sobre el mismo conjunto."
awk -F, -v lrs="${LRS//:/_k}" '
  BEGIN { n = split(lrs, L, " ") }
  NR > 1 {
    key = $1 "/" $2; tot[$3]++
    if ($4 == "SUCCESS") { ok[$3]++; s[key]++; c[key, $3] = $10; t[key, $3] = $9 }
  }
  END {
    printf "   %-6s  %-12s  %-18s  %s\n", "lr", "resueltas", "celdas (comunes)", "CPU s (comunes)"
    m = 0; for (k in s) if (s[k] == n) m++
    for (i = 1; i <= n; i++) {
      l = L[i]; sc = 0; st = 0
      for (k in s) if (s[k] == n) { sc += c[k, l]; st += t[k, l] }
      printf "   %-6s  %4d/%-7d  %-18d  %.2f\n", l, ok[l], tot[l], sc, st
    }
    printf "   instancias resueltas por las %d relajaciones: %d\n", n, m
  }' "$OUT/results.csv"
echo "CSV: $OUT/results.csv"
