"""[raak local] Clasifica el objetivo de cada .bch: 'sin_objetivo' (satisfaccion), 'variable' (minimize x_i: forma
epigrafo, el objetivo no aporta estructura), 'lineal' (solo sumas y productos por constante), 'no_lineal'.
Para la forma epigrafo cuenta en cuantas restricciones aparece la variable objetivo.
uso: python clasificar_objetivos.py <carpetas o archivos .bch>...  -> CSV por stdout
"""
import sys, re, os, glob
sys.dont_write_bytecode = True

TOK = re.compile(r"\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?|[A-Za-z_][A-Za-z_0-9]*|<=|>=|[-+*/^(),;=<>\[\]]")
FUNCS = {"exp", "ln", "log", "sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "abs", "sqr", "sign", "min", "max", "pow", "atan2"}


def classify(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"//[^\n]*", "", txt); txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    m = re.search(r"\b(minimize|maximize)\b(.*?);", txt, flags=re.S | re.I)
    if not m:
        return dict(archivo=os.path.basename(path), clase="sin_objetivo", objetivo="", var_obj="", ctrs_con_var_obj="", n_ctr=len(re.findall(r"(<=|>=|=)\s*[-\d]", txt)))
    obj = m.group(2).strip()
    cons = re.search(r"\bconstraints\b(.*?)\bend\b", txt, flags=re.S | re.I)
    ctrs = [c for c in (cons.group(1) if cons else "").split(";") if re.search(r"(<=|>=|=)", c)]
    toks = TOK.findall(obj)
    idents = [t for t in toks if re.match(r"[A-Za-z_]", t)]
    vars_ = [t for t in idents if t not in FUNCS]
    nonlinear = any(t in FUNCS or t in ("^", "/") for t in toks) or _var_times_var(toks, set(vars_))
    bare = re.sub(r"\s+", "", obj)
    if re.fullmatch(r"-?[A-Za-z_][A-Za-z_0-9]*(\([0-9]+\))?", bare) or re.fullmatch(r"-?\(?[A-Za-z_][A-Za-z_0-9]*\)?", bare):
        v = re.sub(r"[-()]", "", bare)
        n_with = sum(1 for c in ctrs if re.search(r"\b" + re.escape(v) + r"\b", c))
        return dict(archivo=os.path.basename(path), clase="variable", objetivo=bare, var_obj=v, ctrs_con_var_obj=n_with, n_ctr=len(ctrs))
    return dict(archivo=os.path.basename(path), clase="no_lineal" if nonlinear else "lineal", objetivo=obj[:60].replace("\n", " "), var_obj="", ctrs_con_var_obj="", n_ctr=len(ctrs))


def _var_times_var(toks, vars_):
    for i, t in enumerate(toks):
        if t == "*":
            l = toks[i - 1] if i > 0 else ""; r = toks[i + 1] if i + 1 < len(toks) else ""
            if (l in vars_ or l == ")") and (r in vars_ or r == "("): return True
    return False


files = []
for a in sys.argv[1:]:
    files += sorted(glob.glob(os.path.join(a, "*.bch"))) if os.path.isdir(a) else [a]
print("set,archivo,clase,objetivo,var_obj,ctrs_con_var_obj,n_ctr")
for f in files:
    r = classify(f); s = os.path.basename(os.path.dirname(f))
    print(",".join([s, r["archivo"], r["clase"], '"' + str(r["objetivo"]).replace('"', "'") + '"', str(r["var_obj"]), str(r["ctrs_con_var_obj"]), str(r["n_ctr"])]))
