"""Recompute the published Class II maturity count under each re-draw.

Population and method are exactly 15_intext_derived_numbers.py:234-285. For each draw, a code's
invention year is replaced by that draw's year where the 2026-10-27 study drew it, and held at
the deposited value otherwise. Every code within +/-6 years of the threshold was drawn, so the
codes held fixed are ones that could only cross via a large revision; the out-of-band crossing
rate measured on the control sample is reported separately as the residual.

Usage: python3 maturity_sensitivity.py <tree root> <drawn_years.csv>
"""
import collections, pathlib, statistics, sys
import pandas as pd

ROOT = pathlib.Path(sys.argv[1]); RAW = ROOT/"data"/"raw"; DERIVED = ROOT/"data"/"derived"
THRESHOLD, BAND = 60, 6

regnum_p = next(c for c in (DERIVED/"RegNum_Factorized_Synth.csv",
                            RAW/"RegNum_Factorized_Synth.csv") if c.exists())
sn = pd.read_csv(regnum_p, dtype=str, low_memory=False).drop_duplicates("PRODUCTCODE_x")
sn["PRODUCTCODE"] = sn["PRODUCTCODE_x"]
inv = pd.read_csv(RAW/"innovation_year_all_other_FDA_project.csv")
inv510 = pd.merge(inv, sn[["PRODUCTCODE","SUBMISSION_TYPE_ID"]], on="PRODUCTCODE", how="left")
inv510 = inv510[inv510.SUBMISSION_TYPE_ID == "510(K)"]
fs = pd.read_csv(DERIVED/"Full_sample.csv", low_memory=False)

def count_over(year_map):
    """Apply the figure's own method with a given PRODUCTCODE -> invention year mapping."""
    iv = inv510.copy()
    iv["years"] = iv["PRODUCTCODE"].map(year_map).fillna(iv["years"])
    o2 = fs[fs.PRODUCTCODE.isin(iv["PRODUCTCODE"])].merge(
        iv[["PRODUCTCODE","years"]], on="PRODUCTCODE", how="left")
    o2["exp_years"] = 2019 - o2["years"]
    d2 = (o2[o2.year > 2015.0].groupby(["PRODUCTCODE","exp_years"]).mean(numeric_only=True)
          .reset_index().drop_duplicates("PRODUCTCODE"))
    return int(d2.PRODUCTCODE.nunique()), int((d2.exp_years > THRESHOLD).sum()), d2

dep_map = dict(zip(inv510.PRODUCTCODE, inv510.years))
n_pop, n_dep, d2_dep = count_over({})
print(f"population (post-2015 cross-section): {n_pop}")
print(f"deposited count over {THRESHOLD} years     : {n_dep}  ({n_dep/n_pop:.1%})   [manuscript ~650 / 29%]")

drawn = pd.read_csv(sys.argv[2])
pop = set(d2_dep.PRODUCTCODE)
near = set(d2_dep[(d2_dep.exp_years >= THRESHOLD-BAND) & (d2_dep.exp_years <= THRESHOLD+BAND)].PRODUCTCODE)
cov = set(drawn.PRODUCTCODE) & pop
print(f"  of which drawn on 2026-10-27        : {len(cov)} ({len(cov)/n_pop:.1%})")
print(f"  within +/-{BAND} yrs of threshold, drawn : {len(near & set(drawn.PRODUCTCODE))}/{len(near)}")

counts = []
print(f"\n{'draw':<8}{'count':>8}{'share':>9}{'vs deposited':>15}")
for d in sorted(drawn.draw.unique()):
    sub = drawn[drawn.draw == d]
    ym = dict(zip(sub.PRODUCTCODE, sub.year))
    n_c, n_o, _ = count_over(ym)
    counts.append(n_o)
    print(f"draw{d+1:<4}{n_o:>8}{n_o/n_c:>8.1%}{n_o-n_dep:>+15d}")
print(f"\nmean {statistics.mean(counts):.1f}  SD {statistics.pstdev(counts):.2f}"
      f"  range {min(counts)}-{max(counts)}  (deposited {n_dep})")
print(f"spread as a share of the deposited count: {(max(counts)-min(counts))/n_dep:.2%}")

undrawn = len(pop - cov)
print(f"\nResidual: {undrawn} codes in the population were not drawn; all sit more than {BAND}")
print(f"years from the threshold. At the 2.5% out-of-band crossing rate measured on the control")
print(f"sample, they contribute on the order of {round(undrawn*0.025)} further crossings, in both")
print(f"directions, which the figures above do not include.")
