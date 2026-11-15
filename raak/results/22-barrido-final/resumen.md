## Resueltas por variante
| familia | instancias | af2_k0 | raa_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 | por todas |
|---|---|---|---|---|---|---|---|---|
| benchmarks | 10 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| synq | 78 | 56 | 60 | 61 | 61 | 61 | 63 | 56 |
| synl | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 |
| synt | 24 | 21 | 23 | 23 | 23 | 23 | 23 | 21 |

## Cocientes frente a RAA k=0 (celdas / CPU; instancias resueltas por las seis variantes)
| familia | n | af2_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|---|
| benchmarks | 6 | 1.000 / 0.979 | 0.977 / 0.996 | 0.966 / 0.986 | 0.966 / 0.965 | 0.966 / 0.985 |
| synq | 56 | 1.568 / 1.454 | 0.773 / 0.806 | 0.651 / 0.695 | 0.594 / 0.635 | 0.557 / 0.596 |
| synl | 24 | 1.163 / 1.154 | 0.896 / 0.944 | 0.865 / 0.888 | 0.837 / 0.861 | 0.809 / 0.847 |
| synt | 21 | 1.139 / 1.069 | 0.974 / 0.944 | 0.951 / 0.989 | 0.936 / 0.947 | 0.934 / 0.917 |

## Cocientes frente a RAA k=0 (celdas / CPU; instancias resueltas por las cinco variantes RAA, sin exigir AF2)
| familia | n | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|
| benchmarks | 6 | 0.977 / 0.996 | 0.966 / 0.986 | 0.966 / 0.965 | 0.966 / 0.985 |
| synq | 60 | 0.770 / 0.804 | 0.646 / 0.690 | 0.583 / 0.623 | 0.540 / 0.577 |
| synl | 24 | 0.896 / 0.944 | 0.865 / 0.888 | 0.837 / 0.861 | 0.809 / 0.847 |
| synt | 23 | 0.970 / 0.946 | 0.937 / 0.977 | 0.932 / 0.930 | 0.898 / 0.874 |

## Lo mismo, solo instancias con CPU de RAA k=0 >= 1 s
| familia | n | af2_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|---|
| benchmarks | 5 | 1.000 / 0.989 | 0.972 / 0.998 | 0.959 / 0.985 | 0.959 / 0.986 | 0.959 / 1.001 |
| synq | 24 | 1.935 / 1.780 | 0.734 / 0.783 | 0.579 / 0.627 | 0.491 / 0.530 | 0.433 / 0.467 |
| synl | 10 | 1.473 / 1.348 | 0.845 / 0.892 | 0.787 / 0.840 | 0.729 / 0.781 | 0.670 / 0.724 |
| synt | 9 | 1.265 / 1.192 | 0.941 / 0.967 | 0.904 / 0.942 | 0.877 / 0.920 | 0.876 / 0.915 |

## Pares (celdas / CPU, resueltas por ambas) y conteo de instancias con menos, igual o mas celdas
| familia | par | n | celdas | CPU | menos | igual | mas |
|---|---|---|---|---|---|---|---|
| benchmarks | raa_k0/af2_k0 | 6 | 1.000 | 1.021 | 0 | 6 | 0 |
| benchmarks | raa_k4/raa_k3 | 6 | 1.000 | 0.978 | 0 | 6 | 0 |
| benchmarks | raa_k6/raa_k4 | 6 | 1.000 | 1.021 | 0 | 6 | 0 |
| benchmarks | raa_k6/raa_k0 | 6 | 0.966 | 0.985 | 5 | 1 | 0 |
| benchmarks | raa_k6/af2_k0 | 6 | 0.966 | 1.006 | 5 | 1 | 0 |
| synq | raa_k0/af2_k0 | 56 | 0.638 | 0.688 | 50 | 6 | 0 |
| synq | raa_k4/raa_k3 | 61 | 0.902 | 0.903 | 38 | 21 | 2 |
| synq | raa_k6/raa_k4 | 61 | 0.926 | 0.926 | 26 | 35 | 0 |
| synq | raa_k6/raa_k0 | 60 | 0.540 | 0.577 | 56 | 3 | 1 |
| synq | raa_k6/af2_k0 | 56 | 0.355 | 0.410 | 53 | 3 | 0 |
| synl | raa_k0/af2_k0 | 24 | 0.860 | 0.867 | 15 | 6 | 3 |
| synl | raa_k4/raa_k3 | 24 | 0.968 | 0.969 | 7 | 15 | 2 |
| synl | raa_k6/raa_k4 | 24 | 0.966 | 0.984 | 5 | 16 | 3 |
| synl | raa_k6/raa_k0 | 24 | 0.809 | 0.847 | 15 | 9 | 0 |
| synl | raa_k6/af2_k0 | 24 | 0.696 | 0.734 | 16 | 5 | 3 |
| synt | raa_k0/af2_k0 | 21 | 0.878 | 0.935 | 11 | 8 | 2 |
| synt | raa_k4/raa_k3 | 23 | 0.994 | 0.952 | 8 | 13 | 2 |
| synt | raa_k6/raa_k4 | 23 | 0.964 | 0.940 | 5 | 16 | 2 |
| synt | raa_k6/raa_k0 | 23 | 0.898 | 0.874 | 10 | 9 | 4 |
| synt | raa_k6/af2_k0 | 21 | 0.820 | 0.857 | 11 | 8 | 2 |

## Casos con mas celdas que la variante de referencia
| familia | instancia | par | celdas | referencia | cociente |
|---|---|---|---|---|---|
| synq | synq_n05_d20_posneg_normal_s2 | raa_k4/raa_k3 | 24 | 22 | 1.091 |
| synq | synq_n05_d50_posneg_normal_s2 | raa_k4/raa_k3 | 810 | 806 | 1.005 |
| synq | synq_n03_d50_posneg_normal_s1 | raa_k6/raa_k0 | 22 | 18 | 1.222 |
| synl | synl_n05_d90_s2 | raa_k4/raa_k3 | 44 | 42 | 1.048 |
| synl | synl_n10_d90_s2 | raa_k4/raa_k3 | 66058 | 65552 | 1.008 |
| synl | synl_n05_d90_s3 | raa_k6/raa_k4 | 86 | 84 | 1.024 |
| synl | synl_n08_d90_s2 | raa_k6/raa_k4 | 1312 | 1216 | 1.079 |
| synl | synl_n10_d50_s3 | raa_k6/raa_k4 | 186 | 182 | 1.022 |
| synl | synl_n05_d50_s1 | raa_k0/af2_k0 | 14 | 12 | 1.167 |
| synl | synl_n08_d50_s1 | raa_k0/af2_k0 | 122 | 54 | 2.259 |
| synl | synl_n08_d50_s2 | raa_k0/af2_k0 | 14 | 12 | 1.167 |
| synt | synt_n08_d90_s3 | raa_k4/raa_k3 | 34282 | 27540 | 1.245 |
| synt | synt_n10_d90_s3 | raa_k4/raa_k3 | 197680 | 159226 | 1.242 |
| synt | synt_n08_d90_s1 | raa_k6/raa_k4 | 9720 | 9104 | 1.068 |
| synt | synt_n08_d90_s3 | raa_k6/raa_k4 | 36080 | 34282 | 1.052 |
| synt | synt_n05_d50_s1 | raa_k6/raa_k0 | 186 | 164 | 1.134 |
| synt | synt_n08_d50_s1 | raa_k6/raa_k0 | 1740 | 1542 | 1.128 |
| synt | synt_n08_d50_s2 | raa_k6/raa_k0 | 1144 | 1122 | 1.020 |
| synt | synt_n10_d50_s1 | raa_k6/raa_k0 | 2620 | 2616 | 1.002 |
| synt | synt_n08_d50_s3 | raa_k0/af2_k0 | 10490 | 10134 | 1.035 |
| synt | synt_n10_d50_s1 | raa_k0/af2_k0 | 2616 | 2406 | 1.087 |

## Por numero de variables (cocientes de celdas / CPU frente a RAA k=0, resueltas por las seis)
| familia | n vars | instancias | resueltas por todas | raa_k2 | raa_k3 | raa_k4 | raa_k6 | k6/k4 |
|---|---|---|---|---|---|---|---|---|
| synq | 3 | 18 | 18 | 0.851 / 0.866 | 0.811 / 0.833 | 0.811 / 0.832 | 0.811 / 0.855 | 1.000 / 1.028 |
| synq | 5 | 24 | 24 | 0.737 / 0.765 | 0.594 / 0.647 | 0.543 / 0.590 | 0.527 / 0.563 | 0.971 / 0.953 |
| synq | 8 | 18 | 13 | 0.739 / 0.797 | 0.575 / 0.620 | 0.463 / 0.507 | 0.381 / 0.417 | 0.823 / 0.823 |
| synq | 10 | 18 | 1 | 0.766 / 0.880 | 0.602 / 0.642 | 0.491 / 0.524 | 0.339 / 0.365 | 0.692 / 0.697 |
| synl | 3 | 6 | 6 | 0.935 / 1.040 | 0.935 / 0.973 | 0.935 / 0.950 | 0.935 / 0.997 | 1.000 / 1.050 |
| synl | 5 | 6 | 6 | 0.918 / 0.913 | 0.895 / 0.878 | 0.893 / 0.887 | 0.897 / 0.890 | 1.004 / 1.003 |
| synl | 8 | 6 | 6 | 0.872 / 0.920 | 0.838 / 0.842 | 0.773 / 0.801 | 0.726 / 0.755 | 0.938 / 0.942 |
| synl | 10 | 6 | 6 | 0.863 / 0.910 | 0.799 / 0.866 | 0.761 / 0.812 | 0.705 / 0.768 | 0.926 / 0.946 |
| synt | 3 | 6 | 6 | 1.000 / 0.864 | 1.000 / 1.057 | 1.000 / 0.944 | 1.000 / 0.897 | 1.000 / 0.950 |
| synt | 5 | 6 | 6 | 1.001 / 0.993 | 0.978 / 0.993 | 0.965 / 0.994 | 0.960 / 0.941 | 0.995 / 0.947 |
| synt | 8 | 6 | 6 | 0.936 / 0.960 | 0.890 / 0.924 | 0.875 / 0.925 | 0.892 / 0.934 | 1.019 / 1.010 |
| synt | 10 | 6 | 3 | 0.950 / 0.983 | 0.932 / 0.980 | 0.880 / 0.910 | 0.844 / 0.877 | 0.959 / 0.963 |

## Resueltas solo por algunas variantes
| familia | instancia | af2_k0 | raa_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|---|---|
| synq | synq_n08_d20_pos_normal_s3 | - | - | - | - | - | 1597 s |
| synq | synq_n08_d90_pos_normal_s2 | - | 1272 s | 978 s | 733 s | 541 s | 386 s |
| synq | synq_n08_d90_posneg_normal_s3 | - | 796 s | 572 s | 464 s | 333 s | 290 s |
| synq | synq_n10_d20_posneg_normal_s2 | - | - | 1643 s | 1422 s | 1315 s | 1179 s |
| synq | synq_n10_d50_posneg_normal_s1 | - | 1605 s | 1272 s | 1101 s | 929 s | 740 s |
| synq | synq_n10_d50_posneg_normal_s3 | - | 1143 s | 962 s | 758 s | 579 s | 406 s |
| synq | synq_n10_d90_posneg_normal_s2 | - | - | - | - | - | 1722 s |
| synt | synt_n10_d90_s2 | - | 1489 s | 1363 s | 1223 s | 1234 s | 1180 s |
| synt | synt_n10_d90_s3 | - | 1267 s | 1299 s | 1147 s | 890 s | 444 s |

## Instancias que ninguna variante resuelve: cota inferior al limite de tiempo
| familia | instancia | af2_k0 | raa_k0 | raa_k2 | raa_k3 | raa_k4 | raa_k6 |
|---|---|---|---|---|---|---|---|
| benchmarks | 3pk-borne | -74697.6 | -75102.6 | -74915.5 | -72126.3 | -72495.1 | -71824.6 |
| benchmarks | ex6_2_6 | -1.55452e-05 | -1.55452e-05 | -1.55452e-05 | -1.55452e-05 | -1.55452e-05 | -1.55452e-05 |
| benchmarks | mistake | -1.00153 | -1.00154 | -1.00118 | -1.00118 | -1.00116 | -1.00118 |
| benchmarks | s365mod | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 |
| synq | synq_n08_d50_pos_normal_s2 | -7.89409 | -6.63821 | -6.17641 | -5.73362 | -5.40735 | -5.20148 |
| synq | synq_n08_d50_pos_normal_s3 | -12.232 | -12.0529 | -11.4016 | -10.3954 | -9.41075 | -8.21953 |
| synq | synq_n10_d20_pos_normal_s1 | -14.5596 | -14.5303 | -13.8569 | -12.8489 | -11.9935 | -10.5206 |
| synq | synq_n10_d20_pos_normal_s2 | -8.66132 | -7.3257 | -6.5291 | -6.66312 | -6.15892 | -4.90698 |
| synq | synq_n10_d20_pos_normal_s3 | -26.7569 | -24.7974 | -27.0059 | -25.8653 | -24.3587 | -22.7163 |
| synq | synq_n10_d20_posneg_normal_s1 | -30.8119 | -27.7132 | -27.5826 | -27.3431 | -26.1321 | -25.2726 |
| synq | synq_n10_d20_posneg_normal_s3 | -24.536 | -25.8561 | -25.1328 | -23.5 | -22.0883 | -19.6455 |
| synq | synq_n10_d50_pos_normal_s1 | -29.8788 | -30.0099 | -29.4303 | -28.117 | -27.1018 | -25.2242 |
| synq | synq_n10_d50_pos_normal_s2 | -63.4505 | -50.8162 | -49.111 | -46.3659 | -45.0932 | -41.5779 |
| synq | synq_n10_d50_pos_normal_s3 | -18.0383 | -18.2188 | -17.5924 | -16.4802 | -15.0294 | -13.6228 |
| synq | synq_n10_d50_posneg_normal_s2 | -26.0228 | -22.4124 | -21.546 | -24.0888 | -25.5885 | -24.0995 |
| synq | synq_n10_d90_pos_normal_s1 | -28.4635 | -22.2449 | -21.1497 | -19.3446 | -17.9643 | -16.3415 |
| synq | synq_n10_d90_pos_normal_s2 | -43.2296 | -35.7608 | -32.9987 | -31.2055 | -29.2417 | -25.8117 |
| synq | synq_n10_d90_pos_normal_s3 | -59.1217 | -47.6928 | -44.5316 | -41.5948 | -40.0608 | -38.0955 |
| synq | synq_n10_d90_posneg_normal_s1 | -48.1157 | -40.7676 | -39.0544 | -37.2301 | -35.6167 | -32.2503 |
| synt | synt_n10_d50_s3 | -8.8841 | -8.87635 | -8.66194 | -8.86834 | -8.83497 | -8.83451 |

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
