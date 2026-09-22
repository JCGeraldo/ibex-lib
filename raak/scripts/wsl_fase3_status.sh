#!/usr/bin/env bash
# Estado de un barrido de la Fase 3 (nivel 2): tareas hechas / totales, corridas en curso, estados y
# consolidacion parcial de runs.csv (se puede analizar antes de que termine).
# uso: wsl_fase3_status.sh <OUT>
set -uo pipefail
OUT="${1:?uso: $0 <OUT>}"
total=$(wc -l < "$OUT/tasks.txt" 2>/dev/null || echo 0)
done_=$(ls "$OUT/rows" 2>/dev/null | wc -l)
echo "== $(date -Is)  hechas $done_ / $total"
echo "-- en curso:"; pgrep -af "ibexopt-raak" | grep -v pgrep | sed -E 's#.*--lr=#   --lr=#; s#/home/[^ ]*/benchs/optim/#  #' | head -20
echo "-- estados:"; cat "$OUT/rows"/*.csv 2>/dev/null | awk -F, '{c[$2" "$3]++} END{for(k in c) print "   "c[k], k}' | sort -k2
echo "instancia,variante,estado,celdas,f_lb,f_ub,cpu_s,wall_s,exit,raak_stats,trig_stats" > "$OUT/runs_parcial.csv"
cat "$OUT/rows"/*.csv 2>/dev/null | sort >> "$OUT/runs_parcial.csv"
echo "-- parcial: $OUT/runs_parcial.csv ($(( $(wc -l < "$OUT/runs_parcial.csv") - 1 )) filas)"
