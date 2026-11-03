"""[raak local] Conteo estatico de operaciones no lineales en archivos .bch (minibex), aproximado: la sintaxis
parentizada de coconut cuenta ((c*x1)*x2) como producto compuesto. El dato fiable es range_eval (nivel 1).
Uso: python contar_multiplicaciones.py <carpeta_o_archivos...>  -> CSV por stdout.
Columnas: archivo, n_vars, n_ctr, mult_nc (productos con ambos operandos no constantes),
mult_comp (al menos un operando es una expresion compuesta: parentesis o funcion),
mult_vv (variable * variable), sqr_comp (cuadrado/potencia de expresion compuesta),
sqr_var, div_nc (division con denominador no constante), trig, explog, otras."""
import sys, re, os, glob

TOK = re.compile(r"\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?|[A-Za-z_][A-Za-z_0-9]*|<=|>=|:=|[-+*/^(),;=<>\[\]{}]")
FUNCS = {"exp", "ln", "log", "sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "abs", "sqr", "sign", "min", "max", "pow", "atan2", "chi", "integer"}
KEYW = {"constants", "variables", "minimize", "maximize", "constraints", "end", "in", "function", "return", "Constants", "Variables", "Minimize", "Maximize", "Constraints", "End"}


def analyze(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"//[^\n]*", "", txt)
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    low = txt
    # secciones
    m_const = re.search(r"\bconstants\b(.*?)(?=\bvariables\b)", low, flags=re.S | re.I)
    m_vars = re.search(r"\bvariables\b(.*?)(?=\bminimize\b|\bmaximize\b|\bconstraints\b)", low, flags=re.S | re.I)
    m_body = re.search(r"(\bminimize\b|\bmaximize\b|\bconstraints\b)(.*?)(?=\bend\b|$)", low, flags=re.S | re.I)
    consts = set(re.findall(r"([A-Za-z_][A-Za-z_0-9]*)\s*(?:\[[^\]]*\])?\s*=", m_const.group(1))) if m_const else set()
    vars_ = set(re.findall(r"([A-Za-z_][A-Za-z_0-9]*)\s*(?:\[[^\]]*\])*\s*(?:in\b|;|,)", m_vars.group(1))) if m_vars else set()
    vars_ -= KEYW
    body = m_body.group(2) if m_body else ""
    n_ctr = len(re.findall(r"(<=|>=|=)", re.sub(r"\bconstraints\b.*", "", body, flags=re.S))) if False else body.count(";")
    toks = TOK.findall(body)
    c = dict(mult_nc=0, mult_comp=0, mult_vv=0, sqr_comp=0, sqr_var=0, div_nc=0, trig=0, explog=0, otras=0)

    def kind_left(i):
        t = toks[i]
        if t == ")": return "comp"
        if t == "]":  # indexado x[i]
            return "var"
        if re.match(r"^[\d.]", t): return "const"
        if t in consts: return "const"
        if t in vars_: return "var"
        return "var" if t not in FUNCS else "comp"

    def kind_right(i):
        if i >= len(toks): return "const"
        t = toks[i]
        if t == "-" or t == "+": return kind_right(i + 1)
        if t == "(": return "comp"
        if re.match(r"^[\d.]", t): return "const"
        if t in FUNCS: return "comp"
        if t in consts: return "const"
        if t in vars_: return "var"
        return "var"

    for i, t in enumerate(toks):
        if t == "*":
            l, r = kind_left(i - 1), kind_right(i + 1)
            if l == "const" or r == "const": continue
            c["mult_nc"] += 1
            if l == "comp" or r == "comp": c["mult_comp"] += 1
            else: c["mult_vv"] += 1
        elif t == "/":
            if kind_right(i + 1) != "const": c["div_nc"] += 1
        elif t == "^":
            l = kind_left(i - 1)
            if l == "comp": c["sqr_comp"] += 1
            elif l == "var": c["sqr_var"] += 1
        elif t in ("sin", "cos", "tan", "asin", "acos", "atan", "atan2"): c["trig"] += 1
        elif t in ("exp", "ln", "log", "sqrt"): c["explog"] += 1
        elif t == "sqr":
            if i + 1 < len(toks) and toks[i + 1] == "(":
                # sqr(expr): compuesto salvo que sea sqr(var)
                if i + 3 < len(toks) and toks[i + 3] == ")" and kind_left(i + 2) == "var": c["sqr_var"] += 1
                else: c["sqr_comp"] += 1
        elif t in ("abs", "sinh", "cosh", "tanh", "min", "max", "pow"): c["otras"] += 1
    return dict(archivo=os.path.basename(path), n_vars=len(vars_), n_ctr=n_ctr, **c)


files = []
for a in sys.argv[1:]:
    files += sorted(glob.glob(os.path.join(a, "*.bch"))) if os.path.isdir(a) else [a]
cols = ["archivo", "n_vars", "n_ctr", "mult_nc", "mult_comp", "mult_vv", "sqr_comp", "sqr_var", "div_nc", "trig", "explog", "otras"]
print(",".join(cols))
for f in files:
    try:
        r = analyze(f); print(",".join(str(r[k]) for k in cols))
    except Exception as e:
        print(f"{os.path.basename(f)},ERROR,{e}", file=sys.stderr)
