# Brent-8: coherencia de las cajas solucion entre contractores (2026-11-11)

eps_min = 1e-3 (por omision), interseccion estricta:

| soluciones de | cajas | sin cubrir por af2 | sin cubrir por raa | sin cubrir por raa_k6 | sin cubrir por default | sin cubrir por xn |
|---|---|---|---|---|---|---|
| af2 | 186 sol + 0 otras | - | 21 | 21 | 29 | 33 |
| raa | 181 sol + 0 otras | 16 | - | 0 | 26 | 31 |
| raa_k6 | 181 sol + 0 otras | 16 | 0 | - | 26 | 31 |
| default | 146 sol + 18 otras | 15 | 16 | 16 | - | 14 |
| xn | 169 sol + 2 otras | 20 | 22 | 22 | 22 | - |
af2: 186 cajas solucion, 186 grupos disjuntos, ancho max 7.11e-15
raa: 181 cajas solucion, 181 grupos disjuntos, ancho max 7.11e-15
raa_k6: 181 cajas solucion, 181 grupos disjuntos, ancho max 7.11e-15
default: 146 cajas solucion, 146 grupos disjuntos, ancho max 7.11e-15
xn: 169 cajas solucion, 169 grupos disjuntos, ancho max 7.11e-15
tolerancia 0; cajas solucion sin cubrir en total: 397

eps_min = 1e-3, tolerancia = eps_min:

| soluciones de | cajas | sin cubrir por af2 | sin cubrir por raa | sin cubrir por raa_k6 | sin cubrir por default | sin cubrir por xn |
|---|---|---|---|---|---|---|
| af2 | 186 sol + 0 otras | - | 0 | 0 | 0 | 0 |
| raa | 181 sol + 0 otras | 0 | - | 0 | 0 | 0 |
| raa_k6 | 181 sol + 0 otras | 0 | 0 | - | 0 | 0 |
| default | 146 sol + 18 otras | 0 | 0 | 0 | - | 0 |
| xn | 169 sol + 2 otras | 0 | 0 | 0 | 0 | - |
af2: 186 cajas solucion, 159 grupos disjuntos, ancho max 7.11e-15
raa: 181 cajas solucion, 159 grupos disjuntos, ancho max 7.11e-15
raa_k6: 181 cajas solucion, 159 grupos disjuntos, ancho max 7.11e-15
default: 146 cajas solucion, 143 grupos disjuntos, ancho max 7.11e-15
xn: 169 cajas solucion, 158 grupos disjuntos, ancho max 7.11e-15
tolerancia 0.001; cajas solucion sin cubrir en total: 0

eps_min = 1e-9 (-e 1e-9), tolerancia 1e-9: af2 166045 celdas, raa 161345, default 799; 256 soluciones cada una

| soluciones de | cajas | sin cubrir por af2 | sin cubrir por raa | sin cubrir por default |
|---|---|---|---|---|
| af2 | 256 sol + 0 otras | - | 0 | 0 |
| raa | 256 sol + 0 otras | 0 | - | 0 |
| default | 256 sol + 0 otras | 0 | 0 | - |
af2: 256 cajas solucion, 256 grupos disjuntos, ancho max 7.11e-15
raa: 256 cajas solucion, 256 grupos disjuntos, ancho max 7.11e-15
default: 256 cajas solucion, 256 grupos disjuntos, ancho max 7.11e-15
tolerancia 1e-09; cajas solucion sin cubrir en total: 0
