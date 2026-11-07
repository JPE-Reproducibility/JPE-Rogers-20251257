import csv, json, pathlib, random, re, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
SCR=pathlib.Path(sys.argv[1]); OUT=SCR/"iy_band"
MODEL, DRAWS, BAND, THR = "gpt-4o-2024-08-06", 5, 6, 1959
KEY=re.findall(r"sk-[A-Za-z0-9_\-]{20,}", pathlib.Path(
 "<KEY_SOURCE_NOTEBOOK_PATH>/"
 "Query_Prices_GPT_New_Price_Analysis_9_25_25.ipynb").read_text(errors="replace"))[0]

src=(SCR/"gen12.py").read_text()
blk=src.split("# --- GPT-4o query (same instructions as Part 2) ---",1)[1]
blk=blk.split("instructions = (",1)[1].split("\n    )",1)[0]
SYSTEM="".join(re.findall(r'"((?:[^"\\]|\\.)*)"',blk)).encode().decode("unicode_escape")
assert SYSTEM.count("Response:")==4, f"expected 4 few-shot examples, got {SYSTEM.count('Response:')}"
print(f"system prompt: {len(SYSTEM)} chars, 4 few-shot examples", flush=True)

meta={}
for r in csv.DictReader(open(SCR/"regnum.csv",newline="",encoding="utf8",errors="replace")):
    pc=r.get("PRODUCTCODE_x")
    if pc and pc not in meta:
        meta[pc]=((r.get("DEVICENAME") or "")+" "+(r.get("DESCRIPTION_OF_REGNUM") or ""),
                  r.get("SUBMISSION_TYPE_ID"))
inband, outband = [], []
for r in csv.DictReader(open(SCR/"iy_all.csv",newline="",encoding="utf8",errors="replace")):
    pc=r["PRODUCTCODE"]
    try: y=int(float(r["years"]))
    except Exception: continue
    if pc not in meta: continue
    q,st = meta[pc]
    rec={"pc":pc,"query":q,"submission_type":st,"deposited_year":y,
         "in_band":abs(y-THR)<=BAND}
    (inband if rec["in_band"] else outband).append(rec)
rng=random.Random(20260803)
control=rng.sample(outband, min(60,len(outband)))
items=inband+control
print(f"in-band (|year-{THR}|<={BAND}): {len(inband)} | out-of-band control: {len(control)}"
      f" | total {len(items)} x {DRAWS} draws = {len(items)*DRAWS} calls", flush=True)

lock=threading.Lock(); u={"p":0,"c":0,"n":0,"e":0}
def call(a):
    it,d=a
    body=json.dumps({"model":MODEL,"temperature":0,"messages":[
        {"role":"system","content":SYSTEM},{"role":"user","content":it["query"]}]}).encode()
    req=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=body,
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    for att in range(4):
        try:
            with urllib.request.urlopen(req,timeout=120) as r: dd=json.load(r)
            us=dd.get("usage",{})
            with lock:
                u["p"]+=us.get("prompt_tokens",0); u["c"]+=us.get("completion_tokens",0); u["n"]+=1
                if u["n"]%200==0: print(f"  {u['n']}/{len(items)*DRAWS}",flush=True)
            return {**it,"draw":d,"model":MODEL,
                    "raw_response":dd["choices"][0]["message"]["content"],"usage":us}
        except urllib.error.HTTPError as e:
            if e.code in (429,500,502,503) and att<3: time.sleep(4*(att+1)); continue
            with lock: u["e"]+=1
            return {**it,"draw":d,"error":f"HTTP {e.code}"}
        except Exception as e:
            if att<3: time.sleep(4*(att+1)); continue
            with lock: u["e"]+=1
            return {**it,"draw":d,"error":type(e).__name__}
t0=time.time()
with ThreadPoolExecutor(max_workers=10) as ex:
    recs=list(ex.map(call,[(it,d) for d in range(DRAWS) for it in items]))
(OUT/"raw_responses.jsonl").write_text("\n".join(json.dumps(r) for r in recs)+"\n")
print(f"\ndone in {time.time()-t0:.0f}s calls={u['n']} errors={u['e']}")
print(f"tokens: prompt={u['p']:,} completion={u['c']:,}")
