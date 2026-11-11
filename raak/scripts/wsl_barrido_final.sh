#!/usr/bin/env bash
# Barrido definitivo del nivel 2 con el binario final (parches 0001-0014): una sola sesion, reanudable.
# Familias: reales (10), synq (78), synl (24), synt (24) = 136 instancias.
# Variantes por omision: AF2 k=0 y RAA k=0, 2, 3, 4, 6 (816 corridas, 1800 s, P=10; estimado 9 a 10 h).
#
# Variables opcionales:
#   OUT=<dir>        salida (por omision ~/ibex-local/results/nivel2-final-<fecha>)
#   VARIANTS="..."   p. ej. "raa_k0 raa_k2 raa_k3 raa_k4 raa_k6" (sin AF2: unas 7,5 h)
#   TLIM=1800 P=10 SEED=42
#   BOUND=interval|directed   modo de la cota k-nomial    BUDGET=0   presupuesto de la busqueda (0 = sin limite)
# Lanzar y dejar corriendo:
#   setsid nohup bash ~/ibex-local/ibex-lib/raak/scripts/wsl_barrido_final.sh > /dev/null 2>&1 < /dev/null &
# Avance: tail -f $OUT/sweep.log ; termina cuando $OUT/meta.txt contiene BARRIDO_FINAL_LISTO.
# Si se interrumpe, volver a lanzar con el mismo OUT: salta lo ya hecho.
set -uo pipefail
ROOT=$HOME/ibex-local; I=$ROOT/ibex-lib/raak/instancias; S=$ROOT/ibex-lib/raak/scripts
OUT="${OUT:-$ROOT/results/nivel2-final-$(date +%Y%m%d)}"
VARIANTS="${VARIANTS:-af2_k0 raa_k0 raa_k2 raa_k3 raa_k4 raa_k6}"
TLIM="${TLIM:-1800}"; P="${P:-10}"; SEED="${SEED:-42}"; BOUND="${BOUND:-interval}"; BUDGET="${BUDGET:-0}"
FAMILIAS="${FAMILIAS:-reales sinteticas sinteticas-log sinteticas-fun}"
mkdir -p "$OUT"
if pgrep -f 'wsl_sweep_(dir|csp)\.sh' > /dev/null; then echo "ya hay un barrido corriendo; no se lanza" | tee -a "$OUT/meta.txt"; exit 1; fi
{ echo "inicio total: $(date -Is)"; echo "VARIANTS=$VARIANTS TLIM=$TLIM P=$P SEED=$SEED BOUND=$BOUND BUDGET=$BUDGET"
  echo "binario: $(md5sum < $ROOT/ibexopt-raak/build/ibexopt-raak | cut -c1-12)  carga: $(cut -d' ' -f1-3 /proc/loadavg)"; } >> "$OUT/meta.txt"
for s in $FAMILIAS; do
  DIR=$I/$s OUT=$OUT/$s SET=$s VARIANTS="$VARIANTS" P=$P TLIM=$TLIM \
    EXTRA="--seed=$SEED --knomial_bound=$BOUND --knomial_budget=$BUDGET" bash $S/wsl_sweep_dir.sh >> "$OUT/sweep.log" 2>&1
done
echo "fin total: $(date -Is)" >> "$OUT/meta.txt"; echo BARRIDO_FINAL_LISTO >> "$OUT/meta.txt"
