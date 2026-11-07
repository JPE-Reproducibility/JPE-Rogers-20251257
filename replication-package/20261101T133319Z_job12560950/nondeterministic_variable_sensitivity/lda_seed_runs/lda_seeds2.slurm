#!/bin/bash
#SBATCH -J lda_redraw2
#SBATCH -A r00890
#SBATCH -p general
#SBATCH -t 10:00:00
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=48G
#SBATCH -o logs/slurm_%j.out
#SBATCH -e logs/slurm_%j.err
set -uo pipefail
# FDA_WORK: this exercise's work directory. FDA_SIF: the reference container.
W=${FDA_WORK:?set FDA_WORK}
B=$W/base
SIF=${FDA_SIF:?set FDA_SIF}
module load apptainer >/dev/null 2>&1 || true
mkdir -p "$W/home/mpl" "$W/apptmp"

for SEED in 5 6 7 8 9; do
  echo "================ SEED $SEED  $(date) ================"
  sed -i "s/random_state=[0-9][0-9]*, update_every=1/random_state=${SEED}, update_every=1/g" "$B/code/11a_product_variety.py"
  echo "  random_state sites now set to ${SEED}: $(grep -c "random_state=${SEED}, update_every=1" "$B/code/11a_product_variety.py")"
  rm -f "$B"/data/derived/lda_* || true
  rm -f "$B"/output/figures/variety_*.png || true
  apptainer exec --cleanenv --containall -B "$B":"$B" -H "$W/home" -W "$W/apptmp" \
    --env PYTHONHASHSEED=0,MPLCONFIGDIR="$W/home/mpl",NLTK_DATA=/opt/nltk_data,OMP_NUM_THREADS=8 \
    "$SIF" python3 "$B/code/11a_product_variety.py" > "$W/logs/seed_${SEED}.out" 2>&1
  echo "  seed $SEED rc=$?"
  mkdir -p "$W/results/seed_${SEED}"
  cp "$B"/output/figures/variety_*.png "$W/results/seed_${SEED}/" || true
  grep -E "Optimal topics|Topic [0-9]+: est=" "$W/logs/seed_${SEED}.out" > "$W/results/seed_${SEED}/estimates.txt" || true
  echo "  captured $(wc -l < "$W/results/seed_${SEED}/estimates.txt") estimate lines"
done
echo "================ ALL SEEDS DONE $(date) ================"
