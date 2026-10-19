# Fase 2.2 — calidad de la linealizacion de sin/cos

Fuente: `trig_lin.csv` (17640 filas = 4 funciones x 735 intervalos x 2 aritmeticas x 3 modos).

*ratio* = anchura de la forma afin / anchura del rango exacto (media geometrica; 1 = optimo; no definido para
sin^2+cos^2, cuyo rango exacto es un punto). *lin_err* = radio de la parte no lineal de la forma (media).
*ext* / *infl* = solo los intervalos que contienen un extremo / un punto de inflexion de la funcion basica.

| funcion | aritmetica | modo | ratio | ratio (ext) | ratio (infl) | lin_err | lin_err (ext) | lin_err (infl) | viol | ns/eval |
|---|---|---|---|---|---|---|---|---|---|---|
| sin | AF2 | legacy | 1.2790 | 1.5453 | 1.5063 | 0.3138 | 0.6150 | 0.5805 | 0 | 2506 |
| sin | AF2 | cheb | 1.0951 | 1.1502 | 1.1213 | 0.2746 | 0.5390 | 0.5047 | 0 | 2197 |
| sin | AF2 | minrange | 1.0000 | 1.0000 | 1.0000 | 0.4220 | 0.7573 | 0.7576 | 0 | 1679 |
| sin | AA | legacy | 1.2790 | 1.5453 | 1.5063 | 0.3138 | 0.6150 | 0.5805 | 0 | 3324 |
| sin | AA | cheb | 1.0951 | 1.1502 | 1.1213 | 0.2746 | 0.5390 | 0.5047 | 0 | 2942 |
| sin | AA | minrange | 1.0000 | 1.0000 | 1.0000 | 0.4220 | 0.7573 | 0.7576 | 0 | 2170 |
| cos | AF2 | legacy | 1.2720 | 1.5132 | 1.5084 | 0.3150 | 0.6006 | 0.5972 | 0 | 2507 |
| cos | AF2 | cheb | 1.0937 | 1.1438 | 1.1222 | 0.2766 | 0.5282 | 0.5207 | 0 | 2270 |
| cos | AF2 | minrange | 1.0000 | 1.0000 | 1.0000 | 0.4205 | 0.7372 | 0.7742 | 0 | 1701 |
| cos | AA | legacy | 1.2720 | 1.5132 | 1.5084 | 0.3150 | 0.6006 | 0.5972 | 0 | 3365 |
| cos | AA | cheb | 1.0937 | 1.1438 | 1.1222 | 0.2766 | 0.5282 | 0.5207 | 0 | 3296 |
| cos | AA | minrange | 1.0000 | 1.0000 | 1.0000 | 0.4205 | 0.7372 | 0.7742 | 0 | 2243 |
| sin*cos | AF2 | legacy | 2.1259 | 3.8187 | 3.7034 | 1.0118 | 1.9664 | 1.9133 | 0 | 4940 |
| sin*cos | AF2 | cheb | 1.5982 | 2.1916 | 2.1573 | 0.4871 | 0.9121 | 0.8892 | 0 | 4393 |
| sin*cos | AF2 | minrange | 1.5836 | 1.8775 | 1.8545 | 0.4899 | 0.8572 | 0.8382 | 0 | 3122 |
| sin*cos | AA | legacy | 2.3071 | 4.2068 | 4.0682 | 1.1253 | 2.1773 | 2.1179 | 0 | 9705 |
| sin*cos | AA | cheb | 1.7090 | 2.3438 | 2.3026 | 0.5344 | 0.9907 | 0.9656 | 0 | 9304 |
| sin*cos | AA | minrange | 1.5979 | 1.8775 | 1.8545 | 0.4904 | 0.8572 | 0.8382 | 0 | 6649 |
| sin2+cos2 | AF2 | legacy | — | — | — | 2.1175 | 4.0826 | 3.9769 | 0 | 5022 |
| sin2+cos2 | AF2 | cheb | — | — | — | 1.0135 | 1.8682 | 1.8254 | 0 | 4505 |
| sin2+cos2 | AF2 | minrange | — | — | — | 0.9786 | 1.7006 | 1.6638 | 0 | 3303 |
| sin2+cos2 | AA | legacy | — | — | — | 1.3918 | 2.6403 | 2.5750 | 0 | 9897 |
| sin2+cos2 | AA | cheb | — | — | — | 0.6707 | 1.1972 | 1.1725 | 0 | 9666 |
| sin2+cos2 | AA | minrange | — | — | — | 0.6055 | 1.0019 | 0.9819 | 0 | 7210 |

## Comparacion por intervalo del error de linealizacion (misma funcion, aritmetica e intervalo)

| funcion | aritmetica | comparacion | menor | igual (±1e-12) | mayor |
|---|---|---|---|---|---|
| sin | AF2 | cheb vs legacy | 705 | 30 | 0 |
| sin | AF2 | minrange vs legacy | 102 | 30 | 603 |
| sin | AA | cheb vs legacy | 705 | 30 | 0 |
| sin | AA | minrange vs legacy | 102 | 30 | 603 |
| cos | AF2 | cheb vs legacy | 690 | 45 | 0 |
| cos | AF2 | minrange vs legacy | 100 | 45 | 590 |
| cos | AA | cheb vs legacy | 690 | 45 | 0 |
| cos | AA | minrange vs legacy | 100 | 45 | 590 |
| sin*cos | AF2 | cheb vs legacy | 735 | 0 | 0 |
| sin*cos | AF2 | minrange vs legacy | 252 | 0 | 483 |
| sin*cos | AA | cheb vs legacy | 735 | 0 | 0 |
| sin*cos | AA | minrange vs legacy | 288 | 0 | 447 |
| sin2+cos2 | AF2 | cheb vs legacy | 735 | 0 | 0 |
| sin2+cos2 | AF2 | minrange vs legacy | 299 | 0 | 436 |
| sin2+cos2 | AA | cheb vs legacy | 735 | 0 | 0 |
| sin2+cos2 | AA | minrange vs legacy | 347 | 0 | 388 |
