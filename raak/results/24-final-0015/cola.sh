#!/usr/bin/env bash
# Repeticion de todos los experimentos del borrador con el binario del parche 0015 (15/16-11-2026).
# Una sola cola, P=10, reanudable: cada barrido salta lo ya hecho. Etapas 7 a 9 solo si caben antes de LIMITE.
# Lanzar: setsid nohup bash cola.sh > nohup.log 2>&1 < /dev/null &      Avance: cola.log
set -uo pipefail
ROOT=$HOME/ibex-local; O=$ROOT/results/final-0015-20261115; S=$ROOT/ibex-lib/raak/scripts; I=$ROOT/ibex-lib/raak/instancias
LIMITE=$(date -d "2026-11-16 18:00" +%s)
etapa () { echo "== $(date -Is) ETAPA $1" >> $O/cola.log; }
cabe () { [ $(( $(date +%s) + $1 )) -le "$LIMITE" ]; }
{ echo "inicio cola: $(date -Is) carga: $(cut -d' ' -f1-3 /proc/loadavg)"; md5sum $ROOT/ibexopt-raak/build/ibexopt-raak $ROOT/ibexopt-raak/build/ibexsolve-raak $ROOT/tests/range_eval; } >> $O/meta.txt

etapa "1 barrido final de optimizacion 136x6 1800s"
OUT=$O/nivel2 bash $S/wsl_barrido_final.sh >> $O/nohup-barrido.log 2>&1
etapa "1 LISTA"

for seed in 42 1 2 3; do
  etapa "2 semillas synq n=8, semilla $seed, 600s"
  DIR=$ROOT/instancias/synq-n08 OUT=$O/semillas/s$seed SET=sinteticas VARIANTS="raa_k0 raa_k4 raa_k6" EXTRA="--seed=$seed" TLIM=600 P=10 bash $S/wsl_sweep_dir.sh > $O/semillas-s$seed.log 2>&1
done
for seed in 42 1 2 3; do
  etapa "2 semillas synq n=3,5, semilla $seed, 600s"
  DIR=$ROOT/instancias/synq-n03-n05 OUT=$O/semillas-n03-n05/s$seed SET=sinteticas VARIANTS="raa_k0 raa_k4 raa_k6" EXTRA="--seed=$seed" TLIM=600 P=10 bash $S/wsl_sweep_dir.sh > $O/semillas-n03-n05-s$seed.log 2>&1
done
etapa "2 LISTA"

etapa "3 csp 17x7 900s"
LIST=$O/lista-B.txt OUT=$O/csp-900s CONFIGS="default xn affine_af2 affine_raa affine_raa_k4 affine_raa_k6 default+affine_raa_k6" TLIM=900 P=10 bash $S/wsl_sweep_csp.sh > $O/csp-900s.log 2>&1
etapa "3 LISTA"

etapa "4 csp default +afin 17x4 900s"
LIST=$O/lista-B.txt OUT=$O/csp-default-900s CONFIGS="default default+affine_af2 default+affine_raa default+affine_raa_k6" TLIM=900 P=10 bash $S/wsl_sweep_csp.sh > $O/csp-default-900s.log 2>&1
etapa "4 LISTA"

for seed in 1 2 3 7; do
  etapa "5 csp semilla $seed, 17x4, 900s"
  SEED=$seed BIN=$O/bin-seed.sh LIST=$O/lista-B.txt OUT=$O/csp-semillas/s$seed CONFIGS="default default+affine_af2 default+affine_raa default+affine_raa_k6" TLIM=900 P=10 bash $S/wsl_sweep_csp.sh > $O/csp-semillas-s$seed.log 2>&1
done
etapa "5 LISTA"

etapa "6 costo por evaluacion: range_eval 0014 y 0015 alternados, 3 repeticiones, synq, un proceso"
sleep 60
for r in 1 2 3; do
  for b in 0014 0015; do
    bin=$ROOT/tests/range_eval; [ $b = 0014 ] && bin=$ROOT/tests/range_eval-0014
    [ -s $O/tiempos/range_${b}_r$r.csv ] && continue
    $bin --subboxes 2 --samples 200 $I/sinteticas/*.bch > $O/tiempos/range_${b}_r$r.csv 2> $O/tiempos/log_${b}_r$r.txt
    echo "$b r$r rc=$? $(date -Is) carga: $(cut -d' ' -f1-3 /proc/loadavg)" >> $O/tiempos/meta.txt
  done
done
etapa "6 LISTA"

if cabe 6500; then
  etapa "7 csp 264x5 60s"
  LIST=$O/lista-A.txt OUT=$O/csp-60s CONFIGS="default xn affine_af2 affine_raa affine_raa_k6" TLIM=60 P=10 bash $S/wsl_sweep_csp.sh > $O/csp-60s.log 2>&1
  etapa "7 LISTA"
else etapa "7 OMITIDA (no cabe antes del limite)"; fi

if cabe 4500; then
  etapa "8 csp default +afin 264x4 60s"
  LIST=$O/lista-A.txt OUT=$O/csp-default-60s CONFIGS="default default+affine_af2 default+affine_raa default+affine_raa_k6" TLIM=60 P=9 bash $S/wsl_sweep_csp.sh > $O/csp-default-60s.log 2>&1
  etapa "8 LISTA"
else etapa "8 OMITIDA (no cabe antes del limite)"; fi

if cabe 3800; then
  etapa "9 ex6_2_5/7/13 3600s"
  DIR=$ROOT/instancias/ex6_2-largas OUT=$O/ex6_2-3600s SET=ex6_2 VARIANTS="raa_k0 raa_k4 raa_k6" TLIM=3600 P=10 bash $S/wsl_sweep_dir.sh > $O/ex6_2-3600s.log 2>&1
  etapa "9 LISTA"
else etapa "9 OMITIDA (no cabe antes del limite)"; fi
echo "fin cola: $(date -Is)" >> $O/meta.txt
etapa "COLA_LISTA"
