library(tidyverse)
library(didimputation)
library(fixest)
library(did)
# Determinism: pin fixest to a single thread. Multithreaded residualization has a run-to-run
# FP-summation-order non-determinism that, on one ill-conditioned difference-of-counts robustness
# cell, swings the point estimate (1.961 <-> 3.516) and can SIGABRT the II->I estimation. Single-
# threaded is deterministic and stable (see run_all.build_child_env, which also pins OMP/BLAS).
setFixest_nthreads(1)
filter_country <- function(df, coll){
  fml <- as.formula(
    paste0(
      coll,
      " ~ posttreat",
      " | factorized^FE + year^FE"
    )
  )
 
  
  model = feols(fml, df)
  # model = feols(cname ~ i(ET, treatment, -1) | factorized^FE + year^FE, df)
  # coeff_y = coef(model)
  # print(summary(model, cluster = "factorized"))
  # na.rm = FALSE returns residuals aligned 1:1 to the INPUT rows, with NA where feols removed an
  # observation (singleton/collinear FE level, or NA outcome). The Python caller (conley_taber.py)
  # relies on this alignment to keep its permutation-design arrays the same length as the residual
  # vector. When feols removes nothing this is identical to resid(model) -- no rows, no NAs, same
  # values/order -- so deposited (real-data) estimates are unchanged.
  return(c(as.data.frame(coef(model)), as.data.frame(resid(model, na.rm = FALSE))))
}

# Same static-DiD specification as filter_country, but returns the point estimate and its
# class_by_episode-clustered standard error (no residuals). conley_taber.py calls this ONLY as a
# fallback when feols removed observations, so the balanced-panel permutation CI is undefined for
# that sample: it reports feols's still-valid coefficient with a clustered-SE normal-approximation
# interval.
# On the real price panel feols removes observations in singleton or collinear interacted-FE
# cells for the two II->I Expert-concordance BilledAmt samples (8 of 118,414 for Expert; 8 of
# 79,714 for Expert Matched), so this function supplies the interval for those two rows of
# price_utilization_estimates.csv. Every
# call is recorded by conley_taber._record_inference_fallback. No manuscript number is affected: the
# price footnote quotes the BJS_imputation rows, which are estimated elsewhere.
filter_country_se <- function(df, coll){
  fml <- as.formula(paste0(coll, " ~ posttreat | factorized^FE + year^FE"))
  # Fit WITHOUT cluster= so the fit itself cannot choke on cluster processing in a degenerate
  # (heavily NA-removed) sample; the point estimate is cluster-independent. Derive the clustered SE
  # via the same coeftable()/vcov() idiom filter_country_poisson uses -- NOT the bare se() extractor,
  # which errored ("as.character(sc[[1]]): cannot coerce type 'closure'") on such samples. Degrade
  # gracefully: class_by_episode-clustered vcov -> default vcov -> NA (-> caller skips this cell).
  model <- feols(fml, df)
  ct <- tryCatch(
    fixest::coeftable(model, vcov = vcov(model, cluster = ~ class_by_episode)),
    error = function(e){
      message("filter_country_se: clustered vcov failed (", conditionMessage(e),
              "); falling back to default vcov")
      tryCatch(fixest::coeftable(model), error = function(e2) NULL)
    })
  if (is.null(ct) || !("posttreat" %in% rownames(ct))) return(c(NA_real_, NA_real_))
  return(c(as.numeric(ct["posttreat", "Estimate"]), as.numeric(ct["posttreat", "Std. Error"])))
}


filter_country_poisson <- function(df, coll){
  # Convert the column name to a symbol for use in the formula
  
  cname <- sym(coll)
  print(paste("Processing column:", cname))
  
  # Construct the formula dynamically
  formula <- as.formula(paste0(coll, " ~ posttreat | factorized^FE + year^FE"))
  
  # Perform Poisson regression using feglm
  model <- feglm(formula, 
                 data = df, 
                 family = poisson())
  
  # Compute clustered standard errors at the 'factorized' level
  vcov_clustered <- vcov(model, cluster = ~ factorized)
  
  # Extract the coefficient table with clustered standard errors
  coef_table <- coeftable(model, vcov = vcov_clustered)
  
  # Check if 'posttreat' is in the coefficients
  if(!"posttreat" %in% rownames(coef_table)){
    stop("The 'posttreat' variable is not present in the model coefficients.")
  }
  
  # Extract the estimate and clustered standard error for 'posttreat'
  estimate <- coef_table["posttreat", "Estimate"]
  se <- coef_table["posttreat", "Std. Error"]
  
  # Calculate 95% Confidence Intervals using the standard normal approximation
  conf_low <- estimate - 1.96 * se
  conf_high <- estimate + 1.96 * se
  
  # Combine the results into a data frame with the expected column names
  result <- data.frame(
    estimate = estimate,
    conf.low = conf_low,
    conf.high = conf_high
  )
  
  return(result)
}


# Load necessary libraries
library(fixest)  # For feglm function
setFixest_nthreads(1)  # determinism (see note at top of file)
library(dplyr)    # For data manipulation

# Define the Quasi-Poisson regression function
filter_country_quasipoisson <- function(df, coll) {
  # Convert the column name to a symbol for use in the formula
  cname <- sym(coll)
  print(paste("Processing column:", cname))
  
  # Ensure that 'factorized' and 'year' are treated as factors
  df <- df %>%
    mutate(
      factorized = as.factor(factorized),
      year = as.factor(year)
    )
  
  # Construct the formula dynamically
  # The syntax 'posttreat | factorized + year' specifies fixed effects for 'factorized' and 'year'
  formula <- as.formula(paste0(coll, " ~ posttreat | factorized + year"))
  
  # Perform Quasi-Poisson regression using feglm
  # Explicitly name the formula argument as 'fml'
  model <- feglm(
    fml = formula,
    data = df,
    family = quasipoisson(link = "log")
  )
  
  # Compute clustered standard errors at the 'factorized' level
  vcov_clustered <- vcov(model, cluster = ~ factorized)
  
  # Extract the coefficient table with clustered standard errors
  coef_table <- coeftable(model, vcov = vcov_clustered)
  
  # Check if 'posttreat' is in the coefficients
  if (!"posttreat" %in% rownames(coef_table)) {
    stop("The 'posttreat' variable is not present in the model coefficients.")
  }
  
  # Extract the estimate and clustered standard error for 'posttreat'
  estimate <- coef_table["posttreat", "Estimate"]
  se <- coef_table["posttreat", "Std. Error"]
  
  # Calculate 95% Confidence Intervals using the standard normal approximation
  conf_low <- estimate - 1.96 * se
  conf_high <- estimate + 1.96 * se
  
  # Combine the results into a data frame with the expected column names
  result <- data.frame(
    estimate = estimate,
    conf.low = conf_low,
    conf.high = conf_high
  )
  
  return(result)
}


filter_country_2_1 <- function(df, coll){
  formula <- as.formula(paste0(coll, " ~ posttreat | factorized^FE + year^FE"))
  
  model = feols(formula, df,
                cluster = 'class_by_episode')
  coeff_y = coef(model)
  # model = feols(cname ~ i(ET, treatment, -1) | factorized^FE + year^FE, df)
  # coeff_y = coef(model)
  print(summary(model))
  return(c(coeff_y, se(model)))
}

recall_DID <- function(df, coll){
  formula <- as.formula(paste0(coll, " ~ posttreat | factorized + year"))
  model = feols(formula, df,
                cluster = 'class_by_episode')
  print(summary(model))
  return(c(as.data.frame(coef(model)), as.data.frame(se(model))))
}



filter_country_wo <- function(df, coll){
  cname = sym(coll)
  print(cname)
  model = feols(cname ~ 0 | factorized^FE + year^FE, df)
  coeff_y = coef(model)
  # model = feols(cname ~ i(ET, treatment, -1) | factorized^FE + year^FE, df)
  # coeff_y = coef(model)
  # print(summary(model, cluster = "factorized"))
  return(resid(model))
}

filter_country_ES <- function(df, coll){
  formula <- as.formula(paste0(coll, " ~ i(ET, treatment, ref = -1) | factorized^FE + year^FE"))
  
 
  model = feols(formula, df)
  # coeff_y = coef(model)
  # print(summary(model, cluster = "factorized"))
  # print(fixef(model))

  # na.rm = FALSE: residuals aligned 1:1 to the input rows (NA where feols removed an obs), so the
  # Python event-study caller can detect a removed observation. Identical to resid(model) when
  # nothing is removed (the deposited real-data case) -> deposited event-study figures unchanged.
  return(c(as.data.frame(coef(model)), as.data.frame(resid(model, na.rm = FALSE))))
}

# Event-study coefficients with class_by_episode-clustered standard errors (same specification as
# filter_country_ES, no residuals). conley_taber_stacked_es calls this ONLY as a fallback when feols
# removed observations, so the balanced-panel permutation CI is undefined: it reports the per-horizon
# feols coefficient with a clustered-SE normal-approximation interval. Never used on deposited data.
filter_country_es_se <- function(df, coll){
  formula <- as.formula(paste0(coll, " ~ i(ET, treatment, ref = -1) | factorized^FE + year^FE"))
  # Same robustness as filter_country_se: fit without cluster=, then derive per-horizon clustered SEs
  # via coeftable()/vcov() (not bare se()). Return (coef_vector, se_vector) aligned to the model's
  # coefficient order -- identical contract to the original, but crash-proof on degenerate samples.
  model <- feols(formula, df)
  cf <- coef(model)
  ct <- tryCatch(
    fixest::coeftable(model, vcov = vcov(model, cluster = ~ class_by_episode)),
    error = function(e){
      message("filter_country_es_se: clustered vcov failed (", conditionMessage(e),
              "); falling back to default vcov")
      tryCatch(fixest::coeftable(model), error = function(e2) NULL)
    })
  if (is.null(ct)) {
    return(c(as.data.frame(cf), as.data.frame(setNames(rep(NA_real_, length(cf)), names(cf)))))
  }
  se_named <- ct[, "Std. Error"]; names(se_named) <- rownames(ct)
  # align the SE vector to coef()'s order so caller's index_int matches
  se_aligned <- setNames(as.numeric(se_named[names(cf)]), names(cf))
  return(c(as.data.frame(cf), as.data.frame(se_aligned)))
}

recalls_ES <- function(df, coll){
  formula <- as.formula(paste0(coll, " ~ i(ET, treatment, ref = -1) | factorized + year"))

  model = feols(formula, df,
                cluster = 'factorized')
  # coeff_y = coef(model)
  print(summary(model, cluster = "factorized"))
  # print(fixef(model))
  
  return(c(as.data.frame(coef(model)), as.data.frame(se(model))))
}


filter_country_ES_2_1 <- function(df, coll){
  formula <- as.formula(paste0(coll, " ~ i(ET, treatment, ref = -1) | factorized^FE + year^FE"))
  
  
  model = feols(formula, df, 
                cluster = 'class_by_episode')
  # coeff_y = coef(model)
  print(summary(model))
  return(c(as.data.frame(coef(model)), as.data.frame(se(model))))
}

filter_country_ES_2_1_utilization <- function(df, coll){
  formula <- as.formula(paste0(coll, " ~ i(ET, treatment, ref = -1) | factorized + year"))

  model = feols(formula, df, 
                cluster = 'factorized')
  print(summary(model))
  return(c(as.data.frame(coef(model)), as.data.frame(se(model))))
}

