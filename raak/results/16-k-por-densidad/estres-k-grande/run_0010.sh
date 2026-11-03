#!/bin/bash
S=/tmp/claude-1000/-home-jgera-ibex-local/596f84bf-3d30-45df-af73-362b8d0131db/scratchpad/estres
BIN=/home/jgera/ibex-local/ibexopt-raak/build/ibexopt-raak
run() { inst=$1; k=$2; f=$S/inst/synq_n${inst}_d90_pos_normal_s1.bch; log=$S/logs/n${inst}_k${k}.log
  t0=$(date +%s.%N); timeout 300 $BIN --lr=art --arith=raa --knomial_k=$k --trig=auto -t 60 $f > $log 2>&1; code=$?
  echo "exit=$code wall=$(awk -v a=$t0 -v b=$(date +%s.%N) 'BEGIN{printf "%.1f",b-a}')" >> $log; }
export -f run; export S BIN
for inst in 12 15 20 30; do for k in 0 6 8 $inst; do echo "$inst $k"; done; done | xargs -P 8 -n 2 bash -c 'run $0 $1'
echo ESTRES_LISTO > $S/listo
