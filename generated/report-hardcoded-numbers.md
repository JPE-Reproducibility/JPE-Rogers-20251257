## Potentially Hardcoded Numeric Constants


We found the following set of hard coded numbers. This may be completely legitimate (parameter input, thresholds for computations, etc), and is hence only for information.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/conley_taber.py**

- Line 132, : i025 = int(np.floor(0.025 * numbsim))
- Line 133, : i975 = int(np.ceil(0.975 * numbsim))
- Line 480, : # Rounding to 3dp distorts v_serious_rate estimates (~0.001-0.01 scale).

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/r_scripts/preprocess.R**

- Line 7, : # cell, swings the point estimate (1.961 <-> 3.516) and can SIGABRT the II->I estimation. Single-

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/config.py**

- Line 54, : CPI_DEFLATOR_2019 = 0.3891444146542998
- Line 284, : 0.001: "***",

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Table_D12_petitioned_vs_fda.tex**

- Line 9, : Patenting Rate & 0.136 & 0.008 \\
- Line 10, : & (0.403) & (0.266) \\
- Line 12, : Device Approval Rate & 3.353** & 1.882*** \\
- Line 13, : & (1.055) & (0.462) \\
- Line 15, : Citations-Per-Patent & 0.006 & -0.032 \\
- Line 16, : & (0.118) & (0.118) \\
- Line 18, : Average Patent Value & 0.804 & 1.948 \\
- Line 19, : & (0.795) & (1.357) \\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/00_generate_data/gen_01_main_panels.py**

- Line 1458, : # adjacent string literals below ('888.307' '880.621') are concatenated by Python into a
- Line 1459, : # single entry, so regulation numbers 888.307 and 880.621 are not in the list; the list is
- Line 1462, : '870.52', '870.521', '870.41', '870.36', '870.3605', '890.5525',
- Line 1463, : '888.307' '880.621', '884.534', '882.594', '882.58', '892.207']

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD12_SafetyRobustness.tex**

- Line 3, : \hspace{6mm}Pr of any Safety Mention & Embedding Distance & 0.018 & 0.017+ \\
- Line 4, : &  & (0.133) & (0.009) \\
- Line 6, : \hspace{6mm}Pr of any Safety Mention & ``Safety'' Only & 0.022 & 0.014* \\
- Line 7, : &  & (0.148) & (0.007) \\
- Line 14, : \hspace{6mm}Pr of any Safety Mention & Embedding Distance & 0.000 & -0.059* \\
- Line 15, : &  & (0.000) & (0.023) \\
- Line 17, : \hspace{6mm}Pr of any Safety Mention & ``Safety'' Only & 0.000 & -0.004 \\
- Line 18, : &  & (0.000) & (0.014) \\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10c_generate_appendix_tables.py**

- Line 33, : HOSP_M = 0.022      # average inpatient hospitalization, $M ($22,000)
- Line 286, : "0.01, and 0.001 levels, respectively.\n\\end{footnotesize} }\n\\label{tab:Utilization}\n"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/14_breakthrough_patents.py**

- Line 480, : ninety5 = scipy.stats.norm.ppf(0.975)
- Line 481, : ninety9 = scipy.stats.norm.ppf(0.995)
- Line 482, : ninety9point9 = scipy.stats.norm.ppf(0.9995)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/lda_seed_runs/analyze_selection.py**

- Line 76, : print("0.0010 can still fall inside the 1e-3 tolerance in the unrounded values. That")
- Line 78, : print("apparent arg-max of 20 at 0.5030: the deposited seed sits on the tie-break")

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11d_reg_design.py**

- Line 905, : return "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ("+" if p < 0.10 else "")))
- Line 1674, : III->II safety:  β_age = -0.0170, s.e. 0.008, p=0.060
- Line 1675, : II->I  safety:  β_age = -0.0015, s.e. 0.001, p=0.218
- Line 1676, : III->II innov:   β_age = -0.0396, s.e. 0.013, p=0.008
- Line 1677, : II->I  innov:   β_age =  0.0002, s.e. 0.001, p=0.876
- Line 1778, : "3_2_v_serious_est": {"slope": -0.0170, "se": 0.008, "pvalue": 0.060},
- Line 1779, : "3_2_patent_est":    {"slope": -0.0396, "se": 0.013, "pvalue": 0.008},
- Line 1780, : "2_1_v_serious_est": {"slope": -0.0015, "se": 0.001, "pvalue": 0.218},
- Line 1781, : "2_1_patent_est":    {"slope":  0.0002, "se": 0.001, "pvalue": 0.876},
- Line 1794, : match_slope = abs(got["slope"] - ms["slope"]) < 0.005 if np.isfinite(got["slope"]) else False
- Line 1795, : match_se = abs(got["se"] - ms["se"]) < 0.005 if np.isfinite(got["se"]) else False

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD11a_DeviceExperience_3_2.tex**

- Line 10, : Device Experience (years) & -0.0051* & -0.0203 \\
- Line 11, : & (0.0019) & (0.0249) \\
- Line 12, : Intercept & 0.2379* & 1.2131 \\
- Line 13, : & (0.1075) & (1.3833) \\
- Line 14, : Baseline Serious Adverse Events & -0.0005 & 0.0312 \\
- Line 15, : & (0.0040) & (0.0521) \\
- Line 16, : FDA's Own Accord & 0.0128 & -0.2314 \\
- Line 17, : & (0.0401) & (0.5365) \\
- Line 18, : Orthopedic Devices & 0.0736 & 0.7868 \\
- Line 19, : & (0.0952) & (1.2320) \\
- Line 20, : Other Devices & -0.1523+ & -0.3300 \\
- Line 21, : & (0.0761) & (0.9822) \\
- Line 22, : Plastic Surgery, Gastroenterology-Urology Devices & 0.0419 & -0.6571 \\
- Line 23, : & (0.0935) & (1.2020) \\
- Line 24, : Baseline Patent Count & --- & -0.2333*** \\
- Line 25, : & --- & (0.0325) \\
- Line 34, : \begin{footnotesize}Note: The regression relates device-level DiD estimates for (1) serious adverse events and (2) patenting activity to each device type's market age (FDA years of experience) and other covariates, including baseline patenting rates. \textquotedblleft---\textquotedblright\ indicates variables excluded from a given specification. Due to limited data, fixed effects are included only for higher-risk device categories (each with $\geq$ 2 observations); cardiovascular devices are the omitted group. To increase power, FDA-initiated reclassifications (own accord = 0) are included with a corresponding fixed effect. +, *, **, *** denote significance at 0.10, 0.05, 0.01, 0.001 levels.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Table_D11_reg_design.tex**

- Line 11, : constant & 0.2379* & 1.2131 & 0.0163 & 0.3395 \\
- Line 12, : & (0.108) & (1.383) & (0.019) & (0.305) \\
- Line 14, : exp\_years & -0.0051* & -0.0203 & -0.0003+ & -0.0003 \\
- Line 15, : & (0.002) & (0.025) & (0.000) & (0.002) \\
- Line 17, : v\_serious\_event & -0.0005 & 0.0312 & -0.0093 & 0.0982 \\
- Line 18, : & (0.004) & (0.052) & (0.007) & (0.112) \\
- Line 20, : FDA\_own\_accord & 0.0128 & -0.2314 &  &  \\
- Line 21, : & (0.040) & (0.537) &  &  \\
- Line 23, : DPM &  &  & 0.0277 & -0.6393 \\
- Line 24, : &  &  & (0.044) & (0.663) \\
- Line 26, : patents\_allpats &  & -0.2333*** &  & -0.1348*** \\
- Line 27, : &  & (0.032) &  & (0.017) \\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10b_format_remaining_tables.py**

- Line 32, : if pval < 0.001:
- Line 49, : if tstat > scipy.stats.norm.ppf(0.9995):
- Line 51, : if tstat > scipy.stats.norm.ppf(0.995):
- Line 53, : if tstat > scipy.stats.norm.ppf(0.975):
- Line 267, : "at 0.10, 0.05, 0.01, 0.001 levels."
- Line 297, : "+, *, **, *** denote significance at 0.10, 0.05, 0.01, 0.001 levels."

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/run_all.py**

- Line 825, : # MarketComposition, excluding-zero, LaterTreat, firm_expansion_patents: 1.961 <-> 3.516) and

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/13_restricted_samples.py**

- Line 477, : ninety5 = scipy.stats.norm.ppf(0.975)
- Line 478, : ninety9 = scipy.stats.norm.ppf(0.995)
- Line 479, : ninety9point9 = scipy.stats.norm.ppf(0.9995)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Table_D12_petitioned_vs_fda.tex**

- Line 9, : Patenting Rate & 12.152* & 26.140* \\
- Line 10, : & (5.209) & (13.172) \\
- Line 12, : Device Approval Rate & 3.293** & 1.706** \\
- Line 13, : & (1.069) & (0.643) \\
- Line 15, : Citations-Per-Patent & 13.990+ & 23.913 \\
- Line 16, : & (8.350) & (17.055) \\
- Line 18, : Average Patent Value & 11.964 & 8.945 \\
- Line 19, : & (7.357) & (6.656) \\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/09_summary_stats.py**

- Line 978, : if abs_x < 0.001:

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD11a_DeviceExperience_3_2.tex**

- Line 10, : Device Experience (years) & -0.0051* & -1.5231* \\
- Line 11, : & (0.0019) & (0.7125) \\
- Line 12, : Intercept & 0.2379* & 82.2241+ \\
- Line 13, : & (0.1075) & (40.7092) \\
- Line 14, : Baseline Serious Adverse Events & -0.0005 & -1.7597 \\
- Line 15, : & (0.0040) & (1.4963) \\
- Line 16, : FDA's Own Accord & 0.0128 & -21.9656 \\
- Line 17, : & (0.0401) & (15.2212) \\
- Line 18, : Orthopedic Devices & 0.0736 & 5.5511 \\
- Line 19, : & (0.0952) & (35.3210) \\
- Line 20, : Other Devices & -0.1523+ & -52.1829+ \\
- Line 21, : & (0.0761) & (27.9667) \\
- Line 22, : Plastic Surgery, Gastroenterology-Urology Devices & 0.0419 & -24.7850 \\
- Line 23, : & (0.0935) & (34.7247) \\
- Line 24, : Baseline Patent Count & --- & 2.4315*** \\
- Line 25, : & --- & (0.5018) \\
- Line 34, : \begin{footnotesize}Note: The regression relates device-level DiD estimates for (1) serious adverse events and (2) patenting activity to each device type's market age (FDA years of experience) and other covariates, including baseline patenting rates. \textquotedblleft---\textquotedblright\ indicates variables excluded from a given specification. Due to limited data, fixed effects are included only for higher-risk device categories (each with $\geq$ 2 observations); cardiovascular devices are the omitted group. To increase power, FDA-initiated reclassifications (own accord = 0) are included with a corresponding fixed effect. +, *, **, *** denote significance at 0.10, 0.05, 0.01, 0.001 levels.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12_invention_year_generation.py**

- Line 87, : #     corr(yr_invent_or_comm_avail, years) on THIS file = 0.7574 (p=1.2e-05, n=25) -- reproduced + gated by

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/universe_backend.py**

- Line 43, : "patents": {"cardinality": 120_000, "size_family": {"kind": "geometric", "p": 0.999}},
- Line 46, : "adverse_firms": {"cardinality": 4_600, "size_family": {"kind": "nbinom", "r": 1.5, "p": 0.001}},
- Line 345, : {"kind": "nbinom", "r": 1.5, "p": 0.001}, salt="firm|adverse")

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Table_1_summary_stats.tex**

- Line 14, : \textit{A. PMA/510(k) Submissions} & 0.169M & - & - & -\\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/JPE_submission_v8.tex**

- Line 512, : \textit{Findings.} More mature device types become safer post-reclassification. Regressing device-level DiD effects on market age yields a negative age slope for both transitions (Appendix Tables~\ref{tab:impacts_vs_exp_3_2} and \ref{tab:impacts_vs_exp_2_1}). The linear fits cross zero at roughly 30 years (III to II) and roughly 60 years (II to I), beyond which the fitted post-reclassification change in the serious-event measure is negative conditional on covariates (Appendix Figure~\ref{fig:Impact_by_experience}). These crossings should be read as empirical benchmarks rather than rigid decision rules, especially because the II-to-I age slope is estimated imprecisely.\footnote{Using $\log(\text{serious events}+1)$ yields a similar maturity gradient. For Class~III to II, the age slope is negative and marginally significant ($\hat\beta_{\text{age}}=-0.0170$, s.e.\ $0.008$, $p=0.060$); for Class~II to I it is negative but imprecise ($\hat\beta_{\text{age}}=-0.0015$, s.e.\ $0.001$, $p=0.218$). Innovation shows the following pattern: the age slope is $\hat\beta_{\text{age}}=-0.0396$ (s.e.\ $0.013$, $p=0.008$) for Class~III to II and is near zero for Class~II to I ($\hat\beta_{\text{age}}=0.0002$, s.e.\ $0.001$, $p=0.876$).} Innovation effects are largest at lower ages, with steeper negative slopes in the patent-impact regressions for Class~III to II, but remain economically meaningful well beyond the safety thresholds. I measure market age in calendar time. Because safety information likely accumulates with use, cumulative market volume (utilization) is a natural alternative metric; the calendar-time thresholds are therefore best read as benchmarks for device types of roughly average utilization, with higher-volume (lower-volume) types plausibly reaching the safety threshold sooner (later).
- Line 755, : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.365]{../replication_package/output/figures/3_2_nolog_Price_solo_CTs_sept20_25.png}
- Line 758, : \includegraphics[trim=0cm 0cm 0cm 1.5cm,clip,scale=0.365]{../replication_package/output/figures/2_1_nolog_Price_solo_CTs_sept20_25.png}
- Line 830, : \caption*{\footnotesize{Note: This figure plots event-study estimates $\beta_k$ from Equation~\ref{eq:EventStudy} for serious adverse events (life-threatening incidents, deaths, hospitalizations, or disabilities) using annual data. Controls are device types matched on pre-event outcome averages; $\beta_{-1}$ is the omitted reference period. Panel~(a): down-regulation (Class~III to II) vs.\ matched controls. Panel~(b): deregulation (Class~II to I) vs.\ matched controls. Panels~(c)--(d) restrict the sample to the 15 deregulated device types that can be linked to outpatient procedure codes in MarketScan claims (1996--2013). Panel~(c) reports raw event counts for this subset; Panel~(d) normalizes by annual procedure volume. The pre-deregulation mean for the normalizable subset is 0.002 serious events per procedure. Too few Class~III devices are linked to procedure codes to allow a comparable normalization. Conley--Taber 95\% confidence intervals are reported.}}
- Line 1119, : \caption*{ \begin{footnotesize}Note: The table presents estimates of Equation \ref{eq:OLS}, a DiD OLS model. Outcomes are derived from \textit{Dimensions} patent data, FDA administrative data, and \citet{kogan:2017}. Column (1) reports 5-year pre-treatment averages for treated device types. Columns (2)--(4) report DiD estimates using (i) matched controls, (ii) intuitively similar devices (treating similar diseases), and (iii) ``later-treated'' devices (reclassified after the sample window), respectively. Device submissions are unavailable for Class I devices. For Column (4), Class III to II control device types are treated after 2015; thus, all post-2015 observations are dropped. Confidence intervals use Conley--Taber inference. Symbols +, *, **, and *** denote statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 1188, : \caption*{ \begin{footnotesize}Note: The table reports estimates from Equation \ref{eq:OLS}, a DiD OLS model. Column (1) reports 5-year pre-event means for treated device types. Columns (2)--(5) show DiD estimates using controls that match on (2) baseline prices across all procedure codes, (3) device outcomes, (4) intuitively similar diseases, and (5) later-treated devices. Price data are available only for 1996--2013, limiting sample size. Due to data constraints, Columns (4)--(5) omit price results. † Pre-mean prices are unlogged, while estimates are logged. Confidence intervals use Conley--Taber inference. +, *, **, and *** denote statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 1227, : \caption*{ \begin{footnotesize}Note: The table presents estimates of Equation \ref{eq:OLS}, a DiD OLS model. Column (1) reports 5-year pre-event means for treated device types. Adverse event outcomes are derived from the FDA MAUDE database. Columns (2)--(4) show DiD estimates using matched, intuitively similar, and ``later-treated'' control groups, respectively. For Column (4), Class III to II controls are treated after 2015; thus, post-2015 observations are dropped. Confidence intervals use Conley--Taber inference. +, *, **, and *** correspond to statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 1795, : This subsection details the construction of the \emph{market age} variable used in Section~\ref{sec:RegulatoryDesign}. I identify the introduction year using hand coding supplemented by GPT‐4o adjudication for Class~II devices. GPT‐4o was provided with a prompt instructing it to report the earliest introduction date and a plausible source (e.g., a patent filing or an early academic study). I then cross‐validated GPT‐4o encodings with a subset of 25 down-regulated device types for which I independently determined introduction years. The correlation coefficient between the hand-coded and GPT‐4o measures was 0.76 ($p<0.001$), lending credibility to the automated approach. The prompt appears below.
- Line 2118, : % %      \put(60,62){\tiny Static estimate: $-0.007$}
- Line 2508, : \caption*{\footnotesize{Note: Panel (a) illustrates the distribution of market age for current Class III medical devices. Panel (b) presents a similar distribution for Class II medical devices. The data were collected using GPT-4o to gather invention dates for each device. The correlation coefficient between market age determined through a hand-coded correspondence for a subset of 25 down-regulated device types and that generated by GPT-4o is 0.76, with $p < 0.001$, indicating a strong positive correlation between the two measures.
- Line 3060, : Estimation is reported three ways: \emph{Borusyak et al. (2021)} imputation estimator (levels), \emph{Log(+1)} where count outcomes are transformed by $\log(y+1)$, and \emph{Quasi-Poisson} for overdispersed counts. Confidence intervals are based on Conley–Taber test statistics; $+,*,**,***$ denote statistical significance at the 0.10, 0.05, 0.01, and 0.001 levels, respectively. Where present, a ``Sample Size'' row refers to the estimation sample used in Columns (2)–(4).
- Line 3199, : The \emph{Prices} blocks are available only for the Borusyak et al. estimator, as the price outcome is continuous and positive; thus, the log price is always the outcome used. Some control-set columns (e.g., Intuitive/Later) are blank for price estimates. For prices, pre-event means are reported in levels, while estimates are on the log scale. The \emph{Market composition} estimation is reported three ways: \emph{Borusyak et al. (2021)} imputation estimator (levels), \emph{Log(+1)} where count outcomes are transformed by $\log(y+1)$, and \emph{Quasi-Poisson} for overdispersed counts.  Confidence intervals use Conley–Taber test statistics; $+,*,**,***$ mark 0.10, 0.05, 0.01, and 0.001 significance. Any ``Sample Size'' rows refer to the estimation sample for the corresponding control-set columns.
- Line 3302, : \item[] Note: Panel A shows Class III to II; Panel B shows Class II to I. Column (1) reports the 5-year pre-event mean for treated device types. Columns (2)–(4) report DiD estimates using \emph{Matched}, \emph{Intuitive}, and \emph{Later-treated} control sets. For the Later-treated specification in the Class III to II case, control device types are treated after 2015; consequently, post-2015 observations are excluded by construction. Estimation is shown using the \emph{Borusyak et al. (2021)} imputation estimator (levels), \emph{Log(+1)} ($\log(y+1)$), and \emph{Quasi-Poisson}. Confidence intervals follow Conley–Taber; significance codes are $+,*,**,***$ for 0.10, 0.05, 0.01, and 0.001 levels. ``Sample Size'' rows, where present, refer to the estimation sample for Columns (2)–(4).
- Line 3339, : \caption*{ \begin{footnotesize}Note: The table presents estimates of Equation \ref{eq:OLS}, which is a difference-in-differences (DiD) style OLS regression model for device types that are closely related to treated medical device types. Column (1) presents the 5-year baseline average of closely related device types for the outcomes listed on the left-hand side. Column (2) presents OLS estimates of the effect of reclassifications on device types closely related to treated device types, using matched controls. Confidence intervals in Column (2) are calculated using Conley--Taber test statistics. Standard errors allow for clustering at the product-code level. +, *, **, and *** correspond to statistical significance at the 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 3598, : \item[] Note: Each panel reports estimates from Equation~\ref{eq:OLS}, a difference-in-differences (DiD) OLS specification. Device types with only zero counts for a given outcome over the sample are excluded (\emph{Zero-Count Units Excluded}). Column~(1) in every subpanel reports the 5-year pre-event mean for treated device types. For the Innovation and Adverse Events blocks, Columns~(2)–(4) report DiD estimates using three control sets: \emph{Matched}, \emph{Intuitive} (treat similar diseases), and \emph{Later-treated}. For the Market Structure block, Columns~(2)–(5) report DiD estimates using \emph{Price-matched} controls, \emph{Matched} controls (matched on baseline innovation and adverse-event levels), \emph{Intuitive} controls, and \emph{Later-treated} controls, respectively. For the Later-treated specification in the Class~III to II case, control device types are treated after 2015; accordingly, post-2015 observations are dropped by construction. Sample sizes reflect the minimum N across outcomes within each panel; N may vary slightly by outcome because the zero-count exclusion is applied separately for each outcome variable. Confidence intervals are computed using Conley–Taber test statistics. Significance codes: $+$, $*$, $**$, and $***$ denote 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 3645, : % \caption*{\begin{footnotesize}Note: The table presents estimates of equation \ref{eq:OLS}, which is a difference-in-differences (DiD) style OLS regression model. In this analysis, I drop all device types that do not exhibit any positive quantity of the given outcome. Column (1) presents the 5-year baseline average of treated device types for the outcomes listed on the left-hand side. Columns (2)--(4) present DiD estimates for the listed outcomes using different control groups: namely, a matched control group, intuitively similar device types (treat similar diseases), and ``later-treated'' device types (treated after the sample window), respectively. Confidence intervals are calculated using Conley--Taber test statistics. +, *, **, and *** correspond to statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 3714, : % \caption*{ \begin{footnotesize}Note: The table presents estimates of equation \ref{eq:OLS}, which is a difference-in-differences (DiD) style OLS regression model. In this analysis, I drop all device types that do not exhibit any positive quantity of the given outcome. Column (1) presents the 5-year baseline average of treated device types for the outcomes listed on the left-hand side. Columns (2)--(5) present DiD estimates for a given outcome using different control groups: namely, a group matched on baseline prices, a group matched on baseline innovation and adverse event levels, an intuitively comparable group, and a later-treated group, respectively. Confidence intervals are calculated using Conley--Taber test statistics.  +, *, **, and *** correspond to statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 3754, : % \caption*{ \begin{footnotesize}Note: The table presents estimates of equation \ref{eq:OLS}, which is a difference-in-differences (DiD) style OLS regression model. In this analysis, I drop all device types that do not exhibit any positive quantity of the given outcome. Column (1) presents the 5-year baseline average of treated device types for the outcomes listed on the left-hand side. Columns (2)--(4) present DiD estimates for the listed outcomes using different control groups: namely, a matched control group, intuitively similar device types (treat similar diseases), and ``later-treated'' device types (treated after the sample window), respectively. For Column (4), Class III to II,  control device types are treated after 2015; thus, all observations after 2015 are dropped. Confidence intervals are calculated using Conley--Taber test statistics. +, *, **, and *** correspond to statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 3782, : % \hspace{6mm}Market Size & 0.94** & 0.001 \\
- Line 3816, : % 0.072 & 0.0 & 0.0 & 0.0 & 0.0 & 0.0\\
- Line 3818, : % 0.064 & 12.08 & 7.26 & 3.57 & 1.76 & 5.04\\
- Line 3820, : % 0.056 & 25.97 & 13.11 & 6.41 & 3.98 & 9.99\\
- Line 3822, : % 0.048 & 45.94 & 20.44 & 12.41 & 5.15 & 16.31\\
- Line 3826, : % 0.032 & 68.43 & 33.07 & 15.16 & 7.72 & 25.03\\
- Line 3828, : % 0.024 & 84.04 & 39.42 & 21.22 & 9.66 & 30.95\\
- Line 3830, : % 0.016 & 90.02 & 44.71 & 24.39 & 11.19 & 34.65\\
- Line 3832, : % 0.008 & 112.41 & 58.62 & 29.23 & 15.46 & 43.87\\
- Line 3841, : %     \caption*{\footnotesize{Note: This table presents the results of the simulation exercise described in Appendix \ref{sec:appendixGammaSimulation}, which simulates the effect of flattening the learning curve on the rate of unique device submissions at an annual frequency by asset quartiles. Figure \ref{fig:GammaSimulation} illustrates this flattening exercise. Standard errors generated from a Monte Carlo procedure are presented in parenthesis below the estimates. This procedure produces estimates across repeated random draws from the empirical distribution of firm characteristics to calculate confidence intervals. I express changes as percent changes relative to the $\gamma = 0.075$ baseline. I flatten the learning curve relative to the firm with the highest experience in the data. In the Table, $\gamma$ begins at its initial starting point estimated in equation \ref{eq:loglinlearning}. Subsequent rows in the table show the percent change in the rate of unique device submissions as $\gamma$, the learning rate, is reduced. These changes are presented for each experience quartile for Class III device manufacturers. $T_{Sum,25}$ represents the bottom 25th percentile of cumulative FDA experience (in days), $T_{Sum,50}$ represents the 25--50th percentile, $T_{Sum,75}$ represents the 50--75th percentile, and $T_{Sum,100}$ represents the 75th--100th percentile. The far-right column presents the total percent change in unique device submissions from a flattening of the learning curve relative to the baseline frequency of unique device submissions.}}
- Line 3864, : Note: This table presents the estimated effects of reclassification events on the probability of safety mentions, analyzed through two distinct approaches. Panel A reports results for Class II to I reclassifications (sample size: 9,856), while Panel B reports results for Class III to II reclassifications (sample size: 1,056). The "pre-mean" column indicates the average outcome prior to reclassification. The estimates are rounded to three decimal places, with standard errors (SE) shown in parentheses directly below the estimates. For the Safety-Only Approach, the outcome measures the probability of observing any mention of the keyword "safety" within a device type-year pair. For the Embedding Distance Approach, the outcome measures whether any patent was identified as semantically similar to a set of five safety-related reference sentences using the BERT embedding model, within the same device type-year pair. Statistical significance is denoted as follows: + ($p < 0.10$), * ($p < 0.05$), ** ($p < 0.01$), and *** ($p < 0.001$).
- Line 3967, : Note: The table presents estimates of Equation \ref{eq:OLS}, a difference-in-differences (DiD) OLS regression model analyzing patenting rates for restricted patent samples described in Appendix \ref{sec:appendixPatentCollection}. Panel A examines reclassifications from Class III to II, while Panel B examines Class II to I. \textit{GPT-4o Identified Devices} refers to patents determined as devices by GPT-4o, and \textit{Health Patents (No Drugs)} refers to patents classified under the CPC system as "health" (A61) excluding drug patents (not A61P). The ``Pre-mean'' column presents the 5-year baseline average of treated device types for the restrictions listed on the left-hand side. The ``DiD Estimate'' column provides DiD estimates when the treated groups are compared to matched controls for the restrictions listed on the left-hand side. Confidence intervals are calculated using Conley--Taber test statistics. Standard errors are presented in parentheses below the estimates. Significance levels are denoted as follows: + p$<$0.10, * p$<$0.05, ** p$<$0.01, *** p$<$0.001.
- Line 4094, : % \caption*{ \begin{footnotesize}Note: The table presents estimates of equation \ref{eq:OLS}, which is a difference-in-differences (DiD) style OLS regression model. This table differs from Table \ref{tab:Innovation} in that it presents estimates from an estimation that uses a restricted patent sample described in Appendix \ref{sec:appendixPatentCollection}, and only presents the patenting rate outcome. Simply put, patents in this analysis include only those labeled as health-related and non-drug by patent examiners. Patents are derived from the \textit{Dimensions} patent database. Column (1) presents the 5-year baseline average of treated device types for the outcomes listed on the left-hand side. Columns (2)--(4) present DiD estimates for the listed outcomes using different control groups: namely, a matched control group, intuitively similar device types (treat similar diseases), and ``later-treated'' device types (treated after the sample window), respectively. For Column (4), Class III to II,  control device types are treated after 2015; thus, all observations after 2015 are dropped. Confidence intervals are calculated using Conley--Taber test statistics. +, *, **, and *** correspond to statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.
- Line 4116, : % \caption*{ \begin{footnotesize}Note: The table presents the estimates of equation \ref{eq:loglinlearning}, which estimates the learning coefficient $\gamma$ and the baseline time requirement $\beta(R_c)$ for both Class III original PMA approvals (Column 1) and Class II 510(k) clearance (Column 2) of unique devices via OLS. The estimates for Class III devices are calculated by only considering the approval times of filed original PMAs by firms with at least one day of prior experience navigating FDA regulations. The estimates for Class II devices are calculated by only considering the clearance times of 510(k) documents for unique devices that were submitted by firms with at least one day of prior experience navigating FDA regulations. Prior experience is calculated using approval times when filing any prior documentation type (510(k) or PMAs). Standard errors are clustered at the firm level. +, *, **, and *** correspond to statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/10_table_formatting.py**

- Line 404, : df_est.loc[df_est["tstat"] > 1.6449, "stars"] = "+"
- Line 405, : df_est.loc[df_est["tstat"] > 1.9600, "stars"] = "*"
- Line 406, : df_est.loc[df_est["tstat"] > 2.5758, "stars"] = "**"
- Line 407, : df_est.loc[df_est["tstat"] > 3.2905, "stars"] = "***"

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Table_D11_reg_design.tex**

- Line 11, : constant & 0.2379* & 82.2241+ & 0.0163 & -11.0336 \\
- Line 12, : & (0.108) & (40.709) & (0.019) & (8.349) \\
- Line 14, : exp\_years & -0.0051* & -1.5231* & -0.0003+ & -0.1058 \\
- Line 15, : & (0.002) & (0.713) & (0.000) & (0.068) \\
- Line 17, : v\_serious\_event & -0.0005 & -1.7597 & -0.0093 & -0.3647 \\
- Line 18, : & (0.004) & (1.496) & (0.007) & (3.103) \\
- Line 20, : FDA\_own\_accord & 0.0128 & -21.9656 &  &  \\
- Line 21, : & (0.040) & (15.221) &  &  \\
- Line 23, : DPM &  &  & 0.0277 & 4.2571 \\
- Line 24, : &  &  & (0.044) & (18.400) \\
- Line 26, : patents\_allpats &  & 2.4315*** &  & 2.1629*** \\
- Line 27, : &  & (0.502) &  & (0.083) \\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD11_Utilization.tex**

- Line 46, : \caption*{ \begin{footnotesize}Note: The table reports estimates from Equation \ref{eq:OLS}, a DiD OLS model. The outcome is log annual procedure counts (utilization) from MarketScan claims data (1996--2013). Column (1) reports 5-year pre-event means for treated device types. Columns (2)--(3) show DiD estimates using controls that match on (2) baseline procedure counts across all procedure codes and (3) device outcomes. For each panel, the first row reports Conley--Taber stacked DiD estimates and the second row reports BJS imputation estimates. † Pre-mean is unlogged, while estimates are in logs. Confidence intervals use Conley--Taber inference. +, *, **, and *** denote statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/compare_all_numbers.py**

- Line 202, : # 1.100 -> 9.900 and flipped sign reported "max|abs diff| = 0" and PASSED.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00a_extract_parameters.py**

- Line 141, : p = min(max(p, 1e-3), 0.999)
- Line 146, : return {"kind": "geometric", "p": round(min(max(p, 1e-3), 0.999), 3), "mean": m_r}
- Line 481, : check(smooth_rate(0.13712) == 0.137, f"rate {smooth_rate(0.13712)}")
- Line 497, : "missingness": {"col_a": smooth_rate(0.137)},
- Line 503, : "c": {"role": "num", "missing_rate": smooth_rate(0.137),
- Line 532, : "x": {"role": "num", "missing_rate": 0.13712, "kind": "uniform01k"}}}}),  # unrounded rate
- Line 549, : leaky_rate = {"product_codes": [], "entities": {}, "missingness": {"c": 0.13712}}  # unrounded

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/04_event_studies.py**

- Line 991, : # states "0.002 serious events per procedure" (tex:830). Every one of these must
- Line 1007, : "2_1_nolog_v_serious_restrict_oct22_24.png",     # tex:830  0.002 events/procedure

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Table_1_summary_stats.tex**

- Line 14, : \textit{A. PMA/510(k) Submissions} & 0.169M & - & - & -\\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD11_Utilization.tex**

- Line 46, : \caption*{ \begin{footnotesize}Note: The table reports estimates from Equation \ref{eq:OLS}, a DiD OLS model. The outcome is log annual procedure counts (utilization) from MarketScan claims data (1996--2013). Column (1) reports 5-year pre-event means for treated device types. Columns (2)--(3) show DiD estimates using controls that match on (2) baseline procedure counts across all procedure codes and (3) device outcomes. For each panel, the first row reports Conley--Taber stacked DiD estimates and the second row reports BJS imputation estimates. † Pre-mean is unlogged, while estimates are in logs. Confidence intervals use Conley--Taber inference. +, *, **, and *** denote statistical significance at 0.10, 0.05, 0.01, and 0.001 levels, respectively.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output/tables/Formatted/TableD11b_DeviceExperience_2_1.tex**

- Line 10, : Device Experience (years) & -0.0003+ & -0.1058 \\
- Line 11, : & (0.0002) & (0.0685) \\
- Line 12, : Intercept & 0.0163 & -11.0336 \\
- Line 13, : & (0.0191) & (8.3486) \\
- Line 14, : Baseline Serious Adverse Events & -0.0093 & -0.3647 \\
- Line 15, : & (0.0075) & (3.1028) \\
- Line 16, : Device Priority Model Score & 0.0277 & 4.2571 \\
- Line 17, : & (0.0444) & (18.3997) \\
- Line 18, : Cardiovascular Devices & -0.0115 & 16.3703 \\
- Line 19, : & (0.0371) & (15.4027) \\
- Line 20, : Clinical Chemistry And Clinical Toxicology Devices & 0.0029 & -22.6099 \\
- Line 21, : & (0.0371) & (15.6071) \\
- Line 22, : Dental Devices & 0.0206 & 2.6410 \\
- Line 23, : & (0.0479) & (19.9891) \\
- Line 24, : Ear, Nose, And Throat Devices & -0.0800* & 18.6166 \\
- Line 25, : & (0.0389) & (16.4118) \\
- Line 26, : Gastroenterology-Urology Devices & 0.0045 & 15.6497+ \\
- Line 27, : & (0.0214) & (9.2684) \\
- Line 28, : General And Plastic Surgery Devices & -0.1418 & 5.3578 \\
- Line 29, : & (0.1037) & (43.0702) \\
- Line 30, : General Hospital And Personal Use Devices & 0.0268 & 12.8010 \\
- Line 31, : & (0.0261) & (11.1145) \\
- Line 32, : Hematology And Pathology Devices & 0.0046 & 3.9181 \\
- Line 33, : & (0.0389) & (16.3574) \\
- Line 34, : Immunology And Microbiology Devices & -0.0077 & 2.0851 \\
- Line 35, : & (0.0207) & (9.0568) \\
- Line 36, : Neurological Devices & 0.0346 & 15.9747 \\
- Line 37, : & (0.0728) & (30.2834) \\
- Line 38, : Obstetrical And Gynecological Devices & 0.0411 & 21.0217 \\
- Line 39, : & (0.0376) & (15.9464) \\
- Line 40, : Ophthalmic Devices & -0.0041 & 20.8908 \\
- Line 41, : & (0.0343) & (14.5629) \\
- Line 42, : Orthopedic Devices & -0.0296 & 16.9783 \\
- Line 43, : & (0.0726) & (30.2304) \\
- Line 44, : Physical Medicine Devices & 0.0379 & 13.2064 \\
- Line 45, : & (0.0243) & (10.2633) \\
- Line 46, : Radiology Devices & -0.0071 & 10.6918 \\
- Line 47, : & (0.0271) & (11.6077) \\
- Line 48, : Baseline Patent Count & --- & 2.1629*** \\
- Line 49, : & --- & (0.0833) \\
- Line 58, : \begin{footnotesize}Note: The regression relates device-level DiD estimates for (1) serious adverse events and (2) patenting activity to each device type's market age (FDA years of experience) and other covariates, including baseline patenting rates. \textquotedblleft---\textquotedblright\ indicates variables excluded from a given specification. To increase power, all deregulated device types with at least one submission are included. Fixed effects for part descriptions are included, with anesthesiology devices as the omitted group. +, *, **, *** denote significance at 0.10, 0.05, 0.01, 0.001 levels.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/audit_pipeline.py**

- Line 261, : # distinct colours 379; an all-white or all-black image scores 0% and 1 colour, a single dark pixel 0.001%.
- Line 262, : _MIN_NONBACKGROUND_SHARE = 0.005

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/independent_universe.py**

- Line 358, : mask = draw_missingness(100_000, 0.137, salt="col")
- Line 359, : check(abs(mask.mean() - 0.137) < 0.01, f"missingness rate off ({mask.mean():.4f})")
- Line 360, : check(np.array_equal(mask, draw_missingness(100_000, 0.137, salt="col")),
- Line 363, : check(not np.array_equal(mask, draw_missingness(100_000, 0.137, salt="other")),

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/15_intext_derived_numbers.py**

- Line 24, : (matched-control adverse-event level estimates: H = -1.773, D = -0.426)
- Line 26, : - output/tables/firm_heterogeneity_k_pct.csv  (tercile ratios; #4 = 1.612)
- Line 127, : # precision it just verified: a maturity slope of 0.0002 checked at 4 dp was being written to
- Line 185, : h = float(adv.loc[adv.outcome == "H", "Estimate"].iloc[0])   # ~ -1.773
- Line 186, : d = float(adv.loc[adv.outcome == "D", "Estimate"].iloc[0])   # ~ -0.426
- Line 462, : ("3_2", "v_serious_est"): ("maturity_slope_serious_3_2", -0.0170),
- Line 463, : ("3_2", "patent_est"):    ("maturity_slope_patent_3_2",  -0.0396),
- Line 464, : ("2_1", "v_serious_est"): ("maturity_slope_serious_2_1", -0.0015),
- Line 465, : ("2_1", "patent_est"):    ("maturity_slope_patent_2_1",   0.0002),
- Line 672, : "maturity_slope_serious_3_2",        # #7b footnote  -0.0170
- Line 673, : "maturity_slope_patent_3_2",         # #7b footnote  -0.0396
- Line 674, : "maturity_slope_serious_2_1",        # #7b footnote  -0.0015
- Line 675, : "maturity_slope_patent_2_1",         # #7b footnote   0.0002
- Line 721, : "normalizable_serious_per_procedure",  # 0.002 serious events per procedure
- Line 827, : check("breakthrough_panel_n", int(r["n_obs"]), ("approx", 1584, 0.001), "III->II breakthrough panel N")
- Line 834, : """Manuscript footnote L500 + body L1795 + caption L2508: r=0.76 (p<0.001) hold-out validation between
- Line 855, : "GPT-vs-hand invention-year validation (manuscript r=0.76, p<0.001)")
- Line 895, : ("normalizable_serious_per_procedure", 0.002, 3),
- Line 905, : a thirteenth is the normalized panel's caption value ("0.002 serious events per
- Line 1027, : # (tex:203, "$760 million"): xi_real 295.66147 / CPI_DEFLATOR_2019 0.3891444 = 759.77.
- Line 1374, : ("3_2", "v_serious_est"): ("maturity_slope_serious_3_2_se", 0.008, 3,
- Line 1375, : "maturity_slope_serious_3_2_p", 0.060, 3),
- Line 1376, : ("3_2", "patent_est"): ("maturity_slope_patent_3_2_se", 0.013, 3,
- Line 1377, : "maturity_slope_patent_3_2_p", 0.008, 3),
- Line 1378, : ("2_1", "v_serious_est"): ("maturity_slope_serious_2_1_se", 0.001, 3,
- Line 1379, : "maturity_slope_serious_2_1_p", 0.218, 3),
- Line 1380, : ("2_1", "patent_est"): ("maturity_slope_patent_2_1_se", 0.001, 3,
- Line 1381, : "maturity_slope_patent_2_1_p", 0.876, 3),

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/12b_gpt_price_links_generation.py**

- Line 148, : - Regulation: 886.3600; intraocular lens.
- Line 170, : - Regulation: 882.5890; Transcutaneous electrical nerve stimulator for pain relief.
- Line 192, : - Regulation: 862.1215; Creatine phosphokinase/creatine kinase or isoenzymes test system.
- Line 214, : - Regulation: 862.1660; Quality control material (assayed and unassayed).
- Line 236, : - Regulation: 886.4350; Manual ophthalmic surgical instrument.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD12_SafetyRobustness.tex**

- Line 3, : \hspace{6mm}Pr of any Safety Mention & Embedding Distance & 0.011 & 0.009*** \\
- Line 4, : &  & (0.106) & (0.003) \\
- Line 6, : \hspace{6mm}Pr of any Safety Mention & ``Safety'' Only & 0.180 & -0.008 \\
- Line 7, : &  & (0.385) & (0.008) \\
- Line 14, : \hspace{6mm}Pr of any Safety Mention & Embedding Distance & 0.125 & -0.035+ \\
- Line 15, : &  & (0.338) & (0.021) \\
- Line 17, : \hspace{6mm}Pr of any Safety Mention & ``Safety'' Only & 0.458 & 0.097** \\
- Line 18, : &  & (0.509) & (0.035) \\

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/audit_simulated_data.py**

- Line 507, : if copyfrac > 0.999:
- Line 739, : band = 4.0 * std + 0.0005 * n_syn                    # 4 sigma + half-ULP (rate rounded to 3 dp)

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/certification/validate_handentered_tables.py**

- Line 122, : VSL_M, HOSP_M = 10.0, 0.022

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/output-simulated/tables/Formatted/TableD11b_DeviceExperience_2_1.tex**

- Line 10, : Device Experience (years) & -0.0003+ & -0.0003 \\
- Line 11, : & (0.0002) & (0.0025) \\
- Line 12, : Intercept & 0.0163 & 0.3395 \\
- Line 13, : & (0.0191) & (0.3049) \\
- Line 14, : Baseline Serious Adverse Events & -0.0093 & 0.0982 \\
- Line 15, : & (0.0075) & (0.1119) \\
- Line 16, : Device Priority Model Score & 0.0277 & -0.6393 \\
- Line 17, : & (0.0444) & (0.6635) \\
- Line 18, : Cardiovascular Devices & -0.0115 & -0.2501 \\
- Line 19, : & (0.0371) & (0.5580) \\
- Line 20, : Clinical Chemistry And Clinical Toxicology Devices & 0.0029 & 0.2635 \\
- Line 21, : & (0.0371) & (0.5565) \\
- Line 22, : Dental Devices & 0.0206 & -0.5608 \\
- Line 23, : & (0.0479) & (0.7152) \\
- Line 24, : Ear, Nose, And Throat Devices & -0.0800* & 0.1616 \\
- Line 25, : & (0.0389) & (0.5839) \\
- Line 26, : Gastroenterology-Urology Devices & 0.0045 & 0.0069 \\
- Line 27, : & (0.0214) & (0.3205) \\
- Line 28, : General And Plastic Surgery Devices & -0.1418 & -0.7551 \\
- Line 29, : & (0.1037) & (1.5490) \\
- Line 30, : General Hospital And Personal Use Devices & 0.0268 & -0.0017 \\
- Line 31, : & (0.0261) & (0.3908) \\
- Line 32, : Hematology And Pathology Devices & 0.0046 & -0.2212 \\
- Line 33, : & (0.0389) & (0.5844) \\
- Line 34, : Immunology And Microbiology Devices & -0.0077 & -0.0716 \\
- Line 35, : & (0.0207) & (0.3132) \\
- Line 36, : Neurological Devices & 0.0346 & -0.1713 \\
- Line 37, : & (0.0728) & (1.0874) \\
- Line 38, : Obstetrical And Gynecological Devices & 0.0411 & 0.0508 \\
- Line 39, : & (0.0376) & (0.5640) \\
- Line 40, : Ophthalmic Devices & -0.0041 & 0.1721 \\
- Line 41, : & (0.0343) & (0.5162) \\
- Line 42, : Orthopedic Devices & -0.0296 & -0.1935 \\
- Line 43, : & (0.0726) & (1.0847) \\
- Line 44, : Physical Medicine Devices & 0.0379 & 0.2075 \\
- Line 45, : & (0.0243) & (0.3637) \\
- Line 46, : Radiology Devices & -0.0071 & -0.2554 \\
- Line 47, : & (0.0271) & (0.4064) \\
- Line 48, : Baseline Patent Count & --- & -0.1348*** \\
- Line 49, : & --- & (0.0167) \\
- Line 58, : \begin{footnotesize}Note: The regression relates device-level DiD estimates for (1) serious adverse events and (2) patenting activity to each device type's market age (FDA years of experience) and other covariates, including baseline patenting rates. \textquotedblleft---\textquotedblright\ indicates variables excluded from a given specification. To increase power, all deregulated device types with at least one submission are included. Fixed effects for part descriptions are included, with anesthesiology devices as the omitted group. +, *, **, *** denote significance at 0.10, 0.05, 0.01, 0.001 levels.

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/11a_product_variety.py**

- Line 234, : # at the seed below, the III->II scores at 10 and 15 topics are 0.4905 and 0.4907. A

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/code/modules/table_format.py**

- Line 76, : if z >= 3.2905:
- Line 78, : elif z >= 2.576:
- Line 82, : elif z >= 1.645:

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/synthetic_pipeline/generators/gen_00c_synthetic_marketscan.py**

- Line 266, : # 5,541 product codes (mean 1.435 rows per code) with the category code populated on 6,125 of

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/paper/build_manuscript.py**

- Line 145, : # Verified locally (TeX Live 2026, pdfTeX 3.141592653-2.6-1.40.29) that rc==0 is the correct bar

**/Users/florianoswald/actions-runner/_work/JPE-Rogers-20251257/JPE-Rogers-20251257/replication-package/20261101T133319Z_job12560950/nondeterministic_variable_sensitivity/invention_years_2_1/maturity_sensitivity.py**

- Line 64, : print(f"sample, they contribute on the order of {round(undrawn*0.025)} further crossings, in both")

