#!/usr/bin/env python3
"""Resumen de un barrido de ibexsolve-raak (runs.csv de wsl_sweep_csp.sh).
Uso: csp_analisis.py <runs.csv> [--out carpeta] [--pares a:b,c:d]
Terminada = SUCCESS | INFEASIBLE | NOT_ALL_VALIDATED. Cocientes: media geometrica de a/b
sobre las instancias terminadas por ambas configuraciones."""
import csv, sys, math, argparse, collections, os
ap = argparse.ArgumentParser(); ap.add_argument("runs"); ap.add_argument("--out"); ap.add_argument("--pares", default="")
a = ap.parse_args()
FIN = {"SUCCESS", "INFEASIBLE", "NOT_ALL_VALIDATED"}
R = collections.defaultdict(dict)
for r in csv.DictReader(open(a.runs)):
    R[r["instancia"]][r["config"]] = r
cfgs = sorted({c for d in R.values() for c in d})
out = []
def P(s=""): out.append(s); print(s)
def num(r, k):
    try: return float(r[k])
    except Exception: return float("nan")
P(f"instancias: {len(R)}  configuraciones: {', '.join(cfgs)}\n")
P("## Estados por configuracion")
sts = sorted({r["estado"] for d in R.values() for r in d.values()})
P("| config | " + " | ".join(sts) + " | terminadas |"); P("|---|" + "---|" * (len(sts) + 1))
for c in cfgs:
    cnt = collections.Counter(d[c]["estado"] for d in R.values() if c in d)
    P(f"| {c} | " + " | ".join(str(cnt.get(s, 0)) for s in sts) + f" | {sum(cnt[s] for s in FIN)} |")
todas = [i for i, d in R.items() if all(c in d and d[c]["estado"] in FIN for c in cfgs)]
P(f"\nterminadas por todas las configuraciones: {len(todas)}")
P("\n## Comparaciones por pares (a / b)")
P("| a | b | ambas terminan | celdas a/b (mg) | cpu a/b (mg) | cpu a/b (mg, >=1 s) | a menos celdas | igual | b menos celdas | solo a termina | solo b termina |"); P("|---|---|---|---|---|---|---|---|---|---|---|")
pares = [p.split(":") for p in a.pares.split(",") if p]
def gm(v): return math.exp(sum(math.log(x) for x in v) / len(v)) if v else float("nan")
for x, y in pares:
    both = [i for i, d in R.items() if x in d and y in d and d[x]["estado"] in FIN and d[y]["estado"] in FIN]
    cr = [num(R[i][x], "celdas") / num(R[i][y], "celdas") for i in both if num(R[i][y], "celdas") > 0]
    tr = [max(num(R[i][x], "cpu_s"), 1e-3) / max(num(R[i][y], "cpu_s"), 1e-3) for i in both]
    tr1 = [num(R[i][x], "cpu_s") / num(R[i][y], "cpu_s") for i in both if max(num(R[i][x], "cpu_s"), num(R[i][y], "cpu_s")) >= 1]
    lt = sum(1 for v in cr if v < 1); eq = sum(1 for v in cr if v == 1); gt = sum(1 for v in cr if v > 1)
    sx = [i for i, d in R.items() if x in d and y in d and d[x]["estado"] in FIN and d[y]["estado"] not in FIN]
    sy = [i for i, d in R.items() if x in d and y in d and d[y]["estado"] in FIN and d[x]["estado"] not in FIN]
    P(f"| {x} | {y} | {len(both)} | {gm(cr):.3f} | {gm(tr):.3f} | {gm(tr1):.3f} (n={len(tr1)}) | {lt} | {eq} | {gt} | {len(sx)} | {len(sy)} |")
    if sx: P(f"<!-- solo {x}: {' '.join(sorted(sx))} -->")
    if sy: P(f"<!-- solo {y}: {' '.join(sorted(sy))} -->")
P("\n## Coherencia de soluciones entre configuraciones con SUCCESS")
bad = 0
for i, d in sorted(R.items()):
    s = {c: d[c]["soluciones"] for c in cfgs if c in d and d[c]["estado"] == "SUCCESS"}
    inf = [c for c in cfgs if c in d and d[c]["estado"] == "INFEASIBLE"]
    if len(set(s.values())) > 1 or (s and inf):
        bad += 1; P(f"- {i}: soluciones {s} infactible {inf}")
P(f"instancias con discrepancia: {bad}")
P("\n## Instancias con material k-nomial (bloques > 0 en alguna configuracion)")
P("| instancia | config | estado | celdas | cpu_s | productos | con_bloques |"); P("|---|---|---|---|---|---|---|")
for i, d in sorted(R.items()):
    if any(num(r, "bloques") > 0 for r in d.values()):
        for c in cfgs:
            if c in d: r = d[c]; P(f"| {i} | {c} | {r['estado']} | {r['celdas']} | {num(r,'cpu_s'):.2f} | {r['productos']} | {r['con_bloques']} |")
if a.out:
    os.makedirs(a.out, exist_ok=True); open(os.path.join(a.out, "resumen.md"), "w").write("\n".join(out) + "\n")
