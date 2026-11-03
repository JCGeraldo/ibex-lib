#!/usr/bin/env bash
# Barrido completo del nivel 2 con el parche 0009: k=0,2,3,4 sobre reales, synq, synl y synt en una sola sesion.
ROOT=$HOME/ibex-local; O=$ROOT/results/nivel2-0009-20261029; I=$ROOT/ibex-lib/raak/instancias
echo "inicio total: $(date -Is)" >> $O/meta.txt
for s in reales sinteticas sinteticas-log sinteticas-fun; do
  DIR=$I/$s OUT=$O/$s VARIANTS="raa_k0 raa_k2 raa_k3 raa_k4" P=10 TLIM=1800 bash $ROOT/ibex-lib/raak/scripts/wsl_sweep_dir.sh >> $O/sweep.log 2>&1
done
echo "fin total: $(date -Is)" >> $O/meta.txt
echo NIVEL2_0009_LISTO >> $O/meta.txt
