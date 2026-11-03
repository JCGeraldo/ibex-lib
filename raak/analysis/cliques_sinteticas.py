"""[raak local] Tamano de clique disponible por producto en las instancias synq (punto 2 del to-do de fin de octubre:
"mejor k segun densidad").

En synq cada termino es (A_k.x)*(M_k.x) con A y M densas (la densidad rho es de Q = A'M, no de los factores), asi que
los dos factores comparten los n simbolos. En el grafo del k-nomial solo hay aristas entre simbolos i, j con diagonal
del mismo signo (a_ki*m_ki y a_kj*m_kj ambos > 0 o ambos < 0), y entre ellos la arista existe si (a_ki*m_kj + a_kj*m_ki) != 0,
lo que ocurre casi siempre. El clique maximo de cada producto es, por tanto, el tamano de la mayor clase de signo.

Salida: CSV por stdout con, por instancia, n, densidad, diagonal, numero de productos (objetivo + restricciones),
media y maximo del clique maximo por producto, y la fraccion de productos cuyo clique maximo es >= 2, 3, 4, 5.
uso: python analysis/cliques_sinteticas.py instancias/sinteticas/*.bch
"""
import sys, re, os, csv
sys.dont_write_bytecode = True

TERM = re.compile(r"\(([^()]*)\)\*\(([^()]*)\)")
COEF = re.compile(r"([+-]?\s*\d*\.?\d+(?:[eE][-+]?\d+)?)\*x(\d+)")


def coefs(s, n):
    v = [0.0] * n
    s = s.replace(" ", "")
    for m in re.finditer(r"([+-]?)(\d*\.?\d+(?:[eE][-+]?\d+)?)\*x(\d+)", s):
        v[int(m.group(3)) - 1] = float(m.group(2)) * (-1 if m.group(1) == "-" else 1)
    return v


w = csv.writer(sys.stdout)
w.writerow(["instance", "n", "densidad", "diagonal", "productos", "clique_medio", "clique_max", "frac_ge2", "frac_ge3", "frac_ge4", "frac_ge5", "simbolos_mismo_signo_medio"])
for path in sys.argv[1:]:
    name = os.path.basename(path).replace(".bch", "")
    m = re.match(r"synq_n(\d+)_d(\d+)_(\w+?)_(\w+)_s(\d+)", name)
    if not m: continue
    n = int(m.group(1)); rho = int(m.group(2)) / 100; dd = m.group(3)
    txt = open(path, encoding="utf-8").read()
    txt = re.sub(r"//[^\n]*", "", txt)
    cl = []
    for a, b in TERM.findall(txt):
        va, vb = coefs(a, n), coefs(b, n)
        pos = sum(1 for i in range(n) if va[i] * vb[i] > 0); neg = sum(1 for i in range(n) if va[i] * vb[i] < 0)
        cl.append(max(pos, neg))
    if not cl: continue
    k = len(cl)
    w.writerow([name, n, rho, dd, k, round(sum(cl) / k, 2), max(cl)] + [round(sum(1 for c in cl if c >= t) / k, 3) for t in (2, 3, 4, 5)] + [round(sum(cl) / k, 2)])
