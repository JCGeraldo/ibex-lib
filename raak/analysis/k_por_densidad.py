"""[raak local] Punto 2 del to-do de fin de octubre: mejor k segun densidad.
Cruza (i) el tamano de clique disponible por producto (cliques_sinteticas.py), (ii) el nivel 1 con bloques por tamano
y k = 2..6 (range_eval con parche 0010), (iii) el nivel 2 de la sesion 0009 por configuracion (n, densidad).
Produce en <out>: anchura_por_k.csv, bloques_por_tamano.csv, nivel2_por_config.csv, mejor_k_por_instancia.csv y figuras.
uso: python analysis/k_por_densidad.py <range.csv> <cliques_synq.csv> <tabla_raa_baseline.csv> <por_configuracion.csv> --out DIR
"""
import sys, os, argparse
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))
import vizstyle as vz
import matplotlib.pyplot as plt
vz.setup()
ap = argparse.ArgumentParser(); ap.add_argument("range_csv"); ap.add_argument("cliques"); ap.add_argument("tabla"); ap.add_argument("config"); ap.add_argument("--out", required=True)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
def gm(x): x = np.asarray(x, float); x = x[np.isfinite(x) & (x > 0)]; return float(np.exp(np.log(x).mean())) if len(x) else float("nan")

d = pd.read_csv(a.range_csv); d = d[d.active == 1]
KS = ["raa_k2", "raa_k3", "raa_k4", "raa_k5", "raa_k6"]
key = ["set", "instance", "func", "box_id"]
w = d.pivot_table(index=key, columns="variant", values="w_aff")
w = w[np.isfinite(w[["raa_k0"] + KS]).all(axis=1)]
meta = d.drop_duplicates(key).set_index(key)
inst = w.reset_index()[["set", "instance"]]
inst["n"] = inst.instance.str.extract(r"_n(\d+)_").astype(float)
inst["rho"] = inst.instance.str.extract(r"_d(\d+)_").astype(float) / 100
inst["diag"] = inst.instance.str.extract(r"_d\d+_(pos|posneg)_")
inst.loc[inst.set == "reales", "n"] = np.nan
rat = pd.DataFrame({k: (w[k] / w["raa_k0"]).values for k in KS}); rat = pd.concat([inst.reset_index(drop=True), rat], axis=1)

# (1) anchura relativa por k, por familia y por (n, rho) en synq
rows = []
for (s, n, rho), g in rat[rat.set == "sinteticas"].groupby(["set", "n", "rho"]):
    rows.append(dict(familia="synq", n=int(n), densidad=rho, filas=len(g), **{k[4:]: round(gm(g[k]), 4) for k in KS}))
for s, g in rat[rat.set != "sinteticas"].groupby("set"):
    rows.append(dict(familia=s, n=None, densidad=None, filas=len(g), **{k[4:]: round(gm(g[k]), 4) for k in KS}))
anch = pd.DataFrame(rows); anch.to_csv(os.path.join(a.out, "anchura_por_k.csv"), index=False)
print("== anchura afin / RAA k=0 por k (media geometrica)"); print(anch.to_string(index=False))

# (2) bloques por tamano con k=6 (lo que la busqueda encuentra cuando no se la limita) y con k=4
BS = ["b2", "b3", "b4", "b5", "b6", "b7p"]
rows = []
for kv in ["raa_k4", "raa_k6"]:
    sub = d[d.variant == kv].copy()
    sub["n"] = sub.instance.str.extract(r"_n(\d+)_").astype(float); sub["rho"] = sub.instance.str.extract(r"_d(\d+)_").astype(float) / 100
    for (s, n, rho), g in sub[sub.set == "sinteticas"].groupby(["set", "n", "rho"]):
        tot = g[BS].sum(); T = tot.sum()
        rows.append(dict(variante=kv, familia="synq", n=int(n), densidad=rho, bloques=int(T), **{b: round(tot[b] / T, 3) if T else np.nan for b in BS}, bloques_por_fila=round(T / len(g), 2)))
    for s, g in sub[sub.set != "sinteticas"].groupby("set"):
        tot = g[BS].sum(); T = tot.sum()
        rows.append(dict(variante=kv, familia=s, n=None, densidad=None, bloques=int(T), **{b: round(tot[b] / T, 3) if T else np.nan for b in BS}, bloques_por_fila=round(T / len(g), 2)))
bl = pd.DataFrame(rows); bl.to_csv(os.path.join(a.out, "bloques_por_tamano.csv"), index=False)
print("\n== fraccion de bloques por tamano"); print(bl.to_string(index=False))

# (3) nivel 2 por configuracion: mejor k en CPU y en celdas
cfg = pd.read_csv(a.config)
cfg = cfg[cfg.fuerza_diag == "normal"].groupby(["n", "densidad"]).agg(resueltas=("resueltas_por_las_4", "sum"), **{f"{m}_{k}": (f"{m}_gm_raa_{k}", "mean") for m in ("celdas", "cpu") for k in ("k2", "k3", "k4")}).reset_index()
cfg["mejor_k_cpu"] = cfg[["cpu_k2", "cpu_k3", "cpu_k4"]].idxmin(axis=1).str[-2:]
cfg["mejor_k_celdas"] = cfg[["celdas_k2", "celdas_k3", "celdas_k4"]].idxmin(axis=1).str[-2:]
cfg = cfg.round(3); cfg.to_csv(os.path.join(a.out, "nivel2_por_config.csv"), index=False)
print("\n== nivel 2 (sesion 0009) por (n, densidad)"); print(cfg.to_string(index=False))

# (4) por instancia: clique disponible vs ganancia marginal k3->k4 en celdas y CPU
cl = pd.read_csv(a.cliques); t = pd.read_csv(a.tabla); t = t[t.set == "sinteticas"].copy(); t["instance"] = t.instancia
m = t.merge(cl, on="instance")
ok = m[(m.art_raa_k0_estado == "SUCCESS") & (m.art_raa_k3_estado == "SUCCESS") & (m.art_raa_k4_estado == "SUCCESS")].copy()
ok["k4_vs_k3_celdas"] = ok.art_raa_k4_celdas / ok.art_raa_k3_celdas; ok["k4_vs_k3_cpu"] = ok.art_raa_k4_cpu / ok.art_raa_k3_cpu
ok["k3_vs_k2_celdas"] = ok.art_raa_k3_celdas / ok.art_raa_k2_celdas
ok["clase_ge4"] = pd.cut(ok.frac_ge4, [-0.01, 0.0, 0.3, 0.6, 1.0], labels=["0", "0-0.3", "0.3-0.6", "0.6-1"])
print("\n== ganancia k3->k4 segun la fraccion de productos con clique >= 4")
print(ok.groupby("clase_ge4", observed=True).agg(instancias=("instance", "size"), k4_vs_k3_celdas_gm=("k4_vs_k3_celdas", gm), k4_vs_k3_cpu_gm=("k4_vs_k3_cpu", gm), clique_medio=("clique_medio", "mean")).round(3).to_string())
ok[["instance", "n", "densidad", "diagonal", "clique_medio", "clique_max", "frac_ge3", "frac_ge4", "frac_ge5", "k3_vs_k2_celdas", "k4_vs_k3_celdas", "k4_vs_k3_cpu"]].round(3).to_csv(os.path.join(a.out, "mejor_k_por_instancia.csv"), index=False)
print("correlacion (Spearman) frac_ge4 vs k4_vs_k3_celdas:", round(ok[["frac_ge4", "k4_vs_k3_celdas"]].corr(method="spearman").iloc[0, 1], 3), "| clique_medio vs k4_vs_k3_celdas:", round(ok[["clique_medio", "k4_vs_k3_celdas"]].corr(method="spearman").iloc[0, 1], 3))

# figura 1: anchura relativa por k, una linea por n (synq, media sobre densidades), eje lineal
fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.9))
ax = axs[0]; ks = [2, 3, 4, 5, 6]
for i, n in enumerate([3, 5, 8, 10]):
    g = rat[(rat.set == "sinteticas") & (rat.n == n)]
    ax.plot(ks, [gm(g[f"raa_k{k}"]) for k in ks], marker="o", color=vz.SLOTS[i], label=f"n={n}")
for s, lab, c in [("reales", "reales ex6_2_*", "#555"), ("sinteticas-log", "synl", "#999"), ("sinteticas-fun", "synt", "#bbb")]:
    g = rat[rat.set == s]
    ax.plot(ks, [gm(g[f"raa_k{k}"]) for k in ks], marker="s", ls="--", color=c, label=lab)
ax.set_xticks(ks); ax.set_xlabel("k maximo"); ax.set_ylabel("anchura afin / RAA k=0 (media geom.)"); ax.set_title("Nivel 1: que gana cada k adicional", fontsize=10); ax.legend(fontsize=8, ncol=2)
ax = axs[1]
sub = bl[(bl.variante == "raa_k6") & (bl.familia == "synq")].groupby("n")[BS].mean()
bottom = np.zeros(len(sub)); x = np.arange(len(sub))
for j, b in enumerate(BS):
    ax.bar(x, sub[b].values, bottom=bottom, color=vz.SLOTS[j], label={"b2": "2", "b3": "3", "b4": "4", "b5": "5", "b6": "6", "b7p": "7+"}[b]); bottom += sub[b].values
ax.set_xticks(x); ax.set_xticklabels([f"n={int(n)}" for n in sub.index]); ax.set_ylabel("fraccion de bloques"); ax.set_title("Tamano de los bloques que extrae la busqueda con k=6 (synq)", fontsize=10); ax.legend(title="simbolos", fontsize=8, ncol=3)
fig.savefig(os.path.join(a.out, "k_nivel1.png"), bbox_inches="tight"); plt.close(fig)

# figura 2: nivel 2, CPU k/k0 por (n, densidad), una linea por densidad y panel por n
fig, axs = plt.subplots(1, 4, figsize=(12, 3.4), sharey=True)
for ax, n in zip(axs, [3, 5, 8, 10]):
    for i, rho in enumerate([0.2, 0.5, 0.9]):
        r = cfg[(cfg.n == n) & (cfg.densidad == rho)]
        if len(r) and r.resueltas.iloc[0] > 0:
            ax.plot([2, 3, 4], [r.cpu_k2.iloc[0], r.cpu_k3.iloc[0], r.cpu_k4.iloc[0]], marker="o", color=vz.SLOTS[i], label=f"densidad {rho} ({int(r.resueltas.iloc[0])} inst.)")
            ax.plot([2, 3, 4], [r.celdas_k2.iloc[0], r.celdas_k3.iloc[0], r.celdas_k4.iloc[0]], marker="", ls=":", color=vz.SLOTS[i])
    ax.axhline(1.0, color="#777", lw=0.8, ls="--"); ax.set_xticks([2, 3, 4]); ax.set_title(f"n={n}", fontsize=10); ax.set_xlabel("k"); ax.legend(fontsize=7, loc="lower left")
axs[0].set_ylabel("CPU k / CPU RAA k=0 (linea); celdas (punteada)"); fig.suptitle("Nivel 2 (sesion 0009, synq): el mejor k por tamano y densidad", fontsize=10)
fig.savefig(os.path.join(a.out, "k_nivel2.png"), bbox_inches="tight"); plt.close(fig)
print("\nfiguras en", a.out)
