#!/usr/bin/env bash
# Tras el barrido de 60 s: semillas del solver en las 17 instancias con material, default con y sin relajacion afin.
ROOT=$HOME/ibex-local; O=$ROOT/results/dia2-20261111; S=$ROOT/ibex-lib/raak/scripts
until grep -q COLA_LISTA $O/cola.log 2>/dev/null; do sleep 30; done
for seed in 1 2 3 7; do
  echo "== $(date -Is) ETAPA 2 semilla $seed, 17x4, 900s" >> $O/cola.log
  SEED=$seed BIN=$O/bin-seed.sh LIST=$O/lista-B.txt OUT=$O/csp-semillas/s$seed CONFIGS="default default+affine_af2 default+affine_raa default+affine_raa_k6" TLIM=900 P=10 bash $S/wsl_sweep_csp.sh > $O/csp-semillas-s$seed.log 2>&1
done
echo "== $(date -Is) ETAPA SEMILLAS_LISTAS" >> $O/cola.log
