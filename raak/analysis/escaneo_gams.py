"""Structural scan of GAMS scalar models (MINLPLib, COCONUT dag2gams) for k-nomial material.
uso: python -I escaneo_gams.py <carpeta con .gms> --out salida.csv [--maxbytes 3000000]

For every product node of the expression trees whose two factors are affine forms a(x), b(x):
  shared variables, sign classes P = {v: a_v b_v > 0}, N = {v: a_v b_v < 0}; material = max(|P|, |N|).
A product has k-nomial material when material >= 2 (two shared variables in the same sign class).
Also counted:
  fun   : affine form times f(affine form), f in {log, exp, sin, cos, sqrt, ...}, same classes with the argument of f
  lifted: z1*z2 with z1, z2 single variables, each defined by exactly one linear equality (z = affine form of others);
          classes computed after substitution (the material appears only if the defined variables are eliminated)
  square: sqr / power(.,2) / **2 of an affine form with >= 2 variables (already a block; listed for information)
"""
import sys, os, re, csv, argparse, glob

FUNCS = {"log", "exp", "sin", "cos", "sqrt", "tan", "log10", "log2", "abs", "arctan", "sinh", "cosh", "tanh", "errorf",
         "sqr", "power", "min", "max", "rpower", "vcpower", "signpower", "cvpower", "gamma", "loggamma", "entropy",
         "centropy", "mod", "div", "arcsin", "arccos", "sigmoid", "sign", "ceil", "floor", "round", "trunc", "edist", "poly"}
TOK = re.compile(r"\s*(?:(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([A-Za-z_][A-Za-z_0-9]*(?:\(\s*'[^']*'(?:\s*,\s*'[^']*')*\s*\))?)|(\*\*|=[A-Za-z]=|[-+*/^(),]))")

class Aff:
    __slots__ = ("c", "t")
    def __init__(self, c=0.0, t=None): self.c = c; self.t = t if t is not None else {}
    def nvars(self): return sum(1 for v in self.t.values() if v != 0.0)
def scale(a, s): return Aff(a.c * s, {k: v * s for k, v in a.t.items()})

class Scan:
    def __init__(self):
        self.prod = []; self.fun = []; self.sq = 0; self.varprod = []   # varprod: (z1, z2) single-variable products
        self.chain = []                                                   # lengths of chains a1*a2*...*ap of affine forms sharing variables
    def tokens(self, s):
        out = []; pos = 0; n = len(s)
        while pos < n:
            m = TOK.match(s, pos)
            if not m:
                if s[pos:].strip() == "": break
                raise ValueError("token: " + s[pos:pos + 30])
            pos = m.end()
            if m.group(1) is not None: out.append(("n", float(m.group(1))))
            elif m.group(2) is not None: out.append(("i", m.group(2)))
            else: out.append(("o", m.group(3)))
        out.append(("e", None)); return out
    # recursive descent; every parse function returns (aff or None, info) where info = ("fun", name, argaff) for f(affine)
    def parse(self, s):
        self.tk = self.tokens(s); self.p = 0
        r = self.expr()
        if self.tk[self.p][0] != "e": raise ValueError("resto: %r" % (self.tk[self.p],))
        return r
    def peek(self): return self.tk[self.p]
    def expr(self):
        acc = Aff(); ok = True; first = True; info = None; nterms = 0
        sign = 1.0
        while True:
            k, v = self.peek()
            if k == "o" and v in "+-" and (first or True):
                if v in "+-":
                    self.p += 1; sign = -1.0 if v == "-" else 1.0
            elif not first: break
            a, inf = self.term(); nterms += 1
            if a is None: ok = False
            elif ok:
                acc.c += sign * a.c
                for kk, vv in a.t.items(): acc.t[kk] = acc.t.get(kk, 0.0) + sign * vv
            info = inf if nterms == 1 and sign > 0 else None
            first = False; sign = 1.0
            k, v = self.peek()
            if not (k == "o" and v in "+-"): break
        return (acc if ok else None), (info if nterms == 1 else None)
    def term(self):
        a, inf = self.unary()
        facs = [a] if a is not None and a.nvars() else []
        while True:
            k, v = self.peek()
            if not (k == "o" and v in "*/"): break
            self.p += 1; b, infb = self.unary()
            if v == "*" and b is not None and b.nvars(): facs.append(b)
            if v == "*": a, inf = self.mul(a, inf, b, infb)
            else:
                if a is not None and b is not None and not b.nvars() and b.c != 0: a = scale(a, 1.0 / b.c)
                else: a = None; inf = None
        if len(facs) >= 3:
            common = set(k for k, v in facs[0].t.items() if v)
            for f in facs[1:]: common &= set(k for k, v in f.t.items() if v)
            if len(common) >= 2: self.chain.append((len(facs), len(common)))
        return a, inf
    def classes(self, a, b):
        P = N = S = 0
        for k, v in a.t.items():
            w = b.t.get(k, 0.0)
            if v != 0.0 and w != 0.0:
                S += 1
                if v * w > 0: P += 1
                else: N += 1
        return S, P, N
    def mul(self, a, inf, b, infb):
        if a is not None and b is not None:
            na, nb = a.nvars(), b.nvars()
            if na == 0: return scale(b, a.c), infb
            if nb == 0: return scale(a, b.c), inf
            S, P, N = self.classes(a, b)
            ka = sorted(k for k, v in a.t.items() if v); kb = sorted(k for k, v in b.t.items() if v); same = False
            if ka == kb:
                r = b.t[ka[0]] / a.t[ka[0]]
                same = all(abs(b.t[k] - r * a.t[k]) <= 1e-9 * abs(b.t[k]) for k in ka) and abs(b.c - r * a.c) <= 1e-9 * max(abs(b.c), 1e-300)
            self.prod.append((na, nb, S, P, N, same))
            if na == 1 and nb == 1 and S == 0: self.varprod.append((next(k for k, v in a.t.items() if v), next(k for k, v in b.t.items() if v)))
            return None, None
        for x, i in ((a, infb), (b, inf)):      # affine times f(affine)
            if x is not None and x.nvars() and i is not None and i[0] == "fun":
                S, P, N = self.classes(x, i[2]); self.fun.append((i[1], x.nvars(), i[2].nvars(), S, P, N))
        # constant times f(affine) keeps the info so that c*log(.)*(affine) is still seen
        if a is not None and not a.nvars() and infb is not None: return None, infb
        if b is not None and not b.nvars() and inf is not None: return None, inf
        return None, None
    def unary(self):
        k, v = self.peek()
        if k == "o" and v == "-":
            self.p += 1; a, inf = self.unary(); return (scale(a, -1.0) if a is not None else None), inf
        if k == "o" and v == "+": self.p += 1; return self.unary()
        return self.power()
    def square(self, a):
        if a is not None and a.nvars() >= 2: self.sq += 1
    def power(self):
        a, inf = self.atom()
        k, v = self.peek()
        if k == "o" and v in ("**", "^"):
            self.p += 1; b, _ = self.unary()
            if a is not None and not a.nvars() and b is not None and not b.nvars():
                try: return Aff(a.c ** b.c), None
                except Exception: return None, None
            if b is not None and not b.nvars() and b.c == 2.0: self.square(a)
            if b is not None and not b.nvars() and b.c == 1.0: return a, inf
            return None, None
        return a, inf
    def atom(self):
        k, v = self.peek(); self.p += 1
        if k == "n": return Aff(v), None
        if k == "o" and v == "(":
            a, inf = self.expr(); self.close(); return a, inf
        if k == "i":
            low = v.lower()
            if low in FUNCS and self.peek() == ("o", "("):
                self.p += 1; args = [self.expr()[0]]
                while self.peek() == ("o", ","): self.p += 1; args.append(self.expr()[0])
                self.close()
                if low == "sqr" or (low == "power" and len(args) == 2 and args[1] is not None and not args[1].nvars() and args[1].c == 2.0):
                    self.square(args[0])
                    if args[0] is not None and not args[0].nvars(): return Aff(args[0].c ** 2), None
                    return None, None
                if all(x is not None and not x.nvars() for x in args): return None, None   # constant function value: not needed
                if len(args) == 1 and args[0] is not None and args[0].nvars(): return None, ("fun", low, args[0])
                return None, None
            return Aff(0.0, {v: 1.0}), None
        raise ValueError("atomo: %r" % ((k, v),))
    def close(self):
        if self.peek() != ("o", ")"): raise ValueError("falta )")
        self.p += 1

def scan_file(path):
    txt = open(path, errors="replace").read()
    txt = "\n".join(l for l in txt.split("\n") if not l.startswith("*") and not l.startswith("$"))
    eqs = re.findall(r"^\s*([A-Za-z_][A-Za-z_0-9]*)\s*\.\.(.*?);", txt, re.S | re.M)
    sc = Scan(); lineq = []; allvars = set(); nerr = 0
    for name, body in eqs:
        m = re.search(r"=([A-Za-z])=", body)
        if not m: nerr += 1; continue
        try:
            l, _ = sc.parse(body[:m.start()]); r, _ = sc.parse(body[m.end():])
        except (ValueError, RecursionError, IndexError): nerr += 1; continue
        if l is not None and r is not None:
            a = Aff(l.c - r.c, dict(l.t))
            for k, v in r.t.items(): a.t[k] = a.t.get(k, 0.0) - v
            lineq.append((m.group(1).upper(), a))
    # lifted products: both variables defined by exactly one linear equality and absent from the other linear rows
    rows = {}
    for rel, a in lineq:
        for k, v in a.t.items():
            if v != 0.0: rows.setdefault(k, []).append((rel, a))
    def definition(z):
        r = rows.get(z, [])
        if len(r) != 1 or r[0][0] != "E": return None
        a = r[0][1]; cz = a.t[z]
        d = Aff(-a.c / cz, {k: -v / cz for k, v in a.t.items() if k != z and v != 0.0})
        return d if d.nvars() >= 2 else None
    lifted = []
    for z1, z2 in sc.varprod:
        d1, d2 = definition(z1), definition(z2)
        if d1 is not None and d2 is not None and z2 not in d1.t and z1 not in d2.t:
            lifted.append(sc.classes(d1, d2))
    low = txt.lower()
    disc = bool(re.search(r"^\s*(binary|integer)\s+variables", low, re.M))
    nv = len(set(re.findall(r"\b(?:[xbi]\d+|x\('\d+'\))", txt)))
    mat = [max(P, N) for (_, _, S, P, N, sq) in sc.prod]
    gen = [max(P, N) for (_, _, S, P, N, sq) in sc.prod if not sq]
    matf = [max(P, N) for (_, _, _, S, P, N) in sc.fun]
    matl = [max(P, N) for (S, P, N) in lifted]
    return dict(instancia=os.path.basename(path)[:-4], nvars=nv, discreta=int(disc), ecuaciones=len(eqs), errores=nerr,
                prod_afin=len(sc.prod), prod_comparten=sum(1 for p in sc.prod if p[2] >= 1), prod_material=sum(1 for m in mat if m >= 2),
                max_clase=max(mat, default=0), suma_material=sum(m for m in mat if m >= 2),
                genuino_material=sum(1 for m in gen if m >= 2), genuino_max_clase=max(gen, default=0),
                cadenas=len(sc.chain), cadena_max_factores=max((c[0] for c in sc.chain), default=0), cadena_max_comunes=max((c[1] for c in sc.chain), default=0),
                fun_prod=len(sc.fun), fun_material=sum(1 for m in matf if m >= 2), fun_max_clase=max(matf, default=0),
                fun_tipos=" ".join(sorted({f[0] for f in sc.fun if max(f[4], f[5]) >= 2})),
                lifted_prod=len(lifted), lifted_material=sum(1 for m in matl if m >= 2), lifted_max_clase=max(matl, default=0),
                cuadrados_afines=sc.sq)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--out", required=True); ap.add_argument("--maxbytes", type=int, default=3000000)
    A = ap.parse_args(); sys.setrecursionlimit(20000)
    files = sorted(glob.glob(os.path.join(A.dir, "*.gms"))); rows = []; skipped = []
    for i, f in enumerate(files):
        if os.path.getsize(f) > A.maxbytes: skipped.append(os.path.basename(f)); continue
        try: rows.append(scan_file(f))
        except Exception as e: skipped.append(os.path.basename(f) + ":" + type(e).__name__)
        if i % 200 == 0: print(i, len(files), file=sys.stderr, flush=True)
    with open(A.out, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"archivos {len(files)}  escaneados {len(rows)}  omitidos {len(skipped)}")
    print("omitidos:", " ".join(skipped[:60]))
