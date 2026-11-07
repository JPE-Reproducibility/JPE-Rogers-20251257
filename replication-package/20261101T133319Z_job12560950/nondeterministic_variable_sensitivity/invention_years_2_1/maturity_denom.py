"""Reproduce the population the published Class II maturity figures are taken over.

Mirrors 15_intext_derived_numbers.py:234-285 exactly: 510(K) product codes that have
invention-year data, restricted to the post-2015 cross-section of Full_sample.csv, with device
age = 2019 - invention year, deduplicated by product code. Prints the denominator, the count and
share over the 60-year threshold, and -- so the re-draw coverage is visible -- how many of those
codes the 2026-10-27 threshold-targeted sample actually drew.

Usage: python3 maturity_denom.py <tree root> [covered_codes.txt]
"""
import pathlib, sys
import pandas as pd

ROOT = pathlib.Path(sys.argv[1])
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
THRESHOLD = 60          # MANUSCRIPT_MATURITY_THRESHOLD_YEARS (its own comment says 63; the code says 60)

regnum_p = next((c for c in (DERIVED / "RegNum_Factorized_Synth.csv",
                             RAW / "RegNum_Factorized_Synth.csv") if c.exists()), None)
inv_p = RAW / "innovation_year_all_other_FDA_project.csv"
fs_p = DERIVED / "Full_sample.csv"
print(f"regnum: {regnum_p}\ninv   : {inv_p}\nfs    : {fs_p}\n")

sn = pd.read_csv(regnum_p, dtype=str, low_memory=False).drop_duplicates("PRODUCTCODE_x")
sn["PRODUCTCODE"] = sn["PRODUCTCODE_x"]
inv = pd.read_csv(inv_p)
print(f"invention-year rows (all_other)              : {len(inv)}")

inv510 = pd.merge(inv, sn[["PRODUCTCODE", "SUBMISSION_TYPE_ID"]], on="PRODUCTCODE", how="left")
inv510 = inv510[inv510.SUBMISSION_TYPE_ID == "510(K)"]
print(f"  of which 510(K)                            : {len(inv510)}")

fs = pd.read_csv(fs_p, low_memory=False)
o2 = fs[fs.PRODUCTCODE.isin(inv510["PRODUCTCODE"])].merge(
    inv510[["PRODUCTCODE", "years"]], on="PRODUCTCODE", how="left")
print(f"  of which present in Full_sample             : {o2.PRODUCTCODE.nunique()}")

o2["exp_years"] = 2019 - o2["years"]
d2 = (o2[o2.year > 2015.0].groupby(["PRODUCTCODE", "exp_years"]).mean(numeric_only=True)
      .reset_index().drop_duplicates("PRODUCTCODE"))
n_cross = int(d2.PRODUCTCODE.nunique())
n_over = int((d2.exp_years > THRESHOLD).sum())
print(f"\n==> DENOMINATOR (post-2015 cross-section)    : {n_cross}")
print(f"==> over the {THRESHOLD}-year threshold            : {n_over}  ({n_over/n_cross:.1%})")
print(f"    manuscript prints ~650 and 'about 29%'")

# How close to the threshold does the population sit? This is what governs how much
# re-draw churn can cross it.
for band in (3, 6, 10):
    lo, hi = THRESHOLD - band, THRESHOLD + band
    inband = int(((d2.exp_years >= lo) & (d2.exp_years <= hi)).sum())
    print(f"    within +/-{band:2d} years of the threshold     : {inband}  ({inband/n_cross:.1%})")

if len(sys.argv) > 2:
    covered = {l.strip() for l in open(sys.argv[2]) if l.strip()}
    pop = set(d2.PRODUCTCODE)
    print(f"\nre-draw coverage of this population:")
    print(f"  codes drawn on 2026-10-27                  : {len(covered)}")
    print(f"  of the {len(pop)} in the population, drawn     : {len(pop & covered)}"
          f"  ({len(pop & covered)/len(pop):.1%})")
    near = set(d2[(d2.exp_years >= THRESHOLD - 6) & (d2.exp_years <= THRESHOLD + 6)].PRODUCTCODE)
    print(f"  of the {len(near)} within +/-6 years, drawn       : {len(near & covered)}"
          f"  ({len(near & covered)/max(len(near),1):.1%})")
