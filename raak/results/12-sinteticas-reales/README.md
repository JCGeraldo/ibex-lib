# Nivel 2 sobre el subconjunto real y las instancias sinteticas (20-21 de octubre de 2026)

Barrido de `ibexopt-raak` con RAA k=0 (base), k=2 y k=3, relajacion `art`, 1800 s de CPU por corrida, 10 procesos
(`scripts/wsl_sweep_dir.sh`). Instancias: `instancias/reales/` (10) e `instancias/sinteticas/` (78, generadas por
`analysis/generar_sinteticas.py` con el diseno del paper [B]). 264 corridas, 196 resueltas, 68 con tiempo agotado, 0 errores.

| carpeta / archivo | que es |
|---|---|
| `nivel2-reales/`, `nivel2-sinteticas/` | `runs.csv`, `meta.txt` y `tasks.txt` de cada barrido (los logs por corrida quedan en WSL, `~/ibex-local/results/nivel2-*-20261020/logs`). |
| `analisis/` | `analysis/raa_baseline.py` sobre los dos `runs.csv` (README con la tabla resumen, dispersion, perfiles, cociente por instancia, `tabla_raa_baseline.csv`, `resumen.json`) mas `analysis/sinteticas_resumen.py` (`por_n.csv`, `por_configuracion.csv`, `timeouts.csv`, `reales.csv`, `sinteticas_por_n.png`). |

Resultado: en las 64 instancias resueltas por las tres configuraciones, k=3 deja las celdas en 0.672 de RAA k=0 (53 gana / 10 empata / 1 pierde)
y la CPU en 0.796; k=2 en 0.794 y 0.909. En las 18 sinteticas donde las tres agotan el tiempo, k=3 termina con mejor cota inferior en 16.
Informe completo: "Informe RAA-K: instancias sinteticas y k-nomial" (Claude Docs, 21-10-2026).
