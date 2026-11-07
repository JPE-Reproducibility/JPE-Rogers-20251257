#!/usr/bin/env python3
"""preflight_from_raw.py -- verify the simulated-data route has every input the runnable cleaning scripts
need, BEFORE running `run_all.py --synthetic-from-raw`.

The simulated-data route runs every transformation on synthetic/public inputs. gen_02 is deferred until
after matching; gen_03b and gen_07 use deterministic synthetic-only branches; step 10 validates the
acquired invention-year inputs. The scripts read several inputs from data/raw/ with NO existence guard --
a missing one crashes the pipeline deep in a run. This script checks them all up front and prints a
clear PRESENT/MISSING/OPTIONAL table, exiting nonzero if any REQUIRED input is absent, so a coverage
gap surfaces immediately (not as an opaque KeyError three steps in).

Run AFTER `python3 synthetic_pipeline/materialize_simulation.py --for-gen-run` and BEFORE
`python3 run_all.py --synthetic-from-raw --force-estimation`.
"""
import os
import json
import re
import sys

import numpy as np
import pandas as pd

import fromraw_contract

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
DERIVED = os.path.join(ROOT, "data", "derived")

# --- inputs the RUNNABLE gen steps read (from config.GEN_RAW_FILES + the hardcoded reads the
# gen-phase I/O map surfaced). REQUIRED = crashes if absent; OPTIONAL = the script guards/skips. ---
PUBLIC_RAW = [   # shipped FDA/public inputs (must be present in a deposited package)
    "501k_all.csv", "all_pma_approvals.txt", "foiclass.txt", "KPSS_2019_public.csv",
    "CPI_deflator.csv", "3_2_begin_final_revisions.csv", "Good_2_1_Control_2_1.txt",
    "hand_coded_intuitive_3_2.csv", "2_1_GPT_Price_Links.csv", "3_2_GPT_Price_Links.csv",
    "device-recall-0001-of-0001-2.json",
    "innovation_year_2_1_FDA_project.csv", "innovation_year_3_2_FDA_project.csv",
    "innovation_year_all_other_FDA_project.csv",
    "GRID/types.csv",
    "MAUDE/masterevent.txt", "MAUDE/patient.txt",
    "MAUDE/deviceproblems.txt", "MAUDE/problemcodedesc.txt",
    "MAUDE_2020/masterevent.txt", "MAUDE_2020/patient.txt",
    "MAUDE_2020/deviceproblems.txt", "MAUDE_2020/problemcodedesc.txt",
]
SIM_RAW = [      # restricted, provided as synthetic RAW by the generators + materialize
    "FDA_pats_original_firmname.csv", "expanded_3_2_pats.csv", "missed_2_1_pats.csv",
    "expanded_2_1_pats.csv", "all_PC_pats.csv", "all_pats_wtitlesCPC.csv", "FDA_patents_text.csv",
    "compustat_firm_data.csv",
    # the two PC-year citation panels that gen_01 reads from RAW (added for the simulated-data route):
    "PC_by_year_cites_ApplicantOnly.csv", "PC_by_year_diff_ind_appl_only.csv",
    # forward-citation lookup read by code/09_summary_stats.py (Table 1 / D.14 citation rows):
    "Applicant_Cites_Only.csv",
    "MAUDE/All_Adverse_Event_Manufacturers.csv",
    "MAUDE/all_permnos_fname_adverse_events_oct22_24.csv",
    # synthetic twin of the RESTRICTED hand-coded manufacturer->PERMNO crosswalk, counted by
    # code/15_intext_derived_numbers.py for the "hand-linked manufacturers" in-text scalar:
    "manual_permno_corrections.csv",
    # fake-keyed twin of the PUBLIC human-expert device-to-procedure concordance. It OVERRIDES the
    # shipped real file on this route: the real one carries real HCPCS codes, which the synthetic
    # claims do not have, so 05_price_analysis's Expert robustness sample would collapse.
    "FDA_HCPCS_Xwalk_Moazzam.csv",
]
FROZEN_DERIVED = []  # the simulated-data route has no frozen transformation output
STATIC_DERIVED = [   # static prerequisites produced by no gen step (ship in the package)
    "RegNum_Factorized_Synth.csv",              # gen_01 "synth_number" master
]
SIM_DERIVED = [
    os.path.relpath(os.path.join(ROOT, p), DERIVED)
    for p in fromraw_contract.ACQUISITION_DERIVED
]
STATIC_RAW = []
DIR_INPUTS = [       # public directory inputs; each must contain at least one real device file
    ("MAUDE/device_data", RAW), ("MAUDE_2020/device_data", RAW),
]
OPTIONAL = []


def _check(names, base, kind, problems):
    for n in names:
        p = os.path.join(base, n)
        ok = os.path.exists(p)
        print(f"  [{'OK ' if ok else 'MISS'}] {kind:14s} {n}")
        if not ok:
            problems.append(f"{kind}: {n} (expected at {os.path.relpath(p, ROOT)})")


def _check_patent_replacement_contract(problems):
    """Reproduce gen_01's patent replacement logic and fail before an expensive run.

    The supplemental patent files replace the base history for every product code they
    contain. They must therefore stay in their public event-specific scopes, use one
    canonical (code, year) per synthetic patent, preserve all structurally eligible
    recall-treated codes, and keep phase-11 treated support below control capacity.
    """
    n_problems_before = len(problems)
    full_path = os.path.join(
        ROOT, "synthetic_pipeline", "_synthetic_source_internal", "public_master_skeleton.parquet"
    )
    needed = [
        os.path.join(RAW, "all_PC_pats.csv"),
        os.path.join(RAW, "missed_2_1_pats.csv"),
        os.path.join(RAW, "expanded_2_1_pats.csv"),
        os.path.join(RAW, "expanded_3_2_pats.csv"),
    ]
    if not os.path.exists(full_path) or any(not os.path.exists(p) for p in needed):
        return

    panel = pd.read_parquet(full_path, columns=[
        "PRODUCTCODE", "year", "year_reclassified_2_1",
        "year_reclassified_3_2", "controls",
    ])
    panel["PRODUCTCODE"] = panel["PRODUCTCODE"].astype(str)
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce")
    design = panel.drop_duplicates("PRODUCTCODE")
    design["PRODUCTCODE"] = design["PRODUCTCODE"].astype(str)
    event_codes = {
        "2_1": set(design.loc[design["year_reclassified_2_1"].notna(), "PRODUCTCODE"]),
        "3_2": set(design.loc[design["year_reclassified_3_2"].notna(), "PRODUCTCODE"]),
    }

    def read_view(filename):
        p = os.path.join(RAW, filename)
        d = pd.read_csv(
            p, usecols=["id", "year", "PRODUCTCODE", "filing_status"],
            dtype={"id": str, "PRODUCTCODE": str}, low_memory=False,
        )
        d["PRODUCTCODE"] = d["PRODUCTCODE"].astype(str)
        d["year"] = pd.to_numeric(d["year"], errors="coerce")
        return d

    base_all = read_view("all_PC_pats.csv")
    missed_all = read_view("missed_2_1_pats.csv")
    honed_all = read_view("expanded_2_1_pats.csv")
    expanded_all = read_view("expanded_3_2_pats.csv")
    for label, frame, event in (
        ("missed_2_1_pats.csv", missed_all, "2_1"),
        ("expanded_2_1_pats.csv", honed_all, "2_1"),
        ("expanded_3_2_pats.csv", expanded_all, "3_2"),
    ):
        outside = sorted(set(frame["PRODUCTCODE"].dropna()) - event_codes[event])
        if outside:
            problems.append(
                f"patent-scope: {label} contains {len(outside)} code(s) outside {event}: "
                f"{outside[:10]}"
            )

    all_views = pd.concat(
        [base_all.assign(_source="base"), missed_all.assign(_source="missed"),
         honed_all.assign(_source="honed"), expanded_all.assign(_source="expanded")],
        ignore_index=True,
    )
    inconsistent = all_views.groupby("id").agg(
        n_codes=("PRODUCTCODE", "nunique"), n_years=("year", "nunique")
    )
    inconsistent = inconsistent[(inconsistent.n_codes > 1) | (inconsistent.n_years > 1)]
    if len(inconsistent):
        problems.append(
            f"patent-consistency: {len(inconsistent)} patent id(s) have conflicting code/year "
            "across synthetic files"
        )

    # Exact Phase-4 replacement/filter order from gen_01_main_panels.py.
    base = base_all[base_all["filing_status"].eq("Grant")].copy()
    missed = missed_all[missed_all["filing_status"].eq("Grant")].copy()
    honed = honed_all[honed_all["filing_status"].eq("Grant")].copy()
    expanded = expanded_all[expanded_all["filing_status"].eq("Grant")].copy()
    supplements = pd.concat([missed, honed, expanded], ignore_index=True)
    base = base[~base["PRODUCTCODE"].isin(supplements["PRODUCTCODE"])]
    base = base[~base["id"].isin(supplements["id"])]
    effective = pd.concat([base, missed, honed, expanded], ignore_index=True)
    rng = np.random.RandomState(42)
    effective = effective.iloc[rng.permutation(len(effective))].drop_duplicates("id")
    effective_in_panel = effective.merge(
        panel[["PRODUCTCODE", "year"]].drop_duplicates(),
        on=["PRODUCTCODE", "year"], how="inner",
    )

    support_counts = {}
    missing_by_event = {}
    for event, label in (("2_1", "II->I"), ("3_2", "III->II")):
        cohort = design.set_index("PRODUCTCODE")[f"year_reclassified_{event}"]
        treated = set(cohort[cohort.notna()].index)
        event_year = effective_in_panel["PRODUCTCODE"].map(cohort)
        pre_supported = set(effective_in_panel.loc[
            event_year.notna() & (effective_in_panel["year"] < event_year), "PRODUCTCODE"
        ])
        missing_treated = sorted(treated - pre_supported)
        support_counts[event] = (len(treated) - len(missing_treated), len(treated))
        missing_by_event[event] = missing_treated
        if missing_treated and event == "3_2":
            problems.append(
                f"patent-support: {len(missing_treated)}/{len(treated)} {label} treated code(s) "
                f"lack a pre-event Grant after gen_01 replacement: {missing_treated[:10]}"
            )

    controls = set(design.loc[design["controls"].eq(1), "PRODUCTCODE"])
    present = set(effective_in_panel["PRODUCTCODE"])
    missing_controls = sorted(controls - present)
    if missing_controls:
        problems.append(
            f"patent-support: {len(missing_controls)}/{len(controls)} control code(s) "
            f"lack any Grant after gen_01 replacement: {missing_controls[:10]}"
        )

    with open(os.path.join(RAW, "device-recall-0001-of-0001-2.json")) as handle:
        recall_obj = json.load(handle)
    recall = pd.DataFrame(recall_obj.get("results", recall_obj))
    recall_codes = set(recall["product_code"].dropna().astype(str).str.strip())
    cohort_21 = design.set_index("PRODUCTCODE")["year_reclassified_2_1"]
    panel_event = panel["PRODUCTCODE"].map(cohort_21)
    eligible_recall_treated = set(panel.loc[
        panel_event.notna()
        & (panel["year"] < panel_event)
        & (panel["year"] > 1991)
        & (panel["year"] <= 1996),
        "PRODUCTCODE",
    ])
    required_recall_treated = event_codes["2_1"] & recall_codes & eligible_recall_treated
    missing_recall_treated = sorted(
        required_recall_treated - set(effective_in_panel.loc[
            (effective_in_panel["PRODUCTCODE"].isin(event_codes["2_1"]))
            & (effective_in_panel["year"] < effective_in_panel["PRODUCTCODE"].map(
                design.set_index("PRODUCTCODE")["year_reclassified_2_1"]
            )),
            "PRODUCTCODE",
        ])
    )
    if missing_recall_treated:
        problems.append(
            f"patent-support: {len(missing_recall_treated)}/"
            f"{len(required_recall_treated)} public recall-treated II->I code(s) lack "
            f"pre-event panel support: {missing_recall_treated[:10]}"
        )

    # Phase 11 performs one-to-one matching without replacement over a public
    # regulation-number control universe that is broader than `controls`. Reproduce
    # that selection and fail before generation if its synthetic controls run out.
    synth_path = os.path.join(DERIVED, "RegNum_Factorized_Synth.csv")
    good_path = os.path.join(RAW, "Good_2_1_Control_2_1.txt")
    phase11_summary = "phase11 unavailable"
    if os.path.exists(synth_path) and os.path.exists(good_path):
        synth = pd.read_csv(synth_path, dtype={"REGULATIONNUMBER": str}, low_memory=False)
        synth["REGULATIONNUMBER"] = synth["REGULATIONNUMBER"].str.pad(
            width=8, side="right", fillchar="0"
        )
        synth = synth.drop_duplicates("PRODUCTCODE_x")
        synth["PRODUCTCODE"] = synth["PRODUCTCODE_x"].astype(str)

        def get_years(row):
            try:
                values = re.findall(r"\,+\ +[0-9]{1,4}", row.Reg_Change_Text)
                values = [int(value.replace(", ", "")) for value in values]
                return "None" if not values else values
            except Exception:
                return "Null"

        synth["reclass_years"] = synth.apply(get_years, axis=1)
        no_reclass = set(synth.loc[synth.reclass_years == "None", "PRODUCTCODE"])
        with open(good_path) as handle:
            chunks = handle.read().split("§")
        good_regnums = set()
        for value in chunks:
            value = value.strip()
            if (re.search(r"\d\d\d+\.+\d", value)
                    and not re.search(r"\d\d\d+\.+9", value)):
                good_regnums.add(value[:8])
        good_codes = set(synth.loc[
            synth["REGULATIONNUMBER"].isin(good_regnums), "PRODUCTCODE"
        ])

        public_panel = pd.read_parquet(
            full_path,
            columns=["PRODUCTCODE", "DEVICECLASS", "year_reclassified_2_1"],
        ).drop_duplicates("PRODUCTCODE")
        public_panel["PRODUCTCODE"] = public_panel["PRODUCTCODE"].astype(str)
        treated_design = set(public_panel.loc[
            public_panel["year_reclassified_2_1"].notna(), "PRODUCTCODE"
        ])
        class1 = public_panel["DEVICECLASS"].astype(str).eq("1")
        candidate_controls = set(public_panel.loc[
            (public_panel["PRODUCTCODE"].isin(no_reclass)
             | (class1 & ~public_panel["PRODUCTCODE"].isin(treated_design)))
            & public_panel["PRODUCTCODE"].isin(good_codes),
            "PRODUCTCODE",
        ]) & set(design.loc[design["controls"].eq(1), "PRODUCTCODE"])
        effective_event = effective_in_panel["PRODUCTCODE"].map(cohort_21)
        treated_supported = set(effective_in_panel.loc[
            effective_event.notna() & (effective_in_panel["year"] < effective_event),
            "PRODUCTCODE",
        ])
        controls_supported = candidate_controls & present
        phase11_summary = (
            f"phase11 treated={len(treated_supported)}, controls={len(controls_supported)}"
        )
        if len(controls_supported) < len(treated_supported):
            problems.append(
                "patent-support: gen_01 phase-11 one-to-one matching would exhaust "
                f"controls ({len(controls_supported)} controls for "
                f"{len(treated_supported)} treated codes)"
            )

    print(
        f"  [{'OK ' if len(problems) == n_problems_before else 'FAIL'}] "
        f"{'patent-contract':14s} effective={len(effective):,}; "
        f"II->I pre-supported={support_counts['2_1'][0]}/{support_counts['2_1'][1]}; "
        f"III->II pre-supported={support_counts['3_2'][0]}/{support_counts['3_2'][1]}; "
        f"controls supported={len(controls) - len(missing_controls)}/{len(controls)}; "
        f"{phase11_summary}"
    )


def _check_post_run(problems):
    for rel in fromraw_contract.all_transformation_outputs():
        path = os.path.join(ROOT, rel)
        ok = (os.path.isfile(path) and not os.path.islink(path)
              and os.path.getsize(path) > 0 and os.access(path, os.R_OK))
        print(f"  [{'OK ' if ok else 'MISS'}] {'new-output':14s} {rel}")
        if not ok:
            problems.append(f"missing/empty/symlinked transformation output: {rel}")


def main(post_run=False):
    print(f"Simulated-data route preflight — checking inputs under {os.path.relpath(RAW, ROOT)} / "
          f"{os.path.relpath(DERIVED, ROOT)}\n")
    problems = []
    _check(PUBLIC_RAW, RAW, "public-raw", problems)
    _check(SIM_RAW, RAW, "synthetic-raw", problems)
    _check(SIM_DERIVED, DERIVED, "synthetic-input", problems)
    _check(STATIC_RAW, RAW, "static-raw", problems)
    _check(FROZEN_DERIVED, DERIVED, "frozen-derived", problems)
    _check(STATIC_DERIVED, DERIVED, "static-derived", problems)

    # The --for-gen-run materializer must leave only acquisition-level inputs.
    # Any other simulated destination or the three fuzzy-dedup caches would let a
    # transformation reuse an existing output and invalidates the no-skip route.
    try:
        import materialize_simulation as materialize
        raw_dests = {os.path.normpath(d) for _, d in materialize.plan_destinations(for_gen_run=True)}
        stale = []
        for _, dest in materialize.plan_destinations(for_gen_run=False):
            if os.path.normpath(dest) not in raw_dests and (os.path.isfile(dest) or os.path.islink(dest)):
                stale.append(os.path.relpath(dest, ROOT))
        for rel in fromraw_contract.all_transformation_outputs():
            path = os.path.join(ROOT, rel)
            if os.path.isfile(path) or os.path.islink(path):
                stale.append(rel)
        stale = sorted(set(stale))
        if stale and not post_run:
            problems.append("pre-existing transformation outputs/caches: " + ", ".join(sorted(stale)[:20]))
        if not post_run:
            print(f"  [{'OK ' if not stale else 'FAIL'}] {'zero-bypass':14s} "
                  f"pre-existing transformation outputs/caches={len(stale)}")
    except Exception as exc:
        problems.append(f"zero-bypass inventory failed: {exc}")
    for name, base in DIR_INPUTS:
        p = os.path.join(base, name)
        files = []
        if os.path.isdir(p) and not os.path.islink(p):
            files = [entry for entry in os.scandir(p)
                     if entry.is_file(follow_symlinks=False) and not entry.name.startswith(".")]
        ok = bool(files)
        print(f"  [{'OK ' if ok else 'MISS'}] {'public-dir':14s} {name}{'/' }")
        if not ok:
            problems.append(f"public-dir: {name}/ must be a real directory with at least one regular file "
                            f"(expected at {os.path.relpath(p, ROOT)})")
    print()
    for rel, base, why in OPTIONAL:
        ok = os.path.exists(os.path.join(base, rel))
        print(f"  [{'OK ' if ok else 'opt '}] {'optional':14s} {rel}  ({why})")

    _check_patent_replacement_contract(problems)
    if post_run:
        _check_post_run(problems)

    print()
    if problems:
        print(f"PREFLIGHT FAIL — {len(problems)} required input(s) missing:")
        for p in problems:
            print(f"  - {p}")
        print("\nRun `python3 synthetic_pipeline/materialize_simulation.py --for-gen-run` first. "
              "`--for-gen-run` is the form this preflight checks: it materializes only the "
              "acquisition-level inputs and clears every contracted transformation output, which is "
              "what the official no-skip route requires. Then confirm the public FDA inputs + MAUDE "
              "symlink ship in the package. Do NOT run the simulated-data route until this passes.")
        return 1
    if post_run:
        print("POST-RUN CONTRACT PASS — every contracted transformation output is present and nonempty.")
    else:
        print("PREFLIGHT PASS — every required from-raw input is present and every transformation "
              "output is absent. Next:\n"
              "  python3 run_all.py --synthetic-from-raw --force-estimation")
    return 0


if __name__ == "__main__":
    sys.exit(main(post_run="--post-run" in sys.argv[1:]))
