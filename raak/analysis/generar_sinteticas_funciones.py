"""[raak local] Generador de instancias sinteticas con productos de FUNCIONES de formas afines (to-do 21-10).

Dos familias, mismo esquema que generar_sinteticas.py (formas afines densas que comparten simbolos) pero con una
funcion no lineal en uno o en los dos factores de cada producto:

  synl ("log", modelo: ex6_2_* de Floudas, energia de Gibbs)
      objetivo  sum_k (A_k.x) * ln(M_k.x + d_k) + c.x,   x in [1e-6, 1]^n, sum x_i = 1  (fracciones molares)
      M_k >= 0 y d_k > 0, asi el argumento del logaritmo es positivo en toda la caja.
  synt ("trig", modelo: Trigexp2-* de benchs/solver)
      objetivo  sum_k t_k,  con t_k alternando  (A_k.x) * f_k(M_k.x)  y  f_k(A_k.x) * g_k(M_k.x),
      f, g in {sin, cos, exp}, x in [-1, 1]^n; los argumentos de exp se escalan a [-2, 2].

Restricciones: synl, la igualdad sum x_i = 1 mas (n//2 - 1) desigualdades del mismo tipo que el objetivo;
synt, una lineal mas (n//2 - 1) del mismo tipo. Todas factibles por construccion (cota = valor en un punto
aleatorio de la caja + margen). Configuraciones: n in {3,5,8,10} x densidad in {0.5, 0.9} x SEEDS semillas.

Salida: <out>/<familia>_n<n>_d<densidad>_s<seed>.bch y manifest.csv.
uso: python analysis/generar_sinteticas_funciones.py --familia synl|synt [--out DIR] [--seeds 3]
"""
import os, sys, argparse, csv, math
sys.dont_write_bytecode = True
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--familia", required=True, choices=["synl", "synt"])
ap.add_argument("--out")
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--base-seed", type=int, default=20261028)
args = ap.parse_args()
OUT = args.out or os.path.join(REPO, "instancias", {"synl": "sinteticas-log", "synt": "sinteticas-fun"}[args.familia])
os.makedirs(OUT, exist_ok=True)
CONFIGS = [(n, rho) for n in (3, 5, 8, 10) for rho in (0.5, 0.9)]
FUNS = ["sin", "cos", "exp"]


def lin(coefs, const=0.0):
    terms = []
    for i, c in enumerate(coefs):
        if abs(c) < 1e-12: continue
        terms.append(("- " if c < 0 else "+ ") + f"{abs(c):g}*x{i+1}")
    if abs(const) > 1e-12: terms.append(("- " if const < 0 else "+ ") + f"{abs(const):g}")
    if not terms: return "0"
    out = " ".join(terms)
    return "(" + (out[2:] if out.startswith("+ ") else "-" + out[2:]) + ")"


def sparse(rng, n, rho, lo, hi):
    v = np.round(rng.uniform(lo, hi, size=n) * (rng.random(n) < rho), 3)
    if not np.any(v): v[rng.integers(n)] = round(rng.uniform(lo, hi), 3)
    return v


def feval(f, v): return {"sin": math.sin, "cos": math.cos, "exp": math.exp}[f](v)


def gen_log(rng, n, rho):
    """terminos (A_k.x) * ln(M_k.x + d_k); devuelve (expr, funcion evaluadora)."""
    A = [sparse(rng, n, rho, -1, 1) for _ in range(n)]
    M = [sparse(rng, n, max(rho, 0.5), 0.05, 1) for _ in range(n)]
    dk = np.round(rng.uniform(0.1, 1.0, size=n), 3)
    expr = " + ".join(f"{lin(A[k])}*ln{lin(M[k], dk[k])}" for k in range(n))
    val = lambda x: float(sum((A[k] @ x) * math.log(M[k] @ x + dk[k]) for k in range(n)))
    return expr, val


def gen_trig(rng, n, rho):
    A = [sparse(rng, n, rho, -1, 1) for _ in range(n)]
    M = [sparse(rng, n, rho, -1, 1) for _ in range(n)]
    terms, vals = [], []
    for k in range(n):
        f = FUNS[k % 3]; g = FUNS[(k + 1) % 3]
        Mk = M[k] / max(1.0, np.abs(M[k]).sum() / 2.0) if f == "exp" or g == "exp" else M[k]
        Mk = np.round(Mk, 3)
        if k % 2 == 0:   # (A.x) * f(M.x)
            terms.append(f"{lin(A[k])}*{f}{lin(Mk)}")
            vals.append((lambda A_, M_, f_: lambda x: (A_ @ x) * feval(f_, M_ @ x))(A[k], Mk, f))
        else:            # f(A.x) * g(M.x)   (como Trigexp2: sin(.)*sin(.))
            Ak = A[k] / max(1.0, np.abs(A[k]).sum() / 2.0) if f == "exp" else A[k]
            Ak = np.round(Ak, 3)
            terms.append(f"{f}{lin(Ak)}*{g}{lin(Mk)}")
            vals.append((lambda A_, M_, f_, g_: lambda x: feval(f_, A_ @ x) * feval(g_, M_ @ x))(Ak, Mk, f, g))
    return " + ".join(terms), (lambda x: float(sum(v(x) for v in vals)))


rows = []
for (n, rho) in CONFIGS:
    for s in range(1, args.seeds + 1):
        name = f"{args.familia}_n{n:02d}_d{int(rho*100):02d}_s{s}"
        rng = np.random.default_rng([args.base_seed, n, int(rho * 100), s, 1 if args.familia == "synl" else 2])
        gen = gen_log if args.familia == "synl" else gen_trig
        L = ["constants", "", "variables"]
        if args.familia == "synl":
            L += [f"x{i+1} in [1e-6, 1];" for i in range(n)]
            x0 = rng.dirichlet(np.ones(n))
        else:
            L += [f"x{i+1} in [-1, 1];" for i in range(n)]
            x0 = rng.uniform(-1, 1, size=n)
        obj, _ = gen(rng, n, rho)
        c = np.round(rng.uniform(-1, 1, size=n), 3)
        L += ["", "minimize", f"{obj} + {lin(c)};", "", "constraints"]
        if args.familia == "synl":
            L.append(" + ".join(f"x{i+1}" for i in range(n)) + " - 1 = 0;")
        else:
            a = np.round(rng.uniform(-1, 1, size=n), 3); L.append(f"{lin(a)} <= {float(a @ x0) + 0.25:.4f};")
        for j in range(max(0, n // 2 - 1)):
            ge, gv = gen(rng, n, rho)
            p = np.round(rng.uniform(-1, 1, size=n), 3)
            L.append(f"{ge} + {lin(p)} <= {gv(x0) + float(p @ x0) + 0.5:.4f};")
        L += ["", "end", ""]
        with open(os.path.join(OUT, name + ".bch"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(L))
        rows.append({"instance": name + ".bch", "familia": args.familia, "n": n, "densidad": rho, "seed": s, "n_productos_obj": n, "n_ctr": 1 + max(0, n // 2 - 1),
                     "modelo_real": "ex6_2_* (Gibbs)" if args.familia == "synl" else "Trigexp2-* (benchs/solver)"})
with open(os.path.join(OUT, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} instancias {args.familia} en {OUT}")
