"""
materialize_simulation.py -- place the PUBLICLY-REDISTRIBUTABLE simulated dataset
into the pipeline's data/ locations so the full analysis runs with no restricted
data (JPE Data Policy Option 2, published-synthetic route).

Run from the package root. The simulated-data route materializes only
acquisition-level simulated inputs, verifies that transformation outputs/caches
are absent, and then executes every transformation:

    python3 materialize_simulation.py --for-gen-run
    python3 synthetic_pipeline/preflight_from_raw.py
    python3 run_all.py --synthetic-from-raw --force-estimation

SAFETY EXHIBITS (steps 16/17 -> Table D.12), VALIDATED 2026-07-13:
`gen_00h_synthetic_patent_text.py` generates a pure-synthetic `FDA_patents_text.csv` (routed here
to data/raw) so 06b/06c run on synthetic text. Steps 16/17 regenerate the safety estimate CSVs and
step 31 rebuilds Table D.12 from them (synthetic values differ from the paper). Run:

    python3 run_all.py --synthetic-from-raw --force-estimation \
        --regenerate-safety-keywords --regenerate-safety-embeddings   # steps 16 + 31
    # There is no separate numpy sub-environment: the pinned environment already provides
    # numpy 1.26.4 (see requirements-lock.txt), so step 17 (06c embedding) runs under the same
    # interpreter as every other step. The optional FDA_SAFETY_EMBED_PYTHON override exists only
    # for hosts that need to name that interpreter explicitly; leave it unset.

The simulated data ships in simulated_data/ (public). It is a pure simulation:
- every patent identifier is synthetic (no real USPTO numbers; see
  synthetic_pipeline/generators/gen_00g_deidentify_patents.py),
- firm / inventor / assignee / permno / gvkey identities are synthetic,
- all financial values, outcomes, and text are randomized.
Real FDA product codes and regulatory event years are public and retained. Patent ids,
patent filing years, and patent->product-code assignments are generated in an independent
seeded universe; event-specific support constraints provide the variation the estimators
need without retaining the real patent->code distribution.
Numbers produced differ from the paper by construction; the simulated-data route verifies that the
code executes and generates all outputs, not that results match.

WARNING: this OVERWRITES files under data/. Run only on the published package (which
contains no real restricted data) or a throwaway copy -- never over a licensed
real-data working tree.
"""
import os
import sys
import glob
import shutil

import fromraw_contract

_SP = os.path.dirname(os.path.abspath(__file__))   # synthetic_pipeline/
ROOT = os.path.dirname(_SP)                         # package root (parent of synthetic_pipeline/)
SIM = os.path.join(_SP, "simulated_data")
DERIVED = os.path.join(ROOT, "data", "derived")
RAW = os.path.join(ROOT, "data", "raw")


# Patent-subtree members whose reader resolves them under data/raw/ even though their basename
# matches one of the data/derived/ prefixes below. Applicant_Cites_Only.csv is read by
# code/09_summary_stats.py:load_patent_data as config.RAW_DATA_DIR / "Applicant_Cites_Only.csv"
# (and is listed under data/raw/ in RESTRICTED_FILE_INVENTORY.csv), so the generic
# "Applicant_* -> derived" rule would put it where nothing looks for it.
_PATENT_RAW_OVERRIDES = {"Applicant_Cites_Only.csv"}

# MAUDE-linkage members that do NOT live under data/raw/MAUDE/. The synthetic twin of the
# restricted manufacturer->PERMNO crosswalk is read by code/15_intext_derived_numbers.py as
# data/raw/manual_permno_corrections.csv (and by gen_07's REAL branch at the same path), so the
# generic "-> data/raw/MAUDE/" rule for this subtree would put it where nothing looks for it.
_MAUDE_RAW_OVERRIDES = {"manual_permno_corrections.csv"}


def _maude_linkage_router(rel):
    b = os.path.basename(rel)
    if b in _MAUDE_RAW_OVERRIDES:
        return os.path.join(RAW, b)
    return os.path.join(RAW, "MAUDE", rel)


def _patent_router(rel):
    b = os.path.basename(rel)
    if b in _PATENT_RAW_OVERRIDES:
        return os.path.join(RAW, b)
    if b.startswith(("safety_", "Applicant_")):
        return os.path.join(DERIVED, b)
    # PC_by_year_* are RAW inputs (config.GEN_RAW_FILES pc_by_year_*): gen_01 reads them from
    # data/raw/ with no existence guard, so they must land in raw for the simulated-data route.
    return os.path.join(RAW, rel)  # PC_by_year_* + patent files -> raw; keeps new_patent_analysis/ subpath


# One (subdir -> router) entry per simulated source tree. main() and plan_destinations()
# share this table so the destination map can NEVER drift from what actually gets copied.
_ROUTERS = [
    ("synthetic_marketscan",      lambda r: os.path.join(DERIVED, r)),
    ("synthetic_dimensions_wrds", lambda r: os.path.join(RAW, r)
                                  if os.path.basename(r) == "compustat_firm_data.csv"
                                  else os.path.join(DERIVED, r)),
    ("synthetic_maude_linkage",   _maude_linkage_router),
    ("synthetic_patents",         _patent_router),
    ("synthetic_nexis",           lambda r: os.path.join(RAW, "Liability", r)),
    ("synthetic_kpst",            lambda r: os.path.join(RAW, r)),
    # Fake-keyed synthetic replacement for the public KPSS file. It is needed
    # only by the official from-raw route, but keeping it in the shared router
    # makes every copied byte part of the reviewed destination map.
    ("synthetic_kpss",            lambda r: os.path.join(RAW, r)),
    # Synthetic GPT price-link crosswalks (gen_00c) OVERRIDE the shipped real data/raw/*_GPT_Price_Links.csv
    # on both simulated routes so the synthetic-HCPCS MarketScan claims and 05_price's crosswalk stay
    # consistent (the real crosswalk covers only the frozen real matched sample, so a regenerated synthetic
    # matched sample would lose every price control -> feols "posttreat collinear"). Real-data reproduction
    # never runs materialize, so it keeps the deposited real crosswalk.
    ("synthetic_price_links",     lambda r: os.path.join(RAW, r)),
]


_FROM_RAW_DERIVED_INPUTS = {
    # The provider-created aggregate interface is the starting input for the
    # deposited transformations; no deposited step creates it (it is the output of
    # code/00_generate_data/gen_00b_marketscan_extraction.py, run at NBER).
    "outpatient_combined_censored.csv",
}


def _is_from_raw_input(dest):
    dabs = os.path.normpath(os.path.abspath(dest))
    raw_prefix = os.path.normpath(os.path.abspath(RAW)) + os.sep
    return dabs.startswith(raw_prefix) or os.path.basename(dabs) in _FROM_RAW_DERIVED_INPUTS


def plan_destinations(for_gen_run=False):
    """Return the COMPLETE list of (src_abs, dest_abs) materialization pairs WITHOUT copying,
    by applying the exact same routers main() uses. This is the authoritative source->destination
    map: the certification harness reads certification/MATERIALIZE_DESTINATIONS.tsv (each destination
    tagged with a reviewed precondition -- ABSENT for restricted-only destinations, or
    SANITIZED_PUBLIC / PUBLIC_EXPECTED for the two that also ship publicly and are schema/hash
    validated) and the build verifies that shipped map equals this routing (so it can't drift)."""
    pairs = []
    for subdir, router in _ROUTERS:
        src_dir = os.path.join(SIM, subdir)
        for p in sorted(glob.glob(os.path.join(src_dir, "**", "*"), recursive=True)):
            if os.path.isdir(p):
                continue
            dest = router(os.path.relpath(p, src_dir))
            if not for_gen_run or _is_from_raw_input(dest):
                pairs.append((p, dest))
    return pairs


def _assert_safe_dest(dest):
    """Standalone materialization must NOT follow a destination symlink out of the
    package. Walk every path component from ROOT down to dest and reject any symlink;
    reject a dest that resolves outside the real package root. (The build-time guards
    protect only the BUILT package; this script also runs standalone -- as the
    certification harness and reproducers do.)"""
    root_real = os.path.realpath(ROOT)
    dabs = os.path.normpath(os.path.abspath(dest))
    rel = os.path.relpath(dabs, ROOT)
    if rel == ".." or rel.startswith(".." + os.sep):
        raise SystemExit(f"REFUSING to materialize OUTSIDE the package root: {dest}")
    cur = ROOT
    for part in rel.split(os.sep):
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            raise SystemExit(f"REFUSING to materialize: SYMLINK in destination path "
                             f"({cur} -> {os.readlink(cur)}) could write outside the package.")
    parent = os.path.dirname(dabs)
    if os.path.exists(parent) and os.path.commonpath([os.path.realpath(parent), root_real]) != root_real:
        raise SystemExit(f"REFUSING to materialize: destination parent resolves OUTSIDE "
                         f"the package root {root_real}: {os.path.realpath(parent)}")


def _clean_from_raw_transformation_outputs():
    """Delete any materialized transformation output/caches from the throwaway route.

    The simulated-data route must begin with acquisition-level inputs. Public
    sanitized analysis data and old synthetic derived outputs cannot remain in
    place where a transformation could reuse them.
    """
    removed = []
    from_raw = {os.path.normpath(d) for _, d in plan_destinations(for_gen_run=True)}
    for _, dest in plan_destinations(for_gen_run=False):
        if os.path.normpath(dest) in from_raw:
            continue
        if os.path.isfile(dest) or os.path.islink(dest):
            _assert_safe_dest(dest)
            os.remove(dest)
            removed.append(os.path.relpath(dest, ROOT))
    # Remove the complete, reviewed transformation-output inventory. This is
    # intentionally broader than the simulated destination map: public or stale
    # intermediates must not let a transformation take an if-exists shortcut.
    for rel in fromraw_contract.all_transformation_outputs():
        dest = os.path.join(ROOT, rel)
        if os.path.isfile(dest) or os.path.islink(dest):
            _assert_safe_dest(dest)
            os.remove(dest)
            removed.append(os.path.relpath(dest, ROOT))
    print(f"Removed {len(removed)} pre-existing transformation output/cache file(s).")


_COPY_CHUNK = 8 << 20


def _copy_verified(src, dest):
    """Copy with an explicit read/write loop, an fsync, and a post-copy size check.

    shutil.copy2 delegates to os.sendfile / copy_file_range and never fsyncs, so a
    write that fails when the kernel flushes it is reported nowhere: close() discards
    the deferred error, leaving the destination a page-aligned prefix of the source,
    or empty. On a parallel filesystem at a quota or space ceiling that is a live
    failure mode rather than a theoretical one.

    The size check is the part that matters. A truncated .xlsx raises BadZipFile, but
    a truncated .csv is read without complaint, so an unverified copy can move every
    number the pipeline goes on to produce while every gate still reports PASS.
    """
    with open(src, "rb") as fi, open(dest, "wb") as fo:
        for block in iter(lambda: fi.read(_COPY_CHUNK), b""):
            fo.write(block)
        fo.flush()
        os.fsync(fo.fileno())
    shutil.copystat(src, dest)
    src_bytes = os.path.getsize(src)
    dest_bytes = os.path.getsize(dest)
    if dest_bytes != src_bytes:
        raise SystemExit(
            "ABORT: materialize wrote {} of {} bytes to {}.\n"
            "The copy was truncated, so the run stops here rather than letting a step "
            "read a short file. If the destination filesystem is near a quota or space "
            "limit, free space and rerun (on Lustre, `lfs quota -v -u $USER <fs>` shows "
            "per-OST headroom, which can be exhausted while the total still looks "
            "ample).".format(dest_bytes, src_bytes, dest)
        )


def main(for_gen_run=False):
    if os.path.islink(_SP):
        raise SystemExit(f"synthetic_pipeline/ is a SYMLINK ({_SP} -> {os.readlink(_SP)}) -- "
                         f"forbidden (its simulated_data/ could resolve to external data).")
    if not os.path.isdir(SIM):
        raise SystemExit("simulated_data/ not found (run from the package root).")
    total = 0
    for src, dest in plan_destinations(for_gen_run=for_gen_run):
        if os.path.islink(src):
            raise SystemExit(f"REFUSING to materialize: simulated SOURCE is a symlink "
                             f"({src} -> {os.readlink(src)}) -- would copy external bytes into data/.")
        _assert_safe_dest(dest)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        _copy_verified(src, dest)
        total += 1

    # remove trained LDA/word2vec models so 11a retrains on the simulated text
    removed = 0
    for pat in ("lda_*.model*", "lda_dictionary_*.dict", "lda_bigram_*.model",
                "lda_trigram_*.model", "word2vec_patent_corpus.model*"):
        for p in glob.glob(os.path.join(DERIVED, pat)):
            os.remove(p)
            removed += 1

    if for_gen_run:
        _clean_from_raw_transformation_outputs()
    print(f"Materialized {total} simulated {'acquisition inputs' if for_gen_run else 'files'} into data/.")
    print(f"Removed {removed} trained model artifact(s) (11a retrains on simulated text).")
    print("Next:")
    print("  official no-skip route: python3 synthetic_pipeline/preflight_from_raw.py && \\")
    print("       python3 run_all.py --synthetic-from-raw --force-estimation "
          "--regenerate-safety-keywords --regenerate-safety-embeddings")
    print("(--force-estimation makes 03a/03b recompute every estimate on the simulated "
          "data instead of reusing shipped CSVs.)")


def _list_destinations(for_gen_run=False):
    """Print the source->destination map, TAB-separated, paths relative to the package root,
    sorted by destination. Used to generate/verify certification/MATERIALIZE_DESTINATIONS.tsv."""
    rows = []
    for src, dest in plan_destinations(for_gen_run=for_gen_run):
        rows.append((os.path.relpath(src, ROOT).replace(os.sep, "/"),
                     os.path.relpath(dest, ROOT).replace(os.sep, "/")))
    for src_rel, dest_rel in sorted(rows, key=lambda t: t[1]):
        print(f"{src_rel}\t{dest_rel}")


def _parse_args(argv):
    """Real argument parsing with a real --help.

    Until this was added the script simply asked `"--for-gen-run" in argv`, so `--help`, `-h`
    or any typo (`--for-genrun`) fell through to the FULL materialization -- several GB copied
    into data/, and the WRONG overlay for the simulated-data route, with no error at the point
    of the mistake. An unrecognised argument now stops the run.
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog="materialize_simulation.py",
        description=("Copy the publicly-redistributable simulated dataset into the pipeline's "
                     "data/ locations so the full analysis runs with no restricted data."),
        epilog=("Simulated-data route:\n"
                "  python3 synthetic_pipeline/materialize_simulation.py --for-gen-run\n"
                "  python3 synthetic_pipeline/preflight_from_raw.py\n"
                "  python3 run_all.py --synthetic-from-raw --clean-output \\\n"
                "      --regenerate-safety-keywords --regenerate-safety-embeddings\n"
                "\nWARNING: this OVERWRITES files under data/. Run it on the published package "
                "or a throwaway copy, never over a licensed real-data working tree."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source-dir", metavar="PATH",
        help="Materialize from this generated payload instead of the package's "
             "synthetic_pipeline/simulated_data/.")
    parser.add_argument(
        "--for-gen-run", action="store_true",
        help="Place ONLY the acquisition-level inputs the simulated-data route starts from, and "
             "delete every transformation output/cache so no step can take an if-exists "
             "shortcut. THIS IS THE FLAG THE SIMULATED-DATA ROUTE NEEDS. Without it, every "
             "simulated file is placed, including transformation outputs.")
    parser.add_argument(
        "--list-destinations", action="store_true",
        help="Print the full source->destination map (TAB-separated) and exit. Copies nothing.")
    parser.add_argument(
        "--list-for-gen-destinations", action="store_true",
        help="Print the --for-gen-run source->destination map and exit. Copies nothing.")
    args = parser.parse_args(argv)
    if args.list_destinations and args.list_for_gen_destinations:
        parser.error("--list-destinations and --list-for-gen-destinations are mutually exclusive")
    return args


if __name__ == "__main__":
    _args = _parse_args(sys.argv[1:])
    if _args.source_dir:
        SIM = os.path.abspath(_args.source_dir)
    if _args.list_destinations:
        _list_destinations()
    elif _args.list_for_gen_destinations:
        _list_destinations(for_gen_run=True)
    else:
        main(for_gen_run=_args.for_gen_run)
