"""[raak local] RAA k=0 como linea base: k-nomial k=2, k=3 (y k=4 con --cmp) frente a ella, relajacion art, escalas lineales.

Responde al To-Do posterior al informe del 05-10: art (AF2) se archiva, la referencia pasa a ser RAA k=0,
y se comparan contra ella las tecnicas bilineales / k-nomiales (k=2, k=3). Celdas es la metrica principal;
la CPU se reporta como secundaria. Todos los ejes son lineales (antes: log-log).

Datos: etapas B y D de la Fase 3 (easy+medium y hard+others, --lr=art, -t 1800) y la corrida de k=2 del 05-10.
Produce en results/10-raa-baseline/: tabla por instancia (CSV, con los contadores RAA-K de la corrida k=3),
resumen (JSON), tres figuras y un README. Uso: python analysis/raa_baseline.py
"""
import sys, os, json, re, argparse
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # raak/
RES = os.path.join(REPO, "results", "07-fase3-nivel2-solver")
ap = argparse.ArgumentParser()
ap.add_argument("--runs", nargs="*", help="runs.csv a usar (por defecto: etapas B y D de la fase 3 + corrida k=2)")
ap.add_argument("--out", default=os.path.join(REPO, "results", "10-raa-baseline"))
ap.add_argument("--titulo", default="Relajacion art")
ap.add_argument("--cmp", default="art_raa_k2,art_raa_k3", help="variantes a comparar contra la base, separadas por coma (p. ej. art_raa_k2,art_raa_k3,art_raa_k4)")
ap.add_argument("--grupos", default="easy+medium:easy,medium;hard+others:hard,others", help="grupo:set1,set2;... (vacio = un grupo por set)")
args = ap.parse_args()
OUT = args.out
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "analysis"))
import vizstyle as vz
import matplotlib.pyplot as plt
vz.setup()

BASE = "art_raa_k0"
CMP = [v.strip() for v in args.cmp.split(",") if v.strip()]
VARS = [BASE] + CMP
LABEL = {BASE: "RAA k=0 (base)", "art_raa_k2": "RAA k=2 (binomial)", "art_raa_k3": "RAA k=3 (k-nomial)", "art_raa_k4": "RAA k=4 (k-nomial)"}
COLOR = {BASE: vz.VARIANT_COLOR["raa_k0"], "art_raa_k2": vz.SLOTS[1], "art_raa_k3": vz.VARIANT_COLOR["raa_k3"], "art_raa_k4": vz.SLOTS[7]}
MARK = {"art_raa_k2": "+", "art_raa_k3": "x", "art_raa_k4": "^"}
STYLE = {BASE: "-", "art_raa_k2": "-.", "art_raa_k3": "--", "art_raa_k4": ":"}
KS = ", ".join(v.rsplit("k", 1)[1] for v in CMP)  # "2, 3" o "2, 3, 4"
NV = {3: "las tres", 4: "las cuatro"}.get(len(VARS), f"las {len(VARS)}")

# ---------------- datos
GRUPOS = {}
if args.grupos:
    for g in args.grupos.split(";"):
        nombre, sets = g.split(":"); GRUPOS.update({st: nombre for st in sets.split(",")})
def grupo_de_set(st): return GRUPOS.get(st, st)

frames = []
if args.runs:
    for f in args.runs:
        r = pd.read_csv(f); frames.append(r)
else:
    for folder in ["fase3-20260921/B_easy_medium_art", "fase3-20260921/D_hard_others_art", "fase3-k2-20261005/art_raa_k2"]:
        frames.append(pd.read_csv(os.path.join(RES, folder, "runs.csv")))
d = pd.concat(frames)
d = d[d.variante.isin(VARS)].copy()
d["set"] = d.instancia.str.split("/").str[0]
d["inst"] = d.instancia.str.split("/").str[1]
d["grupo"] = d.set.map(grupo_de_set)
GRUPO_LIST = list(dict.fromkeys(d.grupo)) + ["todas"]


def parse_stats(s):
    out = {}
    for m in re.finditer(r"(\w+)=([-\d.eE+]+)", str(s)):
        try: out[m.group(1)] = float(m.group(2))
        except ValueError: pass
    return out


def gm(x):
    x = np.asarray(x, float); x = x[np.isfinite(x) & (x > 0)]
    return float(np.exp(np.log(x).mean())) if len(x) else float("nan")


ok = d[d.estado == "SUCCESS"]
cells = ok.pivot_table(index="instancia", columns="variante", values="celdas")
cpu = ok.pivot_table(index="instancia", columns="variante", values="cpu_s")
grupo_de = d.drop_duplicates("instancia").set_index("instancia").grupo

# ---------------- tabla por instancia (+ contadores RAA-K de la corrida k=3)
STAT_COLS = ["productos", "con_bloques", "bloques", "usados", "cuadrados", "cuadrados_usados", "corner_products", "corner_used"]
rows = []
for inst, g in d.groupby("instancia", sort=False):
    row = {"grupo": g.grupo.iloc[0], "set": g.set.iloc[0], "instancia": g.inst.iloc[0]}
    for v in VARS:
        s = g[g.variante == v]
        if len(s) == 0:
            row[f"{v}_estado"] = "SIN_DATO"; row[f"{v}_celdas"] = ""; row[f"{v}_cpu"] = ""
        else:
            s = s.iloc[0]; row[f"{v}_estado"] = s.estado
            row[f"{v}_celdas"] = "" if pd.isna(s.celdas) else int(s.celdas)
            row[f"{v}_cpu"] = "" if pd.isna(s.cpu_s) else round(float(s.cpu_s), 4)
    for v in CMP:
        a, b = row[f"{v}_celdas"], row[f"{BASE}_celdas"]
        row[f"{v}_celdas_ratio"] = round(a / b, 4) if a != "" and b not in ("", 0) and row[f"{v}_estado"] == "SUCCESS" and row[f"{BASE}_estado"] == "SUCCESS" else ""
    s3 = g[g.variante == "art_raa_k3"]
    st = parse_stats(s3.raak_stats.iloc[0]) if len(s3) else {}
    for c in STAT_COLS: row[f"k3_{c}"] = int(st.get(c, 0))
    rows.append(row)
tab = pd.DataFrame(rows)
tab["o"] = tab.set.map({"easy": 0, "medium": 1, "hard": 2, "others": 3}).fillna(9)
tab = tab.sort_values(["o", "set", "instancia"]).drop(columns="o")
tab.to_csv(os.path.join(OUT, "tabla_raa_baseline.csv"), index=False)

# ---------------- resumen
resumen = {}
for grupo in GRUPO_LIST:
    idx = cells.index if grupo == "todas" else cells.index[grupo_de.loc[cells.index] == grupo]
    n_inst = int(d.instancia.nunique()) if grupo == "todas" else int(d[d.grupo == grupo].instancia.nunique())
    fila = {"n_instancias": n_inst, "resueltas_base": int(cells.loc[idx, BASE].notna().sum())}
    for v in CMP:
        both = cells.loc[idx][[v, BASE]].dropna()
        rc = both[v] / both[BASE]; rt = cpu.loc[both.index, v] / cpu.loc[both.index, BASE]
        fila[v] = {"resueltas": int(cells.loc[idx, v].notna().sum()), "comparables": int(len(both)),
                   "celdas_identicas": int((both[v] == both[BASE]).sum()),
                   "celdas_gm": gm(rc), "celdas_gana": int((rc < 0.95).sum()), "celdas_empata": int(((rc >= 0.95) & (rc <= 1.05)).sum()), "celdas_pierde": int((rc > 1.05).sum()),
                   "celdas_total_base": float(both[BASE].sum()), "celdas_total": float(both[v].sum()),
                   "cpu_gm": gm(rt), "cpu_gana": int((rt < 0.95).sum()), "cpu_empata": int(((rt >= 0.95) & (rt <= 1.05)).sum()), "cpu_pierde": int((rt > 1.05).sum()),
                   "cpu_total_base_s": float(cpu.loc[both.index, BASE].sum()), "cpu_total_s": float(cpu.loc[both.index, v].sum())}
    both = cells.loc[idx][CMP].dropna()
    for a, b in zip(CMP[1:], CMP[:-1]):   # k3 vs k2, k4 vs k3
        fila[f"{a[8:]}_vs_{b[8:]}"] = {"comparables": int(len(both)), "celdas_identicas": int((both[a] == both[b]).sum()),
                                       "celdas_gm": gm(both[a] / both[b]), "celdas_gana": int(((both[a] / both[b]) < 0.95).sum()), "celdas_pierde": int(((both[a] / both[b]) > 1.05).sum())}
    resumen[grupo] = fila

# instancias donde k=2 o k=3 cambian las celdas respecto de la base (fuera de +-0)
allv = cells[VARS].dropna()
chg = allv[np.logical_or.reduce([(allv[v] != allv[BASE]).values for v in CMP])].copy()
for v in CMP: chg["r" + v[-1]] = chg[v] / chg[BASE]
chg = chg.sort_values(BASE)
resumen["instancias_que_cambian"] = [
    {"instancia": i, "base": int(r[BASE]), **{"k" + v[-1]: int(r[v]) for v in CMP}, **{"ratio_k" + v[-1]: float(r["r" + v[-1]]) for v in CMP},
     "k3_con_bloques": int(tab.set_index(tab.set + "/" + tab.instancia).loc[i, "k3_con_bloques"])}
    for i, r in chg.iterrows()]
# donde el k-nomial encontro bloques (k=3), tenga o no efecto en celdas
tb = tab.set_index(tab.set + "/" + tab.instancia)
resumen["instancias_con_bloques_k3"] = [{"instancia": i, "productos": int(r.k3_productos), "con_bloques": int(r.k3_con_bloques), "bloques": int(r.k3_bloques), "usados": int(r.k3_usados)}
                                        for i, r in tb[tb.k3_con_bloques > 0].sort_values("k3_con_bloques", ascending=False).iterrows()]
est = d[d.estado != "SUCCESS"].groupby(["instancia", "estado"]).variante.apply(lambda s: ",".join(sorted(s))).reset_index()
resumen["no_success"] = est.to_dict(orient="records")
with open(os.path.join(OUT, "resumen.json"), "w", encoding="utf-8") as f:
    json.dump(resumen, f, ensure_ascii=False, indent=1)

n_ok = len(allv)

# ---------------- figura 1: dispersion lineal, k=2 y k=3 frente a RAA k=0 (completa y recorte)
fig, axes = plt.subplots(2, 2, figsize=(10.5, 9))
for col, (tbl, lab) in enumerate([(cells, "celdas"), (cpu, "CPU (s)")]):
    both = tbl[VARS].dropna()
    for row, q in enumerate([1.0, 0.9]):
        ax = axes[row, col]
        hi = float(both.max().max()) * 1.05 if q == 1.0 else float(np.quantile(both[BASE], q)) * 1.05
        for v in CMP:
            ax.scatter(both[BASE], both[v], s=30, color=COLOR[v], marker=MARK[v], label=LABEL[v], alpha=0.85, zorder=4, linewidths=1.3)
        ax.plot([0, hi], [0, hi], color=vz.TEXT2, linewidth=1, zorder=2)
        ax.set_xlim(0, hi); ax.set_ylim(0, hi)
        ax.set_xlabel(f"RAA k=0: {lab}"); ax.set_ylabel(f"RAA k={KS.replace(', ', ' / ')}: {lab}")
        ax.set_title(("todas las instancias" if q == 1.0 else f"recorte: base <= percentil {int(q*100)}") + f" ({lab})", fontsize=10)
axes[0, 0].legend(loc="upper left")
fig.suptitle(f"{args.titulo}: k-nomial frente a la base RAA k=0, por instancia ({n_ok} resueltas por {NV}). Ejes lineales; debajo de la diagonal, mejor que la base", y=1.0)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "dispersion_raa_baseline.png"), bbox_inches="tight"); plt.close(fig)


# ---------------- figura 2: perfiles de desempeno con eje x lineal
def perf_profile(ax, table, xlabel):
    best = table.min(axis=1); ratios = table.div(best, axis=0)
    finite = float(ratios.replace([np.inf], np.nan).max().max())
    taus = np.linspace(1.0, max(finite, 1.5) * 1.05, 400)
    for v in table.columns:
        rr = np.nan_to_num(ratios[v].values, nan=np.inf)
        ax.step(taus, [(rr <= t).mean() for t in taus], where="post", color=COLOR[v], label=LABEL[v], linestyle=STYLE[v])
    ax.set_xlabel(xlabel); ax.set_ylabel("fraccion de instancias"); ax.set_ylim(0, 1.02); ax.set_xlim(1.0, taus[-1])


c = cells[VARS]; c = c[c.notna().any(axis=1)]
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
perf_profile(axes[0], c, "celdas / celdas de la mejor (lineal)")
perf_profile(axes[1], cpu.loc[c.index, VARS], "CPU / CPU de la mejor (lineal)")
axes[0].set_title("nodos del B&B (celdas): metrica principal"); axes[1].set_title("tiempo de CPU: secundaria")
axes[1].legend(loc="lower right")
fig.suptitle(f"Perfiles de desempeno, {args.titulo}: RAA k=0 y k={KS} ({len(c)} instancias resueltas por alguna; limite 1800 s)", y=1.0)
fig.savefig(os.path.join(OUT, "perfiles_raa_baseline.png"), bbox_inches="tight"); plt.close(fig)

# ---------------- figura 3: cociente por instancia (solo donde algo cambia), eje lineal
fig, ax = plt.subplots(figsize=(10.5, 4.3))
if len(chg):
    x = np.arange(len(chg))
    ax.axhline(1.0, color=vz.TEXT2, linewidth=1)
    wdt = 0.8 / len(CMP)
    for i, v in enumerate(CMP):
        ax.bar(x + (i - len(CMP) / 2 + 0.5) * wdt, chg["r" + v[-1]], width=wdt, color=COLOR[v], label=LABEL[v])
    if len(chg) <= 30:
        ax.set_xticks(x); ax.set_xticklabels([f"{i.split('/')[1]} ({int(b)})" for i, b in zip(chg.index, chg[BASE])], rotation=30, ha="right", fontsize=8)
        ax.set_xlabel("instancia (celdas de RAA k=0)")
    else:
        ax.set_xticks([]); ax.set_xlabel(f"{len(chg)} instancias ordenadas por celdas de RAA k=0, de {int(chg[BASE].min())} a {int(chg[BASE].max())} (nombres en tabla_raa_baseline.csv)")
    ax.set_ylabel("celdas / celdas de RAA k=0"); ax.legend(loc="upper left")
    ax.set_title(f"Instancias cuyas celdas cambian con el k-nomial: {len(chg)} de {n_ok}; las otras {n_ok - len(chg)} son identicas a la base", fontsize=10)
fig.savefig(os.path.join(OUT, "cociente_por_instancia.png"), bbox_inches="tight"); plt.close(fig)

# ---------------- README
t = resumen["todas"]
def f3(x): return f"{x:.3f}"
lines = [
    "# RAA k=0 como linea base (relajacion `art`, escalas lineales)",
    "",
    "Generado por `analysis/raa_baseline.py` a partir de: " + (", ".join(os.path.relpath(f, REPO) for f in args.runs) if args.runs else "`07-fase3-nivel2-solver/` (etapas B y D, mas la corrida k=2 del 05-10)") + ".",
    "`art` (AF2) queda archivado: la referencia es **RAA k=0** y contra ella se miden las tecnicas k-nomiales k=" + KS + " (k=2 es el binomial del paper [B]).",
    "Celdas = nodos del B&B, metrica principal; CPU secundaria (una sola corrida por configuracion, sin repeticiones).",
    "",
    "| comparacion | instancias comparables | celdas identicas | media geom. celdas | gana / empata / pierde (celdas, +-5 %) | media geom. CPU | gana / empata / pierde (CPU) |",
    "|---|---|---|---|---|---|---|",
]
for v in CMP:
    r = t[v]
    lines.append(f"| {LABEL[v]} vs base | {r['comparables']} | {r['celdas_identicas']} | {f3(r['celdas_gm'])} | {r['celdas_gana']} / {r['celdas_empata']} / {r['celdas_pierde']} | {f3(r['cpu_gm'])} | {r['cpu_gana']} / {r['cpu_empata']} / {r['cpu_pierde']} |")
lines += [
    "",
    f"Instancias en las que alguna configuracion k-nomial (k={KS}) cambia las celdas: {len(chg)} de {n_ok}. Instancias en las que la reescritura k=3 llega a extraer bloques: {len(resumen['instancias_con_bloques_k3'])}.",
    "",
    "| archivo | que muestra |",
    "|---|---|",
    "| `dispersion_raa_baseline.png` | Por instancia, x = RAA k=0, y = k=2 (+) y k=3 (x); celdas y CPU; fila superior todas, fila inferior recorte al percentil 90 de la base. Ejes lineales. |",
    "| `perfiles_raa_baseline.png` | Perfiles de desempeno (fraccion de instancias dentro de un factor X de la mejor), eje x lineal. |",
    "| `cociente_por_instancia.png` | Solo las instancias cuyas celdas cambian: cociente k / base, con las celdas de la base bajo cada nombre. |",
    "| `tabla_raa_baseline.csv` | Estado, celdas y CPU de todas las configuraciones por instancia, cocientes, y los contadores RAA-K de la corrida k=3 (productos, con_bloques, bloques, usados, cuadrados, corner). |",
    "| `resumen.json` | Las cifras de arriba por grupo (easy+medium, hard+others, todas), la lista de instancias que cambian y la de instancias con bloques. |",
]
with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("instancias:", n_ok, "| cambian:", len(chg), "| con bloques k3:", len(resumen["instancias_con_bloques_k3"]))
for v in CMP:
    r = t[v]; print(f"{LABEL[v]}: gm celdas {r['celdas_gm']:.3f} ({r['celdas_gana']}/{r['celdas_empata']}/{r['celdas_pierde']}), identicas {r['celdas_identicas']}/{r['comparables']}; gm cpu {r['cpu_gm']:.3f}")
print("salida:", OUT)
