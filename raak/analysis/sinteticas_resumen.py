"""[raak local] Desglose del nivel 2 sobre reales + sinteticas: por configuracion (n, densidad, diagonal), instancias
resueltas por variante, y que pasa en las que agotan el tiempo (cota inferior alcanzada y celdas a los 1800 s).
Complementa a raa_baseline.py. Produce en <out>: por_configuracion.csv, timeouts.csv, reales.csv, sinteticas_por_n.png.
uso: python analysis/sinteticas_resumen.py <runs_reales.csv> <runs_sinteticas.csv> --out <dir>
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
ap.add_argument("reales"); ap.add_argument("sinteticas")
ap.add_argument("--out", default=os.path.join(REPO, "results", "12-sinteticas-reales", "analisis"))
ap.add_argument("--titulo", default="Sinteticas")
ap.add_argument("--cmp", default="art_raa_k2,art_raa_k3", help="variantes k-nomiales a comparar con la base, separadas por coma")
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
BASE = "art_raa_k0"
CMPS = [v.strip() for v in args.cmp.split(",") if v.strip()]
VARS = [BASE] + CMPS
NV = len(VARS)
LABEL = {v: f"RAA k={v[-1]}" for v in VARS}
COLOR = {"art_raa_k2": vz.SLOTS[1], "art_raa_k3": vz.VARIANT_COLOR["raa_k3"], "art_raa_k4": vz.SLOTS[7]}


def gm(x):
    x = np.asarray(x, float); x = x[np.isfinite(x) & (x > 0)]
    return float(np.exp(np.log(x).mean())) if len(x) else float("nan")


# ---------------- sinteticas por configuracion
s = pd.read_csv(args.sinteticas)
s["inst"] = s.instancia.str.split("/").str[1]
s["n"] = s.inst.str.extract(r"n(\d+)").astype(int)
s["dens"] = s.inst.str.extract(r"_d(\d+)").astype(int) / 100
s["diag"] = s.inst.str.extract(r"_(pos|posneg)_")[0].fillna("-")        # synl/synt no llevan diagonal ni fuerza
s["fuerza"] = s.inst.str.extract(r"_(normal|strong|weak)_")[0].fillna("-")
cfg = s.drop_duplicates("inst").set_index("inst")[["n", "dens", "diag", "fuerza"]]
ok = s[s.estado == "SUCCESS"]
cells = ok.pivot_table(index="inst", columns="variante", values="celdas")
cpu = ok.pivot_table(index="inst", columns="variante", values="cpu_s")
allsolved = cells.dropna()
rows = []
for (n, dens, diag, fuerza), g in cfg.groupby(["n", "dens", "diag", "fuerza"]):
    idx = g.index
    r = {"n": n, "densidad": dens, "diagonal": diag, "fuerza_diag": fuerza, "instancias": len(idx)}
    for v in VARS: r[f"resueltas_{v[4:]}"] = int(cells.reindex(idx)[v].notna().sum()) if v in cells else 0
    both = allsolved.reindex(idx).dropna()
    r[f"resueltas_por_las_{NV}"] = len(both)
    for v in CMPS:
        r[f"celdas_gm_{v[4:]}"] = round(gm(both[v] / both[BASE]), 3) if len(both) else float("nan")
        r[f"cpu_gm_{v[4:]}"] = round(gm(cpu.loc[both.index, v] / cpu.loc[both.index, BASE]), 3) if len(both) else float("nan")
    r["celdas_base_media"] = round(float(both[BASE].mean()), 0) if len(both) else float("nan")
    rows.append(r)
pc = pd.DataFrame(rows)
pc.to_csv(os.path.join(args.out, "por_configuracion.csv"), index=False)

# por n (todas las densidades y diagonales)
rows = []
for n, g in cfg.groupby("n"):
    idx = g.index; both = allsolved.reindex(idx).dropna()
    r = {"n": n, "instancias": len(idx), f"resueltas_por_las_{NV}": len(both)}
    for v in VARS: r[f"resueltas_{v[4:]}"] = int(cells.reindex(idx)[v].notna().sum())
    for v in CMPS:
        rc = both[v] / both[BASE]
        r[f"celdas_gm_{v[4:]}"] = round(gm(rc), 3); r[f"gana_{v[4:]}"] = int((rc < 0.95).sum()); r[f"pierde_{v[4:]}"] = int((rc > 1.05).sum())
        r[f"cpu_gm_{v[4:]}"] = round(gm(cpu.loc[both.index, v] / cpu.loc[both.index, BASE]), 3)
    rows.append(r)
pn = pd.DataFrame(rows)
pn.to_csv(os.path.join(args.out, "por_n.csv"), index=False)

# ---------------- timeouts: cota inferior y celdas a los 1800 s
to = s[s.estado == "TIME_OUT"]
lb = s.pivot_table(index="inst", columns="variante", values="f_lb")
ub = s.pivot_table(index="inst", columns="variante", values="f_ub")
cl = s.pivot_table(index="inst", columns="variante", values="celdas")
st = s.pivot_table(index="inst", columns="variante", values="estado", aggfunc="first")
rows = []
for inst in sorted(set(to.inst)):
    r = {"instancia": inst, **cfg.loc[inst].to_dict()}
    for v in VARS:
        r[f"estado_{v[4:]}"] = st.loc[inst, v]; r[f"f_lb_{v[4:]}"] = lb.loc[inst, v]; r[f"f_ub_{v[4:]}"] = ub.loc[inst, v]; r[f"celdas_{v[4:]}"] = cl.loc[inst, v]
    # brecha relativa al mejor f_ub conocido
    best_ub = float(np.nanmin([ub.loc[inst, v] for v in VARS]))
    for v in VARS: r[f"brecha_{v[4:]}"] = round(float(best_ub - lb.loc[inst, v]), 4)
    rows.append(r)
tt = pd.DataFrame(rows)
tt.to_csv(os.path.join(args.out, "timeouts.csv"), index=False)
all3 = tt[np.logical_and.reduce([(tt[f"estado_{v[4:]}"] == "TIME_OUT").values for v in VARS])] if len(tt) else tt
res_to = {"n_instancias_con_algun_timeout": len(tt), f"las_{NV}_agotan": len(all3)}
for v in (CMPS if len(tt) else []):
    k = v[-1]
    res_to[f"k{k}_mejor_cota_que_k0"] = int((all3[f"f_lb_raa_k{k}"] > all3.f_lb_raa_k0).sum())
    res_to[f"brecha_gm_k{k}_vs_k0"] = round(gm(all3[f"brecha_raa_k{k}"] / all3.brecha_raa_k0), 3) if len(all3) else float("nan")
    res_to[f"celdas_gm_k{k}_vs_k0_en_1800s"] = round(gm(all3[f"celdas_raa_k{k}"] / all3.celdas_raa_k0), 3) if len(all3) else float("nan")
if len(tt):
    any_kn_ok = np.logical_or.reduce([(tt[f"estado_{v[4:]}"] == "SUCCESS").values for v in CMPS])
    all_kn_to = np.logical_and.reduce([(tt[f"estado_{v[4:]}"] == "TIME_OUT").values for v in CMPS])
    res_to["resuelta_solo_con_knomial"] = int(((tt.estado_raa_k0 == "TIME_OUT") & any_kn_ok).sum())
    res_to["resuelta_solo_con_base"] = int(((tt.estado_raa_k0 == "SUCCESS") & all_kn_to).sum())

# ---------------- reales
r_ = pd.read_csv(args.reales); r_["inst"] = r_.instancia.str.split("/").str[1]
rc = r_.pivot_table(index="inst", columns="variante", values="celdas"); rs = r_.pivot_table(index="inst", columns="variante", values="estado", aggfunc="first")
rcpu = r_.pivot_table(index="inst", columns="variante", values="cpu_s")
rows = []
for inst in rc.index:
    row = {"instancia": inst}
    for v in VARS: row[f"estado_{v[4:]}"] = rs.loc[inst, v]; row[f"celdas_{v[4:]}"] = int(rc.loc[inst, v]); row[f"cpu_{v[4:]}"] = round(float(rcpu.loc[inst, v]), 1)
    for v in CMPS: row[f"ratio_celdas_{v[4:]}"] = round(float(rc.loc[inst, v] / rc.loc[inst, BASE]), 3) if rs.loc[inst, v] == "SUCCESS" and rs.loc[inst, BASE] == "SUCCESS" else float("nan")
    rows.append(row)
rt = pd.DataFrame(rows).sort_values("celdas_raa_k0")
rt.to_csv(os.path.join(args.out, "reales.csv"), index=False)

# ---------------- figura: cociente de celdas por n (sinteticas resueltas por las 3), eje lineal
fig, ax = plt.subplots(figsize=(8, 4.2))
x = np.arange(len(pn)); ax.axhline(1, color=vz.TEXT2, linewidth=1)
wdt = 0.8 / len(CMPS)
for i, v in enumerate(CMPS):
    off = (i - len(CMPS) / 2 + 0.5) * wdt; vals = pn[f"celdas_gm_{v[4:]}"]
    ax.bar(x + off, vals, width=wdt, color=COLOR[v], label=LABEL[v])
    for xi, val in zip(x + off, vals): ax.text(xi, val + 0.01, f"{val:.2f}", ha="center", fontsize=8, color=vz.TEXT)
ax.set_xticks(x); ax.set_xticklabels([f"n={int(r.n)}\n{int(getattr(r, f"resueltas_por_las_{NV}"))} de {int(r.instancias)} resueltas" for r in pn.itertuples()], fontsize=9)
ax.set_ylabel("celdas / celdas de RAA k=0 (media geom.)"); ax.set_ylim(0, 1.15); ax.legend(loc="lower left")
ax.set_title(f"{args.titulo}: efecto del k-nomial sobre RAA k=0 por tamano, instancias resueltas por todas las configuraciones", fontsize=10)
fig.savefig(os.path.join(args.out, "sinteticas_por_n.png"), bbox_inches="tight"); plt.close(fig)

print("=== por n ==="); print(pn.to_string(index=False))
print("=== timeouts ==="); print(res_to)
print("=== reales ==="); print(rt.to_string(index=False))
pd.Series(res_to).to_json(os.path.join(args.out, "timeouts_resumen.json"), indent=1)
