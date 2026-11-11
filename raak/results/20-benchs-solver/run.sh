#!/usr/bin/env bash
# Cola de la noche 2026-11-11 (una sola sesion, P=10). Reanudable: cada etapa salta lo ya hecho.
ROOT=$HOME/ibex-local; O=$ROOT/results/noche-20261111; S=$ROOT/ibex-lib/raak/scripts
T0=$(date +%s); horas () { echo $(( ($(date +%s) - T0) / 3600 )); }
etapa () { echo "== $(date -Is) ETAPA $1" >> $O/cola.log; }
etapa "1 csp-A 264x5 60s"
LIST=$O/lista-A.txt OUT=$O/csp-A CONFIGS="default xn affine_af2 affine_raa affine_raa_k6" TLIM=60 P=10 bash $S/wsl_sweep_csp.sh > $O/csp-A.log 2>&1
etapa "2 csp-B 17x7 900s"
LIST=$O/lista-B.txt OUT=$O/csp-B CONFIGS="default xn affine_af2 affine_raa affine_raa_k4 affine_raa_k6 default+affine_raa_k6" TLIM=900 P=10 bash $S/wsl_sweep_csp.sh > $O/csp-B.log 2>&1
etapa "3 ex6_2_5/7/13 3600s"
DIR=$ROOT/instancias/ex6_2-largas OUT=$O/ex6_2-largas SET=ex6_2 VARIANTS="raa_k0 raa_k4 raa_k6" TLIM=3600 P=10 bash $S/wsl_sweep_dir.sh > $O/ex6_2-largas.log 2>&1
for seed in 42 1 2 3; do
  if [ "$(horas)" -ge 9 ]; then etapa "4 semilla $seed OMITIDA (pasadas 9 h)"; continue; fi
  etapa "4 semillas synq n=8, semilla $seed, 600s"
  DIR=$ROOT/instancias/synq-n08 OUT=$O/semillas/s$seed SET=sinteticas VARIANTS="raa_k0 raa_k4 raa_k6" EXTRA="--seed=$seed" TLIM=600 P=10 bash $S/wsl_sweep_dir.sh > $O/semillas-s$seed.log 2>&1
done
etapa "COLA_LISTA"
