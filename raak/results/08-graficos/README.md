# Graficos de los experimentos RAA-K

Fuente: los CSV de `raak/results/`. Un grafico por experimento, en orden cronologico. Generado por `analysis/graficos_resultados.py`.

| archivo | que muestra |
|---|---|
| `01_linea_base_perfil_celdas.png` | Linea base sin modificaciones: que fraccion de instancias resuelve cada relajacion con a lo sumo X veces las celdas de la mejor. |
| `02_prototipo_v1_knomial_vs_base.png` | Primer prototipo (solo productos): cociente de celdas por instancia frente a la misma relajacion sin k-nomial. |
| `03_prototipo_v2_vs_v1_cuadrados.png` | Prototipo v2 frente a v1: cada punto es una instancia; ambos ejes son el cociente de celdas frente a la base. |
| `04_ablacion_raa_vs_bloques_knomial.png` | Ablacion del prototipo: para cada instancia, celdas con solo la parte RAA (k=1) y con RAA mas bloques (k=3), ambas frente a la base. |
| `05_qplib_reduccion_radio_raak.png` | QPLIB evaluado con el port C++: reduccion porcentual del radio de la forma afin con RAA-K k=3 frente a fAF2, por formulacion. |
| `06_sobrecosto_cpu_prototipo.png` | Tiempo de CPU de las variantes RAA frente a art en la misma sesion, con repeticiones, para medir el sobrecosto sin ruido de paralelismo. |
| `07_fase1_regresion_refactor.png` | Regresion de la Fase 1: celdas por instancia y variante tras el refactor; coinciden exactamente con las referencias guardadas antes. |
| `08_validacion_contencion_y_fidelidad.png` | Resumen de todas las pruebas de validez: cuantos casos evaluo cada una y su resultado. |
| `09_fase2_trig_sobreestimacion_por_modo.png` | Fase 2: media geometrica de anchura afin / rango exacto por funcion y modo de linealizacion, en AF2 y en AA. |
| `10_fase2_trig_sobreestimacion_por_anchura.png` | Fase 2: sobreestimacion en funcion de la anchura del intervalo de entrada, para sin y para sin*cos, por modo. |
| `11_fase2_trig_en_el_solver.png` | Fase 2: celdas del B&B por instancia y modo de linealizacion trigonometrica, con art y con compo. |
| `12_fase3_nivel1_sobreestimacion_por_escala.png` | Nivel 1: media geometrica de la sobreestimacion de cada variante segun el tamano de la caja, con la extension de intervalos como referencia. |
| `13_fase3_nivel1_efectos_por_par.png` | Nivel 1: numero de ternas mas estrechas o mas anchas en mas de 5 % para cada par de variantes. |
| `14_fase3_A_easy_medium_compo_perfiles.png` | Nivel 2, Etapa A: easy+medium, relajacion compo: perfil de desempeno en celdas y en CPU; mas arriba y mas a la izquierda es mejor. |
| `15_fase3_B_easy_medium_art_perfiles.png` | Nivel 2, Etapa B: easy+medium, relajacion art: perfil de desempeno en celdas y en CPU; mas arriba y mas a la izquierda es mejor. |
| `16_fase3_C_hard_others_compo_perfiles.png` | Nivel 2, Etapa C: hard+others, relajacion compo: perfil de desempeno en celdas y en CPU; mas arriba y mas a la izquierda es mejor. |
| `17_fase3_D_hard_others_art_perfiles.png` | Nivel 2, Etapa D: hard+others, relajacion art: perfil de desempeno en celdas y en CPU; mas arriba y mas a la izquierda es mejor. |
| `18_fase3_resumen_medias_geometricas.png` | Nivel 2, consolidado: media geometrica de celdas y CPU de cada variante frente a AF2, por etapa. |
