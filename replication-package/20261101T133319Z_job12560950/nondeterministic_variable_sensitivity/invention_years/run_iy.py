import csv, json, pathlib, re, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
SCR = pathlib.Path(sys.argv[1]); OUT = SCR/"iy_pilot"
MODEL, DRAWS = "gpt-4o-2024-08-06", 5     # the snapshot the bare alias resolved to in Sept 2024

KEY = re.findall(r"sk-[A-Za-z0-9_\-]{20,}", pathlib.Path(
 "<KEY_SOURCE_NOTEBOOK_PATH>/"
 "Query_Prices_GPT_New_Price_Analysis_9_25_25.ipynb").read_text(errors="replace"))[0]

src = (SCR/"gen12.py").read_text()
blk = src.split("instructions_3_2 = (",1)[1].split("\n    )",1)[0]
SYSTEM = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', blk))
SYSTEM = SYSTEM.encode().decode("unicode_escape")
print(f"system prompt rebuilt: {len(SYSTEM)} chars", flush=True)

rows = list(csv.DictReader(open(SCR/"iy25.csv", newline="", encoding="utf8", errors="replace")))
print(f"items: {len(rows)} (archived queries, verbatim) x {DRAWS} draws = {len(rows)*DRAWS} calls"
      f" | model={MODEL} temperature=0", flush=True)

lock = threading.Lock(); u_tot = {"p":0,"c":0,"n":0,"e":0}
def call(a):
    row, draw = a
    body = json.dumps({"model": MODEL, "temperature": 0, "messages":[
        {"role":"system","content":SYSTEM},{"role":"user","content":row["query"]}]}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    for att in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r: d = json.load(r)
            txt = d["choices"][0]["message"]["content"]; us = d.get("usage",{})
            with lock:
                u_tot["p"]+=us.get("prompt_tokens",0); u_tot["c"]+=us.get("completion_tokens",0)
                u_tot["n"]+=1
                if u_tot["n"]%25==0: print(f"  {u_tot['n']}/{len(rows)*DRAWS}", flush=True)
            return {"devicename":row["DEVICENAME"],"query":row["query"],"draw":draw,
                    "model":MODEL,"raw_response":txt,"usage":us,
                    "archived_2024_response":row["response"],
                    "deposited_year":row["years"]}
        except urllib.error.HTTPError as e:
            if e.code in (429,500,502,503) and att<3: time.sleep(4*(att+1)); continue
            with lock: u_tot["e"]+=1
            return {"devicename":row["DEVICENAME"],"draw":draw,"error":f"HTTP {e.code}"}
        except Exception as e:
            if att<3: time.sleep(4*(att+1)); continue
            with lock: u_tot["e"]+=1
            return {"devicename":row["DEVICENAME"],"draw":draw,"error":type(e).__name__}

jobs=[(r,d) for d in range(DRAWS) for r in rows]
t0=time.time()
with ThreadPoolExecutor(max_workers=6) as ex: recs=list(ex.map(call,jobs))
(OUT/"raw_responses.jsonl").write_text("\n".join(json.dumps(r) for r in recs)+"\n")
print(f"\ndone in {time.time()-t0:.0f}s | calls={u_tot['n']} errors={u_tot['e']}")
print(f"tokens: prompt={u_tot['p']:,} completion={u_tot['c']:,}")

# ---- immediate analysis ----
yr = lambda t: (re.search(r"Year:\s*(\d{4})", t or "") or [None,None])[1]
import collections, statistics
by=collections.defaultdict(list)
for r in recs:
    if "error" in r: continue
    by[r["devicename"]].append((yr(r["raw_response"]), r))
n=len(by); flip=0; spread=[]; match2024=0
for dn,lst in by.items():
    ys=[y for y,_ in lst if y]
    if len(set(ys))>1:
        flip+=1
        iv=[int(x) for x in ys]; spread.append(max(iv)-min(iv))
    a=yr(lst[0][1]["archived_2024_response"])
    if a and all(y==a for y,_ in lst): match2024+=1
print(f"\n=== INVENTION YEARS: {n} items x {DRAWS} draws, {MODEL}, temperature=0 ===")
print(f"  items where the returned YEAR changes across draws: {flip}/{n} ({flip/n:.0%})")
if spread: print(f"  among those, mean year spread: {statistics.mean(spread):.1f} (max {max(spread)})")
print(f"  all {DRAWS} draws reproduce the ARCHIVED 2024 year: {match2024}/{n} ({match2024/n:.0%})")
