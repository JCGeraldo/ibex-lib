"""[raak local] Parche 0012 (cota k-nomial rigurosa): compara dos corridas de tests/range_eval (misma sesion, mismos
argumentos) fila a fila: anchura afin w_aff, violaciones (viol) y microsegundos por evaluacion (us).
Uso: python3 -I parche0012_nivel1.py range_0011.csv range_0012.csv [--out carpeta]
"""
import sys, csv, math, collections, os, statistics as S
a_path, b_path = sys.argv[1], sys.argv[2]
out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
def load(p):
    rows = {}
    for r in csv.DictReader(open(p)):
        key = (r['instance'], r['func'], r['box_id'], r['scale'], r['variant'])
        rows[key] = r
    return rows
A, B = load(a_path), load(b_path)
common = sorted(set(A) & set(B))
print(f"filas: {len(A)} / {len(B)}, comunes {len(common)}")
by_var = collections.defaultdict(lambda: dict(n=0, same=0, ratio=[], viol_a=0, viol_b=0, us_a=[], us_b=[], wider=0, narrower=0, maxrel=0.0))
rows_out = []
for k in common:
    ra, rb = A[k], B[k]
    v = k[4]; d = by_var[v]
    wa, wb = float(ra['w_aff']), float(rb['w_aff'])
    d['n'] += 1
    if wa == wb: d['same'] += 1
    elif wb > wa: d['wider'] += 1
    else: d['narrower'] += 1
    if wa > 0 and math.isfinite(wa) and math.isfinite(wb):
        d['ratio'].append(wb / wa); d['maxrel'] = max(d['maxrel'], abs(wb - wa) / wa)
    d['viol_a'] += int(float(ra['viol']) > 0); d['viol_b'] += int(float(rb['viol']) > 0)
    try:
        d['us_a'].append(float(ra['us'])); d['us_b'].append(float(rb['us']))
    except ValueError: pass
    rows_out.append(dict(instance=k[0], func=k[1], box=k[2], scale=k[3], variant=v, w_0011=wa, w_0012=wb, viol_0011=ra['viol'], viol_0012=rb['viol'], us_0011=ra['us'], us_0012=rb['us']))
print(f"{'variante':10s} {'filas':>6s} {'iguales':>7s} {'mas ancha':>9s} {'mas estrecha':>12s} {'max |dw|/w':>11s} {'viol 0011':>9s} {'viol 0012':>9s} {'us 0012/0011 (med)':>18s}")
tab = []
for v in sorted(by_var):
    d = by_var[v]
    usr = S.median([b / a for a, b in zip(d['us_a'], d['us_b']) if a > 0]) if d['us_a'] else float('nan')
    print(f"{v:10s} {d['n']:6d} {d['same']:7d} {d['wider']:9d} {d['narrower']:12d} {d['maxrel']:11.2e} {d['viol_a']:9d} {d['viol_b']:9d} {usr:18.3f}")
    tab.append(dict(variante=v, filas=d['n'], iguales=d['same'], mas_ancha=d['wider'], mas_estrecha=d['narrower'], max_rel=d['maxrel'], viol_0011=d['viol_a'], viol_0012=d['viol_b'], us_ratio_med=usr))
if out:
    os.makedirs(out, exist_ok=True)
    w = csv.DictWriter(open(os.path.join(out, 'nivel1_por_variante.csv'), 'w'), fieldnames=list(tab[0].keys())); w.writeheader(); w.writerows(tab)
    w = csv.DictWriter(open(os.path.join(out, 'nivel1_filas.csv'), 'w'), fieldnames=list(rows_out[0].keys())); w.writeheader(); w.writerows(rows_out)
