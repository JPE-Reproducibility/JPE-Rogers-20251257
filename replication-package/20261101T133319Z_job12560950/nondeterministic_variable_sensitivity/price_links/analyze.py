import json, pathlib, re, statistics, sys, collections
OUT = pathlib.Path(sys.argv[1]) / "redraw_pilot"
recs = [json.loads(l) for l in (OUT / "raw_responses.jsonl").read_text().splitlines() if l.strip()]
ok = [r for r in recs if "error" not in r]
err = [r for r in recs if "error" in r]
print(f"records: {len(recs)}  ok: {len(ok)}  errors: {len(err)}")
if err:
    print("  error kinds:", collections.Counter(e["error"] for e in err).most_common())

def parse(txt):
    if not txt: return None
    t = txt.strip()
    t = re.sub(r"^```(?:json)?|```$", "", t, flags=re.M).strip()
    try: return json.loads(t)
    except Exception: pass
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        try: return json.loads(m.group(0))
        except Exception: return None
    return None

def codes(v):
    if v is None: return frozenset()
    if isinstance(v, (list, tuple)): s = " ".join(map(str, v))
    else: s = str(v)
    return frozenset(re.findall(r"\b[A-V]?\d{4,5}\b", s))

by = collections.defaultdict(list)
unparsed = 0
for r in ok:
    p = parse(r["raw_response"])
    if p is None:
        unparsed += 1; continue
    by[(r["label"], r["productcode"])].append((p, r))
print(f"unparseable JSON replies: {unparsed}")

dec_flip = cpt_flip = qual_flip = 0
n = 0
conf_sd, dep_dec_match, dep_cpt_match, dep_n = [], 0, 0, 0
jacc = []
for key, lst in by.items():
    if len(lst) < 2: continue
    n += 1
    decs = {p.get("decision") for p, _ in lst}
    cpts = {codes(p.get("hcpcs_cpt")) for p, _ in lst}
    quals = {p.get("mapping_quality") for p, _ in lst}
    if len(decs) > 1: dec_flip += 1
    if len(cpts) > 1: cpt_flip += 1
    if len(quals) > 1: qual_flip += 1
    confs = [p.get("confidence") for p, _ in lst if isinstance(p.get("confidence"), (int, float))]
    if len(confs) > 1: conf_sd.append(statistics.pstdev(confs))
    # pairwise Jaccard of the CPT sets across draws
    cl = [codes(p.get("hcpcs_cpt")) for p, _ in lst]
    pw = [len(a & b) / len(a | b) for i, a in enumerate(cl) for b in cl[i+1:] if (a | b)]
    if pw: jacc.append(statistics.mean(pw))
    dep = lst[0][1]["deposited"]
    dep_n += 1
    if all(p.get("decision") == dep.get("decision") for p, _ in lst): dep_dec_match += 1
    if all(codes(p.get("hcpcs_cpt")) == codes(dep.get("hcpcs_cpt")) for p, _ in lst): dep_cpt_match += 1

print(f"\n=== RE-DRAW INSTABILITY across 5 draws, {n} items, gpt-5-mini-2025-08-07 ===")
print(f"  items where link/no_link flips      : {dec_flip}/{n}  ({dec_flip/n:.0%})")
print(f"  items where the CPT code set changes: {cpt_flip}/{n}  ({cpt_flip/n:.0%})")
print(f"  items where mapping_quality changes : {qual_flip}/{n}  ({qual_flip/n:.0%})")
if jacc: print(f"  mean pairwise Jaccard of CPT sets   : {statistics.mean(jacc):.3f}")
if conf_sd: print(f"  mean within-item SD of confidence   : {statistics.mean(conf_sd):.3f}")
print(f"\n=== vs the DEPOSITED 2025-09-22 values ({dep_n} items) ===")
print(f"  all 5 draws match deposited decision: {dep_dec_match}/{dep_n}  ({dep_dec_match/dep_n:.0%})")
print(f"  all 5 draws match deposited CPT set : {dep_cpt_match}/{dep_n}  ({dep_cpt_match/dep_n:.0%})")

pt = sum(r["usage"].get("prompt_tokens", 0) for r in ok)
ct = sum(r["usage"].get("completion_tokens", 0) for r in ok)
print(f"\n=== cost basis ===")
print(f"  calls {len(ok)} | prompt {pt:,} tok | completion {ct:,} tok")
print(f"  per call: {pt/max(len(ok),1):.0f} in / {ct/max(len(ok),1):.0f} out")
full = 337 * 5
print(f"  scaled to all 337 price-link items x5 draws = {full} calls:"
      f" ~{pt/max(len(ok),1)*full/1e6:.2f}M in / {ct/max(len(ok),1)*full/1e6:.2f}M out")
