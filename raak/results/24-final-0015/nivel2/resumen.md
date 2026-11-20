## Resueltas por variante
| familia | instancias | af2_k0 | raa_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 | por todas |
|---|---|---|---|---|---|---|---|---|
| benchmarks | 10 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| synq | 78 | 56 | 61 | 61 | 61 | 61 | 62 | 56 |
| synl | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 |
| synt | 24 | 21 | 23 | 23 | 23 | 23 | 23 | 21 |

## Cocientes frente a RAA k=0 (celdas / CPU; instancias resueltas por las seis variantes)
| familia | n | af2_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|---|
| benchmarks | 6 | 1.000 / 0.991 | 0.972 / 0.971 | 0.957 / 0.968 | 0.957 / 0.996 | 0.957 / 0.997 |
| synq | 56 | 1.568 / 1.426 | 0.766 / 0.809 | 0.643 / 0.682 | 0.584 / 0.615 | 0.547 / 0.581 |
| synl | 24 | 1.163 / 1.125 | 0.897 / 0.974 | 0.871 / 0.954 | 0.840 / 0.958 | 0.811 / 0.844 |
| synt | 21 | 1.139 / 0.949 | 0.975 / 0.886 | 0.947 / 0.826 | 0.930 / 0.849 | 0.913 / 0.805 |

## Cocientes frente a RAA k=0 (celdas / CPU; instancias resueltas por las cinco variantes RAA, sin exigir AF2)
| familia | n | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|
| benchmarks | 6 | 0.972 / 0.971 | 0.957 / 0.968 | 0.957 / 0.996 | 0.957 / 0.997 |
| synq | 61 | 0.764 / 0.809 | 0.640 / 0.680 | 0.575 / 0.608 | 0.532 / 0.566 |
| synl | 24 | 0.897 / 0.974 | 0.871 / 0.954 | 0.840 / 0.958 | 0.811 / 0.844 |
| synt | 23 | 0.956 / 0.881 | 0.922 / 0.820 | 0.891 / 0.816 | 0.887 / 0.788 |

## Lo mismo, solo instancias con CPU de RAA k=0 >= 1 s
| familia | n | af2_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|---|
| benchmarks | 5 | 1.000 / 0.969 | 0.967 / 0.971 | 0.949 / 0.953 | 0.949 / 0.971 | 0.949 / 0.977 |
| synq | 23 | 1.961 / 1.797 | 0.726 / 0.787 | 0.566 / 0.621 | 0.475 / 0.526 | 0.415 / 0.461 |
| synl | 10 | 1.473 / 1.343 | 0.843 / 0.910 | 0.798 / 0.873 | 0.728 / 0.785 | 0.668 / 0.729 |
| synt | 9 | 1.265 / 1.196 | 0.943 / 0.992 | 0.895 / 0.949 | 0.866 / 0.931 | 0.831 / 0.895 |

## Pares (celdas / CPU, resueltas por ambas) y conteo de instancias con menos, igual o mas celdas
| familia | par | n | celdas | CPU | menos | igual | mas |
|---|---|---|---|---|---|---|---|
| benchmarks | raa_k0/af2_k0 | 6 | 1.000 | 1.009 | 0 | 6 | 0 |
| benchmarks | raa_k4/raa_k3 | 6 | 1.000 | 1.029 | 0 | 6 | 0 |
| benchmarks | raa_k6/raa_k4 | 6 | 1.000 | 1.001 | 0 | 6 | 0 |
| benchmarks | raa_k6/raa_k0 | 6 | 0.957 | 0.997 | 5 | 1 | 0 |
| benchmarks | raa_k6/af2_k0 | 6 | 0.957 | 1.006 | 5 | 1 | 0 |
| synq | raa_k0/af2_k0 | 56 | 0.638 | 0.701 | 50 | 6 | 0 |
| synq | raa_k4/raa_k3 | 61 | 0.899 | 0.894 | 38 | 21 | 2 |
| synq | raa_k6/raa_k4 | 61 | 0.924 | 0.932 | 26 | 35 | 0 |
| synq | raa_k6/raa_k0 | 61 | 0.532 | 0.566 | 57 | 3 | 1 |
| synq | raa_k6/af2_k0 | 56 | 0.349 | 0.408 | 53 | 3 | 0 |
| synl | raa_k0/af2_k0 | 24 | 0.860 | 0.889 | 15 | 6 | 3 |
| synl | raa_k4/raa_k3 | 24 | 0.964 | 1.005 | 8 | 15 | 1 |
| synl | raa_k6/raa_k4 | 24 | 0.966 | 0.880 | 5 | 16 | 3 |
| synl | raa_k6/raa_k0 | 24 | 0.811 | 0.844 | 14 | 9 | 1 |
| synl | raa_k6/af2_k0 | 24 | 0.698 | 0.750 | 16 | 5 | 3 |
| synt | raa_k0/af2_k0 | 21 | 0.878 | 1.054 | 11 | 8 | 2 |
| synt | raa_k4/raa_k3 | 23 | 0.967 | 0.996 | 8 | 13 | 2 |
| synt | raa_k6/raa_k4 | 23 | 0.996 | 0.966 | 6 | 16 | 1 |
| synt | raa_k6/raa_k0 | 23 | 0.887 | 0.788 | 11 | 9 | 3 |
| synt | raa_k6/af2_k0 | 21 | 0.801 | 0.849 | 11 | 8 | 2 |

## Casos con mas celdas que la variante de referencia
| familia | instancia | par | celdas | referencia | cociente |
|---|---|---|---|---|---|
| synq | synq_n05_d20_posneg_normal_s2 | raa_k4/raa_k3 | 24 | 22 | 1.091 |
| synq | synq_n05_d50_posneg_normal_s2 | raa_k4/raa_k3 | 810 | 806 | 1.005 |
| synq | synq_n03_d50_posneg_normal_s1 | raa_k6/raa_k0 | 22 | 18 | 1.222 |
| synl | synl_n05_d90_s2 | raa_k4/raa_k3 | 44 | 42 | 1.048 |
| synl | synl_n05_d90_s3 | raa_k6/raa_k4 | 86 | 84 | 1.024 |
| synl | synl_n08_d90_s2 | raa_k6/raa_k4 | 1316 | 1216 | 1.082 |
| synl | synl_n10_d50_s3 | raa_k6/raa_k4 | 186 | 182 | 1.022 |
| synl | synl_n08_d50_s1 | raa_k6/raa_k0 | 124 | 122 | 1.016 |
| synl | synl_n05_d50_s1 | raa_k0/af2_k0 | 14 | 12 | 1.167 |
| synl | synl_n08_d50_s1 | raa_k0/af2_k0 | 122 | 54 | 2.259 |
| synl | synl_n08_d50_s2 | raa_k0/af2_k0 | 14 | 12 | 1.167 |
| synt | synt_n08_d90_s3 | raa_k4/raa_k3 | 30892 | 26834 | 1.151 |
| synt | synt_n10_d90_s3 | raa_k4/raa_k3 | 117324 | 113162 | 1.037 |
| synt | synt_n10_d90_s2 | raa_k6/raa_k4 | 222074 | 131684 | 1.686 |
| synt | synt_n05_d50_s1 | raa_k6/raa_k0 | 186 | 164 | 1.134 |
| synt | synt_n08_d50_s1 | raa_k6/raa_k0 | 1740 | 1542 | 1.128 |
| synt | synt_n08_d50_s2 | raa_k6/raa_k0 | 1144 | 1122 | 1.020 |
| synt | synt_n08_d50_s3 | raa_k0/af2_k0 | 10490 | 10134 | 1.035 |
| synt | synt_n10_d50_s1 | raa_k0/af2_k0 | 2616 | 2406 | 1.087 |

## Por numero de variables (cocientes de celdas / CPU frente a RAA k=0, resueltas por las seis)
| familia | n vars | instancias | resueltas por todas | raa_k2 | raa_k3 | raa_k4 | raa_k6 | k6/k4 |
|---|---|---|---|---|---|---|---|---|
| synq | 3 | 18 | 18 | 0.841 / 0.863 | 0.794 / 0.792 | 0.794 / 0.762 | 0.794 / 0.757 | 1.000 / 0.993 |
| synq | 5 | 24 | 24 | 0.729 / 0.768 | 0.586 / 0.633 | 0.528 / 0.579 | 0.512 / 0.575 | 0.970 / 0.992 |
| synq | 8 | 18 | 13 | 0.737 / 0.808 | 0.575 / 0.636 | 0.465 / 0.517 | 0.381 / 0.427 | 0.820 / 0.826 |
| synq | 10 | 18 | 1 | 0.766 / 0.902 | 0.602 / 0.680 | 0.491 / 0.525 | 0.339 / 0.369 | 0.692 / 0.702 |
| synl | 3 | 6 | 6 | 0.935 / 1.082 | 0.935 / 1.118 | 0.935 / 1.346 | 0.935 / 0.922 | 1.000 / 0.685 |
| synl | 5 | 6 | 6 | 0.918 / 0.946 | 0.895 / 0.923 | 0.902 / 0.933 | 0.906 / 0.921 | 1.004 / 0.987 |
| synl | 8 | 6 | 6 | 0.877 / 0.938 | 0.862 / 0.912 | 0.778 / 0.817 | 0.730 / 0.785 | 0.939 / 0.961 |
| synl | 10 | 6 | 6 | 0.860 / 0.937 | 0.799 / 0.879 | 0.759 / 0.822 | 0.701 / 0.760 | 0.923 / 0.924 |
| synt | 3 | 6 | 6 | 1.000 / 0.638 | 1.000 / 0.546 | 1.000 / 0.659 | 1.000 / 0.587 | 1.000 / 0.891 |
| synt | 5 | 6 | 6 | 1.001 / 1.038 | 0.977 / 1.016 | 0.962 / 0.954 | 0.960 / 0.944 | 0.997 / 0.989 |
| synt | 8 | 6 | 6 | 0.939 / 0.991 | 0.882 / 0.937 | 0.859 / 0.934 | 0.822 / 0.897 | 0.957 / 0.960 |
| synt | 10 | 6 | 3 | 0.952 / 0.993 | 0.920 / 0.974 | 0.881 / 0.924 | 0.849 / 0.892 | 0.965 / 0.966 |

## Resueltas solo por algunas variantes
| familia | instancia | af2_k0 | raa_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|---|---|
| synq | synq_n08_d20_pos_normal_s3 | - | - | - | - | - | 1556 s |
| synq | synq_n08_d90_pos_normal_s2 | - | 1228 s | 951 s | 708 s | 519 s | 373 s |
| synq | synq_n08_d90_posneg_normal_s3 | - | 775 s | 574 s | 455 s | 354 s | 293 s |
| synq | synq_n10_d20_posneg_normal_s2 | - | 1787 s | 1615 s | 1357 s | 1269 s | 1179 s |
| synq | synq_n10_d50_posneg_normal_s1 | - | 1646 s | 1302 s | 1157 s | 984 s | 768 s |
| synq | synq_n10_d50_posneg_normal_s3 | - | 1184 s | 1009 s | 803 s | 606 s | 430 s |
| synt | synt_n10_d90_s2 | - | 1494 s | 1499 s | 1386 s | 892 s | 1460 s |
| synt | synt_n10_d90_s3 | - | 1322 s | 924 s | 813 s | 645 s | 532 s |

## Instancias que ninguna variante resuelve: cota inferior al limite de tiempo
| familia | instancia | af2_k0 | raa_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|---|---|
| benchmarks | 3pk-borne | -73161.9 | -73481.8 | -73422 | -70889.8 | -71161.7 | -70645.2 |
| benchmarks | ex6_2_6 | -1.55452e-05 | -1.55452e-05 | -1.55452e-05 | -1.55451e-05 | -1.55451e-05 | -1.55451e-05 |
| benchmarks | mistake | -1.00155 | -1.00155 | -1.00118 | -1.00118 | -1.00118 | -1.00117 |
| benchmarks | s365mod | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 |
| synq | synq_n08_d50_pos_normal_s2 | -7.79169 | -6.51101 | -6.08315 | -5.65014 | -5.32613 | -5.13553 |
| synq | synq_n08_d50_pos_normal_s3 | -12.2265 | -11.8758 | -11.2005 | -10.2317 | -9.28325 | -8.11116 |
| synq | synq_n10_d20_pos_normal_s1 | -14.5596 | -14.2533 | -13.724 | -12.7233 | -11.8725 | -10.3879 |
| synq | synq_n10_d20_pos_normal_s2 | -8.59817 | -7.3257 | -6.51744 | -6.68127 | -6.22449 | -4.97182 |
| synq | synq_n10_d20_pos_normal_s3 | -27.2844 | -25.0578 | -27.0059 | -25.8938 | -24.4615 | -22.9236 |
| synq | synq_n10_d20_posneg_normal_s1 | -31.1027 | -27.5909 | -27.3084 | -27.2686 | -26.0629 | -25.1785 |
| synq | synq_n10_d20_posneg_normal_s3 | -24.536 | -25.9714 | -25.4098 | -23.8262 | -22.3496 | -19.7443 |
| synq | synq_n10_d50_pos_normal_s1 | -29.8788 | -30.3399 | -29.5915 | -28.3071 | -27.3597 | -25.4601 |
| synq | synq_n10_d50_pos_normal_s2 | -63.7793 | -51.386 | -49.3621 | -46.4818 | -45.3058 | -41.7977 |
| synq | synq_n10_d50_pos_normal_s3 | -18.284 | -18.3323 | -17.7485 | -16.6338 | -15.1458 | -13.8376 |
| synq | synq_n10_d50_posneg_normal_s2 | -26.0228 | -22.4124 | -21.546 | -24.4866 | -25.9216 | -24.2435 |
| synq | synq_n10_d90_pos_normal_s1 | -29.1441 | -22.7406 | -21.6301 | -19.9956 | -18.4141 | -16.8277 |
| synq | synq_n10_d90_pos_normal_s2 | -43.7178 | -36.0835 | -33.2997 | -31.6771 | -29.722 | -26.2976 |
| synq | synq_n10_d90_pos_normal_s3 | -59.9085 | -47.9998 | -44.7573 | -41.9978 | -40.4312 | -38.4839 |
| synq | synq_n10_d90_posneg_normal_s1 | -48.6001 | -41.0366 | -39.3812 | -37.6307 | -35.9614 | -32.6755 |
| synq | synq_n10_d90_posneg_normal_s2 | -28.0762 | -25.3387 | -24.7968 | -23.6342 | -22.2127 | -18.6061 |
| synt | synt_n10_d50_s3 | -9.11949 | -9.05481 | -8.96836 | -9.08859 | -9.00866 | -9.01784 |

## Consistencia de optimos
instancias revisadas (resueltas por al menos dos variantes): 114; inconsistencias: 0

## Estados distintos de SUCCESS y TIME_OUT
- benchmarks: SUCCESS (exit 0): 36
- benchmarks: TIME_OUT (exit 0): 24
- synl: SUCCESS (exit 0): 144
- synq: SUCCESS (exit 0): 362
- synq: TIME_OUT (exit 0): 106
- synt: SUCCESS (exit 0): 136
- synt: TIME_OUT (exit 0): 8
