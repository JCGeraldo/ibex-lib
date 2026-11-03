import csv, collections, statistics as S, sys, re
rows=collections.defaultdict(dict)
for r in csv.DictReader(open(sys.argv[1])):
    inst=r['instancia'].split('/')[1]; v=r['variante'].replace('art_raa_','')
    m=re.search(r' bloques=(\d+)',r['raak_stats']); ev=re.search(r'evaluados=(\d+)',r['raak_stats'])
    rows[inst][v]=dict(cells=int(r['celdas']),cpu=float(r['cpu_s']),st=r['estado'],lb=float(r['f_lb']),ub=float(r['f_ub']),
                       blk=int(m.group(1)),ev=int(ev.group(1)))
gm=S.geometric_mean
def cfg(i):
    m=re.match(r'synq_n(\d+)_d(\d+)_(\w+?)_normal_s\d',i); return int(m.group(1)),int(m.group(2)),m.group(3)
insts=sorted(rows)
out=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.append(s)
P("Barrido nivel 2 k=4,5,6 sobre synq n=8,10 (36 instancias x 3 variantes), misma sesion, 2026-11-02 20:25-23:32")
P("")
# global
for v in ['k5','k6']:
    rc=[rows[i][v]['cells']/rows[i]['k4']['cells'] for i in insts]
    rt=[rows[i][v]['cpu']/rows[i]['k4']['cpu'] for i in insts]
    ok=[i for i in insts if rows[i]['k4']['st']=='SUCCESS' and rows[i][v]['st']=='SUCCESS']
    rc2=[rows[i][v]['cells']/rows[i]['k4']['cells'] for i in ok]; rt2=[rows[i][v]['cpu']/rows[i]['k4']['cpu'] for i in ok]
    to=sum(rows[i][v]['st']!='SUCCESS' for i in insts)
    P(f"{v}/k4  todas(36): celdas gm={gm(rc):.3f} med={S.median(rc):.3f}  cpu gm={gm(rt):.3f} med={S.median(rt):.3f} | "
      f"ambas resueltas({len(ok)}): celdas gm={gm(rc2):.3f} cpu gm={gm(rt2):.3f} | timeouts {v}={to}")
P(f"timeouts k4={sum(rows[i]['k4']['st']!='SUCCESS' for i in insts)}")
P("")
P("Por configuracion (n, densidad, signos): media geometrica de celdas y CPU respecto a k4, sobre las 3 semillas; TO = timeouts k4/k5/k6")
P(f"{'config':20s} {'c5/c4':>6s} {'t5/t4':>6s} {'c6/c4':>6s} {'t6/t4':>6s} {'TO':>8s} {'bloq/prod k4':>12s} {'k5':>6s} {'k6':>6s}")
groups=collections.defaultdict(list)
for i in insts: groups[cfg(i)].append(i)
tab=[]
for g in sorted(groups):
    L=groups[g]
    f=lambda v,key: gm([rows[i][v][key]/rows[i]['k4'][key] for i in L])
    to='/'.join(str(sum(rows[i][v]['st']!='SUCCESS' for i in L)) for v in ['k4','k5','k6'])
    bpe=lambda v: S.mean(rows[i][v]['blk']/rows[i][v]['ev'] for i in L)
    P(f"n={g[0]:2d} d={g[1]:2d} {g[2]:6s} {f('k5','cells'):6.3f} {f('k5','cpu'):6.3f} {f('k6','cells'):6.3f} {f('k6','cpu'):6.3f} {to:>8s} {bpe('k4'):12.2f} {bpe('k5'):6.2f} {bpe('k6'):6.2f}")
    tab.append(dict(n=g[0],d=g[1],signos=g[2],c5_c4=round(f('k5','cells'),4),t5_t4=round(f('k5','cpu'),4),c6_c4=round(f('k6','cells'),4),t6_t4=round(f('k6','cpu'),4),to_k4=to.split('/')[0],to_k5=to.split('/')[1],to_k6=to.split('/')[2],bloques_por_eval_k4=round(bpe('k4'),3),bloques_por_eval_k5=round(bpe('k5'),3),bloques_por_eval_k6=round(bpe('k6'),3)))
P("")
P("Instancias con timeout en las tres variantes: brecha ub-lb a los 1800 s (menor es mejor)")
for i in insts:
    if all(rows[i][v]['st']!='SUCCESS' for v in ['k4','k5','k6']):
        P(f"  {i:34s} " + '  '.join(f"{v}: gap={rows[i][v]['ub']-rows[i][v]['lb']:.4g} celdas={rows[i][v]['cells']}" for v in ['k4','k5','k6']))
P("")
P("Por instancia: celdas k4, cpu k4, y cocientes k5/k4, k6/k4 (celdas, cpu)")
for i in insts:
    k4=rows[i]['k4']
    P(f"  {i:34s} k4 {k4['cells']:8d} {k4['cpu']:7.1f}{'*' if k4['st']!='SUCCESS' else ' '} | k5 {rows[i]['k5']['cells']/k4['cells']:.3f} {rows[i]['k5']['cpu']/k4['cpu']:.3f}{'*' if rows[i]['k5']['st']!='SUCCESS' else ' '} | k6 {rows[i]['k6']['cells']/k4['cells']:.3f} {rows[i]['k6']['cpu']/k4['cpu']:.3f}{'*' if rows[i]['k6']['st']!='SUCCESS' else ' '}")
P("(* = timeout a 1800 s; en esos casos celdas y CPU son las alcanzadas al corte)")
# cpu per evaluation: cpu/ev ratio
P("")
P("Costo por evaluacion afin (cpu/evaluados) respecto a k4, instancias resueltas por ambas:")
for v in ['k5','k6']:
    ok=[i for i in insts if rows[i]['k4']['st']=='SUCCESS' and rows[i][v]['st']=='SUCCESS']
    r=[(rows[i][v]['cpu']/rows[i][v]['ev'])/(rows[i]['k4']['cpu']/rows[i]['k4']['ev']) for i in ok]
    P(f"  {v}/k4: gm={gm(r):.3f} min={min(r):.3f} max={max(r):.3f} (n={len(ok)})")
w=csv.DictWriter(open(sys.argv[2],'w'),fieldnames=list(tab[0].keys())); w.writeheader(); w.writerows(tab)
open(sys.argv[3],'w').write('\n'.join(out)+'\n')
