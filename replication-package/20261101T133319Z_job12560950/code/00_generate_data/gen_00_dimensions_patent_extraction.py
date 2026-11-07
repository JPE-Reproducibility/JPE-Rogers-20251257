"""
gen_00_dimensions_patent_extraction.py
======================================
PROVENANCE ONLY -- DO NOT RUN AS PART OF THE DEFAULT PIPELINE.

This script documents how the raw Dimensions patent inputs were extracted from
the Dimensions patent database via the dimcli / DSL API. The downstream pipeline
(gen_01_main_panels.py and later) starts from these already-extracted files and
does NOT call the Dimensions API.

------------------------------------------------------------------------------
IMPORTANT: EXACT RE-EXTRACTION IS NOT POSSIBLE
------------------------------------------------------------------------------
These queries were run against Dimensions DSL **v1.24 (week of 2020-05-11)**.
The Dimensions DSL API has been revised repeatedly since then, and Dimensions
does not allow pinning or querying against a prior DSL/version or a historical
database snapshot. Re-running this script today will hit a newer DSL version and
an updated patent corpus, so it will NOT reproduce the identical patent extract
used in the paper.

The revisions are not only corpus growth and not only the one behaviour change
documented under REPRODUCTION FIDELITY below. The full-text retrieval layer that
decides which patents a phrase returns has itself been CORRECTED over the years:
I identified defects in how phrase queries matched patent text, reported them to
Digital Science, and they were fixed. I have no visibility into the provider's
full revision history and assume other users have found and had corrected others
since. Because no prior version can be queried, the retrieval behaviour this pull
saw cannot be reconstructed, and a re-pull therefore differs for reasons that are
not enumerable from the outside. The archived 2020 extract is the authoritative
input; every derived input built from it is pinned by SHA-256 in
certification/EXPECTED_CONFIDENTIAL_REAL_INPUT_HASHES.csv, and the patent-based
estimates in the paper are reproducible FROM IT, not from a re-derivation of it.

For reproducibility, the JPE Data Editor will be provided the EXACT extracted
files under a confidentiality agreement (see RESTRICTED_DATA_VERIFICATION_MEMO.md
and RESTRICTED_DATA_MANIFEST.csv). This script is included so the extraction
methodology is fully transparent, not as a turnkey re-run.

------------------------------------------------------------------------------
CREDENTIALS
------------------------------------------------------------------------------
No API key is stored in this file. The key is read at runtime from a local
`pw.txt` (one line, the Dimensions API key) or the DIMENSIONS_API_KEY
environment variable. Never hard-code the key. `pw.txt` and `*secret*`/`*token*`
patterns are excluded from the public package by the package build's exclusion rules.

------------------------------------------------------------------------------
WHICH PULL THIS SCRIPT DOCUMENTS
------------------------------------------------------------------------------
This script documents the ORIGINAL patent pull that actually produced the
patent files in this directory, i.e. the one in
`Replication_Gather_and_Compile_Data.ipynb`, the pre-packaging notebook the
gen_*.py scripts were derived from (that notebook is not part of the deposit).
The original used ONE rich query per product code:

    search patents in full_data for "(<phrase>)"
      where filing_status = "Grant" and date_inserted <= "2020-05-18"
            and jurisdiction = "US"
      return patents[id+year+filing_status+title+abstract+times_cited
        +original_assignee_names+original_assignees+inventor_names+cpc
        +granted_year+priority_year]

so title/abstract (-> FDA_patents_text.csv), cpc (-> all_pats_wtitlesCPC.csv),
and assignees (-> FDA_pats_original_firmname.csv) are all column selections from
this single result, routed to output files via `sample_select`.

Two pulls of this corpus were made, and this script documents the first. Both
read the SAME phrase files -- `revise_for_rescrape_3_2_latest.csv`,
`revise_for_rescrape.csv` and `revise_for_rescrape_already_had_2_1.csv`, which
ship in `data/raw/pat_search_augment/` -- and both apply the SAME "prefer
Search_Phrase, else DESCRIPTION_OF_REGNUM + DEVICENAME" rule. They differ only
in query shape:

1. ORIGINAL (what this script documents, and what produced the deposited
   files): the single rich query above; `jurisdiction = "US"` IN the query; no
   `score` and no `sort by score`.
2. RE-PULL (a later re-extraction, not used for any deposited file): a leaner
   scored query, `return patents[id+year+filing_status+title+score] sort by
   score desc`, with US filtered afterwards and separate by-id fetches for the
   extra fields.

For a product code WITH a hand-curated Search_Phrase the search string is the
same in both. Neither can be re-pulled byte-identically today, for the reasons
above; the deposited extract is the authoritative input and the JPE Data Editor
can receive it under confidentiality.

------------------------------------------------------------------------------
REPRODUCTION FIDELITY BY CODE TYPE (measured against the shipped extract)
------------------------------------------------------------------------------
Re-running this query today reproduces the shipped patent sets to very different
degrees, and the split is mechanistic. In DSL v1.24 (2020) `for "(<phrase>)"`
behaved as a BROAD RELEVANCE-ranked full-text search (over title+abstract),
returning large topically-related sets; the current DSL treats the same string
as a STRICTER term/phrase match returning far fewer records. Consequently:
  - Codes with a SPECIFIC phrase (most hand-curated codes, e.g. EXR, FRZ, and
    the IVD/antigen tests) reproduce the shipped Grant set at ~99-100% recall --
    strict and relevance matching converge on the same specific patents.
  - Codes with a GENERIC device phrase (e.g. product code JCA "bleeding time
    device", ILQ "powered communication system", INX "air-fluidized bed") do
    NOT reproduce: the 2020 relevance pull returned thousands of loosely-related
    patents (the bulk of these codes' patents live in all_PC_pats.csv, the master
    universe pull) that today's stricter query no longer returns. This is a
    documented Dimensions behavior change, not a query-construction difference:
    neither a stricter phrase (too few) nor an explicit OR of the terms (returns
    a different 50k-capped set, ~1% overlap) recovers the 2020 relevance set.
The shipped restricted files are the authoritative inputs; this script regenerates
as close as the current DSL allows and is exact for the specific-phrase codes.

------------------------------------------------------------------------------
OUTPUTS (raw Dimensions inputs consumed downstream; restricted, not public)
------------------------------------------------------------------------------
  - all_PC_pats.csv                 patent id + product code + year + filing_status + title + score
  - expanded_2_1_pats.csv           II->I keyword/phrase expansion hits
  - expanded_3_2_pats.csv           III->II keyword/phrase expansion hits
  - missed_2_1_pats.csv             II->I supplemental hits
  - FDA_pats_original_firmname.csv   id + original assignee (firm) names
  - all_pats_wtitlesCPC.csv          id + CPC classification + title
  - FDA_patents_text.csv             id + title + abstract (for safety-text analysis)

Search-phrase inputs (author-created; included in the public package under
data/raw/pat_search_augment/):
  - revise_for_rescrape.csv                 II->I product codes (no prior patents)
  - revise_for_rescrape_already_had_2_1.csv II->I product codes (had prior patents)
  - revise_for_rescrape_3_2_latest.csv      III->II product codes

------------------------------------------------------------------------------
HAND-CURATED SEARCH PHRASES (specificity tuning) -- IMPORTANT METHODOLOGY NOTE
------------------------------------------------------------------------------
The patent search does NOT always use the auto-generated phrase
(DESCRIPTION_OF_REGNUM + DEVICENAME). The hand-curated `Search_Phrase` entries
were added EX POST: after an initial pull, certain product codes were determined
to have LOW SPECIFICITY (the auto device-name query returned too-broad or
off-target patent sets), so additional/sharper keywords were written for those
codes to improve precision. The loop below PREFERS the hand-curated phrase when
present. This matters because it determines which patents map to a given treated
product code (and therefore the patent outcomes for that code).

Coverage of the hand-curated `Search_Phrase` column in the included files:
  - III->II (revise_for_rescrape_3_2_latest.csv): 20 of 30 treated product
    codes use a hand-curated phrase (the rest fall back to the auto phrase).
    These are largely IVD / lab-test devices (immunoassays, tumor-antigen and
    nucleic-acid tests) where the device name alone is too generic — e.g.
    product code LTJ ("Prostate-Specific Antigen (PSA) ...") uses
    "Tumor-associated antigen immunological test Prostate cancer antigen".
  - II->I: 11 of 31 (revise_for_rescrape.csv) and 14 of 24
    (revise_for_rescrape_already_had_2_1.csv) use a hand-curated phrase.

Because these phrase files are bundled, the exact search inputs are transparent
and inspectable even though the resulting Dimensions extract itself cannot be
re-pulled identically (DSL version drift, above).
"""

from __future__ import annotations

import os
import json
import sys
from pathlib import Path

# --- guard: do not run by default ---------------------------------------------
if __name__ == "__main__" and os.environ.get("RUN_DIMENSIONS_EXTRACTION") != "1":
    sys.exit(
        "gen_00_dimensions_patent_extraction.py is provenance documentation and "
        "is not run by default. It requires dimcli + a Dimensions API key and "
        "cannot reproduce the exact paper extract (DSL version drift). "
        "Set RUN_DIMENSIONS_EXTRACTION=1 only to exercise the query path against "
        "the current Dimensions DSL."
    )

# DSL version actually used for the paper extract (documentation only):
DSL_VERSION_USED = "v1.24 (week of 2020-05-11)"
# Date filter used so the extract is reproducible as-of the original pull:
DATE_INSERTED_CUTOFF = "2020-05-18"


def _load_api_key() -> str:
    """Read the Dimensions API key from pw.txt or DIMENSIONS_API_KEY env var."""
    env_key = os.environ.get("DIMENSIONS_API_KEY")
    if env_key:
        return env_key.strip()
    for candidate in ("pw.txt", os.path.expanduser("~/pw.txt")):
        p = Path(candidate)
        if p.exists():
            return p.read_text(encoding="utf-8").splitlines()[0].strip()
    raise SystemExit(
        "No Dimensions API key found. Set DIMENSIONS_API_KEY or place a one-line "
        "pw.txt in the working directory. (Never hard-code the key.)"
    )


def _dsl():
    import dimcli
    dimcli.login(key=_load_api_key(), endpoint="https://app.dimensions.ai")
    return dimcli.Dsl()


# Fields returned by the ORIGINAL single rich query (one query per product code).
# title/abstract -> FDA_patents_text.csv; cpc -> all_pats_wtitlesCPC.csv;
# original_assignee(_names) -> FDA_pats_original_firmname.csv are all column
# selections from this one result, NOT separate queries.
ORIGINAL_RETURN_FIELDS = (
    "id+year+filing_status+title+abstract+times_cited+original_assignee_names+"
    "original_assignees+inventor_names+cpc+granted_year+priority_year"
)
ORIGINAL_KEEP_COLS = [
    "id", "PRODUCTCODE", "year", "filing_status", "title", "abstract",
    "times_cited", "original_assignee_names", "original_assignees",
    "inventor_names", "cpc", "granted_year", "priority_year",
]


# ---------------------------------------------------------------------------
# ORIGINAL pull query (Replication_Gather_and_Compile_Data.ipynb): one rich
# query per product code, US grants, with all downstream fields in a single call.
# ---------------------------------------------------------------------------
def search_patents_for_phrase(dsl, query_string: str, productcode: str):
    """Phrase search over Dimensions full_data for US granted patents.

    This is the ORIGINAL query that produced the patent files in this directory
    (all_PC_pats.csv / expanded_*_pats.csv / missed_2_1_pats.csv). The search
    phrase is the hand-curated Search_Phrase when present, else the auto
    DESCRIPTION_OF_REGNUM + DEVICENAME. `jurisdiction = "US"` is applied IN the
    query (not post-filtered), and there is no `score` / `sort by score`.
    """
    import pandas as pd
    query = (
        'search patents in full_data for "(' + query_string + ')" '
        'where filing_status = "Grant" and date_inserted <= "'
        + DATE_INSERTED_CUTOFF + '" and jurisdiction = "US" '
        "return patents[" + ORIGINAL_RETURN_FIELDS + "]"
    )
    data = pd.DataFrame(dsl.query_iterative(query)["patents"])
    if len(data) == 0:
        return data
    data["PRODUCTCODE"] = productcode
    return data[[c for c in ORIGINAL_KEEP_COLS if c in data.columns]]


# ---------------------------------------------------------------------------
# Supplementary by-id fetch (variant). The ORIGINAL pull returned everything in
# one query (above). A by-id pattern -- `search patents where id in {ids}
# return patents[...]` -- appears as a supplementary lookup in the original
# notebook, and is the form the later re-pull used to fetch extra fields (e.g.
# title+abstract, cpc) for an existing id list. Documented here for completeness.
# ---------------------------------------------------------------------------
def fetch_fields_by_id(dsl, patent_ids: list[str], return_fields: str):
    import pandas as pd
    q = "search patents where id in {} return patents[" + return_fields + "]"
    frames = []
    for i in range(0, len(patent_ids), 512):
        chunk = patent_ids[i : i + 512]
        frames.append(pd.DataFrame(
            dsl.query_iterative(q.format(json.dumps(chunk)), verbose=False)["patents"]
        ))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# Output file routing in the original notebook, controlled by `sample_select`:
SAMPLE_SELECT_OUTPUT = {
    "whole": "all_PC_pats.csv",          # full universe (read all phrase files)
    "3_2": "expanded_3_2_pats.csv",      # III->II treated/controls
    "2_1_no_pats": "missed_2_1_pats.csv",  # II->I codes with no prior patents
    "2_1": "expanded_2_1_pats.csv",      # II->I codes that had prior patents
}


def _output_dir() -> Path:
    """Where regenerated files are written. Override with DIMENSIONS_OUTPUT_DIR; defaults to a local
    `dimensions_extract_regenerated/` so a re-run never overwrites the shipped restricted files."""
    d = Path(os.environ.get("DIMENSIONS_OUTPUT_DIR", "dimensions_extract_regenerated"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def main(sample_select: str = "3_2") -> None:
    """Re-create the ORIGINAL extraction loop and WRITE the regenerated file (as close to the paper
    extract as the current DSL allows; see the version-drift note in the module docstring for why it
    is not byte-identical). One rich query per product code; the text/cpc/assignee inputs used
    downstream are column selections from these files."""
    import pandas as pd

    phrase_file = {
        "3_2": "data/raw/pat_search_augment/revise_for_rescrape_3_2_latest.csv",
        "2_1": "data/raw/pat_search_augment/revise_for_rescrape_already_had_2_1.csv",
        "2_1_no_pats": "data/raw/pat_search_augment/revise_for_rescrape.csv",
        "whole": "data/raw/pat_search_augment/revise_for_rescrape_3_2_latest.csv",
    }[sample_select]
    out_file = SAMPLE_SELECT_OUTPUT[sample_select]

    dsl = _dsl()
    search_terms = pd.read_csv(phrase_file)
    search_terms = search_terms[search_terms.DESCRIPTION_OF_REGNUM.notnull()]

    hits = []
    for _, row in search_terms.iterrows():
        row = row.dropna()
        # Prefer the hand-curated Search_Phrase (specificity tuning) when present;
        # otherwise fall back to the auto phrase. See module docstring.
        phrase = row.get("Search_Phrase") or (
            str(row.get("DESCRIPTION_OF_REGNUM", "")) + str(row.get("DEVICENAME", ""))
        ).lower()
        df = search_patents_for_phrase(dsl, phrase, row.get("PRODUCTCODE_x"))
        if len(df):
            hits.append(df)
    # De-dup on (id, PRODUCTCODE), NOT on id alone: a patent legitimately maps to more than one product
    # code (the shipped all_PC_pats.csv / expanded_*.csv keep id-under-multiple-PC), so id-only de-dup
    # would drop those legitimate rows.
    matched = (pd.concat(hits, ignore_index=True).drop_duplicates(["id", "PRODUCTCODE"])
               if hits else pd.DataFrame())
    out_path = _output_dir() / out_file
    matched.to_csv(out_path, index=False)
    print(f"[{sample_select} -> {out_path}] wrote {len(matched)} patent rows "
          f"(current DSL != {DSL_VERSION_USED}; NOT identical to the paper extract).")


def run_all_samples() -> None:
    """Regenerate every treated-code patent file (expanded_3_2 / expanded_2_1 / missed_2_1)."""
    for s in ("3_2", "2_1", "2_1_no_pats"):
        main(s)


if __name__ == "__main__":
    # Guarded above by RUN_DIMENSIONS_EXTRACTION=1. Usage:
    #   RUN_DIMENSIONS_EXTRACTION=1 python gen_00_dimensions_patent_extraction.py [3_2|2_1|2_1_no_pats|whole|all]
    sel = sys.argv[1] if len(sys.argv) > 1 else "3_2"
    run_all_samples() if sel == "all" else main(sel)
