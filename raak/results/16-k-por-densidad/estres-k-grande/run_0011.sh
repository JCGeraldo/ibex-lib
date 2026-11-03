#!/bin/bash
S=/tmp/claude-1000/-home-jgera-ibex-local/596f84bf-3d30-45df-af73-362b8d0131db/scratchpad/estres
BIN=/home/jgera/ibex-local/ibexopt-raak/build/ibexopt-raak
run() { inst=$1; k=$2; bud=$3; f=$S/inst/synq_n${inst}_d90_pos_normal_s1.bch; log=$S/logs2/n${inst}_k${k}_b${bud}.log
  t0=$(date +%s.%N); RAAK_NODE_BUDGET=$bud timeout 300 $BIN --lr=art --arith=raa --knomial_k=$k --trig=auto -t 60 $f > $log 2>&1; code=$?
  echo "exit=$code wall=$(awk -v a=$t0 -v b=$(date +%s.%N) 'BEGIN{printf "%.1f",b-a}')" >> $log; }
export -f run; export S BIN
{ for inst in 12 15 20 30; do echo "$inst 0 0"; for k in 6 8 $inst; do for bud in 0 2000; do echo "$inst $k $bud"; done; done; done; } | xargs -P 8 -n 3 bash -c 'run $0 $1 $2'
echo LISTO2 > $S/listo2
