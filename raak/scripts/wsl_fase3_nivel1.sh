#!/usr/bin/env bash
# Fase 3, nivel 1: compila tests/range_eval.cpp y lo corre sobre los conjuntos de benchs/optim indicados,
# sin resolver: sobreestimacion de las seis variantes sobre objetivo y restricciones, caja inicial y
# sub-cajas. Luego corre el analisis en Python y copia todo al repo.
# Variables: SETS (por defecto todos los conjuntos con .bch), STAMP, TRIG=auto, SUBBOXES=2, SAMPLES=200
set -uo pipefail
ROOT="$HOME/ibex-local"
REPO=/mnt/c/Users/evapo/OneDrive/Documentos/GitHub/ibex-lib
T="$ROOT/tests"; BENCHS="$ROOT/ibex-lib/benchs/optim"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUT="$ROOT/results/fase3-$STAMP/nivel1"; mkdir -p "$OUT"
SETS="${SETS:-easy medium hard others blowup unsolved benchs-unconstrainedoptim}"
TRIG="${TRIG:-auto}"; SUBBOXES="${SUBBOXES:-2}"; SAMPLES="${SAMPLES:-200}"
export PKG_CONFIG_PATH="$ROOT/prefix/share/pkgconfig:$ROOT/prefix/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
fail () { echo "*** $1"; exit 1; }

cp "$REPO"/raak/tests/range_eval.cpp "$T"/; sed -i 's/\r$//' "$T/range_eval.cpp"
mkdir -p "$ROOT/analysis"; cp "$REPO"/raak/analysis/*.py "$ROOT/analysis/"; sed -i 's/\r$//' "$ROOT/analysis"/*.py
echo "== compilar range_eval ($(date +%T))"
g++ -std=c++11 -O2 -msse3 -frounding-math "$T/range_eval.cpp" $(pkg-config --cflags ibex-affine ibex) -o "$T/range_eval" $(pkg-config --libs ibex-affine ibex) 2> "$ROOT/logs/n1-build.log" || { tail -20 "$ROOT/logs/n1-build.log"; fail "build"; }

FILES=(); for s in $SETS; do for f in "$BENCHS/$s"/*.bch; do [ -f "$f" ] && FILES+=("$f"); done; done
echo "== range_eval sobre ${#FILES[@]} instancias (SETS=$SETS, TRIG=$TRIG) ($(date +%T))"
{ echo "SETS=$SETS TRIG=$TRIG SUBBOXES=$SUBBOXES SAMPLES=$SAMPLES instancias=${#FILES[@]}"; echo "ibex-affine: $(git -C "$ROOT/ibex-affine" log -1 --format='%h') + parches: $(git -C "$ROOT/ibex-affine" status --short -- src | tr '\n' ' ')"; echo "inicio: $(date -Is)"; } > "$OUT/meta.txt"
"$T/range_eval" --subboxes "$SUBBOXES" --samples "$SAMPLES" --trig "$TRIG" "${FILES[@]}" > "$OUT/range.csv" 2> "$OUT/range_log.txt"; rc=$?
echo "fin: $(date -Is) exit=$rc" >> "$OUT/meta.txt"
tail -3 "$OUT/range_log.txt"; echo "   filas: $(( $(wc -l < "$OUT/range.csv") - 1 ))"

echo "== analisis ($(date +%T))"
python3 "$ROOT/analysis/analyze_range.py" "$OUT/range.csv" "$OUT/analisis" && head -30 "$OUT/analisis/nivel1_tabla.md"

mkdir -p "$REPO/raak/results/fase3-$STAMP/nivel1"
cp "$OUT"/meta.txt "$OUT"/range_log.txt "$REPO/raak/results/fase3-$STAMP/nivel1/"
gzip -c "$OUT/range.csv" > "$REPO/raak/results/fase3-$STAMP/nivel1/range.csv.gz"
cp -r "$OUT/analisis" "$REPO/raak/results/fase3-$STAMP/nivel1/"
echo "== listo ($(date +%T))"
