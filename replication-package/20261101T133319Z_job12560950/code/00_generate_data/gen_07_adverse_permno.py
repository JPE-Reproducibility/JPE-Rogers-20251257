"""
gen_07_adverse_permno.py -- Generate adverse-event-to-PERMNO linkage

Produces:
    data/derived/all_adv_events_w_permno5.csv

Maps MAUDE adverse-event manufacturer names to CRSP PERMNOs via two-stage
pandas_dedupe entity resolution (within-manufacturer dedup, then link to
CRSP), followed by the 70 manual corrections for major medical-device firms
held in data/raw/manual_permno_corrections.csv.

Pipeline:
    1. Load raw MAUDE manufacturer data (MDR_REPORT_KEY, MANUFACTURER_D_NAME).
    2. Load pre-built PERMNO universe (firm_name, permno) from CRSPDirectory,
       patent data, and AllPublicCompanies (pre-merged).
    3. Text preprocess: tokenize (RegexpTokenizer), lemmatize (WordNet, verb),
       stopword removal → clean_name.
    4. Deduplicate manufacturers via pandas_dedupe.dedupe_dataframe(['clean_name']).
    5. Find most common clean_name per cluster; merge clusters back to all rows.
    6. Link deduped manufacturer clusters to PERMNO universe via
       pandas_dedupe.link_dataframes(['most common']).
    7. Post-link merge: propagate PERMNO within linked clusters.
    8. Apply the 70 manual corrections (medtronic, dexcom, baxter, etc.).
    9. Deduplicate on MDR_REPORT_KEY and save 6-column output.

Reads:
    data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv
    data/raw/MAUDE/all_permnos_fname_adverse_events_oct22_24.csv
    data/derived/dedupe_settings/adverse_events/dedupe_dataframe_learned_settings
    data/raw/MAUDE/link_dataframes_learned_settings
    data/raw/manual_permno_corrections.csv   (RESTRICTED: manufacturer->CRSP PERMNO
        manual crosswalk; proprietary PERMNOs, withheld from the public deposit,
        ships only in the restricted archive; this step is restricted-data-only)

Writes:
    data/derived/all_adv_events_w_permno5.csv
    data/derived/All_Adverse_Event_Manufacturers_Deduped.csv (intermediate)

Source logic: Dedupe_Manuf_firm_size_adverse_events.py
"""

import os
import sys
import csv
import json
import hashlib
import shutil
import tempfile
import warnings
from pathlib import Path
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd

SYNTHETIC_MODE = os.environ.get("FDA_SYNTHETIC_MODE") == "1"
if not SYNTHETIC_MODE:
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import RegexpTokenizer
    from nltk.corpus import stopwords
    import pandas_dedupe

# pandas_dedupe 1.5 still calls DataFrame.append internally.  pandas removed
# that method in 2.0, so provide the old behavior for the package call below.
if not SYNTHETIC_MODE and not hasattr(pd.DataFrame, "append"):
    def _dataframe_append(self, other, ignore_index=False, sort=False, **kwargs):
        return pd.concat([self, other], ignore_index=ignore_index, sort=sort)
    pd.DataFrame.append = _dataframe_append

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR))
import config
sys.path.insert(0, str(config.MODULES_DIR))
from manufacturer_linkage_coverage import write_coverage

DERIVED = config.DERIVED_DATA_DIR
RAW = config.RAW_DATA_DIR
MAUDE_DIR = RAW / "MAUDE"

OUTPUT_FILE = DERIVED / "all_adv_events_w_permno5.csv"

# Source directories for dedupe settings
DEDUP_SETTINGS_DIR = DERIVED / "dedupe_settings" / "adverse_events"
LINK_SETTINGS_DIR = MAUDE_DIR


def _generate_synthetic(out_path):
    """Execute the linkage on synthetic raw inputs without CRSP or dedupe models.

    The simulator assigns exact synthetic firm labels to fake PERMNOs. This
    branch therefore performs a deterministic exact join. It is enabled only by
    run_all.py --synthetic-from-raw; the licensed real-data algorithm below is
    unchanged.
    """
    manufacturers_path = MAUDE_DIR / "All_Adverse_Event_Manufacturers.csv"
    firms_path = MAUDE_DIR / "all_permnos_fname_adverse_events_oct22_24.csv"
    for path in (manufacturers_path, firms_path):
        if not path.is_file():
            raise RuntimeError(f"synthetic gen_07 input is missing: {path}")
    if out_path.is_symlink():
        raise RuntimeError(f"refusing to overwrite symlink output: {out_path}")

    firms = pd.read_csv(firms_path, usecols=["firm_name", "permno"])
    if firms["firm_name"].isna().any() or firms["firm_name"].duplicated().any():
        raise RuntimeError("synthetic firm universe must have unique, nonmissing firm_name values")
    lookup = firms.set_index("firm_name")["permno"]

    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    if tmp.exists():
        tmp.unlink()
    seen = set()
    wrote_header = False
    n_rows = n_linked = 0
    # First MDR_REPORT_KEY seen for each distinct manufacturer name, in stream order. Used below
    # to rebuild the manufacturer-cluster intermediate that the real branch writes in Phase 4, so
    # the synthetic route regenerates it too instead of leaving the deposited real copy in place.
    first_key_by_name = {}
    for chunk in pd.read_csv(manufacturers_path, chunksize=500_000, low_memory=False):
        required = {"MDR_REPORT_KEY", "MANUFACTURER_D_NAME"}
        if not required.issubset(chunk.columns):
            raise RuntimeError(f"synthetic manufacturer input lacks {sorted(required - set(chunk.columns))}")
        chunk = chunk.drop_duplicates("MDR_REPORT_KEY")
        chunk = chunk.loc[~chunk["MDR_REPORT_KEY"].isin(seen)].copy()
        seen.update(chunk["MDR_REPORT_KEY"].tolist())
        for key, nm in zip(chunk["MDR_REPORT_KEY"].tolist(),
                           chunk["MANUFACTURER_D_NAME"].tolist()):
            if pd.notna(nm) and nm not in first_key_by_name:
                first_key_by_name[nm] = key
        chunk["permno"] = chunk["MANUFACTURER_D_NAME"].map(lookup)
        chunk["clean_name"] = chunk["MANUFACTURER_D_NAME"].str.lower()
        chunk["stock_name"] = chunk["MANUFACTURER_D_NAME"].where(chunk["permno"].notna())
        chunk["manually_encoded"] = 0
        chunk["manual_stock"] = 0.0
        output = chunk[["MDR_REPORT_KEY", "clean_name", "permno", "stock_name",
                        "manually_encoded", "manual_stock"]]
        output.to_csv(tmp, mode="a", header=not wrote_header, index=False)
        wrote_header = True
        n_rows += len(output)
        n_linked += int(output["permno"].notna().sum())
    if not wrote_header:
        raise RuntimeError("synthetic manufacturer input is empty")
    os.replace(tmp, out_path)
    print(f"  Synthetic exact linkage: {n_linked:,} / {n_rows:,} rows linked")
    _write_synthetic_manufacturer_clusters(out_path, first_key_by_name)
    return n_rows


def _write_synthetic_manufacturer_clusters(out_path, first_key_by_name):
    """Write the synthetic-route counterpart of Phase 4's manufacturer-cluster intermediate.

    `All_Adverse_Event_Manufacturers_Deduped.csv` is a transparency intermediate (no shipped
    script reads it), but before 2026-09-17 only the real branch wrote it, so a synthetic run
    left the deposited REAL file in place next to freshly simulated outputs. The synthetic
    linkage is an exact name match rather than a fuzzy dedupe, so each distinct cleaned name is
    its own cluster and every match is certain: `cluster id` == `clean_name_group` and
    `confidence` == 1.0. The schema, column order and the `group` / `clean_name_group` semantics
    (category codes over the sorted distinct values) are the real branch's.
    """
    deduped_out = out_path.parent / "All_Adverse_Event_Manufacturers_Deduped.csv"
    if deduped_out.is_symlink():
        raise RuntimeError(f"refusing to overwrite symlink output: {deduped_out}")
    names = pd.Series(list(first_key_by_name.keys()), dtype=object)
    df = pd.DataFrame({
        "MDR_REPORT_KEY": [first_key_by_name[n] for n in names],
        "MANUFACTURER_D_NAME": names,
    })
    df["group"] = df["MANUFACTURER_D_NAME"].astype("category").cat.codes
    df["clean_name"] = df["MANUFACTURER_D_NAME"].str.lower()
    df["clean_name_group"] = df["clean_name"].astype("category").cat.codes
    df = df.drop_duplicates("clean_name_group").copy()
    df["cluster id"] = df["clean_name_group"]
    df["confidence"] = 1.0
    df = df[["MDR_REPORT_KEY", "MANUFACTURER_D_NAME", "group", "clean_name",
             "clean_name_group", "cluster id", "confidence"]]
    df.to_csv(deduped_out, index=False)
    print(f"    Saved intermediate: {deduped_out.name} "
          f"({len(df):,} exact-match manufacturer clusters)")


def _safe_config_name(settings_dir, prefix):
    """Return a config_name path safe for pandas_dedupe.

    pandas_dedupe replaces spaces with underscores in config_name, which
    breaks paths containing spaces. Work around this by
    copying settings to a temp directory when the path has spaces.
    """
    src = str(settings_dir / prefix)
    if " " not in src:
        return src
    tmp = tempfile.mkdtemp(prefix="dedupe_settings_")
    for suffix in ("_learned_settings", "_training.json"):
        src_file = str(settings_dir / (prefix + suffix))
        if os.path.exists(src_file):
            shutil.copy2(src_file, os.path.join(tmp, prefix + suffix))
    return os.path.join(tmp, prefix)

# ---------------------------------------------------------------------------
# NLTK text preprocessing (matches original script exactly)
# ---------------------------------------------------------------------------
if not SYNTHETIC_MODE:
    _tokenizer = RegexpTokenizer(r'\w+')
    _lemmatizer = WordNetLemmatizer()
    _stop_words = set(stopwords.words('english'))

# Word-level compatibility fixes for NLTK WordNet verb lemmatizer version
# differences. The original analysis used an older NLTK whose lemmatizer was
# more aggressive with verb-pos stripping (e.g., "holdings" → "hold").
# Current NLTK preserves these forms. Applying these substitutions AFTER
# lemmatization makes the clean_name output match the original.
_NLTK_WORD_COMPAT = {
    'aceess': 'ace',
    'acess': 'ace',
    'acesss': 'ace',
    'associateds': 'associate',
    'brookings': 'brook',
    'castings': 'cast',
    'coatings': 'coat',
    'furnishings': 'furnish',
    'givings': 'give',
    'holdings': 'hold',
    'manufacturings': 'manufacture',
    'pacings': 'pace',
    'reprocessings': 'reprocess',
    'stateds': 'state',
    'uniteds': 'unite',
}


def preprocess_text(text):
    """Tokenize, lemmatize (verb), remove stopwords, apply NLTK compat."""
    if not isinstance(text, str):
        return []
    tokens = _tokenizer.tokenize(text)
    lemmas = [_lemmatizer.lemmatize(token.lower(), pos='v') for token in tokens]
    keywords = [_NLTK_WORD_COMPAT.get(lemma, lemma)
                for lemma in lemmas if lemma not in _stop_words]
    return keywords


# Manual manufacturer->PERMNO corrections (restricted crosswalk).
#
# The crosswalk (hand-coded firm patterns + their CRSP PERMNOs / manual stock
# values) is a RESTRICTED, CRSP-derived artifact -- CRSP PERMNO is a proprietary
# WRDS identifier, so the real values are NOT shipped in the public deposit. They
# live in a confidential CSV alongside the other restricted inputs
# (data/raw/manual_permno_corrections.csv), shipped only in the restricted archive.
# gen_07 is a --skip-gen generation step, so the public route never runs it; only a
# restricted (real-data) run needs this file. The CSV mirrors the in-memory dicts
# exactly: `contains` is JSON (str or list[str]); a `permno`/`manual_stock` cell is
# non-empty ONLY where the dict had that key, so the `'permno' in corr` /
# `'manual_stock' in corr` guards below behave identically to the old inline table.
#
# Each reconstructed entry: dict with keys
#   'contains' : str or list[str] (AND) ; 'not_contains' : str (optional)
#   'permno' : float (optional)          ; 'stock_name' : str
#   'manual_stock' : float (optional)    ; 'no_guard'/'undo' : bool (optional)
# Order matters: earlier corrections take priority (manually_encoded guard); the
# first (medtronic) has no guard and overwrites unconditionally.
MANUAL_CORR_CSV = RAW / "manual_permno_corrections.csv"

_MANUAL_CORRECTIONS_CACHE = None


def _load_manual_corrections():
    """Load the restricted manufacturer->PERMNO crosswalk from the confidential CSV.

    Builds the list-of-dicts (including per-entry key presence) that the manual
    correspondence table defines. Raises with a clear message if the restricted file is absent --
    which only happens in the public route, where gen_07 is skipped.
    """
    if not MANUAL_CORR_CSV.exists():
        raise RuntimeError(
            f"Restricted crosswalk not found: {MANUAL_CORR_CSV}. gen_07 links MAUDE "
            "manufacturers to CRSP PERMNOs and needs the confidential manual-corrections "
            "crosswalk, which ships ONLY in the restricted archive (CRSP PERMNO is "
            "proprietary and withheld from the public deposit). This step is "
            "restricted-data-only; the public route skips it (--skip-gen)."
        )
    out = []
    with open(MANUAL_CORR_CSV, newline="") as fh:
        for row in csv.DictReader(fh):
            corr = {"contains": json.loads(row["contains"])}
            if row.get("not_contains"):
                corr["not_contains"] = row["not_contains"]
            if row.get("permno", "") != "":
                corr["permno"] = float(row["permno"])
            if row.get("stock_name"):
                corr["stock_name"] = row["stock_name"]
            if row.get("manual_stock", "") != "":
                corr["manual_stock"] = float(row["manual_stock"])
            if row.get("no_guard"):
                corr["no_guard"] = True
            if row.get("undo"):
                corr["undo"] = True
            out.append(corr)
    return out


def _get_manual_corrections():
    """Lazily load + cache the crosswalk, so importing this module never requires the
    restricted file -- only actually running gen_07 does."""
    global _MANUAL_CORRECTIONS_CACHE
    if _MANUAL_CORRECTIONS_CACHE is None:
        _MANUAL_CORRECTIONS_CACHE = _load_manual_corrections()
    return _MANUAL_CORRECTIONS_CACHE


def _apply_manual_corrections(df):
    """Apply the 70 manual permno/stock_name corrections.

    Corrections are applied in order. Each correction only modifies rows
    where manually_encoded != 1 (except correction #1 which is unconditional).
    """
    df['manually_encoded'] = 0
    df['manual_stock'] = 0.0

    for i, corr in enumerate(_get_manual_corrections()):
        # Build the match mask
        cn = df['clean_name']
        mask = cn.notnull()

        contains = corr['contains']
        if isinstance(contains, str):
            mask = mask & cn.str.contains(contains, na=False)
        else:
            for pattern in contains:
                mask = mask & cn.str.contains(pattern, na=False)

        if corr.get('not_contains'):
            mask = mask & ~cn.str.contains(corr['not_contains'], na=False)

        # Guard: skip rows already manually corrected (except #1)
        if not corr.get('no_guard', False):
            mask = mask & (df['manually_encoded'] != 1)

        n_matched = mask.sum()
        if n_matched == 0:
            continue

        if corr.get('undo', False):
            df.loc[mask, 'permno'] = np.nan
            df.loc[mask, 'stock_name'] = np.nan
            df.loc[mask, 'manually_encoded'] = 0
        else:
            if 'permno' in corr:
                df.loc[mask, 'permno'] = corr['permno']
                df.loc[mask, 'manually_encoded'] = 1
            if 'manual_stock' in corr:
                df.loc[mask, 'manual_stock'] = corr['manual_stock']
            df.loc[mask, 'stock_name'] = corr['stock_name']

    n_manual = (df['manually_encoded'] == 1).sum()
    print(f"    Manual corrections applied: {n_manual:,} rows affected")
    return df


# ---------------------------------------------------------------------------
# Rebuild of the MAUDE manufacturer list
# ---------------------------------------------------------------------------
# data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv is a two-column projection of the
# 23 public FDA MAUDE device files that ship under data/raw/MAUDE/device_data/. It is
# omitted from the public package for its size (306 MB); nothing in it is restricted,
# and certification/verify_maude_manufacturer_rebuild.py checks that this rebuild
# reproduces it byte for byte from those shipped files.
#
# ROW ORDER is load-bearing, not cosmetic. The deposited vintage was written in 2024 by a
# notebook that iterated os.listdir() without sorting, so its block order is that machine's
# directory order; and Phase 3 below takes drop_duplicates("MANUFACTURER_D_NAME"), which
# keeps the FIRST occurrence, so the order of the rows handed to pandas_dedupe depends on
# it. The order is therefore pinned in certification/MAUDE_MFR_SOURCE_ORDER.txt rather than
# normalised, and the rebuild verifies its own digest. Verified byte-identical 2026-10-19.
MFR_LIST_NAME = "All_Adverse_Event_Manufacturers.csv"
MFR_LIST_SHA256 = "8833a9a01599c145f84274cfabdf9d9d87ac8ddd897115d7a428ed28dd768f19"
MFR_LIST_ROWS = 9238809
MFR_SOURCE_ORDER_FILE = (Path(__file__).resolve().parents[2]
                         / "certification" / "MAUDE_MFR_SOURCE_ORDER.txt")


class _Sha256Sink:
    """Text sink so to_csv can be digested without a 306 MB temporary file."""

    def __init__(self):
        self._digest = hashlib.sha256()

    def write(self, chunk):
        if isinstance(chunk, str):
            chunk = chunk.encode("utf-8")
        self._digest.update(chunk)
        return len(chunk)

    def hexdigest(self):
        return self._digest.hexdigest()


def _rebuild_manufacturer_list():
    """Rebuild the MAUDE manufacturer list from the shipped raw device files.

    Fails closed: a rebuild that does not reproduce the deposited digest raises rather
    than feeding a differently ordered input into the order-sensitive dedupe below.
    """
    if SYNTHETIC_MODE:
        raise RuntimeError(
            f"refusing to rebuild {MFR_LIST_NAME} on the synthetic route -- the synthetic "
            "MAUDE linkage inputs are supplied by gen_00i, not by the real FDA device files"
        )
    print("    Rebuilding from device_data files (pinned source order)...")
    device_dir = MAUDE_DIR / "device_data"
    mfr_path = MAUDE_DIR / MFR_LIST_NAME

    if not MFR_SOURCE_ORDER_FILE.exists():
        raise FileNotFoundError(
            f"cannot rebuild {MFR_LIST_NAME}: source-order manifest missing at "
            f"{MFR_SOURCE_ORDER_FILE}"
        )
    order = [ln.strip() for ln in MFR_SOURCE_ORDER_FILE.read_text().splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")]

    absent = [f for f in order if not isfile(str(device_dir / f))]
    if absent:
        raise FileNotFoundError(
            f"cannot rebuild {MFR_LIST_NAME}: {len(absent)} source file(s) absent from "
            f"{device_dir}: {', '.join(absent[:5])}"
        )

    dfs = []
    for f in order:
        print(f"      {f}")
        dfs.append(pd.read_csv(str(device_dir / f), encoding='ISO-8859-1',
                               on_bad_lines='skip', sep="|",
                               usecols=['MDR_REPORT_KEY', 'MANUFACTURER_D_NAME']))
    df = pd.concat(dfs, ignore_index=True)[['MDR_REPORT_KEY', 'MANUFACTURER_D_NAME']]

    sink = _Sha256Sink()
    df.to_csv(sink, index=False, lineterminator="\n")
    got = sink.hexdigest()
    if len(df) != MFR_LIST_ROWS or got != MFR_LIST_SHA256:
        raise ValueError(
            f"rebuilt {MFR_LIST_NAME} does not match the deposited input.\n"
            f"  rows     expected {MFR_LIST_ROWS:,}, got {len(df):,}\n"
            f"  sha256   expected {MFR_LIST_SHA256}\n"
            f"           got      {got}\n"
            "The dedupe below is order-sensitive, so a rebuild that does not reproduce the "
            "digest must not be used. Check that the 23 source files match "
            "certification/PUBLIC_INPUT_HASHES.csv and that pandas is the pinned 2.3.3 "
            "(the parse drops malformed source lines)."
        )
    print(f"    Rebuild verified byte-identical to the deposited input "
          f"({len(df):,} rows, sha256 {got[:12]}...)")

    # Materialise the bytes and hand back a read of THEM, through the same pd.read_csv call
    # the input-present path uses. This is not redundancy: with the default low_memory=True,
    # pd.read_csv infers dtypes PER CHUNK, so a 23-file concat and a single read of the
    # assembled file give identical STRINGS but a different int/str object mix in
    # MDR_REPORT_KEY -- measured on the real data, 2,064,384 of 9,238,809 rows differ in
    # Python type, first diverging at row 786,432 (a chunk boundary). gen_07 later calls
    # drop_duplicates("MDR_REPORT_KEY"), which compares objects rather than strings, so
    # returning the concat directly collapses 422 more rows and all_adv_events_w_permno5.csv
    # stops matching the deposited file -- confirmed against a control run with the input present.
    # Re-reading the written bytes reproduces the deposited behaviour exactly.
    try:
        mfr_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(mfr_path, index=False, lineterminator="\n")
        source = mfr_path
        print(f"    Materialised {MFR_LIST_NAME} at {source}")
    except OSError as exc:
        source = Path(tempfile.gettempdir()) / MFR_LIST_NAME
        df.to_csv(source, index=False, lineterminator="\n")
        print(f"    {mfr_path.parent} is not writable ({exc.strerror}); "
              f"materialised at {source} instead")
    return pd.read_csv(str(source))


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def generate(out_path):
    """Generate adverse-event-to-PERMNO linkage."""

    dedup_config = _safe_config_name(DEDUP_SETTINGS_DIR, "dedupe_dataframe")
    link_config = _safe_config_name(LINK_SETTINGS_DIR, "link_dataframes")

    # ------------------------------------------------------------------
    # Phase 1: Load raw manufacturer data
    # ------------------------------------------------------------------
    print("  Phase 1: Loading MAUDE manufacturer data...")
    mfr_path = MAUDE_DIR / "All_Adverse_Event_Manufacturers.csv"
    if not mfr_path.exists():
        df_combined = _rebuild_manufacturer_list()
    else:
        df_combined = pd.read_csv(str(mfr_path))

    print(f"    Loaded {len(df_combined):,} raw records")

    # ------------------------------------------------------------------
    # Phase 2: Load PERMNO universe
    # ------------------------------------------------------------------
    print("  Phase 2: Loading PERMNO universe...")
    permnos = pd.read_csv(str(MAUDE_DIR / "all_permnos_fname_adverse_events_oct22_24.csv"))
    print(f"    {len(permnos):,} firm-permno pairs")

    # ------------------------------------------------------------------
    # Phase 3: Text preprocessing
    # ------------------------------------------------------------------
    print("  Phase 3: Text preprocessing...")
    df_notnull = df_combined[df_combined.MANUFACTURER_D_NAME.notnull()].copy()
    df_notnull['group'] = df_notnull.MANUFACTURER_D_NAME.astype('category').cat.codes
    df_dropped = df_notnull.drop_duplicates("MANUFACTURER_D_NAME").copy()
    print(f"    Unique manufacturer names: {len(df_dropped):,}")

    df_dropped['clean_name'] = (df_dropped['MANUFACTURER_D_NAME']
                                .apply(preprocess_text).str.join(" "))
    df_dropped['clean_name_group'] = df_dropped.clean_name.astype('category').cat.codes
    df_dropped_clean = df_dropped.drop_duplicates("clean_name_group").copy()
    print(f"    Unique clean names for dedupe: {len(df_dropped_clean):,}")

    # ------------------------------------------------------------------
    # Phase 4: Deduplicate manufacturers
    # ------------------------------------------------------------------
    print("  Phase 4: Deduplicating manufacturers (pandas_dedupe)...")
    print(f"    Using settings: {dedup_config}_learned_settings")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        deduped = pandas_dedupe.dedupe_dataframe(
            df_dropped_clean, ['clean_name'],
            config_name=dedup_config,
        )

    n_clusters = deduped['cluster id'].nunique()
    print(f"    {len(deduped):,} rows, {n_clusters:,} manufacturer clusters")

    # Save intermediate deduped file for comparison/transparency
    deduped_out = out_path.parent / "All_Adverse_Event_Manufacturers_Deduped.csv"
    deduped.to_csv(deduped_out, index=False)
    print(f"    Saved intermediate: {deduped_out.name}")

    # ------------------------------------------------------------------
    # Phase 5: Merge clusters back to all rows
    # ------------------------------------------------------------------
    print("  Phase 5: Merging clusters back to all rows...")
    # Merge cluster IDs from deduped → deduplicated names
    df_dropped['clean_name_group'] = df_dropped['clean_name_group'].astype(int)
    deduped['clean_name_group'] = deduped['clean_name_group'].astype(int)
    df_dropped_w_deduped = pd.merge(
        df_dropped,
        deduped[['clean_name_group', 'cluster id', 'confidence']],
        on='clean_name_group', how='left')

    # Merge back to ALL rows (including duplicated MDR_REPORT_KEYs)
    df_all = pd.merge(
        df_notnull,
        df_dropped_w_deduped[['group', 'clean_name', 'clean_name_group',
                               'cluster id', 'confidence']],
        on='group', how='left')

    # Find most common clean_name per cluster
    clusters = (df_all.groupby('cluster id')['clean_name']
                .agg(lambda x: x.value_counts().index[0]).reset_index())
    clusters.columns = ['cluster id', 'most common']
    df_all = pd.merge(df_all, clusters, on='cluster id', how='left')
    df_all['cluster id'] = pd.to_numeric(df_all['cluster id'], errors='coerce').astype('Int64')

    # One row per cluster for linking
    df_one_per_cluster = df_all.drop_duplicates('cluster id').copy()
    print(f"    {len(df_all):,} total rows, "
          f"{len(df_one_per_cluster):,} unique clusters for linking")

    # ------------------------------------------------------------------
    # Phase 6: Link to PERMNO universe
    # ------------------------------------------------------------------
    print("  Phase 6: Linking manufacturer clusters to PERMNOs...")
    # Preprocess permno firm names the same way
    permnos['clean_name'] = (permnos['firm_name']
                             .apply(preprocess_text).str.join(" "))
    permnos['most common'] = permnos['clean_name']

    print(f"    Using settings: {link_config}_learned_settings")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        merged_master = pandas_dedupe.link_dataframes(
            df_one_per_cluster,
            permnos[['permno', 'most common']],
            ['most common'],
            config_name=link_config,
        )
    print(f"    Link output: {len(merged_master):,} rows")

    # ------------------------------------------------------------------
    # Phase 7: Post-link merge
    # ------------------------------------------------------------------
    print("  Phase 7: Post-link merge logic...")
    # Combine cluster IDs from within-dedupe and cross-link
    merged_master['cluster_id_combined'] = merged_master.get('cluster id_y',
                                                              pd.Series(dtype=float))
    if 'cluster id' in merged_master.columns:
        merged_master.loc[merged_master['cluster_id_combined'].isna(),
                          'cluster_id_combined'] = merged_master['cluster id']

    merged_notnull = merged_master[merged_master.cluster_id_combined.notnull()].copy()

    # Propagate permno within linked clusters
    def extract_match(grp):
        permno_rows = grp[grp.permno.notnull()]
        if len(permno_rows) > 0:
            grp['permno'] = permno_rows['permno'].values[0]
            grp['stock_name'] = permno_rows['most common'].values[0]
        return grp

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        merged_notnull = merged_notnull.groupby(
            'cluster_id_combined', group_keys=False).apply(extract_match)

    # Keep only adverse-event rows that got a permno match
    # cluster id_x = from the left (adverse events) dataframe
    cid_left = 'cluster id_x' if 'cluster id_x' in merged_notnull.columns else 'cluster id'
    merged_matchonly = merged_notnull[
        (merged_notnull[cid_left].notnull()) &
        (merged_notnull.permno.notnull())
    ].copy()

    # Get all adverse-event rows
    merged_all = merged_master[merged_master[cid_left].notnull()].copy()
    if 'cluster_id_combined' in merged_all.columns:
        merged_all = merged_all.drop(columns=['cluster_id_combined'], errors='ignore')
    if 'permno' in merged_all.columns:
        merged_all = merged_all.drop(columns=['permno'], errors='ignore')

    # Left-join permno/stock_name from matched rows
    merged_all = pd.merge(
        merged_all,
        merged_matchonly[[cid_left, 'permno', 'stock_name']].drop_duplicates(cid_left),
        on=cid_left, how='left')

    # Propagate to the full dataset via 'cluster id' from phase 5
    keep_cols = merged_all[[cid_left, 'permno', 'stock_name']].drop_duplicates(cid_left)
    keep_cols.columns = ['cluster id', 'permno', 'stock_name']
    keep_cols['cluster id'] = pd.to_numeric(keep_cols['cluster id'], errors='coerce').astype('Int64')
    result = pd.merge(df_all, keep_cols, on='cluster id', how='left')

    n_matched = result['permno'].notnull().sum()
    print(f"    PERMNO matched: {n_matched:,} / {len(result):,} "
          f"({n_matched/len(result)*100:.1f}%)")

    # ------------------------------------------------------------------
    # Phase 8: Manual corrections
    # ------------------------------------------------------------------
    print("  Phase 8: Applying manual corrections...")
    result = _apply_manual_corrections(result)

    # ------------------------------------------------------------------
    # Phase 9: Save output
    # ------------------------------------------------------------------
    print("  Phase 9: Saving output...")
    result = result.drop_duplicates("MDR_REPORT_KEY")

    output = result[['MDR_REPORT_KEY', 'clean_name', 'permno', 'stock_name',
                      'manually_encoded', 'manual_stock']].copy()
    output.to_csv(out_path, index=False)

    n_with_permno = output['permno'].notnull().sum()
    n_manual = (output['manually_encoded'] == 1).sum()
    n_manual_stock = (output['manual_stock'] > 0).sum()
    print(f"\n  Output: {out_path.name}")
    print(f"    Rows: {len(output):,}")
    print(f"    With PERMNO: {n_with_permno:,} ({n_with_permno/len(output)*100:.1f}%)")
    print(f"    Manually corrected: {n_manual:,}")
    print(f"    Manual stock (non-CRSP): {n_manual_stock:,}")

    return output


def run(staging=False):
    if staging:
        out_dir = DERIVED / "_generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "all_adv_events_w_permno5.csv"
        print(f"STAGING MODE: writing to {out_dir}")
    else:
        out_path = OUTPUT_FILE
    if SYNTHETIC_MODE:
        _generate_synthetic(out_path)
    else:
        generate(out_path)

    # The manuscript's firm-size sentence (tex:305) quotes the top-300 report-count
    # ranking, the share of reports it covers and how many of those names are private.
    # Emit that coverage from the file just written, so step 35 can check the sentence
    # against a shipped artifact instead of against nothing.
    if not staging:
        print("\n  Manufacturer -> CRSP linkage coverage (output/tables/):")
        write_coverage(ROOT_DIR, events_path=out_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", action="store_true",
                        help="Write to _generated/ instead of overwriting main file")
    parser.add_argument("--rebuild-manufacturer-list", action="store_true",
                        help=("Rebuild data/raw/MAUDE/All_Adverse_Event_Manufacturers.csv from "
                              "the shipped device_data files, verify its digest, write it and "
                              "exit. Use when that 306 MB input was omitted for size."))
    parser.add_argument("--out", default=None,
                        help="With --rebuild-manufacturer-list, write here instead of data/raw/MAUDE/")
    args = parser.parse_args()
    print("=== gen_07_adverse_permno.py ===")
    if args.rebuild_manufacturer_list:
        _df = _rebuild_manufacturer_list()
        _dest = Path(args.out) if args.out else MAUDE_DIR / MFR_LIST_NAME
        _dest.parent.mkdir(parents=True, exist_ok=True)
        _df.to_csv(_dest, index=False, lineterminator="\n")
        print(f"  wrote {_dest} ({_dest.stat().st_size:,} B)")
    else:
        run(staging=args.staging)
    print("gen_07_adverse_permno.py complete.")
