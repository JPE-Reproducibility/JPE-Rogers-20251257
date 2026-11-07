"""
gen_06b_permno_universe.py
==========================
PROVENANCE / RESTRICTED-MODE -- DO NOT RUN AS PART OF THE DEFAULT PIPELINE.

Builds the manufacturer-name -> CRSP PERMNO reference table that
`gen_07_adverse_permno.py` uses to attach PERMNOs to MAUDE adverse-event
manufacturer names. The reference is the concatenation of three sources, then
deduplicated on `permno`:

    1. CRSP firm directory (`CRSPDirectory.csv`) -- `NAME OF FIRM` + `PERM NO`
       (renamed to `firm_name` and `permno`).
    2. Patent-assignee PERMNOs from the restricted KPSS / Dimensions patent file
       (`all_patents_w_xi_oct22_24.csv`) for assignees not already in
       CRSPDirectory -- `orig_assignee_solo` -> `firm_name`, `permno`.
    3. Compustat AllPublicCompanies (`AllPublicCompanies.csv`) for `LPERMNO`s
       not already covered -- `conml` -> `firm_name`, `LPERMNO` -> `permno`.

Output:
    data/raw/MAUDE/all_permnos_fname_adverse_events_oct22_24.csv
    (consumed by gen_07_adverse_permno.py; restricted, excluded from the public
    package because it carries CRSP/KPSS/Compustat-derived PERMNOs).

Source logic: `my_paper/analysis/code/Dedupe_Manuf_firm_size_adverse_events.py`
lines 46-76 (the same script gen_05 and gen_07 were derived from).

------------------------------------------------------------------------------
WHY THIS IS NOT RUN BY DEFAULT
------------------------------------------------------------------------------
All three inputs are restricted:
- `CRSPDirectory.csv` is a CRSP firm directory extract (WRDS-licensed CRSP data).
- `all_patents_w_xi_oct22_24.csv` is KPSS-merged Dimensions patent data
  (restricted; see gen_00_dimensions_patent_extraction.py for the patent pull,
  and the WRDS Compustat link for the PERMNO join).
- `AllPublicCompanies.csv` is derived from Compustat (WRDS-licensed CCM
  Fundamentals Annual; see WRDS_EXTRACTION_ROADMAP.md).

The full output is also restricted (PERMNO-linked) and is excluded from the
public package. A licensed user (or the JPE Data Editor with WRDS access) can
rebuild it by providing the three inputs at the documented paths and running
this script. The exact CRSPDirectory.csv source on WRDS should be confirmed --
likely a CRSP company-name / PERMNO directory; see WRDS_EXTRACTION_ROADMAP.md
Query 2.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


# --- guard: do not run by default ---------------------------------------------
if __name__ == "__main__" and os.environ.get("RUN_PERMNO_UNIVERSE_BUILD") != "1":
    sys.exit(
        "gen_06b_permno_universe.py is provenance / restricted-mode and is not "
        "run by default. It requires the CRSP firm directory + KPSS-merged "
        "Dimensions patents + Compustat AllPublicCompanies inputs at the "
        "documented paths. Set RUN_PERMNO_UNIVERSE_BUILD=1 to exercise the build."
    )


# Input paths (relative to package root). All three inputs are restricted and
# are NOT shipped in the public package.
CRSP_DIRECTORY_CSV = "data/raw/CRSPDirectory.csv"            # CRSP firm directory
ALL_PATENTS_W_XI_CSV = "data/derived/all_patents_w_xi_oct22_24.csv"  # KPSS+Dimensions
ALL_PUBLIC_COMPANIES_CSV = "data/raw/AllPublicCompanies.csv"  # Compustat-derived

OUTPUT_CSV = "data/raw/MAUDE/all_permnos_fname_adverse_events_oct22_24.csv"


def build_permno_universe() -> "pd.DataFrame":
    """Concatenate the three (firm_name, permno) sources and dedupe on permno."""
    import pandas as pd

    crsp_direct = pd.read_csv(CRSP_DIRECTORY_CSV)
    crsp_direct["permno"] = crsp_direct["PERM NO"].astype(float)
    crsp_direct["firm_name"] = crsp_direct["NAME OF FIRM"]

    all_pats = pd.read_csv(ALL_PATENTS_W_XI_CSV)
    all_pats_public = all_pats[all_pats["permno"].notnull()]
    remaining_crsp = all_pats_public[
        ~all_pats_public["permno"].isin(crsp_direct["permno"].values)
    ][["orig_assignee_solo", "permno"]].drop_duplicates()
    remaining_crsp["firm_name"] = remaining_crsp["orig_assignee_solo"]

    pub_comp = pd.read_csv(ALL_PUBLIC_COMPANIES_CSV)
    remaining_allpublic = pub_comp[
        ~pub_comp["LPERMNO"].astype(float).isin(crsp_direct["permno"])
    ]
    remaining_allpublic = remaining_allpublic[
        ~remaining_allpublic["LPERMNO"].astype(float).isin(remaining_crsp["permno"])
    ].copy()
    remaining_allpublic["permno"] = remaining_allpublic["LPERMNO"].astype(float)
    remaining_allpublic["firm_name"] = remaining_allpublic["conml"]

    all_permnos = pd.concat(
        [
            crsp_direct[["firm_name", "permno"]],
            remaining_crsp[["firm_name", "permno"]],
            remaining_allpublic[["firm_name", "permno"]],
        ],
        ignore_index=True,
    ).drop_duplicates("permno")

    return all_permnos


def main() -> None:
    import pandas as pd  # noqa: F401  (informational; build_permno_universe imports it)

    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)
    universe = build_permno_universe()
    universe.to_csv(OUTPUT_CSV, index=False)
    print(
        f"Wrote {OUTPUT_CSV}: {len(universe):,} (firm_name, permno) rows "
        f"({universe['permno'].nunique():,} unique PERMNOs)."
    )


if __name__ == "__main__":
    main()
