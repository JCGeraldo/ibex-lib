"""[raak local] Figuras del parche 0009 (29-10-2026):
  sobrecosto_por_evaluacion.png  us por evaluacion afin relativo a RAA k=0 (mediana), antes (28-10) y despues del parche, por n.
  cpu_vs_celdas.png              nivel 2 en una sesion: cociente de CPU frente a cociente de celdas (k/k0) por instancia synq.
uso: python analysis/parche0009_figuras.py <tiempos_relativos_antes.csv> <tiempos_relativos_despues.csv> <tabla_raa_baseline.csv> --out DIR
"""
import sys, os, argparse
sys.dont_write_bytecode = True
import numpy as np, pandas as pd
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))
import vizstyle as vz
import matplotlib.pyplot as plt
vz.setup()
ap = argparse.ArgumentParser(); ap.add_argument("antes"); ap.add_argument("despues"); ap.add_argument("tabla"); ap.add_argument("--out", required=True)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
ra = pd.read_csv(a.antes, index_col=0); rd = pd.read_csv(a.despues, index_col=0)
VARS = ["raa_k2", "raa_k3", "raa_k4"]; LAB = {"raa_k2": "k=2", "raa_k3": "k=3", "raa_k4": "k=4"}
COL = {"raa_k2": vz.SLOTS[6], "raa_k3": vz.VARIANT_COLOR["raa_k3"], "raa_k4": vz.SLOTS[7]}
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, (t, r) in zip(axs, [("Antes del parche (28-10)", ra), ("Con el parche 0009 (29-10)", rd)]):
    ns = list(r.index); x = np.arange(len(ns)); w = 0.26
    for i, v in enumerate(VARS):
        ax.bar(x + (i - 1) * w, r[v].values, width=w, color=COL[v], label=LAB[v])
        for xi, val in zip(x + (i - 1) * w, r[v].values): ax.text(xi, val + 0.01, f"{val:.2f}", ha="center", va="bottom", fontsize=7)
    ax.axhline(1.0, color="#777", lw=0.8, ls="--"); ax.set_xticks(x); ax.set_xticklabels([f"n={int(n)}" for n in ns]); ax.set_title(t, fontsize=10)
axs[0].set_ylabel("tiempo por evaluacion / RAA k=0 (mediana)"); axs[1].legend(fontsize=8, loc="upper left"); axs[0].set_ylim(0, 1.65)
fig.suptitle("Sobrecosto del k-nomial por evaluacion afin (nivel 1, synq, maquina en reposo)", fontsize=10)
fig.savefig(os.path.join(a.out, "sobrecosto_por_evaluacion.png"), bbox_inches="tight"); plt.close(fig)

t = pd.read_csv(a.tabla)
print(t.columns.tolist()[:30])
ok = t[(t.set != "reales")]
for v in ["art_raa_k2", "art_raa_k3", "art_raa_k4"]:
    ok = ok[ok[v + "_estado"] == "SUCCESS"]
ok = ok[ok.art_raa_k0_estado == "SUCCESS"]
fig, ax = plt.subplots(figsize=(5.2, 4.6))
for v, m in [("art_raa_k2", "s"), ("art_raa_k3", "o"), ("art_raa_k4", "^")]:
    xr = ok[v + "_celdas"] / ok.art_raa_k0_celdas; yr = ok[v + "_cpu"] / ok.art_raa_k0_cpu
    ax.scatter(xr, yr, s=22, marker=m, color=COL[v[4:]], alpha=0.8, label=f"RAA {LAB[v[4:]]} ({len(ok)} instancias)", edgecolor="white", lw=0.4)
lim = (0.0, 1.45); ax.plot(lim, lim, color="#777", lw=0.8, ls="--"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("celdas k / celdas RAA k=0"); ax.set_ylabel("CPU k / CPU RAA k=0"); ax.legend(fontsize=8, loc="upper left")
ax.set_title("Con el parche 0009 la CPU sigue a las celdas (synq, una sesion)", fontsize=10)
fig.savefig(os.path.join(a.out, "cpu_vs_celdas.png"), bbox_inches="tight"); plt.close(fig)
print("figuras en", a.out, "| instancias en cpu_vs_celdas:", len(ok))
