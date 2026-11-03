#!/usr/bin/env bash
ROOT=$HOME/ibex-local; O=$ROOT/results/nivel2-k56-20261102
DIR=$ROOT/instancias/synq-n08-n10 OUT=$O/sweep SET=sinteticas VARIANTS="raa_k4 raa_k5 raa_k6" P=10 TLIM=1800 bash $ROOT/ibex-lib/raak/scripts/wsl_sweep_dir.sh > $O/sweep.log 2>&1
echo K56_LISTO >> $O/sweep/meta.txt
