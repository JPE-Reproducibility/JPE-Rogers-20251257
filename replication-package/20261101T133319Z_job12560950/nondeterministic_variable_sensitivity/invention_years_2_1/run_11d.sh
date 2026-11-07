#!/bin/bash
# run_11d.sh <label> <2_1 invention-year csv | BASELINE>
# Substitutes one invention-year vector into the certified tree and re-runs the
# market-age regression step. Only data/raw/innovation_year_2_1_FDA_project.csv
# varies; code, modules and every other input are held fixed.
set -euo pipefail
# Set FDA_WORK to the directory holding this exercise, and FDA_TREE to the extracted
# package the run executes against. Both were on a cluster filesystem when this ran.
W=${FDA_WORK:?set FDA_WORK to the work directory for this exercise}
B=${FDA_TREE:?set FDA_TREE to the extracted package tree}
L=$1; SRC=${2:-BASELINE}

if [ "$SRC" = "BASELINE" ]; then
  cp "$W/innovation_year_2_1_BASELINE.csv" "$B/data/raw/innovation_year_2_1_FDA_project.csv"
else
  cp "$SRC" "$B/data/raw/innovation_year_2_1_FDA_project.csv"
fi

# Clear the four outputs we compare on, so a crash cannot leave a stale file behind.
rm -f "$B/output/tables/maturity_gradient_slopes.csv" \
      "$B/output/tables/exp_impact_zero_crossings.csv" \
      "$B/output/tables/model_v_serious_est_2_1.csv" \
      "$B/output/tables/model_patent_est_2_1.csv" \
      "$B/output/tables/model_v_serious_est_3_2.csv" \
      "$B/output/tables/model_patent_est_3_2.csv"

module load apptainer >/dev/null 2>&1 || true
cd "$B"
apptainer exec --cleanenv --containall \
  -B "$B":"$B" -W /tmp \
  --env HOME=/tmp,PYTHONHASHSEED=0,MPLCONFIGDIR=/tmp/mpl \
  "${FDA_SIF:?set FDA_SIF to the reference container}" \
  python3 "$B/code/11d_reg_design.py" > "$W/logs_${L}.out" 2>&1 || echo "RC=$? (see $W/logs_${L}.out)"

mkdir -p "$W/results/$L"
n=0
for f in maturity_gradient_slopes.csv exp_impact_zero_crossings.csv \
         model_v_serious_est_2_1.csv model_patent_est_2_1.csv \
         model_v_serious_est_3_2.csv model_patent_est_3_2.csv; do
  if cp "$B/output/tables/$f" "$W/results/$L/" 2>/dev/null; then n=$((n+1)); fi
done
echo "$L: captured $n of 6 output tables"
