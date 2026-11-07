"""Re-draw the Class II->I invention years, five times, as faithfully as the archive allows.

The deposited `innovation_year_2_1_FDA_project.csv` keeps only PRODUCTCODE and years, so the
queries are rebuilt from the project-root input the generator names in its own comment,
`DPM2_1_1997/for_gpt_2_1_invention_dates.csv`. That file holds exactly the 293 product codes of
the deposited output, in the same order, so the reconstruction is exact. The system prompt is
lifted verbatim from Part 2 of the deposited generator, and the query is built the way Part 2
builds it: DEVICENAME + DESCRIPTION_OF_REGNUM, with no separator.

Usage:  python3 run_2_1.py <scratch dir> [--dry-run]

<scratch dir> must hold:
  gen12.py                        copy of the deposited 12_invention_year_generation.py
  for_gpt_2_1_invention_dates.csv copy of the project-root query input

--dry-run makes no API calls; it prints the prompt and the first queries for inspection.
"""
import csv, json, pathlib, re, ssl, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

# This Python build ships no populated CA store (its "Install Certificates" step was never run),
# so urllib's default context fails every TLS handshake with CERTIFICATE_VERIFY_FAILED. Build the
# context from certifi's bundle explicitly. Do not run this script with -I: isolated mode drops
# the user site-packages that provide certifi.
import certifi
SSLCTX = ssl.create_default_context(cafile=certifi.where())

SCR = pathlib.Path(sys.argv[1])
DRY = "--dry-run" in sys.argv
OUT = SCR / "iy_2_1b"   # batch 2; batch 1 lives in iy_2_1
OUT.mkdir(parents=True, exist_ok=True)
MODEL, DRAWS = "gpt-4o-2024-08-06", 5
DRAW_OFFSET = 5          # batch 1 used draws 0-4; this one continues at 5

# --- system prompt, verbatim from Part 2 of the deposited generator ---------------------
src = (SCR / "gen12.py").read_text()
blk = src.split("def generate_2_1_invention_years", 1)[1]
blk = blk.split("instructions = (", 1)[1].split("\n    )", 1)[0]
SYSTEM = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', blk)).encode().decode("unicode_escape")
assert SYSTEM.count("Response:") == 4, f"expected 4 few-shot examples, got {SYSTEM.count('Response:')}"
assert "expert in medical devices" in SYSTEM

# --- queries, built exactly as Part 2 builds them --------------------------------------
items, seen = [], set()
for r in csv.DictReader(open(SCR / "for_gpt_2_1_invention_dates.csv", newline="",
                             encoding="utf8", errors="replace")):
    pc = r["PRODUCTCODE"]
    if pc in seen:
        continue
    seen.add(pc)
    items.append({"productcode": pc,
                  "query": (r["DEVICENAME"] or "") + (r["DESCRIPTION_OF_REGNUM"] or ""),
                  "part_description": r.get("PART_DESCRIPTION")})

print(f"system prompt: {len(SYSTEM)} chars, 4 few-shot examples", flush=True)
print(f"items: {len(items)} product codes x {DRAWS} draws (indices "
      f"{DRAW_OFFSET}-{DRAW_OFFSET+DRAWS-1}) = {len(items)*DRAWS} calls"
      f" | model={MODEL} temperature=0", flush=True)

if DRY:
    print("\n--- system prompt ---\n" + SYSTEM)
    print("--- first three queries ---")
    for it in items[:3]:
        print(f"  [{it['productcode']}] {it['query']!r}")
    print("\nDRY RUN: no API calls made.")
    sys.exit(0)

KEY = re.findall(r"sk-[A-Za-z0-9_\-]{20,}", pathlib.Path(
    SCR / "keysrc.ipynb").read_text(errors="replace"))[0]

lock = threading.Lock()
u = {"p": 0, "c": 0, "n": 0, "e": 0}
TOTAL = len(items) * DRAWS
JSONL = OUT / "raw_responses.jsonl"
JSONL.unlink(missing_ok=True)
sink = open(JSONL, "a")


def emit(rec):
    """Append under the lock, so an interrupted run keeps every completed call."""
    with lock:
        sink.write(json.dumps(rec) + "\n")
        sink.flush()
    return rec


def call(a):
    it, d = a
    body = json.dumps({"model": MODEL, "temperature": 0, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": it["query"]}]}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {KEY}",
                                          "Content-Type": "application/json"})
    for att in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120, context=SSLCTX) as r:
                dd = json.load(r)
            us = dd.get("usage", {})
            with lock:
                u["p"] += us.get("prompt_tokens", 0)
                u["c"] += us.get("completion_tokens", 0)
                u["n"] += 1
                if u["n"] % 200 == 0:
                    print(f"  {u['n']}/{TOTAL}", flush=True)
            return emit({**it, "draw": d, "model": MODEL,
                         "raw_response": dd["choices"][0]["message"]["content"], "usage": us})
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and att < 3:
                time.sleep(4 * (att + 1))
                continue
            with lock:
                u["e"] += 1
            return emit({**it, "draw": d, "error": f"HTTP {e.code}"})
        except Exception as e:
            if att < 3:
                time.sleep(4 * (att + 1))
                continue
            with lock:
                u["e"] += 1
            return emit({**it, "draw": d, "error": type(e).__name__, "detail": str(e)[:200]})


t0 = time.time()
with ThreadPoolExecutor(max_workers=10) as ex:
    list(ex.map(call, [(it, d + DRAW_OFFSET) for d in range(DRAWS) for it in items]))
sink.close()
print(f"\ndone in {time.time()-t0:.0f}s calls={u['n']} errors={u['e']}")
print(f"tokens: prompt={u['p']:,} completion={u['c']:,}")
