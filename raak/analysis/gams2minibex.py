"""Converts a GAMS scalar model (MINLPLib format) to Minibex. Only what the converted instances need.
uso: python -I gams2minibex.py modelo.gms salida.bch [--relax] [--solo-objetivo e2,e5] [--cota x1=7.3,x2=56]

  --relax           binary and integer variables become continuous in their bounds (the result is a relaxation)
  --solo-objetivo   keeps the objective and only the listed equations (the result is a different problem)
  --cota            upper bounds for variables that the model leaves unbounded (must be implied by the constraints)
The objective variable is eliminated: the model must define it in one equation "expr + objvar =E= c".
"""
import sys, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument("gms"); ap.add_argument("bch"); ap.add_argument("--relax", action="store_true")
ap.add_argument("--solo-objetivo", default=None); ap.add_argument("--cota", default=""); ap.add_argument("--nota", default="")
A = ap.parse_args()
raw = open(A.gms).read()
sense = re.search(r"Solve\s+\w+\s+using\s+\S+\s+(minimizing|maximizing)\s+(\w+)", raw, re.I)
if not sense: sys.exit("no encuentro la sentencia Solve")
objvar = sense.group(2); maximize = sense.group(1).lower() == "maximizing"
txt = "\n".join(l for l in raw.split("\n") if not l.startswith("*") and not l.startswith("$"))
def decl(kind):
    out = []
    for m in re.finditer(r"^\s*" + kind + r"\s+(.*?);", txt, re.S | re.M | re.I): out += [v.strip() for v in m.group(1).replace("\n", " ").split(",") if v.strip()]
    return out
allv = decl(r"Variables"); pos = set(decl(r"Positive\s+Variables")); binv = set(decl(r"Binary\s+Variables")); intv = set(decl(r"Integer\s+Variables"))
if (binv or intv) and not A.relax: sys.exit("el modelo tiene variables discretas: usar --relax")
lo = {v: (0.0 if v in pos or v in binv or v in intv else None) for v in allv}; up = {v: (1.0 if v in binv else None) for v in allv}
for v, kind, val in re.findall(r"^\s*(\w+)\.(lo|up|fx)\s*=\s*([-+0-9.eE]+)\s*;", txt, re.M):
    if kind in ("lo", "fx"): lo[v] = float(val)
    if kind in ("up", "fx"): up[v] = float(val)
for item in filter(None, A.cota.split(",")):
    v, val = item.split("="); assert up[v] is None, v; up[v] = float(val)
FUN = {"log": "ln", "exp": "exp", "sqrt": "sqrt", "sin": "sin", "cos": "cos", "sqr": "sqr", "abs": "abs", "tan": "tan"}
def expr(s):
    s = " ".join(s.split()).replace("**", "^")
    for f in set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", s)):
        if f not in FUN: sys.exit("funcion no soportada: " + f)
        s = re.sub(r"\b" + f + r"\s*\(", FUN[f] + "(", s)
    return s
REL = {"E": "=", "L": "<=", "G": ">="}
cons = []; obj = None
keep = None if A.solo_objetivo is None else set(filter(None, A.solo_objetivo.split(",")))
for name, body in re.findall(r"^\s*(\w+)\s*\.\.(.*?);", txt, re.S | re.M):
    m = re.search(r"=([ELG])=", body, re.I); lhs, rhs, rel = body[:m.start()], body[m.end():], m.group(1).upper()
    if re.search(r"\b" + objvar + r"\b", body):
        mo = re.match(r"^(.*?)([+-])\s*" + objvar + r"\s*$", lhs.strip(), re.S)
        if not mo or rel != "E" or re.search(r"\b" + objvar + r"\b", mo.group(1) + rhs): sys.exit("definicion del objetivo no reconocida en " + name)
        rest, sg = expr(mo.group(1)), mo.group(2)          # rest (+|-) objvar = rhs
        zero = float(rhs) == 0.0 if re.fullmatch(r"\s*[-+0-9.eE]+\s*", rhs) else False
        obj = (f"-({rest})" if zero else f"({expr(rhs)}) - ({rest})") if sg == "+" else (f"({rest})" if zero else f"({rest}) - ({expr(rhs)})")
        continue
    if keep is not None and name not in keep: continue
    cons.append(f"{expr(lhs)} {REL[rel]} {expr(rhs)};")
if obj is None: sys.exit("no encuentro la ecuacion que define " + objvar)
if maximize: obj = f"-({obj})"
fmt = lambda x, inf: (inf if x is None else repr(x))
with open(A.bch, "w") as f:
    if A.nota: f.write("".join(f"// {l}\n" for l in A.nota.split("|")))
    f.write("variables\n")
    used = set(re.findall(r"\b[A-Za-z_]\w*\b", obj + " " + " ".join(cons)))
    for v in allv:
        if v != objvar and v in used: f.write(f"{v} in [{fmt(lo[v], '-oo')}, {fmt(up[v], '+oo')}];\n")
    f.write("\nminimize\n" + obj + ";\n\nconstraints\n" + "\n".join(cons) + "\nend\n")
print(f"{A.bch}: {len([v for v in allv if v != objvar and v in used])} variables ({len([v for v in allv if v in used and (v in binv or v in intv)])} discretas relajadas), {len(cons)} restricciones, objetivo de {len(obj)} caracteres")
