"""[raak local] Fase 3, nivel 2 y Fase 4: analisis de runs.csv (salida de scripts/wsl_fase3_sweep.sh).

Para cada relajacion (compo, art) presente en el CSV:
  - tabla de estados por variante
  - frente a la base (<lr>_af2_k0): victorias / empates / derrotas en celdas y en CPU (umbral 5 %),
    medias geometricas de los cocientes sobre las instancias resueltas por ambas
  - separacion de efectos: aritmetica (X k=0 vs AF2 k=0) y k-nomial (X k=3 vs X k=0)
  - perfiles de desempeno (Dolan-More) en CPU y en celdas
  - dispersion log-log de celdas y CPU de cada variante frente a la base
  - tabla consolidada por instancia (celdas y CPU de todas las variantes)
Escribe todo en <outdir> mas un README.md que explica cada archivo.
uso: python3 analyze_sweep.py <runs.csv> <outdir> [--tlim 1800]
"""
import csv, math, os, sys
from collections import defaultdict
import numpy as np
import vizstyle as vs

src, out = sys.argv[1], sys.argv[2]
TLIM = float(sys.argv[sys.argv.index("--tlim") + 1]) if "--tlim" in sys.argv else 1800.0
os.makedirs(out, exist_ok=True)
rows = list(csv.DictReader(open(src)))
for r in rows:
    r["celdas"] = float(r["celdas"]) if r["celdas"] not in ("", None) else float("nan")
    r["cpu_s"] = float(r["cpu_s"]) if r["cpu_s"] not in ("", None) else float("nan")
res = defaultdict(dict)                     # (inst) -> variante -> fila
for r in rows: res[r["instancia"]][r["variante"]] = r
variants = sorted(set(r["variante"] for r in rows))
lrs = sorted(set(v.split("_")[0] for v in variants if v != "xn"))
SOLVED = {"SUCCESS", "INFEASIBLE"}

def gm(v):
    v = [x for x in v if x > 0 and math.isfinite(x)]
    return math.exp(np.mean(np.log(v))) if v else float("nan")

def solved(r): return r is not None and r["estado"] in SOLVED

def compare(a, b, metric, thr=0.05):
    rat, only_a, only_b = [], 0, 0
    for inst, d in res.items():
        ra, rb = d.get(a), d.get(b)
        if solved(ra) and solved(rb):
            if rb[metric] > 0: rat.append(ra[metric] / rb[metric])
        elif solved(ra) and rb is not None: only_a += 1
        elif solved(rb) and ra is not None: only_b += 1
    rat = np.array(rat)
    return dict(n=len(rat), gana=int((rat < 1 - thr).sum()), empata=int((abs(rat - 1) <= thr).sum()), pierde=int((rat > 1 + thr).sum()),
                gm=gm(rat), solo_a=only_a, solo_b=only_b)

def perf_profile(ax, vlist, metric, title):
    """Dolan-More: fraccion de instancias con metric <= tau * mejor(metric) entre las variantes de vlist."""
    insts = [i for i in res if all(v in res[i] for v in vlist)]
    best = {}
    for i in insts:
        vals = [res[i][v][metric] for v in vlist if solved(res[i][v]) and res[i][v][metric] > 0]
        best[i] = min(vals) if vals else None
    # tau hasta el mayor cociente finito observado (con margen), no mas alla
    tmax = 1.0
    for i in insts:
        if best[i] is None: continue
        for v in vlist:
            r = res[i][v]
            if solved(r) and r[metric] > 0: tmax = max(tmax, r[metric] / best[i])
    taus = np.logspace(0, math.log10(tmax * 1.5), 200)
    for v in vlist:
        ratios = []
        for i in insts:
            r = res[i][v]
            if best[i] is None: continue
            ratios.append(r[metric] / best[i] if solved(r) and r[metric] > 0 else float("inf"))
        ratios = np.array(ratios)
        ys = [np.mean(ratios <= t) if len(ratios) else 0 for t in taus]
        k = vs.variant_key(v)
        ax.plot(taus, ys, vs.VARIANT_STYLE.get(k, "-"), color=vs.VARIANT_COLOR.get(k, "#888"), label=vs.VARIANT_LABEL.get(k, v))
    ax.set_xscale("log"); ax.set_ylim(0, 1.02); ax.set_xlabel("tau (cociente respecto a la mejor variante)"); ax.set_ylabel("fraccion de instancias")
    ax.set_title(title, loc="left", color=vs.TEXT, fontsize=10); ax.legend(fontsize=7, loc="lower right")

vs.setup()
import matplotlib.pyplot as plt
L = ["# Fase 3, nivel 2 — barrido del solver", "", f"Fuente: `{os.path.basename(src)}`: {len(rows)} corridas, {len(res)} instancias, limite {TLIM:g} s de CPU.", ""]
readme = ["# Resultados del nivel 2 (barrido del solver)", "", f"Datos: `runs.csv` ({len(rows)} corridas, {len(res)} instancias, `-t {TLIM:g}`). Generado por `raak/analysis/analyze_sweep.py`.", "",
          "| archivo | que muestra |", "|---|---|", "| `nivel2_tabla.md` | Todas las tablas: estados, victorias/derrotas/empates, medias geometricas, separacion de efectos y tabla consolidada por instancia. |"]
for lr in lrs:
    base = f"{lr}_af2_k0"
    vl = [v for v in variants if v.startswith(lr + "_")] + (["xn"] if "xn" in variants else [])
    L += [f"## Relajacion `{lr}`", "", "### Estados", "", "| variante | " + " | ".join(sorted(set(r["estado"] for r in rows))) + " | CPU total (h) |", "|---|" + "---|" * (len(set(r["estado"] for r in rows)) + 1)]
    ests = sorted(set(r["estado"] for r in rows))
    for v in vl:
        rv = [r for r in rows if r["variante"] == v]
        L.append(f"| {v} | " + " | ".join(str(sum(1 for r in rv if r["estado"] == e)) for e in ests) + f" | {np.nansum([r['cpu_s'] for r in rv]) / 3600:.2f} |")
    L += ["", f"### Frente a la base `{base}` (instancias resueltas por ambas; gana = menos de 0.95x, pierde = mas de 1.05x)", "",
          "| variante | n | celdas: gana/empata/pierde | celdas media geom. | CPU: gana/empata/pierde | CPU media geom. | resuelve solo esta | resuelve solo la base |", "|---|---|---|---|---|---|---|---|"]
    for v in vl:
        if v == base: continue
        cc = compare(v, base, "celdas"); ct = compare(v, base, "cpu_s")
        L.append(f"| {v} | {cc['n']} | {cc['gana']}/{cc['empata']}/{cc['pierde']} | {cc['gm']:.3f} | {ct['gana']}/{ct['empata']}/{ct['pierde']} | {ct['gm']:.3f} | {cc['solo_a']} | {cc['solo_b']} |")
    L += ["", "### Separacion de efectos", "", "| efecto | comparacion | n | celdas gana/empata/pierde | celdas media geom. | CPU media geom. |", "|---|---|---|---|---|---|"]
    for e, a, b in [("aritmetica", f"{lr}_raa_k0", base), ("aritmetica", f"{lr}_aa_k0", base),
                    ("k-nomial", f"{lr}_af2_k3", base), ("k-nomial", f"{lr}_raa_k3", f"{lr}_raa_k0"), ("k-nomial", f"{lr}_aa_k3", f"{lr}_aa_k0"),
                    ("total", f"{lr}_raa_k3", base), ("total", f"{lr}_aa_k3", base)]:
        if a not in variants or b not in variants: continue
        cc = compare(a, b, "celdas"); ct = compare(a, b, "cpu_s")
        L.append(f"| {e} | {a} / {b} | {cc['n']} | {cc['gana']}/{cc['empata']}/{cc['pierde']} | {cc['gm']:.3f} | {ct['gm']:.3f} |")
    # perfiles
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    perf_profile(axes[0], vl, "cpu_s", f"Perfil de desempeno en CPU ({lr})")
    perf_profile(axes[1], vl, "celdas", f"Perfil de desempeno en celdas ({lr})")
    fig.tight_layout(); fn = f"nivel2_perfil_{lr}.png"; fig.savefig(os.path.join(out, fn)); plt.close(fig)
    readme.append(f"| `{fn}` | Perfiles de desempeno (Dolan-More) con `{lr}`: para cada tau, fraccion de instancias que la variante resuelve con CPU (izq.) o celdas (der.) a lo sumo tau veces la mejor variante. Mas arriba y mas a la izquierda es mejor. Trazo discontinuo = con k-nomial. |")
    # dispersion
    others = [v for v in vl if v != base]
    fig, axes = plt.subplots(2, len(others), figsize=(2.9 * len(others), 5.8), squeeze=False)
    for j, v in enumerate(others):
        for i, (metric, lab) in enumerate([("celdas", "celdas"), ("cpu_s", "CPU (s)")]):
            ax = axes[i][j]; xs, ys, xt, yt = [], [], [], []
            for inst, d in res.items():
                ra, rb = d.get(v), d.get(base)
                if ra is None or rb is None: continue
                if solved(ra) and solved(rb): xs.append(max(rb[metric], 1e-3)); ys.append(max(ra[metric], 1e-3))
                else: xt.append(max(rb[metric], 1e-3) if math.isfinite(rb[metric]) else TLIM); yt.append(max(ra[metric], 1e-3) if math.isfinite(ra[metric]) else TLIM)
            k = vs.variant_key(v)
            ax.scatter(xs, ys, s=14, color=vs.VARIANT_COLOR.get(k, "#888"), alpha=0.75, edgecolors="none")
            if xt: ax.scatter(xt, yt, s=14, facecolors="none", edgecolors=vs.TEXT2, linewidths=0.8)
            allv = xs + ys + xt + yt
            lim = [min(allv) * 0.7, max(allv) * 1.4] if allv else [1e-3, 1]
            ax.plot(lim, lim, color=vs.TEXT2, linewidth=0.8); ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
            ax.set_title(f"{vs.VARIANT_LABEL.get(k, v)}", loc="left", color=vs.TEXT, fontsize=9)
            ax.set_xlabel(f"{lab}, {vs.VARIANT_LABEL['af2_k0']} (base)", fontsize=8); ax.set_ylabel(f"{lab}, variante", fontsize=8)
    fig.suptitle(f"Dispersion frente a la base AF2 ({lr}); debajo de la diagonal = mejor; circulos vacios = alguna no resuelta", x=0.01, ha="left", color=vs.TEXT, fontsize=10)
    fig.tight_layout(); fn = f"nivel2_dispersion_{lr}.png"; fig.savefig(os.path.join(out, fn)); plt.close(fig)
    readme.append(f"| `{fn}` | Dispersion log-log por instancia con `{lr}`: celdas (arriba) y CPU (abajo) de cada variante frente a AF2 sin k-nomial. Un punto bajo la diagonal significa que la variante necesito menos. |")
# tabla consolidada
L += ["", "## Tabla consolidada por instancia (celdas / CPU s; `—` = no resuelta)", "", "| instancia | " + " | ".join(variants) + " |", "|---|" + "---|" * len(variants)]
for inst in sorted(res):
    cells = []
    for v in variants:
        r = res[inst].get(v)
        cells.append("—" if r is None else (f"{r['celdas']:.0f} / {r['cpu_s']:.1f}" if solved(r) else r["estado"]))
    L.append(f"| {inst} | " + " | ".join(cells) + " |")
open(os.path.join(out, "nivel2_tabla.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
readme += ["", "Lectura: *celdas* = nodos del B&B (`number of cells`), *CPU* = `cpu time used`. Las medias geometricas se calculan sobre",
           "las instancias resueltas por las dos variantes comparadas; *gana* = cociente < 0.95, *pierde* = cociente > 1.05."]
open(os.path.join(out, "README.md"), "w", encoding="utf-8").write("\n".join(readme) + "\n")
print("ok:", out)
