#!/usr/bin/env python3
"""Comprueba que las salidas de varias corridas de ibexsolve-raak (--boxes) son coherentes:
cada caja solucion (validada) de una corrida debe intersectar alguna caja de cada otra corrida
completa (un solver completo no puede dejar una solucion fuera de su cobertura).
Con --tol=T la interseccion se relaja a distancia <= T por componente: el Solver de IBEX, al llegar a una
celda de ancho < eps_min, la reemplaza por la solucion que certifica Newton desde su centro, de modo que
la salida solo es completa con resolucion eps_min (usar T = eps_min).
Uso: cajas_cubren.py [--tol=T] nombre=archivo ..."""
import sys
def load(f):
    B = []
    for l in open(f):
        p = l.split(); v = list(map(float, p[1:])); B.append((p[0], v[0::2], v[1::2]))
    return B
TOL = 0.0
args = []
for a in sys.argv[1:]:
    if a.startswith("--tol="): TOL = float(a[6:])
    else: args.append(a)
R = {a.split("=")[0]: load(a.split("=")[1]) for a in args}
inter = lambda a, b: all(al <= bu + TOL and bl <= au + TOL for al, au, bl, bu in zip(a[1], a[2], b[1], b[2]))
fail = 0
print("| soluciones de | cajas | " + " | ".join(f"sin cubrir por {n}" for n in R) + " |"); print("|---|---|" + "---|" * len(R))
for a, A in R.items():
    S = [x for x in A if x[0] == "S"]; row = []
    for b, Bx in R.items():
        if a == b: row.append("-"); continue
        miss = sum(1 for s in S if not any(inter(s, y) for y in Bx)); fail += miss; row.append(str(miss))
    print(f"| {a} | {len(S)} sol + {len(A)-len(S)} otras | " + " | ".join(row) + " |")
# soluciones distintas: componentes de cajas solucion que se intersectan
for a, A in R.items():
    S = [x for x in A if x[0] == "S"]; par = list(range(len(S)))
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i in range(len(S)):
        for j in range(i):
            if inter(S[i], S[j]): par[find(i)] = find(j)
    print(f"{a}: {len(S)} cajas solucion, {len({find(i) for i in range(len(S))})} grupos disjuntos, ancho max {max(max(u-l for l,u in zip(s[1],s[2])) for s in S):.2e}")
print(f"tolerancia {TOL:g}; cajas solucion sin cubrir en total:", fail)
