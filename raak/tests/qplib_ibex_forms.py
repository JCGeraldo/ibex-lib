# -*- coding: utf-8 -*-
"""Formulaciones de la parte cuadratica de instancias QPLIB para evaluarlas con la
aritmetica afin de ibex-affine (evaluador C++ qplib_affine_eval.cpp).

Para cada instancia con caja finita escribe la forma x^T Qeff x (convencion de
qplib_reader: el objetivo QPLIB es 1/2 x^T Q0 x = x^T Qeff x) en varias
formulaciones, todas iguales como funciones salvo redondeo:

  mono : sum_i Q_ii x_i^2 + sum_{i<j} 2 Q_ij x_i x_j         (monomios, como un .bch)
  kn2  : reescritura k-nomial de knomial.py con k=2: Q_res en monomios + sum c (u^T x)^2
  kn3  : idem con k=3
  eig  : sum_k lambda_k (v_k^T x)^2                           (descomposicion espectral)

Formato de cada archivo <id>__<forma>.txt:
  n
  n lineas "lb ub"
  T
  T terminos:  "Q c i"          c * x_i^2
               "P c i j"        c * x_i * x_j
               "S c m i1 a1 ..."  c * (sum a_k x_ik)^2

Ademas guarda predicciones.json con la sobrestimacion en forma cerrada del paper
(af2_error, que equivale a 2 x radio afin) y la discrepancia de cada identidad.
La parte lineal del objetivo se omite: en aritmetica afin es exacta y no cambia el radio.

Uso: python qplib_ibex_forms.py OUT_DIR --knomial RUTA/knomial.py
"""
import argparse
import glob
import importlib.util
import json
import os
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qplib_reader as R  # noqa: E402


def fr(x):
    return repr(float(x))


def load_knomial(path):
    spec = importlib.util.spec_from_file_location("knomial_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mono_terms(Q):
    n = Q.shape[0]
    terms = [f"Q {fr(Q[i, i])} {i}" for i in range(n) if Q[i, i] != 0.0]
    iu, ju = np.nonzero(np.triu(Q, 1))
    terms += [f"P {fr(2.0 * Q[i, j])} {i} {j}" for i, j in zip(iu, ju)]
    return terms


def block_terms(blocks):
    terms = []
    for c, u in blocks:
        u = np.asarray(u, float)
        idx = np.nonzero(u)[0]
        if c == 0.0 or len(idx) == 0:
            continue
        terms.append(f"S {fr(c)} {len(idx)} " + " ".join(f"{i} {fr(u[i])}" for i in idx))
    return terms


def write_form(path, lb, ub, terms):
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(f"{len(lb)}\n")
        for a, b in zip(lb, ub):
            f.write(f"{fr(a)} {fr(b)}\n")
        f.write(f"{len(terms)}\n")
        f.write("\n".join(terms))
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--knomial", required=True, help="ruta a raa_lib/knomial.py")
    ap.add_argument("--nmax", type=int, default=10**9)
    args = ap.parse_args()

    kn = load_knomial(args.knomial)
    os.makedirs(args.out, exist_ok=True)
    preds = []
    files = sorted(glob.glob(os.path.join(HERE, "inst", "*.qplib")))
    for f in files:
        iid = re.search(r"QPLIB_(\d+)", f).group(1)
        d = R.read_qplib(f)
        if not d["box_ok"] or d["n"] > args.nmax:
            continue
        Q, n, lb, ub = d["Qeff"], d["n"], d["lb"], d["ub"]
        w = ub - lb
        rec = dict(id=iid, probtype=d["probtype"], n=n, diag_nz=int(np.count_nonzero(np.diag(Q))),
                   cross_nz=int(np.count_nonzero(np.triu(Q, 1))))
        forms = {"mono": mono_terms(Q)}
        rec["af2_mono"] = kn.af2_error(Q, [], w)
        for k in (2, 3):
            t0 = time.perf_counter()
            Qr, bl = kn.knomial(Q, w, max_k=k)
            rec[f"py_s_kn{k}"] = time.perf_counter() - t0
            forms[f"kn{k}"] = mono_terms(Qr) + block_terms(bl)
            rec[f"af2_kn{k}"] = kn.af2_error(Qr, bl, w)
            rec[f"blocks_kn{k}"] = len(bl)
            rec[f"ident_kn{k}"] = float(np.abs(kn.reconstruct(Qr, bl) - Q).max())
        lam, V = np.linalg.eigh(Q)
        keep = np.abs(lam) > 1e-12 * max(1.0, float(np.abs(lam).max()))
        eb = [(float(lam[k]), V[:, k]) for k in np.nonzero(keep)[0]]
        forms["eig"] = block_terms(eb)
        rec["af2_eig"] = kn.block_error(eb, w)
        rec["ident_eig"] = float(np.abs(kn.reconstruct(np.zeros_like(Q), eb) - Q).max())
        for name, terms in forms.items():
            write_form(os.path.join(args.out, f"{iid}__{name}.txt"), lb, ub, terms)
            rec[f"terms_{name}"] = len(terms)
        preds.append(rec)
        print(f"{iid:>6} n={n:<4} bloques k2={rec['blocks_kn2']:<5} k3={rec['blocks_kn3']:<5}"
              f" knomial k3 {rec['py_s_kn3']:.1f}s", flush=True)
    with open(os.path.join(args.out, "predicciones.json"), "w", encoding="utf-8") as f:
        json.dump(preds, f, indent=1)
    print(f"{len(preds)} instancias -> {args.out}")


if __name__ == "__main__":
    main()
