"""[raak local] Generador de instancias sinteticas con formas cuadraticas, siguiendo el diseno experimental del
paper [B] (Greedy Bilinear Reduction via Diagonal Budgeting), escritas como problemas de optimizacion Minibex.

Por que: el k-nomial dentro de la multiplicacion afin solo actua cuando los dos factores comparten >= 2 simbolos
de ruido, y en benchs/optim eso casi no ocurre (solo la familia ex6_2_*). Aqui la forma cuadratica x'Qx se escribe
como suma de productos de formas afines densas, sum_k (A_k.x)(M_k.x) con Q = A'M, para que cada producto tenga
simbolos compartidos. Escrita monomio a monomio (Q_ij x_i x_j) ninguna aritmetica la distingue (ver dualc* de coconut).

Configuraciones (como la Tabla 1 de [B]): n in {3,5,8,10} x densidad in {0.2,0.5,0.9} x diagonal {pos, posneg},
con fuerza de diagonal 'normal' ([-1,1]); mas n=5, rho=0.5, pos con diagonal 'strong' ([-2,2]) y 'weak' ([-0.5,0.5]).
SEEDS instancias por configuracion. Caja x in [-1,1]^n. Restricciones: 1 lineal + (n//2 - 1) cuadraticas del mismo
tipo, todas factibles por construccion (cota = valor en un punto aleatorio de la caja + margen).

Salida: <out>/synq_n<n>_d<densidad>_<dd>_<ds>_s<seed>.bch y <out>/manifest.csv (parametros y Q efectiva).
uso: python analysis/generar_sinteticas.py [--out raak/instancias/sinteticas] [--seeds 3]
"""
import os, sys, argparse, csv, json
sys.dont_write_bytecode = True
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.path.join(REPO, "instancias", "sinteticas"))
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--base-seed", type=int, default=20261020)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)

CONFIGS = [(n, rho, dd, "normal") for n in (3, 5, 8, 10) for rho in (0.2, 0.5, 0.9) for dd in ("pos", "posneg")]
CONFIGS += [(5, 0.5, "pos", "strong"), (5, 0.5, "pos", "weak")]
DS_RANGE = {"normal": 1.0, "strong": 2.0, "weak": 0.5}


def gen_Q(rng, n, rho, dd, ds):
    Q = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < rho:
                Q[i, j] = Q[j, i] = rng.uniform(-1, 1)
    diag = rng.uniform(0.2, DS_RANGE[ds], size=n)  # magnitud (evita diagonales ~0 sin presupuesto)
    if dd == "posneg":
        sign = rng.choice([-1.0, 1.0], size=n)
        if np.all(sign == sign[0]): sign[0] = -sign[0]
        diag = diag * sign
    Q[np.diag_indices(n)] = diag
    return Q


def factor(rng, Q):
    """Q = A' M con A aleatoria bien condicionada; devuelve A, M redondeadas y la Q efectiva simetrizada."""
    n = Q.shape[0]
    while True:
        A = rng.uniform(-1, 1, size=(n, n))
        if np.linalg.cond(A) < 30: break
    M = np.linalg.solve(A.T, Q)  # A' M = Q
    A = np.round(A, 3); M = np.round(M, 3)
    Qe = 0.5 * (A.T @ M + M.T @ A)
    return A, M, Qe


def lin(coefs, prefix="x"):
    """'(c1*x1 + c2*x2 - ...)' omitiendo ceros."""
    terms = []
    for i, c in enumerate(coefs):
        if abs(c) < 1e-12: continue
        s = f"{abs(c):g}*{prefix}{i+1}"
        terms.append(("- " if c < 0 else "+ ") + s)
    if not terms: return "0"
    out = " ".join(terms)
    return "(" + (out[2:] if out.startswith("+ ") else "-" + out[2:]) + ")"


def quad_expr(A, M):
    return " + ".join(f"{lin(A[k])}*{lin(M[k])}" for k in range(A.shape[0]))


def value_quad(A, M, x):
    return float(sum((A[k] @ x) * (M[k] @ x) for k in range(A.shape[0])))


rows = []
for (n, rho, dd, ds) in CONFIGS:
    for s in range(1, args.seeds + 1):
        name = f"synq_n{n:02d}_d{int(rho*100):02d}_{dd}_{ds}_s{s}"
        rng = np.random.default_rng([args.base_seed, n, int(rho * 100), hash(dd) % 1000, hash(ds) % 1000, s])
        Q = gen_Q(rng, n, rho, dd, ds)
        A, M, Qe = factor(rng, Q)
        c = np.round(rng.uniform(-1, 1, size=n), 3)
        x0 = rng.uniform(-1, 1, size=n)  # punto factible de referencia
        L = ["constants", "", "variables"] + [f"x{i+1} in [-1, 1];" for i in range(n)] + ["", "minimize"]
        L.append(f"{quad_expr(A, M)} + {lin(c)};")
        L += ["", "constraints"]
        # 1 restriccion lineal
        a = np.round(rng.uniform(-1, 1, size=n), 3); b = float(a @ x0) + 0.25
        L.append(f"{lin(a)} <= {b:.4f};")
        # (n//2 - 1) restricciones cuadraticas con 2 productos de formas afines
        for j in range(max(0, n // 2 - 1)):
            P = np.round(rng.uniform(-1, 1, size=(2, n)) * (rng.random((2, n)) < max(rho, 0.5)), 3)
            Rm = np.round(rng.uniform(-1, 1, size=(2, n)) * (rng.random((2, n)) < max(rho, 0.5)), 3)
            p = np.round(rng.uniform(-1, 1, size=n), 3)
            bq = value_quad(P, Rm, x0) + float(p @ x0) + 0.5
            L.append(f"{quad_expr(P, Rm)} + {lin(p)} <= {bq:.4f};")
        L += ["", "end", ""]
        with open(os.path.join(args.out, name + ".bch"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(L))
        eig = np.linalg.eigvalsh(Qe)
        rows.append({"instance": name + ".bch", "n": n, "densidad": rho, "diagonal": dd, "fuerza_diag": ds, "seed": s,
                     "n_productos_obj": n, "n_ctr": 1 + max(0, n // 2 - 1), "lambda_min": round(float(eig.min()), 4), "lambda_max": round(float(eig.max()), 4),
                     "convexa": bool(eig.min() >= 0), "Q_efectiva": json.dumps(np.round(Qe, 4).tolist())})
with open(os.path.join(args.out, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} instancias en {args.out} ({len(CONFIGS)} configuraciones x {args.seeds} semillas); convexas: {sum(r['convexa'] for r in rows)}")
