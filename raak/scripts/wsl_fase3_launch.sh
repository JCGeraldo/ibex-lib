#!/usr/bin/env bash
# Fase 3, nivel 2: prueba corta del barrido y, si pasa, lanza en segundo plano (setsid nohup) la cadena
# de etapas, en este orden (cada etapa reanudable y con su propia carpeta):
#   A  easy+medium, compo (6 variantes + xn)      B  easy+medium, art (6 variantes)
#   C  hard+others, compo (6 + xn)                D  hard+others, art (6)
# Estrategia de computo: P=12 procesos (16 hilos disponibles), limite -t 1800 s de CPU por corrida,
# instancias ordenadas por dificultad creciente. Estado: scripts/wsl_fase3_status.sh <OUT>.
# Variables: STAMP, TLIM=1800, P=12, TRIG=auto
set -uo pipefail
ROOT="$HOME/ibex-local"; S="$ROOT/scripts"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
STAMP="${STAMP:-$(date +%Y%m%d)}"; TLIM="${TLIM:-1800}"; P="${P:-12}"; TRIG="${TRIG:-auto}"
BASE="$ROOT/results/fase3-$STAMP"; mkdir -p "$BASE" "$ROOT/logs"
cp "$REPO"/raak/scripts/wsl_fase3_*.sh "$S"/; sed -i 's/\r$//' "$S"/wsl_fase3_*.sh; chmod +x "$S"/wsl_fase3_*.sh

echo "== prueba corta (ex5_4_3, ex2_1_1; -t 20)"
rm -rf "$BASE/smoke"
OUT="$BASE/smoke" SETS="easy" LRS="compo" ONLY="ex5_4_3,ex2_1_1" TLIM=20 P=7 TRIG="$TRIG" bash "$S/wsl_fase3_sweep.sh" 2>&1 | tail -16
n_ok=$(awk -F, '$3=="SUCCESS"' "$BASE/smoke/runs.csv" | wc -l)
echo "   corridas SUCCESS: $n_ok de 14"
[ "$n_ok" -eq 14 ] || { echo "*** la prueba corta fallo; no se lanza el barrido"; exit 1; }

CHAIN="$BASE/chain.sh"
cat > "$CHAIN" <<EOC
#!/usr/bin/env bash
S="$S"; BASE="$BASE"
OUT="\$BASE/A_easy_medium_compo" SETS="easy medium" LRS="compo" WITH_XN=1 TLIM=$TLIM P=$P TRIG=$TRIG bash "\$S/wsl_fase3_sweep.sh"
OUT="\$BASE/B_easy_medium_art"   SETS="easy medium" LRS="art"   WITH_XN=0 TLIM=$TLIM P=$P TRIG=$TRIG bash "\$S/wsl_fase3_sweep.sh"
OUT="\$BASE/C_hard_others_compo" SETS="hard others" LRS="compo" WITH_XN=1 TLIM=$TLIM P=$P TRIG=$TRIG bash "\$S/wsl_fase3_sweep.sh"
OUT="\$BASE/D_hard_others_art"   SETS="hard others" LRS="art"   WITH_XN=0 TLIM=$TLIM P=$P TRIG=$TRIG bash "\$S/wsl_fase3_sweep.sh"
echo "== cadena terminada \$(date -Is)"
EOC
chmod +x "$CHAIN"
setsid nohup bash "$CHAIN" > "$BASE/chain.log" 2>&1 < /dev/null &
sleep 2
echo "== lanzado: PID $! ; log $BASE/chain.log"
echo "   estado: bash ~/ibex-local/scripts/wsl_fase3_status.sh $BASE/A_easy_medium_compo"
