# -*- coding: utf-8 -*-
"""Lector minimo del formato QPLIB.

Objetivo QPLIB:  sense  1/2 x^T Q0 x + b0^T x + q0
Q0 se almacena por TRIANGULO INFERIOR, indices 1-based.

Para la aritmetica afin usamos la forma  x^T Qeff x  con  Qeff = 0.5 * Q0sym,
que preserva exactamente la razon diagonal/fuera-de-diagonal (lo unico que
importa para el presupuesto diagonal del metodo k-nomial).

Devuelve tambien la caja [lb, ub]. Reglas para obtener una caja FINITA:
  - cotas explicitas finitas del archivo;
  - variables binarias  -> [0, 1];
  - si queda alguna cota infinita, box_ok=False (la instancia se descarta:
    la aritmetica afin necesita un dominio acotado).
"""
import io
import re

import numpy as np

INF = 1e300


def _tok(line):
    """Quita el comentario '#...' y devuelve los campos."""
    return line.split('#', 1)[0].split()


def read_qplib(path):
    raw = io.open(path, encoding='utf-8', errors='replace').read().splitlines()
    lines = [l for l in raw if l.strip()]

    name = lines[0].strip()
    probtype = lines[1].strip()          # p.ej. QCL: O=Q, V=C, C=L
    sense = lines[2].strip()
    p = 3
    n = int(_tok(lines[p])[0]); p += 1

    obj_type, var_type, con_type = probtype[0], probtype[1], probtype[2]
    m = 0
    if con_type != 'N':                  # sin restricciones no hay linea de m
        m = int(_tok(lines[p])[0]); p += 1

    nnz = int(_tok(lines[p])[0]); p += 1
    Q = np.zeros((n, n))
    for k in range(nnz):
        f = _tok(lines[p + k])
        i, j, v = int(f[0]) - 1, int(f[1]) - 1, float(f[2])
        Q[i, j] = v
        Q[j, i] = v                      # triangulo inferior -> simetrica
    p += nnz

    # --- cotas: se localizan por el texto del comentario (presente en QPLIB) ---
    lb = np.full(n, -np.inf)
    ub = np.full(n, np.inf)

    def section(tag):
        """(valor_por_defecto, {idx: valor}) de la seccion cuyo comentario
        contiene `tag`, o None si no aparece."""
        for q in range(p, len(lines)):
            if tag in lines[q]:
                default = float(_tok(lines[q])[0])
                cnt = int(_tok(lines[q + 1])[0])
                over = {}
                for k in range(cnt):
                    f = _tok(lines[q + 2 + k])
                    over[int(f[0]) - 1] = float(f[1])
                return default, over
        return None

    lo = section('default variable lower bound')
    hi = section('default variable upper bound')
    if lo is not None:
        d, ov = lo
        lb[:] = d
        for i, v in ov.items(): lb[i] = v
    if hi is not None:
        d, ov = hi
        ub[:] = d
        for i, v in ov.items(): ub[i] = v

    # binarias / enteras acotadas implicitamente
    if var_type == 'B':
        lb = np.where(np.isfinite(lb) & (lb > -INF), np.maximum(lb, 0.0), 0.0)
        ub = np.where(np.isfinite(ub) & (ub < INF), np.minimum(ub, 1.0), 1.0)

    lb = np.where(lb <= -INF, -np.inf, lb)
    ub = np.where(ub >= INF, np.inf, ub)
    box_ok = bool(np.all(np.isfinite(lb)) and np.all(np.isfinite(ub)))

    return dict(name=name, probtype=probtype, sense=sense, n=n, m=m,
                obj_type=obj_type, var_type=var_type, con_type=con_type,
                Q0=Q, Qeff=0.5 * Q, lb=lb, ub=ub, box_ok=box_ok, nnz=nnz)


def graph_stats(Q, tol=0.0):
    """Densidad, triangulos y clustering global del grafo de dispersion de Q
    (solo fuera de la diagonal)."""
    A = (np.abs(Q) > tol).astype(np.int64)
    np.fill_diagonal(A, 0)
    n = A.shape[0]
    edges = A.sum() / 2
    dens = edges / (n * (n - 1) / 2) if n > 1 else 0.0
    tri = np.trace(A @ A @ A) / 6.0
    deg = A.sum(1)
    paths = (deg * (deg - 1) / 2).sum()
    cc = (3.0 * tri / paths) if paths > 0 else 0.0
    return dict(density=float(dens), edges=int(edges), triangles=float(tri),
                clustering=float(cc), maxdeg=int(deg.max()) if n else 0)
