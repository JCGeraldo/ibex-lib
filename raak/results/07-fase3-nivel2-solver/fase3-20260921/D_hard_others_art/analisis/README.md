# Resultados del nivel 2 (barrido del solver)

Datos: `runs.csv` (90 corridas, 15 instancias, `-t 1800`). Generado por `raak/analysis/analyze_sweep.py`.

| archivo | que muestra |
|---|---|
| `nivel2_tabla.md` | Todas las tablas: estados, victorias/derrotas/empates, medias geometricas, separacion de efectos y tabla consolidada por instancia. |
| `nivel2_perfil_art.png` | Perfiles de desempeno (Dolan-More) con `art`: para cada tau, fraccion de instancias que la variante resuelve con CPU (izq.) o celdas (der.) a lo sumo tau veces la mejor variante. Mas arriba y mas a la izquierda es mejor. Trazo discontinuo = con k-nomial. |
| `nivel2_dispersion_art.png` | Dispersion log-log por instancia con `art`: celdas (arriba) y CPU (abajo) de cada variante frente a AF2 sin k-nomial. Un punto bajo la diagonal significa que la variante necesito menos. |

Lectura: *celdas* = nodos del B&B (`number of cells`), *CPU* = `cpu time used`. Las medias geometricas se calculan sobre
las instancias resueltas por las dos variantes comparadas; *gana* = cociente < 0.95, *pierde* = cociente > 1.05.
