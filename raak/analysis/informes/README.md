# Generadores de los informes (Word)

Dos scripts de Node que arman los `.docx` de `results/09-informes/` con la librería `docx`:

| script | produce | insumos |
|---|---|---|
| `informe.js` | `Informe_RAAK_comparacion_aritmeticas_2026-09-30.docx` (informe completo: To-Do, fases, experimentos, conclusiones) | los 18 PNG de `results/08-graficos/` (`python analysis/graficos_resultados.py`) |
| `informe_corto.js` | `Informe_art_vs_RAA_nodos_y_cpu_2026-10-05.docx` (`art` frente a RAA k=0..3, nodos y CPU por instancia) | `resumen.json`, `tabla_por_instancia_art_vs_raa.csv` y las dos figuras de `results/09-informes/` (`python analysis/art_vs_raa.py`) |

Uso, desde esta carpeta (Node 18 o superior):

```bash
npm install docx          # una vez; crea node_modules/ aquí (no se versiona)
node informe_corto.js
node informe.js
```

Los PDF de `results/09-informes/` se exportaron desde Word a partir de esos `.docx`.
