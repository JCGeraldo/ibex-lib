"""[raak local] Fase 2.2: analisis de trig_lin.csv (salida de tests/trig_lin_test.cpp).

Produce, en la carpeta de salida:
  trig_tabla.md          tabla por (funcion, aritmetica, modo): media geometrica de la sobreestimacion,
                         error de linealizacion medio, desglose por intervalos con extremo / con inflexion,
                         violaciones y tiempo medio
  trig_ratio_vs_width.png  sobreestimacion (media geometrica) frente al ancho del intervalo, sin y cos, AF2
  trig_linerr_vs_width.png error de linealizacion medio frente al ancho, las 4 funciones, AF2
  trig_aa_vs_af2.png       error de linealizacion en AA frente a AF2 (compuestas), por modo
uso: python3 analyze_trig.py <trig_lin.csv> <outdir>
"""
import csv, math, os, sys
from collections import defaultdict
import numpy as np
import vizstyle as vs

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows = list(csv.DictReader(open(src)))
for r in rows:
    for k in ("center", "width", "width_aff", "width_exact", "ratio", "excess", "lin_err", "slope", "ns"):
        r[k] = float(r[k])
    r["viol"] = int(r["viol"]); r["has_ext"] = r["has_ext"] == "1"; r["has_infl"] = r["has_infl"] == "1"

FUNCS = ["sin", "cos", "sin*cos", "sin2+cos2"]; ARITHS = ["AF2", "AA"]; MODES = ["legacy", "cheb", "minrange"]

def gm(vals):
    vals = [v for v in vals if v > 0]
    return math.exp(sum(math.log(v) for v in vals) / len(vals)) if vals else float("nan")

def sel(**kw):
    return [r for r in rows if all(r[k] == v for k, v in kw.items())]

# ---------- tabla
lines = ["# Fase 2.2 — calidad de la linealizacion de sin/cos", "",
         f"Fuente: `{os.path.basename(src)}` ({len(rows)} filas = 4 funciones x 735 intervalos x 2 aritmeticas x 3 modos).",
         "", "*ratio* = anchura de la forma afin / anchura del rango exacto (media geometrica; 1 = optimo; no definido para",
         "sin^2+cos^2, cuyo rango exacto es un punto). *lin_err* = radio de la parte no lineal de la forma (media).",
         "*ext* / *infl* = solo los intervalos que contienen un extremo / un punto de inflexion de la funcion basica.", "",
         "| funcion | aritmetica | modo | ratio | ratio (ext) | ratio (infl) | lin_err | lin_err (ext) | lin_err (infl) | viol | ns/eval |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
for f in FUNCS:
    for a in ARITHS:
        for m in MODES:
            s = sel(func=f, arith=a, mode=m)
            if not s: continue
            e = [r for r in s if r["has_ext"]]; i = [r for r in s if r["has_infl"]]
            fmt = lambda v: "—" if (isinstance(v, float) and math.isnan(v)) else f"{v:.4f}"
            lines.append(f"| {f} | {a} | {m} | {fmt(gm([r['ratio'] for r in s]))} | {fmt(gm([r['ratio'] for r in e]))} | {fmt(gm([r['ratio'] for r in i]))} | "
                         f"{np.mean([r['lin_err'] for r in s]):.4f} | {np.mean([r['lin_err'] for r in e]):.4f} | {np.mean([r['lin_err'] for r in i]):.4f} | "
                         f"{sum(r['viol'] for r in s)} | {np.mean([r['ns'] for r in s]):.0f} |")
# victorias por intervalo (cheb vs legacy, minrange vs legacy) en lin_err
lines += ["", "## Comparacion por intervalo del error de linealizacion (misma funcion, aritmetica e intervalo)", "",
          "| funcion | aritmetica | comparacion | menor | igual (±1e-12) | mayor |", "|---|---|---|---|---|---|"]
for f in FUNCS:
    for a in ARITHS:
        base = {(r["center"], r["width"]): r["lin_err"] for r in sel(func=f, arith=a, mode="legacy")}
        for m in ("cheb", "minrange"):
            lo = eq = hi = 0
            for r in sel(func=f, arith=a, mode=m):
                b = base[(r["center"], r["width"])]
                if abs(r["lin_err"] - b) <= 1e-12: eq += 1
                elif r["lin_err"] < b: lo += 1
                else: hi += 1
            lines.append(f"| {f} | {a} | {m} vs legacy | {lo} | {eq} | {hi} |")
open(os.path.join(out, "trig_tabla.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

# ---------- graficos
vs.setup()
import matplotlib.pyplot as plt
widths = sorted(set(r["width"] for r in rows))

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, f in zip(axes, ["sin", "cos"]):
    for m in MODES:
        ys = [gm([r["ratio"] for r in sel(func=f, arith="AF2", mode=m, width=w)]) for w in widths]
        ax.plot(widths, ys, vs.MODE_LABEL and "-", color=vs.MODE_COLOR[m], marker="o", label=vs.MODE_LABEL[m])
        ax.annotate(m, (widths[-1], ys[-1]), xytext=(4, 0), textcoords="offset points", color=vs.MODE_COLOR[m], fontsize=8, va="center")
    ax.set_xscale("log"); ax.set_title(f"{f}(x): sobreestimacion frente al ancho", color=vs.TEXT, fontsize=10, loc="left")
    ax.set_xlabel("ancho del intervalo"); ax.axhline(1.0, color=vs.TEXT2, linewidth=0.8)
axes[0].set_ylabel("anchura afin / anchura exacta (media geom.)")
axes[0].legend(loc="upper left", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(out, "trig_ratio_vs_width.png")); plt.close(fig)

fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True)
for ax, f in zip(axes.flat, FUNCS):
    for m in MODES:
        ys = [np.mean([r["lin_err"] for r in sel(func=f, arith="AF2", mode=m, width=w)]) for w in widths]
        ax.plot(widths, ys, color=vs.MODE_COLOR[m], marker="o", label=vs.MODE_LABEL[m])
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(f"{f}", color=vs.TEXT, fontsize=10, loc="left")
for ax in axes[1]: ax.set_xlabel("ancho del intervalo")
for ax in axes[:, 0]: ax.set_ylabel("error de linealizacion (media)")
axes[0][0].legend(fontsize=8)
fig.suptitle("Error de linealizacion frente al ancho (Affine2 = base de AF2 y RAA)", color=vs.TEXT, x=0.01, ha="left", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(out, "trig_linerr_vs_width.png")); plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, f in zip(axes, ["sin*cos", "sin2+cos2"]):
    for m in MODES:
        a2 = {(r["center"], r["width"]): r["lin_err"] for r in sel(func=f, arith="AF2", mode=m)}
        xs, ys = [], []
        for r in sel(func=f, arith="AA", mode=m):
            xs.append(a2[(r["center"], r["width"])]); ys.append(r["lin_err"])
        ax.scatter(xs, ys, s=12, color=vs.MODE_COLOR[m], alpha=0.6, edgecolors="none", label=vs.MODE_LABEL[m])
    lim = [1e-6, max(r["lin_err"] for r in sel(func=f)) * 1.2]
    ax.plot(lim, lim, color=vs.TEXT2, linewidth=0.8); ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_title(f"{f}: error AA frente a AF2", color=vs.TEXT, fontsize=10, loc="left"); ax.set_xlabel("error de linealizacion, Affine2 (AF2/RAA)")
axes[0].set_ylabel("error de linealizacion, Affine3 (AA)"); axes[0].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(out, "trig_aa_vs_af2.png")); plt.close(fig)
print("ok:", out)
