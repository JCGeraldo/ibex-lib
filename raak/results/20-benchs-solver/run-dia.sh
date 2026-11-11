#!/usr/bin/env bash
# Cola del dia 2026-11-11 (una sesion, P=10): default con y sin relajacion afin; semillas en synq n=3 y n=5.
ROOT=$HOME/ibex-local; O=$ROOT/results/dia-20261111; S=$ROOT/ibex-lib/raak/scripts
etapa () { echo "== $(date -Is) ETAPA $1" >> $O/cola.log; }
etapa "1 csp default +afin 17x4 900s"
LIST=$O/lista-B.txt OUT=$O/csp-default CONFIGS="default default+affine_af2 default+affine_raa default+affine_raa_k6" TLIM=900 P=10 bash $S/wsl_sweep_csp.sh > $O/csp-default.log 2>&1
for seed in 42 1 2 3; do
  etapa "2 semillas synq n=3,5, semilla $seed, 600s"
  DIR=$ROOT/instancias/synq-n03-n05 OUT=$O/semillas/s$seed SET=sinteticas VARIANTS="raa_k0 raa_k4 raa_k6" EXTRA="--seed=$seed" TLIM=600 P=10 bash $S/wsl_sweep_dir.sh > $O/semillas-s$seed.log 2>&1
done
etapa "COLA_LISTA"
