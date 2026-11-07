#!/usr/bin/env python3
"""build_simulation.py -- THE dedicated simulation script (JPE confidential-data Step 2/3/6).

Regenerates the entire publishable `synthetic_pipeline/simulated_data/` tree from the shipped,
reviewed committed parameters -- WITHOUT reading any real/restricted data. This is the
script the Data Editor can inspect and re-run to reproduce the simulated inputs (confidential.html:
"Include the simulation script ... so the Data Editor can inspect it and, if needed, re-generate the
simulated data").

WHAT IT NEEDS (all shipped; privacy and rights are certified separately before final promotion):
  synthetic_pipeline/_synthetic_source_internal/simulation_parameters.json  (rounded/smoothed params;
      passes gen_00a.disclosure_review -- rounded cardinalities, smoothed size families, public codes)
  synthetic_pipeline/_synthetic_source_internal/pc_effects.parquet          (theta: synthetic random
      effects drawn from FIXED distributions + the PUBLIC product-code / Federal-Register design)
  synthetic_pipeline/_synthetic_source_internal/public_master_skeleton.parquet (Full_sample PUBLIC cols)

WHAT IT RUNS (Stage B only; Stage A is author-side and is NOT re-run here -- its committed outputs
ship only after the privacy and publication-rights gates pass):
  gen_00c  synthetic MarketScan claims + GPT price-link crosswalks
  gen_00d  synthetic WRDS/CRSP dimensions (firm universe, adverse-event->permno, compustat, Full_sample)
  gen_00e  synthetic patents (fresh patnum/permno/PC, KPSS values)
  gen_00f  synthetic Nexis liability corpus
  gen_00i  synthetic raw MAUDE manufacturer + firm-universe linkage inputs
  gen_00g  de-identify patents + generate synthetic KPSS/KPST + PUBLISH every synthetic_* cache into
           simulated_data/ (the assembler)
  gen_00h  synthetic patent title/abstract text

DETERMINISM: every generator seeds from the committed PUBLIC seed -- 20260803, the `PUBLIC_SEED`
constant defined at the top of this script -- via independent_universe.iu_rng, with PYTHONHASHSEED=0.
Two independent runs on the same shipped params produce byte-identical simulated_data.

USAGE (from the package root). --output-dir is effectively required and MUST name a new directory
OUTSIDE the package tree, so generation can never mutate the deposited reference payload:
    PYTHONHASHSEED=0 python3 synthetic_pipeline/build_simulation.py --output-dir /path/outside/pkg
then feed the result to the pipeline with
    python3 synthetic_pipeline/materialize_simulation.py --source-dir /path/outside/pkg --for-gen-run
    # The official analysis route is certification/certify_fromraw_route.sh.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # package root
GEN = os.path.join(HERE, "generators")

# ---------------------------------------------------------------------------------------
# THE PUBLIC SIMULATION SEED (JPE confidential-data Step 3: "set the seed at the top of the
# simulation script"). This is the single integer every generator's entropy derives from:
# generators/independent_universe.py turns it into one numpy Generator per (file, column) tag
# via iu_rng(). It is stated here so a reader of THIS script sees it without opening a helper
# module, and it is cross-checked against the module that actually uses it (below) so the two
# can never drift. Changing it changes every simulated value and nothing else.
# ---------------------------------------------------------------------------------------
PUBLIC_SEED = 20260803
# Optional public perturbation control (generators/synthetic_seed.py). Leave unset for the
# deposited payload; the certification harness sets it to prove the outputs move with the seed.
SEED_OFFSET_ENV = "FDA_SYNTHETIC_SEED_OFFSET"
INTERNAL = os.path.join(HERE, "_synthetic_source_internal")
SIM = os.path.join(HERE, "simulated_data")

# committed Stage-A artifacts the Stage-B generators consume
REQUIRED_COMMITTED = [
    os.path.join(INTERNAL, "simulation_parameters.json"),
    os.path.join(INTERNAL, "pc_effects.parquet"),
    os.path.join(INTERNAL, "public_master_skeleton.parquet"),
    os.path.join(INTERNAL, "simulation_schema_contract.json"),
]

# Stage B, in dependency order. gen_00g is the assembler (publishes caches -> simulated_data);
# gen_00h runs last (reads the already-synthetic patent ids).
STAGE_B = [
    "gen_00c_synthetic_marketscan.py",
    "gen_00d_synthetic_dimensions_wrds.py",
    "gen_00e_synthetic_patents.py",
    "gen_00f_synthetic_nexis.py",
    "gen_00i_synthetic_maude_linkage_inputs.py",
    "gen_00g_deidentify_patents.py",
    "gen_00h_synthetic_patent_text.py",
]


def _fail(msg):
    sys.stderr.write("build_simulation: FATAL: %s\n" % msg)
    raise SystemExit(1)


INVENTORY = os.path.join(
    ROOT, "certification", "regen_determinism", "simulated_data_expected_files.txt"
)
PERMITTED_EXTENSIONS = {".csv", ".parquet", ".xlsx"}


def _expected_inventory():
    if not os.path.isfile(INVENTORY):
        _fail(f"fixed simulated-data inventory is missing: {INVENTORY}")
    expected = set()
    for raw in open(INVENTORY):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        prefix = "simulated_data/"
        if not line.startswith(prefix):
            _fail(f"invalid inventory entry (must start {prefix!r}): {line}")
        rel = line[len(prefix):]
        path = Path(rel)
        if path.is_absolute() or ".." in path.parts or path.suffix.lower() not in PERMITTED_EXTENSIONS:
            _fail(f"unsafe or unsupported inventory entry: {line}")
        if rel in expected:
            _fail(f"duplicate inventory entry: {line}")
        expected.add(rel)
    if not expected:
        _fail("fixed simulated-data inventory is empty")
    return expected


def _validate_generated(sim_dir, expected):
    actual = set()
    for dp, dirs, files in os.walk(sim_dir, followlinks=False):
        for name in dirs + files:
            path = os.path.join(dp, name)
            if os.path.islink(path):
                _fail(f"generated simulation contains a symlink: {path}")
        for name in files:
            path = os.path.join(dp, name)
            rel = os.path.relpath(path, sim_dir).replace(os.sep, "/")
            if Path(name).suffix.lower() not in PERMITTED_EXTENSIONS:
                _fail(f"generated simulation contains an unsupported file: {rel}")
            if not os.path.isfile(path) or not os.access(path, os.R_OK):
                _fail(f"generated simulation contains an unreadable file: {rel}")
            actual.add(rel)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        _fail(f"generated file inventory mismatch; missing={missing}, extra={extra}")
    return len(actual)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default=os.path.join(HERE, "simulated_data-regenerated"),
        help="new directory to receive the regenerated payload (must not already exist)",
    )
    args = parser.parse_args()

    # The official clean-room harness shadows both deposited reference trees
    # with empty read-only mounts. Assert that boundary positively so the two
    # determinism runs cannot pass by copying the shipped simulation or outputs.
    if os.environ.get("FDA_SIM_REFERENCE_DENIED") == "1":
        for forbidden in (SIM, os.path.join(ROOT, "output-simulated")):
            if not os.path.isdir(forbidden):
                _fail(f"reference-denial mount is missing: {forbidden}")
            if any(os.scandir(forbidden)):
                _fail(f"deposited reference bytes are visible to Stage-B generation: {forbidden}")

    target = os.path.abspath(args.output_dir)
    if os.path.lexists(target):
        _fail(f"refusing to overwrite an existing output path: {target}")
    package_real = os.path.realpath(ROOT)
    target_real = os.path.realpath(target)
    if os.path.commonpath([target_real, package_real]) == package_real:
        _fail("--output-dir must be outside the package tree so generation cannot mutate the "
              "deposited reference payload.\n"
              "  You gave: %s\n"
              "  Use, for example:\n"
              "    PYTHONHASHSEED=0 python3 synthetic_pipeline/build_simulation.py "
              "--output-dir /path/outside/the/package\n"
              "  and then consume it with:\n"
              "    python3 synthetic_pipeline/materialize_simulation.py "
              "--source-dir /path/outside/the/package --for-gen-run" % target)
    target_parent = os.path.dirname(target)
    if not os.path.isdir(target_parent) or os.path.islink(target_parent):
        _fail(f"output parent must be an existing real directory: {target_parent}")

    # 0. Stage-A committed artifacts must be present (they ship; Stage A is not re-run here).
    missing = [p for p in REQUIRED_COMMITTED if not os.path.exists(p)]
    if missing:
        _fail("missing committed Stage-A artifact(s) -- the simulation cannot run without the shipped "
              "committed parameters:\n  " + "\n  ".join(missing) +
              "\n(These are produced author-side by gen_00a/gen_00b in the authorized environment and "
              "ship pre-built; a public/Data-Editor run consumes them, it does not re-extract them.)")

    # 1. Fail-closed disclosure review of the committed params before generating anything.
    sys.path.insert(0, GEN)
    # Echo the public seed and prove the constant at the top of this script is the one the
    # generators actually use (fail closed if they ever diverge).
    import independent_universe as _iu                                        # noqa: E402
    _offset = os.environ.get(SEED_OFFSET_ENV, "0")
    if _iu.PUBLIC_SEED != PUBLIC_SEED + int(_offset):
        _fail(f"public seed mismatch: build_simulation.PUBLIC_SEED={PUBLIC_SEED} "
              f"(+{SEED_OFFSET_ENV}={_offset}) but independent_universe.PUBLIC_SEED="
              f"{_iu.PUBLIC_SEED}")
    print("build_simulation: public simulation seed = %d (%s=%s); PYTHONHASHSEED=0."
          % (PUBLIC_SEED, SEED_OFFSET_ENV, _offset))
    try:
        import json
        import gen_00a_extract_parameters as g00a
        params = json.load(open(REQUIRED_COMMITTED[0]))
        g00a.disclosure_review(params)          # raises SystemExit on any un-rounded/raw statistic
        print("build_simulation: committed params passed disclosure_review "
              "(%d entities, %d file specs)." % (len(params.get("entities", {})), len(params.get("files", {}))))
    except SystemExit:
        raise
    except Exception as e:                       # pragma: no cover
        _fail("could not disclosure-review the committed params: %s" % e)

    expected = _expected_inventory()
    scratch = tempfile.mkdtemp(prefix=".simulation-build-", dir=target_parent)
    stage_internal = os.path.join(scratch, "internal")
    stage_sim = os.path.join(scratch, "simulated_data")
    os.makedirs(stage_internal)
    try:
        # Copy only the four committed inputs. No old generated cache or
        # simulated payload enters the clean-room build.
        for src in REQUIRED_COMMITTED:
            shutil.copy2(src, os.path.join(stage_internal, os.path.basename(src)))

        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "0"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = GEN + os.pathsep + env.get("PYTHONPATH", "")
        env["FDA_SYNTHETIC_INTERNAL"] = stage_internal
        env["FDA_SIMULATED_DATA_OUT"] = stage_sim
        for script in STAGE_B:
            path = os.path.join(GEN, script)
            if not os.path.exists(path):
                _fail("Stage-B generator not found: %s" % path)
            print("\n=== build_simulation: running %s ===" % script, flush=True)
            rc = subprocess.run([sys.executable, path], cwd=ROOT, env=env).returncode
            if rc != 0:
                _fail("%s exited %d -- simulation build aborted (see its output above)." % (script, rc))

        n = _validate_generated(stage_sim, expected)
        os.replace(stage_sim, target)
        print("\nbuild_simulation: DONE. clean-room payload assembled with %d files at %s" % (n, target))
        print("The output was generated from an empty staging tree and promoted only after the fixed "
              "inventory passed. Use materialize_simulation.py --source-dir <that directory> in a "
              "throwaway package extraction.")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
