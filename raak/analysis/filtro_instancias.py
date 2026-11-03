"""[raak local] Filtro de instancias: cuales tienen "material" para RAA y para el k-nomial (To-Do, puntos 5 y 6).

Entrada: un range.csv de tests/range_eval.cpp (nivel 1: anchura de la forma afin de cada funcion sobre la
caja inicial y sub-cajas, para las seis variantes) sobre los conjuntos actuales (easy, medium, hard, others)
y los 89 de coconutbenchmark-library2 (carpeta All del escritorio, no estan en benchs/optim).
Opcional: el CSV del conteo estatico (contar_multiplicaciones.py) y la tabla del nivel 2 (10-raa-baseline)
para contrastar el indicador con el efecto real en el solver.

Por instancia, sobre las (funcion, caja) donde las seis formas son activas y finitas:
  sobre_raa      media geom. de w_aff(raa_k0) / w_sample: cuanto sobreestima la base (1 = exacto)
  raa_vs_af2     media geom. de w_aff(raa_k0) / w_aff(af2_k0): lo que gana la RAA sola
  kn_raa         media geom. de w_aff(raa_k3) / w_aff(raa_k0): lo que gana el k-nomial sobre RAA
  kn_af2, kn_aa  idem sobre AF2 y sobre AA
  frac_kn        fraccion de (funcion, caja) donde el k-nomial estrecha mas de 1 %
  k_used_raa3    operaciones en las que raa_k3 reemplazo la cota base (suma)
Clasificacion: 'knomial' si kn_raa < 0.99 o frac_kn >= 0.10; 'raa' si solo raa_vs_af2 < 0.99; 'nada' en otro caso.

uso: python analysis/filtro_instancias.py <range.csv> [--estatico conteo.csv] [--nivel2 tabla_raa_baseline.csv] [--out DIR]
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
ap.add_argument("range_csv"); ap.add_argument("--estatico"); ap.add_argument("--nivel2")
ap.add_argument("--out", default=os.path.join(REPO, "results", "11-filtro-instancias"))
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)


def gm(x):
    x = np.asarray(x, float); x = x[np.isfinite(x) & (x > 0)]
    return float(np.exp(np.log(x).mean())) if len(x) else float("nan")


d = pd.read_csv(args.range_csv)
d = d[(d.active == 1) & np.isfinite(d.w_aff) & (d.w_aff > 0)]
w = d.pivot_table(index=["set", "instance", "func", "box_id"], columns="variant", values="w_aff")
ku = d.pivot_table(index=["set", "instance", "func", "box_id"], columns="variant", values="k_used")
ws = d[d.variant == "raa_k0"].set_index(["set", "instance", "func", "box_id"]).w_sample
VARS = ["af2_k0", "af2_k3", "raa_k0", "raa_k3", "aa_k0", "aa_k3"]
w = w.dropna(subset=VARS)
ku = ku.loc[w.index]; ws = ws.loc[w.index]

rows = []
for (s, inst), g in w.groupby(level=[0, 1]):
    k = ku.loc[g.index]
    kn = g["raa_k3"] / g["raa_k0"]
    rows.append({
        "set": s, "instancia": inst, "funciones": g.index.get_level_values("func").nunique(), "cajas_func": len(g),
        "sobre_raa": gm(g["raa_k0"] / ws.loc[g.index]),
        "raa_vs_af2": gm(g["raa_k0"] / g["af2_k0"]), "frac_raa": float((g["raa_k0"] / g["af2_k0"] < 0.99).mean()),
        "kn_raa": gm(kn), "frac_kn": float((kn < 0.99).mean()), "kn_min": float(kn.min()),
        "kn_af2": gm(g["af2_k3"] / g["af2_k0"]), "kn_aa": gm(g["aa_k3"] / g["aa_k0"]),
        "k_used_raa0": int(k["raa_k0"].sum()), "k_used_raa3": int(k["raa_k3"].sum()), "k_used_aa3": int(k["aa_k3"].sum()),
    })
t = pd.DataFrame(rows)
clipped = d[d.variant == "raa_k0"].groupby(["set", "instance"]).clipped.max().rename("vars_no_acotadas").reset_index().rename(columns={"instance": "instancia"})
t = t.merge(clipped, on=["set", "instancia"], how="left")


def clase(r):
    if r.kn_raa < 0.99 or r.frac_kn >= 0.10: return "knomial"
    if r.raa_vs_af2 < 0.99: return "raa"
    return "nada"


t["clase"] = t.apply(clase, axis=1)

if args.estatico:
    e = pd.read_csv(args.estatico); e["instancia"] = e.archivo.str.replace(".bch", "", regex=False)
    e = e[["instancia", "n_vars", "mult_comp", "mult_vv", "sqr_comp", "sqr_var", "div_nc", "trig", "explog"]].drop_duplicates("instancia")
    t = t.merge(e, on="instancia", how="left")
if args.nivel2:
    n2 = pd.read_csv(args.nivel2)
    n2 = n2[["set", "instancia", "art_raa_k0_estado", "art_raa_k0_celdas", "art_raa_k3_celdas_ratio", "k3_con_bloques"]].rename(
        columns={"art_raa_k0_estado": "n2_estado", "art_raa_k0_celdas": "n2_celdas_base", "art_raa_k3_celdas_ratio": "n2_ratio_k3", "k3_con_bloques": "n2_con_bloques"})
    t = t.merge(n2, on=["set", "instancia"], how="left")

t["o"] = t.set.map({"easy": 0, "medium": 1, "hard": 2, "others": 3, "coconut": 4})
t = t.sort_values(["kn_raa", "raa_vs_af2"]).reset_index(drop=True)
t.drop(columns="o").to_csv(os.path.join(args.out, "tabla_instancias.csv"), index=False)

# ---------------- resumen por conjunto
res = t.groupby("set").agg(n=("instancia", "size"), knomial=("clase", lambda c: (c == "knomial").sum()), raa=("clase", lambda c: (c == "raa").sum()), nada=("clase", lambda c: (c == "nada").sum()),
                           con_k_used=("k_used_raa3", lambda x: (x > 0).sum()), kn_raa_gm=("kn_raa", gm), raa_vs_af2_gm=("raa_vs_af2", gm))
orden = ["easy", "medium", "hard", "others", "coconut"]; res = res.reindex(orden + [s for s in res.index if s not in orden]).dropna(how="all")

# ---------------- figura: k-nomial y RAA por instancia, las 40 con mas efecto, eje lineal
top = t[t.clase != "nada"].sort_values("kn_raa").head(40)
fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(top))
ax.bar(x - 0.2, 1 - top.kn_raa, width=0.4, color=vz.VARIANT_COLOR["raa_k3"], label="k-nomial sobre RAA: 1 - w(raa k=3)/w(raa k=0)")
ax.bar(x + 0.2, 1 - top.raa_vs_af2, width=0.4, color=vz.VARIANT_COLOR["raa_k0"], label="RAA sobre AF2: 1 - w(raa k=0)/w(af2 k=0)")
ax.set_xticks(x); ax.set_xticklabels([f"{r.instancia} [{r.set[:3]}]" for r in top.itertuples()], rotation=60, ha="right", fontsize=7)
ax.set_ylabel("reduccion media de la anchura afin (lineal)"); ax.legend(loc="upper right")
ax.set_title(f"Nivel 1: las {len(top)} instancias con mas material (de {len(t)}: {int((t.clase=='knomial').sum())} con k-nomial, {int((t.clase=='raa').sum())} solo RAA, {int((t.clase=='nada').sum())} nada)", fontsize=10)
fig.savefig(os.path.join(args.out, "material_por_instancia.png"), bbox_inches="tight"); plt.close(fig)

# ---------------- figura: indicador nivel 1 vs efecto nivel 2 (si hay)
if args.nivel2 and t.n2_ratio_k3.notna().any():
    v = t[t.n2_ratio_k3.notna() & (t.n2_estado == "SUCCESS")]
    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.axhline(1, color=vz.TEXT2, linewidth=1); ax.axvline(1, color=vz.TEXT2, linewidth=1)
    ax.scatter(v.kn_raa, v.n2_ratio_k3, s=28, color=vz.VARIANT_COLOR["raa_k3"], alpha=0.8)
    for r in v[(v.kn_raa < 0.99) | (v.n2_ratio_k3 < 0.97) | (v.n2_ratio_k3 > 1.03)].itertuples():
        ax.annotate(r.instancia, (r.kn_raa, r.n2_ratio_k3), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("nivel 1: w(raa k=3) / w(raa k=0), media geom. por instancia"); ax.set_ylabel("nivel 2: celdas(raa k=3) / celdas(raa k=0)")
    ax.set_title("Nivel 1 frente a nivel 2, 147 instancias actuales", fontsize=10)
    fig.savefig(os.path.join(args.out, "nivel1_vs_nivel2.png"), bbox_inches="tight"); plt.close(fig)

# ---------------- README
L = ["# Filtro de instancias: donde tienen material RAA y el k-nomial (nivel 1)", "",
     "Generado por `analysis/filtro_instancias.py` desde `range.csv.gz` (tests/range_eval.cpp, sub-cajas 2, muestras 200) sobre los conjuntos",
     "actuales y las 89 instancias `coconutbenchmark-library2` de la carpeta `All` (no estan en `benchs/optim`; copia local en `~/ibex-local/instancias/coconut`).",
     "Por instancia se promedia (media geometrica) sobre todas las (funcion, caja) donde las seis formas son activas.",
     "", "| conjunto | instancias | con k-nomial | solo RAA | nada | con k_used>0 (raa k=3) | kn_raa media | raa_vs_af2 media |", "|---|---|---|---|---|---|---|---|"]
for s, r in res.iterrows():
    L.append(f"| {s} | {int(r.n)} | {int(r.knomial)} | {int(r.raa)} | {int(r.nada)} | {int(r.con_k_used)} | {r.kn_raa_gm:.3f} | {r.raa_vs_af2_gm:.3f} |")
L += ["", "`kn_raa` = anchura afin con k=3 / con k=0 dentro de RAA (menor es mejor); `raa_vs_af2` = RAA k=0 / AF2 k=0. Clase `knomial`: kn_raa < 0.99 o k-nomial estrecha >1 % en al menos 10 % de las (funcion, caja).", ""]
for s in ["coconut", "easy", "medium", "hard", "others"]:
    sub = t[(t.set == s) & (t.clase == "knomial")].sort_values("kn_raa")
    if len(sub) == 0: continue
    L += [f"## {s}: instancias con material para el k-nomial ({len(sub)})", "", "| instancia | kn_raa | frac_kn | k_used raa k=3 | raa_vs_af2 | sobre_raa | vars no acotadas" + (" | nivel 2: celdas k3/k0 |" if args.nivel2 else " |"), "|---|---|---|---|---|---|---|" + ("---|" if args.nivel2 else "")]
    for r in sub.itertuples():
        extra = f" {r.n2_ratio_k3 if pd.notna(r.n2_ratio_k3) else r.n2_estado if pd.notna(r.n2_estado) else '—'} |" if args.nivel2 else ""
        L.append(f"| {r.instancia} | {r.kn_raa:.3f} | {r.frac_kn:.2f} | {r.k_used_raa3} | {r.raa_vs_af2:.3f} | {r.sobre_raa:.2f} | {int(r.vars_no_acotadas)} |" + extra)
    L.append("")
L += ["| archivo | que es |", "|---|---|",
      "| `tabla_instancias.csv` | Todas las instancias con los indicadores del nivel 1, el conteo estatico y, para las 147 actuales, el cociente de celdas del nivel 2. |",
      "| `material_por_instancia.png` | Las 40 instancias con mas reduccion de anchura por el k-nomial (barra naranja) y por la RAA (verde), eje lineal. |",
      "| `nivel1_vs_nivel2.png` | Indicador del nivel 1 contra el efecto real en celdas del nivel 2, en las instancias ya corridas en el solver. |",
      "| `range.csv.gz`, `meta.txt`, `range_log.txt` | La corrida del nivel 1 (236 instancias, 6 variantes). |"]
with open(os.path.join(args.out, "README.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(res.to_string()); print("salida:", args.out)
