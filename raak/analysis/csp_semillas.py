#!/usr/bin/env python3
"""Repeticiones con semilla del solver: csp_semillas.py <carpeta con s<semilla>/runs.csv> [--out carpeta]
Cocientes de celdas y CPU por semilla y agregados (media geometrica por instancia sobre las semillas,
luego media geometrica de los cocientes), sobre las instancias que terminan con todas las configuraciones y semillas."""
import csv, math, glob, os, sys, statistics, argparse
ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--out"); a = ap.parse_args()
D = {}; seeds = []
for f in sorted(glob.glob(os.path.join(a.dir, "s*/runs.csv")), key=lambda p: int(os.path.basename(os.path.dirname(p))[1:])):
    s = int(os.path.basename(os.path.dirname(f))[1:]); seeds.append(s)
    for r in csv.DictReader(open(f)): D[(r["instancia"], r["config"], s)] = r
FIN = {"SUCCESS", "INFEASIBLE", "NOT_ALL_VALIDATED"}
cf = sorted({k[1] for k in D}, key=lambda c: (len(c), c)); insts = sorted({k[0] for k in D})
gm = lambda v: math.exp(sum(map(math.log, v)) / len(v))
out = []
def P(x=""): out.append(x); print(x)
ok = [i for i in insts if all(D[(i, c, s)]["estado"] in FIN for c in cf for s in seeds)]
P(f"semillas: {seeds}; instancias: {len(insts)}; terminan con todas las configuraciones y semillas: {len(ok)}; fuera: {', '.join(i for i in insts if i not in ok)}\n")
cel = lambda i, c, s: float(D[(i, c, s)]["celdas"]); cpu = lambda i, c, s: max(float(D[(i, c, s)]["cpu_s"]), 1e-3)
P("| a / b | medida | " + " | ".join(f"semilla {s}" for s in seeds) + " | 4 semillas |"); P("|---|---|" + "---|" * (len(seeds) + 1))
base = cf[0]
pares = [(c, base) for c in cf[1:]] + [(cf[i + 1], cf[i]) for i in range(1, len(cf) - 1)]
for x, y in pares:
    for nm, fn in (("celdas", cel), ("cpu", cpu)):
        per = [gm([fn(i, x, s) / fn(i, y, s) for i in ok]) for s in seeds]
        agg = gm([gm([fn(i, x, s) for s in seeds]) / gm([fn(i, y, s) for s in seeds]) for i in ok])
        P(f"| {x} / {y} | {nm} | " + " | ".join(f"{v:.3f}" for v in per) + f" | {agg:.3f} |")
P("\n## Celdas por instancia y semilla")
P("| instancia | " + " | ".join(cf) + " |"); P("|---|" + "---|" * len(cf))
for i in insts:
    P(f"| {i} | " + " | ".join(" / ".join(D[(i, c, s)]["celdas"] if D[(i, c, s)]["estado"] in FIN else "TO" for s in seeds) for c in cf) + " |")
sp = [max(cel(i, c, s) for s in seeds) / min(cel(i, c, s) for s in seeds) for i in ok for c in cf]
P(f"\ndispersion de celdas entre semillas (max/min por instancia y configuracion): mediana {statistics.median(sp):.3f}, maximo {max(sp):.3f}")
if a.out: open(os.path.join(a.out, "resumen.md"), "w").write("\n".join(out) + "\n")
