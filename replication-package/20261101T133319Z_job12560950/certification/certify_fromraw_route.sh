#!/bin/bash
# Official JPE Option-2 outer harness. Host-side code retains the reference;
# analysis runs in an offline Apptainer namespace that is never given the ZIP
# or output-simulated reference.
set -euo pipefail

ZIP=""; ZIP_SHA=""; IMAGE=""; IMAGE_SHA=""; WORKDIR=""
# The certified image is self-contained: it carries ONE Python (3.9.13 at /usr/local/bin/python3,
# numpy 1.26.4, torch 2.2.2 CPU) and every step -- including step 17, the safety-embedding step --
# runs under it. --embed-python-container therefore defaults to `python3`, which is resolved on the
# PATH INSIDE the container, and no host interpreter is bound in. Override it only to point at a
# different interpreter that exists inside the image.
EMBED_PY="python3"
APPTAINER="${APPTAINER:-apptainer}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --zip) ZIP="$2"; shift 2 ;;
    --zip-sha256) ZIP_SHA="$2"; shift 2 ;;
    --image) IMAGE="$2"; shift 2 ;;
    --image-sha256) IMAGE_SHA="$2"; shift 2 ;;
    --workdir) WORKDIR="$2"; shift 2 ;;
    --embed-python-container) EMBED_PY="$2"; shift 2 ;;
    --apptainer) APPTAINER="$2"; shift 2 ;;
    *) echo "ABORT: unknown arg $1" >&2; exit 2 ;;
  esac
done
[[ -n "$ZIP" && -n "$ZIP_SHA" && -n "$IMAGE" && -n "$IMAGE_SHA" && -n "$WORKDIR" ]] || {
  echo "ABORT: ZIP/SHA, image/SHA and an empty workdir are required" >&2
  echo "       (--embed-python-container is OPTIONAL and defaults to the image's own python3)" >&2
  exit 2
}
abort() { echo "CERT ABORT (from-raw): $*" >&2; exit 1; }
log() { echo "[certify-fromraw] $*"; }
# Syntactic validation of the embed interpreter, on the host, before anything expensive runs. The
# value names a program INSIDE the container, so the host filesystem is the wrong place to test it:
# a bare command name is resolved on the container's PATH, and a path must be absolute inside the
# container. Existence/executability is checked in the container itself, once the image hash is
# verified (see "resolve the embedding interpreter inside the image" below).
[[ -n "$EMBED_PY" ]] || abort "--embed-python-container was given an empty value"
case "$EMBED_PY" in
  */*) [[ "$EMBED_PY" == /* ]] || abort "--embed-python-container must be a bare command name \
resolved on the container PATH (e.g. python3) or an ABSOLUTE path inside the container; got: $EMBED_PY" ;;
esac
[[ "$ZIP_SHA" =~ ^[0-9a-f]{64}$ && "$IMAGE_SHA" =~ ^[0-9a-f]{64}$ ]] || abort "hash format invalid"
[[ -f "$ZIP" && -f "$IMAGE" ]] || abort "package ZIP or image missing"
[[ -d "$WORKDIR" && -z "$(ls -A "$WORKDIR" 2>/dev/null)" ]] || abort "workdir must be empty"
WORKDIR="$(cd "$WORKDIR" && pwd -P)"
ZIP="$(cd "$(dirname "$ZIP")" && pwd -P)/$(basename "$ZIP")"
IMAGE="$(cd "$(dirname "$IMAGE")" && pwd -P)/$(basename "$IMAGE")"
command -v "$APPTAINER" >/dev/null || abort "Apptainer executable not found"

# Apptainer reads these launcher variables before --cleanenv applies inside the
# container. Remove every user-controlled implicit bind/environment injection;
# the explicit bind list below is the complete allowed interface.
unset APPTAINER_BIND APPTAINER_BINDPATH SINGULARITY_BIND SINGULARITY_BINDPATH
while IFS='=' read -r name _; do
  case "$name" in
    APPTAINERENV_*|SINGULARITYENV_*) unset "$name" ;;
  esac
done < <(env)

EVID="$WORKDIR/FROMRAW_EVIDENCE"; mkdir -p "$EVID"
GOT_ZIP="$(sha256sum "$ZIP" | awk '{print $1}')"
GOT_IMAGE="$(sha256sum "$IMAGE" | awk '{print $1}')"
{
  echo "zip_sha_expected=$ZIP_SHA"; echo "zip_sha_got=$GOT_ZIP"
  echo "image_sha_expected=$IMAGE_SHA"; echo "image_sha_got=$GOT_IMAGE"
  "$APPTAINER" version
} > "$EVID/00_identity_environment.txt"
[[ "$GOT_ZIP" == "$ZIP_SHA" && "$GOT_IMAGE" == "$IMAGE_SHA" ]] || abort "ZIP or image hash mismatch"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
python3 "$SCRIPT_DIR/verify_candidate_zip.py" --zip "$ZIP" --sha256 "$ZIP_SHA" \
  > "$EVID/00_zip_validation.txt" 2>&1 || abort "package ZIP validation failed"
EXTRACT="$WORKDIR/extract"; mkdir -p "$EXTRACT"
unzip -q "$ZIP" -d "$EXTRACT" || abort "unzip failed"
ARCHIVE="$(dirname "$(find "$EXTRACT" -maxdepth 2 -name run_all.py -type f | head -1)")"
[[ -f "$ARCHIVE/run_all.py" ]] || abort "unique package root not found"
python3 "$ARCHIVE/certification/verify_candidate_zip.py" --zip "$ZIP" --sha256 "$ZIP_SHA" \
  > "$EVID/01_extracted_verifier.txt" 2>&1 || abort "the package's own ZIP verifier failed"
python3 "$ARCHIVE/certification/verify_immutable_tree.py" --root "$ARCHIVE" \
  --manifest "$EVID/02_immutable_members.json" --write \
  > "$EVID/02_immutable_before.txt" 2>&1 || abort "immutable-member bind failed"

# Manuscript dependency closure, checked on the PRISTINE extraction (2026-10-13). This has to happen
# BEFORE the run: the run overwrites output/ with simulated exhibits, and the committed closure pins
# the real-data exhibits the manuscript shows, so after the run there is nothing meaningful to
# compare against. Previously the only closure step ran AFTER the run, in WRITE mode, which re-pinned
# the manifest to the exhibits the run had just produced -- and did so after
# verify_immutable_tree --verify had already passed, so the rewrite of that certification member went
# unnoticed. --verify compares and never writes.
[[ -f "$ARCHIVE/certification/hash_manuscript_closure.py" ]] \
  || abort "certification/hash_manuscript_closure.py missing from the archive -- the manuscript closure cannot be checked"
python3 "$ARCHIVE/certification/hash_manuscript_closure.py" --verify --root "$ARCHIVE" \
  > "$EVID/02b_manuscript_closure_verify.log" 2>&1 \
  || abort "the committed manuscript closure is incomplete or drifted from MANUSCRIPT_CLOSURE.sha256 -- see 02b_manuscript_closure_verify.log"
cp "$ARCHIVE/certification/MANUSCRIPT_CLOSURE.sha256" "$EVID/02b_manuscript_closure.sha256" \
  || abort "could not retain the committed closure manifest as evidence"

# Bind only explicit directories. The package ZIP is never bound into a
# container. Dedicated home/tmp/cache paths contain no host credentials.
ISO_HOME="$WORKDIR/isolated-home"; ISO_TMP="$WORKDIR/isolated-tmp"; ISO_CACHE="$WORKDIR/isolated-cache"
GENROOT="$WORKDIR/generation"
GEN_EMPTY_SIM="$WORKDIR/generator-empty-simulated-data"
GEN_EMPTY_OUTPUT="$WORKDIR/generator-empty-output-reference"
mkdir -p "$ISO_HOME" "$ISO_TMP" "$ISO_CACHE" "$GENROOT" "$GEN_EMPTY_SIM" "$GEN_EMPTY_OUTPUT"
BASE=(exec --cleanenv --containall --net --network none --no-mount home,cwd,hostfs,bind-paths)
ENVARGS=(--env "HOME=/cert-home,XDG_CACHE_HOME=/cert-cache,TMPDIR=/cert-tmp,PYTHONHASHSEED=0,PYTHONDONTWRITEBYTECODE=1")
cd "$ISO_HOME"

# Resolve the embedding interpreter INSIDE the image (the only place it exists) and record what it
# resolved to, so the evidence says which interpreter ran the safety-embedding step. No host
# interpreter is bound into the analysis container.
log "resolve the embedding interpreter inside the image: $EMBED_PY"
EMBED_RESOLVED="$("$APPTAINER" "${BASE[@]}" \
  --bind "$ISO_HOME:/cert-home:rw" --bind "$ISO_TMP:/cert-tmp:rw" --bind "$ISO_CACHE:/cert-cache:rw" \
  "${ENVARGS[@]}" "$IMAGE" bash -c 'command -v "$1"' _ "$EMBED_PY" 2>/dev/null || true)"
[[ -n "$EMBED_RESOLVED" ]] || abort "embedding interpreter not found inside the image: $EMBED_PY"
EMBED_NUMPY="$("$APPTAINER" "${BASE[@]}" \
  --bind "$ISO_HOME:/cert-home:rw" --bind "$ISO_TMP:/cert-tmp:rw" --bind "$ISO_CACHE:/cert-cache:rw" \
  "${ENVARGS[@]}" "$IMAGE" "$EMBED_RESOLVED" -c 'import numpy, sys; print(numpy.__version__, sys.version.split()[0])' 2>/dev/null || true)"
[[ -n "$EMBED_NUMPY" ]] || abort "embedding interpreter cannot import numpy inside the image: $EMBED_RESOLVED"
{
  echo "embed_python_requested=$EMBED_PY"
  echo "embed_python_resolved_in_image=$EMBED_RESOLVED"
  echo "embed_numpy_and_python_version=$EMBED_NUMPY"
} > "$EVID/00_embed_interpreter.txt"
log "embedding interpreter: $EMBED_RESOLVED (numpy/python: $EMBED_NUMPY)"

log "generate the standalone simulation twice in network-denied containers"
for run in run1 run2; do
  "$APPTAINER" "${BASE[@]}" \
    --bind "$ARCHIVE:/package:ro" --bind "$GENROOT:/generation:rw" \
    --bind "$GEN_EMPTY_SIM:/package/synthetic_pipeline/simulated_data:ro" \
    --bind "$GEN_EMPTY_OUTPUT:/package/output-simulated:ro" \
    --bind "$ISO_HOME:/cert-home:rw" --bind "$ISO_TMP:/cert-tmp:rw" --bind "$ISO_CACHE:/cert-cache:rw" \
    "${ENVARGS[@]}" --env "FDA_SIM_REFERENCE_DENIED=1" \
    "$IMAGE" python3 /package/synthetic_pipeline/build_simulation.py \
      --output-dir "/generation/$run" > "$EVID/03_generation_${run}.log" 2>&1 \
    || abort "simulation generation $run failed"
done
python3 "$ARCHIVE/certification/compare_simulated_payloads.py" \
  --shipped "$ARCHIVE/synthetic_pipeline/simulated_data" \
  --generation-one "$GENROOT/run1" --generation-two "$GENROOT/run2" \
  --expected "$ARCHIVE/certification/regen_determinism/simulated_data_expected_files.txt" \
  > "$EVID/03_simulation_identity.txt" 2>&1 || abort "simulator identity failed"

# Defense in depth: the materialize + preflight containers run CANDIDATE code and had the
# reference output-simulated/ visible (unlike the generation step, which overlays it empty). They do not
# need the reference, so overlay it empty here too (defense-in-depth; the reference is still moved fully
# out before the analysis run below). GEN_EMPTY_OUTPUT is the empty dir defined above.
log "materialize generated inputs in an isolated container (reference overlaid empty)"
"$APPTAINER" "${BASE[@]}" \
  --bind "$ARCHIVE:/package:rw" --bind "$GENROOT/run1:/generated:ro" \
  --bind "$GEN_EMPTY_OUTPUT:/package/output-simulated:ro" \
  --bind "$ISO_HOME:/cert-home:rw" --bind "$ISO_TMP:/cert-tmp:rw" --bind "$ISO_CACHE:/cert-cache:rw" \
  "${ENVARGS[@]}" "$IMAGE" python3 /package/synthetic_pipeline/materialize_simulation.py \
    --source-dir /generated --for-gen-run > "$EVID/03_materialize.log" 2>&1 \
  || abort "materialization failed"
"$APPTAINER" "${BASE[@]}" --bind "$ARCHIVE:/package:rw" \
  --bind "$GEN_EMPTY_OUTPUT:/package/output-simulated:ro" \
  --bind "$ISO_HOME:/cert-home:rw" --bind "$ISO_TMP:/cert-tmp:rw" --bind "$ISO_CACHE:/cert-cache:rw" \
  "${ENVARGS[@]}" "$IMAGE" python3 /package/synthetic_pipeline/preflight_from_raw.py \
  > "$EVID/03_preflight.log" 2>&1 || abort "from-raw preflight failed"

# Delete output/figures and output/tables BEFORE the run so the regeneration is provably from empty.
# Done here on the host, by the outer harness itself (not merely delegated into the analysis
# container), so a silent no-op inside the container cannot hide a stale/reused exhibit.
log "deleting output/figures and output/tables so regeneration starts from empty"
mkdir -p "$ARCHIVE/output/figures" "$ARCHIVE/output/tables"
N_DEL_BEFORE=0
for sub in output/figures output/tables; do
  c=$(find "$ARCHIVE/$sub" -type f 2>/dev/null | wc -l | tr -d ' ')
  N_DEL_BEFORE=$((N_DEL_BEFORE + c))
done
find "$ARCHIVE/output/figures" "$ARCHIVE/output/tables" -type f -delete
N_DEL_REMAIN=0
for sub in output/figures output/tables; do
  c=$(find "$ARCHIVE/$sub" -type f 2>/dev/null | wc -l | tr -d ' ')
  N_DEL_REMAIN=$((N_DEL_REMAIN + c))
done
echo "before=$N_DEL_BEFORE remaining_after_delete=$N_DEL_REMAIN" > "$EVID/03b_output_deletion.txt"
[[ "$N_DEL_REMAIN" == "0" ]] || abort "exhibit outputs remain after deletion ($N_DEL_REMAIN)."

# Reference remains on the host and is not among the analysis-container binds.
REFERENCE="$WORKDIR/reference-output"
[[ -d "$ARCHIVE/output-simulated" ]] || abort "output-simulated missing"
mv "$ARCHIVE/output-simulated" "$REFERENCE"
# The pinned embedding interpreter is BAKED INTO the image (the single numpy 1.26.4 Python the
# image installs; see docker/Dockerfile and certification/SIF_PROVENANCE.json). It was resolved and
# recorded above, inside the container, so nothing from the host is bound in for it: the bind list
# below remains the package tree, the evidence directory and the isolated home/tmp/cache.
set +e
"$APPTAINER" "${BASE[@]}" \
  --bind "$ARCHIVE:/package:rw" --bind "$EVID:/evidence:rw" \
  --bind "$ISO_HOME:/cert-home:rw" --bind "$ISO_TMP:/cert-tmp:rw" --bind "$ISO_CACHE:/cert-cache:rw" \
  --env "HOME=/cert-home,XDG_CACHE_HOME=/cert-cache,TMPDIR=/cert-tmp,PYTHONHASHSEED=0,PYTHONDONTWRITEBYTECODE=1,FDA_CERT_ISOLATED=1,FDA_CANDIDATE_SHA256=$ZIP_SHA,FDA_IMAGE_SHA256=$IMAGE_SHA" \
  "$IMAGE" bash /package/certification/run_fromraw_analysis_only.sh \
    --root /package --evidence /evidence --embed-python "$EMBED_RESOLVED" \
    > "$EVID/04_analysis_container.stdout.log" 2>&1
ANALYSIS_RC=$?
set -e
mv "$REFERENCE" "$ARCHIVE/output-simulated"
[[ "$ANALYSIS_RC" == 0 ]] || abort "isolated analysis failed; reference restored"

# Re-verify the exact 36/0/0 tally from the host, independent of the analysis container's own exit
# code, by reading the tally evidence it wrote into the shared bind ($EVID).
[[ -f "$EVID/05_tally.txt" ]] || abort "tally evidence missing (05_tally.txt)."
grep -qE "succeeded=36 failed=0 skipped=0" "$EVID/05_tally.txt" \
  || abort "run tally is not exactly 36/0/0 -- see 05_tally.txt"
# Require 36 distinct successful per-step logs, none swallowed/nonzero/ABI-fallback.
[[ -f "$EVID/05_step_logs.txt" ]] || abort "step-log evidence missing (05_step_logs.txt)."
grep -qE "distinct_steps=36 bad=\[\]" "$EVID/05_step_logs.txt" \
  || abort "did not find 36 clean per-step logs -- see 05_step_logs.txt"
# Every regenerated exhibit output must postdate the pre-run deletion (proves the run, not a stale
# leftover, produced them).
N_DEL_AFTER=0
for sub in output/figures output/tables; do
  c=$(find "$ARCHIVE/$sub" -type f 2>/dev/null | wc -l | tr -d ' ')
  N_DEL_AFTER=$((N_DEL_AFTER + c))
done
echo "regenerated_after_run=$N_DEL_AFTER" >> "$EVID/03b_output_deletion.txt"
[[ "$N_DEL_AFTER" -gt 0 ]] || abort "no exhibit outputs were regenerated after the pre-run deletion."

python3 "$ARCHIVE/certification/compare_output_simulated.py" --root "$ARCHIVE" \
  --report "$EVID/06_output_identity.txt" || abort "fresh outputs differ from output-simulated"
# Exact 283-member byte comparison: compare_output_simulated.py already enforces
# missing=0/differing=0/extras=0 (nothing under output/figures or output/tables is exempt) against whatever is
# shipped as output-simulated/ -- this additionally re-derives the deposited reference COUNT itself,
# so a truncated or substituted output-simulated/ cannot silently pass with fewer than the full 283.
grep -qE "^reference=283 " "$EVID/06_output_identity.txt" \
  || abort "output-simulated/ reference is not exactly 283 members -- see 06_output_identity.txt"
python3 "$ARCHIVE/certification/verify_immutable_tree.py" --root "$ARCHIVE" \
  --manifest "$EVID/02_immutable_members.json" --verify \
  > "$EVID/06_immutable_after.txt" 2>&1 || abort "immutable package members changed"

# Manuscript compile/identity check: hash_manuscript_closure.py enumerates and hashes the full
# manuscript dependency closure (main TeX, every \input fragment, every \includegraphics figure,
# .bib/.cls/.sty, the compiler driver, and the compiled PDF if present) and fails if any referenced
# target is missing. Run on the host against the regenerated $ARCHIVE tree.
# Post-run: record the closure of the tree the run produced, as EVIDENCE ONLY. --out is absolute, so
# this writes into the evidence directory and leaves certification/MANUSCRIPT_CLOSURE.sha256 -- an
# immutable package member that was already bound and verified above -- untouched. The committed
# closure was verified on the pristine extraction before the run (step 02b).
python3 "$ARCHIVE/certification/hash_manuscript_closure.py" --root "$ARCHIVE" \
  --out "$EVID/06_manuscript_closure_after_run.sha256" \
  > "$EVID/06_manuscript_closure.log" 2>&1 \
  || abort "manuscript dependency closure incomplete after the run -- see 06_manuscript_closure.log"

python3 - "$EVID" <<'PY'
import hashlib, os, sys
root=os.path.realpath(sys.argv[1]); rows=[]
for dp, dirs, files in os.walk(root):
    for name in files:
        p=os.path.join(dp,name)
        if name == "EVIDENCE_MANIFEST.sha256": continue
        h=hashlib.sha256()
        with open(p,"rb") as fh:
            for block in iter(lambda: fh.read(1<<20), b""): h.update(block)
        rows.append((os.path.relpath(p,root),h.hexdigest()))
with open(os.path.join(root,"EVIDENCE_MANIFEST.sha256"),"w") as out:
    for rel,digest in sorted(rows): out.write(f"{digest}  {rel}\n")
PY
(cd "$EVID" && sha256sum -c EVIDENCE_MANIFEST.sha256) > "$WORKDIR/EVIDENCE_MANIFEST_VERIFY.txt" \
  || abort "evidence manifest verification failed"
echo "FROM-RAW CERTIFICATION PASSED -- exact 36/0/0; ZIP/reference inaccessible during analysis"
