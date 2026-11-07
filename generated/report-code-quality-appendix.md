## Appendix: Detailed Code Quality Findings

*Generated on 2026-11-07 16:43:44*

### Python

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (validate_handentered_tables.py, line 108)
  → Dr = adv.loc[adv.outcome == "D"].iloc[0]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (validate_handentered_tables.py, line 109)
  → Hr = adv.loc[adv.outcome == "H"].iloc[0]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (validate_handentered_tables.py, line 181)
  → fda32 = len(set(inv32.loc[inv32["FDA_own_accord"] == 1, "PRODUCTCODE"].astype(str)) - set(ATYP))

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (validate_handentered_tables.py, line 185)
  → final21 = int(tr.loc[tr.reclass_type.astype(str) == "2_1", "n_treated"].iloc[0])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (validate_handentered_tables.py, line 187)
  → cov32 = int(cov.loc[cov.reclass_type.astype(str) == "3_2", "n_covered"].iloc[0])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (validate_handentered_tables.py, line 188)
  → cov21 = int(cov.loc[cov.reclass_type.astype(str) == "2_1", "n_covered"].iloc[0])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 55)
  → df_3_2.loc[df_3_2.year_reclassified.notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 87)
  → df_3_2.loc[df_3_2.PRODUCTCODE == PC, "FE"] = i

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 115)
  → df.loc[df.year_reclassified.notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 120)
  → df_src.loc[df_src.treatment == 0, "FE"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 128)
  → df_src.loc[df_src.PRODUCTCODE == PC, "FE"] = i

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 138)
  → df_spillovers.loc[df_spillovers.year_reclassified.notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 140)
  → df_spillovers.loc[df_spillovers.treatment == 0, "FE"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 148)
  → df_spillovers.loc[df_spillovers.PRODUCTCODE == PC, "FE"] = i

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 235)
  → firms_temp.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 248)
  → firms_temp.loc[firms_temp[outcome] < 0, outcome] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 255)
  → firms_temp.loc[firms_temp[outcome] < 0, outcome] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 337)
  → firms.loc[firms["year_reclassified_" + RECLASS_TYPE].notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03a_estimation_3to2.py, line 340)
  → firms.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03b_estimation_2to1.py, line 60)
  → df.loc[df.year_reclassified.notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03b_estimation_2to1.py, line 158)
  → firms_temp.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03b_estimation_2to1.py, line 171)
  → firms_temp.loc[firms_temp[outcome] < 0, outcome] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03b_estimation_2to1.py, line 178)
  → firms_temp.loc[firms_temp[outcome] < 0, outcome] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03b_estimation_2to1.py, line 209)
  → n_treated = int(full.loc[treated_mask, "PRODUCTCODE"].nunique())

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03b_estimation_2to1.py, line 277)
  → firms.loc[firms["year_reclassified_" + RECLASS_TYPE].notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (03b_estimation_2to1.py, line 280)
  → firms.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 345)
  → df.loc[hit, "posttreat_new"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 360)
  → df.loc[df.treatment == 0, "FE"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 368)
  → df.loc[df.PRODUCTCODE == PC, "FE"] = i

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 391)
  → df.loc[df.year_reclassified.notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 400)
  → df.loc[df.year_reclassified.notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 505)
  → df.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 511)
  → df.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 569)
  → group_means.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 577)
  → group_means.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 593)
  → d = (control_groups.loc[list(available), "metric"] - t_val).abs()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 596)
  → pairs_nr.append((t_pc, control_groups.loc[idx, "PRODUCTCODE"]))

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 689)
  → df.loc[df.v_serious.isnull(), "v_serious"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 813)
  → estimates_df.loc[idx, "SE"] = (row["upper_cb"] - row["Effect"]) / 1.96

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (04_event_studies.py, line 815)
  → estimates_df.loc[idx, "SE"] = (row["Effect"] - row["lower_cb"]) / 1.96

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 256)
  → fda_to_hcpcs.loc[fda_to_hcpcs.PRODUCTCODE == "MLM", "HCPCS"] = "80197"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 257)
  → fda_to_hcpcs.loc[fda_to_hcpcs.PRODUCTCODE == "DAD", "HCPCS"] = "83010"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 293)
  → n_1998 = int(matched_21.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 318)
  → pcs |= set(pan.loc[pan["treatment"] == 1, "PRODUCTCODE"].astype(str))

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 329)
  → pcs |= set(xw.loc[xw["treatment"] == 1, "PRODUCTCODE"].astype(str))

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 377)
  → f"{hcpcs_3_2.loc[hcpcs_3_2.treatment == 1, 'PRODUCTCODE'].nunique()} (3_2), "

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 378)
  → f"{hcpcs_2_1.loc[hcpcs_2_1.treatment == 1, 'PRODUCTCODE'].nunique()} (2_1)"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 467)
  → base.loc[base[proc_col].isin(treated_procs), [proc_col, reclass_col]]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 514)
  → cutoff = int(yreclass.loc[t])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 661)
  → + claims.loc[claims.year_reclassified.isnull(), "match_rank"].astype(str)

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 692)
  → full.loc[full[col] == FILL_VAL, col] = np.nan

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 724)
  → stacked.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 918)
  → df.loc[hit, "posttreat_new"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 1132)
  → pre_df = df_panel.loc[mask, outcome]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (05_price_analysis.py, line 1189)
  → n_cov = int(df_panel.loc[df_panel["treatment"] == 1, "PRODUCTCODE"].nunique())

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06a_safety_analysis.py, line 183)
  → df_dd.loc[df_dd.treatment.isnull(), "treatment"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06a_safety_analysis.py, line 256)
  → baseline_mean = df_dd.loc[mask, "safety_prop"].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06a_safety_analysis.py, line 257)
  → baseline_std = df_dd.loc[mask, "safety_prop"].std()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06a_safety_analysis.py, line 322)
  → median_yr = raw_safety.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06b_validate_safety.py, line 282)
  → df_dd.loc[df_dd.treatment.isnull(), "treatment"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06b_validate_safety.py, line 295)
  → df_dd.loc[df_dd.treatment == 0, "FE"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06b_validate_safety.py, line 314)
  → df_dd.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06b_validate_safety.py, line 320)
  → df_dd.loc[df_dd["safety_prop"] > 0, "safety_prop"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06b_validate_safety.py, line 340)
  → baseline_mean = df_dd.loc[mask, "safety_prop"].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06b_validate_safety.py, line 341)
  → baseline_std = df_dd.loc[mask, "safety_prop"].std()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06c_validate_safety_embed.py, line 339)
  → df_dd.loc[df_dd.treatment.isnull(), "treatment"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06c_validate_safety_embed.py, line 352)
  → df_dd.loc[df_dd.treatment == 0, "FE"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06c_validate_safety_embed.py, line 371)
  → df_dd.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06c_validate_safety_embed.py, line 377)
  → df_dd.loc[df_dd["safety_prop"] > 0, "safety_prop"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06c_validate_safety_embed.py, line 397)
  → baseline_mean = df_dd.loc[mask, "safety_prop"].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06c_validate_safety_embed.py, line 398)
  → baseline_std = df_dd.loc[mask, "safety_prop"].std()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (06c_validate_safety_embed.py, line 517)
  → title_abstract.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (07_firm_heterogeneity.py, line 354)
  → conditioning_sizes = notnull.loc[cond_mask, "firm_size"].values

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (07_firm_heterogeneity.py, line 397)
  → df_safety_dd.loc[df_safety_dd.treatment.isnull(), "treatment"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (07_firm_heterogeneity.py, line 749)
  → df_diff.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (07_firm_heterogeneity.py, line 766)
  → df_safety_dda.loc[df_safety_dda.treatment == 0, "year_reclassified"] = np.nan

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (07_firm_heterogeneity.py, line 909)
  → test_main.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 293)
  → df.loc[df[yr_col].notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 392)
  → df_est.loc[pos, "SE"] = (

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 393)
  → df_est.loc[pos, "Estimate"] - df_est.loc[pos, "lower_CI"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 398)
  → df_est.loc[neg, "SE"] = np.abs(

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 399)
  → df_est.loc[neg, "Estimate"] - df_est.loc[neg, "upper_CI"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 404)
  → df_est.loc[df_est["tstat"] > 1.6449, "stars"] = "+"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 405)
  → df_est.loc[df_est["tstat"] > 1.9600, "stars"] = "*"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 406)
  → df_est.loc[df_est["tstat"] > 2.5758, "stars"] = "**"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10_table_formatting.py, line 407)
  → df_est.loc[df_est["tstat"] > 3.2905, "stars"] = "***"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (10c_generate_appendix_tables.py, line 430)
  → fda_all = set(inv32.loc[inv32["FDA_own_accord"] == 1, "PRODUCTCODE"].astype(str))

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11a_product_variety.py, line 373)
  → return counts.loc[counts["diff"].idxmin(), "PRODUCTCODE"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11a_product_variety.py, line 454)
  → temp.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11a_product_variety.py, line 498)
  → est_df.loc[i, "SE"] = (row["upper_cb"] - row["Effect"]) / 1.96

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11a_product_variety.py, line 500)
  → est_df.loc[i, "SE"] = (row["Effect"] - row["lower_cb"]) / 1.96

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11a_product_variety.py, line 596)
  → temp.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11a_product_variety.py, line 640)
  → est_df.loc[i, "SE"] = (row["upper_cb"] - row["Effect"]) / 1.96

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11a_product_variety.py, line 642)
  → est_df.loc[i, "SE"] = (row["Effect"] - row["lower_cb"]) / 1.96

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 427)
  → dfgrouped_merged.loc[dfgrouped_merged.treated != 1, "treated"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 438)
  → final.loc[final.year >= final.year_treated, "post"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 444)
  → final.loc[final.treatment == 0, "ET"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 483)
  → adv_2015.loc[adv_2015.PRODUCTCODE.isin(set(fda_deregs["PRODUCTCODE"].values)), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 569)
  → final_adv.loc[final_adv.year >= final_adv.year_treated, "post"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 575)
  → final_adv.loc[final_adv.treatment == 0, "ET"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 623)
  → dfgrouped_merged3.loc[dfgrouped_merged3.treated == 0, "year_reclassified"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 632)
  → dfgrouped_merged3.loc[dfgrouped_merged3.treatment == 0, "ET"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11b_recall_analysis.py, line 645)
  → dfgrouped_merged3.loc[dfgrouped_merged3.PRODUCTCODE == PC, "FE"] = i

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11c_liability.py, line 184)
  → agg["count"] = agg["count"].values / tort_series.loc[agg.year.values].values

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 334)
  → full.loc[mask, "v_serious_rate"] = (

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 335)
  → full.loc[mask, "v_serious_event"] / full.loc[mask, "event_count"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 338)
  → full.loc[mask, "H_rate"] = full.loc[mask, "H"] / full.loc[mask, "event_count"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 340)
  → full.loc[mask, "D_rate"] = full.loc[mask, "D"] / full.loc[mask, "event_count"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 342)
  → full.loc[mask, "L_rate"] = full.loc[mask, "L"] / full.loc[mask, "event_count"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 424)
  → synth.loc[synth.year >= synth.year_reclassified, "posttreat"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 437)
  → synth.loc[synth.PRODUCTCODE == matched, "FE"] = row["FE"].values[0]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 440)
  → synth.loc[synth.PRODUCTCODE == matched, "year_reclassified"] = ctrl_yr.values[0]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 527)
  → full.loc[:, ["event_count", "L", "H", "S", "R", "D"]] = (

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 722)
  → synth.loc[synth.year >= synth.year_reclassified, "posttreat"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 727)
  → synth.loc[mask, "v_serious_rate"] = (

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 728)
  → synth.loc[mask, "v_serious_event"] / synth.loc[mask, "event_count"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 760)
  → synth.loc[synth.PRODUCTCODE == matched, "FE"] = row["FE"].values[0]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 763)
  → synth.loc[synth.PRODUCTCODE == matched, "year_reclassified"] = ctrl_yr.values[0]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11d_reg_design.py, line 796)
  → df.loc[df.PART_DESCRIPTION == old, "PART_DESCRIPTION"] = new

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (11e_new_entry_2015.py, line 243)
  → all_pats.loc[all_pats.PRODUCTCODE.isin(fda_deregs.PRODUCTCODE), "treated"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (12b_gpt_price_links_generation.py, line 422)
  → df.loc[mask, "hcpcs_cpt"] = edits["hcpcs"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (12b_gpt_price_links_generation.py, line 424)
  → df.loc[mask, "procedure_desc"] = edits["procedure_desc"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 156)
  → firms_temp.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 187)
  → baseline_mean = firms_temp.loc[pre_mask, outcome].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 188)
  → baseline_sd = firms_temp.loc[pre_mask, outcome].std()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 197)
  → baseline_mean = firms_temp.loc[pre_mask2, outcome].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 200)
  → baseline_mean = firms_temp.loc[pre_mask3, outcome].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 481)
  → df_results.loc[df_results["tstat"] > ninety, "stars"] = "+"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 482)
  → df_results.loc[df_results["tstat"] > ninety5, "stars"] = "*"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 483)
  → df_results.loc[df_results["tstat"] > ninety9, "stars"] = "**"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (13_restricted_samples.py, line 484)
  → df_results.loc[df_results["tstat"] > ninety9point9, "stars"] = "***"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 172)
  → firms_temp.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 187)
  → firms_temp.loc[firms_temp[outcome] < 0, outcome] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 221)
  → baseline_mean = firms_orig.loc[pre_mask, outcome].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 222)
  → baseline_sd = firms_orig.loc[pre_mask, outcome].std()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 230)
  → baseline_mean = firms_temp.loc[pre_mask, outcome].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 231)
  → baseline_sd = firms_temp.loc[pre_mask, outcome].std()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 240)
  → baseline_mean = firms_temp.loc[pre_mask2, outcome].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 243)
  → baseline_mean = firms_temp.loc[pre_mask3, outcome].mean()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 484)
  → df_results.loc[df_results["tstat"] > ninety, "stars"] = "+"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 485)
  → df_results.loc[df_results["tstat"] > ninety5, "stars"] = "*"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 486)
  → df_results.loc[df_results["tstat"] > ninety9, "stars"] = "**"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (14_breakthrough_patents.py, line 487)
  → df_results.loc[df_results["tstat"] > ninety9point9, "stars"] = "***"

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 186)
  → d = float(adv.loc[adv.outcome == "D", "Estimate"].iloc[0])   # ~ -0.426

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 246)
  → n_cls2 = int(sn.loc[sn.DEVICECLASS == "2", "PRODUCTCODE"].nunique())

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 342)
  → eff = float(df.loc[h, "Effect"])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 343)
  → tm = float(df.loc[h, "treated_mean"])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 514)
  → df.loc[df[yr].notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 519)
  → pre = df.loc[mask]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 559)
  → return float(mp32.loc[mp32["outcome"] == o, "Estimate"].iloc[0])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 590)
  → return float(mp21.loc[mp21["outcome"] == o, "Estimate"].iloc[0])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 620)
  → return float(mc32.loc[mc32["outcome"] == o, "Estimate"].iloc[0])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (15_intext_derived_numbers.py, line 640)
  → v = _pct_more(float(mc21.loc[mc21["outcome"] == "unique_firms", "Estimate"].iloc[0]), pm21["unique_firms"])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (16_total_patent_value_did.py, line 73)
  → pat = pat.loc[:, ~pat.columns.duplicated()]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (16_total_patent_value_did.py, line 106)
  → firms.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 310)
  → pmas.loc[pmas.STATE.notnull(), 'COUNTRY_CODE'] = 'US'

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 618)
  → main_outcomes.loc[main_outcomes.FDA_own_accord.isnull(),

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 664)
  → patents_xi.loc[patents_xi.year.isnull(), 'year'] = \

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 665)
  → patents_xi.loc[patents_xi.year.isnull(), 'issue_date'].str.split(

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 821)
  → merged_master.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 906)
  → main_outcomes.loc[main_outcomes['year'] > 1991, cols_present] = (

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 907)
  → main_outcomes.loc[main_outcomes['year'] > 1991, cols_present].fillna(0))

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1046)
  → main_outcomes.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1061)
  → main_outcomes.loc[(main_outcomes.controls == 1) |

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1069)
  → main_outcomes.loc[main_outcomes.total_pat_sum > 0,

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1081)
  → main_outcomes.loc[(main_outcomes.controls == 1) |

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1089)
  → main_outcomes.loc[main_outcomes.total_pat_sum > 0,

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1130)
  → foi.loc[foi.Implant_Flag == 'Y', 'implant'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1132)
  → foi.loc[foi.Life_Sustain_support_flag == 'Y', 'life_sustaining'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1229)
  → final.loc[final.PRODUCTCODE.isin(matched_pairs.treated), 'treatment'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1236)
  → final.loc[(final.treatment == 1) &

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1263)
  → final_3_2_matched.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1283)
  → final_3_2_matched.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1344)
  → synth_number2.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1365)
  → synth_2_1_combined_1996.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1369)
  → synth_2_1_combined_1996.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1493)
  → total_spillovers.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1578)
  → final_spillovers.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1590)
  → final_spillovers.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1627)
  → foi.loc[foi.Implant_Flag == 'Y', 'implant'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1629)
  → foi.loc[foi.Life_Sustain_support_flag == 'Y', 'life_sustaining'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1723)
  → final.loc[final.PRODUCTCODE.isin(

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_01_main_panels.py, line 1733)
  → final.loc[(final.treatment == 1) &

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_02_price_matching.py, line 81)
  → exploded.loc[exploded.PRODUCTCODE.isin(treated_pcs), reclass_col] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_02_price_matching.py, line 101)
  → fda_to_hcpcs.loc[mask, 'HCPCS'] = corrections['HCPCS']

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_02_price_matching.py, line 103)
  → fda_to_hcpcs.loc[mask, 'procedure_desc'] = corrections['procedure_desc']

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_02_price_matching.py, line 177)
  → full.loc[full[col] == -99999999999999.0, col] = np.nan

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_02_price_matching.py, line 182)
  → full.loc[full.year_reclassified.notnull(), 'treatment'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_02_price_matching.py, line 211)
  → etpcfull.loc[(etpcfull.year >= etpcfull.year_reclassified) &

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 95)
  → row.loc[row['cluster id'].duplicated(), 'head'] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 192)
  → AD_data2.loc[AD_data2.confidence < .4, "cluster id"] = np.nan

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 216)
  → new_df.loc[mask, 'cluster id app'] = new_df.loc[mask, 'cluster id app_from_ad2']

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 229)
  → new_df.loc[new_df.APPLICANT == '', 'APPLICANT'] = np.nan

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 252)
  → onlyPMAfirms.loc[onlyPMAfirms.Days_take_approve_pma.isnull(), 'Days_take_approve'] = \

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 253)
  → onlyPMAfirms.loc[onlyPMAfirms.Days_take_approve_pma.isnull(), 'Days_take_approve_510k']

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 254)
  → onlyPMAfirms.loc[onlyPMAfirms.Days_take_approve_510k.isnull(), 'Days_take_approve'] = \

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 255)
  → onlyPMAfirms.loc[onlyPMAfirms.Days_take_approve_510k.isnull(), 'Days_take_approve_pma']

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_03_lbd.py, line 266)
  → onlyPMAfirms_cumsum.loc[onlyPMAfirms_cumsum['cumsum_time_t1'] == 0, 'cumsum_time_t1'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_04_parquets.py, line 59)
  → treated_PCs = np.unique(df.loc[df.treatment == 1, 'PRODUCTCODE'])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_04_parquets.py, line 63)
  → df.loc[df.treatment == 0, 'FE'] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_04_parquets.py, line 68)
  → controls = df.loc[df.treatment == 0].copy()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_04_parquets.py, line 114)
  → df_2_1.loc[df_2_1.year_reclassified.notnull(), 'treatment'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 128)
  → chunk = chunk.loc[~chunk["MDR_REPORT_KEY"].isin(seen)].copy()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 346)
  → df.loc[mask, 'permno'] = np.nan

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 347)
  → df.loc[mask, 'stock_name'] = np.nan

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 348)
  → df.loc[mask, 'manually_encoded'] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 351)
  → df.loc[mask, 'permno'] = corr['permno']

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 352)
  → df.loc[mask, 'manually_encoded'] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 354)
  → df.loc[mask, 'manual_stock'] = corr['manual_stock']

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 355)
  → df.loc[mask, 'stock_name'] = corr['stock_name']

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_07_adverse_permno.py, line 600)
  → merged_master.loc[merged_master['cluster_id_combined'].isna(),

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (match_mahal.py, line 101)
  → df.loc[df.treatment == 0, "FDA_own_accord_3_2"] = 0

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (match_mahal.py, line 112)
  → df.loc[df.year_reclassified.notnull(), "treatment"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (match_mahal.py, line 120)
  → df.loc[(df.treatment == 1) & (df.year >= df.year_reclassified), "posttreat"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (table_format.py, line 56)
  → se.loc[pos] = (df.loc[pos, "Estimate"] - df.loc[pos, "lower_CI"]) / 1.96

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (table_format.py, line 61)
  → se.loc[neg] = np.abs(df.loc[neg, "Estimate"] - df.loc[neg, "upper_CI"]) / 1.96

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (table_format.py, line 62)
  → se.loc[zero] = (df.loc[zero, "upper_CI"] - df.loc[zero, "lower_CI"]) / (2 * 1.96)

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 117)
  → "2_1": set(design.loc[design["year_reclassified_2_1"].notna(), "PRODUCTCODE"]),

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 118)
  → "3_2": set(design.loc[design["year_reclassified_3_2"].notna(), "PRODUCTCODE"]),

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 184)
  → pre_supported = set(effective_in_panel.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 196)
  → controls = set(design.loc[design["controls"].eq(1), "PRODUCTCODE"])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 211)
  → eligible_recall_treated = set(panel.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 220)
  → required_recall_treated - set(effective_in_panel.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 258)
  → no_reclass = set(synth.loc[synth.reclass_years == "None", "PRODUCTCODE"])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 267)
  → good_codes = set(synth.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 276)
  → treated_design = set(public_panel.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 280)
  → candidate_controls = set(public_panel.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 285)
  → ]) & set(design.loc[design["controls"].eq(1), "PRODUCTCODE"])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (preflight_from_raw.py, line 287)
  → treated_supported = set(effective_in_panel.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00a_extract_parameters.py, line 284)
  → sub = df.loc[idx]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00b_pc_effects.py, line 124)
  → good_codes = set(synth.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00b_pc_effects.py, line 128)
  → has_window = df.loc[(df["year"] > 1991) & (df["year"] <= 1996)].groupby(

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00b_pc_effects.py, line 162)
  → pc.loc[treated_21 & pc["support_2_1"], "analysis_support_year"] = \

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00b_pc_effects.py, line 163)
  → pc.loc[treated_21 & pc["support_2_1"], "pre_event_support_year"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00b_pc_effects.py, line 168)
  → pc.loc[treated_32, "analysis_support_year"] = \

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00b_pc_effects.py, line 169)
  → pc.loc[treated_32, "pre_event_support_year"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00c_synthetic_marketscan.py, line 232)
  → eligible |= set(t.loc[f | is_c, "PRODUCTCODE"])

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00c_synthetic_marketscan.py, line 244)
  → pcs = sorted(set(t.loc[f | is_c, "PRODUCTCODE"]))

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00c_synthetic_marketscan.py, line 448)
  → treated = theta.loc[theta[flag].astype(bool), "PRODUCTCODE"].astype(str).tolist()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00c_synthetic_marketscan.py, line 449)
  → controls = theta.loc[theta["is_control"].astype(bool), "PRODUCTCODE"].astype(str).tolist()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00c_synthetic_marketscan.py, line 454)
  → treated = theta.loc[theta[flag].astype(bool), "PRODUCTCODE"].astype(str).tolist()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00c_synthetic_marketscan.py, line 455)
  → controls = theta.loc[theta["is_control"].astype(bool), "PRODUCTCODE"].astype(str).tolist()

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00c_synthetic_marketscan.py, line 460)
  → y = lookup.loc[pc, year_col]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00d_synthetic_dimensions_wrds.py, line 278)
  → df.loc[(df["controls"] == 1) | (df["patent_sum_2_1"] > 0), "use_2_1_treat"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00d_synthetic_dimensions_wrds.py, line 283)
  → df.loc[(df["controls"] == 1) | (df["patent_sum_3_2"] > 0), "use_3_2_treat"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00d_synthetic_dimensions_wrds.py, line 286)
  → df.loc[df["total_pat_sum"] > 0, "one_pat_atleast"] = 1

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00e_synthetic_patents.py, line 325)
  → allowed = theta.loc[theta[f"is_reclass_{event}"].astype(bool), "PRODUCTCODE"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00i_synthetic_maude_linkage_inputs.py, line 158)
  → names.loc[missing] = (

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (gen_00i_synthetic_maude_linkage_inputs.py, line 160)
  → + chunk.loc[missing, "MDR_REPORT_KEY"].astype(str)

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (materialize_from_universe.py, line 109)
  → df.loc[mask, col] = np.nan

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (synthetic_universe.py, line 199)
  → treated = design.loc[design[ycol].notna(), "PRODUCTCODE"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (synthetic_universe.py, line 200)
  → pre = support.loc[support["filing_year"] < support[ycol], "PRODUCTCODE"]

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (universe_backend.py, line 132)
  → treated = design.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (universe_backend.py, line 139)
  → supported = set(merged.loc[

[ADVISORY] `.query(` or `.loc[` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (universe_backend.py, line 279)
  → row = design.loc[code]

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (04_event_studies.py, line 546)
  → df = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (04_event_studies.py, line 619)
  → df = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06a_safety_analysis.py, line 124)
  → df_safety_keep = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06a_safety_analysis.py, line 138)
  → df_safety_keep_vars = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06a_safety_analysis.py, line 146)
  → df_safety_keep_w_permno = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06a_safety_analysis.py, line 178)
  → df_dd = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06b_validate_safety.py, line 231)
  → df_safety_keep = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06b_validate_safety.py, line 243)
  → df_safety_keep_vars = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06b_validate_safety.py, line 251)
  → df_safety_keep_w_permno = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06b_validate_safety.py, line 277)
  → df_dd = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06c_validate_safety_embed.py, line 288)
  → df_safety_keep = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06c_validate_safety_embed.py, line 300)
  → df_safety_keep_vars = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06c_validate_safety_embed.py, line 308)
  → df_safety_keep_w_permno = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (06c_validate_safety_embed.py, line 334)
  → df_dd = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (07_firm_heterogeneity.py, line 299)
  → df_safety_keep = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (07_firm_heterogeneity.py, line 320)
  → df_safety_keep_w_permno = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (07_firm_heterogeneity.py, line 392)
  → df_safety_dd = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (07_firm_heterogeneity.py, line 606)
  → df_safety_dda = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (07_firm_heterogeneity.py, line 888)
  → test_main = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (08_lbd_simulation.py, line 185)
  → test_main = pd.merge(test_main, temp,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 204)
  → all_pats = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 220)
  → all_pats_cites = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 314)
  → lbd = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 333)
  → w_fsize = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 402)
  → concat_merge = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 668)
  → concat_merge = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 715)
  → fe_w_class = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 736)
  → fe_dt = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 769)
  → ae_merge = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 854)
  → pats_w_class = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 861)
  → pats_cites_w_class = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (09_summary_stats.py, line 868)
  → pats_xi_w_class = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11a_product_variety.py, line 405)
  → merged = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11a_product_variety.py, line 420)
  → merged = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11a_product_variety.py, line 728)
  → all_pats = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11b_recall_analysis.py, line 424)
  → dfgrouped_merged = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11b_recall_analysis.py, line 494)
  → adv_2015 = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11b_recall_analysis.py, line 591)
  → dfgrouped_merged2 = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11b_recall_analysis.py, line 753)
  → dfgrouped_intuitive = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 289)
  → full = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 309)
  → full = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 347)
  → full = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 428)
  → synth = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 751)
  → synth = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 768)
  → synth = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 779)
  → synth = pd.merge(synth, inv_years[["PRODUCTCODE", "yr_invent"]].drop_duplicates("PRODUCTCODE"),

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 1250)
  → df_done_3_2 = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 1319)
  → df_done_2_1 = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 1332)
  → df_done_2_1 = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 1340)
  → df_done_2_1 = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 1418)
  → inv_pma = pd.merge(inv_all, synth_number[["PRODUCTCODE", "SUBMISSION_TYPE_ID"]],

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 1465)
  → inv_510k = pd.merge(inv_all, synth_number[["PRODUCTCODE", "SUBMISSION_TYPE_ID"]],

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11d_reg_design.py, line 1757)
  → df_done = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11e_new_entry_2015.py, line 205)
  → df_2_1_lt = df_2_1_lt.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (11e_new_entry_2015.py, line 213)
  → df_2_1_lt = df_2_1_lt.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (14_breakthrough_patents.py, line 115)
  → all_pats = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (15_intext_derived_numbers.py, line 256)
  → o2 = fs[fs.PRODUCTCODE.isin(inv510["PRODUCTCODE"])].merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (15_intext_derived_numbers.py, line 287)
  → o3 = fs[fs.PRODUCTCODE.isin(invPMA["PRODUCTCODE"])].merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_00b_marketscan_extraction.py, line 145)
  → outpatient_merged_enrol = pd.merge(outpatient_combined, \

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 428)
  → main_outcomes = pd.merge(synth_number, unique_dev,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 430)
  → main_outcomes = pd.merge(main_outcomes, firm_entrant,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 432)
  → main_outcomes = pd.merge(main_outcomes, total_firm_entrant,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 513)
  → all_pats_wGRID = pd.merge(all_pats_wGRID, GRID[['GRID', 'type']],

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 609)
  → main_outcomes = pd.merge(main_outcomes, all_pats_grouped,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 611)
  → main_outcomes = pd.merge(main_outcomes, pat_counts_newfirm_PC,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 613)
  → main_outcomes = pd.merge(main_outcomes, pat_counts_newfirm,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 615)
  → main_outcomes = pd.merge(main_outcomes, all_pats_grouped_cpc,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 647)
  → main_outcomes = pd.merge(main_outcomes, applicantonlycites,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 649)
  → main_outcomes = pd.merge(main_outcomes, applicantonlycites_outside,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 694)
  → all_pats_wGRID_forxi = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 713)
  → all_pats_wGRID_forxi_test = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 731)
  → main_outcomes = pd.merge(main_outcomes, all_pats_wGRID_grouped,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 811)
  → merged_master = pd.merge(merged_master, patients,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 813)
  → merged_master = pd.merge(merged_master, device_problems,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 893)
  → main_outcomes = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 988)
  → main_outcomes = pd.merge(main_outcomes, df_3_2,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 1014)
  → main_outcomes = pd.merge(main_outcomes, synth_2_1,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 1232)
  → final = pd.merge(final, matched_pairs[['PRODUCTCODE', 'year_reclassified']],

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 1275)
  → final_3_2_matched = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 1583)
  → final_spillovers = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 1618)
  → spillover_treated = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_01_main_panels.py, line 1727)
  → final = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_02_price_matching.py, line 147)
  → claims = pd.merge(rogers_claims_extract, fda_to_hcpcs_mapping,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_02_price_matching.py, line 302)
  → fda_3_2 = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_02_price_matching.py, line 308)
  → fda_2_1 = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_03_lbd.py, line 127)
  → Applicant_Device_data_df = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_03_lbd.py, line 131)
  → Applicant_Device_data_df = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_03_lbd.py, line 170)
  → AD_data1 = pd.merge(AD_data1, dec_lookup,

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_03b_lbd_clusters.py, line 115)
  → ad_df = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_03b_lbd_clusters.py, line 119)
  → ad_df = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_05_adverse_fsize.py, line 170)
  → merged = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_05_adverse_fsize.py, line 172)
  → merged = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_07_adverse_permno.py, line 548)
  → df_dropped_w_deduped = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_07_adverse_permno.py, line 554)
  → df_all = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_07_adverse_permno.py, line 634)
  → merged_all = pd.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (match_mahal.py, line 282)
  → treated_final = final[final["treatment"] == 1].merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (match_mahal.py, line 289)
  → control_final = final[final["treatment"] == 0].merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (maturity_denom.py, line 35)
  → o2 = fs[fs.PRODUCTCODE.isin(inv510["PRODUCTCODE"])].merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (maturity_sensitivity.py, line 30)
  → o2 = fs[fs.PRODUCTCODE.isin(iv["PRODUCTCODE"])].merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (preflight_from_raw.py, line 173)
  → effective_in_panel = effective.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (gen_00c_synthetic_marketscan.py, line 380)
  → remaining = frame.merge(

[ADVISORY] `pd.merge()` or `.merge()` called without explicit `how=` argument — defaults to inner join, which may silently drop rows. (universe_backend.py, line 138)
  → merged = support_rows[["PRODUCTCODE", "filing_year"]].merge(treated, on="PRODUCTCODE")

### R

[ADVISORY] `filter(` call not preceded by a comment within 2 lines — consider adding a comment explaining the criterion. (did_imputation_topython.R, line 25)
  → filter(rel_year >= -20 & rel_year <= 30) %>%

### Unknown

[CRITICAL] Hardcoded absolute path detected — the package will not run on another machine. (run_fromraw_analysis_only.sh, line 46)
  → for token in ("/N/slate", "/geode2", "/Users/parkerrogers", "replication_package_v9_source",

