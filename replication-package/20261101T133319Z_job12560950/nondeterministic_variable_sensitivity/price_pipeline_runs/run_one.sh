#!/bin/bash
# $1 = label (baseline|draw1..5); $2 = dir holding the two concordances, or BASELINE
set -euo pipefail
# Set FDA_WORK to the directory holding this exercise, and FDA_TREE to the extracted
# package the run executes against. Both were on a cluster filesystem when this ran.
W=${FDA_WORK:?set FDA_WORK to the work directory for this exercise}
B=${FDA_TREE:-$W/base}
L=$1; SRCD=${2:-BASELINE}
if [ "$SRCD" != "BASELINE" ]; then
  cp "$SRCD/2_1_GPT_Price_Links.csv" "$SRCD/3_2_GPT_Price_Links.csv" "$B/data/raw/"
else
  cp "$W/baseline_links/"*.csv "$B/data/raw/"
fi
rm -f "$B/output/tables/price_utilization_estimates.csv"
module load apptainer >/dev/null 2>&1 || true
cd "$B"
apptainer exec --cleanenv --containall \
  -B "$B":"$B" -W /tmp \
  --env HOME=/tmp,PYTHONHASHSEED=0,MPLCONFIGDIR=/tmp/mpl \
  "${FDA_SIF:?set FDA_SIF to the reference container}" \
  python3 "$B/code/05_price_analysis.py" > "$W/logs_${L}.out" 2>&1 || echo "RC=$? (see log)"
mkdir -p "$W/results/$L"
cp "$B/output/tables/price_utilization_estimates.csv" "$W/results/$L/" 2>/dev/null \
  && echo "$L: estimates captured" || echo "$L: NO estimates file produced"
