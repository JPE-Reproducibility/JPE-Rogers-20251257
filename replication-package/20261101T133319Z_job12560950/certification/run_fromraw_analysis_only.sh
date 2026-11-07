#!/bin/bash
# Inner half of the official Option-2 certification. This script must run inside
# the network-denied container created by certify_fromraw_route.sh. It never
# receives the package ZIP or output-simulated reference.
set -euo pipefail

ROOT=""; EVID=""
# The image is self-contained: its own python3 is the pinned numpy 1.26.4 interpreter, so
# --embed-python is optional and defaults to it. The outer harness passes whatever it resolved.
EMBED_PY="python3"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) ROOT="$2"; shift 2 ;;
    --evidence) EVID="$2"; shift 2 ;;
    --embed-python) EMBED_PY="$2"; shift 2 ;;
    *) echo "ABORT: unknown arg $1" >&2; exit 2 ;;
  esac
done
[[ -n "$ROOT" && -n "$EVID" && -n "$EMBED_PY" ]] || {
  echo "ABORT: --root and --evidence are required (--embed-python defaults to python3)" >&2; exit 2; }
[[ "${FDA_CERT_ISOLATED:-}" == "1" ]] || {
  echo "ABORT: analysis-only runner requires FDA_CERT_ISOLATED=1" >&2; exit 2; }

abort() { echo "ANALYSIS ABORT: $*" >&2; exit 1; }
[[ -f "$ROOT/run_all.py" ]] || abort "package root invalid"
[[ ! -e "$ROOT/output-simulated" ]] || abort "reference output is visible to analysis"
[[ ! -e /submitted-package.zip && ! -e /submitted-candidate.zip && ! -e /reference-output ]] \
  || abort "forbidden reference mount is visible"
mkdir -p "$EVID"
cd "$ROOT"

python3 - <<'PY'
import os, re, socket
suspicious = re.compile(r"(TOKEN|SECRET|CREDENTIAL|PASSWORD|AWS_|GOOGLE_|OPENAI_|NEXIS|WRDS)", re.I)
bad = sorted(k for k in os.environ if suspicious.search(k))
if bad:
    raise SystemExit("credential-like environment variables survived --cleanenv: " + ", ".join(bad))
try:
    sock = socket.create_connection(("1.1.1.1", 53), timeout=1.0)
except OSError:
    pass
else:
    sock.close()
    raise SystemExit("outbound network connection unexpectedly succeeded")
mounts = open("/proc/self/mountinfo", errors="replace").read()
for token in ("/N/slate", "/geode2", "/Users/parkerrogers", "replication_package_v9_source",
              "fda_v32_final", "fda_v33_remediation_work"):
    if token in mounts:
        raise SystemExit("forbidden host/restricted mount visible: " + token)
PY

{
  echo "package_sha=${FDA_CANDIDATE_SHA256:-MISSING}"
  echo "image_sha=${FDA_IMAGE_SHA256:-MISSING}"
  echo "network_namespace=$(readlink /proc/self/ns/net 2>/dev/null || echo unavailable)"
  echo "mountinfo_sha256=$(sha256sum /proc/self/mountinfo 2>/dev/null | awk '{print $1}')"
  cat /proc/self/mountinfo 2>/dev/null || true
} > "$EVID/04_isolation_mounts.txt"
[[ "${FDA_CANDIDATE_SHA256:-}" =~ ^[0-9a-f]{64}$ ]] || abort "package SHA not bound"
[[ "${FDA_IMAGE_SHA256:-}" =~ ^[0-9a-f]{64}$ ]] || abort "image SHA not bound"

python3 certification/preflight_apimode.py "$ROOT" > "$EVID/04_apimode.log" 2>&1 \
  || abort "rpy2 API-mode preflight failed"
"$EMBED_PY" certification/preflight_apimode.py "$ROOT" --require-model \
  > "$EVID/04_embed_model.log" 2>&1 || abort "embedding/model preflight failed"

python3 - "$ROOT" <<'PY'
import os, sys
root = os.path.realpath(sys.argv[1])
for rel in ("output/figures", "output/tables"):
    base = os.path.join(root, rel)
    os.makedirs(base, exist_ok=True)
    for dp, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            path = os.path.join(dp, name)
            if os.path.islink(path):
                raise SystemExit("symlink under output tree: " + path)
        for name in files:
            os.unlink(os.path.join(dp, name))
PY

# run_all sets PYTHONHASHSEED, the single-threaded BLAS/OpenMP pins, FDA_STRICT_INTEXT=1 and
# FDA_INTEXT_ROUTE itself, from its own route flags, and refuses to start on this route while
# output/figures or output/tables holds a file (the block above emptied them). The values are still
# exported here so the evidence transcript records them explicitly and they cannot silently differ.
LOG="$EVID/04_run_transcript.log"
STEP_LOGS="$EVID/04_step_logs"
mkdir -p "$STEP_LOGS"
set +e
PYTHONHASHSEED=0 PYTHONDONTWRITEBYTECODE=1 FDA_STEP_LOG_DIR="$STEP_LOGS" \
FDA_SAFETY_EMBED_PYTHON="$EMBED_PY" FDA_STRICT_INTEXT=1 FDA_INTEXT_ROUTE=synthetic \
  python3 run_all.py --synthetic-from-raw --force-estimation \
    --regenerate-safety-keywords --regenerate-safety-embeddings > "$LOG" 2>&1
RUN_RC=$?
set -e
echo "run_all_exit_code=$RUN_RC" > "$EVID/04_run_exit.txt"

SUCC="$(grep -oE 'Succeeded:[[:space:]]*[0-9]+' "$LOG" | tail -1 | grep -oE '[0-9]+' || true)"
FAIL="$(grep -oE 'Failed:[[:space:]]*[0-9]+' "$LOG" | tail -1 | grep -oE '[0-9]+' || true)"
SKIP="$(grep -oE 'Skipped:[[:space:]]*[0-9]+' "$LOG" | tail -1 | grep -oE '[0-9]+' || true)"
echo "tally: rc=$RUN_RC succeeded=${SUCC:-?} failed=${FAIL:-?} skipped=${SKIP:-?}" \
  | tee "$EVID/05_tally.txt"
[[ "$RUN_RC" == 0 && "${SUCC:-}" == 36 && "${FAIL:-}" == 0 && "${SKIP:-}" == 0 ]] \
  || abort "tally is not exactly 36/0/0"

python3 synthetic_pipeline/preflight_from_raw.py --post-run \
  > "$EVID/05_transformation_outputs.txt" 2>&1 || abort "transformation-output contract failed"
python3 certification/verify_intext_report.py --root "$ROOT" --route synthetic \
  > "$EVID/05_intext_report.txt" 2>&1 || abort "synthetic in-text inventory failed"
python3 code/audit_pipeline_current.py > "$EVID/05_manuscript_exhibit_audit.txt" 2>&1 \
  || abort "manuscript exhibit audit failed"
python3 certification/validate_handentered_tables.py \
  --manuscript "$ROOT/paper/JPE_submission_v8.tex" --output-dir "$ROOT/output/tables" \
  > "$EVID/05_handentered_tables.txt" 2>&1 || abort "hand-entered table audit failed"

python3 - "$STEP_LOGS" "$EVID/05_step_logs.txt" <<'PY'
import glob, os, re, sys
logs = glob.glob(os.path.join(sys.argv[1], "step_*.log"))
steps, bad = set(), []
for path in logs:
    text = open(path, errors="replace").read()
    rc = re.search(r"# returncode: (-?\d+)", text)
    step = re.search(r"step_(\d+)_", os.path.basename(path))
    if step:
        steps.add(int(step.group(1)))
    if (not rc or rc.group(1) != "0" or "ABI mode" in text or
            "ABI fallback" in text or ".cache/huggingface" in text):
        bad.append(os.path.basename(path))
open(sys.argv[2], "w").write(f"logs={len(logs)} distinct_steps={len(steps)} bad={bad}\n")
raise SystemExit(0 if len(steps) == 36 and not bad else 1)
PY

echo "ANALYSIS-ONLY PASS -- exact 36/0/0; reference and package ZIP were not mounted"
