"""[raak local] Marca que instancias .bch tienen un producto con una funcion trascendente (sin, cos, tan, exp, sinh, cosh, tanh)
o con ln/log en alguno de sus factores. Solo mira el texto: no detecta divisiones ni potencias (xinshe-yang2, mishra*).
uso: python analysis/productos_funciones.py <carpetas>...  -> CSV por stdout (set, instance, prod_trig_exp, prod_log)
"""
import re, sys, os, glob, csv
# marca instancias cuyo texto tiene un producto con una funcion trascendente en algun factor
TRIG = r"(sin|cos|tan|exp|sinh|cosh|tanh)\s*\("
LOG = r"(ln|log)\s*\("
def strip(txt):
    txt = re.sub(r"//[^\n]*", "", txt); return re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
def has_prod(txt, pat):
    # producto: f(...)*... o ...*f(...)  (factor izquierdo o derecho)
    return bool(re.search(r"\*\s*" + pat, txt) or re.search(r"\)\s*\*", txt) and re.search(pat, txt) and _close_prod(txt, pat))
def _close_prod(txt, pat):
    # f( ... ) * : buscar funcion cuyo parentesis de cierre va seguido de '*'
    for m in re.finditer(pat, txt):
        i = m.end() - 1; depth = 0
        for j in range(i, len(txt)):
            if txt[j] == '(': depth += 1
            elif txt[j] == ')':
                depth -= 1
                if depth == 0:
                    k = j + 1
                    while k < len(txt) and txt[k] in " \t\n": k += 1
                    if k < len(txt) and txt[k] == '*': return True
                    break
    return False
w = csv.writer(sys.stdout); w.writerow(["set", "instance", "prod_trig_exp", "prod_log"])
for d in sys.argv[1:]:
    for f in sorted(glob.glob(os.path.join(d, "*.bch"))):
        t = strip(open(f, encoding="utf-8", errors="replace").read())
        w.writerow([os.path.basename(d), os.path.basename(f), int(has_prod(t, TRIG)), int(has_prod(t, LOG))])
