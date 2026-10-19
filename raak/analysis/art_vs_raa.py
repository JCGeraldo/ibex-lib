"""[raak local] art (AF2) frente a RAA k=0, 2 y 3, relajacion art, todas las instancias (etapas B y D + corrida k=2).
Produce en results/09-informes/: tabla por instancia (CSV), resumen (JSON) y dos figuras. Uso: python analysis/art_vs_raa.py"""
import sys, os, json
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # raak/
RES = os.path.join(REPO, "results", "07-fase3-nivel2-solver", "fase3-20260921")
OUT = os.path.join(REPO, "results", "09-informes")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "analysis"))
import vizstyle as vz
import matplotlib.pyplot as plt
vz.setup()

VARS = ["art_af2_k0", "art_raa_k0", "art_raa_k2", "art_raa_k3"]
LABEL = {"art_af2_k0": "art (AF2)", "art_raa_k0": "RAA k=0", "art_raa_k2": "RAA k=2", "art_raa_k3": "RAA k=3"}
COLOR = {"art_af2_k0": vz.VARIANT_COLOR["af2_k0"], "art_raa_k0": vz.VARIANT_COLOR["raa_k0"], "art_raa_k2": vz.SLOTS[1], "art_raa_k3": vz.VARIANT_COLOR["raa_k3"]}
STYLE = {"art_af2_k0": "-", "art_raa_k0": "-", "art_raa_k2": "-.", "art_raa_k3": "--"}

frames = []
for folder, grupo in [("B_easy_medium_art", "easy+medium"), ("D_hard_others_art", "hard+others")]:
    r = pd.read_csv(os.path.join(RES, folder, "runs.csv"))
    r["grupo"] = grupo
    frames.append(r)
# corrida de k=2 (5 de octubre)
k2 = pd.read_csv(os.path.join(REPO, "results", "07-fase3-nivel2-solver", "fase3-k2-20261005", "art_raa_k2", "runs.csv"))
k2["grupo"] = k2.instancia.str.split("/").str[0].map(lambda s: "easy+medium" if s in ("easy", "medium") else "hard+others")
frames.append(k2)
d = pd.concat(frames)
d = d[d.variante.isin(VARS)].copy()
d["set"] = d.instancia.str.split("/").str[0]
d["inst"] = d.instancia.str.split("/").str[1]


def gm(x):
    x = np.asarray(x, float); x = x[np.isfinite(x) & (x > 0)]
    return float(np.exp(np.log(x).mean())) if len(x) else float("nan")


# ---------------- tabla por instancia
rows = []
for (grupo, set_, inst), g in d.groupby(["grupo", "set", "inst"], sort=False):
    row = {"grupo": grupo, "set": set_, "instancia": inst}
    for v in VARS:
        s = g[g.variante == v]
        if len(s) == 0:
            row[f"{v}_estado"] = "SIN_DATO"; row[f"{v}_celdas"] = ""; row[f"{v}_cpu"] = ""
        else:
            s = s.iloc[0]
            row[f"{v}_estado"] = s.estado
            row[f"{v}_celdas"] = "" if pd.isna(s.celdas) else int(s.celdas)
            row[f"{v}_cpu"] = "" if pd.isna(s.cpu_s) else float(s.cpu_s)
    rows.append(row)
tab = pd.DataFrame(rows)
orden_set = {"easy": 0, "medium": 1, "hard": 2, "others": 3}
tab["o"] = tab.set.map(orden_set)
tab = tab.sort_values(["o", "instancia"]).drop(columns="o")
tab.to_csv(os.path.join(OUT, "tabla_por_instancia_art_vs_raa.csv"), index=False)

# ---------------- resumen
ok = d[d.estado == "SUCCESS"]
cells = ok.pivot_table(index="instancia", columns="variante", values="celdas")
cpu = ok.pivot_table(index="instancia", columns="variante", values="cpu_s")
grupo_de = d.drop_duplicates("instancia").set_index("instancia").grupo
resumen = {}
for grupo in ["easy+medium", "hard+others", "todas"]:
    idx = cells.index if grupo == "todas" else cells.index[grupo_de.loc[cells.index] == grupo]
    n_inst = int(d[d.grupo == grupo].instancia.nunique()) if grupo != "todas" else int(d.instancia.nunique())
    fila = {}
    for v in VARS:
        c = cells.loc[idx]
        m = c[v].notna() & c["art_af2_k0"].notna()
        rc = c.loc[m, v] / c.loc[m, "art_af2_k0"]
        rt = cpu.loc[c.index[m], v] / cpu.loc[c.index[m], "art_af2_k0"]
        fila[v] = {
            "resueltas": int(c[v].notna().sum()), "n": n_inst, "comparables": int(m.sum()),
            "gm_celdas": gm(rc), "gm_cpu": gm(rt),
            "celdas_gana": int((rc < 0.95).sum()), "celdas_empata": int(((rc >= 0.95) & (rc <= 1.05)).sum()), "celdas_pierde": int((rc > 1.05).sum()),
            "cpu_gana": int((rt < 0.95).sum()), "cpu_empata": int(((rt >= 0.95) & (rt <= 1.05)).sum()), "cpu_pierde": int((rt > 1.05).sum()),
            "celdas_total": float(c[v].sum()), "cpu_total_h": float(cpu.loc[idx, v].sum() / 3600),
        }
    # k2 y k3 frente a k0 dentro de RAA, y k3 frente a k2
    for a, b, key in [("art_raa_k3", "art_raa_k0", "k3_vs_k0"), ("art_raa_k2", "art_raa_k0", "k2_vs_k0"), ("art_raa_k3", "art_raa_k2", "k3_vs_k2")]:
        both = cells.loc[idx][[a, b]].dropna()
        rc = both[a] / both[b]; rt = cpu.loc[both.index, a] / cpu.loc[both.index, b]
        fila[key] = {"comparables": int(len(both)), "gm_celdas": gm(rc), "gm_cpu": gm(rt),
                     "celdas_gana": int((rc < 0.95).sum()), "celdas_pierde": int((rc > 1.05).sum()),
                     "identicas": int((both[a] == both[b]).sum())}
    resumen[grupo] = fila

# instancias con mayor cambio RAA / art
both = cells[["art_raa_k0", "art_af2_k0"]].dropna()
r = (both["art_raa_k0"] / both["art_af2_k0"]).sort_values()
top = []
for inst, val in list(r.items())[:6]:
    top.append({"instancia": inst, "ratio": float(val), "art": int(both.loc[inst, "art_af2_k0"]), "raa": int(both.loc[inst, "art_raa_k0"]),
                "art_cpu": float(cpu.loc[inst, "art_af2_k0"]), "raa_cpu": float(cpu.loc[inst, "art_raa_k0"])})
resumen["top_raa"] = top
# estados no SUCCESS
est = d[d.estado != "SUCCESS"].groupby(["instancia", "estado"]).variante.apply(lambda s: ",".join(sorted(s))).reset_index()
resumen["no_success"] = est.to_dict(orient="records")
with open(os.path.join(OUT, "resumen.json"), "w", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=1)

# ---------------- figura: perfiles
def perf_profile(ax, table, xlabel):
    best = table.min(axis=1); ratios = table.div(best, axis=0)
    finite = ratios.replace([np.inf], np.nan).max().max()
    taus = np.logspace(0, np.log10(max(finite, 1.5) * 1.05), 300)
    for v in table.columns:
        rr = np.nan_to_num(ratios[v].values, nan=np.inf)
        ax.step(taus, [(rr <= t).mean() for t in taus], where="post", color=COLOR[v], label=LABEL[v], linestyle=STYLE[v])
    ax.set_xscale("log"); ax.set_xlabel(xlabel); ax.set_ylabel("fraccion de instancias"); ax.set_ylim(0, 1.02)

c = cells[VARS]; c = c[c.notna().any(axis=1)]
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
perf_profile(axes[0], c, "celdas / celdas de la mejor (log)")
perf_profile(axes[1], cpu.loc[c.index, VARS], "CPU / CPU de la mejor (log)")
axes[0].set_title("nodos del B&B (celdas)"); axes[1].set_title("tiempo de CPU")
axes[1].legend(loc="lower right")
fig.suptitle(f"Relajacion art: AF2 frente a RAA (k=0, 2, 3). {len(c)} instancias de easy, medium, hard y others resueltas por alguna; limite 1800 s", y=1.0)
fig.savefig(os.path.join(OUT, "perfiles_art_vs_raa.png"), bbox_inches="tight"); plt.close(fig)

# ---------------- figura: dispersion por instancia celdas RAA k0 vs art
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
for ax, (metric, tbl, lab) in zip(axes, [("celdas", cells, "celdas"), ("cpu", cpu, "CPU (s)")]):
    both = tbl[["art_af2_k0", "art_raa_k0", "art_raa_k2", "art_raa_k3"]].dropna()
    ax.scatter(both["art_af2_k0"], both["art_raa_k0"], s=22, color=COLOR["art_raa_k0"], label="RAA k=0", alpha=0.8, zorder=3)
    ax.scatter(both["art_af2_k0"], both["art_raa_k2"], s=22, color=COLOR["art_raa_k2"], label="RAA k=2", alpha=0.8, marker="+", zorder=4)
    ax.scatter(both["art_af2_k0"], both["art_raa_k3"], s=18, color=COLOR["art_raa_k3"], label="RAA k=3", alpha=0.8, marker="x", zorder=5)
    lo = max(both.min().min(), 1e-3 if metric == "cpu" else 0.7); hi = both.max().max() * 1.3
    ax.plot([lo, hi], [lo, hi], color=vz.TEXT2, linewidth=1)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel(f"art (AF2): {lab}"); ax.set_ylabel(f"RAA: {lab}")
axes[0].legend(loc="upper left")
fig.suptitle("Por instancia: RAA frente a art (AF2). Debajo de la diagonal, RAA mejor", y=1.0)
fig.savefig(os.path.join(OUT, "dispersion_art_vs_raa.png"), bbox_inches="tight"); plt.close(fig)

print(json.dumps({g: {v: {k: (round(x, 3) if isinstance(x, float) else x) for k, x in f.items()} for v, f in resumen[g].items()} for g in ["easy+medium", "hard+others", "todas"]}, indent=1, ensure_ascii=False))
print("top RAA:", resumen["top_raa"]); print("no success:", len(resumen["no_success"]))
print("instancias en tabla:", len(tab))
