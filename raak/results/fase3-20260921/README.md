# Resultados de la Fase 3 (2026-09-21)

Comparación de las seis variantes (AF2 | RAA | AA) × (sin | con k-nomial) más el control `xn`.
Binario y parches: ver `meta.txt` de cada carpeta. Diseño y lecturas: `../../docs/FASE3_EXPERIMENTOS.md`.

| carpeta | qué contiene |
|---|---|
| `nivel1/` | Sobreestimación de rangos sin resolver (`tests/range_eval.cpp`): `range.csv.gz` (una fila por instancia × función × caja × variante), `range_log.txt`, `meta.txt` y `analisis/` |
| `nivel1/analisis/nivel1_tabla.md` | Tablas: sobreestimación por variante y escala de caja, separación de efectos (aritmética / k-nomial), por conjunto |
| `nivel1/analisis/nivel1_gm_por_escala.png` | Media geométrica de anchura afín / rango muestreado por variante y tamaño de caja; la línea punteada gris es la extensión natural de intervalos. Más abajo es mejor. |
| `nivel1/analisis/nivel1_efectos.png` | Por par de variantes, cuántas ternas (instancia, función, caja) quedan más estrechas (verde) o más anchas (rojo) en más de 5 %; el resto son iguales. |
| `A_easy_medium_compo/` | Barrido del solver, `easy`+`medium`, relajación `compo`, 6 variantes + `xn`, `-t 1800`: `runs.csv`, `meta.txt`, `analisis/` (con su propio `README.md` que explica cada gráfico) |
| `B_easy_medium_art/` | Ídem con relajación `art` (solo afín, sin X-Taylor) |
| `C_hard_others_compo/`, `D_hard_others_art/` | Ídem para `hard`+`others` |

Columnas de `runs.csv` (nivel 2): `instancia, variante, estado, celdas, f_lb, f_ub, cpu_s, wall_s, exit,
raak_stats, trig_stats`. *celdas* = nodos del B&B; *cpu_s* = tiempo de CPU medido por el optimizador
(el límite `-t` es sobre este valor); `raak_stats`/`trig_stats` = contadores de cuántas veces actuó cada
mecanismo (k-nomial, cuadrados RAA, corner test, AA; linealización de sin/cos).

Regenerar el análisis de cualquier etapa: `python3 raak/analysis/analyze_sweep.py <etapa>/runs.csv <etapa>/analisis --tlim 1800`.
Los logs por corrida (`logs/`) quedan en WSL (`~/ibex-local/results/fase3-20260921/`) y no se copian al repo.
