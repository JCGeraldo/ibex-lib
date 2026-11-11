#!/usr/bin/env python3
"""Repeticiones con semilla: semillas_analisis.py <carpeta con s<semilla>/runs.csv> [--out carpeta]
Cocientes (media geometrica) por semilla sobre las instancias resueltas por ambas variantes, y
dispersion de celdas entre semillas para una misma instancia y variante."""
import csv, sys, math, glob, os, collections, argparse, statistics
ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--out"); a = ap.parse_args()
D = {}  # seed -> inst -> var -> row
for f in sorted(glob.glob(os.path.join(a.dir, "s*/runs.csv"))):
    s = os.path.basename(os.path.dirname(f))[1:]
    D[s] = collections.defaultdict(dict)
    for r in csv.DictReader(open(f)): D[s][r["instancia"].split("/")[-1]][r["variante"]] = r
seeds = sorted(D, key=int); out = []
def P(x=""): out.append(x); print(x)
gm = lambda v: math.exp(sum(map(math.log, v)) / len(v)) if v else float("nan")
ok = lambda r: r["estado"] == "SUCCESS"
V = ["art_raa_k0", "art_raa_k4", "art_raa_k6"]
P("## Resueltas por semilla"); P("| semilla | " + " | ".join(V) + " |"); P("|---|---|---|---|")
for s in seeds: P(f"| {s} | " + " | ".join(str(sum(ok(d[v]) for d in D[s].values())) for v in V) + " |")
P("\n## Cocientes por semilla (instancias resueltas por ambas)")
P("| par | medida | " + " | ".join(f"semilla {s}" for s in seeds) + " | min | max |"); P("|---|---|" + "---|" * (len(seeds) + 2))
for x, y in [("art_raa_k4", "art_raa_k0"), ("art_raa_k6", "art_raa_k0"), ("art_raa_k6", "art_raa_k4")]:
    for m in ["celdas", "cpu_s"]:
        vals = []; ns = []
        for s in seeds:
            b = [d for d in D[s].values() if ok(d[x]) and ok(d[y])]
            vals.append(gm([float(d[x][m]) / float(d[y][m]) for d in b])); ns.append(len(b))
        P(f"| {x[4:]}/{y[4:]} | {m} | " + " | ".join(f"{v:.3f} (n={n})" for v, n in zip(vals, ns)) + f" | {min(vals):.3f} | {max(vals):.3f} |")
P("\n## Mismo conjunto en todas las semillas (resueltas por las dos variantes en las 4 semillas)")
P("| par | n | " + " | ".join(f"celdas s{s}" for s in seeds) + " | " + " | ".join(f"cpu s{s}" for s in seeds) + " |"); P("|---|---|" + "---|" * (2 * len(seeds)))
insts = sorted(D[seeds[0]])
for x, y in [("art_raa_k4", "art_raa_k0"), ("art_raa_k6", "art_raa_k0"), ("art_raa_k6", "art_raa_k4")]:
    c = [i for i in insts if all(ok(D[s][i][x]) and ok(D[s][i][y]) for s in seeds)]
    P(f"| {x[4:]}/{y[4:]} | {len(c)} | " + " | ".join(f"{gm([float(D[s][i][x]['celdas'])/float(D[s][i][y]['celdas']) for i in c]):.3f}" for s in seeds) + " | " + " | ".join(f"{gm([float(D[s][i][x]['cpu_s'])/float(D[s][i][y]['cpu_s']) for i in c]):.3f}" for s in seeds) + " |")
P("\n## Dispersion entre semillas (celdas max/min por instancia, resueltas en las 4 semillas)")
P("| variante | n | mediana max/min | peor max/min | instancias donde gana k6 a k0 en las 4 semillas |"); P("|---|---|---|---|---|")
for v in V:
    c = [i for i in insts if all(ok(D[s][i][v]) for s in seeds)]
    sp = [max(float(D[s][i][v]["celdas"]) for s in seeds) / min(float(D[s][i][v]["celdas"]) for s in seeds) for i in c]
    c2 = [i for i in insts if all(ok(D[s][i]["art_raa_k6"]) and ok(D[s][i]["art_raa_k0"]) for s in seeds)]
    w = sum(all(float(D[s][i]["art_raa_k6"]["celdas"]) < float(D[s][i]["art_raa_k0"]["celdas"]) for s in seeds) for i in c2)
    P(f"| {v[4:]} | {len(c)} | {statistics.median(sp):.3f} | {max(sp):.3f} | {w} de {len(c2)} |")
if a.out: os.makedirs(a.out, exist_ok=True); open(os.path.join(a.out, "resumen.md"), "w").write("\n".join(out) + "\n")
