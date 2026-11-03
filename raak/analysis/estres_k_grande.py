import re,glob,os,sys,csv
S=os.path.dirname(os.path.abspath(__file__))
def parse(f):
    t=re.sub(r'\x1b\[[0-9;]*m','',open(f,errors='replace').read())
    cpu=re.search(r'cpu time used:\s+([0-9.]+)',t); ev=re.search(r'evaluados=(\d+)',t); cells=re.search(r'number of cells:\s+(\d+)',t)
    ex=re.search(r'exit=(\d+) wall=([0-9.]+)',t)
    return dict(cpu=float(cpu.group(1)) if cpu else None, ev=int(ev.group(1)) if ev else None, cells=int(cells.group(1)) if cells else None,
                exit=int(ex.group(1)) if ex else None, wall=float(ex.group(2)) if ex else None)
rows=[]
for f in sorted(glob.glob(S+'/logs/*.log')):
    m=re.match(r'n(\d+)_k(\d+)',os.path.basename(f)); d=parse(f); rows.append(dict(binario='0010',n=int(m.group(1)),k=int(m.group(2)),presupuesto=0,**d))
for f in sorted(glob.glob(S+'/logs2/*.log')):
    m=re.match(r'n(\d+)_k(\d+)_b(\d+)',os.path.basename(f)); d=parse(f); rows.append(dict(binario='0011',n=int(m.group(1)),k=int(m.group(2)),presupuesto=int(m.group(3)),**d))
for r in rows:
    r['us_por_eval']=round(r['cpu']*1e6/r['ev']) if r['cpu'] and r['ev'] else None
    r['estado']='ok' if r['exit']==0 and r['cpu'] else ('matada a 300 s' if r['exit']==124 else 'sin salida')
rows.sort(key=lambda r:(r['n'],r['binario'],r['k'],r['presupuesto']))
w=csv.DictWriter(open(sys.argv[1],'w'),fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# markdown table: per n, columns k0 | k6 | k8 | k=n for each binary/budget
print("| n | material (medio / máx) | binario | k=0 | k=6 | k=8 | k=n |")
print("|---|---|---|---|---|---|---|")
mat={12:'7.1 / 9',15:'8.8 / 12',20:'10.9 / 16',30:'15.8 / 22'}
def cell(r):
    if r is None: return '—'
    if r['us_por_eval'] is None: return 'matada a 300 s' if r['exit']==124 else f"{r['ev']} eval. en {r['wall']:.0f} s"
    return f"{r['us_por_eval']} µs ({r['cells']} celdas)"
for n in (12,15,20,30):
    for lab,b,bud in (('0010 (exhaustiva)','0010',0),('0011 sin presupuesto','0011',0),('0011, presupuesto 2000','0011',2000)):
        get=lambda k: next((r for r in rows if r['n']==n and r['binario']==b and r['k']==k and (r['presupuesto']==bud or k==0)),None)
        print(f"| {n} | {mat[n]} | {lab} | {cell(get(0))} | {cell(get(6))} | {cell(get(8))} | {cell(get(n))} |")
