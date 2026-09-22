#!/usr/bin/env bash
# Fase 1, paso 1.4, tramos de corridas (cada uno < 10 min):
#   regresion : 7 instancias x {xn, art, compo} con --arith=af2 --knomial_k=0, -t 300, comparadas con ref_merged
#   aa_art    : 7 instancias x {aa k=0, aa k=3} con --lr=art,   -t 120 (variantes nuevas: se registran)
#   aa_compo  : idem con --lr=compo
# uso: wsl_fase1_paso14_runs.sh regresion|aa_art|aa_compo
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
S="$ROOT/scripts"; REF="$ROOT/results/fase1-ref"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUTDIR="$ROOT/results/fase1-$STAMP/paso14"
which="$1"
case "$which" in
  regresion)
    OUT="$OUTDIR/regresion" TLIM=300 P=4 REF="$REF/ref_merged.csv" \
    VARIANTS="xn=--lr=xn;art=--lr=art --arith=af2 --knomial_k=0;compo=--lr=compo --arith=af2 --knomial_k=0" \
    MAP="xn=xn,;art=art,;compo=compo," bash "$S/wsl_fase1_runs.sh" | tail -25 ;;
  aa_art)
    OUT="$OUTDIR/aa_art" TLIM=120 P=4 REF="$REF/ref_merged.csv" \
    VARIANTS="art_aa_k0=--lr=art --arith=aa --knomial_k=0;art_aa_k3=--lr=art --arith=aa --knomial_k=3" \
    MAP="" bash "$S/wsl_fase1_runs.sh" | tail -18 ;;
  aa_compo)
    OUT="$OUTDIR/aa_compo" TLIM=120 P=4 REF="$REF/ref_merged.csv" \
    VARIANTS="compo_aa_k0=--lr=compo --arith=aa --knomial_k=0;compo_aa_k3=--lr=compo --arith=aa --knomial_k=3" \
    MAP="" bash "$S/wsl_fase1_runs.sh" | tail -18 ;;
  *) echo "uso: $0 regresion|aa_art|aa_compo"; exit 2 ;;
esac
if [ "$which" != regresion ]; then
  echo "   stats aa_used/aa_products por corrida:"
  for f in "$OUTDIR/$which"/logs/*.log; do printf "   %-40s %s\n" "$(basename "$f" .log)" "$(grep -oE 'aa_products=[0-9]+ aa_used=[0-9]+' "$f")"; done
fi
mkdir -p "$REPO/raak/results/fase1-$STAMP/paso14/$which"
cp "$OUTDIR/$which"/{runs.csv,comparacion.txt,meta.txt} "$REPO/raak/results/fase1-$STAMP/paso14/$which/" 2>/dev/null || cp "$OUTDIR/$which"/{runs.csv,meta.txt} "$REPO/raak/results/fase1-$STAMP/paso14/$which/"
echo "== $which listo ($(date +%T))"
