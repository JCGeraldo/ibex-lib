#!/usr/bin/env bash
# 2026-11-11 (tarde): benchs/solver completo, contractor por omision con y sin relajacion afin, 60 s, P=9.
ROOT=$HOME/ibex-local; O=$ROOT/results/dia2-20261111; S=$ROOT/ibex-lib/raak/scripts
echo "== $(date -Is) ETAPA 1 csp default +afin 264x4 60s" >> $O/cola.log
LIST=$O/lista-A.txt OUT=$O/csp-default-60s CONFIGS="default default+affine_af2 default+affine_raa default+affine_raa_k6" TLIM=60 P=9 bash $S/wsl_sweep_csp.sh > $O/csp-default-60s.log 2>&1
echo "== $(date -Is) ETAPA COLA_LISTA" >> $O/cola.log
