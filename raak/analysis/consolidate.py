"""[raak local] Fase 4: tabla consolidada y grafico resumen de todas las etapas del nivel 2 disponibles.

Lee <base>/<etapa>/runs.csv para cada etapa presente y escribe en <base>:
  RESUMEN.md               una tabla por etapa (variante: instancias resueltas, gana/empata/pierde y media
                           geometrica de celdas y CPU frente a AF2 sin k-nomial) y la separacion de efectos
  resumen_medias_geom.png  medias geometricas de celdas y CPU por variante y etapa (1 = AF2 sin k-nomial)
uso: python3 consolidate.py <base> [etapa ...]
"""
import csv, math, os, sys
from collections import defaultdict
import numpy as np
import vizstyle as vs

base = sys.argv[1]
stages = sys.argv[2:] or sorted(d for d in os.listdir(base) if os.path.isfile(os.path.join(base, d, "runs.csv")))
SOLVED = {"SUCCESS", "INFEASIBLE"}
ORDER = ["af2_k0", "af2_k3", "raa_k0", "raa_k3", "aa_k0", "aa_k3", "xn"]

def gm(v):
    v = [x for x in v if x > 0 and math.isfinite(x)]
    return math.exp(np.mean(np.log(v))) if v else float("nan")

def load(stage):
    res = defaultdict(dict)
    for r in csv.DictReader(open(os.path.join(base, stage, "runs.csv"))):
        r["celdas"] = float(r["celdas"]) if r["celdas"] else float("nan"); r["cpu_s"] = float(r["cpu_s"]) if r["cpu_s"] else float("nan")
        res[r["instancia"]][vs.variant_key(r["variante"])] = r
    return res

def compare(res, a, b, metric, thr=0.05):
    rat = [d[a][metric] / d[b][metric] for d in res.values() if a in d and b in d and d[a]["estado"] in SOLVED and d[b]["estado"] in SOLVED and d[b][metric] > 0]
    rat = np.array(rat)
    return len(rat), int((rat < 1 - thr).sum()), int((abs(rat - 1) <= thr).sum()), int((rat > 1 + thr).sum()), gm(rat)

L = ["# Fase 4 — tabla consolidada del nivel 2", "", f"Etapas: {', '.join(stages)}. Base de cada comparacion: AF2 sin k-nomial de la misma etapa; ",
     "*gana* = cociente < 0.95, *pierde* = > 1.05; medias geometricas sobre las instancias resueltas por ambas.", ""]
summary = {}   # (stage, variant) -> (gm_cells, gm_cpu)
for st in stages:
    res = load(st)
    n_inst = len(res)
    L += [f"## {st}", "", f"{n_inst} instancias.", "",
          "| variante | resueltas | celdas gana / empata / pierde | celdas media geom. | CPU gana / empata / pierde | CPU media geom. |", "|---|---|---|---|---|---|"]
    for v in ORDER:
        if not any(v in d for d in res.values()): continue
        solved = sum(1 for d in res.values() if v in d and d[v]["estado"] in SOLVED)
        if v == "af2_k0":
            L.append(f"| {vs.VARIANT_LABEL[v]} (base) | {solved} | — | 1 | — | 1 |"); summary[(st, v)] = (1.0, 1.0); continue
        n, g, e, p, gc = compare(res, v, "af2_k0", "celdas"); _, gt, et, pt, gcpu = compare(res, v, "af2_k0", "cpu_s")
        summary[(st, v)] = (gc, gcpu)
        L.append(f"| {vs.VARIANT_LABEL[v]} | {solved} | {g} / {e} / {p} | {gc:.3f} | {gt} / {et} / {pt} | {gcpu:.3f} |")
    L += ["", "| efecto | comparacion | celdas gana / empata / pierde | celdas media geom. | CPU media geom. |", "|---|---|---|---|---|"]
    for e, a, b in [("aritmetica", "raa_k0", "af2_k0"), ("aritmetica", "aa_k0", "af2_k0"), ("k-nomial", "af2_k3", "af2_k0"),
                    ("k-nomial", "raa_k3", "raa_k0"), ("k-nomial", "aa_k3", "aa_k0"), ("total", "raa_k3", "af2_k0"), ("total", "aa_k3", "af2_k0")]:
        n, g, eq, p, gc = compare(res, a, b, "celdas"); gcpu = compare(res, a, b, "cpu_s")[4]
        if n: L.append(f"| {e} | {vs.VARIANT_LABEL[a]} / {vs.VARIANT_LABEL[b]} | {g} / {eq} / {p} | {gc:.3f} | {gcpu:.3f} |")
    L.append("")
open(os.path.join(base, "RESUMEN.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

vs.setup()
import matplotlib.pyplot as plt
vlist = [v for v in ORDER if v != "af2_k0" and any((st, v) in summary for st in stages)]
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=False)
x = np.arange(len(vlist)); w = 0.8 / max(1, len(stages))
for j, (metric, title) in enumerate([(0, "celdas"), (1, "CPU")]):
    ax = axes[j]
    for si, st in enumerate(stages):
        vals = [summary.get((st, v), (float("nan"), float("nan")))[metric] for v in vlist]
        bars = ax.bar(x + (si - (len(stages) - 1) / 2) * w, vals, w * 0.92, color=vs.SLOTS[si % len(vs.SLOTS)], label=st)
        for b_, val in zip(bars, vals):
            if math.isfinite(val): ax.annotate(f"{val:.2f}", (b_.get_x() + b_.get_width() / 2, val), ha="center", va="bottom", fontsize=6, color=vs.TEXT2)
    ax.axhline(1.0, color=vs.TEXT2, linewidth=0.8); ax.set_xticks(x); ax.set_xticklabels([vs.VARIANT_LABEL[v] for v in vlist], fontsize=7, rotation=15)
    ax.set_ylabel(f"{title}: media geom. variante / AF2"); ax.set_title(f"Media geometrica de {title} frente a AF2 sin k-nomial", loc="left", color=vs.TEXT, fontsize=10)
axes[0].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(base, "resumen_medias_geom.png")); plt.close(fig)
print("ok:", base)
