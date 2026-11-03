"""[raak local] Tiempos de linealizacion (to-do 21-10): microsegundos por evaluacion afin de cada variante,
a partir de la columna `us` de un range.csv de tests/range_eval.cpp (una fila por instancia, funcion, caja, variante).
Debe medirse con la maquina en reposo (sin barridos en paralelo).

Produce en <out>: tiempos_por_n.csv (media y mediana de us por variante y n), tiempos_relativos.csv (us variante / us raa_k0),
tiempos_por_n.png (eje lineal). Opcionalmente cruza con k_used para estimar el costo por operacion k-nomial.
uso: python analysis/tiempos_linealizacion.py <range.csv> --out DIR [--set sinteticas]
"""
import sys, os, argparse
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))
import vizstyle as vz
import matplotlib.pyplot as plt
vz.setup()

ap = argparse.ArgumentParser()
ap.add_argument("range_csv"); ap.add_argument("--out", required=True); ap.add_argument("--set")
args = ap.parse_args(); os.makedirs(args.out, exist_ok=True)

d = pd.read_csv(args.range_csv)
if args.set: d = d[d.set == args.set]
d = d[d.active == 1]
d["n_inst"] = d.instance.str.extract(r"n(\d+)").astype(float)
VARS = [v for v in ["af2_k0", "af2_k3", "raa_k0", "raa_k2", "raa_k3", "raa_k4", "aa_k0", "aa_k3"] if v in set(d.variant)]
LABEL = {"af2_k0": "AF2", "af2_k3": "AF2 k=3", "raa_k0": "RAA k=0", "raa_k2": "RAA k=2", "raa_k3": "RAA k=3", "raa_k4": "RAA k=4", "aa_k0": "AA", "aa_k3": "AA k=3"}

# por n: media y mediana de us
key = ["set", "instance", "func", "box_id"]
us = d.pivot_table(index=key, columns="variant", values="us").dropna()
ku = d.pivot_table(index=key, columns="variant", values="k_used").reindex(us.index)
nvar = d.drop_duplicates(key).set_index(key).n.reindex(us.index)
g = us.copy(); g["n"] = nvar.values
por_n = g.groupby("n")[VARS].agg(["mean", "median"]).round(1)
por_n.to_csv(os.path.join(args.out, "tiempos_por_n.csv"))
rel = (us[VARS].div(us["raa_k0"], axis=0)).assign(n=nvar.values).groupby("n")[VARS].median().round(2)
rel.to_csv(os.path.join(args.out, "tiempos_relativos.csv"))
# costo por operacion k-nomial: (us_k - us_k0) / k_used_k, mediana donde k_used > 0
costo = {}
for v in ["raa_k2", "raa_k3", "raa_k4"]:
    if v in us:
        m = ku[v] > 0
        costo[v] = float(((us.loc[m, v] - us.loc[m, "raa_k0"]) / ku.loc[m, v]).median()) if m.any() else float("nan")
pd.Series(costo, name="us_por_operacion_knomial_mediana").to_csv(os.path.join(args.out, "costo_por_operacion.csv"))

# figura: us medio por variante y n, lineal
fig, ax = plt.subplots(figsize=(9, 4.3))
ns = sorted(g.n.unique()); x = np.arange(len(ns)); wdt = 0.8 / len(VARS)
colors = {"af2_k0": vz.VARIANT_COLOR["af2_k0"], "af2_k3": vz.VARIANT_COLOR["af2_k3"], "raa_k0": vz.VARIANT_COLOR["raa_k0"], "raa_k2": vz.SLOTS[6], "raa_k3": vz.VARIANT_COLOR["raa_k3"], "raa_k4": vz.SLOTS[7], "aa_k0": vz.VARIANT_COLOR["aa_k0"], "aa_k3": vz.VARIANT_COLOR["aa_k3"]}
for i, v in enumerate(VARS):
    ax.bar(x + (i - len(VARS) / 2 + 0.5) * wdt, [por_n.loc[n, (v, "mean")] for n in ns], width=wdt, color=colors[v], label=LABEL[v])
ax.set_xticks(x); ax.set_xticklabels([f"n={int(n)}" for n in ns]); ax.set_ylabel("microsegundos por evaluacion afin (media)"); ax.legend(ncol=2, fontsize=8, loc="upper left")
ax.set_title("Tiempo de una evaluacion afin (objetivo o restriccion sobre una caja), por variante y tamano", fontsize=10)
fig.savefig(os.path.join(args.out, "tiempos_por_n.png"), bbox_inches="tight"); plt.close(fig)
print(por_n.xs("mean", axis=1, level=1).to_string()); print("\nrelativo a raa_k0 (mediana):"); print(rel.to_string()); print("\ncosto por operacion k-nomial (us, mediana):", {k: round(v, 2) for k, v in costo.items()})
