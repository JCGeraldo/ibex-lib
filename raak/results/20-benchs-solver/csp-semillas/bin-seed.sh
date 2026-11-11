#!/usr/bin/env bash
# envoltorio: ibexsolve-raak con la semilla de la variable SEED
exec "$HOME/ibex-local/ibexopt-raak/build/ibexsolve-raak" --random-seed="${SEED:?}" "$@"
