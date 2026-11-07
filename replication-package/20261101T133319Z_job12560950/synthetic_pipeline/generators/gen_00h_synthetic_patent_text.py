#!/usr/bin/env python3
"""gen_00h_synthetic_patent_text.py -- generate a SYNTHETIC FDA_patents_text.csv so the
synthetic route can regenerate the safety keyword/embedding exhibits (steps 16/17 -> Table D.12).

WHY
---
Steps 16 (06b, Word2Vec keyword) and 17 (06c, sentence-transformer embedding) read
`data/raw/FDA_patents_text.csv` (columns: `id`, `input` = "Title: ...; Abstract: ...; Primary
CPC: ..."). This generator produces a pure-synthetic stand-in for that file, so on the synthetic
route 06b/06c run on synthetic text and Table D.12 is regenerated rather than reused from the real
precomputed outputs (its numbers differ from the real-route table by construction).

PURE-SYNTHETIC (no real data): reads only the already-synthetic
`simulated_data/synthetic_patents/all_pats_wtitlesCPC.csv` (synthetic ids + PRODUCTCODE) and the
shared theta table (public product-code random effects). Writes
`simulated_data/synthetic_patents/FDA_patents_text.csv`, which materialize_simulation.py then
routes to `data/raw/FDA_patents_text.csv`.

SIGNAL: each patent's abstract is synthetic filler tokens PLUS, with probability theta.p_safety
(resp. fixed cost/quality rates), the ACTUAL 06b SAFETY_KEYWORDS / COST_KEYWORDS / QUALITY_KEYWORDS
vocabulary, so the keyword extraction + Word2Vec refinement have real (synthetic) signal that
clusters by product code -- not an all-zero degenerate column. Deterministic (seeded).
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.abspath(os.path.join(HERE, ".."))          # synthetic_pipeline/
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import synthetic_paths
from synthetic_seed import seed

SIM = os.path.join(str(synthetic_paths.simulated_data_dir()), "synthetic_patents")
SRC = os.path.join(SIM, "all_pats_wtitlesCPC.csv")
OUT = os.path.join(SIM, "FDA_patents_text.csv")
SEED = seed(20260713)
CHUNK = 200_000

import gen_00b_pc_effects as pcmod   # shared theta (public PC random effects)

# The exact keyword vocabularies 06b's KeywordProcessor looks for (kept in sync with
# code/06b_validate_safety.py). Injecting these into synthetic abstracts gives 06b/06c real
# (synthetic) safety/cost/quality signal instead of an all-zero column.
SAFETY_KEYWORDS = ["safety", "safe", "safer", "endangering", "precautions", "unsafe",
                   "hazardous", "failsafe", "safely", "dangerous", "hazard", "danger",
                   "harming", "injuring", "injury", "jeopardizing", "risking", "risk",
                   "complication", "life-threatening"]
COST_KEYWORDS = ["cost", "price", "economic", "costs", "revenue", "savings", "discount",
                 "premiums", "pricing", "budget", "expense", "expensive", "costly", "prices",
                 "complexity"]
QUALITY_KEYWORDS = ["performance", "reliability", "performances", "quality", "durability",
                    "accuracy", "robustness", "reproducibility", "transferability",
                    "effectiveness", "sensitivity"]
# neutral device-y filler vocabulary so Word2Vec has a non-trivial corpus with context
FILLER = ["device", "apparatus", "method", "system", "assembly", "component", "material",
          "surface", "element", "portion", "member", "structure", "mechanism", "sensor",
          "signal", "fluid", "chamber", "housing", "electrode", "polymer", "coating",
          "membrane", "actuator", "valve", "catheter", "implant", "tissue", "flow",
          "pressure", "temperature", "measurement", "control", "unit", "region", "layer"]


def main():
    if not os.path.exists(SRC):
        raise SystemExit(f"{SRC} not found -- run gen_00d/gen_00g first.")
    theta = pcmod.load_theta()
    rng = np.random.default_rng(SEED)
    # numpy-array vocabularies so batched rng.choice avoids per-call list->array conversion
    filler = np.asarray(FILLER)
    safety = np.asarray(SAFETY_KEYWORDS)
    cost = np.asarray(COST_KEYWORDS)
    quality = np.asarray(QUALITY_KEYWORDS)
    cpc_letters = np.asarray(["A61A", "A61B", "A61C", "A61D", "A61E", "A61F"])
    written = 0
    header = True
    if os.path.exists(OUT):
        os.remove(OUT)
    for chunk in pd.read_csv(SRC, usecols=["id", "PRODUCTCODE"], chunksize=CHUNK, low_memory=False):
        n = len(chunk)
        pcs = chunk["PRODUCTCODE"].astype(str).to_numpy()
        p_safety = pcmod.theta_lookup(pcs, "p_safety", theta)
        # safety-keyword injection rate CLUSTERS by product code via theta.p_safety; cost/quality
        # get fixed base rates (no restricted signal to key on). Fixed injected counts (2 safety /
        # 1 cost / 1 quality) let the draws be BATCHED (no per-row rng.choice -> ~1.2M rows/min).
        safe_hit = rng.random(n) < p_safety
        cost_hit = rng.random(n) < 0.18
        qual_hit = rng.random(n) < 0.20
        ks = rng.integers(8, 18, n)          # abstract filler length per row
        tks = rng.integers(3, 7, n)          # title length per row
        cpc_idx = rng.integers(0, len(cpc_letters), n)
        abs_pool = rng.choice(filler, size=int(ks.sum()))      # one big draw, sliced per row
        title_pool = rng.choice(filler, size=int(tks.sum()))
        safe_kw = rng.choice(safety, size=(n, 2))              # used only where safe_hit
        cost_kw = rng.choice(cost, size=n)
        qual_kw = rng.choice(quality, size=n)
        inputs = []
        ao = to = 0
        for i in range(n):
            k = int(ks[i]); tk = int(tks[i])
            toks = abs_pool[ao:ao + k].tolist(); ao += k
            if safe_hit[i]:
                toks.extend(safe_kw[i].tolist())
            if cost_hit[i]:
                toks.append(cost_kw[i])
            if qual_hit[i]:
                toks.append(qual_kw[i])
            title = " ".join(title_pool[to:to + tk].tolist()); to += tk
            inputs.append(f"Title: {title}; Abstract: {' '.join(toks)}; "
                          f"Primary CPC: {cpc_letters[cpc_idx[i]]}")
        out = pd.DataFrame({"id": chunk["id"].to_numpy(), "input": inputs})
        out.to_csv(OUT, mode="w" if header else "a", header=header, index=False)
        header = False
        written += n
        print(f"    ... {written:,} rows", flush=True)
    print(f"  wrote {os.path.relpath(OUT, SP)} ({written:,} synthetic patent texts; "
          f"safety-keyword rate ~ theta.p_safety per product code)")


if __name__ == "__main__":
    main()
