#!/usr/bin/env bash
# Parche 0015 (umbrales relativos): binario 0014 contra 0015 en la misma sesion, 5 procesos cada uno a la vez.
set -uo pipefail
ROOT=~/ibex-local; OUT=$ROOT/results/parche0015-20261115; SW=$ROOT/ibex-lib/raak/scripts/wsl_sweep_dir.sh
EX="--seed=42 --knomial_bound=interval --knomial_budget=0"
echo "inicio: $(date -Is) carga: $(cut -d' ' -f1-3 /proc/loadavg)" > $OUT/meta.txt
md5sum $ROOT/ibexopt-raak/build/ibexopt-raak $ROOT/ibexopt-raak/build/ibexopt-raak-0014 >> $OUT/meta.txt
lado () {  # $1 = etiqueta, $2 = binario, $3 = variantes
  for fam in ex62 synq8; do
    DIR=$OUT/inst-$fam SET=$fam OUT=$OUT/$1/$fam VARIANTS="$3" TLIM=900 P=5 EXTRA="$EX" BIN=$2 bash $SW >> $OUT/$1.log 2>&1
  done
}
lado b0014 $ROOT/ibexopt-raak/build/ibexopt-raak-0014 "raa_k4 raa_k6" &
lado b0015 $ROOT/ibexopt-raak/build/ibexopt-raak "raa_k0 raa_k4 raa_k6" &
wait
echo "fin: $(date -Is)" >> $OUT/meta.txt
echo COMPARACION_LISTA >> $OUT/meta.txt
