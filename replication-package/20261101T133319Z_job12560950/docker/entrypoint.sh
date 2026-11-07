#!/usr/bin/env bash
# Entrypoint for the replication container.
#
# The replication package is mounted at /replication. All arguments are passed
# straight through to run_all.py, so:
#   docker run ... fda-repro                       # --help (default)
#   docker run ... fda-repro                        (no args -> full pipeline once
#                                                    you pass an explicit flag)
#   docker run ... fda-repro --continue-on-fail    # full restricted pipeline
set -euo pipefail

export R_HOME="${R_HOME:-/usr/local/lib/R}"
export MPLBACKEND=Agg

# COMMAND PASSTHROUGH: if the first argument is an executable (e.g. `bash`, `sh`, `python3`), run it
# directly instead of the pipeline. This lets a caller open a shell or run an ad-hoc command inside the
# image WITHOUT mounting the package -- e.g. the CI sanity check `docker run <img> bash -lc '...'`, or an
# interactive `docker run -it <img> bash`. run_all.py's own flags (--help,
# --continue-on-fail, ...) start with `-` and are NOT executables, so the default pipeline path below is
# unaffected. (The certification stages invoke the image with `apptainer exec`, which bypasses this
# entrypoint entirely, so this changes nothing for the cert.)
if [ "$#" -gt 0 ] && command -v "$1" >/dev/null 2>&1; then
  exec "$@"
fi

cd /replication 2>/dev/null || {
  echo "ERROR: /replication is empty. Mount the package, e.g.:" >&2
  echo "  -v /path/to/replication_package:/replication" >&2
  exit 2
}
if [ ! -f run_all.py ]; then
  echo "ERROR: run_all.py not found in /replication (is the package mounted?)." >&2
  exit 2
fi

echo "=================================================================="
echo " Replication container"
echo "   Python: $(python3 --version 2>&1)"
Rscript -e 'cat("   R:     ", as.character(getRversion()),
                "| fixest", as.character(packageVersion("fixest")),
                "| didimputation", as.character(packageVersion("didimputation")), "\n")' 2>/dev/null || true
if [ -e data/raw/MAUDE ] && [ ! -e data/raw/MAUDE/. ]; then
  echo "   WARNING: data/raw/MAUDE is an unresolved symlink. For a full"
  echo "            restricted run, mount the MAUDE directory over it:"
  echo "            -v /path/to/MAUDE:/replication/data/raw/MAUDE"
fi
echo "   run_all.py $*"
echo "=================================================================="

exec python3 run_all.py "$@"
