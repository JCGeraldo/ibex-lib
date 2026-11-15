#!/usr/bin/env python3
"""Comparacion binario 0014 (umbrales absolutos) contra 0015 (relativos): analisis.py <carpeta>"""
import csv, os, sys, math, re
base = sys.argv[1] if len(sys.argv) > 1 else "."
out = []
def P(x=""): out.append(x); print(x)
gm = lambda v: math.exp(sum(map(math.log, v)) / len(v)) if v else float("nan")
ok = lambda r: r["estado"] == "SUCCESS"
def load(side, fam):
    return {(r["instancia"].split("/")[-1], r["variante"]): r for r in csv.DictReader(open(os.path.join(base, side, fam, "runs.csv")))}
st = lambda r, k: int(re.search(rf"\b{k}=(\d+)", r["raak_stats"]).group(1))
FAMS = [("ex62", "ex6_2"), ("synq8", "synq n=8")]; KV = ["art_raa_k4", "art_raa_k6"]
D = {f: (load("b0014", f), load("b0015", f)) for f, _ in FAMS}

P("## Celdas del binario 0015 frente al 0014 (instancias resueltas por ambos)")
P("| familia | variante | resueltas 0014 | resueltas 0015 | por ambos | celdas 0015/0014 | menos | igual | mas | min | max |"); P("|---|---|---|---|---|---|---|---|---|---|---|")
for f, name in FAMS:
    A, B = D[f]; insts = sorted({k[0] for k in B})
    for v in KV:
        both = [i for i in insts if ok(A[(i, v)]) and ok(B[(i, v)])]
        q = [float(B[(i, v)]["celdas"]) / float(A[(i, v)]["celdas"]) for i in both]
        P(f"| {name} | {v[8:]} | {sum(ok(A[(i, v)]) for i in insts)} | {sum(ok(B[(i, v)]) for i in insts)} | {len(both)} | {gm(q):.3f} | {sum(x < 1 for x in q)} | {sum(x == 1 for x in q)} | {sum(x > 1 for x in q)} | {min(q):.3f} | {max(q):.3f} |")

P("\n## Celdas frente a RAA k=0 (k=0 del binario 0015; resueltas por k=0 y por ambos binarios)")
P("| familia | variante | n | 0014 | 0015 |"); P("|---|---|---|---|---|")
for f, name in FAMS:
    A, B = D[f]; insts = sorted({k[0] for k in B})
    for v in KV:
        s = [i for i in insts if ok(A[(i, v)]) and ok(B[(i, v)]) and ok(B[(i, "art_raa_k0")])]
        z = lambda X: gm([float(X[(i, v)]["celdas"]) / float(B[(i, "art_raa_k0")]["celdas"]) for i in s])
        P(f"| {name} | {v[8:]} | {len(s)} | {z(A):.3f} | {z(B):.3f} |")

P("\n## Productos con bloques (suma sobre todas las corridas de la familia)")
P("| familia | variante | binario | productos | candidatos evaluados | con bloques | con bloques / productos | con bloques / evaluados |"); P("|---|---|---|---|---|---|---|---|")
for f, name in FAMS:
    for v in KV:
        for X, lab in zip(D[f], ["0014", "0015"]):
            rs = [r for (i, vv), r in X.items() if vv == v]
            p = sum(st(r, "productos") for r in rs); e = sum(st(r, "evaluados") for r in rs); c = sum(st(r, "con_bloques") for r in rs)
            P(f"| {name} | {v[8:]} | {lab} | {p} | {e} | {c} | {100 * c / p:.2f} % | {100 * c / e:.2f} % |")

P("\n## Por instancia (celdas; estado distinto de SUCCESS marcado con *)")
P("| familia | instancia | k0 (0015) | k4 0014 | k4 0015 | k6 0014 | k6 0015 | con bloques / evaluados k6: 0014 | 0015 |"); P("|---|---|---|---|---|---|---|---|---|")
for f, name in FAMS:
    A, B = D[f]
    for i in sorted({k[0] for k in B}):
        c = lambda r: r["celdas"] + ("" if ok(r) else "*")
        fr = lambda r: f"{100 * st(r, 'con_bloques') / max(st(r, 'evaluados'), 1):.1f} %"
        P(f"| {name} | {i} | {c(B[(i, 'art_raa_k0')])} | {c(A[(i, KV[0])])} | {c(B[(i, KV[0])])} | {c(A[(i, KV[1])])} | {c(B[(i, KV[1])])} | {fr(A[(i, KV[1])])} | {fr(B[(i, KV[1])])} |")

P("\n## Consistencia de optimos entre binarios y variantes")
bad = n = 0
for f, name in FAMS:
    A, B = D[f]
    for i in sorted({k[0] for k in B}):
        s = [r for X in (A, B) for (ii, v), r in X.items() if ii == i and ok(r)]
        if len(s) < 2: continue
        n += 1; lo = max(float(r["f_lb"]) for r in s); hi = min(float(r["f_ub"]) for r in s)
        tol = 1e-6 * max(1.0, abs(lo), abs(hi))
        if lo > hi + 2 * tol: bad += 1; P(f"- NO SOLAPAN {name}/{i}")
        for X in (A, B):
            for (ii, v), r in X.items():
                if ii == i and not ok(r) and float(r["f_lb"]) > hi + 2 * tol: bad += 1; P(f"- COTA INFERIOR SOBRE EL OPTIMO {name}/{i} {v}")
P(f"instancias revisadas: {n}; inconsistencias: {bad}")
open(os.path.join(base, "resumen.md"), "w").write("\n".join(out) + "\n")
