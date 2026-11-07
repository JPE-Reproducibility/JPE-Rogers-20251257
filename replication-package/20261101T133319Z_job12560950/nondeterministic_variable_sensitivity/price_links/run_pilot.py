import csv, json, os, random, re, pathlib, sys, time, threading
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

SCR = pathlib.Path(sys.argv[1])
OUT = SCR / "redraw_pilot"
MODEL = "gpt-5-mini-2025-08-07"      # pinned: the snapshot live at the 2025-09-22 run
DRAWS = 5
PER_FILE = 20
SEED = 20260803                      # the package's PUBLIC_SEED, for a recorded design

# ---- key (never printed) ----
pat = re.compile(r"sk-[A-Za-z0-9_\-]{20,}")
KEY = pat.findall(pathlib.Path(
    "<KEY_SOURCE_NOTEBOOK_PATH>/"
    "Query_Prices_GPT_New_Price_Analysis_9_25_25.ipynb").read_text(errors="replace"))[0]

# ---- the deposited prompt, verbatim from code/12b_gpt_price_links_generation.py ----
src = (SCR / "gen12b.py").read_text()
INSTRUCTIONS = src.split('INSTRUCTIONS = """', 1)[1].split('"""', 1)[0]

def user_msg(r):
    return ("Device candidate:\n"
            f"- FDA product code: {r['productcode']}\n"
            f"- Device name: {r['devicename']}\n"
            f"- Regulation: {r['regulationnumber']}; {r['description_of_regnum']}\n"
            f"- Subpart: {r['subpart_description']}\n"
            "Return ONLY the JSON object described in the system message.")

# ---- stratified sample with a recorded design ----
rng = random.Random(SEED)
items = []
for f, label in (("3_2_GPT_Price_Links.csv", "3to2"), ("2_1_GPT_Price_Links.csv", "2to1")):
    rows = list(csv.DictReader(open(SCR / f, newline="", encoding="utf8", errors="replace")))
    pick = rng.sample(rows, min(PER_FILE, len(rows)))
    for r in pick:
        r["_label"] = label
        r["_pi"] = min(PER_FILE, len(rows)) / len(rows)
        items.append(r)
print(f"sampled {len(items)} items ({PER_FILE} per direction); {DRAWS} draws each "
      f"= {len(items)*DRAWS} calls; model={MODEL}", flush=True)

lock = threading.Lock()
usage = {"prompt": 0, "completion": 0, "calls": 0, "errors": 0}

def call(args):
    item, draw = args
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": user_msg(item)}]}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            txt = d["choices"][0]["message"]["content"]
            u = d.get("usage", {})
            with lock:
                usage["prompt"] += u.get("prompt_tokens", 0)
                usage["completion"] += u.get("completion_tokens", 0)
                usage["calls"] += 1
                if usage["calls"] % 25 == 0:
                    print(f"  {usage['calls']}/{len(items)*DRAWS} calls", flush=True)
            return {"productcode": item["productcode"], "label": item["_label"],
                    "pi": item["_pi"], "draw": draw, "model": MODEL,
                    "raw_response": txt, "usage": u,
                    "deposited": {k: item[k] for k in
                                  ("decision","mapping_quality","hcpcs_cpt","hcpcs_level_2","confidence")}}
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(4 * (attempt + 1)); continue
            with lock: usage["errors"] += 1
            return {"productcode": item["productcode"], "draw": draw,
                    "error": f"HTTP {e.code}"}
        except Exception as e:
            if attempt < 3:
                time.sleep(4 * (attempt + 1)); continue
            with lock: usage["errors"] += 1
            return {"productcode": item["productcode"], "draw": draw,
                    "error": f"{type(e).__name__}"}

jobs = [(it, d) for d in range(DRAWS) for it in items]
t0 = time.time()
with ThreadPoolExecutor(max_workers=6) as ex:
    recs = list(ex.map(call, jobs))

with open(OUT / "raw_responses.jsonl", "w") as fh:
    for r in recs:
        fh.write(json.dumps(r) + "\n")
print(f"\ndone in {time.time()-t0:.0f}s | calls={usage['calls']} errors={usage['errors']}")
print(f"tokens: prompt={usage['prompt']:,} completion={usage['completion']:,}")
