#!/usr/bin/env bash
# Los dos binarios a la vez (5 procesos cada uno) sobre las mismas instancias y variantes: misma sesion, misma carga.
ROOT=$HOME/ibex-local; O=$ROOT/results/nivel2-2binarios-20261029; D=$ROOT/instancias/comparacion-2binarios
echo "inicio: $(date -Is)" >> $O/meta.txt
BIN=$ROOT/ibexopt-raak/build/ibexopt-raak-pre0009 DIR=$D OUT=$O/pre0009 SET=cmp VARIANTS="raa_k0 raa_k2 raa_k3 raa_k4" P=5 TLIM=1800 bash $ROOT/ibex-lib/raak/scripts/wsl_sweep_dir.sh > $O/sweep_pre0009.log 2>&1 &
BIN=$ROOT/ibexopt-raak/build/ibexopt-raak DIR=$D OUT=$O/0009 SET=cmp VARIANTS="raa_k0 raa_k2 raa_k3 raa_k4" P=5 TLIM=1800 bash $ROOT/ibex-lib/raak/scripts/wsl_sweep_dir.sh > $O/sweep_0009.log 2>&1 &
wait
echo "fin: $(date -Is)" >> $O/meta.txt; echo DOS_BINARIOS_LISTO >> $O/meta.txt
