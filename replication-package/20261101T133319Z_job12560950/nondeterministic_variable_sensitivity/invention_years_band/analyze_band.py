import json, pathlib, re, statistics, sys, collections
OUT=pathlib.Path(sys.argv[1])/"iy_band"; THR=1959
yr=lambda t:(lambda m:int(m.group(1)) if m else None)(re.search(r"Year:\s*(\d{4})",t or ""))
recs=[json.loads(l) for l in (OUT/"raw_responses.jsonl").read_text().splitlines() if l.strip()]
ok=[r for r in recs if "error" not in r]
print(f"records {len(recs)} ok {len(ok)} errors {len(recs)-len(ok)}")
by=collections.defaultdict(list)
for r in ok:
    y=yr(r["raw_response"])
    if y: by[r["pc"]].append((r["draw"],y,r["deposited_year"],r["in_band"]))
nb=sum(1 for v in by.values() if v[0][3]); nc=len(by)-nb
print(f"items with >=1 parsed draw: {len(by)}  (in-band {nb}, control {nc})")

cross=inband_move=ctrl_move=ctrl_cross=0
counts_per_draw=collections.Counter(); dep_over=0
for pc,v in by.items():
    dep=v[0][2]; band=v[0][3]
    ys=[y for _,y,_,_ in v]
    moved=len(set(ys))>1
    over=[(y<THR) for y in ys]
    crossed=len(set(over))>1
    if band:
        inband_move+=moved; cross+=crossed
    else:
        ctrl_move+=moved; ctrl_cross+=crossed
    if dep<THR: dep_over+=1
    for d,y,_,_ in v: counts_per_draw[d]+= (1 if y<THR else 0)

print(f"\n=== IN-BAND (|deposited year - {THR}| <= 6), n={nb} ===")
print(f"  year changes across draws              : {inband_move}/{nb} ({inband_move/max(nb,1):.0%})")
print(f"  CROSSES the 60-year threshold          : {cross}/{nb} ({cross/max(nb,1):.0%})")
print(f"\n=== OUT-OF-BAND CONTROL, n={nc} ===")
print(f"  year changes across draws              : {ctrl_move}/{max(nc,1)} ({ctrl_move/max(nc,1):.0%})")
print(f"  CROSSES the threshold                  : {ctrl_cross}/{max(nc,1)} ({ctrl_cross/max(nc,1):.0%})")
print(f"    -> {'confirms the band captures essentially all threshold movement' if ctrl_cross==0 else 'WARNING: out-of-band items also cross; widen the band'}")
print(f"\n=== over-60 count among the sampled codes ===")
print(f"  deposited: {dep_over}")
cs=[counts_per_draw[d] for d in sorted(counts_per_draw)]
print(f"  per draw : {cs}")
if len(cs)>1:
    print(f"  mean {statistics.mean(cs):.1f}  SD {statistics.pstdev(cs):.2f}  range {min(cs)}-{max(cs)}")
    print(f"  shift vs deposited: {statistics.mean(cs)-dep_over:+.1f} on a base of {dep_over}")
pt=sum(r["usage"].get("prompt_tokens",0) for r in ok); ct=sum(r["usage"].get("completion_tokens",0) for r in ok)
print(f"\ntokens: prompt {pt:,} completion {ct:,} | per call {pt/max(len(ok),1):.0f} in / {ct/max(len(ok),1):.0f} out")
