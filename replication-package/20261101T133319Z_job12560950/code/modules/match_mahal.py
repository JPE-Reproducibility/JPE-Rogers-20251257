"""
Mahalanobis distance-based matching for treated and control product codes.

Paths come from config.
Preserves API: get_match_mahalanobis() and get_match_mahalanobis_cond().

Inputs: Full_sample.csv from data/derived/
Outputs: Matched sample DataFrames with FE assignments
"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from numpy.linalg import inv
from sklearn.preprocessing import StandardScaler
import logging
import re

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MatchInputError(ValueError):
    """The inputs to a nearest-neighbour match cannot identify a nearest neighbour.

    Raised instead of returning an arbitrary index. Before 2026-10-13 `get_similar` returned
    `np.argpartition(diff, topn)[:topn]` whatever `diff` contained, so a treated unit whose
    matching value was NaN -- e.g. one with no rows in its own pre-event window, which makes
    every squared distance NaN -- was matched to index 0, the FIRST row of a frame that
    `groupby("PRODUCTCODE")` has sorted, i.e. the lowest-numbered control, with no exception and
    no log line. A silent arbitrary match is worse than a failure: it enters the estimation
    sample looking like a real match.
    """


def get_similar(pos_pscore, neg_pscore, topn=5, n_jobs=1):
    """Euclidean nearest-neighbor matching.

    Raises MatchInputError rather than returning an arbitrary index when the treated vector is
    non-finite, when the control pool is too small for `topn`, or when the distances come out
    non-finite. Callers that legitimately want to skip such a unit must catch MatchInputError
    explicitly and SAY SO (count it, log it), not swallow it.
    """
    pos = np.asarray(pos_pscore, dtype="float64")
    neg = np.asarray(neg_pscore, dtype="float64")
    if not np.isfinite(pos).all():
        raise MatchInputError(
            f"treated matching vector is not finite ({pos.ravel().tolist()}): every distance would "
            "be NaN and the 'nearest' control would be whichever row sorts first"
        )
    if neg.shape[0] <= topn:
        raise MatchInputError(
            f"control pool has {neg.shape[0]} unit(s), which cannot supply topn={topn} "
            "nearest neighbour(s)"
        )
    diff = pos - neg
    diff = diff * diff
    diff = np.sum(diff, axis=1)
    if not np.isfinite(diff).all():
        raise MatchInputError(
            f"{int((~np.isfinite(diff)).sum())} of {diff.size} control distance(s) are non-finite; "
            "the control matching values contain NaN or inf"
        )
    idx = np.argpartition(diff, topn)
    return diff, idx[:topn]


def get_similar_mahalanobis(treated_vector, control_matrix, VI, topn=5):
    """Mahalanobis distance between one treated unit and all controls."""
    treated_vector = treated_vector.reshape(1, -1)
    distances = cdist(control_matrix, treated_vector, metric="mahalanobis", VI=VI).flatten()
    top_indices = np.argpartition(distances, topn)[:topn]
    top_indices_sorted = top_indices[np.argsort(distances[top_indices])]
    distances_sorted = distances[top_indices_sorted]
    return distances_sorted, top_indices_sorted


def _load_full_sample():
    """Load Full_sample.csv from config path."""
    path = config.DERIVED_DATA_DIR / config.FULL_SAMPLE
    df = pd.read_csv(path)
    logging.info(f"Loaded main dataset with {len(df)} records from {path}.")
    return df


def _preprocess_event(df, event, universe=False, petitioned=False):
    """Apply event-specific preprocessing to the full sample."""
    if event == "3_2":
        if not universe:
            df = df[(df.patent_sum_3_2 > 0) | (df.controls == 1)]
            df = df[df.one_pat_atleast > 0]
        df["year_reclassified"] = df["year_reclassified_3_2"]
        df = df[df.year != 0]
        # treatment must be set before FDA_own_accord_3_2 filtering
        df["treatment"] = 0
        df.loc[df.year_reclassified.notnull(), "treatment"] = 1
        df.loc[df.treatment == 0, "FDA_own_accord_3_2"] = 0
        if petitioned:
            df = df[(df.FDA_own_accord_3_2 == 0) | (df.treatment == 0)]
        else:
            df = df[(df.FDA_own_accord_3_2 == 1) | (df.treatment == 0)]
    else:
        if not universe:
            df = df[(df.patent_sum_2_1 > 0) | (df.controls == 1)]
            df = df[df.one_pat_atleast > 0]
        df["year_reclassified"] = df["year_reclassified_2_1"]
        df["treatment"] = 0
        df.loc[df.year_reclassified.notnull(), "treatment"] = 1

    # Common processing
    for col in ["D", "L", "H", "S"]:
        df[col] = df[col].fillna(0)
    df["v_serious"] = df["D"] + df["L"] + df["H"] + df["S"]
    df["factorized"] = df.PRODUCTCODE.astype("category").cat.codes
    df["posttreat"] = 0
    df.loc[(df.treatment == 1) & (df.year >= df.year_reclassified), "posttreat"] = 1
    df["real_pats"] = df["patents_allpats"]
    df["unique_firms"] = df["patents_newfirm"]
    df["unique_firmsPC"] = df["patents_newfirmPC"]
    df["times_cited"] = df["times_cited"].fillna(0)
    df["xi_real"] = df["xi_real"].fillna(0)
    df["xi_real_2019"] = df["xi_real"] / config.CPI_DEFLATOR_2019
    df["firm_expansion_patents"] = df["unique_firmsPC"] - df["unique_firms"]

    if event == "3_2":
        df["dev_count"] = df["dev_count"].fillna(0)
        df["firm_count"] = df["firm_count"].fillna(0)
        df["absnew_firm_count"] = df["absnew_firm_count"].fillna(0)
        df["firm_expansion"] = df["firm_count"] - df["absnew_firm_count"]

    return df


def _get_control_filter(event):
    """Return submission type filter for control units."""
    if event == "3_2":
        return ["510(K)", "PMA"]
    else:
        return ["510(K)", "510(K) Exempt"]


def _run_matching(df, event, topn, pre_event_window, variables_to_match,
                  matching_vars, adverse, innovation, quality,
                  pat_col="patents_allpats"):
    """Core matching loop shared by both public functions."""
    treated_df = df[df.treatment == 1].copy()
    control_df = df[df.treatment == 0].copy()
    valid_types = _get_control_filter(event)
    control_df = control_df[control_df.SUBMISSION_TYPE_ID.isin(valid_types)]

    logging.info(f"Treated: {len(treated_df)} rows, Control: {len(control_df)} rows.")

    treated_product_codes = treated_df["PRODUCTCODE"].unique()
    matched_pairs = []

    # Precompute control subsets
    control_pre_event_means = {}
    for ctrl_pc in control_df["PRODUCTCODE"].unique():
        control_pre_event_means[ctrl_pc] = control_df[control_df.PRODUCTCODE == ctrl_pc].copy()

    for i, treated_pc in enumerate(treated_product_codes):
        treated_event_year = treated_df[treated_df.PRODUCTCODE == treated_pc]["year_reclassified"].iloc[0]
        pre_event_start = treated_event_year - pre_event_window
        pre_event_end = treated_event_year - 1

        treated_subset = treated_df[
            (treated_df.PRODUCTCODE == treated_pc)
            & (treated_df.year >= pre_event_start)
            & (treated_df.year <= pre_event_end)
        ]
        if treated_subset.empty:
            logging.warning(f"No pre-event data for {treated_pc}. Skipping.")
            continue

        treated_mean = treated_subset[variables_to_match].mean()

        control_means = []
        control_pcs = []

        if adverse or innovation or quality:
            control_meaned = (
                control_df[
                    (control_df.year >= pre_event_start) & (control_df.year <= pre_event_end)
                ]
                .groupby("PRODUCTCODE")
                .mean(numeric_only=True)
                .reset_index()
            )
            treated_meaned = treated_subset.mean(numeric_only=True)
            control_pcs = control_meaned["PRODUCTCODE"].values
        else:
            for ctrl_pc in control_pre_event_means:
                ctrl_subset = control_pre_event_means[ctrl_pc]
                ctrl_pre = ctrl_subset[
                    (ctrl_subset.year >= pre_event_start) & (ctrl_subset.year <= pre_event_end)
                ]
                if ctrl_pre.empty:
                    continue
                ctrl_mean = ctrl_pre[variables_to_match].mean()
                control_means.append(ctrl_mean.values)
                control_pcs.append(ctrl_pc)

            if not control_means:
                logging.warning(f"No eligible controls for {treated_pc}. Skipping.")
                continue

            control_means = np.array(control_means)
            scaler = StandardScaler()
            match_idx = [variables_to_match.index(v) for v in matching_vars]
            scaler.fit(control_means[:, match_idx])
            treated_std = scaler.transform(
                treated_mean[[v for v in matching_vars]].values.reshape(1, -1)
            )
            control_std = scaler.transform(control_means[:, match_idx])
            cov_matrix = np.cov(control_std, rowvar=False)
            try:
                VI = inv(cov_matrix)
            except np.linalg.LinAlgError:
                cov_matrix += np.eye(cov_matrix.shape[0]) * 1e-10
                VI = inv(cov_matrix)

        # Distance computation
        if adverse:
            distances, indices = get_similar(
                treated_meaned[["v_serious"]].values,
                control_meaned[["v_serious"]].values,
                topn=topn,
            )
        elif quality:
            distances, indices = get_similar(
                treated_meaned[["xi_real_2019", "times_cited"]].values,
                control_meaned[["xi_real_2019", "times_cited"]].values,
                topn=topn,
            )
        elif innovation:
            if event == "2_1":
                match_cols = [pat_col, "patents_newfirm"]
            else:
                match_cols = [pat_col, "dev_count", "patents_newfirm"]
            distances, indices = get_similar(
                treated_meaned[match_cols].values,
                control_meaned[match_cols].values,
                topn=topn,
            )
        else:
            distances, indices = get_similar_mahalanobis(
                treated_std.flatten(), control_std, VI, topn=topn
            )

        matched_indices = indices[:topn]
        matched_pcs = [control_pcs[idx] for idx in matched_indices]
        SSE = np.round(np.sum(distances[: len(matched_pcs)] ** 2), 2)
        unique_fe = f"FE_{i}"

        for match_pc in matched_pcs:
            matched_pairs.append(
                {
                    "PRODUCTCODE": treated_pc,
                    "treated": treated_pc,
                    "match": match_pc,
                    "SSE": SSE,
                    "FE": unique_fe,
                    "year_reclassified_controls": treated_event_year,
                }
            )

    matched_pairs_df = pd.DataFrame(matched_pairs)
    logging.info(f"Total matched pairs: {len(matched_pairs_df)}")
    return matched_pairs_df, treated_product_codes


def _assemble_final(df, matched_pairs_df, treated_product_codes, event):
    """Build final matched dataset with FE assignments."""
    matched_control_pcs = matched_pairs_df["match"].tolist()
    all_pcs = list(treated_product_codes) + matched_control_pcs
    final = df[df["PRODUCTCODE"].isin(all_pcs)].copy()

    treated_final = final[final["treatment"] == 1].merge(
        matched_pairs_df[["treated", "FE"]].drop_duplicates(),
        left_on="PRODUCTCODE",
        right_on="treated",
        how="left",
    ).drop(columns=["treated"])

    control_final = final[final["treatment"] == 0].merge(
        matched_pairs_df[["match", "FE"]],
        left_on="PRODUCTCODE",
        right_on="match",
        how="inner",
    ).drop(columns=["match"])

    final_with_fe = pd.concat([treated_final, control_final], ignore_index=True)

    if event == "3_2":
        final_with_fe["FDA_own_accord"] = final_with_fe.groupby(["FE"])[
            "FDA_own_accord_3_2"
        ].transform("max")

    final_with_fe.reset_index(drop=True, inplace=True)
    logging.info(f"Final matched dataset: {len(final_with_fe)} records.")
    return final_with_fe


# ============================================================================
# Public API
# ============================================================================

def get_match_mahalanobis(event, topn=5, pre_event_window=6, adverse=False,
                          innovation=False, universe=False, quality=False,
                          petitioned=False):
    """
    Mahalanobis distance-based matching on pre-event means.

    Returns DataFrame with treated + matched controls and FE assignments.
    """
    df = _load_full_sample()
    df = _preprocess_event(df, event, universe=universe, petitioned=petitioned)

    # Variable selection
    if adverse:
        variables_to_match = ["v_serious", "H"]
    elif innovation:
        variables_to_match = ["patents_allpats", "patents_newfirmPC", "patents_newfirm"]
    elif quality:
        variables_to_match = ["xi_real_2019", "times_cited"]
    else:
        variables_to_match = [
            "dev_count", "firm_count", "absnew_firm_count",
            "patents_allpats", "patents_newfirmPC", "patents_newfirm",
            "patents_pats_nodrugs", "times_cited", "xi_real",
            "v_serious", "H", "D", "L", "S",
        ]

    outcome_vars = [
        "patents_allpats", "patents_newfirmPC", "patents_newfirm",
        "patents_pats_nodrugs", "real_pats", "unique_firms",
        "unique_firmsPC", "firm_expansion_patents", "xi_real_2019",
        "H", "D", "L", "S",
    ]
    matching_vars = [v for v in variables_to_match if v not in outcome_vars]

    matched_pairs_df, treated_pcs = _run_matching(
        df, event, topn, pre_event_window, variables_to_match,
        matching_vars, adverse, innovation, quality,
        pat_col="patents_allpats",
    )
    return _assemble_final(df, matched_pairs_df, treated_pcs, event)


def get_match_mahalanobis_cond(event, topn=5, pre_event_window=6, adverse=False,
                                innovation=False, condition=None, quality=False,
                                petitioned=False):
    """
    Conditional Mahalanobis matching (e.g., device patents only).

    Same as get_match_mahalanobis but loads device-patent-specific data
    when condition='is_dev'.
    """
    df = _load_full_sample()

    if condition == "is_dev":
        # Keep patents_allpats for _preprocess_event (real_pats); add device column alongside
        dev_pats = pd.read_csv(
            config.RAW_DATA_DIR / "new_patent_analysis" / "all_device_patents_w_pc.csv"
        )
        all_pats = pd.read_csv(config.DERIVED_DATA_DIR / config.SOURCE_FILES["all_patents"])
        all_pats["patent_id"] = (
            all_pats["id"].astype(str).str.split("-").str[1].apply(lambda s: re.sub(r"\D", "", s))
        )
        dev_pats["patent_id"] = dev_pats["patent_id"].astype(str)
        all_pats = all_pats[all_pats.patent_id.isin(dev_pats["patent_id"])]
        all_pats["patents_devpats_gpt4o"] = 1
        all_pats = (
            all_pats.groupby(["PRODUCTCODE", "year"])["patents_devpats_gpt4o"]
            .sum()
            .reset_index()
        )
        df = pd.merge(df, all_pats, on=["year", "PRODUCTCODE"], how="left")
        df["patents_devpats_gpt4o"] = df["patents_devpats_gpt4o"].fillna(0)

    df = _preprocess_event(df, event, petitioned=petitioned)

    # Variable selection (uses device patents instead of all patents)
    pat_col = "patents_devpats_gpt4o" if condition == "is_dev" else "patents_allpats"
    if adverse:
        variables_to_match = ["v_serious", "H"]
    elif innovation:
        variables_to_match = [pat_col, "patents_newfirmPC", "patents_newfirm"]
    elif quality:
        variables_to_match = ["xi_real_2019", "times_cited"]
    else:
        variables_to_match = [
            "dev_count", "firm_count", "absnew_firm_count",
            pat_col, "patents_newfirmPC", "patents_newfirm",
            "patents_pats_nodrugs", "times_cited", "xi_real",
            "v_serious", "H", "D", "L", "S",
        ]

    outcome_vars = [
        pat_col, "patents_newfirmPC", "patents_newfirm",
        "patents_pats_nodrugs", "real_pats", "unique_firms",
        "unique_firmsPC", "firm_expansion_patents", "xi_real_2019",
        "H", "D", "L", "S",
    ]
    matching_vars = [v for v in variables_to_match if v not in outcome_vars]

    matched_pairs_df, treated_pcs = _run_matching(
        df, event, topn, pre_event_window, variables_to_match,
        matching_vars, adverse, innovation, quality,
        pat_col=pat_col,
    )
    return _assemble_final(df, matched_pairs_df, treated_pcs, event)
