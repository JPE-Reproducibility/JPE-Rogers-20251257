import json, pathlib, re, statistics, sys, collections
# One or more response files, pooled. With no argument, both deposited batches are read, which is
# the ten-draw census; pass explicit paths to analyse a subset.
HERE = pathlib.Path(__file__).parent
srcs = [pathlib.Path(a) for a in sys.argv[1:]] or [
    HERE / "raw_responses.jsonl", HERE / "pl_full2" / "raw_responses.jsonl"]
srcs = [p for p in srcs if p.exists()]
if not srcs:
    sys.exit("no response files found")
recs = [json.loads(l) for p in srcs for l in p.read_text().splitlines() if l.strip()]
NDRAWS = len({r.get("draw") for r in recs if "draw" in r})
print(f"pooled {len(srcs)} response file(s), {len(recs)} calls, "
      f"{NDRAWS} draws", flush=True)

def parse(t):
    t = re.sub(r"^```(?:json)?|```$", "", (t or "").strip(), flags=re.M).strip()
    try: return json.loads(t)
    except Exception:
        m = re.search(r"\{.*\}", t, re.S)
        return json.loads(m.group(0)) if m else None
def codes(v):
    s = " ".join(map(str, v)) if isinstance(v, (list, tuple)) else str(v or "")
    return frozenset(re.findall(r"\b[A-V]?\d{4,5}\b", s))

by = collections.defaultdict(list)
for r in recs:
    by[(r["label"], r["productcode"])].append((parse(r["raw_response"]), r))

cat = collections.Counter()
cpt_stable_among_link = cpt_total_among_link = 0
jac_all, jac_link = [], []
dep_rows = []
for (label, pc), lst in by.items():
    decs = [p.get("decision") for p, _ in lst]
    sets = [codes(p.get("hcpcs_cpt")) for p, _ in lst]
    dep  = lst[0][1]["deposited"]
    if len(set(decs)) > 1:        cat["decision MIXED across draws"] += 1
    elif decs[0] == "link":       cat["unanimous link"] += 1
    else:                         cat["unanimous no_link"] += 1
    # Jaccard over ALL items, counting two empty sets as perfect agreement
    pw = [(1.0 if not (a|b) else len(a&b)/len(a|b))
          for i,a in enumerate(sets) for b in sets[i+1:]]
    jac_all.append(statistics.mean(pw))
    if len(set(decs)) == 1 and decs[0] == "link":
        cpt_total_among_link += 1
        if len(set(sets)) == 1: cpt_stable_among_link += 1
        pwl = [len(a&b)/len(a|b) for i,a in enumerate(sets) for b in sets[i+1:] if (a|b)]
        if pwl: jac_link.append(statistics.mean(pwl))
    dep_rows.append((label, pc, dep.get("decision"), decs,
                     codes(dep.get("hcpcs_cpt")), sets))

n = len(by)
print(f"=== DECISION STABILITY, {n} items x {NDRAWS} draws, gpt-5-mini-2025-08-07 ===")
for k, v in cat.most_common():
    print(f"  {k:32s} {v:3d}/{n}  ({v/n:.0%})")
print(f"\n=== CPT CODE SET ===")
print(f"  mean pairwise Jaccard, ALL items (empty==empty counts as agreement): {statistics.mean(jac_all):.3f}")
if jac_link:
    print(f"  mean pairwise Jaccard, items unanimously 'link' (n={len(jac_link)}) : {statistics.mean(jac_link):.3f}")
print(f"  of the {cpt_total_among_link} unanimous-'link' items, identical code set in all {NDRAWS} draws: "
      f"{cpt_stable_among_link} ({cpt_stable_among_link/max(cpt_total_among_link,1):.0%})")

dd = sum(1 for *_ , d, decs, _, _ in [(r[0],r[1],r[2],r[3],r[4],r[5]) for r in dep_rows]
         if all(x == d for x in decs))
print(f"\n=== vs DEPOSITED 2025-09-22 ===")
print(f"  all {NDRAWS} draws reproduce deposited decision: {dd}/{n} ({dd/n:.0%})")
drift = sum(1 for _,_,d,decs,_,_ in dep_rows if len(set(decs))==1 and decs[0]!=d)
print(f"  items STABLE across draws but DIFFERENT from deposited (true drift): {drift}/{n} ({drift/n:.0%})")
print(f"  -> so disagreement with the deposited file is "
      f"{'almost entirely' if drift <= 2 else 'partly'} internal instability, not model drift")
by_lab = collections.Counter()
for label, pc, d, decs, _, _ in dep_rows:
    if len(set(decs)) > 1: by_lab[label] += 1
tot = collections.Counter(l for l, _ in by.keys())
print(f"\n=== flip rate by direction ===")
for l in sorted(tot):
    print(f"  {l}: {by_lab[l]}/{tot[l]} items flip the decision ({by_lab[l]/tot[l]:.0%})")
