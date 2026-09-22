#!/usr/bin/env bash
# Fase 1: corre ibexopt-raak sobre una lista de instancias con una lista de variantes y escribe un CSV
# con las mismas columnas que ref.csv mas la etiqueta de la variante; si se indica REF, compara cada
# fila con la fila de referencia que le corresponde (estado, celdas, f_lb, f_ub).
#
# Variables:
#   OUT=<dir>            carpeta de salida (se crea)            [obligatoria]
#   VARIANTS="etiqueta=args;etiqueta=args;..."                  [obligatoria]
#        p. ej. "art=--lr=art --arith=af2 --knomial_k=0;raak_1=--lr=art --arith=raa --knomial_k=0"
#   INSTS="easy/ex5_4_3 ..."                                    [por defecto las 7 de referencia]
#   TLIM=60  P=4
#   REF=<ref.csv>        referencia (columnas instancia,lr,raak_k,estado,celdas,f_lb,f_ub)
#   MAP="etiqueta=lr,k;..."   a que fila de REF se compara cada etiqueta (k vacio para xn/art/compo);
#                         una etiqueta sin MAP se registra sin comparar ("nueva")
set -uo pipefail
ROOT="$HOME/ibex-local"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
BENCHS="$ROOT/ibex-lib/benchs/optim"
TLIM="${TLIM:-60}"
P="${P:-4}"
INSTS="${INSTS:-easy/ex5_4_3 easy/ex2_1_1 easy/ex2_1_2 medium/ex8_4_4bis medium/bearing medium/ex7_3_4 medium/ex5_3_2}"
: "${OUT:?falta OUT}"; : "${VARIANTS:?falta VARIANTS}"
mkdir -p "$OUT/logs" "$OUT/rows"
export BIN BENCHS TLIM OUT

run_one () {
  local inst="$1" label="$2" argstr="$3"
  local log="$OUT/logs/${inst//\//__}__${label}.log"
  # shellcheck disable=SC2086
  timeout "$(( TLIM * 2 + 30 ))" "$BIN" $argstr -t "$TLIM" "$BENCHS/$inst.bch" > "$log" 2>&1
  local code=$?
  local clean; clean="$(sed -r 's/\x1b\[[0-9;]*m//g' "$log")"
  local status
  if   grep -q "optimization successful"  <<<"$clean"; then status=SUCCESS
  elif grep -q "time limit"               <<<"$clean"; then status=TIME_OUT
  elif grep -q "no feasible point found"  <<<"$clean"; then status=NO_FEASIBLE_FOUND
  elif grep -q "infeasible problem"       <<<"$clean"; then status=INFEASIBLE
  elif [ "$code" -eq 124 ];                            then status=KILLED
  else status=ERROR; fi
  local flb fub cells cpu stats
  flb="$(awk -F'[][,]' '/f\* in/ {print $2; exit}' <<<"$clean")"
  fub="$(awk -F'[][,]' '/f\* in/ {print $3; exit}' <<<"$clean")"
  cells="$(awk -F'\t+' '/number of cells/ {print $2; exit}' <<<"$clean")"
  cpu="$(awk -F'\t+' '/cpu time used/ {v = $2; sub(/s.*$/, "", v); print v; exit}' <<<"$clean")"
  stats="$(grep -oE "RAA-K stats:.*" <<<"$clean" | head -1)"
  echo "$inst,$label,$status,$cells,$flb,$fub,$cpu,\"$stats\"" > "$OUT/rows/${inst//\//__}__${label}.csv"
  echo "[$status] $inst $label celdas=$cells f=[$flb,$fub] cpu=${cpu}s"
}
run_task () {
  local inst label argstr
  IFS=$'\t' read -r inst label argstr <<<"$1"
  run_one "$inst" "$label" "$argstr"
}
export -f run_one run_task

TASKS="$OUT/tasks.txt"; : > "$TASKS"
IFS=';' read -ra VARR <<<"$VARIANTS"
for inst in $INSTS; do
  for v in "${VARR[@]}"; do
    [ -z "$v" ] && continue
    printf '%s\t%s\t%s\n' "$inst" "${v%%=*}" "${v#*=}" >> "$TASKS"
  done
done
{ echo "binario: $BIN"; echo "ibex-affine: $(git -C "$ROOT/ibex-affine" log -1 --format='%h') + parches: $(git -C "$ROOT/ibex-affine" status --short | tr '\n' ' ')"
  echo "TLIM=$TLIM P=$P"; echo "VARIANTS=$VARIANTS"; echo "INSTS=$INSTS"; echo "inicio: $(date -Is)"; } > "$OUT/meta.txt"
xargs -P "$P" -d '\n' -n 1 bash -c 'run_task "$0"' < "$TASKS"
echo "fin: $(date -Is)" >> "$OUT/meta.txt"

echo "instancia,variante,estado,celdas,f_lb,f_ub,cpu_s,stats" > "$OUT/runs.csv"
cat "$OUT/rows"/*.csv | sort >> "$OUT/runs.csv"

if [ -n "${REF:-}" ]; then
  echo
  echo "### comparacion con $(basename "$REF") (TLIM=$TLIM)"
  awk -F, -v map="${MAP:-}" '
    BEGIN {
      n = split(map, M, ";")
      for (i = 1; i <= n; i++) { split(M[i], kv, "="); split(kv[2], lk, ","); mlr[kv[1]] = lk[1]; mk[kv[1]] = lk[2] }
      printf "%-20s %-14s %-10s %-9s %-10s %-9s %s\n", "instancia", "variante", "estado", "celdas", "ref_estado", "ref_celdas", "resultado"
    }
    FNR == NR { if (FNR > 1) { key = $1 "|" $2 "|" $3; rs[key] = $4; rc[key] = $5; rl[key] = $6; ru[key] = $7 }; next }
    FNR > 1 {
      lab = $2
      if (!(lab in mlr)) { printf "%-20s %-14s %-10s %-9s %-10s %-9s %s\n", $1, lab, $3, $4, "-", "-", "nueva (sin referencia)"; nuevas++; next }
      key = $1 "|" mlr[lab] "|" mk[lab]
      if (!(key in rs)) { printf "%-20s %-14s %-10s %-9s %-10s %-9s %s\n", $1, lab, $3, $4, "?", "?", "SIN FILA EN REF"; faltan++; next }
      if (rs[key] == $3 && rc[key] == $4 && rl[key] == $5 && ru[key] == $6) { r = "IDENTICA"; ok++ }
      else if (rs[key] == "TIME_OUT" && $3 == "TIME_OUT") { r = "ambas TIME_OUT (no comparable)"; to++ }
      else { r = "DIFERENTE"; bad++ }
      printf "%-20s %-14s %-10s %-9s %-10s %-9s %s\n", $1, lab, $3, $4, rs[key], rc[key], r
    }
    END { printf "identicas=%d diferentes=%d ambas_timeout=%d nuevas=%d sin_ref=%d\n", ok, bad, to, nuevas, faltan }
  ' "$REF" "$OUT/runs.csv" | tee "$OUT/comparacion.txt"
fi
