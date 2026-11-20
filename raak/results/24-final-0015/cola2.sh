#!/bin/bash
# Etapas 8 y 9 pendientes de cola.sh (la maquina virtual de WSL se detuvo el 2026-11-16 a las 15:25).
# 8a: 262 sistemas con P=9 (sin Yamamura1-0400 ni Yamamura1-1000sp, que llegan al tope de memoria);
# 8b: esos dos con P=2, mismo OUT (el barrido salta lo hecho y consolida runs.csv); 9: ex6_2 a una hora.
# Lanzar: setsid nohup bash cola2.sh > nohup2.log 2>&1 < /dev/null &      Avance: cola.log
set -uo pipefail
ROOT=$HOME/ibex-local; O=$ROOT/results/final-0015-20261115; S=$ROOT/ibex-lib/raak/scripts
etapa () { echo "== $(date -Is) ETAPA $1" >> $O/cola.log; }
C="default default+affine_af2 default+affine_raa default+affine_raa_k6"
etapa "8a csp default +afin 262x4 60s P=9 (sesion del 2026-11-20; carga $(cut -d' ' -f1-3 /proc/loadavg))"
LIST=$O/lista-A-sin-yam-grandes.txt OUT=$O/csp-default-60s CONFIGS="$C" TLIM=60 P=9 bash $S/wsl_sweep_csp.sh > $O/csp-default-60s.log 2>&1
etapa "8a LISTA"
etapa "8b csp default +afin, Yamamura1-0400 y Yamamura1-1000sp, P=2"
LIST=$O/lista-A.txt OUT=$O/csp-default-60s CONFIGS="$C" TLIM=60 P=2 bash $S/wsl_sweep_csp.sh >> $O/csp-default-60s.log 2>&1
etapa "8 LISTA"
etapa "9 ex6_2_5/7/13 3600s"
DIR=$ROOT/instancias/ex6_2-largas OUT=$O/ex6_2-3600s SET=ex6_2 VARIANTS="raa_k0 raa_k4 raa_k6" TLIM=3600 P=10 bash $S/wsl_sweep_dir.sh > $O/ex6_2-3600s.log 2>&1
etapa "9 LISTA"
echo "fin cola2: $(date -Is)" >> $O/meta.txt
etapa "COLA2_LISTA"
