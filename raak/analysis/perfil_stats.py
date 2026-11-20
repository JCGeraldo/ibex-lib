import csv, sys, os, collections
d = sys.argv[1]; D = collections.defaultdict(dict)
for fam in ["reales", "sinteticas", "sinteticas-log", "sinteticas-fun"]:
    for r in csv.DictReader(open(os.path.join(d, fam, "runs.csv"))): D[fam + "/" + r["instancia"].split("/")[-1]][r["variante"]] = r
ok = lambda r: r["estado"] == "SUCCESS"; c = lambda r: max(float(r["celdas"]), 1.0)
V = ["art_af2_k0", "art_raa_k0", "art_raa_k2", "art_raa_k3", "art_raa_k4", "art_raa_k6"]
any_ = {i: v for i, v in D.items() if any(ok(v[x]) for x in V)}
print("instancias", len(D), "resueltas por al menos una", len(any_))
best = lambda v: min(c(v[x]) for x in V if ok(v[x]))
k6 = "art_raa_k6"
print("k6 menor arbol:", sum(ok(v[k6]) and c(v[k6]) <= best(v) for v in any_.values()), " dentro de 5%:", sum(ok(v[k6]) and c(v[k6]) <= 1.05 * best(v) for v in any_.values()))
for x in V: print(x, "mejor:", sum(ok(v[x]) and c(v[x]) <= best(v) for v in any_.values()), "5%:", sum(ok(v[x]) and c(v[x]) <= 1.05 * best(v) for v in any_.values()))
both = {i: v for i, v in D.items() if ok(v[k6]) and ok(v["art_raa_k0"])}
worse = [(i, c(v[k6]), c(v["art_raa_k0"])) for i, v in both.items() if c(v[k6]) > c(v["art_raa_k0"])]
print("ambas", len(both), "k6 > k0:", len(worse), [(i, a, b, round(a / b, 3)) for i, a, b in worse])
for i in ["sinteticas-fun/synt_n08_d90_s3", "sinteticas-fun/synt_n10_d90_s3", "sinteticas-fun/synt_n10_d90_s2", "sinteticas/synq_n08_d20_pos_normal_s3"]:
    print(i, [(x[8:], D[i][x]["estado"][:4], D[i][x]["celdas"], D[i][x]["cpu_s"][:7]) for x in V])
