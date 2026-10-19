"""[raak local] Un grafico por experimento de raak/results (seccion 4 del informe del 30-09).
Lee los CSV de results/ y escribe los PNG y un README en results/08-graficos/. Uso: python analysis/graficos_resultados.py"""
import sys, os
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # raak/
RES = os.path.join(REPO, "results")
OUT = os.path.join(RES, "08-graficos")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "analysis"))
import vizstyle as vz
import matplotlib.pyplot as plt

vz.setup()
S = vz.SLOTS
LR_COLOR = {"xn": S[6], "art": S[0], "compo": S[2]}
LR_LABEL = {"xn": "X-Taylor (xn)", "art": "afin sola (art)", "compo": "afin + X-Taylor (compo)"}
figs = []  # (archivo, descripcion)


def save(fig, name, desc):
    p = os.path.join(OUT, name)
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    figs.append((name, desc))
    print("ok", name)


def gm(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x) & (x > 0)]
    return float(np.exp(np.log(x).mean())) if len(x) else np.nan


def perf_profile(ax, table, colors, labels, styles=None, xlabel="factor respecto de la mejor variante (escala log)"):
    """table: DataFrame instancias x variantes con la metrica (NaN = no resuelta)."""
    best = table.min(axis=1)
    ratios = table.div(best, axis=0)
    finite = ratios.replace([np.inf], np.nan).max().max()
    taus = np.logspace(0, np.log10(max(finite, 1.5) * 1.05), 300)
    for v in table.columns:
        r = ratios[v].values
        rho = [(np.nan_to_num(r, nan=np.inf) <= t).mean() for t in taus]
        ax.step(taus, rho, where="post", color=colors[v], label=labels[v],
                linestyle=(styles or {}).get(v, "-"))
    ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("fraccion de instancias")
    ax.set_ylim(0, 1.02)


# ---------------------------------------------------------------- 01 linea base
d = pd.read_csv(os.path.join(RES, "01-linea-base", "baseline-20260913-193306", "results.csv"))
ok = d[d.status == "SUCCESS"]
cells = ok.pivot_table(index=["set", "instance"], columns="lr", values="cells")
cells = cells[cells.notna().all(axis=1) & (cells > 0).all(axis=1)]
fig, ax = plt.subplots(figsize=(7.5, 4.6))
perf_profile(ax, cells[["xn", "art", "compo"]], LR_COLOR, LR_LABEL)
ax.set_title(f"Linea base (13-09): perfil de desempeno en celdas del B&B\n"
             f"{len(cells)} instancias easy+medium resueltas por las 3 relajaciones, limite 60 s")
ax.legend(loc="lower right")
save(fig, "01_linea_base_perfil_celdas.png",
     "Linea base sin modificaciones: que fraccion de instancias resuelve cada relajacion con a lo sumo X veces las celdas de la mejor.")

# ---------------------------------------------------------------- 02 prototipo v1
d = pd.read_csv(os.path.join(RES, "02-prototipo-raak", "baseline-20260914-120246", "raak_vs_base.csv"))
d = d[d.ratio.notna()].sort_values("ratio")
fig, ax = plt.subplots(figsize=(8, 5))
y = np.arange(len(d))
pc = {"raak/art": S[0], "raakcompo/compo": S[2]}
pl = {"raak/art": "k-nomial sobre art", "raakcompo/compo": "k-nomial sobre compo"}
for p, g in d.groupby("pair"):
    ax.scatter(g.ratio, [y[i] for i in np.where(d.pair == p)[0]], color=pc[p], label=pl[p], s=36, zorder=3)
ax.axvline(1, color=vz.TEXT2, linewidth=1)
ax.set_yticks(y)
ax.set_yticklabels(d.instance, fontsize=8)
ax.set_xscale("log")
ax.set_xlabel("celdas con k-nomial / celdas sin k-nomial (log; < 1 mejora)")
ax.set_ylabel("instancia")
ax.set_title(f"Prototipo v1 (14-09): efecto del k-nomial en el B&B\n{len(d)} corridas donde el k-nomial llego a actuar, limite 60 s")
ax.legend(loc="lower right")
save(fig, "02_prototipo_v1_knomial_vs_base.png",
     "Primer prototipo (solo productos): cociente de celdas por instancia frente a la misma relajacion sin k-nomial.")

# ---------------------------------------------------------------- 03 v1 vs v2
d = pd.read_csv(os.path.join(RES, "02-prototipo-raak", "baseline-20260914-131620", "raak_v2_vs_base.csv"))
d = d[(d.cells_base > 0) & d.cells_v1.notna() & d.cells_v2.notna()]
fig, ax = plt.subplots(figsize=(6.4, 6))
for p, g in d.groupby("pair"):
    ax.scatter(g.cells_v1 / g.cells_base, g.cells_v2 / g.cells_base, color=pc[p], label=pl[p], s=36, zorder=3)
lim = [0.05, 20]
ax.plot(lim, lim, color=vz.TEXT2, linewidth=1)
ax.axhline(1, color=vz.GRID); ax.axvline(1, color=vz.GRID)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("v1 (solo productos): celdas / base (log)")
ax.set_ylabel("v2 (productos + cuadrados de Chebyshev): celdas / base (log)")
ax.set_title(f"Prototipo v2 frente a v1 (14-09): anadir los cuadrados de Chebyshev\n{len(d)} instancias; debajo de la diagonal, v2 mejor que v1")
for _, r in d[d.cells_v2 / d.cells_base < 0.5].iterrows():
    ax.annotate(f"{r.instance} ({r.pair.split('/')[1]})", (r.cells_v1 / r.cells_base, r.cells_v2 / r.cells_base),
                textcoords="offset points", xytext=(8, -3), fontsize=8, color=vz.TEXT2)
ax.legend(loc="upper left")
save(fig, "03_prototipo_v2_vs_v1_cuadrados.png",
     "Prototipo v2 frente a v1: cada punto es una instancia; ambos ejes son el cociente de celdas frente a la base.")

# ---------------------------------------------------------------- 04 ablacion k1/k3
d = pd.read_csv(os.path.join(RES, "02-prototipo-raak", "baseline-20260915-025226", "descomposicion_k1_k3.csv"))
for c in ["k1_over_base", "k3_over_base"]:
    d[c] = pd.to_numeric(d[c], errors="coerce")  # '-' = sin resultado comparable
d = d[d.k1_over_base.notna() & d.k3_over_base.notna()].sort_values("k3_over_base")
fig, ax = plt.subplots(figsize=(8, 6))
y = np.arange(len(d))
ax.hlines(y, d.k1_over_base, d.k3_over_base, color=vz.GRID, linewidth=2)
ax.scatter(d.k1_over_base, y, color=S[2], label="solo parte RAA (k=1), sin bloques", s=36, zorder=3)
ax.scatter(d.k3_over_base, y, color=S[3], label="RAA + bloques k-nomial (k=3)", s=36, zorder=3)
ax.axvline(1, color=vz.TEXT2, linewidth=1)
ax.set_yticks(y); ax.set_yticklabels([f"{r.instance} ({r.pair.split('/')[1]})" for _, r in d.iterrows()], fontsize=7)
ax.set_xscale("log")
ax.set_xlabel("celdas / celdas de la base sin RAA (log; < 1 mejora)")
ax.set_title(f"Ablacion (15-09): que parte del prototipo aporta, la RAA o los bloques k-nomial\n{len(d)} corridas, limite 60 s")
ax.legend(loc="lower right")
save(fig, "04_ablacion_raa_vs_bloques_knomial.png",
     "Ablacion del prototipo: para cada instancia, celdas con solo la parte RAA (k=1) y con RAA mas bloques (k=3), ambas frente a la base.")

# ---------------------------------------------------------------- 05 QPLIB
d = pd.read_csv(os.path.join(RES, "03-qplib", "qplib-eval-20260914-212602", "eval.csv"))
d["inst"] = d.file.str.split("__").str[0]
d["form"] = d.file.str.split("__").str[1].str.replace(".txt", "", regex=False)
w = d.pivot_table(index=["inst", "form"], columns="mode", values="radius").reset_index()
w["red"] = 100 * (1 - w[3] / w[0])
FORM_LABEL = {"mono": "monomio\na monomio", "eig": "descomposicion\nespectral", "kn2": "k-nomial k=2\nprecalculado", "kn3": "k-nomial k=3\nprecalculado"}
FORM_COLOR = {"mono": S[0], "eig": S[1], "kn2": S[2], "kn3": S[3]}
fig, ax = plt.subplots(figsize=(8, 5))
rng = np.random.default_rng(1)
for i, f in enumerate(["mono", "eig", "kn2", "kn3"]):
    g = w[w.form == f]
    ax.scatter(i + rng.uniform(-0.18, 0.18, len(g)), g.red, color=FORM_COLOR[f], s=22, alpha=0.8, zorder=3)
    ax.hlines(g.red.mean(), i - 0.3, i + 0.3, color=vz.TEXT, linewidth=2)
    ax.annotate(f"media {g.red.mean():.1f} %\nsin efecto: {(g.red.abs() < 1e-9).sum()} de {len(g)}",
                (i, g.red.max()), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=8, color=vz.TEXT2)
ax.set_xticks(range(4)); ax.set_xticklabels([FORM_LABEL[f] for f in ["mono", "eig", "kn2", "kn3"]], fontsize=9)
ax.set_xlabel("como esta escrita la forma cuadratica al evaluarla en IBEX")
ax.set_ylabel("reduccion del radio con RAA-K k=3 frente a fAF2 (%)")
ax.set_ylim(min(-1, w.red.min() - 1), w.red.max() + 12)
ax.set_title(f"QPLIB en IBEX (14-09): cuanto estrecha RAA-K la envolvente afin\n{w.inst.nunique()} instancias x 4 formulaciones; la raya negra es la media")
save(fig, "05_qplib_reduccion_radio_raak.png",
     "QPLIB evaluado con el port C++: reduccion porcentual del radio de la forma afin con RAA-K k=3 frente a fAF2, por formulacion.")

# ---------------------------------------------------------------- 06 timing
d = pd.read_csv(os.path.join(RES, "02-prototipo-raak", "timing-20260914-132113", "timing.csv"))
base = d[d.variant == "art"].groupby("instance").cpu_s.mean()
d["ratio"] = d.apply(lambda r: r.cpu_s / base[r.instance], axis=1)
insts = sorted(d.instance.unique(), key=lambda i: base[i])
fig, ax = plt.subplots(figsize=(8.5, 4.8))
x = np.arange(len(insts))
VC = {"raak:0": S[2], "raak:3": S[3]}
VL = {"raak:0": "RAA sin bloques (raak:0)", "raak:3": "RAA + k-nomial k=3 (raak:3)"}
for j, v in enumerate(["raak:0", "raak:3"]):
    g = d[d.variant == v]
    off = -0.15 + 0.3 * j
    for i, inst in enumerate(insts):
        r = g[g.instance == inst].ratio.values
        ax.scatter([x[i] + off] * len(r), r, color=VC[v], s=24, alpha=0.75, zorder=3, label=VL[v] if i == 0 else None)
        ax.hlines(r.mean(), x[i] + off - 0.1, x[i] + off + 0.1, color=VC[v], linewidth=2)
ax.axhline(1, color=vz.TEXT2, linewidth=1)
ax.set_xticks(x); ax.set_xticklabels([i.split("/")[1] for i in insts], rotation=30, ha="right", fontsize=8)
ax.set_xlabel("instancia (ordenadas por CPU de art)")
ax.set_ylabel("CPU / CPU de art (3 repeticiones y su media)")
ax.set_title("Sobrecosto de CPU del prototipo (14-09): corridas secuenciales con orden rotado\n10 instancias x 3 variantes x 3 repeticiones")
ax.legend(loc="upper left")
save(fig, "06_sobrecosto_cpu_prototipo.png",
     "Tiempo de CPU de las variantes RAA frente a art en la misma sesion, con repeticiones, para medir el sobrecosto sin ruido de paralelismo.")

# ---------------------------------------------------------------- 07 regresion refactor
d = pd.read_csv(os.path.join(RES, "04-fase1-validacion", "fase1-20260916", "paso11", "runs.csv"))
d = d[d.celdas.notna()]
vs = ["art", "raak_1", "alias_raak_1", "raak_3", "raakcompo_3", "art_af2_k3"]
VL7 = {"art": "AF2 (art)", "raak_1": "RAA k=0", "alias_raak_1": "alias --lr=raak k=1", "raak_3": "RAA k=3", "raakcompo_3": "RAA k=3 (compo)", "art_af2_k3": "AF2 k=3 (nueva)"}
VC7 = {"art": S[0], "raak_1": S[2], "alias_raak_1": S[7], "raak_3": S[3], "raakcompo_3": S[4], "art_af2_k3": S[1]}
insts = sorted(d.instancia.unique())
fig, ax = plt.subplots(figsize=(9, 4.8))
x = np.arange(len(insts)); wdt = 0.13
for j, v in enumerate(vs):
    vals = [d[(d.instancia == i) & (d.variante == v)].celdas.max() for i in insts]
    ax.bar(x + (j - 2.5) * wdt, [max(c, 0.7) if pd.notna(c) else 0 for c in vals], wdt, color=VC7[v], label=VL7[v])
ax.set_yscale("log")
ax.set_xticks(x); ax.set_xticklabels([i.split("/")[1] for i in insts], fontsize=8)
ax.set_xlabel("instancia de referencia (limite 300 s)")
ax.set_ylabel("celdas del B&B (log)")
ax.set_title("Fase 1, regresion (16-09): tras separar --arith y --knomial_k las celdas son identicas a la referencia\n35 de 35 corridas con referencia identicas; AF2 k=3 es nueva y no tenia referencia")
ax.legend(ncol=3, fontsize=8, loc="upper left")
save(fig, "07_fase1_regresion_refactor.png",
     "Regresion de la Fase 1: celdas por instancia y variante tras el refactor; coinciden exactamente con las referencias guardadas antes.")

# ---------------------------------------------------------------- 08 validacion
tests = [
    ("knomial_golden: bloques C++ = Python", 327, "0 diferencias"),
    ("raak_arith_test: productos + cuadrados fAF2", 6000, "0 violaciones"),
    ("raa_corner_test: pares con corner test", 10000, "0 violaciones"),
    ("aa_knomial_test: productos Affine3", 3000, "0 violaciones"),
    ("aa_linearizer_test: puntos de 200 polinomios", 200000, "0 violaciones"),
    ("trig_lin_test: evaluaciones sin/cos", 17640, "0 violaciones"),
    ("range_eval: evaluaciones en benchs/optim", 124674, "0 violaciones"),
    ("regresiones del solver (fase 1 + fase 2)", 56, "56 identicas"),
]
fig, ax = plt.subplots(figsize=(8.5, 4.6))
y = np.arange(len(tests))[::-1]
ax.barh(y, [t[1] for t in tests], color=S[0], height=0.6)
for yi, t in zip(y, tests):
    ax.annotate(f"{t[1]:,}  ·  {t[2]}", (t[1], yi), textcoords="offset points", xytext=(6, 0), va="center", fontsize=8, color=vz.TEXT2)
ax.set_yticks(y); ax.set_yticklabels([t[0] for t in tests], fontsize=8)
ax.set_xscale("log"); ax.set_xlim(right=3e6)
ax.set_xlabel("casos evaluados (log)")
ax.set_title("Validacion del codigo (fases 1 a 3): contencion, fidelidad al Python y regresiones\nninguna prueba encontro una violacion ni una diferencia")
save(fig, "08_validacion_contencion_y_fidelidad.png",
     "Resumen de todas las pruebas de validez: cuantos casos evaluo cada una y su resultado.")

# ---------------------------------------------------------------- 09 trig sobreestimacion
d = pd.read_csv(os.path.join(RES, "05-fase2-trigonometria", "fase2-20260921", "trig_lin.csv"))
funcs = ["sin", "cos", "sin*cos"]  # sin2+cos2 se omite: su rango exacto tiene anchura 0 y el cociente no esta definido
modes = ["legacy", "cheb", "minrange"]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharey=True)
for ax, arith in zip(axes, ["AF2", "AA"]):
    x = np.arange(len(funcs)); wdt = 0.26
    for j, m in enumerate(modes):
        vals = [gm(d[(d.arith == arith) & (d.func == f) & (d["mode"] == m)].ratio) for f in funcs]
        b = ax.bar(x + (j - 1) * wdt, vals, wdt, color=vz.MODE_COLOR[m], label=vz.MODE_LABEL[m])
        for xi, v in zip(x + (j - 1) * wdt, vals):
            ax.annotate(f"{v:.2f}", (xi, v), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=7, color=vz.TEXT2)
    ax.axhline(1, color=vz.TEXT2, linewidth=1)
    ax.set_xticks(x); ax.set_xticklabels(funcs)
    ax.set_xlabel(f"funcion evaluada con {arith}")
axes[0].set_ylabel("anchura afin / rango exacto (media geom.; 1 = exacto)")
axes[0].legend(loc="upper left", fontsize=8)
fig.suptitle("Fase 2 (21-09): sobreestimacion de sin y cos segun la linealizacion\n735 intervalos por funcion (centros en [-pi, pi], anchos de 0.01 a 2 pi), 0 violaciones; sin2+cos2 omitida (rango exacto de anchura 0)", y=1.02)
save(fig, "09_fase2_trig_sobreestimacion_por_modo.png",
     "Fase 2: media geometrica de anchura afin / rango exacto por funcion y modo de linealizacion, en AF2 y en AA.")

# ---------------------------------------------------------------- 10 trig por anchura
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
for ax, f in zip(axes, ["sin", "sin*cos"]):
    g = d[(d.arith == "AF2") & (d.func == f)].copy()
    g["wbin"] = pd.cut(np.log10(g.width), bins=14)
    for m in modes:
        h = g[g["mode"] == m].groupby("wbin", observed=True)
        xs = [10 ** iv.mid for iv in h.groups.keys()]
        ax.plot(xs, h.ratio.apply(gm).values, color=vz.MODE_COLOR[m], label=vz.MODE_LABEL[m])
    ax.axhline(1, color=vz.TEXT2, linewidth=1)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_yticks([1, 1.5, 2, 3, 4, 6]); ax.set_yticklabels(["1", "1.5", "2", "3", "4", "6"]); ax.minorticks_off()
    ax.set_xlabel(f"anchura del intervalo de entrada ({f}), escala log")
axes[0].set_ylabel("anchura afin / rango exacto (media geom. por anchura)")
axes[0].legend(loc="upper left", fontsize=8)
fig.suptitle("Fase 2 (21-09): la sobreestimacion crece con la anchura del intervalo, y cuanto segun el modo (AF2)", y=1.0)
save(fig, "10_fase2_trig_sobreestimacion_por_anchura.png",
     "Fase 2: sobreestimacion en funcion de la anchura del intervalo de entrada, para sin y para sin*cos, por modo.")

# ---------------------------------------------------------------- 11 trig en el solver
d = pd.read_csv(os.path.join(RES, "05-fase2-trigonometria", "fase2-20260921", "trig_instancias", "runs.csv"))
d = d[d.celdas.notna()]
d["lr"] = d.variante.str.split("_").str[0]
d["mode"] = d.variante.str.split("_").str[1].fillna("")
insts = sorted(d.instancia.unique())
fig, ax = plt.subplots(figsize=(8, 4.4))
x = np.arange(len(insts)); wdt = 0.12
cols = [("art", "legacy"), ("art", "cheb"), ("art", "minrange"), ("compo", "legacy"), ("compo", "cheb"), ("compo", "minrange"), ("xn", "")]
for j, (lr, m) in enumerate(cols):
    vals = [d[(d.instancia == i) & (d.lr == lr) & (d["mode"] == m)].celdas.max() for i in insts]
    color = vz.MODE_COLOR.get(m, S[6])
    lab = f"{lr} · {vz.MODE_LABEL[m].split(' (')[0]}" if m else "X-Taylor (xn)"
    ax.bar(x + (j - 3) * wdt, vals, wdt, color=color, label=lab, hatch="//" if lr == "compo" else None, edgecolor=vz.SURFACE)
ax.set_xticks(x); ax.set_xticklabels([i.split("/")[1] for i in insts])
ax.set_xlabel("instancia con sin/cos (limite 120 s); rayado = compo, liso = art")
ax.set_ylabel("celdas del B&B")
ax.set_title("Fase 2 (21-09): efecto de la linealizacion de sin/cos dentro del solver\n3 instancias resueltas; ex4_1_7 no pudo cargarse")
ax.legend(ncol=2, fontsize=7, loc="upper left")
save(fig, "11_fase2_trig_en_el_solver.png",
     "Fase 2: celdas del B&B por instancia y modo de linealizacion trigonometrica, con art y con compo.")

# ---------------------------------------------------------------- 12 nivel 1 por escala
d = pd.read_csv(os.path.join(RES, "06-fase3-nivel1-rangos", "nivel1", "range.csv.gz"))
act = d[(d.active == 1) & np.isfinite(d.ratio_aff) & (d.ratio_aff > 0)]
scales = [1.0, 0.5, 0.25, 0.125, 0.0625]
fig, ax = plt.subplots(figsize=(8, 5))
for v in ["af2_k0", "af2_k3", "raa_k0", "raa_k3", "aa_k0", "aa_k3"]:
    g = act[act.variant == v]
    ys = [gm(g[g.scale == s].ratio_aff) for s in scales]
    ax.plot(range(len(scales)), ys, color=vz.VARIANT_COLOR[v], linestyle=vz.VARIANT_STYLE[v], marker="o", label=vz.VARIANT_LABEL[v])
gi = act[act.variant == "af2_k0"]
ax.plot(range(len(scales)), [gm(gi[gi.scale == s].ratio_itv) for s in scales], color=vz.TEXT2, linestyle=":", marker="s", label="extension natural de intervalos (referencia)")
ax.set_xticks(range(len(scales))); ax.set_xticklabels(["caja inicial", "1/2", "1/4", "1/8", "1/16"])
ax.set_xlabel("tamano relativo de la caja evaluada")
ax.set_ylabel("anchura afin / rango muestreado (media geom.; mas bajo es mejor)")
ax.set_title(f"Fase 3, nivel 1 (21-09): sobreestimacion de rangos sin resolver, por variante y tamano de caja\n{d.instance.nunique()} instancias, {len(act) // 6:,} ternas (instancia, funcion, caja) por variante, 0 violaciones", fontsize=10)
ax.legend(fontsize=8, loc="upper right")
save(fig, "12_fase3_nivel1_sobreestimacion_por_escala.png",
     "Nivel 1: media geometrica de la sobreestimacion de cada variante segun el tamano de la caja, con la extension de intervalos como referencia.")

# ---------------------------------------------------------------- 13 nivel 1 efectos
key = ["instance", "func", "box_id"]
piv = act.pivot_table(index=key, columns="variant", values="w_aff")
pairs = [("raa_k0", "af2_k0", "aritmetica: RAA / AF2"), ("aa_k0", "af2_k0", "aritmetica: AA / AF2"),
         ("af2_k3", "af2_k0", "k-nomial: AF2+k / AF2"), ("raa_k3", "raa_k0", "k-nomial: RAA+k / RAA"),
         ("aa_k3", "aa_k0", "k-nomial: AA+k / AA"), ("raa_k3", "af2_k0", "total: RAA+k / AF2")]
rows = []
for a, b, lab in pairs:
    r = (piv[a] / piv[b]).dropna()
    rows.append((lab, int((r < 0.95).sum()), int((r > 1.05).sum()), len(r)))
fig, ax = plt.subplots(figsize=(8, 4.2))
y = np.arange(len(rows))[::-1]
ax.barh(y, [-r[1] for r in rows], color=S[2], height=0.6, label="mas estrecha (> 5 %)")
ax.barh(y, [r[2] for r in rows], color=S[7], height=0.6, label="mas ancha (> 5 %)")
for yi, r in zip(y, rows):
    ax.annotate(str(r[1]), (-r[1], yi), textcoords="offset points", xytext=(-4, 0), ha="right", va="center", fontsize=8)
    ax.annotate(str(r[2]), (r[2], yi), textcoords="offset points", xytext=(4, 0), ha="left", va="center", fontsize=8)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=9)
ax.axvline(0, color=vz.TEXT2, linewidth=1)
ax.set_xlabel(f"ternas (instancia, funcion, caja) de {rows[0][3]:,}; el resto son iguales")
ax.set_title("Fase 3, nivel 1 (21-09): en cuantos casos cada comparacion estrecha o ensancha la forma")
ax.legend(loc="lower right", fontsize=8)
save(fig, "13_fase3_nivel1_efectos_por_par.png",
     "Nivel 1: numero de ternas mas estrechas o mas anchas en mas de 5 % para cada par de variantes.")

# ---------------------------------------------------------------- 14-17 etapas A-D
STAGES = [("A_easy_medium_compo", "Etapa A: easy+medium, relajacion compo"),
          ("B_easy_medium_art", "Etapa B: easy+medium, relajacion art"),
          ("C_hard_others_compo", "Etapa C: hard+others, relajacion compo"),
          ("D_hard_others_art", "Etapa D: hard+others, relajacion art")]
summary = []
for n, (folder, title) in enumerate(STAGES, start=14):
    r = pd.read_csv(os.path.join(RES, "07-fase3-nivel2-solver", "fase3-20260921", folder, "runs.csv"))
    r["v"] = r.variante.map(vz.variant_key)
    ok = r[r.estado == "SUCCESS"]
    cells = ok.pivot_table(index="instancia", columns="v", values="celdas")
    cpu = ok.pivot_table(index="instancia", columns="v", values="cpu_s")
    order = [v for v in ["af2_k0", "af2_k3", "raa_k0", "raa_k3", "aa_k0", "aa_k3", "xn"] if v in cells.columns]
    cells = cells[order]; cpu = cpu[order]
    # instancias resueltas por al menos una variante
    cells = cells[cells.notna().any(axis=1)]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    perf_profile(axes[0], cells, vz.VARIANT_COLOR, vz.VARIANT_LABEL, vz.VARIANT_STYLE, "celdas / celdas de la mejor variante (log)")
    perf_profile(axes[1], cpu.loc[cells.index], vz.VARIANT_COLOR, vz.VARIANT_LABEL, vz.VARIANT_STYLE, "CPU / CPU de la mejor variante (log)")
    axes[0].set_title("celdas del B&B"); axes[1].set_title("tiempo de CPU")
    axes[1].legend(loc="lower right", fontsize=8)
    fig.suptitle(f"Fase 3, nivel 2 (22-09). {title}: perfiles de desempeno\n{len(cells)} instancias resueltas por alguna variante, limite 1800 s", y=1.02)
    save(fig, f"{n}_fase3_{folder}_perfiles.png",
         f"Nivel 2, {title}: perfil de desempeno en celdas y en CPU; mas arriba y mas a la izquierda es mejor.")
    for v in order:
        both = cells[[v, "af2_k0"]].dropna()
        summary.append((folder.split("_")[0], v, gm(both[v] / both["af2_k0"]),
                        gm(cpu.loc[both.index, v] / cpu.loc[both.index, "af2_k0"]), int(cells[v].notna().sum())))

# ---------------------------------------------------------------- 18 resumen
sm = pd.DataFrame(summary, columns=["etapa", "v", "gm_cells", "gm_cpu", "resueltas"])
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
order = ["af2_k3", "raa_k0", "raa_k3", "aa_k0", "aa_k3", "xn"]
for ax, col, lab in zip(axes, ["gm_cells", "gm_cpu"], ["celdas", "CPU"]):
    x = np.arange(4); wdt = 0.13
    for j, v in enumerate(order):
        vals = [sm[(sm.etapa == e) & (sm.v == v)][col].max() for e in "ABCD"]
        ax.bar(x + (j - 2.5) * wdt, vals, wdt, color=vz.VARIANT_COLOR[v], label=vz.VARIANT_LABEL[v],
               hatch="//" if v.endswith("k3") else None, edgecolor=vz.SURFACE)
    ax.axhline(1, color=vz.TEXT2, linewidth=1)
    ax.set_xticks(x); ax.set_xticklabels(["A easy+medium\ncompo", "B easy+medium\nart", "C hard+others\ncompo", "D hard+others\nart"], fontsize=8)
    ax.set_title(f"{lab}: media geometrica del cociente variante / AF2")
axes[0].set_ylabel("cociente frente a AF2 sin k-nomial (1 = igual; < 1 mejor)")
axes[0].set_yscale("log")
axes[0].set_yticks([0.5, 0.6, 0.8, 1, 1.5, 2, 3]); axes[0].set_yticklabels(["0.5", "0.6", "0.8", "1", "1.5", "2", "3"]); axes[0].minorticks_off()
axes[1].legend(fontsize=8, loc="upper left")
fig.suptitle("Fase 3, nivel 2 (22-09): resumen de las cuatro etapas, limite 1800 s (instancias resueltas por ambas)", y=1.0)
save(fig, "18_fase3_resumen_medias_geometricas.png",
     "Nivel 2, consolidado: media geometrica de celdas y CPU de cada variante frente a AF2, por etapa.")

# ---------------------------------------------------------------- README
with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
    f.write("# Graficos de los experimentos RAA-K\n\n")
    f.write("Fuente: los CSV de `raak/results/`. Un grafico por experimento, en orden cronologico. Generado por `analysis/graficos_resultados.py`.\n\n")
    f.write("| archivo | que muestra |\n|---|---|\n")
    for name, desc in figs:
        f.write(f"| `{name}` | {desc} |\n")
print("listo:", len(figs), "graficos en", OUT)
