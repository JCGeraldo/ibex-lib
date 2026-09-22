"""[raak local] Fase 3, nivel 1: analisis de range.csv (salida de tests/range_eval.cpp).

Por variante y escala de caja: media geometrica de la sobreestimacion (anchura afin / anchura del
rango muestreado), victorias / empates / derrotas por (instancia, funcion, caja) frente a la variante
base, separando el efecto de la aritmetica (X k=0 frente a AF2 k=0) y el del k-nomial (X k=3 frente
a X k=0). Produce nivel1_tabla.md, nivel1_gm_por_escala.png y nivel1_efectos.png en <outdir>.
uso: python3 analyze_range.py <range.csv> <outdir>
"""
import csv, math, os, sys
from collections import defaultdict
import numpy as np
import vizstyle as vs

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows = [r for r in csv.DictReader(open(src))]
for r in rows:
    for k in ("scale", "w_itv", "w_sample", "w_aff", "nl_err", "ratio_aff", "ratio_itv", "us"):
        r[k] = float(r[k])
    r["viol"] = int(r["viol"]); r["k_used"] = int(r["k_used"]); r["active"] = r["active"] == "1"
VARS = ["af2_k0", "af2_k3", "raa_k0", "raa_k3", "aa_k0", "aa_k3"]
key = lambda r: (r["instance"], r["func"], r["box_id"])
by = defaultdict(dict)
for r in rows:
    by[key(r)][r["variant"]] = r
scales = sorted(set(r["scale"] for r in rows), reverse=True)

def gm(v):
    v = [x for x in v if x > 0 and math.isfinite(x)]
    return math.exp(np.mean(np.log(v))) if v else float("nan")

def compare(a, b, keys, thr=0.05):
    """ratio w_aff[a]/w_aff[b] sobre las cajas donde ambas son activas y finitas."""
    rat = []
    for k in keys:
        ra, rb = by[k].get(a), by[k].get(b)
        if not (ra and rb and ra["active"] and rb["active"] and math.isfinite(ra["w_aff"]) and math.isfinite(rb["w_aff"]) and rb["w_aff"] > 0): continue
        rat.append(ra["w_aff"] / rb["w_aff"])
    rat = np.array(rat)
    return dict(n=len(rat), gana=int((rat < 1 - thr).sum()), empata=int((abs(rat - 1) <= thr).sum()), pierde=int((rat > 1 + thr).sum()),
                gm=gm(rat), identicas=int((rat == 1).sum()))

L = ["# Fase 3, nivel 1 — sobreestimacion de rangos sin resolver", "",
     f"Fuente: `{os.path.basename(src)}`: {len(rows)} filas, {len(by)} (instancia, funcion, caja), "
     f"{len(set(r['instance'] for r in rows))} instancias. Violaciones de contencion: {sum(r['viol'] for r in rows)}.", "",
     "*ratio* = anchura de la forma afin / anchura del rango muestreado (media geometrica sobre las cajas donde la forma es activa).",
     "Escala 1 = caja inicial; 0.5, 0.25, ... = sub-cajas aleatorias de esa anchura relativa.", "",
     "## Sobreestimacion por variante y escala", "",
     "| variante | " + " | ".join(f"escala {s:g}" for s in scales) + " | todas | formas inactivas | k-nomial/RAA actuo (filas) | us/eval |",
     "|---|" + "---|" * (len(scales) + 4)]
for v in VARS:
    rv = [r for r in rows if r["variant"] == v]
    cells = [gm([r["ratio_aff"] for r in rv if r["scale"] == s]) for s in scales]
    L.append(f"| {vs.VARIANT_LABEL[v]} | " + " | ".join(f"{c:.3f}" for c in cells) + f" | {gm([r['ratio_aff'] for r in rv]):.3f} | "
             f"{sum(1 for r in rv if not r['active'])} | {sum(1 for r in rv if r['k_used'] > 0)} | {np.mean([r['us'] for r in rv]):.1f} |")
L += ["", f"Intervalos (extension natural): ratio {gm([r['ratio_itv'] for r in rows if r['variant']=='af2_k0']):.3f} (todas las escalas).", "",
      "## Separacion de efectos (anchura de la forma; gana = mas estrecha en mas de 5 %)", "",
      "| efecto | comparacion | n | gana | empata | pierde | identicas | media geom. |", "|---|---|---|---|---|---|---|---|"]
keys = list(by.keys())
effects = [("aritmetica", "raa_k0", "af2_k0"), ("aritmetica", "aa_k0", "af2_k0"),
           ("k-nomial", "af2_k3", "af2_k0"), ("k-nomial", "raa_k3", "raa_k0"), ("k-nomial", "aa_k3", "aa_k0"),
           ("total", "raa_k3", "af2_k0"), ("total", "aa_k3", "af2_k0")]
eff_rows = []
for e, a, b in effects:
    c = compare(a, b, keys)
    eff_rows.append((e, a, b, c))
    L.append(f"| {e} | {vs.VARIANT_LABEL[a]} / {vs.VARIANT_LABEL[b]} | {c['n']} | {c['gana']} | {c['empata']} | {c['pierde']} | {c['identicas']} | {c['gm']:.4f} |")
L += ["", "## Por conjunto de instancias (media geometrica del ratio, todas las escalas)", "",
      "| conjunto | " + " | ".join(vs.VARIANT_LABEL[v] for v in VARS) + " |", "|---|" + "---|" * len(VARS)]
for s in sorted(set(r["set"] for r in rows)):
    L.append(f"| {s} | " + " | ".join(f"{gm([r['ratio_aff'] for r in rows if r['set']==s and r['variant']==v]):.3f}" for v in VARS) + " |")
open(os.path.join(out, "nivel1_tabla.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

vs.setup()
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 4))
for v in VARS:
    ys = [gm([r["ratio_aff"] for r in rows if r["variant"] == v and r["scale"] == s]) for s in scales]
    ax.plot(range(len(scales)), ys, vs.VARIANT_STYLE[v], color=vs.VARIANT_COLOR[v], marker="o", label=vs.VARIANT_LABEL[v])
ax.set_xticks(range(len(scales))); ax.set_xticklabels([f"{s:g}" for s in scales]); ax.set_xlabel("anchura relativa de la caja (1 = caja inicial)")
ax.set_ylabel("anchura afin / rango muestreado (media geom.)"); ax.set_yscale("log"); ax.legend(fontsize=8, ncol=2)
ax.set_title("Nivel 1: sobreestimacion por variante y tamano de caja", loc="left", color=vs.TEXT, fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(out, "nivel1_gm_por_escala.png")); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 3.6))
labels = [f"{vs.VARIANT_LABEL[a]}\nvs {vs.VARIANT_LABEL[b]}" for _, a, b, _ in eff_rows]
g = [c["gana"] for *_, c in eff_rows]; e_ = [c["empata"] for *_, c in eff_rows]; p = [c["pierde"] for *_, c in eff_rows]
x = np.arange(len(eff_rows)); w = 0.26
ax.bar(x - w, g, w, color=vs.SLOTS[2], label="mas estrecha (>5 %)"); ax.bar(x, e_, w, color="#c3c2b7", label="igual (±5 %)"); ax.bar(x + w, p, w, color=vs.SLOTS[7], label="mas ancha (>5 %)")
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7); ax.set_ylabel("(instancia, funcion, caja)"); ax.legend(fontsize=8)
ax.set_title("Nivel 1: victorias / empates / derrotas por par de variantes", loc="left", color=vs.TEXT, fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(out, "nivel1_efectos.png")); plt.close(fig)
print("ok:", out)
