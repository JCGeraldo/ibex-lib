#!/usr/bin/env bash
# Verifica el parche local de LinearizerAffine2 (guarda is_active() antes de leer
# los coeficientes de una forma afin):
#   1. guarda el parche como archivo (no se hace commit)
#   2. recompila, testea e instala ibex-affine
#   3. recompila ibexopt-raak contra la biblioteca nueva
#   4. repite el programa minimo del crash
#   5. repite las corridas que antes daban segfault
#   6. repite la prueba corta del barrido y la compara con la corrida previa al parche
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HOME/ibex-local"
BIN="$ROOT/ibexopt-raak/build/ibexopt-raak"
EASY="$ROOT/ibex-lib/benchs/optim/easy"
BEFORE="$ROOT/results/baseline-20260913-190737/results.csv"
ONLY_LIST="ex5_4_3,wall,rosenbrock,hs071,ex2_1_1,himmel16,ex7_3_4"

echo "== 1. parche en ibex-affine (rama $(git -C "$ROOT/ibex-affine" branch --show-current), sin commit)"
mkdir -p "$ROOT/patches"
PATCH="$ROOT/patches/0001-LinearizerAffine2-omitir-formas-no-activas.patch"
git -C "$ROOT/ibex-affine" diff > "$PATCH"
if [ ! -s "$PATCH" ]; then
  echo "*** no hay cambios en ibex-affine: el parche no esta aplicado"
  exit 1
fi
echo "   guardado en $PATCH"
cat "$PATCH"

echo
echo "== 2. recompilar, testear e instalar ibex-affine"
if ! bash "$HERE/wsl_build_affine.sh"; then
  echo "*** fallo la compilacion o los tests de ibex-affine"
  exit 1
fi

echo
echo "== 3. recompilar ibexopt-raak"
if ! make -C "$ROOT/ibexopt-raak/build" -B > "$ROOT/logs/cli-make-patch.log" 2>&1; then
  echo "*** fallo la compilacion de ibexopt-raak"
  tail -30 "$ROOT/logs/cli-make-patch.log"
  exit 1
fi
echo "   ok"

echo
echo "== 4. programa minimo (antes del parche: segfault en el paso [3])"
bash "$HERE/wsl_crashtest.sh"

echo
echo "== 5. corridas que antes daban segfault"
for spec in "art:$EASY/wall.bch" "compo:$EASY/wall.bch" "art:$HERE/wall_sym.bch"; do
  lr="${spec%%:*}"
  f="${spec#*:}"
  out="$("$BIN" --lr="$lr" -t 10 "$f" 2>&1)"
  code=$?
  clean="$(sed -r 's/\x1b\[[0-9;]*m//g' <<<"$out")"
  st="$(grep -m1 -E 'successful|infeasible|time limit|no feasible|unbounded|unreached' <<<"$clean" | sed 's/^ *//')"
  fstar="$(grep -m1 'f\* in' <<<"$clean" | tr -d '\t' | sed 's/^ *//')"
  cells="$(awk -F'\t+' '/number of cells/ {print $2}' <<<"$clean")"
  echo "   --lr=$lr $(basename "$f"): exit=$code | ${st:-(sin estado)} | ${fstar:-} | celdas=${cells:-}"
done

echo
echo "== 6. prueba corta del barrido, comparada con la corrida previa al parche"
ONLY="$ONLY_LIST" TLIM=10 P=4 bash "$HERE/wsl_baseline.sh" > "$ROOT/logs/baseline-smoke-postpatch.log" 2>&1
AFTER="$(ls -td "$ROOT"/results/baseline-*/ | head -1)results.csv"
echo "   antes del parche:   $BEFORE"
echo "   despues del parche: $AFTER"
ROWS="$(awk -F, 'FNR == 1 { next }
  NR == FNR { k = $2 " --lr=" $3; s0[k] = $4; c0[k] = $10; next }
  {
    k = $2 " --lr=" $3
    if (s0[k] == $4 && c0[k] == $10)  tag = "igual"
    else if (s0[k] == "ERROR")         tag = "CAMBIO esperado (antes: crash)"
    else                               tag = "CAMBIO NO esperado"
    printf "   %-26s %-8s -> %-8s celdas %6s -> %-6s [%s]\n", k, s0[k], $4, c0[k], $10, tag
  }' "$BEFORE" "$AFTER")"
printf "   %-26s %-20s %-24s %s\n" "instancia" "estado antes -> despues" "celdas antes -> despues" "comparacion"
sort <<<"$ROWS"
echo "   filas iguales: $(grep -c '\[igual\]' <<<"$ROWS")"
echo "   cambios esperados (antes crash): $(grep -c 'CAMBIO esperado' <<<"$ROWS")"
echo "   cambios NO esperados: $(grep -c 'CAMBIO NO esperado' <<<"$ROWS")"
