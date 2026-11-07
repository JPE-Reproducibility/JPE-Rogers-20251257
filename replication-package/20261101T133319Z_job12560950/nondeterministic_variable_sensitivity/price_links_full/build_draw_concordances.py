"""Turn the re-draw responses into drop-in replacements for the two deposited concordances.

Each output keeps the deposited schema and row order; only the model-supplied columns
(decision, mapping_quality, hcpcs_cpt, hcpcs_level_2, procedure_desc, rationale, alternates,
confidence) are replaced with that draw's values. Everything the deposited file carries about the
device itself is left untouched, so substituting one of these into the tree changes the
concordance and nothing else.

Usage:  python3 build_draw_concordances.py <dir with the deposited CSVs> <out dir> <jsonl> [...]
"""
import csv, json, pathlib, re, sys

FILES = {"3to2": "3_2_GPT_Price_Links.csv", "2to1": "2_1_GPT_Price_Links.csv"}
MODEL_COLS = ("decision", "mapping_quality", "hcpcs_cpt", "hcpcs_level_2",
              "procedure_desc", "rationale", "alternates", "confidence")


def parse(text):
    t = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    try:
        return json.loads(t)
    except Exception:
        m = re.search(r"\{.*\}", t, re.S)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:
            return None


def flatten(v):
    """The deposited CSV stores list-valued fields as comma-joined strings."""
    if isinstance(v, (list, tuple)):
        return ",".join(str(x) for x in v)
    if v is None:
        return ""
    return str(v)


def main(dep_dir, out_dir, *jsonls):
    dep_dir, out_dir = pathlib.Path(dep_dir), pathlib.Path(out_dir)
    draws = {}
    for p in jsonls:
        for line in pathlib.Path(p).read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if "error" in rec:
                continue
            obj = parse(rec["raw_response"])
            if obj is None:
                continue
            draws.setdefault(rec["draw"], {})[(rec["label"], rec["productcode"])] = obj

    for d in sorted(draws):
        dest = out_dir / f"draw{d+1}"
        dest.mkdir(parents=True, exist_ok=True)
        for label, fname in FILES.items():
            rows = list(csv.DictReader(open(dep_dir / fname, newline="",
                                            encoding="utf8", errors="replace")))
            cols = list(rows[0].keys())
            n_sub = 0
            for r in rows:
                obj = draws[d].get((label, r["productcode"]))
                if obj is None:
                    continue
                for c in MODEL_COLS:
                    if c in r:
                        r[c] = flatten(obj.get(c, ""))
                n_sub += 1
            with open(dest / fname, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                w.writerows(rows)
            print(f"  draw{d+1}/{fname}: {len(rows)} rows, {n_sub} substituted")


if __name__ == "__main__":
    main(*sys.argv[1:])
