# Perfilado con perf (28-10-2026)

`perf record -e cpu-clock -F 999` sobre `ibexopt-raak --lr=art --arith=raa --knomial_k=K --trig=auto -t 35` (sin reconstruir nada;
simbolos de la biblioteca estatica). Maquina con carga (barrido de las familias log/trig en paralelo): las fracciones por funcion
siguen siendo validas, los tiempos absolutos no.

| archivo | contenido |
|---|---|
| `plano_<k>_<instancia>.txt` | perfil plano (tiempo propio por funcion, `--no-children`), 40 primeras lineas |
| `inclusivo_k3_synq_n08_d50_pos_normal_s1.txt` | perfil inclusivo (`--call-graph dwarf`, `--children`): fraccion del tiempo total dentro de cada funcion y sus llamadas |

Resumen (fraccion del tiempo total de CPU del solver, `synq_n08_d50_pos_normal_s1`):

| componente | k=0 | k=3 | k=4 |
|---|---|---|---|
| `knomial_rewrite` propio | 0 | 4.9 % | 6.8 % |
| malloc / free / arboles rojinegros (std::set, std::map) | 9.1 % | 15.8 % | 19.5 % |
| `knomial_rewrite` inclusivo (con sus set/map) | 0 | 17.0 % | (no medido) |
| producto afin `AF_fAF2::operator*=` inclusivo | - | 21.5 % | - |
| linealizacion afin completa (`LinearizerAffineT::linearize`) | - | 39.7 % | - |
| LP del `CtcPolytopeHull` (`optimizer`) | - | 28.1 % | - |
