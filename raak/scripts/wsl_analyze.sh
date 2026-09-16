#!/usr/bin/env bash
# Analiza un results.csv de wsl_baseline.sh (por defecto, el barrido mas reciente).
# Compara art y compo contra xn usando el numero de celdas del B&B.
#
# Definiciones (todas sobre instancias resueltas -SUCCESS- por las tres relajaciones):
#   cociente  = celdas(lr) / celdas(xn)      < 1 significa que lr explora menos nodos
#   gana      = cociente < 0.95   (al menos 5% menos celdas)
#   pierde    = cociente > 1.05   (al menos 5% mas celdas)
#   empata    = en otro caso
#   media geometrica de los cocientes: resume la mejora tipica sin que la dominen
#   las instancias con muchas celdas
set -uo pipefail

ROOT="$HOME/ibex-local"
CSV="${1:-$(ls -td "$ROOT"/results/baseline-*/ | head -1)results.csv}"
[ -s "$CSV" ] || { echo "No existe $CSV"; exit 1; }
echo "archivo: $CSV"
echo

echo "== 1. Estado de las corridas, por relajacion (numero de instancias)"
awk -F, 'NR > 1 { n[$3 "," $4]++; lrs[$3] = 1; st[$4] = 1 }
  END {
    printf "   %-18s", "estado"; for (l in lrs) printf " %8s", l; printf "\n"
    for (s in st) { printf "   %-18s", s; for (l in lrs) printf " %8d", n[l "," s] + 0; printf "\n" }
  }' "$CSV"

echo
echo "== 2. art y compo frente a xn (instancias resueltas por las tres)"
PAIRS="$(awk -F, 'NR > 1 && $4 == "SUCCESS" { key = $1 "/" $2; ok[key]++; c[key, $3] = $10 + 0; t[key, $3] = $9 + 0 }
  END {
    for (k in ok) if (ok[k] == 3 && c[k, "xn"] > 0)
      printf "%s %d %d %d %.4f %.4f %.4f\n", k, c[k, "xn"], c[k, "art"], c[k, "compo"], t[k, "xn"], t[k, "art"], t[k, "compo"]
  }' "$CSV")"
N="$(grep -c . <<<"$PAIRS")"
echo "   instancias comparables: $N"
awk -v n="$N" '
  { for (j = 0; j < 2; j++) {
      lr = (j == 0 ? "art" : "compo"); col = (j == 0 ? $3 : $4)
      r = (col > 0 ? col : 1) / $2
      if (r < 0.95) g[lr]++; else if (r > 1.05) p[lr]++; else e[lr]++
      lg[lr] += log(r)
    }
    tx += $5; ta += $6; tc += $7
  }
  END {
    printf "   %-6s %6s %7s %7s  %-26s\n", "lr", "gana", "empata", "pierde", "media geom. celdas/xn"
    for (j = 0; j < 2; j++) {
      lr = (j == 0 ? "art" : "compo")
      printf "   %-6s %6d %7d %7d  %.3f\n", lr, g[lr] + 0, e[lr] + 0, p[lr] + 0, (n > 0 ? exp(lg[lr] / n) : 0)
    }
    printf "   CPU total sobre estas instancias (s): xn %.1f | art %.1f | compo %.1f\n", tx, ta, tc
  }' <<<"$PAIRS"

for lr in art compo; do
  col=3; [ "$lr" = compo ] && col=4
  echo
  echo "== 3. $lr: 8 mayores mejoras y 8 peores retrocesos en celdas (cociente $lr/xn)"
  RATIOS="$(awk -v c="$col" '{ printf "%.4f %s %d %d\n", ($c > 0 ? $c : 1) / $2, $1, $2, $c }' <<<"$PAIRS" | sort -g)"
  echo "   mejoras:"
  head -8 <<<"$RATIOS" | awk '{ printf "     %-28s xn %8d -> %-8d cociente %.3f\n", $2, $3, $4, $1 }'
  echo "   retrocesos:"
  tail -8 <<<"$RATIOS" | sort -gr | awk '{ printf "     %-28s xn %8d -> %-8d cociente %.3f\n", $2, $3, $4, $1 }'
done

echo
echo "== 4. Corridas que no terminaron con exito"
awk -F, 'NR > 1 && $4 != "SUCCESS" { printf "   %-28s --lr=%-6s %s (exit %s)\n", $1 "/" $2, $3, $4, $12 }' "$CSV" | sort
