#!/usr/bin/env python3
"""[raak local] Barrido final (wsl_barrido_final.sh): barrido_final_analisis.py <carpeta> [--out carpeta]
<carpeta> contiene reales/, sinteticas/, sinteticas-log/, sinteticas-fun/ con su runs.csv.
Por familia: resueltas por variante, cocientes (media geometrica de celdas y CPU) sobre las instancias
resueltas por todas las variantes, comparaciones por pares, desglose de synq por n, y una verificacion de
consistencia: los intervalos [f_lb, f_ub] de las variantes que resuelven una instancia deben solaparse."""
import csv, sys, math, os, re, collections, argparse
ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--out"); a = ap.parse_args()
FAMS = [("reales", "benchmarks"), ("sinteticas", "synq"), ("sinteticas-log", "synl"), ("sinteticas-fun", "synt")]
V = ["art_af2_k0", "art_raa_k0", "art_raa_k2", "art_raa_k3", "art_raa_k4", "art_raa_k6"]
KV = V[2:]; BASE = "art_raa_k0"
out = []
def P(x=""): out.append(x); print(x)
gm = lambda v: math.exp(sum(map(math.log, v)) / len(v)) if v else float("nan")
ok = lambda r: r["estado"] == "SUCCESS"
fl = lambda r, m: max(float(r[m]), 1e-3 if m == "cpu_s" else 1.0)
D = {}
for d, name in FAMS:
    f = os.path.join(a.dir, d, "runs.csv")
    if not os.path.exists(f): continue
    D[name] = collections.defaultdict(dict)
    for r in csv.DictReader(open(f)): D[name][r["instancia"].split("/")[-1]][r["variante"]] = r

def ratio(rows, x, y, m): return gm([fl(d[x], m) / fl(d[y], m) for d in rows])

P("## Resueltas por variante")
P("| familia | instancias | " + " | ".join(v[4:] for v in V) + " | por todas |"); P("|---|---|" + "---|" * (len(V) + 1))
ALL = {}
for name, I in D.items():
    ALL[name] = [d for d in I.values() if all(v in d and ok(d[v]) for v in V)]
    P(f"| {name} | {len(I)} | " + " | ".join(str(sum(v in d and ok(d[v]) for d in I.values())) for v in V) + f" | {len(ALL[name])} |")

P("\n## Cocientes frente a RAA k=0 (celdas / CPU; instancias resueltas por las seis variantes)")
P("| familia | n | " + " | ".join(v[4:] for v in ["art_af2_k0"] + KV) + " |"); P("|---|---|" + "---|" * (1 + len(KV)))
for name, rows in ALL.items():
    P(f"| {name} | {len(rows)} | " + " | ".join(f"{ratio(rows, v, BASE, 'celdas'):.3f} / {ratio(rows, v, BASE, 'cpu_s'):.3f}" for v in ["art_af2_k0"] + KV) + " |")

RV = [BASE] + KV
P("\n## Cocientes frente a RAA k=0 (celdas / CPU; instancias resueltas por las cinco variantes RAA, sin exigir AF2)")
P("| familia | n | " + " | ".join(v[4:] for v in KV) + " |"); P("|---|---|" + "---|" * len(KV))
for name, I in D.items():
    rows = [d for d in I.values() if all(v in d and ok(d[v]) for v in RV)]
    P(f"| {name} | {len(rows)} | " + " | ".join(f"{ratio(rows, v, BASE, 'celdas'):.3f} / {ratio(rows, v, BASE, 'cpu_s'):.3f}" for v in KV) + " |")

P("\n## Lo mismo, solo instancias con CPU de RAA k=0 >= 1 s")
P("| familia | n | " + " | ".join(v[4:] for v in ["art_af2_k0"] + KV) + " |"); P("|---|---|" + "---|" * (1 + len(KV)))
for name, rows in ALL.items():
    rr = [d for d in rows if float(d[BASE]["cpu_s"]) >= 1.0]
    P(f"| {name} | {len(rr)} | " + " | ".join(f"{ratio(rr, v, BASE, 'celdas'):.3f} / {ratio(rr, v, BASE, 'cpu_s'):.3f}" for v in ["art_af2_k0"] + KV) + " |")

P("\n## Pares (celdas / CPU, resueltas por ambas) y conteo de instancias con menos, igual o mas celdas")
P("| familia | par | n | celdas | CPU | menos | igual | mas |"); P("|---|---|---|---|---|---|---|---|")
for name, I in D.items():
    for x, y in [("art_raa_k0", "art_af2_k0"), ("art_raa_k4", "art_raa_k3"), ("art_raa_k6", "art_raa_k4"), ("art_raa_k6", "art_raa_k0"), ("art_raa_k6", "art_af2_k0")]:
        b = [d for d in I.values() if x in d and y in d and ok(d[x]) and ok(d[y])]
        lt = sum(float(d[x]["celdas"]) < float(d[y]["celdas"]) for d in b); eq = sum(float(d[x]["celdas"]) == float(d[y]["celdas"]) for d in b)
        P(f"| {name} | {x[4:]}/{y[4:]} | {len(b)} | {ratio(b, x, y, 'celdas'):.3f} | {ratio(b, x, y, 'cpu_s'):.3f} | {lt} | {eq} | {len(b) - lt - eq} |")

P("\n## Casos con mas celdas que la variante de referencia")
P("| familia | instancia | par | celdas | referencia | cociente |"); P("|---|---|---|---|---|---|")
for name, I in D.items():
    for x, y in [("art_raa_k4", "art_raa_k3"), ("art_raa_k6", "art_raa_k4"), ("art_raa_k6", "art_raa_k0"), ("art_raa_k0", "art_af2_k0")]:
        for i in sorted(I):
            d = I[i]
            if x in d and y in d and ok(d[x]) and ok(d[y]) and float(d[x]["celdas"]) > float(d[y]["celdas"]):
                P(f"| {name} | {i} | {x[4:]}/{y[4:]} | {d[x]['celdas']} | {d[y]['celdas']} | {float(d[x]['celdas']) / float(d[y]['celdas']):.3f} |")

P("\n## Por numero de variables (cocientes de celdas / CPU frente a RAA k=0, resueltas por las seis)")
P("| familia | n vars | instancias | resueltas por todas | " + " | ".join(v[4:] for v in KV) + " | k6/k4 |"); P("|---|---|---|---|" + "---|" * (len(KV) + 1))
for name, I in D.items():
    if name == "benchmarks": continue
    byn = collections.defaultdict(list)
    for i, d in I.items(): byn[int(re.search(r"_n(\d+)", i).group(1))].append(d)
    for n in sorted(byn):
        rows = [d for d in byn[n] if all(v in d and ok(d[v]) for v in V)]
        if not rows: P(f"| {name} | {n} | {len(byn[n])} | 0 | " + " | ".join("-" for _ in KV) + " | - |"); continue
        P(f"| {name} | {n} | {len(byn[n])} | {len(rows)} | " + " | ".join(f"{ratio(rows, v, BASE, 'celdas'):.3f} / {ratio(rows, v, BASE, 'cpu_s'):.3f}" for v in KV)
          + f" | {ratio(rows, 'art_raa_k6', 'art_raa_k4', 'celdas'):.3f} / {ratio(rows, 'art_raa_k6', 'art_raa_k4', 'cpu_s'):.3f} |")

P("\n## Resueltas solo por algunas variantes")
P("| familia | instancia | " + " | ".join(v[4:] for v in V) + " |"); P("|---|---|" + "---|" * len(V))
for name, I in D.items():
    for i in sorted(I):
        d = I[i]; s = [v in d and ok(d[v]) for v in V]
        if any(s) and not all(s):
            P(f"| {name} | {i} | " + " | ".join((f"{float(d[v]['cpu_s']):.0f} s" if x else "-") for v, x in zip(V, s)) + " |")

P("\n## Instancias que ninguna variante resuelve: cota inferior al limite de tiempo")
P("| familia | instancia | " + " | ".join(v[4:] for v in V) + " |"); P("|---|---|" + "---|" * len(V))
for name, I in D.items():
    for i in sorted(I):
        d = I[i]
        if not any(v in d and ok(d[v]) for v in V):
            P(f"| {name} | {i} | " + " | ".join(f"{float(d[v]['f_lb']):.6g}" if v in d and d[v]["f_lb"] not in ("", "nan") else "?" for v in V) + " |")

P("\n## Consistencia de optimos")
bad = 0; nchk = 0
for name, I in D.items():
    for i, d in sorted(I.items()):
        s = [(v, float(d[v]["f_lb"]), float(d[v]["f_ub"])) for v in V if v in d and ok(d[v])]
        if len(s) < 2: continue
        nchk += 1
        lo = max(x[1] for x in s); hi = min(x[2] for x in s)
        tol = 1e-6 * max(1.0, abs(lo), abs(hi))  # precision del optimizador: 1e-6 relativa y absoluta
        if lo > hi + 2 * tol:
            bad += 1; P(f"- NO SOLAPAN {name}/{i}: " + ", ".join(f"{v[4:]}=[{l:.10g},{u:.10g}]" for v, l, u in s))
        # una variante sin resolver no puede tener cota inferior por encima del optimo encontrado por otra
        for v in V:
            if v in d and not ok(d[v]) and d[v]["f_lb"] not in ("", "nan") and float(d[v]["f_lb"]) > hi + 2 * tol:
                bad += 1; P(f"- COTA INFERIOR SOBRE EL OPTIMO {name}/{i}: {v[4:]} lb={d[v]['f_lb']} optimo<= {hi:.10g}")
P(f"instancias revisadas (resueltas por al menos dos variantes): {nchk}; inconsistencias: {bad}")

P("\n## Estados distintos de SUCCESS y TIME_OUT")
c = collections.Counter((name, d[v]["estado"], d[v]["exit"]) for name, I in D.items() for d in I.values() for v in d)
for k, n in sorted(c.items()): P(f"- {k[0]}: {k[1]} (exit {k[2]}): {n}")
if a.out:
    os.makedirs(a.out, exist_ok=True); open(os.path.join(a.out, "resumen.md"), "w").write("\n".join(out) + "\n")
