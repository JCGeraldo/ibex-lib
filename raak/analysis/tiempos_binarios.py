#!/usr/bin/env python3
"""[raak local] Costo por evaluacion afin de dos binarios alternados: tiempos_binarios.py <carpeta> [--a 0014] [--b 0015]
<carpeta> contiene range_<bin>_r<rep>.csv(.gz) de tests/range_eval.cpp (columna `us`), una serie por binario y repeticion.
Por (instancia, funcion, caja, variante) se toma el mejor tiempo de las repeticiones de cada binario. Informa el cociente
b/a por variante (media geometrica) y, dentro de cada binario, el costo de cada variante RAA-k frente a RAA k=0."""
import sys, os, glob, argparse
import numpy as np, pandas as pd
ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--a", default="0014"); ap.add_argument("--b", default="0015")
A = ap.parse_args(); fr = []
for f in sorted(glob.glob(os.path.join(A.dir, "range_*_r*.csv*"))):
    b, r = os.path.basename(f).split(".csv")[0][6:].split("_r"); d = pd.read_csv(f); d["bin"] = b; d["rep"] = int(r); fr.append(d)
D = pd.concat(fr); key = ["instance", "func", "box_id", "scale", "variant"]
M = D.groupby(key + ["bin", "n"]).us.min().unstack("bin").reset_index()
gm = lambda v: float(np.exp(np.log(v).mean()))
print(f"filas {len(D)}; pares (funcion, caja) por variante: {len(M) // M.variant.nunique()}; repeticiones por binario: {D.rep.nunique()}")
print(f"\n## us({A.b}) / us({A.a}) por variante (media geometrica, mejor de las repeticiones)")
print("| variante | cociente | mediana us " + A.a + " | mediana us " + A.b + " |"); print("|---|---|---|---|")
for v, g in M.groupby("variant"): print(f"| {v} | {gm(g[A.b] / g[A.a]):.3f} | {g[A.a].median():.1f} | {g[A.b].median():.1f} |")
for b in (A.a, A.b):
    P = M.pivot_table(index=["instance", "func", "box_id", "scale", "n"], columns="variant", values=b).reset_index()
    cols = sorted(c for c in P.columns if c.startswith("raa_k") and c != "raa_k0")
    print(f"\n## Binario {b}: us(RAA-k) / us(RAA k=0), media geometrica")
    print("| n | " + " | ".join(cols) + " |"); print("|---|" + "---|" * len(cols))
    for n, g in list(P.groupby("n")) + [("todas", P)]: print(f"| {n} | " + " | ".join(f"{gm(g[c] / g['raa_k0']):.3f}" for c in cols) + " |")
